from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
TRAIN = ROOT / "training" / "b4artists_ml"


class ReviewDirectedV34ProtocolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.protocol = json.loads(
            (TRAIN / "procedural_vertical_slice_protocol_v34.json").read_text(encoding="utf-8")
        )

    def test_retry_changes_control_mapping_not_motion_or_gates(self):
        source = json.loads(
            (TRAIN / "procedural_vertical_slice_protocol_v33.json").read_text(encoding="utf-8")
        )
        self.assertEqual(self.protocol["dense_gait_shaping"], source["dense_gait_shaping"])
        revision = self.protocol["development_revision"]
        self.assertFalse(revision["motion_request_changed"])
        self.assertFalse(revision["gate_relaxed"])
        self.assertIn("row.fk", revision["correction"])
        self.assertFalse(self.protocol["training_authorized"])
        self.assertFalse(self.protocol["model_promotion_authorized"])
        self.assertFalse(self.protocol["cascadeur_connector_authorized"])


if __name__ == "__main__":
    unittest.main()
