"""Bind session-compatible routing/evaluation evidence to release 0.25.0."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "training/b4artists_ml/results/orchestration-route-secondary-world-v20.json"


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    assert not OUT.exists()
    prior = read(ROOT / "training/b4artists_ml/results/orchestration-route-secondary-motion-v19.json")
    regression_path = ROOT / "training/b4artists_ml/results/secondary-world-full-v1-regression.json"
    package_path = ROOT / "training/b4artists_ml/results/secondary-world-package-v1.json"
    source_ui_path = ROOT / "docs/b4artists_ml/secondary-ui-secondary-world-source-v1.json"
    package_ui_path = ROOT / "docs/b4artists_ml/secondary-ui-secondary-world-package-v1.json"
    meta_path = ROOT / "docs/b4artists_ml/package-test-v0.25.0.json"
    archive_path = ROOT / "releases/b4artists_ml_v0.25.0.zip"
    regression = read(regression_path)
    package = read(package_path)
    source_ui = read(source_ui_path)
    package_ui = read(package_ui_path)
    meta = read(meta_path)

    assert len(regression) == 49 and sum(row["tests"] for row in regression) == 465
    assert all(
        row["assertions_passed"]
        and not row.get("failures")
        and not row.get("errors")
        and not row.get("skipped")
        for row in regression
    )
    assert len({json.dumps(row["runtime_sha256"], sort_keys=True) for row in regression}) == 1
    runtime_hash = regression[0]["runtime_sha256"]
    assert package["passed"] and package["tests"] == 42
    assert package["offline_guard_self_test"] and not package["denied_runtime_calls"]
    assert package["exact_package"] and not package["full_goal_complete"]
    assert source_ui["passed"] and package_ui["passed"]
    assert runtime_hash == package["runtime_sha256"] == source_ui["runtime_sha256"]
    assert runtime_hash == package_ui["runtime_sha256"] == meta["runtime_sha256"]
    assert meta["ready_for_local_testing"] and not meta["full_goal_complete"]
    assert meta["package_matches_source"] and meta["forbidden_identities_absent"]
    assert sha(archive_path) == meta["sha256"] == package["package_sha256"]
    metrics = package_ui["metrics"]
    assert metrics["backend"] == "implicit_selected_control_secondary_v2"
    assert metrics["deterministic_physics"] and not metrics["learned"]
    assert metrics["space"] == "WORLD" and metrics["gravity_influence"] > 0
    assert metrics["collision"] and metrics["collision_samples"] > 0
    assert metrics["max_raw_penetration"] > 0 and metrics["max_penetration_after"] == 0
    assert metrics["max_world_location_error"] < 2.0e-4
    assert metrics["max_world_rotation_error_radians"] < 2.0e-3
    assert metrics["priority_poses_preserved"] and metrics["editable_linear_keys"]
    assert source_ui["step_p95_ms"] < 50 and source_ui["step_max_ms"] < 50
    assert package_ui["step_p95_ms"] < 50 and package_ui["step_max_ms"] < 50

    result = dict(
        schema=1,
        recorded_date="2026-09-10",
        session_scope="B4Artists Machine Learning experimental 0.25.0 world-space secondary dynamics",
        installed_validated_baseline=prior["installed_validated_baseline"],
        canonical_current_observation=prior["canonical_current_observation"],
        session_adoption=dict(
            authority_precedence="preserved",
            approval_boundaries="preserved",
            capability_restrictions="preserved",
            execution_routing="T0-T4 preserved; validated native continuation retained after current shared entrypoint failure",
            evaluation_routing="S0-S4 preserved; S3 selected for this coupled runtime/package milestone",
            review_behavior="shadow/classification-only",
            additive_updates=[
                "current authority and task-contract vocabulary",
                "current gated T0-T4 lane definitions",
                "current independent S0-S4 review-depth definitions",
            ],
            unavailable=[
                "gsd-sdk.cmd was not present on PATH",
                "current prime-code-execute.py probe failed because its uv trampoline could not spawn Python",
            ],
            reload_required=False,
            new_session_required=False,
            explicit_approval_required_for_adoption=False,
            providers_activated=False,
            defaults_changed=False,
            services_restarted=False,
            production_state_changed=False,
            shared_source_modified=False,
        ),
        execution=prior["execution"],
        evaluation=dict(
            depth="S3",
            mode="shadow/classification-only",
            classification_only=True,
            runnable=True,
            reviewer_invoked=False,
            review_completed=False,
            model_calls=0,
            policy_fingerprint=prior["evaluation"]["policy_fingerprint"],
            release="0.25.0",
            archive=archive_path.relative_to(ROOT).as_posix(),
            archive_sha256=meta["sha256"],
            source_regression=regression_path.relative_to(ROOT).as_posix(),
            source_regression_sha256=sha(regression_path),
            source_suites=49,
            source_tests=465,
            source_assertions_passed=True,
            runtime_hash_sets=1,
            exact_package=package_path.relative_to(ROOT).as_posix(),
            exact_package_sha256=sha(package_path),
            exact_package_tests=42,
            exact_package_assertions_passed=True,
            outbound_runtime_calls=0,
            source_real_window=source_ui_path.relative_to(ROOT).as_posix(),
            source_real_window_sha256=sha(source_ui_path),
            source_real_window_passed=True,
            package_real_window=package_ui_path.relative_to(ROOT).as_posix(),
            package_real_window_sha256=sha(package_ui_path),
            package_real_window_passed=True,
            lifecycle_events=len(package_ui["events"]),
            source_step_p95_ms=source_ui["step_p95_ms"],
            source_step_max_ms=source_ui["step_max_ms"],
            package_step_p95_ms=package_ui["step_p95_ms"],
            package_step_max_ms=package_ui["step_max_ms"],
            responsiveness_p95_under_50ms_verified=True,
            responsiveness_all_steps_under_50ms_verified=True,
            backend=metrics["backend"],
            world_space_verified=True,
            gravity_verified=True,
            collision_samples=metrics["collision_samples"],
            max_raw_penetration=metrics["max_raw_penetration"],
            max_penetration_after=metrics["max_penetration_after"],
            max_world_location_error=metrics["max_world_location_error"],
            max_world_rotation_error_radians=metrics["max_world_rotation_error_radians"],
            priority_poses_preserved=metrics["priority_poses_preserved"],
            editable_linear_keys=metrics["editable_linear_keys"],
            host_shutdown_qualified=False,
            human_reviewed_cases=0,
            cascadeur_results_present=False,
        ),
        formal_goal=dict(
            state_unchanged=True,
            complete=False,
            remaining_primary_gates=[
                "completed independent animator export and timed correction pass",
                "reviewed motion labels",
                "accepted learned temporal motion",
                "joint and external forces plus arbitrary/deforming collision",
                "deformable and chain secondary dynamics plus production-character review",
                "quadrupeds",
                "executed matched Cascadeur evaluation",
            ],
        ),
    )
    assert result["execution"]["continuation"] == "native"
    assert not result["session_adoption"]["production_state_changed"]
    assert result["evaluation"]["model_calls"] == 0
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "receipt": OUT.relative_to(ROOT).as_posix(),
        "sha256": sha(OUT),
        "route": result["execution"]["continuation"],
        "evaluation": result["evaluation"]["mode"],
        "release": result["evaluation"]["release"],
    }, indent=2))


if __name__ == "__main__":
    main()
