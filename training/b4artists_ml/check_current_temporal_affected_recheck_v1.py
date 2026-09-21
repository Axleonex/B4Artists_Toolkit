"""Validate the isolated current-worktree affected temporal receipt."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "training" / "b4artists_ml" / "results"
RECEIPT = RESULTS / "current-temporal-affected-recheck-v1.json"
OUTPUT = RESULTS / "current-temporal-affected-recheck-validation-v1.json"
EXPECTED = {
    "test_b4artists_ml_temporal_preview_v1": 10,
    "test_b4artists_ml_temporal_runtime_v1": 8,
    "test_b4artists_ml_temporal_private_v1": 10,
    "test_b4artists_ml_temporal_cooperative": 11,
    "test_b4artists_ml_temporal_cooperative_pipeline": 15,
    "test_b4artists_ml_temporal_observer_cooperative": 3,
    "test_b4artists_ml_temporal_projection": 15,
    "test_b4artists_ml_anchor_observations": 9,
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _validate_sources(sources: dict[str, str]) -> None:
    for relative, expected in sources.items():
        path = ROOT / relative
        if not path.is_file() or _sha256(path) != expected:
            raise ValueError("Affected temporal source identity mismatch: " + relative)


def main() -> None:
    report = json.loads(RECEIPT.read_text(encoding="utf-8"))
    if report.get("schema") != "b4ml-current-temporal-affected-recheck-v1":
        raise ValueError("Unexpected affected temporal receipt schema")
    if report.get("status") != "PASS":
        raise ValueError("Affected temporal receipt did not pass")
    totals = report.get("totals", {})
    if totals != {"tests": 81, "passed": 81, "failures": 0, "errors": 0, "skipped": 0}:
        raise ValueError("Affected temporal totals are incomplete")
    runs = report.get("runs", [])
    if len(runs) != len(EXPECTED):
        raise ValueError("Affected temporal process count changed")
    if [run.get("module") for run in runs] != list(EXPECTED):
        raise ValueError("Affected temporal module order changed")
    for run in runs:
        expected = EXPECTED[run["module"]]
        if run.get("tests") != expected or run.get("passed") != expected:
            raise ValueError("Unexpected affected temporal module result")
        if run.get("successful") is not True or any(run.get(key) != 0 for key in ("failures", "errors", "skipped")):
            raise ValueError("Affected temporal assertions were incomplete")
        if run.get("host_exit_classification") not in ("clean", "known_shutdown_only"):
            raise ValueError("Unrecognized host exit classification")
    runtime_sources = report.get("runtime_sources", {})
    expected_runtime = {
        path.relative_to(ROOT).as_posix() for path in (ROOT / "b4artists_ml").glob("*.py")
    }
    if set(runtime_sources) != expected_runtime:
        raise ValueError("Affected temporal runtime source set changed")
    support_sources = report.get("support_sources", {})
    if len(support_sources) != 17:
        raise ValueError("Affected temporal support source set changed")
    _validate_sources(runtime_sources)
    _validate_sources(support_sources)
    boundary = report.get("claim_boundary", {})
    required_false = (
        "exact_package_qualified", "learned_temporal_quality_verified", "model_trained",
        "model_promoted", "independent_animator_usability_verified",
        "cascadeur_parity_verified", "full_goal_complete",
    )
    if boundary.get("current_worktree_only") is not True:
        raise ValueError("Current-worktree boundary is missing")
    if boundary.get("affected_temporal_behavior_verified") is not True:
        raise ValueError("Affected temporal behavior claim is missing")
    if any(boundary.get(key) is not False for key in required_false):
        raise ValueError("Affected temporal claim boundary widened")
    validation = {
        "schema": "b4ml-current-temporal-affected-recheck-validation-v1",
        "status": "PASS",
        "receipt": RECEIPT.relative_to(ROOT).as_posix(),
        "receipt_sha256": _sha256(RECEIPT),
        "runtime_source_count": len(runtime_sources),
        "support_source_count": len(support_sources),
        "isolated_processes": len(runs),
        "tests": totals["tests"],
        "current_worktree_only": True,
        "full_goal_complete": False,
    }
    OUTPUT.write_text(json.dumps(validation, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, indent=2))


if __name__ == "__main__":
    main()
