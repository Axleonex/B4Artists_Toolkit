from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
TRAIN = ROOT / "training" / "b4artists_ml"


class ReviewDirectedV26ProtocolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.protocol = json.loads(
            (TRAIN / "procedural_vertical_slice_protocol_v26.json").read_text(encoding="utf-8")
        )

    def test_run_priority_pelvis_has_constant_forward_speed(self):
        poses = self.protocol["tasks"]["run"]["poses"]
        speeds = []
        for first, second in zip(poses, poses[1:]):
            speeds.append(
                (second["pelvis"][1] - first["pelvis"][1])
                / (second["frame"] - first["frame"])
            )
        self.assertTrue(all(abs(value + 0.018) < 1e-9 for value in speeds))

    def test_run_arm_swing_is_bent_symmetric_and_gradual(self):
        poses = {row["label"]: row for row in self.protocol["tasks"]["run"]["poses"]}
        shaping = self.protocol["full_body_shaping"]["tasks"]["run"]
        relative = []
        for label, recipe in shaping.items():
            pelvis_y = poses[label]["pelvis"][1]
            left = recipe["limbs"]["arm-L"]
            right = recipe["limbs"]["arm-R"]
            self.assertEqual(left[2], -0.02)
            self.assertEqual(right[2], -0.02)
            self.assertAlmostEqual(left[1] - pelvis_y, -(right[1] - pelvis_y))
            relative.append(left[1] - pelvis_y)
        self.assertAlmostEqual(min(relative), -0.05)
        self.assertAlmostEqual(max(relative), 0.05)
        self.assertEqual(relative[4], 0.0)
        self.assertEqual(relative[8], 0.0)

    def test_accepted_jump_and_fail_closed_authority_are_preserved(self):
        source = json.loads(
            (TRAIN / "procedural_vertical_slice_protocol_v25.json").read_text(encoding="utf-8")
        )
        self.assertEqual(self.protocol["tasks"]["jump"], source["tasks"]["jump"])
        self.assertEqual(
            self.protocol["full_body_shaping"]["tasks"]["jump"],
            source["full_body_shaping"]["tasks"]["jump"],
        )
        self.assertFalse(self.protocol["training_authorized"])
        self.assertFalse(self.protocol["model_promotion_authorized"])
        self.assertFalse(self.protocol["cascadeur_connector_authorized"])


if __name__ == "__main__":
    unittest.main()
