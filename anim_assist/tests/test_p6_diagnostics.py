"""Boundary regressions for the actual pure timing-cluster detector."""

import importlib.util
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("aa_p6_diagnostics_regression", ROOT / "core/p6_diagnostics.py")
diagnostics = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = diagnostics
spec.loader.exec_module(diagnostics)


def curves(*frame_lists):
    return [SimpleNamespace(keyframe_points=[SimpleNamespace(co=SimpleNamespace(x=float(frame)))
                                             for frame in frames]) for frames in frame_lists]


class ClusterRadiusTests(unittest.TestCase):
    def test_radius_is_inclusive_for_adjacent_gaps(self):
        source = curves([0, 3])
        self.assertEqual(diagnostics.detect_key_clusters(source, radius=2), [])
        result = diagnostics.detect_key_clusters(source, radius=3)
        self.assertEqual([cluster.frames for cluster in result], [[0.0, 3.0]])
        self.assertEqual([key.co.x for key in source[0].keyframe_points], [0.0, 3.0])

    def test_transitive_cluster_can_span_more_than_radius(self):
        result = diagnostics.detect_key_clusters(curves([4, 0], [2, 2]), radius=2)
        self.assertEqual([cluster.frames for cluster in result], [[0.0, 2.0, 4.0]])
        self.assertEqual(result[0].size, 3)
        self.assertEqual(result[0].spread, 4.0)
        self.assertGreater(result[0].spread, 2)

    def test_duplicate_keys_at_one_time_do_not_form_cluster(self):
        self.assertEqual(diagnostics.detect_key_clusters(curves([2, 2], [2]), radius=2), [])


if __name__ == "__main__":
    unittest.main()
