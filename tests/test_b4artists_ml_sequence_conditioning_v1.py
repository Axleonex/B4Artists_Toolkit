"""Information and authored-control boundaries for sequence requests."""
import unittest,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'training/b4artists_ml'))
from sequence_conditioning_v1 import request,restore_observations
class RequestTests(unittest.TestCase):
 def fixture(self):
  t=np.linspace(0,1,17);y=np.zeros((17,17,9));y[...,3]=1;y[...,7]=1;y[...,0]=t[:,None];m=np.zeros((17,17,2),bool);m[[0,-1]]=True;m[8,7,0]=True;m[8,13,1]=True;r=np.zeros((17,3));return t,y,m,r
 def test_hidden_values_cannot_enter_features(self):
  t,y,m,r=self.fixture();a=request(t,y,m,r);altered=y.copy();altered[~a['mask']]=np.nan;b=request(t,altered,m,r);self.assertTrue(np.array_equal(a['condition'],b['condition']))
 def test_input_mutation_cannot_change_request(self):
  t,y,m,r=self.fixture();a=request(t,y,m,r);before=a['condition'].copy();y[:]=7;t[:]=2;r[:]=8;m[:]=False;self.assertTrue(np.array_equal(a['condition'],before));self.assertTrue(all(not v.flags.writeable for v in a.values()))
 def test_partial_controls_are_preserved_exactly(self):
  t,y,m,r=self.fixture();y[8,7,0]=1/3;a=request(t,y,m,r);p=restore_observations(np.full(y.shape,73.),a);self.assertTrue(np.array_equal(p[a['mask']],y[a['mask']]));self.assertTrue(np.all(p[~a['mask']]==73.))
 def test_bad_time_and_missing_context_rejected(self):
  t,y,m,r=self.fixture();t[4]=t[3]
  with self.assertRaises(ValueError):request(t,y,m,r)
  t,y,m,r=self.fixture();m[0,0,0]=False
  with self.assertRaises(ValueError):request(t,y,m,r)
 def test_nonfinite_known_and_invalid_rotation_rejected(self):
  t,y,m,r=self.fixture();y[0,0,0]=np.nan
  with self.assertRaises(ValueError):request(t,y,m,r)
  t,y,m,r=self.fixture();y[0,0,3:]=0
  with self.assertRaises(ValueError):request(t,y,m,r)
 def test_position_only_pin_does_not_expose_rotation(self):
  t,y,m,r=self.fixture();y[8,7,3:]=np.nan;a=request(t,y,m,r);self.assertTrue(np.isfinite(a['condition']).all());self.assertTrue(np.all(a['observed'][8,7,3:]==0))
 def test_unobserved_future_orientations_cannot_enter_baseline(self):
  t,y,m,r=self.fixture();a=request(t,y,m,r);y[4,:,3:]=92;b=request(t,y,m,r);self.assertTrue(np.array_equal(a['baseline'],b['baseline']))
if __name__=='__main__':unittest.main()
