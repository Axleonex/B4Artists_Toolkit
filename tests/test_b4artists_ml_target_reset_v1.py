"""Per-target preview-start reset coverage for whole-body posing."""
from pathlib import Path
from types import SimpleNamespace
import json,os,sys,unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[os.environ.get('B4ML_PACKAGE',str(ROOT)),str(ROOT/'tests'),str(ROOT/'training/b4artists_ml')]
import bpy
from mathutils import Quaternion
import b4artists_ml
from b4artists_ml import body_preview as body,body_live,workflow as w,posing,rig_state as rs,ui
from test_b4artists_ml_context_rig import ContextRigTests
from test_b4artists_ml_imported_humanoids import authored

RECORDS=[]


class TargetResetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b4artists_ml.register();ContextRigTests.setUpClass();cls.fixtures=ContextRigTests()

    def tearDown(self):
        for ob in list(bpy.data.objects):
            if hasattr(ob,'b4ml') and ob.b4ml.body_payload:
                if ob.users_scene:bpy.context.window.scene=ob.users_scene[0]
                body.finish(ob,bpy.context.scene,False)
        body.reset_runtime()

    def _rig(self,label):
        if label=='unity_humanoid_fbx':
            ob,mesh,roles=authored('unity_humanoid',1)
            return ob,w.raw_pose(ob)
        ob,source,session,targets,mask=self.fixtures.fixture(label,transformed=True)
        session.cancel()
        return ob,source

    def test_reset_restores_owned_helper_transforms_on_supported_rigs(self):
        for label in ('boneforge','rigify_default','unity_humanoid_fbx'):
            with self.subTest(rig=label):
                ob,source=self._rig(label);bpy.context.view_layer.objects.active=ob
                body.begin(ob,bpy.context.scene);bpy.context.view_layer.update()
                self.assertEqual(json.loads(ob.b4ml.body_payload)['controls_version'],5)
                item=ob.b4ml.body_targets['Hand L']
                target_start=item.target.matrix_world.copy();pole_start=item.pole.matrix_world.copy()
                before=w.raw_pose(ob)
                item.target.location.x+=.23
                item.target.rotation_quaternion.rotate(Quaternion((0,0,1),.27))
                item.target.scale=(1.3,.8,1.1)
                item.pole.location.y-=.19
                item.pole.rotation_euler=(.2,.1,-.3)
                item.pole.scale=(.7,1.4,.9)
                item.enabled=False;item.use_orientation=True;item.use_pole=True
                bpy.context.view_layer.update()
                result=body.reset_target(ob,'Hand L')
                self.assertEqual(w.raw_pose(ob),before)
                self.assertLess((item.target.matrix_world.translation-target_start.translation).length,1e-8)
                self.assertLess(body.solver._angle(item.target.matrix_world.to_quaternion(),
                                                   target_start.to_quaternion()),1e-6)
                self.assertTrue(body.np.allclose(item.target.scale,(1.,1.,1.),atol=1e-6))
                self.assertLess((item.pole.matrix_world.translation-pole_start.translation).length,1e-8)
                self.assertLess(body.solver._angle(item.pole.matrix_world.to_quaternion(),
                                                   pole_start.to_quaternion()),1e-6)
                self.assertTrue(body.np.allclose(item.pole.scale,(1.,1.,1.),atol=1e-6))
                self.assertFalse(item.enabled);self.assertTrue(item.use_orientation);self.assertTrue(item.use_pole)
                self.assertTrue(result['orientation']);self.assertTrue(result['pole'])
                RECORDS.append(dict(fixture=label,target='Hand L',pose_unchanged=True,
                                    toggles_preserved=True,evaluated_matrices_verified=True))
                body.finish(ob,bpy.context.scene,False)
                self.assertEqual(w.raw_pose(ob),source)

    def test_reset_rejects_foreign_transform_sources_before_mutation(self):
        ob,source=self._rig('boneforge');bpy.context.view_layer.objects.active=ob
        body.begin(ob,bpy.context.scene);item=ob.b4ml.body_targets['Foot R']
        parent=bpy.data.objects.new('Reset rejection parent',None);bpy.context.scene.collection.objects.link(parent)
        cases=[]
        item.target.parent=parent;cases.append(('parented','parented'))
        for label,message in cases:
            before=item.target.matrix_world.copy();pose=w.raw_pose(ob)
            with self.assertRaisesRegex(ValueError,message):body.reset_target(ob,'Foot R')
            self.assertTrue(body.np.allclose(item.target.matrix_world,before));self.assertEqual(w.raw_pose(ob),pose)
        item.target.parent=None
        item.target.delta_location.x=.1;before=item.target.matrix_world.copy()
        with self.assertRaisesRegex(ValueError,'delta transforms'):body.reset_target(ob,'Foot R')
        self.assertTrue(body.np.allclose(item.target.matrix_world,before));item.target.delta_location=(0,0,0)
        constraint=item.target.constraints.new('COPY_LOCATION');constraint.target=parent
        with self.assertRaisesRegex(ValueError,'constraints'):body.reset_target(ob,'Foot R')
        item.target.constraints.remove(constraint)
        item.target.keyframe_insert(data_path='location',frame=1)
        with self.assertRaisesRegex(ValueError,'animated or driven'):body.reset_target(ob,'Foot R')
        item.target.animation_data_clear()
        item.target.driver_add('location',0);before=item.target.matrix_world.copy();pose=w.raw_pose(ob)
        with self.assertRaisesRegex(ValueError,'animated or driven'):body.reset_target(ob,'Foot R')
        self.assertTrue(body.np.allclose(item.target.matrix_world,before));self.assertEqual(w.raw_pose(ob),pose)
        item.target.animation_data_clear();bpy.data.objects.remove(parent,do_unlink=True)

    def test_reset_validates_all_ownership_before_mutation(self):
        ob,source=self._rig('boneforge');bpy.context.view_layer.objects.active=ob
        body.begin(ob,bpy.context.scene);before=w.raw_pose(ob)
        item=ob.b4ml.body_targets['Foot R'];item.target.location.x+=.12
        changed=item.target.location.copy();item.pole['b4ml_session']='replaced'
        with self.assertRaisesRegex(ValueError,'Pole target is missing or replaced'):
            body.reset_target(ob,'Foot R')
        self.assertLess((item.target.location-changed).length,1e-12)
        with self.assertRaisesRegex(ValueError,'Unknown whole-body target'):
            body.reset_target(ob,'Tail')
        self.assertEqual(w.raw_pose(ob),before)

    def test_foreign_solver_owner_survives_recovery_rejection(self):
        class ForeignOwner:pass
        ob,source=self._rig('boneforge');bpy.context.view_layer.objects.active=ob
        body.begin(ob,bpy.context.scene);item=ob.b4ml.body_targets['Hand L'];before=item.target.matrix_world.copy();pose=w.raw_pose(ob)
        body.reset_runtime();foreign=ForeignOwner();body.solver._SESSIONS[ob.as_pointer()]=foreign
        try:
            with self.assertRaisesRegex(ValueError,'Another solver owns this rig'):
                body.reset_target(ob,'Hand L')
            self.assertIs(body.solver._SESSIONS.get(ob.as_pointer()),foreign)
            self.assertTrue(body.np.allclose(item.target.matrix_world,before));self.assertEqual(w.raw_pose(ob),pose)
        finally:body.solver._SESSIONS.pop(ob.as_pointer(),None)

    def test_malformed_metadata_does_not_recover_or_mutate_rig(self):
        ob,source=self._rig('rigify_basic');bpy.context.view_layer.objects.active=ob
        body.begin(ob,bpy.context.scene);bpy.context.view_layer.update();record=json.loads(ob.b4ml.body_payload)
        target=ob.b4ml.body_targets['Head'].target;target_before=target.matrix_world.copy()
        body.reset_runtime()
        control=ob.pose.bones[record['session']['binding']['controls'][0]]
        control.location.x+=.071;posing._update(ob);pose_before=w.raw_pose(ob);modes_before=rs.mode_values(ob)
        record['target_origins']['Head']=[0.,1.]
        record.get('target_matrices',{}).pop('Head',None)
        ob.b4ml.body_payload=json.dumps(record)
        with self.assertRaisesRegex(ValueError,'Invalid saved whole-body target'):
            body.reset_target(ob,'Head')
        self.assertEqual(w.raw_pose(ob),pose_before);self.assertEqual(rs.mode_values(ob),modes_before)
        self.assertTrue(body.np.allclose(target.matrix_world,target_before))
        self.assertNotIn(ob.as_pointer(),body._LIVE)
        self.assertNotIn(ob.as_pointer(),body.solver._SESSIONS)

    def test_running_and_live_solves_are_refused(self):
        ob,source=self._rig('rigify_basic');bpy.context.view_layer.objects.active=ob
        body.begin(ob,bpy.context.scene);before=w.raw_pose(ob)
        body.start(ob)
        with self.assertRaisesRegex(ValueError,'running solve'):body.reset_target(ob,'Head')
        body.abort(ob);self.assertEqual(w.raw_pose(ob),before)
        body_live.start(ob,now=0.)
        with self.assertRaisesRegex(ValueError,'Stop Live Solve'):body.reset_target(ob,'Head')
        body_live.stop(ob);self.assertFalse(ob.b4ml.body_live)

    def test_version_one_serialized_recovery_and_stale_keep_gate(self):
        ob,source=self._rig('rigify_basic');bpy.context.view_layer.objects.active=ob
        body.begin(ob,bpy.context.scene)
        record=json.loads(ob.b4ml.body_payload);record['controls_version']=1
        record['target_origins'].pop('Chest');record.pop('target_matrices',None);record.pop('pole_matrices',None)
        ob.b4ml.body_payload=json.dumps(record)
        index=ob.b4ml.body_targets.find('Chest');ob.b4ml.body_targets.remove(index)
        head=ob.b4ml.body_targets['Head'];start=record['target_origins']['Head'];head.target.location.x+=.08
        body.reset_runtime();before=w.raw_pose(ob)
        body.reset_target(ob,'Head')
        self.assertEqual(w.raw_pose(ob),before)
        self.assertLess(max(abs(head.target.location[i]-start[i]) for i in range(3)),1e-8)
        self.assertIn(ob.as_pointer(),body._LIVE)
        head.target.location.x+=.06;bpy.context.view_layer.update();body.solve(ob)
        preview=w.raw_pose(ob);body.reset_target(ob,'Head');self.assertEqual(w.raw_pose(ob),preview)
        with self.assertRaisesRegex(ValueError,'Solve the current targets'):
            body.finish(ob,bpy.context.scene,True)
        body.solve(ob);body.finish(ob,bpy.context.scene,True)
        self.assertEqual(w.raw_pose(ob),source);self.assertEqual(len(ob.b4ml.anchors),1)

    def test_target_row_wires_name_and_runtime_gate(self):
        class FakeRow:
            def __init__(self):self.child=None;self.call=None;self.op=None;self.enabled=True
            def row(self,align=False):self.child=FakeRow();return self.child
            def operator(self,*args,**kwargs):
                self.call=(args,kwargs);self.op=SimpleNamespace();return self.op
        row=FakeRow();operator=ui._draw_body_target_reset(row,'Hand L',False)
        self.assertFalse(row.child.enabled)
        self.assertEqual(row.child.call,(('b4ml.body',),{'text':'Reset'}))
        self.assertEqual(operator.operation,'RESET_TARGET');self.assertEqual(operator.target_name,'Hand L')


if __name__=='__main__':
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(TargetResetTests)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    report=dict(tests=result.testsRun,passed=result.wasSuccessful(),failures=len(result.failures),
                errors=len(result.errors),records=RECORDS,package=b4artists_ml.__file__)
    path=ROOT/'training/b4artists_ml/results'/os.environ.get('B4ML_TARGET_RESET_RESULT','target-reset-v1.json')
    path.write_text(json.dumps(report,indent=2)+'\n')
    print('TARGET_RESET_RESULT: '+json.dumps(report),flush=True)
    if not result.wasSuccessful():raise SystemExit(1)
