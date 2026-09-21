"""Numerical COM/support contracts, without bpy or model inference."""
from pathlib import Path
import sys,unittest,math,os
sys.path.insert(0,os.environ.get('B4ML_PACKAGE',str(Path(__file__).resolve().parents[1])))
import numpy as np
from b4artists_ml import support_math as sm

class SupportMathTests(unittest.TestCase):
    def test_mass_response_and_weight_scale(self):
        a=[[0,0,0],[2,0,0]];b=[[0,0,2],[2,0,4]]
        c,centers,w=sm.center_of_mass(a,b,[1,3],[.5,.25])
        np.testing.assert_allclose(c,[1.5,0,1]);np.testing.assert_allclose(w,[.25,.75])
        np.testing.assert_allclose(sm.center_of_mass(a,b,[1e307,3e307],[.5,.25])[0],c)
        np.testing.assert_allclose(sm.center_of_mass(a,b,[0,1],[.5,.25])[0],centers[1])

    def test_invalid_mass_models(self):
        for masses,fractions in (([0],[.5]),([-1],[.5]),([1],[2]),([math.nan],[.5]),([1],[math.inf])):
            with self.assertRaises(ValueError):sm.center_of_mass([[0,0,0]],[[1,0,0]],masses,fractions)
        with self.assertRaises(ValueError):sm.center_of_mass([],[],[],[])

    def analyze(self,com=(0,0,2),points=None,**kw):
        if points is None:points=sm.patch_vertices((0,0,0),(0,0,1),2,4,0)
        return sm.support_analysis(com,points,kw.get('origin',(0,0,0)),kw.get('normal',(0,0,1)),kw.get('gravity',(0,0,-9.81)),kw.get('tolerance',1e-5))

    def test_inside_outside_and_boundary_distance(self):
        inside=self.analyze();self.assertEqual(inside['status'],'INSIDE_SUPPORT');self.assertAlmostEqual(inside['margin'],1.)
        outside=self.analyze((2,3,2));self.assertEqual(outside['status'],'OUTSIDE_SUPPORT');self.assertAlmostEqual(outside['margin'],-math.sqrt(2))
        self.assertEqual(self.analyze((1,0,2))['status'],'SUPPORT_BOUNDARY')

    def test_degenerate_and_absent_support(self):
        for pts in ([[0,0,0]],[[0,0,0],[2,0,0]],[[0,0,0],[1,0,0],[2,0,0]]):
            result=self.analyze(points=pts);self.assertEqual(result['status'],'DEGENERATE_SUPPORT');self.assertLessEqual(result['margin'],0)
        self.assertEqual(self.analyze(points=[])['status'],'NO_SUPPORT')

    def test_gravity_and_plane_scope(self):
        self.assertEqual(self.analyze(gravity=(0,0,0))['status'],'ZERO_GRAVITY')
        self.assertEqual(self.analyze(gravity=(0,0,1))['status'],'GRAVITY_NOT_INTO_PLANE')
        self.assertEqual(self.analyze(gravity=(1,0,0))['status'],'GRAVITY_NOT_INTO_PLANE')
        self.assertEqual(self.analyze((0,0,-1))['status'],'COM_BELOW_PLANE')
        inclined=self.analyze(gravity=(1,0,-1));self.assertEqual(inclined['status'],'INCLINED_GEOMETRY_ONLY')
        np.testing.assert_allclose(inclined['projection'],[2,0,0])

    def test_coordinate_and_length_invariance(self):
        q=np.array([[0,0,1],[1,0,0],[0,1,0]],float);shift=np.array([4,-3,2.])
        pts=sm.patch_vertices((0,0,0),(0,0,1),2,4,0)
        for scale in (.001,1,1000):
            result=self.analyze(q@np.array((.2,.3,2))*scale+shift,pts@q.T*scale+shift,
                origin=shift,normal=q@np.array((0,0,1)),gravity=q@np.array((0,0,-9.81)),tolerance=1e-6*scale)
            self.assertEqual(result['status'],'INSIDE_SUPPORT');self.assertAlmostEqual(result['margin']/scale,.8)

    def test_contact_input_order_and_duplicates(self):
        pts=sm.patch_vertices((0,0,0),(0,0,1),2,4,.3)
        result=self.analyze(points=pts)
        for other in (pts[::-1],np.tile(pts,(3,1)),np.concatenate((pts,[[0,0,0]]))):
            current=self.analyze(points=other);self.assertAlmostEqual(current['margin'],result['margin']);self.assertEqual(current['status'],result['status'])

    def test_invalid_plane_patch_and_points(self):
        with self.assertRaises(ValueError):self.analyze(normal=(0,0,0))
        with self.assertRaises(ValueError):self.analyze(points=[[0,0,.1]])
        with self.assertRaises(ValueError):self.analyze(points=[[0,math.nan,0]])
        with self.assertRaises(ValueError):self.analyze(tolerance=-1)
        with self.assertRaises(ValueError):sm.patch_vertices((0,0,0),(0,0,1),-1,1,0)

if __name__=='__main__':unittest.main()
