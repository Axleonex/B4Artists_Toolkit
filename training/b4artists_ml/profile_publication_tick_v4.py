"""Profile the current final publication tick after the 0.19.4 one-snapshot, one-use optimization."""
from pathlib import Path
import cProfile
import hashlib
import json
import os
import pstats
import subprocess
import sys
import time


HERE = Path(__file__).resolve()
TRAINING = HERE.parent
ROOT = TRAINING.parents[1]
OUT = TRAINING / "results/publication-tick-profile-v4"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def host_main():
    sys.path[:0] = [str(ROOT), str(ROOT / "tests"), str(TRAINING)]
    import bpy
    import b4artists_ml
    from b4artists_ml import contacts, curve_smoothing, rig_state, temporal_generation, temporal_preview
    from b4artists_ml import workflow as w

    b4artists_ml.register()
    reference = TRAINING / "results/broader-shape-runtime-v1/rigify_default/reach_hold-smooth_both.blend"
    bpy.ops.wm.open_mainfile(filepath=str(reference), load_ui=False, use_scripts=False)
    scene = bpy.context.scene
    obj = next(item for item in scene.objects if item.type == "ARMATURE" and item.b4ml.candidate_action)
    w.finish_preview(obj, scene, False)
    source = obj.animation_data.action
    signature = contacts._action_signature(obj)
    pose = w.raw_pose(obj)
    modes = rig_state.mode_values(obj)
    anchors = [(item.frame, item.payload) for item in obj.b4ml.anchors]
    inventory = {name: len(getattr(bpy.data, name)) for name in ("objects", "armatures", "scenes", "actions")}
    timings = {"workflow_preview": [], "smooth_copy": []}

    original_preview = w.preview
    original_smooth = curve_smoothing.smooth_copy
    original_publish = temporal_preview._publish

    def timed_preview(*args, **kwargs):
        started = time.perf_counter()
        try:
            return original_preview(*args, **kwargs)
        finally:
            timings["workflow_preview"].append(time.perf_counter() - started)

    def timed_smooth(*args, **kwargs):
        started = time.perf_counter()
        try:
            return original_smooth(*args, **kwargs)
        finally:
            timings["smooth_copy"].append(time.perf_counter() - started)

    w.preview = timed_preview
    curve_smoothing.smooth_copy = timed_smooth
    profile = cProfile.Profile()
    publication_times = []

    def profiled_publish(*args, **kwargs):
        started = time.perf_counter()
        profile.enable()
        try:
            return original_publish(*args, **kwargs)
        finally:
            profile.disable()
            publication_times.append(time.perf_counter() - started)

    temporal_preview._publish = profiled_publish
    obj.b4ml.temporal_smoothing = True
    temporal_preview.start(obj, scene)
    ordinary_ticks = []
    final_step = None
    while obj.b4ml.temporal_running:
        started = time.perf_counter()
        done = temporal_preview.step(obj)
        elapsed = time.perf_counter() - started
        if done:
            final_step = elapsed
        else:
            ordinary_ticks.append(time.perf_counter() - started)
    assert final_step is not None and len(publication_times) == 1
    assert len(timings["workflow_preview"]) == len(timings["smooth_copy"]) == 1

    stats = pstats.Stats(profile)
    functions = []
    for (filename, line, name), (primitive_calls, calls, own, cumulative, callers) in stats.stats.items():
        functions.append({
            "file": filename.replace("\\", "/"),
            "line": line,
            "name": name,
            "primitive_calls": primitive_calls,
            "calls": calls,
            "own_seconds": own,
            "cumulative_seconds": cumulative,
        })
    functions.sort(key=lambda row: row["cumulative_seconds"], reverse=True)
    candidate = obj.b4ml.candidate_action
    output_signature = contacts._action_signature(obj)
    w.finish_preview(obj, scene, False)
    source_preserved = (obj.animation_data.action == source and contacts._action_signature(obj) == signature and
                        w.raw_pose(obj) == pose and rig_state.mode_values(obj) == modes and
                        anchors == [(item.frame, item.payload) for item in obj.b4ml.anchors])
    inventory_preserved = inventory == {name: len(getattr(bpy.data, name)) for name in inventory}
    assert source_preserved and inventory_preserved
    assert not temporal_preview._JOBS and not temporal_generation._LIVE and not temporal_generation._OWNERS
    report = {
        "schema": 1,
        "complete": True,
        "final_tick_seconds": final_step,
        "publisher_seconds": publication_times[0],
        "workflow_preview_seconds": timings["workflow_preview"][0],
        "smooth_copy_seconds": timings["smooth_copy"][0],
        "unattributed_publication_seconds": max(0.0, publication_times[0] - sum(value[0] for value in timings.values())),
        "ordinary_tick_count": len(ordinary_ticks),
        "ordinary_max_tick_seconds": max(ordinary_ticks),
        "top_functions": functions[:100],
        "candidate_signature_rows": len(output_signature),
        "source_preserved": source_preserved,
        "inventory_preserved": inventory_preserved,
        "production_changed": False,
        "full_goal_complete": False,
        "runtime_sha256": {path.relative_to(ROOT).as_posix(): sha(path) for path in (ROOT / "b4artists_ml").glob("*.py")},
        "limitations": "One profiled headless default-Rigify publication tick; profiler overhead affects absolute timing.",
    }
    write(OUT / "report.json", report)
    profile.dump_stats(OUT / "publication.prof")
    print(json.dumps({key: report[key] for key in (
        "final_tick_seconds", "workflow_preview_seconds", "smooth_copy_seconds",
        "unattributed_publication_seconds", "ordinary_max_tick_seconds")}, indent=2), flush=True)
    print(json.dumps(functions[:25], indent=2), flush=True)


def main():
    OUT.mkdir(exist_ok=False)
    write(OUT / "plan.json", {
        "schema": 1,
        "script_sha256": sha(HERE),
        "routing_sha256": sha(ROOT / "docs/b4artists_ml/publication-packet-production-routing-v1.json"),
        "scope": "Current 0.19.4 production final publication tick only; no runtime changes.",
        "max_seconds": 300,
    })
    with (OUT / "host.log").open("w") as log:
        process = subprocess.run(
            ["X:/5.1.0/bforartists.exe", "--background", "--factory-startup", "--disable-autoexec",
             "--python", str(HERE), "--", "host"],
            stdout=log, stderr=subprocess.STDOUT, timeout=300,
            env=dict(os.environ, OPENBLAS_NUM_THREADS="4", PYTHONDONTWRITEBYTECODE="1"))
    report = json.loads((OUT / "report.json").read_text(encoding="utf-8")) if (OUT / "report.json").exists() else None
    write(OUT / "process.json", {
        "exit_code": process.returncode,
        "complete": bool(report and report["complete"]),
        "assertions_passed": bool(report and report["source_preserved"] and report["inventory_preserved"]),
        "host_shutdown_clean": process.returncode == 0,
        "log_sha256": sha(OUT / "host.log"),
    })
    if report is None:
        print((OUT / "host.log").read_text(encoding="utf-8", errors="replace"))
        raise SystemExit(1)
    print(json.dumps(json.loads((OUT / "process.json").read_text()), indent=2))


if __name__ == "__main__":
    if "host" in sys.argv:
        host_main()
    else:
        main()
