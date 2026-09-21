"""Validate the isolated current-worktree temporal ownership receipt."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "training" / "b4artists_ml" / "results"
RECEIPT = RESULTS / "current-temporal-ownership-recheck-v1.json"
OUTPUT = RESULTS / "current-temporal-ownership-recheck-validation-v1.json"
EXPECTED = {
    "test_b4artists_ml_temporal_preview_v1": 10,
    "test_b4artists_ml_temporal_private_v1": 10,
    "test_b4artists_ml_temporal_cooperative": 11,
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    report = json.loads(RECEIPT.read_text(encoding="utf-8"))
    if report.get("schema") != "b4ml-current-temporal-ownership-recheck-v1":
        raise ValueError("Unexpected temporal ownership receipt schema")
    if report.get("status") != "PASS":
        raise ValueError("Temporal ownership receipt did not pass")
    totals = report.get("totals", {})
    if totals != {"tests": 31, "passed": 31, "failures": 0, "errors": 0, "skipped": 0}:
        raise ValueError("Temporal ownership totals are incomplete")
    runs = report.get("runs", [])
    if len(runs) != len(EXPECTED):
        raise ValueError("Temporal ownership process count changed")
    for run in runs:
        expected = EXPECTED.get(run.get("module"))
        if expected is None or run.get("tests") != expected or run.get("passed") != expected:
            raise ValueError("Unexpected temporal ownership module result")
        if run.get("successful") is not True or any(run.get(key) != 0 for key in ("failures", "errors", "skipped")):
            raise ValueError("Temporal ownership assertions were incomplete")
        if run.get("host_exit_classification") not in ("clean", "known_shutdown_only"):
            raise ValueError("Unrecognized host exit classification")
    boundary = report.get("claim_boundary", {})
    required_false = (
        "exact_package_qualified", "learned_temporal_quality_verified", "model_trained",
        "model_promoted", "independent_animator_usability_verified",
        "cascadeur_parity_verified", "full_goal_complete",
    )
    if boundary.get("current_worktree_only") is not True:
        raise ValueError("Current-worktree boundary is missing")
    if boundary.get("workflow_ownership_and_recovery_verified") is not True:
        raise ValueError("Ownership claim is missing")
    if any(boundary.get(key) is not False for key in required_false):
        raise ValueError("Temporal ownership claim boundary widened")
    sources = report.get("sources", {})
    if len(sources) != 9:
        raise ValueError("Temporal ownership source set changed")
    for relative, expected in sources.items():
        path = ROOT / relative
        if not path.is_file() or _sha256(path) != expected:
            raise ValueError("Temporal ownership source identity mismatch: " + relative)
    validation = {
        "schema": "b4ml-current-temporal-ownership-recheck-validation-v1",
        "status": "PASS",
        "receipt": RECEIPT.relative_to(ROOT).as_posix(),
        "receipt_sha256": _sha256(RECEIPT),
        "source_count": len(sources),
        "isolated_processes": len(runs),
        "tests": totals["tests"],
        "current_worktree_only": True,
        "full_goal_complete": False,
    }
    OUTPUT.write_text(json.dumps(validation, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, indent=2))


if __name__ == "__main__":
    main()
