import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "training/b4artists_ml/procedural_vertical_slice_protocol_v37.json"


class V37Tests(unittest.TestCase):
    def test_stance_ends_before_toeoff_and_flight_starts(self):
        run = json.loads(PROTOCOL.read_text())["tasks"]["run"]
        self.assertEqual([row[2] for row in run["contacts"][:4]], [5, 15, 25, 35])
        self.assertEqual([row[0] for row in run["flights"]], [6, 16, 26, 36])
        self.assertTrue(all(start == end + 1 for end, start in zip(
            [row[2] for row in run["contacts"][:4]],
            [row[0] for row in run["flights"]],
        )))


if __name__ == "__main__":
    unittest.main()
