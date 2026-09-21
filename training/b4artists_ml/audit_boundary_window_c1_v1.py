"""Audit hidden sub-sample motion in the boundary-window C1 candidate."""
from pathlib import Path
import hashlib
import json

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "training" / "b4artists_ml" / "results"
SOURCE = RESULTS / "group-weighted-trajectory-v3"
CANDIDATE = RESULTS / "boundary-window-c1-v11"
OUTPUT = RESULTS / "boundary-window-c1-audit-v1" / "report.json"
AUTHORED_PINS = (1.0, 9.0, 15.0, 33.0, 39.0, 49.0)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def quaternion_from_rotation_vector(vectors):
    angles = np.linalg.norm(vectors, axis=-1)
    half = angles * 0.5
    scales = np.divide(np.sin(half), angles, out=np.full_like(angles, 0.5), where=angles > 1e-12)
    return np.concatenate((np.cos(half)[..., None], vectors * scales[..., None]), axis=-1)


def quaternion_multiply(left, right):
    lw, lx, ly, lz = np.moveaxis(left, -1, 0)
    rw, rx, ry, rz = np.moveaxis(right, -1, 0)
    return np.stack((lw * rw - lx * rx - ly * ry - lz * rz,
                     lw * rx + lx * rw + ly * rz - lz * ry,
                     lw * ry - lx * rz + ly * rw + lz * rx,
                     lw * rz + lx * ry - ly * rx + lz * rw), axis=-1)


def interval_motion(times, values):
    rotations = values[:, 3:].reshape(len(values), -1, 3)
    quaternions = quaternion_from_rotation_vector(rotations)
    inverse = quaternions[:-1].copy()
    inverse[..., 1:] *= -1.0
    relative = quaternion_multiply(inverse, quaternions[1:])
    relative = np.where(relative[..., :1] < 0.0, -relative, relative)
    vector = relative[..., 1:]
    lengths = np.linalg.norm(vector, axis=-1)
    angles = 2.0 * np.arctan2(lengths, np.clip(relative[..., 0], 0.0, None))
    factors = np.divide(angles, lengths, out=np.full_like(lengths, 2.0), where=lengths > 1e-12)
    dt = np.diff(times) / 30.0
    velocity = vector * factors[..., None] / dt[:, None, None]
    speed = np.linalg.norm(velocity, axis=-1)
    midpoints = (times[:-1] + times[1:]) / 60.0
    acceleration = np.diff(velocity, axis=0) / np.diff(midpoints)[:, None, None]
    acceleration_magnitude = np.linalg.norm(acceleration, axis=-1)
    return speed, acceleration_magnitude


def maximum_row(values, times, controls, acceleration=False):
    interval, control = np.unravel_index(int(np.argmax(values)), values.shape)
    offset = 1 if acceleration else 0
    return {
        "value": float(values[interval, control]),
        "control": controls[control],
        "frame_start": float(times[interval]),
        "frame_end": float(times[interval + 1 + offset]),
    }


def grouped_maxima(values, times, controls, groups):
    speed, acceleration = interval_motion(times, values)
    rows = {}
    for group in sorted(set(groups.values())):
        indices = [index for index, control in enumerate(controls) if groups[control] == group]
        group_speed = speed[:, indices]
        group_acceleration = acceleration[:, indices]
        speed_interval, speed_member = np.unravel_index(int(np.argmax(group_speed)), group_speed.shape)
        accel_interval, accel_member = np.unravel_index(int(np.argmax(group_acceleration)), group_acceleration.shape)
        rows[group] = {
            "speed": {
                "value": float(group_speed[speed_interval, speed_member]),
                "control": controls[indices[speed_member]],
                "frame_start": float(times[speed_interval]),
                "frame_end": float(times[speed_interval + 1]),
            },
            "acceleration": {
                "value": float(group_acceleration[accel_interval, accel_member]),
                "control": controls[indices[accel_member]],
                "frame_start": float(times[accel_interval]),
                "frame_end": float(times[accel_interval + 2]),
            },
        }
    return speed, acceleration, rows


