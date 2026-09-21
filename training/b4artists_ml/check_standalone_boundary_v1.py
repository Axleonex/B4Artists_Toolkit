"""Audit the B4ML standalone boundary without changing protected add-ons."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
TRAIN = ROOT / "training" / "b4artists_ml"
RESULTS = TRAIN / "results"
BASELINE = RESULTS / "goal-limit-delivery-audit-v1.json"
OUT = RESULTS / "standalone-boundary-validation-v1.json"
RUNTIME = ROOT / "b4artists_ml"
FORBIDDEN = re.compile(r"(?<![A-Za-z0-9_])(ghost_tool|anim_assist)(?![A-Za-z0-9_])", re.IGNORECASE)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> dict:
    baseline = json.loads(BASELINE.read_text(encoding="utf-8-sig"))
    protected = baseline.get("protected_addons_sha256")
    if not isinstance(protected, dict) or len(protected) != 218:
        raise ValueError("Protected-addon baseline is missing or incomplete")

    protected_mismatches = []
    for relative, expected in sorted(protected.items()):
        path = ROOT / relative
        if not path.is_file():
            protected_mismatches.append({"path": relative, "reason": "missing"})
        elif sha256(path) != expected:
            protected_mismatches.append({"path": relative, "reason": "sha256_mismatch"})

    runtime_files = sorted(
        path for path in RUNTIME.rglob("*.py") if "__pycache__" not in path.parts
    )
    forbidden_references = []
    for path in runtime_files:
        text = path.read_text(encoding="utf-8-sig")
        matches = sorted(set(match.group(1).lower() for match in FORBIDDEN.finditer(text)))
        if matches:
            forbidden_references.append({
                "path": path.relative_to(ROOT).as_posix(),
                "references": matches,
            })

    init_text = (RUNTIME / "__init__.py").read_text(encoding="utf-8-sig")
    host_guard = {
        "is_bforartists_function": "def is_bforartists" in init_text,
        "bforartists_host_tokens": "bforartists" in init_text.lower(),
        "runtime_dependency_absent": not forbidden_references,
    }
    runtime_hashes = {
        path.relative_to(ROOT).as_posix(): sha256(path)
        for path in runtime_files
    }
    if protected_mismatches or forbidden_references or not all(host_guard.values()):
        status = "FAIL"
    else:
        status = "PASS"
    report = {
        "schema": "b4ml-standalone-boundary-validation-v1",
        "status": status,
        "scope": (
            "Read-only B4ML standalone-boundary audit. It verifies protected "
            "Ghost Tool and Anim Assist hashes, forbidden runtime references, and "
            "the Bforartists host guard; it does not prove usability or full-goal completion."
        ),
        "protected_addons": {
            "baseline": BASELINE.relative_to(ROOT).as_posix(),
            "baseline_sha256": sha256(BASELINE),
            "files_checked": len(protected),
            "mismatches": protected_mismatches,
            "unchanged": not protected_mismatches,
        },
        "b4ml_runtime": {
            "files_checked": len(runtime_files),
            "runtime_sha256": runtime_hashes,
            "forbidden_references": forbidden_references,
            "host_guard": host_guard,
        },
        "claims": {
            "standalone_boundary_verified": status == "PASS",
            "independent_animator_usability_verified": False,
            "learned_temporal_quality_verified": False,
            "cascadeur_parity_verified": False,
            "full_goal_complete": False,
        },
    }
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    if status != "PASS":
        raise SystemExit(1)
    return report


if __name__ == "__main__":
    main()
