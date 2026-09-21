"""Independent design-matrix and immutability checks for convex readout fitting."""
from pathlib import Path
import sys,unittest,copy,tempfile
sys.path[:0]=[str(Path(__file__).resolve().parents[1]/'training/b4artists_ml'),str(Path(__file__).resolve().parent)]
import numpy as np
import boundary_trajectory as base
from readout_trajectory import fit_readout
from test_b4artists_ml_semantic_predictor import windows
from sequence_model import statistics
SPEC=dict(baseline_kind='hermite',continuity='C0',hidden=4,epochs=2,batch_size=4,learning_rate=.001,regularization=.001,velocity_weight=.01,acceleration_weight=.0001)
class ReadoutTests(unittest.TestCase):
    def test_matches_independent_explicit_augmented_least_squares(self):
        rows=windows();parent,_=base.fit(rows,SPEC,7);m,d=fit_readout(rows,parent,SPEC,.001)
        _,weights,_,_=statistics(rows);channel=0;design=[];target=[]
        for w,weight in zip(rows,weights):
            x=base.features(w['x'],'motion');z=np.clip((x-parent['mean'])/parent['std'],-8,8);h=np.r_[np.tanh(z@parent['w0']+parent['b0']),1.]
            b=base.operators(w,SPEC)@base.residual_basis(w['t'],'C0');s=base.observation_scale(w['observations'])[channel]
            design.append(np.einsum('h,tk->thk',h,b).reshape(len(b),-1)*s*np.sqrt(weight/153))
            target.append((base.operators(w,SPEC)@(w['target']-w['hermite']))[:,channel]*np.sqrt(weight/153))
        penalty=np.eye(20)*np.sqrt(.001);penalty[-4:]=0.
        expected=np.linalg.lstsq(np.vstack(design+[penalty]),np.r_[np.concatenate(target),np.zeros(20)],rcond=None)[0]
        actual=np.concatenate((m['w1'].reshape(4,4,153)[:,:,channel].ravel(),m['b1'].reshape(4,153)[:,channel]))
        np.testing.assert_allclose(actual,expected,atol=1e-8,rtol=1e-7)
        self.assertLess(d['readout_gradient_max'],1e-9);self.assertLessEqual(d['after_objective'],d['before_objective'])
    def test_parent_immutable_deterministic_and_priorities_preserved(self):
        rows=windows();p,_=base.fit(rows,SPEC,7);original=copy.deepcopy(p);a,da=fit_readout(rows,p,SPEC,.001);b,db=fit_readout(rows,p,SPEC,.001)
        for k in p:np.testing.assert_array_equal(p[k],original[k]);np.testing.assert_array_equal(a[k],b[k])
        self.assertEqual(da,db);w=rows[0];pred=base.predict_packed(a,w['observations'],w['t']);np.testing.assert_array_equal(pred[[0,-1]],w['linear'][[0,-1]])
        w['target'][:]=np.nan;np.testing.assert_array_equal(pred,base.predict_packed(a,w['observations'],w['t']))
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'m.npz';base.save(path,a);np.testing.assert_array_equal(pred,base.predict_packed(base.load(path),w['observations'],w['t']))
    def test_zero_motion_channels_and_invalid_regularization(self):
        from dataclasses import replace
        rows=windows();p,_=base.fit(rows,SPEC,7)
        for w in rows:
            o=w['observations'];o=replace(o,positions=np.repeat(o.positions[:1],4,axis=0),rotations=np.repeat(o.rotations[:1],4,axis=0));w['observations']=o;w['x']=o.features();w['target']=base.reference(o,w['t'],'hermite')
        m,d=fit_readout(rows,p,SPEC,.001)
        for w in rows:np.testing.assert_array_equal(base.predict_packed(m,w['observations'],w['t']),w['target'])
        for reg in [0,-1,float('nan')]:
            with self.assertRaises(ValueError):fit_readout(rows,p,SPEC,reg)
if __name__=='__main__':unittest.main()
