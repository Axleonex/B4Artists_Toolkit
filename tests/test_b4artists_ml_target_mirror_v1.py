"""Semantic left/right helper mirroring for whole-body posing."""
from pathlib import Path
from types import SimpleNamespace
import json,os,sys,unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[os.environ.get('B4ML_PACKAGE',str(ROOT)),str(ROOT/'tests'),str(ROOT/'training/b4artists_ml')]
import bpy
import numpy as np
from mathutils import Matrix,Quaternion,Vector
import b4artists_ml
from b4artists_ml import body_preview as body,workflow as w,ui
from test_b4artists_ml_context_rig import ContextRigTests
from test_b4artists_ml_imported_humanoids import authored

RECORDS=[]


def _matrix(value):return Matrix(value)


def _frame(record):
    basis=np.asarray(record['session']['basis'],float)
    motion=_matrix(record['motion_transform']).to_quaternion().to_matrix()
    return np.asarray(motion,float)@basis


class TargetMirrorTests(unittest.TestCase):
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
            ob,mesh,roles=authored('unity_humanoid',1);return ob,w.raw_pose(ob)
        ob,source,session,targets,mask=self.fixtures.fixture(label,transformed=True)
        session.cancel();return ob,source

    def _assert_semantic_delta(self,record,source,destination,source_start,destination_start):
        frame=_frame(record)
        source_delta=frame.T@np.asarray(source.matrix_world.translation-source_start.translation,float)
        destination_delta=frame.T@np.asarray(destination.matrix_world.translation-destination_start.translation,float)
        self.assertTrue(np.allclose(destination_delta,source_delta*(-1.,1.,1.),atol=1e-7),
                        (source.name,destination.name,source_delta,destination_delta))
        reflection=frame@np.diag((-1.,1.,1.))@frame.T
        source_rotation=np.asarray(source.matrix_world.to_3x3(),float)
        source_origin=np.asarray(source_start.to_3x3(),float)
        destination_origin=np.asarray(destination_start.to_3x3(),float)
        expected=reflection@(source_rotation@source_origin.T)@reflection@destination_origin
        self.assertTrue(np.allclose(np.asarray(destination.matrix_world.to_3x3(),float),expected,atol=1e-6))

    def test_left_to_right_mirrors_targets_and_poles_on_supported_rigs(self):
        for label in ('boneforge','rigify_default','unity_humanoid_fbx'):
            with self.subTest(rig=label):
                ob,source_pose=self._rig(label);bpy.context.view_layer.objects.active=ob
                body.begin(ob,bpy.context.scene);record=json.loads(ob.b4ml.body_payload)
                pose_before=w.raw_pose(ob);source_matrices={};destination_toggles={}
                for source_label,destination_label in body.MIRROR_PAIRS:
                    left=ob.b4ml.body_targets[source_label];right=ob.b4ml.body_targets[destination_label]
                    left.target.location+=Vector((.13,-.07,.05))
                    left.target.rotation_quaternion=Quaternion((0.,0.,1.),.23)@left.target.rotation_quaternion
                    left.pole.location+=Vector((-.04,.09,.03))
                    right.enabled=False;right.use_orientation=True;right.use_pole=False
                    bpy.context.view_layer.update()
                    source_matrices[source_label]=(left.target.matrix_world.copy(),left.pole.matrix_world.copy())
                    destination_toggles[destination_label]=(right.enabled,right.use_orientation,right.use_pole)
                bpy.context.view_layer.update()
                result=body.mirror_targets(ob,'LEFT_TO_RIGHT')
                self.assertEqual(w.raw_pose(ob),pose_before);self.assertEqual(result['targets'],2);self.assertEqual(result['poles'],2)
                for source_label,destination_label in body.MIRROR_PAIRS:
                    left=ob.b4ml.body_targets[source_label];right=ob.b4ml.body_targets[destination_label]
                    left_start=_matrix(record['target_matrices'][source_label]);right_start=_matrix(record['target_matrices'][destination_label])
                    self._assert_semantic_delta(record,left.target,right.target,left_start,right_start)
                    pole_left=_matrix(record['pole_matrices'][source_label]);pole_right=_matrix(record['pole_matrices'][destination_label])
                    frame=_frame(record)
                    source_delta=frame.T@np.asarray(left.pole.matrix_world.translation-pole_left.translation,float)
                    destination_delta=frame.T@np.asarray(right.pole.matrix_world.translation-pole_right.translation,float)
                    self.assertTrue(np.allclose(destination_delta,source_delta*(-1.,1.,1.),atol=1e-7))
                    self.assertTrue(np.allclose(np.asarray(left.target.matrix_world),np.asarray(source_matrices[source_label][0])))
                    self.assertTrue(np.allclose(np.asarray(left.pole.matrix_world),np.asarray(source_matrices[source_label][1])))
                    self.assertEqual((right.enabled,right.use_orientation,right.use_pole),destination_toggles[destination_label])
                RECORDS.append(dict(fixture=label,direction='LEFT_TO_RIGHT',pose_unchanged=True,
                                    targets=2,poles=2,toggles_preserved=True))
                body.finish(ob,bpy.context.scene,False);self.assertEqual(w.raw_pose(ob),source_pose)

    def test_right_to_left_recovers_a_serialized_version_one_preview(self):
        ob,source_pose=self._rig('rigify_basic');bpy.context.view_layer.objects.active=ob
        body.begin(ob,bpy.context.scene);bpy.context.view_layer.update();record=json.loads(ob.b4ml.body_payload)
        starts={name:ob.b4ml.body_targets[name].target.matrix_world.copy() for _,name in body.TARGETS_V1}
        for name in ('Hand R','Foot R'):
            item=ob.b4ml.body_targets[name];item.target.location+=Vector((-.11,.06,.025));item.pole.location.y-=.08
        bpy.context.view_layer.update()
        record['controls_version']=1;record.pop('target_matrices');record.pop('pole_matrices')
        ob.b4ml.body_payload=json.dumps(record);chest=ob.b4ml.body_targets.find('Chest');ob.b4ml.body_targets.remove(chest)
        body.reset_runtime();pose_before=w.raw_pose(ob)
        result=body.mirror_targets(ob,'RIGHT_TO_LEFT')
        self.assertEqual(result['controls_version'],1);self.assertEqual(w.raw_pose(ob),pose_before)
        for left_label,right_label in body.MIRROR_PAIRS:
            left=ob.b4ml.body_targets[left_label];right=ob.b4ml.body_targets[right_label]
            self._assert_semantic_delta(record,right.target,left.target,starts[right_label],starts[left_label])
        body.finish(ob,bpy.context.scene,False);self.assertEqual(w.raw_pose(ob),source_pose)

    def test_external_helpers_and_malformed_body_frame_fail_atomically(self):
        ob,source_pose=self._rig('boneforge');bpy.context.view_layer.objects.active=ob
        body.begin(ob,bpy.context.scene);right=ob.b4ml.body_targets['Hand R'];before=right.target.matrix_world.copy();pose=w.raw_pose(ob)
        parent=bpy.data.objects.new('Mirror rejection parent',None);bpy.context.scene.collection.objects.link(parent);right.target.parent=parent
        with self.assertRaisesRegex(ValueError,'parented'):body.mirror_targets(ob,'LEFT_TO_RIGHT')
        self.assertTrue(body.np.allclose(right.target.matrix_world,before));self.assertEqual(w.raw_pose(ob),pose)
        right.target.parent=None;bpy.data.objects.remove(parent,do_unlink=True)
        original=ob.b4ml.body_payload;record=json.loads(original);record['session']['basis'][0][0]=float('nan')
        ob.b4ml.body_payload=json.dumps(record);body.reset_runtime();before=right.target.matrix_world.copy();pose=w.raw_pose(ob)
        with self.assertRaisesRegex(ValueError,'Invalid saved body frame'):body.mirror_targets(ob,'LEFT_TO_RIGHT')
        self.assertTrue(body.np.allclose(right.target.matrix_world,before));self.assertEqual(w.raw_pose(ob),pose)
        self.assertNotIn(ob.as_pointer(),body._LIVE);self.assertIsNone(body.solver._SESSIONS.get(ob.as_pointer()))
        record=json.loads(original);motion=Matrix(record['motion_transform'])@Matrix.Diagonal((2.,1.,1.,1.))
        record['motion_transform']=[list(row) for row in motion];ob.b4ml.body_payload=json.dumps(record)
        with self.assertRaisesRegex(ValueError,'uniform-scale'):body.mirror_targets(ob,'LEFT_TO_RIGHT')
        self.assertTrue(body.np.allclose(right.target.matrix_world,before));self.assertEqual(w.raw_pose(ob),pose)
        self.assertNotIn(ob.as_pointer(),body._LIVE);self.assertIsNone(body.solver._SESSIONS.get(ob.as_pointer()))
        ob.b4ml.body_payload=original

    def test_foreign_solver_owner_survives_recovery_rejection(self):
        class ForeignOwner:pass
        ob,source_pose=self._rig('boneforge');bpy.context.view_layer.objects.active=ob
        body.begin(ob,bpy.context.scene);right=ob.b4ml.body_targets['Hand R'];before=right.target.matrix_world.copy();pose=w.raw_pose(ob)
        body.reset_runtime();foreign=ForeignOwner();body.solver._SESSIONS[ob.as_pointer()]=foreign
        try:
            with self.assertRaisesRegex(ValueError,'Another solver owns this rig'):
                body.mirror_targets(ob,'LEFT_TO_RIGHT')
            self.assertIs(body.solver._SESSIONS.get(ob.as_pointer()),foreign)
            self.assertTrue(body.np.allclose(right.target.matrix_world,before));self.assertEqual(w.raw_pose(ob),pose)
        finally:body.solver._SESSIONS.pop(ob.as_pointer(),None)

    def test_running_live_and_unknown_directions_are_refused(self):
        ob,source_pose=self._rig('boneforge');bpy.context.view_layer.objects.active=ob;body.begin(ob,bpy.context.scene)
        before=ob.b4ml.body_targets['Hand R'].target.matrix_world.copy();pose=w.raw_pose(ob)
        with self.assertRaisesRegex(ValueError,'Unknown'):body.mirror_targets(ob,'SIDEWAYS')
        ob.b4ml.body_running=True
        with self.assertRaisesRegex(ValueError,'running solve'):body.mirror_targets(ob,'LEFT_TO_RIGHT')
        ob.b4ml.body_running=False;ob.b4ml.body_live=True
        with self.assertRaisesRegex(ValueError,'Stop Live Solve'):body.mirror_targets(ob,'LEFT_TO_RIGHT')
        ob.b4ml.body_live=False
        self.assertTrue(body.np.allclose(ob.b4ml.body_targets['Hand R'].target.matrix_world,before));self.assertEqual(w.raw_pose(ob),pose)

    def test_stale_keep_gate_tracks_only_active_mirrored_requests(self):
        def feasible_preview():
            ob,source_pose,session,targets,mask=self.fixtures.fixture('boneforge',transformed=True)
            session.cancel();bpy.context.view_layer.objects.active=ob;body.begin(ob,bpy.context.scene)
            for index,label in body.TARGETS:ob.b4ml.body_targets[label].target.location=targets[index]
            bpy.context.view_layer.update();return ob,source_pose
        ob,source_pose=feasible_preview();body.solve(ob)
        ob.b4ml.body_targets['Hand L'].target.location.x+=.015;bpy.context.view_layer.update()
        body.mirror_targets(ob,'LEFT_TO_RIGHT')
        with self.assertRaisesRegex(ValueError,'Solve the current targets'):
            body.finish(ob,bpy.context.scene,True)
        body.finish(ob,bpy.context.scene,False);self.assertEqual(w.raw_pose(ob),source_pose)

        ob,source_pose=feasible_preview()
        for source_label,destination_label in body.MIRROR_PAIRS:
            for label in (source_label,destination_label):
                item=ob.b4ml.body_targets[label];item.enabled=False;item.use_orientation=False;item.use_pole=False
        body.solve(ob)
        for source_label,_ in body.MIRROR_PAIRS:
            item=ob.b4ml.body_targets[source_label];item.target.location.x+=.015;item.pole.location.y+=.01
        bpy.context.view_layer.update();body.mirror_targets(ob,'LEFT_TO_RIGHT')
        body.finish(ob,bpy.context.scene,True)
        self.assertEqual(len(ob.b4ml.anchors),1);self.assertEqual(w.raw_pose(ob),source_pose)

    def test_ui_wires_both_directions(self):
        class FakeRow:
            def __init__(self):self.calls=[]
            def operator(self,*args,**kwargs):
                op=SimpleNamespace();self.calls.append((args,kwargs,op));return op
        row=FakeRow();left=ui._draw_body_mirror(row,'LEFT_TO_RIGHT','Mirror L to R')
        right=ui._draw_body_mirror(row,'RIGHT_TO_LEFT','Mirror R to L')
        self.assertEqual([call[:2] for call in row.calls],[(('b4ml.body',),{'text':'Mirror L to R'}),(('b4ml.body',),{'text':'Mirror R to L'})])
        self.assertEqual((left.operation,left.mirror_direction),('MIRROR_TARGETS','LEFT_TO_RIGHT'))
        self.assertEqual((right.operation,right.mirror_direction),('MIRROR_TARGETS','RIGHT_TO_LEFT'))


if __name__=='__main__':
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(TargetMirrorTests)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    report=dict(tests=result.testsRun,passed=result.wasSuccessful(),failures=len(result.failures),
                errors=len(result.errors),records=RECORDS,package=b4artists_ml.__file__)
    path=ROOT/'training/b4artists_ml/results'/os.environ.get('B4ML_TARGET_MIRROR_RESULT','target-mirror-v1.json')
    path.write_text(json.dumps(report,indent=2)+'\n')
    print('TARGET_MIRROR_RESULT: '+json.dumps(report),flush=True)
    if not result.wasSuccessful():raise SystemExit(1)
