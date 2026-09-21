"""Matched temporal learning, known observations, model serialization and endpoints."""
from pathlib import Path
import sys,unittest,copy,tempfile
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'training/b4artists_ml'),str(ROOT/'tests')]
import numpy as np
import semantic_predictor as model
from test_b4artists_ml_semantic_motion_data import sequence
from semantic_motion_data import window


def windows():
    out=[]
    for i in range(1,5):
        w=window(sequence(),i,i+8,context=True);w['clip']='synthetic';out.append(w)
    return out


class SemanticPredictorTests(unittest.TestCase):
    def test_features_have_expected_shape_and_ignore_masked_context(self):
        w=windows()[0];x=w['x'].copy();x[-4:-2]=0
        for variant,size in [('raw',667),('motion',514)]:
            a=model.features(x,variant);b=x.copy();b[306:612]+=123
            np.testing.assert_array_equal(a,model.features(b,variant));self.assertEqual(a.shape,(size,))
    def test_training_changes_predictions_and_keeps_priorities(self):
        rows=windows();m=model.fit(rows,dict(kind='ridge',variant='motion',regularization=.01),7)
        out=model.predict_packed(m,rows[0]['observations'],rows[0]['t'])
        self.assertGreater(np.linalg.norm(out-rows[0]['linear']),1e-5)
        np.testing.assert_array_equal(out[[0,-1]],rows[0]['linear'][[0,-1]])
        self.assertLess(np.linalg.norm(out-rows[0]['target']),np.linalg.norm(rows[0]['linear']-rows[0]['target']))
    def test_prediction_never_reads_hidden_labels(self):
        rows=windows();m=model.fit(rows,dict(kind='ridge',variant='raw',regularization=.1),7)
        w=rows[0];a=model.predict_packed(m,w['observations'],w['t']);w['target'][:]=np.nan
        np.testing.assert_array_equal(a,model.predict_packed(m,w['observations'],w['t']))
    def test_rbf_fit_and_saved_model_reproduce_exactly(self):
        rows=windows();spec=dict(kind='rbf',variant='motion',regularization=.001,width=.75,centers=128)
        a=model.fit(rows,spec,7);b=model.fit(rows,spec,7)
        for key in a:np.testing.assert_array_equal(a[key],b[key])
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'model.npz';model.save(path,a);loaded=model.load(path)
            w=rows[0];np.testing.assert_array_equal(model.predict_packed(a,w['observations'],w['t']),model.predict_packed(loaded,w['observations'],w['t']))
    def test_invalid_feature_shape_timing_and_model_rejected(self):
        x=windows()[0]['x'].copy()
        for value in (x[:-1],np.full_like(x,np.nan),np.r_[x[:-1],0.]):
            with self.assertRaises(ValueError):model.features(value,'motion')
