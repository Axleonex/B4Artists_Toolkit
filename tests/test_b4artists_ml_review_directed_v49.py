import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "training/b4artists_ml/procedural_vertical_slice_protocol_v49.json"


class V49Tests(unittest.TestCase):
    def test_only_flight_start_torso_changes_from_v47(self):
        protocol = json.loads(PROTOCOL.read_text())
        source = json.loads((PROTOCOL.parent / "procedural_vertical_slice_protocol_v47.json").read_text())
        torso = protocol["full_body_shaping"]["tasks"]["run"]
        old = source["full_body_shaping"]["tasks"]["run"]
        for label, row in torso.items():
            if label.endswith("flight-start"):
                self.assertEqual(row["torso"]["chest_pitch_degrees"], -2.5)
                self.assertEqual(row["torso"]["spine_pitch_degrees"], -1.25)
            else:
                self.assertEqual(row, old[label])
        chest = [row["torso"]["chest_pitch_degrees"] for row in torso.values()]
        self.assertGreaterEqual(max(chest) - min(chest), 3.5)


if __name__ == "__main__":
    unittest.main()
