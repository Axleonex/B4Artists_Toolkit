"""Contract tests for the root-context research candidate."""

from pathlib import Path
import json
import sys
import unittest

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "training" / "b4artists_ml"))

from root_context_model import features  # noqa: E402


class RootContextModelTests(unittest.TestCase):
    def test_feature_schema_is_observation_only_and_dimensioned(self):
        poses = np.zeros((4, 141), dtype=float)
        rotation = np.tile([1., 0., 0., 0., 1., 0.], 23)
        poses[:, 3:] = rotation
        window = {
            "x": np.r_[poses.reshape(-1), np.zeros(69), 0., 0., 1., 1.],
            "environment": np.array([0., 1., 0., 9.81, 1., 1., 0., 0., 0., 0., 0.]),
        }
        result = features([window])
        self.assertEqual(result.shape, (1, 431))
        self.assertTrue(np.isfinite(result).all())

    def test_protocol_keeps_holdout_separate(self):
        protocol = json.loads(
            (ROOT / "training" / "b4artists_ml" / "root_context_protocol_v1.json").read_text()
        )
        self.assertEqual(protocol["selection"].split(";", 1)[-1].strip(), "holdout is never used for candidate selection")
        self.assertTrue(protocol["claim_boundary"]["research_only"])


if __name__ == "__main__":
    unittest.main()
