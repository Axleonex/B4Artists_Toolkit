"""Detailed frozen-cohort evaluation for all complete-priority TCN v2 fits."""
from collections import defaultdict
from pathlib import Path
import hashlib
import json
import math
import os
import sys
import time


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import numpy as np
import torch

import train_full_hierarchy_tcn_v1 as engine
import train_full_hierarchy_tcn_v2 as training_v2
from full_hierarchy_sequence_dataset_v2 import load_priority_specs
from full_hierarchy_tcn_v1 import MaskedResidualTCN
from full_hierarchy_torch_kinematics_v1 import forward_kinematics
from full_hierarchy_store_v1 import FullHierarchyStore


PLAN_PATH = ROOT / "full_hierarchy_tcn_training_plan_v2.json"
RESULTS = ROOT / "results/full-hierarchy-tcn-v2"
OUT = RESULTS / "evaluation.json"
METRICS = (
    "root_rmse", "position_rmse", "rotation_degrees", "velocity_rmse",
    "acceleration_rmse", "jerk_rmse", "foot_velocity_rmse",
)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def rms(value, dimensions):
    return torch.sqrt(torch.mean(value.square(), dim=dimensions))


def sample_metrics(state, target, offsets, parents, semantic, dt):
    position, rotation = forward_kinematics(state, offsets, parents)
    target_position, target_rotation = forward_kinematics(target, offsets, parents)
    semantic = tuple(int(value) for value in semantic)
    pp, tp = position[:, :, semantic], target_position[:, :, semantic]
    pr, tr = rotation[:, :, semantic], target_rotation[:, :, semantic]
    relative = torch.matmul(pr.transpose(-1, -2), tr)
    cosine = torch.clamp((torch.diagonal(relative, dim1=-2, dim2=-1).sum(-1) - 1) / 2, -1, 1)
    angles = torch.acos(cosine) * (180 / math.pi)
    step = dt[:, None, None, None]
    velocity = (pp[:, 1:] - pp[:, :-1]) / step
    target_velocity = (tp[:, 1:] - tp[:, :-1]) / step
    acceleration = (velocity[:, 1:] - velocity[:, :-1]) / step
    target_acceleration = (target_velocity[:, 1:] - target_velocity[:, :-1]) / step
    jerk = (acceleration[:, 1:] - acceleration[:, :-1]) / step
    target_jerk = (target_acceleration[:, 1:] - target_acceleration[:, :-1]) / step
    feet = (13, 16)
    foot_indices = tuple(semantic[index] for index in feet)
    foot_velocity = (position[:, 1:, foot_indices] - position[:, :-1, foot_indices]) / step
    target_foot_velocity = (
        target_position[:, 1:, foot_indices] - target_position[:, :-1, foot_indices]
    ) / step
    values = {
        "root_rmse": rms(state[:, :, :3] - target[:, :, :3], (1, 2)),
        "position_rmse": rms(pp - tp, (1, 2, 3)),
        "rotation_degrees": torch.mean(angles, dim=(1, 2)),
        "velocity_rmse": rms(velocity - target_velocity, (1, 2, 3)),
        "acceleration_rmse": rms(acceleration - target_acceleration, (1, 2, 3)),
        "jerk_rmse": rms(jerk - target_jerk, (1, 2, 3)),
        "foot_velocity_rmse": rms(foot_velocity - target_foot_velocity, (1, 2, 3)),
    }
    edge = torch.linalg.vector_norm(
        position[:, :, 1:] - position[:, :, torch.as_tensor(parents[1:], device=state.device)], dim=-1
    )
    expected = torch.linalg.vector_norm(offsets[:, None, 1:], dim=-1)
    values["maximum_edge_error"] = torch.max(torch.abs(edge - expected), dim=2).values.max(dim=1).values
    return values


def append_records(destination, values, metadata, exact_errors):
    for index, item in enumerate(metadata):
        record = {name: float(values[name][index].item()) for name in METRICS}
        record["maximum_edge_error"] = float(values["maximum_edge_error"][index].item())
        record["exact_priority_error"] = float(exact_errors[index].item())
        record["task"] = item["task"]
        record["gap"] = int(item["gap"])
        record["mask"] = item["mask_pattern"]
        destination.append(record)


def summarize(records):
    result = {name: float(np.mean([row[name] for row in records])) for name in METRICS}
    result["maximum_edge_error"] = float(max(row["maximum_edge_error"] for row in records))
    result["exact_priority_error"] = float(max(row["exact_priority_error"] for row in records))
    result["windows"] = len(records)
    return result


