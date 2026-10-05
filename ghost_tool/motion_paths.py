"""motion_paths.py — Per-bone / per-object motion paths drawn by Ghost Tool.

A path is the world position of a bone head (or tail, or an object origin)
sampled over a frame window.  Samples live in a module cache keyed by
(object_name, bone_name, frame).  Pinned paths come from
scene.ghost_tool.motion_paths; "follow selection" adds transient grey paths
for the current selection.  Drawing is a separate POST_VIEW handler.
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Optional

import blf
import bpy
import gpu
from bpy_extras import view3d_utils
from gpu_extras.batch import batch_for_shader
from mathutils import Vector

from .motion_channels import LOCATION_CHANNELS, MOTION_CHANNELS, channel_family
from .utils import debug, get_fcurves_from_action, get_scene_id, log, scene_sampling, tag_viewport_redraw, warn

PALETTE: tuple[tuple[float, float, float], ...] = (
    (0.96, 0.71, 0.00), (0.31, 0.76, 0.97), (0.51, 0.78, 0.52), (0.90, 0.45, 0.45),
    (0.73, 0.53, 0.93), (0.98, 0.60, 0.30), (0.36, 0.85, 0.80), (0.85, 0.85, 0.40),
)
FOLLOW_COLOR: tuple[float, float, float] = (0.6, 0.6, 0.6)
SLOW_RGB = (0.2, 0.4, 1.0)
FAST_RGB = (1.0, 0.3, 0.1)
KEY_DOT_COLOR = (1.0, 1.0, 1.0, 0.95)

PathKey = tuple[str, str]  # (object_name, bone_name); bone_name "" = object origin
ORIGIN_PATHS = ("location", "delta_location")   # the object channels that move its origin

_cache: dict[tuple[str, str, float], Vector] = {}
_dirty: set[PathKey] = set()
_draw_handler = None
_draw_handler_2d = None
_last_refresh_ms: float = 0.0
_marker_uids: dict[str, set[str]] = {}   # per scene id: ghost markers created by Markers on Paths
_anchors: dict[PathKey, str] = {}        # anchor each cached path was sampled with
_cache_scene: Optional[str] = None       # scene id the cached positions were sampled in


@dataclass(frozen=True)
class PathTarget:
    key: PathKey
    obj: bpy.types.Object
    anchor: str          # 'HEAD' | 'TAIL'
    color: tuple[float, float, float]
    thickness: int
    pinned: bool


def clear_cache() -> None:
    _cache.clear()
    _dirty.clear()
    _anchors.clear()


def desired_frames(settings, scene: bpy.types.Scene) -> list[float]:
    mode = settings.paths_range_mode
    if mode == 'SCENE':
        start, end = scene.frame_start, scene.frame_end
    elif mode == 'CUSTOM':
        start, end = settings.custom_range_start, settings.custom_range_end
    else:
        start = scene.frame_current - settings.paths_before
        end = scene.frame_current + settings.paths_after
    step = max(1, settings.paths_step)
    return [float(f) for f in range(int(start), int(end) + 1, step)]


def _resolve(scene: bpy.types.Scene, object_name: str, bone_name: str) -> Optional[bpy.types.Object]:
    obj = scene.objects.get(object_name)   # an object unlinked from this scene has no path here
    if obj is None:
        return None
    if bone_name and (obj.type != 'ARMATURE' or bone_name not in obj.pose.bones):
        return None
    return obj


def entry_is_missing(entry) -> bool:
    return _resolve(entry.id_data, entry.object_name, entry.bone_name) is None   # id_data: the owning scene


def pinned_targets(scene: bpy.types.Scene) -> list[PathTarget]:
    targets: list[PathTarget] = []
    for entry in scene.ghost_tool.motion_paths:
        if not entry.visible:
            continue
        obj = _resolve(scene, entry.object_name, entry.bone_name)
        if obj is None:
            continue
        targets.append(PathTarget((entry.object_name, entry.bone_name), obj, entry.anchor,
                                  tuple(entry.color), entry.thickness, True))
    return targets


def selected_keys(context: bpy.types.Context) -> list[tuple[PathKey, bpy.types.Object]]:
    """(key, object) for the selection: pose bones in Pose mode, else objects."""
    result: list[tuple[PathKey, bpy.types.Object]] = []
    if context.mode == 'POSE':
        for pb in getattr(context, 'selected_pose_bones', None) or []:
            result.append(((pb.id_data.name, pb.name), pb.id_data))
        return result
    for obj in getattr(context, 'selected_objects', None) or []:
        if obj.get("ghost_tool_mesh_ghost"):
            continue
        if obj.type == 'ARMATURE':
            roots = [b for b in obj.pose.bones if b.parent is None]
            if roots:
                result.append(((obj.name, roots[0].name), obj))
                continue
        result.append(((obj.name, ""), obj))
    return result


def follow_targets(context: bpy.types.Context, pinned_keys: set[PathKey]) -> list[PathTarget]:
    settings = context.scene.ghost_tool
    if not settings.paths_follow_selection:
        return []
    seen: set[PathKey] = set(pinned_keys)
    targets: list[PathTarget] = []
    for key, obj in selected_keys(context):
        if key in seen:
            continue
        seen.add(key)
        targets.append(PathTarget(key, obj, 'HEAD', FOLLOW_COLOR, 1, False))
    return targets


def all_targets(context: bpy.types.Context) -> list[PathTarget]:
    pinned = pinned_targets(context.scene)
    return pinned + follow_targets(context, {t.key for t in pinned})


def _sample(depsgraph, obj: bpy.types.Object, bone_name: str, anchor: str) -> Vector:
    ev = obj.evaluated_get(depsgraph)
    if bone_name:
        pb = ev.pose.bones[bone_name]
        local = pb.tail if anchor == 'TAIL' else pb.head
        return (ev.matrix_world @ local).copy()
    return ev.matrix_world.translation.copy()


def mark_dirty(key: PathKey) -> None:
    _dirty.add(key)


def forget(key: PathKey) -> None:
    """Drop one path's cached positions, so a draw sees it as unsampled and asks for a refresh."""
    for stale in [c for c in _cache if (c[0], c[1]) == key]:
        del _cache[stale]
    _anchors.pop(key, None)


