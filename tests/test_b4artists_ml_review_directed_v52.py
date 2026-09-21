import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "training/b4artists_ml/procedural_vertical_slice_protocol_v52.json"


class V52Tests(unittest.TestCase):
    def test_only_dense_arm_amplitude_changes_from_v51(self):
        protocol = json.loads(PROTOCOL.read_text())
        source = json.loads((PROTOCOL.parent / "procedural_vertical_slice_protocol_v51.json").read_text())
        dense = protocol["dense_gait_shaping"]
        old = source["dense_gait_shaping"]
        self.assertEqual(dense["amplitude"], 0.155)
        self.assertEqual(dense["cycle_frames"], old["cycle_frames"])
        self.assertEqual(dense["drop"], old["drop"])
        self.assertEqual(dense["outward"], old["outward"])
        self.assertGreater(dense["amplitude"], 0.15)


if __name__ == "__main__":
    unittest.main()
