"""Reversible sparse whole-body posing for generated Rigify quadrupeds.

This deterministic path uses Rigify's existing four-limb IK controls.  It is
kept separate from the 17-joint humanoid model and does not claim learned
quadruped motion, contact, balance, or gait generation.

SPDX-License-Identifier: GPL-2.0-or-later
"""
import json
import math
import uuid

import bpy
from mathutils import Matrix, Quaternion, Vector

from . import posing as p
from . import workflow as w
from .rigs import detect_rig


LEGACY_TARGETS = ("Body", "Fore Paw L", "Fore Paw R", "Hind Paw L", "Hind Paw R")
TARGETS = LEGACY_TARGETS + ("Head",)
POLE_TARGETS = ("Fore Pole L", "Fore Pole R", "Hind Pole L", "Hind Pole R")
CURRENT_TARGETS = TARGETS + POLE_TARGETS
MIRROR_PAIRS = (("Fore Paw L", "Fore Paw R"), ("Hind Paw L", "Hind Paw R"))
POSE_ASSET_KEY = "b4ml_quadruped_target_pose_asset_v1"
POSE_ASSET_MAX_CHARS = 65536

_SCHEMAS = {
    "Rigify Generated Quadruped (Cat)": {
        "fore": ("upper_arm_parent", "hand_ik", "ORG-f_toe", "upper_arm_ik_target"),
        "hind": ("thigh_parent", "foot_ik", "ORG-r_toe", "thigh_ik_target"),
    },
    "Rigify Generated Quadruped (Horse)": {
        "fore": ("upper_arm_parent", "forefoot_ik", "ORG-f_toe", "upper_arm_ik_target"),
        "hind": ("thigh_parent", "hind_foot_ik", "ORG-r_toe", "thigh_ik_target"),
    },
    "Rigify Generated Quadruped (Wolf)": {
        "fore": ("front_thigh_parent", "front_foot_ik", "ORG-front_toe", "front_thigh_ik_target"),
        "hind": ("thigh_parent", "foot_ik", "ORG-toe", "thigh_ik_target"),
    },
}

_POLE_MATCH_SCHEMAS = {
    "Rigify Generated Quadruped (Cat)": {
        "fore": (("MCH-upper_arm_ik", "MCH-forearm_ik", "MCH-upper_arm_ik_target", "MCH-upper_arm_ik_target"),
                 ("upper_arm_ik", "upper_arm_ik_target", "hand_heel_ik", "hand_ik"), ()),
        "hind": (("MCH-thigh_ik", "MCH-shin_ik", "MCH-thigh_ik_target", "MCH-thigh_ik_target"),
                 ("thigh_ik", "thigh_ik_target", "foot_heel_ik", "foot_ik"), ()),
    },
    "Rigify Generated Quadruped (Horse)": {
        "fore": (("MCH-upper_arm_ik", "MCH-forearm_ik", "MCH-upper_arm_ik_target", "MCH-f_toe_ik_out"),
                 ("upper_arm_ik", "upper_arm_ik_target", "forefoot_heel_ik", "forefoot_ik"),
                 ("f_toe_ik",)),
        "hind": (("MCH-thigh_ik", "MCH-lower_leg_ik", "MCH-thigh_ik_target", "MCH-r_toe_ik_out"),
                 ("thigh_ik", "thigh_ik_target", "hind_foot_heel_ik", "hind_foot_ik"),
                 ("r_toe_ik",)),
    },
    "Rigify Generated Quadruped (Wolf)": {
        "fore": (("MCH-front_thigh_ik", "MCH-front_shin_ik", "MCH-front_thigh_ik_target", "MCH-front_thigh_ik_target"),
                 ("front_thigh_ik", "front_thigh_ik_target", "front_foot_heel_ik", "front_foot_ik"), ()),
        "hind": (("MCH-thigh_ik", "MCH-shin_ik", "MCH-thigh_ik_target", "MCH-thigh_ik_target"),
                 ("thigh_ik", "thigh_ik_target", "foot_heel_ik", "foot_ik"), ()),
    },
}


def _plain(value):
    return json.loads(json.dumps(value, allow_nan=False))


def _frame(scene):
    return (scene.frame_current, scene.frame_subframe)


def _matrix(matrix):
    return [list(row) for row in matrix]


def _world_point(obj, point):
    return obj.matrix_world @ point


def binding(obj):
    w.require_rig(obj)
    profile = detect_rig(obj.data.bones.keys())
    if profile.family != "quadruped":
        raise ValueError("Quadruped whole-body posing requires a recognized quadruped rig")
    schema = _SCHEMAS.get(profile.name)
    if schema is None:
        raise ValueError("Quadruped whole-body posing currently supports generated Rigify cat, horse, and wolf rigs")
    if "torso" not in obj.pose.bones:
        raise ValueError("Generated quadruped torso control is missing")
    limbs = []
    for kind, label in (("fore", "Fore Paw"), ("hind", "Hind Paw")):
        parent_stem, ik_stem, joint_stem, pole_stem = schema[kind]
        for side in ("L", "R"):
            names = (parent_stem + "." + side, ik_stem + "." + side,
                     joint_stem + "." + side, pole_stem + "." + side)
            if any(name not in obj.pose.bones for name in names):
                raise ValueError("Incomplete generated quadruped IK mapping: " + kind + "-" + side)
            parent = obj.pose.bones[names[0]]
            if "IK_FK" not in parent:
                raise ValueError("Generated quadruped IK/FK property is missing: " + names[0])
            value = parent["IK_FK"]
            if not isinstance(value, (int, float)) or not math.isfinite(value):
                raise ValueError("Invalid quadruped IK/FK value: " + names[0])
            limbs.append({"id": kind + "-" + side, "label": label + " " + side,
                          "property_bone": names[0], "ik": names[1], "joint": names[2],
                          "pole_label": label.replace("Paw", "Pole") + " " + side,
                          "pole": names[3]})
    return profile, "torso", limbs


def mode_values(obj, limbs=None):
    if limbs is None:
        _, _, limbs = binding(obj)
    return {row["property_bone"]: float(obj.pose.bones[row["property_bone"]]["IK_FK"])
            for row in limbs}


def pole_mode_values(obj, limbs=None):
    if limbs is None:
        _, _, limbs = binding(obj)
    values = {}
    driven = ({curve.data_path for curve in obj.animation_data.drivers}
              if obj.animation_data else set())
    for row in limbs:
        bone = obj.pose.bones[row["property_bone"]]
        if "pole_vector" not in bone:
            raise ValueError("Generated quadruped Pole Vector property is missing: " + row["property_bone"])
        path = bone.path_from_id() + '[' + json.dumps("pole_vector") + ']'
        if path in driven:
            raise ValueError("Quadruped posing requires an undriven Pole Vector mode: " +
                             row["property_bone"])
        value = bone["pole_vector"]
        if not isinstance(value, (bool, int, float)) or not math.isfinite(float(value)):
            raise ValueError("Invalid quadruped Pole Vector value: " + row["property_bone"])
        values[row["property_bone"]] = float(value)
    return values


def _require_pole_vectors(obj, limbs):
    values = pole_mode_values(obj, limbs)
    disabled = [name for name, value in values.items() if abs(value - 1.0) > 1e-7]
    if disabled:
        raise ValueError("Enable Rigify Pole Vector for all four limbs before using Pole Targets: " +
                         ", ".join(disabled))
    return values


def _pole_match_rows(profile, obj, limbs):
    schema = _POLE_MATCH_SCHEMAS.get(profile.name)
    rig_id = obj.data.get("rig_id")
    if not isinstance(rig_id, str) or not rig_id:
        raise ValueError("Generated Rigify pole-matching operator identity is missing")
    operator_name = "rigify_limb_toggle_pole_" + rig_id
    if not hasattr(bpy.ops.pose, operator_name):
        raise ValueError("This generated Rigify rig has no compatible Toggle Pole operator")
    result = []
    for row in limbs:
        kind, side = row["id"].split("-")
        ik_stems, control_stems, extra_stems = schema[kind]
        names = lambda stems: [stem + "." + side for stem in stems]
        match = dict(row)
        match.update(operator=operator_name, ik_bones=names(ik_stems),
                     ctrl_bones=names(control_stems), extra_ctrls=names(extra_stems))
        required = [*match["ik_bones"], *match["ctrl_bones"], *match["extra_ctrls"]]
        if any(name not in obj.pose.bones for name in required):
            raise ValueError("Incomplete generated Rigify pole-matching mapping: " + row["id"])
        result.append(match)
    return result


def _set_pole_modes(obj, values):
    for name, value in values.items():
        obj.pose.bones[name]["pole_vector"] = value
    obj.update_tag(refresh={"OBJECT"})
    bpy.context.view_layer.update()


