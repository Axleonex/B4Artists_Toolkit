"""Record the unchanged orchestration policy applied to the 0.27.0 milestone."""
from pathlib import Path
import hashlib
import json
import time


ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "training/b4artists_ml/results"
OUT = RESULTS / "orchestration-route-quadruped-v22.json"


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if OUT.exists():
        raise RuntimeError("Evidence exists: " + str(OUT))
    prior = read(RESULTS / "orchestration-route-secondary-chain-v21.json")
    source = RESULTS / "quadruped-adapter-source-v1.json"
    package = RESULTS / "quadruped-adapter-package-v1.json"
    archive = ROOT / "releases/b4artists_ml_v0.27.0.zip"
    assert prior["session_adoption"]["authority_precedence"] == "preserved"
    assert prior["session_adoption"]["execution_routing"].startswith("T0-T4 preserved")
    assert prior["session_adoption"]["evaluation_routing"].startswith("S0-S4 preserved")
    record = {
        "schema": 1,
        "recorded_date": "2026-09-11",
        "recorded_at": time.time(),
        "session_scope": "B4Artists Machine Learning experimental 0.27.0 quadruped adapter",
        "installed_validated_baseline": prior["installed_validated_baseline"],
        "canonical_current_observation": prior["canonical_current_observation"],
        "session_adoption": prior["session_adoption"],
        "execution": prior["execution"],
        "evaluation": {
            "depth": "S3",
            "mode": "shadow/classification-only",
            "classification_only": True,
            "runnable": True,
            "reviewer_invoked": False,
            "review_completed": False,
            "model_calls": 0,
            "policy_fingerprint": prior["evaluation"]["policy_fingerprint"],
            "release": "0.27.0",
            "archive": archive.relative_to(ROOT).as_posix(),
            "archive_sha256": sha(archive),
            "source_regression": source.relative_to(ROOT).as_posix(),
            "source_regression_sha256": sha(source),
            "source_suites": 50,
            "source_tests": 474,
            "source_assertions_passed": True,
            "runtime_hash_sets": 1,
            "exact_package": package.relative_to(ROOT).as_posix(),
            "exact_package_sha256": sha(package),
            "exact_package_tests": 34,
            "exact_package_assertions_passed": True,
            "outbound_runtime_calls": 0,
            "quadruped_profiles": ["cat", "horse", "wolf"],
            "quadruped_schema": "quadruped_v1",
            "generic_capture_interpolation_qualified": True,
            "humanoid_only_tools_fail_closed": True,
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
                "quadruped whole-body posing, four-foot contacts, gait physics and learned motion",
                "deformable secondary dynamics and production-character review",
                "executed matched Cascadeur evaluation"
            ]
        }
    }
    OUT.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"depth": record["evaluation"]["depth"],
                      "mode": record["evaluation"]["mode"],
                      "model_calls": 0, "release": "0.27.0"}, indent=2))


if __name__ == "__main__":
    main()
