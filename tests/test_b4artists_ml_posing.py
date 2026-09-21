"""Assisted posing integration tests; builds reference rigs inside a disposable host."""
import json
import os
from pathlib import Path
import sys
import time
import unittest
METRICS = []
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, os.environ.get("B4ML_PACKAGE", str(ROOT)))
try:
    import bpy
except ImportError:
    bpy = None

def empty_rig(name):
    if bpy.context.object and bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    for ob in bpy.context.selected_objects:
        ob.select_set(False)
    ob = bpy.data.objects.new(name, bpy.data.armatures.new(name))
    bpy.context.scene.collection.objects.link(ob)
    bpy.context.view_layer.objects.active = ob
    ob.select_set(True)
    return ob

def boneforge_rig():
    source = Path(os.environ.get('B4ML_BONEFORGE_SOURCE', str(ROOT.parent / 'BoneForge_B4Artists_github')))
    if not source.joinpath('boneforge').is_dir():
        raise unittest.SkipTest('Set B4ML_BONEFORGE_SOURCE to a BoneForge checkout')
    sys.path.insert(0, str(source))
    from boneforge.autorig.rig_build import RigSpec, compute_build_plan, apply_build_plan
    ob = empty_rig('BoneForge fixture')
    apply_build_plan(compute_build_plan(RigSpec()), ob)
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.context.view_layer.update()
    return ob

def rigify_rig(full=False, generate=True):
    import addon_utils
    addon_utils.enable('rigify', default_set=True, persistent=False)
    from rigify.metarigs.Basic import basic_human
    from rigify.metarigs import human
    ob = empty_rig('Rigify fixture')
    (human if full else basic_human).create(ob)
    bpy.ops.object.mode_set(mode='OBJECT')
    if generate:
        bpy.ops.pose.rigify_generate()
        ob = bpy.context.object
    bpy.context.view_layer.update()
    return ob


from b4artists_ml.math_core import two_bone_positions
import math

class ReachTests(unittest.TestCase):
    def test_scale_invariance_and_bend_limit(self):
        for scale in (1e-6, 1., 1e6):
            for target in ((0,0,0), (scale,0,0), (10*scale,0,0)):
                joint, end = two_bone_positions((0,0,0), target, (0,0,scale), scale, scale*.7, 120.)
                self.assertAlmostEqual(math.dist((0,0,0), joint)/scale, 1., places=6)
                self.assertAlmostEqual(math.dist(joint, end)/scale, .7, places=6)
                self.assertGreaterEqual(math.dist((0,0,0), end)/scale, math.sqrt(1+.49-.7)-1e-6)

    def test_invalid_bend(self):
        for angle in (0., 181., float('nan')):
            with self.assertRaises(ValueError):
                two_bone_positions((0,0,0), (1,0,0), (0,1,0), 1., 1., angle)

