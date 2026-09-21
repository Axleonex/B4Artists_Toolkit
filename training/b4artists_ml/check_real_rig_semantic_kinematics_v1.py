"""Diagnose fixed-offset consistency of the real-rig 17-joint observation layer."""
from pathlib import Path
import hashlib
import json
import os
import sys


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve()
sys.path[:0] = [str(ROOT), str(ROOT / "tests"), str(HERE.parent)]

import numpy as np
import bpy

from context_data import NAMES, PARENTS
from rig_observations import sample
from test_b4artists_ml_imported_humanoids import PROFILES, authored
from test_b4artists_ml_posing import boneforge_rig, rigify_rig


RESULT = ROOT / "training/b4artists_ml/results/real-rig-semantic-kinematics-v1.json"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def analyze(name, obj):
    observation = sample(obj, 2, 12, context=True)
    points = np.asarray(observation.positions, dtype=np.float64)
    rotations = np.asarray(observation.rotations, dtype=np.float64)
    edge_rows = []
    all_residuals = []
    for child, parent in enumerate(PARENTS):
        if parent < 0:
            continue
        initial = points[0, child] - points[0, parent]
        local_offset = rotations[0, parent].T @ initial
        reconstructed = points[:, parent] + np.einsum(
            "fij,j->fi", rotations[:, parent], local_offset
        )
        residual = np.linalg.norm(reconstructed - points[:, child], axis=1)
        lengths = np.linalg.norm(points[:, child] - points[:, parent], axis=1)
        relative_length_change = np.max(np.abs(lengths - lengths[0])) / max(lengths[0], 1e-12)
        edge_rows.append({
            "parent": NAMES[parent],
            "child": NAMES[child],
            "initial_length_body_scales": float(lengths[0]),
            "maximum_rigid_parent_residual_body_scales": float(np.max(residual)),
            "maximum_relative_length_change": float(relative_length_change),
        })
        all_residuals.extend(residual.tolist())
    return {
        "profile": name,
        "schema": observation.schema,
        "frames": [1, 2, 12, 13],
        "maximum_rigid_parent_residual_body_scales": float(max(all_residuals)),
        "rms_rigid_parent_residual_body_scales": float(np.sqrt(np.mean(np.square(all_residuals)))),
        "maximum_relative_edge_length_change": float(max(row["maximum_relative_length_change"] for row in edge_rows)),
        "edges": edge_rows,
    }


def main():
    if RESULT.exists():
        raise RuntimeError("Evidence exists: " + str(RESULT))
    import b4artists_ml
    b4artists_ml.register()
    rigs = {
        "boneforge": boneforge_rig(),
        "rigify_basic_generated": rigify_rig(),
        "rigify_default_generated": rigify_rig(full=True),
        "rigify_basic_metarig": rigify_rig(generate=False),
        "rigify_default_metarig": rigify_rig(full=True, generate=False),
    }
    rigs.update({name: authored(name, index)[0] for index, name in enumerate(PROFILES)})
    rows = [analyze(name, obj) for name, obj in rigs.items()]
    report = {
        "complete": True,
        "schema": "real-rig-semantic-kinematics-v1",
        "purpose": "Determine whether the 17-joint world observation is a valid fixed-offset hierarchy input before designing a production 23-joint task packet.",
        "profiles": rows,
        "maximum_rigid_parent_residual_body_scales": max(row["maximum_rigid_parent_residual_body_scales"] for row in rows),
        "maximum_relative_edge_length_change": max(row["maximum_relative_edge_length_change"] for row in rows),
        "sources": {
            "script": sha(HERE),
            "rig_observations": sha(HERE.parent / "rig_observations.py"),
            "runtime_rigs": sha(ROOT / "b4artists_ml/rigs.py"),
            "runtime_body_solver": sha(ROOT / "b4artists_ml/body_solver.py"),
            "fixture_posing": sha(ROOT / "tests/test_b4artists_ml_posing.py"),
            "fixture_imported": sha(ROOT / "tests/test_b4artists_ml_imported_humanoids.py"),
        },
        "interpretation": "A nontrivial residual rejects direct use of the collapsed 17-joint graph as a fixed-offset local hierarchy; profile-specific intermediate-joint adapters are then required.",
        "model_trained": False,
        "runtime_promoted": False,
        "confirmation_read": False,
        "full_goal_complete": False,
    }
    RESULT.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "complete": True,
        "profiles": len(rows),
        "maximum_rigid_parent_residual_body_scales": report["maximum_rigid_parent_residual_body_scales"],
        "maximum_relative_edge_length_change": report["maximum_relative_edge_length_change"],
        "runtime_promoted": False,
        "confirmation_read": False,
    }, indent=2), flush=True)


if __name__ == "__main__":
    main()
