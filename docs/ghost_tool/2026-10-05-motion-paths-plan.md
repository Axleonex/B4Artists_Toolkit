# Ghost Tool Motion Paths — Implementation Plan

> **For the executing agent:** work task by task on branch `work/ghost-tool-paths`
> in `G:\LapArt\Projects\B4Artists_Toolkit`. Commit after every task with the
> Axlbot identity (`-c user.name=Axlbot -c user.email=57645501+Axleonex@users.noreply.github.com`),
> never a co-author line, never touch `bl_info["description"]`.

**Goal:** Per-bone / per-object motion paths drawn live by Ghost Tool, toggleable one at a time or all at once, reachable from the Dope Sheet and Graph Editor headers — never the N-panel. Spec: `docs/ghost_tool/2026-10-05-motion-paths-design.md`.

**Architecture:** One new module `ghost_tool/motion_paths.py` owns the sample cache, the operators, the UIList/popover and its own `SpaceView3D` draw handler. Scene data lives on `scene.ghost_tool` (a `CollectionProperty` of `GhostPathEntry` defined in `ghost_data.py`). The live pipeline (`ghost_pipeline.py`) calls `motion_paths.refresh_paths()` on the same triggers the onion skins use. Header strips in `ui_panel.py` get a path segment; the same function is appended to `GRAPH_HT_header`.

**Tech stack:** Bforartists 5.1.2 (`bpy`, `gpu`, `gpu_extras.batch`, `blf`), Python 3.11, `unittest` run headless with `bforartists --background --factory-startup --python tests/test_ghost_paths.py`.

**Run tests with:**
```bash
cd "G:/LapArt/Projects/B4Artists_Toolkit" && "/c/Program Files/Bforartists/5.1.2/bforartists.exe" --background --factory-startup --python tests/test_ghost_paths.py 2>&1 | grep -E "^Ran |^OK|^FAILED|^FAIL:|^ERROR:|Error:|Traceback"
```
Always delete `ghost_tool/__pycache__` after a run (`rm -rf ghost_tool/__pycache__`) so no bytecode lands in the tree.

---

### Task 0: Route before the first edit

**Objective:** Bind change evidence before any file changes (LapArt rule: route with declared paths first).

**Step 1:** Route the change through the project's change-evidence router, declaring every file this plan touches in this repository: `ghost_tool/motion_paths.py`, `ghost_tool/ghost_data.py`, `ghost_tool/ghost_pipeline.py`, `ghost_tool/ui_panel.py`, `ghost_tool/__init__.py`, `tests/test_ghost_paths.py`, `README.md`, `releases/VERSIONS.md`, and for the release (Task 17) `releases/b4_ghost_tool_v3.5.0.zip` and `releases/b4_ghost_tool_v3.4.1.zip`. The VERSIONS.md outside this repository (Task 17 step 5) is routed in its own run.

Expected: a decision record with `"authorized": true` and a fallback receipt path; read `actual_lane`, not only the recommended lane. Do not edit anything before the router prints this.

---

### Task 1: Test harness file

**Objective:** Create the headless test file with a scene fixture (2-bone FK rig + animated cube) that every later task adds to.

**Files:**
- Create: `tests/test_ghost_paths.py`

**Step 1: Write the file**
```python
"""Ghost Tool 3.5: motion paths. Run with:
    bforartists --background --factory-startup --python tests/test_ghost_paths.py
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import ghost_tool  # noqa: E402
from ghost_tool import ghost_data as gd  # noqa: E402
from ghost_tool import motion_paths as mp  # noqa: E402


def _clear_scene():
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj)
    for action in list(bpy.data.actions):
        bpy.data.actions.remove(action)


def _rig(name="Rig"):
    data = bpy.data.armatures.new(name)
    rig = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(rig)
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.mode_set(mode='EDIT')
    upper = data.edit_bones.new("upper")
    upper.head, upper.tail = (0, 0, 0), (0, 0, 1)
    lower = data.edit_bones.new("lower")
    lower.head, lower.tail = (0, 0, 1), (0, 0, 2)
    lower.parent = upper
    bpy.ops.object.mode_set(mode='POSE')
    for frame, angle in ((1, 0.0), (10, 0.8), (20, -0.4)):
        for pb in rig.pose.bones:
            pb.rotation_euler = (angle, 0, 0)
            pb.keyframe_insert("rotation_euler", frame=frame)
    bpy.ops.object.mode_set(mode='OBJECT')
    return rig


def _cube(name="Cube"):
    bpy.ops.mesh.primitive_cube_add()
    cube = bpy.context.object
    cube.name = name
    for frame, x in ((1, 0.0), (20, 4.0)):
        cube.location.x = x
        cube.keyframe_insert("location", frame=frame)
    return cube


class GhostPaths(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with patch.object(ghost_tool, "_clear_pycache"):
            ghost_tool.register()

    @classmethod
    def tearDownClass(cls):
        ghost_tool.unregister()

    def setUp(self):
        _clear_scene()
        self.scene = bpy.context.scene
        self.scene.frame_start, self.scene.frame_end = 1, 20
        self.settings = self.scene.ghost_tool
        self.settings.is_active = True
        self.settings.live_point_ghosts = False
        self.settings.live_mesh_ghosts = False
        self.settings.motion_paths.clear()
        self.settings.paths_enabled = True
        self.settings.paths_follow_selection = False
        self.settings.paths_range_mode = 'AROUND_CURSOR'
        self.settings.paths_before = 3
        self.settings.paths_after = 3
        self.settings.paths_step = 1
        mp.clear_cache()
        self.scene.frame_set(10)

    def select_bones(self, rig, *names):
        bpy.context.view_layer.objects.active = rig
        for obj in bpy.data.objects:
            obj.select_set(obj is rig)
        bpy.ops.object.mode_set(mode='POSE')
        for pb in rig.pose.bones:
            pb.bone.select = pb.name in names
        rig.data.bones.active = rig.data.bones[names[0]]

    def test_harness_registers(self):
        self.assertTrue(hasattr(self.settings, "motion_paths"))


if __name__ == "__main__":
    result = unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(GhostPaths))
    print("GHOST_PATHS_RESULT: " + ("PASS" if result.wasSuccessful() else "FAIL"), flush=True)
    if not result.wasSuccessful():
        sys.exit(1)
```

