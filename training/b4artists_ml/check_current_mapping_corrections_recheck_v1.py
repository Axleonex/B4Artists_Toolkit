"""Validate the current mapping-correction adapter receipt."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RECEIPT = ROOT / "training" / "b4artists_ml" / "results" / "current-mapping-corrections-recheck-v3.json"
OUTPUT = ROOT / "training" / "b4artists_ml" / "results" / "current-mapping-corrections-recheck-validation-v2.json"
RUNNER = ROOT / "training" / "b4artists_ml" / "run_current_mapping_corrections_recheck_v1.py"
TEST = ROOT / "tests" / "test_b4artists_ml_mapping_corrections_v1.py"
MODULE = "test_b4artists_ml_mapping_corrections_v1"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    report = json.loads(RECEIPT.read_text(encoding="utf-8"))
    if report.get("schema") != "b4ml-current-mapping-corrections-recheck-v1":
        raise ValueError("Unexpected mapping-correction recheck schema")
    if report.get("status") != "PASS":
        raise ValueError("Mapping-correction recheck did not pass")
    suite = report.get("suite", {})
    if (suite.get("module") != MODULE or suite.get("tests") != 11
            or suite.get("focused_tests") != 11
            or suite.get("passed") is not True
            or suite.get("failures") != 0
            or suite.get("errors") != 0
            or suite.get("skips") != 0):
        raise ValueError("Mapping-correction suite dimensions changed")
    host = report.get("host", {})
    if host.get("exit_code") != 0 and host.get("exit_classification") != "known_shutdown_only":
        raise ValueError("Unexpected host exit classification")
    for relative, expected in report.get("runtime_source_sha256", {}).items():
        path = ROOT / relative
        if not path.is_file() or _sha256(path) != expected:
            raise ValueError("Runtime source changed: " + relative)
    if _sha256(TEST) != report.get("focused_test_sha256"):
        raise ValueError("Mapping-correction test source changed")
    if _sha256(RUNNER) != report.get("orchestrator_sha256"):
        raise ValueError("Recheck runner changed")
    path = ROOT / report["focused_report"]
    if not path.is_file() or _sha256(path) != report["focused_report_sha256"]:
        raise ValueError("Focused report changed")
    claims = report.get("claim_boundary", {})
    for key in ("boneforge_verified", "rigify_basic_verified", "rigify_default_verified",
                "imported_humanoid_verified"):
        if claims.get(key) is not True:
            raise ValueError("Adapter claim missing: " + key)
    for key in ("learned_temporal_quality_verified", "independent_animator_usability_verified",
                "cascadeur_parity_verified", "full_goal_complete"):
        if claims.get(key) is not False:
            raise ValueError("Mapping claim boundary widened: " + key)
    validation = {
        "schema": "b4ml-current-mapping-corrections-recheck-validation-v1",
        "status": "PASS",
        "receipt": RECEIPT.relative_to(ROOT).as_posix(),
        "receipt_sha256": _sha256(RECEIPT),
        "tests": suite["tests"],
        "adapters": ["BoneForge", "Rigify Basic", "Rigify Default",
                     "Mocap Humanoid", "Unity Humanoid", "Unreal Mannequin"],
        "host_exit_classification": host["exit_classification"],
        "full_goal_complete": False,
    }
    OUTPUT.write_text(json.dumps(validation, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, indent=2))


if __name__ == "__main__":
    main()
