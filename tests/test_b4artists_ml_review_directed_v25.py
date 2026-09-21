from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
TRAIN = ROOT / "training" / "b4artists_ml"


class ReviewDirectedV25ProtocolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.protocol = json.loads((TRAIN / "procedural_vertical_slice_protocol_v25.json").read_text(encoding="utf-8"))

    def test_run_arms_follow_the_animated_torso_without_world_space_ik(self):
        shaping = self.protocol["full_body_shaping"]["tasks"]["run"]
        self.assertTrue(all(not row["limbs"] for row in shaping.values()))
        chest = [row["torso"]["chest_pitch_degrees"] for row in shaping.values()]
        self.assertEqual(max(chest) - min(chest), 7)

    def test_extended_run_jump_and_authority_are_preserved(self):
        run = self.protocol["tasks"]["run"]
        self.assertEqual(run["flights"], [[10, 16], [26, 32]])
        self.assertTrue(all(row["landing_blend_frames"] == 6 for row in run["flight_transitions"]))
        self.assertEqual(max(row["frame"] for row in run["poses"]), 40)
        self.assertEqual(self.protocol["tasks"]["jump"]["flights"], [[16, 43]])
        self.assertFalse(self.protocol["training_authorized"])
        self.assertFalse(self.protocol["model_promotion_authorized"])
        self.assertFalse(self.protocol["cascadeur_connector_authorized"])


if __name__ == "__main__":
    unittest.main()
