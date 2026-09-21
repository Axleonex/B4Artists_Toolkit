from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
TRAIN = ROOT / "training" / "b4artists_ml"


class ReviewDirectedV23ProtocolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.protocol = json.loads((TRAIN / "procedural_vertical_slice_protocol_v23.json").read_text(encoding="utf-8"))

    def test_jump_stays_ballistic_until_first_contact_then_absorbs(self):
        jump = self.protocol["tasks"]["jump"]
        self.assertEqual(jump["flights"], [[16, 43]])
        self.assertEqual(jump["contacts"][2][1], 43)
        transition = jump["flight_transitions"][0]
        self.assertEqual(transition["landing_blend_frames"], 6)
        self.assertTrue(transition["match_acceleration"])
        self.assertEqual(transition["contact_impulse_strength"], 1.0)
        self.assertEqual(transition["collision_strength"], 0.0)
        self.assertEqual(transition["non_priority_shape_frames"], [37, 41])

    def test_preimpact_feet_are_not_artificially_raised(self):
        preimpact = next(row for row in self.protocol["tasks"]["jump"]["poses"] if row["label"] == "pre-impact")
        self.assertEqual(preimpact["limbs"]["leg-L"][2], 0.0)
        self.assertEqual(preimpact["limbs"]["leg-R"][2], 0.0)
        crouch = next(row for row in self.protocol["tasks"]["jump"]["poses"] if row["label"] == "absorb crouch")
        self.assertEqual(crouch["limbs"]["leg-L"], [0.0, -0.05, 0.0])
        self.assertEqual(crouch["limbs"]["leg-R"], [0.0, -0.05, 0.0])

    def test_postimpact_upper_body_continues_moving(self):
        shaping = self.protocol["full_body_shaping"]["tasks"]["jump"]
        chest = [shaping[label]["torso"]["chest_pitch_degrees"] for label in ("impact", "absorb crouch", "follow-through")]
        self.assertGreaterEqual(max(chest) - min(chest), 13)
        self.assertNotEqual(shaping["impact"]["limbs"]["arm-L"][2], shaping["absorb crouch"]["limbs"]["arm-L"][2])

    def test_authority_remains_closed(self):
        self.assertFalse(self.protocol["training_authorized"])
        self.assertFalse(self.protocol["model_promotion_authorized"])
        self.assertFalse(self.protocol["cascadeur_connector_authorized"])


if __name__ == "__main__":
    unittest.main()
