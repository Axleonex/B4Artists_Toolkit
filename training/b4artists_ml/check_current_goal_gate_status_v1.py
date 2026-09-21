"""Validate the checksum-bound current B4ML goal-gate aggregation."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RECEIPT = ROOT / "training" / "b4artists_ml" / "results" / "current-goal-gate-status-v1.json"
OUTPUT = ROOT / "training" / "b4artists_ml" / "results" / "current-goal-gate-status-validation-v1.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    report = json.loads(RECEIPT.read_text(encoding="utf-8-sig"))
    if report.get("schema") != "b4ml-current-goal-gate-status-v1":
        raise ValueError("Unexpected goal-gate status schema")
    if report.get("goal_id") != "01a073fe-c240-70c0-b5cd-fe9653aac60e":
        raise ValueError("Unexpected inherited goal ID")
    if report.get("status") != "ACTIVE_INCOMPLETE" or report.get("full_goal_complete") is not False:
        raise ValueError("Goal status widened")
    claims = report.get("claim_boundary", {})
    if any(value is not False for value in claims.values()):
        raise ValueError("Claim boundary widened")
    for entry in report.get("evidence", {}).values():
        path = ROOT / entry["path"]
        if not path.is_file() or sha256(path) != entry["sha256"]:
            raise ValueError("Evidence changed: " + entry["path"])
    gates = report["gates"]
    if gates["capsule_exact_archive_binding"]["status"] != "PASS":
        raise ValueError("Exact capsule gate missing")
    if gates["capsule_foreground_lifecycle"]["status"] != "PASS":
        raise ValueError("Foreground capsule gate missing")
    evaluator = gates["capsule_evaluator_review"]
    if (evaluator["status"] != "PASS_FAIL_CLOSED"
            or evaluator["authority"] is not False
            or evaluator["evaluator_status"] != "BLOCKED_BEFORE_EVALUATION"
            or evaluator["preflight_status"] != "REMOTE_EXECUTOR_REQUIRED"
            or evaluator["advisory_verdict"] != "insufficient_evidence"
            or evaluator["reviewer_invoked"] is not False
            or evaluator["review_completed"] is not False
            or evaluator["deterministic_fallback"] != "PASS"):
        raise ValueError("Capsule evaluator/reviewer boundary changed")
    regression = gates["host_independent_regression_protection"]
    if (regression["status"] != "PASS"
            or regression["collected"] < 343
            or regression["passed_calls"] < 363):
        raise ValueError("Host-independent regression floor missing")
    standalone = gates["standalone_boundary"]
    if (standalone["status"] != "PASS"
            or standalone["protected_addons_unchanged"] is not True
            or standalone["bforartists_host_guard"] is not True
            or standalone["runtime_dependency_absent"] is not True):
        raise ValueError("Standalone boundary is not verified")
    if gates["temporal_training_boundary"]["status"] != "BLOCKED":
        raise ValueError("Temporal boundary no longer fail-closed")
    temporal = gates["temporal_training_boundary"]
    if (temporal["training_authorized"] is not False
            or temporal["intake_status"] != "BLOCKED_INTAKE_MISSING_EVIDENCE"
            or temporal["parent_receipt_status"] != "BLOCKED_DATA_BOUNDARY_UNQUALIFIED"
            or temporal["model_training_permitted"] is not False
            or temporal["model_promotion_permitted"] is not False
            or temporal["model_promoted"] is not False
            or temporal["claim_boundary_closed"] is not True):
        raise ValueError("Temporal child receipts are not directly bound fail-closed")
    if gates["independent_animator_review"]["status"] != "REQUIRED_EXTERNAL":
        raise ValueError("Human gate widened")
    human_review = gates["procedural_vertical_slice_human_review"]
    if (human_review["status"] != "PASS_REVIEWED_EXPORT"
            or human_review["reviewer_id"] != "Axlbot"
            or human_review["experience"] != "10+ years"
            or human_review["cases"] != 32
            or human_review["human_authored"] is not True
            or human_review["export_validated"] is not True
            or human_review["claim_boundary_closed"] is not True):
        raise ValueError("Procedural human-review export gate missing")
    head_orientation = gates["humanoid_head_orientation"]
    if (head_orientation["status"] != "PASS"
            or head_orientation["semantic_joint"] != 4
            or head_orientation["focused_tests"] != 10
            or len(head_orientation["fixtures"]) != 5
            or head_orientation["requested_orientations_per_fixture"] != 6
            or head_orientation["procedural_only"] is not True
            or head_orientation["claim_boundary_closed"] is not True):
        raise ValueError("Humanoid Head-orientation evidence gate failed")
    pole_status = gates["humanoid_pole_status"]
    if (pole_status["status"] != "PASS"
            or pole_status["focused_tests"] != 6
            or pole_status["affected_tests"] != 84
            or pole_status["read_only"] is not True
            or pole_status["claim_boundary_closed"] is not True):
        raise ValueError("Humanoid Pole Bend Status evidence gate failed")
    current_package = gates["current_dev_package"]
    if (current_package["status"] != "PASS"
            or current_package["version"] != "0.37.29-dev"
            or current_package["files"] != 54
            or current_package["pole_regression_tests"] != 82
            or current_package["pole_regression_layout"] != "direct_zip"
            or current_package["pole_regression_validation"] != "PASS"
            or current_package["direct_zip_import_tests"] != 12
            or current_package["foreground_steps"] != 50
            or current_package["native_undo_redo"] != "passed"
            or current_package["claim_boundary_closed"] is not True):
        raise ValueError("Current development package evidence gate failed")
    latest_package = gates["latest_fully_bound_dev_package"]
    if (latest_package["status"] != "PASS"
            or latest_package["version"] != "0.37.42-dev"
            or latest_package["files"] != 54
            or latest_package["archive_sha256"]
            != "e4099811be506e8a64e3585819d2d5d3af54259ece40974ec36d62b0498fc410"
            or latest_package["report_schema"] != 27
            or latest_package["backend"]
            != "implicit_selected_control_chain_location_moving_capsule_v1"
            or latest_package["package_regression_suites"] != 8
            or latest_package["package_regression_tests"] != 85
            or latest_package["host_independent_math_tests"] != 46
            or latest_package["direct_zip_import_tests"] != 12
            or latest_package["moving_deforming_mesh_tests"] != 1
            or latest_package["moving_deforming_mesh_receipt"]
                != "training/b4artists_ml/results/exact-package-v0.37.42-moving-deforming-mesh.json"
            or latest_package["coupled_pelvis_spine_tests"] != 11
            or latest_package["coupled_pelvis_spine_receipt"]
                != "training/b4artists_ml/results/exact-package-v0.37.42-test_b4artists_ml_body_controls.json"
            or latest_package["multiple_static_sphere_collision_tests"] != 8
            or latest_package["multiple_static_sphere_collision_receipt"]
                != "training/b4artists_ml/results/exact-package-v0.37.42-test_b4artists_ml_secondary_multi_sphere_collision_v1.json"
            or latest_package["force_offset_torque_tests"] != 14
            or latest_package["force_offset_torque_receipt"]
                != "training/b4artists_ml/results/exact-package-v0.37.42-test_b4artists_ml_secondary_force_offset_torque_v1.json"
            or latest_package["self_collision_tests"] != 2
            or latest_package["self_collision_receipt"]
                != "training/b4artists_ml/results/exact-package-v0.37.42-test_b4artists_ml_secondary_self_collision_v1.json"
            or latest_package["production_character_generalization_tests"] != 1
            or latest_package["production_character_generalization_receipt"]
                != "training/b4artists_ml/results/exact-package-v0.37.42-production-character-generalization.json"
            or latest_package["continuous_moving_sphere_chain_tests"] != 1
            or latest_package["continuous_moving_sphere_chain_receipt"]
                != "training/b4artists_ml/results/exact-package-v0.37.42-continuous-moving-sphere-chain.json"
            or latest_package["continuous_moving_capsule_chain_tests"] != 1
            or latest_package["continuous_moving_capsule_chain_receipt"]
                != "training/b4artists_ml/results/exact-package-v0.37.42-continuous-moving-capsule-chain.json"
            or latest_package["production_character_generalization_scope"]
            != "three frozen project-owned Unity Humanoid FBX characters"
            or latest_package["foreground_clearance_samples"] != 22
            or latest_package["independent_code_review"] != "NOT_BOUND"
            or latest_package["package_evidence_review"] != "NOT_REQUESTED"
            or latest_package["promoted_or_installed"] is not False
            or latest_package["claim_boundary_closed"] is not True):
        raise ValueError("Latest fully bound development package evidence gate failed")
    handoff = gates["human_gates_handoff_surface"]
    if (handoff["status"] != "PASS_STATIC_READY"
            or handoff["human_input_performed"] is not False
            or handoff["training_authorized"] is not False):
        raise ValueError("Handoff readiness crossed the human-evidence boundary")
    if gates["cascadeur_import_and_api"]["conversion_verified"] is not False:
        raise ValueError("Cascadeur conversion claim widened")
    cascadeur = gates["cascadeur_import_and_api"]
    if (cascadeur["ordinary_python_import_surface"] != "BLOCKED_CSC_UNAVAILABLE"
            or cascadeur["ordinary_python_standard_rig_surface"] != "BLOCKED_CSC_UNAVAILABLE"
            or cascadeur["diagnostic_claim_boundary_closed"] is not True
            or cascadeur["command_wrapper_status"] not in {
                "READY_FOR_EXPLICIT_DEPLOYMENT", "ALREADY_DEPLOYED"
            }
            or cascadeur["command_wrapper_contract_verified"] is not True
            or cascadeur["command_wrapper_mutation_performed"] is not False
            or cascadeur["command_wrapper_bundle_status"] != "STAGED"
            or cascadeur["command_wrapper_bundle_staged"] is not True
            or cascadeur["command_wrapper_deployment_helper_status"] not in {
                "DRY_RUN_READY", "DEPLOYED", "PERMISSION_REQUIRED"
            }
            or cascadeur["command_wrapper_deployment_helper_claims_closed"] is not True):
        raise ValueError("Cascadeur ordinary-Python diagnostic boundary changed")
    protocol = gates["cascadeur_comparison_protocol"]
    if (protocol["status"] != "PASS_PROSPECTIVE"
            or protocol["assets_frozen"] is not True
            or protocol["assets"] != 3
            or protocol["tasks"] != 8
            or protocol["matched_cases_per_animator"] != 24
            or protocol["independent_animators_required"] != 3
            or protocol["results_present"] is not False
            or protocol["conversion_verified"] is not False
            or protocol["parity_verified"] is not False
            or protocol["surpasses_verified"] is not False
            or protocol["claim_boundary_closed"] is not True):
        raise ValueError("Cascadeur prospective protocol boundary changed")
    results_contract = gates["cascadeur_results_contract"]
    if (results_contract["status"] not in {
            "BLOCKED_EXTERNAL_RESULTS_MISSING",
            "RESULTS_PRESENT_INVALID",
            "PASS_CONTRACT_ONLY",
        }
            or results_contract["parity_verified"] is not False
            or results_contract["surpasses_verified"] is not False
            or results_contract["claim_boundary_closed"] is not True):
        raise ValueError("Cascadeur result-contract boundary changed")
    validation = {
        "schema": "b4ml-current-goal-gate-status-validation-v1",
        "status": "PASS",
        "receipt": RECEIPT.relative_to(ROOT).as_posix(),
        "receipt_sha256": sha256(RECEIPT),
        "full_goal_complete": False,
        "temporal_boundary": "BLOCKED",
        "human_review": "REQUIRED_EXTERNAL",
        "cascadeur_conversion": False,
        "cascadeur_parity": False,
    }
    OUTPUT.write_text(json.dumps(validation, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, indent=2))


if __name__ == "__main__":
    main()
