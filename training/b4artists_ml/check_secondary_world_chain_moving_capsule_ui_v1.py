"""Exact-package foreground lifecycle for moving-capsule world-chain coupling."""

from pathlib import Path
import hashlib
import json
import math
import os
import subprocess
import sys
import time
import traceback


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve()
ARCHIVE = Path(os.environ.get(
    "B4ML_ARCHIVE",
    str(ROOT / "releases/b4artists_ml_v0.37.33-dev.zip"),
))
HELPER = ROOT / "tests/test_b4artists_ml_secondary_motion.py"
TAG = os.environ.get("B4ML_FOREGROUND_TAG", "v1")
REPORT = ROOT / f"training/b4artists_ml/results/secondary-world-chain-moving-capsule-foreground-{TAG}.json"
CHAIN_SCREENSHOT = ROOT / f"training/b4artists_ml/cache/secondary-world-chain-controls-{TAG}.png"
SCREENSHOT = ROOT / f"training/b4artists_ml/cache/secondary-world-chain-moving-capsule-controls-{TAG}.png"
COMPLETION = ROOT / f"training/b4artists_ml/cache/secondary-world-chain-moving-capsule-complete-{TAG}.png"
SAVE = ROOT / f"training/b4artists_ml/cache/secondary-world-chain-moving-capsule-kept-{TAG}.blend"
LOG = ROOT / f"training/b4artists_ml/cache/secondary-world-chain-moving-capsule-foreground-{TAG}.log"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stable_hash(value):
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")).hexdigest()


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def rig_structure(obj):
    rows = []
    for bone in sorted(obj.data.bones, key=lambda item: item.name):
        rows.append({
            "name": bone.name,
            "parent": bone.parent.name if bone.parent else None,
            "head": [float(value) for value in bone.head_local],
            "tail": [float(value) for value in bone.tail_local],
            "matrix": [float(value) for row in bone.matrix_local for value in row],
        })
    return {"bones": len(rows), "sha256": stable_hash(rows)}


