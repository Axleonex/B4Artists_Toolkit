"""Encode the train-only CMU corpus as a complete local-joint hierarchy.

SPDX-License-Identifier: GPL-2.0-or-later
Large numeric arrays remain in the Git-ignored research cache.
"""
from collections import Counter
from pathlib import Path
import hashlib
import json
import sys
import time

import numpy as np


ROOT = Path(__file__).resolve().parent
HERE = Path(__file__).resolve()
PLAN_PATH = ROOT / "full_hierarchy_store_plan_v1.json"
SOURCE_MANIFEST = ROOT / "results/cmu-corpus-inventory-v1/train-download-manifest.json"
SOURCE_LAYOUT = ROOT / "results/cmu-sequence-store-v2/layout.json"
OUT = ROOT / "results/full-hierarchy-store-v1"
STORE = (ROOT / "cache-expanded-v1/full-hierarchy-store-v1").resolve()

MOTION_TAGS = {
    "walk": ("walk", "march", "stroll", "sneak"),
    "run": ("run", "jog", "sprint"),
    "jump": ("jump", "leap", "hop", "jete", "vault"),
    "landing": ("land", "landing"),
    "turn": ("turn", "spin", "pirouette"),
    "crouch": ("crouch", "duck", "squat", "bend"),
    "reach_or_object": ("reach", "pick", "grab", "place", "lift", "carry", "throw", "catch", "push", "pull"),
    "recovery": ("get up", "stand up", "rise", "fall"),
    "interaction": ("partner", "hug", "shake hand", "conversation", "pass object", "two subject"),
    "aerial": ("flip", "cartwheel", "handspring", "somersault", "dive"),
    "combat": ("punch", "kick", "sword", "boxing", "fight"),
    "dance": ("dance", "ballet", "salsa", "pirouette", "jete"),
    "gesture": ("gesture", "story", "talk", "wave", "signal"),
}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, data):
    path.write_text(json.dumps(data, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def weak_motion_tags(description, style_tags):
    text = description.lower()
    tags = [name for name, terms in MOTION_TAGS.items() if any(term in text for term in terms)]
    tags.extend(tag for tag in style_tags if tag != "other" and tag not in tags)
    return tags or ["other"]


def sign_continuous(quaternions):
    q = np.asarray(quaternions, dtype=np.float64).copy()
    if len(q) > 1:
        relation = np.where(np.sum(q[1:] * q[:-1], axis=-1) < 0, -1.0, 1.0)
        signs = np.concatenate((np.ones((1, q.shape[1])), np.cumprod(relation, axis=0)), axis=0)
        q *= signs[..., None]
    return q


def encode(source, target_fps, semantic_names):
    points, world = source.transforms()
    semantic_source = [source.names.index(name) for name in semantic_names]
    retained = set()
    for source_id in semantic_source:
        while source_id >= 0:
            retained.add(source_id)
            source_id = source.parents[source_id]
    retained = sorted(retained)
    lookup = {old: new for new, old in enumerate(retained)}
    for source_id in retained[1:]:
        if any(channel.endswith("position") for channel in source.channels[source_id]):
            raise ValueError("Animated non-root translation is unsupported")
    names = tuple(source.names[source_id] for source_id in retained)
    parents = tuple(
        -1 if source.parents[source_id] < 0 else lookup[source.parents[source_id]]
        for source_id in retained
    )
    semantic = tuple(lookup[source_id] for source_id in semantic_source)
    rest = points[0, semantic_source]
    left = rest[11] - rest[14]
    up = (rest[5] + rest[8] - rest[11] - rest[14]) * 0.5
    scale = float(np.linalg.norm(up))
    width = float(np.linalg.norm(left))
    if not np.isfinite([scale, width]).all() or min(scale, width) < 1e-8:
        raise ValueError("Invalid rest reference")
    left /= width
    up -= left * np.dot(up, left)
    up /= np.linalg.norm(up)
    reference = np.stack((left, np.cross(up, left), up), axis=1)
    step = max(1, int(round(1 / (target_fps * source.frame_time))))
    frames = np.arange(1, len(points), step)
    retained_world = world[frames][:, retained]
    local = retained_world.copy()
    for joint, parent in enumerate(parents[1:], 1):
        local[:, joint] = np.swapaxes(retained_world[:, parent], -1, -2) @ retained_world[:, joint]
    return {
        "names": names,
        "parents": parents,
        "semantic": semantic,
        "root_positions": points[frames, semantic_source[0]],
        "semantic_positions": points[frames][:, semantic_source],
        "semantic_rotations": world[frames][:, semantic_source],
        "local_rotations": local,
        "offsets": source.offsets[retained] / scale,
        "reference": reference,
        "rest_pelvis_rotation": world[0, semantic_source[0]],
        "scale": scale,
        "frames": frames,
        "dt": source.frame_time * step,
    }


def main():
    sys.path.insert(0, str(ROOT))
    from bvh_data import parse_bvh
    from context_data import NAMES
    from sequence_kinematics import forward
    from temporal_data import quat_matrix, quaternion, rotation6

    plan = json.loads(PLAN_PATH.read_text())
    manifest = json.loads(SOURCE_MANIFEST.read_text())
    source_layout = json.loads(SOURCE_LAYOUT.read_text())
    assert sha256(HERE) == plan["script_sha256"]
    assert sha256(SOURCE_MANIFEST) == plan["source_manifest_sha256"]
    assert sha256(SOURCE_LAYOUT) == plan["source_layout_sha256"]
    assert all(sha256(ROOT / name) == digest for name, digest in plan["sources"].items())
    assert manifest["complete"] and manifest["file_count"] == plan["clips"]
    assert source_layout["clips"] == plan["clips"] and source_layout["frames"] == plan["frames"]
    assert not manifest["development_motion_downloaded"] and not manifest["confirmation_motion_downloaded"]
    OUT.mkdir(exist_ok=False)
    STORE.mkdir(parents=True, exist_ok=False)
    started = time.perf_counter()
    entries = []
    tag_counts = Counter()
    for source, item in zip(manifest["files"], source_layout["entries"]):
        assert source["clip"] == item["clip"] and source["sha256"] == item["source_sha256"]
        tags = weak_motion_tags(item["description"], item["style_tags"])
        tag_counts.update(tags)
        entries.append({**item, "motion_tags": tags, "motion_tag_source": "description_keyword_heuristic"})

    total_frames = source_layout["frames"]
    joints = plan["joints"]
    layout = {
        "schema": 1,
        "plan_sha256": sha256(PLAN_PATH),
        "clips": len(entries),
        "frames": total_frames,
        "joints": joints,
        "root_position_shape": [total_frames, 3],
        "local_quaternion_shape": [total_frames, joints, 4],
        "velocity_storage": "derived per requested window from root positions and sign-continuous local quaternions",
        "authored_mask_storage": "generated deterministically per requested window over semantic animator controls",
        "motion_tag_source": "weak description/style metadata; not ground-truth intent",
        "entries": entries,
    }
    roots = np.lib.format.open_memmap(
        STORE / "root_positions.npy", mode="w+", dtype=np.float32, shape=(total_frames, 3)
    )
    quaternions = np.lib.format.open_memmap(
        STORE / "local_quaternions.npy", mode="w+", dtype=np.float32, shape=(total_frames, joints, 4)
    )
    offsets = np.lib.format.open_memmap(
        STORE / "offsets.npy", mode="w+", dtype=np.float32, shape=(len(entries), joints, 3)
    )
    references = np.lib.format.open_memmap(
        STORE / "references.npy", mode="w+", dtype=np.float64, shape=(len(entries), 3, 3)
    )
    rest_pelvis = np.lib.format.open_memmap(
        STORE / "rest_pelvis_rotations.npy", mode="w+", dtype=np.float64, shape=(len(entries), 3, 3)
    )
    scales = np.lib.format.open_memmap(
        STORE / "scales.npy", mode="w+", dtype=np.float64, shape=(len(entries),)
    )
    arrays = (roots, quaternions, offsets, references, rest_pelvis, scales)
    source_bytes = 0
    topology = None
    max_position_error = 0.0
    max_rotation_error = 0.0
    max_edge_error = 0.0
    max_quaternion_norm_error = 0.0
    minimum_adjacent_quaternion_dot = 1.0
    for index, (source_row, item) in enumerate(zip(manifest["files"], entries)):
        path = ROOT / source_row["path"]
        raw = path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != source_row["sha256"]:
            raise ValueError("Source checksum changed: " + source_row["clip"])
        source_bytes += len(raw)
        encoded = encode(parse_bvh(raw.decode("ascii")), plan["target_fps"], NAMES)
        identity = (encoded["names"], encoded["parents"], encoded["semantic"])
        if topology is None:
            topology = identity
            layout.update(names=list(identity[0]), parents=list(identity[1]), semantic=list(identity[2]))
        elif identity != topology:
            raise ValueError("Unexpected retained topology: " + source_row["clip"])
        if len(encoded["frames"]) != item["frames"] or abs(encoded["dt"] - item["dt"]) > 1e-12:
            raise ValueError("Sampling layout mismatch: " + source_row["clip"])
        q = sign_continuous(quaternion(encoded["local_rotations"]))
        q32 = q.astype(np.float32)
        root32 = encoded["root_positions"].astype(np.float32)
        offsets32 = encoded["offsets"].astype(np.float32)
        matrices32 = quat_matrix(q32)
        normalized_root = (root32.astype(np.float64) - root32[:1]) / encoded["scale"]
        state = np.concatenate(
            (normalized_root, rotation6(matrices32).reshape(len(root32), -1)), axis=-1
        )
        reconstructed_positions, reconstructed_rotations, _ = forward(
            state, offsets32.astype(np.float64), encoded["parents"]
        )
        expected_positions = (
            encoded["semantic_positions"] - encoded["root_positions"][:1, None]
        ) / encoded["scale"]
        max_position_error = max(
            max_position_error,
            float(np.max(np.abs(reconstructed_positions[:, encoded["semantic"]] - expected_positions))),
        )
        max_rotation_error = max(
            max_rotation_error,
            float(np.max(np.abs(reconstructed_rotations[:, encoded["semantic"]] - encoded["semantic_rotations"]))),
        )
        parents = np.asarray(encoded["parents"][1:])
        edge = np.linalg.norm(reconstructed_positions[:, 1:] - reconstructed_positions[:, parents], axis=-1)
        expected_edge = np.linalg.norm(offsets32[1:], axis=-1)
        max_edge_error = max(max_edge_error, float(np.max(np.abs(edge - expected_edge))))
        max_quaternion_norm_error = max(
            max_quaternion_norm_error,
            float(np.max(np.abs(np.linalg.norm(q32, axis=-1) - 1))),
        )
        if len(q32) > 1:
            minimum_adjacent_quaternion_dot = min(
                minimum_adjacent_quaternion_dot,
                float(np.min(np.sum(q32[1:] * q32[:-1], axis=-1))),
            )
        start = item["offset"]
        end = start + item["frames"]
        roots[start:end] = root32
        quaternions[start:end] = q32
        offsets[index] = offsets32
        references[index] = encoded["reference"]
        rest_pelvis[index] = encoded["rest_pelvis_rotation"]
        scales[index] = encoded["scale"]
        if (index + 1) % 25 == 0:
            for array in arrays:
                array.flush()
            write(
                OUT / "progress.json",
                {
                    "complete": False,
                    "clips": index + 1,
                    "total_clips": len(entries),
                    "frames": end,
                    "total_frames": total_frames,
                    "source_bytes": source_bytes,
                    "seconds": time.perf_counter() - started,
                    "validation_read": False,
                    "confirmation_read": False,
                },
            )
    write(OUT / "layout.json", layout)
    for array in arrays:
        array.flush()
    del roots, quaternions, offsets, references, rest_pelvis, scales, arrays
    files = {}
    store_bytes = 0
    for name in (
        "root_positions.npy",
        "local_quaternions.npy",
        "offsets.npy",
        "references.npy",
        "rest_pelvis_rotations.npy",
        "scales.npy",
    ):
        path = STORE / name
        files[name] = {"bytes": path.stat().st_size, "sha256": sha256(path)}
        store_bytes += path.stat().st_size
    report = {
        "complete": True,
        "clips": len(entries),
        "subjects": len({item["subject"] for item in entries}),
        "frames": total_frames,
        "joints": joints,
        "source_hours": sum((item["source_frames"] - 1) * item["source_frame_time"] for item in entries) / 3600,
        "source_bytes": source_bytes,
        "store_bytes": store_bytes,
        "files": files,
        "layout_sha256": sha256(OUT / "layout.json"),
        "plan_sha256": sha256(PLAN_PATH),
        "source_manifest_sha256": sha256(SOURCE_MANIFEST),
        "source_layout_sha256": sha256(SOURCE_LAYOUT),
        "script_sha256": sha256(HERE),
        "motion_tag_counts": dict(tag_counts),
        "motion_tags_ground_truth": False,
        "maximum_stored_semantic_position_error": max_position_error,
        "maximum_stored_semantic_rotation_matrix_error": max_rotation_error,
        "maximum_stored_true_edge_error": max_edge_error,
        "maximum_stored_quaternion_norm_error": max_quaternion_norm_error,
        "minimum_adjacent_quaternion_dot": minimum_adjacent_quaternion_dot,
        "full_hierarchy_reconstructs_semantics": (
            max_position_error <= plan["quality"]["semantic_position_tolerance"]
            and max_rotation_error <= plan["quality"]["semantic_rotation_tolerance"]
            and max_edge_error <= plan["quality"]["true_edge_tolerance"]
        ),
        "sign_continuous_quaternions": minimum_adjacent_quaternion_dot >= -plan["quality"]["quaternion_dot_tolerance"],
        "memory_mappable": True,
        "velocities_derived_per_window": True,
        "authored_masks_derived_per_window": True,
        "validation_read": False,
        "confirmation_read": False,
        "downloads": [],
        "training_run": False,
        "raw_motion_bundled_with_addon": False,
        "store_bundled_with_addon": False,
        "runtime_promoted": False,
        "seconds": time.perf_counter() - started,
        "full_goal_complete": False,
    }
    if store_bytes > plan["storage"]["maximum_store_bytes"]:
        raise ValueError("Full-hierarchy store exceeds prospective byte limit")
    if not report["full_hierarchy_reconstructs_semantics"] or not report["sign_continuous_quaternions"]:
        raise ValueError("Full-hierarchy quality gate failed")
    write(OUT / "report.json", report)
    write(
        OUT / "progress.json",
        {
            "complete": True,
            "clips": len(entries),
            "frames": total_frames,
            "source_bytes": source_bytes,
            "store_bytes": store_bytes,
            "seconds": report["seconds"],
            "report_sha256": sha256(OUT / "report.json"),
            "validation_read": False,
            "confirmation_read": False,
        },
    )
    print(json.dumps({key: report[key] for key in (
        "complete", "clips", "subjects", "frames", "joints", "source_hours", "store_bytes",
        "maximum_stored_semantic_position_error", "maximum_stored_semantic_rotation_matrix_error",
        "maximum_stored_true_edge_error", "minimum_adjacent_quaternion_dot", "seconds"
    )}, indent=2))


if __name__ == "__main__":
    main()
