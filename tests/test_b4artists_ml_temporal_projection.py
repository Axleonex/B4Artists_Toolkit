"""Temporal proposal projection on actual rig controls and native actions."""
from pathlib import Path
import sys,copy,json,unittest,os
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[os.environ.get('B4ML_PACKAGE',str(ROOT)),str(ROOT/'tests'),str(ROOT/'training/b4artists_ml')]
import bpy,numpy as np
from b4artists_ml import body_solver as bs,workflow as w,posing as p,rig_state as rs
import temporal_projection as tp
from test_b4artists_ml_anchor_observations import AnchorObservationTests
RECORDS=[]


class TemporalProjectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        AnchorObservationTests.setUpClass();cls.helper=AnchorObservationTests()
    @classmethod
    def tearDownClass(cls):
        label=os.environ.get('B4ML_RUN_LABEL','temporal-projection-development')
        (ROOT/f'training/b4artists_ml/results/{label}-projection.json').write_text(json.dumps(RECORDS,indent=2)+'\n')
    def fixture(self,label='boneforge'):
        ob,binding,*_=self.helper.fixture(label)
        ob.b4ml.anchors[1].frame=5
        return ob,binding
    def test_external_proposal_moves_unpinned_joints_without_pose_model(self):
        ob,binding=self.fixture();before=self.helper.state(ob);session=bs.Session(ob)
        try:
            points=session.world_points(session.baseline);target=points.copy();mask=np.zeros(17,bool);mask[0]=True
            proposal=points.copy();proposal[7]+=(.01,.005,.004)
            with patch('b4artists_ml.body_solver.forward',side_effect=AssertionError('Pose model must not run')):
                result=session.solve(target,mask,learned_influence=0.,proposal_world=proposal)
            self.assertEqual(result['proposal_source'],'external_motion');self.assertIsNone(result['model_sha256'])
            self.assertEqual(result['neural_residual_norm'],0.)
            self.assertLess(np.linalg.norm(session.world_points(session.points())[7]-proposal[7]),np.linalg.norm(points[7]-proposal[7]))
            self.assertLess(result['pin_error'],2e-4);self.assertLess(result['length_error'],.002)
        finally:session.cancel()
        self.assertEqual(self.helper.state(ob),before)
    def test_all_eight_profiles_generate_editable_priority_preserving_candidates(self):
        for label in self.helper.builders:
            with self.subTest(profile=label):
                ob,binding=self.fixture(label);before=self.helper.state(ob);anchors=dict(w.read_anchors(ob))
                samples,metrics=tp.generate_samples(ob,tp.procedural,context=False)
                self.assertEqual(self.helper.state(ob),before)
                for f,row in anchors.items():self.assertEqual(json.loads(json.dumps(samples[f])),row['pose'])
                self.assertEqual(set(samples),{3,4,5});self.assertEqual(len(metrics),1)
                w.preview(ob,bpy.context.scene,pose_samples=samples)
                self.assertEqual(ob.b4ml.candidate_action.get('b4ml_backend'),'projected_semantic_motion_v1')
                bpy.context.scene.frame_set(4);p._update(ob)
                actual=w.raw_pose(ob,samples[4]);self.assertEqual(set(actual),set(samples[4]))
                for n,v in samples[4].items():
                    np.testing.assert_allclose(actual[n]['location'],v['location'],atol=2e-6)
                    self.assertGreater(abs(np.dot(actual[n]['rotation'],v['rotation'])),1.-2e-6)
                bpy.context.scene.frame_set(7,subframe=.25);w.finish_preview(ob,bpy.context.scene,False)
                self.assertEqual(self.helper.state(ob),before)
                RECORDS.append(dict(profile=label,metrics=metrics,editable_action=True,source_restored=True))
    def test_hidden_modeled_source_keys_cannot_improve_generated_pose(self):
        for label in ('boneforge','rigify_default','unity_humanoid'):
            ob,binding=self.fixture(label);a,_=tp.generate_samples(ob,tp.procedural,context=False)
            bpy.context.scene.frame_set(4)
            for n in binding['controls']:
                bone=ob.pose.bones[n];bone.location.x+=.7
                bone.keyframe_insert('location',frame=4)
                bs._set_quat(bone,bs._quat(bone)@tp.Quaternion((1,0,0),.8))
                prop='rotation_quaternion' if bone.rotation_mode=='QUATERNION' else ('rotation_axis_angle' if bone.rotation_mode=='AXIS_ANGLE' else 'rotation_euler')
                bone.keyframe_insert(prop,frame=4)
            bpy.context.scene.frame_set(7,subframe=.25);before=self.helper.state(ob)
            b,_=tp.generate_samples(ob,tp.procedural,context=False)
            self.assertEqual(self.helper.state(ob),before)
            for name,row in a[4].items():
                np.testing.assert_allclose(row['location'],b[4][name]['location'],atol=2e-6)
                self.assertGreater(abs(np.dot(row['rotation'],b[4][name]['rotation'])),1.-2e-6)
    def test_invalid_provider_and_cancellation_restore_source(self):
        ob,binding=self.fixture();before=self.helper.state(ob)
        def bad(obs,t):
            points,rot=tp.procedural(obs,t);points[0,2,0]=np.nan;return points,rot
        with self.assertRaises(ValueError):tp.preview(ob,bad,context=False)
        self.assertEqual(self.helper.state(ob),before);self.assertFalse(ob.b4ml.candidate_action)
        calls=[]
        def cancel():calls.append(1);return len(calls)>5
        with self.assertRaises(InterruptedError):tp.preview(ob,tp.procedural,context=False,cancel_requested=cancel)
        self.assertEqual(self.helper.state(ob),before);self.assertFalse(ob.b4ml.candidate_action)
    def test_projected_samples_validate_before_candidate_mutation(self):
        ob,binding=self.fixture();before=self.helper.state(ob);samples,_=tp.generate_samples(ob,tp.procedural,context=False)
        bad=copy.deepcopy(samples);bad[3][binding['root']]['location'][0]+=.02
        with self.assertRaisesRegex(ValueError,'priorities'):w.preview(ob,bpy.context.scene,pose_samples=bad)
        self.assertEqual(self.helper.state(ob),before)
        bad=copy.deepcopy(samples);bad.pop(4)
        with self.assertRaisesRegex(ValueError,'every'):w.preview(ob,bpy.context.scene,pose_samples=bad)
        self.assertEqual(self.helper.state(ob),before)
    def test_external_invalid_proposals_reject_without_pose_mutation(self):
        ob,binding=self.fixture();before=self.helper.state(ob);session=bs.Session(ob)
        try:
            points=session.world_points(session.baseline);mask=np.zeros(17,bool);mask[0]=True;normalized=w.raw_pose(ob)
            for proposal,influence in ((np.zeros((16,3)),0.),(np.full((17,3),np.nan),0.),(points,1.)):
                with self.assertRaises(ValueError):session.solve(points,mask,proposal_world=proposal,learned_influence=influence)
                self.assertEqual(w.raw_pose(ob),normalized)
        finally:session.cancel()
        self.assertEqual(self.helper.state(ob),before)

    def test_multiple_subframe_priorities_and_explicit_contact_pin(self):
        ob,binding=self.fixture('unity_humanoid')
        ob.b4ml.anchors[0].frame=3.25;ob.b4ml.anchors[1].frame=5.5
        extra=ob.b4ml.anchors.add();extra.frame=7.75;extra.payload=ob.b4ml.anchors[0].payload
        samples,metrics=tp.generate_samples(ob,tp.procedural,context=False)
        self.assertEqual(set(samples),{3.25,4,5,5.5,6,7,7.75})
        # Derive an attainable contact from the already projected baseline, then
        # deliberately move its soft proposal. The explicit pin must win.
        source=w.raw_pose(ob);modes=rs.mode_values(ob);scene=bpy.context.scene
        scene.frame_set(4);w.restore_pose(ob,samples[4]);p._update(ob)
        pin=np.array(ob.matrix_world@ob.pose.bones[binding['names'][13]].head)
        w.restore_pose(ob,source);rs.restore_values(ob,modes);scene.frame_set(7,subframe=.25)
        before=self.helper.state(ob)
        def shifted(obs,t):
            points,rot=tp.procedural(obs,t);points[:,13,0]+=.02;return points,rot
        pinned,report=tp.generate_samples(ob,shifted,context=False,constraints={4:{'position_pins':{13:pin}}})
        self.assertLess(report[0]['pin_error'],2e-4);self.assertEqual(self.helper.state(ob),before)
        for f,row in w.read_anchors(ob):self.assertEqual(json.loads(json.dumps(pinned[f])),row['pose'])
        RECORDS.append(dict(case='multiple_subframes_pinned_contact',metrics=report))

    def test_unselected_accessory_curve_and_bound_mesh_survive(self):
        ob,binding=self.fixture('unity_humanoid');scene=bpy.context.scene
        accessory=next(b for b in ob.pose.bones if b.name not in binding['controls'])
        for f,x in ((1,.01),(4,.07),(8,-.02)):
            accessory.location.x=x;accessory.keyframe_insert('location',frame=f)
        scene.frame_set(7,subframe=.25);source=ob.animation_data.action
        path=accessory.path_from_id('location')
        def keys(action):return [(c.array_index,[(tuple(k.co),tuple(k.handle_left),tuple(k.handle_right),k.interpolation) for k in c.keyframe_points]) for c in w.action_curves(action,ob.animation_data.action_slot) if c.data_path==path]
        original=keys(source)
        mesh=next(o for o in scene.objects if o.type=='MESH')
        def vertices():
            p._update(ob);ev=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get())
            return np.array([ev.matrix_world@v.co for v in ev.data.vertices])
        scene.frame_set(4);input_vertices=vertices();scene.frame_set(7,subframe=.25)
        tp.preview(ob,tp.procedural,context=False)
        self.assertEqual(keys(ob.b4ml.candidate_action),original);self.assertEqual(keys(source),original)
        scene.frame_set(4);self.assertTrue(np.isfinite(vertices()).all());self.assertGreater(np.linalg.norm(vertices()-input_vertices),1e-4)
        scene.frame_set(7,subframe=.25);w.finish_preview(ob,scene,False);self.assertIs(ob.animation_data.action,source)
        self.assertEqual(keys(source),original)

    def test_priority_euler_turns_are_kept_in_editable_action(self):
        ob,binding=self.fixture('mocap_humanoid');name=binding['rotations'][1];bone=ob.pose.bones[name]
        bone.rotation_mode='XYZ'
        # Recapture consistent mode metadata, then retain an authored full turn.
        for anchor in ob.b4ml.anchors:
            data=json.loads(anchor.payload);row=data['pose'][name];row['mode']='XYZ';row['raw_rotation']=[6.283185307179586,0.,0.]
            row['rotation']=list(tp.Quaternion((1,0,0),6.283185307179586));anchor.payload=json.dumps(data)
        samples,_=tp.generate_samples(ob,tp.procedural,context=False)
        w.preview(ob,bpy.context.scene,pose_samples=samples)
        for frame in (3,5):
            bpy.context.scene.frame_set(frame);self.assertAlmostEqual(bone.rotation_euler.x,6.283185307179586,places=5)
        bpy.context.scene.frame_set(7,subframe=.25);w.finish_preview(ob,bpy.context.scene,False)

    def test_candidate_insertion_interruption_rolls_back(self):
        ob,binding=self.fixture();samples,_=tp.generate_samples(ob,tp.procedural,context=False);before=self.helper.state(ob)
        original=w.action_curves
        def interrupt(action,*args,**kwargs):
            if action!=before[5]:raise KeyboardInterrupt('injected candidate failure')
            return original(action,*args,**kwargs)
        with patch('b4artists_ml.workflow.action_curves',interrupt):
            with self.assertRaises(KeyboardInterrupt):w.preview(ob,bpy.context.scene,pose_samples=samples)
        self.assertFalse(ob.b4ml.candidate_action);self.assertFalse(ob.b4ml.source_slot)
        self.assertEqual(self.helper.state(ob),before)

    def test_generated_action_keep_save_reload_and_restore(self):
        ob,binding=self.fixture('unreal_mannequin');scene=bpy.context.scene;source=ob.animation_data.action.name;name=ob.name
        tp.preview(ob,tp.procedural,context=False);w.finish_preview(ob,scene,True)
        candidate=ob.animation_data.action.name
        label=os.environ.get('B4ML_RUN_LABEL','temporal-projection-development')
        path=ROOT/f'training/b4artists_ml/cache/{label}-kept.blend'
        bpy.ops.wm.save_as_mainfile(filepath=str(path));bpy.ops.wm.open_mainfile(filepath=str(path))
        ob=bpy.data.objects[name];self.assertEqual(ob.animation_data.action.name,candidate)
        self.assertEqual(ob.b4ml.kept_source.name,source)
        w.restore_kept_source(ob,bpy.context.scene)
        self.assertEqual(ob.animation_data.action.name,source);self.assertIn(candidate,bpy.data.actions)

    def test_intermediate_rotation_proposal_guides_twist(self):
        ob,binding=self.fixture('unity_humanoid');session=bs.Session(ob)
        try:
            from mathutils import Quaternion
            points=session.world_points(session.baseline);mask=np.zeros(17,bool);mask[0]=True
            rotations=[(ob.matrix_world@ob.pose.bones[n].matrix).to_quaternion() for n in binding['names']]
            rotations[5]=rotations[5]@Quaternion((0,1,0),.2)
            before=bs._angle(rotations[5],(ob.matrix_world@ob.pose.bones[binding['names'][5]].matrix).to_quaternion())
            result=session.solve(points,mask,proposal_world=points,proposal_rotations_world=[tuple(q) for q in rotations],learned_influence=0.,iterations=100)
            after=bs._angle(rotations[5],(ob.matrix_world@ob.pose.bones[binding['names'][5]].matrix).to_quaternion())
            self.assertLess(after,before-.01);self.assertIsNotNone(result['proposal_rotation_error_radians'])
            from b4artists_ml import joint_limits
            name=binding['names'][5]
            limited=session.solve(points,mask,proposal_world=points,proposal_rotations_world=[tuple(q) for q in rotations],learned_influence=0.,iterations=100,
                rotation_limits={name:dict(swing=2.9,twist_min=-.005,twist_max=.005)})
            self.assertLess(abs(joint_limits.angles(bs._quat(ob.pose.bones[name]))[1]),.006)
            self.assertLess(limited['joint_limit_error_radians'],.001)
        finally:session.cancel()

    def test_later_projection_failure_never_publishes_partial_action(self):
        ob,binding=self.fixture('unity_humanoid');ob.b4ml.anchors[1].frame=7
        before=self.helper.state(ob);successful=[];original=bs.Session.solve
        def record(session,*args,**kwargs):
            result=original(session,*args,**kwargs);successful.append(bpy.context.scene.frame_current);return result
        with patch.object(bs.Session,'solve',record):
            with self.assertRaises(bs.ProjectionError):
                tp.preview(ob,tp.procedural,context=False,constraints={5:{'position_pins':{13:[30,30,30]}}})
        self.assertEqual(successful,[4]);self.assertEqual(self.helper.state(ob),before);self.assertFalse(ob.b4ml.candidate_action)

    def test_provider_cannot_mutate_world_calibration(self):
        ob,binding=self.fixture();a,_=tp.generate_samples(ob,tp.procedural,context=False)
        def mutate(obs,t):
            out=tp.procedural(obs,t);obs.origin[:]+=100.;obs.basis[:]*=2.;return out
        b,_=tp.generate_samples(ob,mutate,context=False)
        self.assertEqual(a,b)

    def test_invalid_full_orientation_proposal_is_reversible(self):
        ob,binding=self.fixture();before=self.helper.state(ob);session=bs.Session(ob)
        try:
            points=session.world_points(session.baseline);mask=np.zeros(17,bool);mask[0]=True;pose=w.raw_pose(ob)
            for value in (np.zeros((17,4)),np.full((17,4),np.nan),np.ones((16,4))):
                with self.assertRaisesRegex(ValueError,'orientations'):
                    session.solve(points,mask,proposal_world=points,proposal_rotations_world=value,learned_influence=0.)
                self.assertEqual(w.raw_pose(ob),pose)
        finally:session.cancel()
        self.assertEqual(self.helper.state(ob),before)
