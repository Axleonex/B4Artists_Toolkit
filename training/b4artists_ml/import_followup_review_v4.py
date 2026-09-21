"""Strict validation for Axlbot's review-directed repair-2 assessment.

The review is non-blind evidence about the exact v19 repair-2 packet.  It can
direct another procedural iteration, but it never authorizes training or model
promotion.  A raw yes/no flag is retained, while qualified acceptance also
requires non-contradictory scores and preference evidence.
"""
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
TRAIN = ROOT / "training/b4artists_ml"
REVIEW = TRAIN / "results/review-directed-followup-reviewer-v4"
EXPORT = TRAIN / "results/human-review-exports/b4ml-review-directed-followup-human-review-v4-axlbot.json"
PRIOR_REVIEW = TRAIN / "results/human-review-exports/b4ml-review-directed-followup-human-review-v3-axlbot.json"
FOCUSED = TRAIN / "results/procedural-vertical-slice-v19-repair2-focused.json"
DISPLAY_AUDIT = TRAIN / "results/review-directed-followup-reviewer-v4-display-audit/receipt.json"
CAPTURE_HASH = "e0e2f2dbb23983b29e006b6445c09bbe29a37283ffda95650b77343c058a5e37"


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
    display_audit = read(DISPLAY_AUDIT)

    if value.get("schema") != "b4ml-review-directed-followup-human-review-v4":
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
    if value.get("source_qualification_sha256") != data.get("source_qualification_sha256"):
        raise ValueError("Stale qualification identity")
    if value["source_qualification_sha256"] != manifest.get("focused_sha256"):
        raise ValueError("Manifest/qualification identity mismatch")
    if value["source_qualification_sha256"] != sha(FOCUSED):
        raise ValueError("Stale repair-2 qualification receipt")
    if value.get("source_human_review_sha256") != data.get("source_human_review_sha256"):
        raise ValueError("Stale parent human-review identity")
    if value["source_human_review_sha256"] != manifest.get("source_human_review_sha256"):
        raise ValueError("Manifest/parent review identity mismatch")
    if value["source_human_review_sha256"] != sha(PRIOR_REVIEW):
        raise ValueError("Stale parent human-review receipt")
    if value.get("reviewer") != {"id": "Axlbot", "experience": "10+ years"}:
        raise ValueError("Unexpected reviewer metadata")
    if (
        display_audit.get("complete") is not True
        or display_audit.get("source_data_sha256") != value["source_data_sha256"]
        or display_audit.get("native_comparisons") != 16
        or display_audit.get("v4_global_motion_representation_qualified") is not False
        or display_audit.get("relative_pose_feedback_qualified") is not True
        or display_audit.get("maximum_native_instance_error", 1.0) > 2e-6
    ):
        raise ValueError("Unqualified display-audit receipt")

    exported = datetime.fromisoformat(value["exported_utc"].replace("Z", "+00:00"))
    cases = value.get("cases", [])
    expected = {case["id"]: case for case in data["cases"]}
    if len(cases) != 8 or len({case["id"] for case in cases}) != 8:
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
            raise ValueError("Expected original locked non-blind rating")
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
        mapped_preference = (
            "candidate"
            if preference == candidate
            else "baseline"
            if preference == baseline
            else preference
        )
        candidate_scores = [
            int(values[dimension + candidate])
            for dimension in ("naturalness", "contact", "continuity", "intent")
        ]
        raw_acceptance = values["acceptable" + candidate] == "yes"
        qualified_acceptance = (
            raw_acceptance
            and mapped_preference in {"candidate", "tie"}
            and min(candidate_scores) >= 3
        )
        summary.append(
            dict(
                id=case["id"],
                candidate_acceptable=raw_acceptance,
                candidate_qualified_acceptance=qualified_acceptance,
                candidate_acceptance_consistent=(raw_acceptance == qualified_acceptance),
                baseline_acceptable=values["acceptable" + baseline] == "yes",
                candidate_scores=candidate_scores,
                preference=mapped_preference,
                notes=values["notes"],
            )
        )

    if require_capture and canonical_hash(value) != CAPTURE_HASH:
        raise ValueError("Human capture differs from visible browser export")
    result = dict(
        schema="b4ml-human-review-summary-v4",
        complete=True,
        cases=summary,
        candidate_acceptable=sum(case["candidate_acceptable"] for case in summary),
        candidate_qualified_acceptance=sum(case["candidate_qualified_acceptance"] for case in summary),
        acceptance_contradictions=sum(
            not case["candidate_acceptance_consistent"] for case in summary
        ),
        baseline_acceptable=sum(case["baseline_acceptable"] for case in summary),
        preferences={
            key: sum(case["preference"] == key for case in summary)
            for key in ("candidate", "baseline", "tie", "neither")
        },
        export_sha256=sha(EXPORT),
        canonical_capture_sha256=CAPTURE_HASH,
        display_audit_sha256=sha(DISPLAY_AUDIT),
        identity_receipt="not established by reviewer display name",
        prior_exposure=True,
        training_authorized=False,
        model_promotion_authorized=False,
        full_goal_complete=False,
        display_representation_qualified=False,
        relative_pose_feedback_qualified=True,
        global_motion_feedback_qualified=False,
        jump_height_feedback_qualified=False,
        production_acceptance_qualified=False,
        scope=(
            "Non-blind ratings describe the v4 page, whose legacy extraction omitted native "
            "motion-instance transforms. Relative-pose feedback remains usable; global motion, "
            "jump height, and production acceptance do not qualify. Contradictory acceptance "
            "is retained but cannot qualify a candidate."
        ),
    )
    if (result["candidate_acceptable"], result["candidate_qualified_acceptance"], result["baseline_acceptable"]) != (1, 0, 0):
        raise ValueError("Unexpected acceptance summary")
    if result["acceptance_contradictions"] != 1:
        raise ValueError("Unexpected acceptance contradiction count")
    if result["preferences"] != {"candidate": 0, "baseline": 0, "tie": 0, "neither": 8}:
        raise ValueError("Unexpected preference summary")
    return result


if __name__ == "__main__":
    result = validate()
    destination = REVIEW / "human-review-summary-v4-display-audited.json"
    with destination.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2, allow_nan=False)
    print(json.dumps(result, indent=2))
