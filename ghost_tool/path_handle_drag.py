"""path_handle_drag.py — drag the Bezier handles that motion paths show at key dots (design §8 decision 14).

A drag changes handle values only: the key's time and value stay, and so does each handle's time. Shift+G
or a click within 8 px of a handle end starts it; anywhere else the event passes through to the marker
drag and to selection, so a handle end wins when both are in reach.
"""

from __future__ import annotations

from typing import Optional

import bpy
from bpy_extras import view3d_utils
from mathutils import Vector

from . import motion_paths as mp
from .fcurve_utils import restore_fcurve, set_handle_values, snapshot_fcurve
from .utils import get_fcurves_from_action, scene_sampling, tag_viewport_redraw

PICK_RADIUS_PX = 8.0
_addon_keymaps: list = []


def handle_under_cursor(context, region, rv3d, x: float, y: float,
                        radius: float = PICK_RADIUS_PX) -> Optional[tuple[mp.PathTarget, float, str]]:
    """(target, key frame, 'LEFT' | 'RIGHT') of the drawn handle end nearest the cursor within ``radius``."""
    best, best_d = None, radius
    for target in mp.pinned_targets(context.scene):
        for frame in mp._handle_frames(target):
            handle = mp._handles.get((*target.key, frame))
            if handle is None:
                continue
            for side, point in (('LEFT', handle[0]), ('RIGHT', handle[1])):
                screen = view3d_utils.location_3d_to_region_2d(region, rv3d, point)
                if screen is None:
                    continue
                d = (screen - Vector((x, y))).length
                if d <= best_d:
                    best, best_d = (target, frame, side), d
    return best


def keyed_curves(target: mp.PathTarget, data_path: str, frame: float) -> dict[int, bpy.types.FCurve]:
    """The location curves (by axis) that have a key at ``frame``: the only ones a handle drag can change."""
    obj = target.obj
    action = obj.animation_data.action if obj.animation_data else None
    curves = {}
    for fc in get_fcurves_from_action(action, obj) if action else ():
        if fc.data_path == data_path and any(abs(k.co.x - frame) < 1e-4 for k in fc.keyframe_points):
            curves[fc.array_index] = fc
    return curves


def solve_handle_values(transform, world_point: Vector, axes) -> dict[int, float]:
    """Channel values for the keyed ``axes`` that put a handle end at ``world_point`` (the inverse of the
    map key_handles uses). Unkeyed axes cannot move, so the end moves along the keyed axes only."""
    _data_path, to_world, offset, _current = transform
    try:
        local = to_world.inverted() @ world_point - offset
    except ValueError:   # a zero-scale parent has no inverse
        return {}
    return {axis: local[axis] for axis in axes}


class HandleDrag:
    """One handle drag without the modal plumbing, so tests can drive it.

    The transform is read at the key's frame (not the playhead's), the curves keyed there are snapshot,
    and every move writes handle values only."""

    def __init__(self, scene, target: mp.PathTarget, frame: float, side: str):
        self.target, self.frame, self.side = target, frame, side
        self.aligned = False
        self.cache_key = (*target.key, frame)
        self.original_handles = mp._handles.get(self.cache_key)
        with scene_sampling(scene):
            scene.frame_set(int(frame), subframe=frame - int(frame))
            self.transform = mp.handle_transform(target, bpy.context.evaluated_depsgraph_get())
        self.curves = keyed_curves(target, self.transform[0], frame) if self.transform else {}
        self.ok = bool(self.transform and self.curves and self.original_handles)
        if not self.ok:
            return
        self.snapshots = {axis: snapshot_fcurve(fc) for axis, fc in self.curves.items()}
        self.depth = self.original_handles[0 if side == 'LEFT' else 1].copy()
        # An unkeyed axis keeps the value the drawn handle had (its curve's value at the key frame).
        unkeyed = solve_handle_values(self.transform, self.original_handles[0], range(3))
        self._unkeyed = [unkeyed.get(axis, 0.0) for axis in range(3)]
        self._last = None

    def move_to(self, world_point: Vector) -> None:
        self._last = world_point.copy()
        for axis, value in solve_handle_values(self.transform, world_point, self.curves).items():
            set_handle_values(self.curves[axis], self.frame, self.side, value, aligned=self.aligned)
        mp._handles[self.cache_key] = self.handle_points()

    def toggle_aligned(self) -> bool:
        self.aligned = not self.aligned
        # Re-apply at the end's current place, also before any mouse move, so the mode shown is the one saved.
        self.move_to(self._last if self._last is not None else self.depth)
        return self.aligned

    def handle_points(self) -> tuple[Vector, Vector]:
        _data_path, to_world, offset, _current = self.transform
        left, right = [], []
        for axis in range(3):
            fc = self.curves.get(axis)
            key = next((k for k in fc.keyframe_points if abs(k.co.x - self.frame) < 1e-4), None) if fc else None
            left.append(key.handle_left.y if key else self._unkeyed[axis])
            right.append(key.handle_right.y if key else self._unkeyed[axis])
        return to_world @ (Vector(left) + offset), to_world @ (Vector(right) + offset)

    def cancel(self) -> None:
        for axis, fc in self.curves.items():
            restore_fcurve(fc, self.snapshots[axis])
        mp._handles[self.cache_key] = self.original_handles

    def confirm(self, context) -> None:
        # The curve between the keys changed: re-sample this path and every path that follows the object
        # (a pinned child, a constraint user), as a key edit in the Graph Editor would.
        mp.mark_dirty_for_id(self.target.obj)
        mp.refresh_paths(context)


