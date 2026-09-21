"""Train and select a root-context research candidate on validation only."""

from __future__ import annotations

import hashlib
import json
import os
import platform
import time
from pathlib import Path

import numpy as np

os.environ.setdefault("OPENBLAS_NUM_THREADS", "4")

from environment_data import load_environment_windows
from gravity_model import evaluate_model as evaluate_gravity
from kernel_motion import load_model, save_model
from root_context_model import evaluate_model, fit
from sequence_model import acceptance, evaluate_windows
from temporal_data import validate_manifests
from temporal_model import selection
from train_temporal_motion import restore


ROOT = Path(__file__).resolve().parent
PROTOCOL_PATH = ROOT / "root_context_protocol_v1.json"
HOLDOUT_PROTOCOL_PATH = ROOT / "holdout_protocol_v1.json"
OUTPUT = ROOT / "results" / "root_context_motion_v1"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> dict:
    began = time.perf_counter()
    if OUTPUT.exists():
        raise RuntimeError(f"Refusing to overwrite existing research output: {OUTPUT}")
    protocol = json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))
    manifests = []
    for row in protocol["manifests"]:
        path = ROOT / row["path"]
        if digest(path) != row["sha256"]:
            raise ValueError("Manifest checksum mismatch")
        manifests.append(json.loads(path.read_text(encoding="utf-8")))
    validate_manifests(manifests)
    source_names = (
        "environment_data.py",
        "environment_context.py",
        "root_context_model.py",
        "root_context_protocol_v1.json",
        "train_root_context_motion_v1.py",
        "kernel_motion.py",
        "motion_coverage.py",
        "sequence_data.py",
        "sequence_kinematics.py",
        "sequence_model.py",
        "temporal_data.py",
        "temporal_model.py",
        "bvh_data.py",
        "context_data.py",
    )
    source_hashes = {name: digest(ROOT / name) for name in source_names}
    holdout_hash = digest(HOLDOUT_PROTOCOL_PATH)
    train, skeleton = load_environment_windows(ROOT, manifests[0], "train", protocol)
    validation, validation_skeleton = load_environment_windows(ROOT, manifests[0], "validation", protocol)
    if skeleton != validation_skeleton:
        raise ValueError("Training and validation topology mismatch")
    OUTPUT.mkdir(parents=False)
    (OUTPUT / "protocol.json").write_text(json.dumps(protocol, indent=2) + "\n", encoding="utf-8")
    control_path = ROOT / "results" / "kernel_motion_v3" / "selected.npz"
    control = load_model(control_path)
    ridge = restore(ROOT / "results" / "sequence_motion_v2" / "ridge.npz")
    baseline = {
        name: evaluate_windows(validation, skeleton, name, ridge if name == "ridge" else None)
        for name in ("linear", "hermite", "fk_linear", "fk_hermite", "ridge")
    }
    baseline["v3_control"] = __import__("kernel_motion").evaluate_model(control, validation, skeleton)
    v4_model = load_model(ROOT / "results" / "gravity_motion_v4" / "selected.npz")
    baseline["v4_gravity"] = evaluate_gravity(v4_model, validation, skeleton)
    best_score = float("inf")
    best_id = None
    best_model = None
    candidates = []
    for importance in protocol["gravity_weights"]:
        model = fit(train, importance, protocol["base_width"], protocol["regularization"])
        report = evaluate_model(model, validation, skeleton)
        identifier = f"motion_relative_gravity_{importance}"
        candidate_path = OUTPUT / f"candidate_{importance}.npz"
        save_model(candidate_path, model)
        score = selection(report)
        candidates.append({
            "id": identifier,
            "importance": importance,
            "score": score,
            "model_sha256": digest(candidate_path),
            "validation": report,
        })
        if score < best_score:
            best_score = score
            best_id = identifier
            best_model = model
    selected_path = OUTPUT / "selected.npz"
    save_model(selected_path, best_model)
    selected_report = evaluate_model(best_model, validation, skeleton)
    reports = dict(baseline, mlp=selected_report)
    gate_protocol = dict(protocol)
    gate_protocol["baselines"] = ["linear", "hermite", "fk_linear", "fk_hermite", "ridge", "v3_control", "v4_gravity"]
    gates = acceptance(reports, gate_protocol)
    selection_receipt = {
        "selected": best_id,
        "selected_sha256": digest(selected_path),
        "selection_split": "validation",
        "observed_development_loaded": False,
        "holdout_protocol_sha256": holdout_hash,
        "source_sha256": source_hashes,
        "skeleton": {"names": skeleton[0], "parents": skeleton[1], "semantic": skeleton[2]},
    }
    (OUTPUT / "selection.json").write_text(json.dumps(selection_receipt, indent=2) + "\n", encoding="utf-8")
    result = {
        "schema": "b4ml-root-context-motion-v1",
        "status": "RESEARCH_ONLY_GATES_PASSED" if gates["passed"] else "RESEARCH_ONLY_GATES_FAILED",
        "goal_status": "active_incomplete",
        "protocol": protocol,
        "protocol_sha256": digest(PROTOCOL_PATH),
        "holdout_protocol_sha256": holdout_hash,
        "selection": selection_receipt,
        "candidates": candidates,
        "validation": reports,
        "gates": gates,
        "runtime": {
            "seconds": time.perf_counter() - began,
            "python": platform.python_version(),
            "numpy": np.__version__,
            "platform": platform.platform(),
            "blas_threads": os.environ["OPENBLAS_NUM_THREADS"],
        },
        "limitations": [
            "No holdout labels were used for selection",
            "No actual BoneForge/Rigify control-rig workflow",
            "No contact/style/partial-body conditioning",
            "No accepted learned runtime or bundled weights",
            "No independent animator or Cascadeur comparison",
        ],
    }
    (OUTPUT / "report.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "event": "complete",
        "selected": best_id,
        "validation_position": selected_report["aggregate"]["position"],
        "validation_rotation": selected_report["aggregate"]["rotation"],
        "gates_passed": gates["passed"],
        "seconds": result["runtime"]["seconds"],
    }, indent=2), flush=True)
    return result


if __name__ == "__main__":
    main()
