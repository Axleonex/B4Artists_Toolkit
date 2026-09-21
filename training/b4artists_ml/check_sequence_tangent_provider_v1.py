"""Protect canonical endpoint, query and information boundaries with trained weights."""
import unittest,sys,json
from pathlib import Path
from dataclasses import replace
import numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT/'training/b4artists_ml'),str(ROOT/'tests')]
from sequence_tangent_provider_v1 import Provider,observed_request
from sequence_tangent_context_v1 import build
from sequence_packet_v2 import packet
from test_b4artists_ml_semantic_motion_data import sequence
from semantic_motion_data import window,baseline
class ProviderTests(unittest.TestCase):
 def models(self):
  report=json.loads((ROOT/'training/b4artists_ml/results/sequence-tangent-training-v1'/('direct-'+str(SEED))/'report.json').read_text())
  assert report['complete'] and report['completed_epochs']==60
  return [Provider(ROOT/report['weights'],report['weights_sha256'],kind='direct',seed=SEED)]
 def test_training_inference_requests_match(self):
  for context in (False,True):
   p=packet(sequence(),2,10,context=context);req,_=observed_request(p['observations']);expected=build(p['request']['times'],p['request']['observed'],p['mask'],p['request']['rest']);np.testing.assert_array_equal(expected['condition'],req['condition'])
 def test_endpoints_and_query_order(self):
  w=window(sequence(),2,10);t=np.array([0.,.2,.5,.8,1.])
  for m in self.models():
   a=m.predict_packed(w['observations'],t);np.testing.assert_array_equal(a[[0,-1]],w['linear'][[0,-1]])
   for i,q in enumerate(t):np.testing.assert_allclose(a[i],m.predict_packed(w['observations'],np.array([q]))[0],atol=1e-12,rtol=0)
 def test_masked_context_is_ignored(self):
  o=window(sequence(),2,10,context=False)['observations'];p=o.positions.copy();p[2:]=np.nan;r=o.rotations.copy();r[2:]=np.nan
  for m in self.models():np.testing.assert_array_equal(m.predict_packed(o,np.array([.2,.5])),m.predict_packed(replace(o,positions=p,rotations=r),np.array([.2,.5])))
 def test_stationary_hold_exact(self):
  o=window(sequence(),2,10)['observations'];o=replace(o,positions=np.repeat(o.positions[:1],4,axis=0),rotations=np.repeat(o.rotations[:1],4,axis=0));t=np.linspace(0,1,7)
  for m in self.models():np.testing.assert_array_equal(m.predict_packed(o,t),baseline(o,t))
 def test_cache_cannot_be_mutated_by_returned_output(self):
  o=window(sequence(),2,10)['observations']
  for m in self.models():
   a=m.predict_packed(o,np.array([.5]));expected=a.copy();a[:]=np.nan;np.testing.assert_array_equal(m.predict_packed(o,np.array([.5])),expected)
 def test_invalid_queries_and_wrong_weights_rejected(self):
  o=window(sequence(),2,10)['observations'];m=self.models()[0]
  for t in (np.array([np.nan]),np.array([1.2]),np.array([[.5]])):
   with self.assertRaises(ValueError):m.predict_packed(o,t)
  with self.assertRaises(ValueError):Provider(ROOT/'training/b4artists_ml/results/sequence-feasibility-v2/direct-train-only.npz','0'*64,kind='direct')
if __name__=='__main__':
 import hashlib,time
 SEED=int(sys.argv[1]);assert SEED in (20260909,20260910);out=ROOT/('training/b4artists_ml/results/sequence-tangent-provider-'+str(SEED));out.mkdir(exist_ok=False);at=time.perf_counter();result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ProviderTests));p=ROOT/('training/b4artists_ml/results/sequence-tangent-training-v1/direct-'+str(SEED)+'/report.json');trained=json.loads(p.read_text());report=dict(passed=result.wasSuccessful(),tests=result.testsRun,seed=SEED,seconds=time.perf_counter()-at,weights_sha256=trained['weights_sha256'],source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),synthetic_requests_only=True,development_evaluated=False,full_goal_complete=False);(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');raise SystemExit(0 if result.wasSuccessful() else 1)
