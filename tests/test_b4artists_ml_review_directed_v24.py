from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
TRAIN = ROOT / "training" / "b4artists_ml"


class ReviewDirectedV24ProtocolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.protocol = json.loads((TRAIN / "procedural_vertical_slice_protocol_v24.json").read_text(encoding="utf-8"))

    def test_run_has_symmetric_extended_flights_and_contacts(self):
        run = self.protocol["tasks"]["run"]
        self.assertEqual(run["flights"], [[10, 16], [26, 32]])
        self.assertEqual(run["contacts"], [["leg-L", 1, 8], ["leg-R", 16, 24], ["leg-L", 32, 40]])
        self.assertEqual(run["landing_contact_blend_frames"], 2)
        self.assertTrue(all(row["contact_impulse_strength"] == 1.0 for row in run["flight_transitions"]))
        self.assertTrue(all(row["match_acceleration"] for row in run["flight_transitions"]))

    def test_run_countermotion_is_visible_but_time_distributed(self):
        shaping = self.protocol["full_body_shaping"]["tasks"]["run"]
        chest = [row["torso"]["chest_pitch_degrees"] for row in shaping.values()]
        self.assertEqual(max(chest) - min(chest), 7)
        poses = {row["label"]: row for row in self.protocol["tasks"]["run"]["poses"]}
        offsets = []
        for label, recipe in shaping.items():
            pelvis_y = poses[label]["pelvis"][1]
            offsets.extend(abs(recipe["limbs"][arm][1] - pelvis_y) for arm in ("arm-L", "arm-R"))
        self.assertAlmostEqual(max(offsets), .04)
        self.assertEqual(max(row["frame"] for row in poses.values()), 40)

    def test_v23_jump_and_authority_are_preserved(self):
        jump = self.protocol["tasks"]["jump"]
        self.assertEqual(jump["flights"], [[16, 43]])
        self.assertEqual(jump["flight_transitions"][0]["contact_impulse_strength"], 1.0)
        self.assertFalse(self.protocol["training_authorized"])
        self.assertFalse(self.protocol["model_promotion_authorized"])
        self.assertFalse(self.protocol["cascadeur_connector_authorized"])


if __name__ == "__main__":
    unittest.main()
