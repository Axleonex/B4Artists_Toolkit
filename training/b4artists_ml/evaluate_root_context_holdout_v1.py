"""Evaluate the selected root-context candidate on the locked holdout."""

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
from root_context_model import evaluate_model
from sequence_model import acceptance, evaluate_windows
from train_temporal_motion import restore

ROOT = Path(__file__).resolve().parent
PROTOCOL_PATH = ROOT / "root_context_protocol_v1.json"
HOLDOUT_PROTOCOL_PATH = ROOT / "holdout_protocol_v1.json"
HOLDOUT_MANIFEST_PATH = ROOT / "data_manifest.json"
TRAINING_MANIFEST_PATH = ROOT / "results" / "training_manifest_v4.json"
MODEL_DIR = ROOT / "results" / "root_context_motion_v1"
MODEL_PATH = MODEL_DIR / "selected.npz"
SELECTION_PATH = MODEL_DIR / "selection.json"
OUT_PATH = ROOT / "results" / "root-context-holdout-v1.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> dict:
    began = time.perf_counter()
    protocol = json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))
    holdout_protocol = json.loads(HOLDOUT_PROTOCOL_PATH.read_text(encoding="utf-8"))
    selection = json.loads(SELECTION_PATH.read_text(encoding="utf-8"))
    if selection["selection_split"] != "validation" or selection["observed_development_loaded"] is not False:
        raise ValueError("Root-context candidate was not frozen on validation only")
    if selection["holdout_protocol_sha256"] != digest(HOLDOUT_PROTOCOL_PATH):
        raise ValueError("Root-context selection is bound to a different holdout protocol")
    if selection["selected_sha256"] != digest(MODEL_PATH):
        raise ValueError("Selected root-context model hash mismatch")
    source_manifest = json.loads(HOLDOUT_MANIFEST_PATH.read_text(encoding="utf-8"))
    training_manifest = json.loads(TRAINING_MANIFEST_PATH.read_text(encoding="utf-8"))
    from evaluate_temporal_holdout_v1 import holdout_manifest
    derived, rows = holdout_manifest(source_manifest, holdout_protocol, training_manifest)
    windows, skeleton = load_environment_windows(ROOT, derived, "holdout", holdout_protocol)
    ridge = restore(ROOT / "results" / "sequence_motion_v2" / "ridge.npz")
    control = load_model(ROOT / "results" / "kernel_motion_v3" / "selected.npz")
    motion_relative = load_model(ROOT / "results" / "kernel_motion_v3" / "motion_relative_kernel.npz")
    v4_gravity = load_model(ROOT / "results" / "gravity_motion_v4" / "selected.npz")
    root_model = load_model(MODEL_PATH)
    reports = {
        name: evaluate_windows(windows, skeleton, name, ridge if name == "ridge" else None)
        for name in ("linear", "hermite", "fk_linear", "fk_hermite", "ridge")
    }
    reports["v3_control"] = evaluate_kernel(control, windows, skeleton)
    reports["v3_motion_relative"] = evaluate_kernel(motion_relative, windows, skeleton)
    reports["v4_gravity"] = evaluate_gravity(v4_gravity, windows, skeleton)
    reports["root_context"] = evaluate_model(root_model, windows, skeleton)
    gate_protocol = dict(protocol)
    gate_protocol["baselines"] = ["linear", "hermite", "fk_linear", "fk_hermite", "ridge", "v3_control", "v4_gravity"]
    gate_reports = dict(reports, mlp=reports["root_context"])
    gates = acceptance(gate_reports, gate_protocol)
    result = {
        "schema": "b4ml-root-context-holdout-v1",
        "status": "COMPLETE_GATES_PASSED" if gates["passed"] else "COMPLETE_GATES_FAILED",
        "scope": "Locked subject-disjoint holdout evaluation of a validation-selected root-context research candidate; no runtime promotion or parity claim.",
        "protocol_sha256": digest(PROTOCOL_PATH),
        "holdout_protocol_sha256": digest(HOLDOUT_PROTOCOL_PATH),
        "selection": {
            "path": SELECTION_PATH.relative_to(ROOT).as_posix(),
            "sha256": digest(SELECTION_PATH),
            "model": MODEL_PATH.relative_to(ROOT).as_posix(),
            "model_sha256": digest(MODEL_PATH),
            "selected": selection["selected"],
            "selection_split": selection["selection_split"],
            "observed_development_loaded": selection["observed_development_loaded"],
        },
        "holdout": {
            "clips": [row["clip"] for row in rows],
            "subjects": holdout_protocol["holdout_subjects"],
            "windows": len(windows),
            "queries": reports["root_context"]["aggregate"]["queries"],
            "subject_disjoint_from_train_validation": True,
        },
        "reports": reports,
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
    OUT_PATH.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "event": "complete",
        "status": result["status"],
        "selected": selection["selected"],
        "position": reports["root_context"]["aggregate"]["position"],
        "control_position": reports["v3_control"]["aggregate"]["position"],
        "gates_passed": gates["passed"],
        "seconds": result["runtime"]["seconds"],
    }, indent=2), flush=True)
    return result


if __name__ == "__main__":
    main()
