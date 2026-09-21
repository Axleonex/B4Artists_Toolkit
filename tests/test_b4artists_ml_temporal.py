"""Temporal hidden-label isolation, coordinate invariance and training/evaluation tests."""
from pathlib import Path
from copy import deepcopy
import sys,unittest
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'training/b4artists_ml'))
from bvh_data import parse_bvh
from temporal_data import *
from temporal_model import residual_loss,training_arrays,standardize,evaluate,predict
from context_network import initialize


class TemporalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=parse_bvh((ROOT/'training/b4artists_ml/cache/07_01.bvh').read_text())
        cls.motion=temporal_motion(cls.source)

    def test_rotation_representations(self):
        rng=np.random.default_rng(7);q=rng.normal(size=(100,17,4));r=quat_matrix(q)
        np.testing.assert_allclose(quat_matrix(quaternion(r)),r,atol=2e-14)
        result,bad=rotation_matrix(rotation6(r));self.assertFalse(bad.any())
        np.testing.assert_allclose(result,r,atol=2e-14)
        for q in ((0,1,0,0),(0,0,1,0),(0,0,0,1),(1,0,0,0)):
            r=quat_matrix(q);np.testing.assert_allclose(quat_matrix(quaternion(r)),r,atol=1e-14)
        np.testing.assert_allclose(np.linalg.det(result),1,atol=2e-14)

    def test_degenerate_rotation_is_explicit(self):
        base=quat_matrix([.8,.2,.3,.4]);result,bad=rotation_matrix(np.zeros((2,6)),base)
        self.assertTrue(bad.all());np.testing.assert_allclose(result,np.broadcast_to(base,(2,3,3)))
        with self.assertRaises(ValueError):rotation_matrix([np.nan]*6)

    def test_slerp_endpoints_and_half_turn(self):
        a=np.broadcast_to(np.eye(3),(17,3,3));b=np.broadcast_to(quat_matrix([0,0,0,1]),a.shape)
        r=slerp(a,b,np.array([0,.5,1]));np.testing.assert_allclose(r[0],a,atol=1e-14);np.testing.assert_allclose(r[-1],b,atol=1e-14)
        np.testing.assert_allclose(r[1,0]@np.array([1,0,0]),[0,1,0],atol=1e-14)

    def test_frame_zero_excluded_and_actual_time(self):
        self.assertEqual(self.motion.frames[0],1);self.assertTrue(np.all(np.diff(self.motion.frames)==4))
        self.assertAlmostEqual(self.motion.dt,self.source.frame_time*4)

    def test_hidden_pelvis_and_joints_cannot_leak(self):
        a=features(self.motion,4,20,np.linspace(0,1,17));changed=deepcopy(self.motion)
        changed.points[5:20]=np.nan;changed.rotations[5:20]=np.nan
        b=features(changed,4,20,np.linspace(0,1,17))
        for key in ('x','baseline','linear','basis','origin'):np.testing.assert_array_equal(a[key],b[key])
        changed.points[4,0]+=.1
        self.assertFalse(np.array_equal(features(changed,4,20,[.5])['x'],a['x'][8:9]))

    def test_missing_context_is_not_read(self):
        a=features(self.motion,4,20,[.5],False);changed=deepcopy(self.motion)
        changed.points[[3,21]]=np.nan;changed.rotations[[3,21]]=np.nan
        b=features(changed,4,20,[.5],False)
        np.testing.assert_array_equal(a['x'],b['x']);np.testing.assert_array_equal(a['baseline'],b['baseline'])
        with self.assertRaises(ValueError):features(changed,4,20,[.5],True)

    def test_fixed_anchor_inverse(self):
        d=features(self.motion,4,20,[0,.5,1]);target=labels(self.motion,np.array([4,12,20]),d['origin'],d['basis']).reshape(3,J,9)
        world=target[...,:3]@d['basis'].T*self.motion.scale+d['origin']
        np.testing.assert_allclose(world,self.motion.points[[4,12,20]],atol=1e-12)
        r,_=rotation_matrix(target[...,3:]);actual=np.einsum('ij,fkjl->fkil',d['basis'],r)
        np.testing.assert_allclose(actual,self.motion.rotations[[4,12,20]],atol=1e-12)
        self.assertGreater(np.linalg.norm(target[1,0,:3]),.01)

    def test_world_rigid_transform_and_scale_invariance(self):
        m=deepcopy(self.motion);q=quat_matrix([.8,.1,.4,.2]);scale=3.7;translation=np.array([7,-2,4])
        m.points=m.points@q.T*scale+translation;m.rotations=np.einsum('ij,fkjl->fkil',q,m.rotations)
        m.reference=q@m.reference;m.rest_pelvis_rotation=q@m.rest_pelvis_rotation;m.scale*=scale
        a=features(self.motion,4,20,[.25,.5]);b=features(m,4,20,[.25,.5])
        for key in ('x','baseline','linear'):np.testing.assert_allclose(a[key],b[key],atol=1e-12)

    def test_invalid_static_reference_rejected(self):
        for field,value in (('scale',0),('dt',0),('rest',np.full((17,3),np.nan))):
            m=deepcopy(self.motion);setattr(m,field,value)
            with self.assertRaises(ValueError):features(m,4,20,[.5])
        source=deepcopy(self.source)
        class Degenerate:
            names=source.names;frame_time=source.frame_time
            def transforms(self):
                p,r=source.transforms();p[0]=0;return p,r
        with self.assertRaises(ValueError):temporal_motion(Degenerate())

    def fixture(self):
        return windows(self.motion,dict(gaps=[8,16],contexts=[False,True],training_windows_per_gap=2,evaluation_windows_per_gap=2),'train',42)

    def test_window_context_pairing_and_endpoint_envelope(self):
        d=self.fixture();self.assertEqual(d['x'].shape[1],668);self.assertEqual(d['target'].shape[1],153)
        for gap in (8,16):
            starts=[]
            for context in (False,True):starts.append(d['frame'][(d['gap']==gap)&(d['context']==context)&(d['t']==0)])
            np.testing.assert_array_equal(*starts)
        ends=(d['t']==0)|(d['t']==1);self.assertTrue((d['envelope'][ends]==0).all())
        model=dict(kind='ridge',mean=np.zeros(668),std=np.ones(668),coef=np.ones((669,153)))
        np.testing.assert_array_equal(predict(model,d)[ends],d['baseline'][ends])
        np.testing.assert_allclose(d['baseline'][ends],d['target'][ends],atol=1e-12)

    def test_duplicate_clip_and_hash_rejected(self):
        a={'files':[dict(clip='a',sha256='1',split='train')]}
        for row in (dict(clip='a',sha256='2',split='validation'),dict(clip='b',sha256='1',split='validation')):
            with self.assertRaises(ValueError):validate_manifests([a,{'files':[row]}])
        self.assertEqual(validate_manifests([a]),{'a':'train'})

    def test_training_cohort_mass_and_standardization(self):
        d=self.fixture();data=training_arrays([('a',d),('b',d)])
        self.assertTrue((data['envelope']>0).all());self.assertAlmostEqual(float(data['weights'].sum()),1,places=6)
        for duration in np.unique(data['x'][:,-3]):
            self.assertAlmostEqual(float(data['weights'][data['x'][:,-3]==duration].sum()),.5,places=6)
        mean,std=standardize(data);self.assertTrue((std>=.1).all())
        np.testing.assert_allclose(np.sum((data['x']-mean)*data['weights'][:,None],axis=0),0,atol=1e-6)

    def test_loss_gradient(self):
        rng=np.random.default_rng(4);x=rng.normal(size=(4,7));target=rng.normal(size=(4,D));base=rng.normal(size=(4,D));e=np.array([0,.1,.8,1.]);w=np.array([1,2,3,4.])
        params=initialize(7,5,D,dtype=np.float64)
        loss,grad=residual_loss(params,x,target,base,e,w)
        for key,index in (('w0',(2,3)),('b0',(2,)),('w1',(3,5)),('b1',(7,))):
            old=params[key][index];eps=1e-6;params[key][index]=old+eps;high=residual_loss(params,x,target,base,e,w)[0]
            params[key][index]=old-eps;low=residual_loss(params,x,target,base,e,w)[0];params[key][index]=old
            self.assertAlmostEqual(grad[key][index],(high-low)/(2*eps),places=8)

    def test_metrics_do_not_cross_window_boundaries(self):
        d=self.fixture();perfect=evaluate([('a',d)],lambda row:row['target'])
        for key in ('position','root','velocity','acceleration','length','endpoint_position'):self.assertEqual(perfect['aggregate'][key],0)
        # A different constant offset in every window has zero derivative error.
        pred=d['target'].copy().reshape(-1,J,9);pred[...,:3]+=d['window'][:,None,None]*5
        report=evaluate([('a',d)],lambda row:pred.reshape(-1,D))
        self.assertLess(report['aggregate']['velocity'],1e-12);self.assertLess(report['aggregate']['acceleration'],1e-10)
        self.assertGreater(report['aggregate']['position'],0)


if __name__=='__main__':unittest.main(verbosity=2)
