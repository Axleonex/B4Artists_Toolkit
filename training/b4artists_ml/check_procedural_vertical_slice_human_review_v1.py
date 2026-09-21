"""Validate and summarize a completed human export from the v12 review packet."""
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime
import hashlib
import json
import math
import os
import sys


HERE = Path(__file__).resolve()
TRAIN = HERE.parent
BUILD = TRAIN / "results/procedural-vertical-slice-reviewer-v1"
DATA_PATH = BUILD / "review-data.json"
OUT = BUILD / "human-review-summary-v1.json"
DIMENSIONS = ("naturalness", "contact", "continuity", "intent")
SIDES = ("A", "B")
EXPERIENCE = {"Student", "0-2 years", "3-5 years", "6-10 years", "10+ years"}
FAILURES = {"foot_slide", "penetration", "popping", "stretch", "timing", "balance", "intent_loss", "other"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_time(value, label):
    if not isinstance(value, str):
        raise ValueError("Missing " + label)
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("Invalid " + label) from exc
    if parsed.tzinfo is None:
        raise ValueError(label + " must include a timezone")
    return value


def validate(review, data):
    if review.get("schema") != "b4ml-procedural-vertical-slice-human-review-v1":
        raise ValueError("Unsupported human review schema")
    if review.get("source_data_sha256") != sha(DATA_PATH):
        raise ValueError("Human review does not match the frozen reviewer data")
    if review.get("source_aggregate_sha256") != data["aggregate_sha256"] or review.get("source_protocol_sha256") != data["protocol_sha256"]:
        raise ValueError("Human review source identity changed")
    reviewer = review.get("reviewer")
    if not isinstance(reviewer, dict) or not isinstance(reviewer.get("id"), str) or not reviewer["id"].strip() or len(reviewer["id"]) > 200:
        raise ValueError("A bounded reviewer ID or anonymous code is required")
    if reviewer.get("experience") not in EXPERIENCE:
        raise ValueError("Unknown reviewer experience category")
    parse_time(review.get("exported_utc"), "export timestamp")
    if review.get("human_authored") is not True:
        raise ValueError("Review must be explicitly human-authored")
    cases = review.get("cases")
    if not isinstance(cases, list) or len(cases) != len(data["cases"]):
        raise ValueError("A complete 32-case review is required")
    expected_ids = [case["id"] for case in data["cases"]]
    if [case.get("id") for case in cases] != expected_ids:
        raise ValueError("Review case order or identity changed")
    normalized = []
    for submitted, source in zip(cases, data["cases"]):
        if submitted.get("source_blend_sha256") != source["source_blend_sha256"]:
            raise ValueError("Review scene hash mismatch: " + source["id"])
        if submitted.get("revealed_identity") != source["reveal"]:
            raise ValueError("Review method reveal changed: " + source["id"])
        rating = submitted.get("rating")
        if not isinstance(rating, dict) or rating.get("locked") is not True:
            raise ValueError("Unlocked case in completed review: " + source["id"])
        parse_time(rating.get("locked_utc"), "case lock timestamp")
        values = rating.get("values")
        expected_fields = {dimension + side for dimension in DIMENSIONS for side in SIDES}
        expected_fields |= {"acceptableA", "acceptableB", "correctionsA", "correctionsB",
                            "interactionsA", "interactionsB", "preference", "notes"}
        if not isinstance(values, dict) or set(values) != expected_fields:
            raise ValueError("Rating fields changed: " + source["id"])
        row = dict(id=source["id"], methods={})
        for side in SIDES:
            scores = {}
            for dimension in DIMENSIONS:
                value = values[dimension + side]
                if value not in {"1", "2", "3", "4", "5"}:
                    raise ValueError(f"Invalid {dimension} score: {source['id']} {side}")
                scores[dimension] = int(value)
            if values["acceptable" + side] not in {"yes", "no"}:
                raise ValueError("Invalid production acceptability")
            counts = {}
            for name in ("corrections", "interactions"):
                raw = values[name + side]
                try:
                    number = int(raw)
                except (TypeError, ValueError) as exc:
                    raise ValueError(f"Invalid {name}: {source['id']} {side}") from exc
                if str(number) != str(raw) or not 0 <= number <= 999:
                    raise ValueError(f"Out-of-range {name}: {source['id']} {side}")
                counts[name] = number
            tags = rating.get("failures", {}).get(side)
            if not isinstance(tags, list) or len(tags) != len(set(tags)) or not set(tags) <= FAILURES:
                raise ValueError("Invalid visible failure tags")
            kind = source["reveal"][side]["kind"]
            row["methods"][kind] = dict(scores=scores, acceptable=values["acceptable" + side] == "yes",
                                         corrections=counts["corrections"], interactions=counts["interactions"],
                                         failures=tags)
        preference = values["preference"]
        if preference not in {"A", "B", "tie", "neither"}:
            raise ValueError("Invalid overall preference")
        row["preference"] = source["reveal"][preference]["kind"] if preference in SIDES else preference
        if not isinstance(values["notes"], str) or len(values["notes"]) > 10000:
            raise ValueError("Review notes must be bounded text")
        row["notes"] = values["notes"]
        normalized.append(row)
    return reviewer, normalized


def summarize(reviewer, rows, source_review):
    buckets = {kind: dict(scores=defaultdict(list), acceptable=[], corrections=[], interactions=[], failures=Counter())
               for kind in ("pre_contact", "corrected")}
    preferences = Counter()
    for row in rows:
        preferences[row["preference"]] += 1
        for kind, result in row["methods"].items():
            for name, value in result["scores"].items():
                buckets[kind]["scores"][name].append(value)
            buckets[kind]["acceptable"].append(result["acceptable"])
            buckets[kind]["corrections"].append(result["corrections"])
            buckets[kind]["interactions"].append(result["interactions"])
            buckets[kind]["failures"].update(result["failures"])
    methods = {}
    for kind, bucket in buckets.items():
        methods[kind] = dict(
            mean_scores={name: sum(values) / len(values) for name, values in bucket["scores"].items()},
            acceptable_cases=sum(bucket["acceptable"]),
            unacceptable_cases=len(bucket["acceptable"]) - sum(bucket["acceptable"]),
            mean_estimated_corrections=sum(bucket["corrections"]) / len(bucket["corrections"]),
            mean_estimated_interactions=sum(bucket["interactions"]) / len(bucket["interactions"]),
            visible_failure_tags=dict(bucket["failures"]),
        )
    return dict(
        schema="b4ml-procedural-vertical-slice-human-review-summary-v1",
        complete=True,
        human_review_export_validated=True,
        reviewer=reviewer,
        cases=len(rows),
        preferences=dict(preferences),
        methods=methods,
        source_review_sha256=sha(source_review),
        source_data_sha256=sha(DATA_PATH),
        checker_sha256=sha(HERE),
        cascadeur_comparison=False,
        full_goal_complete=False,
    )


def main():
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python check_procedural_vertical_slice_human_review_v1.py <exported-review.json>")
    if OUT.exists():
        raise RuntimeError("Validated human review summary already exists")
    source_review = Path(sys.argv[1]).resolve()
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    review = json.loads(source_review.read_text(encoding="utf-8-sig"))
    reviewer, rows = validate(review, data)
    report = summarize(reviewer, rows, source_review)
    temp = OUT.with_suffix(".tmp")
    temp.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    os.replace(temp, OUT)
    print(json.dumps(report, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
