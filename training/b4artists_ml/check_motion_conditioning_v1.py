"""Contracts for the versioned motion-conditioning schema."""
from dataclasses import replace
from pathlib import Path
import hashlib
import json
import sys
import time

import numpy as np


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "results/motion-conditioning-contract-v1"
sys.path.insert(0, str(ROOT))

from full_hierarchy_store_v1 import FullHierarchyStore
from motion_conditioning_v1 import (
    ACTIONS, EFFECTORS, PROVENANCE, PROVENANCE_CODE, SCENE_PROBES, STYLES,
    MotionConditioning, with_hierarchy_controls,
)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    OUT.mkdir(exist_ok=False)
    started = time.perf_counter()
    frames = 9
    empty = MotionConditioning.empty(frames).validated()
    packed_empty, layout = empty.packed()
    assert packed_empty.shape == (frames, 483)
    assert not np.count_nonzero(packed_empty)
    assert sorted(layout.values()) == sorted(layout.values(), key=lambda row: row[0])
    assert layout["contact_probability"][0] == 0
    assert layout["trajectory_provenance_one_hot"][1] == packed_empty.shape[1]

    contact_known = np.zeros((frames, len(EFFECTORS)), bool)
    contact_known[:, 0] = True
    contact_probability = np.zeros_like(contact_known, dtype=np.float32)
    contact_probability[:, 0] = 1
    contact_confidence = contact_probability.copy()
    contact_provenance = np.zeros_like(contact_known, dtype=np.uint8)
    contact_provenance[:, 0] = PROVENANCE_CODE["authored"]
    support_known = contact_known.copy()
    support_point = np.zeros((frames, len(EFFECTORS), 3), np.float32)
    support_normal = np.zeros_like(support_point)
    support_normal[:, 0, 2] = 1
    support_velocity = np.zeros_like(support_point)
    scene_known = np.zeros((frames, len(SCENE_PROBES)), bool)
    scene_known[:, 0] = True
    scene_normal = np.zeros((frames, len(SCENE_PROBES), 3), np.float32)
    scene_normal[:, 0, 2] = 1
    scene_distance = np.zeros((frames, len(SCENE_PROBES)), np.float32)
    scene_confidence = np.zeros_like(scene_distance)
    scene_confidence[:, 0] = 0.9
    scene_provenance = np.zeros_like(scene_known, dtype=np.uint8)
    scene_provenance[:, 0] = PROVENANCE_CODE["measured"]
    action_known = np.ones(frames, bool)
    action_weight = np.zeros((frames, len(ACTIONS)), np.float32)
    action_weight[:, ACTIONS.index("walk")] = 1
    action_confidence = np.full(frames, 0.4, np.float32)
    action_provenance = np.full(frames, PROVENANCE_CODE["metadata"], np.uint8)
    style_known = np.ones(frames, bool)
    style_weight = np.zeros((frames, len(STYLES)), np.float32)
    style_weight[:, STYLES.index("locomotion")] = 1
    style_confidence = np.full(frames, 0.4, np.float32)
    style_provenance = np.full(frames, PROVENANCE_CODE["metadata"], np.uint8)
    trajectory_known = np.ones(frames, bool)
    desired_velocity = np.zeros((frames, 3), np.float32)
    desired_velocity[:, 1] = 1
    desired_facing = desired_velocity.copy()
    trajectory_confidence = np.ones(frames, np.float32)
    trajectory_provenance = np.full(frames, PROVENANCE_CODE["authored"], np.uint8)
    known = replace(
        empty,
        contact_probability=contact_probability,
        contact_known=contact_known,
        contact_confidence=contact_confidence,
        contact_provenance=contact_provenance,
        support_point=support_point,
        support_normal=support_normal,
        support_velocity=support_velocity,
        support_known=support_known,
        scene_signed_distance=scene_distance,
        scene_normal=scene_normal,
        scene_known=scene_known,
        scene_confidence=scene_confidence,
        scene_provenance=scene_provenance,
        action_weight=action_weight,
        action_known=action_known,
        action_confidence=action_confidence,
        action_provenance=action_provenance,
        style_weight=style_weight,
        style_known=style_known,
        style_confidence=style_confidence,
        style_provenance=style_provenance,
        desired_root_velocity=desired_velocity,
        desired_facing=desired_facing,
        trajectory_known=trajectory_known,
        trajectory_confidence=trajectory_confidence,
        trajectory_provenance=trajectory_provenance,
    ).validated()
    packed_known, known_layout = known.packed()
    assert packed_known.shape == packed_empty.shape and known_layout == layout
    assert np.isfinite(packed_known).all() and np.count_nonzero(packed_known) > 0

    store = FullHierarchyStore()
    clip = store.clip(0)
    window = clip.normalized_window(1, 9, context=True, mask_pattern="extremity_mid")
    controlled = with_hierarchy_controls(known, window)
    controlled_packed, _ = controlled.packed()
    assert controlled_packed.shape == packed_known.shape
    assert np.array_equal(controlled.authored_root_mask, window["masks"]["root"])
    assert np.array_equal(controlled.authored_rotation_mask, window["masks"]["rotation"])
    assert np.array_equal(
        controlled.authored_root[controlled.authored_root_mask],
        window["state"][1:-1, :3].astype(np.float32)[controlled.authored_root_mask],
    )
    rotation = window["state"][1:-1, 3:].reshape(frames, 23, 6)
    assert np.array_equal(
        controlled.authored_rotation6[controlled.authored_rotation_mask],
        rotation.astype(np.float32)[controlled.authored_rotation_mask],
    )
    helpers = sorted(set(range(23)) - set(clip.semantic))
    assert not controlled.authored_rotation_mask[:, helpers].any()

    invalid_cases = []

    def rejects(name, candidate):
        try:
            candidate.validated()
        except ValueError:
            invalid_cases.append(name)
        else:
            raise AssertionError("Accepted invalid conditioning: " + name)

    hidden_action = action_weight.copy()
    rejects("hidden_action_leak", replace(empty, action_weight=hidden_action))
    bad_probability = contact_probability.copy()
    bad_probability[0, 0] = 1.1
    rejects("contact_probability_range", replace(known, contact_probability=bad_probability))
    bad_confidence = contact_confidence.copy()
    bad_confidence[:, 0] = 0.36
    heuristic = contact_provenance.copy()
    heuristic[:, 0] = PROVENANCE_CODE["heuristic"]
    rejects("heuristic_overconfidence", replace(known, contact_confidence=bad_confidence, contact_provenance=heuristic))
    metadata_overconfidence = action_confidence.copy()
    metadata_overconfidence[0] = 0.51
    rejects("metadata_overconfidence", replace(known, action_confidence=metadata_overconfidence))
    bad_normal = support_normal.copy()
    bad_normal[:, 0, 2] = 2
    rejects("support_normal_unit", replace(known, support_normal=bad_normal))
    rejects("support_requires_contact", replace(empty, support_known=support_known, support_normal=support_normal))
    partial_mask = controlled.authored_rotation_mask.copy()
    partial_mask[1, clip.semantic[0], 0] = True
    rejects("partial_rotation_mask", replace(controlled, authored_rotation_mask=partial_mask))
    hidden_authored = controlled.authored_root.copy()
    hidden_authored[1, 0] = 1
    rejects("hidden_authored_leak", replace(controlled, authored_root=hidden_authored))
    rejects(
        "invalid_dimensions",
        replace(
            empty,
            authored_rotation6=np.zeros((frames, 22, 6), np.float32),
            authored_rotation_mask=np.zeros((frames, 22, 6), bool),
        ),
    )
    assert len(invalid_cases) == 9

    report = {
        "complete": True,
        "schema": 1,
        "frames": frames,
        "joints": 23,
        "effectors": list(EFFECTORS),
        "scene_probes": list(SCENE_PROBES),
        "actions": list(ACTIONS),
        "styles": list(STYLES),
        "provenance": list(PROVENANCE),
        "packed_features": packed_known.shape[1],
        "packed_layout": layout,
        "exact_authored_values": True,
        "helper_joints_never_authored": True,
        "unknown_values_zero_required": True,
        "heuristic_confidence_ceiling": 0.35,
        "metadata_confidence_ceiling": 0.5,
        "invalid_cases": invalid_cases,
        "seconds": time.perf_counter() - started,
        "sources": {
            "script": sha256(Path(__file__)),
            "schema_module": sha256(ROOT / "motion_conditioning_v1.py"),
            "hierarchy_module": sha256(ROOT / "full_hierarchy_store_v1.py"),
            "hierarchy_report": sha256(ROOT / "results/full-hierarchy-store-v1/report.json"),
        },
        "validation_read": False,
        "confirmation_read": False,
        "training_run": False,
        "runtime_promoted": False,
        "full_goal_complete": False,
    }
    (OUT / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in (
        "complete", "frames", "joints", "packed_features", "exact_authored_values",
        "helper_joints_never_authored", "unknown_values_zero_required", "invalid_cases", "seconds"
    )}, indent=2))


if __name__ == "__main__":
    main()