def match_pole_vectors(obj, scene):
    """Use the generated Rigify operator to match and enable all four poles."""
    state = obj.b4ml
    busy = (state.quadruped_payload or state.posing_payload or state.body_payload or
            state.candidate_action or state.temporal_running or state.contact_running or
            state.flight_running or state.secondary_running or state.cleanup_running or
            state.contact_suggest_running or
            w.motion_layer.find(obj))
    if busy:
        raise ValueError("Resolve the active preview before matching quadruped poles")
    if bpy.context.screen and bpy.context.screen.is_animation_playing:
        raise ValueError("Stop playback before matching quadruped poles")
    w._reject_nla(obj)
    profile, _, limbs = binding(obj)
    p._check_space(obj)
    _require_ik(obj, limbs)
    before_modes = pole_mode_values(obj, limbs)
    before_mode_raw = {name: obj.pose.bones[name]["pole_vector"] for name in before_modes}
    if any(value not in {0.0, 1.0} for value in before_modes.values()):
        raise ValueError("Rigify Pole Vector modes must be exact Off or On values before matching")
    rows = _pole_match_rows(profile, obj, limbs)
    pending = [row for row in rows if abs(before_modes[row["property_bone"]] - 1.0) > 1e-7]
    if not pending:
        state.quadruped_use_poles = True
        state.status = "All four Rigify Pole Vectors are already enabled"
        return {"matched": 0, "max_position_error": 0.0,
                "max_rotation_error": 0.0, "tolerance": 0.0}
    mode_paths = {obj.pose.bones[name].path_from_id() + '[' + json.dumps("pole_vector") + ']'
                  for name in before_modes}
    written = {name for row in pending for name in
               [row["ctrl_bones"][0], row["ctrl_bones"][1], *row["ctrl_bones"][2:-1]]}
    middle = {name for row in pending for name in row["ctrl_bones"][2:-1]}
    transform_paths = {obj.pose.bones[name].path_from_id(prop) for name in written for prop in
                       ("location", "scale", "rotation_euler", "rotation_quaternion",
                        "rotation_axis_angle")}
    expected_channels = {}
    for row in pending:
        expected_channels.update({
            row["ctrl_bones"][0]: ((False, False, False), (True, False, True), (False, False, False)),
            row["ctrl_bones"][1]: ((False, False, False), (False, False, False), (False, False, False)),
            **{name: ((True, True, True), (False, False, False), (False, False, False))
               for name in row["ctrl_bones"][2:-1]},
        })
    for name in written:
        bone = obj.pose.bones[name]
        actual_channels = (tuple(bone.lock_location), tuple(bone.lock_rotation), tuple(bone.lock_scale))
        if actual_channels != expected_channels[name]:
            raise ValueError("Rigify pole matching control channels changed: " + name)
        if any(not constraint.mute and constraint.influence
               for constraint in bone.constraints):
            raise ValueError("Rigify pole matching cannot overwrite a constrained control: " + name)
    for name in middle:
        bone = obj.data.bones[name]
        if not bone.use_inherit_rotation or bone.inherit_scale != "FULL":
            raise ValueError("Rigify pole matching bone inheritance changed: " + name)
    ad = obj.animation_data
    driven = {curve.data_path for curve in ad.drivers} if ad else set()
    ik_mode_paths = {obj.pose.bones[row["property_bone"]].path_from_id() +
                     '[' + json.dumps("IK_FK") + ']' for row in limbs}
    if driven & ik_mode_paths:
        raise ValueError("Rigify pole matching requires undriven IK/FK modes")
    if driven & transform_paths:
        raise ValueError("Rigify pole matching cannot overwrite driven controls")
    if ad and ad.action:
        curves = w.action_curves(ad.action, getattr(ad, "action_slot", None))
        animated = {curve.data_path for curve in curves}
        if animated & mode_paths:
            raise ValueError("Animated Pole Vector modes cannot be matched at one frame")
        if animated & transform_paths:
            raise ValueError("Animated quadruped limb controls require Rigify's range conversion")
    bpy.context.view_layer.update()
    before_pose = w.raw_pose(obj, set(profile.controls) | written)
    before_bone_state = {name: (obj.data.bones[name].use_inherit_rotation,
                                obj.data.bones[name].inherit_scale) for name in middle}
    observed = {name for row in pending for name in [*row["ik_bones"], row["joint"]]}
    matrices = {name: obj.pose.bones[name].matrix.copy() for name in observed}
    origin = next(iter(matrices.values())).translation
    reference = max(1e-8, max((matrix.translation - origin).length for matrix in matrices.values()))
    tolerance = max(2e-5, reference * 2e-4)
    autokey = scene.tool_settings.use_keyframe_insert_auto
    try:
        scene.tool_settings.use_keyframe_insert_auto = False
        override = {"object": obj, "active_object": obj,
                    "selected_objects": [obj], "selected_editable_objects": [obj]}
        with bpy.context.temp_override(**override):
            for row in pending:
                operator = getattr(bpy.ops.pose, row["operator"])
                result = operator(use_pole=True, prop_bone=row["property_bone"],
                                  pole_prop="pole_vector",
                                  ik_bones=json.dumps(row["ik_bones"]),
                                  ctrl_bones=json.dumps(row["ctrl_bones"]),
                                  extra_ctrls=json.dumps(row["extra_ctrls"]))
                if result != {"FINISHED"}:
                    raise ValueError("Rigify Toggle Pole did not finish: " + row["id"])
        bpy.context.view_layer.update()
        _require_ik(obj, limbs)
        _require_pole_vectors(obj, limbs)
        max_position = 0.0
        max_rotation = 0.0
        max_linear = 0.0
        max_position_bone = ""
        max_rotation_bone = ""
        max_linear_bone = ""
        for name, wanted in matrices.items():
            actual = obj.pose.bones[name].matrix
            position = (actual.translation - wanted.translation).length
            if position > max_position:
                max_position = position
                max_position_bone = name
            angle = actual.to_quaternion().rotation_difference(wanted.to_quaternion()).angle
            angle = min(angle, abs(2.0 * math.pi - angle))
            if angle > max_rotation:
                max_rotation = angle
                max_rotation_bone = name
            linear = max(abs(actual[row][column] - wanted[row][column])
                         for row in range(3) for column in range(3))
            if linear > max_linear:
                max_linear = linear
                max_linear_bone = name
        if max_position > tolerance or max_rotation > 0.001 or max_linear > 0.0002:
            raise ValueError("Rigify pole matching did not preserve the evaluated pose; "
                             f"position error {max_position:.6g} at {max_position_bone}, "
                             f"rotation error {max_rotation:.6g} at {max_rotation_bone}, "
                             f"linear error {max_linear:.6g} at {max_linear_bone}")
        state.quadruped_use_poles = True
        state.status = "Matched and enabled all four Rigify Pole Vectors"
        return {"matched": len(pending), "max_position_error": max_position,
                "max_rotation_error": max_rotation, "max_linear_error": max_linear,
                "tolerance": tolerance, "linear_tolerance": 0.0002}
    except Exception:
        _set_pole_modes(obj, before_mode_raw)
        for name, values in before_bone_state.items():
            obj.data.bones[name].use_inherit_rotation = values[0]
            obj.data.bones[name].inherit_scale = values[1]
        w.restore_pose(obj, before_pose)
        bpy.context.view_layer.update()
        raise
    finally:
        scene.tool_settings.use_keyframe_insert_auto = autokey


def _require_ik(obj, limbs):
    values = mode_values(obj, limbs)
    wrong = [name for name, value in values.items() if abs(value) > 1e-7]
    if wrong:
        raise ValueError("Switch all generated quadruped limbs to IK before posing: " + ", ".join(wrong))
    return values


def _check_writable(obj, body, limbs, rotate=(), move=()):
    controls = [body] + [row["ik"] for row in limbs] + list(move)
    driven = set()
    if obj.animation_data:
        driven = {curve.data_path for curve in obj.animation_data.drivers}
    for name in controls:
        bone = obj.pose.bones[name]
        if set(w._channels(bone)["location"]) != {0, 1, 2}:
            raise ValueError("Quadruped posing requires unlocked XYZ location: " + name)
        if any(not constraint.mute and constraint.influence for constraint in bone.constraints):
            raise ValueError("Quadruped posing cannot move a constrained control: " + name)
        if bone.path_from_id("location") in driven:
            raise ValueError("Quadruped posing cannot move a driven control: " + name)
    for name in rotate:
        bone = obj.pose.bones[name]
        if not w._channels(bone)["rotation"]:
            raise ValueError("Quadruped posing requires unlocked rotation: " + name)
        if any(not constraint.mute and constraint.influence for constraint in bone.constraints):
            raise ValueError("Quadruped posing cannot rotate a constrained control: " + name)
        paths = {bone.path_from_id(prop) for prop in
                 ("rotation_euler", "rotation_quaternion", "rotation_axis_angle")}
        if paths & driven:
            raise ValueError("Quadruped posing cannot rotate a driven control: " + name)
    for row in limbs:
        bone = obj.pose.bones[row["property_bone"]]
        path = bone.path_from_id() + '[' + json.dumps("IK_FK") + ']'
        if path in driven:
            raise ValueError("Quadruped posing requires an undriven IK/FK mode: " + row["property_bone"])


def _read(obj):
    try:
        record = json.loads(obj.b4ml.quadruped_payload)
    except (TypeError, ValueError):
        raise ValueError("Unreadable quadruped pose preview") from None
    if not isinstance(record, dict) or record.get("schema") not in {1, 2, 3, 4}:
        raise ValueError("Unsupported quadruped pose preview")
    return record


def _targets(record):
    if record.get("schema") == 4:
        return CURRENT_TARGETS
    return TARGETS if record.get("schema") in {2, 3} else LEGACY_TARGETS


def _head_control(profile, obj):
    name = profile.roles.get("head")
    if not name or name not in obj.pose.bones or name not in profile.controls:
        raise ValueError("Generated quadruped head control is missing")
    return name


def _spine_controls(profile, obj):
    controls = {}
    for role in ("chest", "neck"):
        name = profile.roles.get(role)
        if not name or name not in obj.pose.bones or name not in profile.controls:
            raise ValueError("Generated quadruped semantic " + role.title() + " control is missing")
        controls[role] = name
    if len(set(controls.values())) != len(controls):
        raise ValueError("Generated quadruped Chest and Neck controls must be distinct")
    return controls


def _spine_weights(follow, neck_share):
    return {"chest": follow * (1.0 - neck_share),
            "neck": follow * neck_share}


def _validate_head_target(item, record):
    helper = item.target
    if tuple(helper.lock_location) != (True, True, True):
        raise ValueError("Quadruped Head target location must remain locked")
    if helper.parent is not None:
        raise ValueError("Quadruped Head target parenting is not supported")
    if any(not constraint.mute and constraint.influence for constraint in helper.constraints):
        raise ValueError("Quadruped Head target constraints are not supported")
    ad = helper.animation_data
    active_nla = bool(ad and any(not track.mute and any(not strip.mute for strip in track.strips)
                                for track in ad.nla_tracks))
    if ad and (ad.action or ad.drivers or active_nla):
        raise ValueError("Quadruped Head target animation or drivers are not supported")
    if (Vector(helper.delta_location).length > 1e-9 or
            Vector(helper.delta_rotation_euler).length > 1e-9 or
            Quaternion(helper.delta_rotation_quaternion).rotation_difference(Quaternion()).angle > 1e-9 or
            any(abs(value - 1.0) > 1e-9 for value in helper.delta_scale)):
        raise ValueError("Quadruped Head target delta transforms are not supported")
    if any(abs(value - 1.0) > 1e-9 for value in helper.scale):
        raise ValueError("Quadruped Head target scale must remain unchanged")
    origin = record.get("origins", {}).get("Head")
    if not isinstance(origin, list) or len(origin) != 3:
        raise ValueError("Invalid saved quadruped Head target")
    tolerance = max(1e-7, float(record.get("scale", 0.0)) * 1e-6)
    if (Vector(helper.location) - Vector(origin)).length > tolerance:
        raise ValueError("Quadruped Head target position changed; keep its location locked")


def _validate_pole_target(item, label, record):
    helper = item.target
    if item.use_orientation:
        raise ValueError("Quadruped pole targets are position-only: " + label)
    if tuple(helper.lock_rotation) != (True, True, True):
        raise ValueError("Quadruped pole target rotation must remain locked: " + label)
    if helper.rotation_mode != "QUATERNION":
        raise ValueError("Quadruped pole target rotation mode must remain Quaternion: " + label)
    if helper.parent is not None:
        raise ValueError("Quadruped pole target parenting is not supported: " + label)
    if any(not constraint.mute and constraint.influence for constraint in helper.constraints):
        raise ValueError("Quadruped pole target constraints are not supported: " + label)
    ad = helper.animation_data
    active_nla = bool(ad and any(not track.mute and any(not strip.mute for strip in track.strips)
                                for track in ad.nla_tracks))
    if ad and (ad.action or ad.drivers or active_nla):
        raise ValueError("Quadruped pole target animation or drivers are not supported: " + label)
    if (Vector(helper.delta_location).length > 1e-9 or
            Vector(helper.delta_rotation_euler).length > 1e-9 or
            Quaternion(helper.delta_rotation_quaternion).rotation_difference(Quaternion()).angle > 1e-9 or
            any(abs(value - 1.0) > 1e-9 for value in helper.delta_scale)):
        raise ValueError("Quadruped pole target delta transforms are not supported: " + label)
    if any(abs(value - 1.0) > 1e-9 for value in helper.scale):
        raise ValueError("Quadruped pole target scale must remain unchanged: " + label)
    saved = record.get("orientations", {}).get(label)
    if not isinstance(saved, list) or len(saved) != 4:
        raise ValueError("Invalid saved quadruped pole target: " + label)
    current = helper.matrix_world.to_quaternion().normalized()
    angle = current.rotation_difference(Quaternion(saved).normalized()).angle
    if angle > 2e-6:
        raise ValueError("Quadruped pole target rotation changed; move its position only: " +
                         label + f" ({angle:.6g} radians)")


def _validate_resettable_target(item, label):
    """Reject transform ownership that would make a reset ambiguous."""
    helper = item.target
    if helper.rotation_mode != "QUATERNION":
        raise ValueError("Quadruped target rotation mode must remain Quaternion: " + label)
    if helper.parent is not None:
        raise ValueError("Quadruped target parenting is not supported: " + label)
    if len(helper.constraints):
        raise ValueError("Quadruped target constraints are not supported: " + label)
    ad = helper.animation_data
    if ad is not None:
        raise ValueError("Quadruped target animation or drivers are not supported: " + label)
    if (Vector(helper.delta_location).length > 1e-9 or
            Vector(helper.delta_rotation_euler).length > 1e-9 or
            Quaternion(helper.delta_rotation_quaternion).rotation_difference(Quaternion()).angle > 1e-9 or
            any(abs(value - 1.0) > 1e-9 for value in helper.delta_scale)):
        raise ValueError("Quadruped target delta transforms are not supported: " + label)
    if any(abs(value - 1.0) > 1e-9 for value in helper.scale):
        raise ValueError("Quadruped target scale must remain unchanged: " + label)


