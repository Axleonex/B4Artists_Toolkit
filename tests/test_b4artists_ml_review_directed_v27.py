from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
TRAIN = ROOT / "training" / "b4artists_ml"


class ReviewDirectedV27ProtocolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.protocol = json.loads(
            (TRAIN / "procedural_vertical_slice_protocol_v27.json").read_text(encoding="utf-8")
        )

    def test_arm_swing_retains_phase_through_landing(self):
        poses = {row["label"]: row for row in self.protocol["tasks"]["run"]["poses"]}
        shaping = self.protocol["full_body_shaping"]["tasks"]["run"]
        relative = {
            label: recipe["limbs"]["arm-L"][1] - poses[label]["pelvis"][1]
            for label, recipe in shaping.items()
        }
        self.assertLess(relative["right pre-land"], 0)
        self.assertLess(relative["right landing"], 0)
        self.assertGreater(relative["left pre-land"], 0)
        self.assertGreater(relative["left landing"], 0)
        self.assertAlmostEqual(min(relative.values()), -0.03)
        self.assertAlmostEqual(max(relative.values()), 0.03)

    def test_failed_gate_is_recorded_without_relaxation(self):
        revision = self.protocol["development_revision"]
        self.assertEqual(revision["failed_gate"], "review_run_angular_acceleration")
        self.assertGreater(revision["measured_p95_rad_s2"], revision["required_max_rad_s2"])
        self.assertEqual(
            self.protocol["review_directed_gates"]["run_upper_body_angular_acceleration_p95_rad_s2"],
            18.0,
        )

    def test_authority_remains_closed(self):
        self.assertFalse(self.protocol["training_authorized"])
        self.assertFalse(self.protocol["model_promotion_authorized"])
        self.assertFalse(self.protocol["cascadeur_connector_authorized"])


if __name__ == "__main__":
    unittest.main()
