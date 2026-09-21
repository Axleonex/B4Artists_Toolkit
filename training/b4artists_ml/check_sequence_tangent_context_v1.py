"""Analytic contracts for research-only sparse tangent conditioning."""
from pathlib import Path
import json,hashlib,time,unittest
import numpy as np
from sequence_tangent_context_v1 import build,rotation_vector
from temporal_data import rotation6,rotation_matrix
TR=Path(__file__).resolve().parent

def rz(a):
 a=np.asarray(a);out=np.zeros((*a.shape,3,3));out[...,0,0]=out[...,1,1]=np.cos(a);out[...,0,1]=-np.sin(a);out[...,1,0]=np.sin(a);out[...,2,2]=1;return out

def fixture(t=None):
 t=np.arange(5,dtype=float) if t is None else np.asarray(t,float)
 y=np.zeros((len(t),17,9));y[:,:,0]=t[:,None]**2;y[:,:,3:]=rotation6(rz(.1*t*t))[:,None]
 m=np.zeros((len(t),17,2),bool);m[[0,1,-2,-1]]=True
 return t,y,m,np.zeros((17,3))

def extra(args):return build(*args)['tangent_context'].reshape(-1,17,16)
class Contracts(unittest.TestCase):
 def test_analytic_position_and_angular_context(self):
  e=extra(fixture())[2];np.testing.assert_allclose(e[:,0],-6);np.testing.assert_allclose(e[:,3],6);np.testing.assert_allclose(e[:,10],-.6,atol=1e-7);np.testing.assert_allclose(e[:,13],.6,atol=1e-7);np.testing.assert_array_equal(e[:,[6,7,14,15]],1)
 def test_nonuniform_observation_times(self):
  e=extra(fixture([0,.5,2,3,5]))[2];np.testing.assert_allclose(e[:,0],-7.5);np.testing.assert_allclose(e[:,3],11.25);np.testing.assert_allclose(e[:,10],-.75,atol=1e-7);np.testing.assert_allclose(e[:,13],1.125,atol=1e-7)
 def test_constant_velocity_is_zero_deviation(self):
  t,y,m,r=fixture();y[:,:,:3]=t[:,None,None]*np.array([1,2,3]);y[:,:,3:]=rotation6(rz(.2*t))[:,None];e=extra((t,y,m,r));np.testing.assert_allclose(e[:,:,[0,1,2,3,4,5,8,9,10,11,12,13]],0,atol=1e-6)
 def test_boundary_only_has_no_exterior_context(self):
  t,y,m,r=fixture();m[:]=False;m[[0,-1]]=True;np.testing.assert_array_equal(extra((t,y,m,r)),0)
 def test_partial_joint_masks_independent(self):
  args=list(fixture());args[2][1,0,0]=False;e=extra(args);np.testing.assert_array_equal(e[2,0,:3],0);np.testing.assert_allclose(e[2,0,3],12);self.assertEqual(e[2,0,6],0);self.assertEqual(e[2,0,7],1);np.testing.assert_allclose(e[2,0,8:],extra(fixture())[2,0,8:]);np.testing.assert_array_equal(e[:,1:],extra(fixture())[:,1:])
 def test_hidden_payload_never_used(self):
  t,y,m,r=fixture();expected=build(t,y,m,r);mask=np.concatenate((np.repeat(m[:,:,:1],3,axis=-1),np.repeat(m[:,:,1:],6,axis=-1)),axis=-1);y[~mask]=np.nan;actual=build(t,y,m,r);np.testing.assert_array_equal(actual['condition'],expected['condition']);y[~mask]=1e25;np.testing.assert_array_equal(build(t,y,m,r)['condition'],expected['condition'])
 def test_time_origin_and_uniform_time_scale(self):
  t,y,m,r=fixture();e=extra((t,y,m,r));np.testing.assert_allclose(extra((t+125,y,m,r)),e,atol=1e-6);np.testing.assert_allclose(extra((t*3,y,m,r)),e,atol=1e-6)
 def test_position_translation_invariance(self):
  t,y,m,r=fixture();e=extra((t,y,m,r));y[:,:,:3]+=np.array([100,-50,30]);np.testing.assert_allclose(extra((t,y,m,r)),e,atol=1e-6)
 def test_rigid_rotation_equivariance(self):
  t,y,m,r=fixture();e=extra((t,y,m,r));q=np.array([[0,0,1],[0,1,0],[-1,0,0]],float);y[:,:,:3]=y[:,:,:3]@q.T;rot,bad=rotation_matrix(y[:,:,3:]);self.assertFalse(bad.any());y[:,:,3:]=rotation6(q@rot);actual=extra((t,y,m,r))
  for j in (0,3,8,11):np.testing.assert_allclose(actual[:,:,j:j+3],e[:,:,j:j+3]@q.T,atol=1e-6)
 def test_stationary_exterior_differs_from_missing(self):
  t,y,m,r=fixture();y[0]=y[1];y[-1]=y[-2];e=extra((t,y,m,r));self.assertGreater(float(np.linalg.norm(e[2])),0);self.assertTrue((e[2,:,[6,7,14,15]]==1).all())
 def test_known_payload_and_inputs_preserved(self):
  args=fixture();copies=[x.copy() for x in args];result=build(*args);req=result['request'];np.testing.assert_array_equal(req['observed'][req['mask']],args[1][req['mask']]);np.testing.assert_array_equal(result['condition'][:,:394],req['condition']);self.assertEqual(result['condition'].shape,(5,666))
  for original,copied in zip(args,copies):np.testing.assert_array_equal(original,copied)
  for key in ('condition','tangent_context'):self.assertFalse(result[key].flags.writeable)
 def test_shortest_rotation_near_pi_and_zero(self):
  angles=np.array([1e-10,np.pi-1e-8,np.pi+1e-8]);v=rotation_vector(rz(angles));np.testing.assert_allclose(v[:,2],[1e-10,np.pi-1e-8,-np.pi+1e-8],atol=1e-7)
 def test_invalid_observed_data_rejected(self):
  t,y,m,r=fixture();y[1,0,0]=np.nan
  with self.assertRaises(ValueError):build(t,y,m,r)
  t,y,m,r=fixture();t[2]=t[1]
  with self.assertRaises(ValueError):build(t,y,m,r)
  t,y,m,r=fixture();m[0,0,0]=False
  with self.assertRaises(ValueError):build(t,y,m,r)
if __name__=='__main__':
 out=TR/'results/sequence-tangent-contracts-v1';out.mkdir(exist_ok=False);start=time.perf_counter();suite=unittest.defaultTestLoader.loadTestsFromTestCase(Contracts);result=unittest.TextTestRunner(verbosity=2).run(suite)
 def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
 report=dict(passed=result.wasSuccessful(),tests=result.testsRun,failures=len(result.failures),errors=len(result.errors),seconds=time.perf_counter()-start,source_sha256={n:sha(TR/n) for n in ('sequence_tangent_context_v1.py','check_sequence_tangent_context_v1.py','sequence_conditioning_v1.py')},plan_sha256=sha(TR/'sequence_tangent_context_plan_v1.json'),model_trained=False,production_changed=False,full_goal_complete=False)
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');raise SystemExit(0 if result.wasSuccessful() else 1)
