"""Validate one human-authored, hash-bound hands-on correction export."""
from pathlib import Path
from datetime import datetime
import hashlib
import json
import math
import sys


HERE = Path(__file__).resolve()
TRAIN = HERE.parent
ROOT = HERE.parents[2]
DATA_PATH = TRAIN / "results/procedural-vertical-slice-reviewer-v2/review-data.json"
AGGREGATE = TRAIN / "results/procedural-vertical-slice-v13/aggregate.json"
FAILURES = {
    "foot_slide", "penetration", "popping", "stretch",
    "timing", "balance", "intent_loss", "other",
}
DIFF_FIELDS = {
    "changed_curves", "added_keys", "removed_keys", "changed_keys",
    "corrective_key_events", "priority_key_events", "priority_poses_preserved",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _timestamp(value, label):
    if not isinstance(value, str):
        raise ValueError("Missing " + label)
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("Invalid " + label) from exc
    if parsed.tzinfo is None:
        raise ValueError(label + " must include a timezone")
    return parsed


def validate_report(report, data=None):
    data = data or json.loads(DATA_PATH.read_text(encoding="utf-8"))
    if report.get("schema") != "b4ml-hands-on-correction-trial-v1":
        raise ValueError("Unsupported correction-trial schema")
    if report.get("human_authored") is not True or report.get("synthetic_smoke") is not False:
        raise ValueError("Synthetic or non-human correction trials cannot become human evidence")
    if report.get("source_review_data_sha256") != sha(DATA_PATH):
        raise ValueError("Correction trial does not match the frozen review packet")
    if report.get("source_aggregate_sha256") != sha(AGGREGATE) or data.get("aggregate_sha256") != sha(AGGREGATE):
        raise ValueError("Correction trial aggregate identity changed")
    cases = {case["id"]: case for case in data["cases"]}
    case = cases.get(report.get("case_id"))
    if case is None or report.get("blind_side") not in {"A", "B"}:
        raise ValueError("Unknown correction-trial case or side")
    if report.get("profile") != case["profile"] or report.get("task") != case["task"]:
        raise ValueError("Correction-trial task metadata changed")
    if report.get("source_scene") != case["source_blend"] or report.get("source_scene_sha256") != case["source_blend_sha256"]:
        raise ValueError("Correction-trial scene identity changed")
    if report.get("method_identity_hidden_during_trial") is not True or "method_identity" in report:
        raise ValueError("Correction trial was not blind")
    reviewer = report.get("reviewer_id")
    if not isinstance(reviewer, str) or not reviewer.strip() or len(reviewer) > 200:
        raise ValueError("A bounded reviewer ID or anonymous code is required")
    started = _timestamp(report.get("started_utc"), "start timestamp")
    completed = _timestamp(report.get("completed_utc"), "completion timestamp")
    if completed < started:
        raise ValueError("Correction trial completed before it started")
    active = report.get("active_work_seconds")
    if not isinstance(active, (int, float)) or isinstance(active, bool) or not math.isfinite(active) or active <= 0:
        raise ValueError("Positive finite active work time is required")
    for field in ("observed_edit_bursts", "observed_frame_events", "tracker_control_interactions", "observed_interaction_events"):
        value = report.get(field)
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            raise ValueError("Invalid interaction count: " + field)
    expected_events = (
        report["observed_edit_bursts"] + report["observed_frame_events"] +
        report["tracker_control_interactions"]
    )
    if report["observed_interaction_events"] != expected_events:
        raise ValueError("Observed interaction total changed")
    difference = report.get("action_difference")
    if not isinstance(difference, dict) or set(difference) != DIFF_FIELDS:
        raise ValueError("Action-difference fields changed")
    for field in DIFF_FIELDS - {"priority_poses_preserved"}:
        if not isinstance(difference[field], int) or isinstance(difference[field], bool) or difference[field] < 0:
            raise ValueError("Invalid action-difference count: " + field)
    if difference["corrective_key_events"] != difference["added_keys"] + difference["removed_keys"] + difference["changed_keys"]:
        raise ValueError("Corrective key total changed")
    if difference["priority_poses_preserved"] != (difference["priority_key_events"] == 0):
        raise ValueError("Priority-pose result contradicts its count")
    if report.get("production_acceptable") not in {"YES", "NO"}:
        raise ValueError("Completed human trial requires a production-acceptability decision")
    failures = report.get("visible_failure_tags")
    if not isinstance(failures, list) or len(failures) != len(set(failures)) or not set(failures) <= FAILURES:
        raise ValueError("Invalid visible failure tags")
    if not isinstance(report.get("notes"), str) or len(report["notes"]) > 10000:
        raise ValueError("Correction-trial notes must be bounded text")
    events = report.get("event_log")
    if not isinstance(events, list) or len(events) != report["observed_edit_bursts"] + report["observed_frame_events"]:
        raise ValueError("Correction-trial event log changed")
    if report.get("full_goal_complete") is not False:
        raise ValueError("A correction trial cannot declare the full goal complete")
    return dict(
        valid=True, case_id=report["case_id"], blind_side=report["blind_side"],
        active_work_seconds=float(active), observed_interaction_events=report["observed_interaction_events"],
        corrective_key_events=difference["corrective_key_events"],
        priority_poses_preserved=difference["priority_poses_preserved"],
        production_acceptable=report["production_acceptable"] == "YES",
        visible_failure_tags=failures,
    )


def main():
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python validate_correction_trial_v1.py <human-trial.json>")
    path = Path(sys.argv[1]).resolve()
    report = json.loads(path.read_text(encoding="utf-8-sig"))
    result = validate_report(report)
    result.update(
        schema="b4ml-hands-on-correction-validation-v1",
        source_trial=str(path), source_trial_sha256=sha(path),
        validator_sha256=sha(HERE), full_goal_complete=False,
    )
    output = path.with_name(path.stem + ".validation.json")
    if output.exists():
        raise ValueError("Correction-trial validation already exists")
    output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
