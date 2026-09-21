"""Fail-closed contract checks for the corrected-review-directed v19 candidate."""
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
TRAIN = ROOT / "training/b4artists_ml"
PROTOCOL = TRAIN / "procedural_vertical_slice_protocol_v19.json"
BUILDER = TRAIN / "build_procedural_vertical_slice_v19.py"


class ReviewDirectedV19CandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.protocol = json.loads(PROTOCOL.read_text(encoding="utf-8"))
        spec = importlib.util.spec_from_file_location(
            "review_import_v3", TRAIN / "import_followup_review_v3.py"
        )
        cls.review = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.review)

    def test_review_failures_drive_scope_and_accepted_landings_are_preserved(self):
        summary = self.review.validate()
        accepted = {case["id"] for case in summary["cases"] if case["candidate_acceptable"]}
        shaping = self.protocol["full_body_shaping"]
        self.assertGreaterEqual(shaping["solve_iterations"], 8)
        self.assertLessEqual(shaping["solve_iterations"], 60)
        self.assertEqual(set(shaping["preserve_exact_cases"]), accepted)
        self.assertEqual(accepted, {"boneforge/land", "rigify_basic/land"})
        for case in summary["cases"]:
            if case["candidate_acceptable"]:
                continue
            task = case["id"].split("/", 1)[1]
            self.assertIn(task, shaping["tasks"])

    def test_jump_has_distinct_anticipation_flight_impact_and_followthrough(self):
        jump = self.protocol["tasks"]["jump"]
        frames = {pose["label"]: pose["frame"] for pose in jump["poses"]}
        labels = [
            "neutral", "compression", "takeoff", "flight-end", "pre-impact", "impact",
            "absorb crouch", "follow-through", "recover",
        ]
        self.assertEqual(list(frames), labels)
        self.assertEqual([frames[label] for label in labels], sorted(frames.values()))
        self.assertEqual(frames["flight-end"], frames["pre-impact"] - 2)
        self.assertEqual(jump["flights"], [[frames["takeoff"], frames["flight-end"]]])
        self.assertEqual(jump["landing_contact_blend_frames"], 2)
        self.assertEqual({row[1] for row in jump["contacts"] if row[1] > 1}, {frames["impact"]})
        shaping = self.protocol["full_body_shaping"]["tasks"]["jump"]
        for label in labels[1:-1]:
            self.assertIn("torso", shaping[label])
            self.assertIn("arm-L", shaping[label]["limbs"])
            self.assertIn("arm-R", shaping[label]["limbs"])

    def test_run_is_not_long_flight_short_support_and_has_opposed_arms(self):
        run = self.protocol["tasks"]["run"]
        for _limb, start, end in run["contacts"]:
            self.assertGreaterEqual(end - start, 5)
        for start, end in run["flights"]:
            self.assertLessEqual(end - start, 5)
        shaping = self.protocol["full_body_shaping"]["tasks"]["run"]
        for pose in run["poses"]:
            recipe = shaping[pose["label"]]
            left = recipe["limbs"]["arm-L"][1] - pose["pelvis"][1]
            right = recipe["limbs"]["arm-R"][1] - pose["pelvis"][1]
            self.assertLess(left * right, 0)
            self.assertIn("torso", recipe)

    def test_imported_elbow_hint_and_fail_closed_learning_boundary(self):
        imported = self.protocol["profile_overrides"]["imported_unity"]["pole_hints"]
        self.assertGreater(imported["arm-L"][1], 0)
        self.assertGreater(imported["arm-R"][1], 0)
        self.assertFalse(self.protocol["learned_bend_prior"]["temporal_motion_model"])
        self.assertFalse(self.protocol["learned_bend_prior"]["promotion_authorized"])

    def test_builder_uses_staged_product_coupling_and_new_immutable_output(self):
        text = BUILDER.read_text(encoding="utf-8")
        self.assertIn("body_preview.begin(obj, scene)", text)
        self.assertIn("body_preview.solve(obj, iterations=", text)
        self.assertIn("body_preview.finish(obj, scene, True)", text)
        self.assertIn("procedural-vertical-slice-v19", text)
        self.assertNotIn('"procedural-vertical-slice-v18"', text)


if __name__ == "__main__":
    unittest.main()
