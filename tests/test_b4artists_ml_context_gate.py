"""Supervised controller targets stay separate from observed-only inference."""
import sys,unittest,tempfile,copy
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'training/b4artists_ml'),str(ROOT/'tests')]
import test_b4artists_ml_sequence as fixture
from sequence_data import known_window
from context_motion import context_baseline
from context_gate import gate_inputs,gate_values,training_targets,predict_locals
from kernel_motion import kernel_trials,save_model,load_model
class GateTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):fixture.SequenceTests.setUpClass();cls.motion=fixture.SequenceTests.motion
 def window(self,context=True):
  w=known_window(self.motion,4,20,np.linspace(0,1,17),context);w['t']=np.linspace(0,1,17);return w
 def model(self,w,target=(.5,.7),variant='compact'):
  x=gate_inputs([w],variant);_,alpha=next(kernel_trials(x,np.ones(1),np.asarray([target]),.5,[.1]));return dict(kind='context_gate_v1',variant=variant,mean=np.zeros(x.shape[1]),std=np.ones(x.shape[1]),centers=x,width=.5,alpha=alpha)
 def test_targets_use_training_labels_only(self):
  w=self.window();a=w['baseline'];b=context_baseline(w['x'],w['t']);w['target_local']=a+.3*(b-a);np.testing.assert_allclose(training_targets([w],[a]),.3,atol=1e-12)
  features=gate_inputs([w],'compact');w['target_local']=a+.8*(b-a);np.testing.assert_allclose(training_targets([w],[a]),.8,atol=1e-12);np.testing.assert_array_equal(features,gate_inputs([w],'compact'))
 def test_inference_ignores_hidden_labels(self):
  w=self.window();model=self.model(w);a=gate_values(model,[w]);self.assertGreater(a.max(),0);w['target_local']=np.full_like(w['baseline'],np.nan);w['target']=np.nan
  np.testing.assert_array_equal(a,gate_values(model,[w]))
 def test_no_context_preserves_incumbent(self):
  w=self.window(False);model=self.model(w);np.testing.assert_array_equal(gate_values(model,[w]),0);np.testing.assert_array_equal(predict_locals(model,[w],[w['baseline']])[0],w['baseline'])
 def test_strengths_bounded_and_zero_outside_training_support(self):
  w=self.window();model=self.model(w,target=(-3,4));np.testing.assert_array_equal(gate_values(model,[w]),[[0,1]]);w['x'][141]+=1000;self.assertLess(gate_values(model,[w]).max(),1e-12)
 def test_saved_gate_and_exact_priorities(self):
  w=self.window();model=self.model(w)
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/'gate.npz';save_model(p,model);again=load_model(p);np.testing.assert_array_equal(gate_values(model,[w]),gate_values(again,[w]))
  got=predict_locals(model,[w],[w['baseline']])[0];np.testing.assert_allclose(got[[0,-1]],w['baseline'][[0,-1]],atol=1e-14)
 def test_raw_and_compact_features_ignore_labels(self):
  w=self.window()
  for variant in ('compact','raw_pose'):
   a=gate_inputs([w],variant);w['target']=np.nan;np.testing.assert_array_equal(a,gate_inputs([w],variant));self.assertEqual(a.shape[0],1)
if __name__=='__main__':unittest.main()
