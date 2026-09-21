"""Fail-closed contract checks for the native-display v20 repair."""
from pathlib import Path
import importlib.util
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
TRAIN = ROOT / "training" / "b4artists_ml"
RESULTS = TRAIN / "results"


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


class ReviewDirectedV20Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.protocol = read(TRAIN / "procedural_vertical_slice_protocol_v20.json")
        cls.summary = read(RESULTS / "procedural-vertical-slice-v20-final" / "summary.json")
        cls.focused = read(RESULTS / "procedural-vertical-slice-v20-focused.json")
        cls.review = read(
            RESULTS / "review-directed-followup-reviewer-v4" /
            "human-review-summary-v4-display-audited.json"
        )

    def test_frozen_matrix_and_learning_boundary(self):
        self.assertEqual(self.protocol["schema"], "procedural-vertical-slice-v20")
        self.assertTrue(self.protocol["frozen_before_results"])
        self.assertEqual(len(self.protocol["case_matrix"]), 16)
        self.assertEqual(
            self.protocol["full_body_shaping"]["preserve_exact_cases"],
            ["boneforge/land", "rigify_basic/land"],
        )
        self.assertFalse(self.protocol["learned_bend_prior"]["temporal_motion_model"])
        self.assertFalse(self.protocol["learned_bend_prior"]["promotion_authorized"])

    def test_v4_review_is_used_only_for_qualified_relative_pose_feedback(self):
        self.assertTrue(self.review["relative_pose_feedback_qualified"])
        self.assertFalse(self.review["display_representation_qualified"])
        self.assertFalse(self.review["global_motion_feedback_qualified"])
        self.assertFalse(self.review["jump_height_feedback_qualified"])
        self.assertFalse(self.review["production_acceptance_qualified"])
        self.assertFalse(self.review["training_authorized"])
        self.assertFalse(self.review["model_promotion_authorized"])

    def test_final_matrix_and_focused_receipt_pass_without_widening_claims(self):
        self.assertTrue(self.summary["complete"])
        self.assertEqual((self.summary["passed"], self.summary["cases"]), (16, 16))
        self.assertTrue(self.focused["complete"])
        self.assertEqual((self.focused["passed"], self.focused["expected"]), (16, 16))
        boundary = self.focused["claim_boundary"]
        self.assertTrue(boundary["deterministic_review_directed_gates_pass"])
        self.assertTrue(boundary["native_display_motion_validated"])
        self.assertTrue(boundary["accepted_landings_authoring_preserved"])
        self.assertFalse(boundary["human_visual_improvement_verified"])
        self.assertFalse(boundary["temporal_model_trained"])
        self.assertFalse(boundary["model_promotion_permitted"])
        self.assertFalse(boundary["cascadeur_connector_activated"])
        self.assertFalse(boundary["full_goal_complete"])

    def test_historical_checker_fails_closed_after_runtime_evolves(self):
        path = TRAIN / "check_review_directed_vertical_slice_v20.py"
        spec = importlib.util.spec_from_file_location("check_v20", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with self.assertRaisesRegex(ValueError, "Runtime changed since case generation"):
            module.validate()


if __name__ == "__main__":
    unittest.main()