@unittest.skipIf(bpy is None, 'Bforartists runtime required')
class PosingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import b4artists_ml
        b4artists_ml.register()
        from b4artists_ml import posing, workflow
        cls.p, cls.w = posing, workflow
        cls.rigs = {'boneforge': boneforge_rig(), 'rigify': rigify_rig(),
                    'rigify_full': rigify_rig(full=not bool(os.environ.get('B4ML_FAST'))), 'metarig': rigify_rig(generate=False), 'metarig_full': rigify_rig(full=True, generate=False)}
        cls.defaults = {name: workflow.raw_pose(ob) for name, ob in cls.rigs.items()}

    def setUp(self):
        if bpy.context.object and bpy.context.object.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.scene.frame_set(1)
        from mathutils import Matrix
        for name, ob in self.rigs.items():
            if ob.b4ml.posing_payload:
                self.p.finish(ob, bpy.context.scene, keep=False)
            if ob.animation_data:
                ob.animation_data.action = None
            ob.matrix_world = Matrix.Identity(4)
            for pb in ob.pose.bones:
                default = self.defaults[name][pb.name]
                pb.rotation_mode = default['mode']
            self.w.restore_pose(ob, self.defaults[name])
            ob.b4ml.anchors.clear()
            self.mode(ob, False)
        bpy.context.view_layer.update()

    def mode(self, ob, ik):
        if 'properties' in ob.pose.bones:
            for k in ob.pose.bones['properties'].keys():
                if k.startswith('IK_FK-'):
                    ob.pose.bones['properties'][k] = float(ik)
        for pb in ob.pose.bones:
            if 'IK_FK' in pb:
                pb['IK_FK'] = 0. if ik else 1.
                pb['pole_vector'] = False
                pb['IK_Stretch'] = 1.
        # Rigid-IK fixtures explicitly disable native stretch. Default IK rejection is tested separately.
        for pb in ob.pose.bones:
            for con in pb.constraints:
                if con.type == 'IK':
                    con.use_stretch = not ik
        ob.update_tag(refresh={'OBJECT'})
        bpy.context.view_layer.update()

    def activate(self, ob):
        for other in bpy.context.selected_objects:
            other.select_set(False)
        bpy.context.view_layer.objects.active = ob
        ob.select_set(True)

    def exercise(self, name, ik=False, transform=False, crouch=False, poles=False):
        from mathutils import Matrix, Vector
        ob = self.rigs[name]
        self.activate(ob)
        if ob.b4ml.posing_payload:
            self.p.finish(ob, bpy.context.scene, keep=False)
        self.mode(ob, ik)
        if poles:
            for pb in ob.pose.bones:
                if 'pole_vector' in pb:
                    pb['pole_vector'] = True
        if transform:
            ob.matrix_world = Matrix.Translation((2,-3,1)) @ Matrix.Rotation(.7, 4, 'Z') @ Matrix.Scale(2.5, 4)
        ob.update_tag(refresh={'OBJECT'})
        bpy.context.view_layer.update()
        before = self.w.raw_pose(ob)
        switches = self.w._switches(ob)
        rows = self.p.begin(ob, bpy.context.scene)
        if crouch:
            ob.b4ml.pose_offset = (0, 0, -.06 * ob.matrix_world.to_scale().x)
        else:
            item = ob.b4ml.pose_targets['arm-L']
            root = ob.matrix_world @ ob.pose.bones[rows[0]['joints'][0]].head
            point = item.target.location.copy()
            item.target.location = point.lerp(root, .15) + Vector((0,-.02,0))
        bpy.context.view_layer.update()
        results = self.p.solve(ob, bpy.context.scene)
        METRICS.append(dict(rig=name, mode='IK input (FK solve)' if ik else 'FK', transformed=transform,
                            crouch=crouch, positional_poles=poles, **json.loads(ob.b4ml.pose_metrics)))
        print('POSE_METRICS', name, 'IK input (FK solve)' if ik else 'FK', 'transformed', transform, 'crouch', crouch,
              'poles', poles, ob.b4ml.pose_metrics)
        for row in results:
            self.assertLess(row['residual'], 2e-4, row)
            if not row['clamped']:
                self.assertLess(row['error'], 5e-4 * ob.matrix_world.to_scale().x, row)
            self.assertLess(row['stretch'], .002, row)
        from b4artists_ml import rig_state
        modes=rig_state.canonical_modes(ob)
        self.assertEqual(rig_state.without_modes(switches,modes), rig_state.without_modes(self.w._switches(ob),modes))
        after = self.w.raw_pose(ob)
        for name, original in before.items():
            if name.startswith(('DEF-', 'ORG-', 'MCH-')) or '.def-' in name or '.mch_' in name:
                # Driven/evaluated properties may differ; writable original transform channels must not.
                self.assertEqual(original['raw_rotation'], after[name]['raw_rotation'])
        self.p.finish(ob, bpy.context.scene, keep=False)
        self.assertFalse(ob.b4ml.posing_payload)
        self.assertEqual(switches,self.w._switches(ob))
        for name, original in before.items():
            if name in self.w.detect_rig(ob.data.bones.keys()).controls:
                restored = self.w.raw_pose(ob, [name])[name]
                self.assertEqual(original['raw_rotation'], restored['raw_rotation'])
                self.assertEqual(original['location'], restored['location'])

    def test_reference_rigs_fk(self):
        for name in self.rigs:
            with self.subTest(rig=name):
                self.exercise(name)

    def test_reference_rigs_ik(self):
        for name in ('rigify', 'rigify_full'):
            with self.subTest(rig=name):
                self.exercise(name, ik=True)

    def test_world_transform_and_scale(self):
        for name, ik in (('boneforge', False), ('rigify', False), ('rigify', True), ('metarig', False)):
            with self.subTest(rig=name, ik=ik):
                self.exercise(name, ik=ik, transform=True)

    def test_four_pins_with_pelvis_offset(self):
        for name, ik in (('boneforge', False), ('rigify', False), ('rigify', True)):
            with self.subTest(rig=name, ik=ik):
                self.exercise(name, ik=ik, crouch=True)

    def test_rigify_positional_poles(self):
        self.exercise('rigify', ik=True, poles=True)

    def test_default_ik_matched_and_cancelled(self):
        for name in ('boneforge', 'rigify'):
            ob = self.rigs[name]
            self.activate(ob)
            self.mode(ob, True)
            for pb in ob.pose.bones:
                for con in pb.constraints:
                    if con.type == 'IK':
                        con.use_stretch = True
            before = self.w.raw_pose(ob)
            modes=__import__('b4artists_ml.rig_state',fromlist=['mode_values']).mode_values(ob)
            self.p.begin(ob, bpy.context.scene)
            self.assertTrue(ob.b4ml.posing_payload)
            self.p.solve(ob,bpy.context.scene)
            self.p.finish(ob,bpy.context.scene,False)
            self.assertFalse(ob.b4ml.posing_payload)
            self.assertEqual(before, self.w.raw_pose(ob))
            self.assertEqual(modes,__import__('b4artists_ml.rig_state',fromlist=['mode_values']).mode_values(ob))

    def test_keep_anchor_and_interpolate_preserves_source(self):
        ob = self.rigs['boneforge']
        self.activate(ob)
        hips = ob.pose.bones['hips']
        hips.keyframe_insert('location', frame=1)
        hips.keyframe_insert('location', frame=11)
        source = ob.animation_data.action
        curves = self.w.action_curves(source, ob.animation_data.action_slot)
        before = [(f.data_path, f.array_index, [tuple(k.co) for k in f.keyframe_points]) for f in curves]
        self.w.capture_anchor(ob, bpy.context.scene)
        bpy.context.scene.frame_set(11)
        self.p.begin(ob, bpy.context.scene)
        ob.b4ml.pose_offset.z = -.05
        self.p.finish(ob, bpy.context.scene, keep=True)
        self.assertEqual(len(ob.b4ml.anchors), 2)
        self.assertIs(ob.animation_data.action, source)
        self.assertFalse(ob.b4ml.pose_targets)
        self.w.preview(ob, bpy.context.scene)
        self.assertIsNot(ob.animation_data.action, source)
        self.w.finish_preview(ob, bpy.context.scene, keep=False)
        self.assertEqual(before, [(f.data_path, f.array_index, [tuple(k.co) for k in f.keyframe_points]) for f in curves])

    def test_failure_rollback_and_session_cancel(self):
        from unittest.mock import patch
        ob = self.rigs['boneforge']
        self.activate(ob)
        self.p.begin(ob, bpy.context.scene)
        before = self.w.raw_pose(ob)
        ob.b4ml.pose_offset.z = -.05
        real = self.p._aim
        count = [0]
        def fail(*args):
            count[0] += 1
            if count[0] == 3:
                raise RuntimeError('injected')
            return real(*args)
        with patch.object(self.p, '_aim', fail), self.assertRaisesRegex(RuntimeError, 'injected'):
            self.p.solve(ob, bpy.context.scene)
        self.assertEqual(before, self.w.raw_pose(ob))
        self.assertTrue(ob.b4ml.posing_payload)
        self.p.finish(ob, bpy.context.scene, False)
        self.assertFalse(ob.b4ml.pose_targets)

    def test_selective_strength_repeat_and_unreachable(self):
        ob = self.rigs['boneforge']
        self.activate(ob)
        self.p.begin(ob, bpy.context.scene)
        item = ob.b4ml.pose_targets['arm-L']
        item.target.location.x -= .1
        other = ob.b4ml.pose_targets['arm-R']
        other.enabled = False
        ob.b4ml.pose_strength = .5
        bpy.context.view_layer.update()
        result = self.p.solve(ob, bpy.context.scene)
        self.assertNotIn('arm-R', [r['limb'] for r in result])
        first = self.w.raw_pose(ob)
        self.p.solve(ob, bpy.context.scene)
        self.assertEqual(first, self.w.raw_pose(ob))
        ob.b4ml.pose_strength = 0.
        self.p.solve(ob, bpy.context.scene)
        data = json.loads(ob.b4ml.posing_payload)
        actual = ob.pose.bones['hand.def-L'].head
        self.assertLess((actual - __import__('mathutils').Vector(data['limbs'][0]['end'])).length, 1e-5)
        ob.b4ml.pose_strength = 1.
        item.target.location.x = 100.
        bpy.context.view_layer.update()
        result = self.p.solve(ob, bpy.context.scene)
        self.assertTrue(result[0]['clamped'])
        self.assertGreater(result[0]['error'], 90.)
        self.assertIn('limits', ob.b4ml.status)
        self.p.finish(ob, bpy.context.scene, False)

    def test_locks_modes_space_frame_and_deleted_target(self):
        ob = self.rigs['boneforge']
        self.activate(ob)
        ob.scale = (1,2,1)
        bpy.context.view_layer.update()
        with self.assertRaisesRegex(ValueError, 'uniform'):
            self.p.begin(ob, bpy.context.scene)
        ob.scale = (1,1,1)
        pb = ob.pose.bones['upperarm.fk-L']
        bpy.context.view_layer.update()
        pb.lock_rotation[0] = True
        with self.assertRaisesRegex(ValueError, 'locked'):
            self.p.begin(ob, bpy.context.scene)
        pb.lock_rotation[0] = False
        bpy.context.view_layer.update()
        self.p.begin(ob, bpy.context.scene)
        bpy.context.scene.frame_set(2)
        with self.assertRaisesRegex(ValueError, 'starting frame'):
            self.p.solve(ob, bpy.context.scene)
        bpy.context.scene.frame_set(1)
        with self.assertRaisesRegex(ValueError, 'assisted posing'):
            self.w.capture_anchor(ob, bpy.context.scene)
        with self.assertRaisesRegex(ValueError, 'assisted posing'):
            self.w.preview(ob, bpy.context.scene)
        bpy.data.objects.remove(ob.b4ml.pose_targets[0].target, do_unlink=True)
        with self.assertRaisesRegex(ValueError, 'deleted'):
            self.p.solve(ob, bpy.context.scene)
        self.p.finish(ob, bpy.context.scene, False)
        self.assertFalse(ob.b4ml.posing_payload)

    def test_helper_selection_and_operator_lifecycle(self):
        ob = self.rigs['boneforge']
        self.activate(ob)
        self.assertEqual(bpy.ops.b4ml.pose(operation='BEGIN'), {'FINISHED'})
        helper = ob.b4ml.pose_targets[0].target
        self.activate(helper)
        self.assertIs(self.w.active_rig(bpy.context), ob)
        self.assertEqual(bpy.ops.b4ml.pose(operation='SOLVE'), {'FINISHED'})
        self.assertEqual(bpy.ops.b4ml.pose(operation='CANCEL'), {'FINISHED'})
        self.assertFalse(ob.b4ml.posing_payload)

    def test_independent_rigs_and_bound_mesh(self):
        a, b = self.rigs['boneforge'], self.rigs['metarig']
        self.activate(a)
        self.p.begin(a, bpy.context.scene)
        self.activate(b)
        self.p.begin(b, bpy.context.scene)
        self.p.finish(a, bpy.context.scene, False)
        self.assertEqual(len(b.b4ml.pose_targets), 4)
        self.p.finish(b, bpy.context.scene, False)
        mesh = bpy.data.objects.new('Bound posing mesh', bpy.data.meshes.new('Bound mesh'))
        bpy.context.scene.collection.objects.link(mesh)
        mod = mesh.modifiers.new('Rig', 'ARMATURE')
        mod.object = a
        self.activate(mesh)
        self.assertIs(self.w.active_rig(bpy.context), a)
        bpy.data.objects.remove(mesh, do_unlink=True)

    def test_actual_bound_mesh_deformation(self):
        from mathutils import Vector
        ob = self.rigs['boneforge']
        self.activate(ob)
        rest = ob.data.bones['hand.def-L'].head_local.copy()
        data = bpy.data.meshes.new('Weighted reference triangle')
        data.from_pydata([rest, rest+Vector((0,.01,0)), rest+Vector((0,0,.01))], [], [(0,1,2)])
        mesh = bpy.data.objects.new('Weighted reference triangle', data)
        bpy.context.scene.collection.objects.link(mesh)
        group = mesh.vertex_groups.new(name='hand.def-L')
        group.add([0,1,2], 1., 'REPLACE')
        modifier = mesh.modifiers.new('Armature', 'ARMATURE')
        modifier.object = ob
        try:
            self.p.begin(ob, bpy.context.scene)
            ob.b4ml.pose_targets['arm-L'].target.location.x -= .1
            self.p.solve(ob, bpy.context.scene)
            evaluated = mesh.evaluated_get(bpy.context.evaluated_depsgraph_get())
            expected = ob.pose.bones['hand.def-L'].head
            self.assertLess((evaluated.data.vertices[0].co-expected).length, 1e-5)
            self.assertGreater((evaluated.data.vertices[0].co-rest).length, .05)
            self.p.finish(ob, bpy.context.scene, False)
        finally:
            bpy.data.objects.remove(mesh, do_unlink=True)
            bpy.data.meshes.remove(data)

    def test_changed_properties_drivers_and_rollback(self):
        ob = self.rigs['boneforge']
        self.activate(ob)
        self.p.begin(ob, bpy.context.scene)
        ob.pose.bones['properties']['IK_FK-arm-L'] = .5
        with self.assertRaisesRegex(ValueError, 'properties changed'):
            self.p.solve(ob, bpy.context.scene)
        ob.pose.bones['properties']['IK_FK-arm-L'] = 0.
        pb = ob.pose.bones['upperarm.fk-L']
        driver = pb.driver_add('rotation_euler', 0)
        try:
            with self.assertRaisesRegex(ValueError, 'Driven control'):
                self.p.solve(ob, bpy.context.scene)
        finally:
            pb.driver_remove('rotation_euler', 0)
        self.p.finish(ob, bpy.context.scene, False)

    def test_zy_undo_redo_target_session(self):
        ob = self.rigs['boneforge']
        self.activate(ob)
        names = {k:v.name for k,v in self.rigs.items()}
        bpy.ops.ed.undo_push(message='Before assisted pose')
        self.assertEqual(bpy.ops.b4ml.pose(operation='BEGIN'), {'FINISHED'})
        bpy.ops.ed.undo_push(message='Started assisted pose')
        self.assertEqual(bpy.ops.ed.undo(), {'FINISHED'})
        type(self).rigs = {k:bpy.data.objects[n] for k,n in names.items()}
        self.assertFalse(self.rigs['boneforge'].b4ml.posing_payload)
        self.assertEqual(bpy.ops.ed.redo(), {'FINISHED'})
        type(self).rigs = {k:bpy.data.objects[n] for k,n in names.items()}
        ob = self.rigs['boneforge']
        self.assertEqual(len(ob.b4ml.pose_targets), 4)
        self.assertIs(ob.b4ml.pose_targets[0].target['b4ml_owner'], ob)
        self.activate(ob)
        self.p.finish(ob, bpy.context.scene, False)

    def test_zz_save_reload_pending_session(self):
        import tempfile
        ob = self.rigs['boneforge']
        self.activate(ob)
        names = {k:v.name for k,v in self.rigs.items()}
        baseline = self.w.raw_pose(ob, self.w.detect_rig(ob.data.bones.keys()).controls)
        self.p.begin(ob, bpy.context.scene)
        ob.b4ml.pose_offset.z = -.06
        self.p.solve(ob, bpy.context.scene)
        with tempfile.TemporaryDirectory(prefix='b4ml-pose-') as directory:
            path = str(Path(directory)/'session.blend')
            bpy.ops.wm.save_as_mainfile(filepath=path, check_existing=False)
            bpy.ops.wm.open_mainfile(filepath=path, load_ui=False, use_scripts=False)
            type(self).rigs = {k:bpy.data.objects[n] for k,n in names.items()}
            ob = self.rigs['boneforge']
            self.activate(ob)
            self.assertEqual(len(ob.b4ml.pose_targets), 4)
            self.assertIs(ob.b4ml.pose_targets[0].target['b4ml_owner'], ob)
            self.p.solve(ob, bpy.context.scene)
            self.p.finish(ob, bpy.context.scene, False)
            self.assertEqual(baseline, self.w.raw_pose(ob, baseline))
            self.assertFalse(ob.b4ml.pose_targets)

if __name__ == '__main__':
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromName(os.environ['B4ML_TEST'], sys.modules[__name__]) if os.environ.get('B4ML_TEST') else unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__]))
    if os.environ.get('B4ML_METRICS_OUT'):
        import datetime, platform
        report = dict(schema=1, passed=result.wasSuccessful(), tests=result.testsRun, skipped=len(result.skipped),
                      fast_fixtures=bool(os.environ.get('B4ML_FAST')), samples=METRICS,
                      timestamp_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                      processor=platform.processor(),
                      host_version=bpy.app.version_string if bpy else None,
                      host_build_hash=bpy.app.build_hash.decode() if bpy else None,
                      package=os.path.basename(os.environ.get('B4ML_PACKAGE', 'source')))
        Path(os.environ['B4ML_METRICS_OUT']).write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print('B4ML_POSING_RESULT:', 'PASS' if result.wasSuccessful() else 'FAIL', flush=True)
    if not result.wasSuccessful():
        raise RuntimeError('Assisted posing tests failed')
