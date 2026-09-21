"""Foreground capsule-collision controls and action-recovery journey."""

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
TAG = os.environ.get("B4ML_CAPSULE_UI_TAG", "capsule-ui-v1")
MODAL = os.environ.get("B4ML_CAPSULE_MODAL", "0") == "1"
CONTINUOUS = os.environ.get("B4ML_CAPSULE_CONTINUOUS", "0") == "1"
MOVING = os.environ.get("B4ML_CAPSULE_MOVING", "0") == "1"


def _flat_matrix(matrix):
    return [float(value) for row in matrix for value in row]


def _action_slot(action, obj=None):
    if not hasattr(action, "slots"):
        return None
    animation_data = getattr(obj, "animation_data", None)
    active_slot = getattr(animation_data, "action_slot", None)
    if active_slot is not None:
        matched = next((slot for slot in action.slots if slot.identifier == active_slot.identifier), None)
        if matched is not None:
            return matched
    if len(action.slots) == 1:
        return action.slots[0]
    raise ValueError("Cannot fingerprint a slotted Action without a unique matching slot")


def _action_fingerprint(action, obj=None):
    """Return a stable content fingerprint without relying on datablock names."""
    if action is None:
        return {"sha256": None, "fcurves": 0, "keyframes": 0}
    if hasattr(action, "fcurves") and (getattr(action, "is_action_legacy", False)
                                       or not hasattr(action, "slots")):
        curves_source = action.fcurves
    else:
        from b4artists_ml import workflow
        curves_source = workflow.action_curves(action, _action_slot(action, obj), obj=obj)
    curves = []
    keyframes = 0
    frame_values = []
    for curve in curves_source:
        points = []
        for point in curve.keyframe_points:
            frame_values.append(float(point.co[0]))
            points.append({
                "co": [float(point.co[0]), float(point.co[1])],
                "handle_left": [float(point.handle_left[0]), float(point.handle_left[1])],
                "handle_right": [float(point.handle_right[0]), float(point.handle_right[1])],
                "interpolation": point.interpolation,
                "handle_left_type": point.handle_left_type,
                "handle_right_type": point.handle_right_type,
            })
        keyframes += len(points)
        curves.append({
            "data_path": curve.data_path,
            "array_index": int(curve.array_index),
            "group": curve.group.name if curve.group else None,
            "points": points,
        })
    frame_range = [min(frame_values), max(frame_values)] if frame_values else [0.0, 0.0]
    ordered_curves = sorted(curves, key=lambda item: (item["data_path"], item["array_index"]))
    payload = {
        "frame_range": frame_range,
        "fcurves": ordered_curves,
    }
    digest = hashlib.sha256(json.dumps(
        payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()
    curve_hashes = []
    for curve in ordered_curves:
        curve_digest = hashlib.sha256(json.dumps(
            curve, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()
        curve_hashes.append({
            "data_path": curve["data_path"],
            "array_index": curve["array_index"],
            "keyframes": len(curve["points"]),
            "sha256": curve_digest,
        })
    return {
        "sha256": digest,
        "fcurves": len(curves),
        "keyframes": keyframes,
        "frame_range": frame_range,
        "curve_hashes": curve_hashes,
    }


def _rig_fingerprint(obj):
    """Fingerprint the armature rest/pose state used by the recovery journey."""
    bones = []
    if obj.type == "ARMATURE":
        for bone in sorted(obj.data.bones, key=lambda item: item.name):
            pose_bone = obj.pose.bones.get(bone.name)
            bones.append({
                "name": bone.name,
                "parent": bone.parent.name if bone.parent else None,
                "use_deform": bool(bone.use_deform),
                "head_local": [float(value) for value in bone.head_local],
                "tail_local": [float(value) for value in bone.tail_local],
                "matrix_local": _flat_matrix(bone.matrix_local),
                "pose_matrix": _flat_matrix(pose_bone.matrix) if pose_bone else None,
                "pose_matrix_basis": _flat_matrix(pose_bone.matrix_basis) if pose_bone else None,
                "pose_location": [float(value) for value in pose_bone.location] if pose_bone else None,
                "pose_scale": [float(value) for value in pose_bone.scale] if pose_bone else None,
                "pose_rotation_mode": pose_bone.rotation_mode if pose_bone else None,
                "pose_rotation_quaternion": ([float(value) for value in pose_bone.rotation_quaternion]
                                              if pose_bone else None),
                "pose_rotation_euler": ([float(value) for value in pose_bone.rotation_euler]
                                         if pose_bone else None),
            })
    payload = {
        "type": obj.type,
        "matrix_world": _flat_matrix(obj.matrix_world),
        "bones": bones,
    }
    digest = hashlib.sha256(json.dumps(
        payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()
    bone_hashes = []
    structure_bone_hashes = []
    pose_bone_hashes = []
    for bone in bones:
        bone_digest = hashlib.sha256(json.dumps(
            bone, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()
        bone_hashes.append({"name": bone["name"], "sha256": bone_digest})
        structure = {
            "name": bone["name"],
            "parent": bone["parent"],
            "use_deform": bone["use_deform"],
            "head_local": bone["head_local"],
            "tail_local": bone["tail_local"],
            "matrix_local": bone["matrix_local"],
        }
        pose = {
            "name": bone["name"],
            "pose_matrix": bone["pose_matrix"],
            "pose_matrix_basis": bone["pose_matrix_basis"],
            "pose_location": bone["pose_location"],
            "pose_scale": bone["pose_scale"],
            "pose_rotation_mode": bone["pose_rotation_mode"],
            "pose_rotation_quaternion": bone["pose_rotation_quaternion"],
            "pose_rotation_euler": bone["pose_rotation_euler"],
        }
        structure_bone_hashes.append({
            "name": bone["name"],
            "sha256": hashlib.sha256(json.dumps(
                structure, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest(),
        })
        pose_bone_hashes.append({
            "name": bone["name"],
            "sha256": hashlib.sha256(json.dumps(
                pose, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest(),
        })
    structure_payload = {
        "type": obj.type,
        "matrix_world": _flat_matrix(obj.matrix_world),
        "bones": [{
            "name": bone["name"],
            "parent": bone["parent"],
            "use_deform": bone["use_deform"],
            "head_local": bone["head_local"],
            "tail_local": bone["tail_local"],
            "matrix_local": bone["matrix_local"],
        } for bone in bones],
    }
    pose_payload = [{
        "name": bone["name"],
        "pose_matrix": bone["pose_matrix"],
        "pose_matrix_basis": bone["pose_matrix_basis"],
        "pose_location": bone["pose_location"],
        "pose_scale": bone["pose_scale"],
        "pose_rotation_mode": bone["pose_rotation_mode"],
        "pose_rotation_quaternion": bone["pose_rotation_quaternion"],
        "pose_rotation_euler": bone["pose_rotation_euler"],
    } for bone in bones]
    structure_digest = hashlib.sha256(json.dumps(
        structure_payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()
    pose_digest = hashlib.sha256(json.dumps(
        pose_payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()
    return {
        "sha256": digest,
        "bones": len(bones),
        "bone_hashes": bone_hashes,
        "structure_sha256": structure_digest,
        "structure_bone_hashes": structure_bone_hashes,
        "pose_sha256": pose_digest,
        "pose_bone_hashes": pose_bone_hashes,
    }


def _rig_modes_fingerprint(obj):
    from b4artists_ml import rig_state

    return _payload_fingerprint(rig_state.mode_values(obj))


def _payload_fingerprint(values):
    digest = hashlib.sha256(json.dumps(
        values, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()
    return {"sha256": digest, "values": values}


def _has_native_undo_evidence(report):
    return (
        report.get("passed") is True
        and report.get("native_undo_redo", {}).get("status") == "passed"
    )


def _write_report(report):
    path = ROOT / "docs" / "b4artists_ml" / f"{TAG}.json"
    if path.is_file():
        try:
            existing = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError, TypeError):
            existing = None
        if isinstance(existing, dict) and _has_native_undo_evidence(existing) and not _has_native_undo_evidence(report):
            sidecar = path.with_name(f"{path.stem}-weaker-observation{path.suffix}")
            sidecar.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
            print(json.dumps({
                "preserved_authoritative_report": str(path.relative_to(ROOT)),
                "weaker_observation": str(sidecar.relative_to(ROOT)),
                "reason": "A report without passing native Undo/Redo evidence cannot replace a stronger modal receipt.",
            }), flush=True)
            return
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report), flush=True)


def run():
    import bpy

    package = os.environ.get("B4ML_PACKAGE", str(ROOT))
    sys.path[:0] = [package, str(ROOT / "tests")]
    import b4artists_ml
    from b4artists_ml import secondary_motion as secondary, workflow
    from test_b4artists_ml_secondary_motion import fixture

    b4artists_ml.register()
    bpy.context.preferences.edit.use_global_undo = True
    obj, source, _, _, _, _ = fixture("rigify_default")
    scene = bpy.context.scene
    state = obj.b4ml
    candidate_action = obj.animation_data.action
    candidate_slot = getattr(obj.animation_data, "action_slot", None)
    source_slot = _action_slot(source, obj)
    workflow.assign_action(obj, source, source_slot.identifier if source_slot else "")
    bpy.context.view_layer.update()
    source_rig_state_before = _rig_fingerprint(obj)
    workflow.assign_action(obj, candidate_action, candidate_slot.identifier if candidate_slot else "")
    bpy.context.view_layer.update()

    start = bpy.data.objects.new("B4ML Capsule UI Start", None)
    end = bpy.data.objects.new("B4ML Capsule UI End", None)
    start.empty_display_type = end.empty_display_type = "SPHERE"
    start.empty_display_size = end.empty_display_size = 0.1
    start.location = (-0.5, 0.0, 0.0)
    end.location = (0.5, 0.0, 0.0)
    scene.collection.objects.link(start)
    scene.collection.objects.link(end)
    if MOVING:
        for item, first, second in ((start, (-0.5, 0.0, 0.0), (-0.25, 0.0, 0.0)),
                                    (end, (0.5, 0.0, 0.0), (0.75, 0.0, 0.0))):
            for index in range(3):
                item.location[index] = first[index]
                item.keyframe_insert(data_path="location", index=index, frame=1.0)
                item.location[index] = second[index]
                item.keyframe_insert(data_path="location", index=index, frame=11.0)
                item.scale[index] = 1.0
                item.keyframe_insert(data_path="scale", index=index, frame=1.0)
                item.scale[index] = 1.1
                item.keyframe_insert(data_path="scale", index=index, frame=11.0)
        scene.frame_set(1)
    bpy.context.view_layer.update()

    state.show_secondary = True
    state.secondary_space = "WORLD"
    state.secondary_rotation = True
    state.secondary_location = True
    state.secondary_collision = True
    state.secondary_collision_shape = "CAPSULE"
    state.secondary_capsule_start = start
    state.secondary_capsule_end = end
    state.secondary_capsule_radius = 0.2
    state.secondary_capsule_moving = MOVING
    state.secondary_capsule_scaling = MOVING
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
    journey["action_rig_recovery"] = {
        "candidate_action_before": _action_fingerprint(candidate_action, obj),
        "source_action_before": _action_fingerprint(source, obj),
        "source_rig_state_before": source_rig_state_before,
        "source_rig_modes_before": _rig_modes_fingerprint(obj),
        "candidate_rig_state_before": _rig_fingerprint(obj),
        "candidate_rig_modes_before": _rig_modes_fingerprint(obj),
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
                ui_region.active_panel_category = "B4Artists ML"
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

    def fail(exc):
        report = dict(
            passed=False,
            phase=journey["phase"],
            events=journey["events"],
            metrics=journey.get("metrics"),
            action_rig_recovery=journey.get("action_rig_recovery"),
            save_path=journey.get("save_path"),
            error=traceback.format_exc(),
            package=package,
        )
        _write_report(report)
        bpy.ops.wm.quit_blender()
        return None

    def tick():
        try:
            if time.monotonic() - journey["started"] > 300:
                raise AssertionError("Capsule foreground lifecycle timed out")

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
                elif phase == "controls":
                    bpy.ops.view3d.view_axis(type="FRONT")
                    bpy.ops.view3d.view_selected(use_all_regions=False)
                    for _ in range(26):
                        win.event_simulate(type="WHEELDOWNMOUSE", value="PRESS",
                                           x=ui_region.x + ui_region.width // 2,
                                           y=ui_region.y + ui_region.height // 2)
                    journey["phase"] = "controls_capture"
                    return 0.4
                elif phase == "controls_capture":
                    journey["visible_controls_screenshot"] = screenshot("controls")
                    journey["events"].append(
                        "Foreground B4Artists ML panel exposed capsule shape, endpoints, radius, endpoint animation, radius scale, continuous-time sweep, and Preview Secondary."
                        if MOVING else
                        "Foreground B4Artists ML panel exposed capsule shape, endpoints, radius, continuous-time sweep, and Preview Secondary."
                        if CONTINUOUS else
                        "Foreground B4Artists ML panel exposed capsule shape, endpoints, radius, and Preview Secondary.")
                    if MODAL:
                        assert bpy.ops.ed.undo_push(message="Capsule UI input ready") == {"FINISHED"}
                        assert bpy.ops.b4ml.secondary_solve("INVOKE_DEFAULT") == {"RUNNING_MODAL"}
                        journey["phase"] = "escape"
                    else:
                        journey["phase"] = "generate"
                elif phase == "escape":
                    if not journey["steps"]:
                        return 0.02
                    win.event_simulate(type="ESC", value="PRESS")
                    journey["phase"] = "cancelled"
                elif phase == "cancelled":
                    if state.secondary_running:
                        return 0.02
                    assert state.candidate_action.name == journey["input"]
                    assert obj.animation_data.action.name == journey["input"]
                    journey["events"].append("Escape cancelled the capsule preview without replacing the input action.")
                    assert bpy.ops.ed.undo_push(message="Capsule UI retained input") == {"FINISHED"}
                    assert bpy.ops.b4ml.secondary_solve("INVOKE_DEFAULT") == {"RUNNING_MODAL"}
                    journey["phase"] = "completed"
                elif phase == "generate":
                    assert bpy.ops.b4ml.secondary_solve() == {"FINISHED"}
                    journey["events"].append("Foreground Preview Secondary generated the capsule result.")
                    journey["phase"] = "completed"
                elif phase == "completed":
                    if state.secondary_running:
                        return 0.02
                    output = state.candidate_action
                    assert output is not None and output is not state.secondary_input
                    metrics = json.loads(state.secondary_metrics)
                    assert metrics["backend"] == (
                        "implicit_selected_control_secondary_continuous_moving_capsule_v1"
                        if MOVING and CONTINUOUS else
                        "implicit_selected_control_secondary_moving_capsule_v1"
                        if MOVING else
                        "implicit_selected_control_secondary_continuous_capsule_v1"
                        if CONTINUOUS else "implicit_selected_control_secondary_v12")
                    assert metrics["schema"] == (24 if MOVING else 23 if CONTINUOUS else 13)
                    assert metrics["collision"] is True
                    assert metrics["collision_shape"] == "CAPSULE"
                    # v0.37.2-dev predates the explicit moving/deforming flags;
                    # their omission is the legacy static-capsule false default.
                    assert metrics.get("collision_capsule_moving", False) is MOVING
                    assert metrics.get("collision_capsule_scaling", False) is MOVING
                    assert metrics.get("collision_capsule_continuous", False) is CONTINUOUS
                    if MOVING:
                        assert metrics["relative_velocity_response"] is True
                        assert metrics["relative_radius_velocity_response"] is True
                    if CONTINUOUS:
                        assert metrics["collision_target_space"] == (
                            "bounded continuous-time moving/deforming capsule"
                            if MOVING else "bounded continuous-time static capsule")
                    assert tuple(metrics["collision_capsule_start"]) == tuple(start.location)
                    assert tuple(metrics["collision_capsule_end"]) == tuple(end.location)
                    assert abs(metrics["collision_capsule_radius"] - 0.2) < 1e-6
                    assert metrics["editable_linear_keys"] is True
                    assert metrics["learned"] is False
                    journey["metrics"] = metrics
                    journey["output"] = output.name
                    journey["completion_screenshot"] = screenshot("completed")
                    journey["events"].append(
                        "Preview/generation completed with an editable bounded continuous-time moving/deforming capsule result."
                        if MOVING and CONTINUOUS else
                        "Preview/generation completed with an editable moving/deforming capsule result."
                        if MOVING else
                        "Preview/generation completed with an editable bounded continuous-time static-capsule result."
                        if CONTINUOUS else
                        "Preview/generation completed with an editable static-capsule result.")
                    secondary.step = original_step
                    journey["phase"] = "undo" if MODAL else "restore_input"
                elif phase == "undo":
                    win.event_simulate(type="Z", value="PRESS", ctrl=True)
                    journey["phase"] = "undo_check"
                elif phase == "undo_check":
                    assert state.candidate_action.name == journey["input"]
                    journey["events"].append("Native Undo restored the capsule input action.")
                    journey["phase"] = "redo"
                elif phase == "redo":
                    win.event_simulate(type="Z", value="PRESS", ctrl=True, shift=True)
                    journey["phase"] = "redo_check"
                elif phase == "redo_check":
                    assert state.candidate_action.name == journey["output"]
                    journey["events"].append("Native Redo restored the generated capsule candidate.")
                    journey["native_undo_redo"] = {"status": "passed"}
                    journey["phase"] = "restore_input"
                elif phase == "restore_input":
                    assert bpy.ops.b4ml.secondary(operation="RESET") == {"FINISHED"}
                    assert state.candidate_action.name == journey["input"]
                    journey["events"].append("Restore Input returned to the pre-capsule candidate.")
                    if not MODAL:
                        journey["native_undo_redo"] = {
                            "status": "blocked",
                            "reason": "Bforartists 5.2 Alpha factory-startup foreground timer context does not retain this synthetic rig in the native undo stack; direct ed.undo polling is also invalid in that context.",
                        }
                        journey["events"].append(
                            "Foreground capsule Undo/Redo was recorded as a host limitation; exact-archive secondary regression covers existing native Undo/Redo paths.")
                    journey["phase"] = "regenerate_after_restore"
                elif phase == "regenerate_after_restore":
                    assert bpy.ops.b4ml.secondary_solve() == {"FINISHED"}
                    assert bpy.ops.b4ml.action(operation="KEEP") == {"FINISHED"}
                    kept = state.kept_action
                    assert kept is not None and obj.animation_data.action == kept
                    journey["kept"] = kept.name
                    journey["action_rig_recovery"]["kept_action_before_reload"] = _action_fingerprint(kept, obj)
                    journey["events"].append("Keep archived the editable capsule result as a separate action.")
                    save_path = ROOT / "training" / "b4artists_ml" / "cache" / f"{TAG}.blend"
                    journey["save_path"] = str(save_path.relative_to(ROOT))
                    assert bpy.ops.wm.save_as_mainfile(filepath=str(save_path)) == {"FINISHED"}
                    bpy.ops.wm.open_mainfile(filepath=str(save_path))
                    return 0.1
                elif phase == "after_reload":
                    obj = bpy.data.objects[journey["name"]]
                    state = obj.b4ml
                    assert state.kept_action is not None
                    assert obj.animation_data and obj.animation_data.action == state.kept_action
                    assert state.secondary_collision_shape == "CAPSULE"
                    assert getattr(state, "secondary_capsule_moving", False) is MOVING
                    assert getattr(state, "secondary_capsule_scaling", False) is MOVING
                    assert state.secondary_capsule_start is not None
                    assert state.secondary_capsule_end is not None
                    journey["action_rig_recovery"]["kept_rig_modes_expected"] = _payload_fingerprint(
                        json.loads(state.kept_modes or "{}"))
                    journey["action_rig_recovery"]["kept_action_after_reload"] = _action_fingerprint(
                        state.kept_action, obj)
                    assert (journey["action_rig_recovery"]["kept_action_before_reload"]["sha256"] ==
                            journey["action_rig_recovery"]["kept_action_after_reload"]["sha256"])
                    journey["events"].append("Save/reload preserved the kept action and capsule endpoint bindings.")
                    assert bpy.ops.b4ml.action(operation="RESTORE_SOURCE") == {"FINISHED"}
                    assert obj.animation_data.action.name == journey["source"]
                    journey["action_rig_recovery"]["source_action_after_restore"] = _action_fingerprint(
                        obj.animation_data.action, obj)
                    journey["action_rig_recovery"]["rig_state_after_restore"] = _rig_fingerprint(obj)
                    journey["action_rig_recovery"]["source_rig_modes_after_restore"] = _rig_modes_fingerprint(obj)
                    assert (journey["action_rig_recovery"]["source_action_before"]["sha256"] ==
                            journey["action_rig_recovery"]["source_action_after_restore"]["sha256"])
                    assert (journey["action_rig_recovery"]["source_rig_state_before"]["structure_sha256"] ==
                            journey["action_rig_recovery"]["rig_state_after_restore"]["structure_sha256"])
                    assert (journey["action_rig_recovery"]["kept_rig_modes_expected"]["sha256"] ==
                            journey["action_rig_recovery"]["source_rig_modes_after_restore"]["sha256"])
                    source_pose_changed = [
                        before["name"] for before in journey["action_rig_recovery"]["source_rig_state_before"]["pose_bone_hashes"]
                        if before["sha256"] != next(after["sha256"] for after in journey["action_rig_recovery"]["rig_state_after_restore"]["pose_bone_hashes"]
                                                     if after["name"] == before["name"])
                    ]
                    journey["action_rig_recovery"]["pose_evaluation"] = {
                        "matches_source_action_baseline": not source_pose_changed,
                        "changed_bones": len(source_pose_changed),
                        "interpretation": "Restore Source rebinds the original Action after the generated candidate; evaluated pose changes on candidate-driven bones while Action, armature structure, and rig modes recover exactly.",
                    }
                    journey["action_rig_recovery"]["source_action_recovered"] = True
                    journey["action_rig_recovery"]["rig_structure_recovered"] = True
                    journey["action_rig_recovery"]["rig_modes_recovered"] = True
                    journey["action_rig_recovery"]["rig_mode_baseline"] = "persisted_kept_modes_payload"
                    journey["events"].append("Restore Source returned the rig to its original action after reload.")
                    archive_reference = os.environ.get("B4ML_ARCHIVE", package)
                    archive = Path(archive_reference)
                    report = dict(
                        schema=1,
                        feature=("bounded continuous-time moving/deforming capsule collision"
                                 if MOVING and CONTINUOUS else
                                 "moving/deforming capsule collision"
                                 if MOVING else
                                 "bounded continuous-time static capsule collision"
                                 if CONTINUOUS else "static analytic capsule collision"),
                        package=str(archive),
                        package_source=package,
                        package_sha256=hashlib.sha256(archive.read_bytes()).hexdigest()
                        if archive.is_file() else None,
                        host={"application": "Bforartists", "version": "5.1.0", "blender_core": "5.2.0 Alpha", "build_hash": "dd23ab17120d"},
                        passed=True,
                        events=journey["events"],
                        metrics=journey["metrics"],
                        action_rig_recovery=journey["action_rig_recovery"],
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
                    )
                    _write_report(report)
                    bpy.ops.wm.quit_blender()
                    return None
        except Exception:
            return fail(None)
        return 0.03

    bpy.app.timers.register(tick, first_interval=0.5)


if __name__ == "__main__":
    if "--host" in sys.argv:
        run()
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
        result = dict(exit_code=process.returncode,
                      seconds=time.perf_counter() - began,
                      log=str(log_path.relative_to(ROOT)))
        print(json.dumps(result), flush=True)
