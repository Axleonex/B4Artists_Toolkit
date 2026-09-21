"""Foreground Bforartists journey for Ripple Pose Retime v1."""
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
REPORT = ROOT / "docs/b4artists_ml/ripple-retime-ui-v1.json"
SCREENSHOT = ROOT / "training/b4artists_ml/cache/ripple-retime-ui-v1.png"
LOG = ROOT / "training/b4artists_ml/cache/ripple-retime-ui-v1.log"
TEST_SCRIPT = ROOT / "tests/test_b4artists_ml_ripple_retime_v1.py"
RIG_NAME = "Ripple Retime UI Rig"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def runtime_hashes():
    return {str(path.relative_to(ROOT)).replace("\\", "/"): sha(path)
            for path in sorted((ROOT / "b4artists_ml").glob("*.py"))}


def run_host():
    import bpy
    sys.path[:0] = [str(ROOT), str(ROOT / "tests")]
    import b4artists_ml
    from b4artists_ml import quadruped_gait, workflow

    b4artists_ml.register()
    frozen_runtime = runtime_hashes()
    frozen_script = sha(HERE)
    frozen_test = sha(TEST_SCRIPT)
    scene = bpy.context.scene
    bpy.context.preferences.edit.use_global_undo = True
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
    for frame, x in ((1, 0.0), (6, 5.0), (11, 10.0), (16, 15.0)):
        scene.frame_set(frame)
        hips.location.x = x
        hips.keyframe_insert("location", frame=frame)
        workflow.capture_anchor(obj, scene)
    for frame, easing, bias, departure, arrival in (
            (6, "EASE_OUT", -.25, .2, .3),
            (11, "SMOOTH", .1, .05, .15),
            (16, "EASE_IN", .2, .1, .2)):
        workflow.set_transition_timing(
            obj, frame, True, easing, bias, departure, arrival)
    for frame, label in ((6, "hero beat"), (11, "anticipation"),
                         (16, "landing")):
        anchor = next(value for value in obj.b4ml.anchors
                      if abs(value.frame-frame) < 1e-5)
        anchor.name += " (" + label + ")"
    source_name = obj.animation_data.action.name
    source_digest = quadruped_gait._action_digest(obj, obj.animation_data.action)
    obj.b4ml.interpolation_method = "POSES"
    obj.b4ml.status = "ripple baseline status"
    scene.tool_settings.use_keyframe_insert_auto = True
    hips.select = True
    obj.pose.bones["upperarm.fk-L"].select = False
    scene.frame_set(8)
    state = {"phase": "dialog", "started": time.monotonic(), "events": []}

    def current():
        rig = bpy.data.objects.get(RIG_NAME)
        assert rig is not None
        bpy.context.view_layer.objects.active = rig
        rig.select_set(True)
        return rig, rig.pose.bones["hips"]

    def anchor_rows(rig):
        return sorted((float(anchor.frame), anchor.name, anchor.payload)
                      for anchor in rig.b4ml.anchors)

    baseline_rows = anchor_rows(obj)
    payloads = [row[2] for row in baseline_rows]
    suffixes = [row[1].split(" - ", 1)[1] for row in baseline_rows]

    def rig_state(rig):
        return {
            bone.name: (tuple(bone.location), tuple(bone.scale), bone.rotation_mode,
                        tuple(bone.rotation_quaternion), tuple(bone.rotation_euler),
                        tuple(bone.rotation_axis_angle), bool(bone.select))
            for bone in rig.pose.bones
        }

    baseline_rig_state = rig_state(obj)

    def source_is_unchanged(rig):
        action = rig.animation_data.action if rig.animation_data else None
        return (action is not None and action.name == source_name and
                quadruped_gait._action_digest(rig, action) == source_digest)

    def assert_baseline(rig):
        assert anchor_rows(rig) == baseline_rows
        assert rig.b4ml.status == "ripple baseline status"
        assert source_is_unchanged(rig)
        assert rig_state(rig) == baseline_rig_state
        assert bpy.context.scene.tool_settings.use_keyframe_insert_auto is True

    def assert_rippled(rig):
        rows = anchor_rows(rig)
        assert [row[0] for row in rows] == [1.0, 8.0, 13.0, 18.0]
        assert [row[2] for row in rows] == payloads
        for index, frame in enumerate((1, 8, 13, 18)):
            expected = baseline_rows[0][1] if index == 0 else (
                f"Frame {frame:.9g} - " + suffixes[index])
            assert rows[index][1] == expected
        assert rig.b4ml.status == "Ripple-retimed 3 priority poses by +2 frames"
        assert source_is_unchanged(rig)
        assert rig_state(rig) == baseline_rig_state
        assert bpy.context.scene.tool_settings.use_keyframe_insert_auto is True
        return rows

    def finish(value):
        if value.get("passed"):
            if (runtime_hashes() != frozen_runtime or sha(HERE) != frozen_script or
                    sha(TEST_SCRIPT) != frozen_test):
                raise AssertionError("Source changed during Ripple Retime UI journey")
            value["runtime_source_count"] = len(frozen_runtime)
            value["runtime_source_sha256"] = frozen_runtime
            value["ui_script_sha256"] = frozen_script
            value["test_script_sha256"] = frozen_test
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        REPORT.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
        print("B4ML_RIPPLE_RETIME_UI: " + json.dumps(value), flush=True)
        bpy.ops.wm.quit_blender()
        return None

    def tick():
        try:
            if time.monotonic() - state["started"] > 90:
                raise AssertionError("Ripple Retime UI journey timed out")
            window = bpy.context.window_manager.windows[0]
            area = next(value for value in window.screen.areas if value.type == "VIEW_3D")
            region = next(value for value in area.regions if value.type == "WINDOW")
            ui_region = next(value for value in area.regions if value.type == "UI")
            area.spaces.active.show_region_ui = True
            if hasattr(ui_region, "active_panel_category"):
                ui_region.active_panel_category = "B4Artists ML"
            rig, hips = current()
            window.view_layer.objects.active = rig
            with bpy.context.temp_override(window=window, area=area, region=region,
                                           object=rig, active_object=rig,
                                           selected_objects=[rig],
                                           selected_editable_objects=[rig]):
                if state["phase"] == "dialog":
                    assert bpy.ops.b4ml.ripple_retime(
                        "INVOKE_DEFAULT", source_frame=6) == {"RUNNING_MODAL"}
                    state["phase"] = "dialog_capture"
                    return .5
                if state["phase"] == "dialog_capture":
                    SCREENSHOT.parent.mkdir(parents=True, exist_ok=True)
                    bpy.ops.screen.screenshot(filepath=str(SCREENSHOT))
                    window.event_simulate(type="ESC", value="PRESS")
                    state["events"].append(
                        "Displayed the frame 6 to 8 three-pose ripple dialog")
                    state["phase"] = "set"
                    return .5
                if state["phase"] == "set":
                    assert bpy.ops.ed.undo_push(message="Ripple retime baseline") == {"FINISHED"}
                    binding = workflow.ripple_retime_context(rig, scene, 6)["binding"]
                    assert bpy.ops.b4ml.ripple_retime(
                        "EXEC_DEFAULT", source_frame=6, destination_frame=8,
                        moved_count=3, source_binding=binding) == {"FINISHED"}
                    state["rippled_rows"] = assert_rippled(rig)
                    state["rippled_status"] = rig.b4ml.status
                    assert bpy.ops.ed.undo_push(message="Priority poses ripple retimed") == {"FINISHED"}
                    state["events"].append(
                        "Ripple-retimed the clicked and later priority poses")
                    state["phase"] = "undo"
                elif state["phase"] == "undo":
                    assert bpy.ops.ed.undo() == {"FINISHED"}
                    rig, _ = current()
                    assert_baseline(rig)
                    state["events"].append(
                        "One native Undo restored every frame, name, payload, and status")
                    state["phase"] = "redo"
                elif state["phase"] == "redo":
                    assert bpy.ops.ed.redo() == {"FINISHED"}
                    rig, _ = current()
                    assert assert_rippled(rig) == state["rippled_rows"]
                    state["events"].append(
                        "One native Redo restored the complete three-pose ripple")
                    state["phase"] = "preview"
                elif state["phase"] == "preview":
                    assert bpy.ops.b4ml.action(operation="PREVIEW") == {"FINISHED"}
                    rig, hips = current()
                    bpy.context.scene.frame_set(8)
                    assert abs(hips.location.x - 5.0) < 1e-5
                    state["preview_value"] = hips.location.x
                    assert bpy.ops.b4ml.action(operation="DISCARD") == {"FINISHED"}
                    rig, _ = current()
                    assert source_is_unchanged(rig)
                    state["events"].append(
                        "Preview honored the ripple and Discard restored the source")
                    state["phase"] = "finish"
                    return .5
                else:
                    rig, _ = current()
                    return finish({
                        "schema": 1, "passed": True,
                        "host": bpy.app.version_string,
                        "fixture": "minimal BoneForge-recognized control rig",
                        "events": state["events"],
                        "native_undo_steps": 1, "native_redo_steps": 1,
                        "source_frame": 6, "destination_frame": 8,
                        "moved_pose_count": 3,
                        "result_frames": [1, 8, 13, 18],
                        "preview_value_at_destination": state["preview_value"],
                        "payloads_preserved_exactly": True,
                        "internal_spacing_preserved": True,
                        "status_undo_redo_verified": True,
                        "rig_state_preserved": True,
                        "source_action_unchanged": source_is_unchanged(rig),
                        "bounded_action_structure_digest_verified": True,
                        "screenshot": str(SCREENSHOT.relative_to(ROOT)).replace("\\", "/"),
                        "screenshot_sha256": sha(SCREENSHOT),
                        "scope": ("Automated foreground dialog/operator/Undo/Redo journey; "
                                  "procedural timeline authoring, not learned motion or usability review."),
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
            raise RuntimeError("Foreground Ripple Retime journey produced no report")
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
