"""Foreground Bforartists journey for wind-relative secondary drag."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys
import time
import traceback


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve()
TEST = ROOT / "tests/test_b4artists_ml_secondary_wind_velocity_v1.py"
REPORT = ROOT / "docs/b4artists_ml/secondary-wind-velocity-ui-v1.json"
SCREENSHOT = ROOT / "training/b4artists_ml/cache/secondary-wind-velocity-ui-v1.png"
LOG = ROOT / "training/b4artists_ml/cache/secondary-wind-velocity-ui-v1.log"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def runtime_hashes():
    return {"b4artists_ml/" + path.name: sha(path)
            for path in sorted((ROOT / "b4artists_ml").glob("*.py"))}


def run_host():
    import bpy
    import numpy as np
    sys.path[:0] = [str(ROOT), str(ROOT / "tests")]
    import b4artists_ml
    from b4artists_ml import flight, secondary_motion as secondary, workflow as w
    from test_b4artists_ml_secondary_external_acceleration_v1 import location_fixture

    b4artists_ml.register()
    frozen_runtime = runtime_hashes()
    frozen_script = sha(HERE)
    frozen_test = sha(TEST)
    bpy.context.preferences.edit.use_global_undo = True
    obj, source, control, path = location_fixture("boneforge")
    scene = bpy.context.scene
    state_data = obj.b4ml
    original = state_data.candidate_action
    original_token = flight._curve_token(obj, original)
    source_token = flight._curve_token(obj, source)
    state_data.secondary_external_acceleration = (0., 0., 0.)
    state_data.secondary_air_friction = .8
    state_data.secondary_wind_velocity = (3., -1., .5)
    state_data.show_secondary = True
    object_name = obj.name
    source_name = source.name
    input_name = original.name
    state = {"phase": "dismiss", "started": time.monotonic(), "events": [],
             "steps": []}
    native_step = secondary.step

    def timed(value):
        began = time.perf_counter()
        before = value.b4ml.secondary_progress
        try:
            return native_step(value)
        finally:
            state["steps"].append({"ms": (time.perf_counter()-began)*1000,
                                   "before": before,
                                   "after": value.b4ml.secondary_progress})
    secondary.step = timed

    def current():
        rig = bpy.data.objects[object_name]
        bpy.context.view_layer.objects.active = rig
        rig.select_set(True)
        return rig

    def finish(value):
        if value.get("passed"):
            if (runtime_hashes() != frozen_runtime or sha(HERE) != frozen_script
                    or sha(TEST) != frozen_test):
                raise AssertionError("Source changed during wind UI journey")
            value["runtime_source_count"] = len(frozen_runtime)
            value["runtime_source_sha256"] = frozen_runtime
            value["ui_script_sha256"] = frozen_script
            value["test_script_sha256"] = frozen_test
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        REPORT.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
        print("B4ML_SECONDARY_WIND_VELOCITY_UI: " + json.dumps(value), flush=True)
        bpy.ops.wm.quit_blender()
        return None

    def tick():
        try:
            if time.monotonic() - state["started"] > 180:
                raise AssertionError("Secondary wind UI journey timed out")
            window = bpy.context.window_manager.windows[0]
            area = next(value for value in window.screen.areas if value.type == "VIEW_3D")
            region = next(value for value in area.regions if value.type == "WINDOW")
            ui_region = next(value for value in area.regions if value.type == "UI")
            area.spaces.active.show_region_ui = True
            if hasattr(ui_region, "active_panel_category"):
                ui_region.active_panel_category = "B4Artists ML"
            rig = current()
            with bpy.context.temp_override(window=window, area=area, region=region,
                                           object=rig, active_object=rig,
                                           selected_objects=[rig],
                                           selected_editable_objects=[rig]):
                phase = state["phase"]
                if phase == "dismiss":
                    window.event_simulate(type="ESC", value="PRESS")
                    state["phase"] = "open"
                    return .4
                if phase == "open":
                    bpy.ops.view3d.view_axis(type="FRONT")
                    bpy.ops.view3d.view_selected(use_all_regions=False)
                    for _ in range(6):
                        window.event_simulate(
                            type="WHEELDOWNMOUSE", value="PRESS",
                            x=ui_region.x + ui_region.width//2,
                            y=ui_region.y + ui_region.height//2)
                    state["phase"] = "capture"
                    return .5
                if phase == "capture":
                    SCREENSHOT.parent.mkdir(parents=True, exist_ok=True)
                    bpy.ops.screen.screenshot(filepath=str(SCREENSHOT))
                    state["events"].append(
                        "Displayed Wind Velocity in the Secondary Motion panel")
                    state["phase"] = "start"
                    return .5
                if phase == "start":
                    bpy.ops.ed.undo_push(message="Secondary wind input ready")
                    assert bpy.ops.b4ml.secondary_solve("INVOKE_DEFAULT") == {"RUNNING_MODAL"}
                    state["phase"] = "complete"
                elif phase == "complete":
                    if rig.b4ml.secondary_running:
                        return .02
                    output = rig.b4ml.candidate_action
                    assert output is not original and rig.b4ml.secondary_input is original
                    metrics = json.loads(rig.b4ml.secondary_metrics)
                    assert metrics["schema"] == 5
                    assert metrics["backend"] == "implicit_selected_control_secondary_v4"
                    assert metrics["external_acceleration"] == [0., 0., 0.]
                    assert metrics["wind_velocity"] == [3., -1., .5]
                    assert abs(metrics["wind_velocity_magnitude"] - 10.25**.5) < 1e-8
                    assert abs(metrics["wind_forcing_acceleration_magnitude"]
                               - metrics["air_friction"] * 10.25**.5) < 1e-8
                    assert metrics["controls"] == [control]
                    assert metrics["priority_poses_preserved"]
                    assert metrics["max_location_correction"] > .001
                    assert metrics["max_world_location_error"] <= 2e-4
                    assert flight._curve_token(rig, original) == original_token
                    state["metrics"] = metrics
                    state["output"] = output.name
                    state["events"].append(
                        "Generated editable world-space secondary motion under wind-relative drag")
                    state["phase"] = "settle"
                    return .3
                elif phase == "settle":
                    assert bpy.ops.ed.undo() == {"FINISHED"}
                    state["phase"] = "undo"
                elif phase == "undo":
                    rig = current()
                    assert rig.b4ml.candidate_action.name == input_name
                    assert rig.animation_data.action == rig.b4ml.candidate_action
                    assert bpy.ops.ed.redo() == {"FINISHED"}
                    state["events"].append("Native Undo restored the wind input")
                    state["phase"] = "redo"
                elif phase == "redo":
                    rig = current()
                    assert rig.b4ml.candidate_action.name == state["output"]
                    state["events"].append("Native Redo restored the wind result")
                    assert bpy.ops.b4ml.secondary(operation="RESET") == {"FINISHED"}
                    assert rig.b4ml.candidate_action.name == input_name
                    assert rig.animation_data.action == rig.b4ml.candidate_action
                    state["events"].append("Restore returned to the retained input")
                    assert bpy.ops.b4ml.secondary_solve() == {"FINISHED"}
                    assert bpy.ops.b4ml.action(operation="KEEP") == {"FINISHED"}
                    assert bpy.ops.b4ml.action(operation="RESTORE_SOURCE") == {"FINISHED"}
                    assert rig.animation_data.action.name == source_name
                    state["events"].append("Keep and Restore Source retained ordinary recovery")
                    durations = [row["ms"] for row in state["steps"]]
                    return finish({
                        "schema": 1, "passed": True,
                        "host": bpy.app.version_string,
                        "fixture": "BoneForge",
                        "events": state["events"],
                        "metrics": state["metrics"],
                        "native_undo_steps": 1, "native_redo_steps": 1,
                        "step_count": len(durations),
                        "step_p95_ms": float(np.percentile(durations, 95)),
                        "step_max_ms": max(durations),
                        "source_action_unchanged": (
                            flight._curve_token(rig, bpy.data.actions[source_name]) == source_token),
                        "screenshot": str(SCREENSHOT.relative_to(ROOT)).replace("\\", "/"),
                        "screenshot_sha256": sha(SCREENSHOT),
                        "scope": ("Automated foreground operator/Undo/Redo journey for uniform "
                                  "procedural wind-relative drag; independent animator judgment, learned "
                                  "motion, force/torque solving, and parity remain unverified."),
                    })
        except Exception:
            return finish({"schema": 1, "passed": False, "phase": state["phase"],
                           "events": state["events"], "error": traceback.format_exc()})
        return .03

    bpy.app.timers.register(tick, first_interval=.5)


def launch():
    startup = subprocess.STARTUPINFO()
    startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startup.wShowWindow = 0
    frozen_runtime = runtime_hashes()
    frozen_script = sha(HERE)
    frozen_test = sha(TEST)
    REPORT.unlink(missing_ok=True)
    LOG.parent.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    with LOG.open("w", encoding="utf-8") as stream:
        process = subprocess.Popen(
            [os.environ.get("B4ML_BFORARTISTS", "X:/5.1.0/bforartists.exe"),
             "--factory-startup", "--no-window-focus", "--enable-event-simulate",
             "--python", str(HERE), "--", "--host"],
            cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT, startupinfo=startup,
            env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1", OPENBLAS_NUM_THREADS="4"))
        deadline = time.monotonic() + 210
        while not REPORT.is_file() and process.poll() is None and time.monotonic() < deadline:
            time.sleep(.2)
        if not REPORT.is_file():
            if process.poll() is None:
                process.terminate()
            raise RuntimeError("Foreground wind journey produced no report")
        try:
            process.wait(timeout=15)
        except subprocess.TimeoutExpired:
            process.terminate()
            process.wait(timeout=10)
    value = json.loads(REPORT.read_text(encoding="utf-8"))
    if (not value.get("passed") or runtime_hashes() != frozen_runtime
            or sha(HERE) != frozen_script or sha(TEST) != frozen_test
            or value.get("runtime_source_sha256") != frozen_runtime
            or value.get("ui_script_sha256") != frozen_script
            or value.get("test_script_sha256") != frozen_test):
        raise RuntimeError(value)
    print(json.dumps({"passed": True, "process_exit_code": process.returncode,
                      "assertions_completed_before_shutdown": True,
                      "seconds": time.perf_counter()-started,
                      "report": str(REPORT), "report_sha256": sha(REPORT)}, indent=2))


if __name__ == "__main__":
    if "--host" in sys.argv:
        run_host()
    else:
        launch()
