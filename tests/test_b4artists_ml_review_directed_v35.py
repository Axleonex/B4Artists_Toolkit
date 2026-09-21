from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
TRAIN = ROOT / "training" / "b4artists_ml"


class ReviewDirectedV35ProtocolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.protocol = json.loads(
            (TRAIN / "procedural_vertical_slice_protocol_v35.json").read_text(encoding="utf-8")
        )

    def test_declared_layer_gate_is_strict_and_preserves_legacy_result(self):
        gate = self.protocol["declared_layer_priority_gate"]
        self.assertEqual(gate["maximum_written_controls"], 4)
        self.assertGreater(gate["minimum_flexion_degrees"], 0)
        self.assertLess(gate["maximum_flexion_degrees"], 180)
        self.assertTrue(gate["require_source_action_unchanged"])
        self.assertTrue(gate["preserve_legacy_result"])
        self.assertFalse(self.protocol["development_revision"]["gate_relaxed"])

    def test_authority_remains_closed(self):
        self.assertFalse(self.protocol["training_authorized"])
        self.assertFalse(self.protocol["model_promotion_authorized"])
        self.assertFalse(self.protocol["cascadeur_connector_authorized"])


if __name__ == "__main__":
    unittest.main()