**Step 2: Run it** — expected: `ModuleNotFoundError: No module named 'ghost_tool.motion_paths'` (the module does not exist yet). That is the failing state for Task 2.

---

### Task 2: Scene data — `GhostPathEntry` and the path settings

**Objective:** Add the per-path collection and the path settings to `ghost_data.py`.

**Files:**
- Modify: `ghost_tool/ghost_data.py` — add the PropertyGroup before `class GhostToolSceneSettings`, add properties after the `mesh_ghost_sources` property, add the class to `CLASSES` before `GhostToolSceneSettings`.

**Step 1: Add the entry type** (insert immediately above `class GhostToolSceneSettings(bpy.types.PropertyGroup):`)
```python
def _on_path_setting_changed(self, context):
    """Range/style changed: drop the path cache so the next refresh re-samples."""
    try:
        from .motion_paths import clear_cache
        clear_cache()
        tag_viewport_redraw(context)
    except Exception as exc:
        warn(f"Motion paths: could not reset cache: {exc}")


class GhostPathEntry(bpy.types.PropertyGroup):
    """One pinned motion path: an object, or a bone of an armature."""

    object_name: bpy.props.StringProperty(name="Object")  # type: ignore[assignment]
    bone_name: bpy.props.StringProperty(name="Bone", default="")  # type: ignore[assignment]
    visible: bpy.props.BoolProperty(name="Visible", default=True)  # type: ignore[assignment]
    color: bpy.props.FloatVectorProperty(
        name="Color", subtype='COLOR', size=3, min=0.0, max=1.0, default=(0.96, 0.71, 0.0),
    )  # type: ignore[assignment]
    thickness: bpy.props.IntProperty(name="Thickness", default=2, min=1, max=6)  # type: ignore[assignment]
    anchor: bpy.props.EnumProperty(
        name="Anchor",
        items=[('HEAD', "Head", "Bone head / object origin"), ('TAIL', "Tail", "Bone tail")],
        default='HEAD',
    )  # type: ignore[assignment]

    @property
    def label(self) -> str:
        return f"{self.object_name} › {self.bone_name}" if self.bone_name else self.object_name
```

**Step 2: Add the settings** (insert after the `mesh_ghost_sources` property block, inside `GhostToolSceneSettings`)
```python
    # ── Motion Paths ────────────────────────────────────────────────────
    motion_paths: bpy.props.CollectionProperty(type=GhostPathEntry)  # type: ignore[assignment]
    motion_paths_index: bpy.props.IntProperty(default=-1)  # type: ignore[assignment]

    paths_enabled: bpy.props.BoolProperty(
        name="Motion Paths",
        description="Draw motion paths for the pinned bones and objects",
        default=False,
        update=_on_path_setting_changed,
    )  # type: ignore[assignment]
    paths_follow_selection: bpy.props.BoolProperty(
        name="Follow Selection",
        description="Also draw a grey path for whatever is selected right now",
        default=False,
        update=_on_path_setting_changed,
    )  # type: ignore[assignment]
    paths_show_markers: bpy.props.BoolProperty(
        name="Markers on Paths",
        description="Generate draggable ghost markers on the pinned paths",
        default=False,
    )  # type: ignore[assignment]
    paths_show_key_dots: bpy.props.BoolProperty(
        name="Key Dots", description="Mark keyframes on each path", default=True,
    )  # type: ignore[assignment]
    paths_show_frame_numbers: bpy.props.BoolProperty(
        name="Frame Numbers", description="Label each sampled frame", default=False,
    )  # type: ignore[assignment]
    paths_range_mode: bpy.props.EnumProperty(
        name="Range",
        items=[
            ('AROUND_CURSOR', "Around Playhead", "Frames before and after the playhead"),
            ('SCENE', "Scene", "The scene frame range"),
            ('CUSTOM', "Custom", "The custom range from Settings"),
        ],
        default='AROUND_CURSOR',
        update=_on_path_setting_changed,
    )  # type: ignore[assignment]
    paths_before: bpy.props.IntProperty(name="Before", default=12, min=0, max=500, update=_on_path_setting_changed)  # type: ignore[assignment]
    paths_after: bpy.props.IntProperty(name="After", default=12, min=0, max=500, update=_on_path_setting_changed)  # type: ignore[assignment]
    paths_step: bpy.props.IntProperty(name="Every", default=1, min=1, max=24, update=_on_path_setting_changed)  # type: ignore[assignment]
    paths_style: bpy.props.EnumProperty(
        name="Style",
        items=[('SOLID', "Solid", "One colour"), ('SPEED', "Speed", "Blue slow, red fast"), ('FADE', "Fade", "Fade with distance from the playhead")],
        default='SOLID',
    )  # type: ignore[assignment]
```

**Step 3: Register the class** — in `CLASSES` (near line 2368) put `GhostPathEntry,` on the line before `GhostToolSceneSettings,`.

**Step 4: Verify** — create a stub `ghost_tool/motion_paths.py` containing only:
```python
"""motion_paths.py — Per-bone / per-object motion paths drawn by Ghost Tool."""
from __future__ import annotations

_cache: dict = {}


def clear_cache() -> None:
    _cache.clear()


def register() -> None:
    pass


def unregister() -> None:
    pass
```
Run the tests. Expected: `Ran 1 test … OK`.

**Step 5: Commit**
```bash
git add ghost_tool/ghost_data.py ghost_tool/motion_paths.py tests/test_ghost_paths.py
git -c user.name=Axlbot -c user.email=57645501+Axleonex@users.noreply.github.com commit -m "Ghost Tool paths: scene data and test harness"
```

---

### Task 3: Register the module

