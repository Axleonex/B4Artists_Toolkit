"""Bind session-compatible routing/evaluation evidence to release 0.24.0."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "training/b4artists_ml/results/orchestration-route-secondary-motion-v19.json"


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    assert not OUT.exists()
    prior = read(ROOT / "training/b4artists_ml/results/orchestration-route-planar-collision-v18.json")
    regression_path = ROOT / "training/b4artists_ml/results/secondary-motion-full-v1-regression.json"
    package_path = ROOT / "training/b4artists_ml/results/secondary-motion-package-v1.json"
    ui_path = ROOT / "docs/b4artists_ml/secondary-ui-secondary-package-v1.json"
    meta_path = ROOT / "docs/b4artists_ml/package-test-v0.24.0.json"
    regression = read(regression_path)
    package = read(package_path)
    ui = read(ui_path)
    meta = read(meta_path)

    assert len(regression) == 49 and sum(row["tests"] for row in regression) == 458
    assert all(
        row["assertions_passed"]
        and not row.get("failures")
        and not row.get("errors")
        and not row.get("skipped")
        for row in regression
    )
    assert len({json.dumps(row["runtime_sha256"], sort_keys=True) for row in regression}) == 1
    assert package["passed"] and package["tests"] == 35 and not package["denied_runtime_calls"]
    assert ui["passed"]
    assert ui["runtime_sha256"] == regression[0]["runtime_sha256"] == package["runtime_sha256"] == meta["runtime_sha256"]
    metrics = ui["metrics"]
    assert metrics["backend"] == "implicit_selected_control_secondary_v1"
    assert metrics["deterministic_physics"] and not metrics["learned"]
    assert metrics["priority_poses_preserved"] and metrics["editable_linear_keys"]
    assert ui["step_p95_ms"] < 50 and ui["step_max_ms"] < 50

    result = dict(
        schema=1,
        recorded_date="2026-09-10",
        session_scope="B4Artists Machine Learning experimental 0.24.0 selected-control secondary motion",
        installed_validated_baseline=prior["canonical"],
        canonical_current_observation=dict(
            orchestration_harness_kit_commit="01665be780909aee3479567732d18748946ca173",
            hermes_agent_self_evolution_commit="ec747e90461a532150b0bfd70e0f9b262cc46a03",
            both_worktrees_dirty=True,
            execution_policy_sha256="74041CC3740F3165B7A3280583628C2FBE21B60B626D08045EB0560771492466",
            adaptive_review_runtime_sha256="E8853319AD88EC4630C4206172350F30782DDD9D6A37D70FB7A00E12E028BA5B",
            execution_policy_mode="gated",
            promoted_lanes=["T0_DETERMINISTIC", "T1_NATIVE", "T2_OMP_LITE"],
            canonical_codex_adapter_sdk_version=2,
            canonical_codex_adapter_harness_version="0.147.0",
        ),
        session_adoption=dict(
            authority_precedence="preserved",
            approval_boundaries="preserved",
            capability_restrictions="preserved",
            execution_routing="T0-T4 preserved; prior task route retained after current entrypoint failure",
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
            release="0.24.0",
            archive="releases/b4artists_ml_v0.24.0.zip",
            archive_sha256=meta["sha256"],
            source_regression=regression_path.relative_to(ROOT).as_posix(),
            source_regression_sha256=sha(regression_path),
            source_suites=49,
            source_tests=458,
            source_assertions_passed=True,
            runtime_hash_sets=1,
            exact_package=package_path.relative_to(ROOT).as_posix(),
            exact_package_sha256=sha(package_path),
            exact_package_tests=35,
            exact_package_assertions_passed=True,
            outbound_runtime_calls=0,
            real_window=ui_path.relative_to(ROOT).as_posix(),
            real_window_sha256=sha(ui_path),
            real_window_passed=True,
            lifecycle_events=len(ui["events"]),
            step_p95_ms=ui["step_p95_ms"],
            step_max_ms=ui["step_max_ms"],
            responsiveness_p95_under_50ms_verified=ui["step_p95_ms"] < 50,
            responsiveness_all_steps_under_50ms_verified=ui["step_max_ms"] < 50,
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
                "secondary gravity/global-space dynamics and production-character review",
                "quadrupeds",
                "executed matched Cascadeur evaluation",
            ],
        ),
    )
    assert result["execution"]["continuation"] == "native"
    assert not result["session_adoption"]["production_state_changed"]
    assert result["evaluation"]["model_calls"] == 0
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "receipt": OUT.relative_to(ROOT).as_posix(),
                "sha256": sha(OUT),
                "route": result["execution"]["continuation"],
                "evaluation": result["evaluation"]["mode"],
                "release": result["evaluation"]["release"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
