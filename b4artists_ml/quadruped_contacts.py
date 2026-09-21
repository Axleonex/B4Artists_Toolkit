"""Reversible four-paw contact correction for generated Rigify quadrupeds.

The correction edits copied candidate-action curves for the existing native IK
controls. It does not infer contacts, gait, balance, or learned motion.

SPDX-License-Identifier: GPL-2.0-or-later
"""
import json
import math
import time

import bpy
from mathutils import Quaternion, Vector

from . import contact_math as cm
from . import quadruped_pose as qp
from . import rig_state as rs
from . import workflow as w


LIMBS = ("fore-L", "fore-R", "hind-L", "hind-R")
_JOBS = {}


def _frame(scene, frame=None):
    if frame is None:
        return scene.frame_current + scene.frame_subframe
    scene.frame_set(math.floor(frame), subframe=frame - math.floor(frame))


def rows(obj):
    return [dict(limb=item.limb, start=item.start, end=item.end,
                 blend=item.blend,
                 blend_in=item.blend_in if item.asymmetric_blend else item.blend,
                 blend_out=item.blend_out if item.asymmetric_blend else item.blend,
                 strength=item.strength,
                 point=list(item.point), rotation=list(item.rotation),
                 offset=list(item.offset), lock_rotation=item.lock_rotation)
            for item in obj.b4ml.contacts
            if item.enabled and item.review_state == "ACCEPTED" and item.limb in LIMBS]


def _signature(obj):
    return [dict(name=item.name, enabled=item.enabled,
                 review_state=item.review_state, limb=item.limb,
                 start=item.start, end=item.end, blend=item.blend,
                 asymmetric_blend=item.asymmetric_blend,
                 blend_in=item.blend_in, blend_out=item.blend_out,
                 strength=item.strength, point=list(item.point),
                 rotation=list(item.rotation), offset=list(item.offset),
                 lock_rotation=item.lock_rotation)
            for item in obj.b4ml.contacts if item.limb in LIMBS]


def _mapping(obj):
    profile, body, limbs = qp.binding(obj)
    qp._require_ik(obj, limbs)
    return profile, body, {row["id"]: row for row in limbs}


def _joint_matrix(obj, row):
    return w.display_world(obj) @ obj.pose.bones[row["joint"]].matrix


def _point(obj, row, offset):
    return _joint_matrix(obj, row) @ Vector(offset)


def _control_rotation(obj, row):
    return (w.display_world(obj) @ obj.pose.bones[row["ik"]].matrix).to_quaternion().normalized()


def _angle(a, b):
    return 2 * math.acos(min(1.0, abs(a.normalized().dot(b.normalized()))))


def _reference(obj, body, row):
    body_point = w.display_world(obj) @ obj.pose.bones[body].matrix.translation
    return max((body_point - _point(obj, row, (0.0, 0.0, 0.0))).length, 1e-8)


def _check_controls(obj, mapping, request):
    driven = {curve.data_path for curve in obj.animation_data.drivers} if obj.animation_data else set()
    rotation_controls = {mapping[row["limb"]]["ik"] for row in request if row["lock_rotation"]}
    for limb in {row["limb"] for row in request}:
        name = mapping[limb]["ik"]
        bone = obj.pose.bones[name]
        if set(w._channels(bone)["location"]) != {0, 1, 2}:
            raise ValueError("Four-paw contacts require unlocked XYZ location: " + name)
        if any(not constraint.mute and constraint.influence for constraint in bone.constraints):
            raise ValueError("Four-paw contacts cannot move a constrained IK control: " + name)
        if bone.path_from_id("location") in driven:
            raise ValueError("Four-paw contacts cannot move a driven IK control: " + name)
        if name in rotation_controls:
            if (any(bone.lock_rotation)
                    or (bone.rotation_mode in {'QUATERNION','AXIS_ANGLE'}
                        and bone.lock_rotations_4d and bone.lock_rotation_w)
                    or not w._channels(bone)["rotation"]):
                raise ValueError("Four-paw contacts require unlocked rotation: " + name)
            paths = {bone.path_from_id(prop) for prop in
                     ("rotation_euler", "rotation_quaternion", "rotation_axis_angle")}
            if paths & driven:
                raise ValueError("Four-paw contacts cannot rotate a driven IK control: " + name)


