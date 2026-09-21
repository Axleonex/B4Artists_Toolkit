"""Deterministic angular-momentum math checks."""
from pathlib import Path
import sys,math,unittest
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from b4artists_ml import angular_math as am


class AngularMathTests(unittest.TestCase):
    def synthetic(self):
        times=np.linspace(0.,1.,41);base=np.array(((-.7,0,0),(.7,0,0),(0,-.4,.2),(0,.4,-.2)))
        rows=[]
        for t in times:
            angle=1.1*t*t
            # Internal arm motion makes the source angular momentum nonconstant.
            shape=base.copy();shape[2,1]+=.28*math.sin(math.pi*t);shape[3,1]-=.18*math.sin(math.pi*t)
            rows.append((am.rotation_matrix(np.array((0,0,angle)))@shape.T).T+np.array((2*t,0,3*t-4.9*t*t)))
        return np.asarray(rows),np.array((3.,3.,1.,1.)),times

    def rigid_segments(self):
        times=np.linspace(0.,1.,41);starts=[];ends=[];hints=[]
        for t in times:
            theta=.8*t
            starts.append(((-1,0,0),(0,0,0),(1,0,0)))
            ends.append(((-1,1,0),(0,1,0),(1,1,0)))
            hints.append(tuple((am.rotation_matrix(np.array((0,theta*(i+1),0)))@np.array((1.,0.,0.))).tolist() for i in range(3)))
        starts=np.asarray(starts,dtype=float);ends=np.asarray(ends,dtype=float);hints=np.asarray(hints,dtype=float)
        return starts,ends,am.segment_orientations(starts,ends,hints),am.segment_principal_inertia(starts,ends,[.2,.25,.3]),times

    def test_rotation_roundtrip_and_validation(self):
        vectors=(np.zeros(3),np.array((.2,-.3,.4)),np.array((math.pi-.0001,0,0)))
        for vector in vectors:
            np.testing.assert_allclose(am.rotation_matrix(am.rotation_vector(am.rotation_matrix(vector))),am.rotation_matrix(vector),atol=2e-6)
        matrices=np.asarray([am.rotation_matrix(v) for v in vectors]);np.testing.assert_allclose(am._rotation_vectors(matrices),[am.rotation_vector(v) for v in matrices],atol=1e-12)
        with self.assertRaises(ValueError):am.rotation_matrix([1,2])
        with self.assertRaises(ValueError):am.rotation_vector(np.zeros((3,3)))

    def test_measure_is_translation_invariant_and_scales_mass(self):
        centers,weights,times=self.synthetic();a=am.measure(centers,weights,times)
        b=am.measure(centers+np.array((90.,-12.,4.)),weights*1e8,times)
        np.testing.assert_allclose(a['momentum'],b['momentum'],atol=2e-12)
        np.testing.assert_allclose(a['inertia'],b['inertia'],atol=2e-12)

    def test_finite_segments_measure_axial_spin_without_orbital_motion(self):
        starts,ends,orientations,moments,times=self.rigid_segments();centers=(starts+ends)*.5
        data=am.measure(centers,[1,2,3],times,orientations,moments)
        np.testing.assert_allclose(data['orbital_momentum'],0,atol=1e-12)
        self.assertGreater(np.linalg.norm(data['spin_momentum'].mean(axis=0)),.01)
        self.assertLess(am.variation(data['spin_momentum'])[0],1e-10)
        self.assertEqual(data['model'],'rigid_segments')

    def test_segment_frames_and_inertia_are_proper_and_scale_quadratically(self):
        starts,ends,frames,moments,_=self.rigid_segments()
        expected=np.broadcast_to(np.eye(3),frames.shape)
        np.testing.assert_allclose(np.einsum('tnji,tnjk->tnik',frames,frames),expected,atol=1e-12)
        np.testing.assert_allclose(np.linalg.det(frames),1,atol=1e-12)
        scaled=am.segment_principal_inertia(starts*7,ends*7,[.2,.25,.3])
        np.testing.assert_allclose(scaled,moments*49,atol=1e-12)

    def test_refinement_preserves_boundary_poses_and_reduces_variation(self):
        centers,weights,times=self.synthetic();result=am.refine(centers,weights,times)
        np.testing.assert_allclose(result['rotations'][0],np.eye(3),atol=1e-12)
        np.testing.assert_allclose(result['rotations'][-1],np.eye(3),atol=3e-6)
        self.assertLessEqual(result['peak_angle'],math.radians(35)+1e-8)
        self.assertLess(result['after_variation'],result['before_variation']*.8)
        self.assertGreater(result['effective_strength'],0)

    def test_zero_strength_is_identity_and_invalid_inputs_fail(self):
        centers,weights,times=self.synthetic();result=am.refine(centers,weights,times,0)
        np.testing.assert_allclose(result['rotations'],np.repeat(np.eye(3)[None],len(times),axis=0),atol=1e-12)
        for bad in (-.1,1.1,float('nan')):
            with self.assertRaises(ValueError):am.refine(centers,weights,times,bad)
        with self.assertRaises(ValueError):am.measure(centers[:3],weights,times[:3])
        with self.assertRaises(ValueError):am.variation([[1,2]])
        starts,ends,orientations,moments,clock=self.rigid_segments();segment_centers=(starts+ends)*.5
        with self.assertRaises(ValueError):am.measure(segment_centers,[1,1,1],clock,orientations,None)
        with self.assertRaises(ValueError):am.measure(segment_centers,[1,1,1],clock,orientations[:,:,:,:2],moments)
        with self.assertRaises(ValueError):am.segment_principal_inertia(starts,ends,[0,.2,.2])
        with self.assertRaises(ValueError):am.segment_orientations(starts,ends,ends-starts)

    def test_variable_timing_large_origin_and_partial_strength(self):
        centers,weights,times=self.synthetic();times=times**1.3
        moved=centers+np.array((1e6,-2e6,3e6));full=am.refine(moved,weights,times);half=am.refine(moved,weights,times,.5)
        self.assertLessEqual(full['after_variation'],full['before_variation']+1e-10)
        self.assertLessEqual(half['after_variation'],half['before_variation']+1e-10)
        self.assertLessEqual(half['peak_angle'],full['peak_angle']*.51+1e-8)


if __name__=='__main__':unittest.main()
