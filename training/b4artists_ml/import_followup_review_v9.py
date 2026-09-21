"""Strictly import Axlbot's two-case cadence-correct run follow-up."""
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
TRAIN = ROOT / "training/b4artists_ml"
REVIEW = TRAIN / "results/review-directed-followup-reviewer-v9"
EXPORT = TRAIN / "results/human-review-exports/b4ml-review-directed-followup-human-review-v9-axlbot.json"
PRIOR_REVIEW = TRAIN / "results/human-review-exports/b4ml-review-directed-followup-human-review-v8-axlbot.json"
FOCUSED = TRAIN / "results/procedural-vertical-slice-v54-run-final/summary.json"
CAPTURE_HASH = "4313971e75b6d39e9f88ccd38bb11169a26fde58b7327963467676735369dd96"


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
    if value.get("schema") != "b4ml-review-directed-followup-human-review-v9":
        raise ValueError("Wrong review schema")
    if any(value.get(key) is not expected for key, expected in required.items()):
        raise ValueError("Invalid authorization or completion field")
    if manifest.get("schema") != "b4ml-review-directed-followup-reviewer-manifest-v9":
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
        raise ValueError("Stale v54 qualification receipt")
    if value.get("source_human_review_sha256") != data.get("source_human_review_sha256"):
        raise ValueError("Stale parent review identity")
    if value["source_human_review_sha256"] != manifest.get("source_human_review_sha256") or value["source_human_review_sha256"] != sha(PRIOR_REVIEW):
        raise ValueError("Stale parent human-review receipt")
    if value.get("reviewer") != {"id": "Axlbot", "experience": "10+ years"}:
        raise ValueError("Unexpected reviewer metadata")
    if not (
        manifest.get("complete") is True
        and manifest.get("cases") == 2
        and manifest.get("variants") == 2
        and manifest.get("candidate_as_A") == 1
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
    if len(cases) != 2 or len({case.get("id") for case in cases}) != 2:
        raise ValueError("Missing or duplicate cases")
    if set(expected) != {case["id"] for case in cases}:
        raise ValueError("Unexpected case identity")

    dimensions = ("naturalness", "contact", "continuity", "intent")
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
        failures = rating["failures"][candidate]
        raw_acceptance = values["acceptable" + candidate] == "yes"
        qualified = raw_acceptance and mapped in {"candidate", "tie"} and min(candidate_scores) >= 3 and not failures
        summary.append({
            "id": case["id"],
            "candidate_label": candidate,
            "candidate_acceptable": raw_acceptance,
            "candidate_qualified_acceptance": qualified,
            "candidate_acceptance_consistent": raw_acceptance == qualified,
            "baseline_acceptable": values["acceptable" + baseline] == "yes",
            "candidate_scores": candidate_scores,
            "baseline_scores": baseline_scores,
            "candidate_failures": failures,
            "candidate_score_deltas": [a - b for a, b in zip(candidate_scores, baseline_scores)],
            "preference": mapped,
            "corrections": int(values["corrections" + candidate]) if values["corrections" + candidate] else None,
            "interactions": int(values["interactions" + candidate]) if values["interactions" + candidate] else None,
            "notes": values["notes"],
        })

    if require_capture and canonical_hash(value) != CAPTURE_HASH:
        raise ValueError("Human capture differs from visible browser state")
    comparisons = {}
    for index, dimension in enumerate(dimensions):
        deltas = [case["candidate_score_deltas"][index] for case in summary]
        comparisons[dimension] = {
            "wins": sum(delta > 0 for delta in deltas),
            "ties": sum(delta == 0 for delta in deltas),
            "losses": sum(delta < 0 for delta in deltas),
        }
    result = {
        "schema": "b4ml-human-review-summary-v9",
        "complete": True,
        "cases": summary,
        "candidate_acceptable": sum(case["candidate_acceptable"] for case in summary),
        "candidate_qualified_acceptance": sum(case["candidate_qualified_acceptance"] for case in summary),
        "acceptance_contradictions": sum(not case["candidate_acceptance_consistent"] for case in summary),
        "baseline_acceptable": sum(case["baseline_acceptable"] for case in summary),
        "preferences": {key: sum(case["preference"] == key for case in summary) for key in ("candidate", "baseline", "tie", "neither")},
        "dimension_comparison": comparisons,
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
        "next_action": (
            "Preserve the accepted BoneForge v54 run exactly. Repair Rigify-only jitter and natural-flow "
            "defects without regressing cadence, contact, flight, torso range, or the accepted BoneForge scene. "
            "Do not train or promote a model."
        ),
        "scope": (
            "Non-blind ratings compare exact v54 runs with exact v35 negative controls. They qualify one "
            "BoneForge production slice and Rigify-specific negative feedback only; they do not establish "
            "identity, authorize training or promotion, or qualify Cascadeur work."
        ),
    }
    if (result["candidate_acceptable"], result["candidate_qualified_acceptance"], result["baseline_acceptable"]) != (1, 1, 0):
        raise ValueError("Unexpected acceptance summary")
    if result["preferences"] != {"candidate": 1, "baseline": 0, "tie": 0, "neither": 1}:
        raise ValueError("Unexpected preference summary")
    if comparisons != {
        "naturalness": {"wins": 2, "ties": 0, "losses": 0},
        "contact": {"wins": 2, "ties": 0, "losses": 0},
        "continuity": {"wins": 1, "ties": 1, "losses": 0},
        "intent": {"wins": 2, "ties": 0, "losses": 0},
    }:
        raise ValueError("Unexpected score-delta summary")
    return result


if __name__ == "__main__":
    destination = REVIEW / "human-review-summary-v9-native-display.json"
    with destination.open("x", encoding="utf-8") as stream:
        json.dump(validate(), stream, indent=2, allow_nan=False)
        stream.write("\n")
    print(destination)
