"""Ghost Tool Round F: Bezier handles on motion paths. Run with:
    bforartists --background --factory-startup --python tests/test_ghost_paths_handles.py
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_ghost_paths import C, GhostPaths, K, _cube, _rig, bpy, ghost_tool, mp  # noqa: E402,F401
from test_ghost_paths_folders import _Layout  # noqa: E402


class GhostPathHandles(unittest.TestCase):
    """Uses GhostPaths' scene setup without re-running its tests."""

    setUp = GhostPaths.setUp
    select_bones = GhostPaths.select_bones
    _drop_deferred_timer = GhostPaths._drop_deferred_timer

    @classmethod
    def setUpClass(cls):
        with patch.object(ghost_tool, "_clear_pycache"):
            ghost_tool.register()

    @classmethod
    def tearDownClass(cls):
        ghost_tool.unregister()

    def test_show_handles_setting_and_toggle(self):
        from ghost_tool import ui_panel
        self.assertFalse(self.settings.paths_show_handles)   # off: existing files look as before
        layout = _Layout()
        ui_panel._draw_motion_paths(layout, bpy.context)
        self.assertIn(("prop", "paths_show_handles", "Handles"), [c[:3] for c in layout.calls])
        with patch.object(ghost_tool.ghost_data, "_schedule_path_refresh") as refresh:
            self.settings.paths_show_handles = True
        refresh.assert_called_once()   # turning it on samples the handle points
        self.settings.paths_show_handles = False
        self._drop_deferred_timer()

    # ── F1: handle geometry ──────────────────────────────────────────────

    def _pin(self, obj, bone=""):
        e = self.settings.motion_paths.add()
        e.object_name, e.bone_name = obj.name, bone
        return e

    def _location_curves(self, obj, bone=""):
        path = f'pose.bones["{bone}"].location' if bone else "location"
        return {fc.array_index: fc for fc in ghost_tool.utils.get_fcurves_from_action(obj.animation_data.action, obj)
                if fc.data_path == path}

    def _world_with_key_moved_to_handle(self, obj, bone, frame, side):
        """Independent check: put the key's value on its handle, evaluate the real position at ``frame``."""
        curves = self._location_curves(obj, bone)
        saved = []
        for fc in curves.values():
            key = next(k for k in fc.keyframe_points if abs(k.co.x - frame) < 1e-4)
            saved.append((key, key.co.y, tuple(key.handle_left), tuple(key.handle_right)))
            key.co.y = (key.handle_left if side == 0 else key.handle_right).y
        self.scene.frame_set(int(frame))
        ev = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
        world = (ev.matrix_world @ ev.pose.bones[bone].head) if bone else ev.matrix_world.translation.copy()
        for key, y, left, right in saved:
            key.co.y = y
            key.handle_left, key.handle_right = left, right
        return world

    def test_object_handle_points_follow_the_location_curves(self):
        cube = _cube()   # location X keys 0 at 1 and 4 at 20 (Bezier)
        self._pin(cube)
        self.settings.paths_range_mode = 'SCENE'
        target = mp.pinned_targets(self.scene)[0]
        self.scene.frame_set(20)
        left, right = mp.key_handles(target, 20.0)
        x = self._location_curves(cube)[0]
        key = next(k for k in x.keyframe_points if k.co.x == 20.0)
        self.assertAlmostEqual(left.x, key.handle_left.y, places=5)
        self.assertAlmostEqual(right.x, key.handle_right.y, places=5)
        self.assertAlmostEqual(left.y, cube.location.y, places=5)   # an unkeyed axis keeps its value
        for side, point in ((0, left), (1, right)):
            expect = self._world_with_key_moved_to_handle(cube, "", 20.0, side)
            self.assertLess((point - expect).length, 1e-4)
        self.scene.frame_set(10)
        self._drop_deferred_timer()

    def test_object_handles_under_a_parent_with_delta_location(self):
        # Review 47b90d36: exercise the parent, parent-inverse and delta terms of the object transform.
        from mathutils import Matrix
        cube = _cube()
        bpy.ops.object.empty_add(location=(1.0, 2.0, 0.5))
        parent = bpy.context.object
        parent.rotation_euler = (0.0, 0.3, 0.7)
        cube.parent = parent
        cube.matrix_parent_inverse = Matrix.Translation((0.5, -0.25, 0.0)) @ Matrix.Rotation(0.4, 4, 'X')
        cube.delta_location = (0.0, 0.3, 1.0)
        self._pin(cube)
        target = mp.pinned_targets(self.scene)[0]
        self.scene.frame_set(20)
        left, right = mp.key_handles(target, 20.0)
        for side, point in ((0, left), (1, right)):
            expect = self._world_with_key_moved_to_handle(cube, "", 20.0, side)
            self.assertLess((point - expect).length, 1e-4)
        self.scene.frame_set(10)
        self._drop_deferred_timer()

    def test_one_frame_path_still_draws_dots_and_handles(self):
        # Review 47b90d36: the draw skipped a path with no line segment before its dots and handles.
        cube = _cube()
        e = self._pin(cube)
        e.use_own_range, e.own_range_mode, e.own_start, e.own_end = True, 'CUSTOM', 20, 20
        with patch.object(ghost_tool.ghost_data, "_schedule_path_refresh"):
            self.settings.paths_show_handles = True
        self.settings.paths_show_key_dots = True
        mp.refresh_paths(bpy.context)
        target = mp.pinned_targets(self.scene)[0]
        self.assertEqual(target.frames, (20.0,))
        segs, dots, lines, ends = mp.draw_parts(bpy.context, target)
        self.assertEqual((len(segs), len(dots), len(lines), len(ends)), (0, 1, 4, 2))
        self.assertEqual(lines[0], mp._cache[C(cube.name, "", 20.0)])   # handle lines start at the key dot
        with patch.object(ghost_tool.ghost_data, "_schedule_path_refresh"):
            self.settings.paths_show_handles = False
        self.assertEqual(mp.draw_parts(bpy.context, target)[2:], ([], []))
        self._drop_deferred_timer()

    def test_bone_head_handle_points_match_the_posed_rig(self):
        rig = _rig()
        bpy.ops.object.mode_set(mode='POSE')
        lower = rig.pose.bones["lower"]
        for frame, y in ((1, 0.0), (10, 0.5), (20, 0.8)):   # rising: auto-clamped handles are flat at a peak
            lower.location = (0.2, y, 0.0)
            lower.keyframe_insert("location", frame=frame)
        bpy.ops.object.mode_set(mode='OBJECT')
        self._pin(rig, "lower")
        target = mp.pinned_targets(self.scene)[0]
        self.scene.frame_set(10)
        left, right = mp.key_handles(target, 10.0)
        self.assertGreater((left - right).length, 1e-3)
        for side, point in ((0, left), (1, right)):
            expect = self._world_with_key_moved_to_handle(rig, "lower", 10.0, side)
            self.assertLess((point - expect).length, 1e-4)
        self.scene.frame_set(10)
        self._drop_deferred_timer()

    def test_no_handles_for_tails_vertices_connected_bones_or_unkeyed_frames(self):
        rig = _rig(); cube = _cube()
        tail = self._pin(rig, "lower"); tail.anchor = 'TAIL'
        vertex = self._pin(cube); vertex.vertex_index = 0
        self.scene.frame_set(10)
        for target in mp.pinned_targets(self.scene):
            self.assertIsNone(mp.key_handles(target, 10.0), target.key)
        self.settings.motion_paths.clear()
        self._pin(cube)
        self.assertIsNone(mp.key_handles(mp.pinned_targets(self.scene)[0], 10.0))   # no key at 10
        bpy.context.view_layer.objects.active = rig
        bpy.ops.object.mode_set(mode='EDIT')
        rig.data.edit_bones["lower"].use_connect = True
        bpy.ops.object.mode_set(mode='OBJECT')
        self.settings.motion_paths.clear()
        self._pin(rig, "lower")
        self.assertFalse(mp.handle_eligible(mp.pinned_targets(self.scene)[0]))   # a connected bone ignores location
        self._drop_deferred_timer()

    def test_refresh_samples_handles_only_when_shown(self):
        cube = _cube()
        self._pin(cube)
        self.settings.paths_range_mode = 'SCENE'
        mp.refresh_paths(bpy.context)
        self.assertEqual(mp._handles, {})                       # off: nothing extra sampled
        with patch.object(ghost_tool.ghost_data, "_schedule_path_refresh"):
            self.settings.paths_show_handles = True
        mp.refresh_paths(bpy.context)
        self.assertEqual(set(mp._handles), {C(cube.name, "", 1.0), C(cube.name, "", 20.0)})
        self.assertIsNotNone(mp._handles[C(cube.name, "", 20.0)])
        self.assertFalse(mp.request_missing_samples(bpy.context))
        self.assertEqual(mp.refresh_paths(bpy.context), 0)      # nothing re-sampled
        mp.forget(K(cube.name))
        self.assertEqual(mp._handles, {})
        mp.mark_dirty(K(cube.name))
        mp.refresh_paths(bpy.context)
        self.assertEqual(len(mp._handles), 2)
        with patch.object(ghost_tool.ghost_data, "_schedule_path_refresh"):
            self.settings.paths_show_handles = False
        self.scene.frame_set(10)
        self._drop_deferred_timer()


    # ── F2: dragging a handle ────────────────────────────────────────────

    def _x_curve(self, cube):
        return self._location_curves(cube)[0]

    def test_set_handle_values_keeps_time(self):
        from ghost_tool.fcurve_utils import set_handle_values
        cube = _cube()
        fc = self._x_curve(cube)
        key = next(k for k in fc.keyframe_points if k.co.x == 20.0)
        co, left, right_x = tuple(key.co), tuple(key.handle_left), key.handle_right.x
        self.assertTrue(set_handle_values(fc, 20.0, 'RIGHT', 7.5))
        self.assertEqual((key.handle_right.x, key.handle_right.y), (right_x, 7.5))
        self.assertEqual(key.handle_right_type, 'FREE')
        self.assertEqual((tuple(key.co), tuple(key.handle_left)), (co, left))   # key and other handle untouched
        self.assertFalse(set_handle_values(fc, 13.0, 'LEFT', 1.0))           # no key at 13
        with self.assertRaises(ValueError):
            set_handle_values(fc, 20.0, 'UP', 1.0)

    def test_aligned_moves_opposite_handle(self):
        from ghost_tool.fcurve_utils import set_handle_values
        cube = _cube()
        fc = self._x_curve(cube)
        key = next(k for k in fc.keyframe_points if k.co.x == 20.0)
        left_x = key.handle_left.x
        set_handle_values(fc, 20.0, 'RIGHT', key.co.y + 2.0, aligned=True)
        self.assertEqual((key.handle_left_type, key.handle_right_type), ('ALIGNED', 'ALIGNED'))
        self.assertAlmostEqual(key.handle_left.x, left_x, places=5)          # its time stays
        slope_right = (key.handle_right.y - key.co.y) / (key.handle_right.x - key.co.x)
        slope_left = (key.handle_left.y - key.co.y) / (key.handle_left.x - key.co.x)
        self.assertAlmostEqual(slope_left, slope_right, places=5)            # collinear through the key

    def test_handle_drag_solve_moves_the_handle_end_not_the_key(self):
        from mathutils import Matrix, Vector
        from ghost_tool.fcurve_utils import set_handle_values
        from ghost_tool.path_handle_drag import solve_handle_values
        cube = _cube()
        bpy.ops.object.empty_add(location=(1.0, 2.0, 0.5))
        parent = bpy.context.object
        parent.rotation_euler = (0.0, 0.3, 0.7)
        cube.parent = parent
        cube.matrix_parent_inverse = Matrix.Translation((0.5, -0.25, 0.0))
        cube.delta_location = (0.0, 0.3, 1.0)
        self._pin(cube)
        target = mp.pinned_targets(self.scene)[0]
        self.scene.frame_set(20)
        transform = mp.handle_transform(target)
        _path, to_world, offset, _current = transform
        fc = self._x_curve(cube)
        key = next(k for k in fc.keyframe_points if k.co.x == 20.0)
        co = tuple(key.co)
        _left, right = mp.key_handles(target, 20.0)
        wanted = to_world @ (to_world.inverted() @ right - offset + Vector((0.5, 0.0, 0.0)) + offset)
        values = solve_handle_values(transform, wanted, [0])
        self.assertEqual(set(values), {0})
        set_handle_values(fc, 20.0, 'RIGHT', values[0])
        self.assertLess((mp.key_handles(target, 20.0)[1] - wanted).length, 1e-4)
        self.assertEqual(tuple(key.co), co)   # the key's time and value stay
        self.scene.frame_set(10)
        self._drop_deferred_timer()

    def test_handle_under_cursor_picks_the_nearest_end_within_8_px(self):
        from types import SimpleNamespace
        from mathutils import Matrix, Vector
        from ghost_tool.path_handle_drag import handle_under_cursor
        cube = _cube()
        self._pin(cube)
        self.settings.paths_range_mode = 'SCENE'
        with patch.object(ghost_tool.ghost_data, "_schedule_path_refresh"):
            self.settings.paths_show_handles = True
        mp.refresh_paths(bpy.context)
        target = mp.pinned_targets(self.scene)[0]
        # Identity view: world (x, y) lands on pixel (500 + 500x, 500 + 500y) in a 1000 px region.
        mp._handles[C(cube.name, "", 20.0)] = (Vector((-0.1, 0.0, 0.0)), Vector((0.1, 0.0, 0.0)))
        mp._handles[C(cube.name, "", 1.0)] = None
        region = SimpleNamespace(width=1000, height=1000)
        rv3d = SimpleNamespace(perspective_matrix=Matrix.Identity(4))
        pick = handle_under_cursor(bpy.context, region, rv3d, 553.0, 500.0)
        self.assertEqual((pick[0].key, pick[1], pick[2]), (target.key, 20.0, 'RIGHT'))
        self.assertEqual(handle_under_cursor(bpy.context, region, rv3d, 445.0, 503.0)[2], 'LEFT')
        self.assertIsNone(handle_under_cursor(bpy.context, region, rv3d, 560.0, 500.0))   # 10 px away
        with patch.object(ghost_tool.ghost_data, "_schedule_path_refresh"):
            self.settings.paths_show_handles = False
        self._drop_deferred_timer()

    def test_free_after_aligned_unlinks_both_handles(self):
        # Review bf07774d: switching back to Free left the opposite handle Aligned.
        from ghost_tool.fcurve_utils import set_handle_values
        cube = _cube()
        fc = self._x_curve(cube)
        key = next(k for k in fc.keyframe_points if k.co.x == 20.0)
        set_handle_values(fc, 20.0, 'RIGHT', key.co.y + 2.0, aligned=True)
        left = tuple(key.handle_left)
        set_handle_values(fc, 20.0, 'RIGHT', key.co.y + 1.0)
        self.assertEqual((key.handle_left_type, key.handle_right_type), ('FREE', 'FREE'))
        self.assertEqual(tuple(key.handle_left), left)   # the other handle keeps its position

    def _drag_setup(self, side='RIGHT'):
        from mathutils import Vector
        from ghost_tool.path_handle_drag import HandleDrag
        cube = _cube()
        self._pin(cube)
        self.settings.paths_range_mode = 'SCENE'
        with patch.object(ghost_tool.ghost_data, "_schedule_path_refresh"):
            self.settings.paths_show_handles = True
        mp.refresh_paths(bpy.context)
        target = mp.pinned_targets(self.scene)[0]
        drag = HandleDrag(self.scene, target, 20.0, side)
        self.assertTrue(drag.ok)
        self.assertEqual(self.scene.frame_current, 10)   # reading the transform at 20 restored the playhead
        return cube, target, drag, Vector

    def test_handle_drag_moves_toggles_and_cancels(self):
        # Review bf07774d: drive the drag itself (move, Alt, cancel), not only its helpers.
        from ghost_tool.fcurve_utils import snapshot_fcurve
        cube, target, drag, Vector = self._drag_setup()
        fc = self._x_curve(cube)
        before = snapshot_fcurve(fc)
        wanted = drag.original_handles[1] + Vector((0.5, 0.0, 0.0))
        drag.move_to(wanted)
        self.assertLess((mp._handles[C(cube.name, "", 20.0)][1] - wanted).length, 1e-4)   # drawn end follows
        key = next(k for k in fc.keyframe_points if k.co.x == 20.0)
        self.assertEqual(key.handle_right_type, 'FREE')
        self.assertTrue(drag.toggle_aligned())                                # Alt: the pair turns Aligned
        self.assertEqual((key.handle_left_type, key.handle_right_type), ('ALIGNED', 'ALIGNED'))
        self.assertFalse(drag.toggle_aligned())                               # Alt again: Free
        self.assertEqual((key.handle_left_type, key.handle_right_type), ('FREE', 'FREE'))
        drag.cancel()                                                         # Esc / right-click
        self.assertEqual(snapshot_fcurve(fc), before)
        self.assertEqual(mp._handles[C(cube.name, "", 20.0)], drag.original_handles)
        with patch.object(ghost_tool.ghost_data, "_schedule_path_refresh"):
            self.settings.paths_show_handles = False
        self._drop_deferred_timer()

    def test_handle_drag_confirm_resamples_paths_that_follow_the_object(self):
        # Review bf07774d: confirming re-sampled only the dragged path; a pinned child kept old positions.
        cube, target, drag, Vector = self._drag_setup('LEFT')   # the left handle of key 20 shapes frames 1-20
        bpy.ops.object.empty_add(location=(0.0, 1.0, 0.0))
        child = bpy.context.object
        child.parent = cube
        self._pin(child)
        mp.refresh_paths(bpy.context)
        old_child = mp._cache[C(child.name, "", 15.0)].copy()
        drag.move_to(drag.original_handles[0] + Vector((-3.0, 0.0, 0.0)))   # bends the curve before frame 20
        drag.confirm(bpy.context)
        self.scene.frame_set(15)
        fresh = child.matrix_world.translation.copy()
        self.scene.frame_set(10)
        self.assertGreater((fresh - old_child).length, 1e-3)                  # the drag moved the child at 15
        self.assertLess((mp._cache[C(child.name, "", 15.0)] - fresh).length, 1e-5)
        self.scene.frame_set(15)
        cube_fresh = cube.matrix_world.translation.copy()
        self.scene.frame_set(10)
        self.assertLess((mp._cache[C(cube.name, "", 15.0)] - cube_fresh).length, 1e-5)   # and the dragged path
        from ghost_tool.path_handle_drag import GHOST_OT_path_handle_drag
        self.assertIn('UNDO', GHOST_OT_path_handle_drag.bl_options)   # one undo step on confirm
        with patch.object(ghost_tool.ghost_data, "_schedule_path_refresh"):
            self.settings.paths_show_handles = False
        self._drop_deferred_timer()

    def test_handle_drag_registered_ahead_of_the_marker_drag(self):
        self.assertEqual(bpy.ops.ghost_tool.path_handle_drag.get_rna_type().identifier.lower(),
                         "ghost_tool_ot_path_handle_drag")
        kc = bpy.context.window_manager.keyconfigs.addon
        if kc is None:
            self.skipTest("no add-on keyconfig in background mode")
        for name in ("Pose", "Object Mode"):
            ids = [kmi.idname for kmi in kc.keymaps[name].keymap_items]
            self.assertIn("ghost_tool.path_handle_drag", ids)
            self.assertLess(ids.index("ghost_tool.path_handle_drag"), ids.index("ghost_tool.drag_ghost"))


if __name__ == "__main__":
    result = unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(GhostPathHandles))
    print("GHOST_PATH_HANDLES_RESULT: " + ("PASS" if result.wasSuccessful() else "FAIL"), flush=True)
    if not result.wasSuccessful():
        sys.exit(1)
