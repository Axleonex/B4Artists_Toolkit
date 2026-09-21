"""Semantic synchronization, missing-data isolation and independent training math tests."""
from pathlib import Path
import sys
import json
import unittest
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'training/b4artists_ml'))
from bvh_data import parse_bvh
from context_data import semantic_motion,examples,encode,retarget_pose,LIMBS,NAMES,JOINTS
from context_network import initialize,forward,loss_and_grad,Adam
try:
    import bpy
except ImportError:
    bpy=None

class ContextDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.motion=parse_bvh((ROOT/'training/b4artists_ml/cache/07_01.bvh').read_text())
        cls.semantic=semantic_motion(cls.motion)

    def test_inverse_coordinates_and_frame_sync(self):
        s=self.semantic;world=self.motion.positions()[:,[self.motion.names.index(n) for n in NAMES]]
        actual=np.einsum('fij,fkj->fki',s.bases,s.positions*s.scale)+s.origins[:,None,:]
        np.testing.assert_allclose(actual,world[s.frames],atol=1e-10)
        self.assertEqual(s.frames[0],1)
        self.assertTrue(np.all(np.diff(s.frames)==8))
        np.testing.assert_allclose(s.positions[:,0],0,atol=1e-10)

    def test_hidden_labels_cannot_leak(self):
        d=examples(self.semantic,3)
        changed=d['target'].copy();changed[~d['mask']]=np.nan
        np.testing.assert_array_equal(encode(d['rest'],d['baseline'],changed,d['mask']),d['x'])
        changed[d['mask']]+=1
        self.assertFalse(np.array_equal(encode(d['rest'],d['baseline'],changed,d['mask']),d['x']))

    def test_prior_is_strictly_earlier_or_reference(self):
        for mode in ('mixed','neutral','prior'):
            d=examples(self.semantic,4,mode=mode)
            self.assertTrue(np.all(d['baseline_frame']<d['frame']))
            self.assertFalse(d['mask'][:,[6,9,12,15]].any())
            self.assertTrue(d['mask'][:,0].all())
            self.assertEqual(d['x'].shape[1],170)

    def test_retarget_preserves_lengths_and_directions(self):
        pose=self.semantic.positions[:5]
        ratios=(.425,.537037,.505879,.541468)
        changed=retarget_pose(pose,ratios)
        for (root,joint,end),ratio in zip(LIMBS,ratios):
            old_a=pose[:,joint]-pose[:,root];old_b=pose[:,end]-pose[:,joint]
            new_a=changed[:,joint]-changed[:,root];new_b=changed[:,end]-changed[:,joint]
            norm=lambda x:np.linalg.norm(x,axis=1,keepdims=True)
            np.testing.assert_allclose(norm(old_a)+norm(old_b),norm(new_a)+norm(new_b),atol=1e-10)
            np.testing.assert_allclose(old_a/norm(old_a),new_a/norm(new_a),atol=1e-10)
            np.testing.assert_allclose(old_b/norm(old_b),new_b/norm(new_b),atol=1e-10)
            np.testing.assert_allclose(norm(new_a)/(norm(new_a)+norm(new_b)),ratio,atol=1e-10)


class ProjectionTests(unittest.TestCase):
    def fixture(self):
        motion=parse_bvh((ROOT/'training/b4artists_ml/cache/07_01.bvh').read_text())
        d=examples(semantic_motion(motion),7,augment=False,mode='neutral')
        return d

    def test_preserves_pins_and_recovers_reference_lengths(self):
        from context_projection import project_pose
        d=self.fixture();target=d['target'][:1];rest=d['rest'][:1]
        mask=d['mask'][:1];start=target.copy()
        start[:,[6,9,12,15]]+=.025
        predicted,stats=project_pose(start,rest,target,mask,iterations=600)
        self.assertTrue(stats['converged'].all())
        np.testing.assert_array_equal(predicted[mask],target[mask])
        self.assertLessEqual(stats['max_length_error'].max(),1e-3)

    def test_newton_batch_length_and_pin_convergence(self):
        from context_projection import project_pose_newton
        d=self.fixture()
        # Multiple substantially displaced starts, not just a near-solution test.
        target=d['target'][:20];rest=d['rest'][:20];mask=d['mask'][:20]
        start=target.copy();start[:,[6,9,12,15]]+=.15
        predicted,stats=project_pose_newton(start,rest,target,mask)
        self.assertTrue(stats['converged'].all())
        np.testing.assert_array_equal(predicted[mask],target[mask])
        impossible=target[0].copy();impossible[7]+=[20,0,0]
        fixed=np.ones(JOINTS,dtype=bool)
        output,failed=project_pose_newton(impossible,rest[0],impossible,fixed,iterations=5)
        self.assertFalse(failed['converged'][0])
        np.testing.assert_array_equal(output,impossible)

    def test_reports_impossible_pins_without_moving_them(self):
        from context_projection import project_pose
        d=self.fixture();target=d['target'][0].copy();mask=np.ones(JOINTS,dtype=bool)
        target[7]+=[20,0,0]
        predicted,stats=project_pose(target,d['rest'][0],target,mask,iterations=5)
        self.assertFalse(stats['converged'][0])
        np.testing.assert_array_equal(predicted,target)
        self.assertEqual(stats['pin_error'][0],0)


