"""Map full-hierarchy windows and weak train-only labels to conditioning v1.

SPDX-License-Identifier: GPL-2.0-or-later

Weak contact inputs are opt-in and target-derived.  Callers must restrict that
mode to training subjects; development and confirmation inputs must use
unknown or independently authored/measured contacts.
"""
from dataclasses import fields

import numpy as np

from motion_conditioning_v1 import (
    ACTIONS,
    EFFECTORS,
    PROVENANCE_CODE,
    STYLES,
    MotionConditioning,
    with_hierarchy_controls,
)
from motion_label_proposals_v1 import contact_signals, normalized_kinematics


STYLE_FROM_ACTION = {
    "walk": "locomotion",
    "run": "locomotion",
    "jump": "jump",
    "landing": "jump",
    "aerial": "acrobatics",
    "combat": "combat",
    "dance": "dance",
    "interaction": "interaction",
    "gesture": "gesture",
}


def _metadata_distribution(names, vocabulary, frames):
    selected = sorted({name for name in names if name in vocabulary and name != "other"})
    if not selected:
        selected = ["other"]
    value = np.zeros((frames, len(vocabulary)), dtype=np.float32)
    for name in selected:
        value[:, vocabulary.index(name)] = 1.0 / len(selected)
    return value


def _copy_fields(conditioning):
    return {item.name: np.array(getattr(conditioning, item.name), copy=True) for item in fields(conditioning)}


def weak_metadata_conditioning(frames, row):
    """Create only reproducible, low-confidence description/style conditioning."""
    if not isinstance(frames, int) or frames < 2:
        raise ValueError("At least two frames are required")
    motion_tags = tuple(row.get("motion_tags", ()))
    style_tags = tuple(row.get("style_tags", ()))
    inferred_styles = tuple(STYLE_FROM_ACTION[tag] for tag in motion_tags if tag in STYLE_FROM_ACTION)
    base = MotionConditioning.empty(frames)
    data = _copy_fields(base)
    data["action_weight"] = _metadata_distribution(motion_tags, ACTIONS, frames)
    data["action_known"][:] = True
    data["action_confidence"][:] = 0.5
    data["action_provenance"][:] = PROVENANCE_CODE["metadata"]
    data["style_weight"] = _metadata_distribution((*style_tags, *inferred_styles), STYLES, frames)
    data["style_known"][:] = True
    data["style_confidence"][:] = 0.5
    data["style_provenance"][:] = PROVENANCE_CODE["metadata"]
    return MotionConditioning(**data).validated()


def training_conditioning(clip, row, thresholds, *, include_weak_contacts):
    """Build full-clip conditioning; weak contacts require an explicit opt-in."""
    frames = len(clip.root_positions)
    result = weak_metadata_conditioning(frames, row)
    if not include_weak_contacts:
        return result
    signals = contact_signals(normalized_kinematics(clip), clip.semantic, thresholds)
    data = _copy_fields(result)
    data["contact_probability"][:, :2] = signals["probability"].astype(np.float32)
    data["contact_known"][:, :2] = True
    data["contact_confidence"][:, :2] = np.maximum(
        signals["confidence"], np.float64(1e-4)
    ).astype(np.float32)
    data["contact_provenance"][:, :2] = PROVENANCE_CODE["heuristic"]
    return MotionConditioning(**data).validated()


def conditioned_window(
    clip,
    row,
    start,
    end,
    *,
    context,
    mask_pattern,
    contact_thresholds,
    include_weak_training_contacts,
):
    """Return a hierarchy target/window and leak-resistant packed controls."""
    full = training_conditioning(
        clip,
        row,
        contact_thresholds,
        include_weak_contacts=include_weak_training_contacts,
    )
    window = clip.normalized_window(start, end, context=context, mask_pattern=mask_pattern)
    data = {
        item.name: np.asarray(getattr(full, item.name))[start : end + 1].copy()
        for item in fields(full)
    }
    core = MotionConditioning(**data).validated()
    controls = with_hierarchy_controls(core, window)
    packed, layout = controls.packed()
    if packed.shape != (end - start + 1, 483):
        raise ValueError("Unexpected packed conditioning width")
    return {"window": window, "conditioning": controls, "packed": packed, "layout": layout}


def assert_train_only_subject(row, training_subjects):
    """Fail closed before target-derived weak contact construction."""
    subject = int(row["subject"])
    if subject not in {int(value) for value in training_subjects}:
        raise ValueError("Weak target-derived contact conditioning is train-only")
    return subject
