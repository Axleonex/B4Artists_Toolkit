"""Foreground Bforartists journey for bounds-created sphere proxies."""
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
TEST = ROOT / "tests/test_b4artists_ml_secondary_sphere_proxy_v1.py"
DEPENDENCIES = tuple(ROOT / "tests" / name for name in (
    "test_b4artists_ml_secondary_sphere_collision_v1.py",
    "test_b4artists_ml_secondary_motion.py",
    "test_b4artists_ml_contacts.py",
    "test_b4artists_ml_posing.py",
))
REPORT = ROOT / "docs/b4artists_ml/secondary-sphere-proxy-ui-v1.json"
SCREENSHOT = ROOT / "training/b4artists_ml/cache/secondary-sphere-proxy-ui-v1.png"
LOG = ROOT / "training/b4artists_ml/cache/secondary-sphere-proxy-ui-v1.log"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def runtime_hashes():
    return {"b4artists_ml/" + path.name: sha(path)
            for path in sorted((ROOT / "b4artists_ml").glob("*.py"))}


def run_host():
    if sys.flags.optimize != 0:
        raise RuntimeError("Sphere-proxy foreground verification requires Python assertions")
    import bpy
    import numpy as np
    sys.path[:0] = [str(ROOT), str(ROOT / "tests")]
    import b4artists_ml
    from mathutils import Vector
    from b4artists_ml import quadruped_gait, secondary_motion as secondary
    from test_b4artists_ml_secondary_sphere_collision_v1 import sphere_fixture
    from test_b4artists_ml_secondary_sphere_proxy_v1 import make_offset_box

    b4artists_ml.register()
    frozen_runtime = runtime_hashes()
    frozen_script = sha(HERE)
    frozen_test = sha(TEST)
    frozen_dependencies = {
        str(path.relative_to(ROOT)).replace("\\", "/"): sha(path)
        for path in DEPENDENCIES
    }
    bpy.context.preferences.edit.use_global_undo = True
    rig, source, control, placeholder, _ = sphere_fixture("boneforge")
    bounds_source = make_offset_box(
        "B4ML Foreground Proxy Bounds",
        placeholder.location - Vector((0.12, -0.04, 0.08)),
        (0.12, -0.04, 0.08), (0.05773502691896258,) * 3)
    rig.b4ml.secondary_sphere_collider = bounds_source
    rig.b4ml.secondary_sphere_radius = 0.02
    object_name = rig.name
    source_name = source.name
    source_token = quadruped_gait._action_digest(rig, source)
    bounds_source_name = bounds_source.name
    bounds_source_matrix = tuple(tuple(row) for row in bounds_source.matrix_world)
    bounds_source_vertices = tuple(tuple(vertex.co) for vertex in bounds_source.data.vertices)
    bpy.context.view_layer.objects.active = rig
    rig.select_set(True)
    if rig.mode != "POSE":
        bpy.ops.object.mode_set(mode="POSE")
    rig.data.bones.active = rig.data.bones[control]
    rig.b4ml.show_secondary = True
    bpy.ops.ed.undo_push(message="Before sphere proxy creation")
    assert bpy.ops.b4ml.secondary_sphere(operation="PROXY", index=-1) == {"FINISHED"}
    assert len(rig.b4ml.secondary_spheres) == 1
    proxy = rig.b4ml.secondary_spheres[0].collider
    proxy_name = proxy.name
    assert abs(rig.b4ml.secondary_spheres[0].radius - 0.1) <= 1e-6
    assert (proxy.matrix_world.translation - placeholder.matrix_world.translation).length <= 1e-6
    bpy.ops.ed.undo_push(message="Sphere proxy creation complete")
    assert bpy.ops.ed.undo() == {"FINISHED"}
    rig = bpy.data.objects[object_name]
    assert proxy_name not in bpy.data.objects and len(rig.b4ml.secondary_spheres) == 0
    assert bpy.ops.ed.redo() == {"FINISHED"}
    rig = bpy.data.objects[object_name]
    proxy = bpy.data.objects[proxy_name]
    assert len(rig.b4ml.secondary_spheres) == 1
    input_action = rig.b4ml.candidate_action
    input_name = input_action.name
    input_token = quadruped_gait._action_digest(rig, input_action)
    collider_names = [proxy.name]
    state = {"phase": "dismiss", "started": time.monotonic(),
             "events": [], "steps": []}
    native_step = secondary.step

    def timed(value):
        began = time.perf_counter()
        before = value.b4ml.secondary_progress
        try:
            return native_step(value)
        finally:
            state["steps"].append({"ms": (time.perf_counter() - began) * 1000,
                                   "before": before,
                                   "after": value.b4ml.secondary_progress})

    secondary.step = timed

    def current():
        value = bpy.data.objects[object_name]
        bpy.context.view_layer.objects.active = value
        value.select_set(True)
        return value

    def finish(value):
        value["python_optimize"] = sys.flags.optimize
        if value.get("passed"):
            if (runtime_hashes() != frozen_runtime or sha(HERE) != frozen_script
                    or sha(TEST) != frozen_test
                    or any(sha(ROOT / relative) != digest
                           for relative, digest in frozen_dependencies.items())):
                raise AssertionError("Source changed during sphere-proxy UI journey")
            value["runtime_source_count"] = len(frozen_runtime)
            value["runtime_source_sha256"] = frozen_runtime
            value["ui_script_sha256"] = frozen_script
            value["test_script_sha256"] = frozen_test
            value["fixture_source_sha256"] = frozen_dependencies
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        REPORT.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
        print("B4ML_SECONDARY_SPHERE_PROXY_UI: " + json.dumps(value), flush=True)
        bpy.ops.wm.quit_blender()
        return None

    def tick():
        try:
            if time.monotonic() - state["started"] > 180:
                raise AssertionError("Sphere-proxy UI journey timed out")
            window = bpy.context.window_manager.windows[0]
            area = next(value for value in window.screen.areas if value.type == "VIEW_3D")
            region = next(value for value in area.regions if value.type == "WINDOW")
            ui_region = next(value for value in area.regions if value.type == "UI")
            area.spaces.active.show_region_ui = True
            if hasattr(ui_region, "active_panel_category"):
                ui_region.active_panel_category = "B4Artists ML"
            rig = current()
            with bpy.context.temp_override(
                    window=window, area=area, region=region, object=rig,
                    active_object=rig, selected_objects=[rig],
                    selected_editable_objects=[rig]):
                phase = state["phase"]
                if phase == "dismiss":
                    window.event_simulate(type="ESC", value="PRESS")
                    state["phase"] = "open"
                    return .4
                if phase == "open":
                    bpy.ops.view3d.view_axis(type="FRONT")
                    bpy.ops.view3d.view_selected(use_all_regions=False)
                    for _ in range(22):
                        window.event_simulate(
                            type="WHEELDOWNMOUSE", value="PRESS",
                            x=ui_region.x + ui_region.width // 2,
                            y=ui_region.y + ui_region.height // 2)
                    state["phase"] = "capture"
                    return .5
                if phase == "capture":
                    SCREENSHOT.parent.mkdir(parents=True, exist_ok=True)
                    bpy.ops.screen.screenshot(filepath=str(SCREENSHOT))
                    state["events"].append(
                        "Displayed a bounds-created proxy row and the visible Create Bounds Proxy control")
                    bpy.ops.ed.undo_push(message="Sphere proxy workflow ready")
                    assert bpy.ops.b4ml.secondary_solve("INVOKE_DEFAULT") == {"RUNNING_MODAL"}
                    state["phase"] = "complete"
                    return .03
                if phase == "complete":
                    if rig.b4ml.secondary_running:
                        return .02
                    output = rig.b4ml.candidate_action
                    assert output is not input_action
                    assert rig.b4ml.secondary_input is input_action
                    metrics = json.loads(rig.b4ml.secondary_metrics)
                    assert metrics["schema"] == 9
                    assert metrics["backend"] == "implicit_selected_control_secondary_v8"
                    assert metrics["collision_shape"] == "SPHERE"
                    assert metrics["collision_surface"] == "STATIC_SPHERE:" + collider_names[0]
                    assert metrics["collision_sphere_count"] == 1
                    assert [item["collider"] for item in metrics["collision_spheres"]] == collider_names
                    assert [item.get("moving", False)
                            for item in metrics["collision_spheres"]] == [False]
                    assert [item.get("scaling", False)
                            for item in metrics["collision_spheres"]] == [False]
                    assert abs(metrics["collision_spheres"][0]["radius"] - .1) <= 1e-6
                    assert "moving_collision_spheres" not in metrics
                    assert "scaling_collision_spheres" not in metrics
                    assert "relative_radius_velocity_response" not in metrics
                    assert "collision_target_space" not in metrics
                    assert abs(metrics["collision_sphere_radius"] - .1) <= 1e-6
                    assert metrics["collision_samples"] > 0
                    assert metrics["max_raw_penetration"] > 0
                    assert metrics["max_desired_penetration_after"] <= 1e-8
                    assert metrics["max_penetration_after"] <= 1e-6
                    assert metrics["collision_penetration_tolerance"] == 1e-6
                    assert metrics["priority_poses_preserved"]
                    assert metrics["max_world_location_error"] <= 2e-4
                    assert quadruped_gait._action_digest(rig, input_action) == input_token
                    proxy = bpy.data.objects[collider_names[0]]
                    assert proxy.type == "EMPTY" and proxy.parent is None
                    assert proxy.get("b4ml_sphere_proxy") is True
                    assert proxy.get("b4ml_sphere_source") == bounds_source_name
                    state["metrics"] = metrics
                    state["output"] = output.name
                    state["events"].append(
                        "Generated editable motion using the unparented bounds-created sphere proxy")
                    state["phase"] = "settle"
                    return .3
                if phase == "settle":
                    assert bpy.ops.ed.undo() == {"FINISHED"}
                    state["phase"] = "undo"
                    return .1
                if phase == "undo":
                    rig = current()
                    assert rig.b4ml.candidate_action.name == input_name
                    assert rig.animation_data.action == rig.b4ml.candidate_action
                    assert bpy.ops.ed.redo() == {"FINISHED"}
                    state["events"].append("Native Undo restored the collision input")
                    state["phase"] = "redo"
                    return .1
                if phase == "redo":
                    rig = current()
                    assert rig.b4ml.candidate_action.name == state["output"]
                    state["events"].append("Native Redo restored the proxy-collision result")
                    assert bpy.ops.b4ml.secondary(operation="RESET") == {"FINISHED"}
                    assert rig.b4ml.candidate_action.name == input_name
                    assert rig.animation_data.action == rig.b4ml.candidate_action
                    state["events"].append("Restore returned to the retained input")
                    assert bpy.ops.b4ml.secondary_solve() == {"FINISHED"}
                    assert bpy.ops.b4ml.action(operation="KEEP") == {"FINISHED"}
                    assert bpy.ops.b4ml.action(operation="RESTORE_SOURCE") == {"FINISHED"}
                    assert rig.animation_data.action.name == source_name
                    durations = [row["ms"] for row in state["steps"]]
                    state["events"].append("Keep and Restore Source retained ordinary recovery")
                    return finish({
                        "schema": 1, "passed": True,
                        "host": bpy.app.version_string,
                        "fixture": "BoneForge",
                        "events": state["events"],
                        "metrics": state["metrics"],
                        "solve_native_undo_steps": 1,
                        "solve_native_redo_steps": 1,
                        "proxy_creation_native_undo_steps": 1,
                        "proxy_creation_native_redo_steps": 1,
                        "step_count": len(durations),
                        "step_p95_ms": float(np.percentile(durations, 95)),
                        "step_max_ms": max(durations),
                        "source_action_unchanged": (
                            quadruped_gait._action_digest(
                                rig, bpy.data.actions[source_name]) == source_token),
                        "bounds_source_unchanged": (
                            tuple(tuple(row) for row in bpy.data.objects[
                                bounds_source_name].matrix_world) == bounds_source_matrix
                            and tuple(tuple(vertex.co) for vertex in bpy.data.objects[
                                bounds_source_name].data.vertices) == bounds_source_vertices),
                        "action_preservation_digest_boundary": (
                            "Action and direct object's AnimData evaluation settings; action slot, "
                            "layer, strip and channelbag structure; curves, keys, samples and modifiers. "
                            "Unrelated object and scene data are outside this digest."),
                        "screenshot": str(SCREENSHOT.relative_to(ROOT)).replace("\\", "/"),
                        "screenshot_sha256": sha(SCREENSHOT),
                        "scope": (
                            "Automated foreground BoneForge selected-control journey that creates and adds "
                            "one unparented Empty sphere proxy at a mesh object's world-bounds center, then "
                            "uses sampled point exclusion, proxy creation and solve native Undo/Redo, "
                            "restore, keep, and source recovery. Proxy creation is a snapshot and does "
                            "not verify arbitrary or deforming mesh collision, bone or mesh "
                            "volumes, continuous collision, self-collision, learned motion, independent "
                            "animator judgment, or parity."),
                    })
        except Exception:
            return finish({"schema": 1, "passed": False, "phase": state["phase"],
                           "events": state["events"], "error": traceback.format_exc()})
        return .03

    bpy.app.timers.register(tick, first_interval=.5)


def launch():
    if sys.flags.optimize != 0:
        raise RuntimeError("Sphere-proxy foreground launcher requires Python assertions")
    startup = subprocess.STARTUPINFO()
    startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startup.wShowWindow = 0
    frozen_runtime = runtime_hashes()
    frozen_script = sha(HERE)
    frozen_test = sha(TEST)
    frozen_dependencies = {
        str(path.relative_to(ROOT)).replace("\\", "/"): sha(path)
        for path in DEPENDENCIES
    }
    REPORT.unlink(missing_ok=True)
    LOG.parent.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    child_env = dict(os.environ)
    child_env.pop("PYTHONOPTIMIZE", None)
    child_env.update(PYTHONDONTWRITEBYTECODE="1", OPENBLAS_NUM_THREADS="4")
    with LOG.open("w", encoding="utf-8") as stream:
        process = subprocess.Popen(
            [os.environ.get("B4ML_BFORARTISTS", "X:/5.1.0/bforartists.exe"),
             "--factory-startup", "--no-window-focus", "--enable-event-simulate",
             "--python", str(HERE), "--", "--host"],
            cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT, startupinfo=startup,
            env=child_env)
        deadline = time.monotonic() + 210
        while not REPORT.is_file() and process.poll() is None and time.monotonic() < deadline:
            time.sleep(.2)
        if not REPORT.is_file():
            if process.poll() is None:
                process.terminate()
            raise RuntimeError("Foreground sphere-proxy journey produced no report")
        try:
            process.wait(timeout=15)
        except subprocess.TimeoutExpired:
            process.terminate()
            process.wait(timeout=10)
    value = json.loads(REPORT.read_text(encoding="utf-8"))
    if (not value.get("passed") or runtime_hashes() != frozen_runtime
            or sha(HERE) != frozen_script or sha(TEST) != frozen_test
            or any(sha(ROOT / relative) != digest
                   for relative, digest in frozen_dependencies.items())
            or value.get("runtime_source_sha256") != frozen_runtime
            or value.get("ui_script_sha256") != frozen_script
            or value.get("test_script_sha256") != frozen_test
            or value.get("fixture_source_sha256") != frozen_dependencies
            or value.get("python_optimize") != 0):
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
