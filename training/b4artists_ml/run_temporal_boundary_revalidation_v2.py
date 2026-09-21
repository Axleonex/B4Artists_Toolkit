"""Revalidate the learned-temporal data boundary without training a model."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import importlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from training.b4artists_ml import check_temporal_training_boundary_v1 as boundary
from training.b4artists_ml import validate_temporal_corpus_intake_v1 as intake


OUTPUT = ROOT / "docs" / "b4artists_ml" / "temporal-boundary-revalidation-v2.json"
TEST_MODULES = (
    "tests.test_b4artists_ml_temporal_corpus_intake_v1",
    "tests.test_b4artists_ml_temporal_training_boundary_v1",
)
SOURCES = (
    "training/b4artists_ml/validate_temporal_corpus_intake_v1.py",
    "training/b4artists_ml/check_temporal_training_boundary_v1.py",
    "tests/test_b4artists_ml_temporal_corpus_intake_v1.py",
    "tests/test_b4artists_ml_temporal_training_boundary_v1.py",
    "training/b4artists_ml/run_temporal_boundary_revalidation_v2.py",
    "training/b4artists_ml/check_temporal_boundary_revalidation_v2.py",
    "training/b4artists_ml/data_manifest.json",
    "training/b4artists_ml/results/action-rig-disjoint-audit-v1.json",
    "training/b4artists_ml/results/action-disjoint-protocol-v1.json",
    "training/b4artists_ml/results/cached-skeleton-provenance-v1.json",
    "training/b4artists_ml/results/joint-action-skeleton-protocol-v1.json",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _run_tests() -> dict:
    suite = unittest.TestSuite()
    for name in TEST_MODULES:
        suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(importlib.import_module(name)))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    report = {
        "tests": result.testsRun,
        "passed": result.testsRun - len(result.failures) - len(result.errors) - len(result.skipped),
        "failures": len(result.failures),
        "errors": len(result.errors),
        "skipped": len(result.skipped),
        "successful": result.wasSuccessful(),
    }
    if report != {
        "tests": 12, "passed": 12, "failures": 0, "errors": 0,
        "skipped": 0, "successful": True,
    }:
        raise RuntimeError("Temporal boundary regression did not pass: " + json.dumps(report))
    return report


def main() -> None:
    tests = _run_tests()
    intake_report = intake.build_report(
        intake.DEFAULT_MANIFEST, intake.DEFAULT_LABELS, intake.DEFAULT_IDENTITY
    )
    intake.DEFAULT_OUT.write_text(
        json.dumps(intake_report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    gate_report = boundary.build_gate(
        _load(boundary.AUDIT),
        _load(boundary.PROTOCOL),
        _load(boundary.SKELETON_AUDIT) if boundary.SKELETON_AUDIT.is_file() else None,
        _load(boundary.JOINT_PROTOCOL) if boundary.JOINT_PROTOCOL.is_file() else None,
        intake_report,
    )
    boundary.OUT.write_text(
        json.dumps(gate_report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    if intake_report["status"] != "BLOCKED_INTAKE_MISSING_EVIDENCE":
        raise RuntimeError("Current corpus unexpectedly passed intake")
    if gate_report["status"] != "BLOCKED_DATA_BOUNDARY_UNQUALIFIED":
        raise RuntimeError("Current corpus unexpectedly passed the parent boundary")
    if intake_report["manifest"]["missing_required_fields"] != [
        "action_id", "skeleton_id", "source_rig_id"
    ]:
        raise RuntimeError("Current manifest failure set changed")
    if intake_report["reviewed_contact_intent"]["present"] is not False:
        raise RuntimeError("Unreviewed contact/intent evidence appeared")
    if intake_report["identity_authorization"]["present"] is not False:
        raise RuntimeError("Unverified reviewer authorization appeared")
    if gate_report["model_training_permitted"] or gate_report["model_promotion_permitted"]:
        raise RuntimeError("Temporal training boundary widened")
    report = {
        "schema": "b4ml-temporal-boundary-revalidation-v2",
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "status": "PASS_FAIL_CLOSED",
        "scope": (
            "Current-worktree host-independent boundary regression. No data is acquired, "
            "no human evidence is inferred, and no model is trained or promoted."
        ),
        "suite": tests,
        "current_intake": {
            "status": intake_report["status"],
            "manifest_sha256": intake_report["manifest"]["manifest_sha256"],
            "rows": intake_report["manifest"]["row_count"],
            "missing_required_fields": intake_report["manifest"]["missing_required_fields"],
            "reviewed_contact_intent_present": False,
            "identity_authorization_present": False,
            "receipt": intake.DEFAULT_OUT.relative_to(ROOT).as_posix(),
            "receipt_sha256": _sha256(intake.DEFAULT_OUT),
        },
        "parent_boundary": {
            "status": gate_report["status"],
            "model_training_permitted": False,
            "model_promotion_permitted": False,
            "receipt": boundary.OUT.relative_to(ROOT).as_posix(),
            "receipt_sha256": _sha256(boundary.OUT),
        },
        "sources": {relative: _sha256(ROOT / relative) for relative in SOURCES},
        "claim_boundary": {
            "learned_temporal_quality_verified": False,
            "independent_animator_usability_verified": False,
            "cascadeur_parity_verified": False,
            "runtime_promoted": False,
            "full_goal_complete": False,
        },
    }
    OUTPUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
