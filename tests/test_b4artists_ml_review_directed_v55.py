import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
TRAIN = ROOT / "training/b4artists_ml"
PROTOCOL = TRAIN / "procedural_vertical_slice_protocol_v55.json"
sys.path.insert(0, str(TRAIN))
import build_procedural_vertical_slice_v21_repair2 as engine


class V55Tests(unittest.TestCase):
    def test_profile_release_override_excludes_terminal_contact(self):
        protocol = json.loads(PROTOCOL.read_text())
        task = protocol["tasks"]["run"]
        override = protocol["profile_overrides"]["rigify_basic"]
        self.assertEqual(engine.contact_blend_out(override, task, "run", 11, 15, 40, 0), 0.5)
        self.assertEqual(engine.contact_blend_out(override, task, "run", 40, 40, 40, 0), 0.0)

    def test_boneforge_has_no_new_override(self):
        protocol = json.loads(PROTOCOL.read_text())
        boneforge = protocol["profile_overrides"]["boneforge"]
        self.assertNotIn("landing_contact_blend_out_frames_by_task", boneforge)
        self.assertEqual(protocol["preserved_evidence"]["exact_case"], "boneforge/run")

    def test_invalid_release_override_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "finite and nonnegative"):
            engine.contact_blend_out(
                {"landing_contact_blend_out_frames_by_task": {"run": -0.5}},
                {"landing_contact_blend_out_frames": 0}, "run", 11, 15, 40, 0,
            )


if __name__ == "__main__":
    unittest.main()
