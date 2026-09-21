"""Compare artificial and recorded jump motion by phase and joint group."""
from pathlib import Path
import hashlib
import json
import math
import sys
import time

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve()
TRAINING = ROOT / "training" / "b4artists_ml"
RESULTS = TRAINING / "results" / "jump-temporal-envelope-v1"
STRESS_PATH = TRAINING / "results" / "coupled-trajectory-reconstruction-v2" / "report.json"
REFERENCE_PATH = TRAINING / "results" / "recorded-jump-reference-v1" / "analysis.json"
SOURCE_PATH = TRAINING / "cache" / "141_04.bvh"
CHECKPOINT_PATH = ROOT / "docs" / "b4artists_ml" / "checkpoint-recorded-jump-reference-v1.json"
PHASES = ("compression", "clear_flight", "recovery")
STATISTICS = ("p95", "p99", "max", "rms")


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def quaternion_multiply(a, b):
    aw, ax, ay, az = np.moveaxis(a, -1, 0)
    bw, bx, by, bz = np.moveaxis(b, -1, 0)
    return np.stack((
        aw * bw - ax * bx - ay * by - az * bz,
        aw * bx + ax * bw + ay * bz - az * by,
        aw * by - ax * bz + ay * bw + az * bx,
        aw * bz + ax * by - ay * bx + az * bw,
    ), axis=-1)


def quaternion_velocity(sequence, dt):
    sequence = sequence / np.linalg.norm(sequence, axis=-1, keepdims=True)
    inverse = sequence[:-1].copy()
    inverse[..., 1:] *= -1
    relative = quaternion_multiply(inverse, sequence[1:])
    relative = np.where((relative[..., :1] < 0), -relative, relative)
    vector = relative[..., 1:]
    length = np.linalg.norm(vector, axis=-1)
    angle = 2.0 * np.arctan2(length, np.clip(relative[..., 0], 0.0, None))
    factor = np.divide(angle, length, out=np.full_like(length, 2.0), where=length > 1e-12)
    return vector * factor[..., None] / dt


def matrix_velocity(sequence, dt):
    relative = np.swapaxes(sequence[:-1], -1, -2) @ sequence[1:]
    cosine = np.clip((np.trace(relative, axis1=-2, axis2=-1) - 1.0) * 0.5, -1.0, 1.0)
    angle = np.arccos(cosine)
    skew = np.stack((relative[..., 2, 1] - relative[..., 1, 2],
                     relative[..., 0, 2] - relative[..., 2, 0],
                     relative[..., 1, 0] - relative[..., 0, 1]), axis=-1)
    denominator = 2.0 * np.sin(angle)
    factor = np.divide(angle, denominator, out=np.full_like(angle, 0.5), where=np.abs(denominator) > 1e-12)
    return skew * factor[..., None] / dt


def metric(values, labels, interval_starts):
    magnitude = np.linalg.norm(values, axis=-1)
    flat_index = int(np.argmax(magnitude))
    interval, member = np.unravel_index(flat_index, magnitude.shape)
    flat = magnitude.reshape(-1)
    return {
        "p95": float(np.percentile(flat, 95)),
        "p99": float(np.percentile(flat, 99)),
        "max": float(flat[flat_index]),
        "rms": float(np.sqrt(np.mean(flat * flat))),
        "max_member": labels[member],
        "max_interval_start": float(interval_starts[interval]),
        "samples": int(flat.size),
    }


def phase_metrics(sequence, dt, labels, groups, interval_starts):
    velocity = quaternion_velocity(sequence, dt) if sequence.shape[-1] == 4 else matrix_velocity(sequence, dt)
    acceleration = np.diff(velocity, axis=0) / dt
    rows = {}
    for group, members in groups.items():
        ids = [labels.index(name) for name in members]
        rows[group] = {
            "angular_speed_rad_s": metric(velocity[:, ids], members, interval_starts[:-1]),
            "angular_acceleration_rad_s2": metric(acceleration[:, ids], members, interval_starts[1:-1]),
        }
    return rows