def _dependencies(obj: bpy.types.Object) -> set[str]:
    """Names of the objects whose motion can move ``obj``: parents and constraint
    targets, followed transitively (a parent's parent, a target's parent)."""
    seen: set[str] = set()
    stack = [obj]
    while stack:
        o = stack.pop()
        refs = [o.parent] + [getattr(c, 'target', None) for c in o.constraints]
        if o.type == 'ARMATURE' and o.pose is not None:
            refs += [getattr(c, 'target', None) for pb in o.pose.bones for c in pb.constraints]
        for ref in refs:
            if ref is not None and ref.name not in seen and ref is not obj:
                seen.add(ref.name)
                stack.append(ref)
    return seen


def mark_dirty_for_id(block) -> None:
    """A depsgraph update on this ID: re-sample the paths that depend on it, including
    paths of children and constraint users whose position follows the changed object."""
    if isinstance(block, bpy.types.Object):
        changed = {block.name}
    elif isinstance(block, bpy.types.Action):
        changed = {obj.name for obj in bpy.data.objects
                   if obj.animation_data and obj.animation_data.action == block}
    else:
        return
    if not changed:
        return
    affected: dict[str, bool] = {}
    for key in _cache_keys():
        name = key[0]
        if name not in affected:
            obj = bpy.data.objects.get(name)
            affected[name] = name in changed or (obj is not None and not changed.isdisjoint(_dependencies(obj)))
        if affected[name]:
            _dirty.add(key)


def _cache_keys() -> set[PathKey]:
    return {(o, b) for (o, b, _f) in _cache}


