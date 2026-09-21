"""Train the versioned complete-priority TCN comparison."""
from collections import defaultdict
from pathlib import Path
import argparse
import hashlib
import json
import sys
import time


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import numpy as np
import torch

import train_full_hierarchy_tcn_v1 as engine
from full_hierarchy_sequence_dataset_v2 import PriorityHierarchySequenceDataset, load_priority_specs
from full_hierarchy_tcn_v1 import INPUT_WIDTH, STATE_WIDTH


PLAN_PATH = ROOT / "full_hierarchy_tcn_training_plan_v2.json"
CACHE = ROOT / "cache-expanded-v1/full-hierarchy-tcn-v2"
RESULTS = ROOT / "results/full-hierarchy-tcn-v2"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_plan():
    plan = json.loads(PLAN_PATH.read_text())
    paths = {
        "trainer": Path(__file__).resolve(),
        "training_engine": ROOT / "train_full_hierarchy_tcn_v1.py",
        "model": ROOT / "full_hierarchy_tcn_v1.py",
        "kinematics": ROOT / "full_hierarchy_torch_kinematics_v1.py",
        "dataset": ROOT / "full_hierarchy_sequence_dataset_v2.py",
        "priority_plan": ROOT / "priority_cohort_plan_v2.json",
        "priority_split": ROOT / "results/priority-cohorts-v2/split.json",
        "priority_specs": ROOT / "results/priority-sequence-specs-v2/specs.json",
        "priority_report": ROOT / "results/priority-sequence-specs-v2/report.json",
        "label_plan": ROOT / "motion_label_proposals_plan_v1.json",
        "hierarchy_layout": ROOT / "results/full-hierarchy-store-v1/layout.json",
        "v1_rejection": ROOT / "results/full-hierarchy-tcn-v1/priority-helper-diagnosis.json",
    }
    actual = {name: sha(path) for name, path in paths.items()}
    if actual != plan["sources"]:
        mismatch = {name: [plan["sources"].get(name), value] for name, value in actual.items()
                    if plan["sources"].get(name) != value}
        raise ValueError("V2 training plan source mismatch: " + json.dumps(mismatch, sort_keys=True))
    if plan["confirmation_read"] or plan["runtime_promotion_allowed"]:
        raise ValueError("V2 training cannot open confirmation or promote runtime")
    return plan


def materialize(specs, split_name, split, labels, weak_contacts):
    dataset = PriorityHierarchySequenceDataset(
        specs, split_name, split["training_subjects"], labels["thresholds"]["contact"],
        weak_contacts=weak_contacts, root=ROOT,
    )
    positions = defaultdict(list)
    for index, spec in enumerate(specs):
        positions[int(spec["gap"])].append(index)
    result = {}
    layout = None
    started = time.perf_counter()
    completed = 0
    for gap in sorted(positions):
        indices = positions[gap]
        frames = gap + 1
        count = len(indices)
        arrays = {
            "features": np.empty((count, frames, INPUT_WIDTH), np.float32),
            "target": np.empty((count, frames, STATE_WIDTH), np.float32),
            "mask": np.empty((count, frames, STATE_WIDTH), bool),
            "offsets": np.empty((count, 23, 3), np.float32),
            "contact": np.empty((count, frames, 2), np.float32),
            "dt": np.empty((count,), np.float32),
        }
        metadata = []
        for destination, source in enumerate(indices):
            example = dataset[source]
            arrays["features"][destination] = example["features"]
            arrays["target"][destination] = example["target"]
            arrays["mask"][destination] = example["authored_mask"]
            arrays["offsets"][destination] = example["offsets"]
            arrays["contact"][destination] = example["contact_weight"]
            arrays["dt"][destination] = example["dt"]
            metadata.append(example["metadata"])
            if layout is None:
                layout = example["conditioning_layout"]
            completed += 1
            if completed % 250 == 0:
                print(json.dumps({"stage": "materialize-v2", "split": split_name,
                                  "completed": completed, "total": len(specs)}), flush=True)
        arrays["metadata"] = metadata
        result[gap] = arrays
    return result, layout, time.perf_counter() - started


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    plan = verify_plan()
    split = json.loads((ROOT / "results/priority-cohorts-v2/split.json").read_text())
    labels = json.loads((ROOT / "motion_label_proposals_plan_v1.json").read_text())
    training_specs, development_specs = load_priority_specs(ROOT)
    if args.verify_only:
        print(json.dumps({"passed": True, "plan_sha256": sha(PLAN_PATH),
                          "training_specs": len(training_specs),
                          "development_specs": len(development_specs),
                          "complete_priority_contract": True,
                          "confirmation_read": False}), flush=True)
        return
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if plan["environment"]["cuda_required"] and device.type != "cuda":
        raise RuntimeError("The v2 training plan requires qualified CUDA")
    training, layout, train_seconds = materialize(training_specs, "training", split, labels, True)
    development, development_layout, development_seconds = materialize(
        development_specs, "development", split, labels, False
    )
    if layout != development_layout:
        raise ValueError("V2 conditioning layouts differ")
    from full_hierarchy_store_v1 import FullHierarchyStore
    store = FullHierarchyStore(ROOT)
    engine.PLAN_PATH = PLAN_PATH
    engine.CACHE = CACHE
    engine.RESULTS = RESULTS
    reports = []
    for mode in plan["contact_modes"]:
        for seed in plan["seeds"]:
            reports.append(engine.train_run(
                mode, int(seed), training, development, layout, plan, device,
                store.parents, store.semantic,
            ))
    engine.write_json(RESULTS / "training-summary.json", {
        "complete": True,
        "plan_sha256": sha(PLAN_PATH),
        "complete_priority_contract": True,
        "training_materialization_seconds": train_seconds,
        "development_materialization_seconds": development_seconds,
        "runs": [{key: report[key] for key in (
            "run_id", "mode", "seed", "epochs", "best_epoch",
            "best_development_loss", "checkpoint_sha256"
        )} for report in reports],
        "development_subjects": len(split["development_subjects"]),
        "excluded_exposed_v1_development_subjects": len(
            split["excluded_exposed_v1_development_subjects"]
        ),
        "confirmation_read": False,
        "runtime_promoted": False,
        "quality_qualified": False,
    })
    print(json.dumps({"complete": True, "version": 2, "runs": len(reports),
                      "confirmation_read": False, "runtime_promoted": False}, indent=2))


if __name__ == "__main__":
    main()
