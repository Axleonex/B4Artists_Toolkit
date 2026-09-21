"""Full-hierarchy reconstruction, leakage isolation and temporal analytic gradients."""
import sys,unittest
from pathlib import Path
from copy import deepcopy
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'training/b4artists_ml'))
from bvh_data import parse_bvh
from temporal_data import quat_matrix
from sequence_data import full_motion,known_window,target_window,semantic_output,coefficients_basis
from sequence_kinematics import forward,backward,sequence_loss


class SequenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=parse_bvh((ROOT/'training/b4artists_ml/cache/07_01.bvh').read_text());cls.motion=full_motion(cls.source)
        cls.skeleton=(cls.motion.names,cls.motion.parents,cls.motion.semantic)

    def window(self):
        d=known_window(self.motion,4,20,np.arange(17)/16,True)
        local,target=target_window(self.motion,np.arange(4,21),d['origin'],d['basis'])
        return d,local,target

    def test_full_chain_recovers_original_motion(self):
        self.assertEqual(len(self.motion.names),23)
        self.assertIn('LeftShoulder',self.motion.names);self.assertIn('LowerBack',self.motion.names)
        d,local,target=self.window()
        np.testing.assert_allclose(semantic_output(local,d['offsets'],self.skeleton),target,atol=1e-12)

    def test_actual_edges_cannot_stretch(self):
        d,local,target=self.window();rng=np.random.default_rng(7);local[:,3:]+=rng.normal(0,.4,local[:,3:].shape)
        p,r,_=forward(local,d['offsets'],self.motion.parents)
        lengths=np.linalg.norm(p[:,1:]-p[:,np.asarray(self.motion.parents[1:])],axis=-1)
        np.testing.assert_allclose(lengths,np.broadcast_to(np.linalg.norm(d['offsets'][1:],axis=-1),lengths.shape),atol=2e-14)
        np.testing.assert_allclose(np.linalg.det(r),1,atol=2e-14)

    def test_forward_backward_gradient(self):
        d,local,target=self.window();local=local[[2,7]].copy();rng=np.random.default_rng(4)
        local[:,3:]+=rng.normal(0,.04,local[:,3:].shape)
        p,r,cache=forward(local,d['offsets'],self.motion.parents);gp=rng.normal(size=p.shape);gr=rng.normal(size=r.shape)
        grad=backward(gp,gr,cache)
        def objective():
            p,r,_=forward(local,d['offsets'],self.motion.parents);return (p*gp).sum()+(r*gr).sum()
        for index in ((0,0),(0,3),(0,7),(1,35),(1,82),(0,136)):
            old=local[index];eps=1e-6;local[index]=old+eps;hi=objective();local[index]=old-eps;lo=objective();local[index]=old
            self.assertAlmostEqual(grad[index],(hi-lo)/(2*eps),places=6)

    def test_sequence_loss_gradient(self):
        d,local,target=self.window();local=local[None].copy();rng=np.random.default_rng(8);local+=rng.normal(0,.01,local.shape)
        truth=target.reshape(1,17,17,9);from temporal_data import rotation_matrix
        tr,_=rotation_matrix(truth[...,3:]);args=(d['offsets'],self.motion.parents,self.motion.semantic,truth[...,:3],tr,np.array([self.motion.semantic_motion.dt]))
        loss,grad=sequence_loss(local,*args)
        for index in ((0,0,0),(0,3,6),(0,8,2),(0,15,59),(0,16,90)):
            old=local[index];eps=1e-6;local[index]=old+eps;hi=sequence_loss(local,*args)[0];local[index]=old-eps;lo=sequence_loss(local,*args)[0];local[index]=old
            self.assertAlmostEqual(grad[index],(hi-lo)/(2*eps),places=6)

    def test_hidden_rotations_and_pelvis_do_not_leak(self):
        m=deepcopy(self.motion);a=known_window(m,4,20,[0,.5,1],True)
        m.local_rotation[5:20]=np.nan;m.semantic_motion.points[5:20]=np.nan;m.semantic_motion.rotations[5:20]=np.nan
        b=known_window(m,4,20,[0,.5,1],True)
        for key in a:np.testing.assert_array_equal(a[key],b[key])

    def test_disabled_context_does_not_read_outside_poses(self):
        m=deepcopy(self.motion);a=known_window(m,4,20,[.5],False)
        m.local_rotation[[3,21]]=np.nan;m.semantic_motion.points[[3,21]]=np.nan;m.semantic_motion.rotations[[3,21]]=np.nan
        b=known_window(m,4,20,[.5],False);np.testing.assert_array_equal(a['x'],b['x'])
        with self.assertRaises(ValueError):known_window(m,4,20,[.5],True)

    def test_local_baseline_endpoints_are_exact(self):
        d,local,target=self.window()
        for key in ('baseline','hermite_local'):
            out=semantic_output(d[key],d['offsets'],self.skeleton)
            np.testing.assert_allclose(out[[0,-1]],target[[0,-1]],atol=1e-12)

    def test_basis_preserves_anchors_and_scales_with_duration(self):
        a=coefficients_basis(np.array([0,.3,1]),.25);b=coefficients_basis(np.array([0,.3,1]),1)
        self.assertTrue((a[[0,-1]]==0).all());np.testing.assert_allclose(b,16*a)
        # The curve is query-order independent and may learn endpoint derivatives.
        np.testing.assert_array_equal(coefficients_basis(np.array([.3]),.25),a[1:2])
        self.assertGreater(abs(coefficients_basis(np.array([1e-4]),.25)[0,0]),0)

    def test_nonroot_translation_rejected(self):
        source=deepcopy(self.source);cursor=len(source.channels[0]);source.channels[1].insert(0,'Xposition');source.values=np.insert(source.values,cursor,0,axis=1)
        with self.assertRaisesRegex(ValueError,'non-root translation'):full_motion(source)

    def test_global_reference_equivariance(self):
        m=deepcopy(self.motion);q=quat_matrix([.8,.1,.3,.2]);sem=m.semantic_motion
        sem.points=sem.points@q.T*2+np.array([3,4,5]);sem.rotations=np.einsum('ij,fkjl->fkil',q,sem.rotations)
        sem.reference=q@sem.reference;sem.rest_pelvis_rotation=q@sem.rest_pelvis_rotation;sem.scale*=2
        m.local_rotation[:,0]=np.einsum('ij,fjk->fik',q,m.local_rotation[:,0])
        a=known_window(self.motion,4,20,[.2,.8],True);b=known_window(m,4,20,[.2,.8],True)
        for key in ('x','baseline','hermite_local','basis_functions'):np.testing.assert_allclose(a[key],b[key],atol=1e-12)

    def test_complete_network_gradient(self):
        from sequence_model import batch_loss
        from context_network import initialize
        d,local,target=self.window();d.update(target=target,dt=self.motion.semantic_motion.dt)
        params=initialize(len(d['x']),5,4*local.shape[-1],dtype=np.float64)
        model=dict(kind='mlp',mean=np.zeros(len(d['x'])),std=np.ones(len(d['x'])),params=params)
        protocol=dict(velocity_weight=.01,acceleration_weight=.0001,rotation_weight=.1,regularization=.0001)
        loss,grad=batch_loss(model,[d],self.skeleton,protocol)
        for key,index in (('w0',(9,2)),('b0',(3,)),('w1',(2,1)),('b1',(140,))):
            old=params[key][index];eps=1e-6;params[key][index]=old+eps;hi=batch_loss(model,[d],self.skeleton,protocol)[0]
            params[key][index]=old-eps;lo=batch_loss(model,[d],self.skeleton,protocol)[0];params[key][index]=old
            self.assertAlmostEqual(grad[key][index],(hi-lo)/(2*eps),places=6)

    def test_model_has_continuous_queries_and_hard_endpoints(self):
        from sequence_model import predict_local
        from context_network import initialize
        d,local,target=self.window();model=dict(kind='mlp',mean=np.zeros(len(d['x'])),std=np.ones(len(d['x'])),params=initialize(len(d['x']),5,4*local.shape[-1]))
        prediction=predict_local(model,d)
        np.testing.assert_array_equal(prediction[[0,-1]],d['baseline'][[0,-1]])
        one=known_window(self.motion,4,20,np.array([.5]),True)
        np.testing.assert_allclose(predict_local(model,one)[0],prediction[8],atol=1e-12)

    def test_acceptance_uses_strongest_baseline(self):
        from sequence_model import acceptance
        import json
        protocol=json.loads((ROOT/'training/b4artists_ml/sequence_protocol_v2.json').read_text())
        agg=dict(position=1.,rotation=1.,velocity=1.,acceleration=1.,length=1.,endpoint_position=0.,endpoint_rotation_matrix=0.,true_edge_length_max=0.)
        reports={k:dict(aggregate=agg.copy(),cohorts={'a':dict(position=1.)}) for k in protocol['baselines']+['mlp']}
        reports['mlp']['aggregate']['position']=.5;reports['mlp']['cohorts']['a']['position']=.5
        self.assertTrue(acceptance(reports,protocol)['passed'])
        reports['fk_linear']['aggregate']['position']=.4
        self.assertFalse(acceptance(reports,protocol)['checks']['position'])


if __name__=='__main__':unittest.main(verbosity=2)
