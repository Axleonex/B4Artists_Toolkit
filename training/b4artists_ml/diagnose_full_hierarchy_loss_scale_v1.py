"""Measure prospective full-hierarchy loss scales on training data only."""
from collections import defaultdict
from pathlib import Path
import json
import sys


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import numpy as np
import torch

from full_hierarchy_sequence_dataset_v1 import HierarchySequenceDataset, load_specs
from full_hierarchy_torch_kinematics_v1 import motion_loss


WEIGHTS = {
    "root": 1.0,
    "position": 1.0,
    "rotation": 1.0,
    "velocity": 0.05,
    "acceleration": 0.0005,
    "contact": 0.1,
}
PER_GAP = 20


def stats(values):
    values = np.asarray(values, dtype=np.float64)
    return {
        "mean": float(np.mean(values)),
        "median": float(np.median(values)),
        "p95": float(np.quantile(values, 0.95)),
        "maximum": float(np.max(values)),
    }


def main():
    split = json.loads((ROOT / "results/hierarchy-cohorts-v1/split.json").read_text())
    labels = json.loads((ROOT / "motion_label_proposals_plan_v1.json").read_text())
    training, _ = load_specs(ROOT)
    selected = []
    for gap in (8, 16, 32, 64, 96):
        selected.extend([item for item in training if item["gap"] == gap][:PER_GAP])
    dataset = HierarchySequenceDataset(
        selected,
        "training",
        split["training_subjects"],
        labels["thresholds"]["contact"],
        weak_contacts=True,
        root=ROOT,
    )
    raw = defaultdict(list)
    weighted = defaultdict(list)
    totals = []
    by_gap = defaultdict(list)
    with torch.no_grad():
        for example in dataset:
            baseline = torch.as_tensor(np.array(example["baseline"], copy=True)).unsqueeze(0)
            target = torch.as_tensor(np.array(example["target"], copy=True)).unsqueeze(0)
            offsets = torch.as_tensor(np.array(example["offsets"], copy=True)).unsqueeze(0)
            contact = torch.as_tensor(np.array(example["contact_weight"], copy=True)).unsqueeze(0)
            total, terms, _ = motion_loss(
                baseline,
                target,
                offsets,
                tuple(int(value) for value in example["parents"]),
                tuple(int(value) for value in example["semantic"]),
                torch.tensor((float(example["dt"]),)),
                contact,
                WEIGHTS,
            )
            totals.append(float(total.item()))
            by_gap[str(example["metadata"]["gap"])].append(float(total.item()))
            for name, value in terms.items():
                raw[name].append(float(value.item()))
                weighted[name].append(float(value.item()) * WEIGHTS[name])
    print(json.dumps({
        "passed": True,
        "scope": "100 deterministic training windows; no development or confirmation read",
        "windows": len(selected),
        "per_gap": PER_GAP,
        "weights": WEIGHTS,
        "total": stats(totals),
        "total_by_gap": {gap: stats(values) for gap, values in sorted(by_gap.items(), key=lambda item: int(item[0]))},
        "raw_terms": {name: stats(values) for name, values in sorted(raw.items())},
        "weighted_terms": {name: stats(values) for name, values in sorted(weighted.items())},
        "development_read": False,
        "confirmation_read": False,
        "model_outcomes_read": False,
    }, indent=2))


if __name__ == "__main__":
    main()
