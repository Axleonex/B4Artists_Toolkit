"""Foreground Bforartists journey for interpolation timing controls."""
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
REPORT = ROOT / "docs/b4artists_ml/timing-controls-ui-v1.json"
SCREENSHOT = ROOT / "training/b4artists_ml/cache/timing-controls-ui-v1.png"
LOG = ROOT / "training/b4artists_ml/cache/timing-controls-ui-v1.log"
TEST_SCRIPT = ROOT / "tests/test_b4artists_ml_timing_controls_v1.py"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def runtime_hashes():
    return {str(path.relative_to(ROOT)).replace("\\", "/"): sha(path)
            for path in sorted((ROOT / "b4artists_ml").glob("*.py"))}


def run_host():
    import bpy
    sys.path[:0] = [str(ROOT), str(ROOT / "tests")]
    import b4artists_ml
    from b4artists_ml import math_core, quadruped_gait, workflow

    b4artists_ml.register()
    frozen_runtime = runtime_hashes()
    frozen_script = sha(HERE)
    frozen_test = sha(TEST_SCRIPT)
    scene = bpy.context.scene
    data = bpy.data.armatures.new("Timing UI Rig")
    obj = bpy.data.objects.new("Timing UI Rig", data)
    scene.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    for index, name in enumerate(("hips", "upperarm.fk-L", "thigh.fk-R")):
        bone = data.edit_bones.new(name)
        bone.head = (float(index), 0.0, 0.0)
        bone.tail = (float(index), 0.0, 1.0)
    bpy.ops.object.mode_set(mode="POSE")
    hips = obj.pose.bones["hips"]
    hips.rotation_mode = "QUATERNION"
    scene.frame_set(1)
    hips.location.x = 0.0
    hips.keyframe_insert("location", frame=1)
    workflow.capture_anchor(obj, scene)
    scene.frame_set(11)
    hips.location.x = 10.0
    hips.keyframe_insert("location", frame=11)
    workflow.capture_anchor(obj, scene)
    source = obj.animation_data.action
    source_name = source.name
    source_digest = quadruped_gait._action_digest(obj, source)
    obj.b4ml.interpolation_method = "POSES"
    obj.b4ml.easing = "EASE_OUT"
    obj.b4ml.timing_bias = -.5
    state = {"phase": "generate", "started": time.monotonic(), "events": []}

    def finish(value):
        if value.get("passed"):
            if (runtime_hashes() != frozen_runtime or sha(HERE) != frozen_script or
                    sha(TEST_SCRIPT) != frozen_test):
                raise AssertionError("Source changed during timing-controls UI journey")
            value["runtime_source_count"] = len(frozen_runtime)
            value["runtime_source_sha256"] = frozen_runtime
            value["ui_script_sha256"] = frozen_script
            value["test_script_sha256"] = frozen_test
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        REPORT.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
        print("B4ML_TIMING_CONTROLS_UI: " + json.dumps(value), flush=True)
        bpy.ops.wm.quit_blender()
        return None

    def tick():
        try:
            if time.monotonic() - state["started"] > 90:
                raise AssertionError("Timing-controls UI journey timed out")
            window = bpy.context.window_manager.windows[0]
            area = next(value for value in window.screen.areas if value.type == "VIEW_3D")
            region = next(value for value in area.regions if value.type == "WINDOW")
            ui_region = next(value for value in area.regions if value.type == "UI")
            area.spaces.active.show_region_ui = True
            if hasattr(ui_region, "active_panel_category"):
                ui_region.active_panel_category = "B4Artists ML"
            window.view_layer.objects.active = obj
            obj.select_set(True)
            with bpy.context.temp_override(window=window, area=area, region=region,
                                           object=obj, active_object=obj,
                                           selected_objects=[obj], selected_editable_objects=[obj]):
                if state["phase"] == "generate":
                    scene.frame_set(6)
                    assert bpy.ops.b4ml.action(operation="PREVIEW") == {"FINISHED"}
                    candidate = obj.animation_data.action
                    expected = 10.0 * math_core.timing_weight(.5, "EASE_OUT", -.5)
                    assert abs(hips.location.x - expected) < 1e-5
                    assert candidate["b4ml_timing_easing"] == "EASE_OUT"
                    assert abs(candidate["b4ml_timing_bias"] + .5) < 1e-7
                    state["midpoint"] = hips.location.x
                    state["events"].append(
                        "Generated Ease Out preview with -0.50 later-arrival bias")
                    assert bpy.ops.b4ml.action(operation="DISCARD") == {"FINISHED"}
                    assert obj.animation_data.action is source
                    assert source.name == source_name
                    assert quadruped_gait._action_digest(obj, source) == source_digest
                    state["events"].append("Discard restored the untouched source action")
                    window.cursor_warp(ui_region.x + ui_region.width // 2,
                                       ui_region.y + ui_region.height // 2)
                    for _ in range(20):
                        window.event_simulate(type="WHEELDOWNMOUSE", value="PRESS",
                                              x=ui_region.x + ui_region.width // 2,
                                              y=ui_region.y + ui_region.height // 2)
                    state["phase"] = "capture"
                    return .75
                SCREENSHOT.parent.mkdir(parents=True, exist_ok=True)
                bpy.ops.screen.screenshot(filepath=str(SCREENSHOT))
                assert obj.b4ml.easing == "EASE_OUT"
                assert abs(obj.b4ml.timing_bias + .5) < 1e-7
                return finish({
                    "schema": 1,
                    "passed": True,
                    "host": bpy.app.version_string,
                    "fixture": "minimal BoneForge-recognized control rig",
                    "events": state["events"],
                    "easing": obj.b4ml.easing,
                    "timing_bias": obj.b4ml.timing_bias,
                    "midpoint_value": state["midpoint"],
                    "authored_pose_frames": [1, 11],
                    "source_action_unchanged": True,
                    "bounded_action_structure_digest_verified": True,
                    "screenshot": str(SCREENSHOT.relative_to(ROOT)).replace("\\", "/"),
                    "screenshot_sha256": sha(SCREENSHOT),
                    "scope": ("Automated foreground panel and operator journey; deterministic "
                              "timing assistance, not learned inbetweening or independent usability."),
                })
        except Exception:
            return finish({"schema": 1, "passed": False, "phase": state["phase"],
                           "events": state["events"], "error": traceback.format_exc()})
        return .15

    bpy.app.timers.register(tick, first_interval=.5)


def launch():
    startup = subprocess.STARTUPINFO()
    startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startup.wShowWindow = 0
    frozen_runtime = runtime_hashes()
    frozen_script = sha(HERE)
    frozen_test = sha(TEST_SCRIPT)
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
        deadline = time.monotonic() + 120
        while not REPORT.is_file() and process.poll() is None and time.monotonic() < deadline:
            time.sleep(.2)
        if not REPORT.is_file():
            if process.poll() is None:
                process.terminate()
            raise RuntimeError("Foreground timing-controls journey produced no report")
        try:
            process.wait(timeout=15)
        except subprocess.TimeoutExpired:
            process.terminate()
            process.wait(timeout=10)
    value = json.loads(REPORT.read_text(encoding="utf-8"))
    if (not value.get("passed") or runtime_hashes() != frozen_runtime or
            sha(HERE) != frozen_script or sha(TEST_SCRIPT) != frozen_test or
            value.get("runtime_source_sha256") != frozen_runtime or
            value.get("runtime_source_count") != len(frozen_runtime) or
            value.get("ui_script_sha256") != frozen_script or
            value.get("test_script_sha256") != frozen_test):
        raise RuntimeError(value)
    print(json.dumps({"passed": True, "process_exit_code": process.returncode,
                      "assertions_completed_before_shutdown": True,
                      "seconds": time.perf_counter() - started,
                      "report": str(REPORT), "report_sha256": sha(REPORT)}, indent=2))


if __name__ == "__main__":
    if "--host" in sys.argv:
        run_host()
    else:
        launch()
