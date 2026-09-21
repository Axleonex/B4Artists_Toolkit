from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
TRAIN = ROOT / "training" / "b4artists_ml"


class ReviewDirectedV28ProtocolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.protocol = json.loads(
            (TRAIN / "procedural_vertical_slice_protocol_v28.json").read_text(encoding="utf-8")
        )

    def test_landing_arm_targets_do_not_reverse(self):
        poses = {row["label"]: row for row in self.protocol["tasks"]["run"]["poses"]}
        shaping = self.protocol["full_body_shaping"]["tasks"]["run"]
        relative = {
            label: recipe["limbs"]["arm-L"][1] - poses[label]["pelvis"][1]
            for label, recipe in shaping.items()
        }
        self.assertAlmostEqual(relative["right pre-land"], relative["right landing"])
        self.assertAlmostEqual(relative["left pre-land"], relative["left landing"])
        self.assertAlmostEqual(min(relative.values()), -0.02)
        self.assertAlmostEqual(max(relative.values()), 0.02)

    def test_only_enforced_forward_step_gate_remains(self):
        gates = self.protocol["review_directed_gates"]
        self.assertNotIn("run_forward_step_peak_ratio", gates)
        self.assertEqual(gates["run_pelvis_forward_step_peak_ratio"], 2.0)

    def test_failed_host_evidence_and_authority_are_preserved(self):
        revision = self.protocol["development_revision"]
        self.assertEqual(revision["source"], "procedural-vertical-slice-v27-smoke-boneforge-run")
        self.assertGreater(revision["measured_p95_rad_s2"], revision["required_max_rad_s2"])
        self.assertFalse(self.protocol["training_authorized"])
        self.assertFalse(self.protocol["model_promotion_authorized"])
        self.assertFalse(self.protocol["cascadeur_connector_authorized"])


if __name__ == "__main__":
    unittest.main()