def refresh_paths(context: bpy.types.Context) -> int:
    """Sample what the window needs and the cache lacks. Returns samples taken."""
    global _cache_scene
    scene = context.scene
    settings = scene.ghost_tool
    if not settings.paths_enabled:
        return 0
    if get_scene_id(scene) != _cache_scene:
        clear_cache()   # positions sampled in another scene may differ (drivers, constraints)
        _cache_scene = get_scene_id(scene)
    targets = all_targets(context)
    for t in targets:
        if _anchors.get(t.key, t.anchor) != t.anchor:
            _dirty.add(t.key)   # HEAD <-> TAIL: the cached positions belong to the other point
        _anchors[t.key] = t.anchor
    frames = desired_frames(settings, scene)
    wanted = {(t.key[0], t.key[1], f) for t in targets for f in frames}
    for stale in [c for c in _cache if c not in wanted]:
        del _cache[stale]
    for key in _dirty:
        for f in frames:
            _cache.pop((key[0], key[1], f), None)
    _dirty.clear()
    missing: dict[float, list[PathTarget]] = {}
    for t in targets:
        for f in frames:
            if (t.key[0], t.key[1], f) not in _cache:
                missing.setdefault(f, []).append(t)
    if not missing:
        return 0
    global _last_refresh_ms
    count = 0
    t0 = time.perf_counter()
    with scene_sampling(scene):
        for f in sorted(missing):
            scene.frame_set(int(f), subframe=f - int(f))
            depsgraph = context.evaluated_depsgraph_get()
            for t in missing[f]:
                _cache[(t.key[0], t.key[1], f)] = _sample(depsgraph, t.obj, t.key[1], t.anchor)
                count += 1
    _last_refresh_ms = (time.perf_counter() - t0) * 1000.0
    debug(f"Motion paths: sampled {count} positions in {_last_refresh_ms:.1f} ms")
    return count


def last_refresh_ms() -> float:
    return _last_refresh_ms


def key_frames(target: PathTarget) -> list[float]:
    """Frames with a keyframe on channels that move this target."""
    obj = target.obj
    ad = obj.animation_data
    if not ad or not ad.action:
        return []
    if target.key[1]:
        # Same channels as the path's markers: a head moves only by location, a tail also by rotation.
        bone = f'pose.bones["{bpy.utils.escape_identifier(target.key[1])}"].'
        channels = MOTION_CHANNELS if target.anchor == 'TAIL' else LOCATION_CHANNELS
        paths = {bone + channel_family(c) for c in channels}
    else:
        paths = set(ORIGIN_PATHS)
    frames: set[float] = set()
    for fc in get_fcurves_from_action(ad.action, obj):
        if fc.data_path in paths:
            frames.update(float(k.co.x) for k in fc.keyframe_points)
    return sorted(frames)


def path_segments(context, target: PathTarget, frames: list[float]) -> list[tuple[Vector, Vector, tuple]]:
    settings = context.scene.ghost_tool
    current = float(context.scene.frame_current)
    pts = [(f, _cache.get((target.key[0], target.key[1], f))) for f in frames]
    pts = [(f, p) for f, p in pts if p is not None]
    if len(pts) < 2:
        return []
    r, g, b = target.color
    style = settings.paths_style
    span = max(frames[-1] - frames[0], 1.0)
    lengths = [(pts[i + 1][1] - pts[i][1]).length for i in range(len(pts) - 1)]
    longest = max(lengths) or 1.0
    segs = []
    for i, ((f0, p0), (f1, p1)) in enumerate(zip(pts, pts[1:])):
        if style == 'SPEED':
            t = lengths[i] / longest
            color = (SLOW_RGB[0] + (FAST_RGB[0] - SLOW_RGB[0]) * t,
                     SLOW_RGB[1] + (FAST_RGB[1] - SLOW_RGB[1]) * t,
                     SLOW_RGB[2] + (FAST_RGB[2] - SLOW_RGB[2]) * t, 0.9)
        elif style == 'FADE':
            d = min(abs((f0 + f1) * 0.5 - current) / span, 1.0)
            color = (r, g, b, max(0.9 * (1.0 - d), 0.1))
        else:
            color = (r, g, b, 0.9)
        segs.append((p0, p1, color))
    return segs


def _active_key(context) -> Optional[PathKey]:
    pb = getattr(context, 'active_pose_bone', None)
    if pb is not None:
        return (pb.id_data.name, pb.name)
    obj = getattr(context, 'active_object', None)
    return (obj.name, "") if obj is not None else None


