import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "training/b4artists_ml/procedural_vertical_slice_protocol_v53.json"


class V53Tests(unittest.TestCase):
    def test_exact_contact_boundaries_preserve_transition_coverage(self):
        protocol = json.loads(PROTOCOL.read_text())
        run = protocol["tasks"]["run"]
        self.assertEqual(run["landing_contact_blend_frames"], 0)
        self.assertEqual(run["landing_contact_blend_out_frames"], 0)
        self.assertEqual(run["contacts"][-1], ["leg-L", 40, 40])
        for flight, transition, contact in zip(
            run["flights"][:-1], run["flight_transitions"][:-1], run["contacts"][1:4]
        ):
            self.assertEqual(contact[1], flight[1])
            self.assertEqual(contact[2], flight[1] + transition["landing_blend_frames"])


if __name__ == "__main__":
    unittest.main()
