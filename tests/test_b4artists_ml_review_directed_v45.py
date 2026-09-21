import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "training/b4artists_ml/procedural_vertical_slice_protocol_v45.json"


class V45Tests(unittest.TestCase):
    def test_internal_blends_end_on_contacted_midstance(self):
        protocol = json.loads(PROTOCOL.read_text())
        run = protocol["tasks"]["run"]
        frames = {row["frame"] for row in run["poses"]}
        self.assertEqual([row["landing_blend_frames"] for row in run["flight_transitions"]], [4, 4, 4, 0])
        self.assertTrue({15, 25, 35}.issubset(frames))
        self.assertEqual([row[2] for row in run["contacts"][1:4]], [15, 25, 35])
        for flight in run["flights"][:-1]:
            self.assertIn(flight[1] + 4, frames)

    def test_shift_preserves_constant_forward_speed(self):
        protocol = json.loads(PROTOCOL.read_text())
        poses = protocol["tasks"]["run"]["poses"]
        by_frame = {row["frame"]: row for row in poses}
        for frame in (15, 25, 35):
            self.assertAlmostEqual(by_frame[frame]["pelvis"][1], -0.05 * (frame - 1), places=9)


if __name__ == "__main__":
    unittest.main()
