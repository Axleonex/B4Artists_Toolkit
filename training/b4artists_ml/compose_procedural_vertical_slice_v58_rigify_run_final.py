"""Freeze the independently validated v58 Rigify run as a review source."""
from pathlib import Path
import hashlib
import json
import shutil


HERE = Path(__file__).resolve()
TRAIN = HERE.parent
RESULTS = TRAIN / "results"
DESTINATION = RESULTS / "procedural-vertical-slice-v58-rigify-run-final"
PROTOCOL = TRAIN / "procedural_vertical_slice_protocol_v58.json"
SOURCE = RESULTS / "procedural-vertical-slice-v58-smoke-rigify-basic-run" / "rigify_basic" / "run"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if DESTINATION.exists():
        raise RuntimeError("Immutable v58 Rigify run final already exists: " + str(DESTINATION))
    report_path = SOURCE / "report.json"
    blend_path = SOURCE / "rigify_basic-run.blend"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    failed = sorted(key for key, passed in report["automated_gates"].items() if passed is not True)
    if report.get("complete") is not True or report.get("failures") or failed:
        raise ValueError("Unqualified v58 Rigify run: " + ", ".join(failed))
    if report.get("schema") != "procedural-vertical-slice-case-v58":
        raise ValueError("Unexpected v58 report schema")
    overrides = report.get("profile_override", {}).get("pose_frame_overrides_by_task", {}).get("run", {})
    if set(overrides) != {"6", "16", "26", "36"}:
        raise ValueError("Missing v58 frame-addressed Rigify evidence")
    if any(len(value.get("limbs", {})) != 2 for value in overrides.values()):
        raise ValueError("Missing v58 support-and-swing target evidence")
    if sha(blend_path) != report.get("blend_sha256"):
        raise ValueError("Stale v58 blend identity")
    destination = DESTINATION / "rigify_basic" / "run"
    shutil.copytree(SOURCE, destination)
    copied_report = destination / "report.json"
    copied_blend = destination / "rigify_basic-run.blend"
    summary = {
        "schema": "procedural-vertical-slice-summary-v58-rigify-run-final",
        "complete": True,
        "cases": [{
            "id": "rigify_basic/run",
            "report_sha256": sha(copied_report),
            "blend_sha256": sha(copied_blend),
            "complete": True,
        }],
        "passed": 1,
        "failed": 0,
        "protocol_sha256": sha(PROTOCOL),
        "source_human_review_schema": "b4ml-human-review-summary-v9",
        "source_human_review": "review-directed-followup-reviewer-v9/human-review-summary-v9-native-display.json",
        "preserved_exact_case": "boneforge/run@v54",
        "review_status": "awaiting bounded visual re-review of Rigify jitter repair",
        "training_authorized": False,
        "model_promotion_authorized": False,
        "cascadeur_connector_authorized": False,
        "full_goal_complete": False,
    }
    (DESTINATION / "summary.json").write_text(
        json.dumps(summary, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    print(DESTINATION)


if __name__ == "__main__":
    main()