**Objective:** Make `motion_paths` part of the add-on's import/reload/register cycle.

**Files:**
- Modify: `ghost_tool/__init__.py` — `_import_modules` and `_REGISTER_ORDER`.

**Step 1:** In `_import_modules`, after `from . import mesh_ghosts` add `from . import motion_paths`; in the reload block after `importlib.reload(mesh_ghosts)` add `importlib.reload(motion_paths)`; in the returned dict add `"motion_paths": motion_paths,` after `"mesh_ghosts"`.

**Step 2:** In `_REGISTER_ORDER` add `"motion_paths",` after `"mesh_ghosts",` (before `"viewport_draw"`).

**Step 3: Test** — add to `GhostPaths`:
```python
    def test_module_registered(self):
        self.assertIn("motion_paths", ghost_tool._REGISTER_ORDER)
```
Run: expected `Ran 2 tests … OK`. Also run `tests/smoke_bforartists.py`: exit 0.

**Step 4: Commit** — `"Ghost Tool paths: register module"`.

---

### Task 4: Frame window and target resolution

**Objective:** Pure helpers: which frames to sample, and which (object, bone) targets exist.

**Files:**
- Modify: `ghost_tool/motion_paths.py`

**Step 1: Failing tests**
```python
    def test_desired_frames_around_cursor(self):
        self.assertEqual(mp.desired_frames(self.settings, self.scene), [7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0])
        self.settings.paths_step = 2
        self.assertEqual(mp.desired_frames(self.settings, self.scene), [7.0, 9.0, 11.0, 13.0])
        self.settings.paths_range_mode = 'SCENE'
        self.settings.paths_step = 5
        self.assertEqual(mp.desired_frames(self.settings, self.scene), [1.0, 6.0, 11.0, 16.0])

    def test_pinned_targets_resolve_and_skip_missing(self):
        rig = _rig()
        e = self.settings.motion_paths.add(); e.object_name, e.bone_name = rig.name, "lower"
        m = self.settings.motion_paths.add(); m.object_name, m.bone_name = rig.name, "nope"
        targets = mp.pinned_targets(self.scene)
        self.assertEqual([(t.key, t.obj) for t in targets], [((rig.name, "lower"), rig)])
        self.assertTrue(mp.entry_is_missing(m))
        self.assertFalse(mp.entry_is_missing(e))
```
Run: expected `AttributeError: module … has no attribute 'desired_frames'`.

**Step 2: Implementation** (replace the stub body of `motion_paths.py`)
```python
"""motion_paths.py — Per-bone / per-object motion paths drawn by Ghost Tool.

A path is the world position of a bone head (or tail, or an object origin)
sampled over a frame window.  Samples live in a module cache keyed by
(object_name, bone_name, frame).  Pinned paths come from
scene.ghost_tool.motion_paths; "follow selection" adds transient grey paths
for the current selection.  Drawing is a separate POST_VIEW handler.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import bpy
from mathutils import Vector

from .utils import debug, log, scene_sampling, tag_viewport_redraw, warn

PALETTE: tuple[tuple[float, float, float], ...] = (
    (0.96, 0.71, 0.00), (0.31, 0.76, 0.97), (0.51, 0.78, 0.52), (0.90, 0.45, 0.45),
    (0.73, 0.53, 0.93), (0.98, 0.60, 0.30), (0.36, 0.85, 0.80), (0.85, 0.85, 0.40),
)
FOLLOW_COLOR: tuple[float, float, float] = (0.6, 0.6, 0.6)

PathKey = tuple[str, str]  # (object_name, bone_name); bone_name "" = object origin

_cache: dict[tuple[str, str, float], Vector] = {}
_dirty: set[PathKey] = set()


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


def _resolve(object_name: str, bone_name: str) -> Optional[bpy.types.Object]:
    obj = bpy.data.objects.get(object_name)
    if obj is None:
        return None
    if bone_name and (obj.type != 'ARMATURE' or bone_name not in obj.pose.bones):
        return None
    return obj


def entry_is_missing(entry) -> bool:
    return _resolve(entry.object_name, entry.bone_name) is None


def pinned_targets(scene: bpy.types.Scene) -> list[PathTarget]:
    targets: list[PathTarget] = []
    for entry in scene.ghost_tool.motion_paths:
        if not entry.visible:
            continue
        obj = _resolve(entry.object_name, entry.bone_name)
        if obj is None:
            continue
        targets.append(PathTarget((entry.object_name, entry.bone_name), obj, entry.anchor,
                                  tuple(entry.color), entry.thickness, True))
    return targets


def register() -> None:
    pass


def unregister() -> None:
    pass
```
Run: expected `Ran 4 tests … OK`.

**Step 3: Commit** — `"Ghost Tool paths: frame window and target resolution"`.

---

### Task 5: Follow-selection targets

**Objective:** Grey transient targets for the current selection, de-duplicated against pinned ones.

**Step 1: Failing test**
```python
    def test_follow_selection_targets(self):
        rig = _rig()
        cube = _cube()
        self.settings.paths_follow_selection = True
        self.select_bones(rig, "upper", "lower")
        keys = {t.key for t in mp.follow_targets(bpy.context, pinned_keys=set())}
        self.assertEqual(keys, {(rig.name, "upper"), (rig.name, "lower")})
        self.assertTrue(all(t.color == mp.FOLLOW_COLOR and not t.pinned for t in mp.follow_targets(bpy.context, pinned_keys=set())))
        # a pinned bone is not duplicated
        self.assertEqual({t.key for t in mp.follow_targets(bpy.context, pinned_keys={(rig.name, "upper")})}, {(rig.name, "lower")})
        bpy.ops.object.mode_set(mode='OBJECT')
        for obj in bpy.data.objects:
            obj.select_set(obj is cube)
        bpy.context.view_layer.objects.active = cube
        self.assertEqual({t.key for t in mp.follow_targets(bpy.context, pinned_keys=set())}, {(cube.name, "")})
        self.settings.paths_follow_selection = False
        self.assertEqual(mp.follow_targets(bpy.context, pinned_keys=set()), [])
```

