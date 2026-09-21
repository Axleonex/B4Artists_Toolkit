import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "training/b4artists_ml/procedural_vertical_slice_protocol_v38.json"


class V38Tests(unittest.TestCase):
    def test_reach_and_transition_corrections_are_bounded(self):
        run = json.loads(PROTOCOL.read_text())["tasks"]["run"]
        self.assertEqual([row[2] for row in run["contacts"][:4]], [4, 14, 24, 34])
        self.assertEqual(
            [row["non_priority_shape_frames"] for row in run["flight_transitions"]],
            [[9], [19], [29], [39]],
        )
        poses = {row["frame"]: row for row in run["poses"]}
        self.assertAlmostEqual(poses[7]["limbs"]["leg-L"][1], -0.12)
        self.assertAlmostEqual(poses[9]["limbs"]["leg-L"][1], -0.20)


if __name__ == "__main__":
    unittest.main()
