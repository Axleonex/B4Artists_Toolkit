"""Build the current bounded-goal aggregate from exact source receipts."""
from pathlib import Path
import hashlib
import json


ROOT = Path(__file__).resolve().parents[2]
TRAIN = ROOT / "training/b4artists_ml"
RESULTS = TRAIN / "results"
OUTPUT = RESULTS / "current-goal-gate-status-v2.json"
GOAL_ID = "01a073fe-c240-70c0-b5cd-fe9653aac60e"

INPUTS = {
    "package": ROOT / "docs/b4artists_ml/package-test-v0.37.51-dev.json",
    "package_regression": RESULTS / "exact-package-pole-v0.37.51.json",
    "package_generalization": RESULTS / "exact-package-v0.37.51-production-character-generalization.json",
    "production_generalization": RESULTS / "production-character-generalization-v1-20260919.json",
    "coupled_full_body": RESULTS / "coupled-full-body-v1-all-adapters-pass.json",
    "momentum": RESULTS / "momentum-host.json",
    "angular_momentum": RESULTS / "angular-momentum-angular-host.json",
    "temporal_pipeline": RESULTS / "temporal-minimal-pipeline-v1.json",
    "human_review": RESULTS / "review-directed-followup-reviewer-v11/human-review-summary-v11-native-display.json",
    "human_export": RESULTS / "human-review-exports/b4ml-review-directed-followup-human-review-v11-axlbot.json",
    "cascadeur_capability": RESULTS / "cascadeur-capability-probe-validation-v1.json",
    "cascadeur_deployment": RESULTS / "cascadeur-command-wrapper-deployment-v1.json",
    "cascadeur_results": RESULTS / "cascadeur-comparison-results-contract-v1.json",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def evidence(name, value):
    path = INPUTS[name]
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "sha256": sha(path),
        "schema": value.get("schema"),
    }


