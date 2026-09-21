import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "training/b4artists_ml/procedural_vertical_slice_protocol_v54.json"


class V54Tests(unittest.TestCase):
    def test_cross_rig_arm_margin_preserves_cycle(self):
        protocol = json.loads(PROTOCOL.read_text())
        source = json.loads((PROTOCOL.parent / "procedural_vertical_slice_protocol_v53.json").read_text())
        dense = protocol["dense_gait_shaping"]
        old = source["dense_gait_shaping"]
        self.assertEqual(dense["amplitude"], 0.15)
        self.assertEqual(dense["cycle_frames"], 20.0)
        self.assertEqual(dense["drop"], old["drop"])
        self.assertEqual(dense["outward"], old["outward"])
        self.assertGreaterEqual(dense["amplitude"], 0.15)


if __name__ == "__main__":
    unittest.main()