def capture(obj, scene):
    w.require_rig(obj)
    state = obj.b4ml
    if (state.contact_running or state.contact_suggest_running or state.flight_running
            or state.secondary_running or state.cleanup_running or state.body_payload or state.posing_payload
            or state.quadruped_payload):
        raise ValueError("Finish the active solve or posing preview first")
    if len(state.contacts) >= 32:
        raise ValueError("Limit a candidate to 32 contacts")
    _, _, mapping = _mapping(obj)
    limb = state.quadruped_contact_limb
    if limb not in mapping:
        raise ValueError("Choose a generated quadruped paw")
    row = mapping[limb]
    matrix = _joint_matrix(obj, row)
    joint = obj.pose.bones[row["joint"]]
    offset = matrix.inverted() @ (w.display_world(obj) @ joint.tail)
    offset += Vector(state.contact_offset)
    point = matrix @ offset
    rotation = _control_rotation(obj, row)
    if not all(math.isfinite(value) for value in (*point, *rotation, *offset)):
        raise ValueError("Paw contact transform must be finite")
    item = state.contacts.add()
    item.name = f"{limb} paw contact {len(state.contacts)}"
    item.limb = limb
    item.start = _frame(scene)
    item.end = item.start
    item.point = point
    item.rotation = rotation
    item.offset = offset
    item.review_state = "ACCEPTED"
    item.confidence = 1.0
    item.provenance = "MANUAL_QUADRUPED"
    item.reason = "Captured by the animator from the generated Rigify paw"
    state.contact_index = len(state.contacts) - 1
    state.status = "Paw contact captured; set its interval, blend and orientation lock"
    return item


def _action_signature(obj, action):
    slot = getattr(obj.animation_data, "action_slot", None)
    def primitive(value):
        if isinstance(value, (str, bool, int, float)):
            return value
        try:
            return tuple(value)
        except TypeError:
            return None
    def modifier_signature(modifier):
        values = []
        for prop in modifier.bl_rna.properties:
            if prop.identifier == 'rna_type' or prop.is_readonly:
                continue
            value = primitive(getattr(modifier, prop.identifier, None))
            if value is not None:
                values.append((prop.identifier, value))
        envelope=tuple((float(point.frame),float(point.min),float(point.max))
                       for point in getattr(modifier,'control_points',()))
        return tuple(values),envelope
    return [(curve.data_path, curve.array_index, curve.lock, curve.mute,
             curve.extrapolation,
             tuple(modifier_signature(modifier) for modifier in curve.modifiers),
             [(tuple(key.co), tuple(key.handle_left), tuple(key.handle_right),
               key.interpolation, key.handle_left_type, key.handle_right_type,
               key.easing, key.amplitude, key.back, key.period)
              for key in curve.keyframe_points],
             [tuple(point.co) for point in curve.sampled_points])
            for curve in w.action_curves(action, slot)]


def _rotation_values(bone):
    if bone.rotation_mode == "QUATERNION":
        return "rotation_quaternion", tuple(bone.rotation_quaternion)
    if bone.rotation_mode == "AXIS_ANGLE":
        return "rotation_axis_angle", tuple(bone.rotation_axis_angle)
    return "rotation_euler", tuple(bone.rotation_euler)


def _apply(obj, row, request, amount):
    current_point = _point(obj, row, request["offset"])
    target = current_point.lerp(Vector(request["point"]), amount)
    current_rotation = _control_rotation(obj, row)
    desired = (current_rotation.slerp(Quaternion(request["rotation"]), amount)
               if request["lock_rotation"] else current_rotation)
    if request["lock_rotation"]:
        qp._write_world_rotation(obj, row["ik"], desired)
    passes = 0
    for passes in range(1, 9):
        error = target - _point(obj, row, request["offset"])
        if error.length <= 1e-9:
            break
        qp._translate_control(obj, row["ik"], error)
    return target, desired, passes


def _owned_intervals(request, mapping, first, last):
    result = {}
    for row in request:
        name = mapping[row["limb"]]["ik"]
        result.setdefault(name, []).append((max(first, row["start"] - row["blend_in"]),
                                            min(last, row["end"] + row["blend_out"]),
                                            bool(row["lock_rotation"])))
    return result


