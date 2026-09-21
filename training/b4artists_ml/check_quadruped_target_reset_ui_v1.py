"""Foreground Bforartists journey for quadruped per-target reset and Undo/Redo."""
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
REPORT = ROOT / "docs/b4artists_ml/quadruped-target-reset-ui-v1.json"
SCREENSHOT = ROOT / "training/b4artists_ml/cache/quadruped-target-reset-ui-v1.png"
LOG = ROOT / "training/b4artists_ml/cache/quadruped-target-reset-ui-v1.log"
BLEND = ROOT / "training/b4artists_ml/cache/quadruped-target-reset-ui-v1.blend"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def matrix_error(actual, expected):
    return max(abs(actual[row][column] - expected[row][column])
               for row in range(4) for column in range(4))


def run_host():
    import addon_utils
    import bpy
    sys.path[:0] = [str(ROOT), str(ROOT / "tests")]
    import b4artists_ml
    from b4artists_ml import quadruped_pose as pose
    from b4artists_ml import workflow
    from test_b4artists_ml_quadruped_pose import _generate

    addon_utils.enable("rigify", default_set=True, persistent=False)
    b4artists_ml.register()
    bpy.context.preferences.edit.use_global_undo = True
    scene, obj = _generate("horse")
    obj.name = "B4ML Target Reset UI Rig"
    object_name = obj.name
    pose.begin(obj, scene)
    bpy.context.view_layer.update()
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))
    bpy.ops.wm.open_mainfile(filepath=str(BLEND), use_scripts=False)
    scene = bpy.context.scene
    obj = bpy.data.objects[object_name]
    bpy.context.view_layer.objects.active = obj
    item = obj.b4ml.quadruped_targets["Body"]
    start = item.target.matrix_world.copy()
    item.enabled = False
    item.use_orientation = True
    source_pose = workflow.raw_pose(obj)
    action = obj.animation_data.action if obj.animation_data else None
    state = {"phase": "dismiss", "started": time.monotonic(), "events": []}

    def current():
        rig = bpy.data.objects[object_name]
        target = rig.b4ml.quadruped_targets["Body"]
        return rig, target

    def finish(report):
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print("B4ML_TARGET_RESET_UI: " + json.dumps(report), flush=True)
        bpy.ops.wm.quit_blender()
        return None

    def tick():
        try:
            if time.monotonic() - state["started"] > 120:
                raise AssertionError("Target-reset UI journey timed out")
            window = bpy.context.window_manager.windows[0]
            area = next(value for value in window.screen.areas if value.type == "VIEW_3D")
            region = next(value for value in area.regions if value.type == "WINDOW")
            ui_region = next(value for value in area.regions if value.type == "UI")
            area.spaces.active.show_region_ui = True
            if hasattr(ui_region, "active_panel_category"):
                ui_region.active_panel_category = "B4Artists ML"
            rig, target = current()
            window.view_layer.objects.active = rig
            rig.select_set(True)
            with bpy.context.temp_override(window=window, area=area, region=region):
                if state["phase"] == "dismiss":
                    window.event_simulate(type="ESC", value="PRESS")
                    bpy.ops.object.select_all(action="DESELECT")
                    target.target.select_set(True)
                    window.view_layer.objects.active = target.target
                    assert bpy.ops.transform.translate(
                        value=(0.0, 0.09, 0.0), orient_type="GLOBAL") == {"FINISHED"}
                    bpy.context.view_layer.update()
                    state["moved"] = target.target.matrix_world.copy()
                    assert bpy.ops.ed.undo_push(
                        message="Quadruped target moved") == {"FINISHED"}
                    target.target.select_set(False)
                    rig.select_set(True)
                    window.view_layer.objects.active = rig
                    state["phase"] = "reset"
                elif state["phase"] == "reset":
                    assert bpy.ops.b4ml.quadruped_pose(
                        operation="RESET_TARGET", target_name="Body") == {"FINISHED"}
                    rig, target = current()
                    assert matrix_error(target.target.matrix_world, start) < 1e-7
                    assert not target.enabled and target.use_orientation
                    assert workflow.raw_pose(rig) == source_pose
                    assert (rig.animation_data.action if rig.animation_data else None) == action
                    assert bpy.ops.ed.undo_push(
                        message="Quadruped target reset complete") == {"FINISHED"}
                    state["events"].append(
                        "Body Reset returned the helper to its preview-start transform")
                    state["phase"] = "undo"
                elif state["phase"] == "undo":
                    assert bpy.ops.ed.undo() == {"FINISHED"}
                    rig, target = current()
                    undo_count = 1
                    if matrix_error(target.target.matrix_world, state["moved"]) >= 1e-7:
                        assert bpy.ops.ed.undo() == {"FINISHED"}
                        rig, target = current()
                        undo_count = 2
                    assert matrix_error(target.target.matrix_world, state["moved"]) < 1e-7
                    assert not target.enabled and target.use_orientation
                    state["undo_count"] = undo_count
                    state["events"].append("Native Undo restored the moved helper")
                    state["phase"] = "redo"
                elif state["phase"] == "redo":
                    for _ in range(state["undo_count"]):
                        assert bpy.ops.ed.redo() == {"FINISHED"}
                    rig, target = current()
                    assert matrix_error(target.target.matrix_world, start) < 1e-7
                    assert workflow.raw_pose(rig) == source_pose
                    assert (rig.animation_data.action if rig.animation_data else None) == action
                    state["events"].append("Native Redo reapplied the per-target reset")
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
                        "events": state["events"],
                        "reset_buttons_expected": len(rig.b4ml.quadruped_targets),
                        "source_pose_unchanged": True,
                        "source_action_unchanged": True,
                        "enabled_and_orientation_preserved": True,
                        "native_undo_redo_verified": True,
                        "screenshot": str(SCREENSHOT.relative_to(ROOT)).replace("/", "\\"),
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
    LOG.parent.mkdir(parents=True, exist_ok=True)
    REPORT.unlink(missing_ok=True)
    with LOG.open("w", encoding="utf-8") as stream:
        process = subprocess.Popen(
            [os.environ.get("B4ML_BFORARTISTS", "X:/5.1.0/bforartists.exe"),
             "--factory-startup", "--no-window-focus", "--enable-event-simulate",
             "--python", str(HERE), "--", "--host"],
            cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT, startupinfo=startup,
            env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1", OPENBLAS_NUM_THREADS="4"))
        deadline = time.monotonic() + 180
        while not REPORT.is_file() and process.poll() is None and time.monotonic() < deadline:
            time.sleep(0.2)
        if not REPORT.is_file():
            if process.poll() is None:
                process.terminate()
            raise RuntimeError("Foreground target-reset journey produced no report")
        try:
            process.wait(timeout=15)
        except subprocess.TimeoutExpired:
            process.terminate()
            process.wait(timeout=10)
    value = json.loads(REPORT.read_text(encoding="utf-8"))
    if not value.get("passed"):
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
