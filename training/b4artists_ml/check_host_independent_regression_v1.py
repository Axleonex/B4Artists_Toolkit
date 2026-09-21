"""Validate the reproducible host-independent regression receipt."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RECEIPT = ROOT / "training" / "b4artists_ml" / "results" / "host-independent-regression-v1.json"
OUTPUT = ROOT / "training" / "b4artists_ml" / "results" / "host-independent-regression-validation-v1.json"
RUNNER = ROOT / "training" / "b4artists_ml" / "run_host_independent_regression_v1.py"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    report = json.loads(RECEIPT.read_text(encoding="utf-8"))
    if report.get("schema") != "b4ml-host-independent-regression-v1":
        raise ValueError("Unexpected host-independent regression schema")
    if report.get("status") != "PASS":
        raise ValueError("Host-independent regression did not pass")
    pytest_report = report.get("pytest", {})
    if (pytest_report.get("exit_code") != 0
            or pytest_report.get("failed_calls") != 0
            or pytest_report.get("collection_errors") != 0
            or pytest_report.get("skipped_calls") != 0
            or pytest_report.get("passed_calls", 0) <= 0):
        raise ValueError("Host-independent regression receipt is not clean")
    selected = report.get("selected_sources", {})
    if len(selected) != 56:
        raise ValueError("Unexpected selected source count")
    for relative, expected in selected.items():
        path = ROOT / relative
        if not path.is_file() or _sha256(path) != expected:
            raise ValueError("Selected source changed: " + relative)
    if _sha256(RUNNER) != report.get("runner_sha256"):
        raise ValueError("Regression runner changed")
    validator = ROOT / report.get("validator", "")
    if not validator.is_file() or _sha256(validator) != report.get("validator_sha256"):
        raise ValueError("Regression validator changed")
    claims = report.get("claim_boundary", {})
    if any(claims.get(key) is not False for key in (
        "host_runtime_verified", "independent_animator_usability_verified",
        "learned_temporal_quality_verified", "cascadeur_comparison_verified",
        "full_goal_complete",
    )):
        raise ValueError("Regression claim boundary widened")
    validation = {
        "schema": "b4ml-host-independent-regression-validation-v1",
        "status": "PASS",
        "receipt": RECEIPT.relative_to(ROOT).as_posix(),
        "receipt_sha256": _sha256(RECEIPT),
        "selected_source_count": len(selected),
        "excluded_source_count": len(report.get("excluded_host_bound_sources", {})),
        "collected": pytest_report["collected"],
        "passed_calls": pytest_report["passed_calls"],
        "full_goal_complete": False,
    }
    OUTPUT.write_text(json.dumps(validation, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, indent=2))


if __name__ == "__main__":
    main()
