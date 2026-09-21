"""Contracts for complete priority poses and the fresh v2 subject holdout."""
from pathlib import Path
import json
import sys


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import numpy as np

from full_hierarchy_sequence_dataset_v2 import PriorityHierarchySequenceDataset, load_priority_specs


def main():
    split = json.loads((ROOT / "results/priority-cohorts-v2/split.json").read_text())
    labels = json.loads((ROOT / "motion_label_proposals_plan_v1.json").read_text())
    training, development = load_priority_specs(ROOT)
    assert {item["subject"] for item in training} == set(split["training_subjects"])
    assert {item["subject"] for item in development} == set(split["development_subjects"])
    assert not set(split["training_subjects"]) & set(split["development_subjects"])
    assert not (set(split["training_subjects"]) | set(split["development_subjects"])) & set(
        split["excluded_exposed_v1_development_subjects"]
    )
    dataset = PriorityHierarchySequenceDataset(
        training, "training", split["training_subjects"],
        labels["thresholds"]["contact"], weak_contacts=True, root=ROOT,
    )
    example = dataset[0]
    frames = example["metadata"]["gap"] + 1
    assert example["features"].shape == (frames, 766)
    rotation_mask = example["authored_mask"][:, 3:].reshape(frames, 23, 6)
    assert rotation_mask[[0, -1]].all()
    assert np.array_equal(example["baseline"][[0, -1]], example["target"][[0, -1]])
    helpers = sorted(set(range(23)) - set(int(value) for value in example["semantic"]))
    assert not example["direct_control_rotation_mask"][:, helpers].any()
    assert example["derived_priority_rotation_mask"][[0, -1]][:, helpers].all()
    if frames > 2:
        assert not example["derived_priority_rotation_mask"][1:-1].any()
    invalid = 0
    try:
        PriorityHierarchySequenceDataset(
            development, "development", split["training_subjects"],
            labels["thresholds"]["contact"], weak_contacts=True, root=ROOT,
        )
    except ValueError:
        invalid += 1
    assert invalid == 1
    print(json.dumps({
        "passed": True,
        "training_windows": len(training),
        "development_windows": len(development),
        "training_subjects": len(split["training_subjects"]),
        "development_subjects": len(split["development_subjects"]),
        "excluded_exposed_v1_subjects": len(split["excluded_exposed_v1_development_subjects"]),
        "complete_priority_hierarchy_exact": True,
        "direct_animator_controls_semantic_only": True,
        "derived_helper_constraints_priority_frames_only": True,
        "weak_development_contacts_rejected": True,
        "confirmation_read": False,
        "invalid_cases": invalid,
    }, indent=2))


if __name__ == "__main__":
    main()
