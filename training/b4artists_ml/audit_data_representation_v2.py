"""Train-only coverage, contact-label and full-hierarchy representation audit.

SPDX-License-Identifier: GPL-2.0-or-later
This script reads the already acquired CMU train corpus. It does not download data,
read development/confirmation motion, or fit a model.
"""
from collections import Counter
from pathlib import Path
import hashlib
import json
import sys
import time


HERE = Path(__file__).resolve()
TR = HERE.parent
sys.path.insert(0, str(TR))

import numpy as np

from bvh_data import parse_bvh
from sequence_data import full_motion, known_window, semantic_output, target_window
from sequence_store_v1 import SequenceStore


PLAN_PATH = TR / "data_representation_audit_plan_v1.json"
BASE = TR / "results/data-representation-audit-v1"
FOOT_INDICES = (13, 16)
CATEGORIES = {
    "walk": ("walk", "march", "sneak", "stroll"),
    "run": ("run", "jog", "sprint"),
    "jump": ("jump", "leap", "hop", "jete", "flip", "vault"),
    "explicit_landing_label": ("land", "landing"),
    "turn": ("turn", "spin", "pirouette"),
    "crouch_or_duck": ("crouch", "duck", "squat", "bend"),
    "reach_or_object_handling": ("reach", "pick", "grab", "place", "lift", "carry", "throw", "catch", "push", "pull"),
    "recovery": ("get up", "stand up", "rise", "fall"),
    "interaction": ("partner", "hug", "shake hand", "conversation", "pass object", "two subject"),
    "dance_or_named_style": ("dance", "stylized", "clumsy", "relaxed", "drunk", "silly", "angry", "sad", "happy"),
    "combat_or_sport": ("punch", "kick", "sword", "basketball", "football", "boxing", "sport", "golf", "baseball"),
    "idle_or_gesture": ("idle", "gesture", "story", "talk", "wave", "signal"),
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def write(path, data):
    path.write_text(json.dumps(data, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def clip_seconds(row):
    return row["frames"] * row["dt"]


def coverage(entries):
    result = {}
    for name, terms in CATEGORIES.items():
        rows = [row for row in entries if any(term in row["description"].lower() for term in terms)]
        result[name] = {
            "clips": len(rows),
            "subjects": len({row["subject"] for row in rows}),
            "hours": sum(map(clip_seconds, rows)) / 3600,
        }
    return result


def contact_audit(store, plan):
    primary = plan["contact_pseudo_label"]["primary_thresholds"]
    sensitivity_thresholds = plan["contact_pseudo_label"]["sensitivity_thresholds"]
    threshold_pairs = [primary, *sensitivity_thresholds]
    floor_percentile = plan["contact_pseudo_label"]["clip_floor_percentile"]
    aggregates = [
        {"contact_frames": 0, "double_frames": 0, "transitions": 0, "fractions": []}
        for _ in threshold_pairs
    ]
    total_frames = 0
    per_clip = []
    for index, row in enumerate(store.entries):
        start = row["offset"]
        end = start + row["frames"]
        positions = np.asarray(store.positions[start:end], dtype=np.float64)
        rest = np.asarray(store.rest_positions[index], dtype=np.float64)
        left = rest[11] - rest[14]
        up = (rest[5] + rest[8] - rest[11] - rest[14]) * 0.5
        scale = float(np.linalg.norm(up))
        left /= np.linalg.norm(left)
        up -= left * np.dot(up, left)
        up /= np.linalg.norm(up)
        forward = np.cross(up, left)
        reference = np.stack((left, forward, up), axis=1)
        feet = positions[:, FOOT_INDICES]
        local = np.einsum("tji,ik->tjk", feet, reference) / scale
        height = local[..., 2]
        floor = float(np.percentile(height, floor_percentile))
        velocity = np.empty_like(local)
        velocity[1:] = (local[1:] - local[:-1]) / row["dt"]
        velocity[0] = velocity[1] if len(velocity) > 1 else 0
        speed = np.linalg.norm(velocity, axis=-1)
        frames = len(local)
        total_frames += frames * 2
        primary_contact = None
        for aggregate, thresholds in zip(aggregates, threshold_pairs):
            contact = (
                speed <= thresholds["maximum_speed_body_heights_per_second"]
            ) & (
                height
                <= floor + thresholds["maximum_height_above_clip_floor_body_heights"]
            )
            change = np.count_nonzero(contact[1:] != contact[:-1]) if len(contact) > 1 else 0
            aggregate["contact_frames"] += int(contact.sum())
            aggregate["double_frames"] += int(np.all(contact, axis=1).sum())
            aggregate["transitions"] += int(change)
            aggregate["fractions"].append(float(contact.mean()))
            if thresholds is primary:
                primary_contact = contact
        per_clip.append(
            {
                "clip": row["clip"],
                "subject": row["subject"],
                "frames": frames,
                "contact_fraction": float(primary_contact.mean()),
                "double_support_fraction": float(np.all(primary_contact, axis=1).mean()),
                "floor": floor,
            }
        )

    def summarize(thresholds, aggregate):
        fractions = np.asarray(aggregate["fractions"])
        return {
            "thresholds": thresholds,
            "contact_fraction": aggregate["contact_frames"] / total_frames,
            "double_support_fraction": aggregate["double_frames"] / (total_frames / 2),
            "transitions": aggregate["transitions"],
            "clip_contact_fraction_p05": float(np.percentile(fractions, 5)),
            "clip_contact_fraction_p50": float(np.percentile(fractions, 50)),
            "clip_contact_fraction_p95": float(np.percentile(fractions, 95)),
            "zero_contact_clips": int(np.count_nonzero(fractions == 0)),
            "all_contact_clips": int(np.count_nonzero(fractions == 1)),
        }

    primary_summary = summarize(primary, aggregates[0])
    return {
        "method": "Heuristic pseudo-label only: per-clip low foot height plus low foot speed; no force plate, scene geometry, toe marker or animator verification.",
        "clips": len(per_clip),
        "foot_frames": total_frames,
        **primary_summary,
        "sensitivity": [
            summarize(thresholds, aggregate)
            for thresholds, aggregate in zip(threshold_pairs[1:], aggregates[1:])
        ],
        "ground_truth": False,
        "suitable_as_unreviewed_hard_constraint": False,
    }


def hierarchy_audit(store, manifest, plan):
    source_by_clip = {row["clip"]: row for row in manifest["files"]}
    selected = []
    for subject in store.subjects:
        candidates = [store.entries[index] for index in store.by_subject[subject]]
        candidates = [row for row in candidates if row["frames"] >= plan["hierarchy"]["gap"] + 3]
        row = min(candidates, key=lambda item: source_by_clip[item["clip"]]["bytes"])
        selected.append(row)
    topologies = Counter()
    maximum_position_error = 0.0
    maximum_rotation6_error = 0.0
    maximum_true_edge_error = 0.0
    failures = []
    for row in selected:
        source = TR / row["source_path"]
        try:
            motion = full_motion(parse_bvh(source.read_text()), plan["hierarchy"]["fps"])
            topology = json.dumps(
                {"names": motion.names, "parents": motion.parents, "semantic": motion.semantic},
                separators=(",", ":"),
            )
            topologies[hashlib.sha256(topology.encode()).hexdigest()] += 1
            gap = plan["hierarchy"]["gap"]
            start = max(1, min(len(motion.semantic_motion.points) // 2 - gap // 2, len(motion.semantic_motion.points) - gap - 2))
            indices = np.arange(start, start + gap + 1)
            t = np.arange(gap + 1, dtype=np.float64) / gap
            known = known_window(motion, start, start + gap, t, True)
            target_local, target_semantic = target_window(
                motion, indices, known["origin"], known["basis"]
            )
            skeleton = (motion.names, motion.parents, motion.semantic)
            reconstructed = semantic_output(target_local, motion.offsets, skeleton)
            shaped_actual = target_semantic.reshape(len(indices), 17, 9)
            shaped_reconstructed = reconstructed.reshape(len(indices), 17, 9)
            maximum_position_error = max(
                maximum_position_error,
                float(np.max(np.abs(shaped_actual[..., :3] - shaped_reconstructed[..., :3]))),
            )
            maximum_rotation6_error = max(
                maximum_rotation6_error,
                float(np.max(np.abs(shaped_actual[..., 3:] - shaped_reconstructed[..., 3:]))),
            )
            points, _, _ = __import__("sequence_kinematics").forward(
                target_local, motion.offsets, motion.parents
            )
            parents = np.asarray(motion.parents[1:])
            edge = np.linalg.norm(points[:, 1:] - points[:, parents], axis=-1)
            expected = np.linalg.norm(motion.offsets[1:], axis=-1)
            maximum_true_edge_error = max(
                maximum_true_edge_error,
                float(np.max(np.abs(edge - expected))),
            )
        except Exception as exc:
            failures.append({"clip": row["clip"], "subject": row["subject"], "error": repr(exc)})
    return {
        "selection": "Smallest eligible train-only clip per subject; no development or confirmation motion.",
        "subjects_checked": len(selected),
        "clips_checked": len(selected),
        "unique_topologies": len(topologies),
        "topology_counts": dict(topologies),
        "failures": failures,
        "maximum_semantic_position_reconstruction_error": maximum_position_error,
        "maximum_semantic_rotation6_reconstruction_error": maximum_rotation6_error,
        "maximum_true_edge_length_error": maximum_true_edge_error,
        "full_hierarchy_reconstructs_semantics": not failures
        and maximum_position_error < 1e-5
        and maximum_rotation6_error < 1e-5
        and maximum_true_edge_error < 1e-6,
    }


def main():
    started = time.perf_counter()
    plan = read(PLAN_PATH)
    assert plan["validation_read"] is False and plan["confirmation_read"] is False
    store = SequenceStore(cache_clips=2)
    manifest_path = TR / "results/cmu-corpus-inventory-v1/train-download-manifest.json"
    manifest = read(manifest_path)
    assert manifest["complete"] and not manifest["development_motion_downloaded"]
    assert not manifest["confirmation_motion_downloaded"]
    assert len(store.entries) == 1840 and len(store.subjects) == 85
    BASE.mkdir(exist_ok=False)
    report = {
        "complete": True,
        "scope": "Existing train-only CMU corpus; metadata coverage, heuristic foot-contact feasibility and full-hierarchy reconstruction. No model fit.",
        "clips": len(store.entries),
        "subjects": len(store.subjects),
        "frames": store.layout["frames"],
        "source_hours": store.report["source_hours"],
        "metadata_coverage": coverage(store.entries),
        "style_tag_counts": dict(Counter(tag for row in store.entries for tag in row["style_tags"])),
        "other_only_or_unclassified_clips": sum(row["style_tags"] == ["other"] for row in store.entries),
        "contact_pseudo_label": contact_audit(store, plan),
        "full_hierarchy": hierarchy_audit(store, manifest, plan),
        "representation_decision": {
            "current_17_joint_world_pose": "Retain as the rig-neutral semantic constraint and evaluation layer, not the sole generative state.",
            "canonical_full_hierarchy": "Use root translation plus ancestor-local rotations and fixed per-character offsets for learned generation; this structurally prevents source-edge stretching.",
            "rig_adaptation": "Map BoneForge/Rigify/imported chains to versioned canonical roles with explicit virtual/intermediate joints, then validate the semantic controls on the original rig.",
            "contact": "Add foot/hand contact probabilities and scene/support context. Existing height/speed labels are weak pseudo-labels and require calibration or animator review.",
            "intent_style": "Use explicit motion class/style conditioning. Coarse CMU tags are insufficient; 100STYLE is a candidate style supplement pending a separately approved download and topology adapter.",
        },
        "data_decision": plan["data_candidates"],
        "validation_read": False,
        "confirmation_read": False,
        "downloads": [],
        "training_run": False,
        "runtime_promoted": False,
        "full_goal_complete": False,
        "seconds": time.perf_counter() - started,
        "sources": {
            "script": sha(HERE),
            "plan": sha(PLAN_PATH),
            "sequence_store_report": sha(TR / "results/cmu-sequence-store-v2/report.json"),
            "sequence_store_layout": sha(TR / "results/cmu-sequence-store-v2/layout.json"),
            "train_manifest": sha(manifest_path),
        },
    }
    write(BASE / "report.json", report)
    print(json.dumps({
        "complete": report["complete"],
        "clips": report["clips"],
        "subjects": report["subjects"],
        "contact_fraction": report["contact_pseudo_label"]["contact_fraction"],
        "hierarchy": report["full_hierarchy"],
        "seconds": report["seconds"],
    }))


if __name__ == "__main__":
    main()
