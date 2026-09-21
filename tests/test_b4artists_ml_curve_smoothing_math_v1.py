"""Shape curve math: fixed samples, scalar bounds, and shared derivatives."""
from pathlib import Path
import sys,unittest
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'training/b4artists_ml')]
from b4artists_ml.curve_smoothing import tangents,handles

class ShapeCurveTests(unittest.TestCase):
    def evaluate(self,x,y):
        left,right=handles(x,y);out=[]
        for i in range(len(x)-1):
            u=np.linspace(0,1,301);v=(1-u)**3*y[i]+3*(1-u)**2*u*right[i,1]+3*(1-u)*u**2*left[i+1,1]+u**3*y[i+1];out.append(v)
        return out,left,right
    def test_fixed_keys_and_no_extremum_overshoot(self):
        x=np.array([1.,11.,21.]);y=np.array([0.,-.15,0.]);values,_,_=self.evaluate(x,y)
        for i,v in enumerate(values):self.assertEqual(v[0],y[i]);self.assertEqual(v[-1],y[i+1]);self.assertGreaterEqual(v.min(),-.15);self.assertLessEqual(v.max(),0.)
        self.assertEqual(tangents(x,y)[1],0.)
    def test_nonuniform_monotone_shape(self):
        rng=np.random.default_rng(9812)
        for _ in range(30):
            x=np.cumsum(rng.uniform(.02,8.,12));y=np.cumsum(rng.uniform(0.,10.,12));values,_,_=self.evaluate(x,y)
            for i,v in enumerate(values):self.assertTrue(np.all(np.diff(v)>=-1e-12));self.assertGreaterEqual(v.min(),y[i]-1e-12);self.assertLessEqual(v.max(),y[i+1]+1e-12)
    def test_incoming_and_outgoing_derivatives_agree(self):
        x=np.array([0.,.125,4.,5.5,9.]);y=np.array([1.,2.,4.,3.,0.]);_,left,right=self.evaluate(x,y)
        incoming=(y[1:-1]-left[1:-1,1])/(x[1:-1]-left[1:-1,0]);outgoing=(right[1:-1,1]-y[1:-1])/(right[1:-1,0]-x[1:-1]);np.testing.assert_allclose(incoming,outgoing,rtol=0,atol=1e-14)
    def test_two_keys_are_linear(self):
        x=np.array([2.,7.]);y=np.array([5.,-3.]);values,_,_=self.evaluate(x,y);np.testing.assert_allclose(values[0],np.linspace(5.,-3.,301),atol=2e-15)
    def test_flat_interval_stays_fixed(self):
        x=np.array([1.,2.,7.,8.]);y=np.array([0.,1.,1.,0.]);values,_,_=self.evaluate(x,y);np.testing.assert_allclose(values[1],1.,atol=2e-16)
    def test_time_translation_and_positive_scale(self):
        x=np.array([1.,3.,8.]);y=np.array([2.,5.,3.]);left,right=handles(x,y);a,b=handles(x*4+100,y)
        for orig,new in [(left,a),(right,b)]:np.testing.assert_allclose(new[:,0],orig[:,0]*4+100);np.testing.assert_allclose(new[:,1],orig[:,1])
    def test_vectorized_interiors_are_bit_exact_scalar_reference(self):
        from b4artists_ml.temporal_math import harmonic_tangent
        rng=np.random.default_rng(1904)
        for _ in range(40):
            x=np.cumsum(rng.uniform(.001,20.,int(rng.integers(3,241))));y=rng.normal(size=len(x));h=np.diff(x);d=np.diff(y)/h
            expected=np.r_[d[0],[harmonic_tangent(d[i-1],d[i],h[i-1],h[i]) for i in range(1,len(x)-1)],d[-1]]
            np.testing.assert_array_equal(tangents(x,y),expected)
    def test_invalid_input_rejects(self):
        for x,y in [([0,0],[1,2]),([1,0],[1,2]),([0],[1]),([0,1],[1,float('nan')]),([0,1],[1]),([0,1],1.),([0,float('inf')],[1,2])]:
            with self.assertRaises(ValueError):tangents(x,y)
    def test_quaternion_same_sign_component_cannot_cross_zero(self):
        # A same-sign component at both endpoints stays nonzero under the scalar
        # bounds. With positive adjacent quaternion dot products, at least one
        # such component exists, so normalizing an interval cannot hit zero.
        rng=np.random.default_rng(180);q=rng.normal(size=(8,4));q/=np.linalg.norm(q,axis=1)[:,None]
        for i in range(1,len(q)):
            if np.dot(q[i-1],q[i])<0:q[i]*=-1
        values=[self.evaluate(np.arange(8.),q[:,j])[0] for j in range(4)]
        for i in range(7):self.assertGreater(np.linalg.norm(np.stack([v[i] for v in values],axis=-1),axis=-1).min(),0.)
if __name__=='__main__':unittest.main()
