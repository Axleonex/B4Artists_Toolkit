"""Strictly import Axlbot's one-case v58 Rigify jitter follow-up."""
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
TRAIN = ROOT / "training/b4artists_ml"
REVIEW = TRAIN / "results/review-directed-followup-reviewer-v11"
EXPORT = TRAIN / "results/human-review-exports/b4ml-review-directed-followup-human-review-v11-axlbot.json"
PRIOR_REVIEW = TRAIN / "results/human-review-exports/b4ml-review-directed-followup-human-review-v9-axlbot.json"
FOCUSED = TRAIN / "results/procedural-vertical-slice-v58-rigify-run-final/summary.json"
CAPTURE_HASH = "3a9fef4fd6eff1735aa7682fc09d9a608ddf1237530a2f5c5380ea6567b2bbdb"


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
    return json.loads(
        path.read_text(encoding="utf-8-sig"),
        object_pairs_hook=unique,
        parse_constant=lambda value: (_ for _ in ()).throw(ValueError("Nonfinite JSON: " + value)),
    )


def canonical_hash(value):
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode()
    return hashlib.sha256(encoded).hexdigest()


def validate(value=None, *, require_capture=True):
    value = read(EXPORT) if value is None else value
    data = read(REVIEW / "review-data.json")
    manifest = read(REVIEW / "manifest.json")
    required = {
        "complete": True,
        "human_authored": True,
        "prior_exposure": True,
        "native_display_validated": True,
        "training_authorized": False,
        "model_promotion_authorized": False,
    }
    if value.get("schema") != "b4ml-review-directed-followup-human-review-v11":
        raise ValueError("Wrong review schema")
    if any(value.get(key) is not expected for key, expected in required.items()):
        raise ValueError("Invalid authorization or completion field")
    if manifest.get("schema") != "b4ml-review-directed-followup-reviewer-manifest-v11":
        raise ValueError("Wrong reviewer manifest schema")
    if value.get("source_data_sha256") != sha(REVIEW / "review-data.json"):
        raise ValueError("Stale review data")
    if manifest.get("data_sha256") != value["source_data_sha256"]:
        raise ValueError("Manifest/data identity mismatch")
    if manifest.get("html_sha256") != sha(REVIEW / "reviewer.html"):
        raise ValueError("Reviewer HTML identity mismatch")
    if value.get("source_qualification_sha256") != data.get("source_qualification_sha256"):
        raise ValueError("Stale qualification identity")
    if value["source_qualification_sha256"] != manifest.get("focused_sha256") or value["source_qualification_sha256"] != sha(FOCUSED):
        raise ValueError("Stale v58 qualification receipt")
    if value.get("source_human_review_sha256") != data.get("source_human_review_sha256"):
        raise ValueError("Stale parent review identity")
    if value["source_human_review_sha256"] != manifest.get("source_human_review_sha256") or value["source_human_review_sha256"] != sha(PRIOR_REVIEW):
        raise ValueError("Stale parent human-review receipt")
    if value.get("reviewer") != {"id": "Axlbot", "experience": "10+ years"}:
        raise ValueError("Unexpected reviewer metadata")
    if not (
        manifest.get("complete") is True
        and manifest.get("cases") == 1
        and manifest.get("variants") == 2
        and manifest.get("candidate_as_A") == 0
        and manifest.get("candidate_as_B") == 1
        and manifest.get("native_display_validated") is True
        and manifest.get("maximum_native_instance_error", 1.0) <= 2e-6
        and data.get("native_display_validated") is True
        and data.get("prior_exposure") is True
    ):
        raise ValueError("Unqualified native-display reviewer packet")

    exported = datetime.fromisoformat(value["exported_utc"].replace("Z", "+00:00"))
    cases = value.get("cases", [])
    expected = {case["id"]: case for case in data["cases"]}
    if len(cases) != 1 or cases[0].get("id") != "rigify_basic/run":
        raise ValueError("Missing or unexpected case")
    dimensions = ("naturalness", "contact", "continuity", "intent")
    case = cases[0]
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
            if values.get(dimension + label) not in {"1", "2", "3", "4", "5"}:
                raise ValueError("Missing or invalid score")
    for label in ("A", "B"):
        if values.get("acceptable" + label) not in {"yes", "no"}:
            raise ValueError("Missing acceptability")
        failures = rating.get("failures", {}).get(label)
        if not isinstance(failures, list) or not all(isinstance(item, str) and item for item in failures):
            raise ValueError("Invalid failure tags")
        for field in ("corrections", "interactions"):
            estimate = values.get(field + label)
            if not isinstance(estimate, str) or (estimate and not re.fullmatch(r"\d{1,3}", estimate)):
                raise ValueError("Invalid optional estimate")
        blend = (ROOT / identity[label]["blend_path"]).resolve()
        if (
            not blend.is_relative_to(ROOT.resolve())
            or sha(blend) != identity[label]["blend_sha256"]
            or sha(blend.parent / "report.json") != identity[label]["report_sha256"]
        ):
            raise ValueError("Stale or out-of-scope native scene identity")
    if values.get("preference") not in {"A", "B", "tie", "neither"}:
        raise ValueError("Invalid preference")
    if not isinstance(values.get("notes"), str):
        raise ValueError("Invalid notes")

    candidate = next(label for label, item in identity.items() if item["variant"] == "candidate")
    baseline = "B" if candidate == "A" else "A"
    preference = values["preference"]
    mapped = "candidate" if preference == candidate else "baseline" if preference == baseline else preference
    candidate_scores = [int(values[dimension + candidate]) for dimension in dimensions]
    baseline_scores = [int(values[dimension + baseline]) for dimension in dimensions]
    candidate_failures = rating["failures"][candidate]
    raw_acceptance = values["acceptable" + candidate] == "yes"
    qualified = raw_acceptance and mapped in {"candidate", "tie"} and min(candidate_scores) >= 3 and not candidate_failures
    summary_case = {
        "id": case["id"],
        "candidate_label": candidate,
        "candidate_acceptable": raw_acceptance,
        "candidate_qualified_acceptance": qualified,
        "candidate_acceptance_consistent": raw_acceptance == qualified,
        "baseline_acceptable": values["acceptable" + baseline] == "yes",
        "candidate_scores": candidate_scores,
        "baseline_scores": baseline_scores,
        "candidate_failures": candidate_failures,
        "candidate_score_deltas": [a - b for a, b in zip(candidate_scores, baseline_scores)],
        "preference": mapped,
        "corrections": int(values["corrections" + candidate]) if values["corrections" + candidate] else None,
        "interactions": int(values["interactions" + candidate]) if values["interactions" + candidate] else None,
        "notes": values["notes"],
    }
    if require_capture and canonical_hash(value) != CAPTURE_HASH:
        raise ValueError("Human capture differs from visible browser state")
    if summary_case != {
        "id": "rigify_basic/run",
        "candidate_label": "B",
        "candidate_acceptable": True,
        "candidate_qualified_acceptance": True,
        "candidate_acceptance_consistent": True,
        "baseline_acceptable": True,
        "candidate_scores": [4, 4, 4, 5],
        "baseline_scores": [4, 3, 1, 5],
        "candidate_failures": [],
        "candidate_score_deltas": [0, 1, 3, 0],
        "preference": "candidate",
        "corrections": 0,
        "interactions": 0,
        "notes": "Knees on candidate A snap too sharply per step. ",
    }:
        raise ValueError("Unexpected human-rating summary")
    result = {
        "schema": "b4ml-human-review-summary-v11",
        "complete": True,
        "cases": [summary_case],
        "candidate_acceptable": 1,
        "candidate_qualified_acceptance": 1,
        "acceptance_contradictions": 0,
        "baseline_acceptable": 1,
        "preferences": {"candidate": 1, "baseline": 0, "tie": 0, "neither": 0},
        "dimension_comparison": {
            "naturalness": {"wins": 0, "ties": 1, "losses": 0},
            "contact": {"wins": 1, "ties": 0, "losses": 0},
            "continuity": {"wins": 1, "ties": 0, "losses": 0},
            "intent": {"wins": 0, "ties": 1, "losses": 0},
        },
        "export_sha256": sha(EXPORT),
        "canonical_capture_sha256": CAPTURE_HASH,
        "reviewer_manifest_sha256": sha(REVIEW / "manifest.json"),
        "identity_receipt": "not established by reviewer display name",
        "prior_exposure": True,
        "training_authorized": False,
        "model_promotion_authorized": False,
        "cascadeur_connector_authorized": False,
        "full_goal_complete": False,
        "production_acceptance_qualified": True,
        "production_candidates_accepted": 1,
        "preserve_exact_cases": ["boneforge/run@v54", "rigify_basic/run@v58"],
        "next_action": (
            "Preserve the accepted BoneForge v54 and Rigify v58 runs exactly. Continue only remaining "
            "non-human production-character and fail-closed temporal evaluation work; do not train or promote."
        ),
        "scope": (
            "Non-blind review qualifies the exact Rigify v58 run against its v54 baseline. It does not "
            "establish reviewer identity, authorize training or promotion, or qualify Cascadeur work."
        ),
    }
    return result


if __name__ == "__main__":
    destination = REVIEW / "human-review-summary-v11-native-display.json"
    with destination.open("x", encoding="utf-8") as stream:
        json.dump(validate(), stream, indent=2, allow_nan=False)
        stream.write("\n")
    print(destination)
