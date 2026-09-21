"""Shared temporal input, target, coordinate and split-isolation tests."""
from pathlib import Path
import sys,unittest,copy,json,hashlib
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'training/b4artists_ml'),str(ROOT/'tests')]
import numpy as np
import semantic_motion_data as data
from rig_observations import encode
from temporal_data import rotation_matrix,quat_matrix,rotation6


def sequence():
    from test_b4artists_ml_rig_observations import fixture
    rest,rest_r,_,_=fixture();n=14;t=np.arange(n)[:,None,None]
    points=rest[None]+np.array([.02,.005,.01])[None,None]*t
    points[:,7,1]+=.03*np.sin(np.arange(n)*.3)
    rolls=quat_matrix(np.random.default_rng(12).normal(size=(17,4)));rest_r=rest_r@rolls
    q=np.broadcast_to(np.eye(3),(n,17,3,3)).copy()
    q[:,:,0,0]=np.cos(t[:,:,0]*.01);q[:,:,0,1]=-np.sin(t[:,:,0]*.01)
    q[:,:,1,0]=np.sin(t[:,:,0]*.01);q[:,:,1,1]=np.cos(t[:,:,0]*.01)
    return data.SemanticSequence(rest,rest_r,points,q@rest_r,np.arange(1,n+1),1/30)


class SemanticMotionTests(unittest.TestCase):
    def test_exact_shared_encoder_and_endpoint_targets(self):
        s=sequence();w=data.window(s,2,10);o=w['observations'];indices=[2,10,1,11]
        expected=encode(s.rest,s.rest_rotations,s.positions[indices],s.rotations[indices],duration=8*s.dt,dt=s.dt,context=True)
        np.testing.assert_array_equal(o.features(),expected.features());self.assertEqual(w['x'].shape,(667,))
        np.testing.assert_allclose(w['linear'][[0,-1]],w['target'][[0,-1]],atol=1e-14)
        np.testing.assert_allclose(w['hermite'][[0,-1]],w['target'][[0,-1]],atol=1e-14)

    def test_hidden_labels_never_enter_observations_or_baselines(self):
        s=sequence();a=data.window(s,2,10);s.positions[3:10]+=.7;s.rotations[3:10]=quat_matrix(np.array([.7,.2,-.1,.3]))@s.rotations[3:10]
        b=data.window(s,2,10)
        for name in ('x','linear','hermite'):np.testing.assert_array_equal(a[name],b[name])
        self.assertGreater(np.linalg.norm(a['target']-b['target']),1.)

    def test_missing_context_reads_only_two_poses(self):
        s=sequence();a=data.window(s,0,13,context=False)
        np.testing.assert_array_equal(a['linear'],a['hermite']);self.assertFalse(a['observations'].context)
        with self.assertRaisesRegex(ValueError,'Outside-gap'):data.window(s,0,13,context=True)
        a=data.window(s,2,10,context=False);s.positions[[1,11]]+=91
        np.testing.assert_array_equal(a['x'],data.window(s,2,10,context=False)['x'])

    def test_targets_decode_to_original_world_poses_and_rotations(self):
        s=sequence();w=data.window(s,2,10);o=w['observations'];packed=w['target'].reshape(-1,17,9)
        rotations,bad=rotation_matrix(packed[...,3:]);self.assertFalse(bad.any())
        np.testing.assert_allclose(o.world_points(packed[...,:3]),s.positions[2:11],atol=1e-13)
        np.testing.assert_allclose(o.world_rotations(rotations),s.rotations[2:11],atol=1e-13)

    def test_global_similarity_and_bone_roll_leave_features_and_labels_invariant(self):
        s=sequence();a=data.window(s,2,10);r=quat_matrix(np.array([.8,.2,-.3,.1]));roll=quat_matrix(np.random.default_rng(4).normal(size=(17,4)))
        transformed=data.SemanticSequence(s.rest@r.T*1.7+8,r@s.rest_rotations@roll,s.positions@r.T*1.7+8,r@s.rotations@roll,s.frames,s.dt)
        b=data.window(transformed,2,10)
        for key in ('x','target','linear','hermite'):np.testing.assert_allclose(a[key],b[key],atol=1e-12)

    def test_procedural_context_changes_interior_without_rewriting_endpoints(self):
        w=data.window(sequence(),2,10)
        self.assertGreater(np.linalg.norm(w['linear'][1:-1]-w['hermite'][1:-1]),1e-5)
        np.testing.assert_array_equal(w['linear'][[0,-1]],w['hermite'][[0,-1]])

    def test_source_hierarchy_targets_match_after_explicit_rotation_calibration(self):
        from bvh_data import parse_bvh
        from sequence_data import full_motion,known_window,target_window
        path=ROOT/'training/b4artists_ml/cache/07_01.bvh';source=parse_bvh(path.read_text());s=data.from_bvh(source);a=data.window(s,2,10)
        full=full_motion(source);known=known_window(full,2,10,a['t'],True)
        _,legacy=target_window(full,np.arange(2,11),known['origin'],known['basis']);v=legacy.reshape(-1,17,9)
        rotations,bad=rotation_matrix(v[...,3:]);self.assertFalse(bad.any())
        corrected=rotations@np.swapaxes(a['observations'].rest_alignment,-1,-2)
        expected=np.concatenate((v[...,:3],rotation6(corrected)),axis=-1).reshape(-1,153)
        np.testing.assert_allclose(a['target'],expected,atol=1e-12)
        self.assertEqual(known['x'].shape,(637,));self.assertNotEqual(known['x'].shape,a['x'].shape)
        self.assertTrue(np.all(a['frame']>0))

    def test_manifest_checksum_and_split_ownership_are_enforced(self):
        root=ROOT/'training/b4artists_ml';manifest=json.loads((root/'results/training_manifest_v4.json').read_text());row=copy.deepcopy(next(r for r in manifest['files'] if r['clip']=='07_01'))
        protocol=dict(seed=4,target_fps=30,gaps=[8],contexts=[False,True],training_windows_per_gap=2,evaluation_windows_per_gap=1)
        rows=data.load_windows(root,dict(files=[row]),'train',protocol);self.assertEqual(len(rows),4);self.assertTrue(all(w['clip']=='07_01' for w in rows))
        with self.assertRaisesRegex(ValueError,'No matching'):data.load_windows(root,dict(files=[row]),'validation',protocol)
        row['sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'checksum'):data.load_windows(root,dict(files=[row]),'train',protocol)

    def test_invalid_indices_and_timing_fail(self):
        s=sequence()
        for a,b in ((True,3),(-1,4),(4,4),(1,99)):
            with self.assertRaises(ValueError):data.observe(s,a,b)
        o=data.observe(s,2,10)
        for indices in ([],[-1],[99],[1.5]):
            with self.assertRaises(ValueError):data.encode_targets(s,indices,o)
