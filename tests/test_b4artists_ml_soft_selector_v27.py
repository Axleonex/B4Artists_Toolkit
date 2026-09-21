"""Soft readout geometry, endpoint, context and local continuity checks."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','4')
from pathlib import Path
import sys,unittest,copy
from dataclasses import replace
from unittest.mock import patch
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'training/b4artists_ml'),str(ROOT/'tests')]
import soft_selector_v27 as m
import projected_selector_v26 as hard
from temporal_data import rotation6,quat_matrix,rotation_matrix,quaternion
from projected_pool_v26 import combine
from test_b4artists_ml_semantic_predictor import windows

class SoftReadoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.model=m.load(ROOT/'training/b4artists_ml/results/projected_selector_v26/best_learned.npz')
    def experts(self,t):
        a=np.zeros((4,len(t),17,9));angles=[-2.,0.,0.,2.];positions=[-1.,2.,.5,3.]
        for i in range(4):
            a[i,...,:3]=positions[i];q=np.array([np.cos(angles[i]/2),0.,0.,np.sin(angles[i]/2)]);a[i,...,3:]=rotation6(quat_matrix(q))
        return a.reshape(4,len(t),153)
    def test_single_choice_matches_each_expert_inside_interval(self):
        t=np.array([.5]);x=self.experts(t)
        for i in range(12):
            p=np.eye(12)[i];np.testing.assert_array_equal(m.blend(x,p,t),combine(x,i))
    def test_marginal_position_weights_and_proper_rotations(self):
        t=np.array([.2,.5,.8]);x=self.experts(t);p=np.arange(1,13,dtype=float);p/=p.sum();a=m.blend(x,p,t).reshape(3,17,9)
        expected=np.sum(p.reshape(4,3).sum(axis=1)*np.array([-1.,2.,.5,3.]));np.testing.assert_allclose(a[...,:3],expected,rtol=0,atol=1e-14)
        rot,bad=rotation_matrix(a[...,3:]);self.assertFalse(bad.any());np.testing.assert_allclose(np.swapaxes(rot,-1,-2)@rot,np.broadcast_to(np.eye(3),rot.shape),rtol=0,atol=1e-12)
    def test_exact_endpoint_priority_override(self):
        t=np.array([0.,.5,1.]);x=self.experts(t)
        for p in (np.ones(12)/12,np.eye(12)[11]):np.testing.assert_array_equal(m.blend(x,p,t)[[0,2]],x[0,[0,2]])
    def test_smooth_across_probability_rank_switch(self):
        t=np.array([.5]);x=self.experts(t);a=np.zeros(12);b=a.copy();eps=1e-6;a[0]=b[11]=.5+eps;a[11]=b[0]=.5-eps
        sa=m.blend(x,a,t);sb=m.blend(x,b,t);self.assertLess(float(abs(sa-sb).max()),1e-4);self.assertGreater(float(abs(combine(x,int(a.argmax()))-combine(x,int(b.argmax()))).max()),1.)
    def test_quaternion_signs_do_not_change_mixture(self):
        t=np.array([.5]);x=self.experts(t);p=np.ones(12)/12;expected=m.blend(x,p,t)
        def flipped(matrix):q=quaternion(matrix);q[0]*=-1;q[2]*=-1;return q
        with patch.object(m,'quaternion',side_effect=flipped):actual=m.blend(x,p,t)
        np.testing.assert_allclose(actual,expected,rtol=0,atol=1e-14)
    def test_ambiguous_halfturn_mixture_rejects(self):
        t=np.array([.5]);x=self.experts(t).reshape(4,1,17,9)
        for i,angle in ((0,np.pi),(3,-np.pi)):x[i,...,3:]=rotation6(quat_matrix([np.cos(angle/2),0,0,np.sin(angle/2)]))
        p=np.zeros(12);p[0]=p[11]=.5
        with self.assertRaisesRegex(ValueError,'Ambiguous'):m.blend(x.reshape(4,1,153),p,t)
    def test_invalid_inputs_reject(self):
        t=np.array([.5]);x=self.experts(t)
        for p in (np.ones(11)/11,np.ones(12),np.full(12,np.nan),np.r_[-.1,np.full(11,1.1/11)]):
            with self.assertRaises(ValueError):m.blend(x,p,t)
        for t in (np.array(.5),np.array([np.nan]),np.array([-.1]),np.array([[.5]])):
            with self.assertRaises(ValueError):m.blend(x,np.ones(12)/12,t)
    def test_stationary_exact_reference_and_queries_independent(self):
        w=windows()[0];o=w['observations'];static=replace(o,positions=np.repeat(o.positions[:1],4,axis=0),rotations=np.repeat(o.rotations[:1],4,axis=0))
        np.testing.assert_array_equal(m.predict_packed(self.model,static,w['t']),hard.predict_packed(self.model,static,w['t']))
        all_values=m.predict_packed(self.model,o,w['t'])
        for i,t in enumerate(w['t']):np.testing.assert_allclose(m.predict_packed(self.model,o,np.array([t]))[0],all_values[i],rtol=0,atol=1e-12)
        np.testing.assert_array_equal(all_values[[0,-1]],w['linear'][[0,-1]])
    def test_hidden_targets_and_masked_context_do_not_affect_inference(self):
        w=windows()[0];o=w['observations'];expected=m.predict_packed(self.model,o,w['t']);w['target'][:]=np.nan;np.testing.assert_array_equal(expected,m.predict_packed(self.model,o,w['t']))
        masked=replace(o,context=False);positions=masked.positions.copy();positions[2:]+=100
        np.testing.assert_array_equal(m.predict_packed(self.model,masked,w['t']),m.predict_packed(self.model,replace(masked,positions=positions),w['t']))
if __name__=='__main__':unittest.main(verbosity=2)