def build():
    values = {name: read(path) for name, path in INPUTS.items()}
    package = values["package"]
    package_regression = values["package_regression"]
    package_generalization = values["package_generalization"]
    production = values["production_generalization"]
    coupled = values["coupled_full_body"]
    momentum = values["momentum"]
    angular = values["angular_momentum"]
    temporal = values["temporal_pipeline"]
    review = values["human_review"]
    cascadeur_capability = values["cascadeur_capability"]
    cascadeur_deployment = values["cascadeur_deployment"]
    cascadeur_results = values["cascadeur_results"]

    archive = ROOT / "releases/b4artists_ml_v0.37.51-dev.zip"
    if not archive.is_file() or sha(archive) != package.get("sha256"):
        raise ValueError("v0.37.51 archive identity mismatch")
    if not (
        package.get("version") == "0.37.51-dev"
        and package.get("files") == 54
        and package.get("package_matches_source") is True
        and package.get("ready_for_local_testing") is True
        and package.get("full_goal_complete") is False
        and package_regression.get("status") == "PASS"
        and package_regression.get("tests") == 87
        and package_regression.get("archive_sha256") == package["sha256"]
        and package_generalization.get("assertions_passed") is True
        and package_generalization.get("tests") == 3
        and package_generalization.get("package_sha256") == package["sha256"]
    ):
        raise ValueError("Unqualified current exact package")
    if not (
        production.get("complete") is True
        and production.get("passed") == production.get("expected") == 9
        and production.get("human_review_not_run") is True
        and production.get("learned_temporal_quality_not_claimed") is True
        and production.get("universal_production_compatibility_not_claimed") is True
    ):
        raise ValueError("Unqualified bounded production-character generalization")
    if not (
        coupled.get("schema") == "b4ml-coupled-full-body-v1"
        and coupled.get("passed") is True
        and coupled.get("failures") == coupled.get("errors") == 0
        and len(coupled.get("records", [])) == 6
        and coupled.get("claim_boundary", {}).get("procedural_only") is True
        and coupled["claim_boundary"].get("human_visual_quality") is False
    ):
        raise ValueError("Unqualified bounded coupled solver")
    if not (
        momentum.get("passed") is True
        and len(momentum.get("rows", [])) == 5
        and angular.get("passed") is True
        and len(angular.get("rows", [])) == 3
    ):
        raise ValueError("Unqualified momentum host evidence")
    if not (
        temporal.get("schema") == "b4ml-temporal-minimal-pipeline-v1"
        and temporal.get("status") == "BLOCKED_BEFORE_TRAINING"
        and temporal.get("training_started") is False
        and temporal.get("candidate_artifact_created") is False
        and temporal.get("model_promotion_permitted") is False
        and temporal.get("runtime_integration_permitted") is False
        and temporal.get("full_goal_complete") is False
    ):
        raise ValueError("Temporal pipeline did not fail closed")
    if not (
        review.get("schema") == "b4ml-human-review-summary-v11"
        and review.get("complete") is True
        and review.get("candidate_qualified_acceptance") == 1
        and review.get("acceptance_contradictions") == 0
        and review.get("preserve_exact_cases") == ["boneforge/run@v54", "rigify_basic/run@v58"]
        and review.get("training_authorized") is False
        and review.get("model_promotion_authorized") is False
        and review.get("cascadeur_connector_authorized") is False
        and review.get("identity_receipt") == "not established by reviewer display name"
        and review.get("export_sha256") == sha(INPUTS["human_export"])
    ):
        raise ValueError("Unqualified or over-authorized human review")
    if not (
        cascadeur_capability.get("complete") is True
        and cascadeur_capability.get("status") == "PASS"
        and cascadeur_capability.get("conversion_attempted") is False
        and cascadeur_capability.get("parity_verified") is False
        and cascadeur_deployment.get("status") == "DRY_RUN_READY"
        and cascadeur_deployment.get("mutation_performed") is False
        and cascadeur_results.get("status") == "BLOCKED_EXTERNAL_RESULTS_MISSING"
        and cascadeur_results.get("results_present") is False
        and cascadeur_results.get("parity_verified") is False
        and cascadeur_results.get("surpasses_verified") is False
    ):
        raise ValueError("Cascadeur boundary is not closed")

    return {
        "schema": "b4ml-current-goal-gate-status-v2",
        "goal_id": GOAL_ID,
        "status": "ACTIVE_INCOMPLETE_EXTERNAL_GATES",
        "full_goal_complete": False,
        "current_local_package": {
            "version": package["version"],
            "archive": "releases/b4artists_ml_v0.37.51-dev.zip",
            "archive_sha256": package["sha256"],
            "files": package["files"],
            "source_matched": True,
            "installed_or_promoted": False,
        },
        "declared_workstreams": {
            "coupled_pelvis_spine_and_chest_shaping": {
                "status": "PASS_BOUNDED",
                "adapters": 6,
                "procedural_only": True,
                "human_visual_quality": False,
            },
            "coupled_force_momentum_and_collision": {
                "status": "PASS_BOUNDED",
                "linear_momentum_profiles": len(momentum["rows"]),
                "angular_momentum_profiles": len(angular["rows"]),
                "exact_package_secondary_tests": package.get("secondary_motion_tests"),
                "exact_package_compound_collision_tests": package.get("compound_collision_tests"),
                "scope": "bounded through three moving spheres plus a static support set; arbitrary rigid-body dynamics remain unclaimed",
            },
            "production_character_generalization": {
                "status": "PASS_BOUNDED",
                "profiles": production["passed"],
                "exact_package_tests": package_generalization["tests"],
                "universal_compatibility_claimed": False,
            },
            "temporal_training_evaluation_pipeline": {
                "status": "PASS_FAIL_CLOSED",
                "training_started": False,
                "candidate_artifact_created": False,
                "training_authorized": False,
                "model_promotion_authorized": False,
                "failures": temporal["preflight"]["failures"],
            },
            "entitlement_aware_cascadeur_connector": {
                "status": "BLOCKED_ENTITLEMENT_AND_EXTERNAL_RESULTS",
                "capability_probe": "PASS_NO_CONVERSION",
                "wrapper": "STAGED_DRY_RUN_ONLY",
                "deployment_mutation_performed": False,
                "conversion_verified": False,
                "parity_verified": False,
            },
        },
        "human_visual_acceptance": {
            "status": "PASS_EXACT_CASES",
            "reviewer": "Axlbot",
            "experience": "10+ years",
            "accepted_exact_cases": review["preserve_exact_cases"],
            "rigify_candidate_scores": review["cases"][0]["candidate_scores"],
            "rigify_candidate_corrections": review["cases"][0]["corrections"],
            "rigify_candidate_interactions": review["cases"][0]["interactions"],
            "identity_receipt_valid": False,
            "training_authorized": False,
        },
        "remaining_prerequisite_independent_work_in_declared_workstreams": [],
        "remaining_external_or_human_gates": [
            "qualified action- and skeleton-disjoint temporal corpus",
            "manifest-bound reviewed contact/intent provenance",
            "separate reviewer identity and training-authorization receipt",
            "independent animator complete-journey and timed correction trials",
            "Cascadeur entitlement, conversion settings, matched outputs, and independent comparison results",
        ],
        "claim_boundary": {
            "learned_temporal_quality_verified": False,
            "model_training_permitted": False,
            "model_promotion_permitted": False,
            "cascadeur_connector_activation_permitted": False,
            "cascadeur_parity_verified": False,
            "surpasses_cascadeur": False,
            "universal_production_compatibility": False,
            "full_goal_complete": False,
        },
        "evidence": {name: evidence(name, value) for name, value in values.items()},
    }


def main():
    if OUTPUT.exists():
        raise RuntimeError("Immutable v2 goal status already exists: " + str(OUTPUT))
    OUTPUT.write_text(json.dumps(build(), indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(OUTPUT)


if __name__ == "__main__":
    main()