**Step 2: Implementation** (add to `motion_paths.py`)
```python
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
```
Run: expected `Ran 5 tests … OK`. **Commit** — `"Ghost Tool paths: follow-selection targets"`.

---

### Task 6: Sampling into the cache

**Objective:** `refresh_paths()` samples every missing (key, frame), restores the playhead, and only samples what is missing.

**Step 1: Failing tests**
```python
    def test_refresh_samples_bone_head_and_restores_playhead(self):
        rig = _rig()
        e = self.settings.motion_paths.add(); e.object_name, e.bone_name = rig.name, "lower"
        self.scene.frame_set(10)
        n = mp.refresh_paths(bpy.context)
        self.assertEqual(n, 7)
        self.assertEqual(self.scene.frame_current, 10)
        self.scene.frame_set(8)
        dg = bpy.context.evaluated_depsgraph_get()
        expect = rig.evaluated_get(dg).matrix_world @ rig.evaluated_get(dg).pose.bones["lower"].head
        self.assertLess((mp._cache[(rig.name, "lower", 8.0)] - expect).length, 1e-5)
        self.scene.frame_set(10)

    def test_refresh_is_incremental(self):
        rig = _rig()
        e = self.settings.motion_paths.add(); e.object_name, e.bone_name = rig.name, "upper"
        self.assertEqual(mp.refresh_paths(bpy.context), 7)
        self.assertEqual(mp.refresh_paths(bpy.context), 0)
        self.scene.frame_set(11)
        self.assertEqual(mp.refresh_paths(bpy.context), 1)   # only frame 14 is new
        self.assertNotIn((rig.name, "upper", 7.0), mp._cache)  # frame 7 left the window

    def test_object_path_uses_origin(self):
        cube = _cube()
        e = self.settings.motion_paths.add(); e.object_name = cube.name
        mp.refresh_paths(bpy.context)
        self.scene.frame_set(13)
        self.assertLess((mp._cache[(cube.name, "", 13.0)] - cube.matrix_world.translation).length, 1e-5)
        self.scene.frame_set(10)
```

**Step 2: Implementation**
```python
def _sample(depsgraph, obj: bpy.types.Object, bone_name: str, anchor: str) -> Vector:
    ev = obj.evaluated_get(depsgraph)
    if bone_name:
        pb = ev.pose.bones[bone_name]
        local = pb.tail if anchor == 'TAIL' else pb.head
        return (ev.matrix_world @ local).copy()
    return ev.matrix_world.translation.copy()


def mark_dirty(key: PathKey) -> None:
    _dirty.add(key)


def mark_dirty_for_id(block) -> None:
    """A depsgraph update on this ID: re-sample the paths that depend on it."""
    if isinstance(block, bpy.types.Object):
        _dirty.update(k for k in _cache_keys() if k[0] == block.name)
    elif isinstance(block, bpy.types.Action):
        for obj in bpy.data.objects:
            ad = obj.animation_data
            if ad and ad.action == block:
                _dirty.update(k for k in _cache_keys() if k[0] == obj.name)


def _cache_keys() -> set[PathKey]:
    return {(o, b) for (o, b, _f) in _cache}


def refresh_paths(context: bpy.types.Context) -> int:
    """Sample what the window needs and the cache lacks. Returns samples taken."""
    scene = context.scene
    settings = scene.ghost_tool
    if not settings.paths_enabled:
        return 0
    targets = all_targets(context)
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
    count = 0
    with scene_sampling(scene):
        for f in sorted(missing):
            scene.frame_set(int(f), subframe=f - int(f))
            depsgraph = context.evaluated_depsgraph_get()
            for t in missing[f]:
                _cache[(t.key[0], t.key[1], f)] = _sample(depsgraph, t.obj, t.key[1], t.anchor)
                count += 1
    debug(f"Motion paths: sampled {count} positions")
    return count
```
Run: expected `Ran 8 tests … OK`. **Commit** — `"Ghost Tool paths: incremental sampling cache"`.

---

### Task 7: Dirty tracking on key edits

**Objective:** Editing a key re-samples only that object's paths.

**Step 1: Failing test**
```python
    def test_key_edit_dirties_only_that_object(self):
        rig = _rig(); cube = _cube()
        a = self.settings.motion_paths.add(); a.object_name, a.bone_name = rig.name, "upper"
        b = self.settings.motion_paths.add(); b.object_name = cube.name
        mp.refresh_paths(bpy.context)
        mp.mark_dirty_for_id(cube.animation_data.action)
        self.assertEqual(mp.refresh_paths(bpy.context), 7)          # cube only
        mp.mark_dirty_for_id(rig)
        self.assertEqual(mp.refresh_paths(bpy.context), 7)          # rig only
```
Run: expected PASS already if Task 6 was done exactly (the helpers exist). If it passes first time, that is fine — keep the test. **Commit** — `"Ghost Tool paths: dirty tracking test"`.

---

### Task 8: Operators — add, remove, clear, toggle, colour

**Objective:** The five operators from the spec.

