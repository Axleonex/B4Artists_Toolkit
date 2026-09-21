"""Validate and summarize the bounded recorded-jump reference milestone."""
from pathlib import Path
import hashlib
import json
import math
import sys
import time

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
TRAINING = ROOT / "training" / "b4artists_ml"
RESULTS = TRAINING / "results" / "recorded-jump-reference-v1"
DOCS = ROOT / "docs" / "b4artists_ml"
SOURCE = TRAINING / "cache" / "141_04.bvh"
ANALYSIS = RESULTS / "analysis.json"
HOST = RESULTS / "scene-host-report.json"
WRAPPER = RESULTS / "scene-wrapper-report.json"
SUMMARY = RESULTS / "summary.json"


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def rotation_vector(relative):
    cosine = np.clip((np.trace(relative, axis1=-2, axis2=-1) - 1.0) * 0.5, -1.0, 1.0)
    angle = np.arccos(cosine)
    skew = np.stack((relative[..., 2, 1] - relative[..., 1, 2],
                     relative[..., 0, 2] - relative[..., 2, 0],
                     relative[..., 1, 0] - relative[..., 0, 1]), axis=-1)
    denominator = 2.0 * np.sin(angle)
    factor = np.where(angle < 1e-7, 0.5, angle / denominator)
    return skew * factor[..., None]


def percentile_row(values, labels):
    flat = values.reshape(-1)
    maximum = int(np.argmax(values))
    frame_index, joint_index = np.unravel_index(maximum, values.shape)
    return {
        "p95": float(np.percentile(flat, 95)),
        "p99": float(np.percentile(flat, 99)),
        "max": float(flat[maximum]),
        "max_joint": labels[joint_index],
        "local_interval_index": int(frame_index),
    }


