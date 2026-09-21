import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "training/b4artists_ml/procedural_vertical_slice_protocol_v51.json"


class V51Tests(unittest.TestCase):
    def test_torso_values_include_projection_margin(self):
        protocol = json.loads(PROTOCOL.read_text())
        torso = protocol["full_body_shaping"]["tasks"]["run"]
        sampled = [
            torso[label]["torso"]["chest_pitch_degrees"] for label in (
                "left support", "left midstance", "left toe-off", "left flight-start",
                "right landing", "right midstance", "right toe-off", "right flight-start",
                "left landing",
            )
        ]
        self.assertGreater(max(sampled) - min(sampled), 3.5)
        for side in ("left", "right"):
            self.assertEqual(torso[f"{side} toe-off"]["torso"]["chest_pitch_degrees"], -2.76)
            self.assertLess(abs(
                torso[f"{side} midstance"]["torso"]["chest_pitch_degrees"] + 2.76
            ), 1.27)


if __name__ == "__main__":
    unittest.main()
