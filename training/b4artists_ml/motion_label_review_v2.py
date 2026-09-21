"""Strict contracts for completed human review of weak motion labels.

This module is deliberately independent of Blender and NumPy so exported
reviews can be checked in a small local Python process before they are used by
any training code.
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime
from hashlib import sha256
import json
import math


SCHEMA = "b4ml-reviewed-motion-labels-v2"
CONTRACT_SCHEMA = "b4ml-motion-label-review-contract-v2"
VERDICTS = frozenset(("accepted", "rejected", "uncertain"))
INTENTS = frozenset(
    (
        "unknown",
        "walk",
        "run",
        "jump",
        "land",
        "turn",
        "reach",
        "crouch",
        "interaction",
        "combat",
        "dance",
        "gesture",
        "other",
    )
)
EXPERIENCE = frozenset(("under_1_year", "1_3_years", "3_5_years", "5_plus_years"))


def canonical_bytes(value):
    return (
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def digest_document(value):
    return sha256(canonical_bytes(value)).hexdigest()


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON field: {key}")
        result[key] = value
    return result


def loads_strict(raw, name, *, maximum_bytes, maximum_depth=8, maximum_nodes=20000):
    """Parse bounded UTF-8 JSON, rejecting duplicates and nonstandard numbers."""
    if not isinstance(raw, bytes):
        raise TypeError(f"{name} must be supplied as frozen bytes")
    if not raw or len(raw) > maximum_bytes:
        raise ValueError(f"{name} size must be between 1 and {maximum_bytes} bytes")

    def reject_constant(value):
        raise ValueError(f"{name} contains nonstandard numeric constant {value}")

    try:
        value = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=_unique_object,
            parse_constant=reject_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, RecursionError) as exc:
        raise ValueError(f"{name} is not bounded strict UTF-8 JSON") from exc
    nodes = 0
    stack = [(value, 0)]
    while stack:
        current, depth = stack.pop()
        nodes += 1
        if nodes > maximum_nodes or depth > maximum_depth:
            raise ValueError(f"{name} exceeds the structural limit")
        if isinstance(current, dict):
            stack.extend((item, depth + 1) for item in current.values())
        elif isinstance(current, list):
            stack.extend((item, depth + 1) for item in current)
    return value


def _mapping(value, name):
    if not isinstance(value, dict):
        raise ValueError(f"{name} must be an object")
    return value


def _exact_keys(value, expected, name):
    actual = set(value)
    expected = set(expected)
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        raise ValueError(f"{name} fields differ; missing={missing}, extra={extra}")


def _clean_text(value, name, *, minimum=0, maximum=2000):
    if not isinstance(value, str):
        raise ValueError(f"{name} must be text")
    result = value.strip()
    if not minimum <= len(result) <= maximum:
        raise ValueError(f"{name} length must be between {minimum} and {maximum}")
    return result


def _whole_frame(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{name} must be a finite whole frame")
    result = int(value)
    if result != value:
        raise ValueError(f"{name} must be a finite whole frame")
    return result


def _utc_timestamp(value, name="exported_utc"):
    value = _clean_text(value, name, minimum=1, maximum=80)
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{name} must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None:
        raise ValueError(f"{name} must include a timezone")
    return value, parsed


def validate_contract(contract, queue, queue_sha256):
    contract = _mapping(contract, "review contract")
    queue = _mapping(queue, "source queue")
    if contract.get("schema") != CONTRACT_SCHEMA:
        raise ValueError("Unexpected review-contract schema")
    _exact_keys(contract, ("schema", "goal_id", "source_queue_sha256", "items"), "review contract")
    if contract.get("source_queue_sha256") != queue_sha256:
        raise ValueError("Review contract is not bound to the source queue")
    queue_items = queue.get("items")
    rows = contract.get("items")
    if not isinstance(queue_items, list) or not isinstance(rows, list):
        raise ValueError("Queue and contract items must be arrays")
    if len(rows) != len(queue_items) or not rows:
        raise ValueError("Review contract must cover every queued item exactly once")
    queue_ids = [item.get("review_id") for item in queue_items if isinstance(item, dict)]
    contract_ids = [item.get("review_id") for item in rows if isinstance(item, dict)]
    if len(queue_ids) != len(queue_items) or contract_ids != queue_ids:
        raise ValueError("Review contract order or identifiers changed")
    if len(set(queue_ids)) != len(queue_ids):
        raise ValueError("Source queue contains duplicate review identifiers")
    bounds = {}
    for row in rows:
        _mapping(row, "review-contract item")
        _exact_keys(row, ("review_id", "preview_first", "preview_last"), "review-contract item")
        first = _whole_frame(row.get("preview_first"), "preview_first")
        last = _whole_frame(row.get("preview_last"), "preview_last")
        if first < 0 or first > last:
            raise ValueError("Review contract contains invalid preview bounds")
        bounds[row["review_id"]] = (first, last)
    return queue_items, bounds


def validate_review(document, queue, queue_sha256, contract):
    """Return a normalized reviewed-label artifact and a compact report.

    Validation is all-or-nothing: partial, duplicate, reordered, anonymous, or
    out-of-preview reviews are rejected. Accepted labels remain human-reviewed
    observations; the result never calls them physical ground truth.
    """
    document = _mapping(document, "review export")
    _exact_keys(
        document,
        (
            "schema",
            "complete",
            "source_queue_sha256",
            "review_contract_sha256",
            "session_started_utc",
            "exported_utc",
            "reviewer",
            "items",
        ),
        "review export",
    )
    if document.get("schema") != SCHEMA:
        raise ValueError("Unexpected review-export schema")
    if document.get("complete") is not True:
        raise ValueError("Only a completed review export is admissible")
    if document.get("source_queue_sha256") != queue_sha256:
        raise ValueError("Review export source-queue binding failed")
    contract_sha = digest_document(contract)
    if document.get("review_contract_sha256") != contract_sha:
        raise ValueError("Review export contract binding failed")
    session_started_utc, session_started_at = _utc_timestamp(
        document.get("session_started_utc"), "session_started_utc"
    )
    exported_utc, exported_at = _utc_timestamp(document.get("exported_utc"))
    if exported_at < session_started_at:
        raise ValueError("exported_utc precedes session_started_utc")
    reviewer = _mapping(document.get("reviewer"), "reviewer")
    _exact_keys(reviewer, ("code", "experience", "independent_animator"), "reviewer")
    reviewer_code = _clean_text(reviewer.get("code"), "reviewer code", minimum=2, maximum=80)
    experience = reviewer.get("experience")
    if experience not in EXPERIENCE:
        raise ValueError("Reviewer experience is missing or unsupported")
    if reviewer.get("independent_animator") is not True:
        raise ValueError("Independent-animator self-attestation is required")

    queue_items, bounds = validate_contract(contract, queue, queue_sha256)
    reviews = document.get("items")
    if not isinstance(reviews, list) or len(reviews) != len(queue_items):
        raise ValueError("Completed export must contain every queued review")
    expected_ids = [item["review_id"] for item in queue_items]
    actual_ids = [item.get("review_id") for item in reviews if isinstance(item, dict)]
    if len(actual_ids) != len(reviews) or actual_ids != expected_ids:
        raise ValueError("Review identifiers must be unique and retain exact queue order")

    normalized_rows = []
    counts = Counter()
    for source, review in zip(queue_items, reviews):
        _mapping(review, "review item")
        _exact_keys(
            review,
            (
                "review_id",
                "verdict",
                "corrected_start",
                "corrected_end",
                "intent",
                "notes",
                "reviewed_utc",
            ),
            "review item",
        )
        review_id = source["review_id"]
        verdict = review.get("verdict")
        if verdict not in VERDICTS:
            raise ValueError(f"{review_id} has no supported verdict")
        start = _whole_frame(review.get("corrected_start"), f"{review_id} corrected_start")
        end = _whole_frame(review.get("corrected_end"), f"{review_id} corrected_end")
        first, last = bounds[review_id]
        if not first <= start <= end <= last:
            raise ValueError(f"{review_id} corrected interval is outside its reviewed preview")
        intent = review.get("intent")
        if intent not in INTENTS:
            raise ValueError(f"{review_id} has no supported intent")
        notes = _clean_text(review.get("notes", ""), f"{review_id} notes")
        reviewed_utc, reviewed_at = _utc_timestamp(
            review.get("reviewed_utc"), f"{review_id} reviewed_utc"
        )
        if not session_started_at <= reviewed_at <= exported_at:
            raise ValueError(f"{review_id} reviewed_utc is outside the review session")
        counts[verdict] += 1
        normalized_rows.append(
            {
                "review_id": review_id,
                "clip": source["clip"],
                "subject": source["subject"],
                "kind": source["kind"],
                "proposed_start": source["start"],
                "proposed_end": source["end"],
                "reviewed_start": start,
                "reviewed_end": end,
                "verdict": verdict,
                "intent": intent,
                "notes": notes,
                "reviewed_utc": reviewed_utc,
                "source_provenance": source.get("provenance"),
                "review_provenance": "human_self_attested_independent_animator",
                "physical_ground_truth": False,
            }
        )

    normalized = {
        "schema": "b4ml-validated-motion-labels-v2",
        "goal_id": queue.get("goal_id"),
        "source_queue_sha256": queue_sha256,
        "review_contract_sha256": contract_sha,
        "source_export_sha256": digest_document(document),
        "session_started_utc": session_started_utc,
        "exported_utc": exported_utc,
        "reviewer": {
            "code": reviewer_code,
            "experience": experience,
            "independent_animator_self_attested": True,
        },
        "items": normalized_rows,
        "reviewed_items": len(normalized_rows),
        "verdict_counts": {name: counts[name] for name in sorted(VERDICTS)},
        "human_review_self_attested": True,
        "human_identity_verified": False,
        "physical_ground_truth": False,
        "model_training_authorized": False,
    }
    report = {
        "schema": "b4ml-motion-label-review-validation-v2",
        "valid": True,
        "complete": True,
        "reviewed_items": len(normalized_rows),
        "expected_items": len(queue_items),
        "verdict_counts": normalized["verdict_counts"],
        "queue_order_exact": True,
        "queue_binding_valid": True,
        "contract_binding_valid": True,
        "timestamp_order_valid": True,
        "independent_animator_self_attested": True,
        "human_identity_verified": False,
        "physical_ground_truth": False,
        "model_training_authorized": False,
    }
    return normalized, report
