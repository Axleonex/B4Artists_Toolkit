import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "training/b4artists_ml/procedural_vertical_slice_protocol_v47.json"


class V47Tests(unittest.TestCase):
    def test_contacts_cover_blends_without_release_extension(self):
        protocol = json.loads(PROTOCOL.read_text())
        run = protocol["tasks"]["run"]
        self.assertEqual(run["landing_contact_blend_out_frames"], 0)
        self.assertEqual([row["landing_blend_frames"] for row in run["flight_transitions"]], [4, 4, 4, 0])
        self.assertEqual([row[2] for row in run["contacts"][1:4]], [15, 25, 35])
        for flight, contact in zip(run["flights"][:-1], run["contacts"][1:4]):
            self.assertEqual(flight[1] + 4, contact[2])


if __name__ == "__main__":
    unittest.main()
