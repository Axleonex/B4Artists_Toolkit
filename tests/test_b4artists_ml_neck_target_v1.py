"""Semantic Neck position and orientation for the 0.33 humanoid posing workflow."""
from pathlib import Path
import json,os,sys,unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'tests'),str(ROOT/'training/b4artists_ml')]
import bpy,numpy as np
from mathutils import Quaternion
import b4artists_ml
from b4artists_ml import body_preview as body,body_solver as solver,posing,workflow as w
from test_b4artists_ml_chest_orientation_v1 import ChestOrientationTests
from test_b4artists_ml_imported_humanoids import keys

RECORDS=[]


class NeckTargetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ChestOrientationTests.setUpClass();cls.support=ChestOrientationTests()
        cls.support.fixtures=ChestOrientationTests.fixtures

    def tearDown(self):
        for obj in list(bpy.data.objects):
            if hasattr(obj,'b4ml') and obj.b4ml.body_payload:
                if obj.users_scene:bpy.context.window.scene=obj.users_scene[0]
                body.finish(obj,bpy.context.scene,False)
        body.reset_runtime()

    def _fixture(self,label):return self.support._fixture(label)

    def _reachable_neck_goal(self,obj):
        session=solver.Session(obj);neck=solver.orientation_bone(session.binding,3)
        baseline_q=obj.pose.bones[neck].matrix.to_quaternion().copy()
        baseline_point=session.world_points(session.points())[3].copy();best=None
        for control_index,name in enumerate(session.binding['rotations']):
            if name==session.binding['names'][0]:continue
            for axis in range(3):
                x=np.zeros(3+3*len(session.q0));x[3+control_index*3+axis]=.08
                session._apply(x);posing._update(obj)
                current_q=obj.pose.bones[neck].matrix.to_quaternion().copy()
                current_point=session.world_points(session.points())[3].copy()
                score=solver._angle(baseline_q,current_q)+float(np.linalg.norm(current_point-baseline_point))/session.scale
                if best is None or score>best[0]:
                    best=(score,name,axis,current_point,session.world.to_quaternion()@current_q)
                w.restore_pose(obj,session.normalized);posing._update(obj)
        self.assertGreater(best[0],.04)
        result=best[1:];session.cancel();return result

    def _solve(self,label):
        obj,source,action,action_keys=self._fixture(label)
        bpy.context.view_layer.objects.active=obj;obj.select_set(True)
        control,axis,goal_point,goal_rotation=self._reachable_neck_goal(obj)
        body.begin(obj,bpy.context.scene)
        self.assertEqual(json.loads(obj.b4ml.body_payload)['controls_version'],5)
        self.assertEqual([name for _,name in body.TARGETS][2],'Neck')
        for item in obj.b4ml.body_targets:
            item.enabled=item.name=='Pelvis';item.use_orientation=False
        neck=obj.b4ml.body_targets['Neck'];neck.enabled=True;neck.use_orientation=True
        neck.target.location=goal_point;neck.target.rotation_quaternion=goal_rotation
        bpy.context.view_layer.update();body.solve(obj);session=body._get(obj)
        actual_point=session.world_points(session.points())[3]
        actual_rotation=(session.world.to_quaternion()
                         @obj.pose.bones[solver.orientation_bone(session.binding,3)].matrix.to_quaternion())
        position_error=float(np.linalg.norm(actual_point-goal_point))
        rotation_error=solver._angle(goal_rotation,actual_rotation)
        metrics=json.loads(obj.b4ml.body_payload)['metrics']
        self.assertLess(position_error,session.scale*2e-4)
        self.assertLess(rotation_error,.001)
        self.assertEqual(metrics['requested_orientations'],1)
        RECORDS.append(dict(fixture=label,driving_control=control,axis=axis,
            neck_position_error=position_error,neck_orientation_error_radians=rotation_error,
            evaluations=metrics['evaluations'],elapsed_ms=metrics['elapsed_ms']))
        body.finish(obj,bpy.context.scene,False);self.assertEqual(w.raw_pose(obj),source)
        if action is not None:
            self.assertEqual(obj.animation_data.action,action);self.assertEqual(keys(obj),action_keys)

    def test_opt_in_neck_position_and_orientation_on_six_adapters(self):
        for label in (*self.support.fixtures.builders,'unity_humanoid_fbx'):
            with self.subTest(rig=label):self._solve(label)

    def test_neck_position_and_rotation_are_independent(self):
        obj,source,action,action_keys=self._fixture('boneforge')
        bpy.context.view_layer.objects.active=obj;body.begin(obj,bpy.context.scene)
        neck=obj.b4ml.body_targets['Neck']
        self.assertFalse(neck.enabled);self.assertFalse(neck.use_orientation)
        self.assertTrue(body.target_supports_orientation('Neck'))
        neck.use_orientation=True
        request=body._request(obj,body._get(obj))
        self.assertFalse(request[1][3]);self.assertIn(3,request[3])
        neck.use_orientation=False;neck.enabled=True
        request=body._request(obj,body._get(obj))
        self.assertTrue(request[1][3]);self.assertNotIn(3,request[3])
        body.finish(obj,bpy.context.scene,False);self.assertEqual(w.raw_pose(obj),source)

    def test_neck_reset_reload_and_keep(self):
        obj,source,action,action_keys=self._fixture('rigify_basic')
        bpy.context.view_layer.objects.active=obj
        control,axis,goal_point,goal_rotation=self._reachable_neck_goal(obj)
        body.begin(obj,bpy.context.scene);bpy.context.view_layer.update()
        neck=obj.b4ml.body_targets['Neck']
        start=neck.target.matrix_world.copy()
        neck.target.location.x+=.1;neck.target.rotation_quaternion.rotate(Quaternion((0.,0.,1.),.1))
        bpy.context.view_layer.update();result=body.reset_target(obj,'Neck')
        self.assertTrue(np.allclose(np.asarray(neck.target.matrix_world),np.asarray(start),atol=1e-7))
        self.assertTrue(result['orientation'])
        for item in obj.b4ml.body_targets:
            item.enabled=item.name=='Pelvis';item.use_orientation=False
        neck.enabled=True;neck.use_orientation=True
        neck.target.location=goal_point;neck.target.rotation_quaternion=goal_rotation
        bpy.context.view_layer.update();body.solve(obj)
        name=obj.name;path=ROOT/'training/b4artists_ml/cache/neck-target-v1-reload.blend'
        bpy.ops.wm.save_as_mainfile(filepath=str(path));bpy.ops.wm.open_mainfile(filepath=str(path))
        obj=bpy.data.objects[name];bpy.context.view_layer.objects.active=obj
        neck=obj.b4ml.body_targets['Neck']
        self.assertTrue(neck.enabled);self.assertTrue(neck.use_orientation)
        self.assertEqual(json.loads(obj.b4ml.body_payload)['controls_version'],5)
        body.finish(obj,bpy.context.scene,True)
        self.assertEqual(len(obj.b4ml.anchors),1);self.assertEqual(w.raw_pose(obj),source)

    def test_version_four_rows_and_invalid_neck_axes_are_safe(self):
        obj,source,action,action_keys=self._fixture('boneforge')
        bpy.context.view_layer.objects.active=obj;body.begin(obj,bpy.context.scene)
        neck=obj.b4ml.body_targets['Neck'];record=json.loads(obj.b4ml.body_payload)
        record['controls_version']=4;obj.b4ml.body_payload=json.dumps(record)
        neck.enabled=True;neck.use_orientation=True
        request=body._request(obj,body._get(obj))
        self.assertFalse(request[1][3]);self.assertNotIn(3,request[3])
        record['controls_version']=5;obj.b4ml.body_payload=json.dumps(record)
        before=w.raw_pose(obj);neck.target.scale.x=-1.;bpy.context.view_layer.update()
        with self.assertRaisesRegex(ValueError,'non-reflected axes'):
            body._request(obj,body._get(obj))
        self.assertEqual(w.raw_pose(obj),before)


if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(NeckTargetTests))
    report=dict(tests=result.testsRun,passed=result.wasSuccessful(),failures=len(result.failures),
                errors=len(result.errors),records=RECORDS,package=b4artists_ml.__file__)
    path=ROOT/'training/b4artists_ml/results'/os.environ.get(
        'B4ML_NECK_TARGET_RESULT','neck-target-v1.json')
    path.write_text(json.dumps(report,indent=2)+'\n')
    print('NECK_TARGET_RESULT: '+json.dumps(report),flush=True)
    if not result.wasSuccessful():raise SystemExit(1)
