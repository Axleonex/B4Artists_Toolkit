"""Strictly import Axlbot's native-display v21 repair-2 versus v20 follow-up.

The review can qualify visual feedback and production acceptance for the exact
native-display packet.  It cannot establish reviewer identity or authorize
training, model promotion, or Cascadeur work.  Acceptance remains fail-closed:
a raw ``yes`` also requires non-contradictory scores and preference.
"""
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
TRAIN = ROOT / "training/b4artists_ml"
REVIEW = TRAIN / "results/review-directed-followup-reviewer-v6"
EXPORT = TRAIN / "results/human-review-exports/b4ml-review-directed-followup-human-review-v6-axlbot.json"
PRIOR_REVIEW = TRAIN / "results/human-review-exports/b4ml-review-directed-followup-human-review-v5-axlbot.json"
FOCUSED = TRAIN / "results/procedural-vertical-slice-v21-repair2-focused.json"
CAPTURE_HASH = "319baccef09bd11b242766e1526ce351dabe9be41764475e7d76ecb3565dbc91"


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

    if value.get("schema") != "b4ml-review-directed-followup-human-review-v6":
        raise ValueError("Wrong review schema")
    for key, expected in (
        ("complete", True),
        ("human_authored", True),
        ("prior_exposure", True),
        ("native_display_validated", True),
        ("training_authorized", False),
        ("model_promotion_authorized", False),
    ):
        if value.get(key) is not expected:
            raise ValueError("Invalid authorization/completion field: " + key)
    if manifest.get("schema") != "b4ml-review-directed-followup-reviewer-manifest-v6":
        raise ValueError("Wrong reviewer manifest schema")
    if value.get("source_data_sha256") != sha(REVIEW / "review-data.json"):
        raise ValueError("Stale review data")
    if manifest.get("data_sha256") != value["source_data_sha256"]:
        raise ValueError("Manifest/data identity mismatch")
    if manifest.get("html_sha256") != sha(REVIEW / "reviewer.html"):
        raise ValueError("Reviewer HTML identity mismatch")
    if value.get("source_qualification_sha256") != data.get("source_qualification_sha256"):
        raise ValueError("Stale qualification identity")
    if value["source_qualification_sha256"] != manifest.get("focused_sha256"):
        raise ValueError("Manifest/qualification identity mismatch")
    if value["source_qualification_sha256"] != sha(FOCUSED):
        raise ValueError("Stale v21 repair-2 qualification receipt")
    if value.get("source_human_review_sha256") != data.get("source_human_review_sha256"):
        raise ValueError("Stale parent human-review identity")
    if value["source_human_review_sha256"] != manifest.get("source_human_review_sha256"):
        raise ValueError("Manifest/parent review identity mismatch")
    if value["source_human_review_sha256"] != sha(PRIOR_REVIEW):
        raise ValueError("Stale parent human-review receipt")
    if value.get("reviewer") != {"id": "Axlbot", "experience": "10+ years"}:
        raise ValueError("Unexpected reviewer metadata")
    if (
        manifest.get("complete") is not True
        or manifest.get("cases") != 8
        or manifest.get("variants") != 2
        or manifest.get("candidate_as_A") != 4
        or manifest.get("candidate_as_B") != 4
        or manifest.get("native_display_validated") is not True
        or manifest.get("maximum_native_instance_error", 1.0) > 2e-6
        or data.get("native_display_validated") is not True
        or data.get("prior_exposure") is not True
    ):
        raise ValueError("Unqualified native-display reviewer packet")

    exported = datetime.fromisoformat(value["exported_utc"].replace("Z", "+00:00"))
    cases = value.get("cases", [])
    expected = {case["id"]: case for case in data["cases"]}
    if len(cases) != 8 or len({case["id"] for case in cases}) != 8:
        raise ValueError("Missing or duplicate cases")
    if set(expected) != {case["id"] for case in cases}:
        raise ValueError("Unexpected case identity")

    summary = []
    dimensions = ("naturalness", "contact", "continuity", "intent")
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
        for dimension in dimensions:
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

        candidate = next(
            label for label, item in identity.items() if item["variant"] == "candidate"
        )
        baseline = "B" if candidate == "A" else "A"
        preference = values["preference"]
        mapped_preference = (
            "candidate"
            if preference == candidate
            else "baseline"
            if preference == baseline
            else preference
        )
        candidate_scores = [int(values[dimension + candidate]) for dimension in dimensions]
        baseline_scores = [int(values[dimension + baseline]) for dimension in dimensions]
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
                baseline_scores=baseline_scores,
                candidate_score_deltas=[
                    candidate_score - baseline_score
                    for candidate_score, baseline_score in zip(
                        candidate_scores, baseline_scores
                    )
                ],
                preference=mapped_preference,
                corrections=int(values["corrections" + candidate])
                if values["corrections" + candidate]
                else None,
                interactions=int(values["interactions" + candidate])
                if values["interactions" + candidate]
                else None,
                notes=values["notes"],
            )
        )

    if require_capture and canonical_hash(value) != CAPTURE_HASH:
        raise ValueError("Human capture differs from visible browser export")
    dimension_comparison = {}
    for index, dimension in enumerate(dimensions):
        deltas = [case["candidate_score_deltas"][index] for case in summary]
        dimension_comparison[dimension] = {
            "wins": sum(delta > 0 for delta in deltas),
            "ties": sum(delta == 0 for delta in deltas),
            "losses": sum(delta < 0 for delta in deltas),
        }
    result = dict(
        schema="b4ml-human-review-summary-v6",
        complete=True,
        cases=summary,
        candidate_acceptable=sum(case["candidate_acceptable"] for case in summary),
        candidate_qualified_acceptance=sum(
            case["candidate_qualified_acceptance"] for case in summary
        ),
        acceptance_contradictions=sum(
            not case["candidate_acceptance_consistent"] for case in summary
        ),
        baseline_acceptable=sum(case["baseline_acceptable"] for case in summary),
        preferences={
            key: sum(case["preference"] == key for case in summary)
            for key in ("candidate", "baseline", "tie", "neither")
        },
        dimension_comparison=dimension_comparison,
        export_sha256=sha(EXPORT),
        canonical_capture_sha256=CAPTURE_HASH,
        reviewer_manifest_sha256=sha(REVIEW / "manifest.json"),
        identity_receipt="not established by reviewer display name",
        prior_exposure=True,
        training_authorized=False,
        model_promotion_authorized=False,
        cascadeur_connector_authorized=False,
        full_goal_complete=False,
        display_representation_qualified=True,
        relative_pose_feedback_qualified=True,
        global_motion_feedback_qualified=True,
        jump_height_feedback_qualified=True,
        production_acceptance_qualified=True,
        production_candidates_accepted=sum(
            case["candidate_qualified_acceptance"] for case in summary
        ),
        next_action=(
            "Preserve the two accepted landing slices. Use the qualified notes for a bounded "
            "jump-impact continuity and run whole-body repair. Do not train or promote a model."
        ),
        scope=(
            "Non-blind ratings compare the exact v21 repair-2 native-display scenes with the "
            "reviewed v20 scenes. The packet qualifies visible global motion, jump height, "
            "relative pose, and production-acceptance feedback. It does not establish reviewer "
            "identity, skin deformation, mesh collision quality, training authorization, model "
            "promotion, or Cascadeur entitlement."
        ),
    )
    expected_counts = (2, 2, 0, 2)
    actual_counts = (
        result["candidate_acceptable"],
        result["candidate_qualified_acceptance"],
        result["acceptance_contradictions"],
        result["baseline_acceptable"],
    )
    if actual_counts != expected_counts:
        raise ValueError("Unexpected acceptance summary")
    if result["preferences"] != {
        "candidate": 1,
        "baseline": 0,
        "tie": 2,
        "neither": 5,
    }:
        raise ValueError("Unexpected preference summary")
    if result["dimension_comparison"] != {
        "naturalness": {"wins": 1, "ties": 7, "losses": 0},
        "contact": {"wins": 0, "ties": 6, "losses": 2},
        "continuity": {"wins": 1, "ties": 7, "losses": 0},
        "intent": {"wins": 0, "ties": 8, "losses": 0},
    }:
        raise ValueError("Unexpected score-delta summary")
    return result


if __name__ == "__main__":
    result = validate()
    destination = REVIEW / "human-review-summary-v6-native-display.json"
    with destination.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2, allow_nan=False)
    print(json.dumps(result, indent=2))
