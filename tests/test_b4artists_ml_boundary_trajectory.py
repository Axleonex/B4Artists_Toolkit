"""Neural trajectory calculus, actual learning and observation-only inference."""
from pathlib import Path
import sys,unittest,tempfile,copy
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'training/b4artists_ml'),str(ROOT/'tests')]
import numpy as np
import boundary_trajectory as model
from test_b4artists_ml_semantic_predictor import windows
SPEC=dict(baseline_kind='hermite',continuity='C1',hidden=8,epochs=20,batch_size=4,learning_rate=.003,regularization=1e-5,velocity_weight=.01,acceleration_weight=.0001)

class BoundaryTrajectoryTests(unittest.TestCase):
    def test_compressed_loss_matches_explicit_trajectories(self):
        rows=windows();x=np.random.default_rng(1).normal(size=(4,514));p=model.initialize(514,8,612,3,dtype=np.float64);weights=np.array([.1,.2,.3,.4]);terms=model.trajectory_terms(rows,SPEC)
        value,_=model.loss_and_grad(p,x,terms,weights,0.);c=model.forward(p,x).reshape(4,4,153);expected=0.
        for w,coef,weight in zip(rows,c,weights):
            error=model.reference(w['observations'],w['t'],SPEC['baseline_kind'])+model.residual_basis(w['t'],SPEC['continuity'])@(coef*model.observation_scale(w['observations'])[None,:])-w['target'];expected+=.5*weight*np.sum((model.operators(w,SPEC)@error)**2)/153
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

    def test_identical_observations_have_exact_zero_corrections(self):
        from dataclasses import replace
        rows=windows();m,_=model.fit(rows,SPEC,7);base=rows[0]['observations']
        for gap in [8,16,32]:
            for context in [False,True]:
                o=replace(base,positions=np.repeat(base.positions[:1],4,axis=0),rotations=np.repeat(base.rotations[:1],4,axis=0),duration=gap*base.dt,context=context)
                np.testing.assert_array_equal(model.observation_scale(o),np.zeros(153));t=np.linspace(0,1,gap+1)
                np.testing.assert_array_equal(model.predict_packed(m,o,t),model.reference(o,t,m['baseline_kind']))
    def test_near_stationary_corrections_converge_without_a_floor(self):
        from dataclasses import replace
        rows=windows();m,_=model.fit(rows,SPEC,7);base=rows[0]['observations'];r=np.repeat(base.rotations[:1],4,axis=0);errors=[]
        for epsilon in [1e-3,1e-6,1e-9]:
            p=np.repeat(base.positions[:1],4,axis=0);p[1,:,0]+=epsilon;o=replace(base,positions=p,rotations=r,context=False);t=np.linspace(0,1,9)
            errors.append(float(np.max(abs(model.predict_packed(m,o,t)-model.reference(o,t,m['baseline_kind'])))))
        self.assertGreater(errors[0],0.);self.assertLess(errors[-1],errors[0]*1e-5)
    def test_masked_context_and_stationary_joints_are_preserved(self):
        from dataclasses import replace
        rows=windows();m,_=model.fit(rows,SPEC,7);base=rows[0]['observations'];p=np.repeat(base.positions[:1],4,axis=0);r=np.repeat(base.rotations[:1],4,axis=0);p[1,7,0]+=.1;o=replace(base,positions=p,rotations=r,context=False);t=np.linspace(0,1,9)
        a=model.predict_packed(m,o,t);bad=replace(o,positions=p.copy(),rotations=r.copy());bad.positions[2:]+=999;bad.rotations[2:]+=9
        np.testing.assert_array_equal(a,model.predict_packed(m,bad,t));out=a.reshape(-1,17,9);line=model.reference(o,t,m['baseline_kind']).reshape(-1,17,9)
        np.testing.assert_array_equal(out[:,0],line[:,0])
    def test_context_velocity_supports_equal_endpoint_motion(self):
        from dataclasses import replace
        base=windows()[0]['observations'];p=np.repeat(base.positions[:1],4,axis=0);r=np.repeat(base.rotations[:1],4,axis=0);p[2,7,0]-=.01;p[3,7,0]+=.01
        a=replace(base,positions=p,rotations=r,context=False);b=replace(a,context=True)
        self.assertEqual(float(model.observation_scale(a).sum()),0.);self.assertGreater(float(model.observation_scale(b).sum()),0.)

    def test_c1_basis_preserves_values_and_has_zero_endpoint_derivatives(self):
        eps=1e-7
        np.testing.assert_array_equal(model.residual_basis(np.array([0.,1.]),'C1'),np.zeros((2,4)))
        derivative_start=model.residual_basis(np.array([eps]),'C1')/eps
        derivative_end=-model.residual_basis(np.array([1-eps]),'C1')/eps
        self.assertLess(float(np.max(abs(derivative_start))),2e-6);self.assertLess(float(np.max(abs(derivative_end))),2e-6)
        self.assertGreater(float(np.max(abs(model.residual_basis(np.array([eps]),'C0')/eps))),1.)
    def test_nonzero_learned_correction_preserves_reference_boundary_velocity(self):
        rows=windows();m,_=model.fit(rows,SPEC,7);o=rows[0]['observations'];errors=[]
        for eps in [1e-4,1e-6]:
            t=np.array([0.,eps,1-eps,1.]);delta=model.predict_packed(m,o,t)-model.reference(o,t,m['baseline_kind'])
            errors.append(float(np.max(abs(delta[[1,2]])))/eps/o.duration)
        self.assertGreater(errors[0],0.);self.assertLess(errors[1],errors[0]*.02)
    def test_reference_and_representation_choices_are_explicit(self):
        o=windows()[0]['observations'];t=np.linspace(0,1,9)
        self.assertGreater(np.linalg.norm(model.reference(o,t,'linear')-model.reference(o,t,'hermite')),1e-5)
        with self.assertRaises(ValueError):model.reference(o,t,'unknown')
        with self.assertRaises(ValueError):model.residual_basis(t,'C2')
