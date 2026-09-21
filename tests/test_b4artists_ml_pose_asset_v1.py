"""Scene-persistent semantic target pose assets across supported humanoid rigs."""
from pathlib import Path
import copy,json,os,sys,unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'tests'),str(ROOT/'training/b4artists_ml')]
import bpy,numpy as np
from mathutils import Quaternion,Vector
import b4artists_ml
from b4artists_ml import body_preview as body,rig_state as rs,ui,workflow as w
from test_b4artists_ml_chest_orientation_v1 import ChestOrientationTests
from test_b4artists_ml_imported_humanoids import keys

RECORDS=[]


def _plain(value):return json.loads(json.dumps(value,allow_nan=False))


class PoseAssetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ChestOrientationTests.setUpClass();cls.support=ChestOrientationTests()
        cls.support.fixtures=ChestOrientationTests.fixtures

    def tearDown(self):
        for obj in list(bpy.data.objects):
            if hasattr(obj,'b4ml') and obj.b4ml.body_payload:
                if obj.users_scene:bpy.context.window.scene=obj.users_scene[0]
                body.finish(obj,bpy.context.scene,False)
        for scene in bpy.data.scenes:
            if body.POSE_ASSET_KEY in scene:del scene[body.POSE_ASSET_KEY]
        body.reset_runtime()

    def _fixture(self,label):return self.support._fixture(label)

    def _nudge_pose_without_changing_contract(self,obj):
        record=body._read(obj)
        for name in record['session']['binding']['controls']:
            pb=obj.pose.bones[name];channels=w._channels(pb)
            if channels['location']:
                pb.location[channels['location'][0]]+=.031
                bpy.context.view_layer.update();return name
            if channels['rotation']:
                if pb.rotation_mode=='QUATERNION':
                    pb.rotation_quaternion=pb.rotation_quaternion@Quaternion((0.,0.,1.),.031)
                else:pb.rotation_euler.z+=.031
                bpy.context.view_layer.update();return name
        raise AssertionError('Fixture has no writable control to perturb')
    def _authored_asset(self,operator=False):
        obj,source,action,action_keys=self._fixture('boneforge')
        scene=bpy.context.scene;bpy.context.view_layer.objects.active=obj;obj.select_set(True)
        body.begin(obj,scene);session=body._get(obj)
        for item in obj.b4ml.body_targets:
            item.enabled=item.name=='Pelvis';item.use_orientation=False;item.use_pole=False
        hand=obj.b4ml.body_targets['Hand L'];hand.enabled=True;hand.use_pole=True
        hand.target.location+=Vector(session.basis[:,0]*session.scale*.012)
        hand.pole.location+=Vector(session.basis[:,1]*session.scale*.01)
        neck=obj.b4ml.body_targets['Neck'];neck.use_orientation=True
        neck.target.rotation_quaternion=(neck.target.rotation_quaternion@Quaternion((0.,0.,1.),.008))
        bpy.context.view_layer.update();body.solve(obj)
        if operator:
            self.assertEqual(bpy.ops.b4ml.body(operation='SAVE_POSE_ASSET'),{'FINISHED'})
            asset=body._read_pose_asset(scene)
        else:asset=body.capture_pose_asset(obj,scene)
        self.assertEqual(asset['representation'],'semantic_target_delta_body_v1')
        self.assertTrue(asset['verified_solve']);self.assertFalse(asset['learned'])
        self.assertEqual(_plain(w.raw_pose(obj,session.binding['controls'])),
                         json.loads(obj.b4ml.body_payload)['preview'])
        body.finish(obj,scene,False);self.assertEqual(w.raw_pose(obj),source)
        if action is not None:
            self.assertEqual(obj.animation_data.action,action);self.assertEqual(keys(obj),action_keys)
        return scene,asset

    def _assert_asset_applied(self,obj,asset):
        record=body._read(obj);session=body._get(obj)
        frame=body._pose_asset_frame(session,record,'testing a pose asset')
        for (index,label),row in zip(body._target_rows(record),asset['targets']):
            item=obj.b4ml.body_targets[label];start=body._saved_target_matrix(record,index,label)
            actual=(np.asarray(item.target.matrix_world.translation-start.translation,float)
                    @frame/session.scale)
            self.assertTrue(np.allclose(actual,row['position_delta'],atol=2e-6),(label,actual,row))
            self.assertEqual(item.enabled,row['position_enabled'])
            self.assertEqual(item.use_orientation,row['orientation_enabled'])
            current=np.asarray(item.target.matrix_world.to_3x3(),float)
            relative=frame.T@current@np.asarray(start.to_3x3(),float).T@frame
            expected=np.asarray(Quaternion(row['orientation_delta']).to_matrix(),float)
            self.assertTrue(np.allclose(relative,expected,atol=2e-6),(label,relative,expected))
            if index in body.POLE_JOINTS:
                pole_start=body._saved_pole_matrix(record,label)
                pole=(np.asarray(item.pole.matrix_world.translation-pole_start.translation,float)
                      @frame/session.scale)
                self.assertTrue(np.allclose(pole,row['pole']['delta'],atol=2e-6),(label,pole,row['pole']))
                self.assertEqual(item.use_pole,row['pole']['enabled'])
                self.assertAlmostEqual(item.pole_distance,row['pole']['distance'],places=6)

    def test_verified_asset_applies_to_six_humanoid_adapters_without_rig_mutation(self):
        scene,asset=self._authored_asset()
        for label in (*self.support.fixtures.builders,'unity_humanoid_fbx'):
            with self.subTest(rig=label):
                obj,source,action,action_keys=self._fixture(label)
                bpy.context.view_layer.objects.active=obj;obj.select_set(True);body.begin(obj,scene)
                pose=_plain(w.raw_pose(obj));modes=rs.mode_values(obj)
                result=body.apply_pose_asset(obj,scene)
                self.assertEqual(result['targets'],len(body.TARGETS))
                self.assertEqual(result['cross_rig'],result['source_profile']!=result['target_profile'])
                self.assertIsNone(json.loads(obj.b4ml.body_payload)['signature'])
                self.assertEqual(_plain(w.raw_pose(obj)),pose);self.assertEqual(rs.mode_values(obj),modes)
                self._assert_asset_applied(obj,asset)
                RECORDS.append(dict(fixture=label,source_profile=result['source_profile'],
                                    target_profile=result['target_profile'],cross_rig=result['cross_rig'],
                                    rig_pose_unchanged=True,target_count=result['targets']))
                body.finish(obj,scene,False);self.assertEqual(w.raw_pose(obj),source)
                if action is not None:
                    self.assertEqual(obj.animation_data.action,action);self.assertEqual(keys(obj),action_keys)

    def test_cross_rig_apply_solves_reloads_and_keeps_editable_anchor(self):
        scene,asset=self._authored_asset();asset_text=scene[body.POSE_ASSET_KEY]
        obj,source,action,action_keys=self._fixture('rigify_basic')
        scene=bpy.context.scene;scene[body.POSE_ASSET_KEY]=asset_text
        bpy.context.view_layer.objects.active=obj;obj.select_set(True);body.begin(obj,scene)
        result=body.apply_pose_asset(obj,scene);self.assertTrue(result['cross_rig'])
        body.solve(obj);record=json.loads(obj.b4ml.body_payload)
        self.assertIsNotNone(record['signature']);self.assertEqual(record['metrics']['requested_orientations'],1)
        name=obj.name;path=ROOT/'training/b4artists_ml/cache/pose-asset-v1-reload.blend'
        bpy.ops.wm.save_as_mainfile(filepath=str(path));bpy.ops.wm.open_mainfile(filepath=str(path))
        obj=bpy.data.objects[name];scene=bpy.context.scene;bpy.context.view_layer.objects.active=obj
        self.assertEqual(scene[body.POSE_ASSET_KEY],asset_text)
        self._assert_asset_applied(obj,asset)
        body.finish(obj,scene,True)
        self.assertEqual(len(obj.b4ml.anchors),1);self.assertEqual(w.raw_pose(obj),source)

    def test_invalid_assets_and_unsolved_capture_fail_without_partial_changes(self):
        scene,asset=self._authored_asset();valid=scene[body.POSE_ASSET_KEY]
        obj,source,action,action_keys=self._fixture('boneforge')
        bpy.context.view_layer.objects.active=obj;body.begin(obj,scene)
        with self.assertRaisesRegex(ValueError,'Solve the current targets'):
            body.capture_pose_asset(obj,scene)
        snapshot=[(item.name,item.enabled,item.use_orientation,item.use_pole,item.pole_distance,
                   tuple(tuple(row) for row in item.target.matrix_world),
                   tuple(tuple(row) for row in item.pole.matrix_world) if item.pole else None)
                  for item in obj.b4ml.body_targets]
        invalid=['{','x'*(body.POSE_ASSET_MAX_CHARS+1)]
        wrong=copy.deepcopy(asset);wrong['schema']=2;invalid.append(json.dumps(wrong))
        wrong=copy.deepcopy(asset);wrong['unknown']=True;invalid.append(json.dumps(wrong))
        wrong=copy.deepcopy(asset);wrong['source_profile']='';invalid.append(json.dumps(wrong))
        wrong=copy.deepcopy(asset);wrong['targets'][0]['position_enabled']=False;invalid.append(json.dumps(wrong))
        wrong=copy.deepcopy(asset);wrong['targets'][1]['position_delta']=[float('nan'),0,0];invalid.append(json.dumps(wrong))
        wrong=copy.deepcopy(asset);wrong['targets'][1]['label']='Pelvis';invalid.append(json.dumps(wrong))
        wrong=copy.deepcopy(asset);wrong['targets'][1]['unknown']=True;invalid.append(json.dumps(wrong))
        wrong=copy.deepcopy(asset);wrong['targets'][4]['pole']['unknown']=True;invalid.append(json.dumps(wrong))
        for text in invalid:
            with self.subTest(size=len(text)):
                scene[body.POSE_ASSET_KEY]=text
                with self.assertRaises(ValueError):body.apply_pose_asset(obj,scene)
                current=[(item.name,item.enabled,item.use_orientation,item.use_pole,item.pole_distance,
                          tuple(tuple(row) for row in item.target.matrix_world),
                          tuple(tuple(row) for row in item.pole.matrix_world) if item.pole else None)
                         for item in obj.b4ml.body_targets]
                self.assertEqual(current,snapshot);self.assertEqual(w.raw_pose(obj),source)
        scene[body.POSE_ASSET_KEY]=valid

    def test_cold_recovery_rejects_without_pose_mode_payload_status_or_owner_changes(self):
        scene,asset=self._authored_asset();valid=json.dumps(asset,separators=(',',':'))
        obj,source,action,action_keys=self._fixture('boneforge')
        scene=bpy.context.scene;scene[body.POSE_ASSET_KEY]=valid
        bpy.context.view_layer.objects.active=obj;obj.select_set(True);body.begin(obj,scene)
        payload_v5=obj.b4ml.body_payload;body.reset_runtime()
        self._nudge_pose_without_changing_contract(obj)
        pose_before=_plain(w.raw_pose(obj));modes_before=rs.mode_values(obj)
        record=json.loads(payload_v5);record['controls_version']=4
        obj.b4ml.body_payload=json.dumps(record);obj.b4ml.status='cold version rejection sentinel'
        payload_before=obj.b4ml.body_payload;status_before=obj.b4ml.status;key=obj.as_pointer()
        with self.assertRaisesRegex(ValueError,'older preview'):
            body.capture_pose_asset(obj,scene)
        self.assertEqual(_plain(w.raw_pose(obj)),pose_before);self.assertEqual(rs.mode_values(obj),modes_before)
        self.assertEqual(obj.b4ml.body_payload,payload_before);self.assertEqual(obj.b4ml.status,status_before)
        self.assertNotIn(key,body._LIVE);self.assertNotIn(key,body.solver._SESSIONS)

        obj.b4ml.body_payload=payload_v5;obj.b4ml.status='cold invalid asset sentinel'
        wrong=copy.deepcopy(asset);wrong['targets'][4]['pole']['unknown']=True
        scene[body.POSE_ASSET_KEY]=json.dumps(wrong)
        helpers=[(item.name,item.enabled,item.use_orientation,item.use_pole,item.pole_distance,
                  tuple(tuple(row) for row in item.target.matrix_world),
                  tuple(tuple(row) for row in item.pole.matrix_world) if item.pole else None)
                 for item in obj.b4ml.body_targets]
        payload_before=obj.b4ml.body_payload;status_before=obj.b4ml.status
        with self.assertRaises(ValueError):body.apply_pose_asset(obj,scene)
        current=[(item.name,item.enabled,item.use_orientation,item.use_pole,item.pole_distance,
                  tuple(tuple(row) for row in item.target.matrix_world),
                  tuple(tuple(row) for row in item.pole.matrix_world) if item.pole else None)
                 for item in obj.b4ml.body_targets]
        self.assertEqual(current,helpers);self.assertEqual(_plain(w.raw_pose(obj)),pose_before)
        self.assertEqual(rs.mode_values(obj),modes_before);self.assertEqual(obj.b4ml.body_payload,payload_before)
        self.assertEqual(obj.b4ml.status,status_before);self.assertNotIn(key,body._LIVE)
        self.assertNotIn(key,body.solver._SESSIONS)

        scene[body.POSE_ASSET_KEY]=valid;result=body.apply_pose_asset(obj,scene)
        self.assertEqual(result['targets'],len(body.TARGETS));self.assertEqual(_plain(w.raw_pose(obj)),pose_before)
        self.assertEqual(rs.mode_values(obj),modes_before);self.assertNotIn(key,body._LIVE)
        self.assertNotIn(key,body.solver._SESSIONS)
    def test_operator_contract_and_scene_asset_survive_save_reload(self):
        scene,asset=self._authored_asset(operator=True)
        self.assertIn('operation',ui.B4ML_OT_body.__annotations__)
        text=scene[body.POSE_ASSET_KEY]
        obj,source,action,action_keys=self._fixture('boneforge')
        scene=bpy.context.scene;scene[body.POSE_ASSET_KEY]=text
        bpy.context.view_layer.objects.active=obj;body.begin(obj,scene)
        obj.b4ml.body_targets['Hand L'].target.location.x+=.2
        self.assertEqual(bpy.ops.b4ml.body(operation='APPLY_POSE_ASSET'),{'FINISHED'})
        self.assertIsNone(json.loads(obj.b4ml.body_payload)['signature'])
        path=ROOT/'training/b4artists_ml/cache/pose-asset-v1-scene.blend'
        bpy.ops.wm.save_as_mainfile(filepath=str(path));bpy.ops.wm.open_mainfile(filepath=str(path))
        self.assertEqual(bpy.context.scene[body.POSE_ASSET_KEY],text)


if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(PoseAssetTests))
    report=dict(tests=result.testsRun,passed=result.wasSuccessful(),failures=len(result.failures),
                errors=len(result.errors),records=RECORDS,package=b4artists_ml.__file__)
    path=ROOT/'training/b4artists_ml/results'/os.environ.get(
        'B4ML_POSE_ASSET_RESULT','pose-asset-v1.json')
    path.write_text(json.dumps(report,indent=2)+'\n')
    print('POSE_ASSET_RESULT: '+json.dumps(report),flush=True)
    if not result.wasSuccessful():raise SystemExit(1)