def active_entry_index(context) -> int:
    """Index of the pinned path that follows the active bone or object, or -1."""
    key = _active_key(context)
    for index, entry in enumerate(context.scene.ghost_tool.motion_paths):
        if (entry.object_name, entry.bone_name) == key:
            return index
    return -1


def dialog_props(entry) -> tuple[str, ...]:
    """Properties the path settings dialog shows; an object origin has no tail."""
    return ("color", "thickness", "anchor") if entry.bone_name else ("color", "thickness")


def draw_motion_paths() -> None:
    context = bpy.context
    scene = context.scene
    if not hasattr(scene, 'ghost_tool'):
        return
    settings = scene.ghost_tool
    if not settings.is_active or not settings.paths_enabled:
        return
    if request_missing_samples(context) and get_scene_id(scene) != _cache_scene:
        return   # cache belongs to another scene; the scheduled refresh replaces it
    frames = desired_frames(settings, scene)
    active = _active_key(context)
    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    gpu.state.blend_set('ALPHA')
    try:
        for target in all_targets(context):
            segs = path_segments(context, target, frames)
            if not segs:
                continue
            width = float(target.thickness + (1 if target.key == active else 0))
            gpu.state.line_width_set(width)
            buckets: dict[tuple, list[Vector]] = {}
            for p0, p1, color in segs:
                buckets.setdefault(tuple(round(c, 2) for c in color), []).extend((p0, p1))
            for color, verts in buckets.items():
                batch = batch_for_shader(shader, 'LINES', {"pos": verts})
                shader.bind(); shader.uniform_float("color", color); batch.draw(shader)
            if settings.paths_show_key_dots:
                dots = [_cache[(target.key[0], target.key[1], f)] for f in key_frames(target)
                        if (target.key[0], target.key[1], f) in _cache]
                if dots:
                    gpu.state.point_size_set(6.0)
                    batch = batch_for_shader(shader, 'POINTS', {"pos": dots})
                    shader.bind(); shader.uniform_float("color", KEY_DOT_COLOR); batch.draw(shader)
    finally:
        gpu.state.line_width_set(1.0)
        gpu.state.blend_set('NONE')


def draw_frame_numbers() -> None:
    context = bpy.context
    scene = context.scene
    if not hasattr(scene, 'ghost_tool'):
        return
    settings = scene.ghost_tool
    if not (settings.is_active and settings.paths_enabled and settings.paths_show_frame_numbers):
        return
    if get_scene_id(scene) != _cache_scene:
        return   # cached positions belong to another scene
    region, rv3d = context.region, context.region_data
    if region is None or rv3d is None:
        return
    font = 0
    blf.size(font, 11)
    blf.color(font, 0.9, 0.9, 0.9, 0.9)
    frames = desired_frames(settings, scene)
    for target in all_targets(context):
        for f in frames:
            pos = _cache.get((target.key[0], target.key[1], f))
            if pos is None:
                continue
            p2 = view3d_utils.location_3d_to_region_2d(region, rv3d, pos)
            if p2 is None:
                continue
            blf.position(font, p2.x + 4, p2.y + 4, 0)
            blf.draw(font, f"{int(f)}")


