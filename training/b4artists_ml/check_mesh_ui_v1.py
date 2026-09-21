"""Foreground static arbitrary-mesh controls and action-recovery journey."""

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
TAG = os.environ.get("B4ML_MESH_UI_TAG", "mesh-ui-v1")
MODAL = os.environ.get("B4ML_MESH_UI_MODAL", "1") == "1"
DEFORMING = os.environ.get("B4ML_MESH_UI_DEFORMING", "0") == "1"
VOLUME = os.environ.get("B4ML_MESH_UI_VOLUME", "0") == "1"
CONTINUOUS = os.environ.get("B4ML_MESH_UI_CONTINUOUS", "0") == "1"
MOVING = os.environ.get("B4ML_MESH_UI_MOVING", "0") == "1"
EXACT_SWEPT_VOLUME = CONTINUOUS and VOLUME and not DEFORMING and not MOVING
BOUNDED_SWEPT_VOLUME = CONTINUOUS and VOLUME and (DEFORMING or MOVING)


def write_report(report):
    path = ROOT / "docs" / "b4artists_ml" / f"{TAG}.json"
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report), flush=True)


def run_host():
    import bpy

    package = os.environ.get("B4ML_PACKAGE", str(ROOT))
    sys.path[:0] = [package, str(ROOT / "tests")]
    import b4artists_ml
    from b4artists_ml import secondary_motion as secondary
    from test_b4artists_ml_secondary_motion import fixture

    b4artists_ml.register()
    bpy.context.preferences.edit.use_global_undo = True
    obj, source, _, _, _, _ = fixture("rigify_default")
    scene = bpy.context.scene
    state = obj.b4ml

    mesh_data = bpy.data.meshes.new("B4ML Arbitrary Mesh Data")
    mesh_data.from_pydata(
        ((-1, -1, -1), (-1, 1, -1), (-1, 1, 1), (-1, -1, 1),
         (1, -1, -1), (1, -1, 1), (1, 1, 1), (1, 1, -1)), [],
        ((0, 1, 2, 3), (4, 5, 6, 7), (0, 4, 7, 1),
         (3, 2, 6, 5), (0, 3, 5, 4), (1, 7, 6, 2)))
    mesh_data.update()
    surface = bpy.data.objects.new("B4ML Arbitrary Mesh", mesh_data)
    scene.collection.objects.link(surface)
    if MOVING:
        surface.location = (2., 0., 0.)
        surface.keyframe_insert(data_path="location", frame=1)
        surface.location = (-2., 0., 0.)
        surface.keyframe_insert(data_path="location", frame=11)
    if DEFORMING:
        surface.shape_key_add(name="Basis")
        key = surface.shape_key_add(name="Crouch")
        for vertex in key.data:
            if vertex.co.z > 0.0:
                vertex.co.z *= 1.4
        key.value = 0.0
        key.keyframe_insert(data_path="value", frame=1)
        key.value = 1.0
        key.keyframe_insert(data_path="value", frame=11)
    bpy.context.view_layer.update()

    state.show_secondary = True
    state.secondary_space = "WORLD"
    state.secondary_rotation = True
    state.secondary_location = True
    state.secondary_collision = True
    state.secondary_collision_shape = "VOLUME" if VOLUME else "MESH"
    state.secondary_collision_mesh = surface
    state.secondary_collision_mesh_deforming = DEFORMING
    state.secondary_collision_mesh_moving = MOVING
    state.secondary_collision_volume_radius = 0.12
    state.secondary_collision_continuous = CONTINUOUS
    state.secondary_collision_clearance = 0.02
    state.secondary_restitution = 0.0
    state.secondary_surface_friction = 0.0

    journey = {
        "name": obj.name,
        "source": source.name,
        "input": state.candidate_action.name,
        "phase": "dismiss",
        "started": time.monotonic(),
        "events": [],
        "steps": [],
    }
    original_step = secondary.step

    def timed_step(value):
        began = time.perf_counter()
        before = value.b4ml.secondary_progress
        try:
            return original_step(value)
        finally:
            journey["steps"].append({
                "ms": (time.perf_counter() - began) * 1000.0,
                "before": before,
                "after": value.b4ml.secondary_progress,
            })

    secondary.step = timed_step

    def active_context():
        win = bpy.context.window_manager.windows[0]
        area = next(area for area in win.screen.areas if area.type == "VIEW_3D")
        region = next(region for region in area.regions if region.type == "WINDOW")
        area.spaces.active.show_region_ui = True
        for ui_region in area.regions:
            if ui_region.type == "UI" and hasattr(ui_region, "active_panel_category"):
                try:
                    ui_region.active_panel_category = "B4Artists ML"
                except (AttributeError, TypeError):
                    # Blender 5.2/Bforartists can expose this as read-only;
                    # the panel remains discoverable through its registered type.
                    pass
        value = bpy.data.objects[journey["name"]]
        win.view_layer.objects.active = value
        value.select_set(True)
        ui_region = next(region for region in area.regions if region.type == "UI")
        return win, area, region, value, ui_region

    def screenshot(name):
        path = ROOT / "training" / "b4artists_ml" / "cache" / f"{TAG}-{name}.png"
        bpy.ops.screen.screenshot(filepath=str(path))
        return str(path.relative_to(ROOT))

    @bpy.app.handlers.persistent
    def after_reload(_):
        if after_reload in bpy.app.handlers.load_post:
            bpy.app.handlers.load_post.remove(after_reload)
        journey["phase"] = "after_reload"
        bpy.app.timers.register(tick, first_interval=0.5)

    bpy.app.handlers.load_post.append(after_reload)

    def fail(_):
        write_report(dict(passed=False, phase=journey["phase"],
                          events=journey["events"], error=traceback.format_exc(),
                          package=package))
        bpy.ops.wm.quit_blender()
        return None

    def tick():
        try:
            if time.monotonic() - journey["started"] > 300:
                raise AssertionError("Mesh foreground lifecycle timed out")
            win, area, region, obj, ui_region = active_context()
            state = obj.b4ml
            (ROOT / "training" / "b4artists_ml" / "cache" / f"{TAG}-phase.txt").write_text(
                journey["phase"], encoding="utf-8")
            with bpy.context.temp_override(window=win, area=area, region=region):
                phase = journey["phase"]
                if phase == "dismiss":
                    win.event_simulate(type="ESC", value="PRESS")
                    win.event_simulate(type="LEFTMOUSE", value="PRESS",
                                       x=win.width // 2, y=int(win.height * 0.63))
                    win.event_simulate(type="LEFTMOUSE", value="RELEASE",
                                       x=win.width // 2, y=int(win.height * 0.63))
                    journey["phase"] = "controls"
                    return 0.4
                if phase == "controls":
                    bpy.ops.view3d.view_axis(type="FRONT")
                    bpy.ops.view3d.view_selected(use_all_regions=False)
                    for _ in range(26):
                        win.event_simulate(type="WHEELDOWNMOUSE", value="PRESS",
                                           x=ui_region.x + ui_region.width // 2,
                                           y=ui_region.y + ui_region.height // 2)
                    journey["phase"] = "controls_capture"
                    return 0.4
                if phase == "controls_capture":
                    journey["visible_controls_screenshot"] = screenshot("controls")
                    journey["events"].append(
                        "Foreground B4Artists ML panel exposed "
                        + ("closed-volume shape, triangle-mesh binding, " if VOLUME
                           else "mesh shape, triangle-mesh binding, ")
                        + ("continuous-time sweep, and Preview Secondary."
                           if CONTINUOUS else
                           "shape-key deformation, and Preview Secondary."
                           if DEFORMING else "and Preview Secondary."))
                    assert bpy.ops.ed.undo_push(message="Mesh UI input ready") == {"FINISHED"}
                    assert bpy.ops.b4ml.secondary_solve("INVOKE_DEFAULT") == {"RUNNING_MODAL"}
                    journey["phase"] = "escape"
                    return 0.1
                if phase == "escape":
                    if not journey["steps"]:
                        return 0.02
                    win.event_simulate(type="ESC", value="PRESS")
                    journey["phase"] = "cancelled"
                    return 0.1
                if phase == "cancelled":
                    if state.secondary_running:
                        return 0.02
                    assert state.candidate_action.name == journey["input"]
                    assert obj.animation_data.action.name == journey["input"]
                    journey["events"].append(
                        "Escape cancelled the mesh preview without replacing the input action.")
                    assert bpy.ops.ed.undo_push(message="Mesh UI retained input") == {"FINISHED"}
                    assert bpy.ops.b4ml.secondary_solve("INVOKE_DEFAULT") == {"RUNNING_MODAL"}
                    journey["phase"] = "completed"
                    return 0.1
                if phase == "completed":
                    if state.secondary_running:
                        return 0.02
                    output = state.candidate_action
                    assert output is not None and output is not state.secondary_input
                    assert state.secondary_metrics, (
                        "Secondary foreground solve failed: " + state.status)
                    metrics = json.loads(state.secondary_metrics)
                    expected_backend = ("implicit_selected_control_secondary_exact_swept_volume_v1"
                                        if EXACT_SWEPT_VOLUME else
                                        "implicit_selected_control_secondary_continuous_moving_deforming_swept_volume_v1"
                                        if BOUNDED_SWEPT_VOLUME and MOVING and DEFORMING else
                                        "implicit_selected_control_secondary_continuous_moving_swept_volume_v1"
                                        if BOUNDED_SWEPT_VOLUME and MOVING else
                                        "implicit_selected_control_secondary_continuous_deforming_swept_volume_v1"
                                        if BOUNDED_SWEPT_VOLUME and DEFORMING else
                                        "implicit_selected_control_secondary_continuous_moving_deforming_volume_v1"
                                        if CONTINUOUS and MOVING and DEFORMING and VOLUME else
                                        "implicit_selected_control_secondary_continuous_moving_deforming_mesh_v1"
                                        if CONTINUOUS and MOVING and DEFORMING else
                                        "implicit_selected_control_secondary_continuous_moving_volume_v1"
                                        if CONTINUOUS and MOVING and VOLUME else
                                        "implicit_selected_control_secondary_continuous_moving_mesh_v1"
                                        if CONTINUOUS and MOVING else
                                        "implicit_selected_control_secondary_continuous_deforming_volume_v1"
                                        if CONTINUOUS and DEFORMING and VOLUME else
                                        "implicit_selected_control_secondary_continuous_deforming_mesh_v1"
                                        if CONTINUOUS and DEFORMING else
                                        "implicit_selected_control_secondary_continuous_volume_v1"
                                        if CONTINUOUS and VOLUME else
                                        "implicit_selected_control_secondary_continuous_mesh_v1"
                                        if CONTINUOUS else
                                        "implicit_selected_control_secondary_volume_v1"
                                        if VOLUME else
                                        "implicit_selected_control_secondary_deforming_mesh_v1"
                                        if DEFORMING else
                                        "implicit_selected_control_secondary_mesh_v1")
                    assert metrics["backend"] == expected_backend
                    assert metrics["collision"] is True
                    assert metrics["collision_shape"] == ("VOLUME" if VOLUME else "MESH")
                    assert metrics["collision_mesh"] == surface.name_full
                    assert metrics["collision_mesh_triangles"] == 12
                    assert metrics["collision_mesh_closed"] is True
                    assert metrics["collision_mesh_deforming"] is DEFORMING
                    assert metrics["collision_mesh_moving"] is MOVING
                    assert metrics["collision_mesh_continuous"] is CONTINUOUS
                    assert metrics["collision_mesh_exact_swept_volume"] is EXACT_SWEPT_VOLUME
                    assert metrics["collision_mesh_bounded_swept_volume"] is BOUNDED_SWEPT_VOLUME
                    if CONTINUOUS:
                        assert metrics["schema"] == (21 if EXACT_SWEPT_VOLUME else
                                                      22 if BOUNDED_SWEPT_VOLUME else
                                                      20 if MOVING else 18 if DEFORMING else 17)
                        assert metrics["collision_target_space"] == (
                            "exact swept-sphere closed evaluated triangle volume"
                            if EXACT_SWEPT_VOLUME else
                            "bounded continuous-time closed moving deforming swept triangle volume"
                            if BOUNDED_SWEPT_VOLUME and MOVING and DEFORMING else
                            "bounded continuous-time closed moving swept triangle volume"
                            if BOUNDED_SWEPT_VOLUME and MOVING else
                            "bounded continuous-time closed deforming swept triangle volume"
                            if BOUNDED_SWEPT_VOLUME and DEFORMING else
                            "continuous-time closed moving deforming triangle volume"
                            if MOVING and DEFORMING and VOLUME else
                            "continuous-time closed moving deforming triangle mesh"
                            if MOVING and DEFORMING else
                            "continuous-time closed moving triangle volume"
                            if MOVING and VOLUME else
                            "continuous-time closed moving triangle mesh"
                            if MOVING else
                            "continuous-time closed deforming triangle volume"
                            if DEFORMING and VOLUME else
                            "continuous-time closed evaluated triangle volume"
                            if VOLUME else
                            "continuous-time closed deforming triangle mesh"
                            if DEFORMING else "continuous-time closed evaluated triangle mesh")
                    elif VOLUME:
                        assert metrics["schema"] == 16
                        assert abs(metrics["collision_mesh_volume_radius"] - .12) < 1e-8
                        assert metrics["collision_target_space"] == "closed evaluated triangle volume"
                    elif DEFORMING:
                        assert metrics["schema"] == 15
                        assert metrics["collision_mesh_sample_count"] >= 2
                        assert metrics["collision_target_space"] == "evaluated shape-key triangle mesh"
                    else:
                        assert metrics["schema"] == 14
                    assert metrics["editable_linear_keys"] is True
                    assert metrics["learned"] is False
                    journey["metrics"] = metrics
                    journey["output"] = output.name
                    journey["completion_screenshot"] = screenshot("completed")
                    journey["events"].append(
                        "Preview/generation completed with an editable "
                           + ("bounded continuous-time closed moving/deforming swept-volume result."
                           if BOUNDED_SWEPT_VOLUME and MOVING and DEFORMING else
                           "bounded continuous-time closed moving swept-volume result."
                           if BOUNDED_SWEPT_VOLUME and MOVING else
                           "bounded continuous-time closed deforming swept-volume result."
                           if BOUNDED_SWEPT_VOLUME and DEFORMING else
                           "continuous-time closed deforming-volume result."
                           if CONTINUOUS and DEFORMING and VOLUME else
                           "continuous-time closed deforming-mesh result."
                           if CONTINUOUS and DEFORMING else
                           "continuous-time closed-volume result."
                           if CONTINUOUS and VOLUME else
                           "continuous-time closed-mesh result."
                           if CONTINUOUS else
                           "finite closed-volume result."
                           if VOLUME else
                           "deforming shape-key mesh result."
                           if DEFORMING else "static arbitrary-mesh result."))
                    secondary.step = original_step
                    journey["phase"] = "undo"
                    return 0.1
                if phase == "undo":
                    win.event_simulate(type="Z", value="PRESS", ctrl=True)
                    journey["phase"] = "undo_check"
                    return 0.1
                if phase == "undo_check":
                    assert state.candidate_action.name == journey["input"]
                    journey["events"].append("Native Undo restored the mesh input action.")
                    journey["phase"] = "redo"
                    return 0.1
                if phase == "redo":
                    win.event_simulate(type="Z", value="PRESS", ctrl=True, shift=True)
                    journey["phase"] = "redo_check"
                    return 0.1
                if phase == "redo_check":
                    assert state.candidate_action.name == journey["output"]
                    journey["events"].append("Native Redo restored the generated mesh candidate.")
                    journey["native_undo_redo"] = {"status": "passed"}
                    journey["phase"] = "restore_input"
                    return 0.1
                if phase == "restore_input":
                    assert bpy.ops.b4ml.secondary(operation="RESET") == {"FINISHED"}
                    assert state.candidate_action.name == journey["input"]
                    journey["events"].append("Restore Input returned to the pre-mesh candidate.")
                    journey["phase"] = "regenerate_after_restore"
                    return 0.1
                if phase == "regenerate_after_restore":
                    assert bpy.ops.b4ml.secondary_solve() == {"FINISHED"}
                    assert bpy.ops.b4ml.action(operation="KEEP") == {"FINISHED"}
                    kept = state.kept_action
                    assert kept is not None and obj.animation_data.action == kept
                    journey["kept"] = kept.name
                    journey["events"].append("Keep archived the editable mesh result as a separate action.")
                    save_path = ROOT / "training" / "b4artists_ml" / "cache" / f"{TAG}.blend"
                    journey["save_path"] = str(save_path.relative_to(ROOT))
                    assert bpy.ops.wm.save_as_mainfile(filepath=str(save_path)) == {"FINISHED"}
                    bpy.ops.wm.open_mainfile(filepath=str(save_path))
                    return 0.1
                if phase == "after_reload":
                    obj = bpy.data.objects[journey["name"]]
                    state = obj.b4ml
                    assert state.kept_action is not None
                    assert obj.animation_data and obj.animation_data.action == state.kept_action
                    assert state.secondary_collision_shape == ("VOLUME" if VOLUME else "MESH")
                    assert state.secondary_collision_mesh is not None
                    journey["events"].append("Save/reload preserved the kept action and collision-mesh binding.")
                    assert bpy.ops.b4ml.action(operation="RESTORE_SOURCE") == {"FINISHED"}
                    assert obj.animation_data.action.name == journey["source"]
                    journey["events"].append("Restore Source returned the rig to its original action after reload.")
                    archive = Path(package)
                    write_report(dict(
                        schema=1,
                        feature=("exact swept-sphere closed finite-volume triangle-mesh collision"
                                 if EXACT_SWEPT_VOLUME else
                                 "bounded continuous-time closed moving/deforming swept finite-volume triangle-mesh collision"
                                 if BOUNDED_SWEPT_VOLUME and MOVING and DEFORMING else
                                 "bounded continuous-time closed moving swept finite-volume triangle-mesh collision"
                                 if BOUNDED_SWEPT_VOLUME and MOVING else
                                 "bounded continuous-time closed deforming swept finite-volume triangle-mesh collision"
                                 if BOUNDED_SWEPT_VOLUME and DEFORMING else
                                 "continuous-time closed finite-volume triangle-mesh collision"
                                 if CONTINUOUS and VOLUME else
                                 "continuous-time closed moving triangle-mesh collision"
                                 if CONTINUOUS and MOVING else
                                 "continuous-time closed triangle-mesh collision"
                                 if CONTINUOUS else
                                 "closed finite-volume triangle-mesh collision"
                                 if VOLUME else
                                 "deforming shape-key triangle-mesh collision"
                                 if DEFORMING else "static arbitrary triangle-mesh collision"),
                        package=str(archive),
                        package_sha256=hashlib.sha256(archive.read_bytes()).hexdigest()
                        if archive.is_file() else None,
                        host={"application": "Bforartists", "version": "5.1.0",
                              "blender_core": "5.2.0 Alpha", "build_hash": "dd23ab17120d"},
                        passed=True,
                        events=journey["events"],
                        metrics=journey["metrics"],
                        native_undo_redo=journey["native_undo_redo"],
                        visible_controls_screenshot=journey["visible_controls_screenshot"],
                        completion_screenshot=journey["completion_screenshot"],
                        save_path=journey["save_path"],
                        step_count=len(journey["steps"]),
                        step_max_ms=max(item["ms"] for item in journey["steps"]),
                        elapsed_seconds=time.monotonic() - journey["started"],
                        scope="Automated foreground control/lifecycle evidence; independent animator usability and motion-quality review remain unverified.",
                        learned_temporal_quality=False,
                        cascadeur_comparison=False,
                    ))
                    bpy.ops.wm.quit_blender()
                    return None
        except Exception:
            return fail(None)
        return 0.03

    bpy.app.timers.register(tick, first_interval=0.5)


if __name__ == "__main__":
    if "--host" in sys.argv:
        run_host()
    else:
        startup = subprocess.STARTUPINFO()
        startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startup.wShowWindow = 0
        began = time.perf_counter()
        log_path = ROOT / "training" / "b4artists_ml" / "cache" / f"{TAG}.log"
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", OPENBLAS_NUM_THREADS="4")
        with log_path.open("w", encoding="utf-8") as log:
            process = subprocess.run(
                ["X:/5.1.0/bforartists.exe", "--factory-startup", "--no-window-focus",
                 "--enable-event-simulate", "--python", str(HERE), "--", "--host"],
                stdout=log, stderr=subprocess.STDOUT, startupinfo=startup,
                env=env, timeout=360)
        print(json.dumps(dict(exit_code=process.returncode,
                              seconds=time.perf_counter() - began,
                              log=str(log_path.relative_to(ROOT)))), flush=True)
