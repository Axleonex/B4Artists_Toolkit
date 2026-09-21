"""Independent numerical and grouping checks before fitting v28."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','4')
from pathlib import Path
import sys,unittest
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'training/b4artists_ml'))
import tail_risk_selector_v28 as m
from context_network import initialize

class TailRiskTests(unittest.TestCase):
    def setUp(self):
        self.rng=np.random.default_rng(9841);self.params=initialize(596,3,12,881,dtype=np.float64);self.x=self.rng.normal(size=(5,596))*.1;self.p=self.rng.uniform(.7,1.6,(5,12));self.r=self.rng.uniform(.8,1.3,(5,12));self.g=np.array([0,0,1,2,2])
    def loss(self,params=None,**kw):return m.loss_and_grad(params or self.params,kw.get('x',self.x),kw.get('p',self.p),kw.get('r',self.r),kw.get('g',self.g))
    def test_gradients_match_central_difference(self):
        _,grad,_=self.loss()
        for key,indices in [('w0',[(0,0),(14,1),(595,2)]),('b0',[(0,),(2,)]),('w1',[(0,0),(1,7),(2,11)]),('b1',[(0,),(7,),(11,)])]:
            for ix in indices:
                old=self.params[key][ix];eps=1e-6;self.params[key][ix]=old+eps;plus=self.loss()[0];self.params[key][ix]=old-eps;minus=self.loss()[0];self.params[key][ix]=old
                self.assertAlmostEqual(float(grad[key][ix]),(plus-minus)/(2*eps),delta=2e-7)
    def test_equal_cohort_mass_unchanged_by_within_group_duplication(self):
        a=self.loss();ids=np.array([0,1,0,1,2,3,4]);b=self.loss(x=self.x[ids],p=self.p[ids],r=self.r[ids],g=self.g[ids]);self.assertAlmostEqual(a[0],b[0],places=12)
        for k in a[1]:np.testing.assert_allclose(a[1][k],b[1][k],rtol=1e-12,atol=1e-12)
    def test_row_permutation_preserves_objective_and_gradient(self):
        ids=np.array([4,2,0,3,1]);a=self.loss();b=self.loss(x=self.x[ids],p=self.p[ids],r=self.r[ids],g=self.g[ids]);self.assertAlmostEqual(a[0],b[0],places=12)
        for k in a[1]:np.testing.assert_allclose(a[1][k],b[1][k],rtol=1e-12,atol=1e-12)
    def test_tail_penalty_increases_cost_of_failed_groups(self):
        a=m.loss_and_grad(self.params,self.x,self.p,self.r,self.g,penalty=0)[0];self.assertGreater(self.loss()[0],a)
        low=np.full((5,12),.5);a=m.loss_and_grad(self.params,self.x,low,low,self.g,penalty=0)[0];b=self.loss(p=low,r=low)[0];self.assertEqual(a,b)
    def test_normalization_separate_metrics_best_complete_control(self):
        identities=[dict(clip='a',gap=8,context=False),dict(clip='a',gap=8,context=False),dict(clip='b',gap=8,context=True)];p=np.full((3,12),10.);r=np.full((3,12),4.);p[:2,0]=[1.,3.];p[:2,4]=3.;r[:2,0]=2.;r[:2,7]=1.;pn,rn,g,records=m.normalize_costs(identities,p,r)
        np.testing.assert_array_equal(g,[0,0,1]);self.assertEqual(records[0]['position_denominator'],2.);self.assertEqual(records[0]['rotation_denominator'],1.);np.testing.assert_array_equal(pn[0],p[0]/2.);np.testing.assert_array_equal(rn[0],r[0])
    def test_invalid_training_inputs_fail(self):
        for kw in [dict(p=np.full((5,12),np.nan)),dict(r=-self.r),dict(g=np.array([0,0,2,2,2])),dict(g=np.full(5,99)),dict(g=self.g.astype(float)),dict(x=self.x[:,:4])]:
            with self.assertRaises(ValueError):self.loss(**kw)
    def test_inference_is_exact_unmodified_soft_readout(self):
        import soft_selector_v27 as old
        self.assertIs(m.predict_packed,old.predict_packed);self.assertIs(m.provider,old.provider);self.assertIs(m.probabilities,old.probabilities)
if __name__=='__main__':unittest.main(verbosity=2)
