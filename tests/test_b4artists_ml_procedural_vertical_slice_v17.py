"""Contract tests for the single-authority locomotion/jump v17 candidate."""
from pathlib import Path
import ast
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
TRAIN = ROOT / "training" / "b4artists_ml"
BUILDER = TRAIN / "build_procedural_vertical_slice_v17.py"
PROTOCOL = TRAIN / "procedural_vertical_slice_protocol_v17.json"
RECEIPT = TRAIN / "results" / "procedural-vertical-slice-v17-focused.json"


class ProceduralVerticalSliceV17Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = BUILDER.read_text(encoding="utf-8")
        cls.protocol_text = PROTOCOL.read_text(encoding="utf-8")
        cls.protocol = json.loads(cls.protocol_text)

    def test_candidate_is_separately_versioned_and_dynamic_length(self):
        ast.parse(self.source, filename=str(BUILDER))
        self.assertEqual(self.protocol["schema"], "procedural-vertical-slice-v17")
        self.assertEqual(self.protocol["supersedes"], "procedural_vertical_slice_protocol_v16.json")
        self.assertIn("scene.frame_end = math.ceil(end_frame)", self.source)
        self.assertIn("np.linspace(1.0, end_frame, sample_count)", self.source)

    def test_rejected_second_timing_authority_is_removed(self):
        self.assertNotIn("incoming_timing", self.protocol_text)
        self.assertNotIn("set_transition_timing", self.source)
        self.assertIn("one timing authority", self.protocol["purpose"])
        self.assertIn("refuses a second timing authority", self.protocol["revision_reason"])

    def test_walk_uses_nonuniform_authored_spacing_and_vertical_hip_motion(self):
        walk = self.protocol["tasks"]["walk"]
        frames = [row["frame"] for row in walk["poses"]]
        self.assertEqual(frames, [1, 8, 14, 21, 27])
        self.assertEqual([b - a for a, b in zip(frames, frames[1:])], [7, 6, 7, 6])
        self.assertGreater(walk["poses"][1]["pelvis"][2], walk["poses"][2]["pelvis"][2])
        self.assertGreater(walk["poses"][3]["pelvis"][2], walk["poses"][4]["pelvis"][2])
        self.assertEqual(walk["contacts"], [["leg-L", 1, 14], ["leg-R", 14, 27]])

    def test_run_spacing_contacts_and_flights_share_boundaries(self):
        run = self.protocol["tasks"]["run"]
        frames = [row["frame"] for row in run["poses"]]
        self.assertEqual(frames, [1, 4, 13, 16, 26, 29])
        self.assertEqual(run["contacts"], [["leg-L", 1, 4], ["leg-R", 13, 16], ["leg-L", 26, 29]])
        self.assertEqual(run["flights"], [[4, 13], [16, 26]])
        self.assertLessEqual(abs(run["poses"][2]["pelvis"][1] - run["poses"][2]["limbs"]["leg-R"][1]), 0.031)
        self.assertLessEqual(abs(run["poses"][4]["pelvis"][1] - run["poses"][4]["limbs"]["leg-L"][1]), 0.031)

    def test_jump_extends_airborne_duration_without_promotion(self):
        jump = self.protocol["tasks"]["jump"]
        self.assertEqual(jump["flights"], [[7, 23]])
        self.assertEqual(jump["poses"][-1]["frame"], 31)
        prior = self.protocol["learned_bend_prior"]
        self.assertFalse(prior["temporal_motion_model"])
        self.assertFalse(prior["promotion_authorized"])

    def test_focused_receipt_binds_all_cases_and_keeps_claims_closed(self):
        if not RECEIPT.exists():
            self.skipTest("Focused native receipt has not been assembled yet")
        receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
        self.assertEqual(receipt["schema"], "b4ml-review-directed-procedural-vertical-slice-v17-focused")
        self.assertEqual(receipt["status"], "PASS_FOCUSED_DETERMINISTIC")
        self.assertEqual(receipt["passed"], 12)
        self.assertEqual(receipt["expected"], 12)
        self.assertEqual(len(receipt["cases"]), 12)
        self.assertEqual(len(receipt["jump_flight_evidence"]), 4)
        self.assertTrue(all(row["frames"] == [7, 23] for row in receipt["jump_flight_evidence"]))
        self.assertTrue(all(abs(row["duration_seconds"] - (16 / 30)) < 1e-9 for row in receipt["jump_flight_evidence"]))
        self.assertIn("Projected samples already define timing", receipt["rejected_predecessor"]["reason"])
        self.assertTrue(receipt["known_host_shutdown_fault_not_qualified"])
        self.assertTrue(all(value is False for value in receipt["claim_boundary"].values()))


if __name__ == "__main__":
    unittest.main()