def _saved_target_matrix(record, label):
    origins = record.get("origins")
    orientations = record.get("orientations")
    if not isinstance(origins, dict) or not isinstance(orientations, dict):
        raise ValueError("Invalid saved quadruped target metadata: " + label)
    origin = origins.get(label)
    orientation = orientations.get(label)
    if (not isinstance(origin, list) or len(origin) != 3 or
            not isinstance(orientation, list) or len(orientation) != 4 or
            any(not isinstance(value, (int, float)) or not math.isfinite(float(value))
                for value in [*origin, *orientation])):
        raise ValueError("Invalid saved quadruped target metadata: " + label)
    rotation = Quaternion(orientation)
    if rotation.magnitude <= 1e-12:
        raise ValueError("Invalid saved quadruped target rotation: " + label)
    rotation.normalize()
    return Matrix.LocRotScale(Vector(origin), rotation, Vector((1.0, 1.0, 1.0)))


def _proper_helper_matrix(matrix, label):
    """Return a copy of one finite, unit-scale, shear-free helper transform."""
    value = matrix.copy()
    if any(not math.isfinite(float(value[row][column]))
           for row in range(4) for column in range(4)):
        raise ValueError("Invalid quadruped mirror helper transform: " + label)
    linear = value.to_3x3()
    axes = [Vector((linear[0][column], linear[1][column], linear[2][column]))
            for column in range(3)]
    if (any(abs(axis.length - 1.0) > 1e-6 for axis in axes) or
            any(abs(axes[left].dot(axes[right])) > 1e-6
                for left, right in ((0, 1), (0, 2), (1, 2))) or
            linear.determinant() <= 0.0):
        raise ValueError("Quadruped mirror helper has scale, shear, or reflection: " + label)
    return value


def _mirror_reflection(record):
    """Derive the saved quadruped sagittal reflection from paired paw baselines."""
    pair_axes = []
    for left, right in MIRROR_PAIRS:
        axis = (_saved_target_matrix(record, left).translation -
                _saved_target_matrix(record, right).translation)
        if not all(math.isfinite(float(value)) for value in axis) or axis.length <= 1e-8:
            raise ValueError("Invalid saved quadruped left/right span")
        axis.normalize()
        if pair_axes and axis.dot(pair_axes[0]) < 0.0:
            axis.negate()
        pair_axes.append(axis)
    estimate = pair_axes[0] + pair_axes[1]
    if estimate.length <= 1e-8:
        raise ValueError("Ambiguous saved quadruped mirror plane")
    estimate.normalize()
    body = _saved_target_matrix(record, "Body").to_3x3()
    body_axes = [Vector((body[0][column], body[1][column], body[2][column])).normalized()
                 for column in range(3)]
    normal = max(body_axes, key=lambda axis: abs(axis.dot(estimate)))
    if normal.dot(estimate) < 0.0:
        normal.negate()
    if abs(normal.dot(estimate)) < 0.7 or any(abs(normal.dot(axis)) < 0.55 for axis in pair_axes):
        raise ValueError("Saved quadruped sides do not define a stable mirror plane")
    reflection = Matrix.Identity(3)
    for row in range(3):
        for column in range(3):
            reflection[row][column] -= 2.0 * normal[row] * normal[column]
    return reflection


def _mirrored_target_matrix(current, source_start, destination_start, reflection,
                            position_only=False):
    current = _proper_helper_matrix(current, "source")
    source_start = _proper_helper_matrix(source_start, "saved source")
    destination_start = _proper_helper_matrix(destination_start, "saved destination")
    location = (destination_start.translation +
                reflection @ (current.translation - source_start.translation))
    if position_only:
        rotation = destination_start.to_quaternion()
    else:
        delta = current.to_3x3() @ source_start.to_3x3().transposed()
        rotation = (reflection @ delta @ reflection @ destination_start.to_3x3()).to_quaternion()
        rotation.normalize()
    return _proper_helper_matrix(
        Matrix.LocRotScale(location, rotation, Vector((1.0, 1.0, 1.0))),
        "mirrored destination")


def _helper_snapshot(item):
    helper = item.target
    return {
        "helper": helper,
        "matrix": helper.matrix_world.copy(),
        "mode": helper.rotation_mode,
        "scale": tuple(helper.scale),
        "locks": (tuple(helper.lock_location), tuple(helper.lock_rotation),
                  tuple(helper.lock_scale), helper.lock_rotation_w,
                  helper.lock_rotations_4d),
        "deltas": (tuple(helper.delta_location), tuple(helper.delta_rotation_euler),
                   tuple(helper.delta_rotation_quaternion), tuple(helper.delta_scale)),
        "owner": helper.get("b4ml_owner"),
        "session": helper.get("b4ml_session"),
        "enabled": item.enabled,
        "orientation": item.use_orientation,
    }


def _target_topology_snapshot(state):
    """Capture every collection row so rollback can rebuild removed or renamed rows."""
    return [{
        "name": item.name,
        "target": item.target,
        "pole": item.pole,
        "enabled": item.enabled,
        "orientation": item.use_orientation,
        "use_pole": item.use_pole,
        "pole_distance": item.pole_distance,
        "learn_bend": item.learn_bend,
    } for item in state.quadruped_targets]


def _target_topology_matches(state, topology):
    current = list(state.quadruped_targets)
    return len(current) == len(topology) and all(
        item.name == saved["name"] and item.target is saved["target"] and
        item.pole is saved["pole"] and item.enabled == saved["enabled"] and
        item.use_orientation == saved["orientation"] and
        item.use_pole == saved["use_pole"] and
        item.pole_distance == saved["pole_distance"] and
        item.learn_bend == saved["learn_bend"]
        for item, saved in zip(current, topology))


def _helper_matches_snapshot(helper, snapshot):
    matrix_error = max(abs(helper.matrix_world[row][column] - snapshot["matrix"][row][column])
                       for row in range(4) for column in range(4))
    return (matrix_error <= 1e-9 and helper.rotation_mode == snapshot["mode"] and
            tuple(helper.scale) == snapshot["scale"] and helper.parent is None and
            not len(helper.constraints) and helper.animation_data is None and
            (tuple(helper.lock_location), tuple(helper.lock_rotation),
             tuple(helper.lock_scale), helper.lock_rotation_w,
             helper.lock_rotations_4d) == snapshot["locks"] and
            (tuple(helper.delta_location), tuple(helper.delta_rotation_euler),
             tuple(helper.delta_rotation_quaternion),
             tuple(helper.delta_scale)) == snapshot["deltas"] and
            helper.get("b4ml_owner") == snapshot["owner"] and
            helper.get("b4ml_session") == snapshot["session"])


def _helper_matches_asset_invariants(helper, snapshot):
    """Check helper state that a pose-asset apply is never allowed to change."""
    return (helper.rotation_mode == snapshot["mode"] and
            tuple(helper.scale) == snapshot["scale"] and helper.parent is None and
            not len(helper.constraints) and helper.animation_data is None and
            (tuple(helper.lock_location), tuple(helper.lock_rotation),
             tuple(helper.lock_scale), helper.lock_rotation_w,
             helper.lock_rotations_4d) == snapshot["locks"] and
            (tuple(helper.delta_location), tuple(helper.delta_rotation_euler),
             tuple(helper.delta_rotation_quaternion),
             tuple(helper.delta_scale)) == snapshot["deltas"] and
            helper.get("b4ml_owner") == snapshot["owner"] and
            helper.get("b4ml_session") == snapshot["session"])


def _restore_target_topology(state, topology, snapshots):
    state.quadruped_targets.clear()
    for saved in topology:
        item = state.quadruped_targets.add()
        item.name = saved["name"]
        item.target = saved["target"]
        item.pole = saved["pole"]
        item.enabled = saved["enabled"]
        item.use_orientation = saved["orientation"]
        item.use_pole = saved["use_pole"]
        item.pole_distance = saved["pole_distance"]
        item.learn_bend = saved["learn_bend"]
        snapshot = snapshots.get(saved["name"])
        if snapshot is not None and not _helper_matches_snapshot(saved["target"], snapshot):
            _restore_helper_snapshot(item, snapshot)


def _restore_helper_snapshot(item, snapshot):
    helper = snapshot["helper"]
    item.target = helper
    item.enabled = snapshot["enabled"]
    item.use_orientation = snapshot["orientation"]
    helper.parent = None
    while len(helper.constraints):
        helper.constraints.remove(helper.constraints[-1])
    if helper.animation_data is not None:
        helper.animation_data_clear()
    helper["b4ml_owner"] = snapshot["owner"]
    helper["b4ml_session"] = snapshot["session"]
    helper.delta_location, helper.delta_rotation_euler = snapshot["deltas"][:2]
    helper.delta_rotation_quaternion, helper.delta_scale = snapshot["deltas"][2:]
    locks = snapshot["locks"]
    helper.lock_location, helper.lock_rotation, helper.lock_scale = locks[:3]
    helper.lock_rotation_w, helper.lock_rotations_4d = locks[3:]
    helper.rotation_mode = snapshot["mode"]
    helper.matrix_world = snapshot["matrix"]
    helper.scale = snapshot["scale"]


def _pose_settings(obj):
    return {bone.name: (bone.rotation_mode, tuple(bone.lock_location),
                        tuple(bone.lock_rotation), tuple(bone.lock_scale),
                        bone.lock_rotation_w, bone.lock_rotations_4d)
            for bone in obj.pose.bones}


def _restore_pose_settings(obj, pose, settings):
    for name, values in settings.items():
        bone = obj.pose.bones.get(name)
        if bone is not None:
            bone.rotation_mode = values[0]
    w.restore_pose(obj, pose)
    for name, values in settings.items():
        bone = obj.pose.bones.get(name)
        if bone is not None:
            bone.lock_location, bone.lock_rotation, bone.lock_scale = values[1:4]
            bone.lock_rotation_w, bone.lock_rotations_4d = values[4:]


def _validate(obj, scene, record):
    profile, body, limbs = binding(obj)
    p._check_space(obj)
    if record.get("profile") != profile.name or record.get("rest") != w._rest_signature(obj):
        raise ValueError("Rig changed; quadruped pose recovery needs the original rig")
    if record.get("world") != _matrix(obj.matrix_world):
        raise ValueError("Return the rig object to its saved transform before recovering")
    if tuple(record.get("frame", ())) != _frame(scene):
        raise ValueError("Return to the quadruped pose frame, or cancel it")
    ad = obj.animation_data
    if (ad.action if ad else None) != obj.b4ml.quadruped_source:
        raise ValueError("Return to the source action before recovering this quadruped preview")
    if (w._slot(ad) if ad else "") != record.get("slot"):
        raise ValueError("Return to the source action slot")
    if set(record.get("source", {})) != set(profile.controls):
        raise ValueError("Invalid saved quadruped control set")
    if mode_values(obj, limbs) != record.get("modes"):
        raise ValueError("Restore the saved quadruped IK modes before recovering")
    token = record.get("token")
    _head_control(profile, obj)
    if record.get("schema") in {3, 4}:
        controls = _spine_controls(profile, obj)
        if record.get("spine_controls") != controls:
            raise ValueError("Quadruped spine control mapping changed; cancel and restart posing")
    if record.get("schema") == 4:
        pole_controls = {row["id"]: row["pole"] for row in limbs}
        if record.get("pole_controls") != pole_controls:
            raise ValueError("Quadruped pole control mapping changed; cancel and restart posing")
        if record.get("pole_modes") != pole_mode_values(obj, limbs):
            raise ValueError("Quadruped Pole Vector mode changed; restore all four saved modes")
    for label in _targets(record):
        item = obj.b4ml.quadruped_targets.get(label)
        if item is None or not p._owned(item.target, obj, token):
            raise ValueError("Quadruped pose target is missing or replaced: " + label)
        if label == "Head":
            _validate_head_target(item, record)
        elif label in POLE_TARGETS:
            _validate_pole_target(item, label, record)
    return profile, body, limbs


