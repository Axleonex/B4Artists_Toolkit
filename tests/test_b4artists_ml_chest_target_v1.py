"""Semantic chest-position target coverage for whole-body posing."""
from pathlib import Path
import json,os,sys,unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[os.environ.get('B4ML_PACKAGE',str(ROOT)),str(ROOT/'tests'),str(ROOT/'training/b4artists_ml')]
import bpy,numpy as np
import b4artists_ml
from b4artists_ml import body_preview as body,workflow as w,posing
from test_b4artists_ml_context_rig import ContextRigTests
from test_b4artists_ml_imported_humanoids import authored,keys

RECORDS=[]


class ChestTargetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b4artists_ml.register();ContextRigTests.setUpClass();cls.fixtures=ContextRigTests()

    def tearDown(self):
        for ob in list(bpy.data.objects):
            if hasattr(ob,'b4ml') and ob.b4ml.body_payload:
                if ob.users_scene:bpy.context.window.scene=ob.users_scene[0]
                body.finish(ob,bpy.context.scene,False)
        body.reset_runtime()

    def _feasible_points(self,label):
        ob,source,session,targets,mask=self.fixtures.fixture(label,transformed=True)
        x=np.zeros(3+3*len(session.q0));x[3:6]=(.025,-.015,.02)
        session._apply(x);posing._update(ob)
        points=session.world_points(session.points())
        session.cancel()
        return ob,source,points

    def _assert_chest(self,ob,source,points,label,action=None,action_signature=None):
        bpy.context.view_layer.objects.active=ob;body.begin(ob,bpy.context.scene)
        self.assertEqual([name for _,name in body.TARGETS][1],'Chest')
        self.assertEqual(json.loads(ob.b4ml.body_payload)['controls_version'],5)
        for item in ob.b4ml.body_targets:item.enabled=item.name in {'Pelvis','Chest'}
        chest=ob.b4ml.body_targets['Chest']
        self.assertIsNone(chest.pole)
        self.assertTrue(body.target_supports_orientation('Chest'))
        self.assertFalse(body.target_supports_pole('Chest'))
        chest.target.location=points[2];bpy.context.view_layer.update()
        body.solve(ob)
        session=body._get(ob);actual=session.world_points(session.points())[2]
        error=float(np.linalg.norm(actual-points[2])/session.scale)
        metrics=json.loads(ob.b4ml.body_payload)['metrics']
        RECORDS.append(dict(fixture=label,chest_error_body_scales=error,
                            pin_error=metrics['pin_error'],semantic_joint=2))
        self.assertLess(error,2e-4)
        self.assertEqual(metrics['requested_orientations'],0)
        self.assertEqual(metrics['requested_poles'],0)
        body.finish(ob,bpy.context.scene,False)
        self.assertEqual(w.raw_pose(ob),source)
        if action is not None:
            self.assertEqual(ob.animation_data.action,action)
            self.assertEqual(keys(ob),action_signature)

    def test_position_only_chest_target_on_six_rigs(self):
        for label in self.fixtures.builders:
            with self.subTest(rig=label):
                ob,source,points=self._feasible_points(label)
                self._assert_chest(ob,source,points,label)
        ob,mesh,roles=authored('unity_humanoid',1);source=w.raw_pose(ob)
        action=ob.animation_data.action;action_signature=keys(ob);session=body.solver.Session(ob)
        x=np.zeros(3+3*len(session.q0));x[3:6]=(.025,-.015,.02)
        session._apply(x);posing._update(ob);points=session.world_points(session.points());session.cancel()
        self._assert_chest(ob,source,points,'unity_humanoid_fbx',action,action_signature)

    def test_scripted_unsupported_chest_pole_fails_without_pose_change(self):
        ob,source,points=self._feasible_points('boneforge')
        bpy.context.view_layer.objects.active=ob;body.begin(ob,bpy.context.scene)
        before=w.raw_pose(ob);ob.b4ml.body_targets['Chest'].use_pole=True
        with self.assertRaisesRegex(ValueError,'Chest does not support pole targets'):
            body._request(ob,body._get(ob))
        self.assertEqual(w.raw_pose(ob),before)
        body.finish(ob,bpy.context.scene,False)
        self.assertEqual(w.raw_pose(ob),source)

    def test_version_one_preview_does_not_require_chest(self):
        ob,source,points=self._feasible_points('rigify_basic')
        bpy.context.view_layer.objects.active=ob;body.begin(ob,bpy.context.scene)
        record=json.loads(ob.b4ml.body_payload);record['controls_version']=1
        record['target_origins'].pop('Chest');ob.b4ml.body_payload=json.dumps(record)
        index=ob.b4ml.body_targets.find('Chest');self.assertGreaterEqual(index,0)
        ob.b4ml.body_targets.remove(index)
        request=body._request(ob,body._get(ob))
        self.assertEqual(len(request[2]['helpers']),6)
        body.solve(ob);body.finish(ob,bpy.context.scene,True)
        self.assertEqual(len(ob.b4ml.anchors),1)
        self.assertEqual(w.raw_pose(ob),source)


if __name__=='__main__':
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(ChestTargetTests)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    report=dict(tests=result.testsRun,passed=result.wasSuccessful(),failures=len(result.failures),
                errors=len(result.errors),records=RECORDS,package=b4artists_ml.__file__)
    path=ROOT/'training/b4artists_ml/results'/os.environ.get('B4ML_CHEST_RESULT','chest-target-v1.json')
    path.write_text(json.dumps(report,indent=2)+'\n')
    print('CHEST_TARGET_RESULT: '+json.dumps(report),flush=True)
    if not result.wasSuccessful():raise SystemExit(1)
