"""Freeze the two independently validated v35 run cases as one review source."""
from pathlib import Path
import hashlib
import json
import shutil


HERE = Path(__file__).resolve()
TRAIN = HERE.parent
RESULTS = TRAIN / "results"
DESTINATION = RESULTS / "procedural-vertical-slice-v35-run-final"
PROTOCOL = TRAIN / "procedural_vertical_slice_protocol_v35.json"
SOURCES = {
    "boneforge": RESULTS / "procedural-vertical-slice-v35-smoke-boneforge-run" / "boneforge" / "run",
    "rigify_basic": RESULTS / "procedural-vertical-slice-v35-smoke-rigify-basic-run-factory" / "rigify_basic" / "run",
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
    if report.get("complete") is not True or failed:
        raise ValueError(f"Unqualified v35 run case {profile}: {failed}")
    if report.get("schema") != "procedural-vertical-slice-case-v35":
        raise ValueError(f"Unexpected v35 report schema for {profile}")
    if report.get("automated_gates", {}).get("priority_non_arm_exact") is not True:
        raise ValueError(f"Non-arm priority preservation is unproved for {profile}")
    if report.get("automated_gates", {}).get("priority_declared_arm_layer") is not True:
        raise ValueError(f"Declared arm layer is unqualified for {profile}")
    if not blend_path.is_file():
        raise ValueError(f"Missing v35 blend for {profile}")
    return report_path, blend_path


def main():
    if DESTINATION.exists():
        raise RuntimeError("Immutable v35 run final already exists: " + str(DESTINATION))
    qualified = {profile: validate_case(profile, source) for profile, source in SOURCES.items()}
    DESTINATION.mkdir(parents=True)
    cases = []
    for profile, source in SOURCES.items():
        destination = DESTINATION / profile / "run"
        shutil.copytree(source, destination)
        report_path = destination / "report.json"
        blend_path = destination / f"{profile}-run.blend"
        cases.append({
            "id": f"{profile}/run",
            "report_sha256": sha(report_path),
            "blend_sha256": sha(blend_path),
            "complete": True,
        })
    summary = {
        "schema": "procedural-vertical-slice-summary-v35-run-final",
        "complete": True,
        "cases": cases,
        "passed": len(cases),
        "failed": 0,
        "protocol": PROTOCOL.relative_to(TRAIN.parents[1]).as_posix(),
        "protocol_sha256": sha(PROTOCOL),
        "source_human_review_schema": "b4ml-human-review-summary-v7",
        "source_human_review": "review-directed-followup-reviewer-v7/human-review-summary-v7-native-display.json",
        "review_status": "awaiting bounded visual re-review of run skipping repair",
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
