"""Aggregate the hash-consistent 0.28.0 quadruped-pose source regression."""
from pathlib import Path
import hashlib
import json


ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "training/b4artists_ml/results"
OUT = RESULTS / "quadruped-pose-source-v1.json"


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if OUT.exists():
        raise RuntimeError("Evidence exists: " + str(OUT))
    prior = read(RESULTS / "quadruped-adapter-release-v1-regression.json")
    current = read(RESULTS / "quadruped-pose-release-v1-regression.json")
    protocol_path = ROOT / "training/b4artists_ml/quadruped_pose_protocol_v1.json"
    protocol = read(protocol_path)
    expected = [row["suite"] for row in prior] + ["test_b4artists_ml_quadruped_pose"]
    assert protocol["release"] == "0.28.0"
    assert [row["suite"] for row in current] == expected
    assert len(current) == len(set(expected)) == 51
    assert sum(row["tests"] for row in current) == 478
    assert all(row["assertions_passed"] and not row.get("failures")
               and not row.get("errors") and not row.get("skipped") for row in current)
    runtime_sets = {tuple(sorted(row["runtime_sha256"].items())) for row in current}
    assert len(runtime_sets) == 1
    runtime = current[0]["runtime_sha256"]
    source = {path.relative_to(ROOT).as_posix(): sha(path)
              for path in (ROOT / "b4artists_ml").glob("*.py")}
    assert source == runtime
    pose = next(row for row in current if row["suite"] == "test_b4artists_ml_quadruped_pose")
    assert pose["tests"] == 4
    direct = read(RESULTS / "quadruped-pose-v1.json")
    assert direct["complete"] and direct["tests_run"] == 4
    assert [row["profile"] for row in direct["records"]] == ["cat", "horse", "wolf"]
    assert all(row["metrics"]["max_paw_error"] <= row["metrics"]["tolerance"]
               and row["metrics"]["body_error"] <= row["metrics"]["tolerance"]
               and row["source_restored"] and row["anchor_saved"] for row in direct["records"])
    report = {
        "complete": True,
        "full_goal_complete": False,
        "release": "0.28.0",
        "protocol": protocol_path.relative_to(ROOT).as_posix(),
        "protocol_sha256": sha(protocol_path),
        "regression": "training/b4artists_ml/results/quadruped-pose-release-v1-regression.json",
        "suites": len(current),
        "tests": sum(row["tests"] for row in current),
        "runtime_hash_sets": len(runtime_sets),
        "runtime_sha256": runtime,
        "host_shutdown_qualified": all(row.get("host_exit") == 0 for row in current),
        "known_host_exit": sorted(set(row.get("host_exit") for row in current)),
        "quadruped_pose": direct,
        "human_reviews": 0,
        "cascadeur_comparisons": 0,
        "outbound_calls": 0,
        "qualification": protocol["claim_boundaries"],
    }
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in
                      ("complete", "release", "suites", "tests", "runtime_hash_sets",
                       "host_shutdown_qualified")}, indent=2))


if __name__ == "__main__":
    main()
