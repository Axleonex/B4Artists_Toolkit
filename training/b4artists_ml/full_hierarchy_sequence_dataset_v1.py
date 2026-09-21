"""Streaming full-hierarchy sequence examples for fixed model comparisons.

SPDX-License-Identifier: GPL-2.0-or-later
"""
from collections import defaultdict
from pathlib import Path
import hashlib
import json

import numpy as np

from full_hierarchy_store_v1 import FullHierarchyStore
from hierarchy_conditioning_adapter_v1 import assert_train_only_subject, conditioned_window
from masked_hierarchy_baseline_v1 import model_window_example


MASK_PATTERNS = ("endpoints", "upper_mid", "foot_contacts", "extremity_mid")
TASKS = (
    "walk", "run", "jump", "turn", "crouch", "reach_or_object", "recovery",
    "interaction", "aerial", "combat", "dance", "gesture", "other",
)


def _digest(*parts):
    return hashlib.sha256("|".join(map(str, parts)).encode("utf-8")).hexdigest()


def _task(row):
    for name in TASKS[:-1]:
        if name in row.get("motion_tags", ()):
            return name
    return "other"


def build_training_specs(layout, split, config):
    """Select metadata-only windows; no motion arrays or model outcomes are read."""
    training = {int(value) for value in split["training_subjects"]}
    development = {int(value) for value in split["development_subjects"]}
    if training & development:
        raise ValueError("Subject split overlaps")
    seed = int(config["seed"])
    maximum = int(config["maximum_windows_per_gap"])
    per_clip = int(config["candidate_starts_per_clip_gap"])
    specs = []
    for gap in config["gaps"]:
        candidates = []
        for index, row in enumerate(layout["entries"]):
            if row["subject"] not in training or row["frames"] < gap + 3:
                continue
            available = row["frames"] - gap - 2
            count = min(per_clip, available)
            starts = set()
            attempt = 0
            while len(starts) < count:
                value = int(_digest(seed, row["clip"], gap, attempt)[:16], 16)
                starts.add(1 + value % available)
                attempt += 1
            for start in sorted(starts):
                candidates.append(
                    {
                        "clip_index": index,
                        "clip": row["clip"],
                        "subject": row["subject"],
                        "task": _task(row),
                        "start": start,
                        "end": start + gap,
                        "gap": gap,
                        "context": True,
                        "selection_hash": _digest(seed, row["clip"], gap, start),
                    }
                )
        groups = defaultdict(list)
        for item in candidates:
            groups[item["task"]].append(item)
        for values in groups.values():
            values.sort(key=lambda item: item["selection_hash"])
        selected = []
        task_order = sorted(groups, key=lambda name: _digest(seed, gap, name))
        position = defaultdict(int)
        while len(selected) < min(maximum, len(candidates)):
            changed = False
            for task in task_order:
                values = groups[task]
                cursor = position[task]
                if cursor >= len(values):
                    continue
                item = values[cursor]
                position[task] += 1
                item["mask_pattern"] = MASK_PATTERNS[
                    sum(existing["task"] == task for existing in selected) % len(MASK_PATTERNS)
                ]
                selected.append(item)
                changed = True
                if len(selected) == maximum:
                    break
            if not changed:
                break
        specs.extend(selected)
    specs.sort(key=lambda item: (item["gap"], item["selection_hash"]))
    return specs


def flatten_development_specs(layout, split):
    """Flatten the already-frozen development task windows without reading poses."""
    development = {int(value) for value in split["development_subjects"]}
    by_clip = {row["clip"]: index for index, row in enumerate(layout["entries"])}
    result = []
    for task, by_gap in split["task_windows"].items():
        for gap_text, values in by_gap.items():
            for item in values:
                if item["subject"] not in development:
                    raise ValueError("Development window contains a non-development subject")
                result.append(
                    {
                        "clip_index": by_clip[item["clip"]],
                        "clip": item["clip"],
                        "subject": item["subject"],
                        "task": task,
                        "start": item["start"],
                        "end": item["end"],
                        "gap": int(gap_text),
                        "context": bool(item["context"]),
                        "mask_pattern": item["sparse_mask"],
                        "task_source": item["task_source"],
                    }
                )
    return result


class HierarchySequenceDataset:
    """Read examples lazily from the qualified memory-mapped hierarchy store."""

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
        result = conditioned_window(
            self.store.clip(spec["clip_index"]),
            row,
            spec["start"],
            spec["end"],
            context=spec["context"],
            mask_pattern=spec["mask_pattern"],
            contact_thresholds=self.contact_thresholds,
            include_weak_training_contacts=self.weak_contacts,
        )
        example = model_window_example(result)
        condition = result["conditioning"]
        example["offsets"] = np.asarray(result["window"]["offsets"], dtype=np.float32)
        example["contact_weight"] = (
            condition.contact_probability[:, :2] * condition.contact_confidence[:, :2]
        ).astype(np.float32)
        example["semantic"] = np.asarray(self.store.semantic, dtype=np.int64)
        example["parents"] = np.asarray(self.store.parents, dtype=np.int64)
        example["dt"] = np.float32(self.store.clip(spec["clip_index"]).dt)
        example["metadata"] = dict(spec)
        return example


def load_specs(root=None):
    root = Path(root or Path(__file__).resolve().parent)
    value = json.loads((root / "results/full-hierarchy-sequence-specs-v1/specs.json").read_text())
    return value["training"], value["development"]
