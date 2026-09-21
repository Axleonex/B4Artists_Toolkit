"""Neural trajectory calculus, actual learning and observation-only inference."""
from pathlib import Path
import sys,unittest,tempfile,copy
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'training/b4artists_ml'),str(ROOT/'tests')]
import numpy as np
import neural_trajectory as model
from test_b4artists_ml_semantic_predictor import windows
SPEC=dict(hidden=8,epochs=20,batch_size=4,learning_rate=.003,regularization=1e-5,velocity_weight=.01,acceleration_weight=.0001)

class NeuralTrajectoryTests(unittest.TestCase):
    def test_compressed_loss_matches_explicit_trajectories(self):
        rows=windows();x=np.random.default_rng(1).normal(size=(4,514));p=model.initialize(514,8,612,3,dtype=np.float64);weights=np.array([.1,.2,.3,.4]);terms=model.trajectory_terms(rows,SPEC)
        value,_=model.loss_and_grad(p,x,terms,weights,0.);c=model.forward(p,x).reshape(4,4,153);expected=0.
        for w,coef,weight in zip(rows,c,weights):
            error=w['linear']+model.coefficients_basis(w['t'],w['observations'].duration)@coef-w['target'];expected+=.5*weight*np.sum((model.operators(w,SPEC)@error)**2)/153
        self.assertAlmostEqual(value,expected,places=12)
    def test_network_gradient_matches_finite_differences_all_parameters(self):
        rows=windows();x=np.random.default_rng(1).normal(size=(4,514));p=model.initialize(514,8,612,3,dtype=np.float64);terms=model.trajectory_terms(rows,SPEC);weights=np.ones(4);reg=.001
        _,grad=model.loss_and_grad(p,x,terms,weights,reg);rng=np.random.default_rng(8);eps=1e-5
        for name in p:
            direction=rng.normal(0,.01,p[name].shape);before=p[name].copy();p[name]=before+eps*direction;a=model.loss_and_grad(p,x,terms,weights,reg)[0];p[name]=before-eps*direction;b=model.loss_and_grad(p,x,terms,weights,reg)[0];p[name]=before
            self.assertAlmostEqual((a-b)/(2*eps),float(np.sum(grad[name]*direction)),places=8)
    def test_training_learns_hidden_features_and_lowers_objective(self):
        m,d=model.fit(windows(),dict(SPEC,regularization=0.),7);self.assertLess(d['training_objective'],d['initial_objective']);self.assertGreater(d['hidden_feature_change'],1e-4)
    def test_priorities_labels_and_serialization(self):
        rows=windows();m,_=model.fit(rows,SPEC,7);w=rows[0];a=model.predict_packed(m,w['observations'],w['t']);np.testing.assert_array_equal(a[[0,-1]],w['linear'][[0,-1]])
        w['target'][:]=np.nan;np.testing.assert_array_equal(a,model.predict_packed(m,w['observations'],w['t']))
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/'model.npz';model.save(p,m);loaded=model.load(p);np.testing.assert_array_equal(a,model.predict_packed(loaded,w['observations'],w['t']))
            m['std'][0]=0;model.save(p,m)
            with self.assertRaises(ValueError):model.load(p)
    def test_deterministic_fit_and_invalid_training_inputs(self):
        rows=windows();a,da=model.fit(rows,SPEC,7);b,db=model.fit(rows,SPEC,7)
        for k in a:np.testing.assert_array_equal(a[k],b[k])
        self.assertEqual(da,db)
        with self.assertRaises(ValueError):model.fit(rows,dict(SPEC,hidden=0),7)
        rows[0]['target'][0,0]=np.nan
        with self.assertRaises(ValueError):model.fit(rows,SPEC,7)
