"""Bind the focused v17 locomotion/jump experiment to its review and rejection evidence."""
from pathlib import Path
import hashlib
import json
import os


ROOT = Path(__file__).resolve().parents[2]
TRAIN = ROOT / "training" / "b4artists_ml"
RESULTS = TRAIN / "results"
CASE_ROOT = RESULTS / "procedural-vertical-slice-v17"
OUT = RESULTS / "procedural-vertical-slice-v17-focused.json"
PROTOCOL = TRAIN / "procedural_vertical_slice_protocol_v17.json"
BUILDER = TRAIN / "build_procedural_vertical_slice_v17.py"
REVIEW = RESULTS / "human-review-exports" / "b4ml-procedural-vertical-slice-human-review-v2-axlbot.json"
ADDENDUM = RESULTS / "human-review-exports" / "b4ml-procedural-vertical-slice-human-review-v2-axlbot-addendum.json"
REJECTED_V16 = RESULTS / "procedural-vertical-slice-v16" / "boneforge" / "walk" / "report.json"
EXPECTED = tuple(
    (profile, task)
    for profile in ("boneforge", "rigify_basic", "rigify_default", "imported_unity")
    for task in ("walk", "run", "jump")
)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if OUT.exists():
        raise RuntimeError("Focused v17 receipt already exists")

    protocol = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    if protocol.get("schema") != "procedural-vertical-slice-v17":
        raise ValueError("Unexpected v17 protocol schema")
    protocol_sha = sha(PROTOCOL)

    rejected = json.loads(REJECTED_V16.read_text(encoding="utf-8"))
    expected_rejection = "Projected samples already define timing; remove per-transition overrides"
    rejected_errors = [row.get("error", "") for row in rejected.get("failures", [])]
    if rejected.get("complete") is not False or not any(expected_rejection in value for value in rejected_errors):
        raise ValueError("The v16 single-authority rejection evidence changed")

    rows = []
    jump_flights = []
    for profile, task in EXPECTED:
        report_path = CASE_ROOT / profile / task / "report.json"
        report = json.loads(report_path.read_text(encoding="utf-8"))
        if report.get("schema") != "procedural-vertical-slice-case-v17":
            raise ValueError(f"Unexpected report schema: {profile}/{task}")
        if report.get("profile") != profile or report.get("task") != task:
            raise ValueError(f"Report identity mismatch: {profile}/{task}")
        if report.get("protocol_sha256") != protocol_sha:
            raise ValueError(f"Stale protocol binding: {profile}/{task}")
        if report.get("complete") is not True or report.get("failures"):
            raise ValueError(f"Incomplete focused case: {profile}/{task}")
        if report.get("learned_scope") != "bundled local limb-bend direction prior only":
            raise ValueError(f"Learned scope changed: {profile}/{task}")
        if report.get("temporal_learned_motion") is not False:
            raise ValueError(f"Temporal claim changed: {profile}/{task}")
        if report.get("source_restored") is not True or report.get("save_reload_passed") is not True:
            raise ValueError(f"Lifecycle failed: {profile}/{task}")
        if report.get("anchor_payloads_unchanged") is not True:
            raise ValueError(f"Anchor payload changed: {profile}/{task}")
        blend_path = ROOT / report["blend_path"]
        if sha(blend_path) != report.get("blend_sha256"):
            raise ValueError(f"Blend evidence changed: {profile}/{task}")
        bend_sources = sorted({
            limb.get("bend_source")
            for authoring in report.get("authoring", [])
            for limb in authoring.get("limbs", [])
            if limb.get("limb", "").startswith(("arm-", "leg-"))
        })
        row = {
            "id": f"{profile}/{task}",
            "report": report_path.relative_to(ROOT).as_posix(),
            "report_sha256": sha(report_path),
            "blend": report["blend_path"],
            "blend_sha256": report["blend_sha256"],
            "bend_sources": bend_sources,
            "interaction_count": report["interaction_count"],
            "scripted_correction_count": report["scripted_correction_count"],
            "source_restored": True,
            "save_reload_passed": True,
            "anchor_payloads_unchanged": True,
        }
        if task == "jump":
            intervals = report.get("automated_metrics", {}).get("flight_report", {}).get("intervals", [])
            if len(intervals) != 1 or intervals[0].get("start") != 7.0 or intervals[0].get("end") != 23.0:
                raise ValueError(f"Jump interval changed: {profile}/{task}")
            duration = intervals[0].get("duration_seconds")
            if duration is None or abs(duration - (16.0 / 30.0)) > 1e-9:
                raise ValueError(f"Jump duration changed: {profile}/{task}")
            row["flight_interval_frames"] = [7, 23]
            row["flight_duration_seconds"] = duration
            jump_flights.append({"id": row["id"], "frames": [7, 23], "duration_seconds": duration})
        rows.append(row)

    review = json.loads(REVIEW.read_text(encoding="utf-8-sig"))
    if review.get("human_authored") is not True or len(review.get("cases", [])) != 32:
        raise ValueError("Human review source is incomplete")

    receipt = {
        "schema": "b4ml-review-directed-procedural-vertical-slice-v17-focused",
        "status": "PASS_FOCUSED_DETERMINISTIC",
        "complete": True,
        "cases": rows,
        "passed": len(rows),
        "expected": len(EXPECTED),
        "protocol": PROTOCOL.relative_to(ROOT).as_posix(),
        "protocol_sha256": protocol_sha,
        "builder": BUILDER.relative_to(ROOT).as_posix(),
        "builder_sha256": sha(BUILDER),
        "human_review_source": REVIEW.relative_to(ROOT).as_posix(),
        "human_review_source_sha256": sha(REVIEW),
        "human_review_addendum": ADDENDUM.relative_to(ROOT).as_posix(),
        "human_review_addendum_sha256": sha(ADDENDUM),
        "rejected_predecessor": {
            "report": REJECTED_V16.relative_to(ROOT).as_posix(),
            "report_sha256": sha(REJECTED_V16),
            "reason": expected_rejection,
        },
        "jump_flight_evidence": jump_flights,
        "changes_under_test": [
            "Increase authored forward hip travel and vertical hip variation in walk.",
            "Align run landing hips more closely with the landing feet while preserving contact/flight boundaries.",
            "Extend the authored jump flight from 12 to 16 frames at 30 fps.",
            "Use projected samples as the sole timing authority after v16 correctly rejected overrides.",
        ],
        "host_process_exit_capture": False,
        "known_host_shutdown_fault_not_qualified": True,
        "claim_boundary": {
            "human_visual_improvement_verified": False,
            "temporal_model_trained": False,
            "model_promotion_permitted": False,
            "cascadeur_parity_verified": False,
            "full_goal_complete": False,
        },
    }
    temporary = OUT.with_suffix(".tmp")
    temporary.write_text(json.dumps(receipt, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    os.replace(temporary, OUT)
    print(json.dumps(receipt, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
