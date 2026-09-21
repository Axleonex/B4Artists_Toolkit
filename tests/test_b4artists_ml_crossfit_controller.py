"""Group exclusion, constrained training targets and observation-only prediction."""
from pathlib import Path
import sys,unittest,copy,tempfile
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'training/b4artists_ml'),str(ROOT/'tests')]
from crossfit_controller import grouped_folds,simplex,fit_blend,training_targets,strengths,predict
from context_gate import gate_inputs
from kernel_motion import save_model,load_model
from sequence_data import known_window
import test_b4artists_ml_sequence as fixture

class CrossfitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): fixture.SequenceTests.setUpClass();cls.motion=fixture.SequenceTests.motion
    def window(self,context=True):
        w=known_window(self.motion,4,20,np.linspace(0,1,17),context);w['t']=np.linspace(0,1,17)
        return w
    def model(self,w,alpha=(.3,.2,.4,.1)):
        x=gate_inputs([w],'compact')
        return dict(kind='simplex_controller_v1',variant='compact',mean=np.zeros(x.shape[1]),std=np.ones(x.shape[1]),centers=x,width=1.,alpha=np.array([alpha]))
    def test_complete_groups_never_cross_a_fold(self):
        windows=[dict(clip=f'{g:02}_{c:02}') for g in range(8) for c in range(3)]*2
        seen=[]
        for train,held in grouped_folds(windows):
            a={windows[i]['clip'].split('_')[0] for i in train}
            b={windows[i]['clip'].split('_')[0] for i in held}
            self.assertFalse(a&b);self.assertEqual(len(train)+len(held),len(windows));seen.extend(held)
        self.assertEqual(sorted(seen),list(range(len(windows))))
        with self.assertRaises(ValueError): grouped_folds([dict(clip='01_01')])
    def test_simplex_projection_and_finite_gate(self):
        values=np.array([[.2,.3],[-1,.2],[3,1],[2,2],[-2,-3]])
        np.testing.assert_allclose(simplex(values),[[.2,.3],[0,.2],[1,0],[.5,.5],[0,0]])
        with self.assertRaises(ValueError):simplex([np.nan,0])
    def test_exact_interior_and_vertex_fit(self):
        a=np.array([1.,0.,0.]);b=np.array([0.,1.,0.])
        for c in ([.2,.3],[1.,0.],[0.,1.],[0.,0.]):
            np.testing.assert_allclose(fit_blend(a,b,a*c[0]+b*c[1]),c,atol=1e-14)
        np.testing.assert_allclose(fit_blend(a,b,np.array([2.,2.,0.])),[.5,.5])
    def test_inference_does_not_read_hidden_labels(self):
        w=self.window();model=self.model(w);a=predict(model,[w],[w['baseline']])[0]
        w['target_local']=np.nan;w['target']=np.nan
        np.testing.assert_array_equal(a,predict(model,[w],[w['baseline']])[0])
    def test_no_context_still_controls_learned_base(self):
        w=self.window(False);m=self.model(w);g=strengths(m,[w])
        self.assertTrue(np.all(g[:,:,0]>0));np.testing.assert_array_equal(g[:,:,1],0)
        base=w['baseline'].copy();base[1:-1,:3]+=.3
        result=predict(m,[w],[base])[0]
        self.assertGreater(float(abs(result-w['baseline']).max()),0.)
        self.assertLess(float(abs(result-w['baseline']).max()),.3)
    def test_priorities_and_outside_support_fallback(self):
        w=self.window();m=self.model(w);base=w['baseline'].copy();base[1:-1,:3]+=.1
        result=predict(m,[w],[base])[0]
        np.testing.assert_allclose(result[[0,-1]],w['baseline'][[0,-1]],atol=1e-14)
        w['x'][141]+=1000
        np.testing.assert_allclose(strengths(m,[w]),0.,atol=1e-12)
    def test_model_roundtrip(self):
        w=self.window();m=self.model(w)
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'model.npz';save_model(path,m);loaded=load_model(path)
        np.testing.assert_array_equal(strengths(m,[w]),strengths(loaded,[w]))
    def test_training_target_cannot_affect_features(self):
        w=self.window();base=w['baseline'].copy();base[1:-1,:3]+=.1
        before=gate_inputs([w],'compact');w['target_local']=w['baseline']+.4*(base-w['baseline'])
        targets=training_targets([w],[base]);self.assertAlmostEqual(targets[0,0],.4)
        np.testing.assert_array_equal(before,gate_inputs([w],'compact'))
if __name__=='__main__':unittest.main()
