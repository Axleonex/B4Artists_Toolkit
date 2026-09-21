from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
TRAIN = ROOT / "training" / "b4artists_ml"


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


class ReviewDirectedV22Repair2ProtocolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.protocol = read(TRAIN / "procedural_vertical_slice_protocol_v22_repair2.json")

    def test_jump_transition_has_explicit_foot_clearance(self):
        preimpact = next(
            row for row in self.protocol["tasks"]["jump"]["poses"]
            if row["label"] == "pre-impact"
        )
        self.assertEqual(preimpact["limbs"]["leg-L"][2], 0.04)
        self.assertEqual(preimpact["limbs"]["leg-R"][2], 0.04)

    def test_run_uses_c1_transitions_and_low_amplitude_arms(self):
        run = self.protocol["tasks"]["run"]
        self.assertTrue(all(not row["match_acceleration"] for row in run["flight_transitions"]))
        shaping = self.protocol["full_body_shaping"]["tasks"]["run"]
        poses = {row["label"]: row for row in run["poses"]}
        amplitudes = []
        for label, recipe in shaping.items():
            pelvis_y = poses[label]["pelvis"][1]
            amplitudes.extend(
                abs(recipe["limbs"][arm][1] - pelvis_y)
                for arm in ("arm-L", "arm-R")
            )
        self.assertAlmostEqual(max(amplitudes), 0.015)
        chest = [row["torso"]["chest_pitch_degrees"] for row in shaping.values()]
        self.assertGreaterEqual(max(chest) - min(chest), 4)

    def test_authority_remains_closed(self):
        self.assertFalse(self.protocol["training_authorized"])
        self.assertFalse(self.protocol["model_promotion_authorized"])
        self.assertFalse(self.protocol["cascadeur_connector_authorized"])


if __name__ == "__main__":
    unittest.main()
