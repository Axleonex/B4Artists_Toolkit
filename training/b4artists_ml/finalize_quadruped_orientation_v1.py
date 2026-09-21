"""Aggregate the hash-consistent 0.29.0 quadruped-orientation regression."""
from pathlib import Path
import hashlib
import json


ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "training/b4artists_ml/results"
OUT = RESULTS / "quadruped-orientation-source-v1.json"


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if OUT.exists():
        raise RuntimeError("Evidence exists: " + str(OUT))
    regression_path = RESULTS / "quadruped-orientation-release-v1-regression.json"
    rows = read(regression_path)
    protocol_path = ROOT / "training/b4artists_ml/quadruped_orientation_protocol_v1.json"
    protocol = read(protocol_path)
    assert protocol["release"] == "0.29.0"
    assert len(rows) == 51 and len({row["suite"] for row in rows}) == 51
    assert sum(row["tests"] for row in rows) == 478
    assert all(row["assertions_passed"] and not row.get("failures")
               and not row.get("errors") and not row.get("skipped") for row in rows)
    runtime_sets = {tuple(sorted(row["runtime_sha256"].items())) for row in rows}
    assert len(runtime_sets) == 1
    runtime = rows[0]["runtime_sha256"]
    source = {path.relative_to(ROOT).as_posix(): sha(path)
              for path in (ROOT / "b4artists_ml").glob("*.py")}
    assert source == runtime
    direct_path = RESULTS / "quadruped-pose-orientation-v1.json"
    direct = read(direct_path)
    assert direct["complete"] and direct["tests_run"] == 4
    assert [row["profile"] for row in direct["records"]] == ["cat", "horse", "wolf"]
    assert direct["runtime_sha256"]["quadruped_pose"] == runtime["b4artists_ml/quadruped_pose.py"]
    assert all(row["metrics"]["max_paw_error"] <= row["metrics"]["tolerance"]
               and row["metrics"]["body_error"] <= row["metrics"]["tolerance"]
               and row["metrics"]["max_orientation_error"] <= row["metrics"]["orientation_tolerance"]
               and len(row["metrics"]["orientation_errors"]) == 5
               and row["source_restored"] and row["anchor_saved"]
               for row in direct["records"])
    report = {
        "complete": True,
        "full_goal_complete": False,
        "release": "0.29.0",
        "protocol": protocol_path.relative_to(ROOT).as_posix(),
        "protocol_sha256": sha(protocol_path),
        "regression": regression_path.relative_to(ROOT).as_posix(),
        "regression_sha256": sha(regression_path),
        "direct_evidence": direct_path.relative_to(ROOT).as_posix(),
        "direct_evidence_sha256": sha(direct_path),
        "suites": len(rows),
        "tests": sum(row["tests"] for row in rows),
        "runtime_hash_sets": len(runtime_sets),
        "runtime_sha256": runtime,
        "host_shutdown_qualified": all(row.get("host_exit") == 0 for row in rows),
        "known_host_exit": sorted(set(row.get("host_exit") for row in rows)),
        "quadruped_orientation": direct,
        "human_reviews": 0,
        "cascadeur_comparisons": 0,
        "outbound_calls": 0,
        "qualification": protocol["claim_boundaries"]
    }
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in
                      ("complete", "release", "suites", "tests", "runtime_hash_sets",
                       "host_shutdown_qualified")}, indent=2))


if __name__ == "__main__":
    main()
