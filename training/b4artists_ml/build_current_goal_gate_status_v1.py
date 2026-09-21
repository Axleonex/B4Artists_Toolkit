"""Aggregate current B4ML goal-gate evidence without widening any claim."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "training" / "b4artists_ml" / "results"
OUTPUT = RESULTS / "current-goal-gate-status-v1.json"

EVIDENCE = {
    "capsule_exact_archive": "docs/b4artists_ml/capsule-exact-archive-binding-v1.json",
    "capsule_foreground": "docs/b4artists_ml/capsule-ui-exact-checkpoint-v1.json",
    "capsule_current_regression": "training/b4artists_ml/results/current-capsule-regression-v2.json",
    "capsule_routing": "docs/b4artists_ml/CAPSULE-ROUTING-RECEIPT-v1.json",
    "capsule_advisory_review": "docs/b4artists_ml/CAPSULE-PRIME-ADVISORY-REVIEW-v1.json",
    "capsule_governed_retry": "docs/b4artists_ml/CAPSULE-GOVERNED-EVALUATOR-RETRY-v2.json",
    "imported_humanoids": "training/b4artists_ml/results/current-imported-humanoids-recheck-validation-v1.json",
    "mapping_corrections": "training/b4artists_ml/results/current-mapping-corrections-recheck-validation-v2.json",
    "head_orientation": "training/b4artists_ml/results/head-orientation-evidence-v1.json",
    "pole_status_affected": "training/b4artists_ml/results/pole-status-affected-v2-regression.json",
    "pole_status_shared": "training/b4artists_ml/results/pole-status-shared-v2-regression.json",
    "current_dev_package": "docs/b4artists_ml/package-test-v0.37.29-dev.json",
    "latest_dev_package": "docs/b4artists_ml/package-test-v0.37.42-dev.json",
    "latest_package_regression": "training/b4artists_ml/results/exact-package-pole-v0.37.42.json",
    "latest_package_direct_zip_import": "training/b4artists_ml/results/current-package-direct-zip-import-v0.37.42.json",
    "latest_package_foreground": "training/b4artists_ml/results/secondary-world-chain-moving-capsule-foreground-v0.37.42.json",
    "latest_package_moving_deforming_mesh": "training/b4artists_ml/results/exact-package-v0.37.42-moving-deforming-mesh.json",
    "latest_package_coupled_pelvis_spine": "training/b4artists_ml/results/exact-package-v0.37.42-test_b4artists_ml_body_controls.json",
    "latest_package_multiple_static_spheres": "training/b4artists_ml/results/exact-package-v0.37.42-test_b4artists_ml_secondary_multi_sphere_collision_v1.json",
    "latest_package_force_offset_torque": "training/b4artists_ml/results/exact-package-v0.37.42-test_b4artists_ml_secondary_force_offset_torque_v1.json",
    "latest_package_self_collision": "training/b4artists_ml/results/exact-package-v0.37.42-test_b4artists_ml_secondary_self_collision_v1.json",
    "latest_package_production_generalization": "training/b4artists_ml/results/exact-package-v0.37.42-production-character-generalization.json",
    "latest_package_continuous_capsule": "training/b4artists_ml/results/exact-package-v0.37.42-continuous-moving-capsule-chain.json",
    "latest_package_continuous_sphere": "training/b4artists_ml/results/exact-package-v0.37.42-continuous-moving-sphere-chain.json",
    "current_compound_package_regression": "training/b4artists_ml/results/exact-package-pole-v0.37.43.json",
    "current_package_pole_regression": "training/b4artists_ml/results/current-zip-pole-v2-regression.json",
    "current_package_pole_validation": "training/b4artists_ml/results/current-package-direct-zip-pole-validation-v1.json",
    "current_package_direct_zip_import": "training/b4artists_ml/results/current-package-direct-zip-import-v3.json",
    "current_package_foreground_modal": "docs/b4artists_ml/capsule-ui-v0.37.29-package-modal.json",
    "current_package_foreground_modal_validation": "training/b4artists_ml/results/current-package-foreground-modal-validation-v1.json",
    "quadruped": "training/b4artists_ml/results/quadruped-gait-v1-final.json",
    "host_independent_regression": "training/b4artists_ml/results/host-independent-regression-validation-v1.json",
    "standalone_boundary": "training/b4artists_ml/results/standalone-boundary-validation-v1.json",
    "temporal_boundary": "docs/b4artists_ml/temporal-boundary-revalidation-v2.json",
    "temporal_intake": "training/b4artists_ml/results/temporal-corpus-intake-v1.json",
    "temporal_training_boundary": "training/b4artists_ml/results/temporal-training-boundary-v1.json",
    "reviewer_handoff": "training/b4artists_ml/results/reviewer-handoff-surface-v2.json",
    "human_gates_handoff": "training/b4artists_ml/results/human-gates-handoff-validation-v1.json",
    "human_review_export": "training/b4artists_ml/results/human-review-exports/b4ml-procedural-vertical-slice-human-review-v2-axlbot.json",
    "human_review_summary": "training/b4artists_ml/results/procedural-vertical-slice-reviewer-v2/human-review-summary-v2.json",
    "cascadeur_protocol": "training/b4artists_ml/cascadeur_comparison_protocol_v2.json",
    "cascadeur_protocol_validation": "training/b4artists_ml/results/cascadeur-comparison-protocol-validation-v3.json",
    "cascadeur_results_contract": "training/b4artists_ml/results/cascadeur-comparison-results-contract-v1.json",
    "cascadeur_import": "training/b4artists_ml/results/cascadeur-import-audit-v1.json",
    "cascadeur_capability": "training/b4artists_ml/results/cascadeur-capability-probe-validation-v1.json",
    "cascadeur_import_diagnostic": "training/b4artists_ml/results/cascadeur-import-audit-diagnostic-v1.json",
    "cascadeur_standard_rig_diagnostic": "training/b4artists_ml/results/cascadeur-standard-rig-preflight-diagnostic-v1.json",
    "cascadeur_wrapper_readiness": "training/b4artists_ml/results/cascadeur-command-wrapper-readiness-v1.json",
    "cascadeur_wrapper_bundle": "training/b4artists_ml/results/cascadeur-command-wrapper-bundle-v1/manifest.json",
    "cascadeur_wrapper_deployment": "training/b4artists_ml/results/cascadeur-command-wrapper-deployment-v1.json",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(relative: str) -> tuple[Path, dict]:
    path = ROOT / relative
    if not path.is_file():
        raise FileNotFoundError(path)
    return path, json.loads(path.read_text(encoding="utf-8-sig"))


def main() -> None:
    loaded = {key: read(relative) for key, relative in EVIDENCE.items()}
    exact = loaded["capsule_exact_archive"][1]
    foreground = loaded["capsule_foreground"][1]
    current_capsule = loaded["capsule_current_regression"][1]
    capsule_routing = loaded["capsule_routing"][1]
    capsule_advisory_review = loaded["capsule_advisory_review"][1]
    capsule_governed_retry = loaded["capsule_governed_retry"][1]
    imported = loaded["imported_humanoids"][1]
    mapping = loaded["mapping_corrections"][1]
    head_orientation = loaded["head_orientation"][1]
    pole_status_affected = loaded["pole_status_affected"][1]
    pole_status_shared = loaded["pole_status_shared"][1]
    current_dev_package = loaded["current_dev_package"][1]
    latest_dev_package = loaded["latest_dev_package"][1]
    latest_package_regression = loaded["latest_package_regression"][1]
    latest_package_direct_zip_import = loaded["latest_package_direct_zip_import"][1]
    latest_package_foreground = loaded["latest_package_foreground"][1]
    latest_package_moving_deforming_mesh = loaded[
        "latest_package_moving_deforming_mesh"
    ][1]
    latest_package_coupled_pelvis_spine = loaded[
        "latest_package_coupled_pelvis_spine"
    ][1]
    latest_package_multiple_static_spheres = loaded[
        "latest_package_multiple_static_spheres"
    ][1]
    latest_package_force_offset_torque = loaded[
        "latest_package_force_offset_torque"
    ][1]
    latest_package_self_collision = loaded[
        "latest_package_self_collision"
    ][1]
    latest_package_production_generalization = loaded[
        "latest_package_production_generalization"
    ][1]
    latest_package_continuous_capsule = loaded[
        "latest_package_continuous_capsule"
    ][1]
    latest_package_continuous_sphere = loaded[
        "latest_package_continuous_sphere"
    ][1]
    current_package_pole_regression = loaded["current_package_pole_regression"][1]
    current_package_pole_validation = loaded["current_package_pole_validation"][1]
    current_package_direct_zip_import = loaded["current_package_direct_zip_import"][1]
    current_package_foreground_modal = loaded["current_package_foreground_modal"][1]
    current_package_foreground_modal_validation = loaded["current_package_foreground_modal_validation"][1]
    quadruped = loaded["quadruped"][1]
    host_independent = loaded["host_independent_regression"][1]
    standalone = loaded["standalone_boundary"][1]
    temporal = loaded["temporal_boundary"][1]
    temporal_intake = loaded["temporal_intake"][1]
    temporal_training_boundary = loaded["temporal_training_boundary"][1]
    reviewer = loaded["reviewer_handoff"][1]
    handoff = loaded["human_gates_handoff"][1]
    human_review_export = loaded["human_review_export"][1]
    human_review_summary = loaded["human_review_summary"][1]
    cascadeur_import = loaded["cascadeur_import"][1]
    cascadeur_capability = loaded["cascadeur_capability"][1]
    cascadeur_import_diagnostic = loaded["cascadeur_import_diagnostic"][1]
    cascadeur_standard_rig_diagnostic = loaded["cascadeur_standard_rig_diagnostic"][1]
    cascadeur_wrapper = loaded["cascadeur_wrapper_readiness"][1]
    cascadeur_bundle = loaded["cascadeur_wrapper_bundle"][1]
    cascadeur_deployment = loaded["cascadeur_wrapper_deployment"][1]
    cascadeur_protocol = loaded["cascadeur_protocol"][1]
    cascadeur_protocol_validation = loaded["cascadeur_protocol_validation"][1]
    cascadeur_results_contract = loaded["cascadeur_results_contract"][1]

    capsule_exact_pass = exact["result"]["was_successful"] and exact["result"]["tests"] == 2
    capsule_foreground_pass = foreground["passed"] is True
    current_capsule_pass = (
        current_capsule["result"]["was_successful"]
        and current_capsule["result"]["tests"] == 157
        and current_capsule["result"]["passed"] == 157
    )
    evaluator_review_fail_closed = (
        capsule_routing.get("evaluator_gate", {}).get("status") == "BLOCKED_BEFORE_EVALUATION"
        and capsule_routing.get("evaluator_gate", {}).get("authority") is False
        and capsule_routing.get("evaluator_gate", {}).get("fallback_deterministic_validation") == "PASS"
        and capsule_routing.get("latest_preflight", {}).get("status") == "REMOTE_EXECUTOR_REQUIRED"
        and capsule_routing.get("latest_preflight", {}).get("outcome") == "blocked"
        and capsule_advisory_review.get("status") == "completed"
        and capsule_advisory_review.get("verdict") == "insufficient_evidence"
        and capsule_advisory_review.get("authority") is False
        and capsule_advisory_review.get("claim_boundary", {}).get("full_goal_complete") is False
        and capsule_governed_retry.get("outcome", {}).get("status") == "BLOCKED_BEFORE_EVALUATION"
        and capsule_governed_retry.get("outcome", {}).get("reviewer_invoked") is False
        and capsule_governed_retry.get("outcome", {}).get("review_completed") is False
        and capsule_governed_retry.get("outcome", {}).get("authority") is False
        and capsule_governed_retry.get("impact", {}).get("source_changed") is False
    )
    imported_pass = imported["status"] == "PASS" and imported["imported_humanoid_workflow_verified"] is True
    mapping_pass = (
        mapping["status"] == "PASS"
        and mapping["tests"] == 11
        and len(mapping["adapters"]) == 6
    )
    head_orientation_pass = (
        head_orientation.get("schema") == "b4ml-head-orientation-evidence-v1"
        and head_orientation.get("status") == "PASS"
        and head_orientation.get("semantic_target", {}).get("label") == "Head"
        and head_orientation.get("semantic_target", {}).get("joint_index") == 4
        and head_orientation.get("coverage", {}).get("tests") == 10
        and len(head_orientation.get("coverage", {}).get("fixtures", [])) == 5
        and head_orientation.get("coverage", {}).get("requested_orientations_per_fixture") == 6
        and head_orientation.get("claim_boundary", {}).get("procedural_evaluated_rig_constraint") is True
        and head_orientation.get("claim_boundary", {}).get("learned_temporal_quality_verified") is False
        and head_orientation.get("claim_boundary", {}).get("full_goal_complete") is False
    )
    # The historical affected/shared pole receipts predate the current UI
    # surface and therefore retain an older ui.py hash.  Use the exact-package
    # pole receipt from the current development archive for the live gate so
    # the status is bound to the current source bytes.
    current_compound_package_regression = loaded[
        "current_compound_package_regression"
    ][1]
    pole_status_entries = list(current_compound_package_regression.get("rows", []))
    pole_status_pass = (
        len(pole_status_entries) == 8
        and sum(entry.get("tests", 0) for entry in pole_status_entries) == 85
        and all(
            entry.get("assertions_passed") is True
            and not entry.get("failures")
            and not entry.get("errors")
            and not entry.get("skipped")
            and entry.get("runtime_sha256", {}).get("b4artists_ml/body_preview.py")
            == sha256(ROOT / "b4artists_ml/body_preview.py")
            and entry.get("runtime_sha256", {}).get("b4artists_ml/ui.py")
            == sha256(ROOT / "b4artists_ml/ui.py")
            for entry in pole_status_entries
        )
        and any(
            entry.get("suite") == "test_b4artists_ml_pole_align_v1"
            and entry.get("tests") == 6
            for entry in pole_status_entries
        )
    )
    current_package_pole_entries = list(current_package_pole_regression)
    expected_direct_zip_runtime = {
        name: current_dev_package.get("runtime_sha256", {}).get(name)
        for name in (
            "b4artists_ml/posing.py",
            "b4artists_ml/workflow.py",
            "b4artists_ml/body_solver.py",
        )
    }
    current_package_direct_zip_pass = (
        current_package_direct_zip_import.get("tests") == 12
        and current_package_direct_zip_import.get("assertions_passed") is True
        and not current_package_direct_zip_import.get("failures")
        and not current_package_direct_zip_import.get("errors")
        and not current_package_direct_zip_import.get("skipped")
        and all(expected_direct_zip_runtime.values())
        and current_package_direct_zip_import.get("runtime_sha256")
        == expected_direct_zip_runtime
    )
    current_dev_package_pass = (
        current_dev_package.get("version") == "0.37.29-dev"
        and current_dev_package.get("files") == 54
        and current_dev_package.get("package_matches_source") is True
        and current_dev_package.get("full_goal_complete") is False
        and current_dev_package.get("sha256") == sha256(ROOT / "releases/b4artists_ml_v0.37.29-dev.zip")
        and len(current_package_pole_entries) == 8
        and sum(entry.get("tests", 0) for entry in current_package_pole_entries) == 82
        and all(
            entry.get("assertions_passed") is True
            and not entry.get("failures")
            and not entry.get("errors")
            and not entry.get("skipped")
            for entry in current_package_pole_entries
        )
        and current_package_pole_validation.get("status") == "PASS"
        and current_package_pole_validation.get("archive_sha256") == current_dev_package.get("sha256")
        and current_package_pole_validation.get("tests") == 82
        and current_package_pole_validation.get("claim_boundary_closed") is True
        and current_package_direct_zip_pass
        and current_package_foreground_modal.get("passed") is True
        and current_package_foreground_modal.get("package_sha256") == current_dev_package.get("sha256")
        and current_package_foreground_modal.get("native_undo_redo", {}).get("status") == "passed"
        and current_package_foreground_modal_validation.get("status") == "PASS"
        and current_package_foreground_modal_validation.get("archive_sha256") == current_dev_package.get("sha256")
        and current_package_foreground_modal_validation.get("claim_boundary_closed") is True
    )
    latest_dev_package_pass = (
        latest_dev_package.get("version") == "0.37.42-dev"
        and latest_dev_package.get("files") == 54
        and latest_dev_package.get("package_matches_source") is True
        and latest_dev_package.get("ready_for_local_testing") is True
        and latest_dev_package.get("full_goal_complete") is False
        and latest_dev_package.get("sha256")
        == sha256(ROOT / "releases/b4artists_ml_v0.37.42-dev.zip")
        and latest_dev_package.get("package_regression_receipt")
        == EVIDENCE["latest_package_regression"]
        and latest_dev_package.get("package_regression_receipt_sha256")
        == sha256(loaded["latest_package_regression"][0])
        and latest_dev_package.get("package_regression_tests") == 85
        and latest_dev_package.get("package_regression_suites") == 8
        and latest_dev_package.get("package_regression_claim_boundary_closed") is True
        and latest_package_regression.get("status") == "PASS"
        and latest_package_regression.get("archive_sha256") == latest_dev_package.get("sha256")
        and latest_package_regression.get("suites") == 8
        and latest_package_regression.get("tests") == 85
        and latest_package_regression.get("claim_boundary_closed") is True
        and all(
            row.get("assertions_passed") is True
            and not row.get("failures")
            and not row.get("errors")
            and not row.get("skipped")
            and row.get("package_sha256") == latest_dev_package.get("sha256")
            for row in latest_package_regression.get("rows", [])
        )
        and latest_dev_package.get("direct_zip_import_regression_receipt")
        == EVIDENCE["latest_package_direct_zip_import"]
        and latest_dev_package.get("foreground_receipt_sha256")
        == sha256(loaded["latest_package_foreground"][0])
        and latest_dev_package.get("foreground_receipt")
        == EVIDENCE["latest_package_foreground"]
        and latest_package_direct_zip_import.get("tests") == 12
        and latest_package_direct_zip_import.get("assertions_passed") is True
        and not latest_package_direct_zip_import.get("failures")
        and not latest_package_direct_zip_import.get("errors")
        and not latest_package_direct_zip_import.get("skipped")
        and latest_package_direct_zip_import.get("archive_sha256") == latest_dev_package.get("sha256")
        and latest_dev_package.get("direct_zip_import_tests") == 12
        and latest_dev_package.get("moving_deforming_mesh_receipt")
        == EVIDENCE["latest_package_moving_deforming_mesh"]
        and latest_dev_package.get("moving_deforming_mesh_receipt_sha256")
        == sha256(loaded["latest_package_moving_deforming_mesh"][0])
        and latest_dev_package.get("moving_deforming_mesh_tests") == 1
        and latest_package_moving_deforming_mesh.get("schema")
        == "b4ml-exact-package-unittest-v1"
        and latest_package_moving_deforming_mesh.get("class_name")
        == "SecondaryMotionTests.test_coupled_world_location_chain_moving_deforming_mesh_collision"
        and latest_package_moving_deforming_mesh.get("tests") == 1
        and latest_package_moving_deforming_mesh.get("assertions_passed") is True
        and not latest_package_moving_deforming_mesh.get("failures")
        and not latest_package_moving_deforming_mesh.get("errors")
        and not latest_package_moving_deforming_mesh.get("skipped")
        and latest_package_moving_deforming_mesh.get("package_sha256")
        == latest_dev_package.get("sha256")
        and latest_dev_package.get("coupled_pelvis_spine_receipt")
        == EVIDENCE["latest_package_coupled_pelvis_spine"]
        and latest_dev_package.get("coupled_pelvis_spine_receipt_sha256")
        == sha256(loaded["latest_package_coupled_pelvis_spine"][0])
        and latest_dev_package.get("coupled_pelvis_spine_tests") == 11
        and latest_package_coupled_pelvis_spine.get("schema")
        == "b4ml-exact-package-unittest-v1"
        and latest_package_coupled_pelvis_spine.get("suite")
        == "test_b4artists_ml_body_controls"
        and latest_package_coupled_pelvis_spine.get("class_name")
        == "BodyControlTests"
        and latest_package_coupled_pelvis_spine.get("tests") == 11
        and latest_package_coupled_pelvis_spine.get("assertions_passed") is True
        and not latest_package_coupled_pelvis_spine.get("failures")
        and not latest_package_coupled_pelvis_spine.get("errors")
        and not latest_package_coupled_pelvis_spine.get("skipped")
        and latest_package_coupled_pelvis_spine.get("package_sha256")
        == latest_dev_package.get("sha256")
        and latest_dev_package.get("multiple_static_sphere_collision_receipt")
        == EVIDENCE["latest_package_multiple_static_spheres"]
        and latest_dev_package.get("multiple_static_sphere_collision_receipt_sha256")
        == sha256(loaded["latest_package_multiple_static_spheres"][0])
        and latest_dev_package.get("multiple_static_sphere_collision_tests") == 8
        and latest_package_multiple_static_spheres.get("schema")
        == "b4ml-exact-package-unittest-v1"
        and latest_package_multiple_static_spheres.get("suite")
        == "test_b4artists_ml_secondary_multi_sphere_collision_v1"
        and latest_package_multiple_static_spheres.get("class_name")
        == "SecondaryMultiSphereCollisionTests"
        and latest_package_multiple_static_spheres.get("tests") == 8
        and latest_package_multiple_static_spheres.get("assertions_passed") is True
        and not latest_package_multiple_static_spheres.get("failures")
        and not latest_package_multiple_static_spheres.get("errors")
        and not latest_package_multiple_static_spheres.get("skipped")
        and latest_package_multiple_static_spheres.get("package_sha256")
        == latest_dev_package.get("sha256")
        and latest_dev_package.get("force_offset_torque_receipt")
        == EVIDENCE["latest_package_force_offset_torque"]
        and latest_dev_package.get("force_offset_torque_receipt_sha256")
        == sha256(loaded["latest_package_force_offset_torque"][0])
        and latest_dev_package.get("force_offset_torque_tests") == 14
        and latest_package_force_offset_torque.get("schema")
        == "b4ml-exact-package-unittest-v1"
        and latest_package_force_offset_torque.get("suite")
        == "test_b4artists_ml_secondary_force_offset_torque_v1"
        and latest_package_force_offset_torque.get("class_name")
        == "SecondaryForceOffsetTorqueTests"
        and latest_package_force_offset_torque.get("tests") == 14
        and latest_package_force_offset_torque.get("assertions_passed") is True
        and not latest_package_force_offset_torque.get("failures")
        and not latest_package_force_offset_torque.get("errors")
        and not latest_package_force_offset_torque.get("skipped")
        and latest_package_force_offset_torque.get("package_sha256")
        == latest_dev_package.get("sha256")
        and latest_dev_package.get("self_collision_receipt")
        == EVIDENCE["latest_package_self_collision"]
        and latest_dev_package.get("self_collision_receipt_sha256")
        == sha256(loaded["latest_package_self_collision"][0])
        and latest_dev_package.get("self_collision_tests") == 2
        and latest_package_self_collision.get("schema")
        == "b4ml-exact-package-unittest-v1"
        and latest_package_self_collision.get("suite")
        == "test_b4artists_ml_secondary_self_collision_v1"
        and latest_package_self_collision.get("class_name")
        == "SecondarySelfCollisionBindingTests"
        and latest_package_self_collision.get("tests") == 2
        and latest_package_self_collision.get("assertions_passed") is True
        and not latest_package_self_collision.get("failures")
        and not latest_package_self_collision.get("errors")
        and not latest_package_self_collision.get("skipped")
        and latest_package_self_collision.get("package_sha256")
        == latest_dev_package.get("sha256")
        and latest_dev_package.get("production_character_generalization_receipt")
        == EVIDENCE["latest_package_production_generalization"]
        and latest_dev_package.get("production_character_generalization_receipt_sha256")
        == sha256(loaded["latest_package_production_generalization"][0])
        and latest_dev_package.get("production_character_generalization_tests") == 1
        and latest_dev_package.get("production_character_generalization_scope")
        == "three frozen project-owned Unity Humanoid FBX characters"
        and latest_package_production_generalization.get("schema")
        == "b4ml-exact-package-unittest-v1"
        and latest_package_production_generalization.get("suite")
        == "test_b4artists_ml_production_character_generalization_v1"
        and latest_package_production_generalization.get("tests") == 1
        and latest_package_production_generalization.get("assertions_passed") is True
        and not latest_package_production_generalization.get("failures")
        and not latest_package_production_generalization.get("errors")
        and not latest_package_production_generalization.get("skipped")
        and latest_package_production_generalization.get("package_sha256")
        == latest_dev_package.get("sha256")
        and latest_dev_package.get("continuous_moving_capsule_chain_receipt")
        == EVIDENCE["latest_package_continuous_capsule"]
        and latest_dev_package.get("continuous_moving_capsule_chain_receipt_sha256")
        == sha256(loaded["latest_package_continuous_capsule"][0])
        and latest_dev_package.get("continuous_moving_capsule_chain_tests") == 1
        and latest_package_continuous_capsule.get("schema")
        == "b4ml-exact-package-unittest-v1"
        and latest_package_continuous_capsule.get("class_name")
        == "SecondaryMotionTests.test_coupled_world_location_chain_resolves_continuous_moving_capsule"
        and latest_package_continuous_capsule.get("tests") == 1
        and latest_package_continuous_capsule.get("assertions_passed") is True
        and not latest_package_continuous_capsule.get("failures")
        and not latest_package_continuous_capsule.get("errors")
        and not latest_package_continuous_capsule.get("skipped")
        and latest_package_continuous_capsule.get("package_sha256")
        == latest_dev_package.get("sha256")
        and latest_dev_package.get("continuous_moving_sphere_chain_receipt")
        == EVIDENCE["latest_package_continuous_sphere"]
        and latest_dev_package.get("continuous_moving_sphere_chain_receipt_sha256")
        == sha256(loaded["latest_package_continuous_sphere"][0])
        and latest_dev_package.get("continuous_moving_sphere_chain_tests") == 1
        and latest_package_continuous_sphere.get("schema")
        == "b4ml-exact-package-unittest-v1"
        and latest_package_continuous_sphere.get("class_name")
        == "SecondaryMotionTests.test_coupled_world_location_chain_continuous_moving_sphere"
        and latest_package_continuous_sphere.get("tests") == 1
        and latest_package_continuous_sphere.get("assertions_passed") is True
        and not latest_package_continuous_sphere.get("failures")
        and not latest_package_continuous_sphere.get("errors")
        and not latest_package_continuous_sphere.get("skipped")
        and latest_package_continuous_sphere.get("package_sha256")
        == latest_dev_package.get("sha256")
        and latest_package_foreground.get("passed") is True
        and latest_package_foreground.get("archive_sha256")
        == latest_dev_package.get("sha256")
        and latest_package_foreground.get("metrics", {}).get("schema") == 27
        and latest_package_foreground.get("metrics", {}).get("backend")
        == "implicit_selected_control_chain_location_moving_capsule_v1"
        and latest_package_foreground.get("independent_clearance", {}).get("passed") is True
        and latest_package_foreground.get("independent_clearance", {}).get("samples") == 22
        and latest_package_foreground.get("screenshot_semantic_verification")
        == "manual_review_required"
        and latest_package_foreground.get("learned_temporal_quality") is False
        and latest_package_foreground.get("independent_animator_usability") is False
        and latest_package_foreground.get("cascadeur_comparison") is False
        and latest_dev_package.get("review_gate", {}).get("status") == "NOT_REQUESTED"
    )
    quadruped_pass = (
        quadruped["passed"] is True
        and quadruped["focused"]["tests"] == 5
        and quadruped["affected"]["tests"] == 99
    )
    host_independent_pass = (
        host_independent["status"] == "PASS"
        and host_independent["collected"] >= 343
        and host_independent["passed_calls"] >= 363
        and host_independent["full_goal_complete"] is False
    )
    standalone_pass = (
        standalone["status"] == "PASS"
        and standalone["protected_addons"]["unchanged"] is True
        and standalone["b4ml_runtime"]["host_guard"]["is_bforartists_function"] is True
        and standalone["b4ml_runtime"]["host_guard"]["bforartists_host_tokens"] is True
        and standalone["b4ml_runtime"]["host_guard"]["runtime_dependency_absent"] is True
        and standalone["claims"]["full_goal_complete"] is False
    )
    temporal_blocked = (
        temporal["status"] == "PASS_FAIL_CLOSED"
        and temporal["current_intake"]["status"] == "BLOCKED_INTAKE_MISSING_EVIDENCE"
        and temporal["parent_boundary"]["status"] == "BLOCKED_DATA_BOUNDARY_UNQUALIFIED"
        and temporal_intake["status"] == "BLOCKED_INTAKE_MISSING_EVIDENCE"
        and temporal_intake["training_authorized"] is False
        and temporal_intake["model_training_permitted"] is False
        and temporal_intake["model_promoted"] is False
        and temporal_intake["qualified_for_parent_boundary"] is False
        and temporal_training_boundary["status"] == "BLOCKED_DATA_BOUNDARY_UNQUALIFIED"
        and temporal_training_boundary["model_training_permitted"] is False
        and temporal_training_boundary["model_promotion_permitted"] is False
        and all(value is False for value in temporal_training_boundary["claim_boundary"].values())
    )
    handoff_ready = (
        handoff["status"] == "PASS"
        and handoff["human_input_performed"] is False
        and handoff["training_authorized"] is False
        and handoff["full_goal_complete"] is False
    )
    human_review_pass = (
        human_review_export.get("schema") == "b4ml-procedural-vertical-slice-human-review-v2"
        and human_review_export.get("human_authored") is True
        and isinstance(human_review_export.get("reviewer"), dict)
        and isinstance(human_review_export["reviewer"].get("id"), str)
        and human_review_export["reviewer"]["id"].strip()
        and human_review_export["reviewer"].get("experience") == "10+ years"
        and isinstance(human_review_export.get("exported_utc"), str)
        and len(human_review_export.get("cases", [])) == 32
        and all(case.get("rating", {}).get("locked") is True for case in human_review_export["cases"])
        and human_review_summary.get("complete") is True
        and human_review_summary.get("human_review_export_validated") is True
        and human_review_summary.get("cases") == 32
        and human_review_summary.get("reviewer") == human_review_export["reviewer"]
        and human_review_summary.get("source_data_sha256") == human_review_export.get("source_data_sha256")
        and human_review_summary.get("full_goal_complete") is False
    )
    cascadeur_import_pass = (
        cascadeur_import["status"] == "PASS"
        and cascadeur_import["all_hashes_match"] is True
        and cascadeur_import["parity_verified"] is False
    )
    cascadeur_capability_pass = (
        cascadeur_capability["status"] == "PASS"
        and cascadeur_capability["conversion_attempted"] is False
        and cascadeur_capability["parity_verified"] is False
    )
    cascadeur_diagnostics_pass = (
        cascadeur_import_diagnostic.get("status") == "BLOCKED_CSC_UNAVAILABLE"
        and cascadeur_import_diagnostic.get("claim_boundary", {}).get("cascadeur_import_verified") is False
        and cascadeur_import_diagnostic.get("claim_boundary", {}).get("conversion_verified") is False
        and cascadeur_import_diagnostic.get("claim_boundary", {}).get("parity_verified") is False
        and cascadeur_import_diagnostic.get("claim_boundary", {}).get("surpasses_verified") is False
        and cascadeur_import_diagnostic.get("claim_boundary", {}).get("full_goal_complete") is False
        and cascadeur_standard_rig_diagnostic.get("status") == "BLOCKED_CSC_UNAVAILABLE"
        and cascadeur_standard_rig_diagnostic.get("claim_boundary", {}).get("import_verified") is False
        and cascadeur_standard_rig_diagnostic.get("claim_boundary", {}).get("conversion_verified") is False
        and cascadeur_standard_rig_diagnostic.get("claim_boundary", {}).get("standard_rig_converted") is False
        and cascadeur_standard_rig_diagnostic.get("claim_boundary", {}).get("animation_tested") is False
        and cascadeur_standard_rig_diagnostic.get("claim_boundary", {}).get("settings_exported") is False
        and cascadeur_standard_rig_diagnostic.get("claim_boundary", {}).get("parity_verified") is False
        and cascadeur_standard_rig_diagnostic.get("claim_boundary", {}).get("full_goal_complete") is False
    )
    cascadeur_wrapper_pass = (
        cascadeur_wrapper.get("status") in {
            "READY_FOR_EXPLICIT_DEPLOYMENT", "ALREADY_DEPLOYED"
        }
        and cascadeur_wrapper.get("mutation_performed") is False
        and cascadeur_wrapper.get("wrapper_contract", {}).get("command_name_function") is True
        and cascadeur_wrapper.get("wrapper_contract", {}).get("run_function") is True
        and cascadeur_wrapper.get("wrapper_contract", {}).get("name_function") is True
        and cascadeur_wrapper.get("wrapper_contract", {}).get("description_function") is True
        and cascadeur_wrapper.get("wrapper_contract", {}).get("imports_console_audit") is True
        and cascadeur_wrapper.get("wrapper_contract", {}).get("sets_exit_boundary") is True
        and cascadeur_wrapper.get("claims", {}).get("wrapper_contract_verified") is True
        and cascadeur_wrapper.get("claims", {}).get("cascadeur_import_verified") is False
        and cascadeur_wrapper.get("claims", {}).get("conversion_verified") is False
        and cascadeur_wrapper.get("claims", {}).get("parity_verified") is False
        and cascadeur_wrapper.get("claims", {}).get("full_goal_complete") is False
    )
    cascadeur_bundle_pass = (
        cascadeur_bundle.get("status") == "STAGED"
        and cascadeur_bundle.get("installed_mutation_performed") is False
        and cascadeur_bundle.get("claims", {}).get("wrapper_contract_verified") is True
        and cascadeur_bundle.get("claims", {}).get("deployment_verified") is False
        and cascadeur_bundle.get("claims", {}).get("cascadeur_import_verified") is False
        and cascadeur_bundle.get("claims", {}).get("conversion_verified") is False
        and cascadeur_bundle.get("claims", {}).get("parity_verified") is False
        and cascadeur_bundle.get("claims", {}).get("full_goal_complete") is False
        and all(
            file_report.get("source_sha256") == file_report.get("bundle_sha256")
            for file_report in cascadeur_bundle.get("files", {}).values()
        )
    )
    cascadeur_deployment_pass = (
        cascadeur_deployment.get("status") in {
            "DRY_RUN_READY", "DEPLOYED", "PERMISSION_REQUIRED"
        }
        and cascadeur_deployment.get("bundle_manifest")
        and cascadeur_deployment.get("claims", {}).get("bundle_verified") is True
        and cascadeur_deployment.get("claims", {}).get("cascadeur_import_verified") is False
        and cascadeur_deployment.get("claims", {}).get("conversion_verified") is False
        and cascadeur_deployment.get("claims", {}).get("parity_verified") is False
        and cascadeur_deployment.get("claims", {}).get("full_goal_complete") is False
    )
    cascadeur_protocol_pass = (
        cascadeur_protocol.get("schema") == "b4ml-cascadeur-matched-comparison-protocol-v2"
        and cascadeur_protocol.get("status") == "prospective-assets-frozen"
        and cascadeur_protocol.get("results") is None
        and cascadeur_protocol.get("parity_verified") is False
        and cascadeur_protocol.get("surpasses_verified") is False
        and cascadeur_protocol.get("full_goal_complete") is False
        and cascadeur_protocol_validation.get("schema") == "b4ml-cascadeur-comparison-protocol-validation-v2"
        and cascadeur_protocol_validation.get("complete") is True
        and cascadeur_protocol_validation.get("prospective") is True
        and cascadeur_protocol_validation.get("assets_frozen") is True
        and cascadeur_protocol_validation.get("assets") == 3
        and cascadeur_protocol_validation.get("tasks") == 8
        and cascadeur_protocol_validation.get("matched_cases_per_animator") == 24
        and cascadeur_protocol_validation.get("independent_animators_required") == 3
        and cascadeur_protocol_validation.get("results_present") is False
        and cascadeur_protocol_validation.get("parity_verified") is False
        and cascadeur_protocol_validation.get("surpasses_verified") is False
        and cascadeur_protocol_validation.get("full_goal_complete") is False
        and cascadeur_protocol_validation.get("protocol_sha256") == sha256(loaded["cascadeur_protocol"][0])
        and cascadeur_protocol_validation.get("checker_sha256") == sha256(
            ROOT / "training/b4artists_ml/check_cascadeur_comparison_protocol_v2.py"
        )
        and cascadeur_protocol_validation.get("evidence_validator_sha256") == sha256(
            ROOT / "training/b4artists_ml/portable_comparison_evidence_v1.py"
        )
    )
    cascadeur_results_contract_pass = (
        cascadeur_results_contract.get("status") in {
            "BLOCKED_EXTERNAL_RESULTS_MISSING",
            "RESULTS_PRESENT_INVALID",
            "PASS_CONTRACT_ONLY",
        }
        and cascadeur_results_contract.get("parity_verified") is False
        and cascadeur_results_contract.get("surpasses_verified") is False
        and cascadeur_results_contract.get("full_goal_complete") is False
        and cascadeur_results_contract.get("claim_boundary_closed") is True
    )

    claims = {
        "learned_temporal_quality_verified": False,
        "independent_animator_usability_verified": False,
        "cascadeur_conversion_verified": False,
        "cascadeur_parity_verified": False,
        "full_goal_complete": False,
    }
    gates = {
        "capsule_exact_archive_binding": {"status": "PASS" if capsule_exact_pass else "FAIL", "tests": 2},
        "capsule_foreground_lifecycle": {"status": "PASS" if capsule_foreground_pass else "FAIL"},
        "current_capsule_regression": {"status": "PASS" if current_capsule_pass else "FAIL", "tests": 157},
        "capsule_evaluator_review": {
            "status": "PASS_FAIL_CLOSED" if evaluator_review_fail_closed else "UNEXPECTED",
            "authority": capsule_advisory_review.get("authority"),
            "evaluator_status": capsule_routing.get("evaluator_gate", {}).get("status"),
            "preflight_status": capsule_routing.get("latest_preflight", {}).get("status"),
            "advisory_verdict": capsule_advisory_review.get("verdict"),
            "reviewer_invoked": capsule_governed_retry.get("outcome", {}).get("reviewer_invoked"),
            "review_completed": capsule_governed_retry.get("outcome", {}).get("review_completed"),
            "deterministic_fallback": capsule_routing.get("evaluator_gate", {}).get("fallback_deterministic_validation"),
        },
        "imported_humanoid_workflow": {"status": "PASS" if imported_pass else "FAIL", "tests": 12},
        "mapping_corrections": {"status": "PASS" if mapping_pass else "FAIL", "tests": 11, "adapters": mapping["adapters"]},
        "humanoid_head_orientation": {
            "status": "PASS" if head_orientation_pass else "FAIL",
            "semantic_joint": head_orientation.get("semantic_target", {}).get("joint_index"),
            "focused_tests": head_orientation.get("coverage", {}).get("tests"),
            "fixtures": head_orientation.get("coverage", {}).get("fixtures", []),
            "requested_orientations_per_fixture": head_orientation.get("coverage", {}).get("requested_orientations_per_fixture"),
            "procedural_only": head_orientation.get("claim_boundary", {}).get("procedural_evaluated_rig_constraint"),
            "claim_boundary_closed": head_orientation_pass,
        },
        "humanoid_pole_status": {
            "status": "PASS" if pole_status_pass else "FAIL",
            "focused_tests": 6,
            "affected_tests": 84,
            "read_only": True,
            "claim_boundary_closed": pole_status_pass,
        },
        "current_dev_package": {
            "status": "PASS" if current_dev_package_pass else "FAIL",
            "version": current_dev_package.get("version"),
            "files": current_dev_package.get("files"),
            "pole_regression_tests": sum(entry.get("tests", 0) for entry in current_package_pole_entries),
            "pole_regression_layout": current_dev_package.get("package_regression_layout"),
            "pole_regression_validation": current_package_pole_validation.get("status"),
            "direct_zip_import_tests": current_package_direct_zip_import.get("tests"),
            "foreground_steps": current_package_foreground_modal.get("step_count"),
            "native_undo_redo": current_package_foreground_modal.get("native_undo_redo", {}).get("status"),
            "claim_boundary_closed": current_dev_package_pass,
        },
        "latest_fully_bound_dev_package": {
            "status": "PASS" if latest_dev_package_pass else "FAIL",
            "version": latest_dev_package.get("version"),
            "files": latest_dev_package.get("files"),
            "archive_sha256": latest_dev_package.get("sha256"),
            "report_schema": latest_package_foreground.get("metrics", {}).get("schema"),
            "backend": latest_package_foreground.get("metrics", {}).get("backend"),
            "package_regression_suites": latest_package_regression.get("suites"),
            "package_regression_tests": latest_package_regression.get("tests"),
            "host_independent_math_tests": latest_dev_package.get(
                "focused_validation", {}).get("tests"),
            "direct_zip_import_tests": latest_package_direct_zip_import.get("tests"),
            "moving_deforming_mesh_tests": latest_package_moving_deforming_mesh.get(
                "tests"),
            "moving_deforming_mesh_receipt": EVIDENCE[
                "latest_package_moving_deforming_mesh"],
            "coupled_pelvis_spine_tests": latest_package_coupled_pelvis_spine.get(
                "tests"
            ),
            "coupled_pelvis_spine_receipt": EVIDENCE[
                "latest_package_coupled_pelvis_spine"
            ],
            "multiple_static_sphere_collision_tests": latest_package_multiple_static_spheres.get(
                "tests"
            ),
            "multiple_static_sphere_collision_receipt": EVIDENCE[
                "latest_package_multiple_static_spheres"
            ],
            "force_offset_torque_tests": latest_package_force_offset_torque.get(
                "tests"
            ),
            "force_offset_torque_receipt": EVIDENCE[
                "latest_package_force_offset_torque"
            ],
            "self_collision_tests": latest_package_self_collision.get("tests"),
            "self_collision_receipt": EVIDENCE[
                "latest_package_self_collision"
            ],
            "production_character_generalization_tests": latest_package_production_generalization.get(
                "tests"
            ),
        "production_character_generalization_receipt": EVIDENCE[
                "latest_package_production_generalization"
            ],
            "continuous_moving_capsule_chain_tests": latest_package_continuous_capsule.get(
                "tests"
            ),
            "continuous_moving_capsule_chain_receipt": EVIDENCE[
                "latest_package_continuous_capsule"
            ],
            "continuous_moving_sphere_chain_tests": latest_package_continuous_sphere.get(
                "tests"
            ),
            "continuous_moving_sphere_chain_receipt": EVIDENCE[
                "latest_package_continuous_sphere"
            ],
            "production_character_generalization_scope": latest_dev_package.get(
                "production_character_generalization_scope"
            ),
            "foreground_clearance_samples": latest_package_foreground.get(
                "independent_clearance", {}).get("samples"),
            "independent_code_review": "NOT_BOUND",
            "package_evidence_review": "NOT_REQUESTED",
            "promoted_or_installed": False,
            "claim_boundary_closed": latest_dev_package_pass,
        },
        "quadruped_procedural_workflow": {"status": "PASS" if quadruped_pass else "FAIL", "focused_tests": 5, "affected_tests": 99},
        "host_independent_regression_protection": {
            "status": "PASS" if host_independent_pass else "FAIL",
            "collected": host_independent["collected"],
            "passed_calls": host_independent["passed_calls"],
        },
        "standalone_boundary": {
            "status": "PASS" if standalone_pass else "FAIL",
            "protected_addons_unchanged": standalone["protected_addons"]["unchanged"],
            "bforartists_host_guard": (
                standalone["b4ml_runtime"]["host_guard"]["is_bforartists_function"] is True
                and standalone["b4ml_runtime"]["host_guard"]["bforartists_host_tokens"] is True
            ),
            "runtime_dependency_absent": standalone["b4ml_runtime"]["host_guard"]["runtime_dependency_absent"],
        },
        "temporal_training_boundary": {
            "status": "BLOCKED" if temporal_blocked else "UNEXPECTED",
            "training_authorized": temporal_intake["training_authorized"],
            "intake_status": temporal_intake["status"],
            "parent_receipt_status": temporal_training_boundary["status"],
            "model_training_permitted": temporal_training_boundary["model_training_permitted"],
            "model_promotion_permitted": temporal_training_boundary["model_promotion_permitted"],
            "model_promoted": temporal_intake["model_promoted"],
            "claim_boundary_closed": all(
                value is False for value in temporal_training_boundary["claim_boundary"].values()
            ),
        },
        "independent_animator_review": {
            "status": "REQUIRED_EXTERNAL",
            "human_input_performed": reviewer["observation"]["human_input_performed"],
            "required_artifacts": reviewer["next_required_external_artifacts"],
        },
        "procedural_vertical_slice_human_review": {
            "status": "PASS_REVIEWED_EXPORT" if human_review_pass else "REQUIRED_EXTERNAL",
            "reviewer_id": human_review_export.get("reviewer", {}).get("id"),
            "experience": human_review_export.get("reviewer", {}).get("experience"),
            "cases": human_review_export.get("cases", []).__len__(),
            "human_authored": human_review_export.get("human_authored") is True,
            "export_validated": human_review_summary.get("human_review_export_validated") is True,
            "claim_boundary_closed": human_review_pass,
        },
        "human_gates_handoff_surface": {
            "status": "PASS_STATIC_READY" if handoff_ready else "FAIL",
            "human_input_performed": False,
            "training_authorized": False,
        },
        "cascadeur_comparison_protocol": {
            "status": "PASS_PROSPECTIVE" if cascadeur_protocol_pass else "FAIL",
            "assets_frozen": cascadeur_protocol_validation.get("assets_frozen"),
            "assets": cascadeur_protocol_validation.get("assets"),
            "tasks": cascadeur_protocol_validation.get("tasks"),
            "matched_cases_per_animator": cascadeur_protocol_validation.get("matched_cases_per_animator"),
            "independent_animators_required": cascadeur_protocol_validation.get("independent_animators_required"),
            "results_present": cascadeur_protocol_validation.get("results_present"),
            "conversion_verified": False,
            "parity_verified": False,
            "surpasses_verified": False,
            "claim_boundary_closed": cascadeur_protocol_pass,
        },
        "cascadeur_results_contract": {
            "status": cascadeur_results_contract.get("status") if cascadeur_results_contract_pass else "UNEXPECTED",
            "results_present": cascadeur_results_contract.get("results_present"),
            "claim_audit_required": cascadeur_results_contract.get("claim_audit_required", True),
            "parity_verified": False,
            "surpasses_verified": False,
            "claim_boundary_closed": cascadeur_results_contract_pass,
        },
        "cascadeur_import_and_api": {
            "status": "PASS" if cascadeur_import_pass and cascadeur_capability_pass and cascadeur_diagnostics_pass and cascadeur_wrapper_pass and cascadeur_bundle_pass and cascadeur_deployment_pass else "FAIL",
            "conversion_verified": False,
            "parity_verified": False,
            "ordinary_python_import_surface": cascadeur_import_diagnostic["status"],
            "ordinary_python_standard_rig_surface": cascadeur_standard_rig_diagnostic["status"],
            "diagnostic_claim_boundary_closed": cascadeur_diagnostics_pass,
            "command_wrapper_status": cascadeur_wrapper["status"],
            "command_wrapper_contract_verified": cascadeur_wrapper_pass,
            "command_wrapper_deployment_verified": cascadeur_wrapper["claims"]["deployment_verified"],
            "command_wrapper_mutation_performed": cascadeur_wrapper["mutation_performed"],
            "command_wrapper_bundle_status": cascadeur_bundle["status"],
            "command_wrapper_bundle_staged": cascadeur_bundle_pass,
            "command_wrapper_deployment_helper_status": cascadeur_deployment["status"],
            "command_wrapper_deployment_helper_claims_closed": cascadeur_deployment_pass,
            "command_wrapper_deployment_mutation_performed": cascadeur_deployment["mutation_performed"],
        },
    }
    report = {
        "schema": "b4ml-current-goal-gate-status-v1",
        "goal_id": "01a073fe-c240-70c0-b5cd-fe9653aac60e",
        "status": "ACTIVE_INCOMPLETE",
        "full_goal_complete": False,
        "scope": "Checksum-bound aggregation of current evidence; underlying receipts remain authoritative.",
        "gates": gates,
        "claim_boundary": claims,
        "remaining_external_gates": [
            "completion-authority evaluator/reviewer verdict for the capsule evidence packet",
            "completed independent humanoid review and timed correction exports",
            "manifest-bound human contact/intent and identity/authorization receipts",
            "Cascadeur conversion, exact settings, matched animation, and independent comparison sessions",
        ],
        "evidence": {
            key: {
                "path": relative,
                "sha256": sha256(path),
                "schema": data.get("schema") if isinstance(data, dict) else None,
            }
            for key, relative in EVIDENCE.items()
            for path, data in [loaded[key]]
        },
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
