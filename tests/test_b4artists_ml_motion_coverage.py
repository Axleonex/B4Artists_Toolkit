"""Known-motion feature isolation and explicit oracle diagnostic boundaries."""
import sys,unittest
from pathlib import Path
from copy import deepcopy
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'training/b4artists_ml'))
from bvh_data import parse_bvh
from sequence_data import full_motion,known_window,target_window
from motion_coverage import observed_features,rotation_log,squared_distance,fit_feature_normalization,oracle_coefficients
from temporal_data import quat_matrix

class CoverageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.motion=full_motion(parse_bvh((ROOT/'training/b4artists_ml/cache/07_01.bvh').read_text()))

    def window(self,context=True):
        w=known_window(self.motion,4,20,np.arange(17)/16,context)
        w['target_local'],w['target']=target_window(self.motion,np.arange(4,21),w['origin'],w['basis'])
        return w

    def test_target_labels_cannot_change_features(self):
        w=self.window();a=observed_features(w);self.assertEqual(a.shape,(427,))
        w['target_local'][:]=np.nan;w['target'][:]=np.nan;w['baseline'][:]=np.nan;w['basis_functions'][:]=np.nan
        np.testing.assert_array_equal(observed_features(w),a)

    def test_only_observations_required(self):
        w=self.window();np.testing.assert_array_equal(observed_features({'x':w['x']}),observed_features(w))
        changed=w['x'].copy();changed[141]+=.1
        self.assertFalse(np.array_equal(observed_features({'x':changed}),observed_features(w)))

    def test_missing_context_velocity_suppressed(self):
        w=self.window(False);a=observed_features(w);w['x'][282:564]=self.window(True)['x'][282:564]
        np.testing.assert_array_equal(observed_features(w),a)
        self.assertTrue((a[207:345]==0).all());self.assertTrue((a[348:354]==0).all())

    def test_rotation_log_identity_small_and_pi(self):
        for angle in (0.,1e-9,.3,np.pi-1e-9,np.pi):
            r=quat_matrix([np.cos(angle/2),0,np.sin(angle/2),0]);v=rotation_log(r)
            np.testing.assert_allclose(v,[0,angle,0],atol=1e-10)

    def test_distance_matches_explicit_difference(self):
        rng=np.random.default_rng(42);a=rng.normal(size=(5,7));b=rng.normal(size=(9,7))
        np.testing.assert_allclose(squared_distance(a,b),np.mean((a[:,None]-b[None])**2,axis=-1),atol=1e-14)
        np.testing.assert_allclose(np.diag(squared_distance(a,a)),0,atol=1e-14)

    def test_normalization_uses_only_supplied_training_rows(self):
        a=np.array([[0.,2.],[4.,6.]]);mean,std=fit_feature_normalization(a,np.array([.75,.25]))
        np.testing.assert_allclose(mean,[1,3]);np.testing.assert_allclose(std,np.sqrt(3))
        before=mean.copy();other=np.full((4,2),1000.);other-=mean
        np.testing.assert_array_equal(mean,before)

    def test_oracle_recovers_known_curve_but_is_not_input(self):
        w=self.window();rng=np.random.default_rng(9);coefficient=rng.normal(size=(4,141))*.01
        w['target_local']=w['baseline']+w['basis_functions']@coefficient
        np.testing.assert_allclose(oracle_coefficients(w),coefficient,atol=1e-12)
        a=observed_features(w);w['target_local']+=w['basis_functions']@coefficient
        np.testing.assert_allclose(oracle_coefficients(w),2*coefficient,atol=1e-12);np.testing.assert_array_equal(observed_features(w),a)

    def test_invalid_observed_values_and_timing_rejected(self):
        for index,value in ((0,np.nan),(-1,0),(-2,-1),(-4,.5)):
            w=self.window();w['x'][index]=value
            with self.assertRaises(ValueError):observed_features(w)

    def test_kernel_weighted_solution_matches_direct_solve(self):
        from kernel_motion import kernel,kernel_trials
        rng=np.random.default_rng(12);x=rng.normal(size=(8,5));y=rng.normal(size=(8,7));weights=np.arange(1,9,dtype=float);weights/=weights.sum()
        for reg,alpha in kernel_trials(x,weights,y,.5,[.01,.1]):
            expected=np.linalg.solve(kernel(x,x,.5)+np.diag(reg/(len(weights)*weights)),y)
            np.testing.assert_allclose(alpha,expected,atol=1e-11)

    def test_learned_query_ignores_hidden_labels_and_shrinks_outside_support(self):
        from kernel_motion import kernel_trials,infer_coefficients
        w=self.window();x=observed_features(w)[None];target=np.ones((1,564))*.01
        _,alpha=next(kernel_trials(x,np.ones(1),target,.5,[.1]))
        model=dict(kind='kernel',variant='motion_relative',mean=np.zeros(427),std=np.ones(427),width=.5,centers=x.copy(),alpha=alpha)
        a=infer_coefficients(model,[w]);self.assertGreater(np.linalg.norm(a),0)
        w['target'][:]=np.nan;w['target_local'][:]=np.nan
        np.testing.assert_array_equal(infer_coefficients(model,[w]),a)
        w['x'][141]+=1000
        self.assertLess(np.linalg.norm(infer_coefficients(model,[w])),1e-10)

    def test_model_roundtrip_and_endpoint_kinematics(self):
        import tempfile
        from kernel_motion import kernel_trials,infer_coefficients,save_model,load_model
        from sequence_kinematics import forward
        w=self.window();x=observed_features(w)[None];_,alpha=next(kernel_trials(x,np.ones(1),np.ones((1,564))*.01,.5,[.1]))
        model=dict(kind='kernel',variant='motion_relative',mean=np.zeros(427),std=np.ones(427),width=.5,centers=x,alpha=alpha)
        with tempfile.TemporaryDirectory(dir=ROOT/'training/b4artists_ml/cache') as directory:
            path=Path(directory)/'model.npz';save_model(path,model);restored=load_model(path)
            coeff=infer_coefficients(restored,[w])[0];np.testing.assert_array_equal(coeff,infer_coefficients(model,[w])[0])
            local=w['baseline']+w['basis_functions']@coeff;np.testing.assert_array_equal(local[[0,-1]],w['baseline'][[0,-1]])
            pos,rot,_=forward(local,w['offsets'],self.motion.parents)
            actual=np.linalg.norm(pos[:,1:]-pos[:,np.asarray(self.motion.parents[1:])],axis=-1)
            np.testing.assert_allclose(actual,np.broadcast_to(np.linalg.norm(w['offsets'][1:],axis=-1),actual.shape),atol=1e-12)

if __name__=='__main__':unittest.main(verbosity=2)
