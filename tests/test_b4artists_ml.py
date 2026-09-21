"""Run with Python for kernels, or Bforartists --background --factory-startup --python.
B4ML_PACKAGE may point to the packaged ZIP for release verification.
"""
import importlib.util
import json
import math
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, os.environ.get('B4ML_PACKAGE', str(ROOT)))
import b4artists_ml
from b4artists_ml import math_core as core, rigs
try:
    import bpy
except ImportError:
    bpy = None

class KernelTests(unittest.TestCase):
    def test_host_guard(self):
        from types import SimpleNamespace
        self.assertFalse(b4artists_ml.is_bforartists(SimpleNamespace(binary_path='/usr/bin/blender')))
        self.assertTrue(b4artists_ml.is_bforartists(SimpleNamespace(binary_path='X:/Bforartists/bforartists.exe')))

    def test_stock_blender_registers_only_unsupported_host_stub(self):
        from types import SimpleNamespace

        registered = []
        unregistered = []
        addon_preferences = type('AddonPreferences', (), {})
        fake_bpy = SimpleNamespace(
            app=SimpleNamespace(binary_path='/usr/bin/blender'),
            types=SimpleNamespace(AddonPreferences=addon_preferences),
            utils=SimpleNamespace(
                register_class=registered.append,
                unregister_class=unregistered.append,
            ),
        )
        b4artists_ml._registered = False
        b4artists_ml._stub = None
        with patch.dict(sys.modules, {'bpy': fake_bpy}):
            b4artists_ml.register()
            self.assertFalse(b4artists_ml._registered)
            self.assertIsNotNone(b4artists_ml._stub)
            self.assertEqual(registered, [b4artists_ml._stub])
            b4artists_ml.unregister()
        self.assertEqual(unregistered, [registered[0]])

    def test_quaternion_short_path_and_normalization(self):
        q = core.slerp((1,0,0,0), (-1,0,0,0), .5)
        self.assertAlmostEqual(abs(q[0]), 1.)
        q = core.slerp((1,0,0,0), (0,0,0,1), .5)
        self.assertAlmostEqual(q[0], math.sqrt(.5))
        self.assertAlmostEqual(sum(v*v for v in q), 1.)

    def test_reject_nonfinite(self):
        for bad in ((float('nan'),0,0,0), (0,0,0,0), (True,0,0,0)):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                core.slerp(bad, (1,0,0,0), .5)

    def test_reach_lengths_and_unreachable(self):
        for target in ((1,1,0), (10,0,0), (0,0,0)):
            with self.subTest(target=target):
                joint, end = core.two_bone_positions((0,0,0), target, (0,0,1), 1., 1.)
                self.assertAlmostEqual(math.dist((0,0,0), joint), 1., places=6)
                self.assertAlmostEqual(math.dist(joint, end), 1., places=6)
                self.assertLessEqual(math.dist((0,0,0), end), 2.)

    def test_boneforge_maps(self):
        maps = rigs.source_maps()
        self.assertEqual(set(maps), {'rigify_deform', 'mocap_humanoid', 'unity_humanoid', 'unreal_mannequin'})
        for name, data in maps.items():
            with self.subTest(name=name):
                profile = rigs.detect_rig(data['bones'])
                self.assertEqual(profile.name, data['name'])
                self.assertEqual(profile.roles, {v:k for k,v in data['bones'].items()})
                if name == 'rigify_deform':
                    self.assertFalse(profile.controls)

    def test_boneforge_control_names(self):
        names = set(rigs.REQUIRED) | {'root', 'forearm.ik-L', 'arm.pole-L', 'upperarm.def-L', 'properties'}
        profile = rigs.detect_rig(names)
        self.assertEqual(profile.name, 'BoneForge Control Rig')
        self.assertIn('forearm.ik-L', profile.controls)
        self.assertNotIn('upperarm.def-L', profile.controls)
        self.assertNotIn('properties', profile.controls)

    def test_rigify_controls_not_deforms(self):
        names = {'torso', 'hips', 'upper_arm_fk.L', 'thigh_fk.R', 'hand_ik.L', 'DEF-upper_arm.L', 'MCH-arm'}
        profile = rigs.detect_rig(names)
        self.assertEqual(profile.name, 'Rigify Generated')
        self.assertIn('hand_ik.L', profile.controls)
        self.assertNotIn('DEF-upper_arm.L', profile.controls)

    def test_rigify_generated_quadrupeds_precede_humanoid_detection(self):
        horse = {'root', 'torso', 'hips', 'chest', 'neck', 'head',
                 'upper_arm_fk.L', 'forearm_fk.L', 'forefoot_fk.L', 'f_toe_fk.L',
                 'upper_arm_fk.R', 'forearm_fk.R', 'forefoot_fk.R', 'f_toe_fk.R',
                 'thigh_fk.L', 'lower_leg_fk.L', 'hind_foot_fk.L', 'r_toe_fk.L',
                 'thigh_fk.R', 'lower_leg_fk.R', 'hind_foot_fk.R', 'r_toe_fk.R',
                 'forefoot_ik.L', 'hind_foot_ik.R', 'DEF-upper_arm.L', 'MCH-spine'}
        profile = rigs.detect_rig(horse)
        self.assertEqual(profile.name, 'Rigify Generated Quadruped (Horse)')
        self.assertEqual(profile.family, 'quadruped')
        self.assertEqual(profile.schema, 'quadruped_v1')
        self.assertFalse(profile.missing)
        self.assertIn('forefoot_ik.L', profile.controls)
        self.assertNotIn('DEF-upper_arm.L', profile.controls)
        self.assertNotIn('MCH-spine', profile.controls)

        wolf = {'root', 'torso', 'hips', 'chest', 'neck', 'head',
                'front_thigh_fk.L', 'front_shin_fk.L', 'front_foot_fk.L', 'front_toe.L',
                'front_thigh_fk.R', 'front_shin_fk.R', 'front_foot_fk.R', 'front_toe.R',
                'thigh_fk.L', 'shin_fk.L', 'foot_fk.L', 'toe.L',
                'thigh_fk.R', 'shin_fk.R', 'foot_fk.R', 'toe.R'}
        profile = rigs.detect_rig(wolf)
        self.assertEqual(profile.name, 'Rigify Generated Quadruped (Wolf)')
        self.assertEqual(profile.family, 'quadruped')
        self.assertFalse(profile.missing)

        cat = {'root', 'torso', 'hips', 'chest', 'neck', 'head',
               'upper_arm_fk.L', 'forearm_fk.L', 'hand_fk.L', 'f_toe.L',
               'upper_arm_fk.R', 'forearm_fk.R', 'hand_fk.R', 'f_toe.R',
               'thigh_fk.L', 'shin_fk.L', 'foot_fk.L', 'r_toe.L',
               'thigh_fk.R', 'shin_fk.R', 'foot_fk.R', 'r_toe.R',
               'hand_ik.L', 'foot_ik.R'}
        profile = rigs.detect_rig(cat)
        self.assertEqual(profile.name, 'Rigify Generated Quadruped (Cat)')
        self.assertFalse(profile.missing)
        self.assertIn('hand_ik.L', profile.controls)
        self.assertIn('foot_ik.R', profile.controls)

    def test_rigify_quadruped_metarigs(self):
        horse = {'spine.001', 'spine.006', 'head',
                 'upper_arm.L', 'forearm.L', 'forefoot.L', 'f_toe.L',
                 'upper_arm.R', 'forearm.R', 'forefoot.R', 'f_toe.R',
                 'thigh.L', 'lower_leg.L', 'hind_foot.L', 'r_toe.L',
                 'thigh.R', 'lower_leg.R', 'hind_foot.R', 'r_toe.R'}
        profile = rigs.detect_rig(horse)
        self.assertEqual(profile.name, 'Rigify Quadruped Metarig (Horse)')
        self.assertFalse(profile.missing)
        self.assertEqual(profile.family, 'quadruped')

        wolf = {'spine.004', 'spine.008', 'spine.011', 'face',
                'front_thigh.L', 'front_shin.L', 'front_foot.L', 'front_toe.L',
                'front_thigh.R', 'front_shin.R', 'front_foot.R', 'front_toe.R',
                'thigh.L', 'shin.L', 'foot.L', 'toe.L',
                'thigh.R', 'shin.R', 'foot.R', 'toe.R'}
        profile = rigs.detect_rig(wolf)
        self.assertEqual(profile.name, 'Rigify Quadruped Metarig (Wolf)')
        self.assertFalse(profile.missing)

        cat = {'spine', 'spine.006', 'face', 'tail.001', 'pelvis.C',
               'upper_arm.L', 'forearm.L', 'hand.L', 'f_toe.L',
               'upper_arm.R', 'forearm.R', 'hand.R', 'f_toe.R',
               'thigh.L', 'shin.L', 'foot.L', 'r_toe.L',
               'thigh.R', 'shin.R', 'foot.R', 'r_toe.R'}
        profile = rigs.detect_rig(cat)
        self.assertEqual(profile.name, 'Rigify Quadruped Metarig (Cat)')
        self.assertFalse(profile.missing)


    def test_mmd_japanese_and_vroid(self):
        names = ['\u4e0b\u534a\u8eab', '\u4e0a\u534a\u8eab', '\u4e0a\u534a\u8eab2', '\u9996', '\u982d']
        names += [side + part for side in ('\u5de6', '\u53f3')
                  for part in ('\u8155', '\u3072\u3058', '\u624b\u9996', '\u8db3', '\u3072\u3056', '\u8db3\u9996')]
        profile = rigs.detect_rig(names)
        self.assertEqual(profile.name, 'MMD')
        self.assertFalse(profile.missing)
        self.assertEqual(len(set(profile.roles.values())), len(profile.roles))
        vroid = ['J_Bip_C_' + p for p in ('Hips','Spine','Chest','Neck','Head')]
        vroid += ['J_Bip_' + side + '_' + p for side in ('L','R')
                  for p in ('UpperArm','LowerArm','Hand','UpperLeg','LowerLeg','Foot')]
        profile = rigs.detect_rig(vroid)
        self.assertEqual(profile.name, 'VRoid / VRM')
        self.assertFalse(profile.missing)

    def test_unknown_does_not_guess(self):
        profile = rigs.detect_rig(['Head', 'Left', 'Right', 'MyShoulder'])
        self.assertFalse(profile.controls)
        self.assertEqual(profile.family, 'unknown')
        self.assertEqual(profile.schema, 'unmapped')