def main():
    started = time.perf_counter()
    analysis = read(ANALYSIS)
    host = read(HOST)
    wrapper = read(WRAPPER)
    assert analysis["complete"] and not analysis["qualified"] and len(analysis["jumps"]) == 3
    assert analysis["source_sha256"] == sha256(SOURCE)
    assert analysis["script_sha256"] == sha256(TRAINING / "analyze_recorded_jump_v1.py")
    assert analysis["plot_sha256"] == sha256(RESULTS / "jump-phases.png")
    assert host["complete"] and host["saved"] and not host["qualified"]
    assert host["analysis_sha256"] == sha256(ANALYSIS)
    assert host["builder_sha256"] == sha256(TRAINING / "build_recorded_jump_scene_v1.py")
    assert host["blend_sha256"] == sha256(RESULTS / "recorded-jump-reference-v1.blend")
    assert host["action_api"] == "layered_channelbag"
    assert host["action_frame_range"] == [1.0, 548.0] and host["scene_frame_range"] == [1, 548]
    assert host["scene_fps"] == 120.0 and len(host["timeline_markers"]) == 15
    assert host["max_rigid_mapping_error"] < 5e-4
    assert host["max_pairwise_distance_error"] < 5e-4
    assert wrapper["complete"] and wrapper["production_sources_unchanged"]
    assert wrapper["host_returncode"] == 3221225477 and wrapper["known_shutdown_crash_tolerated"]
    assert not any((TRAINING / "cache" / f"{name}.bvh").exists()
                   for name in read(TRAINING / "temporal_expansion_plan_v19.json")["planned_splits"]["confirmation"])
    assert not any(item["confirmation_read"] for item in (analysis, host, wrapper))

    sys.path.insert(0, str(TRAINING))
    from bvh_data import parse_bvh
    motion = parse_bvh(SOURCE.read_text(encoding="utf-8"))
    _, rotations = motion.transforms()
    names = list(motion.names)
    semantic = [name for name in analysis["site_names"] if name in names]
    semantic += [name for name in (
        "Hips", "Spine", "Spine1", "Neck1", "Head",
        "LeftArm", "LeftForeArm", "LeftHand", "RightArm", "RightForeArm", "RightHand",
        "LeftUpLeg", "LeftLeg", "RightUpLeg", "RightLeg",
    ) if name not in semantic]
    ids = [names.index(name) for name in semantic]
    selected = rotations[:, ids]
    relative = np.swapaxes(selected[:-1], -1, -2) @ selected[1:]
    velocity = rotation_vector(relative) / motion.frame_time
    acceleration = np.diff(velocity, axis=0) / motion.frame_time
    speed = np.linalg.norm(velocity, axis=-1)
    accel = np.linalg.norm(acceleration, axis=-1)
    groups = {
        "upper_body": [semantic.index(name) for name in (
            "Spine", "Spine1", "Neck1", "Head", "LeftArm", "LeftForeArm", "LeftHand",
            "RightArm", "RightForeArm", "RightHand",
        )],
        "legs_and_feet": [semantic.index(name) for name in (
            "LeftUpLeg", "LeftLeg", "LeftFoot", "LeftToeBase",
            "RightUpLeg", "RightLeg", "RightFoot", "RightToeBase",
        )],
    }
    motion_rows = []
    for number, jump in enumerate(analysis["jumps"], 1):
        start = jump["preparation"]
        end = jump["landing"]
        speeds = speed[start:end]
        accelerations = accel[start:max(start + 1, end - 1)]
        speed_row = percentile_row(speeds, semantic)
        accel_row = percentile_row(accelerations, semantic)
        speed_row["source_interval_start"] = start + speed_row.pop("local_interval_index")
        accel_row["source_interval_start"] = start + accel_row.pop("local_interval_index")
        group_rows = {}
        for group_name, group_ids in groups.items():
            labels = [semantic[index] for index in group_ids]
            group_speed = percentile_row(speeds[:, group_ids], labels)
            group_accel = percentile_row(accelerations[:, group_ids], labels)
            group_speed["source_interval_start"] = start + group_speed.pop("local_interval_index")
            group_accel["source_interval_start"] = start + group_accel.pop("local_interval_index")
            group_rows[group_name] = {
                "angular_speed_rad_s": group_speed,
                "angular_acceleration_rad_s2": group_accel,
            }
        motion_rows.append({
            "jump": number,
            "source_window": [start, end],
            "global_joint_angular_speed_rad_s": speed_row,
            "global_joint_angular_acceleration_rad_s2": accel_row,
            "joint_groups": group_rows,
        })

    vertical_acceleration = np.asarray([
        jump["estimated_com_acceleration_leg_lengths_per_second2"][1]
        for jump in analysis["jumps"]
    ])
    fit_errors = [jump["estimated_com_fit_max_error_leg_lengths"] for jump in analysis["jumps"]]
    summary = {
        "schema": 1,
        "complete": True,
        "full_goal_complete": False,
        "method_promoted": False,
        "source": "CMU 141_04 Jump Distances",
        "source_split": "validation_exposed",
        "source_sha256": analysis["source_sha256"],
        "recorded_jumps": 3,
        "phase_markers": 15,
        "reference_scene": RESULTS.joinpath("recorded-jump-reference-v1.blend").relative_to(ROOT).as_posix(),
        "reference_scene_sha256": host["blend_sha256"],
        "reference_scene_bytes": host["blend_bytes"],
        "host_geometry_validation": {
            "frames": len(host["validation_frames"]),
            "max_rigid_mapping_error": host["max_rigid_mapping_error"],
            "max_pairwise_distance_error": host["max_pairwise_distance_error"],
        },
        "clear_flight_vertical_com_acceleration_leg_lengths_per_second2": {
            "values": vertical_acceleration.tolist(),
            "mean": float(vertical_acceleration.mean()),
            "range": float(np.ptp(vertical_acceleration)),
        },
        "clear_flight_max_com_fit_error_leg_lengths": fit_errors,
        "recorded_motion_bounds": motion_rows,
        "corrective_host_attempts": 2,
        "first_attempt_failure": "Legacy action.fcurves assumption on layered Blender 5.2 Action API",
        "second_attempt_complete": True,
        "host_shutdown_clean": False,
        "production_sources_unchanged": True,
        "confirmation_read": False,
        "decision": "Use the three recorded jumps as a realistic calibration reference before adding temporal constraints to the retained artificial stress solve. Preserve the stress failure and do not promote or release a solver from this reference alone.",
        "limits": [
            "One actor and one exposed clip; no diversity or generalization qualification.",
            "Kinematic floor/contact estimates only; no force, torque, or measured center of mass.",
            "Imported source motion is a reference action, not a generated or retargeted result.",
            "No animator usability rating or Cascadeur comparison.",
        ],
        "runtime_seconds": time.perf_counter() - started,
    }
    assert np.ptp(vertical_acceleration) < 1.0
    assert max(fit_errors) < 0.02
    write_json(SUMMARY, summary)
    print(json.dumps({
        "recorded_jumps": summary["recorded_jumps"],
        "phase_markers": summary["phase_markers"],
        "vertical_acceleration": summary["clear_flight_vertical_com_acceleration_leg_lengths_per_second2"],
        "motion_bounds": summary["recorded_motion_bounds"],
        "host_geometry_validation": summary["host_geometry_validation"],
        "full_goal_complete": False,
    }, indent=2))


if __name__ == "__main__":
    main()
