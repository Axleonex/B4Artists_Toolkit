"""Contract tests for the review-directed locomotion/jump v16 candidate."""
from pathlib import Path
import ast
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
TRAIN = ROOT / "training" / "b4artists_ml"
BUILDER = TRAIN / "build_procedural_vertical_slice_v16.py"
PROTOCOL = TRAIN / "procedural_vertical_slice_protocol_v16.json"


class ProceduralVerticalSliceV16Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = BUILDER.read_text(encoding="utf-8")
        cls.protocol = json.loads(PROTOCOL.read_text(encoding="utf-8"))

    def test_candidate_is_separately_versioned_and_supports_task_length(self):
        ast.parse(self.source, filename=str(BUILDER))
        self.assertEqual(self.protocol["schema"], "procedural-vertical-slice-v16")
        self.assertEqual(self.protocol["supersedes"], "procedural_vertical_slice_protocol_v15.json")
        self.assertIn("end_frame = max", self.source)
        self.assertIn("scene.frame_end = math.ceil(end_frame)", self.source)
        self.assertIn("np.linspace(1.0, end_frame, sample_count)", self.source)

    def test_walk_uses_alternating_timing_and_vertical_hip_motion(self):
        poses = self.protocol["tasks"]["walk"]["poses"]
        timing = [row["incoming_timing"] for row in poses[1:]]
        self.assertEqual([row["bias"] for row in timing], [-0.2, 0.2, -0.2, 0.2])
        self.assertEqual({row["easing"] for row in timing}, {"SMOOTH"})
        self.assertGreater(poses[1]["pelvis"][2], poses[2]["pelvis"][2])
        self.assertGreater(poses[3]["pelvis"][2], poses[4]["pelvis"][2])

    def test_run_hips_track_landing_feet_more_closely(self):
        poses = self.protocol["tasks"]["run"]["poses"]
        right_landing = poses[2]
        left_landing = poses[4]
        self.assertLessEqual(abs(right_landing["pelvis"][1] - right_landing["limbs"]["leg-R"][1]), 0.031)
        self.assertLessEqual(abs(left_landing["pelvis"][1] - left_landing["limbs"]["leg-L"][1]), 0.031)
        self.assertTrue(all("incoming_timing" in row for row in poses[1:]))

    def test_jump_extends_airborne_duration_without_promotion(self):
        jump = self.protocol["tasks"]["jump"]
        self.assertEqual(jump["flights"], [[7, 23]])
        self.assertEqual(jump["poses"][-1]["frame"], 31)
        self.assertEqual(jump["contacts"][-1][1:], [23, 31])
        self.assertEqual(jump["flights"][0][1] - jump["flights"][0][0], 16)
        prior = self.protocol["learned_bend_prior"]
        self.assertFalse(prior["temporal_motion_model"])
        self.assertFalse(prior["promotion_authorized"])

    def test_builder_applies_only_declared_transition_overrides(self):
        self.assertIn('timing = pose_spec.get("incoming_timing")', self.source)
        self.assertIn("workflow.set_transition_timing(", self.source)
        self.assertIn('interaction("set_transition_timing")', self.source)


if __name__ == "__main__":
    unittest.main()
