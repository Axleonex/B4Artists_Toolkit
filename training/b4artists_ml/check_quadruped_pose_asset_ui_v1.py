"""Foreground Bforartists journey for quadruped pose Save/Apply and Undo/Redo."""
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
REPORT = ROOT / "docs/b4artists_ml/quadruped-pose-asset-ui-v1.json"
SCREENSHOT = ROOT / "training/b4artists_ml/cache/quadruped-pose-asset-ui-v1.png"
LOG = ROOT / "training/b4artists_ml/cache/quadruped-pose-asset-ui-v1.log"
BLEND = ROOT / "training/b4artists_ml/cache/quadruped-pose-asset-ui-v1.blend"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def runtime_hashes():
    return {str(path.relative_to(ROOT)).replace("\\", "/"): sha(path)
            for path in sorted((ROOT / "b4artists_ml").glob("*.py"))}


def matrix_error(actual, expected):
    return max(abs(actual[row][column] - expected[row][column])
               for row in range(4) for column in range(4))


def run_host():
    import addon_utils
    import bpy
    from mathutils import Quaternion, Vector
    sys.path[:0] = [str(ROOT), str(ROOT / "tests")]
    import b4artists_ml
    from b4artists_ml import quadruped_pose as pose
    from b4artists_ml import workflow
    from test_b4artists_ml_quadruped_pose import _generate

    addon_utils.enable("rigify", default_set=True, persistent=False)
    b4artists_ml.register()
    bpy.context.preferences.edit.use_global_undo = True
    frozen_runtime = runtime_hashes()
    frozen_script = sha(HERE)

    source_scene, source = _generate("cat")
    bpy.context.view_layer.objects.active = source
    pose.begin(source, source_scene)
    source.b4ml.quadruped_spine_follow = 0.42
    source.b4ml.quadruped_neck_share = 0.68
    paw = source.b4ml.quadruped_targets["Fore Paw L"]
    paw.target.location += Vector((0.035, -0.018, 0.012))
    paw.use_orientation = True
    paw.target.rotation_quaternion.rotate(Quaternion((0.0, 1.0, 0.0), 0.04))
    bpy.context.view_layer.update()
    pose.solve(source, source_scene)
    assert bpy.ops.b4ml.quadruped_pose(operation="SAVE_POSE_ASSET") == {"FINISHED"}
    asset_text = source_scene[pose.POSE_ASSET_KEY]
    asset = pose._read_pose_asset(source_scene)
    pose.finish(source, source_scene, False)

    scene, obj = _generate("horse")
    obj.name = "B4ML Pose Asset UI Rig"
    object_name = obj.name
    scene[pose.POSE_ASSET_KEY] = asset_text
    bpy.context.view_layer.objects.active = obj
    pose.begin(obj, scene)
    bpy.context.view_layer.update()
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))
    bpy.ops.wm.open_mainfile(filepath=str(BLEND), use_scripts=False)
    scene = bpy.context.scene
    obj = bpy.data.objects[object_name]
    bpy.context.view_layer.objects.active = obj
    source_pose = workflow.raw_pose(obj)
    source_action = obj.animation_data.action if obj.animation_data else None
    state = {"phase": "apply", "started": time.monotonic(), "events": []}

    def current():
        rig = bpy.data.objects[object_name]
        return rig, rig.b4ml.quadruped_targets["Fore Paw L"]

    def finish(report):
        if report.get("passed"):
            if runtime_hashes() != frozen_runtime or sha(HERE) != frozen_script:
                raise AssertionError("Source changed during quadruped pose-asset UI journey")
            report["runtime_source_count"] = len(frozen_runtime)
            report["runtime_source_sha256"] = frozen_runtime
            report["ui_script_sha256"] = frozen_script
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print("B4ML_QUADRUPED_POSE_ASSET_UI: " + json.dumps(report), flush=True)
        bpy.ops.wm.quit_blender()
        return None

    def tick():
        try:
            if time.monotonic() - state["started"] > 150:
                raise AssertionError("Quadruped pose-asset UI journey timed out")
            window = bpy.context.window_manager.windows[0]
            area = next(value for value in window.screen.areas if value.type == "VIEW_3D")
            region = next(value for value in area.regions if value.type == "WINDOW")
            ui_region = next(value for value in area.regions if value.type == "UI")
            area.spaces.active.show_region_ui = True
            if hasattr(ui_region, "active_panel_category"):
                ui_region.active_panel_category = "B4Artists ML"
            rig, paw_item = current()
            window.view_layer.objects.active = rig
            rig.select_set(True)
            with bpy.context.temp_override(window=window, area=area, region=region):
                if state["phase"] == "apply":
                    window.event_simulate(type="ESC", value="PRESS")
                    state["before"] = {item.name: item.target.matrix_world.copy()
                                       for item in rig.b4ml.quadruped_targets}
                    state["follow_before"] = rig.b4ml.quadruped_spine_follow
                    state["neck_before"] = rig.b4ml.quadruped_neck_share
                    assert bpy.ops.b4ml.quadruped_pose(
                        operation="APPLY_POSE_ASSET") == {"FINISHED"}
                    rig, paw_item = current()
                    state["after"] = {item.name: item.target.matrix_world.copy()
                                      for item in rig.b4ml.quadruped_targets}
                    assert matrix_error(paw_item.target.matrix_world,
                                        state["before"]["Fore Paw L"]) > 1e-5
                    assert abs(rig.b4ml.quadruped_spine_follow - asset["spine_follow"]) < 1e-7
                    assert abs(rig.b4ml.quadruped_neck_share - asset["neck_share"]) < 1e-7
                    assert json.loads(rig.b4ml.quadruped_payload)["signature"] is None
                    assert workflow.raw_pose(rig) == source_pose
                    assert (rig.animation_data.action if rig.animation_data else None) == source_action
                    assert bpy.ops.ed.undo_push(message="Quadruped pose asset applied") == {"FINISHED"}
                    state["events"].append("Applied the Cat pose request to the Horse preview")
                    state["phase"] = "undo"
                elif state["phase"] == "undo":
                    undo_count = 0
                    while undo_count < 3:
                        assert bpy.ops.ed.undo() == {"FINISHED"}
                        undo_count += 1
                        rig, paw_item = current()
                        if matrix_error(paw_item.target.matrix_world,
                                        state["before"]["Fore Paw L"]) < 1e-7:
                            break
                    assert matrix_error(paw_item.target.matrix_world,
                                        state["before"]["Fore Paw L"]) < 1e-7
                    assert abs(rig.b4ml.quadruped_spine_follow - state["follow_before"]) < 1e-7
                    assert abs(rig.b4ml.quadruped_neck_share - state["neck_before"]) < 1e-7
                    state["undo_count"] = undo_count
                    state["events"].append("Native Undo restored the pre-apply request")
                    state["phase"] = "redo"
                elif state["phase"] == "redo":
                    for _ in range(state["undo_count"]):
                        assert bpy.ops.ed.redo() == {"FINISHED"}
                    rig, paw_item = current()
                    for label, expected in state["after"].items():
                        assert matrix_error(rig.b4ml.quadruped_targets[label].target.matrix_world,
                                            expected) < 1e-6
                    assert abs(rig.b4ml.quadruped_spine_follow - asset["spine_follow"]) < 1e-7
                    assert abs(rig.b4ml.quadruped_neck_share - asset["neck_share"]) < 1e-7
                    assert workflow.raw_pose(rig) == source_pose
                    assert (rig.animation_data.action if rig.animation_data else None) == source_action
                    state["events"].append("Native Redo reapplied the cross-profile request")
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
                        "source_profile": asset["source_profile"],
                        "target_profile": json.loads(rig.b4ml.quadruped_payload)["profile"],
                        "save_operator_verified": True,
                        "apply_operator_verified": True,
                        "cross_profile": True,
                        "source_pose_unchanged": True,
                        "source_action_unchanged": True,
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
    frozen_runtime = runtime_hashes()
    frozen_script = sha(HERE)
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
            raise RuntimeError("Foreground quadruped pose-asset journey produced no report")
        try:
            process.wait(timeout=15)
        except subprocess.TimeoutExpired:
            process.terminate()
            process.wait(timeout=10)
    value = json.loads(REPORT.read_text(encoding="utf-8"))
    if (not value.get("passed") or runtime_hashes() != frozen_runtime or
            sha(HERE) != frozen_script or
            value.get("runtime_source_sha256") != frozen_runtime or
            value.get("runtime_source_count") != len(frozen_runtime) or
            value.get("ui_script_sha256") != frozen_script):
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