def sync_markers(context) -> int:
    """Markers on paths: ghost markers for the pinned paths, or none.

    Only markers this function owns are touched; Generate's markers stay, except one on the
    same key as a path marker, which it takes over (and removes with it when turned off). A re-sync
    reconciles instead of rebuilding: a marker whose (object, bone, channel, frame) is
    still wanted keeps its uid, pin and selection and only takes the new position; a
    pinned marker that left the window stays until Markers on Paths is turned off.

    Markers sit on the path: only keys on sampled frames, at the path's anchor. A bone's
    own rotation never moves its head, and a rotation drag aims the tail, so a HEAD path
    carries location markers only and a TAIL path carries location and rotation markers."""
    from .ghost_data import GhostStore, generate_ghosts_at_keyframes, LOCATION_CHANNELS, MOTION_CHANNELS
    scene = context.scene
    settings = scene.ghost_tool
    store = GhostStore.get(scene)
    owned = _marker_uids.setdefault(get_scene_id(scene), set())
    current = {g.uid: g for g in (store.get_by_uid(uid) for uid in owned) if g is not None}
    if not settings.paths_show_markers:
        for uid in current:
            store.remove(uid)
        owned.clear()
        tag_viewport_redraw(context)
        return 0
    by_identity = {(g.object_name, g.bone_name, g.channel, g.frame): g for g in current.values()}
    # A Generate marker on the same key is taken over, never doubled: it moves onto the path and
    # becomes a path marker (owned), the same way Generate defers to path markers on a rebuild.
    others = {(g.object_name, g.bone_name, g.channel, g.frame): g for g in store if g.uid not in current}
    wanted: set[str] = set()
    bones_by_job: dict[tuple[str, str], list[str]] = {}
    object_paths: list[str] = []
    for t in pinned_targets(scene):
        if t.key[1]:
            bones_by_job.setdefault((t.key[0], t.anchor), []).append(t.key[1])
        else:
            object_paths.append(t.key[0])
    jobs = [(name, bones, bpy.data.objects[name], anchor,
             MOTION_CHANNELS if anchor == 'TAIL' else LOCATION_CHANNELS)
            for (name, anchor), bones in bones_by_job.items()]
    jobs += [(name, [], None, None, MOTION_CHANNELS) for name in object_paths]
    frames = desired_frames(settings, scene)
    if not frames:
        jobs = []   # empty window: no markers wanted; the reconcile below still removes old ones
    window = (int(frames[0]), int(frames[-1])) if frames else None   # keys on the drawn stretch
    sampled = set(frames)   # with Every > 1 a key between samples has no point on the path
    moved = relevelled = False
    for object_name, bones, armature, anchor, channels in jobs:
        ghosts = generate_ghosts_at_keyframes(bpy.data.objects[object_name], armature, bones, channels,
                                              frame_range=window, anchor=anchor, frames=sampled)
        for g in ghosts:
            identity = (g.object_name, g.bone_name, g.channel, g.frame)
            kept = by_identity.get(identity) or others.get(identity)
            if kept is not None:
                if tuple(kept.world_position) != tuple(g.world_position) or kept.local_value != g.local_value:
                    moved = True
                kept.world_position, kept.local_value = g.world_position, g.local_value
                kept.parent_frame_a, kept.parent_frame_b = g.parent_frame_a, g.parent_frame_b
                if kept.generation_level != g.generation_level:   # a taken-over marker is a keyframe marker now
                    kept.generation_level = g.generation_level
                    relevelled = moved = True
                wanted.add(kept.uid)
            else:
                store.add(g)
                wanted.add(g.uid)
    for uid, g in current.items():
        if uid not in wanted and not g.is_pinned:
            store.remove(uid)
    owned.clear()
    owned.update(wanted | {uid for uid, g in current.items() if g.is_pinned})
    if relevelled:
        store._update_level_counts()   # count_by_level caches per-level totals at add/remove time
    if moved:
        store._bump_version()   # in-place moves are invisible to version-keyed caches otherwise
    tag_viewport_redraw(context)
    return len(wanted)


def reset_for_new_file() -> None:
    """A loaded file has new ghosts and scenes: forget cached positions and marker ownership."""
    global _cache_scene
    clear_cache()
    _marker_uids.clear()
    _cache_scene = None


def owned_markers(scene) -> list:
    """The markers Markers on Paths created in this scene, so a store rebuild can keep them."""
    from .ghost_data import GhostStore
    owned = _marker_uids.get(get_scene_id(scene), set())
    return [g for g in GhostStore.get(scene) if g.uid in owned]


def request_missing_samples(context) -> bool:
    """Schedule a pipeline refresh when a drawn path lacks samples. Safe in a draw handler:
    it only registers a timer, never samples. Returns True when a refresh was requested."""
    scene = context.scene
    settings = scene.ghost_tool
    if not settings.paths_enabled:
        return False
    frames = desired_frames(settings, scene)
    stale = get_scene_id(scene) != _cache_scene
    if not stale and all((t.key[0], t.key[1], f) in _cache
                         for t in all_targets(context) for f in frames):
        return False
    from .ghost_pipeline import GhostPipeline, _schedule_deferred_update
    GhostPipeline.get(scene).mark_dirty()
    _schedule_deferred_update()
    return True