def _evaluated_pole_bend_points(profile, obj, row):
    """Return the evaluated world-space root, middle, and end of one IK bend."""
    schema = _POLE_MATCH_SCHEMAS.get(profile.name)
    kind, side = row["id"].split("-")
    if schema is None or kind not in schema:
        raise ValueError("Quadruped pole bend mapping is unavailable: " + row["id"])
    stems = schema[kind][0]
    if len(stems) < 2:
        raise ValueError("Quadruped pole bend mapping is incomplete: " + row["id"])
    upper_name, lower_name = (stems[0] + "." + side, stems[1] + "." + side)
    evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    upper = evaluated.pose.bones.get(upper_name)
    lower = evaluated.pose.bones.get(lower_name)
    if upper is None or lower is None:
        raise ValueError("Quadruped evaluated pole bend chain is missing: " + row["id"])
    world = evaluated.matrix_world
    points = (world @ upper.head, world @ lower.head, world @ lower.tail)
    if any(not math.isfinite(float(value)) for point in points for value in point):
        raise ValueError("Quadruped evaluated pole bend chain is invalid: " + row["id"])
    return (upper_name, lower_name), points


def _requested_pole_distance(value):
    if (isinstance(value, bool) or not isinstance(value, (int, float)) or
            not math.isfinite(float(value)) or not 0.1 <= float(value) <= 4.0):
        raise ValueError("Pole Target distance must be a finite number from 0.1 to 4 body scales")
    return float(value)


def _pole_edit_conflict(obj):
    """Return workflows that cannot share ownership with an active pole edit."""
    state = obj.b4ml
    return bool(state.candidate_action or state.posing_payload or state.body_payload or
                state.temporal_running or state.body_running or state.body_live or
                state.contact_running or state.contact_suggest_running or
                state.flight_running or state.secondary_running or state.cleanup_running or
                w.motion_layer.find(obj))


def _object_transform_snapshot(obj):
    return {
        "matrix_world": obj.matrix_world.copy(),
        "parent": obj.parent,
        "parent_inverse": obj.matrix_parent_inverse.copy(),
        "rotation_mode": obj.rotation_mode,
        "location": tuple(obj.location),
        "rotation_euler": tuple(obj.rotation_euler),
        "rotation_quaternion": tuple(obj.rotation_quaternion),
        "rotation_axis_angle": tuple(obj.rotation_axis_angle),
        "scale": tuple(obj.scale),
        "delta_location": tuple(obj.delta_location),
        "delta_rotation_euler": tuple(obj.delta_rotation_euler),
        "delta_rotation_quaternion": tuple(obj.delta_rotation_quaternion),
        "delta_scale": tuple(obj.delta_scale),
    }


def _restore_object_transform(obj, snapshot):
    obj.parent = snapshot["parent"]
    obj.matrix_parent_inverse = snapshot["parent_inverse"]
    obj.rotation_mode = snapshot["rotation_mode"]
    obj.location = snapshot["location"]
    obj.rotation_euler = snapshot["rotation_euler"]
    obj.rotation_quaternion = snapshot["rotation_quaternion"]
    obj.rotation_axis_angle = snapshot["rotation_axis_angle"]
    obj.scale = snapshot["scale"]
    obj.delta_location = snapshot["delta_location"]
    obj.delta_rotation_euler = snapshot["delta_rotation_euler"]
    obj.delta_rotation_quaternion = snapshot["delta_rotation_quaternion"]
    obj.delta_scale = snapshot["delta_scale"]


def _object_transform_matches(obj, snapshot):
    matrix_error = max(abs(obj.matrix_world[row][column] -
                           snapshot["matrix_world"][row][column])
                       for row in range(4) for column in range(4))
    parent_inverse_error = max(
        abs(obj.matrix_parent_inverse[row][column] -
            snapshot["parent_inverse"][row][column])
        for row in range(4) for column in range(4))
    return (matrix_error <= 1e-12 and obj.parent is snapshot["parent"] and
            parent_inverse_error <= 1e-12 and
            obj.rotation_mode == snapshot["rotation_mode"] and
            tuple(obj.location) == snapshot["location"] and
            tuple(obj.rotation_euler) == snapshot["rotation_euler"] and
            tuple(obj.rotation_quaternion) == snapshot["rotation_quaternion"] and
            tuple(obj.rotation_axis_angle) == snapshot["rotation_axis_angle"] and
            tuple(obj.scale) == snapshot["scale"] and
            tuple(obj.delta_location) == snapshot["delta_location"] and
            tuple(obj.delta_rotation_euler) == snapshot["delta_rotation_euler"] and
            tuple(obj.delta_rotation_quaternion) == snapshot["delta_rotation_quaternion"] and
            tuple(obj.delta_scale) == snapshot["delta_scale"])


def _edit_pole_target(obj, scene, label, operation, requested_distance=None):
    """Apply one guarded current-frame edit to a schema-4 pole helper."""
    names = {"ALIGN": "Align Bend", "FLIP": "Flip Side", "DISTANCE": "Set Distance"}
    action = names.get(operation)
    if action is None:
        raise ValueError("Unknown quadruped Pole Target edit")
    if bpy.context.screen and bpy.context.screen.is_animation_playing:
        raise ValueError("Stop playback before editing a quadruped pole target")
    if _pole_edit_conflict(obj):
        raise ValueError("Finish the active animation workflow before editing a quadruped Pole Target")
    record = _read(obj)
    profile, _, limbs = _validate(obj, scene, record)
    if record.get("schema") != 4:
        raise ValueError(action + " requires a schema-4 quadruped Pole Target preview")
    rows = {row["pole_label"]: row for row in limbs}
    row = rows.get(label)
    if row is None:
        raise ValueError("Unknown quadruped Pole Target: " + label)
    state = obj.b4ml
    item = state.quadruped_targets.get(label)
    if item is None or not p._owned(item.target, obj, record.get("token")):
        raise ValueError("Quadruped Pole Target is missing or replaced: " + label)
    _validate_resettable_target(item, label)
    _validate_pole_target(item, label, record)
    if tuple(item.target.lock_location) != (False, False, False):
        raise ValueError("Quadruped Pole Target needs unlocked XYZ location: " + label)
    if tuple(item.target.lock_scale) != (False, False, False):
        raise ValueError("Quadruped Pole Target needs unlocked XYZ scale for normalized edits: " + label)
    topology = _target_topology_snapshot(state)
    if [saved["name"] for saved in topology] != list(_targets(record)):
        raise ValueError("Quadruped " + action + " target collection topology is invalid")
    snapshots = {}
    for target_label in _targets(record):
        current = state.quadruped_targets.get(target_label)
        if current is None or not p._owned(current.target, obj, record.get("token")):
            raise ValueError("Quadruped " + action + " target is missing or replaced: " + target_label)
        _validate_resettable_target(current, target_label)
        if target_label == "Head":
            _validate_head_target(current, record)
        elif target_label in POLE_TARGETS:
            _validate_pole_target(current, target_label, record)
        snapshots[target_label] = _helper_snapshot(current)
    helper = item.target
    payload_before = state.quadruped_payload
    status_before = state.status
    source_before = state.quadruped_source
    follow_before = state.quadruped_spine_follow
    neck_before = state.quadruped_neck_share
    before_pose = w.raw_pose(obj)
    before_pose_settings = _pose_settings(obj)
    ad = obj.animation_data
    had_animation_data = ad is not None
    action_before = ad.action if ad else None
    slot_before = w._slot(ad) if ad else ""
    mode_raw_before = {value["property_bone"]:
                       obj.pose.bones[value["property_bone"]]["IK_FK"] for value in limbs}
    pole_raw_before = {value["property_bone"]:
                       obj.pose.bones[value["property_bone"]]["pole_vector"] for value in limbs}
    autokey_before = scene.tool_settings.use_keyframe_insert_auto
    object_transform_before = _object_transform_snapshot(obj)
    scale = _preview_scale(record)
    requested = (_requested_pole_distance(requested_distance)
                 if operation == "DISTANCE" else None)
    next_record = _plain(record)
    next_record["signature"] = None
    next_record["metrics"] = None
    next_payload = json.dumps(next_record, allow_nan=False)
    try:
        chain_names, (root, middle, end) = _evaluated_pole_bend_points(profile, obj, row)
        threshold = max(scale * 1e-5, 1e-8)
        current_ray = helper.matrix_world.translation - middle
        distance = current_ray.length
        minimum = max(scale * 0.1, threshold * 10.0)
        maximum = scale * 8.0
        tolerance=max(1e-7*scale,1e-9)
        if (not math.isfinite(distance) or distance < minimum-tolerance or distance > maximum+tolerance):
            raise ValueError(label + " Pole Target distance must remain from 0.1 to 8 body scales")
        current_ray.normalize()
        if operation == "DISTANCE":
            direction = current_ray
            distance = scale * requested
            comparison = current_ray
        else:
            axis = end - root
            if not math.isfinite(axis.length) or axis.length <= threshold:
                raise ValueError(label + " limb has no stable root-to-end axis for " + action)
            axis.normalize()
            bend = middle - root
            bend -= axis * bend.dot(axis)
            if not math.isfinite(bend.length) or bend.length <= threshold:
                raise ValueError(label + " limb is too straight to infer a stable bend direction")
            bend.normalize()
            direction = bend if operation == "ALIGN" else -bend
            comparison = direction
        expected = helper.matrix_world.copy()
        expected.translation = middle + direction * distance
        if any(not math.isfinite(float(expected[r][c]))
               for r in range(4) for c in range(4)):
            raise ValueError(label + " " + action + " produced an invalid helper transform")
        if (state.quadruped_payload != payload_before or
                state.quadruped_source is not source_before or
                not _target_topology_matches(state, topology)):
            raise ValueError("Quadruped state changed while evaluating " + action)
        helper.matrix_world = expected
        helper.scale = (1.0, 1.0, 1.0)
        if operation == "DISTANCE":
            item.pole_distance = requested
        topology_after = [dict(saved) for saved in topology]
        if operation == "DISTANCE":
            stored_distance = float(item.pole_distance)
            next(saved for saved in topology_after
                 if saved["name"] == label)["pole_distance"] = stored_distance
        bpy.context.view_layer.update()
        if _pole_edit_conflict(obj):
            raise ValueError("Another animation workflow started while editing the quadruped Pole Target")
        if state.quadruped_payload != payload_before:
            raise ValueError("Quadruped preview metadata changed while applying " + action)
        current_ad = obj.animation_data
        if (state.quadruped_source is not source_before or
                (current_ad.action if current_ad else None) is not action_before or
                (w._slot(current_ad) if current_ad else "") != slot_before):
            raise ValueError("Quadruped source binding changed while applying " + action)
        _validate(obj, scene, record)
        if not _target_topology_matches(state, topology_after):
            raise ValueError("Quadruped target collection changed while applying " + action)
        if (state.quadruped_spine_follow != follow_before or
                state.quadruped_neck_share != neck_before):
            raise ValueError("Quadruped spine settings changed while aligning Pole Target")
        if scene.tool_settings.use_keyframe_insert_auto != autokey_before:
            raise ValueError("Auto Key changed while applying " + action)
        for target_label, snapshot in snapshots.items():
            current = state.quadruped_targets.get(target_label)
            if (current is None or current.target is not snapshot["helper"] or
                    not p._owned(current.target, obj, record.get("token"))):
                raise ValueError("Quadruped " + action + " target changed: " + target_label)
            if not _helper_matches_asset_invariants(current.target, snapshot):
                raise ValueError("Quadruped helper settings changed while applying " + action + ": " + target_label)
            wanted = expected if target_label == label else snapshot["matrix"]
            error = max(abs(current.target.matrix_world[r][c] - wanted[r][c])
                        for r in range(4) for c in range(4))
            if not math.isfinite(error) or error > 1e-6:
                raise ValueError("Quadruped helper changed unexpectedly while applying " + action + ": " + target_label)
        if w.raw_pose(obj) != before_pose or _pose_settings(obj) != before_pose_settings:
            raise ValueError("Quadruped rig changed while applying " + action)
        for name, value in mode_raw_before.items():
            current = obj.pose.bones[name]["IK_FK"]
            if current != value or type(current) is not type(value):
                raise ValueError("Quadruped IK/FK mode changed while applying " + action)
        for name, value in pole_raw_before.items():
            current = obj.pose.bones[name]["pole_vector"]
            if current != value or type(current) is not type(value):
                raise ValueError("Quadruped Pole Vector mode changed while applying " + action)
        if not _object_transform_matches(obj, object_transform_before):
            raise ValueError("Quadruped rig object transform changed while applying " + action)
        state.quadruped_payload = next_payload
    except BaseException:
        foreign_workflow_started = _pole_edit_conflict(obj)
        try:
            if foreign_workflow_started:
                current = state.quadruped_targets.get(label)
                saved = snapshots.get(label)
                topology_row = next((value for value in topology
                                     if value["name"] == label), None)
                if (current is not None and saved is not None and topology_row is not None and
                        current.target is saved["helper"]):
                    _restore_helper_snapshot(current, saved)
                    current.pole_distance = topology_row["pole_distance"]
                    bpy.context.view_layer.update()
            else:
                if had_animation_data:
                    w.assign_action(obj, action_before, slot_before)
                elif obj.animation_data is not None:
                    obj.animation_data_clear()
                state.quadruped_source = source_before
                for name, value in mode_raw_before.items():
                    obj.pose.bones[name]["IK_FK"] = value
                _set_pole_modes(obj, pole_raw_before)
                if not _object_transform_matches(obj, object_transform_before):
                    _restore_object_transform(obj, object_transform_before)
                _restore_pose_settings(obj, before_pose, before_pose_settings)
                _restore_target_topology(state, topology, snapshots)
                state.quadruped_spine_follow = follow_before
                state.quadruped_neck_share = neck_before
                scene.tool_settings.use_keyframe_insert_auto = autokey_before
                bpy.context.view_layer.update()
        finally:
            if not foreign_workflow_started:
                state.quadruped_payload = payload_before
                state.status = status_before
        raise
    resulting_direction = (helper.matrix_world.translation - middle).normalized()
    angle = resulting_direction.angle(comparison)
    state.status = label + " " + action + " applied; solve again"
    return {"label": label, "limb": row["id"], "chain": list(chain_names),
            "distance": distance, "distance_body_scales": distance / scale,
            "direction_error_radians": angle, "operation": operation,
            "stored_distance_body_scales": (stored_distance
                                             if operation == "DISTANCE" else None),
            "source_unchanged": True}