class PipelineTests(unittest.TestCase):
    def test_real_model_missing_inputs_strength_and_preservation(self):
        from context_pipeline import decode_model,complete_pose
        params=decode_model((ROOT/'training/b4artists_ml/results/context_pose_mlp_v1.npz').read_bytes())
        motion=parse_bvh((ROOT/'training/b4artists_ml/cache/75_02.bvh').read_text())
        d=examples(semantic_motion(motion),9,augment=False,mode='neutral')
        i=min(12,len(d['x'])-1)
        rest=d['rest'][i].copy();baseline=d['baseline'][i].copy();target=d['target'][i].copy();mask=d['mask'][i].copy()
        original=(rest.copy(),baseline.copy(),target.copy(),mask.copy())
        expected,stats=complete_pose(params,rest,baseline,target,mask)
        target[~mask]=np.nan
        actual,_=complete_pose(params,rest,baseline,target,mask)
        np.testing.assert_array_equal(actual,expected)
        geometric,_=complete_pose(params,rest,baseline,target,mask,learned_influence=0)
        self.assertGreater(float(np.linalg.norm(actual-geometric)),1e-5)
        np.testing.assert_array_equal(actual[mask],target[mask])
        np.testing.assert_array_equal(rest,original[0]);np.testing.assert_array_equal(baseline,original[1]);np.testing.assert_array_equal(mask,original[3])
        self.assertLessEqual(stats['max_length_error'],1e-3)

    def test_rejects_corrupt_model_and_failed_constraints(self):
        from context_pipeline import decode_model,complete_pose
        with self.assertRaises(ValueError):decode_model(b'corrupt')
        params=decode_model((ROOT/'training/b4artists_ml/results/context_pose_mlp_v1.npz').read_bytes())
        motion=parse_bvh((ROOT/'training/b4artists_ml/cache/75_02.bvh').read_text())
        pose=semantic_motion(motion).rest
        targets=pose.copy();targets[7]+=[20,0,0]
        with self.assertRaisesRegex(ValueError,'did not converge'):
            complete_pose(params,pose,pose,targets,np.ones(JOINTS,bool))
        np.testing.assert_array_equal(pose,semantic_motion(motion).rest)

class NetworkTests(unittest.TestCase):
    def test_gradients_against_finite_differences(self):
        rng=np.random.default_rng(4);p=initialize(4,5,3,dtype=np.float64)
        x=rng.normal(size=(3,4));target=rng.normal(size=(3,3));weights=rng.random((3,3))
        _,gradient=loss_and_grad(p,x,target,weights,regularization=.003)
        for key,value in p.items():
            for index in np.ndindex(value.shape):
                old=value[index];step=1e-6
                value[index]=old+step;plus=loss_and_grad(p,x,target,weights,.003)[0]
                value[index]=old-step;minus=loss_and_grad(p,x,target,weights,.003)[0]
                value[index]=old
                self.assertAlmostEqual(gradient[key][index],(plus-minus)/(2*step),places=7)

    def test_training_reduces_known_nonlinear_loss(self):
        rng=np.random.default_rng(5);x=rng.normal(size=(64,3)).astype(np.float32)
        target=np.tanh(x[:,:1]*2-x[:,1:2]);weights=np.ones_like(target)
        p=initialize(3,16,1);opt=Adam(p,.01)
        initial=loss_and_grad(p,x,target,weights)[0]
        for _ in range(150):
            loss,grad=loss_and_grad(p,x,target,weights);opt.step(p,grad)
        self.assertLess(loss,initial*.1)

@unittest.skipIf(bpy is None,'Bforartists runtime required')
class HostSemanticTests(unittest.TestCase):
    def test_actual_imported_landmarks_and_pelvis_rotation(self):
        from io_anim_bvh import import_bvh
        from mathutils import Matrix
        records=[]
        for clip in ('07_01','15_06'):
            path=ROOT/'training/b4artists_ml/cache'/(clip+'.bvh')
            motion=parse_bvh(path.read_text());s=semantic_motion(motion)
            import_bvh.load(bpy.context,filepath=str(path),global_matrix=Matrix.Identity(4),global_scale=1.,
                frame_start=1,use_fps_scale=False,update_scene_fps=False,update_scene_duration=False,rotate_mode='NATIVE')
            obj=bpy.context.object;errors=[]
            _,rotations=motion.transforms()
            for i in np.linspace(0,len(s.frames)-1,7,dtype=int):
                bpy.context.scene.frame_set(int(s.frames[i])+1)
                evaluated=obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
                reconstructed=np.einsum('ij,kj->ki',s.bases[i],s.positions[i]*s.scale)+s.origins[i]
                for j,name in enumerate(NAMES):
                    errors.append(float(np.linalg.norm(np.asarray(evaluated.pose.bones[name].head)-reconstructed[j])))
                pb=evaluated.pose.bones['Hips']
                actual=np.asarray(pb.matrix.to_3x3()@pb.bone.matrix_local.to_3x3().inverted())
                np.testing.assert_allclose(actual,rotations[s.frames[i],motion.names.index('Hips')],atol=1e-5)
            self.assertLess(max(errors),2e-4)
            records.append(dict(clip=clip,joint_samples=len(errors),max_world_error=max(errors)))
        print('CONTEXT_HOST_EVIDENCE: '+json.dumps(records),flush=True)

if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__]))
    print('B4ML_CONTEXT_RESULT: '+('PASS' if result.wasSuccessful() else 'FAIL'),flush=True)
    if not result.wasSuccessful():raise SystemExit(1)
