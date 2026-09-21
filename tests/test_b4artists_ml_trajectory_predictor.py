"""Trajectory objective equivalence, temporal weighting and inference isolation."""
from pathlib import Path
import sys,unittest,copy,tempfile
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'training/b4artists_ml'),str(ROOT/'tests')]
import numpy as np
import trajectory_predictor as model
from sequence_data import coefficients_basis
from test_b4artists_ml_semantic_predictor import windows
SPEC=dict(kind='rbf',variant='motion',centers=128,width=1.5,regularization=.001,velocity_weight=.01,acceleration_weight=.0001)

class TrajectoryPredictorTests(unittest.TestCase):
    def test_grouped_system_matches_independent_dense_least_squares(self):
        rows=windows()[:3];phi=np.array([[1,.1],[1,.3],[1,-.2]]);weights=np.array([.2,.3,.5]);h,r=model.normal_system(phi,rows,weights,SPEC)
        a=[];target=[]
        for x,w,weight in zip(phi,rows,weights):
            op=model.operators(w,SPEC);b=op@coefficients_basis(w['t'],w['observations'].duration)
            a.append(np.concatenate([v*b for v in x],axis=1)*np.sqrt(weight))
            target.append(op@(w['target']-w['linear'])*np.sqrt(weight))
        a=np.concatenate(a);target=np.concatenate(target)
        np.testing.assert_allclose(h,a.T@a+SPEC['regularization']*np.eye(8),rtol=1e-10,atol=1e-12)
        np.testing.assert_allclose(r,a.T@target,rtol=1e-10,atol=1e-12)
        direct=np.linalg.lstsq(np.r_[a,np.eye(8)*np.sqrt(SPEC['regularization'])],np.r_[target,np.zeros((8,153))],rcond=None)[0]
        np.testing.assert_allclose(np.linalg.solve(h,r),direct,rtol=1e-8,atol=1e-10)
    def test_objective_gradient_and_stationary_solution(self):
        rows=windows()[:2];phi=np.array([[1,.2],[1,-.3]]);weights=np.array([.4,.6]);h,r=model.normal_system(phi,rows,weights,SPEC)
        c=np.random.default_rng(4).normal(0,.03,(8,153));direction=np.random.default_rng(5).normal(0,.03,c.shape);eps=1e-5
        actual=(model.objective(c+eps*direction,phi,rows,weights,SPEC)-model.objective(c-eps*direction,phi,rows,weights,SPEC))/(2*eps)
        self.assertAlmostEqual(actual,float(np.sum(2*(h@c-r)*direction)),places=7)
        solved=np.linalg.solve(h,r);self.assertLess(model.objective(solved,phi,rows,weights,SPEC),model.objective(np.zeros_like(c),phi,rows,weights,SPEC))
    def test_derivative_terms_detect_motion_error_and_invalid_timing(self):
        w=windows()[0];plain=dict(SPEC,velocity_weight=0,acceleration_weight=0)
        op=model.operators(w,SPEC);a=model.operators(w,plain);constant=np.ones(len(w['t']));alternating=(-1.)**np.arange(len(constant))
        self.assertAlmostEqual(float(np.sum((op@constant)**2)),float(np.sum((a@constant)**2)))
        self.assertGreater(np.sum((op@alternating)**2),np.sum((a@alternating)**2)*2)
        bad=copy.deepcopy(w);bad['dt']*=2
        with self.assertRaises(ValueError):model.operators(bad,SPEC)
        with self.assertRaises(ValueError):model.operators(w,dict(SPEC,velocity_weight=-1))
    def test_fit_prediction_priorities_hidden_label_isolation_and_serialization(self):
        rows=windows();m,d=model.fit(rows,SPEC,7);self.assertLess(d['training_objective'],d['zero_objective']);self.assertLess(d['normal_residual'],1e-8)
        w=rows[0];a=model.predict_packed(m,w['observations'],w['t']);np.testing.assert_array_equal(a[[0,-1]],w['linear'][[0,-1]])
        self.assertGreater(np.linalg.norm(a-w['linear']),1e-5);w['target'][:]=np.nan
        np.testing.assert_array_equal(a,model.predict_packed(m,w['observations'],w['t']))
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/'model.npz';model.save(p,m);loaded=model.load(p);np.testing.assert_array_equal(a,model.predict_packed(loaded,w['observations'],w['t']))
    def test_fit_is_exactly_reproducible_and_rejects_invalid_labels(self):
        rows=windows();a,da=model.fit(rows,SPEC,7);b,db=model.fit(rows,SPEC,7)
        for key in a:np.testing.assert_array_equal(a[key],b[key])
        self.assertEqual(da,db);rows[0]['target'][:]=np.nan
        with self.assertRaises(ValueError):model.fit(rows,SPEC,7)
