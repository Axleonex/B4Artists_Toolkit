"""Validate that the external human-gate handoff surface is locally complete.

This is a static readiness check only.  It proves that the documented pages,
validators, probes, and current claim-boundary receipt are available.  It does
not create human evidence, authorize training, or claim Cascadeur parity.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve()
ROOT = Path(os.environ.get(
    "B4ML_REPO",
    r"X:\Scripting Attempts\B4Artists_Tools\B4Artists_Anim_Tools_github",
))
TRAIN = ROOT / "training" / "b4artists_ml"
RESULTS = TRAIN / "results"
OUT = RESULTS / "human-gates-handoff-validation-v1.json"

REQUIRED = {
    "handoff_document": ROOT / "docs" / "b4artists_ml" / "NEXT-HUMAN-GATES-v1.md",
    "delivery_document": ROOT / "docs" / "b4artists_ml" / "DELIVERY-ORDER-v1.md",
    "humanoid_reviewer_page": RESULTS / "procedural-vertical-slice-reviewer-v2" / "reviewer.html",
    "humanoid_review_validator": TRAIN / "check_procedural_vertical_slice_human_review_v2.py",
    "correction_trial_launcher": TRAIN / "launch_correction_trial_v1.py",
    "correction_trial_validator": TRAIN / "validate_correction_trial_v1.py",
    "temporal_intake_validator": TRAIN / "validate_temporal_corpus_intake_v1.py",
    "cascadeur_import_probe": TRAIN / "cascadeur_import_audit_console_v1.py",
    "cascadeur_embedded_gate_runner": TRAIN / "cascadeur_embedded_gate_runner_console_v1.py",
    "cascadeur_capability_probe": TRAIN / "cascadeur_capability_probe_console_v1.py",
    "cascadeur_capability_validator": TRAIN / "check_cascadeur_capability_probe_v1.py",
    "cascadeur_standard_rig_probe": TRAIN / "cascadeur_standard_rig_preflight_console_v1.py",
    "cascadeur_standard_rig_validator": TRAIN / "check_cascadeur_standard_rig_preflight_v1.py",
    "cascadeur_import_diagnostic": RESULTS / "cascadeur-import-audit-diagnostic-v1.json",
    "cascadeur_standard_rig_diagnostic": RESULTS / "cascadeur-standard-rig-preflight-diagnostic-v1.json",
    "cascadeur_command_package_init": TRAIN / "cascadeur_cli" / "__init__.py",
    "cascadeur_command_module_init": TRAIN / "cascadeur_cli" / "commands" / "__init__.py",
    "cascadeur_command_wrapper": TRAIN / "cascadeur_cli" / "commands" / "b4ml_cascadeur_import_audit.py",
    "cascadeur_command_wrapper_validator": TRAIN / "check_cascadeur_command_wrapper_v1.py",
    "cascadeur_command_wrapper_readiness": RESULTS / "cascadeur-command-wrapper-readiness-v1.json",
    "cascadeur_command_wrapper_stager": TRAIN / "stage_cascadeur_command_wrapper_v1.py",
    "cascadeur_command_wrapper_bundle": RESULTS / "cascadeur-command-wrapper-bundle-v1" / "manifest.json",
    "cascadeur_command_wrapper_deployer": TRAIN / "deploy_cascadeur_command_wrapper_v1.py",
    "cascadeur_command_wrapper_deployment_receipt": RESULTS / "cascadeur-command-wrapper-deployment-v1.json",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return value


def main() -> dict[str, Any]:
    missing = [
        key for key, path in REQUIRED.items()
        if not path.is_file()
    ]
    if missing:
        raise RuntimeError("Missing handoff surface files: " + ", ".join(missing))

    files = {
        key: {
            "path": path.relative_to(ROOT).as_posix(),
            "sha256": sha256(path),
            "bytes": path.stat().st_size,
        }
        for key, path in REQUIRED.items()
    }
    report = {
        "schema": "b4ml-human-gates-handoff-validation-v1",
        "status": "PASS",
        "scope": (
            "Static handoff-surface readiness only; this receipt does not contain "
            "human review, temporal training authorization, Cascadeur conversion, "
            "matched animation, parity, or full-goal evidence."
        ),
        "required_files": files,
        "next_required_external_artifacts": [
            "completed independent humanoid review and timed correction exports",
            "manifest-bound human contact/intent and identity/authorization receipts",
            "Cascadeur conversion, exact settings, matched animation, and independent comparison sessions",
        ],
        "human_input_performed": False,
        "training_authorized": False,
        "full_goal_complete": False,
        "checker_sha256": sha256(HERE),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    temporary = OUT.with_suffix(".tmp")
    temporary.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    os.replace(temporary, OUT)
    print(json.dumps(report, indent=2, allow_nan=False))
    return report


if __name__ == "__main__":
    main()
