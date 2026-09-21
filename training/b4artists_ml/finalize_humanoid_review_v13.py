"""Bind current-release humanoid, reviewer, and correction-study evidence."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "training/b4artists_ml/results/humanoid-review-v13-evidence.json"


def read(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def sha(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def main() -> None:
    aggregate_path = "training/b4artists_ml/results/procedural-vertical-slice-v13/aggregate.json"
    protocol_path = "training/b4artists_ml/procedural_vertical_slice_protocol_v13.json"
    manifest_path = "training/b4artists_ml/results/procedural-vertical-slice-reviewer-v2/manifest.json"
    reviewer_validation_path = "training/b4artists_ml/results/procedural-vertical-slice-reviewer-v2/validation.json"
    browser_path = "training/b4artists_ml/results/procedural-vertical-slice-reviewer-v2/browser-interaction-validation-v3.json"
    correction_path = "training/b4artists_ml/results/correction-trial-smoke-v2/validation.json"
    correction_validator_path = "training/b4artists_ml/results/correction-trial-validator-v1.json"
    route_path = "training/b4artists_ml/results/orchestration-route-secondary-world-v20.json"
    package_path = "docs/b4artists_ml/package-test-v0.25.0.json"

    aggregate = read(aggregate_path)
    protocol = read(protocol_path)
    manifest = read(manifest_path)
    reviewer = read(reviewer_validation_path)
    browser = read(browser_path)
    correction = read(correction_path)
    correction_validator = read(correction_validator_path)
    route = read(route_path)
    package = read(package_path)

    aggregate_sha = sha(aggregate_path)
    protocol_sha = sha(protocol_path)
    assert aggregate["schema"] == "procedural-vertical-slice-aggregate-v13"
    assert aggregate["complete"] and aggregate["cases"] == aggregate["passed"] == 32
    assert aggregate["failed"] == 0 and aggregate["automated_procedural_floor_complete"]
    assert aggregate["protocol_sha256"] == protocol_sha
    assert protocol["frozen_before_results"] and protocol["supersedes"] == "procedural_vertical_slice_protocol_v12.json"
    assert len(protocol["rigs"]) == 4 and len(protocol["tasks"]) == 8
    assert aggregate["runtime_sha256"] == package["runtime_sha256"] == package["tested_runtime_sha256"]
    for relative, expected in package["runtime_sha256"].items():
        assert sha(relative) == expected
    assert package["version"] == "0.25.0" and package["package_matches_source"]
    assert sha("releases/b4artists_ml_v0.25.0.zip") == package["sha256"]

    assert manifest["complete"] and manifest["cases"] == 32 and manifest["variants"] == 2
    assert manifest["aggregate_sha256"] == aggregate_sha
    assert manifest["protocol_sha256"] == protocol_sha
    assert manifest["balanced_blinding"] == {"corrected_as_A": 16, "corrected_as_B": 16}
    assert manifest["reviewed_cases"] == 0 and not manifest["full_goal_complete"]
    assert reviewer["complete"] and reviewer["source_scene_hashes_exact"]
    assert reviewer["source_report_hashes_exact"] and reviewer["priority_variant_max_component_error"] == 0.0
    assert reviewer["balanced_blinding"] and reviewer["identity_hidden_until_lock"]
    assert reviewer["automated_metrics_hidden_until_lock"] and reviewer["complete_ratings_required_for_export"]
    assert reviewer["data_sha256"] == manifest["data_sha256"]
    assert reviewer["html_sha256"] == manifest["html_sha256"]
    assert reviewer["reviewed_cases"] == 0 and not reviewer["cascadeur_comparison"]

    assert browser["complete"] and browser["local_file_loaded"] and browser["javascript_initialized"]
    assert browser["synthetic_review_isolated"] and browser["incomplete_export_blocked"]
    assert browser["lock_before_reveal"] and browser["local_storage_reload_persisted"]
    assert browser["uncaught_browser_exceptions"] == 0
    assert browser["reviewer_html_sha256"] == manifest["html_sha256"]
    assert browser["reviewed_cases"] == 0 and not browser["full_goal_complete"]

    correction_report = correction["host_report"]
    assert correction["complete"] and correction["host_exit_qualified"]
    assert not correction["clean_host_shutdown"] and correction["human_reviewed_cases"] == 0
    assert correction_report["cancelled_source_restored"] and correction_report["frozen_source_unchanged"]
    assert correction_report["active_pause_excluded"]
    assert correction_report["synthetic_smoke"] and not correction_report["human_authored"]
    assert correction_report["action_difference"]["priority_poses_preserved"]
    assert correction_validator["complete"] and correction_validator["synthetic_rejected_as_human"]
    assert correction_validator["valid_contract_fixture_accepted"]
    assert not correction_validator["fixture_persisted"] and correction_validator["human_reviewed_cases"] == 0
    blend_hashes = {item["blend"]: item["blend_sha256"] for item in aggregate["evidence"]}
    assert blend_hashes[correction["scene"]] == correction["scene_sha256"]
    assert correction["review_data_sha256"] == manifest["data_sha256"]

    assert route["session_adoption"]["authority_precedence"] == "preserved"
    assert route["session_adoption"]["execution_routing"].startswith("T0-T4 preserved")
    assert route["session_adoption"]["evaluation_routing"].startswith("S0-S4 preserved")
    assert route["execution"]["continuation"] == "native"
    assert route["evaluation"]["depth"] == "S3"
    assert route["evaluation"]["mode"] == "shadow/classification-only"
    assert route["evaluation"]["model_calls"] == 0 and route["evaluation"]["outbound_runtime_calls"] == 0
    assert not route["formal_goal"]["complete"] and route["evaluation"]["human_reviewed_cases"] == 0
    assert not route["evaluation"]["cascadeur_results_present"]

    evidence_paths = [
        aggregate_path,
        protocol_path,
        manifest_path,
        reviewer_validation_path,
        browser_path,
        correction_path,
        correction_validator_path,
        route_path,
        package_path,
        "training/b4artists_ml/results/procedural-vertical-slice-reviewer-v2/browser-interaction-smoke-v3.png",
    ]
    report = {
        "schema": "b4ml-humanoid-review-v13-evidence",
        "complete": True,
        "release": "0.25.0",
        "runtime_unchanged_from_release": True,
        "runtime_hashes_exact": True,
        "archive_sha256": package["sha256"],
        "procedural_matrix": {
            "cases": aggregate["cases"],
            "passed": aggregate["passed"],
            "failed": aggregate["failed"],
            "rigs": aggregate["rigs"],
            "tasks": aggregate["tasks"],
            "maxima": aggregate["maxima"],
            "total_contact_checks": aggregate["total_contact_checks"],
            "total_contact_validation_frames": aggregate["total_contact_validation_frames"],
            "clean_host_shutdown": aggregate["clean_host_shutdown"],
        },
        "blind_reviewer": {
            "cases": manifest["cases"],
            "variants": manifest["variants"],
            "balanced_blinding": manifest["balanced_blinding"],
            "embedded_frames": manifest["embedded_frames"],
            "static_validation_passed": reviewer["complete"],
            "browser_interaction_passed": browser["complete"],
            "browser_product_version": browser["browser_product_version"],
            "uncaught_browser_exceptions": browser["uncaught_browser_exceptions"],
            "reviewed_cases": 0,
        },
        "correction_trial": {
            "smoke_passed": correction["complete"],
            "synthetic_rejected_as_human": correction_validator["synthetic_rejected_as_human"],
            "source_restoration_verified": correction_report["cancelled_source_restored"],
            "frozen_source_unchanged": correction_report["frozen_source_unchanged"],
            "pause_exclusion_verified": correction_report["active_pause_excluded"],
            "priority_poses_preserved": correction_report["action_difference"]["priority_poses_preserved"],
            "human_reviewed_cases": 0,
        },
        "orchestration": {
            "execution_route": "validated native continuation",
            "evaluation_depth": "S3",
            "review_mode": "shadow/classification-only",
            "model_calls": 0,
            "providers_activated": False,
            "reload_required": False,
            "new_session_required": False,
        },
        "claims": {
            "automated_procedural_floor_current_release": True,
            "human_visual_acceptance": False,
            "human_correction_effort": False,
            "learned_temporal_motion": False,
            "cascadeur_parity": False,
            "cascadeur_superiority": False,
            "clean_host_shutdown": False,
            "full_goal_complete": False,
        },
        "remaining_primary_gates": route["formal_goal"]["remaining_primary_gates"],
        "evidence": {relative: sha(relative) for relative in evidence_paths},
        "script_sha256": sha("training/b4artists_ml/finalize_humanoid_review_v13.py"),
        "full_goal_complete": False,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "complete": report["complete"],
        "release": report["release"],
        "procedural_cases": report["procedural_matrix"]["cases"],
        "browser_interaction_passed": report["blind_reviewer"]["browser_interaction_passed"],
        "correction_smoke_passed": report["correction_trial"]["smoke_passed"],
        "human_reviewed_cases": 0,
        "model_calls": 0,
        "full_goal_complete": False,
    }, indent=2))


if __name__ == "__main__":
    main()
