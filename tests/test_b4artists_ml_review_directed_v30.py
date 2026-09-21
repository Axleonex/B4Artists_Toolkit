from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
TRAIN = ROOT / "training" / "b4artists_ml"


class ReviewDirectedV30ProtocolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.protocol = json.loads(
            (TRAIN / "procedural_vertical_slice_protocol_v30.json").read_text(encoding="utf-8")
        )

    def test_retry_changes_binding_derivation_not_motion(self):
        source = json.loads(
            (TRAIN / "procedural_vertical_slice_protocol_v29.json").read_text(encoding="utf-8")
        )
        self.assertEqual(self.protocol["dense_gait_shaping"], source["dense_gait_shaping"])
        revision = self.protocol["development_revision"]
        self.assertFalse(revision["motion_request_changed"])
        self.assertFalse(revision["gate_relaxed"])

    def test_authority_remains_closed(self):
        self.assertFalse(self.protocol["training_authorized"])
        self.assertFalse(self.protocol["model_promotion_authorized"])
        self.assertFalse(self.protocol["cascadeur_connector_authorized"])


if __name__ == "__main__":
    unittest.main()
