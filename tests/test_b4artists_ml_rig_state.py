"""Real evaluated-rig state conversion and candidate preservation tests."""
import os
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0, os.environ.get('B4ML_PACKAGE', str(ROOT)))
sys.path.insert(0, str(ROOT/'tests'))
try:
    import bpy
except ImportError:
    bpy=None
if bpy:
    import b4artists_ml
    from b4artists_ml import rig_state as rs, workflow as w
    from test_b4artists_ml_posing import boneforge_rig, rigify_rig

@unittest.skipIf(bpy is None,'Bforartists runtime required')
class RigStateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b4artists_ml.register()
        cls.rigs={'boneforge':boneforge_rig(), 'rigify':rigify_rig()}
        if not os.environ.get('B4ML_FAST'):
            cls.rigs['rigify_full']=rigify_rig(full=True)
        cls.original_poses={k:w.raw_pose(obj) for k,obj in cls.rigs.items()}
        cls.original_modes={k:rs.mode_values(obj) for k,obj in cls.rigs.items()}

    def setUp(self):
        from b4artists_ml import posing
        for name,obj in self.rigs.items():
            bpy.context.view_layer.objects.active=obj
            if obj.b4ml.posing_payload:
                posing.finish(obj,bpy.context.scene,False)
            if obj.b4ml.candidate_action:
                w.finish_preview(obj,bpy.context.scene,False)
            if obj.animation_data:
                obj.animation_data.action=None
            obj.b4ml.anchors.clear()
            w.restore_pose(obj,self.original_poses[name])
            rs.restore_values(obj,self.original_modes[name])
        bpy.context.scene.frame_set(1)

    def test_01_default_ik_conversion(self):
        for name,obj in self.rigs.items():
            with self.subTest(rig=name):
                bpy.context.view_layer.objects.active=obj
                modes=rs.mode_bindings(obj)
                original=rs.mode_values(obj)
                for row in modes:
                    obj.pose.bones[row['property_bone']][row['key']]=1.-row['fk_value']
                obj.update_tag(refresh={'OBJECT'})
                bpy.context.view_layer.update()
                before=w.raw_pose(obj)
                snapshot=rs.normalize_fk(obj)
                print('FK_CONVERSION',name,snapshot['max_position_error'])
                self.assertLess(snapshot['max_position_error'],2e-4)
                rs.restore_snapshot(obj,snapshot)
                after=w.raw_pose(obj)
                for row in modes:
                    for control in row['controls']:
                        self.assertEqual(before[control],after[control])
                rs.restore_values(obj,original)

    def test_02_ik_anchor_candidate_restore(self):
        for name,obj in self.rigs.items():
            with self.subTest(rig=name):
                bpy.context.view_layer.objects.active=obj
                rows=rs.mode_bindings(obj)
                for row in rows:
                    obj.pose.bones[row['property_bone']][row['key']]=1.-row['fk_value']
                obj.update_tag(refresh={'OBJECT'})
                bpy.context.view_layer.update()
                modes=rs.mode_values(obj)
                obj.b4ml.anchors.clear()
                scene=bpy.context.scene
                scene.frame_set(1)
                root=obj.pose.bones['torso' if name.startswith('rigify') else 'hips']
                root.keyframe_insert('location',frame=1)
                root.location.x += .1
                root.keyframe_insert('location',frame=11)
                source=obj.animation_data.action
                expected={}
                for frame in (1,11):
                    scene.frame_set(frame)
                    expected[frame]={j:obj.pose.bones[j].matrix.copy() for row in rows for j in row['joints']}
                    w.capture_anchor(obj,scene)
                    self.assertEqual(modes,rs.mode_values(obj))
                w.preview(obj,scene)
                self.assertIsNot(obj.animation_data.action,source)
                for frame in (1,11):
                    scene.frame_set(frame)
                    self.assertEqual(rs.mode_values(obj),rs.canonical_modes(obj))
                    for j,matrix in expected[frame].items():
                        self.assertLess((obj.pose.bones[j].head-matrix.translation).length,2e-4,j)
                scene.frame_set(12)
                self.assertEqual(rs.mode_values(obj),modes)
                scene.frame_set(5)
                w.finish_preview(obj,scene,keep=False)
                self.assertIs(obj.animation_data.action,source)
                self.assertEqual(rs.mode_values(obj),modes)
                w.preview(obj,scene)
                w.finish_preview(obj,scene,keep=True)
                candidate=obj.animation_data.action
                w.restore_kept_source(obj,scene)
                self.assertIs(obj.animation_data.action,source)
                self.assertEqual(rs.mode_values(obj),modes)
                self.assertTrue(candidate.use_fake_user)

    def test_03_default_ik_assisted_pose(self):
        from b4artists_ml import posing
        for name,obj in self.rigs.items():
            with self.subTest(rig=name):
                bpy.context.view_layer.objects.active=obj
                scene=bpy.context.scene
                scene.frame_set(1)
                for row in rs.mode_bindings(obj):
                    obj.pose.bones[row['property_bone']][row['key']]=1.-row['fk_value']
                obj.update_tag(refresh={'OBJECT'})
                bpy.context.view_layer.update()
                original_modes=rs.mode_values(obj)
                original=w.raw_pose(obj)
                posing.begin(obj,scene)
                self.assertEqual(rs.mode_values(obj),rs.canonical_modes(obj))
                obj.b4ml.pose_targets['arm-L'].target.location.x -= .06
                results=posing.solve(obj,scene)
                self.assertLess(results[0]['error'],2e-4)
                posing.finish(obj,scene,keep=True)
                self.assertEqual(original_modes,rs.mode_values(obj))
                for control, values in original.items():
                    if control in __import__('b4artists_ml.rigs',fromlist=['detect_rig']).detect_rig(obj.data.bones.keys()).controls:
                        self.assertEqual(values,w.raw_pose(obj,[control])[control])

    def test_04_moved_rigify_ik_and_source_channels(self):
        from b4artists_ml import posing
        obj=self.rigs['rigify']
        bpy.context.view_layer.objects.active=obj
        obj.animation_data.action=None
        for row in rs.mode_bindings(obj):
            obj.pose.bones[row['property_bone']][row['key']]=1.-row['fk_value']
        hand=obj.pose.bones['hand_ik.L']
        hand.location.z += .15
        obj.update_tag(refresh={'OBJECT'})
        bpy.context.view_layer.update()
        before=w.raw_pose(obj)
        snapshot=rs.normalize_fk(obj)
        self.assertLess(snapshot['max_position_error'],2e-4)
        rs.restore_snapshot(obj,snapshot)
        posing.begin(obj,bpy.context.scene)
        obj.b4ml.pose_targets['arm-L'].target.location.x -= .025
        result=posing.solve(obj,bpy.context.scene)
        self.assertLess(result[0]['error'],2e-4)
        posing.finish(obj,bpy.context.scene,False)
        self.assertEqual(before['hand_ik.L'],w.raw_pose(obj)['hand_ik.L'])

    def test_05_animated_modes_and_exact_source_preservation(self):
        obj=self.rigs['boneforge']
        bpy.context.view_layer.objects.active=obj
        obj.animation_data.action=None
        obj.b4ml.anchors.clear()
        scene=bpy.context.scene
        rows=rs.mode_bindings(obj)
        for frame,value in ((1,0.),(11,1.)):
            scene.frame_set(frame)
            for row in rows:
                pb=obj.pose.bones[row['property_bone']]
                pb[row['key']]=value
                pb.keyframe_insert('['+__import__('json').dumps(row['key'])+']',frame=frame)
            obj.update_tag(refresh={'OBJECT'})
            bpy.context.view_layer.update()
            w.capture_anchor(obj,scene)
        source=obj.animation_data.action
        curves=w.action_curves(source,obj.animation_data.action_slot)
        original=[(c.data_path,[(tuple(k.co),tuple(k.handle_left),tuple(k.handle_right),k.interpolation) for k in c.keyframe_points]) for c in curves]
        w.preview(obj,scene)
        scene.frame_set(6)
        self.assertEqual(rs.mode_values(obj),rs.canonical_modes(obj))
        w.finish_preview(obj,scene,False)
        self.assertEqual(original,[(c.data_path,[(tuple(k.co),tuple(k.handle_left),tuple(k.handle_right),k.interpolation) for k in c.keyframe_points]) for c in curves])
        self.assertTrue(all(.1 < value < .9 for props in rs.mode_values(obj).values() for value in props.values()))

    def test_06_normalization_failure_restores_input(self):
        from unittest.mock import patch
        obj=self.rigs['rigify']
        bpy.context.view_layer.objects.active=obj
        obj.animation_data.action=None
        for row in rs.mode_bindings(obj):
            obj.pose.bones[row['property_bone']][row['key']]=1.-row['fk_value']
        obj.update_tag(refresh={'OBJECT'})
        bpy.context.view_layer.update()
        before=w.raw_pose(obj)
        modes=rs.mode_values(obj)
        real=w._channels
        def fail(pb):
            if pb.name=='forearm_fk.L' and obj.pose.bones['upper_arm_parent.L']['IK_FK']==1.:
                raise RuntimeError('injected FK conversion failure')
            return real(pb)
        # Inject after mode switching and after the first matched controls.
        with patch.object(w,'_channels',fail),self.assertRaisesRegex(RuntimeError,'injected'):
            rs.normalize_fk(obj)
        self.assertEqual(modes,rs.mode_values(obj))
        for row in rs.mode_bindings(obj):
            for name in row['controls']:
                self.assertEqual(before[name],w.raw_pose(obj,[name])[name])

    def test_07_all_deform_weighted_samples_survive_conversion(self):
        for name,obj in self.rigs.items():
            with self.subTest(rig=name):
                bpy.context.view_layer.objects.active=obj
                for row in rs.mode_bindings(obj):
                    obj.pose.bones[row['property_bone']][row['key']]=1.-row['fk_value']
                ctrl='hand_ik.L' if name.startswith('rigify') else 'forearm.ik-L'
                obj.pose.bones[ctrl].location.z += .12
                obj.update_tag(refresh={'OBJECT'})
                bpy.context.view_layer.update()
                bones=[b for b in obj.data.bones if b.use_deform]
                mesh=bpy.data.meshes.new('Deform samples')
                points=[tuple(p) for b in bones for p in (b.head_local,b.tail_local)]
                mesh.from_pydata(points,[],[])
                probe=bpy.data.objects.new('Deform samples',mesh)
                bpy.context.scene.collection.objects.link(probe)
                for i,bone in enumerate(bones):
                    group=probe.vertex_groups.new(name=bone.name)
                    group.add([2*i,2*i+1],1.,'REPLACE')
                probe.modifiers.new('Rig','ARMATURE').object=obj
                bpy.context.view_layer.update()
                evaluated=probe.evaluated_get(bpy.context.evaluated_depsgraph_get())
                expected=[v.co.copy() for v in evaluated.data.vertices]
                snapshot=None
                try:
                    snapshot=rs.normalize_fk(obj)
                    evaluated=probe.evaluated_get(bpy.context.evaluated_depsgraph_get())
                    error=max((v.co-before).length for v,before in zip(evaluated.data.vertices,expected))
                    print('DEFORM_CONVERSION',name,len(points),error)
                    self.assertLess(error,2e-4)
                finally:
                    rs.restore_snapshot(obj,snapshot)
                    bpy.data.objects.remove(probe,do_unlink=True)
                    bpy.data.meshes.remove(mesh)

    def test_zy_saved_kept_candidate_restores_source_modes(self):
        import tempfile
        obj=self.rigs['rigify']
        bpy.context.view_layer.objects.active=obj
        scene=bpy.context.scene
        original_modes=rs.mode_values(obj)
        for frame in (1,11):
            scene.frame_set(frame)
            w.capture_anchor(obj,scene)
        w.preview(obj,scene)
        w.finish_preview(obj,scene,True)
        names={k:v.name for k,v in self.rigs.items()}
        with tempfile.TemporaryDirectory(prefix='b4ml-kept-') as directory:
            path=str(Path(directory)/'kept.blend')
            bpy.ops.wm.save_as_mainfile(filepath=path,check_existing=False)
            bpy.ops.wm.open_mainfile(filepath=path,load_ui=False,use_scripts=False)
            type(self).rigs={k:bpy.data.objects[v] for k,v in names.items()}
            obj=self.rigs['rigify']
            bpy.context.view_layer.objects.active=obj
            self.assertEqual(bpy.ops.b4ml.action(operation='RESTORE_SOURCE'),{'FINISHED'})
            self.assertIsNone(obj.animation_data.action)
            self.assertEqual(original_modes,rs.mode_values(obj))

    def test_zz_saved_ik_session_reenters_fk(self):
        import tempfile
        from b4artists_ml import posing
        obj=self.rigs['boneforge']
        bpy.context.view_layer.objects.active=obj
        scene=bpy.context.scene
        for frame,value in ((1,0.),(11,1.)):
            for row in rs.mode_bindings(obj):
                pb=obj.pose.bones[row['property_bone']]
                pb[row['key']]=value
                pb.keyframe_insert('['+__import__('json').dumps(row['key'])+']',frame=frame)
        scene.frame_set(11)
        modes=rs.mode_values(obj)
        self.assertNotEqual(modes,rs.canonical_modes(obj))
        posing.begin(obj,scene)
        posing.solve(obj,scene)
        names={k:v.name for k,v in self.rigs.items()}
        with tempfile.TemporaryDirectory(prefix='b4ml-ik-') as directory:
            path=str(Path(directory)/'session.blend')
            bpy.ops.wm.save_as_mainfile(filepath=path,check_existing=False)
            bpy.ops.wm.open_mainfile(filepath=path,load_ui=False,use_scripts=False)
            type(self).rigs={k:bpy.data.objects[v] for k,v in names.items()}
            obj=self.rigs['boneforge']
            bpy.context.view_layer.objects.active=obj
            posing.solve(obj,bpy.context.scene)
            posing.finish(obj,bpy.context.scene,False)
            self.assertEqual(modes,rs.mode_values(obj))

if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__]))
    print('B4ML_RIG_STATE_RESULT:', 'PASS' if result.wasSuccessful() else 'FAIL', flush=True)
    if not result.wasSuccessful():
        raise RuntimeError('Rig-state tests failed')