def ratio(value, baseline):
    if baseline <= 1e-12:
        return 1.0 if value <= 1e-12 else None
    return value / baseline


def compare(model_records, baseline_records, thresholds):
    aggregate_model = summarize(model_records)
    aggregate_baseline = summarize(baseline_records)
    groups_model = defaultdict(list)
    groups_baseline = defaultdict(list)
    for model, baseline in zip(model_records, baseline_records):
        key = f"{model['task']}|{model['gap']}"
        groups_model[key].append(model)
        groups_baseline[key].append(baseline)
    cohorts = {}
    for key in sorted(groups_model):
        candidate = summarize(groups_model[key])
        base = summarize(groups_baseline[key])
        cohorts[key] = {
            "windows": candidate["windows"],
            "position_ratio": ratio(candidate["position_rmse"], base["position_rmse"]),
            "rotation_ratio": ratio(candidate["rotation_degrees"], base["rotation_degrees"]),
            "velocity_ratio": ratio(candidate["velocity_rmse"], base["velocity_rmse"]),
            "foot_velocity_ratio": ratio(candidate["foot_velocity_rmse"], base["foot_velocity_rmse"]),
        }
    position_ratios = [item["position_ratio"] for item in cohorts.values() if item["position_ratio"] is not None]
    rotation_ratios = [item["rotation_ratio"] for item in cohorts.values() if item["rotation_ratio"] is not None]
    aggregate_position_ratio = ratio(aggregate_model["position_rmse"], aggregate_baseline["position_rmse"])
    aggregate_rotation_ratio = ratio(aggregate_model["rotation_degrees"], aggregate_baseline["rotation_degrees"])
    gates = {
        "aggregate_position": aggregate_position_ratio is not None and aggregate_position_ratio <= 1 - thresholds["aggregate_position_improvement_minimum"],
        "aggregate_rotation": aggregate_rotation_ratio is not None and aggregate_rotation_ratio <= 1 - thresholds["aggregate_rotation_improvement_minimum"],
        "worst_task_gap_position": max(position_ratios) <= thresholds["worst_task_gap_position_ratio_maximum"],
        "worst_task_gap_rotation": max(rotation_ratios) <= thresholds["worst_task_gap_rotation_ratio_maximum"],
        "exact_complete_priority": aggregate_model["exact_priority_error"] <= thresholds["exact_complete_priority_error_maximum"],
        "fixed_offset_edges": aggregate_model["maximum_edge_error"] <= thresholds["fixed_offset_edge_error_maximum"],
        "reviewed_contact_slip": False,
    }
    return {
        "candidate": aggregate_model,
        "baseline": aggregate_baseline,
        "ratios": {
            "position": aggregate_position_ratio,
            "rotation": aggregate_rotation_ratio,
            "velocity": ratio(aggregate_model["velocity_rmse"], aggregate_baseline["velocity_rmse"]),
            "acceleration": ratio(aggregate_model["acceleration_rmse"], aggregate_baseline["acceleration_rmse"]),
            "jerk": ratio(aggregate_model["jerk_rmse"], aggregate_baseline["jerk_rmse"]),
            "foot_velocity": ratio(aggregate_model["foot_velocity_rmse"], aggregate_baseline["foot_velocity_rmse"]),
        },
        "worst_task_gap_position_ratio": max(position_ratios),
        "worst_task_gap_rotation_ratio": max(rotation_ratios),
        "cohorts": cohorts,
        "gates": gates,
        "automated_motion_gates_pass": all(value for name, value in gates.items() if name != "reviewed_contact_slip"),
        "promotion_ready": all(gates.values()),
    }


