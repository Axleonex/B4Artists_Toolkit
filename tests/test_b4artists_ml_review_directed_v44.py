import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "training/b4artists_ml/procedural_vertical_slice_protocol_v44.json"


class V44Tests(unittest.TestCase):
    def test_internal_blends_end_on_contacted_midstance(self):
        protocol = json.loads(PROTOCOL.read_text())
        run = protocol["tasks"]["run"]
        frames = {row["frame"] for row in run["poses"]}
        self.assertEqual([row["landing_blend_frames"] for row in run["flight_transitions"]], [3, 3, 3, 0])
        self.assertTrue({14, 24, 34}.issubset(frames))
        self.assertEqual([row[2] for row in run["contacts"][1:4]], [14, 24, 34])
        for flight in run["flights"][:-1]:
            self.assertIn(flight[1] + 3, frames)


if __name__ == "__main__":
    unittest.main()
