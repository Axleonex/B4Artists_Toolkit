"""Audit skeleton topology provenance from the already-pinned BVH cache.

This derives reproducible skeleton fingerprints without changing the frozen
manifest, downloading data, training a model, or authorizing promotion.  A
topology fingerprint is evidence about the cached BVH skeleton, not a claim
that the source rig identity or a joint action/rig-disjoint split is solved.
"""

from __future__ import annotations

from collections import defaultdict
import hashlib
import json
import os
from pathlib import Path

from bvh_data import parse_bvh


ROOT = Path(os.environ.get(
    "B4ML_REPO",
    r"X:\Scripting Attempts\B4Artists_Tools\B4Artists_Anim_Tools_github"))
TRAINING = ROOT / "training" / "b4artists_ml"
MANIFEST = TRAINING / "data_manifest.json"
CACHE = TRAINING / "cache"
OUT = TRAINING / "results" / "cached-skeleton-provenance-v1.json"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def skeleton_fingerprint(motion) -> tuple[str, dict]:
    payload = {
        "names": motion.names,
        "parents": motion.parents,
        "offsets": motion.offsets.tolist(),
        "channels": motion.channels,
    }
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")
    return sha256_bytes(encoded), payload


def connected_components(rows: list[dict]) -> list[dict]:
    """Join action and skeleton nodes to expose joint-split feasibility."""
    parent: dict[str, str] = {}

    def find(node: str) -> str:
        parent.setdefault(node, node)
        while parent[node] != node:
            parent[node] = parent[parent[node]]
            node = parent[node]
        return node

    def union(left: str, right: str) -> None:
        left_root, right_root = find(left), find(right)
        if left_root != right_root:
            parent[right_root] = left_root

    for row in rows:
        union("action:" + row["action"], "skeleton:" + row["skeleton_sha256"])
    groups: dict[str, dict[str, set[str]]] = defaultdict(
        lambda: {"actions": set(), "skeletons": set()})
    for node in parent:
        root = find(node)
        kind, value = node.split(":", 1)
        groups[root]["actions" if kind == "action" else "skeletons"].add(value)
    return [
        {
            "actions": sorted(value["actions"]),
            "skeletons": sorted(value["skeletons"]),
        }
        for value in sorted(
            groups.values(),
            key=lambda item: (sorted(item["actions"]), sorted(item["skeletons"])),
        )
    ]


def main() -> dict:
    manifest_text = MANIFEST.read_text(encoding="utf-8")
    manifest = json.loads(manifest_text)
    rows: list[dict] = []
    failures: list[str] = []
    skeleton_payloads: dict[str, dict] = {}
    for item in manifest["files"]:
        clip = item["clip"]
        path = CACHE / (clip + ".bvh")
        if not path.is_file():
            failures.append(f"missing cache file: {clip}")
            continue
        data = path.read_bytes()
        file_sha256 = sha256_bytes(data)
        if file_sha256 != item["sha256"]:
            failures.append(f"manifest checksum mismatch: {clip}")
            continue
        motion = parse_bvh(data.decode("utf-8"))
        skeleton_sha256, payload = skeleton_fingerprint(motion)
        skeleton_payloads.setdefault(skeleton_sha256, payload)
        subject, action = clip.split("_", 1)
        rows.append({
            "clip": clip,
            "split": item["split"],
            "subject": subject,
            "action": action,
            "cache_file": str(path),
            "file_sha256": file_sha256,
            "skeleton_sha256": skeleton_sha256,
            "joint_count_including_end_sites": len(motion.names),
            "frame_time": motion.frame_time,
        })

    skeleton_groups: dict[str, dict[str, list[str]]] = {}
    for row in rows:
        group = skeleton_groups.setdefault(
            row["skeleton_sha256"],
            {"clips": [], "subjects": [], "splits": [], "actions": []},
        )
        for key in ("clips", "subjects", "splits", "actions"):
            value = row["clip"] if key == "clips" else row[key[:-1]] if key[:-1] in row else None
            if value is not None and value not in group[key]:
                group[key].append(value)
    for group in skeleton_groups.values():
        for key in group:
            group[key].sort()

    components = connected_components(rows) if not failures else []
    report = {
        "schema": "b4ml-cached-skeleton-provenance-v1",
        "status": (
            "CACHE_INTEGRITY_FAILURE"
            if failures
            else "DERIVED_SKELETON_IDENTITIES_FOUND_JOINT_SPLIT_UNQUALIFIED"
        ),
        "scope": (
            "Read-only topology fingerprints from the pinned local BVH cache; "
            "no manifest rewrite, download, training, or model promotion."
        ),
        "source_manifest": "training/b4artists_ml/data_manifest.json",
        "source_manifest_sha256": sha256_bytes(manifest_text.encode("utf-8")),
        "cache_root": str(CACHE),
        "row_count": len(rows),
        "cache_failures": failures,
        "skeleton_group_count": len(skeleton_groups),
        "skeleton_groups": dict(sorted(skeleton_groups.items())),
        "skeleton_payload_sha256_keys": sorted(skeleton_payloads),
        "action_skeleton_connected_components": components,
        "joint_action_skeleton_partition_feasible": len(components) > 1,
        "manifest_rig_identity_fields": sorted(
            field for field in manifest["files"][0]
            if any(token in field.lower() for token in ("rig", "skeleton", "source_rig"))
        ),
        "derived_identity_kind": "BVH hierarchy, parent, offset and channel topology SHA-256",
        "rig_identity_proven": False,
        "rig_disjoint_temporal_evaluation_qualified": False,
        "reviewed_contact_intent_available": False,
        "training_authorized": False,
        "model_promoted": False,
        "claim_boundary": {
            "skeleton_topology_provenance": not failures,
            "action_disjoint_temporal_evaluation_qualified": False,
            "rig_disjoint_temporal_evaluation_qualified": False,
            "learned_temporal_quality_verified": False,
            "full_goal_complete": False,
        },
        "rows": rows,
    }
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return report


if __name__ == "__main__":
    main()
