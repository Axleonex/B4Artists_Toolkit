"""Regression coverage for the aggregate goal-gate claim boundary."""

import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "training" / "b4artists_ml" / "results" / "current-goal-gate-status-v1.json"


class CurrentGoalGateStatusTests(unittest.TestCase):
    def test_status_remains_incomplete_and_external_gates_remain_fail_closed(self):
        report = json.loads(RECEIPT.read_text(encoding="utf-8-sig"))
        self.assertEqual(report["schema"], "b4ml-current-goal-gate-status-v1")
        self.assertEqual(report["goal_id"], "01a073fe-c240-70c0-b5cd-fe9653aac60e")
        self.assertEqual(report["status"], "ACTIVE_INCOMPLETE")
        self.assertFalse(report["full_goal_complete"])
        self.assertTrue(all(value is False for value in report["claim_boundary"].values()))
        gates = report["gates"]
        self.assertEqual(gates["temporal_training_boundary"]["status"], "BLOCKED")
        evaluator = gates["capsule_evaluator_review"]
        self.assertEqual(evaluator["status"], "PASS_FAIL_CLOSED")
        self.assertFalse(evaluator["authority"])
        self.assertEqual(evaluator["evaluator_status"], "BLOCKED_BEFORE_EVALUATION")
        self.assertEqual(evaluator["preflight_status"], "REMOTE_EXECUTOR_REQUIRED")
        self.assertEqual(evaluator["advisory_verdict"], "insufficient_evidence")
        self.assertFalse(evaluator["reviewer_invoked"])
        self.assertFalse(evaluator["review_completed"])
        self.assertEqual(evaluator["deterministic_fallback"], "PASS")
        temporal = gates["temporal_training_boundary"]
        self.assertFalse(temporal["training_authorized"])
        self.assertEqual(temporal["intake_status"], "BLOCKED_INTAKE_MISSING_EVIDENCE")
        self.assertEqual(temporal["parent_receipt_status"], "BLOCKED_DATA_BOUNDARY_UNQUALIFIED")
        self.assertFalse(temporal["model_training_permitted"])
        self.assertFalse(temporal["model_promotion_permitted"])
        self.assertFalse(temporal["model_promoted"])
        self.assertTrue(temporal["claim_boundary_closed"])
        self.assertEqual(gates["independent_animator_review"]["status"], "REQUIRED_EXTERNAL")
        human_review = gates["procedural_vertical_slice_human_review"]
        self.assertEqual(human_review["status"], "PASS_REVIEWED_EXPORT")
        self.assertEqual(human_review["reviewer_id"], "Axlbot")
        self.assertEqual(human_review["experience"], "10+ years")
        self.assertEqual(human_review["cases"], 32)
        self.assertTrue(human_review["human_authored"])
        self.assertTrue(human_review["export_validated"])
        self.assertTrue(human_review["claim_boundary_closed"])
        head_orientation = gates["humanoid_head_orientation"]
        self.assertEqual(head_orientation["status"], "PASS")
        self.assertEqual(head_orientation["semantic_joint"], 4)
        self.assertEqual(head_orientation["focused_tests"], 10)
        self.assertEqual(len(head_orientation["fixtures"]), 5)
        self.assertTrue(head_orientation["procedural_only"])
        self.assertTrue(head_orientation["claim_boundary_closed"])
        pole_status = gates["humanoid_pole_status"]
        self.assertEqual(pole_status["status"], "PASS")
        self.assertEqual(pole_status["focused_tests"], 6)
        self.assertEqual(pole_status["affected_tests"], 84)
        self.assertTrue(pole_status["read_only"])
        self.assertTrue(pole_status["claim_boundary_closed"])
        current_package = gates["current_dev_package"]
        self.assertEqual(current_package["status"], "PASS")
        self.assertEqual(current_package["version"], "0.37.29-dev")
        self.assertEqual(current_package["files"], 54)
        self.assertEqual(current_package["pole_regression_tests"], 82)
        self.assertEqual(current_package["pole_regression_layout"], "direct_zip")
        self.assertEqual(current_package["pole_regression_validation"], "PASS")
        self.assertEqual(current_package["direct_zip_import_tests"], 12)
        self.assertEqual(current_package["foreground_steps"], 50)
        self.assertEqual(current_package["native_undo_redo"], "passed")
        self.assertTrue(current_package["claim_boundary_closed"])
        latest_package = gates["latest_fully_bound_dev_package"]
        self.assertEqual(latest_package["status"], "PASS")
        self.assertEqual(latest_package["version"], "0.37.42-dev")
        self.assertEqual(latest_package["files"], 54)
        self.assertEqual(
            latest_package["archive_sha256"],
            "e4099811be506e8a64e3585819d2d5d3af54259ece40974ec36d62b0498fc410",
        )
        self.assertEqual(latest_package["report_schema"], 27)
        self.assertEqual(
            latest_package["backend"],
            "implicit_selected_control_chain_location_moving_capsule_v1",
        )
        self.assertEqual(latest_package["package_regression_suites"], 8)
        self.assertEqual(latest_package["package_regression_tests"], 85)
        self.assertEqual(latest_package["host_independent_math_tests"], 46)
        self.assertEqual(latest_package["direct_zip_import_tests"], 12)
        self.assertEqual(latest_package["moving_deforming_mesh_tests"], 1)
        self.assertEqual(
            latest_package["moving_deforming_mesh_receipt"],
            "training/b4artists_ml/results/exact-package-v0.37.42-moving-deforming-mesh.json",
        )
        self.assertEqual(latest_package["production_character_generalization_tests"], 1)
        self.assertEqual(
            latest_package["production_character_generalization_receipt"],
            "training/b4artists_ml/results/exact-package-v0.37.42-production-character-generalization.json",
        )
        self.assertEqual(latest_package["continuous_moving_capsule_chain_tests"], 1)
        self.assertEqual(
            latest_package["continuous_moving_capsule_chain_receipt"],
            "training/b4artists_ml/results/exact-package-v0.37.42-continuous-moving-capsule-chain.json",
        )
        self.assertEqual(latest_package["continuous_moving_sphere_chain_tests"], 1)
        self.assertEqual(
            latest_package["continuous_moving_sphere_chain_receipt"],
            "training/b4artists_ml/results/exact-package-v0.37.42-continuous-moving-sphere-chain.json",
        )
        self.assertEqual(
            latest_package["production_character_generalization_scope"],
            "three frozen project-owned Unity Humanoid FBX characters",
        )
        self.assertEqual(latest_package["foreground_clearance_samples"], 22)
        self.assertEqual(latest_package["independent_code_review"], "NOT_BOUND")
        self.assertEqual(latest_package["package_evidence_review"], "NOT_REQUESTED")
        self.assertFalse(latest_package["promoted_or_installed"])
        self.assertTrue(latest_package["claim_boundary_closed"])
        self.assertEqual(gates["human_gates_handoff_surface"]["status"], "PASS_STATIC_READY")
        protocol = gates["cascadeur_comparison_protocol"]
        self.assertEqual(protocol["status"], "PASS_PROSPECTIVE")
        self.assertTrue(protocol["assets_frozen"])
        self.assertEqual(protocol["assets"], 3)
        self.assertEqual(protocol["tasks"], 8)
        self.assertEqual(protocol["matched_cases_per_animator"], 24)
        self.assertEqual(protocol["independent_animators_required"], 3)
        self.assertFalse(protocol["results_present"])
        self.assertFalse(protocol["conversion_verified"])
        self.assertFalse(protocol["parity_verified"])
        self.assertFalse(protocol["surpasses_verified"])
        self.assertTrue(protocol["claim_boundary_closed"])
        results_contract = gates["cascadeur_results_contract"]
        self.assertEqual(results_contract["status"], "BLOCKED_EXTERNAL_RESULTS_MISSING")
        self.assertFalse(results_contract["results_present"])
        self.assertFalse(results_contract["parity_verified"])
        self.assertFalse(results_contract["surpasses_verified"])
        self.assertTrue(results_contract["claim_boundary_closed"])
        self.assertFalse(gates["cascadeur_import_and_api"]["conversion_verified"])
        self.assertFalse(gates["cascadeur_import_and_api"]["parity_verified"])
        self.assertEqual(
            gates["cascadeur_import_and_api"]["ordinary_python_import_surface"],
            "BLOCKED_CSC_UNAVAILABLE",
        )
        self.assertEqual(
            gates["cascadeur_import_and_api"]["ordinary_python_standard_rig_surface"],
            "BLOCKED_CSC_UNAVAILABLE",
        )
        self.assertTrue(gates["cascadeur_import_and_api"]["diagnostic_claim_boundary_closed"])
        self.assertEqual(
            gates["cascadeur_import_and_api"]["command_wrapper_status"],
            "READY_FOR_EXPLICIT_DEPLOYMENT",
        )
        self.assertTrue(gates["cascadeur_import_and_api"]["command_wrapper_contract_verified"])
        self.assertFalse(gates["cascadeur_import_and_api"]["command_wrapper_mutation_performed"])
        self.assertEqual(
            gates["cascadeur_import_and_api"]["command_wrapper_bundle_status"],
            "STAGED",
        )
        self.assertTrue(gates["cascadeur_import_and_api"]["command_wrapper_bundle_staged"])
        self.assertIn(
            gates["cascadeur_import_and_api"]["command_wrapper_deployment_helper_status"],
            {"DRY_RUN_READY", "DEPLOYED", "PERMISSION_REQUIRED"},
        )
        self.assertTrue(gates["cascadeur_import_and_api"]["command_wrapper_deployment_helper_claims_closed"])
        self.assertGreaterEqual(
            gates["host_independent_regression_protection"]["collected"], 343
        )
        self.assertGreaterEqual(
            gates["host_independent_regression_protection"]["passed_calls"], 363
        )
        self.assertEqual(gates["standalone_boundary"]["status"], "PASS")
        self.assertTrue(gates["standalone_boundary"]["protected_addons_unchanged"])
        self.assertTrue(gates["standalone_boundary"]["bforartists_host_guard"])
        self.assertTrue(gates["standalone_boundary"]["runtime_dependency_absent"])
        for entry in report["evidence"].values():
            path = ROOT / entry["path"]
            self.assertTrue(path.is_file(), entry["path"])
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), entry["sha256"])


if __name__ == "__main__":
    unittest.main()
