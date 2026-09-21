"""Derive a training-throughput matrix view from the checked quaternion store.

SPDX-License-Identifier: GPL-2.0-or-later
"""
from pathlib import Path
import hashlib
import json
import sys
import time

import numpy as np


ROOT = Path(__file__).resolve().parent
HERE = Path(__file__).resolve()
PLAN_PATH = ROOT / "rotation_matrix_store_plan_v1.json"
SOURCE_REPORT = ROOT / "results/cmu-sequence-store-v2/report.json"
SOURCE_LAYOUT = ROOT / "results/cmu-sequence-store-v2/layout.json"
SOURCE = ROOT / "cache-expanded-v1/sequence-store-v2"
STORE = ROOT / "cache-expanded-v1/rotation-matrix-store-v1"
OUT = ROOT / "results/rotation-matrix-store-v1"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, data):
    path.write_text(json.dumps(data, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def main():
    sys.path.insert(0, str(ROOT))
    from temporal_data import quat_matrix

    plan = json.loads(PLAN_PATH.read_text())
    source_report = json.loads(SOURCE_REPORT.read_text())
    layout = json.loads(SOURCE_LAYOUT.read_text())
    assert sha256(HERE) == plan["script_sha256"]
    assert sha256(SOURCE_REPORT) == plan["source_report_sha256"]
    assert sha256(SOURCE_LAYOUT) == source_report["layout_sha256"]
    assert source_report["complete"] and not source_report["validation_read"] and not source_report["confirmation_read"]
    OUT.mkdir(exist_ok=False)
    STORE.mkdir(parents=True, exist_ok=False)
    started = time.perf_counter()
    source = np.load(SOURCE / "quaternions.npy", mmap_mode="r", allow_pickle=False)
    rest_source = np.load(SOURCE / "rest_quaternions.npy", mmap_mode="r", allow_pickle=False)
    if source.shape != tuple(layout["quaternion_shape"]) or source.dtype != np.float32:
        raise ValueError("Unexpected source quaternion store")
    rotations = np.lib.format.open_memmap(
        STORE / "rotation_matrices.npy",
        mode="w+",
        dtype=np.float32,
        shape=(layout["frames"], 17, 3, 3),
    )
    chunk = plan["chunk_frames"]
    for start in range(0, len(source), chunk):
        end = min(start + chunk, len(source))
        value = quat_matrix(np.asarray(source[start:end])).astype(np.float32)
        if not np.isfinite(value).all():
            raise ValueError("Nonfinite derived rotation")
        rotations[start:end] = value
        if end % (chunk * 16) == 0:
            rotations.flush()
            write(
                OUT / "progress.json",
                {
                    "complete": False,
                    "frames": end,
                    "total_frames": len(source),
                    "seconds": time.perf_counter() - started,
                    "validation_read": False,
                    "confirmation_read": False,
                },
            )
    rest_rotations = np.lib.format.open_memmap(
        STORE / "rest_rotation_matrices.npy",
        mode="w+",
        dtype=np.float32,
        shape=(layout["clips"], 17, 3, 3),
    )
    rest_rotations[:] = quat_matrix(np.asarray(rest_source)).astype(np.float32)
    rotations.flush()
    rest_rotations.flush()
    del rotations, rest_rotations
    files = {}
    total = 0
    for name in ("rotation_matrices.npy", "rest_rotation_matrices.npy"):
        path = STORE / name
        files[name] = {"bytes": path.stat().st_size, "sha256": sha256(path)}
        total += path.stat().st_size
    if total > plan["maximum_bytes"]:
        raise ValueError("Matrix store exceeds prospective cap")
    check = np.load(STORE / "rotation_matrices.npy", mmap_mode="r", allow_pickle=False)
    indices = np.linspace(0, len(check) - 1, 4096, dtype=np.int64)
    sample = np.asarray(check[indices], dtype=np.float64)
    orthogonality = float(np.max(np.abs(np.swapaxes(sample, -1, -2) @ sample - np.eye(3))))
    determinant_error = float(np.max(np.abs(np.linalg.det(sample) - 1)))
    if orthogonality > 2e-6 or determinant_error > 2e-6:
        raise ValueError("Derived rotation quality mismatch")
    report = {
        "complete": True,
        "frames": layout["frames"],
        "clips": layout["clips"],
        "bytes": total,
        "files": files,
        "sampled_rotation_checks": len(indices),
        "max_orthogonality_error": orthogonality,
        "max_determinant_error": determinant_error,
        "source_report_sha256": sha256(SOURCE_REPORT),
        "source_layout_sha256": sha256(SOURCE_LAYOUT),
        "plan_sha256": sha256(PLAN_PATH),
        "script_sha256": sha256(HERE),
        "validation_read": False,
        "confirmation_read": False,
        "runtime_bundled": False,
        "seconds": time.perf_counter() - started,
        "full_goal_complete": False,
    }
    write(OUT / "report.json", report)
    write(
        OUT / "progress.json",
        {
            "complete": True,
            "frames": layout["frames"],
            "bytes": total,
            "seconds": report["seconds"],
            "report_sha256": sha256(OUT / "report.json"),
            "validation_read": False,
            "confirmation_read": False,
        },
    )
    print(json.dumps({key: report[key] for key in ("complete", "frames", "clips", "bytes", "max_orthogonality_error", "max_determinant_error", "seconds")}, indent=2))


if __name__ == "__main__":
    main()