def align_pole_to_current_bend(obj, scene, label):
    """Place one schema-4 pole helper on its current evaluated limb-bend ray."""
    return _edit_pole_target(obj, scene, label, "ALIGN")


def flip_pole_to_opposite_bend(obj, scene, label):
    """Place one schema-4 pole helper opposite its current evaluated bend ray."""
    return _edit_pole_target(obj, scene, label, "FLIP")


def set_pole_distance(obj, scene, label, distance_body_scales):
    """Set one schema-4 pole helper's current ray distance in body-scale units."""
    return _edit_pole_target(obj, scene, label, "DISTANCE", distance_body_scales)


def reset_target(obj, scene, label):
    """Restore one owned helper to its verified preview-start world transform."""
    if bpy.context.screen and bpy.context.screen.is_animation_playing:
        raise ValueError("Stop playback before resetting a quadruped target")
    record = _read(obj)
    _, _, limbs = _validate(obj, scene, record)
    if label not in _targets(record):
        raise ValueError("Unknown quadruped target: " + label)
    item = obj.b4ml.quadruped_targets.get(label)
    if item is None or not p._owned(item.target, obj, record.get("token")):
        raise ValueError("Quadruped pose target is missing or replaced: " + label)
    _validate_resettable_target(item, label)
    expected = _saved_target_matrix(record, label)
    helper = item.target
    before_mode = helper.rotation_mode
    before_matrix = helper.matrix_world.copy()
    helper_scale_before = tuple(helper.scale)
    before_pose = w.raw_pose(obj)
    before_pose_settings = {
        bone.name: {
            "mode": bone.rotation_mode,
            "lock_location": tuple(bone.lock_location),
            "lock_rotation": tuple(bone.lock_rotation),
            "lock_scale": tuple(bone.lock_scale),
            "lock_rotation_w": bone.lock_rotation_w,
            "lock_rotations_4d": bone.lock_rotations_4d,
        }
        for bone in obj.pose.bones
    }
    state = obj.b4ml
    payload_before = state.quadruped_payload
    status_before = state.status
    enabled_before = item.enabled
    orientation_before = item.use_orientation
    helper_locks_before = {
        "location": tuple(helper.lock_location),
        "rotation": tuple(helper.lock_rotation),
        "scale": tuple(helper.lock_scale),
        "rotation_w": helper.lock_rotation_w,
        "rotations_4d": helper.lock_rotations_4d,
    }
    owner_before = helper.get("b4ml_owner")
    session_before = helper.get("b4ml_session")
    helper_had_animation_data = helper.animation_data is not None
    delta_location_before = tuple(helper.delta_location)
    delta_euler_before = tuple(helper.delta_rotation_euler)
    delta_quaternion_before = tuple(helper.delta_rotation_quaternion)
    delta_scale_before = tuple(helper.delta_scale)
    ad = obj.animation_data
    had_animation_data = ad is not None
    action_before = ad.action if ad else None
    slot_before = w._slot(ad) if ad else ""
    mode_raw_before = {row["property_bone"]: obj.pose.bones[row["property_bone"]]["IK_FK"]
                       for row in limbs}
    modes_before = mode_values(obj, limbs)
    pole_mode_raw_before = ({row["property_bone"]:
                             obj.pose.bones[row["property_bone"]]["pole_vector"]
                             for row in limbs} if record.get("schema") == 4 else None)
    pole_modes_before = pole_mode_values(obj, limbs) if record.get("schema") == 4 else None
    next_record = _plain(record)
    next_record["signature"] = None
    next_record["metrics"] = None
    next_payload = json.dumps(next_record, allow_nan=False)
    try:
        helper.rotation_mode = "QUATERNION"
        helper.matrix_world = expected
        helper.scale = (1.0, 1.0, 1.0)
        bpy.context.view_layer.update()
        current_item = state.quadruped_targets.get(label)
        if current_item is None or current_item.target is not helper:
            raise ValueError("Quadruped pose target changed while resetting: " + label)
        if not p._owned(helper, obj, record.get("token")):
            raise ValueError("Quadruped target ownership changed while resetting: " + label)
        if state.quadruped_payload != payload_before:
            raise ValueError("Quadruped preview metadata changed while resetting: " + label)
        if current_item.enabled != enabled_before or current_item.use_orientation != orientation_before:
            raise ValueError("Quadruped target options changed while resetting: " + label)
        _validate_resettable_target(current_item, label)
        if label == "Head":
            _validate_head_target(current_item, record)
        elif label in POLE_TARGETS:
            _validate_pole_target(current_item, label, record)
        helper_locks = {
            "location": tuple(helper.lock_location),
            "rotation": tuple(helper.lock_rotation),
            "scale": tuple(helper.lock_scale),
            "rotation_w": helper.lock_rotation_w,
            "rotations_4d": helper.lock_rotations_4d,
        }
        if helper_locks != helper_locks_before:
            raise ValueError("Quadruped target lock settings changed while resetting: " + label)
        position_error = (helper.matrix_world.translation - expected.translation).length
        rotation_error = helper.matrix_world.to_quaternion().rotation_difference(
            expected.to_quaternion()).angle
        rotation_error = min(rotation_error, abs(2.0 * math.pi - rotation_error))
        scale_error = max(abs(value - 1.0) for value in helper.scale)
        if position_error > 1e-7 or rotation_error > 1e-7 or scale_error > 1e-7:
            raise ValueError(label + " helper could not be restored to its preview-start transform; "
                             f"position {position_error:.6g}, rotation {rotation_error:.6g}, "
                             f"scale {scale_error:.6g}")
        current_ad = obj.animation_data
        if ((current_ad.action if current_ad else None) is not action_before or
                (w._slot(current_ad) if current_ad else "") != slot_before):
            raise ValueError("Quadruped source action changed while resetting target: " + label)
        if mode_values(obj, limbs) != modes_before:
            raise ValueError("Quadruped IK/FK modes changed while resetting target: " + label)
        if pole_modes_before is not None and pole_mode_values(obj, limbs) != pole_modes_before:
            raise ValueError("Quadruped Pole Vector modes changed while resetting target: " + label)
        pose_settings = {
            bone.name: {
                "mode": bone.rotation_mode,
                "lock_location": tuple(bone.lock_location),
                "lock_rotation": tuple(bone.lock_rotation),
                "lock_scale": tuple(bone.lock_scale),
                "lock_rotation_w": bone.lock_rotation_w,
                "lock_rotations_4d": bone.lock_rotations_4d,
            }
            for bone in obj.pose.bones
        }
        if w.raw_pose(obj) != before_pose or pose_settings != before_pose_settings:
            raise ValueError("Quadruped rig changed while resetting target: " + label)
        state.quadruped_payload = next_payload
    except BaseException:
        try:
            if had_animation_data:
                w.assign_action(obj, action_before, slot_before)
            elif obj.animation_data is not None:
                obj.animation_data_clear()
            for name, value in mode_raw_before.items():
                obj.pose.bones[name]["IK_FK"] = value
            if pole_mode_raw_before is not None:
                _set_pole_modes(obj, pole_mode_raw_before)
            for name, values in before_pose_settings.items():
                bone = obj.pose.bones.get(name)
                if bone is not None:
                    bone.rotation_mode = values["mode"]
            w.restore_pose(obj, before_pose)
            for name, values in before_pose_settings.items():
                bone = obj.pose.bones.get(name)
                if bone is not None:
                    bone.lock_location = values["lock_location"]
                    bone.lock_rotation = values["lock_rotation"]
                    bone.lock_scale = values["lock_scale"]
                    bone.lock_rotation_w = values["lock_rotation_w"]
                    bone.lock_rotations_4d = values["lock_rotations_4d"]
            current_item = state.quadruped_targets.get(label)
            if current_item is not None:
                current_item.target = helper
                current_item.enabled = enabled_before
                current_item.use_orientation = orientation_before
            helper.parent = None
            while helper.constraints:
                helper.constraints.remove(helper.constraints[-1])
            if helper.animation_data is not None:
                helper.animation_data_clear()
            if helper_had_animation_data:
                helper.animation_data_create()
            helper["b4ml_owner"] = owner_before
            helper["b4ml_session"] = session_before
            helper.delta_location = delta_location_before
            helper.delta_rotation_euler = delta_euler_before
            helper.delta_rotation_quaternion = delta_quaternion_before
            helper.delta_scale = delta_scale_before
            helper.lock_location = helper_locks_before["location"]
            helper.lock_rotation = helper_locks_before["rotation"]
            helper.lock_scale = helper_locks_before["scale"]
            helper.lock_rotation_w = helper_locks_before["rotation_w"]
            helper.lock_rotations_4d = helper_locks_before["rotations_4d"]
            helper.rotation_mode = before_mode
            helper.matrix_world = before_matrix
            helper.scale = helper_scale_before
            bpy.context.view_layer.update()
        finally:
            state.quadruped_payload = payload_before
            state.status = status_before
        raise
    state.status = label + " helper reset to preview start; solve again if the request changed"
    return {"label": label, "position_error": position_error,
            "rotation_error": rotation_error, "source_unchanged": True}


