"""Actual stored-anchor sampling and input/label compatibility across supported rigs."""
from pathlib import Path
import sys,os,json,time,unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'tests'),str(ROOT/'training/b4artists_ml')]
import bpy,numpy as np
from mathutils import Quaternion
import b4artists_ml
from b4artists_ml import workflow as w,posing as p,rig_state as rs,body_solver as solver,body_preview as body
import rig_observations as observations
from semantic_motion_data import SemanticSequence,observe
from test_b4artists_ml_rig_observations import ObservationRigTests
RECORDS=[]


class AnchorObservationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b4artists_ml.register()
        from test_b4artists_ml_posing import boneforge_rig,rigify_rig
        from test_b4artists_ml_imported_humanoids import authored
        cls.builders=dict(boneforge=boneforge_rig,rigify_basic=rigify_rig,rigify_default=lambda:rigify_rig(full=True),
            metarig_basic=lambda:rigify_rig(generate=False),metarig_default=lambda:rigify_rig(full=True,generate=False))
        for i,key in enumerate(('mocap_humanoid','unity_humanoid','unreal_mannequin')):
            cls.builders[key]=lambda key=key,i=i:authored(key,i)[0]
        cls.helper=ObservationRigTests()
    @classmethod
    def tearDownClass(cls):
        label=os.environ.get('B4ML_RUN_LABEL','anchor-observations-development')
        (ROOT/f'training/b4artists_ml/results/{label}-observations.json').write_text(json.dumps(RECORDS,indent=2)+'\n')
    def state(self,ob):return self.helper.state(ob)
    def pose(self,ob,binding):
        p._update(ob);evaluated=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());world=evaluated.matrix_world
        return (np.array([world@evaluated.pose.bones[n].head for n in binding['names']]),
                np.array([observations._orientation(world@evaluated.pose.bones[n].matrix) for n in binding['names']]))
    def fixture(self,label='boneforge'):
        bpy.context.window.scene=bpy.data.scenes.new('Authored anchors '+label)
        ob=self.builders[label]();scene=bpy.context.scene;scene.render.fps=30
        bpy.context.view_layer.objects.active=ob;binding=solver.mapping(ob,writable=False)
        root=ob.pose.bones[binding['root']]
        for frame in (1,3,11,13):root.location.x=frame*.008;root.keyframe_insert('location',frame=frame)
        scene.frame_set(7,subframe=.25)
        expected={};context={}
        for frame in (2,12):scene.frame_set(frame);context[frame]=self.pose(ob,binding)
        for i,frame in enumerate((3,11)):
            scene.frame_set(frame);source=w.raw_pose(ob);modes=rs.mode_values(ob)
            rs.normalize_fk(ob)
            root.location.x+=.035*(i+1)
            name=binding['rotations'][-7];pb=ob.pose.bones[name];solver._set_quat(pb,solver._quat(pb)@Quaternion((1,0,0),.12*(i+1)))
            p._update(ob);expected[frame]=self.pose(ob,binding)
            w.capture_anchor(ob,scene)
            w.restore_pose(ob,source);rs.restore_values(ob,modes)
        scene.frame_set(7,subframe=.25);p._update(ob)
        return ob,binding,expected,context

    def test_eight_profiles_read_authored_anchors_and_restore_all_source_state(self):
        for label in self.builders:
            with self.subTest(profile=label):
                ob,binding,expected,context=self.fixture(label);before=self.state(ob);start=time.perf_counter()
                result=observations.sample_anchors(ob,3,11);elapsed=(time.perf_counter()-start)*1000
                self.assertEqual(self.state(ob),before)
                expected_points=np.stack([expected[3][0],expected[11][0],context[2][0],context[12][0]])
                expected_rotations=np.stack([expected[3][1],expected[11][1],context[2][1],context[12][1]])
                actual=result.world_points(result.positions);error=float(np.max(np.abs(actual-expected_points)))
                np.testing.assert_allclose(actual,expected_points,atol=2e-5)
                np.testing.assert_allclose(result.world_rotations(result.rotations),expected_rotations,atol=2e-5)
                ordinary=observations.sample(ob,3,11)
                self.assertGreater(np.linalg.norm(result.positions[:2]-ordinary.positions[:2]),.005)
                self.assertEqual(self.state(ob),before)
                RECORDS.append(dict(profile=label,anchor_sampling_ms=elapsed,max_world_component_error=error,source_restored=True,known_frames=[3,11,2,12]))

    def test_training_sequence_and_host_anchor_features_match(self):
        ob,binding,expected,context=self.fixture('unity_humanoid');before=self.state(ob)
        result=observations.sample_anchors(ob,3,11)
        # Build an independent motion container from poses recorded while authoring,
        # before capture and source restoration; hidden samples are deliberately NaN.
        points=np.full((14,17,3),np.nan);rotations=np.full((14,17,3,3),np.nan)
        for f,(pnts,rots) in dict(expected,**{}).items():points[f]=pnts;rotations[f]=rots
        for f,(pnts,rots) in context.items():points[f]=pnts;rotations[f]=rots
        world=ob.matrix_world;rest=np.array([world@ob.data.bones[n].head_local for n in binding['names']]);rest_r=np.array([observations._orientation(world@ob.data.bones[n].matrix_local) for n in binding['names']])
        sequence=SemanticSequence(rest,rest_r,points,rotations,np.arange(14),1/30)
        encoded=observe(sequence,3,11)
        np.testing.assert_allclose(encoded.features(),result.features(),atol=2e-5);self.assertEqual(self.state(ob),before)

    def test_only_known_frames_are_visited_with_optional_context(self):
        ob,*_=self.fixture();before=self.state(ob);original=observations._frame_set
        for context,frames in ((True,[3,11,2,12,7]),(False,[3,11,7])):
            visited=[]
            def track(scene,frame,**kw):visited.append(frame);return original(scene,frame,**kw)
            with patch('rig_observations._frame_set',track):observations.sample_anchors(ob,3,11,context=context)
            self.assertEqual(visited,frames);self.assertEqual(self.state(ob),before)

    def test_cancel_and_failed_frame_restore_unkeyed_channels_and_modes(self):
        for label in ('boneforge','rigify_default','unreal_mannequin'):
            ob,*_=self.fixture(label);before=self.state(ob);calls=[]
            def cancel():calls.append(1);return len(calls)==2
            with self.assertRaises(InterruptedError):observations.sample_anchors(ob,3,11,cancel_requested=cancel)
            self.assertEqual(self.state(ob),before)
            original=observations._frame_set;visits=[]
            def fail(scene,frame,**kw):
                visits.append(frame)
                if len(visits)==2:raise RuntimeError('injected anchor evaluation failure')
                return original(scene,frame,**kw)
            with patch('rig_observations._frame_set',fail):
                with self.assertRaisesRegex(RuntimeError,'injected'):observations.sample_anchors(ob,3,11)
            self.assertEqual(self.state(ob),before)

    def test_restored_body_payload_without_live_owner_is_rejected(self):
        ob,*_=self.fixture();body.begin(ob,bpy.context.scene);body.reset_runtime()
        self.assertTrue(ob.b4ml.body_payload);self.assertNotIn(ob.as_pointer(),solver._SESSIONS)
        before=self.state(ob)
        try:
            for call in (observations.sample,observations.sample_anchors):
                with self.assertRaisesRegex(ValueError,'active'):call(ob,3,11)
                self.assertEqual(self.state(ob),before)
        finally:body.finish(ob,bpy.context.scene,False)

    def test_subframe_priorities_are_sampled_and_restored(self):
        ob,*_=self.fixture('mocap_humanoid');ob.b4ml.anchors[0].frame=3.25;ob.b4ml.anchors[1].frame=11.5
        before=self.state(ob);visited=[];original=observations._frame_set
        def track(scene,frame,**kw):visited.append(frame+kw.get('subframe',0));return original(scene,frame,**kw)
        with patch('rig_observations._frame_set',track):result=observations.sample_anchors(ob,3.25,11.5)
        self.assertEqual(visited,[3.25,11.5,2.25,12.5,7.25]);self.assertAlmostEqual(result.duration,8.25/30);self.assertEqual(self.state(ob),before)

    def test_invalid_or_missing_anchors_fail_without_sampling(self):
        ob,*_=self.fixture();before=self.state(ob)
        for a,b in ((2,11),(11,3),(True,11),(3,3)):
            with self.assertRaises(ValueError):observations.sample_anchors(ob,a,b)
            self.assertEqual(self.state(ob),before)

    def test_context_uses_stored_neighbor_anchors_when_present(self):
        ob,binding,*_=self.fixture('unity_humanoid');before_no_context=observations.sample_anchors(ob,3,11,context=False)
        base=next(a for a in ob.b4ml.anchors if a.frame==3);payload=json.loads(base.payload)
        for frame,delta in ((2,.11),(12,-.08)):
            value=json.loads(json.dumps(payload));value['pose'][binding['root']]['location'][0]+=delta
            item=ob.b4ml.anchors.add();item.frame=frame;item.payload=json.dumps(value)
        expected=[];source=w.raw_pose(ob);modes=rs.mode_values(ob);scene=bpy.context.scene
        for frame in (2,12):
            scene.frame_set(frame);value=json.loads(next(a for a in ob.b4ml.anchors if a.frame==frame).payload)
            rs.restore_values(ob,value.get('rig_modes',{}));w.restore_pose(ob,value['pose']);expected.append(self.pose(ob,binding)[0])
            w.restore_pose(ob,source);rs.restore_values(ob,modes)
        scene.frame_set(7,subframe=.25);before=self.state(ob)
        result=observations.sample_anchors(ob,3,11)
        np.testing.assert_allclose(result.world_points(result.positions)[2:],expected,atol=2e-5)
        np.testing.assert_allclose(observations.sample_anchors(ob,3,11,context=False).features(),before_no_context.features(),atol=2e-5)
        self.assertEqual(self.state(ob),before)

    def test_interval_cannot_silently_skip_an_authored_priority_pose(self):
        ob,*_=self.fixture();middle=ob.b4ml.anchors.add();middle.frame=7;middle.payload=ob.b4ml.anchors[0].payload
        before=self.state(ob)
        with self.assertRaisesRegex(ValueError,'adjacent'):observations.sample_anchors(ob,3,11)
        self.assertEqual(self.state(ob),before)
        self.assertAlmostEqual(observations.sample_anchors(ob,3,7).duration,4/30)
        self.assertEqual(self.state(ob),before)