**Step 1: Failing tests**
```python
    def test_add_selected_pins_without_duplicates(self):
        rig = _rig()
        self.select_bones(rig, "upper", "lower")
        self.assertEqual(bpy.ops.ghost_tool.paths_add_selected(), {'FINISHED'})
        self.assertEqual([(e.object_name, e.bone_name) for e in self.settings.motion_paths],
                         [(rig.name, "upper"), (rig.name, "lower")])
        bpy.ops.ghost_tool.paths_add_selected()
        self.assertEqual(len(self.settings.motion_paths), 2)
        self.assertNotEqual(tuple(self.settings.motion_paths[0].color), tuple(self.settings.motion_paths[1].color))
        bpy.ops.object.mode_set(mode='OBJECT')
        for obj in bpy.data.objects:
            obj.select_set(False)
        bpy.context.view_layer.objects.active = None
        self.assertFalse(bpy.ops.ghost_tool.paths_add_selected.poll())

    def test_toggle_remove_clear(self):
        rig = _rig()
        self.select_bones(rig, "upper", "lower")
        bpy.ops.ghost_tool.paths_add_selected()
        bpy.ops.ghost_tool.paths_toggle_visible(action='ALL_OFF')
        self.assertFalse(any(e.visible for e in self.settings.motion_paths))
        bpy.ops.ghost_tool.paths_toggle_visible(action='ONE', index=1)
        self.assertEqual([e.visible for e in self.settings.motion_paths], [False, True])
        bpy.ops.ghost_tool.paths_toggle_visible(action='ALL_ON')
        self.assertTrue(all(e.visible for e in self.settings.motion_paths))
        bpy.ops.ghost_tool.paths_remove(index=0)
        self.assertEqual([e.bone_name for e in self.settings.motion_paths], ["lower"])
        mp.refresh_paths(bpy.context)
        bpy.ops.ghost_tool.paths_clear()
        self.assertEqual(len(self.settings.motion_paths), 0)
        self.assertEqual(len(mp._cache), 0)
```

**Step 2: Implementation** (add to `motion_paths.py`; also update `register`/`unregister`)
```python
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
        tag_viewport_redraw(context)
        self.report({'INFO'}, f"Pinned {added} motion path(s)")
        return {'FINISHED'}


class GHOST_OT_paths_remove(bpy.types.Operator):
    bl_idname = "ghost_tool.paths_remove"
    bl_label = "Remove Path"
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
        for stale in [c for c in _cache if (c[0], c[1]) == key]:
            del _cache[stale]
        settings.motion_paths_index = min(idx, len(settings.motion_paths) - 1)
        tag_viewport_redraw(context)
        return {'FINISHED'}


class GHOST_OT_paths_clear(bpy.types.Operator):
    bl_idname = "ghost_tool.paths_clear"
    bl_label = "Clear Paths"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.ghost_tool.motion_paths.clear()
        context.scene.ghost_tool.motion_paths_index = -1
        clear_cache()
        tag_viewport_redraw(context)
        return {'FINISHED'}


class GHOST_OT_paths_toggle_visible(bpy.types.Operator):
    bl_idname = "ghost_tool.paths_toggle_visible"
    bl_label = "Toggle Path"
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
        tag_viewport_redraw(context)
        return {'FINISHED'}


class GHOST_OT_paths_set_color(bpy.types.Operator):
    bl_idname = "ghost_tool.paths_set_color"
    bl_label = "Path Colour"
    bl_options = {'REGISTER', 'UNDO'}
    index: bpy.props.IntProperty(default=-1)  # type: ignore[assignment]
    color: bpy.props.FloatVectorProperty(subtype='COLOR', size=3, min=0.0, max=1.0)  # type: ignore[assignment]
    thickness: bpy.props.IntProperty(min=1, max=6, default=2)  # type: ignore[assignment]

    def invoke(self, context, event):
        entry = context.scene.ghost_tool.motion_paths[self.index]
        self.color, self.thickness = tuple(entry.color), entry.thickness
        return context.window_manager.invoke_props_dialog(self, width=220)

    def execute(self, context):
        entry = context.scene.ghost_tool.motion_paths[self.index]
        entry.color, entry.thickness = self.color, self.thickness
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
    for cls in CLASSES:
        bpy.utils.register_class(cls)
    log("Motion paths module registered.")


def unregister() -> None:
    for cls in reversed(CLASSES):
        try:
            bpy.utils.unregister_class(cls)
        except RuntimeError:
            pass
    clear_cache()
```
Run: expected `Ran 11 tests … OK`. **Commit** — `"Ghost Tool paths: operators"`.

---

### Task 9: Draw handler

**Objective:** Draw each visible path as a GPU line strip (Solid / Speed / Fade), active bone 1 px thicker, key dots.

**Step 1: Failing test** (draw cannot run headless; test the geometry builder instead)
```python
    def test_path_segments_builder(self):
        rig = _rig()
        e = self.settings.motion_paths.add(); e.object_name, e.bone_name = rig.name, "lower"
        mp.refresh_paths(bpy.context)
        segs = mp.path_segments(bpy.context, mp.pinned_targets(self.scene)[0], mp.desired_frames(self.settings, self.scene))
        self.assertEqual(len(segs), 6)                       # 7 frames -> 6 segments
        self.assertTrue(all(len(c) == 4 for _p0, _p1, c in segs))
        self.settings.paths_style = 'FADE'
        far = mp.path_segments(bpy.context, mp.pinned_targets(self.scene)[0], mp.desired_frames(self.settings, self.scene))
        self.assertLess(far[0][2][3], far[2][2][3])          # farther from playhead = more transparent

    def test_key_frames_for_target(self):
        rig = _rig()
        e = self.settings.motion_paths.add(); e.object_name, e.bone_name = rig.name, "lower"
        self.assertEqual(mp.key_frames(mp.pinned_targets(self.scene)[0]), [1.0, 10.0, 20.0])

    def test_draw_handler_registered(self):
        self.assertIsNotNone(mp._draw_handler)
```

