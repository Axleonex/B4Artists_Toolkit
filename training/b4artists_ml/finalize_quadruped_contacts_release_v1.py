"""Write the 0.30.0 routing receipt and final evidence audit."""
from pathlib import Path
import ast
import hashlib
import json
import time


ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "training/b4artists_ml/results"
DOCS = ROOT / "docs/b4artists_ml"


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    source_path = RESULTS / "quadruped-contacts-source-v1.json"
    package_path = RESULTS / "quadruped-contacts-package-v1.json"
    archive = ROOT / "releases/b4artists_ml_v0.30.0.zip"
    meta_path = DOCS / "package-test-v0.30.0.json"
    source, package, meta = read(source_path), read(package_path), read(meta_path)
    assert source["complete"] and source["suites"] == 52 and source["tests"] == 481
    assert source["runtime_hash_sets"] == 1
    assert package["passed"] and package["tests"] == 41 and package["exact_package"]
    assert package["offline_guard_self_test"] and not package["denied_runtime_calls"]
    assert meta["ready_for_local_testing"] and meta["package_matches_source"]
    assert sha(archive) == package["package_sha256"] == meta["sha256"]

    route = read(RESULTS / "orchestration-route-quadruped-orientation-v24.json")
    route["recorded_at"] = time.time()
    route["session_scope"] = "B4Artists Machine Learning experimental 0.30.0 four-paw contacts"
    evaluation = route["evaluation"]
    evaluation.update({
        "release": "0.30.0",
        "archive": "releases/b4artists_ml_v0.30.0.zip",
        "archive_sha256": sha(archive),
        "source_regression": source_path.relative_to(ROOT).as_posix(),
        "source_regression_sha256": sha(source_path),
        "source_suites": 52,
        "source_tests": 481,
        "source_assertions_passed": True,
        "runtime_hash_sets": 1,
        "exact_package": package_path.relative_to(ROOT).as_posix(),
        "exact_package_sha256": sha(package_path),
        "exact_package_tests": 41,
        "exact_package_assertions_passed": True,
        "outbound_runtime_calls": 0,
        "quadruped_profiles": ["cat", "horse", "wolf"],
        "quadruped_schema": "quadruped_v1",
        "animator_authored_four_paw_contacts_qualified": True,
        "automatic_contact_or_gait_inference_qualified": False,
        "host_shutdown_qualified": False,
        "human_reviewed_cases": 0,
        "cascadeur_results_present": False
    })
    evaluation.pop("deterministic_position_and_orientation_qualified", None)
    route["formal_goal"]["remaining_primary_gates"] = [
        "completed independent animator export and timed correction pass",
        "reviewed motion labels and accepted learned temporal motion",
        "joint and external forces plus arbitrary/deforming collision",
        "automatic quadruped contact/gait inference, balance/flight physics and learned motion",
        "quadruped pole/spine shaping and imported/custom rig adapters",
        "deformable secondary dynamics and production-character review",
        "executed matched Cascadeur evaluation"
    ]
    route_path = RESULTS / "orchestration-route-quadruped-contacts-v25.json"
    if route_path.exists():
        raise RuntimeError("Evidence exists: " + str(route_path))
    route_path.write_text(json.dumps(route, indent=2) + "\n", encoding="utf-8")

    python_paths = (list((ROOT / "b4artists_ml").glob("*.py")) +
                    list((ROOT / "tests").glob("test_b4artists_ml*.py")) +
                    list((ROOT / "training/b4artists_ml").glob("*.py")))
    for path in python_paths:
        ast.parse(path.read_bytes())
    protocol = read(ROOT / "training/b4artists_ml/quadruped_contacts_protocol_v1.json")
    audit = {
        "passed": True,
        "full_goal_complete": False,
        "release": "0.30.0",
        "python_files_parsed": len(python_paths),
        "runtime_files": len(source["runtime_sha256"]),
        "source_suites": 52,
        "source_tests": 481,
        "exact_package_tests": 41,
        "quadruped_profiles": ["cat", "horse", "wolf"],
        "package_files": meta["files"],
        "package_bytes": meta["bytes"],
        "package_sha256": meta["sha256"],
        "package_matches_source": True,
        "offline_guard": True,
        "outbound_calls": 0,
        "forbidden_identities_absent": meta["forbidden_identities_absent"],
        "host_shutdown_qualified": False,
        "human_reviews": 0,
        "cascadeur_comparisons": 0,
        "routing": {
            "execution": "T0-T4 preserved; DEGRADED_NATIVE_CONTINUE used",
            "evaluation": "S3 shadow/classification-only",
            "canonical_evaluator_completed": False,
            "model_calls": 0
        },
        "remaining": protocol["claim_boundaries"]["not_qualified"]
    }
    audit_path = RESULTS / "quadruped-contacts-final-audit-v1.json"
    if audit_path.exists():
        raise RuntimeError("Evidence exists: " + str(audit_path))
    audit_path.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"route": route_path.relative_to(ROOT).as_posix(),
                      "audit": audit_path.relative_to(ROOT).as_posix(),
                      "package_sha256": meta["sha256"],
                      "source_tests": source["tests"],
                      "package_tests": package["tests"]}, indent=2))


if __name__ == "__main__":
    main()