def run_host():
    import bpy
    import numpy as np

    package = os.environ.get("B4ML_PACKAGE", str(ARCHIVE))
    expected_helper_sha = os.environ.get("B4ML_HELPER_SHA256", "")
    require(expected_helper_sha and sha(HELPER) == expected_helper_sha,
            "Fixture helper changed before import")
    sys.path[:0] = [package, str(ROOT / "tests")]
    import b4artists_ml
    from b4artists_ml import flight, rig_state, secondary_motion as secondary, workflow
    from test_b4artists_ml_secondary_motion import (
        animate_location_group, fixture, location_chain, make_static_endpoint)
    from mathutils import Vector

    require(Path(package).resolve() == ARCHIVE.resolve(), "Unexpected package path")
    require(str(getattr(b4artists_ml, "__file__", "")).replace("\\", "/").startswith(
            str(ARCHIVE).replace("\\", "/") + "/"),
            "Addon was not imported from the exact archive")
    b4artists_ml.register()
    bpy.context.preferences.edit.use_global_undo = True
    obj, source, _, _, _, _ = fixture("boneforge")
    scene = bpy.context.scene
    state = obj.b4ml
    chain = location_chain(obj)
    for index, definition in enumerate(chain):
        animate_location_group(state.candidate_action, obj, definition, .12 / (index + 1))
    for bone in obj.pose.bones:
        if hasattr(bone, "select"):
            bone.select = False
        else:
            bone.bone.select = False
    for bone, _, _ in chain:
        if hasattr(bone, "select"):
            bone.select = True
        else:
            bone.bone.select = True
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    if obj.mode != "POSE":
        bpy.ops.object.mode_set(mode="POSE")
    secondary.assign_control_loads(obj, (0., 0., -4.), 2.)

    positions = []
    for frame in (1, 6, 11):
        scene.frame_set(frame)
        for bone, _, _ in chain:
            positions.append((workflow.display_world(obj) @ bone.matrix).translation.copy())
    lowest = min(positions, key=lambda value: value.z)
    capsule_start = make_static_endpoint(
        "B4ML Foreground Chain Moving Capsule Start",
        lowest - Vector((0., 0., 2.03)))
    capsule_end = make_static_endpoint(
        "B4ML Foreground Chain Moving Capsule End",
        lowest - Vector((0., 0., 1.03)))
    for endpoint, base, direction in (
            (capsule_start, capsule_start.location.copy(), -1.),
            (capsule_end, capsule_end.location.copy(), 1.)):
        for frame, offset, scale in (
                (1., -.04, 1.), (6., 0., 1.08), (11., .04, 1.)):
            endpoint.location = base + Vector((offset, .02 * direction, 0.))
            endpoint.scale = (scale, scale, scale)
            endpoint.keyframe_insert(data_path="location", frame=frame)
            endpoint.keyframe_insert(data_path="scale", frame=frame)
        for curve in workflow.action_curves(
                endpoint.animation_data.action,
                getattr(endpoint.animation_data, "action_slot", None)):
            for key in curve.keyframe_points:
                key.interpolation = "LINEAR"
    scene.frame_set(1)

    state.show_secondary = True
    state.secondary_space = "WORLD"
    state.secondary_rotation = False
    state.secondary_location = True
    state.secondary_chain = True
    state.secondary_chain_propagation = .85
    state.secondary_collision = True
    state.secondary_collision_shape = "CAPSULE"
    state.secondary_capsule_start = capsule_start
    state.secondary_capsule_end = capsule_end
    state.secondary_capsule_radius = 1.
    state.secondary_capsule_moving = True
    state.secondary_capsule_scaling = True
    state.secondary_gravity = 4.
    state.secondary_collision_clearance = .01
    state.secondary_restitution = .2
    state.secondary_surface_friction = .4
    priority = state.anchors.add()
    priority.frame = 6.
    priority.payload = state.anchors[0].payload

    source_name = source.name
    input_action = state.candidate_action
    input_name = input_action.name
    source_token = flight._curve_token(obj, source)
    input_token = flight._curve_token(obj, input_action)
    capsule_names = [capsule_start.name, capsule_end.name]
    capsule_action_names = [
        capsule_start.animation_data.action.name,
        capsule_end.animation_data.action.name,
    ]
    capsule_tokens = [
        flight._curve_token(capsule_start, capsule_start.animation_data.action),
        flight._curve_token(capsule_end, capsule_end.animation_data.action),
    ]
    structure_before = rig_structure(obj)
    modes_before = stable_hash(rig_state.mode_values(obj))
    object_name = obj.name
    archive_sha = sha(ARCHIVE)
    script_sha = sha(HERE)
    helper_sha = expected_helper_sha
    journey = {"phase": "dismiss", "started": time.monotonic(), "events": [], "steps": []}
    native_step = secondary.step

    def timed_step(value):
        began = time.perf_counter()
        before = value.b4ml.secondary_progress
        try:
            return native_step(value)
        finally:
            journey["steps"].append({
                "ms": (time.perf_counter() - began) * 1000.,
                "before": before, "after": value.b4ml.secondary_progress})

    secondary.step = timed_step

    def active():
        value = bpy.data.objects[object_name]
        bpy.context.view_layer.objects.active = value
        value.select_set(True)
        return value

    def finish(value):
        secondary.step = native_step
        value.setdefault("archive", ARCHIVE.relative_to(ROOT).as_posix())
        value.setdefault("archive_sha256", archive_sha)
        value.setdefault("ui_script_sha256", script_sha)
        value.setdefault("fixture_helper", HELPER.relative_to(ROOT).as_posix())
        value.setdefault("fixture_helper_sha256", helper_sha)
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        REPORT.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
        print("B4ML_WORLD_CHAIN_MOVING_CAPSULE_FOREGROUND: " + json.dumps(value), flush=True)
        bpy.ops.wm.quit_blender()
        return None

    @bpy.app.handlers.persistent
    def after_reload(_):
        if after_reload in bpy.app.handlers.load_post:
            bpy.app.handlers.load_post.remove(after_reload)
        journey["phase"] = "after_reload"
        bpy.app.timers.register(tick, first_interval=.5)

    bpy.app.handlers.load_post.append(after_reload)

    def tick():
        try:
            if time.monotonic() - journey["started"] > 240:
                raise AssertionError("Moving-capsule world-chain foreground journey timed out")
            window = bpy.context.window_manager.windows[0]
            area = next(value for value in window.screen.areas if value.type == "VIEW_3D")
            region = next(value for value in area.regions if value.type == "WINDOW")
            ui_region = next(value for value in area.regions if value.type == "UI")
            area.spaces.active.show_region_ui = True
            if hasattr(ui_region, "active_panel_category"):
                ui_region.active_panel_category = "B4Artists ML"
            obj = active()
            state = obj.b4ml
            with bpy.context.temp_override(window=window, area=area, region=region,
                                           object=obj, active_object=obj,
                                           selected_objects=[obj], selected_editable_objects=[obj]):
                phase = journey["phase"]
                if phase == "dismiss":
                    window.event_simulate(type="ESC", value="PRESS")
                    journey["phase"] = "controls"
                    return .4
                if phase == "controls":
                    bpy.ops.view3d.view_axis(type="FRONT")
                    bpy.ops.view3d.view_selected(use_all_regions=False)
                    for _ in range(40):
                        window.event_simulate(type="WHEELUPMOUSE", value="PRESS",
                                              x=ui_region.x + ui_region.width // 2,
                                              y=ui_region.y + ui_region.height // 2)
                    journey["phase"] = "chain_capture"
                    return .4
                if phase == "chain_capture":
                    CHAIN_SCREENSHOT.parent.mkdir(parents=True, exist_ok=True)
                    bpy.ops.screen.screenshot(filepath=str(CHAIN_SCREENSHOT))
                    journey["events"].append(
                        "Captured the foreground panel at the configured World, Location, Coupled Chain, propagation, and selected-control load region for later visual review; semantic pixel verification is not automated.")
                    for _ in range(24):
                        window.event_simulate(type="WHEELDOWNMOUSE", value="PRESS",
                                              x=ui_region.x + ui_region.width // 2,
                                              y=ui_region.y + ui_region.height // 2)
                    journey["phase"] = "capture"
                    return .4
                if phase == "capture":
                    SCREENSHOT.parent.mkdir(parents=True, exist_ok=True)
                    bpy.ops.screen.screenshot(filepath=str(SCREENSHOT))
                    journey["events"].append(
                        "Captured the foreground panel at the configured Capsule, Follow Endpoint Animation, Follow Radius Scale, clearance, bounce, friction, and Preview Secondary region for later visual review; semantic pixel verification is not automated.")
                    require(bpy.ops.ed.undo_push(message="Moving capsule world-chain ready") == {"FINISHED"},
                            "Could not seed native undo")
                    require(bpy.ops.b4ml.secondary_solve("INVOKE_DEFAULT") == {"RUNNING_MODAL"},
                            "Modal preview did not start")
                    journey["phase"] = "complete"
                    return .03
                if phase == "complete":
                    if state.secondary_running:
                        return .02
                    output = state.candidate_action
                    metrics = json.loads(state.secondary_metrics)
                    require(output is not input_action, "Preview did not produce a distinct action")
                    require(obj.animation_data.action is output,
                            "Generated output action was not active for evaluation")
                    require(metrics["schema"] == 27, "Unexpected metrics schema")
                    require(metrics["backend"] == "implicit_selected_control_chain_location_moving_capsule_v1",
                            "Unexpected backend")
                    require(metrics["chain_mode"] == "WORLD_LOCATION", "Unexpected chain mode")
                    require(metrics["momentum_transfer"] is True, "Momentum transfer not reported")
                    require(metrics["collision"] is True, "Collision not reported")
                    require(metrics["collision_shape"] == "CAPSULE", "Unexpected collision shape")
                    require(metrics["relative_velocity_response"] is True,
                            "Center-relative response not reported")
                    require(metrics["relative_radius_velocity_response"] is True,
                            "Radius-relative response not reported")
                    require(metrics["priority_poses_preserved"] is True,
                            "Priority poses not reported preserved")
                    require(metrics["collision_samples"] > 0, "No collision samples reported")
                    require(metrics["max_raw_penetration"] > 0., "Fixture did not penetrate")
                    require(metrics["max_penetration_after"] <= 1e-8,
                            "Reported penetration remained")
                    require(flight._curve_token(obj, input_action) == input_token,
                            "Input action changed during preview")
                    current_endpoints = [bpy.data.objects[name] for name in capsule_names]
                    for endpoint, token in zip(current_endpoints, capsule_tokens):
                        require(flight._curve_token(
                            endpoint, endpoint.animation_data.action) == token,
                            "Capsule endpoint action changed during preview")
                    clearance_samples = []
                    for frame in range(1, 12):
                        scene.frame_set(frame)
                        bpy.context.view_layer.update()
                        evaluated = [endpoint.evaluated_get(
                            bpy.context.evaluated_depsgraph_get())
                            for endpoint in current_endpoints]
                        scales = [[abs(float(value)) for value in
                                   endpoint.matrix_world.to_scale()]
                                  for endpoint in evaluated]
                        require(all(math.isfinite(value) for scale in scales for value in scale),
                                "Animated capsule scale was non-finite")
                        require(all(max(scale) - min(scale) <= 1e-5 for scale in scales),
                                "Animated capsule scale was not uniform")
                        require(max(abs(a - b) for a, b in zip(scales[0], scales[1])) <= 1e-5,
                                "Animated capsule endpoint scales did not match")
                        start = evaluated[0].matrix_world.translation
                        end = evaluated[1].matrix_world.translation
                        require(all(math.isfinite(float(value)) for point in (start, end)
                                    for value in point),
                                "Animated capsule endpoint was non-finite")
                        axis = end - start
                        axis_sq = float(axis.length_squared)
                        require(axis_sq > 1e-12, "Animated capsule was degenerate")
                        radius = (float(state.secondary_capsule_radius)
                                  * sum(scales[0]) / 3.)
                        require(math.isfinite(radius), "Animated capsule radius was non-finite")
                        for bone_name in metrics["chain_controls"]:
                            position = (workflow.display_world(obj) @ obj.pose.bones[bone_name].matrix).translation
                            require(all(math.isfinite(float(value)) for value in position),
                                    "Evaluated control position was non-finite")
                            amount = max(0., min(1., float((position - start).dot(axis)) / axis_sq))
                            nearest = start + axis * amount
                            clearance = float((position - nearest).length - radius
                                              - state.secondary_collision_clearance)
                            require(math.isfinite(clearance), "Evaluated clearance was non-finite")
                            clearance_samples.append(clearance)
                    scene.frame_set(1)
                    minimum_clearance = min(clearance_samples)
                    require(minimum_clearance >= -1e-6,
                            "Independent evaluated action sample penetrated the animated capsule")
                    journey["output"] = output.name
                    journey["output_token"] = flight._curve_token(obj, output)
                    journey["metrics"] = metrics
                    journey["independent_clearance"] = {
                        "samples": len(clearance_samples),
                        "minimum": minimum_clearance,
                        "tolerance": 1e-6,
                        "passed": True,
                    }
                    bpy.ops.screen.screenshot(filepath=str(COMPLETION))
                    journey["events"].append("Foreground Preview Secondary generated editable schema-27 moving-capsule world-chain motion.")
                    journey["phase"] = "settle"
                    return .3
                if phase == "settle":
                    require(bpy.ops.ed.undo() == {"FINISHED"}, "Native Undo failed")
                    journey["phase"] = "undo"
                    return .1
                if phase == "undo":
                    obj = active()
                    require(obj.b4ml.candidate_action.name == input_name,
                            "Undo did not restore the input action")
                    require(flight._curve_token(obj, obj.b4ml.candidate_action) == input_token,
                            "Undo restored the input name but not its curves")
                    require(bpy.ops.ed.redo() == {"FINISHED"}, "Native Redo failed")
                    journey["events"].append("Native Undo restored the input action.")
                    journey["phase"] = "redo"
                    return .1
                if phase == "redo":
                    obj = active()
                    require(obj.b4ml.candidate_action.name == journey["output"],
                            "Redo did not restore the output action")
                    require(flight._curve_token(obj, obj.b4ml.candidate_action) == journey["output_token"],
                            "Redo restored the output name but not its curves")
                    journey["events"].append("Native Redo restored the schema-27 result.")
                    require(bpy.ops.b4ml.secondary(operation="RESET") == {"FINISHED"},
                            "Restore Input failed")
                    require(obj.b4ml.candidate_action.name == input_name,
                            "Restore Input did not restore the input action")
                    require(flight._curve_token(obj, obj.b4ml.candidate_action) == input_token,
                            "Restore Input restored the name but not the curves")
                    journey["events"].append("Restore Input returned to the retained candidate.")
                    require(bpy.ops.b4ml.secondary_solve() == {"FINISHED"},
                            "Synchronous regeneration failed")
                    require(bpy.ops.b4ml.action(operation="KEEP") == {"FINISHED"}, "Keep failed")
                    kept = obj.b4ml.kept_action
                    require(kept is not None and obj.animation_data.action == kept,
                            "Keep did not retain the active result")
                    journey["kept"] = kept.name
                    journey["kept_token"] = flight._curve_token(obj, kept)
                    require(bpy.ops.wm.save_as_mainfile(filepath=str(SAVE)) == {"FINISHED"},
                            "Save for reload failed")
                    journey["events"].append("Keep retained the editable result and saved it for reload recovery.")
                    bpy.ops.wm.open_mainfile(filepath=str(SAVE))
                    return .1
                if phase == "after_reload":
                    obj = active()
                    state = obj.b4ml
                    reloaded_endpoints = [bpy.data.objects[name] for name in capsule_names]
                    require(state.kept_action is not None, "Kept action missing after reload")
                    require(state.kept_action.name == journey["kept"],
                            "Wrong kept action after reload")
                    require(obj.animation_data.action == state.kept_action,
                            "Kept action was not active after reload")
                    require(flight._curve_token(obj, state.kept_action) == journey["kept_token"],
                            "Kept action curves changed across reload")
                    require(state.secondary_chain is True, "Chain setting was not retained")
                    require(state.secondary_space == "WORLD", "World-space setting was not retained")
                    require(state.secondary_location is True, "Location setting was not retained")
                    require(state.secondary_collision_shape == "CAPSULE",
                            "Capsule shape setting was not retained")
                    require(state.secondary_capsule_start == reloaded_endpoints[0]
                            and state.secondary_capsule_end == reloaded_endpoints[1],
                            "Capsule endpoint bindings were not retained")
                    require(state.secondary_capsule_moving is True,
                            "Moving-capsule setting was not retained")
                    require(state.secondary_capsule_scaling is True,
                            "Scaling-capsule setting was not retained")
                    saved_metrics = json.loads(state.kept_action["b4ml_secondary_metrics"])
                    require(saved_metrics["schema"] == 27, "Saved schema was not retained")
                    require(saved_metrics["backend"] ==
                            "implicit_selected_control_chain_location_moving_capsule_v1",
                            "Saved backend was not retained")
                    for endpoint, action_name, token in zip(
                            reloaded_endpoints, capsule_action_names, capsule_tokens):
                        require(flight._curve_token(
                            endpoint, bpy.data.actions[action_name]) == token,
                            "Capsule endpoint action changed across reload")
                    journey["events"].append("Save/reload preserved the kept schema-27 action and moving/scaling capsule bindings.")
                    require(bpy.ops.b4ml.action(operation="RESTORE_SOURCE") == {"FINISHED"},
                            "Restore Source failed")
                    require(obj.animation_data.action.name == source_name,
                            "Restore Source did not bind the source action")
                    require(flight._curve_token(obj, obj.animation_data.action) == source_token,
                            "Source action curves changed")
                    require(rig_structure(obj) == structure_before, "Rig structure changed")
                    require(stable_hash(rig_state.mode_values(obj)) == modes_before,
                            "Rig modes changed")
                    journey["events"].append("Restore Source recovered the original Action, rig structure, and rig modes after reload.")
                    durations = [item["ms"] for item in journey["steps"]]
                    return finish({
                        "schema": 1,
                        "status": "ASSERTIONS_PASS_SHUTDOWN_PENDING",
                        "passed": False,
                        "assertions_passed": True,
                        "feature": "procedural moving and uniformly scaling capsule world-location selected-control chain coupling",
                        "host": {"application": "Bforartists", "version": bpy.app.version_string},
                        "package_import_origin": str(b4artists_ml.__file__).replace("\\", "/"),
                        "events": journey["events"],
                        "metrics": journey["metrics"],
                        "independent_clearance": journey["independent_clearance"],
                        "native_undo_redo": True,
                        "restore_input": True,
                        "keep_save_reload": True,
                        "restore_source": True,
                        "source_action_unchanged": True,
                        "capsule_endpoint_actions_unchanged": True,
                        "rig_structure_recovered": True,
                        "rig_modes_recovered": True,
                        "chain_controls_screenshot": CHAIN_SCREENSHOT.relative_to(ROOT).as_posix(),
                        "chain_controls_screenshot_sha256": sha(CHAIN_SCREENSHOT),
                        "visible_controls_screenshot": SCREENSHOT.relative_to(ROOT).as_posix(),
                        "visible_controls_screenshot_sha256": sha(SCREENSHOT),
                        "completion_screenshot": COMPLETION.relative_to(ROOT).as_posix(),
                        "completion_screenshot_sha256": sha(COMPLETION),
                        "screenshot_semantic_verification": "manual_review_required",
                        "save_path": SAVE.relative_to(ROOT).as_posix(),
                        "step_count": len(durations),
                        "step_p95_ms": float(np.percentile(durations, 95)),
                        "step_max_ms": max(durations),
                        "learned_temporal_quality": False,
                        "independent_animator_usability": False,
                        "cascadeur_comparison": False,
                        "scope": "Automated exact-package foreground BoneForge lifecycle evidence for one directly animated and uniformly scaling capsule collider in selected-control world-location chain mode; no human usability, broad dynamics, learned-motion, production-character, or Cascadeur claim.",
                    })
        except Exception:
            return finish({"schema": 1, "status": "FAIL", "passed": False,
                           "phase": journey["phase"], "events": journey["events"],
                           "error": traceback.format_exc()})
        return .03

    bpy.app.timers.register(tick, first_interval=.5)


def launch():
    REPORT.unlink(missing_ok=True)
    LOG.parent.mkdir(parents=True, exist_ok=True)
    startup = subprocess.STARTUPINFO()
    startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startup.wShowWindow = 0
    helper_sha = sha(HELPER)
    env = dict(os.environ, B4ML_PACKAGE=str(ARCHIVE), B4ML_ARCHIVE=str(ARCHIVE),
               B4ML_HELPER_SHA256=helper_sha,
               PYTHONOPTIMIZE="0", PYTHONDONTWRITEBYTECODE="1", OPENBLAS_NUM_THREADS="4")
    started = time.perf_counter()

    def stop_process(process):
        if process.poll() is not None:
            return
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=10)

    with LOG.open("w", encoding="utf-8") as stream:
        process = subprocess.Popen(
            [os.environ.get("B4ML_BFORARTISTS", "X:/5.1.0/bforartists.exe"),
             "--factory-startup", "--no-window-focus", "--enable-event-simulate",
             "--python", str(HERE), "--", "--host"],
            cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT,
            startupinfo=startup, env=env)
        deadline = time.monotonic() + 270
        while not REPORT.is_file() and process.poll() is None and time.monotonic() < deadline:
            time.sleep(.2)
        if not REPORT.is_file():
            stop_process(process)
            raise RuntimeError("Foreground moving-capsule world-chain journey produced no report")
        try:
            process.wait(timeout=15)
        except subprocess.TimeoutExpired:
            stop_process(process)
    value = json.loads(REPORT.read_text(encoding="utf-8"))
    log_text = LOG.read_text(encoding="utf-8", errors="replace")
    clean_exit = process.returncode == 0
    known_shutdown_fault = (
        process.returncode == 0xC0000005
        and "EXCEPTION_ACCESS_VIOLATION" in log_text
        and "ucrtbase.dll" in log_text
        and "Bforartists quit" in log_text
    )
    require(clean_exit or known_shutdown_fault,
            "Unexpected Bforartists exit after the foreground assertions")
    require(value.get("passed") is False and value.get("assertions_passed") is True,
            "Foreground child assertions did not produce a fail-closed provisional receipt")
    require(value.get("status") == "ASSERTIONS_PASS_SHUTDOWN_PENDING",
            "Child receipt was not provisional")
    require(value.get("archive_sha256") == sha(ARCHIVE), "Receipt archive hash mismatch")
    require(value.get("ui_script_sha256") == sha(HERE), "Receipt script hash mismatch")
    require(value.get("fixture_helper_sha256") == helper_sha == sha(HELPER),
            "Fixture helper hash mismatch")
    require(value.get("package_import_origin", "").startswith(
            str(ARCHIVE).replace("\\", "/") + "/"), "Receipt import origin mismatch")
    value.update({
        "passed": True,
        "status": ("PASS_CLEAN_EXIT" if clean_exit
                   else "PASS_WITH_OBSERVED_KNOWN_HOST_SHUTDOWN_LIMITATION"),
        "process_exit_code": process.returncode,
        "process_exit_clean": clean_exit,
        "known_shutdown_fault_observed": known_shutdown_fault,
        "shutdown_signature": ("EXCEPTION_ACCESS_VIOLATION:ucrtbase.dll"
                               if known_shutdown_fault else None),
        "elapsed_seconds": time.perf_counter() - started,
    })
    REPORT.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "passed": True,
        "process_exit_code": process.returncode,
        "process_exit_clean": clean_exit,
        "known_shutdown_fault_observed": known_shutdown_fault,
        "assertions_completed_before_shutdown": True,
        "seconds": time.perf_counter() - started,
        "report": REPORT.relative_to(ROOT).as_posix(),
        "report_sha256": sha(REPORT),
        "archive_sha256": sha(ARCHIVE),
    }, indent=2))


if __name__ == "__main__":
    if "--host" in sys.argv:
        run_host()
    else:
        launch()