def _status(drag: HandleDrag) -> str:
    return (f"Drag handle · Aligned: {'on' if drag.aligned else 'off'} (Alt toggles) · "
            "Click: confirm · Esc/Right-click: cancel")


class GHOST_OT_path_handle_drag(bpy.types.Operator):
    """Drag a Bezier handle shown on a motion path: the handle's value changes, its time and the key stay.
    Alt toggles Aligned (the opposite handle turns with it); Esc or right-click restores."""

    bl_idname = "ghost_tool.path_handle_drag"
    bl_label = "Drag Path Handle"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        settings = getattr(context.scene, "ghost_tool", None)
        return (settings is not None and settings.is_active and settings.paths_enabled
                and settings.paths_show_handles and context.area is not None and context.area.type == 'VIEW_3D')

    def invoke(self, context, event):
        pick = handle_under_cursor(context, context.region, context.region_data,
                                   event.mouse_region_x, event.mouse_region_y)
        if pick is None:
            return {'PASS_THROUGH'}   # the marker drag or selection gets the event
        self._drag = HandleDrag(context.scene, *pick)
        if not self._drag.ok:
            return {'PASS_THROUGH'}
        self._via_click = event.type == 'LEFTMOUSE'
        context.window_manager.modal_handler_add(self)
        context.workspace.status_text_set(_status(self._drag))
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        drag = self._drag
        if event.type == 'MOUSEMOVE':
            drag.move_to(view3d_utils.region_2d_to_location_3d(
                context.region, context.region_data, (event.mouse_region_x, event.mouse_region_y), drag.depth))
            tag_viewport_redraw(context)
        elif event.type in {'LEFT_ALT', 'RIGHT_ALT'} and event.value == 'PRESS':
            drag.toggle_aligned()
            context.workspace.status_text_set(_status(drag))
            tag_viewport_redraw(context)
        elif event.type == 'LEFTMOUSE' and event.value == ('RELEASE' if self._via_click else 'PRESS'):
            drag.confirm(context)
            self._finish(context)
            return {'FINISHED'}
        elif event.type in {'RIGHTMOUSE', 'ESC'} and event.value == 'PRESS':
            drag.cancel()
            self._finish(context)
            return {'CANCELLED'}
        return {'RUNNING_MODAL'}

    def _finish(self, context):
        context.workspace.status_text_set(None)
        tag_viewport_redraw(context)


CLASSES: tuple[type, ...] = (GHOST_OT_path_handle_drag,)


def register() -> None:
    for cls in CLASSES:
        bpy.utils.register_class(cls)
    kc = bpy.context.window_manager.keyconfigs.addon
    if kc is None:
        return
    # Registered before preferences adds Shift+G for the marker drag, so this item is tried first and
    # passes the event through when no handle end is within reach.
    for keymap in ('Pose', 'Object Mode'):
        km = kc.keymaps.new(name=keymap, space_type='VIEW_3D')
        for kwargs in ({"type": 'G', "value": 'PRESS', "shift": True}, {"type": 'LEFTMOUSE', "value": 'PRESS'}):
            _addon_keymaps.append((km, km.keymap_items.new(GHOST_OT_path_handle_drag.bl_idname, **kwargs)))


def unregister() -> None:
    for km, kmi in _addon_keymaps:
        try:
            km.keymap_items.remove(kmi)
        except (ReferenceError, RuntimeError):
            pass
    _addon_keymaps.clear()
    for cls in reversed(CLASSES):
        try:
            bpy.utils.unregister_class(cls)
        except RuntimeError:
            pass
