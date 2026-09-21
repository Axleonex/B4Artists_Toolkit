"""Encode the train-only CMU corpus once for streamed temporal sampling.

SPDX-License-Identifier: GPL-2.0-or-later
Large numeric arrays remain in the Git-ignored research cache.
"""
from pathlib import Path
import hashlib
import json
import re
import sys
import time

import numpy as np


ROOT = Path(__file__).resolve().parent
HERE = Path(__file__).resolve()
PLAN_PATH = ROOT / "cmu_sequence_store_plan_v2.json"
SOURCE_MANIFEST = ROOT / "results/cmu-corpus-inventory-v1/train-download-manifest.json"
OUT = ROOT / "results/cmu-sequence-store-v2"
STORE = (ROOT / "cache-expanded-v1/sequence-store-v2").resolve()
TARGET_FPS = 30.0


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, data):
    path.write_text(json.dumps(data, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def header(path):
    with path.open("rb") as handle:
        prefix = handle.read(262144).decode("ascii", errors="strict")
    match = re.search(r"MOTION\s*Frames:\s*(\d+)\s*Frame Time:\s*([0-9.eE+-]+)", prefix)
    if not match:
        raise ValueError("Motion header exceeds bounded scan or is invalid: " + path.name)
    frames = int(match.group(1))
    frame_time = float(match.group(2))
    if frames < 2 or not 0 < frame_time < 1:
        raise ValueError("Invalid motion header: " + path.name)
    step = max(1, int(round(1 / (TARGET_FPS * frame_time))))
    samples = len(range(1, frames, step))
    return frames, frame_time, step, samples


def motion_view(motion, values, frame_time):
    from bvh_data import Motion

    return Motion(
        motion.names,
        motion.parents,
        motion.offsets,
        motion.channels,
        values,
        frame_time,
    )


def main():
    sys.path.insert(0, str(ROOT))
    from bvh_data import parse_bvh
    from context_data import NAMES
    from temporal_data import quaternion

    plan = json.loads(PLAN_PATH.read_text())
    manifest = json.loads(SOURCE_MANIFEST.read_text())
    assert sha256(SOURCE_MANIFEST) == plan["source_manifest_sha256"]
    assert sha256(HERE) == plan["script_sha256"]
    assert all(sha256(ROOT / name) == digest for name, digest in plan["sources"].items())
    assert manifest["complete"] and manifest["file_count"] == plan["clips"]
    assert not manifest["development_motion_downloaded"] and not manifest["confirmation_motion_downloaded"]
    OUT.mkdir(exist_ok=False)
    STORE.mkdir(parents=True, exist_ok=False)
    started = time.perf_counter()
    layouts = []
    offset = 0
    for row in manifest["files"]:
        path = ROOT / row["path"]
        frames, frame_time, step, samples = header(path)
        layouts.append(
            {
                "clip": row["clip"],
                "subject": row["subject"],
                "description": row["description"],
                "style_tags": row["style_tags"],
                "source_path": row["path"],
                "source_sha256": row["sha256"],
                "source_frames": frames,
                "source_frame_time": frame_time,
                "sample_step": step,
                "frames": samples,
                "offset": offset,
                "dt": frame_time * step,
            }
        )
        offset += samples
    total_frames = offset
    if total_frames <= 0 or total_frames > plan["storage"]["maximum_frames"]:
        raise ValueError("Unexpected encoded frame count")
    layout = {
        "schema": 1,
        "plan_sha256": sha256(PLAN_PATH),
        "clips": len(layouts),
        "frames": total_frames,
        "joint_names": NAMES,
        "position_shape": [total_frames, 17, 3],
        "quaternion_shape": [total_frames, 17, 4],
        "entries": layouts,
    }
    write(OUT / "layout.json", layout)
    positions = np.lib.format.open_memmap(
        STORE / "positions.npy", mode="w+", dtype=np.float32, shape=(total_frames, 17, 3)
    )
    rotations = np.lib.format.open_memmap(
        STORE / "quaternions.npy", mode="w+", dtype=np.float32, shape=(total_frames, 17, 4)
    )
    rest_positions = np.lib.format.open_memmap(
        STORE / "rest_positions.npy", mode="w+", dtype=np.float32, shape=(len(layouts), 17, 3)
    )
    rest_rotations = np.lib.format.open_memmap(
        STORE / "rest_quaternions.npy", mode="w+", dtype=np.float32, shape=(len(layouts), 17, 4)
    )
    source_bytes = 0
    for index, (source, item) in enumerate(zip(manifest["files"], layouts)):
        path = ROOT / source["path"]
        raw = path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != source["sha256"]:
            raise ValueError("Source checksum changed: " + source["clip"])
        source_bytes += len(raw)
        motion = parse_bvh(raw.decode("ascii"))
        if len(motion.values) != item["source_frames"] or motion.frame_time != item["source_frame_time"]:
            raise ValueError("Header/full-parse mismatch: " + source["clip"])
        try:
            semantic_ids = [motion.names.index(name) for name in NAMES]
        except ValueError as exc:
            raise ValueError("Missing semantic joint: " + source["clip"]) from exc
        rest_points, rest_matrices = motion_view(
            motion, motion.values[:1], motion.frame_time
        ).transforms()
        sampled_values = motion.values[1 :: item["sample_step"]]
        points, matrices = motion_view(
            motion, sampled_values, item["dt"]
        ).transforms()
        points = points[:, semantic_ids]
        matrices = matrices[:, semantic_ids]
        rest_points = rest_points[0, semantic_ids]
        rest_matrices = rest_matrices[0, semantic_ids]
        quaternions = quaternion(matrices)
        rest_quaternion = quaternion(rest_matrices)
        if (
            len(points) != item["frames"]
            or not np.isfinite(points).all()
            or not np.isfinite(quaternions).all()
            or not np.isfinite(rest_points).all()
            or not np.isfinite(rest_quaternion).all()
        ):
            raise ValueError("Invalid transformed motion: " + source["clip"])
        start = item["offset"]
        end = start + item["frames"]
        positions[start:end] = points.astype(np.float32)
        rotations[start:end] = quaternions.astype(np.float32)
        rest_positions[index] = rest_points.astype(np.float32)
        rest_rotations[index] = rest_quaternion.astype(np.float32)
        if (index + 1) % 25 == 0:
            for array in (positions, rotations, rest_positions, rest_rotations):
                array.flush()
            write(
                OUT / "progress.json",
                {
                    "complete": False,
                    "clips": index + 1,
                    "total_clips": len(layouts),
                    "frames": end,
                    "total_frames": total_frames,
                    "source_bytes": source_bytes,
                    "seconds": time.perf_counter() - started,
                    "validation_read": False,
                    "confirmation_read": False,
                },
            )
    for array in (positions, rotations, rest_positions, rest_rotations):
        array.flush()
    del positions, rotations, rest_positions, rest_rotations
    files = {}
    store_bytes = 0
    for name in ("positions.npy", "quaternions.npy", "rest_positions.npy", "rest_quaternions.npy"):
        path = STORE / name
        files[name] = {"bytes": path.stat().st_size, "sha256": sha256(path)}
        store_bytes += path.stat().st_size
    source_seconds = sum((item["source_frames"] - 1) * item["source_frame_time"] for item in layouts)
    report = {
        "complete": True,
        "clips": len(layouts),
        "subjects": len({item["subject"] for item in layouts}),
        "frames": total_frames,
        "source_seconds": source_seconds,
        "source_hours": source_seconds / 3600,
        "source_bytes": source_bytes,
        "store_bytes": store_bytes,
        "files": files,
        "layout_sha256": sha256(OUT / "layout.json"),
        "plan_sha256": sha256(PLAN_PATH),
        "source_manifest_sha256": sha256(SOURCE_MANIFEST),
        "script_sha256": sha256(HERE),
        "single_copy_sequence_storage": True,
        "memory_mappable": True,
        "window_materialization": "training_batch_only",
        "validation_read": False,
        "confirmation_read": False,
        "raw_motion_bundled_with_addon": False,
        "store_bundled_with_addon": False,
        "seconds": time.perf_counter() - started,
        "full_goal_complete": False,
    }
    if store_bytes > plan["storage"]["maximum_store_bytes"]:
        raise ValueError("Encoded store exceeds prospective byte limit")
    write(OUT / "report.json", report)
    write(
        OUT / "progress.json",
        {
            "complete": True,
            "clips": len(layouts),
            "frames": total_frames,
            "source_bytes": source_bytes,
            "store_bytes": store_bytes,
            "seconds": report["seconds"],
            "report_sha256": sha256(OUT / "report.json"),
            "validation_read": False,
            "confirmation_read": False,
        },
    )
    print(json.dumps({key: report[key] for key in ("complete", "clips", "subjects", "frames", "source_hours", "source_bytes", "store_bytes", "seconds")}, indent=2))


if __name__ == "__main__":
    main()
