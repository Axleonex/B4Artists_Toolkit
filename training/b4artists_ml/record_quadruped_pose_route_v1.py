"""Record the shared orchestration path used for the 0.28.0 milestone."""
from pathlib import Path
import hashlib
import json
import time


ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "training/b4artists_ml/results"
OUT = RESULTS / "orchestration-route-quadruped-pose-v23.json"


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if OUT.exists():
        raise RuntimeError("Evidence exists: " + str(OUT))
    source_path = RESULTS / "quadruped-pose-source-v1.json"
    package_path = RESULTS / "quadruped-pose-package-v1.json"
    archive = ROOT / "releases/b4artists_ml_v0.28.0.zip"
    source = read(source_path)
    package = read(package_path)
    assert source["complete"] and source["suites"] == 51 and source["tests"] == 478
    assert package["passed"] and package["tests"] == 38 and package["exact_package"]
    assert package["package_sha256"] == sha(archive)

    record = {
        "schema": 2,
        "recorded_date": "2026-09-11",
        "recorded_at": time.time(),
        "session_scope": "B4Artists Machine Learning experimental 0.28.0 quadruped posing",
        "authority_sources_read": [
            "G:/LapArt/.claude/AUTHORITY-CONSTITUTION.md",
            "G:/LapArt/.claude/SHARED-RULES.md",
            "G:/LapArt/.claude/SHARED-ESSENTIALS.md",
            "G:/LapArt/.claude/INSTRUCTION-TASK-CONTRACT.md",
            "G:/LapArt/.claude/STATIC-NATIVE-EXECUTION-POLICY.md",
            "G:/LapArt/.claude/EXECUTION-ROUTING-TROUBLESHOOTING.md",
            "G:/LapArt/hermes-agent-self-evolution/docs/GOALPOST-EVALUATION.md",
            "G:/LapArt/.claude/hermes-update/sdk-disconnect-check/docs/v2/"
        ],
        "already_active": {
            "authority_precedence": "preserved",
            "approval_boundaries": "preserved",
            "capability_restrictions": "preserved",
            "execution_policy_mode": "gated",
            "execution_routing": "T0-T4",
            "promoted_lanes": ["T0_DETERMINISTIC", "T1_NATIVE", "T2_OMP_LITE"],
            "max_escalations": 1,
            "evaluation_depths": "S0-S4 independent of execution lane",
            "review_behavior": "shadow/advisory",
            "active_codex_model": "gpt-6-astra",
            "active_reasoning_effort": "medium",
            "subscription_auth_only": True
        },
        "canonical_current_observation": {
            "hermes_agent_self_evolution_commit": "ec747e90461a532150b0bfd70e0f9b262cc46a03",
            "hermes_agent_self_evolution_dirty_paths": 142,
            "orchestration_harness_kit_commit": "b35ebe0abb106e7da1453c132839c66e2f7817ef",
            "orchestration_harness_kit_dirty_paths": 17,
            "execution_policy_sha256": "74041CC3740F3165B7A3280583628C2FBE21B60B626D08045EB0560771492466",
            "adaptive_review_runtime_sha256": "5D4225C3706B96EE0CD9F54A875BF97B3FAA5A015320A5D6074DF510DFB8C7B9",
            "canonical_codex_adapter_protocol_generation": 2,
            "canonical_codex_adapter_harness_version": "0.147.0"
        },
        "compatibility": {
            "installed_codex_cli_version": "0.146.0",
            "canonical_adapter_expected_harness_version": "0.147.0",
            "adapter_activated": False,
            "compatible_additive_session_rules_applied": [
                "current authority and task-contract precedence",
                "current gated T0-T4 lane definitions",
                "independent S0-S4 evaluation-depth definitions",
                "recoverable native-continuation receipt requirement"
            ],
            "unavailable": [
                "gsd-sdk.cmd was not present on PATH",
                "prime-code-execute.py stopped before routing because its uv trampoline could not spawn a Python child process"
            ],
            "local_project_system_replaced": False,
            "providers_activated": False,
            "defaults_changed": False,
            "services_restarted": False,
            "production_state_changed": False,
            "shared_source_modified": False
        },
        "reload_and_approval": {
            "reload_required_for_current_native_work": False,
            "new_session_required_for_current_native_work": False,
            "explicit_approval_required_for_session_adoption": False,
            "future_adapter_activation_requires_separate_update_and_new_session": True,
            "history_changes_require_confirm_merge_update": True
        },
        "execution": {
            "canonical_entrypoint_attempted": True,
            "canonical_entrypoint_completed": False,
            "canonical_router_recommended_lane": None,
            "failure_stage": "uv trampoline before evaluator/dispatcher",
            "failure": "error: uv trampoline failed to spawn Python child process",
            "classification": "DEGRADED_NATIVE_CONTINUE",
            "continuation": "native",
            "continuation_basis": "STATIC-NATIVE-EXECUTION-POLICY recoverable pre-dispatch infrastructure failure",
            "execution_routing_preserved": "T0-T4",
            "source_or_package_mutation_after_evidence": False
        },
        "evaluation": {
            "depth": "S3",
            "selection": "manual policy classification for coupled runtime/package milestone",
            "mode": "shadow/classification-only",
            "classification_only": True,
            "canonical_evaluator_completed": False,
            "reviewer_invoked": False,
            "review_completed": False,
            "model_calls": 0,
            "evaluation_routing_preserved": "S0-S4",
            "release": "0.28.0",
            "archive": archive.relative_to(ROOT).as_posix(),
            "archive_sha256": sha(archive),
            "source_regression": source_path.relative_to(ROOT).as_posix(),
            "source_regression_sha256": sha(source_path),
            "source_suites": source["suites"],
            "source_tests": source["tests"],
            "source_assertions_passed": True,
            "runtime_hash_sets": source["runtime_hash_sets"],
            "exact_package": package_path.relative_to(ROOT).as_posix(),
            "exact_package_sha256": sha(package_path),
            "exact_package_tests": package["tests"],
            "exact_package_assertions_passed": True,
            "outbound_runtime_calls": len(package["denied_runtime_calls"]),
            "quadruped_profiles": ["cat", "horse", "wolf"],
            "quadruped_schema": "quadruped_v1",
            "deterministic_body_four_paw_pose_qualified": True,
            "host_shutdown_qualified": False,
            "human_reviewed_cases": 0,
            "cascadeur_results_present": False
        },
        "formal_goal": {
            "state_unchanged": True,
            "complete": False,
            "remaining_primary_gates": [
                "completed independent animator export and timed correction pass",
                "reviewed motion labels and accepted learned temporal motion",
                "joint and external forces plus arbitrary/deforming collision",
                "quadruped orientation, contacts, gait physics and learned motion",
                "deformable secondary dynamics and production-character review",
                "executed matched Cascadeur evaluation"
            ]
        }
    }
    OUT.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "classification": record["execution"]["classification"],
        "depth": record["evaluation"]["depth"],
        "mode": record["evaluation"]["mode"],
        "model_calls": record["evaluation"]["model_calls"],
        "source_tests": record["evaluation"]["source_tests"],
        "package_tests": record["evaluation"]["exact_package_tests"]
    }, indent=2))


if __name__ == "__main__":
    main()
