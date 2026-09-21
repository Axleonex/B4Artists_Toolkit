"""Evaluated semantic Chest orientation for the 0.33 posing workflow."""
from pathlib import Path
import json,os,sys,unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'tests'),str(ROOT/'training/b4artists_ml')]
import bpy,numpy as np
from mathutils import Quaternion
import b4artists_ml
from b4artists_ml import body_preview as body,body_solver as solver,posing,workflow as w
from test_b4artists_ml_context_rig import ContextRigTests
from test_b4artists_ml_imported_humanoids import authored,keys

RECORDS=[]


class ChestOrientationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b4artists_ml.register();ContextRigTests.setUpClass();cls.fixtures=ContextRigTests()

    def tearDown(self):
        for obj in list(bpy.data.objects):
            if hasattr(obj,'b4ml') and obj.b4ml.body_payload:
                if obj.users_scene:bpy.context.window.scene=obj.users_scene[0]
                body.finish(obj,bpy.context.scene,False)
        body.reset_runtime()

    def _fixture(self,label):
        if label=='unity_humanoid_fbx':
            obj,mesh,roles=authored('unity_humanoid',1);source=w.raw_pose(obj)
            return obj,source,obj.animation_data.action,keys(obj)
        obj,source,session,targets,mask=self.fixtures.fixture(label,transformed=True)
        session.cancel();return obj,source,None,None

    def _reachable_chest_goal(self,obj):
        session=solver.Session(obj);chest=solver.orientation_bone(session.binding,2)
        baseline=session.obj.pose.bones[chest].matrix.to_quaternion().copy()
        best=None
        for control_index,name in enumerate(session.binding['rotations']):
            if name==session.binding['names'][0]:continue
            for axis in range(3):
                x=np.zeros(3+3*len(session.q0));x[3+control_index*3+axis]=.12
                session._apply(x);posing._update(obj)
                current=obj.pose.bones[chest].matrix.to_quaternion().copy()
                angle=solver._angle(baseline,current)
                if best is None or angle>best[0]:best=(angle,name,axis,current)
                w.restore_pose(obj,session.normalized);posing._update(obj)
        self.assertGreater(best[0],.08)
        goal=session.world.to_quaternion()@best[3]
        control,axis=best[1],best[2];session.cancel()
        return goal,control,axis

    def _solve(self,label):
        obj,source,action,action_keys=self._fixture(label)
        bpy.context.view_layer.objects.active=obj;obj.select_set(True)
        goal,control,axis=self._reachable_chest_goal(obj)
        body.begin(obj,bpy.context.scene)
        self.assertEqual(json.loads(obj.b4ml.body_payload)['controls_version'],5)
        for item in obj.b4ml.body_targets:
            item.enabled=item.name=='Pelvis';item.use_orientation=False
        chest=obj.b4ml.body_targets['Chest'];chest.use_orientation=True
        chest.target.rotation_quaternion=goal;bpy.context.view_layer.update()
        body.solve(obj);session=body._get(obj)
        actual=session.world.to_quaternion()@obj.pose.bones[solver.orientation_bone(session.binding,2)].matrix.to_quaternion()
        error=solver._angle(goal,actual);metrics=json.loads(obj.b4ml.body_payload)['metrics']
        self.assertLess(error,.001)
        self.assertEqual(metrics['requested_orientations'],1)
        self.assertLess(metrics['orientation_error_radians'],.001)
        RECORDS.append(dict(fixture=label,driving_control=control,axis=axis,
                            chest_orientation_error_radians=error,
                            evaluations=metrics['evaluations'],elapsed_ms=metrics['elapsed_ms']))
        body.finish(obj,bpy.context.scene,False)
        self.assertEqual(w.raw_pose(obj),source)
        if action is not None:
            self.assertEqual(obj.animation_data.action,action);self.assertEqual(keys(obj),action_keys)

    def test_opt_in_chest_orientation_on_supported_rigs(self):
        for label in (*self.fixtures.builders,'unity_humanoid_fbx'):
            with self.subTest(rig=label):self._solve(label)

    def test_chest_rotation_persists_through_reload_and_keep(self):
        obj,source,action,action_keys=self._fixture('rigify_basic')
        bpy.context.view_layer.objects.active=obj;goal,control,axis=self._reachable_chest_goal(obj)
        body.begin(obj,bpy.context.scene)
        for item in obj.b4ml.body_targets:item.enabled=item.name=='Pelvis'
        chest=obj.b4ml.body_targets['Chest'];chest.use_orientation=True
        chest.target.rotation_quaternion=goal;bpy.context.view_layer.update();body.solve(obj)
        name=obj.name;path=ROOT/'training/b4artists_ml/cache/chest-orientation-v1-reload.blend'
        bpy.ops.wm.save_as_mainfile(filepath=str(path));bpy.ops.wm.open_mainfile(filepath=str(path))
        obj=bpy.data.objects[name];bpy.context.view_layer.objects.active=obj
        self.assertTrue(obj.b4ml.body_targets['Chest'].use_orientation)
        self.assertEqual(json.loads(obj.b4ml.body_payload)['controls_version'],5)
        body.finish(obj,bpy.context.scene,True)
        self.assertEqual(len(obj.b4ml.anchors),1);self.assertEqual(w.raw_pose(obj),source)

    def test_old_preview_and_invalid_axes_fail_before_pose_mutation(self):
        obj,source,action,action_keys=self._fixture('boneforge');bpy.context.view_layer.objects.active=obj
        body.begin(obj,bpy.context.scene);chest=obj.b4ml.body_targets['Chest'];chest.use_orientation=True
        record=json.loads(obj.b4ml.body_payload);record['controls_version']=3
        obj.b4ml.body_payload=json.dumps(record);before=w.raw_pose(obj)
        with self.assertRaisesRegex(ValueError,'older preview'):body._request(obj,body._get(obj))
        self.assertEqual(w.raw_pose(obj),before)
        record['controls_version']=4;obj.b4ml.body_payload=json.dumps(record)
        chest.target.scale.x=-1.;bpy.context.view_layer.update()
        with self.assertRaisesRegex(ValueError,'non-reflected axes'):body._request(obj,body._get(obj))
        self.assertEqual(w.raw_pose(obj),before)


if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(ChestOrientationTests))
    report=dict(tests=result.testsRun,passed=result.wasSuccessful(),failures=len(result.failures),
                errors=len(result.errors),records=RECORDS,package=b4artists_ml.__file__)
    path=ROOT/'training/b4artists_ml/results'/os.environ.get(
        'B4ML_CHEST_ORIENTATION_RESULT','chest-orientation-v1.json')
    path.write_text(json.dumps(report,indent=2)+'\n')
    print('CHEST_ORIENTATION_RESULT: '+json.dumps(report),flush=True)
    if not result.wasSuccessful():raise SystemExit(1)
