"""Regression: training targets must match native rest-calibrated motion."""
import unittest,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'training/b4artists_ml'),str(ROOT/'tests')]
from test_b4artists_ml_semantic_motion_data import sequence
from semantic_motion_data import SemanticSequence,window,from_bvh
from sequence_packet_v2 import packet
from temporal_data import rotation_matrix,quat_matrix
from bvh_data import parse_bvh
class PacketTests(unittest.TestCase):
 def test_exact_existing_target_representation(self):
  s=sequence()
  for context in (False,True):
   p=packet(s,2,10,context=context);expected=window(s,2,10,context=context);part=p['target'][1:-1] if context else p['target'];np.testing.assert_array_equal(part.reshape(-1,153),expected['target'])
 def test_world_positions_and_rotations_roundtrip(self):
  s=sequence();p=packet(s,2,10,context=True);r,bad=rotation_matrix(p['target'][...,3:]);self.assertFalse(bad.any());o=p['observations'];np.testing.assert_allclose(o.world_rotations(r),s.rotations[p['indices']],atol=1e-12);np.testing.assert_allclose(o.world_points(p['target'][...,:3]),s.positions[p['indices']],atol=1e-12)
 def test_bone_roll_and_global_similarity_invariance(self):
  s=sequence();a=packet(s,2,10,context=True,pattern=2);q=quat_matrix(np.array([.8,.2,-.3,.1]));roll=quat_matrix(np.random.default_rng(4).normal(size=(17,4)));v=SemanticSequence(s.rest@q.T*1.7+8,q@s.rest_rotations@roll,s.positions@q.T*1.7+8,q@s.rotations@roll,s.frames,s.dt);b=packet(v,2,10,context=True,pattern=2);np.testing.assert_allclose(a['target'],b['target'],atol=1e-12);np.testing.assert_allclose(a['request']['condition'],b['request']['condition'],atol=1e-6)
 def test_hidden_targets_do_not_change_conditioning(self):
  s=sequence();a=packet(s,2,10,context=True);s.positions[3:10]+=.9;s.rotations[3:10]=quat_matrix(np.array([.7,.2,-.1,.3]))@s.rotations[3:10];b=packet(s,2,10,context=True);np.testing.assert_array_equal(a['request']['condition'],b['request']['condition']);self.assertGreater(np.linalg.norm(a['target']-b['target']),1)
 def test_real_training_clip_uses_same_encoder(self):
  s=from_bvh(parse_bvh((ROOT/'training/b4artists_ml/cache/07_01.bvh').read_text()));p=packet(s,1,33,context=True);o=p['observations'];r,bad=rotation_matrix(p['target'][...,3:]);self.assertFalse(bad.any());np.testing.assert_allclose(o.world_rotations(r),s.rotations[p['indices']],atol=1e-12);self.assertTrue(np.all(s.frames[p['indices']]>0))
if __name__=='__main__':unittest.main()
