import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "training/b4artists_ml/procedural_vertical_slice_protocol_v43.json"


class V43Tests(unittest.TestCase):
    def test_internal_blends_end_on_existing_midstance_anchors(self):
        protocol = json.loads(PROTOCOL.read_text())
        run = protocol["tasks"]["run"]
        self.assertEqual(
            [row["landing_blend_frames"] for row in run["flight_transitions"]],
            [2, 2, 2, 0],
        )
        frames = {row["frame"] for row in run["poses"]}
        for flight in run["flights"][:-1]:
            self.assertIn(flight[1] + 2, frames)


if __name__ == "__main__":
    unittest.main()
