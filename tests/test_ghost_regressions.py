"""Ghost Tool regression checks in Bforartists, without touching user scenes.
Run: bforartists --background --factory-startup --python-exit-code 1 --python tests/test_ghost_regressions.py
"""
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import bpy
from mathutils import Vector, Matrix
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import ghost_tool
from ghost_tool import ghost_data as gd, ghost_pipeline as gp, fcurve_utils as fc, viewport_draw as vd

def make_rig(count=12):
    arm = bpy.data.armatures.new('GhostRegressionRig')
    obj = bpy.data.objects.new('GhostRegressionRig', arm)
    bpy.context.scene.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    for i in range(count):
        b = arm.edit_bones.new(f'Bone{i}')
        b.head, b.tail = (i, 0, 0), (i, 0, 1)
    bpy.ops.object.mode_set(mode='OBJECT')
    for i, b in enumerate(obj.pose.bones):
        for frame in (1, 21):
            b.location = (frame / 10, i / 10, frame / 20)
            b.keyframe_insert('location', frame=frame)
    return obj

class GhostRegression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with patch.object(ghost_tool, '_clear_pycache'):
            ghost_tool.register()
        cls.obj = make_rig()
        cls.bones = [b.name for b in cls.obj.pose.bones]

    @classmethod
    def tearDownClass(cls):
        ghost_tool.unregister()

    def setUp(self):
        self.scene = bpy.context.scene
        self.settings = self.scene.ghost_tool
        self.settings.is_active = False
        self.settings.live_point_ghosts = False
        self.settings.live_mesh_ghosts = False
        self.settings.ghost_mode = 'FRAME_STEP'
        self.settings.ghost_range_mode = 'CUSTOM'
        self.settings.custom_range_start = 2
        self.settings.custom_range_end = 5
        self.settings.frame_step = 1
        gd.GhostStore.get(self.scene).clear()
        fc.invalidate_keyframe_cache()
        self.scene.frame_set(7, subframe=0.25)

    def generate(self, mode):
        args = (self.obj, self.obj, self.bones, gd.LOCATION_CHANNELS)
        if mode == 'step':
            return gd.generate_ghosts_frame_step(*args, [2, 4, 6, 8])
        if mode == 'keys':
            return gd.generate_ghosts_at_keyframes(*args)
        return gd.generate_ghosts(*args, 2)

    def test_clear_level_invalidates_range_and_version(self):
        store = gd.GhostStore()
        store.add(gd.Ghost(frame=1, generation_level=1))
        store.add(gd.Ghost(frame=20, generation_level=2))
        self.assertEqual(store.frame_range, (1, 20))
        version = store.version
        self.assertEqual(store.clear_level(2), 1)
        self.assertGreater(store.version, version)
        self.assertEqual(store.frame_range, (1, 1))

    def test_all_generators_restore_subframe(self):
        for mode in ('step', 'keys', 'subdivision'):
            with self.subTest(mode=mode):
                self.scene.frame_set(7, subframe=0.25)
                self.assertTrue(self.generate(mode))
                self.assertAlmostEqual(self.scene.frame_current_final, 7.25)

    def test_sampling_once_per_distinct_frame(self):
        visits = []
        def record(scene, depsgraph=None):
            visits.append(scene.frame_current_final)
        bpy.app.handlers.frame_change_post.append(record)
        try:
            ghosts = self.generate('step')
        finally:
            bpy.app.handlers.frame_change_post.remove(record)
        self.assertEqual(len(ghosts), 12 * 3 * 4)
        self.assertLessEqual(len(visits), 5, visits)
        for g in ghosts:
            self.scene.frame_set(int(g.frame))
            expected = self.obj.matrix_world @ self.obj.pose.bones[g.bone_name].head
            self.assertLess((g.world_position - expected).length, 1e-5)

    def test_generation_failure_restores_subframe(self):
        original = gd._get_world_position_cached
        def fail_after_seek(*args, **kwargs):
            original(*args, **kwargs)
            raise RuntimeError('injected sampling failure')
        for mode in ('step', 'keys', 'subdivision'):
            with self.subTest(mode=mode):
                self.scene.frame_set(7, subframe=0.25)
                with patch.object(gd, '_get_world_position_cached', side_effect=fail_after_seek):
                    with self.assertRaises(RuntimeError):
                        self.generate(mode)
                self.assertAlmostEqual(self.scene.frame_current_final, 7.25)

    def test_pipeline_preserves_previous_ghosts_on_failure(self):
        store = gd.GhostStore.get(self.scene)
        pipeline = gp.GhostPipeline.get(self.scene)
        for method in (pipeline.generate_manual, pipeline.generate_manual_with_preview):
            with self.subTest(method=method.__name__):
                old = gd.Ghost(frame=99)
                store.replace_all([old])
                with patch.object(pipeline, '_evaluate_ghosts', side_effect=RuntimeError('failure')):
                    with self.assertRaises(RuntimeError):
                        method(bpy.context, self.obj, self.obj, self.bones, gd.LOCATION_CHANNELS, 1)
                self.assertEqual(store.all_ghosts, [old])
                self.assertFalse(gp._BAKE_IN_PROGRESS)
                self.assertIsNone(gp._staging_store)

    def test_generate_append_preserves_existing(self):
        pipeline = gp.GhostPipeline.get(self.scene)
        store = gd.GhostStore.get(self.scene)
        for method in (pipeline.generate_manual, pipeline.generate_manual_with_preview):
            old, new = gd.Ghost(frame=99), gd.Ghost(frame=2)
            store.replace_all([old])
            with patch.object(pipeline, '_evaluate_ghosts', return_value=[new]):
                method(bpy.context, self.obj, self.obj, self.bones, gd.LOCATION_CHANNELS, 1, clear_existing=False)
            self.assertEqual(store.all_ghosts, [old, new])

    def test_sampling_does_not_schedule_live_regeneration(self):
        self.settings.is_active = True
        self.settings.live_point_ghosts = True
        with patch.object(gp, '_schedule_deferred_update') as schedule:
            self.generate('step')
        self.assertEqual(schedule.call_count, 0)

    def test_draw_guard_still_rejects_sampling(self):
        with patch.object(gd, '_IN_DRAW_HANDLER', True):
            with self.assertRaises(RuntimeError):
                self.generate('step')

    def test_same_size_key_reorder_refreshes_cache(self):
        curve = fc.resolve_fcurve(self.obj, self.bones[0], 'location.x')
        points = curve.keyframe_points
        old = [(p.co.copy(), p.handle_left.copy(), p.handle_right.copy()) for p in points]
        try:
            fc._get_sorted_keyframes(curve)
            points[0].co.x = 30
            actual = [p.co.x for p in fc._get_sorted_keyframes(curve)]
            self.assertEqual(actual, sorted(actual))
        finally:
            for p, (co, left, right) in zip(points, old):
                p.co, p.handle_left, p.handle_right = co, left, right
            curve.update()
            fc.invalidate_keyframe_cache()

    def test_unregister_removes_pending_timers(self):
        gp._schedule_deferred_update()
        gp._schedule_forced_mesh_regen()
        try:
            gp.unregister()
            self.assertFalse(bpy.app.timers.is_registered(gp._deferred_live_update))
            self.assertFalse(bpy.app.timers.is_registered(gp._forced_mesh_regen_callback))
        finally:
            for callback in (gp._deferred_live_update, gp._forced_mesh_regen_callback):
                if bpy.app.timers.is_registered(callback):
                    bpy.app.timers.unregister(callback)
            gp.register()

    def test_range_callbacks_keep_bounds_ordered(self):
        self.settings.custom_range_start = 30
        self.assertEqual(self.settings.custom_range_end, 31)
        self.settings.custom_range_end = 10
        self.assertEqual(self.settings.custom_range_start, 9)

    def test_marker_cache_invalidates_render_inputs(self):
        store = gd.GhostStore.get(self.scene)
        ghosts = self.generate('step')
        store.replace_all(ghosts)
        right, up = Vector((1, 0, 0)), Vector((0, 1, 0))
        radius, frame = 0.05, 7
        def get():
            return vd._get_marker_batches(None, store, ghosts, self.settings,
                radius, right, up, frame, store.frame_range)
        # Inspect CPU geometry uploaded to the GPU; no GPU context in background.
        def batch(shader, mode, data, indices):
            return (mode, tuple(data['pos']), tuple(indices))
        with patch.object(vd, 'batch_for_shader', side_effect=batch) as build:
            for mode in ('LEVEL', 'TIME', 'FADE', 'RAINBOW', 'KEY_INBETWEEN'):
                self.settings.ghost_color_mode = mode
                vd._batch_cache.clear()
                first = get()
                self.assertTrue(first)
                self.assertEqual(sum(len(b[0][1]) for b in first), len(ghosts) * vd.SPHERE_SEGMENTS)
                build.reset_mock()
                self.assertIs(first, get())
                self.assertEqual(build.call_count, 0)
                ghosts[0].world_position.x += 1
                changed = get()
                self.assertNotEqual(first, changed)
                self.assertGreater(build.call_count, 0)
                right, up = up, right
                self.assertNotEqual(changed, get())
            before = get()
            self.settings.ghost_key_color = (0.1, 0.2, 0.3)
            ghosts[0].generation_level = 0
            self.assertNotEqual(before, get())
            before = get()
            radius *= 2
            self.assertNotEqual(before, get())
            before = get()
            frame += 4
            self.assertNotEqual(before, get())
        vd._batch_cache.clear()

    def test_mesh_sampling_restores_frame_and_preserves_geometry(self):
        from ghost_tool import mesh_ghosts as mg
        bpy.ops.mesh.primitive_cube_add()
        cube = bpy.context.object
        bpy.context.view_layer.objects.active = cube
        for f, x in ((1, 0), (11, 10)):
            cube.location.x = x
            cube.keyframe_insert('location', frame=f)
        self.scene.frame_set(7, subframe=0.25)
        try:
            count = mg.generate_mesh_ghosts(bpy.context, cube, [2.5, 8.5])
            self.assertEqual(count, 2)
            self.assertAlmostEqual(self.scene.frame_current_final, 7.25)
            coll = bpy.data.collections[mg.GHOST_MESH_COLLECTION]
            for obj in coll.objects:
                frame = obj[mg.GHOST_TOOL_FRAME_KEY]
                self.scene.frame_set(int(frame), subframe=frame % 1)
                self.assertLess((obj.matrix_world.translation - cube.matrix_world.translation).length, 1e-5)
                self.assertTrue(mg._same_mesh_topology(cube.data, obj.data))
            self.scene.frame_set(7, subframe=0.25)
            with patch.object(mg, '_compute_desired_mesh_frames_from_settings', return_value={2.5, 8.5}):
                self.assertTrue(mg.update_mesh_ghosts_incremental(bpy.context))
            self.assertAlmostEqual(self.scene.frame_current_final, 7.25)
            def fail(*args, **kwargs):
                self.scene.frame_set(3)
                raise RuntimeError('mesh conversion failure')
            with patch.object(mg, '_evaluate_and_create_ghost_mesh', side_effect=fail):
                with self.assertRaises(RuntimeError):
                    mg.generate_mesh_ghosts(bpy.context, cube, [2, 8])
            self.assertAlmostEqual(self.scene.frame_current_final, 7.25)
        finally:
            mg.clear_mesh_ghosts(bpy.context)
            bpy.context.view_layer.objects.active = self.obj

    def test_equal_vertex_counts_do_not_hide_topology_changes(self):
        from ghost_tool import mesh_ghosts as mg
        a, b = bpy.data.meshes.new('TopologyA'), bpy.data.meshes.new('TopologyB')
        try:
            vertices = [(0,0,0), (1,0,0), (0,1,0), (1,1,0)]
            a.from_pydata(vertices, [], [(0,1,2), (1,3,2)])
            b.from_pydata(vertices, [], [(0,1,3), (0,3,2)])
            self.assertFalse(mg._same_mesh_topology(a, b))
        finally:
            bpy.data.meshes.remove(a)
            bpy.data.meshes.remove(b)

    def test_cancel_restores_all_dragged_ghosts(self):
        from ghost_tool.modal_operator import GhostDragOperator
        primary, neighbor, other = (gd.Ghost(frame=5, local_value=10) for _ in range(3))
        state = SimpleNamespace(_active_ghost=primary, _original_position=Vector((1,2,3)),
            _original_local_value=1, _falloff_neighbors=[(neighbor, 2, 0.5)],
            _multi_drag_ghosts=[(other, 3, Vector((3,2,1)))],
            _editing_mode='RESHAPE', _undo_snapshots={}, _affected_fcurves={},
            _cleanup=lambda: None, report=lambda *args: None)
        GhostDragOperator._cancel_drag(state, bpy.context)
        self.assertEqual([primary.local_value, neighbor.local_value, other.local_value], [1,2,3])

    def test_live_timers_defer_during_drag(self):
        from ghost_tool.session_state import SessionState
        self.settings.is_active = True
        self.settings.live_point_ghosts = True
        self.settings.show_mesh_ghosts = True
        state = SessionState.get(self.scene)
        state.drag_active = True
        pipeline = gp.GhostPipeline.get(self.scene)
        try:
            with patch.object(pipeline, '_run_live_update') as run:
                self.assertEqual(gp._deferred_live_update(), 0.05)
                self.assertFalse(pipeline.update_if_needed(bpy.context))
                self.assertEqual(run.call_count, 0)
            self.assertEqual(gp._forced_mesh_regen_callback(), 0.05)
        finally:
            state.drag_active = False

    def test_refresh_api_resamples_external_edits(self):
        from ghost_tool import api
        ghosts = self.generate('step')
        gd.GhostStore.get(self.scene).replace_all(ghosts)
        curve = fc.resolve_fcurve(self.obj, self.bones[0], 'location.x')
        snapshot = fc.snapshot_fcurve(curve)
        try:
            self.assertEqual(api.refresh_ghosts(self.obj.name), len(ghosts))
            before = ghosts[0].world_position.copy()
            for point in curve.keyframe_points:
                point.co.y += 2
                point.handle_left.y += 2
                point.handle_right.y += 2
            curve.update()
            self.assertEqual(api.refresh_ghosts(self.obj.name), len(ghosts))
            self.assertAlmostEqual(ghosts[0].world_position.x - before.x, 2, places=4)
            self.assertAlmostEqual(self.scene.frame_current_final, 7.25)
        finally:
            fc.restore_fcurve(curve, snapshot)

    def test_constraint_and_negative_subframe_sampling(self):
        target = bpy.data.objects.new('ConstraintTarget', None)
        self.scene.collection.objects.link(target)
        target.location = (3, 4, 5)
        bone = self.obj.pose.bones[0]
        constraint = bone.constraints.new('COPY_LOCATION')
        constraint.target = target
        try:
            frames = [-1.5, 2.25, 6.75]
            ghosts = gd.generate_ghosts_frame_step(self.obj, self.obj, self.bones,
                                                  gd.LOCATION_CHANNELS, frames)
            self.assertAlmostEqual(self.scene.frame_current_final, 7.25)
            for ghost in ghosts:
                import math
                whole = math.floor(ghost.frame)
                self.scene.frame_set(whole, subframe=ghost.frame - whole)
                evaluated = self.obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
                expected = evaluated.matrix_world @ evaluated.pose.bones[ghost.bone_name].head
                self.assertLess((ghost.world_position - expected).length, 1e-5)
        finally:
            bone.constraints.remove(constraint)
            bpy.data.objects.remove(target, do_unlink=True)

    def test_live_generation_replaces_store_without_scheduling_itself(self):
        self.settings.is_active = True
        self.settings.live_point_ghosts = True
        self.settings.live_mesh_ghosts = False
        store = gd.GhostStore.get(self.scene)
        old = gd.Ghost(frame=99)
        store.replace_all([old])
        pipeline = gp.GhostPipeline.get(self.scene)
        with patch.object(gp, '_schedule_deferred_update') as schedule:
            pipeline._run_live_update(bpy.context, self.settings, gp.compute_settings_hash(self.settings))
        self.assertGreater(len(store), 0)
        self.assertNotIn(old.uid, {g.uid for g in store})
        self.assertFalse(pipeline._get_cache().is_dirty)
        self.assertEqual(schedule.call_count, 0)
        self.assertAlmostEqual(self.scene.frame_current_final, 7.25)

    def test_throttled_timer_reuses_registration(self):
        self.settings.is_active = True
        self.settings.live_point_ghosts = True
        cache = gp.GhostPipeline.get(self.scene)._get_cache()
        cache.mark_clean()
        cache.mark_dirty()
        with patch.object(gp.bpy.app.timers, 'register') as register:
            delay = gp._deferred_live_update()
        self.assertGreater(delay, 0)
        self.assertEqual(register.call_count, 0)

    def test_path_colour_before_follows_colour_until_set(self):
        # Review F1 (Round B): a path saved before 3.6 has no colour-before; Split must
        # dim its own colour, not a fixed gold.
        paths = self.settings.motion_paths
        e = paths.add()
        try:
            e.color = (0.31, 0.76, 0.97)
            for before, colour in zip(e.color_before, e.color):
                self.assertAlmostEqual(before, colour * 0.55, places=5)
            e.color_before = (0.1, 0.2, 0.3)
            e.color = (1.0, 1.0, 1.0)   # a chosen colour-before stays put
            self.assertEqual([round(c, 5) for c in e.color_before], [0.1, 0.2, 0.3])
        finally:
            paths.remove(len(paths) - 1)

if __name__ == '__main__':
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(GhostRegression))
    print('GHOST_REGRESSION_RESULT: ' + ('PASS' if result.wasSuccessful() else 'FAIL'), flush=True)
    if not result.wasSuccessful():
        raise RuntimeError('Ghost Tool regression checks failed')
