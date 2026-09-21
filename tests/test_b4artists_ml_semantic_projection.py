"""Actual ancestry, known-only initialization and physical projection checks."""
from pathlib import Path
import sys,unittest,copy
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'training/b4artists_ml')]
import numpy as np
from bvh_data import parse_bvh
from semantic_motion_data import from_bvh,window
from sequence_data import full_motion,known_window
from sequence_kinematics import forward
from temporal_data import rotation6
import semantic_projection as projection


def fixture():
    src=parse_bvh((ROOT/'training/b4artists_ml/cache/07_01.bvh').read_text())
    sem=window(from_bvh(src),2,10,context=True);motion=full_motion(src)
    known=known_window(motion,2,10,sem['t'],True)
    sem['projection_initial']=known['baseline'];sem['offsets']=motion.offsets
    return sem,(motion.names,motion.parents,motion.semantic)


class SemanticProjectionTests(unittest.TestCase):
    def test_known_endpoints_and_true_physical_lengths(self):
        w,skeleton=fixture();out,metrics=projection.project_windows([w],[w['hermite']],skeleton,dict(steps=8))
        np.testing.assert_allclose(out[0][[0,-1]],w['target'][[0,-1]],atol=1e-12)
        self.assertLess(metrics['true_edge_length_max'],1e-12)
    def test_hidden_labels_never_enter_projection(self):
        w,skeleton=fixture();a,_=projection.project_windows([w],[w['linear']],skeleton,dict(steps=8))
        w['target'][:]=np.nan;w['target_local']=np.full_like(w['projection_initial'],np.nan)
        b,_=projection.project_windows([w],[w['linear']],skeleton,dict(steps=8))
        np.testing.assert_array_equal(a[0],b[0])
    def test_attainable_proposal_reduces_error_and_keeps_root(self):
        w,skeleton=fixture();initial=w['projection_initial'];p,r,_=forward(initial,w['offsets'],skeleton[1]);desired=p[:,skeleton[2]].copy()
        desired[1:-1,7,0]+=.02;rots=r[:,skeleton[2]];ends=(w['t']==0)|(w['t']==1)
        actual,rotation,metrics=projection.project(initial,w['offsets'],skeleton[1],skeleton[2],desired,rots,ends)
        self.assertLess(np.linalg.norm(actual-desired),np.linalg.norm(p[:,skeleton[2]]-desired))
        np.testing.assert_allclose(actual[:,0],desired[:,0],atol=1e-14)
        for j in (0,4,7,10,13,16):np.testing.assert_allclose(rotation[:,j],rots[:,j],atol=1e-12)
    def test_batch_order_and_size_do_not_change_projection(self):
        w,skeleton=fixture();a,_=projection.project_windows([w],[w['linear']],skeleton,dict(steps=8))
        b,_=projection.project_windows([w,w],[w['hermite'],w['linear']],skeleton,dict(steps=8))
        np.testing.assert_allclose(a[0],b[1],atol=1e-12)
    def test_invalid_proposals_fail_without_mutating_inputs(self):
        w,skeleton=fixture();before=w['projection_initial'].copy();bad=w['linear'].copy();bad[3,2]=np.nan
        with self.assertRaises(ValueError):projection.project_windows([w],[bad],skeleton,dict(steps=8))
        np.testing.assert_array_equal(w['projection_initial'],before)
