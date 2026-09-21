import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
TRAIN = ROOT / "training/b4artists_ml"
PROTOCOL = TRAIN / "procedural_vertical_slice_protocol_v56.json"
sys.path.insert(0, str(TRAIN))
import build_procedural_vertical_slice_v21_repair2 as engine


class V56Tests(unittest.TestCase):
    def test_ambiguous_repeated_label_override_fails_closed(self):
        protocol = json.loads(PROTOCOL.read_text())
        original = protocol["tasks"]["run"]
        override = protocol["profile_overrides"]["rigify_basic"]
        with self.assertRaisesRegex(ValueError, "ambiguous duplicate labels"):
            engine.task_with_profile_pose_overrides(original, override, "run")

    def test_unknown_pose_label_fails_closed(self):
        protocol = json.loads(PROTOCOL.read_text())
        with self.assertRaisesRegex(ValueError, "unknown labels"):
            engine.task_with_profile_pose_overrides(
                protocol["tasks"]["run"],
                {"pose_overrides_by_task": {"run": {"missing": {"limbs": {}}}}},
                "run",
            )

    def test_boneforge_remains_unmodified(self):
        protocol = json.loads(PROTOCOL.read_text())
        resolved = engine.task_with_profile_pose_overrides(
            protocol["tasks"]["run"], protocol["profile_overrides"]["boneforge"], "run"
        )
        self.assertEqual(resolved, protocol["tasks"]["run"])


if __name__ == "__main__":
    unittest.main()
