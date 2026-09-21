"""Complete-priority hierarchy examples for the repaired TCN comparison.

The 17 semantic joints remain the direct animator-control surface.  At complete
priority frames, the captured values of all 23 hierarchy joints become exact
derived constraints so intermediate bones cannot change the evaluated pose.
"""
from dataclasses import fields
from pathlib import Path
import json

import numpy as np

from full_hierarchy_store_v1 import FullHierarchyStore
from hierarchy_conditioning_adapter_v1 import assert_train_only_subject, conditioned_window
from masked_hierarchy_baseline_v1 import model_window_example
from motion_conditioning_v1 import MotionConditioning


def complete_priority_conditioning(window_result):
    condition = window_result["conditioning"].validated()
    state = np.asarray(window_result["window"]["state"], dtype=np.float32)
    pad = int(window_result["window"]["context"])
    core = state[pad:pad + condition.frames]
    if core.shape != (condition.frames, 141):
        raise ValueError("Priority state and conditioning frames disagree")
    direct_mask = np.array(condition.authored_rotation_mask, copy=True)
    values = np.array(condition.authored_rotation6, copy=True)
    fixed_mask = np.array(condition.authored_rotation_mask, copy=True)
    rotations = core[:, 3:].reshape(condition.frames, 23, 6)
    fixed_mask[[0, -1], :, :] = True
    values[[0, -1], :, :] = rotations[[0, -1], :, :]
    data = {item.name: np.array(getattr(condition, item.name), copy=True) for item in fields(condition)}
    data["authored_rotation6"] = values
    data["authored_rotation_mask"] = fixed_mask
    repaired = MotionConditioning(**data).validated()
    packed, layout = repaired.packed()
    return {
        "window": window_result["window"],
        "conditioning": repaired,
        "packed": packed,
        "layout": layout,
        "direct_control_rotation_mask": direct_mask,
        "derived_priority_rotation_mask": fixed_mask & ~direct_mask,
    }


class PriorityHierarchySequenceDataset:
    def __init__(self, specs, split_name, training_subjects, contact_thresholds, *, weak_contacts=False, root=None):
        if split_name not in ("training", "development"):
            raise ValueError("Unknown dataset split")
        if split_name == "development" and weak_contacts:
            raise ValueError("Target-derived weak contacts are forbidden for development")
        self.specs = tuple(specs)
        self.split_name = split_name
        self.training_subjects = tuple(int(value) for value in training_subjects)
        self.contact_thresholds = contact_thresholds
        self.weak_contacts = bool(weak_contacts)
        self.store = FullHierarchyStore(root or Path(__file__).resolve().parent)

    def __len__(self):
        return len(self.specs)

    def __getitem__(self, index):
        if not isinstance(index, (int, np.integer)) or not 0 <= int(index) < len(self.specs):
            raise IndexError(index)
        spec = self.specs[int(index)]
        row = self.store.entries[spec["clip_index"]]
        if row["clip"] != spec["clip"] or row["subject"] != spec["subject"]:
            raise ValueError("Sequence spec identity mismatch")
        if self.weak_contacts:
            assert_train_only_subject(row, self.training_subjects)
        raw = conditioned_window(
            self.store.clip(spec["clip_index"]), row, spec["start"], spec["end"],
            context=spec["context"], mask_pattern=spec["mask_pattern"],
            contact_thresholds=self.contact_thresholds,
            include_weak_training_contacts=self.weak_contacts,
        )
        result = complete_priority_conditioning(raw)
        example = model_window_example(result)
        condition = result["conditioning"]
        example["offsets"] = np.asarray(result["window"]["offsets"], dtype=np.float32)
        example["contact_weight"] = (
            condition.contact_probability[:, :2] * condition.contact_confidence[:, :2]
        ).astype(np.float32)
        example["semantic"] = np.asarray(self.store.semantic, dtype=np.int64)
        example["parents"] = np.asarray(self.store.parents, dtype=np.int64)
        example["dt"] = np.float32(self.store.clip(spec["clip_index"]).dt)
        example["direct_control_rotation_mask"] = result["direct_control_rotation_mask"]
        example["derived_priority_rotation_mask"] = result["derived_priority_rotation_mask"]
        example["metadata"] = dict(spec)
        return example


def load_priority_specs(root=None):
    root = Path(root or Path(__file__).resolve().parent)
    value = json.loads((root / "results/priority-sequence-specs-v2/specs.json").read_text())
    return value["training"], value["development"]
