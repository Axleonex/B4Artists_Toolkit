"""Contracts for the train-only full-hierarchy motion store."""
from pathlib import Path
import hashlib
import json
import sys
import time

import numpy as np


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "results/full-hierarchy-store-contract-v1"
sys.path.insert(0, str(ROOT))

from full_hierarchy_store_v1 import FullHierarchyStore, HierarchyClip, _angular_velocity
from sequence_kinematics import forward
from sequence_store_v1 import SequenceStore


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def transformed(clip, *, translation=None, scale=1.0, quaternion_signs=None):
    roots = np.asarray(clip.root_positions, dtype=np.float64) * scale
    if translation is not None:
        roots = roots + np.asarray(translation, dtype=np.float64)
    quaternions = np.asarray(clip.local_quaternions, dtype=np.float64).copy()
    if quaternion_signs is not None:
        quaternions *= np.asarray(quaternion_signs, dtype=np.float64)[:, None, None]
    return HierarchyClip(
        roots,
        quaternions,
        np.asarray(clip.offsets),
        np.asarray(clip.reference),
        np.asarray(clip.rest_pelvis_rotation),
        clip.scale * scale,
        clip.dt,
        clip.names,
        clip.parents,
        clip.semantic,
    )


def main():
    OUT.mkdir(exist_ok=False)
    started = time.perf_counter()
    store = FullHierarchyStore(verify_hashes=True)
    semantic_store = SequenceStore(cache_clips=2)
    assert len(store.entries) == len(semantic_store.entries) == 1840
    assert len({row["subject"] for row in store.entries}) == 85
    assert store.report["full_hierarchy_reconstructs_semantics"]
    assert store.report["sign_continuous_quaternions"]
    patterns = ("endpoints", "upper_mid", "foot_contacts", "extremity_mid")
    max_position_error = 0.0
    max_rotation_error = 0.0
    max_invariance_error = 0.0
    max_velocity_sign_error = 0.0
    checked = []
    subjects = sorted({row["subject"] for row in store.entries})
    for case, subject in enumerate(subjects):
        candidates = [
            (index, row)
            for index, row in enumerate(store.entries)
            if row["subject"] == subject and row["frames"] >= 35
        ]
        index, row = min(candidates, key=lambda pair: pair[1]["frames"])
        clip = store.clip(index)
        old = semantic_store.clip(index)
        gap = 32
        start = max(1, min(len(clip.root_positions) // 2 - gap // 2, len(clip.root_positions) - gap - 2))
        end = start + gap
        pattern = patterns[case % len(patterns)]
        window = clip.normalized_window(start, end, context=True, mask_pattern=pattern)
        positions, rotations, _ = forward(window["state"], window["offsets"], clip.parents)
        expected_positions = (
            np.asarray(old.positions[window["indices"]], dtype=np.float64) - window["origin"]
        ) @ window["basis"] / clip.scale
        expected_rotations = np.einsum(
            "ij,fkjl->fkil",
            window["basis"].T,
            np.asarray(old.rotations[window["indices"]], dtype=np.float64),
        )
        position_error = float(np.max(np.abs(positions[:, clip.semantic] - expected_positions)))
        rotation_error = float(np.max(np.abs(rotations[:, clip.semantic] - expected_rotations)))
        max_position_error = max(max_position_error, position_error)
        max_rotation_error = max(max_rotation_error, rotation_error)
        assert window["state"].shape == (gap + 3, 3 + 6 * 23)
        assert window["root_velocity"].shape == (gap + 3, 3)
        assert window["angular_velocity"].shape == (gap + 3, 23, 3)
        assert np.allclose(window["basis"].T @ window["basis"], np.eye(3), atol=1e-6)
        masks = window["masks"]
        assert masks["root"].shape == (gap + 1, 3)
        assert masks["rotation"].shape == (gap + 1, 23, 6)
        assert masks["root"][0].all() and masks["root"][-1].all()
        assert masks["rotation"][0, clip.semantic].all() and masks["rotation"][-1, clip.semantic].all()
        helpers = sorted(set(range(23)) - set(clip.semantic))
        assert not masks["rotation"][:, helpers].any()

        moved = transformed(clip, translation=(1000, -500, 200), scale=2.5)
        moved_window = moved.normalized_window(start, end, context=True, mask_pattern=pattern)
        invariance_error = float(np.max(np.abs(moved_window["state"] - window["state"])))
        max_invariance_error = max(max_invariance_error, invariance_error)
        signs = np.where(np.arange(len(clip.local_quaternions)) % 2, -1.0, 1.0)
        signed = transformed(clip, quaternion_signs=signs)
        signed_window = signed.normalized_window(start, end, context=True, mask_pattern=pattern)
        max_velocity_sign_error = max(
            max_velocity_sign_error,
            float(np.max(np.abs(signed_window["angular_velocity"] - window["angular_velocity"]))),
        )
        assert np.array_equal(signed_window["masks"]["root"], masks["root"])
        assert np.array_equal(signed_window["masks"]["rotation"], masks["rotation"])
        checked.append({"clip": row["clip"], "subject": subject, "pattern": pattern})

    identity = np.zeros((5, 23, 4), dtype=np.float64)
    identity[..., 0] = 1
    assert np.array_equal(_angular_velocity(identity, 1 / 30), np.zeros((5, 23, 3)))
    invalid = 0
    clip = store.clip(0)
    for action in (
        lambda: store.clip(-1),
        lambda: clip.normalized_window(0, len(clip.root_positions), context=False),
        lambda: clip.normalized_window(0, 8, context=True),
        lambda: clip.normalized_window(1, 8, mask_pattern="unknown"),
        lambda: _angular_velocity(identity[:1], 1 / 30),
        lambda: _angular_velocity(identity, 0),
    ):
        try:
            action()
        except ValueError:
            invalid += 1
    assert invalid == 6
    assert max_position_error < 2e-5
    assert max_rotation_error < 2e-6
    assert max_invariance_error < 2e-5
    assert max_velocity_sign_error < 1e-10
    report = {
        "complete": True,
        "clips": len(store.entries),
        "subjects": len(subjects),
        "representative_subject_windows": len(checked),
        "patterns": list(patterns),
        "maximum_semantic_position_roundtrip_error": max_position_error,
        "maximum_semantic_rotation_roundtrip_error": max_rotation_error,
        "maximum_translation_scale_invariance_error": max_invariance_error,
        "maximum_quaternion_sign_velocity_error": max_velocity_sign_error,
        "helper_joints_never_authored": True,
        "endpoint_semantic_controls_authored": True,
        "velocities_derived": True,
        "memory_mapped": True,
        "invalid_cases": invalid,
        "checked": checked,
        "seconds": time.perf_counter() - started,
        "sources": {
            "script": sha256(Path(__file__)),
            "module": sha256(ROOT / "full_hierarchy_store_v1.py"),
            "store_report": sha256(ROOT / "results/full-hierarchy-store-v1/report.json"),
            "store_layout": sha256(ROOT / "results/full-hierarchy-store-v1/layout.json"),
        },
        "validation_read": False,
        "confirmation_read": False,
        "training_run": False,
        "runtime_promoted": False,
        "full_goal_complete": False,
    }
    (OUT / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in (
        "complete", "clips", "subjects", "representative_subject_windows",
        "maximum_semantic_position_roundtrip_error", "maximum_semantic_rotation_roundtrip_error",
        "maximum_translation_scale_invariance_error", "maximum_quaternion_sign_velocity_error",
        "helper_joints_never_authored", "invalid_cases", "seconds"
    )}, indent=2))


if __name__ == "__main__":
    main()