def mirror_targets(obj, scene, direction):
    """Mirror edited paw and optional pole helpers through the saved body plane."""
    if direction not in {"LEFT_TO_RIGHT", "RIGHT_TO_LEFT"}:
        raise ValueError("Unknown quadruped mirror direction")
    if bpy.context.screen and bpy.context.screen.is_animation_playing:
        raise ValueError("Stop playback before mirroring quadruped targets")
    record = _read(obj)
    _, _, limbs = _validate(obj, scene, record)
    state = obj.b4ml
    pairs = (MIRROR_PAIRS if direction == "LEFT_TO_RIGHT" else
             tuple((right, left) for left, right in MIRROR_PAIRS))
    if record.get("schema") == 4:
        pole_pairs = tuple((left.replace("Paw", "Pole"), right.replace("Paw", "Pole"))
                           for left, right in pairs)
        pairs = pairs + pole_pairs
    reflection = _mirror_reflection(record)
    topology = _target_topology_snapshot(state)
    if [row["name"] for row in topology] != list(_targets(record)):
        raise ValueError("Quadruped mirror target collection topology is invalid")
    snapshots = {}
    for label in _targets(record):
        item = state.quadruped_targets.get(label)
        if item is None or not p._owned(item.target, obj, record.get("token")):
            raise ValueError("Quadruped mirror target is missing or replaced: " + label)
        _validate_resettable_target(item, label)
        if label == "Head":
            _validate_head_target(item, record)
        elif label in POLE_TARGETS:
            _validate_pole_target(item, label, record)
        snapshots[label] = _helper_snapshot(item)
    expected = {}
    for source_label, destination_label in pairs:
        source_start = _saved_target_matrix(record, source_label)
        destination_start = _saved_target_matrix(record, destination_label)
        expected[destination_label] = _mirrored_target_matrix(
            snapshots[source_label]["matrix"], source_start, destination_start, reflection,
            position_only=destination_label in POLE_TARGETS)
    payload_before = state.quadruped_payload
    status_before = state.status
    before_pose = w.raw_pose(obj)
    before_pose_settings = _pose_settings(obj)
    ad = obj.animation_data
    had_animation_data = ad is not None
    action_before = ad.action if ad else None
    slot_before = w._slot(ad) if ad else ""
    source_before = state.quadruped_source
    mode_raw_before = {row["property_bone"]: obj.pose.bones[row["property_bone"]]["IK_FK"]
                       for row in limbs}
    pole_raw_before = ({row["property_bone"]:
                        obj.pose.bones[row["property_bone"]]["pole_vector"]
                        for row in limbs} if record.get("schema") == 4 else None)
    next_record = _plain(record)
    next_record["signature"] = None
    next_record["metrics"] = None
    next_payload = json.dumps(next_record, allow_nan=False)
    try:
        for label, matrix in expected.items():
            helper = snapshots[label]["helper"]
            helper.rotation_mode = "QUATERNION"
            helper.matrix_world = matrix
            helper.scale = (1.0, 1.0, 1.0)
        bpy.context.view_layer.update()
        if state.quadruped_payload != payload_before:
            raise ValueError("Quadruped preview metadata changed while mirroring targets")
        current_ad = obj.animation_data
        if (state.quadruped_source is not source_before or
                (current_ad.action if current_ad else None) is not action_before or
                (w._slot(current_ad) if current_ad else "") != slot_before):
            raise ValueError("Quadruped source binding changed while mirroring targets")
        _validate(obj, scene, record)
        if not _target_topology_matches(state, topology):
            raise ValueError("Quadruped target collection changed while mirroring targets")
        for label, snapshot in snapshots.items():
            item = state.quadruped_targets.get(label)
            helper = snapshot["helper"]
            if item is None or item.target is not helper or not p._owned(
                    helper, obj, record.get("token")):
                raise ValueError("Quadruped mirror target changed while mirroring: " + label)
            if item.enabled != snapshot["enabled"] or item.use_orientation != snapshot["orientation"]:
                raise ValueError("Quadruped target options changed while mirroring: " + label)
            _validate_resettable_target(item, label)
            if label == "Head":
                _validate_head_target(item, record)
            elif label in POLE_TARGETS:
                _validate_pole_target(item, label, record)
            locks = (tuple(helper.lock_location), tuple(helper.lock_rotation),
                     tuple(helper.lock_scale), helper.lock_rotation_w,
                     helper.lock_rotations_4d)
            if locks != snapshot["locks"]:
                raise ValueError("Quadruped target lock settings changed while mirroring: " + label)
            wanted = expected.get(label, snapshot["matrix"])
            error = max(abs(helper.matrix_world[row][column] - wanted[row][column])
                        for row in range(4) for column in range(4))
            if error > 1e-6:
                raise ValueError("Quadruped helper changed unexpectedly while mirroring: " + label)
        if w.raw_pose(obj) != before_pose or _pose_settings(obj) != before_pose_settings:
            raise ValueError("Quadruped rig changed while mirroring targets")
        state.quadruped_payload = next_payload
    except BaseException:
        try:
            if had_animation_data:
                w.assign_action(obj, action_before, slot_before)
            elif obj.animation_data is not None:
                obj.animation_data_clear()
            state.quadruped_source = source_before
            for name, value in mode_raw_before.items():
                obj.pose.bones[name]["IK_FK"] = value
            if pole_raw_before is not None:
                _set_pole_modes(obj, pole_raw_before)
            _restore_pose_settings(obj, before_pose, before_pose_settings)
            _restore_target_topology(state, topology, snapshots)
            bpy.context.view_layer.update()
        finally:
            state.quadruped_payload = payload_before
            state.status = status_before
        raise
    state.status = ("Mirrored left quadruped targets to right" if direction == "LEFT_TO_RIGHT"
                    else "Mirrored right quadruped targets to left") + "; solve again"
    return {"direction": direction, "targets": len(expected),
            "paws": 2, "poles": 2 if record.get("schema") == 4 else 0,
            "source_unchanged": True}


def _asset_vector(value, message, limit=8.0):
    if (not isinstance(value, list) or len(value) != 3 or
            any(isinstance(component, bool) or not isinstance(component, (int, float)) or
                not math.isfinite(float(component)) for component in value)):
        raise ValueError(message)
    vector = Vector(value)
    if vector.length > limit:
        raise ValueError(message)
    return vector


def _asset_quaternion(value, message):
    if (not isinstance(value, list) or len(value) != 4 or
            any(isinstance(component, bool) or not isinstance(component, (int, float)) or
                not math.isfinite(float(component)) for component in value)):
        raise ValueError(message)
    quaternion = Quaternion(value)
    if quaternion.magnitude <= 1e-12:
        raise ValueError(message)
    quaternion.normalize()
    return quaternion


def _preview_scale(record):
    raw_scale = record.get("scale")
    if (isinstance(raw_scale, bool) or not isinstance(raw_scale, (int, float)) or
            not math.isfinite(float(raw_scale)) or float(raw_scale) <= 1e-8):
        raise ValueError("Invalid quadruped preview scale")
    return float(raw_scale)


def _quadruped_asset_frame(record):
    frame = _saved_target_matrix(record, "Body").to_3x3()
    axes = [Vector((frame[0][column], frame[1][column], frame[2][column]))
            for column in range(3)]
    if (any(abs(axis.length - 1.0) > 1e-6 for axis in axes) or
            any(abs(axes[left].dot(axes[right])) > 1e-6
                for left, right in ((0, 1), (0, 2), (1, 2))) or
            frame.determinant() <= 0.0):
        raise ValueError("Invalid saved quadruped body frame")
    return frame


def _read_pose_asset(scene):
    text = scene.get(POSE_ASSET_KEY)
    if not isinstance(text, str) or not text or len(text) > POSE_ASSET_MAX_CHARS:
        raise ValueError("Save a valid quadruped target pose in this scene first")
    try:
        asset = json.loads(text)
    except (TypeError, ValueError, RecursionError) as exc:
        raise ValueError("Saved quadruped target pose is invalid") from exc
    keys = {"schema", "representation", "source_profile", "use_poles", "spine_follow",
            "neck_share", "targets", "learned", "verified_solve"}
    if (not isinstance(asset, dict) or set(asset) != keys or asset.get("schema") != 1 or
            asset.get("representation") != "semantic_quadruped_target_delta_body_v1" or
            not isinstance(asset.get("source_profile"), str) or
            not asset["source_profile"].strip() or len(asset["source_profile"]) > 128 or
            not isinstance(asset.get("use_poles"), bool) or
            not isinstance(asset.get("targets"), list) or asset.get("learned") is not False or
            asset.get("verified_solve") is not True):
        raise ValueError("Saved quadruped target pose is invalid")
    for field in ("spine_follow", "neck_share"):
        value = asset.get(field)
        if (isinstance(value, bool) or not isinstance(value, (int, float)) or
                not math.isfinite(float(value)) or not 0.0 <= float(value) <= 1.0):
            raise ValueError("Saved quadruped target pose has invalid spine settings")
    expected_labels = list(CURRENT_TARGETS if asset["use_poles"] else TARGETS)
    if (len(asset["targets"]) != len(expected_labels) or
            [row.get("label") if isinstance(row, dict) else None
             for row in asset["targets"]] != expected_labels):
        raise ValueError("Saved quadruped target pose has an incompatible target set")
    return asset


def capture_pose_asset(obj, scene):
    """Save one verified quadruped target request in body-relative coordinates."""
    state = obj.b4ml
    record = _read(obj)
    if record.get("schema") not in {3, 4}:
        raise ValueError("Restart this legacy preview before saving a quadruped pose asset")
    _, _, signature, _, _ = _request(obj, scene, record)
    if record.get("signature") is None or signature != record["signature"]:
        raise ValueError("Solve the current quadruped targets before saving a pose asset")
    frame = _quadruped_asset_frame(record)
    scale = _preview_scale(record)
    rows = []
    for label in _targets(record):
        item = state.quadruped_targets.get(label)
        if item is None or not p._owned(item.target, obj, record.get("token")):
            raise ValueError("Quadruped pose target is missing or replaced: " + label)
        _validate_resettable_target(item, label)
        if label == "Head":
            _validate_head_target(item, record)
        elif label in POLE_TARGETS:
            _validate_pole_target(item, label, record)
        start = _saved_target_matrix(record, label)
        current = _proper_helper_matrix(item.target.matrix_world, label)
        delta = frame.transposed() @ (current.translation - start.translation) / scale
        delta = _asset_vector(
            list(delta),
            "Quadruped target pose exceeds the supported body-relative range: " + label)
        row = {"label": label, "position_delta": list(delta)}
        if label not in POLE_TARGETS:
            relative = (frame.transposed() @ current.to_3x3() @
                        start.to_3x3().transposed() @ frame)
            quaternion = relative.to_quaternion().normalized()
            if quaternion.w < 0.0:
                quaternion.negate()
            quaternion = _asset_quaternion(
                list(quaternion),
                "Quadruped target pose contains an invalid rotation: " + label)
            row.update({"orientation_enabled": bool(item.use_orientation),
                        "orientation_delta": list(quaternion)})
        rows.append(row)
    asset = {
        "schema": 1,
        "representation": "semantic_quadruped_target_delta_body_v1",
        "source_profile": str(record["profile"])[:128],
        "use_poles": record.get("schema") == 4,
        "spine_follow": float(state.quadruped_spine_follow),
        "neck_share": float(state.quadruped_neck_share),
        "targets": rows,
        "learned": False,
        "verified_solve": True,
    }
    text = json.dumps(asset, allow_nan=False, separators=(",", ":"))
    if len(text) > POSE_ASSET_MAX_CHARS:
        raise ValueError("Quadruped target pose exceeds the serialized size limit")
    had_asset = POSE_ASSET_KEY in scene
    asset_before = scene.get(POSE_ASSET_KEY)
    status_before = state.status
    try:
        scene[POSE_ASSET_KEY] = text
    except BaseException:
        if had_asset:
            scene[POSE_ASSET_KEY] = asset_before
        elif POSE_ASSET_KEY in scene:
            del scene[POSE_ASSET_KEY]
        state.status = status_before
        raise
    state.status = "Saved verified quadruped target pose for cross-rig reuse"
    return asset


