"""Analyze an exposed recorded jump without changing corpus or model state."""
from pathlib import Path
import hashlib
import json
import sys
import time

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve()
TRAINING = HERE.parent
CACHE = TRAINING / "cache"
RESULTS = TRAINING / "results" / "recorded-jump-reference-v1"
CLIP = "141_04"
SITE_NAMES = ("LeftFoot", "RightFoot", "LeftToeBase", "RightToeBase")
SEMANTIC_NAMES = (
    "Hips", "Spine", "Spine1", "Neck1", "Head",
    "LeftArm", "LeftForeArm", "LeftHand",
    "RightArm", "RightForeArm", "RightHand",
    "LeftUpLeg", "LeftLeg", "LeftFoot",
    "RightUpLeg", "RightLeg", "RightFoot",
)
SEGMENTS = (
    (0, 1, 12.0), (1, 2, 12.0), (2, 3, 18.0), (3, 4, 2.0),
    (4, None, 8.0), (5, 6, 4.0), (6, 7, 2.0), (7, None, 1.0),
    (8, 9, 4.0), (9, 10, 2.0), (10, None, 1.0),
    (11, 12, 10.0), (12, 13, 5.0), (13, None, 2.0),
    (14, 15, 10.0), (15, 16, 5.0), (16, None, 2.0),
)
TERMINALS = {4: "Head__end", 7: "LeftFingerBase", 10: "RightFingerBase",
             13: "LeftToeBase", 16: "RightToeBase"}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def contiguous(mask):
    spans = []
    start = None
    for index, value in enumerate(mask):
        if value and start is None:
            start = index
        if start is not None and (not value or index == len(mask) - 1):
            spans.append((start, index - 1 if not value else index))
            start = None
    return spans


def rotation_angle(a, b):
    relative = np.swapaxes(a, -1, -2) @ b
    return np.arccos(np.clip((np.trace(relative, axis1=-2, axis2=-1) - 1.0) * 0.5, -1.0, 1.0))