**Step 2: Implementation** (add to `motion_paths.py`)
```python
import gpu
from gpu_extras.batch import batch_for_shader
from .utils import get_fcurves_from_action

SLOW_RGB = (0.2, 0.4, 1.0)
FAST_RGB = (1.0, 0.3, 0.1)
KEY_DOT_COLOR = (1.0, 1.0, 1.0, 0.95)
_draw_handler = None


def key_frames(target: PathTarget) -> list[float]:
    """Frames with a keyframe on channels that move this target."""
    obj = target.obj
    ad = obj.animation_data
    if not ad or not ad.action:
        return []
    needle = f'pose.bones["{target.key[1]}"]' if target.key[1] else None
    frames: set[float] = set()
    for fc in get_fcurves_from_action(ad.action, obj):
        if needle is None and fc.data_path.startswith("pose.bones"):
            continue
        if needle is not None and needle not in fc.data_path:
            continue
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


def draw_motion_paths() -> None:
    context = bpy.context
    scene = context.scene
    if not hasattr(scene, 'ghost_tool'):
        return
    settings = scene.ghost_tool
    if not settings.is_active or not settings.paths_enabled:
        return
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
```
And in `register()` / `unregister()`:
```python
    global _draw_handler
    _draw_handler = bpy.types.SpaceView3D.draw_handler_add(draw_motion_paths, (), 'WINDOW', 'POST_VIEW')
```
```python
    global _draw_handler
    if _draw_handler is not None:
        bpy.types.SpaceView3D.draw_handler_remove(_draw_handler, 'WINDOW')
        _draw_handler = None
```
Run: expected `Ran 14 tests … OK`. **Commit** — `"Ghost Tool paths: draw handler"`.

---

### Task 10: Live refresh through the pipeline

**Objective:** Paths refresh on frame change, key edits and playback stop, without needing markers or an active object.

**Files:**
- Modify: `ghost_tool/ghost_pipeline.py`

**Step 1: Failing test**
```python
    def test_pipeline_refreshes_paths_on_frame_change(self):
        from ghost_tool import ghost_pipeline as gp
        rig = _rig()
        e = self.settings.motion_paths.add(); e.object_name, e.bone_name = rig.name, "upper"
        bpy.context.view_layer.objects.active = None
        gp.GhostPipeline.get(self.scene)._run_live_update(bpy.context, self.settings, "h")
        self.assertIn((rig.name, "upper", 10.0), mp._cache)
        self.assertTrue(gp._any_live(self.settings))
        self.settings.paths_enabled = False
        self.assertFalse(gp._any_live(self.settings))
```

**Step 2: Implementation**
1. Add near `compute_settings_hash`:
```python
def _any_live(settings) -> bool:
    return bool(settings.live_point_ghosts or settings.live_mesh_ghosts or settings.paths_enabled)
```
2. Replace the four occurrences of
```python
        live_points = settings.live_point_ghosts
        live_mesh = settings.live_mesh_ghosts
        if not live_points and not live_mesh:
            return …
```
(in `update_if_needed`, `_deferred_live_update`, `_on_frame_change_pipeline`, `_on_playback_post`, `_on_depsgraph_update_pipeline`) with `if not _any_live(settings): return …` keeping each function's own return value (`False`, `None`, or bare `return`). Keep later uses of `live_points`/`live_mesh` by re-reading them where they are still needed (`_run_live_update` reads them itself).
3. In `_run_live_update`, before `obj = context.active_object` / `if not obj: return`, insert:
```python
        if settings.paths_enabled:
            try:
                from . import motion_paths
                motion_paths.refresh_paths(context)
            except Exception as exc:
                warn(f"Motion paths refresh error: {exc}")
```
and change the early return so paths still refreshed: move the `obj = context.active_object; if not obj: return` block below the path refresh (it already is, once the block is inserted above it).
4. In `_on_depsgraph_update_pipeline`, inside the `for update in depsgraph.updates:` loop, before the existing `isinstance` check, add:
```python
        if hasattr(update, 'id') and update.id is not None:
            try:
                from . import motion_paths
                motion_paths.mark_dirty_for_id(update.id)
            except Exception:
                pass
```
5. In `compute_settings_hash`, append to the tuple: `settings.paths_enabled, settings.paths_follow_selection, settings.paths_range_mode, settings.paths_before, settings.paths_after, settings.paths_step,`.

Run all suites: `test_ghost_paths.py` → 15 OK; `test_ghost_header_ui.py`, `test_ghost_correctness.py`, `test_ghost_regressions.py` all still OK (regressions has 20, correctness 46, header 16). **Commit** — `"Ghost Tool paths: live refresh through the pipeline"`.

---

### Task 11: Markers on paths

**Objective:** `paths_show_markers` generates ghost markers for exactly the pinned bones.

**Step 1: Failing test**
```python
    def test_markers_on_paths_generates_for_pinned_bones_only(self):
        rig = _rig()
        e = self.settings.motion_paths.add(); e.object_name, e.bone_name = rig.name, "lower"
        self.settings.paths_show_markers = True
        count = mp.sync_markers(bpy.context)
        self.assertGreater(count, 0)
        store = gd.GhostStore.get(self.scene)
        self.assertTrue(all(g.bone_name == "lower" for g in store.get_all()))
        self.settings.paths_show_markers = False
        self.assertEqual(mp.sync_markers(bpy.context), 0)
        self.assertEqual(len(store), 0)
```
(If `GhostStore` has no `get_all`, use the iteration method it exposes — check `ghost_data.GhostStore` and adjust the assertion, not the behaviour.)

**Step 2: Implementation** — look at `ghost_pipeline.GhostPipeline.generate` / `_evaluate_ghosts` and `ghost_data.generate_ghosts_at_keyframes(obj, armature, bones, channels)` (used in `tests/test_ghost_regressions.py:generate`). Add to `motion_paths.py`:
```python
def sync_markers(context) -> int:
    """Markers on paths: ghost markers for the pinned bones, or none."""
    from .ghost_data import GhostStore, generate_ghosts_at_keyframes, LOCATION_CHANNELS
    scene = context.scene
    settings = scene.ghost_tool
    store = GhostStore.get(scene)
    if not settings.paths_show_markers:
        store.clear()
        return 0
    store.clear()
    total = 0
    by_obj: dict[str, list[str]] = {}
    for t in pinned_targets(scene):
        if t.key[1]:
            by_obj.setdefault(t.key[0], []).append(t.key[1])
    for object_name, bones in by_obj.items():
        obj = bpy.data.objects[object_name]
        ghosts = generate_ghosts_at_keyframes(obj, obj, bones, LOCATION_CHANNELS)
        for g in ghosts:
            store.add(g)
        total += len(ghosts)
    tag_viewport_redraw(context)
    return total
```
Wire it: in `ghost_data.py` give `paths_show_markers` an `update=` callback:
```python
def _on_paths_show_markers_changed(self, context):
    try:
        from .motion_paths import sync_markers
        sync_markers(context)
    except Exception as exc:
        warn(f"Motion paths markers: {exc}")
```
Run: expected 16 OK. **Commit** — `"Ghost Tool paths: markers on paths"`.

