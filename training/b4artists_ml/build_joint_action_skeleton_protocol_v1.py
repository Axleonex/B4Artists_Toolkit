"""Build a proposal-only joint action/skeleton-disjoint protocol.

The pinned corpus is small and its action/skeleton graph may be connected.
This audit searches for the highest-coverage action-group removal that leaves
at least three connected components.  It never rewrites the manifest, changes
source splits, authorizes training, or promotes a model.  A proposal is not a
qualified temporal evaluation: reviewed contact/intent labels, rig identity,
and adequate cohort size must still be established separately.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import os
from collections import defaultdict
from pathlib import Path


ROOT = Path(os.environ.get(
    "B4ML_REPO",
    r"X:\Scripting Attempts\B4Artists_Tools\B4Artists_Anim_Tools_github"))
DATA = ROOT / "training" / "b4artists_ml"
MANIFEST = DATA / "data_manifest.json"
SKELETON_AUDIT = DATA / "results" / "cached-skeleton-provenance-v1.json"
OUT = DATA / "results" / "joint-action-skeleton-protocol-v1.json"


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _load_rows(manifest: dict, skeleton_audit: dict) -> list[dict]:
    rows = manifest.get("files")
    audited = skeleton_audit.get("rows")
    if not isinstance(rows, list) or not rows:
        raise ValueError("Manifest files must be a non-empty list")
    if not isinstance(audited, list) or not audited:
        raise ValueError("Skeleton audit rows must be a non-empty list")

    audited_by_clip = {row.get("clip"): row for row in audited}
    if len(audited_by_clip) != len(audited):
        raise ValueError("Skeleton audit contains duplicate clip identities")

    output = []
    seen = set()
    for row in rows:
        clip = row.get("clip")
        if not isinstance(clip, str) or "_" not in clip:
            raise ValueError("Manifest clip identity must use SUBJECT_ACTION form")
        if clip in seen:
            raise ValueError("Duplicate manifest clip: " + clip)
        seen.add(clip)
        audited_row = audited_by_clip.get(clip)
        if audited_row is None:
            raise ValueError("Missing skeleton audit row for " + clip)
        action = audited_row.get("action")
        skeleton = audited_row.get("skeleton_sha256")
        if not isinstance(action, str) or not isinstance(skeleton, str):
            raise ValueError("Audited row lacks action/skeleton identity: " + clip)
        output.append({
            "action": action,
            "clip": clip,
            "source_split": row.get("split"),
            "skeleton_sha256": skeleton,
        })
    if set(audited_by_clip) != seen:
        missing = sorted(set(audited_by_clip) - seen)
        raise ValueError("Skeleton audit has rows absent from manifest: " + str(missing))
    return output


def _components(rows: list[dict]) -> list[dict]:
    adjacency: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        action_node = "action:" + row["action"]
        skeleton_node = "skeleton:" + row["skeleton_sha256"]
        adjacency[action_node].add(skeleton_node)
        adjacency[skeleton_node].add(action_node)

    components = []
    unseen = set(adjacency)
    while unseen:
        start = min(unseen)
        stack = [start]
        unseen.remove(start)
        nodes = []
        while stack:
            node = stack.pop()
            nodes.append(node)
            for neighbour in sorted(adjacency[node], reverse=True):
                if neighbour in unseen:
                    unseen.remove(neighbour)
                    stack.append(neighbour)
        actions = sorted(node.removeprefix("action:") for node in nodes
                         if node.startswith("action:"))
        skeletons = sorted(node.removeprefix("skeleton:") for node in nodes
                           if node.startswith("skeleton:"))
        component_rows = [row for row in rows
                          if row["action"] in actions
                          and row["skeleton_sha256"] in skeletons]
        signature = "|".join(actions) + "||" + "|".join(skeletons)
        components.append({
            "actions": actions,
            "skeletons": skeletons,
            "clips": sorted(row["clip"] for row in component_rows),
            "row_count": len(component_rows),
            "signature": signature,
        })
    return sorted(components, key=lambda item: item["signature"])


def _best_reduction(rows: list[dict], actions: list[str]) -> dict:
    candidates = []
    for size in range(len(actions) + 1):
        for excluded_tuple in itertools.combinations(actions, size):
            excluded = set(excluded_tuple)
            retained = [row for row in rows if row["action"] not in excluded]
            components = _components(retained) if retained else []
            if len(components) < 3:
                continue
            candidates.append({
                "excluded_actions": sorted(excluded),
                "retained_rows": retained,
                "components": components,
            })
    if not candidates:
        return {
            "excluded_actions": [],
            "retained_rows": [],
            "components": [],
            "found": False,
        }

    # Maximize retained evidence first.  Stable tie-breakers make the result
    # reproducible and prefer fewer exclusions and fewer dropped action groups.
    candidates.sort(key=lambda candidate: (
        -len(candidate["retained_rows"]),
        len(candidate["excluded_actions"]),
        tuple(candidate["excluded_actions"]),
        -len(candidate["components"]),
    ))
    selected = candidates[0]
    selected["found"] = True
    return selected


def build_protocol(manifest: dict, skeleton_audit: dict, *, manifest_hash: str) -> dict:
    rows = _load_rows(manifest, skeleton_audit)
    actions = sorted({row["action"] for row in rows})
    full_components = _components(rows)
    best = _best_reduction(rows, actions)

    assignment = {}
    proposed_rows = []
    if best["found"]:
        ordered_components = sorted(
            best["components"],
            key=lambda item: hashlib.sha256(
                ("component:" + item["signature"]).encode("utf-8")).hexdigest(),
        )
        split_names = ("train", "validation", "test")
        component_by_clip = {}
        for index, component in enumerate(ordered_components):
            proposed_split = split_names[index % len(split_names)]
            for clip in component["clips"]:
                component_by_clip[clip] = proposed_split
        excluded = set(best["excluded_actions"])
        for row in rows:
            if row["action"] in excluded:
                continue
            proposed_rows.append({
                **row,
                "proposed_split": component_by_clip[row["clip"]],
            })
        assignment = {
            split: sorted(row["clip"] for row in proposed_rows
                          if row["proposed_split"] == split)
            for split in split_names
        }

    excluded_rows = [row for row in rows
                     if row["action"] in set(best["excluded_actions"])]
    retained_count = len(best["retained_rows"])
    total_count = len(rows)
    leakage_free = False
    if best["found"]:
        by_split = defaultdict(list)
        for row in proposed_rows:
            by_split[row["proposed_split"]].append(row)
        leakage_free = True
        split_names = ("train", "validation", "test")
        for left_index, left_name in enumerate(split_names):
            for right_name in split_names[left_index + 1:]:
                left_actions = {row["action"] for row in by_split[left_name]}
                right_actions = {row["action"] for row in by_split[right_name]}
                left_skeletons = {
                    row["skeleton_sha256"] for row in by_split[left_name]
                }
                right_skeletons = {
                    row["skeleton_sha256"] for row in by_split[right_name]
                }
                if left_actions.intersection(right_actions):
                    leakage_free = False
                if left_skeletons.intersection(right_skeletons):
                    leakage_free = False
    return {
        "schema": "b4ml-joint-action-skeleton-protocol-v1",
        "status": (
            "REDUCED_JOINT_PARTITION_PROPOSAL_READY"
            if best["found"] else "NO_REDUCED_JOINT_PARTITION_FOUND"
        ),
        "scope": (
            "Deterministic, outcome-independent proposal only. It does not "
            "rewrite data_manifest.json, alter source splits, authorize "
            "training, or promote a model."
        ),
        "source_manifest": "training/b4artists_ml/data_manifest.json",
        "source_manifest_sha256": manifest_hash,
        "source_skeleton_audit": (
            "training/b4artists_ml/results/cached-skeleton-provenance-v1.json"
        ),
        "selection_rule": (
            "Enumerate action-group exclusions; retain the candidate with "
            "maximum rows that leaves at least three action/skeleton connected "
            "components. Tie-break by fewer exclusions, lexical exclusions, "
            "then more components. Assign components by stable SHA-256 order "
            "round-robin to train/validation/test."
        ),
        "full_corpus": {
            "row_count": total_count,
            "action_count": len(actions),
            "connected_component_count": len(full_components),
            "components": full_components,
            "joint_partition_using_all_rows": len(full_components) >= 3,
        },
        "proposal": {
            "excluded_actions": best["excluded_actions"],
            "excluded_rows": sorted(row["clip"] for row in excluded_rows),
            "retained_row_count": retained_count,
            "retained_fraction": retained_count / total_count if total_count else 0.0,
            "connected_components": best["components"],
            "split_clip_assignment": assignment,
            "proposed_rows": proposed_rows,
            "no_action_or_skeleton_leakage_across_proposed_splits": leakage_free,
        },
        "manifest_rig_identity_fields": sorted(
            field for field in manifest["files"][0]
            if any(token in field.lower()
                   for token in ("rig", "skeleton", "source_rig"))
        ),
        "derived_skeleton_topology_is_not_rig_identity": True,
        "reviewed_contact_intent_available": bool(
            skeleton_audit.get("reviewed_contact_intent_available", False)
        ),
        "rig_disjoint": False,
        "training_authorized": False,
        "model_promoted": False,
        "claim_boundary": {
            "full_corpus_joint_partition_qualified": False,
            "reduced_joint_partition_is_proposal_only": True,
            "reduced_joint_partition_temporal_evaluation_qualified": False,
            "rig_disjoint_temporal_evaluation_qualified": False,
            "reviewed_contact_intent_required": True,
            "full_goal_complete": False,
        },
    }


def main() -> dict:
    manifest_text = MANIFEST.read_text(encoding="utf-8")
    manifest = json.loads(manifest_text)
    skeleton_audit = json.loads(SKELETON_AUDIT.read_text(encoding="utf-8"))
    report = build_protocol(
        manifest,
        skeleton_audit,
        manifest_hash=_sha256_text(manifest_text),
    )
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n",
                   encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return report


if __name__ == "__main__":
    main()
