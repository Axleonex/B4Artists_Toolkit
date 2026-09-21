"""Build an outcome-independent action-group partition proposal.

This never rewrites data_manifest.json and never authorizes training.  It is a
data-boundary artifact for use after rig identity and reviewed labels exist.
"""
from __future__ import annotations

import hashlib
import json
import os
from collections import defaultdict
from pathlib import Path


ROOT = Path(os.environ.get(
    "B4ML_REPO",
    r"X:\Scripting Attempts\B4Artists_Tools\B4Artists_Anim_Tools_github"))
MANIFEST = ROOT / "training" / "b4artists_ml" / "data_manifest.json"
OUT = ROOT / "training" / "b4artists_ml" / "results" / "action-disjoint-protocol-v1.json"


def _group_rows(manifest: dict) -> dict[str, list[dict[str, str]]]:
    rows = manifest.get("files")
    if not isinstance(rows, list) or not rows:
        raise ValueError("Manifest files must be a non-empty list")
    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    seen: set[str] = set()
    for row in rows:
        if not isinstance(row, dict) or not all(key in row for key in ("clip", "split", "sha256")):
            raise ValueError("Manifest rows require clip, split and sha256")
        clip = row["clip"]
        if not isinstance(clip, str) or "_" not in clip:
            raise ValueError("Clip identity must use SUBJECT_ACTION form: " + str(clip))
        if clip in seen:
            raise ValueError("Duplicate clip identity: " + clip)
        seen.add(clip)
        action = clip.split("_", 1)[1]
        groups[action].append({"clip": clip, "source_split": row["split"]})
    return dict(groups)


def _stable_actions(groups: dict[str, list[dict[str, str]]]) -> list[str]:
    return sorted(groups, key=lambda action: hashlib.sha256(
        ("action:" + action).encode("utf-8")).hexdigest())


def build_protocol(manifest: dict, *, manifest_hash: str | None = None) -> dict:
    groups = _group_rows(manifest)
    actions = _stable_actions(groups)
    count = len(actions)
    if count < 6:
        raise ValueError("At least six action groups are required for the proposal")
    train_end = max(1, min(count - 2, round(count * 0.70)))
    validation_end = max(train_end + 1, min(count - 1, round(count * 0.85)))
    assignment = {}
    for index, action in enumerate(actions):
        assignment[action] = (
            "train" if index < train_end
            else "validation" if index < validation_end
            else "test"
        )
    proposed_rows = []
    split_counts = defaultdict(int)
    for action in actions:
        for row in sorted(groups[action], key=lambda value: value["clip"]):
            split = assignment[action]
            proposed_rows.append({
                "action": action,
                "clip": row["clip"],
                "source_split": row["source_split"],
                "proposed_split": split,
            })
            split_counts[split] += 1
    leakage = {
        action: split for action, split in assignment.items()
        if len({row["proposed_split"] for row in proposed_rows if row["action"] == action}) != 1
    }
    if leakage:
        raise AssertionError("Action group was assigned to multiple proposed splits")
    rig_fields = sorted(
        field for field in manifest["files"][0]
        if any(token in field.lower() for token in ("rig", "skeleton", "source_rig"))
    )
    return {
        "schema": "b4ml-action-disjoint-protocol-v1",
        "status": "ACTION_DISJOINT_PARTITION_READY_RIG_IDENTITY_MISSING",
        "scope": "Outcome-independent action-group partition proposal; no manifest rewrite, training, download, or model promotion.",
        "source_manifest": "training/b4artists_ml/data_manifest.json",
        "source_manifest_sha256": manifest_hash,
        "selection_rule": "Sort action groups by SHA-256 of UTF-8 action:<action>; assign first 70 percent to train, next 15 percent to validation, remainder to test, with at least two groups in validation and test.",
        "action_group_order": actions,
        "action_group_assignment": dict(sorted(assignment.items())),
        "proposed_split_counts": dict(sorted(split_counts.items())),
        "proposed_rows": proposed_rows,
        "action_partition_has_no_group_leakage": not leakage,
        "manifest_rig_identity_fields": rig_fields,
        "rig_disjoint": False,
        "reviewed_contact_intent_available": False,
        "training_authorized": False,
        "model_promoted": False,
        "claim_boundary": {
            "action_disjoint_partition_is_a_proposal_only": True,
            "action_disjoint_temporal_evaluation_qualified": False,
            "rig_disjoint_temporal_evaluation_qualified": False,
            "full_goal_complete": False,
        },
    }


def main() -> dict:
    text = MANIFEST.read_text(encoding="utf-8")
    report = build_protocol(
        json.loads(text),
        manifest_hash=hashlib.sha256(text.encode("utf-8")).hexdigest(),
    )
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return report


if __name__ == "__main__":
    main()