def apply_pose_asset(obj, scene):
    """Apply the scene quadruped pose asset without changing the rig pose."""
    state = obj.b4ml
    asset_text_before = scene.get(POSE_ASSET_KEY)
    asset = _read_pose_asset(scene)
    if scene.get(POSE_ASSET_KEY) != asset_text_before:
        raise ValueError("Quadruped pose asset changed while preparing Apply Pose")
    record = _read(obj)
    if record.get("schema") not in {3, 4}:
        raise ValueError("Restart this legacy preview before applying a quadruped pose asset")
    if asset["use_poles"] != (record.get("schema") == 4):
        raise ValueError("Quadruped pose asset Pole Target mode does not match this preview")
    _, _, limbs = _validate(obj, scene, record)
    frame = _quadruped_asset_frame(record)
    scale = _preview_scale(record)
    topology = _target_topology_snapshot(state)
    if [row["name"] for row in topology] != list(_targets(record)):
        raise ValueError("Quadruped pose asset target collection topology is invalid")
    snapshots = {}
    expected = {}
    topology_after = [dict(row) for row in topology]
    rows = {row["label"]: row for row in asset["targets"]}
    for label in _targets(record):
        item = state.quadruped_targets.get(label)
        if item is None or not p._owned(item.target, obj, record.get("token")):
            raise ValueError("Quadruped pose target is missing or replaced: " + label)
        _validate_resettable_target(item, label)
        if label == "Head":
            _validate_head_target(item, record)
        elif label in POLE_TARGETS:
            _validate_pole_target(item, label, record)
        snapshots[label] = _helper_snapshot(item)
        row = rows[label]
        required = ({"label", "position_delta"} if label in POLE_TARGETS else
                    {"label", "position_delta", "orientation_enabled", "orientation_delta"})
        if set(row) != required:
            raise ValueError("Saved quadruped target pose contains invalid " + label + " settings")
        delta = _asset_vector(row["position_delta"],
                              "Saved quadruped target pose contains invalid " + label + " position")
        if label == "Head" and delta.length > 1e-7:
            raise ValueError("Saved quadruped Head position must remain fixed")
        start = _saved_target_matrix(record, label)
        try:
            location = start.translation + frame @ delta * scale
        except OverflowError as exc:
            raise ValueError("Saved quadruped target pose exceeds the supported world range: " +
                             label) from exc
        if label in POLE_TARGETS:
            rotation = start.to_quaternion()
            orientation_enabled = False
        else:
            if not isinstance(row["orientation_enabled"], bool):
                raise ValueError("Saved quadruped target pose contains invalid " + label + " rotation")
            relative = _asset_quaternion(
                row["orientation_delta"],
                "Saved quadruped target pose contains invalid " + label + " rotation")
            rotation = (frame @ relative.to_matrix() @ frame.transposed() @
                        start.to_3x3()).to_quaternion().normalized()
            orientation_enabled = row["orientation_enabled"]
        try:
            matrix = _proper_helper_matrix(
                Matrix.LocRotScale(location, rotation, Vector((1.0, 1.0, 1.0))),
                "pose asset " + label)
        except OverflowError as exc:
            raise ValueError("Saved quadruped target pose exceeds the supported world range: " +
                             label) from exc
        expected[label] = (matrix, orientation_enabled)
        if label not in POLE_TARGETS:
            next(row for row in topology_after if row["name"] == label)["orientation"] = orientation_enabled
    payload_before = state.quadruped_payload
    status_before = state.status
    follow_before = state.quadruped_spine_follow
    neck_before = state.quadruped_neck_share
    before_pose = w.raw_pose(obj)
    before_pose_settings = _pose_settings(obj)
    ad = obj.animation_data
    had_animation_data = ad is not None
    action_before = ad.action if ad else None
    slot_before = w._slot(ad) if ad else ""
    source_before = state.quadruped_source
    mode_raw_before = {row["property_bone"]: obj.pose.bones[row["property_bone"]]["IK_FK"]
                       for row in limbs}
    pole_raw_before = ({row["property_bone"]:
                        obj.pose.bones[row["property_bone"]]["pole_vector"]
                        for row in limbs} if record.get("schema") == 4 else None)
    next_record = _plain(record)
    next_record["signature"] = None
    next_record["metrics"] = None
    next_payload = json.dumps(next_record, allow_nan=False)
    try:
        for label, (matrix, orientation_enabled) in expected.items():
            item = state.quadruped_targets[label]
            item.target.rotation_mode = "QUATERNION"
            item.target.matrix_world = matrix
            item.target.scale = (1.0, 1.0, 1.0)
            if label not in POLE_TARGETS:
                item.use_orientation = orientation_enabled
        state.quadruped_spine_follow = float(asset["spine_follow"])
        state.quadruped_neck_share = float(asset["neck_share"])
        bpy.context.view_layer.update()
        if (POSE_ASSET_KEY not in scene or
                scene.get(POSE_ASSET_KEY) != asset_text_before):
            raise ValueError("Quadruped pose asset changed while applying pose asset")
        if state.quadruped_payload != payload_before:
            raise ValueError("Quadruped preview metadata changed while applying pose asset")
        current_ad = obj.animation_data
        if (state.quadruped_source is not source_before or
                (current_ad.action if current_ad else None) is not action_before or
                (w._slot(current_ad) if current_ad else "") != slot_before):
            raise ValueError("Quadruped source binding changed while applying pose asset")
        _validate(obj, scene, record)
        if not _target_topology_matches(state, topology_after):
            raise ValueError("Quadruped target collection changed while applying pose asset")
        applied_follow = float(state.quadruped_spine_follow)
        applied_neck = float(state.quadruped_neck_share)
        if (not math.isfinite(applied_follow) or not math.isfinite(applied_neck) or
                abs(applied_follow - float(asset["spine_follow"])) > 1e-7 or
                abs(applied_neck - float(asset["neck_share"])) > 1e-7):
            raise ValueError("Quadruped spine settings changed while applying pose asset")
        for label, snapshot in snapshots.items():
            item = state.quadruped_targets.get(label)
            matrix, orientation_enabled = expected[label]
            if item is None or item.target is not snapshot["helper"]:
                raise ValueError("Quadruped target changed while applying pose asset: " + label)
            if not p._owned(item.target, obj, record.get("token")):
                raise ValueError("Quadruped target ownership changed while applying pose asset: " + label)
            _validate_resettable_target(item, label)
            if label == "Head":
                _validate_head_target(item, record)
            elif label in POLE_TARGETS:
                _validate_pole_target(item, label, record)
            current_matrix = _proper_helper_matrix(item.target.matrix_world, label)
            if not _helper_matches_asset_invariants(item.target, snapshot):
                raise ValueError("Quadruped helper settings changed while applying pose asset: " + label)
            if ((label not in POLE_TARGETS and item.use_orientation != orientation_enabled) or
                    item.enabled != snapshot["enabled"]):
                raise ValueError("Quadruped target options changed while applying pose asset: " + label)
            error = max(abs(current_matrix[row][column] - matrix[row][column])
                        for row in range(4) for column in range(4))
            if not math.isfinite(error) or error > 1e-6:
                raise ValueError("Quadruped helper could not apply pose asset: " + label)
        if w.raw_pose(obj) != before_pose or _pose_settings(obj) != before_pose_settings:
            raise ValueError("Quadruped rig changed while applying pose asset")
        state.quadruped_payload = next_payload
    except BaseException:
        try:
            if had_animation_data:
                w.assign_action(obj, action_before, slot_before)
            elif obj.animation_data is not None:
                obj.animation_data_clear()
            state.quadruped_source = source_before
            for name, value in mode_raw_before.items():
                obj.pose.bones[name]["IK_FK"] = value
            if pole_raw_before is not None:
                _set_pole_modes(obj, pole_raw_before)
            _restore_pose_settings(obj, before_pose, before_pose_settings)
            _restore_target_topology(state, topology, snapshots)
            state.quadruped_spine_follow = follow_before
            state.quadruped_neck_share = neck_before
            scene[POSE_ASSET_KEY] = asset_text_before
            bpy.context.view_layer.update()
        finally:
            try:
                scene[POSE_ASSET_KEY] = asset_text_before
            finally:
                state.quadruped_payload = payload_before
                state.status = status_before
        raise
    state.status = "Applied quadruped target pose from " + asset["source_profile"] + "; solve before keeping"
    return {"schema": 1, "source_profile": asset["source_profile"],
            "target_profile": record["profile"], "targets": len(expected),
            "cross_rig": asset["source_profile"] != record["profile"],
            "use_poles": asset["use_poles"]}


def begin(obj, scene):
    state = obj.b4ml
    if state.quadruped_payload:
        raise ValueError("Resolve the existing quadruped pose preview first")
    if state.posing_payload or state.body_payload or state.candidate_action:
        raise ValueError("Keep or cancel the active preview first")
    if bpy.context.screen and bpy.context.screen.is_animation_playing:
        raise ValueError("Stop playback before quadruped posing")
    w._reject_nla(obj)
    profile, body, limbs = binding(obj)
    p._check_space(obj)
    head = _head_control(profile, obj)
    spine_controls = _spine_controls(profile, obj)
    modes = _require_ik(obj, limbs)
    use_poles = bool(state.quadruped_use_poles)
    pole_modes = _require_pole_vectors(obj, limbs) if use_poles else None
    follow = float(state.quadruped_spine_follow)
    neck_share = float(state.quadruped_neck_share)
    if not all(math.isfinite(value) and 0.0 <= value <= 1.0
               for value in (follow, neck_share)):
        raise ValueError("Quadruped spine settings must be finite values from zero to one")
    rotate = [head]
    weights = _spine_weights(follow, neck_share)
    rotate.extend(spine_controls[role] for role, amount in weights.items() if amount > 0.0)
    _check_writable(obj, body, limbs, rotate,
                    (row["pole"] for row in limbs) if use_poles else ())
    source = w.raw_pose(obj, profile.controls)
    token = uuid.uuid4().hex
    ad = obj.animation_data
    origins = {"Body": list(_world_point(obj, obj.pose.bones[body].matrix.translation)),
               "Head": list(_world_point(obj, obj.pose.bones[head].matrix.translation))}
    orientations = {"Body": list((obj.matrix_world @ obj.pose.bones[body].matrix).to_quaternion()),
                    "Head": list((obj.matrix_world @ obj.pose.bones[head].matrix).to_quaternion())}
    for row in limbs:
        origins[row["label"]] = list(_world_point(obj, obj.pose.bones[row["joint"]].tail))
        orientations[row["label"]] = list(
            (obj.matrix_world @ obj.pose.bones[row["ik"]].matrix).to_quaternion())
        if use_poles:
            origins[row["pole_label"]] = list(
                _world_point(obj, obj.pose.bones[row["pole"]].matrix.translation))
            orientations[row["pole_label"]] = list(
                (obj.matrix_world @ obj.pose.bones[row["pole"]].matrix).to_quaternion())
    distances = [(Vector(point) - Vector(origins["Body"])).length
                 for label, point in origins.items() if label != "Body"]
    scale = max([1e-6, *distances])
    record = {"schema": 4 if use_poles else 3, "token": token, "profile": profile.name,
              "frame": list(_frame(scene)), "world": _matrix(obj.matrix_world),
              "rest": w._rest_signature(obj), "source": source,
              "preview": source, "modes": modes, "origins": origins,
              "orientations": orientations,
              "spine_controls": spine_controls,
              "signature": None, "metrics": None, "scale": scale,
              "slot": w._slot(ad) if ad else ""}
    if use_poles:
        record["pole_controls"] = {row["id"]: row["pole"] for row in limbs}
        record["pole_modes"] = pole_modes
    state.quadruped_source = ad.action if ad else None
    state.quadruped_payload = json.dumps(record, allow_nan=False)
    try:
        state.quadruped_targets.clear()
        targets = CURRENT_TARGETS if use_poles else TARGETS
        for label in targets:
            item = state.quadruped_targets.add()
            item.name = label
            item.enabled = True
            item.target = p._helper(obj, scene, token, "Quadruped " + label,
                                    Vector(origins[label]), scale * (0.045 if label in {"Body", "Head"} else 0.035))
            item.use_orientation = label == "Head"
            item.target.rotation_mode = "QUATERNION"
            item.target.rotation_quaternion = Quaternion(orientations[label])
            item.target.empty_display_type = "ARROWS" if label in {"Body", "Head"} else "CIRCLE"
            if label == "Head":
                item.target.lock_location = (True, True, True)
            elif label in POLE_TARGETS:
                item.target.lock_rotation = (True, True, True)
        bpy.context.view_layer.update()
        # Bind recovery to the transforms the host actually stored on the helpers.
        # Some generated quadruped pole controls carry axes that Blender normalizes
        # when their quaternion is assigned, especially on the horse profile.
        for item in state.quadruped_targets:
            record["origins"][item.name] = list(item.target.matrix_world.translation)
            orientation = item.target.matrix_world.to_quaternion().normalized()
            if orientation.w < 0.0:
                orientation.negate()
            record["orientations"][item.name] = list(orientation)
        state.quadruped_payload = json.dumps(record, allow_nan=False)
        state.status = ("Move the body, paw, and pole targets, rotate Head, then solve the quadruped pose"
                        if use_poles else
                        "Move the body and four paw targets, rotate Head, then solve the quadruped pose")
    except Exception:
        _cleanup(obj, record, restore=True)
        raise
    return len(targets)