def _deferred_marker_sync() -> None:
    """Timer body: marker generation calls frame_set, which a property update callback must not."""
    try:
        sync_markers(bpy.context)
    except Exception as exc:
        warn(f"Motion paths markers: {exc}")
    return None


def request_marker_sync() -> None:
    if not bpy.app.timers.is_registered(_deferred_marker_sync):
        bpy.app.timers.register(_deferred_marker_sync, first_interval=0.0)


def _sync_markers_if_shown(context) -> None:
    """Operators that change the pinned list keep Markers on Paths in step with it."""
    if context.scene.ghost_tool.paths_show_markers:
        sync_markers(context)


def _next_color(settings) -> tuple[float, float, float]:
    return PALETTE[len(settings.motion_paths) % len(PALETTE)]


class GHOST_OT_paths_add_selected(bpy.types.Operator):
    bl_idname = "ghost_tool.paths_add_selected"
    bl_label = "Add Path for Selected"
    bl_description = "Pin a motion path for each selected bone (Pose mode) or object"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if selected_keys(context):
            return True
        cls.poll_message_set("Select bones or objects first")
        return False

    def execute(self, context):
        settings = context.scene.ghost_tool
        existing = {(e.object_name, e.bone_name) for e in settings.motion_paths}
        added = 0
        for (object_name, bone_name), _obj in selected_keys(context):
            if (object_name, bone_name) in existing:
                continue
            entry = settings.motion_paths.add()
            entry.object_name, entry.bone_name = object_name, bone_name
            entry.color = _next_color(settings)
            existing.add((object_name, bone_name))
            added += 1
        settings["paths_enabled"] = True
        settings.motion_paths_index = len(settings.motion_paths) - 1
        refresh_paths(context)  # draw the new paths now, not on the next frame change
        _sync_markers_if_shown(context)
        tag_viewport_redraw(context)
        self.report({'INFO'}, f"Pinned {added} motion path(s)")
        return {'FINISHED'}


class GHOST_OT_paths_remove(bpy.types.Operator):
    bl_idname = "ghost_tool.paths_remove"
    bl_label = "Remove Path"
    bl_description = "Unpin this motion path"
    bl_options = {'REGISTER', 'UNDO'}
    index: bpy.props.IntProperty(default=-1)  # type: ignore[assignment]

    def execute(self, context):
        settings = context.scene.ghost_tool
        idx = self.index if self.index >= 0 else settings.motion_paths_index
        if not 0 <= idx < len(settings.motion_paths):
            return {'CANCELLED'}
        entry = settings.motion_paths[idx]
        key = (entry.object_name, entry.bone_name)
        settings.motion_paths.remove(idx)
        forget(key)
        settings.motion_paths_index = min(idx, len(settings.motion_paths) - 1)
        _sync_markers_if_shown(context)
        tag_viewport_redraw(context)
        return {'FINISHED'}


class GHOST_OT_paths_clear(bpy.types.Operator):
    bl_idname = "ghost_tool.paths_clear"
    bl_label = "Clear Paths"
    bl_description = "Unpin every motion path"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.ghost_tool.motion_paths.clear()
        context.scene.ghost_tool.motion_paths_index = -1
        clear_cache()
        _sync_markers_if_shown(context)
        tag_viewport_redraw(context)
        return {'FINISHED'}


class GHOST_OT_paths_toggle_visible(bpy.types.Operator):
    bl_idname = "ghost_tool.paths_toggle_visible"
    bl_label = "Toggle Path"
    bl_description = "Show or hide one motion path, or all of them"
    bl_options = {'REGISTER', 'UNDO'}
    action: bpy.props.EnumProperty(items=[('ONE', "One", ""), ('ALL_ON', "All on", ""), ('ALL_OFF', "All off", "")], default='ONE')  # type: ignore[assignment]
    index: bpy.props.IntProperty(default=-1)  # type: ignore[assignment]

    def execute(self, context):
        paths = context.scene.ghost_tool.motion_paths
        if self.action == 'ONE':
            if not 0 <= self.index < len(paths):
                return {'CANCELLED'}
            paths[self.index].visible = not paths[self.index].visible
        else:
            for entry in paths:
                entry.visible = self.action == 'ALL_ON'
        _sync_markers_if_shown(context)
        tag_viewport_redraw(context)
        return {'FINISHED'}


