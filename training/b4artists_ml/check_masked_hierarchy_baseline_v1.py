"""Contracts for the full-hierarchy sparse-key baseline."""
from dataclasses import fields
from pathlib import Path
import json
import sys

import numpy as np


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from full_hierarchy_store_v1 import FullHierarchyStore
from hierarchy_conditioning_adapter_v1 import conditioned_window
from masked_hierarchy_baseline_v1 import (
    JOINTS,
    MODEL_INPUT_WIDTH,
    STATE_WIDTH,
    baseline_from_authored,
    model_window_example,
    project_authored,
)
from motion_conditioning_v1 import MotionConditioning


def copied(conditioning, **changes):
    data = {item.name: np.array(getattr(conditioning, item.name), copy=True) for item in fields(conditioning)}
    data.update(changes)
    return MotionConditioning(**data).validated()


def main():
    label_plan = json.loads((ROOT / "motion_label_proposals_plan_v1.json").read_text())
    split = json.loads((ROOT / "results/hierarchy-cohorts-v1/split.json").read_text())
    store = FullHierarchyStore(ROOT)
    index = next(
        index for index, row in enumerate(store.entries)
        if row["subject"] in split["training_subjects"] and row["frames"] >= 35
    )
    row, clip = store.entries[index], store.clip(index)
    result = conditioned_window(
        clip, row, 1, 33, context=True, mask_pattern="upper_mid",
        contact_thresholds=label_plan["thresholds"]["contact"], include_weak_training_contacts=True,
    )
    example = model_window_example(result)
    assert example["features"].shape == (33, MODEL_INPUT_WIDTH)
    assert example["target"].shape == example["baseline"].shape == (33, STATE_WIDTH)
    assert np.array_equal(example["baseline"][example["authored_mask"]], example["target"][example["authored_mask"]])
    assert np.all(example["residual"][example["authored_mask"]] == 0)
    context_start, context_end = example["model_feature_layout"]["boundary_context_delta"]
    known_start, known_end = example["model_feature_layout"]["boundary_context_known"]
    assert np.count_nonzero(example["features"][:, known_start:known_end]) == 2
    assert np.count_nonzero(example["features"][:, context_start:context_end]) > 0

    # Hidden target edits cannot alter model input; immediate outside motion can.
    hidden_edit = {"window": dict(result["window"]), "conditioning": result["conditioning"]}
    hidden_edit["window"]["state"] = np.array(result["window"]["state"], copy=True)
    hidden_edit["window"]["state"][2:-2, :3] += 123
    hidden_example = model_window_example(hidden_edit)
    assert np.array_equal(hidden_example["features"], example["features"])
    assert not np.array_equal(hidden_example["target"], example["target"])
    context_edit = {"window": dict(result["window"]), "conditioning": result["conditioning"]}
    context_edit["window"]["state"] = np.array(result["window"]["state"], copy=True)
    context_edit["window"]["state"][0, 0] += 1
    context_example = model_window_example(context_edit)
    assert not np.array_equal(context_example["features"], example["features"])
    assert np.array_equal(context_example["target"], example["target"])

    condition = result["conditioning"]
    roots = np.zeros_like(condition.authored_root)
    root_mask = np.zeros_like(condition.authored_root_mask)
    roots[0] = (0, 0, 0)
    roots[16] = (1, 2, 3)
    roots[-1] = (2, 4, 6)
    root_mask[[0, 16, -1]] = True
    multi = copied(condition, authored_root=roots, authored_root_mask=root_mask)
    baseline = baseline_from_authored(multi)
    assert np.allclose(baseline[8, :3], (0.5, 1, 1.5))
    assert np.allclose(baseline[24, :3], (1.5, 3, 4.5))
    assert np.array_equal(baseline[[0, 16, -1], :3], roots[[0, 16, -1]])

    blank = MotionConditioning.empty(4).validated()
    blank_baseline = baseline_from_authored(blank)
    assert blank_baseline.shape == (4, STATE_WIDTH)
    assert np.all(blank_baseline[:, :3] == 0)
    assert np.allclose(blank_baseline[:, 3:].reshape(4, JOINTS, 6)[..., :3], (1, 0, 0))
    assert np.allclose(blank_baseline[:, 3:].reshape(4, JOINTS, 6)[..., 3:], (0, 1, 0))

    invalid = 0
    for action in (
        lambda: project_authored(np.zeros((2, STATE_WIDTH)), condition),
        lambda: project_authored(np.zeros((condition.frames, STATE_WIDTH - 1)), condition),
    ):
        try:
            action()
        except ValueError:
            invalid += 1
    assert invalid == 2
    print(json.dumps({
        "passed": True,
        "input_features": int(example["features"].shape[1]),
        "state_width": STATE_WIDTH,
        "exact_authored_projection": True,
        "hidden_target_used_by_baseline": False,
        "surrounding_context_encoded": True,
        "hidden_inbetween_leakage": False,
        "invalid_cases": invalid,
    }, indent=2))


if __name__ == "__main__":
    main()
