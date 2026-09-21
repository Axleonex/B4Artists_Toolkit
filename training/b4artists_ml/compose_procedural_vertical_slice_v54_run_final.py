"""Freeze the two independently validated v54 run cases as one review source."""
from pathlib import Path
import hashlib
import json
import shutil


HERE = Path(__file__).resolve()
TRAIN = HERE.parent
RESULTS = TRAIN / "results"
DESTINATION = RESULTS / "procedural-vertical-slice-v54-run-final"
PROTOCOL = TRAIN / "procedural_vertical_slice_protocol_v54.json"
SOURCES = {
    "boneforge": RESULTS / "procedural-vertical-slice-v54-smoke-boneforge-run" / "boneforge" / "run",
    "rigify_basic": RESULTS / "procedural-vertical-slice-v54-smoke-rigify-basic-run" / "rigify_basic" / "run",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def validate_case(profile, source):
    report_path = source / "report.json"
    blend_path = source / f"{profile}-run.blend"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    failed = sorted(key for key, passed in report["automated_gates"].items() if passed is not True)
    if report.get("complete") is not True or report.get("failures") or failed:
        raise ValueError(f"Unqualified v54 run case {profile}: {failed}")
    if report.get("schema") != "procedural-vertical-slice-case-v54":
        raise ValueError(f"Unexpected v54 report schema for {profile}")
    if report.get("run_mechanics") != {
        "forward_speed_body_per_second": 1.5,
        "step_cadence_per_minute": 184.6153846153846,
        "flight_fraction": 0.375,
        "contact_starts": [1.0, 11.0, 21.0, 31.0, 40.0],
    }:
        raise ValueError(f"Unexpected v54 mechanics receipt for {profile}")
    if not blend_path.is_file() or sha(blend_path) != report.get("blend_sha256"):
        raise ValueError(f"Missing or stale v54 blend for {profile}")
    return report_path, blend_path


def main():
    if DESTINATION.exists():
        raise RuntimeError("Immutable v54 run final already exists: " + str(DESTINATION))
    qualified = {profile: validate_case(profile, source) for profile, source in SOURCES.items()}
    DESTINATION.mkdir(parents=True)
    cases = []
    for profile, source in SOURCES.items():
        destination = DESTINATION / profile / "run"
        shutil.copytree(source, destination)
        report_path = destination / "report.json"
        blend_path = destination / f"{profile}-run.blend"
        report = json.loads(report_path.read_text(encoding="utf-8"))
        cases.append({
            "id": f"{profile}/run",
            "report_sha256": sha(report_path),
            "blend_sha256": sha(blend_path),
            "complete": True,
            "upper_body_angular_acceleration_p95_rad_s2": report["automated_metrics"]["review_directed"]["upper_body_angular_acceleration_p95_rad_s2"],
            "coupled_chest_pitch_range_degrees": report["automated_metrics"]["review_directed"]["coupled_chest_pitch_range_degrees"],
            "pelvis_jerk_p95_body_s3": report["automated_metrics"]["review_directed"]["pelvis_jerk_p95_body_s3"],
        })
    summary = {
        "schema": "procedural-vertical-slice-summary-v54-run-final",
        "complete": True,
        "cases": cases,
        "passed": len(cases),
        "failed": 0,
        "protocol": PROTOCOL.relative_to(TRAIN.parents[1]).as_posix(),
        "protocol_sha256": sha(PROTOCOL),
        "source_human_review_schema": "b4ml-human-review-summary-v8",
        "source_human_review": "review-directed-followup-reviewer-v8/human-review-summary-v8-native-display.json",
        "review_status": "awaiting bounded visual re-review of cadence-correct run redesign",
        "known_host_shutdown_fault": "ucrtbase.dll after completed report and saved blend",
        "training_authorized": False,
        "model_promotion_authorized": False,
        "cascadeur_connector_authorized": False,
        "full_goal_complete": False,
    }
    write(DESTINATION / "summary.json", summary)
    print(DESTINATION)


if __name__ == "__main__":
    main()