---

### Task 12: Header strip segment (Dope Sheet + Graph Editor)

**Objective:** `〰 Paths · 🦴 Add · ⌖ Follow · ▾` in both headers.

**Files:**
- Modify: `ghost_tool/ui_panel.py`

**Step 1: Failing test** (in `test_ghost_paths.py`)
```python
    def test_header_strips_appended(self):
        from ghost_tool import ui_panel
        self.assertIn(ui_panel._draw_timeline_header_extension, bpy.types.DOPESHEET_HT_header._dyn_ui_initialize())
        self.assertIn(ui_panel._draw_graph_header_extension, bpy.types.GRAPH_HT_header._dyn_ui_initialize())
        self.assertTrue(hasattr(bpy.types, "GHOST_PT_paths_popover"))
```

**Step 2: Implementation**
1. Add a shared segment function above `_draw_timeline_header_extension`:
```python
def _draw_paths_segment(row, settings) -> None:
    row.separator(factor=0.5)
    row.prop(settings, "paths_enabled", text="Paths", icon='CURVE_PATH', toggle=True)
    row.operator("ghost_tool.paths_add_selected", text="Add", icon='BONE_DATA')
    row.prop(settings, "paths_follow_selection", text="Follow", icon='RESTRICT_SELECT_OFF', toggle=True)
    row.popover(panel="GHOST_PT_paths_popover", text="", icon='DOWNARROW_HLT')
```
2. In `_draw_timeline_header_extension`, right after the line `row.prop(settings, "show_mesh_ghosts", text="", icon=icon_mesh, toggle=True)` add `_draw_paths_segment(row, settings)`.
3. Add the Graph Editor strip after `_draw_timeline_header_extension`:
```python
def _draw_graph_header_extension(self, context: bpy.types.Context) -> None:
    """Ghost toggle plus the motion-path segment in the Graph Editor header."""
    scene = context.scene
    if not hasattr(scene, 'ghost_tool'):
        return
    settings = scene.ghost_tool
    layout = self.layout
    layout.separator_spacer()
    row = layout.row(align=True)
    row.prop(settings, "is_active", text="", icon='GHOST_ENABLED' if settings.is_active else 'GHOST_DISABLED', toggle=True)
    if settings.is_active:
        _draw_paths_segment(row, settings)
```
4. In `register()`, after the Dope Sheet append block, add the same try/except for `bpy.types.GRAPH_HT_header.append(_draw_graph_header_extension)` recording it in `_header_appends`.
5. Add the popover panel class (next to `GHOST_PT_header_menu`) and put it in `CLASSES`:
```python
class GHOST_PT_paths_popover(bpy.types.Panel):
    bl_idname = "GHOST_PT_paths_popover"
    bl_label = "Motion Paths"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'HEADER'
    bl_ui_units_x = 14

    def draw(self, context):
        _draw_motion_paths(self.layout, context)
```
`_draw_motion_paths` is written in Task 13; for this task make it `def _draw_motion_paths(layout, context): layout.label(text="Motion Paths")` so the module imports.

Run: expected 17 OK. **Commit** — `"Ghost Tool paths: header strip in Dope Sheet and Graph Editor"`.

---

### Task 13: Popover content and the Ghost Tool popover section

**Objective:** The UIList popover from the spec, and the "Motion Paths" section in the viewport-header popover.

**Step 1: Failing test**
```python
    def test_paths_section_in_popover_and_uilist(self):
        from ghost_tool import ui_panel
        self.assertIn("paths", [s[0] for s in ui_panel.GHOST_SECTIONS])
        self.assertTrue(hasattr(bpy.types, "GHOST_UL_paths"))
        self.assertIn("motion_paths", ui_panel._HELP_TOPICS)
```

**Step 2: Implementation** (in `ui_panel.py`)
```python
class GHOST_UL_paths(bpy.types.UIList):
    bl_idname = "GHOST_UL_paths"

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        from .motion_paths import entry_is_missing
        row = layout.row(align=True)
        op = row.operator("ghost_tool.paths_toggle_visible", text="", emboss=False,
                          icon='HIDE_OFF' if item.visible else 'HIDE_ON')
        op.action, op.index = 'ONE', index
        swatch = row.operator("ghost_tool.paths_set_color", text="", icon='COLOR', emboss=False)
        swatch.index = index
        missing = entry_is_missing(item)
        sub = row.row(); sub.enabled = not missing
        sub.label(text=item.label + ("  (missing)" if missing else ""))
        rm = row.operator("ghost_tool.paths_remove", text="", icon='X', emboss=False)
        rm.index = index


def _draw_motion_paths(layout, context) -> None:
    settings = context.scene.ghost_tool
    row = layout.row(align=True)
    row.scale_y = 1.2
    row.operator("ghost_tool.paths_add_selected", text="Add Path for Selected", icon='ADD')
    row = layout.row(align=True)
    row.label(text=f"Motion paths · {len(settings.motion_paths)}")
    row.operator("ghost_tool.paths_toggle_visible", text="All on").action = 'ALL_ON'
    row.operator("ghost_tool.paths_toggle_visible", text="All off").action = 'ALL_OFF'
    row.operator("ghost_tool.paths_clear", text="", icon='TRASH')
    layout.template_list("GHOST_UL_paths", "", settings, "motion_paths", settings, "motion_paths_index", rows=4, maxrows=8)
    col = layout.column(align=True)
    col.label(text="Range")
    col.prop(settings, "paths_range_mode", text="")
    if settings.paths_range_mode == 'AROUND_CURSOR':
        row = col.row(align=True)
        row.prop(settings, "paths_before", text="Before")
        row.prop(settings, "paths_after", text="After")
    col.prop(settings, "paths_step", text="Every")
    col = layout.column(align=True)
    col.label(text="Style")
    col.prop(settings, "paths_style", expand=True)
    row = layout.row(align=True)
    row.prop(settings, "paths_show_markers", text="Markers", toggle=True)
    row.prop(settings, "paths_show_key_dots", text="Key dots", toggle=True)
    row.prop(settings, "paths_show_frame_numbers", text="Frame #", toggle=True)
```
Replace the Task 12 placeholder with this. Add to `GHOST_SECTIONS` after the `"onion"` row:
```python
    ("paths", "Motion Paths", 'CURVE_PATH', _draw_motion_paths, "motion_paths", False),
```
Add `GHOST_UL_paths` to `CLASSES`. Add a help topic to `_HELP_TOPICS` in the same shape as the others:
```python
    "motion_paths": (
        "Motion Paths",
        "Pin a path to any bone or object and watch it follow the playhead.",
        "Add pins the selected bones (Pose mode) or objects. Follow adds a grey path for "
        "whatever is selected. Paths sample the bone itself, so they work with markers off; "
        "turn Markers on to drag keys along a path. One range and style apply to all paths.",
    ),
```
Run: expected 18 OK; `smoke_bforartists.py` exit 0. **Commit** — `"Ghost Tool paths: popover and Ghost Tool section"`.

