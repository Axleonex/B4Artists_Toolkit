"""Independently validate the modal current development package journey."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "docs/b4artists_ml/capsule-ui-v0.37.29-package-modal.json"
ARCHIVE = ROOT / "releases/b4artists_ml_v0.37.29-dev.zip"
OUTPUT = ROOT / "training/b4artists_ml/results/current-package-foreground-modal-validation-v1.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    report = json.loads(REPORT.read_text(encoding="utf-8-sig"))
    metrics = report.get("metrics", {})
    events = set(report.get("events", []))
    required_events = {
        "Escape cancelled the capsule preview without replacing the input action.",
        "Native Undo restored the capsule input action.",
        "Native Redo restored the generated capsule candidate.",
        "Restore Input returned to the pre-capsule candidate.",
        "Keep archived the editable capsule result as a separate action.",
        "Save/reload preserved the kept action and capsule endpoint bindings.",
        "Restore Source returned the rig to its original action after reload.",
    }
    if (
        report.get("schema") != 1
        or report.get("passed") is not True
        or report.get("package_sha256") != sha256(ARCHIVE)
        or report.get("feature") != "moving/deforming capsule collision"
        or metrics.get("schema") != 24
        or metrics.get("backend") != "implicit_selected_control_secondary_moving_capsule_v1"
        or metrics.get("collision") is not True
        or metrics.get("collision_shape") != "CAPSULE"
        or metrics.get("collision_capsule_moving") is not True
        or metrics.get("collision_capsule_scaling") is not True
        or metrics.get("learned") is not False
        or metrics.get("editable_linear_keys") is not True
        or metrics.get("relative_velocity_response") is not True
        or metrics.get("relative_radius_velocity_response") is not True
        or not required_events.issubset(events)
        or report.get("native_undo_redo", {}).get("status") != "passed"
        or report.get("action_rig_recovery", {}).get("source_action_recovered") is not True
        or report.get("action_rig_recovery", {}).get("rig_structure_recovered") is not True
        or report.get("action_rig_recovery", {}).get("rig_modes_recovered") is not True
        or report.get("action_rig_recovery", {}).get("pose_evaluation", {}).get("changed_bones") != 294
        or report.get("step_count") != 50
        or float(report.get("step_max_ms", 0.0)) <= 0.0
        or float(report.get("elapsed_seconds", 0.0)) <= 0.0
    ):
        raise ValueError("Modal foreground package contract failed")
    for key in ("visible_controls_screenshot", "completion_screenshot", "save_path"):
        if not (ROOT / report[key]).is_file():
            raise FileNotFoundError(report[key])
    validation = {
        "schema": "b4ml-current-package-foreground-modal-validation-v1",
        "status": "PASS",
        "report": REPORT.relative_to(ROOT).as_posix(),
        "report_sha256": sha256(REPORT),
        "archive": ARCHIVE.relative_to(ROOT).as_posix(),
        "archive_sha256": sha256(ARCHIVE),
        "feature": report["feature"],
        "steps": report["step_count"],
        "max_callback_ms": report["step_max_ms"],
        "elapsed_seconds": report["elapsed_seconds"],
        "native_undo_redo": report["native_undo_redo"],
        "learned_temporal_quality": False,
        "cascadeur_comparison": False,
        "claim_boundary_closed": True,
    }
    OUTPUT.write_text(json.dumps(validation, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, indent=2))


if __name__ == "__main__":
    main()
