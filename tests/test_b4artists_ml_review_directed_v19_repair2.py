"""Fail-closed scope checks for the BoneForge-only v19 repair-2."""
from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
TRAIN = ROOT / "training" / "b4artists_ml"


class ReviewDirectedV19Repair2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = json.loads((
            TRAIN / "procedural_vertical_slice_protocol_v19.json"
        ).read_text(encoding="utf-8"))
        cls.repair = json.loads((
            TRAIN / "procedural_vertical_slice_protocol_v19_repair2.json"
        ).read_text(encoding="utf-8"))

    def test_motion_gates_and_case_contract_are_unchanged(self):
        for key in (
            "case_matrix", "tasks", "full_body_shaping", "automated_gates",
            "review_directed_gates", "learned_bend_prior",
        ):
            self.assertEqual(self.repair[key], self.base[key], key)

    def test_only_boneforge_contact_blend_is_overridden(self):
        base_overrides = self.base["profile_overrides"]
        repair_overrides = self.repair["profile_overrides"]
        self.assertEqual(
            repair_overrides["imported_unity"], base_overrides["imported_unity"]
        )
        boneforge = dict(repair_overrides["boneforge"])
        self.assertEqual(boneforge.pop("landing_contact_blend_frames"), 0)
        self.assertEqual(boneforge, base_overrides["boneforge"])
        self.assertEqual(self.base["tasks"]["jump"]["landing_contact_blend_frames"], 2)

    def test_builder_and_protocol_keep_learning_fail_closed(self):
        text = (TRAIN / "build_procedural_vertical_slice_v19_repair2.py").read_text(
            encoding="utf-8"
        )
        self.assertIn('profile_override.get(\n                    "landing_contact_blend_frames"', text)
        self.assertIn("procedural-vertical-slice-v19-repair2", text)
        self.assertFalse(self.repair["learned_bend_prior"]["temporal_motion_model"])
        self.assertFalse(self.repair["learned_bend_prior"]["promotion_authorized"])


if __name__ == "__main__":
    unittest.main()