def main():
    plan = training_v2.verify_plan()
    split = json.loads((ROOT / "results/priority-cohorts-v2/split.json").read_text())
    labels = json.loads((ROOT / "motion_label_proposals_plan_v1.json").read_text())
    _, development_specs = load_priority_specs(ROOT)
    prepared, layout, materialize_seconds = training_v2.materialize(
        development_specs, "development", split, labels, False
    )
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    store = FullHierarchyStore(ROOT)
    ranges = engine.contact_slices(layout)
    run_reports = sorted(RESULTS.glob("*-seed-*.json"))
    if len(run_reports) != 4:
        raise ValueError("Expected four completed v2 run reports")
    models = {}
    source_hashes = {"training_plan": sha(PLAN_PATH)}
    for report_path in run_reports:
        report = json.loads(report_path.read_text())
        if not report["complete"] or report["plan_sha256"] != source_hashes["training_plan"]:
            raise ValueError("Incomplete or mismatched training report")
        checkpoint_path = ROOT / report["checkpoint"]
        if sha(checkpoint_path) != report["checkpoint_sha256"]:
            raise ValueError("Checkpoint hash mismatch")
        checkpoint = torch.load(checkpoint_path, map_location=device, weights_only=False)
        model = MaskedResidualTCN(**plan["model"]).to(device).eval()
        model.load_state_dict(checkpoint["model"])
        models[report["run_id"]] = model
        source_hashes[report["run_id"]] = report["checkpoint_sha256"]
    records = {"baseline": []}
    records.update({name: [] for name in models})
    started = time.perf_counter()
    with torch.no_grad():
        for gap, group in prepared.items():
            rng = np.random.default_rng(0)
            batch_size = int(plan["optimization"]["batch_size_by_gap"][str(gap)])
            for indices in engine.batches(group, batch_size, rng, False):
                data = engine.batch_to_device(
                    group, indices, device, "unknown_contact", ranges, 0.0, rng
                )
                baseline_values = sample_metrics(
                    data["baseline"], data["target"], data["offsets"],
                    store.parents, store.semantic, data["dt"],
                )
                baseline_exact = torch.max(
                    torch.abs(data["baseline"] - data["target"]).masked_fill(~data["mask"], 0), dim=2
                ).values.max(dim=1).values
                metadata = [group["metadata"][int(index)] for index in indices]
                append_records(records["baseline"], baseline_values, metadata, baseline_exact)
                for name, model in models.items():
                    output = model(data["features"], data["baseline"], data["mask"])
                    values = sample_metrics(
                        output, data["target"], data["offsets"],
                        store.parents, store.semantic, data["dt"],
                    )
                    exact = torch.max(
                        torch.abs(output - data["target"]).masked_fill(~data["mask"], 0), dim=2
                    ).values.max(dim=1).values
                    append_records(records[name], values, metadata, exact)
    comparisons = {
        name: compare(value, records["baseline"], plan["quality_evaluation"])
        for name, value in records.items() if name != "baseline"
    }
    by_mode = {}
    for mode in plan["contact_modes"]:
        selected = [value for name, value in comparisons.items() if name.startswith(mode + "-")]
        by_mode[mode] = {
            "seeds": len(selected),
            "both_automated_motion_gates_pass": len(selected) == 2 and all(
                value["automated_motion_gates_pass"] for value in selected
            ),
            "promotion_ready": len(selected) == 2 and all(value["promotion_ready"] for value in selected),
        }
    report = {
        "complete": True,
        "schema": "full-hierarchy-tcn-evaluation-v2",
        "evaluator_sha256": sha(Path(__file__).resolve()),
        "sources": source_hashes,
        "development_windows": len(development_specs),
        "development_subjects": len(split["development_subjects"]),
        "excluded_exposed_v1_development_subjects": len(split["excluded_exposed_v1_development_subjects"]),
        "materialization_seconds": materialize_seconds,
        "evaluation_seconds": time.perf_counter() - started,
        "comparisons": comparisons,
        "by_mode": by_mode,
        "contact_evaluation": "Overall foot-velocity error is reported, but no target-derived heuristic is treated as reviewed contact truth; reviewed contact-slip promotion remains unresolved.",
        "confirmation_read": False,
        "runtime_promoted": False,
        "quality_qualified": any(value["promotion_ready"] for value in by_mode.values()),
        "full_goal_complete": False,
    }
    write(OUT, report)
    print(json.dumps({
        "complete": True,
        "development_windows": report["development_windows"],
        "by_mode": by_mode,
        "runs": {name: {
            "ratios": value["ratios"],
            "worst_task_gap_position_ratio": value["worst_task_gap_position_ratio"],
            "worst_task_gap_rotation_ratio": value["worst_task_gap_rotation_ratio"],
            "gates": value["gates"],
            "automated_motion_gates_pass": value["automated_motion_gates_pass"],
            "promotion_ready": value["promotion_ready"],
        } for name, value in comparisons.items()},
        "confirmation_read": False,
        "runtime_promoted": False,
        "quality_qualified": report["quality_qualified"],
    }, indent=2))


if __name__ == "__main__":
    main()
