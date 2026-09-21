"""Contract tests for the frozen Axlbot v21 repair-1 revision."""
from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
TRAIN = ROOT / "training" / "b4artists_ml"


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


class ReviewDirectedV21Repair1ProtocolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.protocol = read(TRAIN / "procedural_vertical_slice_protocol_v21_repair1.json")

    def test_v21_binds_qualified_v5_native_display_review(self):
        self.assertEqual(self.protocol["schema"], "procedural-vertical-slice-v21-repair1")
        self.assertEqual(self.protocol["source_human_review_schema"], "b4ml-human-review-summary-v5")
        self.assertTrue(self.protocol["source_feedback_qualification"]["global_motion"])
        self.assertTrue(self.protocol["source_feedback_qualification"]["production_acceptance"])
        self.assertFalse(self.protocol["training_authorized"])
        self.assertFalse(self.protocol["model_promotion_authorized"])

    def test_jump_begins_absorption_at_impact(self):
        jump = {row["label"]: row for row in self.protocol["tasks"]["jump"]["poses"]}
        self.assertLessEqual(jump["pre-impact"]["pelvis"][2], 0.0)
        self.assertLessEqual(jump["impact"]["pelvis"][2], -0.035)
        self.assertLess(jump["absorb crouch"]["pelvis"][2], jump["impact"]["pelvis"][2])
        gates = self.protocol["review_directed_gates"]
        self.assertGreaterEqual(gates["jump_impact_knee_flexion_degrees"], 20)
        self.assertGreaterEqual(gates["jump_preimpact_knee_flexion_degrees"], 12)

    def test_non_preserved_landings_have_visible_upper_body_range(self):
        shaping = self.protocol["full_body_shaping"]
        land = shaping["tasks"]["land"]
        pitches = [row["torso"]["chest_pitch_degrees"] for row in land.values()]
        self.assertGreaterEqual(max(pitches) - min(pitches), 6)
        self.assertTrue(all("limbs" in land[label] for label in ("pre-impact", "impact", "absorb crouch", "recover")))
        self.assertGreaterEqual(
            self.protocol["review_directed_gates"]["land_chest_pitch_range_degrees"], 6
        )
        self.assertLessEqual(
            self.protocol["review_directed_gates"]["land_upper_body_angular_acceleration_p95_rad_s2"],
            40,
        )

    def test_run_has_counterbalance_and_acceleration_gate(self):
        run = self.protocol["full_body_shaping"]["tasks"]["run"]
        pitches = [row["torso"]["chest_pitch_degrees"] for row in run.values()]
        self.assertTrue(all(value >= 1 for value in pitches))
        gates = self.protocol["review_directed_gates"]
        self.assertLessEqual(gates["run_upper_body_angular_acceleration_p95_rad_s2"], 18)
        self.assertLessEqual(gates["run_pelvis_jerk_p95_body_s3"], 1200)

    def test_learning_and_connector_boundaries_remain_closed(self):
        self.assertFalse(self.protocol["learned_bend_prior"]["temporal_motion_model"])
        self.assertFalse(self.protocol["learned_bend_prior"]["promotion_authorized"])
        self.assertFalse(self.protocol["cascadeur_connector_authorized"])

    def test_repair_scope_targets_only_failed_edges(self):
        self.assertEqual(
            self.protocol["supersedes"], "procedural_vertical_slice_protocol_v21.json"
        )
        jump = {row["label"]: row for row in self.protocol["tasks"]["jump"]["poses"]}
        self.assertEqual(set(jump["flight-end"]["limbs"]), {"leg-L", "leg-R"})
        land = self.protocol["full_body_shaping"]["tasks"]["land"]["absorb crouch"]
        self.assertLessEqual(land["torso"]["chest_pitch_degrees"], -4.1)
        self.assertGreaterEqual(land["limbs"]["arm-L"][2], -0.02)


if __name__ == "__main__":
    unittest.main()
