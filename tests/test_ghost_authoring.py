"""Behavioral checks for authoring new poses while Ghost Tool samples frames."""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace

import bpy

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import ghost_tool
from ghost_tool import utils, ghost_pipeline as gp, ghost_data as gd
from ghost_tool import mesh_ghosts as mg, motion_paths as mp
from ghost_tool import draw_to_keys as dk


class AuthoringRegression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Blender is a stand-in for animation evaluation only when BFA is absent.
        cls.host_is_bforartists = ghost_tool._is_bforartists()
        with patch.object(ghost_tool, '_is_bforartists', return_value=True), \
                patch.object(ghost_tool, '_clear_pycache'):
            ghost_tool.register()

    @classmethod
    def tearDownClass(cls):
        ghost_tool.unregister()

    def setUp(self):
        self.scene = bpy.context.scene
        self.settings = self.scene.ghost_tool
        self.settings.is_active = False
        bpy.ops.object.select_all(action='DESELECT')
        arm = bpy.data.armatures.new('AuthoringRig')
        self.obj = bpy.data.objects.new('AuthoringRig', arm)
        self.scene.collection.objects.link(self.obj)
        self.obj.select_set(True)
        bpy.context.view_layer.objects.active = self.obj
        bpy.ops.object.mode_set(mode='EDIT')
        bone = arm.edit_bones.new('Control')
        bone.head, bone.tail = (0, 0, 0), (0, 0, 1)
        bpy.ops.object.mode_set(mode='POSE')
        self.bone = self.obj.pose.bones['Control']
        for frame, value in ((1, 0), (21, 2)):
            self.obj.location.x = value
            self.obj.keyframe_insert('location', frame=frame)
            self.bone.location.y = value
            self.bone.keyframe_insert('location', frame=frame)
        self.scene.frame_set(7, subframe=0.25)
        self.settings.live_throttle_ms = 0
        self.settings.live_point_ghosts = True
        self.settings.live_mesh_ghosts = False
        self.settings.paths_enabled = False
        self.settings.ghost_mode = 'FRAME_STEP'
        self.settings.ghost_range_mode = 'CUSTOM'
        self.settings.custom_range_start = 2
        self.settings.custom_range_end = 5
        self.settings.frame_step = 1

    def tearDown(self):
        self.settings.is_active = False
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.data.objects.remove(self.obj, do_unlink=True)
        gp.GhostPipeline.clear_all_instances()

    def edit_pose(self):
        self.obj.location = (8, 9, 10)
        self.bone.location = (11, 12, 13)
        bpy.context.view_layer.update()

    def assert_pose(self):
        self.assertEqual(tuple(self.obj.location), (8, 9, 10))
        self.assertEqual(tuple(self.bone.location), (11, 12, 13))
        self.assertAlmostEqual(self.scene.frame_current_final, 7.25)
        self.assertFalse(utils.is_sampling())

    def test_sampling_preserves_unkeyed_pose(self):
        self.edit_pose()
        with utils.scene_sampling(self.scene):
            self.scene.frame_set(2)
            self.assertNotAlmostEqual(self.obj.location.x, 8)
        self.assert_pose()

    def test_live_refresh_preserves_pose_for_new_key(self):
        self.settings.is_active = True
        self.edit_pose()
        for _ in range(3):
            pipeline = gp.GhostPipeline.get(self.scene)
            pipeline.mark_dirty()
            gp._deferred_live_update()
            self.assertTrue(gd.GhostStore.get(self.scene).all_ghosts)
            self.assert_pose()
        self.bone.keyframe_insert('location', frame=7.25)
        self.obj.keyframe_insert('location', frame=7.25)
        self.scene.frame_set(1)
        self.scene.frame_set(7, subframe=0.25)
        self.assert_pose()

    def test_failed_and_nested_sampling_preserve_pose(self):
        self.edit_pose()
        with self.assertRaisesRegex(RuntimeError, 'injected'):
            with utils.scene_sampling(self.scene):
                self.scene.frame_set(2)
                intermediate = tuple(self.bone.location)
                with utils.scene_sampling(self.scene):
                    self.scene.frame_set(4)
                self.assertEqual(tuple(self.bone.location), intermediate)
                raise RuntimeError('injected')
        self.assert_pose()

    def test_sampling_same_frame_preserves_pose(self):
        self.edit_pose()
        with utils.scene_sampling(self.scene):
            self.scene.frame_set(7, subframe=0.25)
        self.assert_pose()

    def test_sampling_preserves_all_rotation_modes_and_delta_transforms(self):
        for mode, name, value in (
                ('XYZ', 'rotation_euler', (0.2, 0.3, 0.4)),
                ('QUATERNION', 'rotation_quaternion', (0.8, 0.2, 0.3, 0.4)),
                ('AXIS_ANGLE', 'rotation_axis_angle', (0.7, 0, 0, 1))):
            with self.subTest(mode=mode):
                for holder in (self.obj, self.bone):
                    holder.rotation_mode = mode
                    setattr(holder, name, value)
                    holder.keyframe_insert(name, frame=1)
                    holder.keyframe_insert('scale', frame=1)
                self.obj.keyframe_insert('delta_location', frame=1)
                self.scene.frame_set(7, subframe=0.25)
                expected = {}
                for holder in (self.obj, self.bone):
                    setattr(holder, name, tuple(v + 0.1 for v in value))
                    holder.scale = (1.2, 1.3, 1.4)
                    expected[holder.name] = tuple(getattr(holder, name))
                self.obj.delta_location = (2, 3, 4)
                with utils.scene_sampling(self.scene):
                    self.scene.frame_set(3)
                for holder in (self.obj, self.bone):
                    self.assertEqual(tuple(getattr(holder, name)), expected[holder.name])
                    self.assertEqual(tuple(round(v, 4) for v in holder.scale), (1.2, 1.3, 1.4))
                self.assertEqual(tuple(self.obj.delta_location), (2, 3, 4))

    def test_sampling_preserves_custom_controls_and_shape_keys(self):
        for holder in (self.obj, self.bone):
            holder['control'] = 1.0
            holder.keyframe_insert('["control"]', frame=1)
            holder['control'] = 3.0
        mesh = bpy.data.meshes.new('AuthoringMesh')
        mesh.from_pydata([(0, 0, 0)], [], [])
        obj = bpy.data.objects.new('AuthoringMesh', mesh)
        self.scene.collection.objects.link(obj)
        obj.shape_key_add(name='Basis')
        key = obj.shape_key_add(name='Expression')
        key.keyframe_insert('value', frame=1)
        key.value = 0.75
        try:
            with utils.scene_sampling(self.scene):
                self.scene.frame_set(3)
            self.assertAlmostEqual(key.value, 0.75)
            for holder in (self.obj, self.bone):
                self.assertAlmostEqual(holder['control'], 3.0)
        finally:
            bpy.data.objects.remove(obj, do_unlink=True)

    def test_mesh_generation_preserves_pose_and_uses_animated_samples(self):
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.mesh.primitive_cube_add()
        cube = bpy.context.object
        for frame, value in ((1, 0), (21, 20)):
            cube.location.x = value
            cube.keyframe_insert('location', frame=frame)
        self.scene.frame_set(7, subframe=0.25)
        cube.location.x = 99
        try:
            self.assertEqual(mg.generate_mesh_ghosts(bpy.context, cube, [2, 4]), 2)
            self.assertEqual(cube.location.x, 99)
            ghosts = [o for o in self.scene.objects if o.get(mg.GHOST_TOOL_MESH_GHOST_KEY)]
            self.assertTrue(all(o.matrix_world.translation.x < 20 for o in ghosts))
            self.assertAlmostEqual(self.scene.frame_current_final, 7.25)
        finally:
            mg.clear_mesh_ghosts(bpy.context)
            bpy.data.objects.remove(cube, do_unlink=True)
            bpy.context.view_layer.objects.active = self.obj
            bpy.ops.object.mode_set(mode='POSE')

    def test_native_transform_defers_live_and_forced_updates(self):
        self.settings.is_active = True
        self.settings.live_mesh_ghosts = True
        self.settings.show_mesh_ghosts = True
        context = SimpleNamespace(
            scene=self.scene, screen=None,
            window_manager=SimpleNamespace(windows=[SimpleNamespace(
                modal_operators=[SimpleNamespace(bl_idname='TRANSFORM_OT_translate')])]))
        with patch.object(gp.bpy, 'context', context), \
                patch.object(gp.GhostPipeline, '_run_live_update') as run, \
                patch.object(mg, 'generate_mesh_ghosts') as generate:
            self.assertFalse(gp.GhostPipeline.get(self.scene).update_if_needed(context))
            self.assertEqual(gp._deferred_live_update(), 0.05)
            self.assertEqual(gp._forced_mesh_regen_callback(), 0.05)
            run.assert_not_called()
            generate.assert_not_called()
        context.window_manager.windows[0].modal_operators.clear()
        with patch.object(gp.bpy, 'context', context), \
                patch.object(gp.GhostPipeline, '_run_live_update') as run:
            gp._deferred_live_update()
            run.assert_called_once()

    def test_transform_guard_ignores_ghost_hover_operator(self):
        context = SimpleNamespace(window_manager=SimpleNamespace(windows=[
            SimpleNamespace(modal_operators=[SimpleNamespace(bl_idname='GHOSTTOOL_OT_hover')])]))
        self.assertFalse(utils.is_native_transform_active(context))

    def test_sampling_can_intentionally_write_new_keys(self):
        with utils.scene_sampling(self.scene, preserve_pose=False):
            self.scene.frame_set(7, subframe=0.25)
            self.bone.location = (11, 12, 13)
            self.bone.keyframe_insert('location', frame=7.25)
            self.scene.frame_set(3)
        self.assertEqual(tuple(self.bone.location), (11, 12, 13))

    def test_motion_paths_preserve_pose(self):
        self.settings.paths_enabled = True
        self.edit_pose()
        target = mp.PathTarget((self.obj.name, self.bone.name, -1), self.obj,
                               frames=(2, 4), anchor='HEAD', color=(1, 1, 1),
                               thickness=1, pinned=True)
        mp.clear_cache()
        with patch.object(mp, 'all_targets', return_value=[target]):
            self.assertGreater(mp.refresh_paths(bpy.context), 0)
        self.assert_pose()

    def test_draw_to_keys_evaluates_new_animation_at_playhead(self):
        bpy.ops.object.mode_set(mode='OBJECT')
        self.scene.frame_set(1)
        strokes = [[(0, 0, 0), (10, 0, 0)],
                   [(3, -1, 0), (3, 1, 0)], [(7, -1, 0), (7, 1, 0)]]
        with patch.object(dk, 'annotation_strokes', return_value=(strokes, 0)):
            result = bpy.ops.ghost_tool.paths_draw_to_keys(
                use_current_frame=False, start_frame=1, frame_step=4, interpolation='LINEAR')
        self.assertEqual(result, {'FINISHED'})
        self.assertEqual(tuple(self.obj.location), (3, 0, 0))
        self.scene.frame_set(5)
        self.assertEqual(tuple(self.obj.location), (7, 0, 0))
        bpy.ops.object.mode_set(mode='POSE')

    def test_marker_sync_waits_for_native_transform(self):
        context = SimpleNamespace(window_manager=SimpleNamespace(windows=[SimpleNamespace(
            modal_operators=[SimpleNamespace(bl_idname='TRANSFORM_OT_rotate')])]))
        with patch.object(mp.bpy, 'context', context), patch.object(mp, 'sync_markers') as sync:
            self.assertEqual(mp._deferred_marker_sync(), 0.05)
            sync.assert_not_called()


if __name__ == '__main__':
    result = unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(AuthoringRegression))
    print('AUTHORING_HOST:', bpy.app.version_string, flush=True)
    if not result.wasSuccessful():
        raise RuntimeError('Ghost Tool authoring regression failed')
