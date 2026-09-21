"""Fail-closed structural validation for future Cascadeur comparison results.

This checker does not score parity or superiority.  It only verifies that a
future external packet contains the complete protocol-shaped evidence needed
for a later, independent claim audit.  With no packet present it writes an
explicit blocked receipt and exits successfully so handoff automation remains
safe and deterministic.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TRAIN = ROOT / "training" / "b4artists_ml"
PROTOCOL_PATH = TRAIN / "cascadeur_comparison_protocol_v2.json"
PACKET_PATH = Path(os.environ.get(
    "B4ML_CASCADEUR_RESULTS_PACKET",
    str(TRAIN / "results/cascadeur-comparison-results-v1.json"),
))
OUTPUT = Path(os.environ.get(
    "B4ML_CASCADEUR_RESULTS_CONTRACT_OUT",
    str(TRAIN / "results/cascadeur-comparison-results-contract-v1.json"),
))

SCHEMA = "b4ml-cascadeur-matched-comparison-results-v1"
CONTRACT_SCHEMA = "b4ml-cascadeur-comparison-results-contract-v1"
ALLOWED_PREFERENCES = {"b4ml", "cascadeur", "tie", "undecided"}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _sha_text(value, label: str) -> None:
    _require(isinstance(value, str) and len(value) == 64, f"{label} must be a SHA-256 string")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{label} must be hexadecimal") from exc


def _text(value, label: str) -> None:
    _require(isinstance(value, str) and bool(value.strip()), f"{label} must be non-empty text")


def _finite_number(value, label: str) -> None:
    _require(isinstance(value, (int, float)) and not isinstance(value, bool),
             f"{label} must be numeric")
    _require(math.isfinite(float(value)), f"{label} must be finite")


def _artifact(value, label: str) -> None:
    _require(isinstance(value, dict), f"{label} must be an artifact object")
    _text(value.get("path"), f"{label}.path")
    _sha_text(value.get("sha256"), f"{label}.sha256")


def _validate_method(method, label: str, automated_metrics: list[str]) -> None:
    _require(isinstance(method, dict), f"{label} must be an object")
    _text(method.get("status"), f"{label}.status")
    _require(method["status"] == "PASS", f"{label}.status must be PASS")
    _sha_text(method.get("source_hash"), f"{label}.source_hash")
    _sha_text(method.get("output_hash"), f"{label}.output_hash")
    _artifact(method.get("raw_event_log"), f"{label}.raw_event_log")
    metrics = method.get("automated_metrics")
    _require(isinstance(metrics, dict), f"{label}.automated_metrics must be an object")
    for metric in automated_metrics:
        _finite_number(metrics.get(metric), f"{label}.automated_metrics.{metric}")


def _validate_human_metrics(case, human_metrics: list[str]) -> None:
    metrics = case.get("human_metrics")
    _require(isinstance(metrics, dict), "case.human_metrics must be an object")
    for metric in human_metrics:
        _require(metric in metrics, f"case.human_metrics.{metric} is missing")
    for metric in (
        "naturalness_1_to_5",
        "contact_stability_1_to_5",
        "transition_continuity_1_to_5",
        "intent_preservation_1_to_5",
    ):
        value = metrics[metric]
        _finite_number(value, f"case.human_metrics.{metric}")
        _require(1.0 <= float(value) <= 5.0, f"case.human_metrics.{metric} is out of range")
    _require(isinstance(metrics["production_acceptable"], bool),
             "case.human_metrics.production_acceptable must be boolean")
    for metric in ("actual_corrective_edits", "actual_interactions"):
        value = metrics[metric]
        _require(isinstance(value, int) and not isinstance(value, bool) and value >= 0,
                 f"case.human_metrics.{metric} must be a non-negative integer")
    _finite_number(metrics["active_work_seconds"], "case.human_metrics.active_work_seconds")
    _require(float(metrics["active_work_seconds"]) >= 0.0,
             "case.human_metrics.active_work_seconds must be non-negative")
    _require(metrics["blind_overall_preference"] in ALLOWED_PREFERENCES,
             "case.human_metrics.blind_overall_preference is invalid")
    tags = metrics["visible_failure_tags"]
    _require(isinstance(tags, list) and all(isinstance(tag, str) for tag in tags),
             "case.human_metrics.visible_failure_tags must be a string list")


def validate_packet(packet: dict, protocol: dict) -> dict:
    """Validate packet completeness without making a quality claim."""
    _require(packet.get("schema") == SCHEMA, "Results packet schema changed")
    _require(packet.get("status") == "COMPLETE", "Results packet is not complete")
    _require(packet.get("protocol") == "training/b4artists_ml/cascadeur_comparison_protocol_v2.json",
             "Results packet protocol binding changed")
    _require(packet.get("protocol_sha256") == sha(PROTOCOL_PATH),
             "Results packet protocol hash does not match the current protocol")
    _require(packet.get("protocol_sha256") == packet.get("protocol_sha256_recorded"),
             "Results packet protocol hash was not independently recorded")

    metadata = packet.get("run_metadata")
    _require(isinstance(metadata, dict), "run_metadata is missing")
    for field in ("cascadeur_version", "edition", "entitlement", "started_at", "completed_at"):
        _text(metadata.get(field), f"run_metadata.{field}")
    _require(isinstance(metadata.get("hardware"), dict) and metadata["hardware"],
             "run_metadata.hardware is missing")
    _require(isinstance(metadata.get("background_load"), dict),
             "run_metadata.background_load is missing")
    _require(metadata.get("settings_exported") is True, "Cascadeur settings export is missing")
    _artifact(metadata.get("settings_export"), "run_metadata.settings_export")

    identity = packet.get("identity_authorization_receipt")
    _artifact(identity, "identity_authorization_receipt")
    _require(identity.get("authorized") is True,
             "identity_authorization_receipt.authorized must be true")
    _require(identity.get("human_authored") is True,
             "identity_authorization_receipt.human_authored must be true")

    assets = packet.get("assets")
    expected_assets = protocol["portable_characters"]["assets"]
    _require(isinstance(assets, list) and len(assets) == 3, "Results asset list must contain three assets")
    expected_ids = [item["id"] for item in expected_assets]
    _require([item.get("id") for item in assets] == expected_ids,
             "Results asset identities or order changed")
    for expected, actual in zip(expected_assets, assets):
        asset_id = expected["id"]
        _require(actual.get("source_fbx_sha256") == expected["fbx_sha256"],
                 f"Results source FBX hash changed: {asset_id}")
        _sha_text(actual.get("cascadeur_input_sha256"), f"results.{asset_id}.cascadeur_input_sha256")
        _sha_text(actual.get("b4ml_output_sha256"), f"results.{asset_id}.b4ml_output_sha256")
        _sha_text(actual.get("cascadeur_output_sha256"), f"results.{asset_id}.cascadeur_output_sha256")
        _require(actual.get("conversion_verified") is True,
                 f"Results conversion is not verified: {asset_id}")
        _require(actual.get("standard_rig_verified") is True,
                 f"Results standard-rig mapping is not verified: {asset_id}")

    tasks = protocol["tasks"]
    animators = packet.get("animators")
    _require(isinstance(animators, list) and len(animators) == 3,
             "Results must contain exactly three independent animators")
    animator_ids = [item.get("id") for item in animators]
    _require(all(isinstance(item, str) and item for item in animator_ids)
             and len(set(animator_ids)) == 3,
             "Animator identities are missing or duplicated")
    _require(sum(bool(item.get("five_or_more_years_experience")) for item in animators) >= 1,
             "At least one animator experience record is required")

    cases = packet.get("cases")
    expected_keys = {
        (animator_id, asset_id, task)
        for animator_id in animator_ids
        for asset_id in expected_ids
        for task in tasks
    }
    _require(isinstance(cases, list) and len(cases) == len(expected_keys),
             "Results must contain exactly 72 matched cases")
    actual_keys = set()
    for case in cases:
        _require(isinstance(case, dict), "Each matched case must be an object")
        key = (case.get("animator_id"), case.get("asset_id"), case.get("task"))
        _require(key in expected_keys, "Results contain an unknown or malformed matched case")
        _require(key not in actual_keys, "Results contain a duplicate matched case")
        actual_keys.add(key)
        _require(case.get("ratings_locked_before_identity_reveal") is True,
                 "Ratings were not locked before identity reveal")
        _require(case.get("method_identity_revealed_after_lock") is True,
                 "Method identity was revealed before ratings were locked")
        _validate_method(case.get("b4ml"), "case.b4ml", protocol["automated_metrics"])
        _validate_method(case.get("cascadeur"), "case.cascadeur", protocol["automated_metrics"])
        _validate_human_metrics(case, protocol["human_metrics"])
    _require(actual_keys == expected_keys, "Results case matrix is incomplete")

    gates = packet.get("claim_gates")
    _require(isinstance(gates, dict), "claim_gates are missing")
    parity = gates.get("parity")
    surpasses = gates.get("surpasses")
    _require(isinstance(parity, dict) and isinstance(surpasses, dict),
             "claim_gates parity/surpasses objects are required")
    for field in (
        "all_24_matched_cases_complete",
        "all_source_and_output_hashes_present",
        "no_automated_safety_threshold_weakened",
        "no_unreported_failed_or_excluded_case",
    ):
        _require(isinstance(parity.get(field), bool), f"claim_gates.parity.{field} must be boolean")
    for field in (
        "parity_gate_required",
        "remaining_regressions_and_gaps_reported",
    ):
        _require(isinstance(surpasses.get(field), bool), f"claim_gates.surpasses.{field} must be boolean")
    _require(packet.get("parity_verified") is False and packet.get("surpasses_verified") is False,
             "Results packet cannot assert parity or superiority")
    _require(packet.get("full_goal_complete") is False,
             "Results packet cannot assert full-goal completion")
    return {"assets": 3, "animators": 3, "tasks": len(tasks), "cases": len(cases)}


def _write(report: dict) -> dict:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, allow_nan=False))
    return report


def main() -> dict:
    protocol = json.loads(PROTOCOL_PATH.read_text(encoding="utf-8-sig"))
    base = {
        "schema": CONTRACT_SCHEMA,
        "packet": str(PACKET_PATH),
        "protocol": str(PROTOCOL_PATH.relative_to(ROOT)).replace("\\", "/"),
        "protocol_sha256": sha(PROTOCOL_PATH),
        "results_present": PACKET_PATH.is_file(),
        "parity_verified": False,
        "surpasses_verified": False,
        "full_goal_complete": False,
        "claim_boundary_closed": True,
    }
    if not PACKET_PATH.is_file():
        return _write({
            **base,
            "status": "BLOCKED_EXTERNAL_RESULTS_MISSING",
            "scope": "Contract handoff only; no Cascadeur comparison result packet is present.",
            "reason": "A complete independent result packet is required before conversion, parity, or superiority can be considered.",
        })
    try:
        summary = validate_packet(
            json.loads(PACKET_PATH.read_text(encoding="utf-8-sig")), protocol
        )
    except (OSError, json.JSONDecodeError, TypeError, ValueError) as exc:
        return _write({
            **base,
            "status": "RESULTS_PRESENT_INVALID",
            "scope": "Contract handoff only; the supplied result packet is not structurally admissible.",
            "reason": type(exc).__name__ + ": " + str(exc),
        })
    return _write({
        **base,
        "status": "PASS_CONTRACT_ONLY",
        "scope": "Complete result-packet structure is present; independent claim-gate review is still required.",
        "summary": summary,
        "claim_audit_required": True,
    })


if __name__ == "__main__":
    main()
