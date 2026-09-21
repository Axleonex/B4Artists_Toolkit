import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "training/b4artists_ml/procedural_vertical_slice_protocol_v50.json"


class V50Tests(unittest.TestCase):
    def test_minimal_torso_adjustment_preserves_required_range(self):
        protocol = json.loads(PROTOCOL.read_text())
        torso = protocol["full_body_shaping"]["tasks"]["run"]
        chest = {label: row["torso"]["chest_pitch_degrees"] for label, row in torso.items()}
        sampled = [chest[label] for label in (
            "left support", "left midstance", "left toe-off", "left flight-start",
            "right landing", "right midstance", "right toe-off", "right flight-start",
            "left landing",
        )]
        self.assertAlmostEqual(max(sampled) - min(sampled), 3.5, places=9)
        for side in ("left", "right"):
            self.assertEqual(chest[f"{side} toe-off"], -2.8)
            self.assertEqual(chest[f"{side} flight-start"], -2.5)
            self.assertLess(abs(chest[f"{side} midstance"] - chest[f"{side} toe-off"]), 1.31)


if __name__ == "__main__":
    unittest.main()
