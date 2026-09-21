"""Synthetic contract checks for train-only weak motion-label proposals."""
from dataclasses import replace
from pathlib import Path
import json
import sys

import numpy as np


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from full_hierarchy_store_v1 import HierarchyClip
from motion_label_proposals_v1 import (
    HEURISTIC_CONFIDENCE_CEILING,
    _hysteresis,
    _runs,
    clip_proposals,
    contact_signals,
    event_proposals,
    normalized_kinematics,
)


def synthetic_clip(frames=40, dt=1 / 30):
    parents = (-1, 0, 0, 2, 3, 0, 5, 6, 7, 0, 9, 10, 11, 12, 13, 11, 15, 16, 17, 11, 19, 20, 21)
    offsets = np.zeros((23, 3), dtype=np.float64)
    offsets[2] = (-0.1, 0, -0.15)
    offsets[3] = (0, 0, -0.35)
    offsets[4] = (0, 0, -0.35)
    offsets[5] = (0.1, 0, 0)
    offsets[6] = (0, 0, -0.15)
    offsets[7] = (0, 0, -0.35)
    offsets[8] = (0, 0, -0.35)
    offsets[9] = (0, 0, 0.2)
    offsets[10] = (0, 0, 0.2)
    offsets[11] = (0, 0, 0.2)
    offsets[12] = (0, 0, 0.15)
    offsets[13] = (0, 0, 0.1)
    offsets[14] = (0, 0, 0.15)
    offsets[15] = (-0.1, 0, 0.1)
    offsets[16] = (-0.25, 0, 0)
    offsets[17] = (-0.25, 0, 0)
    offsets[18] = (-0.15, 0, 0)
    offsets[19] = (0.1, 0, 0.1)
    offsets[20] = (0.25, 0, 0)
    offsets[21] = (0.25, 0, 0)
    offsets[22] = (0.15, 0, 0)
    root = np.zeros((frames, 3), dtype=np.float64)
    root[:, 2] = 0.85
    q = np.zeros((frames, 23, 4), dtype=np.float64)
    q[..., 0] = 1
    return HierarchyClip(
        root,
        q,
        offsets,
        np.eye(3),
        np.eye(3),
        1.0,
        dt,
        tuple(f"j{i}" for i in range(23)),
        parents,
        (0, 10, 11, 13, 14, 16, 17, 18, 20, 21, 22, 2, 3, 4, 6, 7, 8),
    )


def main():
    plan = json.loads((ROOT / "motion_label_proposals_plan_v1.json").read_text())
    thresholds = plan["thresholds"]
    assert _runs([False, True, True, False, True]) == [(1, 2), (4, 4)]
    assert np.array_equal(
        _hysteresis(np.array([0.0, 0.7, 0.6, 0.4, 0.3, 0.8, 0.2]), 0.65, 0.35, 2),
        np.array([False, True, True, True, False, False, False]),
    )
    clip = synthetic_clip()
    kin = normalized_kinematics(clip)
    assert kin.positions.shape == (40, 23, 3)
    assert np.allclose(kin.positions[:, clip.semantic[13], 2], -0.85)
    assert np.allclose(kin.positions[:, clip.semantic[16], 2], -0.85)
    signals = contact_signals(kin, clip.semantic, thresholds["contact"])
    assert signals["foot_indices"] == (4, 8)
    assert signals["contact"].all()
    assert np.max(signals["confidence"]) <= HEURISTIC_CONFIDENCE_CEILING

    contact = np.ones((20, 2), dtype=bool)
    contact[5:11] = False
    velocity = np.zeros((20, 3), dtype=np.float64)
    velocity[3:7, 2] = 0.2
    velocity[9:13, 2] = -0.2
    events = event_proposals({"contact": contact}, velocity, thresholds["events"])
    assert [(item["kind"], item["frame"]) for item in events] == [("takeoff", 5), ("landing", 11)]
    assert max(item["confidence"] for item in events) <= HEURISTIC_CONFIDENCE_CEILING

    proposal = clip_proposals(clip, thresholds)
    assert proposal["scene_geometry_known"] is False
    assert proposal["hand_contacts_known"] is False
    assert proposal["ground_truth"] is False
    assert len(proposal["static"]) >= 1
    assert all(item["confidence"] <= HEURISTIC_CONFIDENCE_CEILING for item in proposal["contacts"])

    moved = replace(clip, root_positions=clip.root_positions * 2.5 + np.array((20.0, -5.0, 2.0)), scale=2.5)
    moved_kin = normalized_kinematics(moved)
    assert np.allclose(moved_kin.positions, kin.positions, atol=1e-12)

    invalid = 0
    actions = (
        lambda: _hysteresis(np.array([0.0, 1.0]), 0.3, 0.5, 1),
        lambda: contact_signals(kin, (0, 1), thresholds["contact"]),
        lambda: normalized_kinematics(replace(clip, scale=0.0)),
    )
    for action in actions:
        try:
            action()
        except ValueError:
            invalid += 1
    assert invalid == len(actions)
    print(json.dumps({"passed": True, "synthetic_cases": 8, "invalid_cases": invalid}, indent=2))


if __name__ == "__main__":
    main()
