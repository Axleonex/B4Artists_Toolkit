"""Contract tests for review-directed reach and landing corrections in v15."""
from pathlib import Path
import ast
import hashlib
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
TRAIN = ROOT / "training" / "b4artists_ml"
BUILDER = TRAIN / "build_procedural_vertical_slice_v15.py"
PROTOCOL = TRAIN / "procedural_vertical_slice_protocol_v15.json"
RECEIPT = TRAIN / "results" / "procedural-vertical-slice-v15-focused.json"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class ProceduralVerticalSliceV15Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = BUILDER.read_text(encoding="utf-8")
        cls.protocol = json.loads(PROTOCOL.read_text(encoding="utf-8"))

    def test_candidate_is_separately_versioned(self):
        ast.parse(self.source, filename=str(BUILDER))
        self.assertEqual(self.protocol["schema"], "procedural-vertical-slice-v15")
        self.assertEqual(self.protocol["supersedes"], "procedural_vertical_slice_protocol_v14.json")
        self.assertIn("procedural-vertical-slice-v15", self.source)

    def test_reach_moves_primarily_forward(self):
        reach = self.protocol["tasks"]["reach"]["poses"]
        for row in reach[1:3]:
            target = row["limbs"]["arm-L"]
            self.assertGreater(abs(target[1]), abs(target[0]) * 3)
            self.assertLess(target[1], 0)

    def test_landing_impacts_before_deeper_absorption(self):
        land = self.protocol["tasks"]["land"]
        impact, absorb = land["poses"][1:3]
        self.assertEqual(impact["frame"], land["contacts"][0][1])
        self.assertEqual(impact["label"], "impact")
        self.assertEqual(absorb["label"], "absorb crouch")
        self.assertLess(absorb["pelvis"][2], impact["pelvis"][2])
        self.assertEqual(land["poses"][0]["limbs"], {})
        self.assertIn("No midair knee bend is introduced", self.protocol["revision_reason"])

    def test_bend_prior_remains_bounded(self):
        prior = self.protocol["learned_bend_prior"]
        self.assertTrue(prior["enabled"])
        self.assertFalse(prior["temporal_motion_model"])
        self.assertFalse(prior["promotion_authorized"])

    def test_focused_native_receipt_is_bound_and_non_promotional(self):
        receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
        self.assertEqual(receipt["status"], "PASS_FOCUSED_DETERMINISTIC")
        self.assertEqual(receipt["passed"], 8)
        self.assertEqual(receipt["expected"], 8)
        self.assertEqual(receipt["protocol_sha256"], sha(PROTOCOL))
        self.assertFalse(receipt["claim_boundary"]["human_visual_improvement_verified"])
        self.assertFalse(receipt["claim_boundary"]["temporal_model_trained"])
        self.assertFalse(receipt["claim_boundary"]["model_promotion_permitted"])
        self.assertFalse(receipt["claim_boundary"]["cascadeur_parity_verified"])
        self.assertFalse(receipt["claim_boundary"]["full_goal_complete"])


if __name__ == "__main__":
    unittest.main()
