"""Validate the current-worktree imported-humanoid host receipt."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RECEIPT = ROOT / "training" / "b4artists_ml" / "results" / "current-imported-humanoids-recheck-v1.json"
OUTPUT = ROOT / "training" / "b4artists_ml" / "results" / "current-imported-humanoids-recheck-validation-v1.json"
RUNNER = ROOT / "training" / "b4artists_ml" / "run_current_imported_humanoids_recheck_v1.py"
HOST_RUNNER = ROOT / "training" / "b4artists_ml" / "run_unittest_report.py"
MODULE = "test_b4artists_ml_imported_humanoids"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    report = json.loads(RECEIPT.read_text(encoding="utf-8"))
    if report.get("schema") != "b4ml-current-imported-humanoids-recheck-v1":
        raise ValueError("Unexpected imported-humanoid recheck schema")
    if report.get("status") != "PASS":
        raise ValueError("Imported-humanoid recheck did not pass")
    suite = report.get("suite", {})
    if suite != {
        "module": MODULE, "tests": 12, "passed": True,
        "failures": 0, "errors": 0, "skips": 0,
        "elapsed_seconds": suite.get("elapsed_seconds"),
    }:
        raise ValueError("Imported-humanoid suite dimensions changed")
    host = report.get("host", {})
    if host.get("exit_code") != 0 and host.get("exit_classification") != "known_shutdown_only":
        raise ValueError("Unexpected host exit classification")
    for relative, expected in report.get("runtime_source_sha256", {}).items():
        path = ROOT / relative
        if not path.is_file() or _sha256(path) != expected:
            raise ValueError("Runtime source changed: " + relative)
    test_path = ROOT / "tests" / f"{MODULE}.py"
    if _sha256(test_path) != report.get("test_sha256"):
        raise ValueError("Imported-humanoid test source changed")
    if _sha256(HOST_RUNNER) != report.get("host_runner_sha256"):
        raise ValueError("Host test runner changed")
    if _sha256(RUNNER) != report.get("orchestrator_sha256"):
        raise ValueError("Recheck runner changed")
    host_report = ROOT / report["host_report"]
    if not host_report.is_file() or _sha256(host_report) != report.get("host_report_sha256"):
        raise ValueError("Child host report changed")
    claims = report.get("claim_boundary", {})
    if claims.get("imported_humanoid_workflow_verified") is not True:
        raise ValueError("Imported workflow was not recorded")
    if any(claims.get(key) is not False for key in (
        "learned_temporal_quality_verified", "independent_animator_usability_verified",
        "cascadeur_parity_verified", "full_goal_complete",
    )):
        raise ValueError("Imported-humanoid claim boundary widened")
    validation = {
        "schema": "b4ml-current-imported-humanoids-recheck-validation-v1",
        "status": "PASS",
        "receipt": RECEIPT.relative_to(ROOT).as_posix(),
        "receipt_sha256": _sha256(RECEIPT),
        "tests": suite["tests"],
        "host_exit_classification": host["exit_classification"],
        "imported_humanoid_workflow_verified": True,
        "full_goal_complete": False,
    }
    OUTPUT.write_text(json.dumps(validation, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, indent=2))


if __name__ == "__main__":
    main()
