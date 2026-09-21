import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "training/b4artists_ml/procedural_vertical_slice_protocol_v46.json"


class V46Tests(unittest.TestCase):
    def test_blends_end_after_reachable_contacts(self):
        protocol = json.loads(PROTOCOL.read_text())
        run = protocol["tasks"]["run"]
        frames = {row["frame"] for row in run["poses"]}
        self.assertEqual([row["landing_blend_frames"] for row in run["flight_transitions"]], [4, 4, 4, 0])
        self.assertTrue({15, 25, 35}.issubset(frames))
        self.assertEqual([row[2] for row in run["contacts"][1:4]], [14, 24, 34])
        for flight, contact in zip(run["flights"][:-1], run["contacts"][1:4]):
            self.assertEqual(flight[1] + 4, contact[2] + 1)


if __name__ == "__main__":
    unittest.main()
