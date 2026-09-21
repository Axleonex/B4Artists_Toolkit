import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "training/b4artists_ml/procedural_vertical_slice_protocol_v41.json"


class V41Tests(unittest.TestCase):
    def test_transition_and_torso_range_are_bounded(self):
        protocol = json.loads(PROTOCOL.read_text())
        run = protocol["tasks"]["run"]
        self.assertTrue(all(row["landing_blend_frames"] == 1 for row in run["flight_transitions"]))
        torso = protocol["full_body_shaping"]["tasks"]["run"]
        used = {row["label"] for row in run["poses"]}
        chest = [torso[label]["torso"]["chest_pitch_degrees"] for label in used if label in torso]
        self.assertGreaterEqual(max(chest) - min(chest), 3.5)
        self.assertLessEqual(max(chest) - min(chest), 3.7)


if __name__ == "__main__":
    unittest.main()
