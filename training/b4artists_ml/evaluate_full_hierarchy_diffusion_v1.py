"""Frozen-cohort evaluation for every diffusion v1 fit and DDIM budget."""
from pathlib import Path
import hashlib
import json
import os
import sys
import time


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import numpy as np
import torch

import evaluate_full_hierarchy_tcn_v2 as metrics
import train_full_hierarchy_diffusion_v1 as training
import train_full_hierarchy_tcn_v1 as batches
import train_full_hierarchy_tcn_v2 as data_v2
from full_hierarchy_diffusion_v1 import ConditionalResidualDiffusionUNet, ddim_sample
from full_hierarchy_sequence_dataset_v2 import load_priority_specs
from full_hierarchy_store_v1 import FullHierarchyStore


PLAN_PATH = ROOT / "full_hierarchy_diffusion_training_plan_v1.json"
RESULTS = ROOT / "results/full-hierarchy-diffusion-v1"
OUT = RESULTS / "evaluation.json"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def exact_error(state, target, mask):
    return torch.max(
        torch.abs(state - target).masked_fill(~mask, 0), dim=2
    ).values.max(dim=1).values


def main():
    plan = training.verify_plan()
    split = json.loads((ROOT / "results/priority-cohorts-v2/split.json").read_text())
    labels = json.loads((ROOT / "motion_label_proposals_plan_v1.json").read_text())
    _, development_specs = load_priority_specs(ROOT)
    prepared, layout, materialization_seconds = data_v2.materialize(
        development_specs, "development", split, labels, False
    )
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if plan["environment"]["cuda_required"] and device.type != "cuda":
        raise RuntimeError("Diffusion evaluation requires the qualified CUDA environment")
    store = FullHierarchyStore(ROOT)
    contact_ranges = batches.contact_slices(layout)
    expected_runs = {
        f"{mode}-seed-{seed}"
        for mode in plan["contact_modes"] for seed in plan["seeds"]
    }
    report_paths = sorted(
        path for path in RESULTS.glob("*-seed-*.json")
        if path.stem in expected_runs
    )
    if {path.stem for path in report_paths} != expected_runs:
        raise ValueError("Expected all four completed diffusion run reports")
    plan_hash = sha(PLAN_PATH)
    models = {}
    source_hashes = {"training_plan": plan_hash, "evaluator": sha(Path(__file__).resolve())}
    for report_path in report_paths:
        report = json.loads(report_path.read_text())
        run_id = report_path.stem
        if report.get("run_id") != run_id or not report.get("complete"):
            raise ValueError(f"Incomplete or mismatched report: {report_path.name}")
        if report.get("plan_sha256") != plan_hash:
            raise ValueError(f"Training-plan mismatch: {report_path.name}")
        checkpoint_path = ROOT / report["checkpoint"]
        if sha(checkpoint_path) != report["checkpoint_sha256"]:
            raise ValueError(f"Checkpoint hash mismatch: {run_id}")
        checkpoint = torch.load(checkpoint_path, map_location=device, weights_only=False)
        model = ConditionalResidualDiffusionUNet(**plan["model"]).to(device).eval()
        model.load_state_dict(checkpoint["model"])
        models[run_id] = model
        source_hashes[run_id] = report["checkpoint_sha256"]

    step_counts = tuple(int(value) for value in plan["quality_evaluation"]["ddim_steps"])
    records = {"baseline": []}
    records.update({f"{run_id}|steps-{steps}": [] for run_id in models for steps in step_counts})
    started = time.perf_counter()
    with torch.no_grad():
        for gap, group in prepared.items():
            rng = np.random.default_rng(0)
            batch_size = int(plan["optimization"]["batch_size_by_gap"][str(gap)])
            for batch_number, indices in enumerate(batches.batches(group, batch_size, rng, False)):
                data = batches.batch_to_device(
                    group, indices, device, "unknown_contact", contact_ranges, 0.0, rng
                )
                metadata = [group["metadata"][int(index)] for index in indices]
                baseline_values = metrics.sample_metrics(
                    data["baseline"], data["target"], data["offsets"],
                    store.parents, store.semantic, data["dt"],
                )
                metrics.append_records(
                    records["baseline"], baseline_values, metadata,
                    exact_error(data["baseline"], data["target"], data["mask"]),
                )
                sample_seed = int(plan["optimization"]["selection_noise_seed"]) + gap * 1000 + batch_number
                for run_id, model in models.items():
                    for steps in step_counts:
                        output = ddim_sample(
                            model, data["features"], data["baseline"], data["mask"],
                            steps, sample_seed,
                        )
                        values = metrics.sample_metrics(
                            output, data["target"], data["offsets"],
                            store.parents, store.semantic, data["dt"],
                        )
                        metrics.append_records(
                            records[f"{run_id}|steps-{steps}"], values, metadata,
                            exact_error(output, data["target"], data["mask"]),
                        )

    comparisons = {
        name: metrics.compare(value, records["baseline"], plan["quality_evaluation"])
        for name, value in records.items() if name != "baseline"
    }
    by_mode_and_steps = {}
    for mode in plan["contact_modes"]:
        by_mode_and_steps[mode] = {}
        for steps in step_counts:
            selected = [
                value for name, value in comparisons.items()
                if name.startswith(mode + "-seed-") and name.endswith(f"|steps-{steps}")
            ]
            by_mode_and_steps[mode][str(steps)] = {
                "seeds": len(selected),
                "both_automated_motion_gates_pass": len(selected) == 2 and all(
                    value["automated_motion_gates_pass"] for value in selected
                ),
                "promotion_ready": False,
            }
    any_motion_pass = any(
        value["both_automated_motion_gates_pass"]
        for mode in by_mode_and_steps.values() for value in mode.values()
    )
    report = {
        "complete": True,
        "schema": "full-hierarchy-diffusion-evaluation-v1",
        "sources": source_hashes,
        "development_windows": len(development_specs),
        "development_subjects": len(split["development_subjects"]),
        "excluded_exposed_v1_development_subjects": len(split["excluded_exposed_v1_development_subjects"]),
        "materialization_seconds": materialization_seconds,
        "evaluation_seconds": time.perf_counter() - started,
        "ddim_steps": list(step_counts),
        "noise_policy": "Same fixed initial-noise seed per development batch for every run and DDIM budget.",
        "comparisons": comparisons,
        "by_mode_and_steps": by_mode_and_steps,
        "contact_evaluation": "Foot-velocity error is descriptive only; no target-derived contact heuristic is treated as reviewed truth.",
        "bforartists_latency_qualified": False,
        "automated_motion_quality_qualified": any_motion_pass,
        "runtime_promoted": False,
        "quality_qualified": False,
        "confirmation_read": False,
        "full_goal_complete": False,
    }
    write(OUT, report)
    print(json.dumps({
        "complete": True,
        "development_windows": report["development_windows"],
        "by_mode_and_steps": by_mode_and_steps,
        "runs": {
            name: {
                "ratios": value["ratios"],
                "worst_task_gap_position_ratio": value["worst_task_gap_position_ratio"],
                "worst_task_gap_rotation_ratio": value["worst_task_gap_rotation_ratio"],
                "gates": value["gates"],
                "automated_motion_gates_pass": value["automated_motion_gates_pass"],
                "promotion_ready": False,
            }
            for name, value in comparisons.items()
        },
        "bforartists_latency_qualified": False,
        "automated_motion_quality_qualified": any_motion_pass,
        "runtime_promoted": False,
        "quality_qualified": False,
        "confirmation_read": False,
    }, indent=2))


if __name__ == "__main__":
    main()