def main():
    started = time.perf_counter()
    sys.path[:0] = [str(ROOT), str(TRAINING)]
    from bvh_data import parse_bvh
    from b4artists_ml.support_math import center_of_mass

    source = CACHE / f"{CLIP}.bvh"
    manifest = json.loads((TRAINING / "temporal_training_manifest_v19.json").read_text(encoding="utf-8-sig"))
    row = next(item for item in manifest["files"] if item["clip"] == CLIP)
    assert row["split"] == "validation" and row["status"] == "complete"
    assert source.stat().st_size == row["bytes"] and sha256(source) == row["sha256"]
    assert source.stat().st_size < 8_000_000
    sealed = json.loads((TRAINING / "temporal_expansion_plan_v19.json").read_text(encoding="utf-8-sig"))["planned_splits"]["confirmation"]
    assert all(not (CACHE / f"{name}.bvh").exists() for name in sealed)

    motion = parse_bvh(source.read_text(encoding="utf-8"))
    positions, rotations = motion.transforms()
    index = {name: i for i, name in enumerate(motion.names)}
    required = set(SITE_NAMES) | set(SEMANTIC_NAMES) | set(TERMINALS.values())
    assert required <= set(index)
    leg_length = float(np.mean([
        sum(np.linalg.norm(positions[0, index[side + child]] - positions[0, index[side + parent]])
            for child, parent in (("Leg", "UpLeg"), ("Foot", "Leg")))
        for side in ("Left", "Right")
    ]))
    assert leg_length > 0 and abs(motion.frame_time - 0.0083333) < 1e-9

    sites = np.stack([positions[:, index[name], 1] for name in SITE_NAMES], axis=1)
    floors = np.percentile(sites, 2, axis=0)
    clearance = np.min((sites - floors) / leg_length, axis=1)
    pelvis_y = positions[:, index["Hips"], 1]
    jumps = []
    for clear_start, clear_end in contiguous(clearance > 0.05):
        duration = (clear_end - clear_start + 1) * motion.frame_time
        segment = pelvis_y[clear_start:clear_end + 1]
        prominence = float((segment.max() - min(segment[0], segment[-1])) / leg_length)
        if not 0.12 <= duration <= 0.25 or prominence < 0.15:
            continue
        before = max(0, clear_start - 15)
        after = min(len(clearance) - 1, clear_end + 15)
        preparation = before + int(np.argmin(clearance[before:clear_start + 1]))
        landing = clear_end + int(np.argmin(clearance[clear_end:after + 1]))
        apex = preparation + int(np.argmax(pelvis_y[preparation:landing + 1]))
        jumps.append({
            "preparation": preparation,
            "clear_takeoff": clear_start,
            "apex": apex,
            "clear_landing": clear_end,
            "landing": landing,
            "clear_duration_seconds": duration,
            "pelvis_prominence_leg_lengths": prominence,
        })
    assert len(jumps) == 3, jumps

    semantic_ids = [index[name] for name in SEMANTIC_NAMES]
    semantic = positions[:, semantic_ids]
    terminal = {joint: positions[:, index[name]] for joint, name in TERMINALS.items()}
    starts, ends, weights = [], [], []
    for a, b, weight in SEGMENTS:
        starts.append(semantic[:, a])
        ends.append(semantic[:, b] if b is not None else terminal[a])
        weights.append(weight)
    starts = np.moveaxis(np.asarray(starts), 0, 1)
    ends = np.moveaxis(np.asarray(ends), 0, 1)
    com = np.stack([
        center_of_mass(frame_starts, frame_ends, weights, [0.5] * len(weights))[0]
        for frame_starts, frame_ends in zip(starts, ends)
    ])
    assert com.shape == (len(positions), 3) and np.isfinite(com).all()

    lower_names = ("LeftUpLeg", "LeftLeg", "LeftFoot", "RightUpLeg", "RightLeg", "RightFoot")
    lower_ids = [index[name] for name in lower_names]
    phase_rows = []
    for jump_index, jump in enumerate(jumps, 1):
        order = ("preparation", "clear_takeoff", "apex", "clear_landing", "landing")
        frames = [jump[key] for key in order]
        reference = frames[0]
        for key, frame in zip(order, frames):
            phase_rows.append({
                "jump": jump_index,
                "phase": key,
                "source_frame": frame,
                "review_frame": frame + 1,
                "seconds": frame * motion.frame_time,
                "site_clearance_leg_lengths": ((sites[frame] - floors) / leg_length).tolist(),
                "site_displacement_from_preparation_leg_lengths":
                    ((positions[frame, [index[name] for name in SITE_NAMES]] -
                      positions[reference, [index[name] for name in SITE_NAMES]]) / leg_length).tolist(),
                "pelvis_height_leg_lengths": float(pelvis_y[frame] / leg_length),
                "estimated_com_leg_lengths": (com[frame] / leg_length).tolist(),
                "lower_rotation_change_from_preparation_radians":
                    rotation_angle(rotations[reference, lower_ids], rotations[frame, lower_ids]).tolist(),
            })

    # Fit constant acceleration to the estimated COM during each confirmed clear-flight span.
    for jump in jumps:
        frames = np.arange(jump["clear_takeoff"], jump["clear_landing"] + 1)
        t = (frames - frames[0]) * motion.frame_time
        design = np.column_stack((np.ones(len(t)), t, 0.5 * t * t))
        coefficients = np.linalg.lstsq(design, com[frames] / leg_length, rcond=None)[0]
        fitted = design @ coefficients
        jump["estimated_com_acceleration_leg_lengths_per_second2"] = coefficients[2].tolist()
        jump["estimated_com_fit_max_error_leg_lengths"] = float(np.max(np.linalg.norm(fitted - com[frames] / leg_length, axis=1)))

    RESULTS.mkdir(exist_ok=False)
    report = {
        "schema": 1,
        "complete": True,
        "qualified": False,
        "clip": CLIP,
        "description": "Jump Distances",
        "source_split": "validation_exposed",
        "source_sha256": sha256(source),
        "source_bytes": source.stat().st_size,
        "manifest_sha256": sha256(TRAINING / "temporal_training_manifest_v19.json"),
        "parser_sha256": sha256(TRAINING / "bvh_data.py"),
        "script_sha256": sha256(HERE),
        "frames": len(positions),
        "fps": 1.0 / motion.frame_time,
        "leg_length_source_units": leg_length,
        "vertical_axis": "BVH Y",
        "site_names": SITE_NAMES,
        "site_floor_source_units": floors.tolist(),
        "detection": {
            "clearance_threshold_leg_lengths": 0.05,
            "duration_seconds": [0.12, 0.25],
            "pelvis_prominence_min_leg_lengths": 0.15,
            "contact_observation_search_frames": 15,
            "interpretation": "Kinematic phase observations; no force or exact contact claim.",
        },
        "jumps": jumps,
        "phases": phase_rows,
        "estimated_com_model": "Current B4ML artist-default segment weights at midpoint, adapted to mapped BVH joints",
        "confirmation_read": False,
        "limitations": [
            "One actor and one exposed clip containing three distance jumps.",
            "Floor and phase boundaries are kinematic estimates, not force-plate contact events.",
            "COM uses artist-default segment masses and approximate BVH terminal joints.",
            "No retargeting, learned prediction, animator rating or Cascadeur comparison.",
        ],
        "runtime_seconds": time.perf_counter() - started,
    }
    write_json(RESULTS / "analysis.json", report)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    t = np.arange(len(positions)) * motion.frame_time
    figure, axes = plt.subplots(2, 1, figsize=(11, 7), sharex=True, layout="constrained")
    axes[0].plot(t, (pelvis_y - pelvis_y.min()) / leg_length, label="Pelvis height above clip minimum")
    axes[0].plot(t, (com[:, 1] - com[:, 1].min()) / leg_length, label="Estimated COM height above clip minimum")
    axes[1].plot(t, clearance, color="#2874a6", label="Minimum ankle/toe clearance")
    axes[1].axhline(0.05, color="#922b21", linestyle="--", label="Confirmed clear-flight threshold")
    for number, jump in enumerate(jumps, 1):
        axes[0].axvspan(jump["clear_takeoff"] * motion.frame_time,
                       jump["clear_landing"] * motion.frame_time, color="#f4d03f", alpha=0.25)
        axes[1].axvspan(jump["clear_takeoff"] * motion.frame_time,
                       jump["clear_landing"] * motion.frame_time, color="#f4d03f", alpha=0.25)
        axes[0].text(jump["apex"] * motion.frame_time,
                     (pelvis_y[jump["apex"]] - pelvis_y.min()) / leg_length,
                     f"J{number}", ha="center", va="bottom")
    axes[0].set_ylabel("Height / leg length")
    axes[1].set_ylabel("Clearance / leg length")
    axes[1].set_xlabel("Seconds (source 120 fps)")
    for axis in axes:
        axis.grid(alpha=0.2)
        axis.legend(loc="upper right")
    figure.suptitle("Recorded CMU 141_04 jump phases\nKinematic thresholds; shaded spans are confirmed clear-flight observations")
    figure.savefig(RESULTS / "jump-phases.png", dpi=150)
    plt.close(figure)
    report["plot_sha256"] = sha256(RESULTS / "jump-phases.png")
    write_json(RESULTS / "analysis.json", report)
    print(json.dumps({"complete": True, "jumps": jumps, "phases": len(phase_rows),
                      "confirmation_read": False, "runtime_seconds": report["runtime_seconds"]}, indent=2))


if __name__ == "__main__":
    main()
