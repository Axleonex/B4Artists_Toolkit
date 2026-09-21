"""Measure motion quality regressions visible in the v4 reviewer samples."""
import hashlib
import json
import math
from pathlib import Path
from statistics import median

ROOT = Path(__file__).resolve().parents[2]
REVIEW = ROOT / "training/b4artists_ml/results/review-directed-followup-reviewer-v4"
SOURCE = REVIEW / "review-data.json"
OUTPUT = REVIEW / "motion-audit-v4.json"

UPPER = tuple(range(1, 11))
ALL = tuple(range(17))
SEGMENTS = {
    "pelvis_spine": (0, 1),
    "spine_chest": (1, 2),
    "chest_neck": (2, 3),
    "upper_arm_L": (5, 6),
    "forearm_L": (6, 7),
    "upper_arm_R": (8, 9),
    "forearm_R": (9, 10),
    "thigh_L": (11, 12),
    "shin_L": (12, 13),
    "thigh_R": (14, 15),
    "shin_R": (15, 16),
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def norm(vector):
    return math.sqrt(sum(component * component for component in vector))


def sub(left, right):
    return tuple(a - b for a, b in zip(left, right))


def scale(vector, divisor):
    return tuple(component / divisor for component in vector)


def percentile(values, fraction):
    ordered = sorted(values)
    if not ordered:
        return 0.0
    index = min(len(ordered) - 1, max(0, math.ceil(fraction * len(ordered)) - 1))
    return ordered[index]


def derivatives(samples, frames, fps, joints, *, relative_to_pelvis=False):
    points = []
    for sample in samples:
        pelvis = sample[0]
        points.append([
            sub(sample[index], pelvis) if relative_to_pelvis else tuple(sample[index])
            for index in joints
        ])
    velocity = []
    velocity_dt = []
    for index in range(1, len(points)):
        dt = (frames[index] - frames[index - 1]) / fps
        velocity.append([scale(sub(a, b), dt) for a, b in zip(points[index], points[index - 1])])
        velocity_dt.append(dt)
    acceleration = []
    acceleration_dt = []
    for index in range(1, len(velocity)):
        dt = (velocity_dt[index] + velocity_dt[index - 1]) * 0.5
        acceleration.append([scale(sub(a, b), dt) for a, b in zip(velocity[index], velocity[index - 1])])
        acceleration_dt.append(dt)
    jerk = []
    for index in range(1, len(acceleration)):
        dt = (acceleration_dt[index] + acceleration_dt[index - 1]) * 0.5
        jerk.append([scale(sub(a, b), dt) for a, b in zip(acceleration[index], acceleration[index - 1])])
    return {
        "speed": [norm(value) for row in velocity for value in row],
        "acceleration": [norm(value) for row in acceleration for value in row],
        "jerk": [norm(value) for row in jerk for value in row],
    }


def angular_metrics(samples, frames, fps):
    directions = {}
    for name, (start, end) in SEGMENTS.items():
        rows = []
        for sample in samples:
            vector = sub(sample[end], sample[start])
            length = norm(vector)
            rows.append(scale(vector, length))
        directions[name] = rows
    speeds = []
    per_segment = {}
    for name, rows in directions.items():
        values = []
        for index in range(1, len(rows)):
            dt = (frames[index] - frames[index - 1]) / fps
            dot = max(-1.0, min(1.0, sum(a * b for a, b in zip(rows[index], rows[index - 1]))))
            values.append(math.acos(dot) / dt)
        per_segment[name] = {
            "p95_rad_s": percentile(values, 0.95),
            "max_rad_s": max(values, default=0.0),
        }
        speeds.extend(values)
    return {
        "p95_rad_s": percentile(speeds, 0.95),
        "max_rad_s": max(speeds, default=0.0),
        "segments": per_segment,
    }


def summarize(method, task):
    samples = method["samples"]
    frames = method["frames"]
    fps = float(method["fps"])
    upper = derivatives(samples, frames, fps, UPPER, relative_to_pelvis=True)
    whole = derivatives(samples, frames, fps, ALL)
    pelvis_z = [sample[0][2] for sample in samples]
    pelvis_y = [sample[0][1] for sample in samples]
    endpoint_z = max(pelvis_z[0], pelvis_z[-1])
    forward_steps = [pelvis_y[index] - pelvis_y[index - 1] for index in range(1, len(pelvis_y))]
    reverse_steps = sum(step > 1e-6 for step in forward_steps) if pelvis_y[-1] < pelvis_y[0] else sum(step < -1e-6 for step in forward_steps)
    result = {
        "duration_seconds": method["duration_seconds"],
        "pelvis_vertical_rise": max(pelvis_z) - endpoint_z,
        "pelvis_forward_distance": abs(pelvis_y[-1] - pelvis_y[0]),
        "pelvis_reverse_samples": reverse_steps,
        "upper_relative_p95_acceleration": percentile(upper["acceleration"], 0.95),
        "upper_relative_max_acceleration": max(upper["acceleration"], default=0.0),
        "upper_relative_p95_jerk": percentile(upper["jerk"], 0.95),
        "upper_relative_max_jerk": max(upper["jerk"], default=0.0),
        "whole_body_p95_acceleration": percentile(whole["acceleration"], 0.95),
        "whole_body_max_acceleration": max(whole["acceleration"], default=0.0),
        "angular": angular_metrics(samples, frames, fps),
    }
    if task == "run":
        magnitudes = [abs(step) for step in forward_steps]
        typical = median(magnitudes) if magnitudes else 0.0
        result["pelvis_forward_step_peak_ratio"] = max(magnitudes, default=0.0) / max(typical, 1e-12)
    return result


def build():
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    cases = []
    for case in data["cases"]:
        candidate_label = next(
            label for label, identity in case["reveal"].items()
            if identity["variant"] == "candidate"
        )
        baseline_label = "B" if candidate_label == "A" else "A"
        candidate = summarize(case["methods"][candidate_label], case["task"])
        baseline = summarize(case["methods"][baseline_label], case["task"])
        ratios = {}
        for field in (
            "upper_relative_p95_acceleration",
            "upper_relative_max_acceleration",
            "upper_relative_p95_jerk",
            "upper_relative_max_jerk",
            "whole_body_p95_acceleration",
            "whole_body_max_acceleration",
        ):
            ratios[field] = candidate[field] / max(baseline[field], 1e-12)
        cases.append({
            "id": case["id"],
            "candidate_label": candidate_label,
            "candidate": candidate,
            "baseline": baseline,
            "candidate_to_baseline_ratios": ratios,
        })
    return {
        "schema": "b4ml-review-directed-followup-motion-audit-v4",
        "source_data_sha256": sha(SOURCE),
        "complete": True,
        "training_authorized": False,
        "model_promotion_authorized": False,
        "cases": cases,
    }


if __name__ == "__main__":
    report = build()
    OUTPUT.write_text(json.dumps(report, indent=2, allow_nan=False), encoding="utf-8")
    print(json.dumps(report, indent=2, allow_nan=False))
