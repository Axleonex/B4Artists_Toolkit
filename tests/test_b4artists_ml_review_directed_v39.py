import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "training/b4artists_ml/procedural_vertical_slice_protocol_v39.json"


class V39Tests(unittest.TestCase):
    def test_flight_and_amplitudes_are_bounded(self):
        protocol = json.loads(PROTOCOL.read_text())
        run = protocol["tasks"]["run"]
        self.assertEqual([row[0] for row in run["flights"]], [7, 17, 27, 37])
        self.assertLessEqual(
            max(row["pelvis"][2] for row in run["poses"])
            - min(row["pelvis"][2] for row in run["poses"]),
            0.035,
        )
        torso = protocol["full_body_shaping"]["tasks"]["run"]
        chest = [recipe["torso"]["chest_pitch_degrees"] for recipe in torso.values()]
        self.assertLessEqual(max(chest) - min(chest), 4.0)
        self.assertGreaterEqual(max(chest) - min(chest), 3.5)


if __name__ == "__main__":
    unittest.main()
