"""Foreground Bforartists journey for quadruped Align Bend and Undo/Redo."""
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
REPORT = ROOT / "docs/b4artists_ml/quadruped-pole-align-ui-v1.json"
SCREENSHOT = ROOT / "training/b4artists_ml/cache/quadruped-pole-align-ui-v1.png"
LOG = ROOT / "training/b4artists_ml/cache/quadruped-pole-align-ui-v1.log"
BLEND = ROOT / "training/b4artists_ml/cache/quadruped-pole-align-ui-v1.blend"
FIXTURE_SCRIPT = ROOT / "tests/test_b4artists_ml_quadruped_pose.py"


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
    from b4artists_ml import quadruped_pose as pose, workflow
    from test_b4artists_ml_quadruped_pose import _action_signature, _generate

    addon_utils.enable("rigify", default_set=True, persistent=False)
    b4artists_ml.register()
    bpy.context.preferences.edit.use_global_undo = True
    frozen_runtime = runtime_hashes()
    frozen_script = sha(HERE)
    frozen_fixture = sha(FIXTURE_SCRIPT)

    scene, obj = _generate("wolf")
    obj.name = "B4ML Align Bend UI Rig"
    object_name = obj.name
    bpy.context.view_layer.objects.active = obj
    _, _, limbs = pose.binding(obj)
    for row in limbs:
        obj.pose.bones[row["property_bone"]]["pole_vector"] = True
    obj.b4ml.quadruped_use_poles = True
    scene.frame_set(23)
    obj.pose.bones["root"].location = (0.006, -0.004, 0.002)
    obj.pose.bones["root"].keyframe_insert("location", frame=23)
    bpy.context.view_layer.update()
    pose.begin(obj, scene)
    source_pose = workflow.raw_pose(obj)
    action_name = obj.animation_data.action.name
    action_signature = _action_signature(obj, obj.animation_data.action)
    modes = pose.mode_values(obj)
    pole_modes = pose.pole_mode_values(obj)

    evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    upper = evaluated.pose.bones["MCH-front_thigh_ik.L"]
    lower = evaluated.pose.bones["MCH-front_shin_ik.L"]
    world = evaluated.matrix_world
    root, middle, end = world @ upper.head, world @ lower.head, world @ lower.tail
    axis = (end - root).normalized()
    bend = middle - root
    bend -= axis * bend.dot(axis)
    bend.normalize()
    side = axis.cross(bend).normalized()
    item = obj.b4ml.quadruped_targets["Fore Pole L"]
    matrix = item.target.matrix_world.copy()
    matrix.translation = middle + side * (json.loads(obj.b4ml.quadruped_payload)["scale"] * 0.75)
    item.target.matrix_world = matrix
    item.target.scale = (1.0, 1.0, 1.0)
    bpy.context.view_layer.update()
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))
    bpy.ops.wm.open_mainfile(filepath=str(BLEND), use_scripts=False)

    scene = bpy.context.scene
    state = {"phase": "align", "started": time.monotonic(), "events": []}

    def current():
        rig = bpy.data.objects[object_name]
        return rig, rig.b4ml.quadruped_targets["Fore Pole L"]

    def verify_source(rig):
        assert workflow.raw_pose(rig) == source_pose
        assert rig.animation_data.action.name == action_name
        assert _action_signature(rig, rig.animation_data.action) == action_signature
        assert pose.mode_values(rig) == modes
        assert pose.pole_mode_values(rig) == pole_modes

    def finish(report):
        if report.get("passed"):
            if (runtime_hashes() != frozen_runtime or sha(HERE) != frozen_script or
                    sha(FIXTURE_SCRIPT) != frozen_fixture):
                raise AssertionError("Source changed during quadruped Align Bend UI journey")
            report["runtime_source_count"] = len(frozen_runtime)
            report["runtime_source_sha256"] = frozen_runtime
            report["ui_script_sha256"] = frozen_script
            report["fixture_script_sha256"] = frozen_fixture
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print("B4ML_QUADRUPED_POLE_ALIGN_UI: " + json.dumps(report), flush=True)
        bpy.ops.wm.quit_blender()
        return None

    def tick():
        try:
            if time.monotonic() - state["started"] > 150:
                raise AssertionError("Quadruped Align Bend UI journey timed out")
            window = bpy.context.window_manager.windows[0]
            area = next(value for value in window.screen.areas if value.type == "VIEW_3D")
            region = next(value for value in area.regions if value.type == "WINDOW")
            ui_region = next(value for value in area.regions if value.type == "UI")
            area.spaces.active.show_region_ui = True
            if hasattr(ui_region, "active_panel_category"):
                ui_region.active_panel_category = "B4Artists ML"
            rig, pole = current()
            window.view_layer.objects.active = rig
            rig.select_set(True)
            with bpy.context.temp_override(window=window, area=area, region=region):
                if state["phase"] == "align":
                    window.event_simulate(type="ESC", value="PRESS")
                    state["before_matrix"] = pole.target.matrix_world.copy()
                    state["before_payload"] = rig.b4ml.quadruped_payload
                    state["before_status"] = rig.b4ml.status
                    state["target_name"] = pole.target.name
                    assert bpy.ops.ed.undo_push(message="Quadruped Align Bend baseline") == {"FINISHED"}
                    assert bpy.ops.b4ml.quadruped_pose(
                        operation="ALIGN_POLE", target_name="Fore Pole L") == {"FINISHED"}
                    rig, pole = current()
                    state["after_matrix"] = pole.target.matrix_world.copy()
                    state["after_payload"] = rig.b4ml.quadruped_payload
                    state["after_status"] = rig.b4ml.status
                    assert matrix_error(state["after_matrix"], state["before_matrix"]) > 1e-5
                    after = json.loads(state["after_payload"])
                    assert after["signature"] is None and after["metrics"] is None
                    assert pole.target.name == state["target_name"]
                    verify_source(rig)
                    assert bpy.ops.ed.undo_push(message="Quadruped Align Bend complete") == {"FINISHED"}
                    state["events"].append("Aligned Fore Pole L through the visible operator")
                    state["phase"] = "undo"
                elif state["phase"] == "undo":
                    undo_count = 0
                    while undo_count < 4:
                        assert bpy.ops.ed.undo() == {"FINISHED"}
                        undo_count += 1
                        rig, pole = current()
                        if (matrix_error(pole.target.matrix_world, state["before_matrix"]) < 1e-7 and
                                rig.b4ml.quadruped_payload == state["before_payload"]):
                            break
                    assert matrix_error(pole.target.matrix_world, state["before_matrix"]) < 1e-7
                    assert rig.b4ml.quadruped_payload == state["before_payload"]
                    assert rig.b4ml.status == state["before_status"]
                    assert pole.target.name == state["target_name"]
                    verify_source(rig)
                    state["undo_count"] = undo_count
                    state["events"].append("Native Undo restored the helper and solved metadata")
                    state["phase"] = "redo"
                elif state["phase"] == "redo":
                    for _ in range(state["undo_count"]):
                        assert bpy.ops.ed.redo() == {"FINISHED"}
                    rig, pole = current()
                    assert matrix_error(pole.target.matrix_world, state["after_matrix"]) < 1e-6
                    assert rig.b4ml.quadruped_payload == state["after_payload"]
                    assert rig.b4ml.status == state["after_status"]
                    assert pole.target.name == state["target_name"]
                    verify_source(rig)
                    state["events"].append("Native Redo restored the aligned request")
                    for _ in range(15):
                        window.event_simulate(type="WHEELDOWNMOUSE", value="PRESS",
                                              x=ui_region.x + ui_region.width // 2,
                                              y=ui_region.y + ui_region.height // 2)
                    state["phase"] = "capture"
                elif state["phase"] == "capture":
                    SCREENSHOT.parent.mkdir(parents=True, exist_ok=True)
                    bpy.ops.screen.screenshot(filepath=str(SCREENSHOT))
                    return finish({
                        "schema": 1,
                        "passed": True,
                        "host": bpy.app.version_string,
                        "fixture": "generated Rigify wolf",
                        "events": state["events"],
                        "align_operator_verified": True,
                        "native_undo_redo_verified": True,
                        "helper_pointer_preserved": True,
                        "payload_undo_redo_verified": True,
                        "source_pose_unchanged": True,
                        "source_action_unchanged": True,
                        "modes_unchanged": True,
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
            raise RuntimeError("Foreground quadruped Align Bend journey produced no report")
        try:
            process.wait(timeout=15)
        except subprocess.TimeoutExpired:
            process.terminate()
            process.wait(timeout=10)
    value = json.loads(REPORT.read_text(encoding="utf-8"))
    if (not value.get("passed") or runtime_hashes() != frozen_runtime or
            sha(HERE) != frozen_script or sha(FIXTURE_SCRIPT) != frozen_fixture or
            value.get("runtime_source_sha256") != frozen_runtime or
            value.get("runtime_source_count") != len(frozen_runtime) or
            value.get("ui_script_sha256") != frozen_script or
            value.get("fixture_script_sha256") != frozen_fixture):
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