def main():
    weighted = read(SOURCE / "report.json")
    candidate = read(CANDIDATE / "report.json")
    process = read(CANDIDATE / "process.json")
    assert weighted["complete"] and weighted["selected"] == "grouped16"
    assert candidate["complete"] and candidate["sampled_constraints_passed"]
    assert not candidate["qualified"] and not candidate["method_promoted"]
    assert process["complete"] and process["exit_code"] == 3221225477
    assert process["log_sha256"] == sha256(CANDIDATE / "host.log")
    assert candidate["optimized_trajectory_sha256"] == sha256(CANDIDATE / "optimized.npz")

    controls = list(weighted["control_groups"])
    groups = weighted["control_groups"]
    with np.load(SOURCE / "grouped16.npz", allow_pickle=False) as archive:
        baseline_times = archive["frames"].copy()
        baseline_values = archive["values"].copy()
    with np.load(CANDIDATE / "optimized.npz", allow_pickle=False) as archive:
        candidate_times = archive["frames"].copy()
        candidate_values = archive["values"].copy()
    assert candidate_values.shape[1] == 3 + 3 * len(controls)

    baseline_speed, baseline_acceleration, baseline_groups = grouped_maxima(
        baseline_values, baseline_times, controls, groups)
    candidate_speed, candidate_acceleration, candidate_groups = grouped_maxima(
        candidate_values, candidate_times, controls, groups)
    baseline_speed_max = maximum_row(baseline_speed, baseline_times, controls)
    baseline_acceleration_max = maximum_row(
        baseline_acceleration, baseline_times, controls, acceleration=True)
    candidate_speed_max = maximum_row(candidate_speed, candidate_times, controls)
    candidate_acceleration_max = maximum_row(
        candidate_acceleration, candidate_times, controls, acceleration=True)

    pin_errors = {}
    for frame in AUTHORED_PINS:
        baseline_indices = np.flatnonzero(np.isclose(baseline_times, frame, rtol=0.0, atol=1e-12))
        candidate_indices = np.flatnonzero(np.isclose(candidate_times, frame, rtol=0.0, atol=1e-12))
        assert len(baseline_indices) == len(candidate_indices) == 1
        pin_errors[str(int(frame))] = float(np.max(np.abs(
            candidate_values[candidate_indices[0]] - baseline_values[baseline_indices[0]])))

    minimum_span = float(np.min(np.diff(candidate_times)))
    report = {
        "schema": 1,
        "complete": True,
        "qualified": False,
        "method_promoted": False,
        "candidate_report_sha256": sha256(CANDIDATE / "report.json"),
        "candidate_trajectory_sha256": sha256(CANDIDATE / "optimized.npz"),
        "baseline_trajectory_sha256": sha256(SOURCE / "grouped16.npz"),
        "candidate_spatial_pass": True,
        "candidate_spatial_max": candidate["spatial_max"],
        "candidate_validation_samples": candidate["validation_samples"],
        "authored_pin_max_errors": pin_errors,
        "authored_pins_exact": max(pin_errors.values()) == 0.0,
        "candidate_knots": int(len(candidate_times)),
        "minimum_frame_span": minimum_span,
        "baseline": {
            "max_speed_rad_s": baseline_speed_max,
            "max_acceleration_rad_s2": baseline_acceleration_max,
            "groups": baseline_groups,
        },
        "candidate": {
            "max_speed_rad_s": candidate_speed_max,
            "max_acceleration_rad_s2": candidate_acceleration_max,
            "groups": candidate_groups,
        },
        "speed_to_baseline_ratio": candidate_speed_max["value"] / baseline_speed_max["value"],
        "acceleration_to_baseline_ratio": (
            candidate_acceleration_max["value"] / baseline_acceleration_max["value"]),
        "subinterval_temporal_regression": bool(
            candidate_speed_max["value"] > baseline_speed_max["value"] * 1.01 or
            candidate_acceleration_max["value"] > baseline_acceleration_max["value"] * 1.01),
        "production_changed": False,
        "confirmation_read": False,
        "decision": (
            "Reject the C1 candidate for promotion. Its dense spatial pass and exact pins are necessary, but newly "
            "inserted adaptive knots create hidden sub-quarter-frame speed or acceleration above the retained "
            "grouped baseline. The next solver must keep a fixed output lattice and treat adaptive samples as "
            "collocation constraints rather than output keys."
        ),
        "limitations": (
            "One artificial BoneForge jump. Rotation-vector secants are converted to shortest-arc quaternion "
            "velocity, but this audit does not assess forces, visual quality, other motions or other rigs."
        ),
    }
    assert report["authored_pins_exact"]
    assert report["subinterval_temporal_regression"]
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "spatial_pass": report["candidate_spatial_pass"],
        "authored_pins_exact": report["authored_pins_exact"],
        "minimum_frame_span": report["minimum_frame_span"],
        "speed": report["candidate"]["max_speed_rad_s"],
        "speed_to_baseline_ratio": report["speed_to_baseline_ratio"],
        "acceleration": report["candidate"]["max_acceleration_rad_s2"],
        "acceleration_to_baseline_ratio": report["acceleration_to_baseline_ratio"],
        "subinterval_temporal_regression": report["subinterval_temporal_regression"],
        "method_promoted": False,
    }, indent=2))


if __name__ == "__main__":
    main()
