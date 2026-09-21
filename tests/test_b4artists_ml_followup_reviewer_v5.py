"""Integrity checks for the corrected native-display v5 review packet."""
from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "training" / "b4artists_ml" / "results" / "review-directed-followup-reviewer-v5"


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


class FollowupReviewerV5Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = read(BUILD / "manifest.json")
        cls.data = read(BUILD / "review-data.json")
        cls.extracts = [read(path) for path in sorted((BUILD / "extracted").glob("*.json"))]

    def test_manifest_and_extracts_require_native_display(self):
        self.assertTrue(self.manifest["complete"])
        self.assertEqual(self.manifest["cases"], 8)
        self.assertTrue(self.manifest["native_display_validated"])
        self.assertLessEqual(self.manifest["maximum_native_instance_error"], 2e-6)
        self.assertEqual(len(self.extracts), 16)
        for value in self.extracts:
            self.assertTrue(value["complete"])
            self.assertTrue(value["native_display_validated"])
            self.assertEqual(value["display_representation"], "native depsgraph armature instance")
            self.assertLessEqual(value["maximum_native_instance_error"], 2e-6)
            self.assertEqual((len(value["samples"]), len(value["samples"][0])), (49, 17))

    def test_packet_compares_v20_to_reviewed_v19_without_authorizing_learning(self):
        self.assertEqual(self.data["schema"], "b4ml-review-directed-followup-review-data-v5")
        self.assertEqual(len(self.data["cases"]), 8)
        self.assertTrue(self.data["native_display_validated"])
        self.assertFalse(self.data["training_authorized"])
        self.assertFalse(self.data["model_promotion_authorized"])
        self.assertFalse(self.data["full_goal_complete"])
        for case in self.data["cases"]:
            variants = {identity["variant"] for identity in case["reveal"].values()}
            self.assertEqual(variants, {"candidate", "baseline"})
            candidate = next(identity for identity in case["reveal"].values()
                             if identity["variant"] == "candidate")
            baseline = next(identity for identity in case["reveal"].values()
                            if identity["variant"] == "baseline")
            self.assertIn("procedural-vertical-slice-v20-final", candidate["blend_path"])
            self.assertIn("procedural-vertical-slice-v19-repair2", baseline["blend_path"])

    def test_native_jump_motion_is_visible_in_every_jump_comparison(self):
        jump_cases = [case for case in self.data["cases"] if case["task"] == "jump"]
        self.assertEqual(len(jump_cases), 4)
        for case in jump_cases:
            for label, method in case["methods"].items():
                pelvis_z = [sample[0][2] for sample in method["samples"]]
                rise = max(pelvis_z) - max(pelvis_z[0], pelvis_z[-1])
                self.assertGreater(rise, 0.2, f"{case['id']}/{label}")


if __name__ == "__main__":
    unittest.main()
