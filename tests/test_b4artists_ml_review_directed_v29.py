from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
TRAIN = ROOT / "training" / "b4artists_ml"


class ReviewDirectedV29ProtocolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.protocol = json.loads(
            (TRAIN / "procedural_vertical_slice_protocol_v29.json").read_text(encoding="utf-8")
        )

    def test_sparse_run_hand_targets_are_removed(self):
        shaping = self.protocol["full_body_shaping"]["tasks"]["run"]
        self.assertTrue(all(not recipe["limbs"] for recipe in shaping.values()))

    def test_dense_candidate_only_request_is_bounded(self):
        request = self.protocol["dense_gait_shaping"]
        self.assertEqual(request["task"], "run")
        self.assertEqual((request["first_frame"], request["last_frame"]), (1, 40))
        self.assertLessEqual(request["amplitude"], 0.10)
        self.assertTrue(request["source_action_unchanged"])
        self.assertTrue(request["candidate_only"])
        self.assertFalse(self.protocol["development_revision"]["gate_relaxed"])

    def test_authority_remains_closed(self):
        self.assertFalse(self.protocol["training_authorized"])
        self.assertFalse(self.protocol["model_promotion_authorized"])
        self.assertFalse(self.protocol["cascadeur_connector_authorized"])


if __name__ == "__main__":
    unittest.main()