def _request(obj, scene, record):
    bpy.context.view_layer.update()
    profile, _, limbs = _validate(obj, scene, record)
    head = _head_control(profile, obj)
    spine_controls = (_spine_controls(profile, obj) if record.get("schema") in {3, 4} else {})
    points = {}
    orientations = {}
    intent = []
    rotate = []
    for label in _targets(record):
        item = obj.b4ml.quadruped_targets[label]
        point = Vector(item.target.matrix_world.translation)
        if not all(math.isfinite(value) for value in point):
            raise ValueError("Invalid quadruped target position: " + label)
        if label != "Head":
            points[label] = point
        orientation = None
        if item.use_orientation:
            quat = item.target.matrix_world.to_quaternion().normalized()
            if not all(math.isfinite(value) for value in quat):
                raise ValueError("Invalid quadruped target rotation: " + label)
            if quat.w < 0:
                quat.negate()
            orientation = list(quat)
            orientations[label] = quat
            rotate.append("torso" if label == "Body" else head if label == "Head" else
                          next(row["ik"] for row in limbs if row["label"] == label))
        intent.append([label, list(point), bool(item.use_orientation), orientation])
    follow = float(obj.b4ml.quadruped_spine_follow) if record.get("schema") in {3, 4} else 0.0
    neck_share = float(obj.b4ml.quadruped_neck_share) if record.get("schema") in {3, 4} else 0.0
    if not all(math.isfinite(value) and 0.0 <= value <= 1.0
               for value in (follow, neck_share)):
        raise ValueError("Quadruped spine settings must be finite values from zero to one")
    distribution = {"active": bool("Head" in orientations and follow > 0.0),
                    "follow": follow, "neck_share": neck_share,
                    "controls": spine_controls}
    if distribution["active"]:
        weights = _spine_weights(follow, neck_share)
        rotate.extend(spine_controls[role] for role, amount in weights.items() if amount > 0.0)
    move = [row["pole"] for row in limbs] if record.get("schema") == 4 else []
    _check_writable(obj, "torso", limbs, rotate, move)
    intent.append(["Spine Follow", follow, neck_share])
    return points, orientations, _plain(intent), limbs, distribution


def _translate_control(obj, name, world_delta):
    matrix = obj.pose.bones[name].matrix.copy()
    matrix.translation += obj.matrix_world.inverted().to_3x3() @ world_delta
    obj.pose.bones[name].matrix = matrix
    obj.update_tag(refresh={"OBJECT"})
    bpy.context.view_layer.update()


def _write_world_rotation(obj, name, world_rotation):
    pose_rotation = obj.matrix_world.to_quaternion().inverted() @ world_rotation
    matrix = pose_rotation.to_matrix().to_4x4()
    matrix.translation = obj.pose.bones[name].matrix.translation
    p._write_rotation(obj, name, matrix)


def _world_rotation(obj, name):
    return (obj.matrix_world @ obj.pose.bones[name].matrix).to_quaternion().normalized()


def _rotation_error(first, second):
    angle = first.rotation_difference(second).angle
    return min(angle, abs(2.0*math.pi-angle))


def _distribute_head_rotation(obj, head, target, distribution):
    if not distribution["active"]:
        return {}, 0.0
    current_head = _world_rotation(obj, head)
    delta = (target @ current_head.inverted()).normalized()
    if delta.w < 0:
        delta.negate()
    controls = distribution["controls"]
    weights = _spine_weights(distribution["follow"], distribution["neck_share"])
    desired = {}
    for role in ("chest", "neck"):
        amount = weights[role]
        current = _world_rotation(obj, controls[role])
        turn = Quaternion().slerp(delta, amount)
        wanted = (turn @ current).normalized()
        desired[role] = wanted
        if amount > 0.0:
            _write_world_rotation(obj, controls[role], wanted)
    return desired, delta.angle


def solve(obj, scene):
    record = _read(obj)
    profile, body, limbs = _validate(obj, scene, record)
    points, orientations, signature, limbs, distribution = _request(obj, scene, record)
    previous = w.raw_pose(obj, profile.controls)
    try:
        w.restore_pose(obj, record["source"])
        bpy.context.view_layer.update()
        body_origin = Vector(record["origins"]["Body"])
        _translate_control(obj, body, points["Body"] - body_origin)
        if "Body" in orientations:
            _write_world_rotation(obj, body, orientations["Body"])
        distributed = {}
        distributed_angle = 0.0
        if "Head" in orientations:
            head = _head_control(profile, obj)
            distributed, distributed_angle = _distribute_head_rotation(
                obj, head, orientations["Head"], distribution)
            _write_world_rotation(obj, head, orientations["Head"])
        for row in limbs:
            if row["label"] in orientations:
                _write_world_rotation(obj, row["ik"], orientations[row["label"]])
        passes = 0
        for passes in range(1, 9):
            maximum = 0.0
            body_actual = _world_point(obj, obj.pose.bones[body].matrix.translation)
            body_residual = points["Body"] - body_actual
            maximum = max(maximum, body_residual.length)
            if body_residual.length > 1e-9:
                _translate_control(obj, body, body_residual)
            for row in limbs:
                actual = _world_point(obj, obj.pose.bones[row["joint"]].tail)
                error = points[row["label"]] - actual
                maximum = max(maximum, error.length)
                if error.length > 1e-9:
                    _translate_control(obj, row["ik"], error)
            if record.get("schema") == 4:
                for row in limbs:
                    actual = _world_point(obj, obj.pose.bones[row["pole"]].matrix.translation)
                    error = points[row["pole_label"]] - actual
                    maximum = max(maximum, error.length)
                    if error.length > 1e-9:
                        _translate_control(obj, row["pole"], error)
            if maximum <= max(1e-7, float(record["scale"]) * 2e-6):
                break
        pin_errors = {}
        for row in limbs:
            actual = _world_point(obj, obj.pose.bones[row["joint"]].tail)
            pin_errors[row["label"]] = (actual - points[row["label"]]).length
        pole_errors = {}
        if record.get("schema") == 4:
            for row in limbs:
                actual = _world_point(obj, obj.pose.bones[row["pole"]].matrix.translation)
                pole_errors[row["pole_label"]] = (actual - points[row["pole_label"]]).length
        body_error = (_world_point(obj, obj.pose.bones[body].matrix.translation) - points["Body"]).length
        maximum = max(pin_errors.values())
        maximum_pole = max(pole_errors.values(), default=0.0)
        tolerance = max(2e-5, float(record["scale"]) * 2e-4)
        orientation_errors = {}
        for label, target in orientations.items():
            name = body if label == "Body" else _head_control(profile, obj) if label == "Head" else next(
                row["ik"] for row in limbs if row["label"] == label)
            orientation_errors[label] = _rotation_error(_world_rotation(obj, name), target)
        spine_errors = {role: _rotation_error(_world_rotation(obj, distribution["controls"][role]), target)
                        for role, target in distributed.items()}
        max_orientation_error = max([*orientation_errors.values(), *spine_errors.values()], default=0.0)
        orientation_tolerance = 2e-5
        if (maximum > tolerance or maximum_pole > tolerance or body_error > tolerance or
                max_orientation_error > orientation_tolerance):
            raise ValueError("Quadruped targets exceed the current IK reach or precision; "
                             f"paw error {maximum:.6g}, pole error {maximum_pole:.6g}, "
                             f"body error {body_error:.6g}, "
                             f"rotation error {max_orientation_error:.6g}")
        record["preview"] = _plain(w.raw_pose(obj, profile.controls))
        record["signature"] = signature
        record["metrics"] = {"profile": profile.name, "passes": passes,
                             "max_paw_error": maximum, "body_error": body_error,
                             "max_pole_error": maximum_pole, "pole_errors": pole_errors,
                             "tolerance": tolerance, "paw_errors": pin_errors,
                             "max_orientation_error": max_orientation_error,
                             "orientation_tolerance": orientation_tolerance,
                             "orientation_errors": orientation_errors,
                             "spine_distribution": {"active": distribution["active"],
                                 "follow": distribution["follow"],
                                 "neck_share": distribution["neck_share"],
                                 "head_delta_radians": distributed_angle,
                                 "weights": _spine_weights(distribution["follow"], distribution["neck_share"]),
                                 "orientation_errors": spine_errors}}
        obj.b4ml.quadruped_payload = json.dumps(record, allow_nan=False)
        obj.b4ml.status = "Quadruped pose ready; maximum paw error " + format(maximum, ".3g")
        return record["metrics"]
    except Exception:
        w.restore_pose(obj, previous)
        bpy.context.view_layer.update()
        raise


def _cleanup(obj, record, *, restore):
    if restore and isinstance(record.get("source"), dict):
        w.restore_pose(obj, record["source"])
        bpy.context.view_layer.update()
    token = record.get("token")
    if token and p._owned(bpy.context.active_object, obj, token):
        visible = w.motion_layer.find(obj) or obj
        bpy.context.view_layer.objects.active = visible
        visible.select_set(True)
    for helper in list(bpy.data.objects):
        if token and p._owned(helper, obj, token):
            bpy.data.objects.remove(helper, do_unlink=True)
    obj.b4ml.quadruped_targets.clear()
    obj.b4ml.quadruped_payload = ""
    obj.b4ml.quadruped_source = None


def finish(obj, scene, keep=False):
    record = _read(obj)
    if keep:
        profile, _, _ = _validate(obj, scene, record)
        _, _, signature, _, _ = _request(obj, scene, record)
        if record.get("signature") is None or signature != record["signature"]:
            raise ValueError("Solve the current quadruped targets before keeping")
        if _plain(w.raw_pose(obj, profile.controls)) != record.get("preview"):
            raise ValueError("Quadruped controls changed after solving; solve again before keeping")
        w._capture_anchor(obj, scene, False, from_posing=True)
    _cleanup(obj, record, restore=True)
    obj.b4ml.status = ("Saved quadruped pose anchor and restored source" if keep else
                       "Cancelled quadruped pose preview and restored source")


def register():
    return None


def unregister():
    for obj in list(bpy.data.objects):
        if hasattr(obj, "b4ml") and obj.b4ml.quadruped_payload:
            scene = next(iter(obj.users_scene), bpy.context.scene)
            with bpy.context.temp_override(scene=scene, view_layer=scene.view_layers[0]):
                try:
                    finish(obj, scene, False)
                except (ValueError, ReferenceError, RuntimeError):
                    try:
                        _cleanup(obj, _read(obj), restore=True)
                    except (ValueError, ReferenceError, RuntimeError):
                        obj.b4ml.quadruped_targets.clear()
                        obj.b4ml.quadruped_payload = ""
                        obj.b4ml.quadruped_source = None
