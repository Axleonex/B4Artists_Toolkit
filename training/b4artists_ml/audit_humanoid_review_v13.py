"""Audit the v13 current-release humanoid review checkpoint."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "training/b4artists_ml/results/humanoid-review-v13-final-audit.json"


def sha(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def read(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def main() -> None:
    evidence_path = "training/b4artists_ml/results/humanoid-review-v13-evidence.json"
    package_path = "docs/b4artists_ml/package-test-v0.25.0.json"
    evidence = read(evidence_path)
    package = read(package_path)

    scripts = [
        "training/b4artists_ml/build_procedural_vertical_slice_v13.py",
        "training/b4artists_ml/finalize_procedural_vertical_slice_v13.py",
        "training/b4artists_ml/build_procedural_vertical_slice_reviewer_v2.py",
        "training/b4artists_ml/check_procedural_vertical_slice_reviewer_v2.py",
        "training/b4artists_ml/check_procedural_vertical_slice_human_review_v2.py",
        "training/b4artists_ml/smoke_procedural_vertical_slice_reviewer_browser_v3.py",
        "training/b4artists_ml/correction_trial_v1.py",
        "training/b4artists_ml/launch_correction_trial_v1.py",
        "training/b4artists_ml/check_correction_trial_v2.py",
        "training/b4artists_ml/validate_correction_trial_v1.py",
        "training/b4artists_ml/check_correction_trial_validator_v1.py",
        "training/b4artists_ml/finalize_humanoid_review_v13.py",
    ]
    syntax_hashes = {}
    for relative in scripts:
        source = (ROOT / relative).read_text(encoding="utf-8")
        ast.parse(source, filename=relative)
        syntax_hashes[relative] = sha(relative)

    assert evidence["complete"] and evidence["release"] == package["version"] == "0.25.0"
    assert evidence["runtime_unchanged_from_release"] and evidence["runtime_hashes_exact"]
    assert evidence["archive_sha256"] == package["sha256"] == sha("releases/b4artists_ml_v0.25.0.zip")
    for relative, expected in package["runtime_sha256"].items():
        assert expected == package["tested_runtime_sha256"][relative] == sha(relative)
    for relative, expected in evidence["evidence"].items():
        assert sha(relative) == expected

    assert evidence["procedural_matrix"]["cases"] == evidence["procedural_matrix"]["passed"] == 32
    assert evidence["procedural_matrix"]["failed"] == 0
    assert evidence["blind_reviewer"]["static_validation_passed"]
    assert evidence["blind_reviewer"]["browser_interaction_passed"]
    assert evidence["blind_reviewer"]["reviewed_cases"] == 0
    assert evidence["correction_trial"]["smoke_passed"]
    assert evidence["correction_trial"]["synthetic_rejected_as_human"]
    assert evidence["correction_trial"]["human_reviewed_cases"] == 0
    assert evidence["orchestration"]["evaluation_depth"] == "S3"
    assert evidence["orchestration"]["review_mode"] == "shadow/classification-only"
    assert evidence["orchestration"]["model_calls"] == 0
    assert all(value is False for key, value in evidence["claims"].items() if key != "automated_procedural_floor_current_release")
    assert evidence["claims"]["automated_procedural_floor_current_release"]
    assert not evidence["full_goal_complete"]

    docs = [
        "docs/b4artists_ml/HUMANOID-REVIEW-AND-CORRECTION-v13.md",
        "docs/b4artists_ml/PROJECT.md",
        "docs/b4artists_ml/ROADMAP.md",
        "docs/b4artists_ml/REQUIREMENTS.md",
        "docs/b4artists_ml/VALIDATION.md",
        "docs/b4artists_ml/USER_GUIDE.md",
    ]
    doc_hashes = {relative: sha(relative) for relative in docs}
    combined = "\n".join((ROOT / relative).read_text(encoding="utf-8") for relative in docs)
    for phrase in (
        "human reviewed cases remain zero",
        "Cascadeur parity",
        "synthetic",
        "HUMANOID-REVIEW-AND-CORRECTION-v13.md",
    ):
        assert phrase.lower() in combined.lower()

    report = {
        "schema": "b4ml-humanoid-review-v13-final-audit",
        "complete": True,
        "release": "0.25.0",
        "syntax_valid_scripts": len(scripts),
        "syntax_sha256": syntax_hashes,
        "evidence_path": evidence_path,
        "evidence_sha256": sha(evidence_path),
        "evidence_hashes_exact": True,
        "runtime_hashes_exact": True,
        "archive_hash_exact": True,
        "documentation_sha256": doc_hashes,
        "procedural_cases_passed": 32,
        "browser_interaction_passed": True,
        "correction_smoke_passed": True,
        "synthetic_rejected_as_human": True,
        "human_reviewed_cases": 0,
        "model_calls": 0,
        "cascadeur_results_present": False,
        "learned_temporal_motion_accepted": False,
        "clean_host_shutdown": False,
        "runtime_or_package_rebuilt": False,
        "full_goal_complete": False,
        "script_sha256": sha("training/b4artists_ml/audit_humanoid_review_v13.py"),
    }
    OUT.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "complete": True,
        "syntax_valid_scripts": len(scripts),
        "evidence_hashes_exact": True,
        "runtime_hashes_exact": True,
        "procedural_cases_passed": 32,
        "human_reviewed_cases": 0,
        "model_calls": 0,
        "full_goal_complete": False,
    }, indent=2))


if __name__ == "__main__":
    main()
