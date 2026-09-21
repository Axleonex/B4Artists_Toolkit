"""Independent numeric contracts for procedural airborne COM correction."""
from pathlib import Path
import sys,unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
from b4artists_ml import flight_math as fm

class FlightMathTests(unittest.TestCase):
    def test_endpoints_acceleration_and_velocity(self):
        start=np.array([1.,2.,3.]);end=np.array([3.,1.,4.]);g=np.array([1.,-2.,-9.81]);duration=2.
        u=np.linspace(0,1,101);path=fm.trajectory(start,end,u,duration,g)
        np.testing.assert_allclose(path[[0,-1]],[start,end])
        np.testing.assert_allclose(np.diff(path,n=2,axis=0)/(duration/100)**2,np.broadcast_to(g,(99,3)),atol=1e-10)
        a,b=fm.endpoint_velocities(start,end,duration,g)
        np.testing.assert_allclose(b-a,g*duration)
        np.testing.assert_allclose(start+a*duration+.5*g*duration**2,end)
    def test_zero_gravity_and_coordinate_covariance(self):
        start=np.array([1.,2.,3.]);end=np.array([3.,1.,4.]);g=np.array([0.,0.,-9.81]);q=np.array([[0,0,1],[1,0,0],[0,1,0.]])
        u=np.linspace(0,1,7);offset=np.array([5.,-2.,1.])
        np.testing.assert_allclose(fm.trajectory(q@start+offset,q@end+offset,u,2,q@g),fm.trajectory(start,end,u,2,g)@q.T+offset)
        np.testing.assert_allclose(fm.trajectory(start,end,[.5],2,[0,0,0])[0],(start+end)/2)
    def test_cubic_reproduces_arbitrary_polynomials(self):
        coeff=np.array([[1.,2.,3.],[2.,-3.,5.],[-1.,8.,2.],[9.,1.,-4.]])
        def poly(t):return sum(t[:,None]**i*c for i,c in enumerate(coeff))
        samples=poly(np.array([0,1/3,2/3,1.]));a,b=fm.cubic_controls(samples);t=np.linspace(0,1,33)[:,None]
        path=(1-t)**3*samples[0]+3*(1-t)**2*t*a+3*(1-t)*t*t*b+t**3*samples[-1]
        np.testing.assert_allclose(path,poly(t[:,0]),atol=1e-13)
    def test_invalid_numeric_inputs(self):
        for samples in (0,[],[1,2,3],[1,2,np.nan,4]):
            with self.assertRaises(ValueError):fm.cubic_controls(samples)
        for u,duration in (([-.1],1),([1.1],1),([np.nan],1),([.5],0),([.5],np.inf)):
            with self.assertRaises(ValueError):fm.trajectory([0]*3,[1]*3,u,duration,[0,0,-9.81])
    def test_authored_intervals_contacts_and_adjoining_flights(self):
        row=dict(start=1.,end=11.,strength=1.)
        self.assertEqual(len(fm.validate([row,dict(row,start=11.,end=21.)],[1.,11.,21.],[])),2)
        contact=dict(start=-1.,end=0.,blend=1.,strength=1.)
        fm.validate([row],[1.,11.],[contact])
        for bad in (dict(row,start=2.),dict(row,end=1.),dict(row,strength=-1.)):
            with self.assertRaises(ValueError):fm.validate([bad],[1.,11.],[])
        for bad in (dict(row,collision_strength=-.1),dict(row,collision_strength=1.1),dict(row,collision_clearance=-.1),dict(row,collision_clearance=1.1)):
            with self.assertRaises(ValueError):fm.validate([bad],[1.,11.],[])
        with self.assertRaisesRegex(ValueError,'overlap'):fm.validate([row],[1.,11.],[dict(contact,blend=2.)])
        with self.assertRaisesRegex(ValueError,'overlap'):fm.validate([row,row],[1.,11.],[])

if __name__=='__main__':unittest.main()
