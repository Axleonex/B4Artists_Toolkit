"""Foreground Bforartists Undo/Redo journey for Transition Timing Transfer."""
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
REPORT = ROOT / "docs/b4artists_ml/transition-timing-transfer-ui-v1.json"
SCREENSHOT = ROOT / "training/b4artists_ml/cache/transition-timing-transfer-ui-v1.png"
LOG = ROOT / "training/b4artists_ml/cache/transition-timing-transfer-ui-v1.log"
TEST_SCRIPT = ROOT / "tests/test_b4artists_ml_transition_timing_transfer_v1.py"
RIG_NAME = "Timing Transfer UI Rig"


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
    data = bpy.data.armatures.new(RIG_NAME)
    obj = bpy.data.objects.new(RIG_NAME, data)
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
    for frame, x in ((1, 0.0), (11, 10.0), (21, 0.0)):
        scene.frame_set(frame)
        hips.location.x = x
        hips.keyframe_insert("location", frame=frame)
        workflow.capture_anchor(obj, scene)
    source_name = obj.animation_data.action.name
    source_digest = quadruped_gait._action_digest(obj, obj.animation_data.action)
    obj.b4ml.interpolation_method = "POSES"
    workflow.set_transition_timing(obj, 11, True, "EASE_OUT", -.25, .2, .3)
    state = {"phase": "copy", "started": time.monotonic(), "events": []}

    def current():
        rig = bpy.data.objects.get(RIG_NAME)
        assert rig is not None
        bpy.context.view_layer.objects.active = rig
        rig.select_set(True)
        return rig, rig.pose.bones["hips"]

    def source_is_unchanged(rig):
        action = rig.animation_data.action if rig.animation_data else None
        return (action is not None and action.name == source_name and
                quadruped_gait._action_digest(rig, action) == source_digest)

    def finish(value):
        if value.get("passed"):
            if (runtime_hashes() != frozen_runtime or sha(HERE) != frozen_script or
                    sha(TEST_SCRIPT) != frozen_test):
                raise AssertionError("Source changed during timing-transfer UI journey")
            value["runtime_source_count"] = len(frozen_runtime)
            value["runtime_source_sha256"] = frozen_runtime
            value["ui_script_sha256"] = frozen_script
            value["test_script_sha256"] = frozen_test
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        REPORT.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
        print("B4ML_TRANSITION_TIMING_TRANSFER_UI: " + json.dumps(value), flush=True)
        bpy.ops.wm.quit_blender()
        return None

    def tick():
        try:
            if time.monotonic() - state["started"] > 90:
                raise AssertionError("Transition-timing-transfer UI journey timed out")
            window = bpy.context.window_manager.windows[0]
            area = next(value for value in window.screen.areas if value.type == "VIEW_3D")
            region = next(value for value in area.regions if value.type == "WINDOW")
            ui_region = next(value for value in area.regions if value.type == "UI")
            area.spaces.active.show_region_ui = True
            if hasattr(ui_region, "active_panel_category"):
                ui_region.active_panel_category = "B4Artists ML"
            rig, hips = current()
            scene = bpy.context.scene
            window.view_layer.objects.active = rig
            with bpy.context.temp_override(window=window, area=area, region=region,
                                           object=rig, active_object=rig,
                                           selected_objects=[rig], selected_editable_objects=[rig]):
                if state["phase"] == "copy":
                    assert bpy.ops.b4ml.transition_timing_transfer(
                        'EXEC_DEFAULT', operation='COPY', frame=11) == {"FINISHED"}
                    copied = json.loads(rig.b4ml.timing_clipboard)
                    assert copied["source_frame"] == 11 and copied["source"] == "OVERRIDE"
                    assert copied["timing"]["easing"] == "EASE_OUT"
                    assert abs(copied["timing"]["bias"] + .25) < 1e-6
                    assert source_is_unchanged(rig)
                    state["events"].append("Copied easing, bias and holds from the interval into frame 11")
                    state["phase"] = "capture"
                    return .5
                elif state["phase"] == "capture":
                    SCREENSHOT.parent.mkdir(parents=True, exist_ok=True)
                    bpy.ops.screen.screenshot(filepath=str(SCREENSHOT))
                    assert bpy.ops.ed.undo_push(message="Timing transfer baseline") == {"FINISHED"}
                    assert bpy.ops.b4ml.transition_timing_transfer(
                        'EXEC_DEFAULT', operation='PASTE', frame=21) == {"FINISHED"}
                    assert bpy.ops.ed.undo_push(message="Timing transfer applied") == {"FINISHED"}
                    timing = workflow.transition_timing(rig, 21)
                    assert timing["easing"] == "EASE_OUT" and abs(timing["bias"] + .25) < 1e-6
                    assert abs(timing["departure_hold"] - .2) < 1e-6
                    assert abs(timing["arrival_hold"] - .3) < 1e-6
                    assert source_is_unchanged(rig)
                    state["events"].append("Pasted the copied timing into frame 21")
                    state["phase"] = "undo"
                    return .5
                elif state["phase"] == "undo":
                    assert bpy.ops.ed.undo() == {"FINISHED"}
                    rig, _ = current()
                    undo_count = 1
                    if workflow.transition_timing(rig, 21) is not None:
                        assert bpy.ops.ed.undo() == {"FINISHED"}
                        rig, _ = current()
                        undo_count = 2
                    assert workflow.transition_timing(rig, 21) is None
                    assert workflow.transition_timing(rig, 11) is not None
                    assert source_is_unchanged(rig)
                    state["undo_count"] = undo_count
                    state["events"].append("Native Undo removed only the pasted destination timing")
                    state["phase"] = "redo"
                elif state["phase"] == "redo":
                    for _ in range(state["undo_count"]):
                        assert bpy.ops.ed.redo() == {"FINISHED"}
                    rig, _ = current()
                    assert workflow.transition_timing(rig, 21) == workflow.transition_timing(rig, 11)
                    assert source_is_unchanged(rig)
                    state["events"].append("Native Redo restored the pasted timing")
                    state["phase"] = "preview"
                elif state["phase"] == "preview":
                    scene.frame_set(16)
                    assert bpy.ops.b4ml.action(operation="PREVIEW") == {"FINISHED"}
                    rig, hips = current()
                    active_t = math_core.timing_window(.5, .2, .3)
                    weight = math_core.timing_weight(active_t, "EASE_OUT", -.25)
                    expected = 10.0 * (1.0-weight)
                    assert abs(hips.location.x - expected) < 1e-5
                    metadata = json.loads(rig.animation_data.action["b4ml_transition_timing"])
                    assert metadata[0]["override"] and metadata[1]["override"]
                    for key in ("easing", "bias", "departure_hold", "arrival_hold", "override"):
                        assert metadata[0][key] == metadata[1][key]
                    assert metadata[0]["destination_frame"] == 11.0
                    assert metadata[1]["destination_frame"] == 21.0
                    state["midpoint"] = hips.location.x
                    assert bpy.ops.b4ml.action(operation="DISCARD") == {"FINISHED"}
                    rig, _ = current()
                    assert source_is_unchanged(rig)
                    state["events"].append("Preview used identical copied timing in both intervals")
                    state["phase"] = "finish"
                    return .75
                else:
                    rig, _ = current()
                    return finish({
                        "schema": 1,
                        "passed": True,
                        "host": bpy.app.version_string,
                        "fixture": "minimal BoneForge-recognized control rig",
                        "events": state["events"],
                        "undo_count": state["undo_count"],
                        "source_frame": 11,
                        "destination_frame": 21,
                        "easing": "EASE_OUT",
                        "bias": -.25,
                        "departure_hold": .2,
                        "arrival_hold": .3,
                        "midpoint_value": state["midpoint"],
                        "source_action_unchanged": source_is_unchanged(rig),
                        "bounded_action_structure_digest_verified": True,
                        "screenshot": str(SCREENSHOT.relative_to(ROOT)).replace("\\", "/"),
                        "screenshot_sha256": sha(SCREENSHOT),
                        "scope": ("Automated foreground copy/paste/operator/Undo/Redo journey; "
                                  "deterministic timing transfer, not learned motion or usability review."),
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
            raise RuntimeError("Foreground transition-timing-transfer journey produced no report")
        try:
            process.wait(timeout=15)
        except subprocess.TimeoutExpired:
            process.terminate();process.wait(timeout=10)
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
