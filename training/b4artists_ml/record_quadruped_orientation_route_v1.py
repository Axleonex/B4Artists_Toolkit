"""Record the preserved orchestration path used for the 0.29.0 milestone."""
from pathlib import Path
import hashlib
import json
import time


ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "training/b4artists_ml/results"
OUT = RESULTS / "orchestration-route-quadruped-orientation-v24.json"


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if OUT.exists():
        raise RuntimeError("Evidence exists: " + str(OUT))
    prior = read(RESULTS / "orchestration-route-quadruped-pose-v23.json")
    source_path = RESULTS / "quadruped-orientation-source-v1.json"
    package_path = RESULTS / "quadruped-orientation-package-v1.json"
    archive = ROOT / "releases/b4artists_ml_v0.29.0.zip"
    source = read(source_path)
    package = read(package_path)
    assert prior["execution"]["classification"] == "DEGRADED_NATIVE_CONTINUE"
    assert prior["evaluation"]["mode"] == "shadow/classification-only"
    assert source["complete"] and source["suites"] == 51 and source["tests"] == 478
    assert package["passed"] and package["tests"] == 38 and package["exact_package"]
    assert package["package_sha256"] == sha(archive)

    record = {key: value for key, value in prior.items()
              if key not in ("recorded_at", "session_scope", "evaluation", "formal_goal")}
    record.update({
        "recorded_at": time.time(),
        "session_scope": "B4Artists Machine Learning experimental 0.29.0 quadruped orientation",
        "execution": dict(prior["execution"], source_or_package_mutation_after_evidence=False),
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
            "release": "0.29.0",
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
            "deterministic_position_and_orientation_qualified": True,
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
                "quadruped poles/spine shaping, contacts, gait physics and learned motion",
                "deformable secondary dynamics and production-character review",
                "executed matched Cascadeur evaluation"
            ]
        }
    })
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
