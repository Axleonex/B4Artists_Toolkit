"""Prior changes are observable-only and zero prior preserves frozen V9."""
from pathlib import Path
import sys,unittest,tempfile
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'training/b4artists_ml'),str(ROOT/'tests')]
import test_b4artists_ml_crossfit_controller as fixture
from context_prior_controller import strengths,predict,prior_values
from crossfit_controller import strengths as old_strengths,predict as old_predict
from context_motion import context_baseline
from kernel_motion import save_model,load_model
class PriorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):fixture.CrossfitTests.setUpClass();cls.helper=fixture.CrossfitTests()
    def test_zero_prior_preserves_v9_exactly(self):
        w=self.helper.window();m=self.helper.model(w);m['context_prior']=np.zeros(2)
        np.testing.assert_array_equal(strengths(m,[w]),old_strengths(m,[w]))
        np.testing.assert_array_equal(predict(m,[w],[w['baseline']])[0],old_predict(m,[w],[w['baseline']])[0])
    def test_outside_support_uses_known_context(self):
        w=self.helper.window();m=self.helper.model(w);m['context_prior']=np.ones(2);m['centers']=m['centers']+1000
        np.testing.assert_allclose(strengths(m,[w]),[[[0,1],[0,1]]],atol=1e-12)
        np.testing.assert_allclose(predict(m,[w],[w['baseline']])[0],context_baseline(w['x'],w['t']),atol=1e-13)
    def test_absent_context_has_no_context_prior(self):
        w=self.helper.window(False);m=self.helper.model(w);m['context_prior']=np.ones(2);m['centers']=m['centers']+1000
        np.testing.assert_allclose(strengths(m,[w]),0.,atol=1e-12)
        np.testing.assert_allclose(predict(m,[w],[w['baseline']])[0],w['baseline'],atol=1e-13)
    def test_hidden_labels_do_not_affect_prior_or_prediction(self):
        w=self.helper.window();m=self.helper.model(w);m['context_prior']=np.array([1.,0.]);expected=predict(m,[w],[w['baseline']])[0]
        w['target']=np.nan;w['target_local']=np.nan
        np.testing.assert_array_equal(expected,predict(m,[w],[w['baseline']])[0])
    def test_invalid_prior_and_masks_rejected(self):
        w=self.helper.window()
        for p in ([np.nan,0],[-1,0],[0,2],[0]):
            with self.assertRaises(ValueError):prior_values([w],p)
        w['x'][-4]=.5
        with self.assertRaises(ValueError):prior_values([w],[1,1])
    def test_saved_model_and_priority_preservation(self):
        w=self.helper.window();m=self.helper.model(w);m['context_prior']=np.array([1.,1.]);m['kind']='context_prior_v1'
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'gate.npz';save_model(p,m);again=load_model(p)
        np.testing.assert_array_equal(strengths(m,[w]),strengths(again,[w]))
        prediction=predict(again,[w],[w['baseline']])[0]
        np.testing.assert_allclose(prediction[[0,-1]],w['baseline'][[0,-1]],atol=1e-13)
if __name__=='__main__':unittest.main()
