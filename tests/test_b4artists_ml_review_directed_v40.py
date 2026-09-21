import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "training/b4artists_ml/procedural_vertical_slice_protocol_v40.json"


class V40Tests(unittest.TestCase):
    def test_flights_have_adjacent_priority_anchors(self):
        run = json.loads(PROTOCOL.read_text())["tasks"]["run"]
        frames = {row["frame"] for row in run["poses"]}
        for start, end in run["flights"]:
            self.assertIn(start, frames)
            self.assertIn(end, frames)
            self.assertFalse(any(start < frame < end for frame in frames))
        self.assertEqual([row[2] for row in run["contacts"][:4]], [3, 13, 23, 33])


if __name__ == "__main__":
    unittest.main()