---

### Task 14: Frame numbers (2D overlay)

**Objective:** Optional frame labels along each path.

**Step 1: Test** — keep it to registration:
```python
    def test_frame_number_handler_registered(self):
        self.assertIsNotNone(mp._draw_handler_2d)
```

**Step 2: Implementation** (`motion_paths.py`)
```python
import blf
from bpy_extras import view3d_utils
_draw_handler_2d = None


def draw_frame_numbers() -> None:
    context = bpy.context
    scene = context.scene
    if not hasattr(scene, 'ghost_tool'):
        return
    settings = scene.ghost_tool
    if not (settings.is_active and settings.paths_enabled and settings.paths_show_frame_numbers):
        return
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
```
Register as `POST_PIXEL` next to the 3D handler; remove in `unregister`. Run: 19 OK. **Commit** — `"Ghost Tool paths: frame numbers"`.

---

### Task 15: Performance gate and slow warning

**Objective:** Prove the 500-sample budget and surface slowness in the strip.

**Step 1: Test**
```python
    def test_refresh_budget_500_samples(self):
        import time
        rig = _rig()
        for i in range(10):
            for bone in ("upper", "lower"):
                e = self.settings.motion_paths.add(); e.object_name, e.bone_name = rig.name, bone
                e.bone_name = bone  # duplicates are fine for the budget test
        self.settings.paths_before = self.settings.paths_after = 12
        t0 = time.perf_counter()
        n = mp.refresh_paths(bpy.context)
        dt = (time.perf_counter() - t0) * 1000
        print(f"PATHS_PERF samples={n} ms={dt:.0f}", flush=True)
        self.assertLess(dt, 50.0)
```
(Duplicate entries collapse to 2 keys × 25 frames = 50 samples; make 10 distinct rigs if you want a true 500. Use `_rig(name=f"Rig{i}")` and pin both bones of each — then `n == 500`.)

**Step 2: Implementation** — in `refresh_paths`, time the sampling block and store `_last_refresh_ms`; in `_draw_paths_segment` add:
```python
    from .motion_paths import last_refresh_ms
    if last_refresh_ms() > 200.0:
        row.label(text="", icon='ERROR')
```
with `def last_refresh_ms() -> float: return _last_refresh_ms` in `motion_paths.py` and a tooltip-bearing operator is not needed — the icon's hover text comes from the label; set `text="slow"` if you want words.
Run: 20 OK, printed `PATHS_PERF` line under 50 ms. **Commit** — `"Ghost Tool paths: performance gate"`.

---

### Task 16: Full-suite pass and manual checklist

**Objective:** Nothing else regressed; eyes on the parts headless cannot see.

**Step 1:** Run all four suites + smoke; expected: paths 20 OK, header 16 OK, correctness 46 OK, regressions 20 OK, smoke exit 0. Delete `__pycache__`.

**Step 2:** Build the zip into a temp folder (same recipe as 3.4.1) and install it in Bforartists. Check, and record the answers in the PR/commit message:
- Dope Sheet header shows `Paths · Add · Follow · ▾`; Graph Editor header too.
- Add with two bones selected → two coloured paths; popover lists them; eye toggles hide one.
- Scrub: paths move with the playhead; no stutter at 20 bones.
- Play, stop: paths land on the stop frame.
- Select a prop: pinned paths stay; Follow on → prop gets a grey path.
- Popover scrolls past 8 entries; colour dialog works; Frame # shows numbers.
- Open an old 3.4.1 file: nothing drawn until Paths is turned on.

---

### Task 17: Release 3.5.0 (owner-gated)

**Objective:** Version bump and release artefacts. **Do not commit or push without "Confirm merge update?"** — this task lands on the release branch.

1. `ghost_tool/__init__.py`: `"version": (3, 5, 0)` — description untouched.
2. `releases/`: build `b4_ghost_tool_v3.5.0.zip` byte-identical to `ghost_tool/` (no `__pycache__`), delete `b4_ghost_tool_v3.4.1.zip`, update the row in `releases/VERSIONS.md` (size, sha256 first 12).
3. `README.md`: both Ghost Tool rows → 3.5.0, link to `ghost-v3.5.0`.
4. Show the before→after table, ask **Confirm merge update?**, then: merge `work/ghost-tool-paths` into `toolkit-main`, push to `toolkit main`, `gh release create ghost-v3.5.0 releases/b4_ghost_tool_v3.5.0.zip --target main --title "Ghost Tool 3.5.0"`.
5. Update `G:\LapArt\Projects\Blender Ghost_Tool B4Artists\VERSIONS.md` and the memory note.
