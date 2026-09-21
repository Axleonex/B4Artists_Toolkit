"""Contract tests for the review-directed v14 bend-prior experiment."""
from pathlib import Path
import ast
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
TRAIN = ROOT / "training" / "b4artists_ml"
BUILDER = TRAIN / "build_procedural_vertical_slice_v14.py"
PROTOCOL = TRAIN / "procedural_vertical_slice_protocol_v14.json"


class ProceduralVerticalSliceV14Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = BUILDER.read_text(encoding="utf-8")
        cls.protocol = json.loads(PROTOCOL.read_text(encoding="utf-8"))

    def test_builder_and_protocol_are_separately_versioned(self):
        ast.parse(self.source, filename=str(BUILDER))
        self.assertEqual(self.protocol["schema"], "procedural-vertical-slice-v14")
        self.assertEqual(self.protocol["supersedes"], "procedural_vertical_slice_protocol_v13.json")
        self.assertIn("procedural-vertical-slice-v14", self.source)
        self.assertNotIn('PROTOCOL_PATH = Path(__file__).with_name("procedural_vertical_slice_protocol_v13.json")', self.source)

    def test_local_bend_prior_is_explicitly_bounded_and_fail_closed(self):
        prior = self.protocol["learned_bend_prior"]
        self.assertTrue(prior["enabled"])
        self.assertEqual(prior["strength"], 1.0)
        self.assertFalse(prior["temporal_motion_model"])
        self.assertFalse(prior["promotion_authorized"])
        self.assertIn("does not satisfy learned inbetweening", self.protocol["interpretation"]["learned_motion"])

    def test_builder_enables_every_pose_target_and_reports_the_scope(self):
        self.assertIn("pose_target.learn_bend = True", self.source)
        self.assertIn("enable_local_learned_bend_prior", self.source)
        self.assertIn('learned_scope="bundled local limb-bend direction prior only"', self.source)
        self.assertIn("temporal_learned_motion=False", self.source)
        self.assertIn("temporal_learned_motion_promoted=False", self.source)


if __name__ == "__main__":
    unittest.main()
