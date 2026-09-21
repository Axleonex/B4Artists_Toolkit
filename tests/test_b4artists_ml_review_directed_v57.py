import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
TRAIN = ROOT / "training/b4artists_ml"
PROTOCOL = TRAIN / "procedural_vertical_slice_protocol_v57.json"
sys.path.insert(0, str(TRAIN))
import build_procedural_vertical_slice_v21_repair2 as engine


class V57Tests(unittest.TestCase):
    def test_frame_addressed_targets_cover_both_strides(self):
        protocol = json.loads(PROTOCOL.read_text())
        original = protocol["tasks"]["run"]
        override = protocol["profile_overrides"]["rigify_basic"]
        resolved = engine.task_with_profile_pose_overrides(original, override, "run")
        by_frame = {int(pose["frame"]): pose for pose in resolved["poses"]}
        expected = {
            6: ("leg-L", [0, -0.04, 0.025]),
            16: ("leg-R", [0, -0.54, 0.025]),
            26: ("leg-L", [0, -1.04, 0.025]),
            36: ("leg-R", [0, -1.54, 0.025]),
        }
        for frame, (limb, target) in expected.items():
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

    def test_unknown_frame_fails_closed(self):
        protocol = json.loads(PROTOCOL.read_text())
        with self.assertRaisesRegex(ValueError, "unknown frames"):
            engine.task_with_profile_pose_overrides(
                protocol["tasks"]["run"],
                {"pose_frame_overrides_by_task": {"run": {"999": {"limbs": {}}}}},
                "run",
            )


if __name__ == "__main__":
    unittest.main()