def main():
    started = time.perf_counter()
    checkpoint = read(CHECKPOINT_PATH)
    evidence = read(ROOT / checkpoint["evidence"])
    protected = evidence["artifacts"]
    for path in (STRESS_PATH, REFERENCE_PATH, SOURCE_PATH):
        relative = path.relative_to(ROOT).as_posix()
        assert relative in protected and protected[relative] == sha256(path), relative
    assert not checkpoint["active_jobs"] and checkpoint["round"] == 69
    assert all(not (TRAINING / "cache" / f"{name}.bvh").exists()
               for name in read(TRAINING / "temporal_expansion_plan_v19.json")["planned_splits"]["confirmation"])

    stress = read(STRESS_PATH)
    reference = read(REFERENCE_PATH)
    assert stress["complete"] and stress["sampled_constraints_passed"] and not stress["qualified"]
    assert reference["complete"] and not reference["qualified"] and reference["confirmation_read"] is False
    quarter_rows = [row for row in stress["dense"] if abs(row["frame"] * 4 - round(row["frame"] * 4)) < 1e-9]
    quarter_rows.sort(key=lambda row: row["frame"])
    stress_frames = np.asarray([row["frame"] for row in quarter_rows])
    assert len(quarter_rows) == 193 and np.allclose(np.diff(stress_frames), 0.25, rtol=0, atol=1e-12)
    stress_labels = list(stress["controls"])
    stress_sequence = np.asarray([[row["control_quaternions"][name] for name in stress_labels]
                                  for row in quarter_rows])
    stress_groups = {
        "upper_body": [name for name in stress_labels if name in {
            "chest", "clavicle.fk-L", "clavicle.fk-R", "upperarm.fk-L", "upperarm.fk-R",
            "forearm.fk-L", "forearm.fk-R", "hand.fk-L", "hand.fk-R", "head", "neck",
            "spine.01", "spine.02",
        }],
        "legs_and_feet": [name for name in stress_labels if name in {
            "thigh.fk-L", "thigh.fk-R", "shin.fk-L", "shin.fk-R", "foot.fk-L", "foot.fk-R",
        }],
        "core": ["hips"],
    }
    assert set().union(*map(set, stress_groups.values())) == set(stress_labels)
    stress_boundaries = {
        "compression": (9.0, 15.0),
        "clear_flight": (15.0, 33.0),
        "recovery": (33.0, 39.0),
    }
    common_dt = 1.0 / 120.0
    stress_results = {}
    for phase, (first, last) in stress_boundaries.items():
        mask = (stress_frames >= first) & (stress_frames <= last)
        stress_results[phase] = phase_metrics(
            stress_sequence[mask], common_dt, stress_labels, stress_groups,
            ((stress_frames[mask] - first) * common_dt / 0.25),
        )

    sys.path.insert(0, str(TRAINING))
    from bvh_data import parse_bvh
    motion = parse_bvh(SOURCE_PATH.read_text(encoding="utf-8"))
    _, rotations = motion.transforms()
    assert abs(motion.frame_time - common_dt) < 1e-7
    reference_labels = list(motion.names)
    reference_groups = {
        "upper_body": [
            "Spine", "Spine1", "Neck1", "Head", "LeftArm", "LeftForeArm", "LeftHand",
            "RightArm", "RightForeArm", "RightHand",
        ],
        "legs_and_feet": [
            "LeftUpLeg", "LeftLeg", "LeftFoot", "LeftToeBase",
            "RightUpLeg", "RightLeg", "RightFoot", "RightToeBase",
        ],
        "core": ["Hips"],
    }
    assert set().union(*map(set, reference_groups.values())) <= set(reference_labels)
    reference_boundaries = {
        "compression": ("preparation", "clear_takeoff"),
        "clear_flight": ("clear_takeoff", "clear_landing"),
        "recovery": ("clear_landing", "landing"),
    }
    reference_results = []
    for number, jump in enumerate(reference["jumps"], 1):
        phases = {}
        for phase, (first_key, last_key) in reference_boundaries.items():
            first, last = jump[first_key], jump[last_key]
            phases[phase] = phase_metrics(
                rotations[first:last + 1], common_dt, reference_labels, reference_groups,
                np.arange(last - first + 1) * common_dt,
            )
        reference_results.append({"jump": number, "phases": phases})

    envelopes = {}
    comparisons = []
    for phase in PHASES:
        envelopes[phase] = {}
        for group in stress_groups:
            envelopes[phase][group] = {}
            for quantity in ("angular_speed_rad_s", "angular_acceleration_rad_s2"):
                envelope = {
                    statistic: max(row["phases"][phase][group][quantity][statistic]
                                   for row in reference_results)
                    for statistic in STATISTICS
                }
                envelopes[phase][group][quantity] = envelope
                stress_metric = stress_results[phase][group][quantity]
                ratios = {statistic: stress_metric[statistic] / envelope[statistic]
                          for statistic in STATISTICS}
                comparisons.append({
                    "phase": phase,
                    "group": group,
                    "quantity": quantity,
                    "stress": stress_metric,
                    "recorded_envelope": envelope,
                    "ratios": ratios,
                })
    comparisons.sort(key=lambda row: row["ratios"]["p99"], reverse=True)
    material = [row for row in comparisons if row["ratios"]["p99"] > 1.25 or row["ratios"]["max"] > 1.5]
    assert material

    RESULTS.mkdir(exist_ok=False)
    report = {
        "schema": 1,
        "complete": True,
        "qualified": False,
        "method_promoted": False,
        "common_sample_interval_seconds": common_dt,
        "effective_sample_rate_hz": 120.0,
        "stress_input": STRESS_PATH.relative_to(ROOT).as_posix(),
        "stress_input_sha256": sha256(STRESS_PATH),
        "reference_input": REFERENCE_PATH.relative_to(ROOT).as_posix(),
        "reference_input_sha256": sha256(REFERENCE_PATH),
        "source_sha256": sha256(SOURCE_PATH),
        "script_sha256": sha256(HERE),
        "stress_groups": stress_groups,
        "reference_groups": reference_groups,
        "stress_phase_boundaries": stress_boundaries,
        "reference_phase_boundaries": reference_boundaries,
        "stress": stress_results,
        "recorded_jumps": reference_results,
        "recorded_envelopes": envelopes,
        "comparisons": comparisons,
        "material_exceedances": material,
        "source_preserved": True,
        "production_changed": False,
        "confirmation_read": False,
        "decision": "Use phase- and group-sensitive temporal penalties only where artificial p99/max behavior materially exceeds the recorded envelope; preserve all hard spatial constraints and pins.",
        "limitations": [
            "One recorded actor/clip and one artificial BoneForge request; ratios are diagnostics, not population thresholds.",
            "Global joint/control orientations are compared by group, not one-to-one retargeted semantics.",
            "Finite 120 Hz differences do not certify continuous angular bounds or anatomical joint limits.",
            "No force, torque, visual quality, animator rating, learned-model or Cascadeur comparison.",
        ],
        "runtime_seconds": time.perf_counter() - started,
    }
    write_json(RESULTS / "report.json", report)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    figure, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True, layout="constrained")
    labels = [f"{row['phase']}\n{row['group']}" for row in comparisons if row["quantity"] == "angular_speed_rad_s"]
    x = np.arange(len(labels))
    for axis, quantity, title in zip(
            axes,
            ("angular_speed_rad_s", "angular_acceleration_rad_s2"),
            ("Angular speed", "Angular acceleration")):
        rows = [row for row in comparisons if row["quantity"] == quantity]
        rows.sort(key=lambda row: (PHASES.index(row["phase"]), list(stress_groups).index(row["group"])))
        axis.bar(x - 0.19, [row["ratios"]["p95"] for row in rows], 0.19, label="p95 ratio")
        axis.bar(x, [row["ratios"]["p99"] for row in rows], 0.19, label="p99 ratio")
        axis.bar(x + 0.19, [row["ratios"]["max"] for row in rows], 0.19, label="max ratio")
        axis.axhline(1.0, color="#922b21", linestyle="--", linewidth=1)
        axis.set_ylabel(f"{title}\nstress / recorded envelope")
        axis.grid(axis="y", alpha=0.2)
        axis.legend(loc="upper right", ncol=3)
    ordered_labels = [f"{phase.replace('_', ' ')}\n{group.replace('_', ' ')}"
                      for phase in PHASES for group in stress_groups]
    axes[-1].set_xticks(x, ordered_labels)
    figure.suptitle("Artificial BoneForge jump vs recorded CMU 141_04 envelope\nEqual 1/120 s differences; diagnostic ratios, not acceptance thresholds")
    figure.savefig(RESULTS / "temporal-envelope-ratios.png", dpi=150)
    plt.close(figure)
    report["plot_sha256"] = sha256(RESULTS / "temporal-envelope-ratios.png")
    write_json(RESULTS / "report.json", report)
    print(json.dumps({
        "complete": True,
        "material_exceedances": [{
            "phase": row["phase"], "group": row["group"], "quantity": row["quantity"],
            "p99_ratio": row["ratios"]["p99"], "max_ratio": row["ratios"]["max"],
            "max_member": row["stress"]["max_member"],
        } for row in material],
        "confirmation_read": False,
    }, indent=2))


if __name__ == "__main__":
    main()
