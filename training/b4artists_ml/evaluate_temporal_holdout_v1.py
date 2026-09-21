"""Evaluate the frozen temporal learner on an untouched subject-disjoint split.

This evaluator consumes only the existing cached BVH files and frozen model
artifacts. It never trains, selects, rewrites model files, or changes the
B4Artists runtime. The holdout is subject-disjoint from the training and
validation rows and excludes subject 13 because that subject appears in the
older training/confirmation material.
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import time
from pathlib import Path

os.environ.setdefault("OPENBLAS_NUM_THREADS", "4")

from environment_data import load_environment_windows
from gravity_model import evaluate_model as evaluate_gravity
from kernel_motion import evaluate_model as evaluate_kernel, load_model
from sequence_model import acceptance, evaluate_windows
from train_temporal_motion import restore
from temporal_data import validate_manifests


ROOT = Path(__file__).resolve().parent
PROTOCOL_PATH = ROOT / "holdout_protocol_v1.json"
MANIFEST_PATH = ROOT / "data_manifest.json"
TRAINING_MANIFEST_PATH = ROOT / "results" / "training_manifest_v4.json"
GRAVITY_MODEL_PATH = ROOT / "results" / "gravity_motion_v4" / "selected.npz"
GRAVITY_SELECTION_PATH = ROOT / "results" / "gravity_motion_v4" / "selection.json"
GRAVITY_REPORT_PATH = ROOT / "results" / "gravity_motion_v4" / "report.json"
CONTROL_MODEL_PATH = ROOT / "results" / "kernel_motion_v3" / "selected.npz"
MOTION_RELATIVE_MODEL_PATH = ROOT / "results" / "kernel_motion_v3" / "motion_relative_kernel.npz"
CONTROL_REPORT_PATH = ROOT / "results" / "kernel_motion_v3" / "report.json"
RIDGE_PATH = ROOT / "results" / "sequence_motion_v2" / "ridge.npz"
OUT_PATH = ROOT / "results" / "temporal-holdout-v1.json"


def digest(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            sha.update(block)
    return sha.hexdigest()


def subject(clip: str) -> str:
    return clip.split("_", 1)[0]


def holdout_manifest(
    manifest: dict, protocol: dict, training_manifest: dict | None = None
) -> tuple[dict, list[dict]]:
    rows = manifest.get("files", [])
    if not rows:
        raise ValueError("Training manifest has no files")
    validate_manifests([manifest])
    allowed = set(protocol["holdout_subjects"])
    excluded = set(protocol["excluded_test_subjects"])
    train_validation_subjects = {
        subject(row["clip"])
        for row in rows
        if row["split"] in {"train", "validation"}
    }
    if training_manifest is not None:
        train_validation_subjects.update(
            subject(row["clip"])
            for row in training_manifest.get("files", [])
            if row["split"] in {"train", "validation"}
        )
    if allowed & train_validation_subjects:
        raise ValueError("Holdout subject overlaps training or validation")
    selected = []
    for row in rows:
        if row["split"] != protocol["source_split"]:
            continue
        if subject(row["clip"]) in excluded:
            continue
        if subject(row["clip"]) in allowed:
            copy = dict(row)
            copy["source_split"] = copy["split"]
            copy["split"] = "holdout"
            selected.append(copy)
    if not selected:
        raise ValueError("No subject-disjoint holdout rows selected")
    selected_subjects = {subject(row["clip"]) for row in selected}
    if selected_subjects != allowed:
        raise ValueError("Holdout rows do not cover the declared subject set")
    derived = dict(manifest)
    derived["files"] = selected
    return derived, selected


def assert_frozen_selection(protocol: dict) -> dict:
    selection = json.loads(GRAVITY_SELECTION_PATH.read_text(encoding="utf-8"))
    if selection.get("selection_split") != protocol["selection_split_required"]:
        raise ValueError("Selected model was not selected on validation")
    if selection.get("observed_development_loaded") is not protocol["observed_development_loaded_required"]:
        raise ValueError("Selected model receipt does not prove untouched selection")
    if selection.get("selected_sha256") != digest(GRAVITY_MODEL_PATH):
        raise ValueError("Selected model hash does not match selection receipt")
    for report_path in (GRAVITY_REPORT_PATH, CONTROL_REPORT_PATH):
        report = json.loads(report_path.read_text(encoding="utf-8"))
        for split_name in ("validation", "observed_development"):
            for row in report.get(split_name, {}).values():
                for key in row.get("cohorts", {}):
                    if key.split("/", 1)[0] in {"16_01", "16_17", "35_01", "35_17"}:
                        raise ValueError("Holdout clip appears in a prior evaluation receipt")
    return selection


def main() -> dict:
    began = time.perf_counter()
    protocol = json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    training_manifest = json.loads(TRAINING_MANIFEST_PATH.read_text(encoding="utf-8"))
    derived, rows = holdout_manifest(manifest, protocol, training_manifest)
    selection = assert_frozen_selection(protocol)
    windows, skeleton = load_environment_windows(ROOT, derived, "holdout", protocol)
    control = load_model(CONTROL_MODEL_PATH)
    motion_relative = load_model(MOTION_RELATIVE_MODEL_PATH)
    learned = load_model(GRAVITY_MODEL_PATH)
    ridge = restore(RIDGE_PATH)
    baselines = {
        name: evaluate_windows(windows, skeleton, name, ridge if name == "ridge" else None)
        for name in ("linear", "hermite", "fk_linear", "fk_hermite", "ridge")
    }
    baselines["v3_control"] = evaluate_kernel(control, windows, skeleton)
    motion_relative_report = evaluate_kernel(motion_relative, windows, skeleton)
    learned_report = evaluate_gravity(learned, windows, skeleton)
    gate_reports = dict(baselines, mlp=learned_report)
    gate_protocol = dict(protocol)
    gate_protocol["baselines"] = ["linear", "hermite", "fk_linear", "fk_hermite", "ridge", "v3_control"]
    gate_protocol["gates"] = json.loads(
        (ROOT / "gravity_protocol_v4.json").read_text(encoding="utf-8")
    )["gates"]
    gates = acceptance(gate_reports, gate_protocol)
    report = {
        "schema": "b4ml-temporal-holdout-v1",
        "status": "COMPLETE_GATES_PASSED" if gates["passed"] else "COMPLETE_GATES_FAILED",
        "scope": "Frozen gravity-conditioned research model evaluated on subject-disjoint cached motion; no training, selection, runtime promotion, animator or Cascadeur claim.",
        "protocol": {
            "path": PROTOCOL_PATH.relative_to(ROOT).as_posix(),
            "sha256": digest(PROTOCOL_PATH),
            "source_manifest": MANIFEST_PATH.relative_to(ROOT).as_posix(),
            "source_manifest_sha256": digest(MANIFEST_PATH),
            "training_manifest": TRAINING_MANIFEST_PATH.relative_to(ROOT).as_posix(),
            "training_manifest_sha256": digest(TRAINING_MANIFEST_PATH),
            "source_split": protocol["source_split"],
            "holdout_subjects": protocol["holdout_subjects"],
            "excluded_test_subjects": protocol["excluded_test_subjects"],
            "selection_split": selection["selection_split"],
            "observed_development_loaded": selection["observed_development_loaded"],
        },
        "holdout": {
            "rows": [
                {
                    "clip": row["clip"],
                    "subject": subject(row["clip"]),
                    "source_split": row["source_split"],
                    "bytes": row["bytes"],
                    "sha256": row["sha256"],
                }
                for row in rows
            ],
            "clips": [row["clip"] for row in rows],
            "subjects": sorted({subject(row["clip"]) for row in rows}),
            "windows": len(windows),
            "queries": int(learned_report["aggregate"]["queries"]),
            "subject_disjoint_from_train_validation": True,
            "prior_selection_receipt_excludes_holdout": True,
        },
        "models": {
            "selected": {
                "path": GRAVITY_MODEL_PATH.relative_to(ROOT).as_posix(),
                "sha256": digest(GRAVITY_MODEL_PATH),
                "selection_receipt": GRAVITY_SELECTION_PATH.relative_to(ROOT).as_posix(),
                "selection_receipt_sha256": digest(GRAVITY_SELECTION_PATH),
                "kind": "gravity_direction_conditioned_kernel",
            },
            "control": {
                "path": CONTROL_MODEL_PATH.relative_to(ROOT).as_posix(),
                "sha256": digest(CONTROL_MODEL_PATH),
                "report": CONTROL_REPORT_PATH.relative_to(ROOT).as_posix(),
                "report_sha256": digest(CONTROL_REPORT_PATH),
            },
            "secondary_candidate": {
                "path": MOTION_RELATIVE_MODEL_PATH.relative_to(ROOT).as_posix(),
                "sha256": digest(MOTION_RELATIVE_MODEL_PATH),
                "kind": "v3_motion_relative_kernel",
            },
        },
        "reports": dict(baselines, motion_relative=motion_relative_report, learned=learned_report),
        "gates": gates,
        "runtime": {
            "seconds": time.perf_counter() - began,
            "python": platform.python_version(),
            "numpy": __import__("numpy").__version__,
            "platform": platform.platform(),
            "blas_threads": os.environ["OPENBLAS_NUM_THREADS"],
        },
        "claim_boundary": {
            "learned_model_accepted": False,
            "runtime_promoted": False,
            "actual_rig_workflow_verified": False,
            "independent_animator_usability_verified": False,
            "cascadeur_import_verified": False,
            "cascadeur_parity_verified": False,
            "full_goal_complete": False,
        },
    }
    OUT_PATH.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "event": "complete",
        "status": report["status"],
        "holdout_clips": report["holdout"]["clips"],
        "windows": report["holdout"]["windows"],
        "gates_passed": gates["passed"],
        "position": learned_report["aggregate"]["position"],
        "control_position": baselines["v3_control"]["aggregate"]["position"],
        "seconds": report["runtime"]["seconds"],
    }, indent=2), flush=True)
    return report


if __name__ == "__main__":
    main()
