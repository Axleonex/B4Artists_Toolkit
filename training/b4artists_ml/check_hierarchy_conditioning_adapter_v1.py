"""Contracts for full-hierarchy authored and weak-label conditioning."""
from pathlib import Path
import json
import sys

import numpy as np


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from full_hierarchy_store_v1 import FullHierarchyStore
from hierarchy_conditioning_adapter_v1 import (
    assert_train_only_subject,
    conditioned_window,
    training_conditioning,
)
from motion_conditioning_v1 import PROVENANCE_CODE


def main():
    plan = json.loads((ROOT / "motion_label_proposals_plan_v1.json").read_text())
    split = json.loads((ROOT / "results/hierarchy-cohorts-v1/split.json").read_text())
    store = FullHierarchyStore(ROOT)
    index = next(
        index for index, row in enumerate(store.entries)
        if row["subject"] in split["training_subjects"] and row["frames"] >= 35
    )
    row = store.entries[index]
    clip = store.clip(index)
    assert assert_train_only_subject(row, split["training_subjects"]) == row["subject"]

    unknown = training_conditioning(
        clip, row, plan["thresholds"]["contact"], include_weak_contacts=False
    )
    assert not unknown.contact_known.any()
    assert not unknown.contact_probability.any()
    assert unknown.action_known.all() and unknown.style_known.all()

    weak = training_conditioning(
        clip, row, plan["thresholds"]["contact"], include_weak_contacts=True
    )
    assert weak.contact_known[:, :2].all()
    assert not weak.contact_known[:, 2:].any()
    assert np.all(weak.contact_provenance[:, :2] == PROVENANCE_CODE["heuristic"])
    assert np.max(weak.contact_confidence) <= 0.35
    assert np.all(weak.contact_probability[:, 2:] == 0)
    assert not weak.scene_known.any() and not weak.support_known.any() and not weak.trajectory_known.any()

    start, end = 1, 33
    result = conditioned_window(
        clip,
        row,
        start,
        end,
        context=True,
        mask_pattern="foot_contacts",
        contact_thresholds=plan["thresholds"]["contact"],
        include_weak_training_contacts=True,
    )
    controls = result["conditioning"]
    assert result["packed"].shape == (33, 483)
    assert controls.authored_root_mask[[0, -1]].all()
    assert controls.authored_rotation_mask[0, clip.semantic].all()
    assert controls.authored_rotation_mask[-1, clip.semantic].all()
    helpers = sorted(set(range(23)) - set(clip.semantic))
    assert not controls.authored_rotation_mask[:, helpers].any()
    assert np.all(controls.authored_rotation6[~controls.authored_rotation_mask] == 0)
    assert not controls.scene_known.any() and not controls.trajectory_known.any()

    invalid = 0
    for action in (
        lambda: assert_train_only_subject(
            {"subject": split["development_subjects"][0]}, split["training_subjects"]
        ),
        lambda: conditioned_window(
            clip,
            row,
            start,
            end,
            context=True,
            mask_pattern="invalid",
            contact_thresholds=plan["thresholds"]["contact"],
            include_weak_training_contacts=False,
        ),
    ):
        try:
            action()
        except ValueError:
            invalid += 1
    assert invalid == 2
    print(
        json.dumps(
            {
                "passed": True,
                "clip": row["clip"],
                "subject": row["subject"],
                "frames": len(clip.root_positions),
                "packed_features": result["packed"].shape[1],
                "contact_modes": ["unknown", "weak_train_only"],
                "development_weak_contact_rejected": True,
                "helper_joints_authored": False,
                "scene_geometry_claimed": False,
                "invalid_cases": invalid,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
