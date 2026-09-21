"""Strict, read-only validation of the corrected-display Axlbot review.

The ten ratings are evidence about the exact native-display v3 packet.  They do
not authorize training or model promotion and are explicitly non-blind because
the reviewer had already seen the underlying v15/v17/v18 comparisons.
"""
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
TRAIN = ROOT / "training/b4artists_ml"
REVIEW = TRAIN / "results/review-directed-followup-reviewer-v3"
EXPORT = TRAIN / "results/human-review-exports/b4ml-review-directed-followup-human-review-v3-axlbot.json"
CAPTURE_HASH = "828f601c88bc6fe8eae07362d6fb418c9eba0bdaf8d4660548156fd746bda60f"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("Duplicate JSON key: " + key)
            result[key] = value
        return result

    def invalid(value):
        raise ValueError("Nonfinite JSON: " + value)

    return json.loads(
        path.read_text(encoding="utf-8-sig"),
        object_pairs_hook=unique,
        parse_constant=invalid,
    )


def canonical_hash(value):
    encoded = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode()
    return hashlib.sha256(encoded).hexdigest()


def validate(value=None, *, require_capture=True):
    value = read(EXPORT) if value is None else value
    data = read(REVIEW / "review-data.json")
    manifest = read(REVIEW / "manifest.json")
    recovery = read(REVIEW / "display-recovery.json")

    if value.get("schema") != "b4ml-review-directed-followup-human-review-v3":
        raise ValueError("Wrong review schema")
    for key, expected in (
        ("complete", True),
        ("human_authored", True),
        ("prior_exposure", True),
        ("training_authorized", False),
        ("model_promotion_authorized", False),
    ):
        if value.get(key) is not expected:
            raise ValueError("Invalid authorization/completion field: " + key)
    if value.get("source_data_sha256") != sha(REVIEW / "review-data.json"):
        raise ValueError("Stale review data")
    if manifest.get("data_sha256") != value["source_data_sha256"]:
        raise ValueError("Manifest/data identity mismatch")
    if manifest.get("recovery_sha256") != sha(REVIEW / "display-recovery.json"):
        raise ValueError("Stale display-recovery receipt")
    if value.get("source_qualification_sha256") != data.get("source_qualification_sha256"):
        raise ValueError("Stale qualification identity")
    if value["source_qualification_sha256"] != sha(TRAIN / "results/procedural-vertical-slice-v18-focused.json"):
        raise ValueError("Stale qualification receipt")
    if value.get("source_display_recovery_sha256") != data.get("source_display_recovery_sha256"):
        raise ValueError("Stale display-recovery identity")
    if value["source_display_recovery_sha256"] != canonical_hash(recovery["evidence"]):
        raise ValueError("Display-recovery evidence changed")
    if value.get("reviewer") != {"id": "Axlbot", "experience": "10+ years"}:
        raise ValueError("Unexpected reviewer metadata")

    exported = datetime.fromisoformat(value["exported_utc"].replace("Z", "+00:00"))
    cases = value.get("cases", [])
    expected = {case["id"]: case for case in data["cases"]}
    if len(cases) != 10 or len({case["id"] for case in cases}) != 10:
        raise ValueError("Missing or duplicate cases")
    if set(expected) != {case["id"] for case in cases}:
        raise ValueError("Unexpected case identity")

    summary = []
    for case in cases:
        rating = case["rating"]
        identity = expected[case["id"]]["reveal"]
        if case.get("revealed_identity") != identity:
            raise ValueError("Changed revealed identity mapping")
        if (
            rating.get("locked") is not True
            or rating.get("blind_at_rating") is not False
            or rating.get("reveal_seen") is not True
            or rating.get("history")
        ):
            raise ValueError("Expected original locked non-blind corrected-display rating")
        if datetime.fromisoformat(rating["locked_utc"].replace("Z", "+00:00")) > exported:
            raise ValueError("Lock after export")
        values = rating["values"]
        for dimension in ("naturalness", "contact", "continuity", "intent"):
            for label in ("A", "B"):
                if values.get(dimension + label) not in ("1", "2", "3", "4", "5"):
                    raise ValueError("Missing/invalid score")
        for label in ("A", "B"):
            if values.get("acceptable" + label) not in ("yes", "no"):
                raise ValueError("Missing acceptability")
            for field in ("corrections", "interactions"):
                estimate = values.get(field + label)
                if not isinstance(estimate, str) or (
                    estimate != "" and not re.fullmatch(r"\d{1,3}", estimate)
                ):
                    raise ValueError("Invalid optional estimate")
            blend = (ROOT / identity[label]["blend_path"]).resolve()
            if (
                not blend.is_relative_to(ROOT.resolve())
                or sha(blend) != identity[label]["blend_sha256"]
                or sha(blend.parent / "report.json") != identity[label]["report_sha256"]
            ):
                raise ValueError("Stale/out-of-scope native scene identity")
        if values.get("preference") not in ("A", "B", "tie", "neither"):
            raise ValueError("Invalid preference")
        if not isinstance(values.get("notes"), str):
            raise ValueError("Invalid notes")
        candidate = next(label for label, item in identity.items() if item["variant"] == "candidate")
        baseline = "B" if candidate == "A" else "A"
        preference = values["preference"]
        summary.append(
            dict(
                id=case["id"],
                candidate_acceptable=values["acceptable" + candidate] == "yes",
                baseline_acceptable=values["acceptable" + baseline] == "yes",
                preference=(
                    "candidate"
                    if preference == candidate
                    else "baseline"
                    if preference == baseline
                    else preference
                ),
                notes=values["notes"],
            )
        )

    if require_capture and canonical_hash(value) != CAPTURE_HASH:
        raise ValueError("Human capture differs from visible browser export")
    result = dict(
        schema="b4ml-human-review-summary-v3",
        complete=True,
        cases=summary,
        candidate_acceptable=sum(case["candidate_acceptable"] for case in summary),
        baseline_acceptable=sum(case["baseline_acceptable"] for case in summary),
        preferences={
            key: sum(case["preference"] == key for case in summary)
            for key in ("candidate", "baseline", "tie", "neither")
        },
        export_sha256=sha(EXPORT),
        canonical_capture_sha256=CAPTURE_HASH,
        display_recovery_sha256=sha(REVIEW / "display-recovery.json"),
        identity_receipt="not established by reviewer display name",
        prior_exposure=True,
        training_authorized=False,
        model_promotion_authorized=False,
        full_goal_complete=False,
        scope="Ratings describe the exact native-display v3 packet; they are non-blind and do not authorize training.",
    )
    if (result["candidate_acceptable"], result["baseline_acceptable"]) != (2, 2):
        raise ValueError("Unexpected acceptance summary")
    if result["preferences"] != {"candidate": 1, "baseline": 0, "tie": 2, "neither": 7}:
        raise ValueError("Unexpected preference summary")
    return result


if __name__ == "__main__":
    result = validate()
    destination = REVIEW / "human-review-summary-v3.json"
    with destination.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2, allow_nan=False)
    print(json.dumps(result, indent=2))
