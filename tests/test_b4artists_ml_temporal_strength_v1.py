"""Host-independent contract for procedural temporal proposal strength."""
from pathlib import Path
import sys
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from b4artists_ml.temporal_math import (  # noqa: E402
    blend_proposal, validate_proposal_strength)


class TemporalStrengthTests(unittest.TestCase):
    def setUp(self):
        self.base_points = np.zeros((3, 17, 3), dtype=float)
        self.proposal_points = np.ones((3, 17, 3), dtype=float)
        self.base_rotations = np.broadcast_to(np.eye(3), (3, 17, 3, 3)).copy()
        quarter_turn = np.array(((0., -1., 0.), (1., 0., 0.), (0., 0., 1.)))
        self.proposal_rotations = np.broadcast_to(quarter_turn, (3, 17, 3, 3)).copy()

    def test_zero_is_exact_baseline_and_one_is_exact_proposal(self):
        points, rotations = blend_proposal(
            self.base_points, self.base_rotations,
            self.proposal_points, self.proposal_rotations, 0.)
        np.testing.assert_array_equal(points, self.base_points)
        np.testing.assert_array_equal(rotations, self.base_rotations)
        points, rotations = blend_proposal(
            self.base_points, self.base_rotations,
            self.proposal_points, self.proposal_rotations, 1.)
        np.testing.assert_array_equal(points, self.proposal_points)
        np.testing.assert_array_equal(rotations, self.proposal_rotations)

    def test_fractional_strength_blends_positions_and_preserves_rotation_validity(self):
        points, rotations = blend_proposal(
            self.base_points, self.base_rotations,
            self.proposal_points, self.proposal_rotations, .5)
        np.testing.assert_allclose(points, .5)
        np.testing.assert_allclose(
            np.einsum('...ji,...jk->...ik', rotations, rotations),
            np.broadcast_to(np.eye(3), (3, 17, 3, 3)), atol=1e-12)
        np.testing.assert_allclose(np.linalg.det(rotations), 1., atol=1e-12)

    def test_invalid_strengths_fail_closed(self):
        for value in (True, -1e-6, 1.000001, float('nan'), float('inf'), 'half'):
            with self.assertRaises(ValueError):
                validate_proposal_strength(value)

    def test_invalid_arrays_fail_closed(self):
        with self.assertRaises(ValueError):
            blend_proposal(
                self.base_points[:, :16], self.base_rotations,
                self.proposal_points, self.proposal_rotations, .5)


if __name__ == '__main__':
    unittest.main()
