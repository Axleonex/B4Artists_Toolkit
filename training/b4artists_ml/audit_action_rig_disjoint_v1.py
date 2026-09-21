"""Audit action and rig identity boundaries without rewriting the frozen corpus."""
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
OUT = ROOT / "training" / "b4artists_ml" / "results" / "action-rig-disjoint-audit-v1.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _identity(clip: str) -> tuple[str, str]:
    subject, separator, action = clip.partition("_")
    if not separator or not subject or not action:
        raise ValueError("Clip identity must use SUBJECT_ACTION form: " + clip)
    return subject, action


def build_report(manifest: dict, *, manifest_hash: str | None = None) -> dict:
    rows = manifest.get("files")
    if not isinstance(rows, list) or not rows:
        raise ValueError("Manifest files must be a non-empty list")

    action_groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    split_counts: dict[str, int] = defaultdict(int)
    subjects_by_split: dict[str, set[str]] = defaultdict(set)
    row_keys: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("Manifest rows must be objects")
        required = {"clip", "split", "sha256"}
        if not required.issubset(row):
            raise ValueError("Manifest row is missing required identity fields")
        clip = row["clip"]
        split = row["split"]
        if not isinstance(clip, str) or not isinstance(split, str):
            raise ValueError("Clip and split identities must be strings")
        if clip in row_keys:
            raise ValueError("Duplicate clip identity: " + clip)
        row_keys.add(clip)
        subject, action = _identity(clip)
        action_groups[action].append({"clip": clip, "split": split, "subject": subject})
        split_counts[split] += 1
        subjects_by_split[split].add(subject)

    cross_split_actions = {
        action: sorted(values, key=lambda value: value["clip"])
        for action, values in sorted(action_groups.items())
        if len({value["split"] for value in values}) > 1
    }
    row_fields = set(rows[0])
    rig_fields = sorted(
        field for field in row_fields
        if any(token in field.lower() for token in ("rig", "skeleton", "source_rig"))
    )
    action_disjoint = not cross_split_actions
    rig_disjoint = bool(rig_fields)
    reasons = []
    if not action_disjoint:
        reasons.append("action identities cross the frozen train/validation/test split")
    if not rig_disjoint:
        reasons.append("manifest contains no rig or skeleton identity")
    return {
        "schema": "b4ml-action-rig-disjoint-audit-v1",
        "status": "QUALIFIED" if action_disjoint and rig_disjoint
        else "UNQUALIFIED_ACTION_AND_RIG_DISJOINTNESS",
        "scope": "Read-only audit of the frozen motion manifest; no split rewrite, download, training, or model promotion.",
        "source_manifest": "training/b4artists_ml/data_manifest.json",
        "source_manifest_sha256": manifest_hash,
        "row_count": len(rows),
        "split_counts": dict(sorted(split_counts.items())),
        "action_group_count": len(action_groups),
        "action_groups": {
            action: sorted(values, key=lambda value: value["clip"])
            for action, values in sorted(action_groups.items())
        },
        "cross_split_action_groups": cross_split_actions,
        "subjects_by_split": {
            split: sorted(subjects)
            for split, subjects in sorted(subjects_by_split.items())
        },
        "manifest_rig_identity_fields": rig_fields,
        "action_disjoint": action_disjoint,
        "rig_disjoint": rig_disjoint,
        "reasons": reasons,
        "claim_boundary": {
            "action_disjoint_temporal_evaluation_available": action_disjoint,
            "rig_disjoint_temporal_evaluation_available": rig_disjoint,
            "training_authorized": False,
            "model_promoted": False,
            "full_goal_complete": False,
        },
    }


def main() -> dict:
    manifest_text = MANIFEST.read_text(encoding="utf-8")
    report = build_report(
        json.loads(manifest_text),
        manifest_hash=hashlib.sha256(manifest_text.encode("utf-8")).hexdigest(),
    )
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return report


if __name__ == "__main__":
    result = main()
    if result["status"] != "QUALIFIED":
        raise SystemExit(2)