@unittest.skipIf(bpy is None, 'Bforartists runtime required')
class RuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not b4artists_ml.is_bforartists():
            raise unittest.SkipTest('Bforartists required')
        b4artists_ml.register()
        from b4artists_ml import workflow
        cls.w = workflow

    def setUp(self):
        if bpy.context.object and bpy.context.object.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        self.data = bpy.data.armatures.new('B4ML Test')
        self.obj = bpy.data.objects.new('B4ML Test', self.data)
        bpy.context.scene.collection.objects.link(self.obj)
        bpy.context.view_layer.objects.active = self.obj
        self.obj.select_set(True)
        bpy.ops.object.mode_set(mode='EDIT')
        bone = self.data.edit_bones.new('hips')
        bone.head = (0,0,0)
        bone.tail = (0,0,1)
        bpy.ops.object.mode_set(mode='POSE')
        self.bone = self.obj.pose.bones['hips']
        self.bone.rotation_mode = 'QUATERNION'
        if hasattr(self.bone, 'select'):
            self.bone.select = True
        else:
            self.bone.bone.select = True
        self.obj.b4ml.selected_only = True
        self.scene = bpy.context.scene
        self.scene.frame_set(1)

    def tearDown(self):
        if bpy.context.object and bpy.context.object.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        # Save/reload tests invalidate RNA handles; find the current object by name.
        obj = bpy.data.objects.get('B4ML Test')
        if obj:
            data = obj.data
            bpy.data.objects.remove(obj, do_unlink=True)
            if not data.users:
                bpy.data.armatures.remove(data)

    def anchors(self, keyed=True):
        self.bone.location = (0,0,0)
        if keyed:
            self.bone.keyframe_insert('location', frame=1)
        self.w.capture_anchor(self.obj, self.scene, True)
        self.scene.frame_set(11)
        self.bone.location = (10,0,0)
        self.bone.rotation_quaternion = (0,0,0,1)
        if keyed:
            self.bone.keyframe_insert('location', frame=11)
        self.w.capture_anchor(self.obj, self.scene, True)

    def curve_signature(self, action):
        curves = self.w.action_curves(action, self.obj.animation_data.action_slot if hasattr(self.obj.animation_data, 'action_slot') else None)
        return [(f.data_path, f.array_index, [(tuple(k.co), tuple(k.handle_left), tuple(k.handle_right), k.interpolation)
                for k in f.keyframe_points]) for f in curves]

    def test_preview_preserves_source_and_discard(self):
        self.anchors()
        source = self.obj.animation_data.action
        before = self.curve_signature(source)
        slot = self.w._slot(self.obj.animation_data)
        self.scene.frame_set(6)
        frame_count, _ = self.w.preview(self.obj, self.scene)
        self.assertEqual(frame_count, 11)
        self.assertIsNotNone(self.obj.b4ml.candidate_action)
        self.assertAlmostEqual(self.bone.location.x, 5., places=4)
        candidate = self.obj.animation_data.action
        self.assertNotEqual(source, candidate)
        self.w.finish_preview(self.obj, self.scene)
        self.assertEqual(source, self.obj.animation_data.action)
        self.assertEqual(slot, self.w._slot(self.obj.animation_data))
        self.assertEqual(before, self.curve_signature(source))

    def test_no_action_discard(self):
        self.anchors(False)
        old_pose = tuple(self.bone.location)
        self.w.preview(self.obj, self.scene)
        self.w.finish_preview(self.obj, self.scene)
        self.assertIsNone(self.obj.animation_data.action)
        self.assertEqual(tuple(self.bone.location), old_pose)

    def test_keep_preserves_original(self):
        self.anchors()
        source = self.obj.animation_data.action
        self.w.preview(self.obj, self.scene)
        candidate = self.obj.animation_data.action
        self.w.finish_preview(self.obj, self.scene, True)
        self.assertEqual(self.obj.animation_data.action, candidate)
        self.assertTrue(source.use_fake_user)
        self.assertIsNone(self.obj.b4ml.candidate_action)

    def test_failed_generation_rolls_back(self):
        self.anchors()
        source = self.obj.animation_data.action
        before = self.w.raw_pose(self.obj)
        actual_blend = self.w.blend_pose
        calls = []
        action_count = len(bpy.data.actions)
        def failing_blend(*args, **kwargs):
            calls.append(1)
            if len(calls) == 4:
                raise ValueError('injected failure after candidate creation')
            return actual_blend(*args, **kwargs)
        with patch.object(self.w, 'blend_pose', side_effect=failing_blend):
            with self.assertRaises(ValueError):
                self.w.preview(self.obj, self.scene)
        self.assertEqual(len(bpy.data.actions), action_count)
        self.assertEqual(len(calls), 4)
        self.assertEqual(self.obj.animation_data.action, source)
        self.assertEqual(self.w.raw_pose(self.obj), before)
        self.assertIsNone(self.obj.b4ml.candidate_action)

    def test_locks_changed_rejected(self):
        self.anchors()
        self.bone.lock_location[0] = True
        with self.assertRaises(ValueError):
            self.w.preview(self.obj, self.scene)
        self.assertIsNone(self.obj.b4ml.candidate_action)

    def test_locked_axis_not_written(self):
        self.bone.lock_location[1] = True
        self.anchors(False)
        self.w.preview(self.obj, self.scene)
        curves = self.w.action_curves(self.obj.animation_data.action, getattr(self.obj.animation_data,'action_slot',None))
        self.assertIsNone(curves.find(self.bone.path_from_id('location'), index=1))
        self.w.finish_preview(self.obj, self.scene)

    def test_three_anchors_preserved(self):
        self.anchors(False)
        self.scene.frame_set(6)
        self.bone.location = (3,2,1)
        self.w.capture_anchor(self.obj, self.scene, True)
        self.w.preview(self.obj, self.scene)
        self.assertAlmostEqual(self.bone.location.x, 3., places=4)
        self.assertAlmostEqual(self.bone.location.y, 2., places=4)
        self.w.finish_preview(self.obj, self.scene)

    def test_nan_anchor_rejected(self):
        self.anchors()
        payload = json.loads(self.obj.b4ml.anchors[0].payload)
        payload['pose']['hips']['location'][0] = float('nan')
        self.obj.b4ml.anchors[0].payload = json.dumps(payload)
        with self.assertRaises(ValueError):
            self.w.preview(self.obj, self.scene)

    def test_range_budget(self):
        self.anchors()
        self.obj.b4ml.anchors[1].frame = 1000
        with self.assertRaises(ValueError):
            self.w.preview(self.obj, self.scene)

    def test_ik_fk_switch_changes_rejected(self):
        self.bone['IK_FK'] = 0.
        self.anchors()
        self.bone['IK_FK'] = 1.
        with self.assertRaises(ValueError):
            self.w.preview(self.obj, self.scene)

    def test_save_reload_pending_candidate(self):
        self.anchors()
        source_name = self.obj.animation_data.action.name
        self.w.preview(self.obj, self.scene)
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / 'ml_roundtrip.blend')
            bpy.ops.wm.save_as_mainfile(filepath=path)
            bpy.ops.wm.open_mainfile(filepath=path)
            obj = bpy.data.objects['B4ML Test']
            self.assertEqual(len(obj.b4ml.anchors), 2)
            self.assertIsNotNone(obj.b4ml.candidate_action)
            self.w.finish_preview(obj, bpy.context.scene)
            self.assertEqual(obj.animation_data.action.name, source_name)

    def test_operator_ui_workflow(self):
        self.anchors(False)
        self.assertEqual(bpy.ops.b4ml.action(operation='PREVIEW'), {'FINISHED'})
        self.assertEqual(bpy.ops.b4ml.action(operation='DISCARD'), {'FINISHED'})


    def test_quaternion_antipodal_anchors_no_flip(self):
        self.anchors(False)
        second = json.loads(self.obj.b4ml.anchors[1].payload)
        second['pose']['hips']['rotation'] = [-1.,0.,0.,0.]
        second['pose']['hips']['raw_rotation'] = [-1.,0.,0.,0.]
        self.obj.b4ml.anchors[1].payload = json.dumps(second)
        self.w.preview(self.obj, self.scene)
        for frame in (1,5,10.5,11):
            self.scene.frame_set(int(frame), subframe=frame-int(frame))
            self.assertGreater(self.bone.rotation_quaternion.magnitude, .99)
            self.assertAlmostEqual(abs(self.bone.rotation_quaternion.w), 1., places=5)
        self.w.finish_preview(self.obj, self.scene)

    def test_euler_wrap_uses_short_path(self):
        self.bone.rotation_mode = 'XYZ'
        self.bone.rotation_euler.z = math.radians(179)
        self.w.capture_anchor(self.obj, self.scene, True)
        self.scene.frame_set(11)
        self.bone.rotation_euler.z = math.radians(-179)
        self.w.capture_anchor(self.obj, self.scene, True)
        self.w.preview(self.obj, self.scene)
        self.scene.frame_set(6)
        self.assertAlmostEqual(abs(self.bone.rotation_euler.z), math.pi, places=4)
        self.w.finish_preview(self.obj, self.scene)

    def test_nla_and_drivers_rejected(self):
        self.anchors()
        source = self.obj.animation_data.action
        track = self.obj.animation_data.nla_tracks.new()
        track.strips.new('Test strip', 1, source)
        with self.assertRaises(ValueError):
            self.w.preview(self.obj, self.scene)
        track.mute = True
        self.bone.driver_add('location', 0)
        with self.assertRaises(ValueError):
            self.w.preview(self.obj, self.scene)
        self.bone.driver_remove('location', 0)

    def test_switching_action_during_preview_does_not_overwrite(self):
        self.anchors()
        self.w.preview(self.obj, self.scene)
        unrelated = bpy.data.actions.new('Other Action')
        self.obj.animation_data.action = unrelated
        with self.assertRaises(ValueError):
            self.w.finish_preview(self.obj, self.scene)
        self.assertEqual(self.obj.animation_data.action, unrelated)

    def test_fake_user_candidate_cleanup(self):
        self.anchors()
        self.obj.animation_data.action.use_fake_user = True
        before = len(bpy.data.actions)
        self.w.preview(self.obj, self.scene)
        self.w.finish_preview(self.obj, self.scene)
        self.assertEqual(len(bpy.data.actions), before)

    def test_bound_mesh_resolution(self):
        mesh = bpy.data.objects.new('ML Mesh', bpy.data.meshes.new('ML Mesh'))
        self.scene.collection.objects.link(mesh)
        modifier = mesh.modifiers.new('Rig', 'ARMATURE')
        modifier.object = self.obj
        from types import SimpleNamespace
        self.assertEqual(self.w.active_rig(SimpleNamespace(active_object=mesh, view_layer=bpy.context.view_layer)), self.obj)
        bpy.data.objects.remove(mesh, do_unlink=True)

    def test_armatures_do_not_share_anchors(self):
        self.anchors(False)
        other = bpy.data.objects.new('Other Rig', self.data)
        self.scene.collection.objects.link(other)
        self.assertEqual(len(other.b4ml.anchors), 0)
        bpy.data.objects.remove(other, do_unlink=True)

    def test_registration_and_standard_blender_stub(self):
        b4artists_ml.unregister()
        with patch.object(b4artists_ml, 'is_bforartists', return_value=False):
            b4artists_ml.register()
            self.assertFalse(b4artists_ml._registered)
            self.assertIsNotNone(b4artists_ml._stub)
            self.assertFalse(hasattr(bpy.types.Object, 'b4ml'))
            b4artists_ml.unregister()
        b4artists_ml.register()
        b4artists_ml.register()
        self.assertTrue(b4artists_ml._registered)

    def test_actual_rigify_basic_human(self):
        self._rigify_roundtrip(False)

    def test_actual_rigify_default_human(self):
        self._rigify_roundtrip(True)

    def _rigify_roundtrip(self, full):
        bpy.ops.object.mode_set(mode='OBJECT')
        import rigify
        if not hasattr(bpy.types.PoseBone, 'rigify_type'):
            import addon_utils
            addon_utils.enable('rigify', default_set=True, persistent=False)
        if full:
            from rigify.metarigs import human as basic_human
        else:
            from rigify.metarigs.Basic import basic_human
        data = bpy.data.armatures.new('ML Metarig')
        meta = bpy.data.objects.new('ML Metarig', data)
        self.scene.collection.objects.link(meta)
        bpy.context.view_layer.objects.active = meta
        self.obj.select_set(False)
        meta.select_set(True)
        try:
            basic_human.create(meta)
            bpy.ops.object.mode_set(mode='OBJECT')
            profile = rigs.detect_rig(meta.data.bones.keys())
            self.assertEqual(profile.name, 'BoneForge Legacy / Rigify Metarig')
            self.assertIn('upper_arm.L', profile.controls)
            bpy.ops.pose.rigify_generate()
            generated = bpy.context.object
            profile = rigs.detect_rig(generated.data.bones.keys())
            self.assertEqual(profile.name, 'Rigify Generated')
            self.assertFalse(any(n.startswith(('DEF-', 'MCH-', 'ORG-')) for n in profile.controls))
            self.scene.frame_set(1)
            self.w.capture_anchor(generated, self.scene)
            self.scene.frame_set(11)
            generated.pose.bones['torso'].location.x += .1
            self.w.capture_anchor(generated, self.scene)
            from time import perf_counter
            started = perf_counter()
            self.w.preview(generated, self.scene)
            elapsed_ms = (perf_counter() - started)*1000
            self.scene.frame_set(6)
            self.assertAlmostEqual(generated.pose.bones['torso'].location.x, .05, places=4)
            print(f'B4ML_TIMING: full={full}, controls={len(profile.controls)}, preview_ms={elapsed_ms:.2f}', flush=True)
            self.w.finish_preview(generated, self.scene)
            print(f'B4ML_RIGIFY: real full={full} generation, midpoint motion, capture, preview and discard PASS', flush=True)
        finally:
            if bpy.context.object and bpy.context.object.mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')
            for obj in (meta,):
                if obj.name in bpy.data.objects:
                    bpy.data.objects.remove(obj, do_unlink=True)

if __name__ == '__main__':
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__]))
    if bpy and b4artists_ml._registered:
        b4artists_ml.unregister()
    print('B4ML_RESULT: ' + ('PASS' if result.wasSuccessful() else 'FAIL'), flush=True)
    if not result.wasSuccessful():
        raise SystemExit(1)
