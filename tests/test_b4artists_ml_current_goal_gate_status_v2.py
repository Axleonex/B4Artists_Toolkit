import copy
import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
TRAIN = ROOT / "training/b4artists_ml"
RECEIPT = TRAIN / "results/current-goal-gate-status-v2.json"
sys.path.insert(0, str(TRAIN))
import build_current_goal_gate_status_v2 as builder


class CurrentGoalGateStatusV2Tests(unittest.TestCase):
    def test_stored_receipt_equals_recomputed_evidence(self):
        stored = json.loads(RECEIPT.read_text(encoding="utf-8"))
        self.assertEqual(stored, builder.build())
        self.assertEqual(stored["status"], "ACTIVE_INCOMPLETE_EXTERNAL_GATES")
        self.assertEqual(stored["current_local_package"]["version"], "0.37.51-dev")
        self.assertEqual(
            stored["human_visual_acceptance"]["accepted_exact_cases"],
            ["boneforge/run@v54", "rigify_basic/run@v58"],
        )
        self.assertEqual(stored["remaining_prerequisite_independent_work_in_declared_workstreams"], [])

    def test_training_promotion_and_connector_remain_fail_closed(self):
        report = builder.build()
        boundary = report["claim_boundary"]
        self.assertFalse(boundary["model_training_permitted"])
        self.assertFalse(boundary["model_promotion_permitted"])
        self.assertFalse(boundary["cascadeur_connector_activation_permitted"])
        self.assertFalse(boundary["full_goal_complete"])
        self.assertEqual(
            report["declared_workstreams"]["temporal_training_evaluation_pipeline"]["status"],
            "PASS_FAIL_CLOSED",
        )

    def test_human_review_cannot_substitute_for_identity_authorization(self):
        report = builder.build()
        changed = copy.deepcopy(report)
        changed["human_visual_acceptance"]["identity_receipt_valid"] = True
        self.assertNotEqual(changed, report)
        self.assertFalse(report["human_visual_acceptance"]["identity_receipt_valid"])


if __name__ == "__main__":
    unittest.main()
