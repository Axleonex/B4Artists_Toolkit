import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "training/b4artists_ml/procedural_vertical_slice_protocol_v42.json"


class V42Tests(unittest.TestCase):
    def test_only_terminal_landing_blend_is_zero(self):
        transitions = json.loads(PROTOCOL.read_text())["tasks"]["run"]["flight_transitions"]
        self.assertEqual([row["landing_blend_frames"] for row in transitions], [1, 1, 1, 0])


if __name__ == "__main__":
    unittest.main()
