"""Actual generated-rig contextual completion and source preservation tests."""
from pathlib import Path
import os,sys,json,time,unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'tests'),str(ROOT/'training/b4artists_ml')]
import numpy as np
try:import bpy
except ImportError:bpy=None
RECORDS=[]

@unittest.skipIf(bpy is None,'Bforartists required')
class ContextRigTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import b4artists_ml
        b4artists_ml.register()
        from test_b4artists_ml_posing import boneforge_rig,rigify_rig
        cls.builders={'boneforge':boneforge_rig,'rigify_basic':rigify_rig,
            'rigify_default':lambda:rigify_rig(full=True),'metarig_basic':lambda:rigify_rig(generate=False),
            'metarig_default':lambda:rigify_rig(full=True,generate=False)}

    def fixture(self,label,transformed=False,animated=False,pose_factor=1.):
        from b4artists_ml import posing as p,workflow as w
        from context_rig import Session,_quat,_set_quat
        from mathutils import Quaternion
        bpy.context.window.scene=bpy.data.scenes.new('Context fixture '+label)
        ob=self.builders[label]()
        if transformed:
            ob.location=(2,-1,.5);ob.rotation_euler=(.2,-.1,.45);ob.scale=(1.7,)*3
        if animated:
            ob.pose.bones['hips'].keyframe_insert(data_path='location',frame=1)
            ob.pose.bones['hips'].keyframe_insert(data_path='location',frame=10)
        p._update(ob)
        source=w.raw_pose(ob);session=Session(ob)
        rest=session.world_points(session.baseline)
        # Obtain feasible target pins by authoring real controls, then restore the starting pose.
        body='spine.01' if label=='boneforge' else 'chest' if label.startswith('rigify') else 'spine.001'
        bone=ob.pose.bones[body];_set_quat(bone,_quat(bone)@Quaternion((1,0,0),.12*pose_factor))
        for name in session.binding['rotations'][-8:]:
            bone=ob.pose.bones[name];_set_quat(bone,_quat(bone)@Quaternion((1,0,0),.18*pose_factor))
        ob.pose.bones[session.binding['root']].location.z-=.015*pose_factor
        p._update(ob);targets=session.world_points(session.points())
        w.restore_pose(ob,session.normalized);p._update(ob)
        mask=np.zeros(17,bool);mask[[0,4,7,10,13,16]]=True
        self.assertGreater(float(np.linalg.norm(targets-rest)),.01)
        return ob,source,session,targets,mask

    def test_real_rigs_learned_projection_and_cancel(self):
        from b4artists_ml import workflow as w,rig_state as rs
        from mathutils import Vector
        labels=os.environ.get('B4ML_CONTEXT_RIGS',','.join(self.builders)).split(',')
        for label in labels:
            with self.subTest(rig=label):
                ob,source,session,targets,mask=self.fixture(label)
                before_modes=session.source_modes
                constraints={b.name:[(c.name,c.type,c.influence,c.mute) for c in b.constraints] for b in ob.pose.bones}
                # Bound vertex follows an actual deform bone, not a control head proxy.
                joint=session.binding['names'][7]
                deform='hand.def-L' if label=='boneforge' else 'DEF-hand.L' if label.startswith('rigify') else joint
                data=bpy.data.meshes.new('Context weighted mesh')
                point=ob.data.bones[deform].head_local.copy()
                data.from_pydata([point,point+Vector((0.01,0,0)),point+Vector((0,0.01,0))],[],[(0,1,2)])
                mesh=bpy.data.objects.new('Context weighted mesh',data);bpy.context.scene.collection.objects.link(mesh)
                mesh.vertex_groups.new(name=deform).add([0,1,2],1.,'REPLACE')
                mesh.modifiers.new('Armature','ARMATURE').object=ob
                try:
                    geometric=session.solve(targets,mask,learned_influence=0.)
                    stats=session.solve(targets,mask)
                    arm_effect=float(np.max(np.linalg.norm(stats['points'][[6,9]]-geometric['points'][[6,9]],axis=1)))
                    self.assertGreater(arm_effect,1e-5)
                    stats['learned_arm_change_vs_geometric']=arm_effect
                    actual=session.world_points(session.points())
                    self.assertLess(float(np.max(np.linalg.norm(actual[mask]-targets[mask],axis=1)))/session.scale,2e-4)
                    self.assertGreater(stats['neural_residual_norm'],.001)
                    evaluated=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get())
                    expected=ob.pose.bones[deform].matrix@ob.data.bones[deform].matrix_local.inverted()@point
                    self.assertLess((evaluated.data.vertices[0].co-expected).length,1e-5)
                    self.assertGreater((evaluated.data.vertices[0].co-point).length,.005)
                    self.assertEqual(constraints,{b.name:[(c.name,c.type,c.influence,c.mute) for c in b.constraints] for b in ob.pose.bones})
                    row={k:v for k,v in stats.items() if k!='points'};row['fixture']=label;RECORDS.append(row)
                    print('CONTEXT_RIG_METRIC: '+json.dumps(row),flush=True)
                finally:
                    session.cancel()
                    bpy.data.objects.remove(mesh,do_unlink=True);bpy.data.meshes.remove(data)
                self.assertEqual(rs.mode_values(ob),before_modes)
                restored=w.raw_pose(ob,session.binding['controls'])
                self.assertEqual(restored,{n:source[n] for n in restored})

    def test_pelvis_translation_uses_zero_origin_model_frame(self):
        from unittest.mock import patch
        from context_rig import forward
        ob,source,session,targets,mask=self.fixture('boneforge')
        seen=[]
        def inspect(params,features):
            raw=features*params['scale']+params['mean']
            seen.append(raw.copy())
            np.testing.assert_allclose(raw[0,102:105],0.,atol=1e-7)
            return forward(params,features)
        try:
            with patch('context_rig.forward',side_effect=inspect):
                session.solve(targets,mask)
            self.assertEqual(len(seen),1)
        finally:session.cancel()

    def test_transformed_rig_preserves_source_animation(self):
        from b4artists_ml import workflow as w
        ob,source,session,targets,mask=self.fixture('boneforge',transformed=True,animated=True)
        action=ob.animation_data.action;slot=ob.animation_data.action_slot
        def keys():
            return [(fc.data_path,fc.array_index,[(tuple(k.co),tuple(k.handle_left),tuple(k.handle_right),k.interpolation) for k in fc.keyframe_points])
                    for fc in w.action_curves(action,slot)]
        original=keys()
        try:
            result=session.solve(targets,mask)
            self.assertLess(result['pin_error'],2e-4)
            self.assertEqual(keys(),original)
            self.assertEqual(ob.animation_data.action,action)
            self.assertEqual(ob.animation_data.action_slot,slot)
        finally:session.cancel()
        self.assertEqual(keys(),original)
        self.assertEqual(w.raw_pose(ob,session.binding['controls']),{n:source[n] for n in session.binding['controls']})

    def test_derivative_reuse_matches_dense_gates(self):
        labels=os.environ.get('B4ML_CONTEXT_RIGS',','.join(self.builders)).split(',')
        for label in labels:
            with self.subTest(rig=label):
                ob,source,session,targets,mask=self.fixture(label)
                try:
                    dense=session.solve(targets,mask,jacobian_mode='dense')
                    reused=session.solve(targets,mask,jacobian_mode='reuse')
                    comparison=dict(fixture=label,dense={k:v for k,v in dense.items() if k!='points'},
                        reused={k:v for k,v in reused.items() if k!='points'})
                    RECORDS.append(comparison)
                    print('CONTEXT_REUSE: '+json.dumps(comparison),flush=True)
                    self.assertLess(reused['pin_error'],2e-4)
                    self.assertLess(reused['length_error'],.002)
                    self.assertLessEqual(reused['proposal_error'],dense['proposal_error']*1.05)
                    self.assertLess(reused['evaluations'],dense['evaluations']*.5)
                finally:session.cancel()

    def test_mid_solve_cancellation_restores_previous_preview(self):
        from b4artists_ml import workflow as w,rig_state as rs
        ob,source,session,targets,mask=self.fixture('boneforge')
        try:
            session.solve(targets,mask)
            before=w.raw_pose(ob,session.binding['controls']);modes=rs.mode_values(ob)
            calls=0
            def cancelled():
                nonlocal calls
                calls+=1
                return calls==20
            with self.assertRaises(InterruptedError):
                session.solve(targets,mask,jacobian_mode='reuse',cancel_requested=cancelled)
            self.assertEqual(calls,20)
            self.assertEqual(w.raw_pose(ob,session.binding['controls']),before)
            self.assertEqual(rs.mode_values(ob),modes)
        finally:session.cancel()

    def test_progress_close_restores_state_and_prevents_overlap(self):
        from b4artists_ml import workflow as w
        ob,source,session,targets,mask=self.fixture('boneforge')
        before=w.raw_pose(ob,session.binding['controls'])
        steps=session.solve_steps(targets,mask,jacobian_mode='reuse')
        try:
            progress=next(steps)
            self.assertEqual(progress['phase'],'derivatives')
            self.assertTrue(session.running)
            # First progress comes before fitting: no derivative probe must remain visible.
            self.assertEqual(w.raw_pose(ob,session.binding['controls']),before)
            with self.assertRaisesRegex(ValueError,'already active'):session.solve(targets,mask)
        finally:steps.close()
        self.assertFalse(session.running)
        self.assertEqual(w.raw_pose(ob,session.binding['controls']),before)
        session.cancel()

    def test_progress_exhaustion_matches_synchronous_result(self):
        label=os.environ.get('B4ML_PROGRESS_RIG','boneforge')
        ob,source,session,targets,mask=self.fixture(label)
        try:
            expected=session.solve(targets,mask,jacobian_mode='reuse')
            steps=session.solve_steps(targets,mask,jacobian_mode='reuse');progress=[];durations=[]
            while True:
                try:
                    began=time.perf_counter();progress.append(next(steps));durations.append((time.perf_counter()-began)*1000)
                except StopIteration as done:
                    actual=done.value;break
            self.assertFalse(session.running)
            self.assertGreater(len(progress),10)
            np.testing.assert_allclose(actual['points'],expected['points'],atol=2e-5)
            self.assertLess(actual['pin_error'],2e-4)
            row=dict(kind='progress_scheduling',fixture=label,checkpoints=len(progress),
                median_checkpoint_ms=float(np.median(durations)),p95_checkpoint_ms=float(np.percentile(durations,95)),
                max_checkpoint_ms=max(durations),synchronous_ms=expected['elapsed_ms'],cooperative_ms=actual['elapsed_ms'],
                pin_error=actual['pin_error'],max_pose_difference=float(np.max(np.linalg.norm(actual['points']-expected['points'],axis=1))))
            RECORDS.append(row);print('CONTEXT_PROGRESS: '+json.dumps(row),flush=True)
        finally:session.cancel()

    def test_reuse_varied_reachable_poses(self):
        for label in ('boneforge','rigify_basic'):
            for factor in (-.75,2.):
                with self.subTest(rig=label,factor=factor):
                    ob,source,session,targets,mask=self.fixture(label,pose_factor=factor)
                    try:
                        dense=session.solve(targets,mask,iterations=80,jacobian_mode='dense')
                        reused=session.solve(targets,mask,iterations=80,jacobian_mode='reuse')
                        row=dict(fixture=label,pose_factor=factor,dense={k:v for k,v in dense.items() if k!='points'},
                            reused={k:v for k,v in reused.items() if k!='points'})
                        RECORDS.append(row);print('CONTEXT_VARIED: '+json.dumps(row),flush=True)
                        self.assertLess(reused['pin_error'],2e-4)
                        self.assertLessEqual(reused['proposal_error'],dense['proposal_error']*1.05)
                        self.assertLess(reused['evaluations'],dense['evaluations']*.5)
                    finally:session.cancel()

    def test_single_session_ownership_released_on_cancel(self):
        from context_rig import Session
        from b4artists_ml import workflow as w
        ob,source,session,targets,mask=self.fixture('boneforge')
        before=w.raw_pose(ob)
        with self.assertRaisesRegex(ValueError,'owns this rig'):Session(ob)
        self.assertEqual(w.raw_pose(ob),before)
        session.cancel()
        replacement=Session(ob)
        replacement.cancel()

    def test_impossible_request_rolls_back(self):
        from b4artists_ml import workflow as w
        ob,source,session,targets,mask=self.fixture('boneforge')
        before=w.raw_pose(ob,session.binding['controls'])
        targets[7]+=[20,0,0]
        with self.assertRaisesRegex(ValueError,'Actual rig projection failed'):
            session.solve(targets,mask,iterations=3)
        self.assertEqual(w.raw_pose(ob,session.binding['controls']),before)
        session.cancel()

if __name__=='__main__':
    selection=os.environ.get('B4ML_CONTEXT_TEST')
    suite=unittest.defaultTestLoader.loadTestsFromName(selection,sys.modules[__name__]) if selection else unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    (ROOT/'training/b4artists_ml/results'/(os.environ.get('B4ML_CONTEXT_RESULT') or ('context_rig_supplement_v1.json' if selection else 'context_rig_v1.json'))).write_text(json.dumps(dict(tests=result.testsRun,failures=len(result.failures),errors=len(result.errors),skips=len(result.skipped),passed=result.wasSuccessful(),records=RECORDS),indent=2)+'\n')
    print('CONTEXT_RIG_RESULT: '+('PASS' if result.wasSuccessful() else 'FAIL'),flush=True)
    if not result.wasSuccessful():raise SystemExit(1)