def correction_steps(obj, scene):
    state = obj.b4ml
    w.require_rig(obj)
    w._reject_nla(obj)
    if state.flight_running or state.secondary_running or state.cleanup_running or state.contact_suggest_running:
        raise ValueError("Finish the active animation process first")
    if state.body_payload or state.posing_payload or state.quadruped_payload:
        raise ValueError("Finish the active posing preview first")
    previous = state.candidate_action
    if previous is None or not obj.animation_data or obj.animation_data.action != previous:
        raise ValueError("Generate and select a quadruped Pose Blending candidate first")
    if state.contact_output == previous and not state.contact_input:
        raise ValueError("Retained four-paw contact input is missing; generate a new candidate")
    original = state.contact_input if state.contact_output == previous and state.contact_input else previous
    profile, body, mapping = _mapping(obj)
    raw_request = rows(obj)
    if any(row["limb"] not in mapping for row in raw_request):
        raise ValueError("Four-paw contacts contain a limb outside this quadruped rig")
    # Give animators the control-specific failure before the broader anchor
    # compatibility check reports that the stored control schema changed.
    _check_controls(obj, mapping, raw_request)
    anchors = w.read_anchors(obj)
    first, last = anchors[0][0], anchors[-1][0]
    request = cm.validate(raw_request, first, last)
    selected = {row["limb"] for row in request}
    controls = {mapping[limb]["ik"] for limb in selected}
    if not controls.issubset(anchors[0][1]["pose"]):
        raise ValueError("Capture every contacted paw IK control in each priority pose")
    frames = cm.sample_frames(request, [frame for frame, _ in anchors], first, last)
    if len(frames) * len(controls) * 7 > w.MAX_KEYS:
        raise ValueError("Four-paw correction exceeds the editable key budget")
    intervals = _owned_intervals(request, mapping, first, last)
    priority = {frame for frame, _ in anchors}
    original_frame = _frame(scene)
    original_pose = w.raw_pose(obj)
    original_modes = rs.mode_values(obj)
    quadruped_modes = qp.mode_values(obj)
    rest = w._rest_signature(obj)
    world = [list(row) for row in obj.matrix_world]
    request_signature = _signature(obj)
    slot = w._slot(obj.animation_data)
    w.assign_action(obj, original, slot)
    try:
        input_signature = _action_signature(obj, original)
    finally:
        w.assign_action(obj, previous, slot)
    previous_signature = _action_signature(obj, previous)
    samples = {}
    candidate = None
    committed = False
    at_checkpoint = False
    checkpoint_pose = None
    maximum_before = 0.0
    drift_before = 0.0
    max_passes = 0
    started = time.perf_counter()

    def restore_previous():
        w.assign_action(obj, previous, slot)
        _frame(scene, original_frame)
        w.restore_pose(obj, original_pose)
        rs.restore_values(obj, original_modes)
        bpy.context.view_layer.update()

    def guard():
        allowed = {previous, original}
        if candidate is not None:
            allowed.add(candidate)
        if state.candidate_action != previous or not obj.animation_data or obj.animation_data.action not in allowed:
            raise ValueError("Candidate changed during four-paw contact correction")
        if _action_signature(obj, previous) != previous_signature:
            raise ValueError("Active candidate changed during four-paw contact correction")
        if _signature(obj) != request_signature or w._rest_signature(obj) != rest:
            raise ValueError("Contacts or rig changed during four-paw contact correction")
        if [list(row) for row in obj.matrix_world] != world:
            raise ValueError("Rig object transform changed during four-paw contact correction")
        if qp.mode_values(obj) != quadruped_modes:
            raise ValueError("Quadruped IK modes changed during contact correction")
        if abs(_frame(scene) - original_frame) > 1e-5:
            raise ValueError("Playhead changed during four-paw contact correction")
        if at_checkpoint and checkpoint_pose is not None and w.raw_pose(obj) != checkpoint_pose:
            raise ValueError("Pose controls changed during four-paw contact correction")

    try:
        for frame in frames:
            guard()
            w.assign_action(obj, original, slot)
            _frame(scene, frame)
            bpy.context.view_layer.update()
            _, current_body, current_mapping = _mapping(obj)
            for contact in request:
                amount = cm.weight(contact, frame)
                if amount <= 0.0:
                    continue
                row = current_mapping[contact["limb"]]
                reference = _reference(obj, current_body, row)
                point_error = (_point(obj, row, contact["offset"]) - Vector(contact["point"])).length / reference
                rotation_error = (_angle(_control_rotation(obj, row), Quaternion(contact["rotation"]))
                                  if contact["lock_rotation"] else 0.0)
                maximum_before = max(maximum_before, point_error * amount)
                if contact["start"] <= frame <= contact["end"]:
                    drift_before = max(drift_before, point_error)
                if frame in priority:
                    if point_error * amount > 2e-4 or rotation_error * amount > 1e-3:
                        raise ValueError(f"Paw contact conflicts with priority pose at frame {frame:g}: " + contact["limb"])
                else:
                    _, _, passes = _apply(obj, row, contact, amount)
                    max_passes = max(max_passes, passes)
            for limb in selected:
                name = current_mapping[limb]["ik"]
                if not any(start <= frame <= end for start, end, _ in intervals[name]):
                    continue
                bone = obj.pose.bones[name]
                for index, value in enumerate(bone.location):
                    samples.setdefault((bone.path_from_id("location"), index), []).append((frame, float(value)))
                if any(start <= frame <= end and rotate for start, end, rotate in intervals[name]):
                    prop, values = _rotation_values(bone)
                    for index, value in enumerate(values):
                        samples.setdefault((bone.path_from_id(prop), index), []).append((frame, float(value)))
            restore_previous()
            checkpoint_pose = w.raw_pose(obj)
            at_checkpoint = True
            yield dict(phase="Fitting four-paw contacts", frame=frame, total=len(frames))
            guard()
            at_checkpoint = False

        guard()
        w.assign_action(obj, original, slot)
        if _action_signature(obj, original) != input_signature:
            raise ValueError("Input candidate changed during four-paw contact correction")
        candidate = original.copy()
        candidate.name = original.name + " Four-Paw Contacts"
        candidate.use_fake_user = False
        w.assign_action(obj, candidate, slot)
        curves = w.action_curves(candidate, getattr(obj.animation_data, "action_slot", None),
                                 ensure=True, obj=obj)
        path_intervals = {}
        for limb in selected:
            name = mapping[limb]["ik"]
            bone = obj.pose.bones[name]
            owned = [(start, end) for start, end, _ in intervals[name]]
            rotation_owned = [(start, end) for start, end, rotate in intervals[name] if rotate]
            path_intervals[bone.path_from_id("location")] = owned
            for prop in ("rotation_quaternion", "rotation_axis_angle", "rotation_euler"):
                path_intervals[bone.path_from_id(prop)] = rotation_owned
        for (path, index), points in samples.items():
            curve = curves.find(path, index=index) or curves.new(path, index=index)
            if curve.lock or curve.mute or len(curve.modifiers):
                raise ValueError("Four-paw control curves contain locks, muting or modifiers")
            boundaries = {value for interval in path_intervals[path] for value in interval}
            preserved = {float(key.co.x) for key in curve.keyframe_points
                         if any(abs(float(key.co.x)-boundary) <= 1e-8
                                for boundary in boundaries)}
            if len(preserved) != len(boundaries):
                raise ValueError('Four-paw correction requires existing keys at contact interval boundaries')
            boundary_interpolation = {}
            boundary_handles = {}
            ordered_keys = sorted(curve.keyframe_points, key=lambda key: float(key.co.x))
            for boundary in boundaries:
                left = [key for key in ordered_keys if float(key.co.x) <= boundary]
                boundary_interpolation[boundary] = (left[-1].interpolation if left else 'BEZIER')
                existing=next((key for key in ordered_keys
                               if abs(float(key.co.x)-boundary)<=1e-8),None)
                if existing is not None:
                    is_start=any(abs(boundary-start)<=1e-8
                                 for start,_ in path_intervals[path])
                    boundary_handles[boundary]=(
                        existing.handle_left_type if is_start else existing.handle_right_type,
                        tuple(existing.handle_left if is_start else existing.handle_right),is_start,
                        existing.interpolation)
            for key_index in range(len(curve.keyframe_points) - 1, -1, -1):
                frame = curve.keyframe_points[key_index].co.x
                if (any(start <= frame <= end for start, end in path_intervals[path])
                        and not any(abs(frame-boundary) <= 1e-8 for boundary in boundaries)):
                    curve.keyframe_points.remove(curve.keyframe_points[key_index], fast=True)
            points = [(frame, value) for frame, value in points
                      if not any(abs(frame-boundary) <= 1e-8 for boundary in preserved)]
            start_index = len(curve.keyframe_points)
            curve.keyframe_points.add(len(points))
            for key_index, (frame, value) in enumerate(points, start_index):
                key = curve.keyframe_points[key_index]
                key.co = (frame, value)
                key.interpolation = "LINEAR"
                for start, end in path_intervals[path]:
                    if abs(frame-end) <= 1e-8:
                        key.interpolation = boundary_interpolation[end]
                        break
            curve.keyframe_points.sort()
            curve.keyframe_points.handles_recalc()
            for boundary,(handle_type,handle,is_start,interpolation) in boundary_handles.items():
                existing=next((key for key in curve.keyframe_points
                               if abs(float(key.co.x)-boundary)<=1e-8),None)
                if existing is None:
                    raise ValueError('Four-paw correction lost a contact boundary key')
                if is_start:
                    existing.interpolation='LINEAR'
                    existing.handle_left_type=handle_type;existing.handle_left=handle
                else:
                    existing.handle_right_type=handle_type;existing.handle_right=handle
                    existing.interpolation=interpolation

        validation_frames = sorted(set(frames) | {(a + b) * 0.5 for a, b in zip(frames, frames[1:])})
        maximum_after = 0.0
        drift_after = 0.0
        orientation_after = 0.0
        checks = 0
        for frame in validation_frames:
            guard()
            w.assign_action(obj, original, slot)
            _frame(scene, frame)
            bpy.context.view_layer.update()
            _, source_body, source_mapping = _mapping(obj)
            expected = []
            source_priority = w.raw_pose(obj, profile.controls) if frame in priority else None
            for contact in request:
                amount = cm.weight(contact, frame)
                if amount <= 0.0:
                    continue
                row = source_mapping[contact["limb"]]
                source_point = _point(obj, row, contact["offset"])
                source_rotation = _control_rotation(obj, row)
                target = source_point.lerp(Vector(contact["point"]), amount)
                desired = (source_rotation.slerp(Quaternion(contact["rotation"]), amount)
                           if contact["lock_rotation"] else source_rotation)
                expected.append((contact, target, desired, _reference(obj, source_body, row)))
            w.assign_action(obj, candidate, slot)
            _frame(scene, frame)
            bpy.context.view_layer.update()
            _, _, current_mapping = _mapping(obj)
            for contact, target, desired, reference in expected:
                row = current_mapping[contact["limb"]]
                error = (_point(obj, row, contact["offset"]) - target).length / reference
                orientation = (_angle(_control_rotation(obj, row), desired)
                               if contact["lock_rotation"] else 0.0)
                maximum_after = max(maximum_after, error)
                orientation_after = max(orientation_after, orientation)
                if contact["start"] <= frame <= contact["end"]:
                    drift_after = max(drift_after,
                                      (_point(obj, row, contact["offset"]) - Vector(contact["point"])).length / reference)
                if error > 2e-4 or orientation > 1e-3:
                    raise ValueError(f"Evaluated paw contact failed at frame {frame:g}: "
                                     f"{contact['limb']}, position={error:.6g}, rotation={orientation:.6g}")
                checks += 1
            if source_priority is not None:
                current_priority = w.raw_pose(obj, profile.controls)
                for name, source_value in source_priority.items():
                    current_value = current_priority[name]
                    if (max(abs(a - b) for a, b in zip(source_value["location"], current_value["location"])) > 2e-5
                            or _angle(Quaternion(source_value["rotation"]), Quaternion(current_value["rotation"])) > 2e-5):
                        raise ValueError("Four-paw correction changed an authored priority pose")
            restore_previous()
            checkpoint_pose = w.raw_pose(obj)
            at_checkpoint = True
            yield dict(phase="Checking four-paw contacts", frame=frame, total=len(validation_frames))
            guard()
            at_checkpoint = False

        w.assign_action(obj, original, slot)
        if _action_signature(obj, original) != input_signature:
            raise ValueError("Input candidate changed during four-paw contact correction")
        w.assign_action(obj, candidate, slot)
        _frame(scene, original_frame)
        report = dict(schema=1, backend="generated_rigify_four_paw_contacts_v1",
                      profiles=[profile.name], frames=len(frames),
                      validation_frames=len(validation_frames), contacts=len(request),
                      checks=checks, max_before=maximum_before, max_after=maximum_after,
                      contact_drift_before=drift_before, contact_drift_after=drift_after,
                      orientation_error_radians=orientation_after, max_residual_passes=max_passes,
                      position_units="fraction of body-to-paw reference distance",
                      sample_interval_frames=0.25,
                      validation_max_interval_frames=max(
                          (b - a for a, b in zip(validation_frames, validation_frames[1:])), default=0.0),
                      elapsed_ms=(time.perf_counter() - started) * 1000.0,
                      learned=False, gait_inference=False)
        candidate["b4ml_quadruped_contacts"] = json.dumps(request, allow_nan=False)
        candidate["b4ml_quadruped_contact_metrics"] = json.dumps(report, allow_nan=False)
        state.candidate_action = candidate
        state.contact_input = original
        state.contact_output = candidate
        state.contact_metrics = json.dumps(report, allow_nan=False)
        state.status = (f"Four-paw drift {drift_before:.3g} -> {drift_after:.3g}; "
                        f"sampled fit {maximum_after:.3g}")
        original.use_fake_user = True
        if previous is not original and previous.users == 0:
            bpy.data.actions.remove(previous)
        committed = True
        return report
    finally:
        if not committed:
            if not at_checkpoint:
                restore_previous()
            if candidate is not None and candidate.users == 0:
                bpy.data.actions.remove(candidate)


