"""Exercise correction-trial lifecycle and objective edit accounting on a v13 scene."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys
import time
import traceback


HERE = Path(__file__).resolve()
TRAIN = HERE.parent
ROOT = HERE.parents[2]
DATA = TRAIN / "results/procedural-vertical-slice-reviewer-v2/review-data.json"
OUT = TRAIN / "results/correction-trial-smoke-v1"
HOST = Path("X:/5.1.0/bforartists.exe")
CASE_ID = "boneforge/reach"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write(path, value):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def host():
    import bpy
    sys.path[:0] = [str(ROOT), str(TRAIN)]
    import b4artists_ml
    import correction_trial_v1 as trial

    result = dict(schema="b4ml-correction-trial-smoke-host-v1", complete=False)
    try:
        if not hasattr(bpy.types.Object, "b4ml"):
            b4artists_ml.register()
        trial.register()
        common = dict(
            review_data=str(DATA), case_id=CASE_ID, reviewer_id="synthetic-smoke",
            output_directory=str(OUT), mode="SYNTHETIC",
        )
        trial.configure(dict(common, side="A"))
        scene = bpy.context.scene
        original = trial._armature().animation_data.action
        cancelled = trial.start_trial(scene)
        cancel_source_hash = cancelled["source_snapshot_sha256"]
        point = next(
            point for curve in trial._curves(cancelled["obj"], cancelled["working"])
            for point in curve.keyframe_points
            if round(float(point.co.x), 6) not in {round(float(frame), 6) for frame in trial._CONFIG["case"]["priority_frames"]}
        )
        point.co.y += 0.005
        trial._poll_session(cancelled)
        if not trial.cancel_trial(scene) or cancelled["obj"].animation_data.action != original:
            raise ValueError("Cancel did not restore the pre-trial action")
        if trial._json_hash(trial.action_snapshot(cancelled["obj"], cancelled["source"])) != cancel_source_hash:
            raise ValueError("Cancel changed the frozen method action")

        trial.configure(dict(common, side="B"))
        session = trial.start_trial(scene)
        priorities = {round(float(frame), 6) for frame in trial._CONFIG["case"]["priority_frames"]}
        point = next(
            point for curve in trial._curves(session["obj"], session["working"])
            for point in curve.keyframe_points if round(float(point.co.x), 6) not in priorities
        )
        point.co.y += 0.01
        trial._poll_session(session)
        scene.frame_set(2)
        trial._poll_session(session)
        trial.pause_trial(scene, True)
        paused_seconds = session["active_seconds"]
        time.sleep(0.02)
        trial._poll_session(session)
        if session["active_seconds"] != paused_seconds:
            raise ValueError("Paused wall time was counted as active work")
        trial.pause_trial(scene, False)
        path, report = trial.finish_trial(scene)
        if report["human_authored"] or not report["synthetic_smoke"]:
            raise ValueError("Synthetic smoke was misclassified as human evidence")
        if report["action_difference"]["corrective_key_events"] < 1:
            raise ValueError("Animation edit was not counted")
        if not report["action_difference"]["priority_poses_preserved"]:
            raise ValueError("Non-priority synthetic edit changed a priority pose")
        if report["observed_edit_bursts"] < 1 or report["observed_frame_events"] < 1:
            raise ValueError("Observed interaction events were not counted")
        if trial._json_hash(trial.action_snapshot(session["obj"], session["source"])) != session["source_snapshot_sha256"]:
            raise ValueError("Finished trial changed the frozen source action")
        result.update(
            complete=True, cancelled_source_restored=True, frozen_source_unchanged=True,
            export=path.relative_to(ROOT).as_posix(), export_sha256=sha(path),
            active_pause_excluded=True, human_authored=False, synthetic_smoke=True,
            action_difference=report["action_difference"],
            observed_edit_bursts=report["observed_edit_bursts"],
            observed_frame_events=report["observed_frame_events"],
            observed_interaction_events=report["observed_interaction_events"],
            full_goal_complete=False,
        )
    except BaseException:
        result["error"] = traceback.format_exc()
    write(OUT / "host-report.json", result)
    print("B4ML_CORRECTION_TRIAL=" + json.dumps(result, allow_nan=False), flush=True)


def main():
    if OUT.exists():
        raise RuntimeError("Correction-trial smoke evidence already exists")
    data = read(DATA)
    case = next(case for case in data["cases"] if case["id"] == CASE_ID)
    scene = ROOT / case["source_blend"]
    if sha(scene) != case["source_blend_sha256"]:
        raise ValueError("Smoke source scene identity changed")
    OUT.mkdir(parents=True)
    log = OUT / "host.log"
    started = time.perf_counter()
    with log.open("w", encoding="utf-8") as stream:
        process = subprocess.run(
            [str(HOST), "--background", "--factory-startup", "--disable-autoexec", str(scene),
             "--python", str(HERE), "--", "host"],
            stdout=stream, stderr=subprocess.STDOUT, timeout=180,
            env=dict(os.environ, OPENBLAS_NUM_THREADS="4", PYTHONDONTWRITEBYTECODE="1"),
        )
    report = read(OUT / "host-report.json")
    log_text = log.read_text(encoding="utf-8", errors="replace")
    qualified = process.returncode == 0 or (
        process.returncode in {1, 11, -1073741819, 3221225477}
        and report.get("complete") and "ucrtbase.dll" in log_text
    )
    if not qualified or not report.get("complete"):
        raise RuntimeError("Correction-trial host smoke failed: " + json.dumps(report))
    result = dict(
        schema="b4ml-correction-trial-validation-v1", complete=True,
        scene=case["source_blend"], scene_sha256=case["source_blend_sha256"],
        review_data_sha256=sha(DATA), script_sha256=sha(TRAIN / "correction_trial_v1.py"),
        checker_sha256=sha(HERE), host_exit=process.returncode,
        host_exit_qualified=qualified, clean_host_shutdown=process.returncode == 0,
        host_report=report, log_sha256=sha(log), seconds=time.perf_counter() - started,
        human_reviewed_cases=0, full_goal_complete=False,
    )
    write(OUT / "validation.json", result)
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    if "--" in sys.argv:
        host()
    else:
        main()
