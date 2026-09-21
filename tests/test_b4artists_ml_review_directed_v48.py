import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "training/b4artists_ml/procedural_vertical_slice_protocol_v48.json"


class V48Tests(unittest.TestCase):
    def test_torso_cycle_retains_range_without_toeoff_flight_snap(self):
        protocol = json.loads(PROTOCOL.read_text())
        torso = protocol["full_body_shaping"]["tasks"]["run"]
        chest = {label: row["torso"]["chest_pitch_degrees"] for label, row in torso.items()}
        self.assertGreaterEqual(max(chest.values()) - min(chest.values()), 3.5)
        for side in ("left", "right"):
            self.assertLessEqual(abs(chest[f"{side} toe-off"] - chest[f"{side} flight-start"]), 0.600001)
            self.assertLessEqual(abs(chest[f"{side} midstance"] - chest[f"{side} toe-off"]), 0.600001)


if __name__ == "__main__":
    unittest.main()