def start(obj, scene):
    pointer = obj.as_pointer()
    if pointer in _JOBS:
        raise ValueError("Four-paw contact correction is already running")
    iterator = correction_steps(obj, scene)
    _JOBS[pointer] = dict(obj=obj, iterator=iterator)
    obj.b4ml.contact_running = True
    obj.b4ml.contact_progress = "Preparing four-paw contacts"


def step(obj):
    job = _JOBS.get(obj.as_pointer())
    if job is None:
        raise InterruptedError("Four-paw contact correction stopped")
    try:
        info = next(job["iterator"])
        obj.b4ml.contact_progress = f"{info['phase']}: frame {info['frame']:g}"
        return False
    except StopIteration:
        _JOBS.pop(obj.as_pointer(), None)
        obj.b4ml.contact_running = False
        obj.b4ml.contact_progress = ""
        return True
    except BaseException:
        abort(obj)
        raise


def abort(obj):
    job = _JOBS.pop(obj.as_pointer(), None)
    try:
        if job:
            job["iterator"].close()
    finally:
        obj.b4ml.contact_running = False
        obj.b4ml.contact_progress = ""


def solve(obj, scene):
    start(obj, scene)
    while not step(obj):
        pass
    return json.loads(obj.b4ml.contact_metrics)


def restore_before_contacts(obj, scene):
    state = obj.b4ml
    if state.contact_running or state.flight_running or state.secondary_running or state.cleanup_running:
        raise ValueError("Finish or cancel the active correction first")
    if (not state.contact_input or state.contact_output != state.candidate_action
            or not obj.animation_data or obj.animation_data.action != state.contact_output):
        raise ValueError("Select the corrected four-paw candidate first")
    w.assign_action(obj, state.contact_input, w._slot(obj.animation_data))
    state.candidate_action = state.contact_input
    state.contact_input = None
    state.contact_output = None
    state.contact_metrics = ""
    _frame(scene, _frame(scene))
    state.status = "Quadruped candidate restored before four-paw correction"


def register():
    return None


def unregister():
    for job in list(_JOBS.values()):
        try:
            abort(job["obj"])
        except (ReferenceError, RuntimeError):
            pass
    _JOBS.clear()
