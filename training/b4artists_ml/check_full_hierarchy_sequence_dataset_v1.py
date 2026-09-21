"""Contracts for metadata specs and streaming hierarchy examples."""
from collections import Counter
from pathlib import Path
import json
import sys

import numpy as np


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from full_hierarchy_sequence_dataset_v1 import HierarchySequenceDataset, load_specs


def main():
    split = json.loads((ROOT / "results/hierarchy-cohorts-v1/split.json").read_text())
    label_plan = json.loads((ROOT / "motion_label_proposals_plan_v1.json").read_text())
    training, development = load_specs(ROOT)
    assert {item["subject"] for item in training} == set(split["training_subjects"])
    assert {item["subject"] for item in development} == set(split["development_subjects"])
    assert not {item["subject"] for item in training} & {item["subject"] for item in development}
    assert len(development) == 1125
    assert set(Counter(item["mask_pattern"] for item in training)) == {
        "endpoints", "upper_mid", "foot_contacts", "extremity_mid"
    }
    dataset = HierarchySequenceDataset(
        training,
        "training",
        split["training_subjects"],
        label_plan["thresholds"]["contact"],
        weak_contacts=True,
        root=ROOT,
    )
    first = dataset[0]
    frames = first["metadata"]["gap"] + 1
    assert first["features"].shape == (frames, 766)
    assert first["target"].shape == first["baseline"].shape == (frames, 141)
    assert first["offsets"].shape == (23, 3)
    assert first["contact_weight"].shape == (frames, 2)
    assert first["semantic"].shape == (17,) and first["parents"].shape == (23,)
    assert float(first["dt"]) > 0
    assert np.all(first["residual"][first["authored_mask"]] == 0)
    invalid = 0
    try:
        HierarchySequenceDataset(
            development,
            "development",
            split["training_subjects"],
            label_plan["thresholds"]["contact"],
            weak_contacts=True,
            root=ROOT,
        )
    except ValueError:
        invalid += 1
    try:
        dataset[-1]
    except IndexError:
        invalid += 1
    assert invalid == 2
    print(json.dumps({
        "passed": True,
        "training_specs": len(training),
        "development_specs": len(development),
        "training_subjects": len(set(item["subject"] for item in training)),
        "development_subjects": len(set(item["subject"] for item in development)),
        "streamed_actual_training_examples": 1,
        "development_pose_examples_read": 0,
        "input_features": first["features"].shape[1],
        "surrounding_context_encoded": True,
        "target_features": first["target"].shape[1],
        "weak_development_contacts_rejected": True,
        "invalid_cases": invalid,
    }, indent=2))


if __name__ == "__main__":
    main()