class GHOST_OT_paths_set_color(bpy.types.Operator):
    bl_idname = "ghost_tool.paths_set_color"
    bl_label = "Path Settings"
    bl_description = "Change the colour, thickness and traced point of this motion path"
    bl_options = {'REGISTER', 'UNDO'}
    index: bpy.props.IntProperty(default=-1)  # type: ignore[assignment]
    color: bpy.props.FloatVectorProperty(
        name="Colour", description="Colour of this path", subtype='COLOR', size=3, min=0.0, max=1.0,
    )  # type: ignore[assignment]
    thickness: bpy.props.IntProperty(
        name="Thickness", description="Line width of this path in pixels", min=1, max=6, default=2,
    )  # type: ignore[assignment]
    anchor: bpy.props.EnumProperty(
        name="Trace",
        description="Which point of the bone the path traces",
        items=[('HEAD', "Head", "Trace the bone head"), ('TAIL', "Tail", "Trace the bone tail")],
        default='HEAD',
    )  # type: ignore[assignment]

    def invoke(self, context, event):
        paths = context.scene.ghost_tool.motion_paths
        if not 0 <= self.index < len(paths):   # -1 would silently pick the last path
            return {'CANCELLED'}
        entry = paths[self.index]
        self.color, self.thickness, self.anchor = tuple(entry.color), entry.thickness, entry.anchor
        return context.window_manager.invoke_props_dialog(self, width=220)

    def draw(self, context):
        paths = context.scene.ghost_tool.motion_paths
        if 0 <= self.index < len(paths):
            for name in dialog_props(paths[self.index]):
                self.layout.prop(self, name, expand=name == "anchor")

    def execute(self, context):
        paths = context.scene.ghost_tool.motion_paths
        if not 0 <= self.index < len(paths):
            return {'CANCELLED'}
        entry = paths[self.index]
        # Only what the caller set: the list's Head/Tail button passes the anchor alone.
        for name in dialog_props(entry):
            if not self.properties.is_property_set(name):
                continue
            if name == "anchor" and entry.anchor == self.anchor:
                continue   # rewriting the same anchor would re-sample the whole path
            setattr(entry, name, getattr(self, name))
        tag_viewport_redraw(context)
        return {'FINISHED'}


CLASSES: tuple[type, ...] = (
    GHOST_OT_paths_add_selected,
    GHOST_OT_paths_remove,
    GHOST_OT_paths_clear,
    GHOST_OT_paths_toggle_visible,
    GHOST_OT_paths_set_color,
)


def register() -> None:
    global _draw_handler, _draw_handler_2d
    for cls in CLASSES:
        bpy.utils.register_class(cls)
    _draw_handler = bpy.types.SpaceView3D.draw_handler_add(draw_motion_paths, (), 'WINDOW', 'POST_VIEW')
    _draw_handler_2d = bpy.types.SpaceView3D.draw_handler_add(draw_frame_numbers, (), 'WINDOW', 'POST_PIXEL')
    log("Motion paths module registered.")


def unregister() -> None:
    global _draw_handler, _draw_handler_2d
    if bpy.app.timers.is_registered(_deferred_marker_sync):
        bpy.app.timers.unregister(_deferred_marker_sync)
    _marker_uids.clear()
    if _draw_handler is not None:
        bpy.types.SpaceView3D.draw_handler_remove(_draw_handler, 'WINDOW')
        _draw_handler = None
    if _draw_handler_2d is not None:
        bpy.types.SpaceView3D.draw_handler_remove(_draw_handler_2d, 'WINDOW')
        _draw_handler_2d = None
    for cls in reversed(CLASSES):
        try:
            bpy.utils.unregister_class(cls)
        except RuntimeError:
            pass
    clear_cache()
