"""Training-mean and per-joint controller invariants."""
import sys,unittest,tempfile
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'training/b4artists_ml'),str(ROOT/'tests')]
import test_b4artists_ml_sequence as fixture
from sequence_data import known_window
from sequence_kinematics import forward
from context_motion import context_baseline
from context_gate_robust import gate_inputs,gate_values,training_targets,predict_locals
from kernel_motion import save_model,load_model
class RobustGateTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):fixture.SequenceTests.setUpClass();cls.motion=fixture.SequenceTests.motion
 def window(self,context=True):
  w=known_window(self.motion,4,20,np.linspace(0,1,17),context);w['t']=np.linspace(0,1,17);return w
 def model(self,w,mean):
  x=gate_inputs([w],'compact');return dict(kind='context_gate_v2',variant='compact',mean=np.zeros(x.shape[1]),std=np.ones(x.shape[1]),centers=x,width=.5,alpha=np.zeros((1,24)),target_mean=np.asarray(mean))
 def test_independent_targets_are_training_supervision(self):
  w=self.window();a=w['baseline'];b=context_baseline(w['x'],w['t']);g=np.linspace(.1,.9,24);wanted=a.copy();wanted[:,:3]+=g[0]*(b[:,:3]-a[:,:3])
  for j in range(23):
   sl=slice(3+j*6,9+j*6);wanted[:,sl]+=g[j+1]*(b[:,sl]-a[:,sl])
  w['target_local']=wanted;got=training_targets([w],[a])[0]
  for j,sl in enumerate([slice(0,3)]+[slice(3+6*k,9+6*k) for k in range(23)]):
   if np.sum((b[1:-1,sl]-a[1:-1,sl])**2)>1e-16:self.assertAlmostEqual(got[j],g[j],places=10)
 def test_prior_persists_outside_kernel_support(self):
  w=self.window();mean=np.linspace(0,1,24);model=self.model(w,mean);model['alpha'][:]=.2;w['x'][141]+=1000
  np.testing.assert_allclose(gate_values(model,[w]),mean[None],atol=1e-12)
 def test_no_context_can_denoise_without_reading_other_poses(self):
  w=self.window(False);model=self.model(w,np.ones(24));a=w['baseline'].copy();a[1:-1,0]+=.05;got=predict_locals(model,[w],[a])[0];np.testing.assert_allclose(got,w['baseline'],atol=1e-14)
  w['x'][282:564]=self.window(True)['x'][282:564];np.testing.assert_allclose(predict_locals(model,[w],[a])[0],got,atol=1e-14)
 def test_inference_ignores_labels_and_saved_model_preserves_values(self):
  w=self.window();model=self.model(w,np.full(24,.4));expected=gate_values(model,[w]);w['target_local']=np.nan;w['target']=np.nan
  np.testing.assert_array_equal(expected,gate_values(model,[w]))
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/'gate.npz';save_model(p,model);np.testing.assert_array_equal(expected,gate_values(load_model(p),[w]))
 def test_blend_preserves_priorities_and_physical_edges(self):
  w=self.window();model=self.model(w,np.linspace(0,1,24));got=predict_locals(model,[w],[w['baseline']])[0];np.testing.assert_allclose(got[[0,-1]],w['baseline'][[0,-1]],atol=1e-14)
  p,_,_=forward(got,w['offsets'],self.motion.parents);lengths=np.linalg.norm(p[:,1:]-p[:,np.asarray(self.motion.parents[1:])],axis=-1);np.testing.assert_allclose(lengths,np.broadcast_to(np.linalg.norm(w['offsets'][1:],axis=-1),lengths.shape),atol=1e-13)
 def test_strengths_remain_bounded(self):
  w=self.window();mean=np.r_[np.full(12,-3.),np.full(12,4.)];model=self.model(w,mean);np.testing.assert_array_equal(gate_values(model,[w]),np.r_[np.zeros(12),np.ones(12)][None])
if __name__=='__main__':unittest.main()
