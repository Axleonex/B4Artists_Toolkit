from pathlib import Path
import os,sys,unittest,math
sys.path.insert(0,os.environ.get('B4ML_PACKAGE',str(Path(__file__).resolve().parents[1])))
import numpy as np
from b4artists_ml import balance_math as bm

class BalanceMathTests(unittest.TestCase):
    def test_inset_square_and_nearest_target(self):
        hull=bm.inset_hull([[-1,-2],[1,-2],[1,2],[-1,2]],.2)
        np.testing.assert_allclose(hull,[[-.8,-1.8],[.8,-1.8],[.8,1.8],[-.8,1.8]])
        np.testing.assert_allclose(bm.closest_in_hull([2,3],hull),[.8,1.8])
        np.testing.assert_allclose(bm.closest_in_hull([.1,.2],hull),[.1,.2])
    def test_triangle_and_coordinate_scale(self):
        original=np.array([[0,0],[2,0],[0,2]],float);point=np.array([1.2,1.2])
        baseline=bm.inset_hull(original,.1);target=bm.closest_in_hull(point,baseline)
        for scale in (.001,3,1000):
            angle=.6;q=np.array([[np.cos(angle),-np.sin(angle)],[np.sin(angle),np.cos(angle)]])
            shift=np.array([4.,-2.]);h=bm.inset_hull(original@q.T*scale+shift,.1*scale)
            np.testing.assert_allclose(bm.closest_in_hull(q@point*scale+shift,h),q@target*scale+shift,atol=1e-10)
    def test_degenerate_and_oversized_insets(self):
        for points,margin in (([[0,0],[1,0]],0),([[0,0],[1,0],[1,1],[0,1]],.5),([[0,0],[1,0],[1,1],[0,1]],2),([[0,0],[1,0],[1,1]],-1)):
            with self.assertRaises(ValueError):bm.inset_hull(points,margin)
    def test_duplicates_and_order(self):
        p=np.array([[-1,-1],[1,-1],[1,1],[-1,1],[0,0],[-1,-1]])
        np.testing.assert_allclose(bm.inset_hull(p,.1),bm.inset_hull(p[::-1],.1))

    def test_capture_point_uses_world_velocity_and_pendulum_time_constant(self):
        point,tau,height,velocity=bm.capture_point(
            [0.,0.,2.],[1.,-.5,4.],[0.,0.,-10.],[0.,0.,0.],[0.,0.,1.],[1.,0.,0.],[0.,1.,0.])
        self.assertAlmostEqual(height,2.)
        self.assertAlmostEqual(tau,math.sqrt(.2))
        np.testing.assert_allclose(velocity,[1.,-.5])
        np.testing.assert_allclose(point,[math.sqrt(.2),-.5*math.sqrt(.2)])

    def test_capture_point_rejects_wrong_gravity_and_nonpositive_height(self):
        args=([0.,0.,1.],[0.,0.,0.],[0.,0.,-9.81],[0.,0.,0.],[0.,0.,1.],[1.,0.,0.],[0.,1.,0.])
        with self.assertRaises(ValueError):bm.capture_point(*args[:2], [0.,0.,9.81], *args[3:])
        with self.assertRaises(ValueError):bm.capture_point([0.,0.,-.1],*args[1:])

if __name__=='__main__':unittest.main()
