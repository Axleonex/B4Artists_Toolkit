"""Focused reusable local pose-anchor coverage for the 0.33 usability slice."""
from pathlib import Path
from unittest.mock import patch
import json,math,os,sys,unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'tests'),str(ROOT/'training/b4artists_ml')]
import addon_utils,bpy
from mathutils import Quaternion
import b4artists_ml
from b4artists_ml import motion_layer,rig_state as rs,ui,workflow as w
from test_b4artists_ml_context_rig import ContextRigTests
from test_b4artists_ml_imported_humanoids import authored
from test_b4artists_ml_quadruped_pose import _generate as generated_quadruped

RECORDS=[]


def _plain(value):
    return json.loads(json.dumps(value,allow_nan=False))


def _matrix(value):
    return tuple(tuple(row) for row in value)


def _action_snapshot(obj):
    ad=obj.animation_data
    if not ad or not ad.action:return None
    slot=getattr(ad,'action_slot',None)
    return dict(name=ad.action.name,slot=w._slot(ad),curves=[
        (curve.data_path,curve.array_index,[
            (tuple(key.co),tuple(key.handle_left),tuple(key.handle_right),key.interpolation)
            for key in curve.keyframe_points])
        for curve in w.action_curves(ad.action,slot)
    ])


def _anchors(obj):
    return [(a.frame,a.name,a.payload) for a in obj.b4ml.anchors]


def _alter_captured_control(obj,payload):
    for name,value in payload['pose'].items():
        bone=obj.pose.bones[name]
        channels=value['channels']
        for index,enabled in enumerate(channels['location']):
            if enabled:
                bone.location[index]+=.071
                return name
        if any(channels['rotation']):
            if bone.rotation_mode=='QUATERNION':
                bone.rotation_quaternion=bone.rotation_quaternion@Quaternion((1.,0.,0.),.19)
            elif bone.rotation_mode=='AXIS_ANGLE':
                bone.rotation_axis_angle[0]+=.19
            else:
                bone.rotation_euler.rotate_axis('X',.19)
            return name
    raise AssertionError('fixture has no writable captured control')


class PoseReuseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        addon_utils.enable('rigify',default_set=True,persistent=False)
        b4artists_ml.register();ContextRigTests.setUpClass();cls.fixtures=ContextRigTests()

    def _rig(self,label):
        if label=='unity_humanoid_fbx':
            obj,mesh,roles=authored('unity_humanoid',1)
        elif label=='rigify_cat':
            scene,obj=generated_quadruped('cat')
        else:
            obj,source,session,targets,mask=self.fixtures.fixture(label,transformed=True)
            session.cancel()
        bpy.context.view_layer.objects.active=obj;obj.select_set(True)
        return obj,bpy.context.scene

    def _two_anchors(self,obj,scene):
        scene.frame_set(1);w.capture_anchor(obj,scene)
        first=json.loads(obj.b4ml.anchors[0].payload)
        changed=_alter_captured_control(obj,first);bpy.context.view_layer.update()
        scene.frame_set(9);w.capture_anchor(obj,scene)
        return first,changed

    def test_reuse_is_read_only_and_becomes_an_exact_priority_pose(self):
        for label in ('boneforge','rigify_default','unity_humanoid_fbx','rigify_cat'):
            with self.subTest(rig=label):
                obj,scene=self._rig(label)
                first,changed=self._two_anchors(obj,scene)
                scene.frame_set(5);bpy.context.view_layer.update()
                pose_before=_plain(w.raw_pose(obj));modes=rs.mode_values(obj)
                world=_matrix(obj.matrix_world);action=_action_snapshot(obj)
                self.assertGreater(w.reuse_anchor(obj,scene,1.),0)
                self.assertEqual(len(obj.b4ml.anchors),3)
                reused=next(json.loads(a.payload) for a in obj.b4ml.anchors if abs(a.frame-5.)<1e-5)
                self.assertEqual(reused,first)
                self.assertEqual(_plain(w.raw_pose(obj)),pose_before)
                self.assertEqual(rs.mode_values(obj),modes)
                self.assertEqual(_matrix(obj.matrix_world),world)
                self.assertEqual(_action_snapshot(obj),action)
                w.preview(obj,scene);scene.frame_set(5);bpy.context.view_layer.update()
                candidate=_plain(w.raw_pose(obj,first['pose'].keys()))
                self.assertEqual(candidate,first['pose'])
                w.finish_preview(obj,scene,False);scene.frame_set(5);bpy.context.view_layer.update()
                self.assertEqual(_plain(w.raw_pose(obj)),pose_before)
                self.assertEqual(_action_snapshot(obj),action)
                RECORDS.append(dict(fixture=label,source_frame=1,destination_frame=5,
                                    control_count=len(first['pose']),altered_control=changed,
                                    rig_and_action_unchanged=True,priority_pose_exact=True))

    def test_one_anchor_reuse_and_existing_destination_overwrite(self):
        obj,scene=self._rig('boneforge')
        scene.frame_set(1);w.capture_anchor(obj,scene)
        source=json.loads(obj.b4ml.anchors[0].payload)
        scene.frame_set(5);w.reuse_anchor(obj,scene,1.)
        self.assertEqual(len(obj.b4ml.anchors),2)
        self.assertEqual(json.loads(next(a.payload for a in obj.b4ml.anchors if a.frame==5)),source)
        _alter_captured_control(obj,source);scene.frame_set(9);w.capture_anchor(obj,scene)
        count=len(obj.b4ml.anchors);scene.frame_set(5);w.reuse_anchor(obj,scene,1.)
        self.assertEqual(len(obj.b4ml.anchors),count)
        target=next(a for a in obj.b4ml.anchors if a.frame==5)
        self.assertEqual(json.loads(target.payload),source)
        self.assertIn('reused from 1',target.name)

    def test_invalid_or_busy_state_fails_before_anchor_mutation(self):
        obj,scene=self._rig('boneforge');self._two_anchors(obj,scene)
        scene.frame_set(5);baseline=_anchors(obj)
        cases=[
            ('same frame',lambda:w.reuse_anchor(obj,scene,5.)),
            ('missing source',lambda:w.reuse_anchor(obj,scene,3.)),
            ('non-finite source',lambda:w.reuse_anchor(obj,scene,float('nan'))),
        ]
        for label,operation in cases:
            with self.subTest(case=label),self.assertRaises(ValueError):operation()
            self.assertEqual(_anchors(obj),baseline)
        scene.frame_set(1)
        with self.assertRaisesRegex(ValueError,'different frame'):w.reuse_anchor(obj,scene,1.)
        self.assertEqual(_anchors(obj),baseline)
        scene.frame_set(w.MAX_FRAMES+20)
        with self.assertRaisesRegex(ValueError,'experimental preview'):w.reuse_anchor(obj,scene,1.)
        self.assertEqual(_anchors(obj),baseline)
        scene.frame_set(5)
        original=obj.b4ml.anchors[0].payload;obj.b4ml.anchors[0].payload='{'
        corrupt=_anchors(obj)
        with self.assertRaisesRegex(ValueError,'Invalid pose anchor'):w.reuse_anchor(obj,scene,1.)
        self.assertEqual(_anchors(obj),corrupt);obj.b4ml.anchors[0].payload=original
        duplicate=obj.b4ml.anchors.add();duplicate.frame=1;duplicate.name='Duplicate';duplicate.payload=original
        ambiguous=_anchors(obj)
        with self.assertRaisesRegex(ValueError,'finite and distinct'):w.reuse_anchor(obj,scene,1.)
        self.assertEqual(_anchors(obj),ambiguous);obj.b4ml.anchors.remove(len(obj.b4ml.anchors)-1)
        baseline=_anchors(obj)
        for field in ('posing_payload','body_payload','quadruped_payload'):
            with self.subTest(active=field):
                setattr(obj.b4ml,field,'{}')
                with self.assertRaisesRegex(ValueError,'active preview'):w.reuse_anchor(obj,scene,1.)
                setattr(obj.b4ml,field,'')
                self.assertEqual(_anchors(obj),baseline)
        obj.b4ml.temporal_running=True
        self.assertFalse(ui.B4ML_OT_action.poll(bpy.context))
        with self.assertRaisesRegex(ValueError,'motion generation'):w.reuse_anchor(obj,scene,1.)
        obj.b4ml.temporal_running=False
        self.assertEqual(_anchors(obj),baseline)
        candidate=bpy.data.actions.new('Pose reuse blocker');obj.b4ml.candidate_action=candidate
        with self.assertRaisesRegex(ValueError,'active preview'):w.reuse_anchor(obj,scene,1.)
        obj.b4ml.candidate_action=None;bpy.data.actions.remove(candidate)
        with patch.object(motion_layer,'find',return_value=object()):
            with self.assertRaisesRegex(ValueError,'kept motion source'):w.reuse_anchor(obj,scene,1.)
        with patch.object(w,'_reject_nla',side_effect=ValueError('NLA tracks are not supported')):
            with self.assertRaisesRegex(ValueError,'NLA'):w.reuse_anchor(obj,scene,1.)
        self.assertEqual(_anchors(obj),baseline)

    def test_corrupt_and_oversized_payloads_are_bounded(self):
        obj,scene=self._rig('boneforge');scene.frame_set(1);w.capture_anchor(obj,scene)
        anchor=obj.b4ml.anchors[0];original=anchor.payload
        for payload in ('[]','{"schema":1}','['*1500+'0'+']'*1500,' '*w.MAX_ANCHOR_PAYLOAD_CHARS+'x'):
            with self.subTest(size=len(payload)):
                anchor.payload=payload;before=_anchors(obj);scene.frame_set(5)
                with self.assertRaises(ValueError):w.reuse_anchor(obj,scene,1.)
                self.assertEqual(_anchors(obj),before)
        padding=' '*(w.MAX_ANCHOR_PAYLOAD_CHARS//2)
        anchor.payload=padding+original
        second=obj.b4ml.anchors.add();second.frame=9.;second.name='Bounded total';second.payload=padding+original
        before=_anchors(obj)
        with self.assertRaises(ValueError):w.reuse_anchor(obj,scene,1.)
        self.assertEqual(_anchors(obj),before)
        obj.b4ml.anchors.clear();scene.frame_set(1);w.capture_anchor(obj,scene)
        anchor=obj.b4ml.anchors[0];original=anchor.payload
        anchor.payload=' '*(w.MAX_ANCHOR_PAYLOAD_CHARS-len(original)-1)+original
        before=_anchors(obj);scene.frame_set(5)
        with self.assertRaisesRegex(ValueError,'payload limit'):w.reuse_anchor(obj,scene,1.)
        self.assertEqual(_anchors(obj),before)

    def test_hostile_payload_and_anchor_count_fail_atomically(self):
        obj,scene=self._rig('boneforge');self._two_anchors(obj,scene);scene.frame_set(5)
        payload=json.loads(obj.b4ml.anchors[0].payload)
        payload['ignored_non_finite']=float('nan')
        obj.b4ml.anchors[0].payload=json.dumps(payload)
        before=_anchors(obj)
        with self.assertRaises((ValueError,TypeError)):
            w.reuse_anchor(obj,scene,1.)
        self.assertEqual(_anchors(obj),before)

        obj.b4ml.anchors.clear();scene.frame_set(1);w.capture_anchor(obj,scene)
        payload=obj.b4ml.anchors[0].payload
        for frame in range(2,130):
            anchor=obj.b4ml.anchors.add();anchor.frame=float(frame)
            anchor.name=f'Frame {frame}';anchor.payload=payload
        before=_anchors(obj);scene.frame_set(5)
        with self.assertRaisesRegex(ValueError,'at most 128'):
            w.reuse_anchor(obj,scene,1.)
        self.assertEqual(_anchors(obj),before)

    def test_all_supported_anchors_are_reachable_by_page(self):
        obj,scene=self._rig('boneforge');scene.frame_set(1);w.capture_anchor(obj,scene)
        payload=obj.b4ml.anchors[0].payload
        for frame in range(2,13):
            anchor=obj.b4ml.anchors.add();anchor.frame=float(frame)
            anchor.name=f'Frame {frame}';anchor.payload=payload
        obj.b4ml.anchor_page=2
        anchors,page,page_count=ui._anchor_page(obj.b4ml)
        self.assertEqual((page,page_count),(2,2))
        self.assertEqual([anchor.frame for anchor in anchors],[11.,12.])
        obj.b4ml.anchor_page=13
        anchors,page,page_count=ui._anchor_page(obj.b4ml)
        self.assertEqual((page,page_count),(2,2))
        self.assertEqual([anchor.frame for anchor in anchors],[11.,12.])
        self.assertEqual(bpy.ops.b4ml.anchor_page(page=2),{'FINISHED'})
        self.assertEqual(obj.b4ml.anchor_page,2)
        self.assertEqual(ui._anchor_page_label(page,page_count),'Pose Page 2 of 2')

    def test_reused_anchor_survives_save_reload(self):
        obj,scene=self._rig('boneforge');scene.frame_set(1);w.capture_anchor(obj,scene)
        source=json.loads(obj.b4ml.anchors[0].payload);scene.frame_set(5);w.reuse_anchor(obj,scene,1.)
        name=obj.name;path=ROOT/'training/b4artists_ml/cache/pose-reuse-v1-reload.blend'
        bpy.ops.wm.save_as_mainfile(filepath=str(path));bpy.ops.wm.open_mainfile(filepath=str(path))
        obj=bpy.data.objects[name]
        self.assertEqual(len(obj.b4ml.anchors),2)
        self.assertEqual(json.loads(next(a.payload for a in obj.b4ml.anchors if a.frame==5)),source)
        rows=w.read_anchors(obj);self.assertEqual([frame for frame,payload in rows],[1.,5.])

    def test_operator_contract_exposes_reuse_without_applying_pose(self):
        obj,scene=self._rig('boneforge');scene.frame_set(1);w.capture_anchor(obj,scene)
        pose=_plain(w.raw_pose(obj));scene.frame_set(5)
        self.assertTrue({'operation','anchor_frame'}<=set(ui.B4ML_OT_action.__annotations__))
        self.assertEqual(bpy.ops.b4ml.action(operation='REUSE',anchor_frame=1.),{'FINISHED'})
        self.assertEqual(len(obj.b4ml.anchors),2);self.assertEqual(_plain(w.raw_pose(obj)),pose)


if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(PoseReuseTests))
    report=dict(tests=result.testsRun,passed=result.wasSuccessful(),
                failures=len(result.failures),errors=len(result.errors),
                records=RECORDS,package=b4artists_ml.__file__)
    path=ROOT/'training/b4artists_ml/results'/os.environ.get(
        'B4ML_POSE_REUSE_RESULT','pose-reuse-v1.json')
    path.write_text(json.dumps(report,indent=2)+'\n')
    print('POSE_REUSE_RESULT: '+json.dumps(report),flush=True)
    if not result.wasSuccessful():raise SystemExit(1)
