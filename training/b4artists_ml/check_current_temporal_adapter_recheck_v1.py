"""Validate the current-worktree temporal/adapter Bforartists receipt."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "training" / "b4artists_ml" / "results"
RECEIPT = RESULTS / "current-temporal-adapter-recheck-v1.json"
OUTPUT = RESULTS / "current-temporal-adapter-recheck-validation-v1.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    report = json.loads(RECEIPT.read_text(encoding="utf-8"))
    if report.get("schema") != "b4ml-current-temporal-adapter-recheck-v1":
        raise ValueError("Unexpected temporal adapter receipt schema")
    result = report.get("result", {})
    if result != {
        "tests": 24,
        "passed": 24,
        "failed": 0,
        "errors": 0,
        "skipped": 0,
        "was_successful": True,
        "failure_ids": [],
        "error_ids": [],
    }:
        raise ValueError("Temporal adapter assertions are incomplete")
    if report.get("modules") != [
        "test_b4artists_ml_temporal_runtime_math_v1",
        "test_b4artists_ml_rig_observations",
    ]:
        raise ValueError("Temporal adapter module set changed")
    boundary = report.get("claim_boundary", {})
    required_false = (
        "exact_package_qualified",
        "learned_temporal_quality_verified",
        "model_trained",
        "model_promoted",
        "independent_animator_usability_verified",
        "cascadeur_parity_verified",
        "full_goal_complete",
    )
    if boundary.get("current_worktree_only") is not True or any(
        boundary.get(key) is not False for key in required_false
    ):
        raise ValueError("Temporal adapter claim boundary widened")
    sources = report.get("sources", {})
    if len(sources) != 6:
        raise ValueError("Temporal adapter source set changed")
    for relative, expected in sources.items():
        path = ROOT / relative
        if not path.is_file() or _sha256(path) != expected:
            raise ValueError("Temporal adapter source identity mismatch: " + relative)
    validation = {
        "schema": "b4ml-current-temporal-adapter-recheck-validation-v1",
        "status": "PASS",
        "receipt": RECEIPT.relative_to(ROOT).as_posix(),
        "receipt_sha256": _sha256(RECEIPT),
        "source_count": len(sources),
        "tests": result["tests"],
        "current_worktree_only": True,
        "full_goal_complete": False,
    }
    OUTPUT.write_text(json.dumps(validation, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, indent=2))


if __name__ == "__main__":
    main()
