"""Physical versus coordinate transforms, explicit unknowns and scene-read semantics."""
from pathlib import Path
from copy import deepcopy
from types import SimpleNamespace
import sys,unittest
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'training/b4artists_ml'))
from environment_context import Environment,SupportPlane,encode_environment,from_scene,timeline_seconds,free_flight_points
from environment_data import environment_window,gravity_features
from sequence_data import full_motion
from bvh_data import parse_bvh
from temporal_data import quat_matrix

class EnvironmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.motion=full_motion(parse_bvh((ROOT/'training/b4artists_ml/cache/07_01.bvh').read_text()))

    def test_known_zero_and_unknown_are_different(self):
        unknown=encode_environment(Environment(),[0,0,0],np.eye(3),1,1)
        zero=encode_environment(Environment(acceleration=(0,0,0)),[0,0,0],np.eye(3),1,1)
        self.assertEqual(unknown[5],0);self.assertEqual(zero[5],1);self.assertEqual(zero[4],0)
        np.testing.assert_array_equal(zero[:4],0)

    def test_direction_hint_never_invents_acceleration(self):
        e=Environment(direction_hint=(0,0,-2));a=encode_environment(e,[0,0,0],np.eye(3),.5,2)
        np.testing.assert_array_equal(a[:3],[0,0,-1]);self.assertEqual(a[4],1);self.assertEqual(a[5],0);self.assertEqual(a[3],0)
        with self.assertRaisesRegex(ValueError,'known acceleration'):free_flight_points([0,0,0],[1,0,0],[0,.5,1],1,e)

    def test_dimensionless_strength_and_plane_height(self):
        e=Environment(acceleration=(0,0,-10),support=SupportPlane((0,0,1),(0,0,5)))
        a=encode_environment(e,[0,0,3],np.eye(3),2,.5)
        self.assertEqual(a[3],1.25);np.testing.assert_array_equal(a[6:9],[0,0,1]);self.assertEqual(a[9],1);self.assertEqual(a[10],1)

    def test_coordinate_length_and_time_unit_invariance(self):
        q=quat_matrix([.8,.1,.3,.2]);basis=quat_matrix([.7,.2,-.1,.3]);origin=np.array([2.,4.,3.]);translation=np.array([10.,-2.,7.]);u=3.2;k=.5
        e=Environment(acceleration=(1,0,-9),support=SupportPlane((1,2,0),(0,0,1)))
        original=encode_environment(e,origin,basis,.7,1.2)
        changed=Environment(acceleration=tuple(q@e.acceleration*u/k**2),support=SupportPlane(tuple(q@e.support.point*u+translation),tuple(q@e.support.normal)))
        result=encode_environment(changed,q@origin*u+translation,q@basis,.7*u,1.2*k)
        np.testing.assert_allclose(result,original,atol=1e-12)

    def test_physical_tilt_alias_is_fixed(self):
        m=deepcopy(self.motion);q=quat_matrix([np.sqrt(.5),np.sqrt(.5),0,0]);sem=m.semantic_motion
        sem.points=sem.points@q.T;sem.rotations=np.einsum('ij,fkjl->fkil',q,sem.rotations);m.local_rotation[:,0]=np.einsum('ij,fjk->fik',q,m.local_rotation[:,0])
        env=Environment(direction_hint=(0,-1,0));a=environment_window(self.motion,4,20,[0,.5,1],True,env);b=environment_window(m,4,20,[0,.5,1],True,env)
        np.testing.assert_allclose(a['x'],b['x'],atol=1e-12)
        self.assertGreater(np.linalg.norm(a['environment'][:3]-b['environment'][:3]),1)
        self.assertGreater(np.linalg.norm(gravity_features([a])-gravity_features([b])),1)

    def test_scene_coordinate_rotation_remains_invariant(self):
        m=deepcopy(self.motion);q=quat_matrix([.8,.1,.3,.2]);sem=m.semantic_motion
        sem.points=sem.points@q.T;sem.rotations=np.einsum('ij,fkjl->fkil',q,sem.rotations);m.local_rotation[:,0]=np.einsum('ij,fjk->fik',q,m.local_rotation[:,0])
        a=environment_window(self.motion,4,20,[.5],True,Environment(direction_hint=(0,-1,0)))
        b=environment_window(m,4,20,[.5],True,Environment(direction_hint=tuple(q@np.array([0,-1,0]))))
        np.testing.assert_allclose(gravity_features([a]),gravity_features([b]),atol=1e-12)

    def test_hidden_motion_and_support_are_not_inferred(self):
        env=Environment(direction_hint=(0,-1,0));m=deepcopy(self.motion);a=environment_window(m,4,20,[.5],True,env)
        m.local_rotation[5:20]=np.nan;m.semantic_motion.points[5:20]=np.nan;m.semantic_motion.rotations[5:20]=np.nan
        b=environment_window(m,4,20,[.5],True,env)
        np.testing.assert_array_equal(gravity_features([a]),gravity_features([b]));self.assertEqual(a['environment'][10],0)

    def test_inference_does_not_consume_labels_or_untrained_strength(self):
        w=environment_window(self.motion,4,20,[.5],True,Environment(acceleration=(0,-9,0),support=SupportPlane((0,0,0),(0,1,0))))
        a=gravity_features([w]);w['target']=np.nan;w['target_local']=np.nan;w['environment'][3]*=2;w['environment'][9]+=10
        np.testing.assert_array_equal(gravity_features([w]),a)
        self.assertEqual(a.shape,(1,641))

    def test_unknown_or_zero_direction_is_rejected_by_direction_model(self):
        for env in (Environment(),Environment(acceleration=(0,0,0))):
            w=environment_window(self.motion,4,20,[.5],True,env)
            with self.assertRaisesRegex(ValueError,'known gravity direction'):gravity_features([w])

    def test_free_flight_has_exact_endpoints_and_acceleration(self):
        env=Environment(acceleration=(0,0,-9.81));t=np.arange(41)/40;a=np.array([0.,0.,1.]);b=np.array([2.,0.,1.])
        p=free_flight_points(a,b,t,1,env)
        np.testing.assert_array_equal(p[[0,-1]],[a,b]);self.assertAlmostEqual(p[20,2],2.22625)
        np.testing.assert_allclose(np.diff(p,n=2,axis=0)/(.025**2),np.broadcast_to(env.acceleration,(39,3)),atol=1e-10)
        line=free_flight_points(a,b,t,1,Environment(acceleration=(0,0,0)))
        np.testing.assert_allclose(line,a[None]*(1-t[:,None])+b[None]*t[:,None])

    def test_scene_adapter_is_read_only_and_uses_internal_units(self):
        scene=SimpleNamespace(use_gravity=True,gravity=(1,2,-9),unit_settings=SimpleNamespace(scale_length=.01),render=SimpleNamespace(fps=30,fps_base=1.001))
        self.assertEqual(from_scene(scene).acceleration,(1,2,-9));self.assertEqual(scene.gravity,(1,2,-9))
        scene.unit_settings.scale_length=100;self.assertEqual(from_scene(scene).acceleration,(1,2,-9))
        scene.use_gravity=False;self.assertEqual(from_scene(scene).acceleration,(0,0,0));self.assertAlmostEqual(timeline_seconds(scene,10.25,40.25),1.001)

    def test_invalid_frames_vectors_and_bases_rejected(self):
        for env in (dict(acceleration=(0,np.nan,0)),dict(direction_hint=(0,0,0)),dict(acceleration=(0,0,-1),direction_hint=(0,0,-1))):
            with self.assertRaises(ValueError):Environment(**env)
        with self.assertRaises(ValueError):SupportPlane((0,0,0),(0,0,0))
        for basis in (np.eye(3)*2,np.diag([-1,1,1]),np.full((3,3),np.nan)):
            with self.assertRaises(ValueError):encode_environment(Environment(),[0,0,0],basis,1,1)
        with self.assertRaises(ValueError):timeline_seconds(SimpleNamespace(render=SimpleNamespace(fps=30,fps_base=1)),2,1)

    def test_kernel_denominator_control_is_unchanged(self):
        from kernel_motion import kernel
        rng=np.random.default_rng(17);a=rng.normal(size=(3,637));b=rng.normal(size=(5,637))
        padded_a=np.c_[a,np.zeros((3,4))];padded_b=np.c_[b,np.zeros((5,4))]
        np.testing.assert_allclose(kernel(a,b,.25),kernel(padded_a,padded_b,.25*np.sqrt(637/641)),atol=1e-14)

    def test_gravity_model_consumes_direction_and_ignores_hidden_labels(self):
        from gravity_model import infer_coefficients,SCHEMA
        a=environment_window(self.motion,4,20,[.5],True,Environment(direction_hint=(0,-1,0)))
        b=environment_window(self.motion,4,20,[.5],True,Environment(direction_hint=(0,0,-1)))
        std=np.ones(641);std[-4:]=.1;centers=gravity_features([a])/std
        model=dict(kind='kernel',variant='raw_pose',feature_schema=SCHEMA,mean=np.zeros(641),std=std,centers=centers,width=.25,alpha=np.ones((1,564))*.01)
        original=infer_coefficients(model,[a]);self.assertGreater(np.linalg.norm(original-infer_coefficients(model,[b])),.01)
        a['target']=np.nan;a['target_local']=np.nan;a['environment'][3]=999
        np.testing.assert_array_equal(infer_coefficients(model,[a]),original)
        model['feature_schema']='unknown'
        with self.assertRaises(ValueError):infer_coefficients(model,[a])

if __name__=='__main__':unittest.main(verbosity=2)
