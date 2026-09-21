"""Fail-closed preflight for a future learned-motion corpus.

This is an intake validator, not a trainer and not an authorization grant.
It deliberately requires explicit action and source-rig identities instead of
inferring them from clip names or cached topology.  A future corpus may pass
this preflight only when its split boundaries, reviewed label receipt, and
separate identity/authorization receipt are all bound to the same manifest.
The current frozen corpus is expected to fail.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(os.environ.get(
    "B4ML_REPO",
    r"X:\Scripting Attempts\B4Artists_Tools\B4Artists_Anim_Tools_github"))
RESULTS = ROOT / "training" / "b4artists_ml" / "results"
DEFAULT_MANIFEST = ROOT / "training" / "b4artists_ml" / "data_manifest.json"
DEFAULT_LABELS = RESULTS / "reviewed-contact-intent-v1.json"
DEFAULT_IDENTITY = RESULTS / "temporal-reviewer-identity-v1.json"
DEFAULT_OUT = RESULTS / "temporal-corpus-intake-v1.json"
SPLITS = ("train", "validation", "test")
REQUIRED_ROW_FIELDS = ("clip", "split", "sha256", "action_id", "source_rig_id", "skeleton_id")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as stream:
        value = json.load(stream)
    if not isinstance(value, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return value


def _timestamp_is_valid(value: Any) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None


def _cross_split(values_by_group: dict[str, list[dict[str, str]]]) -> dict[str, list[dict[str, str]]]:
    return {
        group: sorted(values, key=lambda value: value["clip"])
        for group, values in sorted(values_by_group.items())
        if len({value["split"] for value in values}) > 1
    }


def _manifest_report(
    manifest: dict[str, Any], manifest_hash: str, cache_root: Path
) -> dict[str, Any]:
    failures: list[str] = []
    rows = manifest.get("files")
    if not isinstance(rows, list) or not rows:
        return {
            "row_count": 0,
            "split_counts": {},
            "missing_required_fields": list(REQUIRED_ROW_FIELDS),
            "cross_split_action_groups": {},
            "cross_split_rig_groups": {},
            "cross_split_skeleton_groups": {},
            "missing_source_files": [],
            "checksum_mismatches": [],
            "byte_count_mismatches": [],
            "source_bytes_bound": False,
            "action_disjoint": False,
            "rig_disjoint": False,
            "skeleton_disjoint": False,
            "explicit_identity_fields": False,
            "failures": ["manifest.files must be a non-empty list"],
        }

    missing_fields = sorted({
        field for field in REQUIRED_ROW_FIELDS
        if any(not isinstance(row, dict) or field not in row for row in rows)
    })
    if missing_fields:
        failures.append("manifest rows lack explicit fields: " + ", ".join(missing_fields))

    seen: set[str] = set()
    split_counts: dict[str, int] = defaultdict(int)
    actions: dict[str, list[dict[str, str]]] = defaultdict(list)
    rigs: dict[str, list[dict[str, str]]] = defaultdict(list)
    skeletons: dict[str, list[dict[str, str]]] = defaultdict(list)
    malformed_rows: list[str] = []
    invalid_identity_rows: list[str] = []
    missing_source_files: list[str] = []
    checksum_mismatches: list[str] = []
    byte_count_mismatches: list[str] = []
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            malformed_rows.append(str(index))
            continue
        clip = row.get("clip")
        split = row.get("split")
        action = row.get("action_id")
        rig = row.get("source_rig_id")
        skeleton = row.get("skeleton_id")
        checksum = row.get("sha256")
        if not isinstance(clip, str) or not clip.strip() or clip in seen:
            malformed_rows.append(str(index))
            continue
        seen.add(clip)
        if split not in SPLITS:
            malformed_rows.append(clip)
            continue
        split_counts[split] += 1
        if (not isinstance(checksum, str) or len(checksum) != 64
                or any(character not in "0123456789abcdefABCDEF" for character in checksum)):
            malformed_rows.append(clip)
        source_name = clip if clip.lower().endswith(".bvh") else clip + ".bvh"
        source_path = cache_root / source_name
        if Path(source_name).name != source_name or not source_path.is_file():
            missing_source_files.append(clip)
        else:
            source_bytes = source_path.read_bytes()
            if (isinstance(checksum, str)
                    and hashlib.sha256(source_bytes).hexdigest().lower() != checksum.lower()):
                checksum_mismatches.append(clip)
            declared_bytes = row.get("bytes")
            if (declared_bytes is not None
                    and (isinstance(declared_bytes, bool)
                         or not isinstance(declared_bytes, int)
                         or declared_bytes != len(source_bytes))):
                byte_count_mismatches.append(clip)
        valid_identity_values = all(
            isinstance(value, str) and value.strip()
            for value in (action, rig, skeleton)
        )
        if not valid_identity_values:
            if all(field in row for field in ("action_id", "source_rig_id", "skeleton_id")):
                invalid_identity_rows.append(clip)
            continue
        row_identity = {
            "clip": clip,
            "split": split,
            "action_id": action,
            "source_rig_id": rig,
            "skeleton_id": skeleton,
        }
        actions[action].append(row_identity)
        rigs[rig].append(row_identity)
        skeletons[skeleton].append(row_identity)

    if malformed_rows:
        failures.append("malformed or duplicate manifest rows: " + ", ".join(malformed_rows))
    if invalid_identity_rows:
        failures.append(
            "manifest rows lack non-empty action/rig/skeleton identities: "
            + ", ".join(invalid_identity_rows)
        )
    if missing_source_files:
        failures.append(
            "manifest source files are missing from the bound cache: "
            + ", ".join(missing_source_files)
        )
    if checksum_mismatches:
        failures.append(
            "manifest source checksums do not match cached bytes: "
            + ", ".join(checksum_mismatches)
        )
    if byte_count_mismatches:
        failures.append(
            "manifest declared byte counts do not match cached bytes: "
            + ", ".join(byte_count_mismatches)
        )
    cross_actions = _cross_split(actions)
    cross_rigs = _cross_split(rigs)
    cross_skeletons = _cross_split(skeletons)
    complete_identities = not missing_fields and not invalid_identity_rows
    action_disjoint = bool(actions) and not cross_actions and complete_identities
    rig_disjoint = bool(rigs) and not cross_rigs and complete_identities
    skeleton_disjoint = bool(skeletons) and not cross_skeletons and complete_identities
    if not action_disjoint:
        failures.append("explicit action identities are missing or cross split boundaries")
    if not rig_disjoint:
        failures.append("explicit source-rig identities are missing or cross split boundaries")
    if not skeleton_disjoint:
        failures.append("explicit skeleton identities are missing or cross split boundaries")
    if any(split_counts.get(split, 0) == 0 for split in SPLITS):
        failures.append("train, validation, and test must each contain at least one row")

    return {
        "row_count": len(rows),
        "split_counts": dict(sorted(split_counts.items())),
        "missing_required_fields": missing_fields,
        "malformed_rows": malformed_rows,
        "invalid_identity_rows": invalid_identity_rows,
        "missing_source_files": missing_source_files,
        "checksum_mismatches": checksum_mismatches,
        "byte_count_mismatches": byte_count_mismatches,
        "source_bytes_bound": not (
            malformed_rows or missing_source_files or checksum_mismatches
            or byte_count_mismatches
        ),
        "explicit_identity_fields": complete_identities,
        "action_group_count": len(actions),
        "source_rig_group_count": len(rigs),
        "skeleton_group_count": len(skeletons),
        "cross_split_action_groups": cross_actions,
        "cross_split_rig_groups": cross_rigs,
        "cross_split_skeleton_groups": cross_skeletons,
        "action_disjoint": action_disjoint,
        "rig_disjoint": rig_disjoint,
        "skeleton_disjoint": skeleton_disjoint,
        "manifest_sha256": manifest_hash,
        "failures": failures,
    }


def _labels_report(path: Path, manifest_hash: str) -> dict[str, Any]:
    if not path.is_file():
        return {
            "path": str(path),
            "present": False,
            "valid": False,
            "failures": ["reviewed contact/intent receipt is missing"],
        }
    try:
        receipt = _load_json(path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return {
            "path": str(path),
            "present": True,
            "valid": False,
            "failures": ["reviewed contact/intent receipt is unreadable: " + str(exc)],
        }

    failures = []
    human_authored = receipt.get("human_authored") is True
    validated_export = receipt.get("human_review_export_validated") is True
    if not (human_authored or validated_export):
        failures.append("reviewed contact/intent receipt is not human-authored")
    if receipt.get("complete") is not True:
        failures.append("reviewed contact/intent receipt is not complete")
    count = receipt.get("reviewed_items", receipt.get("human_reviewed_items", receipt.get("cases", 0)))
    if not isinstance(count, int) or count <= 0:
        failures.append("reviewed contact/intent receipt contains no reviewed items")
    if receipt.get("source_manifest_sha256") != manifest_hash:
        failures.append("reviewed contact/intent receipt is not bound to this manifest")
    reviewer = receipt.get("reviewer")
    if not isinstance(reviewer, dict) or not isinstance(reviewer.get("id"), str) or not reviewer["id"].strip():
        failures.append("reviewed contact/intent receipt lacks a reviewer identity")
    if not _timestamp_is_valid(receipt.get("exported_utc")):
        failures.append("reviewed contact/intent receipt lacks a timezone-bound export timestamp")
    return {
        "path": str(path),
        "present": True,
        "valid": not failures,
        "schema": receipt.get("schema"),
        "reviewed_items": count,
        "human_authored": human_authored,
        "reviewer_id": reviewer.get("id") if isinstance(reviewer, dict) else None,
        "source_manifest_bound": receipt.get("source_manifest_sha256") == manifest_hash,
        "receipt_sha256": _sha256(path),
        "failures": failures,
    }


def _identity_report(path: Path, manifest_hash: str) -> dict[str, Any]:
    if not path.is_file():
        return {
            "path": str(path),
            "present": False,
            "valid": False,
            "failures": ["separate identity/authorization receipt is missing"],
        }
    try:
        receipt = _load_json(path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return {
            "path": str(path),
            "present": True,
            "valid": False,
            "failures": ["identity/authorization receipt is unreadable: " + str(exc)],
        }
    failures = []
    if receipt.get("authorized") is not True:
        failures.append("identity/authorization receipt is not explicitly authorized")
    if receipt.get("source_manifest_sha256") != manifest_hash:
        failures.append("identity/authorization receipt is not bound to this manifest")
    if not isinstance(receipt.get("reviewer_id"), str) or not receipt["reviewer_id"].strip():
        failures.append("identity/authorization receipt lacks reviewer_id")
    if not _timestamp_is_valid(receipt.get("issued_utc")):
        failures.append("identity/authorization receipt lacks a timezone-bound issued timestamp")
    return {
        "path": str(path),
        "present": True,
        "valid": not failures,
        "reviewer_id": receipt.get("reviewer_id"),
        "receipt_sha256": _sha256(path),
        "source_manifest_bound": receipt.get("source_manifest_sha256") == manifest_hash,
        "failures": failures,
    }


def build_report(manifest_path: Path, labels_path: Path, identity_path: Path) -> dict[str, Any]:
    manifest = _load_json(manifest_path)
    manifest_hash = _sha256(manifest_path)
    manifest_report = _manifest_report(manifest, manifest_hash, manifest_path.parent / "cache")
    labels = _labels_report(labels_path, manifest_hash)
    identity = _identity_report(identity_path, manifest_hash)
    failures = list(manifest_report["failures"])
    failures.extend(labels["failures"])
    failures.extend(identity["failures"])
    if (labels.get("reviewer_id") and identity.get("reviewer_id")
            and labels["reviewer_id"] != identity["reviewer_id"]):
        failures.append(
            "reviewed contact/intent reviewer does not match the authorized reviewer"
        )
    qualified = not failures
    return {
        "schema": "b4ml-temporal-corpus-intake-v1",
        "status": "QUALIFIED_FOR_PARENT_BOUNDARY" if qualified else "BLOCKED_INTAKE_MISSING_EVIDENCE",
        "scope": (
            "Read-only future-corpus preflight. It does not rewrite a manifest, "
            "download data, train a model, authorize training, or promote a checkpoint."
        ),
        "source_manifest": str(manifest_path),
        "manifest": manifest_report,
        "reviewed_contact_intent": labels,
        "identity_authorization": identity,
        "failures": failures,
        "qualified_for_parent_boundary": qualified,
        "training_authorized": False,
        "model_training_permitted": False,
        "model_promoted": False,
        "claim_boundary": {
            "action_disjoint_temporal_evaluation_qualified": qualified,
            "rig_disjoint_temporal_evaluation_qualified": qualified,
            "reviewed_contact_intent_available": labels["valid"],
            "learned_temporal_quality_verified": False,
            "full_goal_complete": False,
        },
    }


def main() -> dict[str, Any]:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--labels-receipt", type=Path, default=DEFAULT_LABELS)
    parser.add_argument("--identity-receipt", type=Path, default=DEFAULT_IDENTITY)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    report = build_report(args.manifest, args.labels_receipt, args.identity_receipt)
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return report


if __name__ == "__main__":
    result = main()
    if result["status"] != "QUALIFIED_FOR_PARENT_BOUNDARY":
        raise SystemExit(2)
