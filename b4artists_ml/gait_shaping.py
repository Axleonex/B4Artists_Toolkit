"""Deterministic dense gait shaping applied to an isolated candidate action."""
import math


def arm_swing_fraction(frame, cycle_start=1.0, cycle_frames=31.0):
    """Return a continuous full-cycle arm phase in [-1, 1]."""
    frame = float(frame)
    cycle_start = float(cycle_start)
    cycle_frames = float(cycle_frames)
    if not all(math.isfinite(value) for value in (frame, cycle_start, cycle_frames)):
        raise ValueError("Arm-swing phase requires finite values")
    if cycle_frames <= 0:
        raise ValueError("Arm-swing cycle must be positive")
    return math.sin(2.0 * math.pi * (frame - cycle_start) / cycle_frames)


def apply_dense_arm_swing(
    obj,
    scene,
    *,
    first_frame=1,
    last_frame=40,
    cycle_frames=31.0,
    amplitude=0.10,
    drop=0.52,
    outward=0.12,
):
    """Write smooth cross-rig FK arm swing to the active candidate action.

    The candidate must already be assigned.  Every integer frame is keyed so
    sparse target interpolation cannot reverse the arm at a landing boundary.
    The operation does not touch the source action, hands, root, legs, contacts,
    or torso controls.
    """
    import bpy
    from mathutils import Vector
    from . import posing, workflow
    from .math_core import two_bone_positions

    if obj.b4ml.candidate_action is None:
        raise ValueError("Dense gait shaping requires an isolated candidate action")
    if (isinstance(first_frame, bool) or isinstance(last_frame, bool)
            or not math.isfinite(float(first_frame))
            or not math.isfinite(float(last_frame))
            or not float(first_frame).is_integer()
            or not float(last_frame).is_integer()):
        raise ValueError("Dense gait shaping requires integer frame bounds")
    first_frame, last_frame = int(first_frame), int(last_frame)
    if not (1 <= first_frame <= last_frame):
        raise ValueError("Dense gait shaping requires an ordered frame range")
    for value in (cycle_frames, amplitude, drop, outward):
        if not math.isfinite(float(value)):
            raise ValueError("Dense gait shaping settings must be finite")
    if not (0.0 <= amplitude <= 0.25 and 0.25 <= drop <= 0.8 and 0.0 <= outward <= 0.3):
        raise ValueError("Dense gait shaping settings are outside bounded limits")

    profile, root_name, rows = posing.bindings(obj)
    arms = {row["id"]: row for row in rows if row["id"] in {"arm-L", "arm-R"}}
    if set(arms) != {"arm-L", "arm-R"}:
        raise ValueError("Dense gait shaping requires both semantic arms")
    for row in arms.values():
        if len(row["joints"]) != 3 or len(row["fk"]) != 3:
            raise ValueError("Dense gait shaping requires two-bone semantic arms")

    action = obj.b4ml.candidate_action
    curves = workflow.action_curves(
        action, getattr(obj.animation_data, "action_slot", None), ensure=True, obj=obj
    )
    original_frame = scene.frame_current
    original_subframe = scene.frame_subframe
    frames = list(range(int(first_frame), int(last_frame) + 1))
    snapshots = {}
    curve_samples = {}
    non_arm_names = sorted({
        name for role, name in profile.roles.items()
        if not any(part in role for part in ("upperarm", "forearm", "hand", "clavicle"))
        and name in obj.pose.bones
    })
    non_arm_before = {}

    def matrix_values(pb):
        return tuple(float(value) for row in pb.matrix for value in row)

    def rotation_value(pb):
        if pb.rotation_mode == "QUATERNION":
            return tuple(pb.rotation_quaternion)
        if pb.rotation_mode == "AXIS_ANGLE":
            return tuple(pb.rotation_axis_angle)
        return tuple(pb.rotation_euler)

    def restore_rotation(pb, value):
        if pb.rotation_mode == "QUATERNION":
            pb.rotation_quaternion = value
        elif pb.rotation_mode == "AXIS_ANGLE":
            pb.rotation_axis_angle = value
        else:
            pb.rotation_euler = value

    def key_rotation(pb, frame):
        channel = (
            "rotation_quaternion"
            if pb.rotation_mode == "QUATERNION"
            else "rotation_axis_angle"
            if pb.rotation_mode == "AXIS_ANGLE"
            else "rotation_euler"
        )
        values = getattr(pb, channel)
        path = pb.path_from_id(channel)
        for index, value in enumerate(values):
            curve_samples.setdefault((path, index), []).append((frame, float(value)))

    try:
        # Capture unmodified candidate rotations before adding any dense keys.
        for frame in frames:
            scene.frame_set(frame)
            posing._update(obj)
            snapshots[frame] = {
                name: rotation_value(obj.pose.bones[name])
                for row in arms.values()
                for name in row["fk"][:2]
            }
            non_arm_before[frame] = {
                name: matrix_values(obj.pose.bones[name]) for name in non_arm_names
            }

        scene.frame_set(frames[0])
        posing._update(obj)
        left_root = obj.pose.bones[arms["arm-L"]["fk"][0]].head.copy()
        right_root = obj.pose.bones[arms["arm-R"]["fk"][0]].head.copy()
        lateral = left_root - right_root
        if lateral.length < 1e-7:
            raise ValueError("Dense gait shaping found degenerate shoulder width")
        lateral.normalize()
        world = workflow.display_world(obj)
        up = world.inverted().to_3x3() @ Vector((0.0, 0.0, 1.0))
        up -= lateral * up.dot(lateral)
        if up.length < 1e-7:
            raise ValueError("Dense gait shaping found degenerate body up axis")
        up.normalize()
        forward = lateral.cross(up)
        forward.normalize()

        maximum_fitted_error = 0.0
        flexion_samples = {"arm-L": [], "arm-R": []}
        for frame in frames:
            scene.frame_set(frame)
            for name, value in snapshots[frame].items():
                restore_rotation(obj.pose.bones[name], value)
            posing._update(obj)
            phase = arm_swing_fraction(frame, first_frame, cycle_frames)
            for limb, side in (("arm-L", 1.0), ("arm-R", -1.0)):
                row = arms[limb]
                upper_name, middle_name, end_name = row["fk"]
                upper = obj.pose.bones[upper_name]
                middle = obj.pose.bones[middle_name]
                end = obj.pose.bones[end_name]
                root = upper.head.copy()
                upper_length = (middle.head - upper.head).length
                lower_length = (end.head - middle.head).length
                total = upper_length + lower_length
                if min(upper_length, lower_length) < 1e-7:
                    raise ValueError("Dense gait shaping found a degenerate semantic arm")
                desired_end = (
                    root
                    + lateral * (side * outward * total)
                    - up * (drop * total)
                    + forward * (side * amplitude * phase * total)
                )
                pole = root + lateral * (side * total) - up * (0.15 * total)
                desired_middle, fitted_end = two_bone_positions(
                    tuple(root), tuple(desired_end), tuple(pole),
                    upper_length, lower_length,
                    obj.b4ml.max_bend,
                )
                desired_middle = Vector(desired_middle)
                fitted_end = Vector(fitted_end)
                maximum_fitted_error = max(maximum_fitted_error, (fitted_end - desired_end).length)
                posing._aim(obj, upper_name, middle.head - upper.head, desired_middle - root)
                posing._aim(obj, middle_name, end.head - middle.head, fitted_end - desired_middle)
                key_rotation(upper, frame)
                key_rotation(middle, frame)
                joint_upper, joint_middle, joint_end = (
                    obj.pose.bones[name].head for name in row["joints"]
                )
                first = joint_upper - joint_middle
                second = joint_end - joint_middle
                angle = first.angle(second, math.pi)
                flexion_samples[limb].append(math.degrees(max(0.0, math.pi - angle)))
        boundary_state = {}
        for path_index in curve_samples:
            path, index = path_index
            curve = curves.find(path, index=index)
            if curve is None:
                raise ValueError('Dense arm swing requires existing keys at both range boundaries')
            first_key = last_key = None
            for existing in curve.keyframe_points:
                if abs(float(existing.co.x)-first_frame) <= 1e-8:
                    first_key = existing
                if abs(float(existing.co.x)-last_frame) <= 1e-8:
                    last_key = existing
            if first_key is None or last_key is None:
                raise ValueError('Dense arm swing requires existing keys at both range boundaries')
            boundary_state[path_index] = (
                (first_key.handle_left_type, tuple(first_key.handle_left)),
                (last_key.interpolation, last_key.handle_right_type,
                 tuple(last_key.handle_right)))
        for (path, index), points in curve_samples.items():
            curve = curves.find(path, index=index)
            for key_index in range(len(curve.keyframe_points) - 1, -1, -1):
                if first_frame < curve.keyframe_points[key_index].co.x < last_frame:
                    curve.keyframe_points.remove(curve.keyframe_points[key_index], fast=True)
            for frame, value in points:
                if (abs(frame-first_frame) <= 1e-8
                        or abs(frame-last_frame) <= 1e-8):
                    continue
                key = curve.keyframe_points.insert(frame, value, options={"FAST"})
                key.interpolation = "LINEAR"
            curve.update()
            first_key = next(key for key in curve.keyframe_points
                             if abs(float(key.co.x)-first_frame) <= 1e-8)
            last_key = next(key for key in curve.keyframe_points
                            if abs(float(key.co.x)-last_frame) <= 1e-8)
            incoming, outgoing = boundary_state[(path, index)]
            first_key.interpolation = "LINEAR"
            first_key.handle_left_type = incoming[0]
            first_key.handle_left = incoming[1]
            last_key.interpolation = outgoing[0]
            last_key.handle_right_type = outgoing[1]
            last_key.handle_right = outgoing[2]
        action["b4ml_dense_arm_swing"] = True
        action["b4ml_dense_arm_swing_cycle_frames"] = float(cycle_frames)
        non_arm_error = 0.0
        final_flexions = {"arm-L": [], "arm-R": []}
        for frame in frames:
            scene.frame_set(frame)
            posing._update(obj)
            for name in non_arm_names:
                before = non_arm_before[frame][name]
                after = matrix_values(obj.pose.bones[name])
                non_arm_error = max(
                    non_arm_error,
                    max(abs(first - second) for first, second in zip(before, after)),
                )
            for limb, row in arms.items():
                joint_upper, joint_middle, joint_end = (
                    obj.pose.bones[name].head for name in row["joints"]
                )
                first = joint_upper - joint_middle
                second = joint_end - joint_middle
                angle = first.angle(second, math.pi)
                final_flexions[limb].append(math.degrees(max(0.0, math.pi - angle)))
        return {
            "schema": "b4ml-dense-arm-swing-v1",
            "frames": len(frames),
            "cycle_frames": float(cycle_frames),
            "amplitude": float(amplitude),
            "drop": float(drop),
            "outward": float(outward),
            "maximum_fitted_error": float(maximum_fitted_error),
            "immediate_minimum_flexion_degrees": min(min(values) for values in flexion_samples.values()),
            "immediate_maximum_flexion_degrees": max(max(values) for values in flexion_samples.values()),
            "minimum_flexion_degrees": min(min(values) for values in final_flexions.values()),
            "maximum_flexion_degrees": max(max(values) for values in final_flexions.values()),
            "non_arm_priority_matrix_error": float(non_arm_error),
            "written_controls": sorted({name for row in arms.values() for name in row["fk"][:2]}),
            "written_curve_count": len(curve_samples),
            "source_action_unchanged": True,
        }
    finally:
        scene.frame_set(original_frame, subframe=original_subframe)
        posing._update(obj)
