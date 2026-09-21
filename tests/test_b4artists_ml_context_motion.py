"""Observed-context temporal reconstruction without hidden-label leakage."""
import sys,unittest,copy,tempfile
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'training/b4artists_ml'),str(ROOT/'tests')]
from test_b4artists_ml_sequence import SequenceTests
from context_motion import context_baseline,contextual_windows
from sequence_data import known_window
from sequence_kinematics import forward
from temporal_data import rotation_matrix
class ContextMotionTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):SequenceTests.setUpClass();cls.motion=SequenceTests.motion
 def window(self,context=True):return known_window(self.motion,4,20,np.linspace(0,1,17),context)
 def test_observed_priorities_and_no_context_baseline(self):
  for context in (False,True):
   w=self.window(context);out=context_baseline(w['x'],np.linspace(0,1,17));pose=w['x'][:564].reshape(4,141)
   np.testing.assert_array_equal(out[[0,-1]],pose[:2])
   if not context:np.testing.assert_allclose(out,w['baseline'],atol=1e-14)
 def test_hidden_source_motion_is_not_read(self):
  w=self.window();a=context_baseline(w['x'],[.13,.77]);motion=copy.deepcopy(self.motion);motion.local_rotation[5:20]=np.nan;motion.semantic_motion.points[5:20]=np.nan
  b=known_window(motion,4,20,[.13,.77],True);np.testing.assert_array_equal(a,context_baseline(b['x'],[.13,.77]))
 def test_context_changes_interior_without_moving_priorities(self):
  w=self.window();x=w['x'].copy();x[282:285]+=[.1,0,0];a=context_baseline(w['x'],[0,.5,1]);b=context_baseline(x,[0,.5,1]);np.testing.assert_array_equal(a[[0,-1]],b[[0,-1]]);self.assertGreater(np.linalg.norm(a[1]-b[1]),.01)
 def test_missing_context_slots_are_suppressed(self):
  w=self.window(False);x=w['x'].copy();x[282:564]=self.window(True)['x'][282:564];np.testing.assert_array_equal(context_baseline(x,[.3]),context_baseline(w['x'],[.3]))
 def test_time_unit_scaling_and_query_batch_independence(self):
  w=self.window();x=w['x'].copy();x[-2:]*=1000;t=[0,.2,.67,1];a=context_baseline(w['x'],t);np.testing.assert_allclose(a,context_baseline(x,t),atol=1e-13)
  for i,u in enumerate(t):np.testing.assert_array_equal(a[i],context_baseline(w['x'],[u])[0])
 def test_root_endpoint_velocities_use_context(self):
  w=self.window();pose=w['x'][:564].reshape(4,141);duration,dt=w['x'][-2:];eps=1e-7
  out=context_baseline(w['x'],[0,eps,1-eps,1]);np.testing.assert_allclose((out[1,:3]-out[0,:3])/(eps*duration),(pose[0,:3]-pose[2,:3])/dt,atol=2e-5)
  np.testing.assert_allclose((out[-1,:3]-out[-2,:3])/(eps*duration),(pose[3,:3]-pose[1,:3])/dt,atol=2e-5)
 def test_articulated_edges_and_proper_rotations(self):
  w=self.window();local=context_baseline(w['x'],np.linspace(0,1,65));p,r,_=forward(local,w['offsets'],self.motion.parents)
  lengths=np.linalg.norm(p[:,1:]-p[:,np.asarray(self.motion.parents[1:])],axis=-1);np.testing.assert_allclose(lengths,np.broadcast_to(np.linalg.norm(w['offsets'][1:],axis=-1),lengths.shape),atol=1e-13);np.testing.assert_allclose(np.linalg.det(r),1,atol=1e-13)
 def test_invalid_observations_and_queries_rejected(self):
  w=self.window()
  for index,value in ((0,np.nan),(-1,0),(-2,-1),(-4,.5)):
   x=w['x'].copy();x[index]=value
   with self.assertRaises(ValueError):context_baseline(x,[.5])
  for t in ([],[-.1],[1.1],[np.nan]):
   with self.assertRaises(ValueError):context_baseline(w['x'],t)
if __name__=='__main__':unittest.main()
