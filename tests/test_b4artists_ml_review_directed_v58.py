import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
TRAIN = ROOT / "training/b4artists_ml"
PROTOCOL = TRAIN / "procedural_vertical_slice_protocol_v58.json"
sys.path.insert(0, str(TRAIN))
import build_procedural_vertical_slice_v21_repair2 as engine


class V58Tests(unittest.TestCase):
    def test_frame_targets_cover_support_and_swing_legs(self):
        protocol = json.loads(PROTOCOL.read_text())
        original = protocol["tasks"]["run"]
        override = protocol["profile_overrides"]["rigify_basic"]
        resolved = engine.task_with_profile_pose_overrides(original, override, "run")
        by_frame = {int(pose["frame"]): pose for pose in resolved["poses"]}
        expected = {
            6: {"leg-L": [0, -0.04, 0.025], "leg-R": [0, -0.3875, 0.09]},
            16: {"leg-L": [0, -0.775, 0.1], "leg-R": [0, -0.54, 0.025]},
            26: {"leg-L": [0, -1.04, 0.025], "leg-R": [0, -1.275, 0.1]},
            36: {"leg-L": [0, -1.775, 0.1], "leg-R": [0, -1.54, 0.025]},
        }
        for frame, limbs in expected.items():
            for limb, target in limbs.items():
                self.assertEqual(by_frame[frame]["limbs"][limb], target)

    def test_original_task_and_boneforge_are_unchanged(self):
        protocol = json.loads(PROTOCOL.read_text())
        original = protocol["tasks"]["run"]
        before = json.dumps(original, sort_keys=True)
        engine.task_with_profile_pose_overrides(
            original, protocol["profile_overrides"]["rigify_basic"], "run"
        )
        self.assertEqual(json.dumps(original, sort_keys=True), before)
        self.assertEqual(
            engine.task_with_profile_pose_overrides(
                original, protocol["profile_overrides"]["boneforge"], "run"
            ),
            original,
        )


if __name__ == "__main__":
    unittest.main()
