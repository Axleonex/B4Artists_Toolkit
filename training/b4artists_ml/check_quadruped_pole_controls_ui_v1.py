"""Foreground Bforartists journey for quadruped Flip Side, Set Distance and Undo/Redo."""
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
REPORT = ROOT / "docs/b4artists_ml/quadruped-pole-controls-ui-v1.json"
SCREENSHOT = ROOT / "training/b4artists_ml/cache/quadruped-pole-controls-ui-v1.png"
LOG = ROOT / "training/b4artists_ml/cache/quadruped-pole-controls-ui-v1.log"
BLEND = ROOT / "training/b4artists_ml/cache/quadruped-pole-controls-ui-v1.blend"
FIXTURE_SCRIPT = ROOT / "tests/test_b4artists_ml_quadruped_pose.py"
TEST_SCRIPT = ROOT / "tests/test_b4artists_ml_quadruped_pole_controls_v1.py"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def runtime_hashes():
    return {str(path.relative_to(ROOT)).replace("\\", "/"): sha(path)
            for path in sorted((ROOT / "b4artists_ml").glob("*.py"))}


def matrix_error(left, right):
    return max(abs(left[row][column] - right[row][column])
               for row in range(4) for column in range(4))


def run_host():
    import addon_utils
    import bpy
    sys.path[:0] = [str(ROOT), str(ROOT / "tests")]
    import b4artists_ml
    from b4artists_ml import quadruped_gait, quadruped_pose as pose, ui as ui_module, workflow
    from test_b4artists_ml_quadruped_pose import _generate

    addon_utils.enable("rigify", default_set=True, persistent=False)
    b4artists_ml.register()
    bpy.context.preferences.edit.use_global_undo = True
    frozen_runtime = runtime_hashes()
    frozen_script = sha(HERE)
    frozen_fixture = sha(FIXTURE_SCRIPT)
    frozen_test = sha(TEST_SCRIPT)

    scene, obj = _generate("wolf")
    obj.name = "B4ML Pole Controls UI Rig"
    object_name = obj.name
    bpy.context.view_layer.objects.active = obj
    _, _, limbs = pose.binding(obj)
    for row in limbs:
        obj.pose.bones[row["property_bone"]]["pole_vector"] = True
    obj.b4ml.quadruped_use_poles = True
    scene.frame_set(27)
    obj.pose.bones["root"].location = (0.005, -0.002, 0.003)
    obj.pose.bones["root"].keyframe_insert("location", frame=27)
    bpy.context.view_layer.update()
    pose.begin(obj, scene)
    source_pose = workflow.raw_pose(obj)
    action_name = obj.animation_data.action.name
    modes = pose.mode_values(obj)
    pole_modes = pose.pole_mode_values(obj)
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))
    bpy.ops.wm.open_mainfile(filepath=str(BLEND), use_scripts=False)

    scene = bpy.context.scene
    reloaded_rig = bpy.data.objects[object_name]
    source_action = reloaded_rig.animation_data.action
    action_digest = quadruped_gait._action_digest(reloaded_rig, source_action)
    action_slot_handle = getattr(reloaded_rig.animation_data, "action_slot_handle", 0)
    action_slot = getattr(reloaded_rig.animation_data, "action_slot", None)
    action_slot_identifier = getattr(action_slot, "identifier", None)
    state = {"phase": "apply", "started": time.monotonic(), "events": []}

    def current():
        rig = bpy.data.objects[object_name]
        return rig, rig.b4ml.quadruped_targets["Fore Pole L"]

    def verify_source(rig):
        assert workflow.raw_pose(rig) == source_pose
        assert rig.animation_data.action is source_action
        assert rig.animation_data.action.name == action_name
        assert quadruped_gait._action_digest(rig, source_action) == action_digest
        assert getattr(rig.animation_data, "action_slot_handle", 0) == action_slot_handle
        assert getattr(getattr(rig.animation_data, "action_slot", None),
                       "identifier", None) == action_slot_identifier
        assert pose.mode_values(rig) == modes
        assert pose.pole_mode_values(rig) == pole_modes

    def finish(report):
        if report.get("passed"):
            if (runtime_hashes() != frozen_runtime or sha(HERE) != frozen_script or
                    sha(FIXTURE_SCRIPT) != frozen_fixture or
                    sha(TEST_SCRIPT) != frozen_test):
                raise AssertionError("Source changed during quadruped Pole Controls UI journey")
            report["runtime_source_count"] = len(frozen_runtime)
            report["runtime_source_sha256"] = frozen_runtime
            report["ui_script_sha256"] = frozen_script
            report["fixture_script_sha256"] = frozen_fixture
            report["test_script_sha256"] = frozen_test
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print("B4ML_QUADRUPED_POLE_CONTROLS_UI: " + json.dumps(report), flush=True)
        bpy.ops.wm.quit_blender()
        return None

    def tick():
        try:
            if time.monotonic() - state["started"] > 150:
                raise AssertionError("Quadruped Pole Controls UI journey timed out")
            window = bpy.context.window_manager.windows[0]
            area = next(value for value in window.screen.areas if value.type == "VIEW_3D")
            region = next(value for value in area.regions if value.type == "WINDOW")
            ui_region = next(value for value in area.regions if value.type == "UI")
            assert ui_region.width <= 300
            area.spaces.active.show_region_ui = True
            if hasattr(ui_region, "active_panel_category"):
                ui_region.active_panel_category = "B4Artists ML"
            rig, pole = current()
            window.view_layer.objects.active = rig
            rig.select_set(True)
            with bpy.context.temp_override(window=window, area=area, region=region):
                if state["phase"] == "apply":
                    window.event_simulate(type="ESC", value="PRESS")
                    state["before_matrix"] = pole.target.matrix_world.copy()
                    state["before_distance"] = pole.pole_distance
                    state["before_payload"] = rig.b4ml.quadruped_payload
                    state["before_status"] = rig.b4ml.status
                    state["target_name"] = pole.target.name
                    assert bpy.ops.ed.undo_push(message="Quadruped Pole Controls baseline") == {"FINISHED"}
                    assert bpy.ops.b4ml.quadruped_pose(
                        operation="FLIP_POLE", target_name="Fore Pole L") == {"FINISHED"}
                    rig, pole = current()
                    state["flip_matrix"] = pole.target.matrix_world.copy()
                    assert matrix_error(state["flip_matrix"], state["before_matrix"]) > 1e-5
                    pole.pole_distance = 0.62
                    assert bpy.ops.b4ml.quadruped_pose(
                        operation="SET_POLE_DISTANCE", target_name="Fore Pole L") == {"FINISHED"}
                    rig, pole = current()
                    state["after_matrix"] = pole.target.matrix_world.copy()
                    state["after_distance"] = pole.pole_distance
                    state["after_payload"] = rig.b4ml.quadruped_payload
                    state["after_status"] = rig.b4ml.status
                    assert abs(state["after_distance"] - 0.62) < 1e-6
                    assert matrix_error(state["after_matrix"], state["flip_matrix"]) > 1e-5
                    after = json.loads(state["after_payload"])
                    assert after["signature"] is None and after["metrics"] is None
                    assert pole.target.name == state["target_name"]
                    verify_source(rig)
                    assert bpy.ops.ed.undo_push(message="Quadruped Pole Controls complete") == {"FINISHED"}
                    state["events"].extend([
                        "Flipped Fore Pole L through the visible operator",
                        "Set Fore Pole L distance to 0.62 body scales through the visible operator",
                    ])
                    state["phase"] = "undo"
                elif state["phase"] == "undo":
                    undo_count = 0
                    while undo_count < 6:
                        assert bpy.ops.ed.undo() == {"FINISHED"}
                        undo_count += 1
                        rig, pole = current()
                        if (matrix_error(pole.target.matrix_world, state["before_matrix"]) < 1e-7 and
                                abs(pole.pole_distance - state["before_distance"]) < 1e-7 and
                                rig.b4ml.quadruped_payload == state["before_payload"]):
                            break
                    assert matrix_error(pole.target.matrix_world, state["before_matrix"]) < 1e-7
                    assert abs(pole.pole_distance - state["before_distance"]) < 1e-7
                    assert rig.b4ml.quadruped_payload == state["before_payload"]
                    assert rig.b4ml.status == state["before_status"]
                    assert pole.target.name == state["target_name"]
                    verify_source(rig)
                    state["undo_count"] = undo_count
                    state["events"].append("Native Undo restored the helper, distance and request metadata")
                    state["phase"] = "redo"
                elif state["phase"] == "redo":
                    for _ in range(state["undo_count"]):
                        assert bpy.ops.ed.redo() == {"FINISHED"}
                    rig, pole = current()
                    assert matrix_error(pole.target.matrix_world, state["after_matrix"]) < 1e-6
                    assert abs(pole.pole_distance - state["after_distance"]) < 1e-7
                    assert rig.b4ml.quadruped_payload == state["after_payload"]
                    assert rig.b4ml.status == state["after_status"]
                    assert pole.target.name == state["target_name"]
                    verify_source(rig)
                    state["events"].append("Native Redo restored the flipped, distance-adjusted request")
                    for _ in range(13):
                        window.event_simulate(type="WHEELDOWNMOUSE", value="PRESS",
                                              x=ui_region.x + ui_region.width // 2,
                                              y=ui_region.y + ui_region.height // 2)
                    state["phase"] = "capture"
                elif state["phase"] == "capture":
                    SCREENSHOT.parent.mkdir(parents=True, exist_ok=True)
                    bpy.ops.screen.screenshot(filepath=str(SCREENSHOT))
                    visible_pole_labels = [
                        ui_module._quadruped_target_ui_label(name)
                        for name in pose.POLE_TARGETS
                    ]
                    assert visible_pole_labels == [
                        "Fore L Pole", "Fore R Pole", "Hind L Pole", "Hind R Pole"]
                    return finish({
                        "schema": 1,
                        "passed": True,
                        "host": bpy.app.version_string,
                        "fixture": "generated Rigify wolf",
                        "events": state["events"],
                        "flip_operator_verified": True,
                        "distance_operator_verified": True,
                        "native_undo_redo_verified": True,
                        "helper_pointer_preserved": True,
                        "distance_undo_redo_verified": True,
                        "payload_undo_redo_verified": True,
                        "source_pose_unchanged": True,
                        "source_action_unchanged": True,
                        "complete_action_digest_verified": True,
                        "action_slot_verified": True,
                        "modes_unchanged": True,
                        "visible_pole_labels": visible_pole_labels,
                        "narrow_panel_width": ui_region.width,
                        "screenshot": str(SCREENSHOT.relative_to(ROOT)).replace("\\", "/"),
                        "screenshot_sha256": sha(SCREENSHOT),
                        "scope": ("Automated foreground panel and operator journey. "
                                  "Independent animator visual assessment remains unverified."),
                    })
        except Exception:
            return finish({"schema": 1, "passed": False, "phase": state["phase"],
                           "events": state["events"], "error": traceback.format_exc()})
        return 0.15

    bpy.app.timers.register(tick, first_interval=0.5)


def launch():
    startup = subprocess.STARTUPINFO()
    startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startup.wShowWindow = 0
    started = time.perf_counter()
    frozen_runtime = runtime_hashes()
    frozen_script = sha(HERE)
    frozen_fixture = sha(FIXTURE_SCRIPT)
    frozen_test = sha(TEST_SCRIPT)
    LOG.parent.mkdir(parents=True, exist_ok=True)
    REPORT.unlink(missing_ok=True)
    with LOG.open("w", encoding="utf-8") as stream:
        process = subprocess.Popen(
            [os.environ.get("B4ML_BFORARTISTS", "X:/5.1.0/bforartists.exe"),
             "--factory-startup", "--no-window-focus", "--enable-event-simulate",
             "--python", str(HERE), "--", "--host"],
            cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT, startupinfo=startup,
            env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1", OPENBLAS_NUM_THREADS="4"))
        deadline = time.monotonic() + 210
        while not REPORT.is_file() and process.poll() is None and time.monotonic() < deadline:
            time.sleep(0.2)
        if not REPORT.is_file():
            if process.poll() is None:
                process.terminate()
            raise RuntimeError("Foreground quadruped Pole Controls journey produced no report")
        try:
            process.wait(timeout=15)
        except subprocess.TimeoutExpired:
            process.terminate()
            process.wait(timeout=10)
    value = json.loads(REPORT.read_text(encoding="utf-8"))
    if (not value.get("passed") or runtime_hashes() != frozen_runtime or
            sha(HERE) != frozen_script or sha(FIXTURE_SCRIPT) != frozen_fixture or
            sha(TEST_SCRIPT) != frozen_test or
            value.get("runtime_source_sha256") != frozen_runtime or
            value.get("runtime_source_count") != len(frozen_runtime) or
            value.get("ui_script_sha256") != frozen_script or
            value.get("fixture_script_sha256") != frozen_fixture or
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
