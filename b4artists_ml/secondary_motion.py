"""Selected-control secondary motion on reversible animation candidates.

SPDX-License-Identifier: GPL-2.0-or-later

The solver is deterministic physics refinement. It does not use a learned
model. Blender data is read and written on the main thread in cooperative
steps, and the input action is never edited in place.
"""
import json
import math
import time

import bpy
import numpy as np
from mathutils import Euler, Matrix, Quaternion, Vector

from . import workflow as w, secondary_math as sm, rig_mapping, quadruped_gait
from . import contacts, flight

_JOBS = {}


def busy(state, *, allow_secondary=False):
    """Return whether another workflow owns mutable rig or candidate state."""
    return bool(
        (state.secondary_running and not allow_secondary)
        or state.temporal_running or state.body_running or state.body_live
        or state.body_payload or state.posing_payload or state.quadruped_payload
        or state.flight_running or state.contact_running
        or state.contact_suggest_running or state.cleanup_running)


_CHAIN_DIRECTIONS = frozenset(('PARENTS', 'CHILDREN'))
_MAX_AUTO_CHAIN_CONTROLS = 32
_MAX_CONTROL_LOAD_TEXT = 1024 * 1024


def _chain_mode(state):
    """Return the explicitly supported chain channel, or ``None``."""
    if state.secondary_space == 'LOCAL' and state.secondary_rotation:
        return 'LOCAL_ROTATION'
    if state.secondary_space == 'WORLD' and state.secondary_location:
        return 'WORLD_LOCATION'
    return None


def _busy(state):
    """Return whether another preview or solver owns animation state."""
    return busy(state)


def _candidate_identity(obj, candidate):
    animation = obj.animation_data
    slot = getattr(animation, 'action_slot', None) if animation else None
    return {
        'action_pointer': candidate.as_pointer(),
        'slot_pointer': (slot.as_pointer()
                         if slot and hasattr(slot, 'as_pointer') else None),
        'slot_identifier': getattr(slot, 'identifier', None),
        'slot_handle': getattr(animation, 'action_slot_handle', None),
    }


def _valid_candidate_identity(value):
    keys = {'action_pointer', 'slot_pointer', 'slot_identifier', 'slot_handle'}
    return bool(isinstance(value, dict) and set(value) == keys
                and type(value['action_pointer']) is int
                and value['action_pointer'] > 0
                and (value['slot_pointer'] is None
                     or type(value['slot_pointer']) is int)
                and (value['slot_identifier'] is None
                     or isinstance(value['slot_identifier'], str))
                and (value['slot_handle'] is None
                     or type(value['slot_handle']) is int))


def selected_controls(obj):
    def selected(bone):
        return bool(getattr(bone, 'select', getattr(bone.bone, 'select', False)))
    return tuple(sorted(bone.name for bone in obj.pose.bones if selected(bone)))


def _control_load_record(obj):
    """Read persistent, rig-bound per-control force and torque assignments."""
    text = obj.b4ml.secondary_control_loads
    if not text:
        return {}
    if not isinstance(text, str) or len(text) > _MAX_CONTROL_LOAD_TEXT:
        raise ValueError('Stored secondary control loads exceed the data limit')
    try:
        record = json.loads(text)
    except (TypeError, ValueError, RecursionError) as exc:
        raise ValueError('Stored secondary control loads are invalid') from exc
    if (not isinstance(record, dict)
            or set(record) != {'schema', 'bone_signature', 'loads'}
            or type(record['schema']) is not int or record['schema'] not in (1, 2)
            or not isinstance(record['bone_signature'], str)
            or record['bone_signature'] != rig_mapping.bone_signature(obj)
            or not isinstance(record['loads'], list)
            or len(record['loads']) > len(obj.pose.bones)):
        raise ValueError('Stored secondary control loads do not match this rig')
    result = {}
    previous = None
    for item in record['loads']:
        expected = ({'control', 'force', 'mass'} if record['schema'] == 1 else
                    {'control', 'force', 'mass', 'offset', 'rotational_inertia'})
        if (not isinstance(item, dict) or set(item) != expected
                or not isinstance(item['control'], str) or not item['control']
                or (previous is not None and item['control'] <= previous)
                or obj.pose.bones.get(item['control']) is None):
            raise ValueError('Stored secondary control loads contain an invalid control')
        acceleration = sm.control_load_acceleration(item['force'], item['mass'])
        offset = item.get('offset', [0.0, 0.0, 0.0])
        inertia = item.get('rotational_inertia', 1.0)
        sm.validate_control_torque_settings(item['force'], offset, inertia)
        force = [float(value) for value in item['force']]
        mass = float(item['mass'])
        result[item['control']] = dict(force=force, mass=mass,
                                       offset=[float(value) for value in offset],
                                       rotational_inertia=float(inertia),
                                       acceleration=[float(value) for value in acceleration])
        previous = item['control']
    return result


def control_load_count(obj):
    """Return the validated assignment count, or None for a corrupt record."""
    try:
        return len(_control_load_record(obj))
    except ValueError:
        return None


def _eligible_load_controls(obj, names):
    if not names:
        raise ValueError('Select one or more pose controls')
    recognized = set(w.profile_for_object(obj).controls)
    for name in names:
        bone = obj.pose.bones.get(name)
        if bone is None:
            raise ValueError('Selected control disappeared: ' + name)
        if bone.bone.use_deform and name not in recognized:
            raise ValueError(name + ' is an unrecognized deform bone, not an animator control')
        category = rig_mapping.structural_category(name)
        if category:
            raise ValueError(name + ' is a ' + category + ' bone, not an animator control')


def _write_control_loads(obj, loads):
    torque_schema = any(loads[name]['offset'] != [0.0, 0.0, 0.0]
                        or loads[name]['rotational_inertia'] != 1.0
                        for name in loads)
    rows = []
    for name in sorted(loads):
        row = dict(control=name, force=loads[name]['force'], mass=loads[name]['mass'])
        if torque_schema:
            row['offset'] = loads[name]['offset']
            row['rotational_inertia'] = loads[name]['rotational_inertia']
        rows.append(row)
    if not rows:
        obj.b4ml.secondary_control_loads = ''
        return
    record = dict(schema=2 if torque_schema else 1,
                  bone_signature=rig_mapping.bone_signature(obj), loads=rows)
    text = json.dumps(record, sort_keys=True, separators=(',', ':'), allow_nan=False)
    if len(text) > _MAX_CONTROL_LOAD_TEXT:
        raise ValueError('Secondary control loads exceed the data limit')
    obj.b4ml.secondary_control_loads = text


def assign_control_loads(obj, force, mass, offset=(0.0, 0.0, 0.0),
                         rotational_inertia=1.0):
    """Assign one validated force, mass, offset, and inertia to selected controls."""
    w.require_rig(obj)
    state = obj.b4ml
    if busy(state):
        raise ValueError('Finish the active pose or correction first')
    if (not state.candidate_action or not obj.animation_data
            or obj.animation_data.action != state.candidate_action):
        raise ValueError('Generate and select an animation candidate first')
    if obj.mode != 'POSE':
        raise ValueError('Enter Pose Mode before assigning secondary control loads')
    names = selected_controls(obj)
    _eligible_load_controls(obj, names)
    acceleration = sm.control_load_acceleration(force, mass)
    _, validated_offset, validated_inertia = sm.validate_control_torque_settings(
        force, offset, rotational_inertia)
    loads = _control_load_record(obj)
    normalized = dict(force=[float(value) for value in force], mass=float(mass),
                      offset=[float(value) for value in validated_offset],
                      rotational_inertia=validated_inertia,
                      acceleration=[float(value) for value in acceleration])
    for name in names:
        loads[name] = dict(normalized)
    _write_control_loads(obj, loads)
    state.status = f'Assigned force, mass, and application offset to {len(names)} selected controls'
    return dict(controls=list(names), force=normalized['force'], mass=normalized['mass'],
                offset=normalized['offset'], rotational_inertia=normalized['rotational_inertia'],
                acceleration=normalized['acceleration'], assigned=len(loads))


def load_active_control_load(obj):
    """Recall one active selected control assignment into the visible settings."""
    w.require_rig(obj)
    state = obj.b4ml
    if busy(state):
        raise ValueError('Finish the active pose or correction first')
    if (not state.candidate_action or not obj.animation_data
            or obj.animation_data.action != state.candidate_action):
        raise ValueError('Generate and select an animation candidate first')
    if obj.mode != 'POSE':
        raise ValueError('Enter Pose Mode before loading a secondary control assignment')
    active = obj.data.bones.active
    if active is None or active.name not in selected_controls(obj):
        raise ValueError('Select one active pose control')
    _eligible_load_controls(obj, (active.name,))
    loads = _control_load_record(obj)
    if active.name not in loads:
        raise ValueError('The active pose control has no assigned load')
    load = loads[active.name]
    state.secondary_load_force = load['force']
    state.secondary_load_mass = load['mass']
    state.secondary_load_offset = load['offset']
    state.secondary_load_inertia = load['rotational_inertia']
    state.status = 'Loaded secondary assignment from ' + active.name
    return dict(control=active.name, force=list(load['force']), mass=load['mass'],
                offset=list(load['offset']),
                rotational_inertia=load['rotational_inertia'])


def clear_control_loads(obj):
    """Remove persistent load assignments from the selected pose controls."""
    w.require_rig(obj)
    state = obj.b4ml
    if busy(state):
        raise ValueError('Finish the active pose or correction first')
    if (not state.candidate_action or not obj.animation_data
            or obj.animation_data.action != state.candidate_action):
        raise ValueError('Generate and select an animation candidate first')
    if obj.mode != 'POSE':
        raise ValueError('Enter Pose Mode before clearing selected secondary control loads')
    names = selected_controls(obj)
    _eligible_load_controls(obj, names)
    loads = _control_load_record(obj)
    removed = sum(1 for name in names if loads.pop(name, None) is not None)
    _write_control_loads(obj, loads)
    state.status = f'Cleared force, mass, and torque from {removed} selected controls'
    return dict(controls=list(names), removed=removed, assigned=len(loads))


def clear_all_control_loads(obj):
    """Remove every stored assignment, including a malformed stale record."""
    w.require_rig(obj)
    state = obj.b4ml
    if busy(state):
        raise ValueError('Finish the active pose or correction first')
    if (not state.candidate_action or not obj.animation_data
            or obj.animation_data.action != state.candidate_action):
        raise ValueError('Generate and select an animation candidate first')
    state.secondary_control_loads = ''
    state.status = 'Cleared all secondary control loads'
    return dict(removed_all=True, assigned=0)


def _sphere_collider_values(state, scene, rig, collider, radius, moving=False, scaling=False):
    """Return one validated world-space sphere and mutation token."""
    if collider is None:
        raise ValueError('Choose a sphere-center object')
    if collider == rig:
        raise ValueError('The animated rig cannot be its own sphere collider')
    if scene.objects.get(collider.name) is not collider:
        raise ValueError('The sphere-center object must belong to the active scene')
    if collider.parent or collider.constraints:
        if moving:
            raise ValueError('The moving sphere-center object must be unparented without constraints')
        raise ValueError('The sphere-center object must be unparented and static without constraints or animation')
    animation = collider.animation_data
    if (getattr(collider, 'rigid_body', None) is not None
            or getattr(collider, 'rigid_body_constraint', None) is not None):
        raise ValueError('The sphere-center object cannot use rigid-body simulation')
    action = animation.action if animation else None
    if moving or scaling:
        if animation and (animation.drivers or len(animation.nla_tracks)):
            raise ValueError('Animated spheres support direct object animation without drivers or NLA')
        if action is None:
            raise ValueError('Following sphere animation requires a direct object Action')
        curves = list(w.action_curves(
            action, getattr(animation, 'action_slot', None)))
        if any(curve.modifiers for curve in curves):
            raise ValueError('Moving sphere centers do not support animation curve modifiers')
        paths = {curve.data_path for curve in curves}
        if paths & {'delta_scale', 'delta_location'}:
            raise ValueError('Animated spheres do not support animated delta transforms')
        location_indices = {curve.array_index for curve in curves
                            if curve.data_path == 'location'}
        if (location_indices != {0, 1, 2}
                or any(curve.mute for curve in curves
                       if curve.data_path == 'location')):
            if moving:
                raise ValueError('Moving sphere centers require complete direct object location curves')
        if not moving and 'location' in paths:
            raise ValueError('Enable Follow Animation to use sphere-center location curves')
        scale_indices = {curve.array_index for curve in curves
                         if curve.data_path == 'scale'}
        if scaling and (scale_indices != {0, 1, 2}
                        or any(curve.mute for curve in curves
                               if curve.data_path == 'scale')):
            raise ValueError('Animated sphere radii require complete direct object scale curves')
        if not scaling and 'scale' in paths:
            raise ValueError('Enable Follow Radius Scale to use sphere scale curves')
    elif animation and (action or animation.drivers or len(animation.nla_tracks)):
        raise ValueError('Static sphere centers cannot use animation; enable Follow Animation for direct location keys')
    matrix = collider.matrix_world.copy()
    center, radius = sm.validate_sphere_collider(tuple(matrix.translation), radius)
    if scaling:
        scale = tuple(float(value) for value in matrix.to_scale())
        if (not all(math.isfinite(value) and value > 0.0 for value in scale)
                or max(scale)-min(scale) > 1e-6*max(1.0, max(scale))):
            raise ValueError('Animated sphere radius requires positive uniform evaluated scale')
        sm.validate_sphere_collider(center, radius*(sum(scale)/3.0))
    if moving or scaling:
        slot = getattr(animation, 'action_slot', None)
        token = (collider.as_pointer(), 'ANIMATED', bool(moving), bool(scaling), action.as_pointer(),
                 (slot.as_pointer() if slot and hasattr(slot, 'as_pointer') else None),
                 getattr(slot, 'identifier', None),
                 quadruped_gait._action_digest(collider, action),
                 tuple(float(value) for value in collider.delta_location),
                 tuple(float(value) for value in collider.delta_scale), radius)
        surface = (('MOVING_' if moving else '')
                   + ('SCALING_' if scaling else '') + 'SPHERE:' + collider.name)
    else:
        token = (collider.as_pointer(), tuple(center), radius)
        surface = 'STATIC_SPHERE:' + collider.name
    return Vector(center), radius, surface, token


def _sphere_collider(state, scene, rig):
    return _sphere_collider_values(
        state, scene, rig, state.secondary_sphere_collider,
        state.secondary_sphere_radius, state.secondary_sphere_moving,
        state.secondary_sphere_scaling)


def _capsule_collider_values(state, scene, rig, start, end, radius,
                             moving=False, scaling=False):
    """Return one validated capsule and a stable binding token.

    Animated endpoints and uniform radius scale are sampled by the solve at
    bounded solver frames.  The binding token covers the direct Actions and
    settings, not the current frame's evaluated transform.
    """
    if start is None or end is None:
        raise ValueError('Choose distinct capsule endpoint objects')
    authored_radius = float(radius)
    if start == rig or end == rig:
        raise ValueError('The animated rig cannot be a capsule endpoint')
    if start == end:
        raise ValueError('Capsule endpoints must use two distinct objects')
    for endpoint, label in ((start, 'start'), (end, 'end')):
        if scene.objects.get(endpoint.name) is not endpoint:
            raise ValueError(f'The capsule {label} object must belong to the active scene')
        if endpoint.parent or endpoint.constraints:
            raise ValueError('Capsule endpoints must be unparented without constraints')
        animation = endpoint.animation_data
        action = animation.action if animation else None
        if moving or scaling:
            if animation and (animation.drivers or len(animation.nla_tracks)):
                raise ValueError('Animated capsule endpoints support direct object animation without drivers or NLA')
            if action is None:
                raise ValueError('Animated capsule endpoints require a direct object Action')
            curves = list(w.action_curves(
                action, getattr(animation, 'action_slot', None)))
            if any(curve.modifiers or curve.mute or curve.lock for curve in curves):
                raise ValueError('Animated capsule endpoint curves must be editable, unmuted, and modifier-free')
            allowed = {
                endpoint.path_from_id('location'),
                endpoint.path_from_id('scale'),
            }
            if any(curve.data_path not in allowed for curve in curves):
                raise ValueError('Animated capsule endpoints support direct location and scale curves only')
            paths = {curve.data_path for curve in curves}
            if paths & {'delta_scale', 'delta_location'}:
                raise ValueError('Animated capsule endpoints do not support animated delta transforms')
            location_indices = {curve.array_index for curve in curves
                                if curve.data_path == endpoint.path_from_id('location')}
            if moving and location_indices != {0, 1, 2}:
                raise ValueError('Moving capsule endpoints require complete direct location curves')
            scale_indices = {curve.array_index for curve in curves
                             if curve.data_path == endpoint.path_from_id('scale')}
            if scaling and scale_indices != {0, 1, 2}:
                raise ValueError('Animated capsule radius requires complete direct uniform scale curves')
            if not moving and endpoint.path_from_id('location') in paths:
                raise ValueError('Enable Follow Endpoint Animation to use capsule location curves')
            if not scaling and endpoint.path_from_id('scale') in paths:
                raise ValueError('Enable Follow Radius Scale to use capsule scale curves')
        elif animation and (action or animation.drivers or len(animation.nla_tracks)):
            raise ValueError('Capsule endpoints must be static without animation')
        if (getattr(endpoint, 'rigid_body', None) is not None
                or getattr(endpoint, 'rigid_body_constraint', None) is not None):
            raise ValueError('Capsule endpoints cannot use rigid-body simulation')
    start_value, end_value, radius = sm.validate_capsule_collider(
        tuple(start.matrix_world.translation), tuple(end.matrix_world.translation), radius)
    if scaling:
        scale_values = []
        for endpoint, label in ((start, 'start'), (end, 'end')):
            scale = tuple(float(value) for value in endpoint.matrix_world.to_scale())
            if (not all(math.isfinite(value) and value > 0.0 for value in scale)
                    or max(scale)-min(scale) > 1e-6*max(1.0, max(scale))):
                raise ValueError('Animated capsule radius requires positive uniform evaluated scale')
            scale_values.append(sum(scale) / 3.0)
        if abs(scale_values[0] - scale_values[1]) > 1e-6*max(1.0, *scale_values):
            raise ValueError('Capsule endpoint radius scales must agree')
        radius *= scale_values[0]
        sm.validate_capsule_collider(tuple(start_value), tuple(end_value), radius)
    if moving or scaling:
        actions = tuple(endpoint.animation_data.action.as_pointer()
                        for endpoint in (start, end))
        slots = tuple(
            (getattr(endpoint.animation_data, 'action_slot', None).as_pointer()
             if getattr(endpoint.animation_data, 'action_slot', None)
             and hasattr(getattr(endpoint.animation_data, 'action_slot', None), 'as_pointer')
             else None)
            for endpoint in (start, end))
        token = (start.as_pointer(), end.as_pointer(), 'ANIMATED', bool(moving), bool(scaling),
                 actions, slots,
                 tuple(quadruped_gait._action_digest(endpoint, endpoint.animation_data.action)
                       for endpoint in (start, end)),
                 tuple(tuple(float(value) for value in endpoint.delta_location)
                       for endpoint in (start, end)),
                 tuple(tuple(float(value) for value in endpoint.delta_scale)
                       for endpoint in (start, end)), authored_radius)
        surface = (('MOVING_' if moving else '')
                   + ('SCALING_' if scaling else '')
                   + 'CAPSULE:' + start.name + ':' + end.name)
    else:
        token = (start.as_pointer(), end.as_pointer(), tuple(start_value), tuple(end_value), radius)
        surface = 'STATIC_CAPSULE:' + start.name + ':' + end.name
    return Vector(start_value), Vector(end_value), radius, surface, token


def _capsule_collider(state, scene, rig):
    return _capsule_collider_values(
        state, scene, rig, state.secondary_capsule_start,
        state.secondary_capsule_end, state.secondary_capsule_radius,
        state.secondary_capsule_moving, state.secondary_capsule_scaling)


def _sample_capsule_trajectories(scene, start, end, radius, frames,
                                 moving=False, scaling=False):
    """Sample direct endpoint Actions at the solver frames."""
    original = scene.frame_current + scene.frame_subframe
    starts = []
    ends = []
    radii = []
    try:
        for frame in frames:
            scene.frame_set(math.floor(frame), subframe=float(frame)-math.floor(frame))
            start_value = tuple(start.matrix_world.translation)
            end_value = tuple(end.matrix_world.translation)
            value = float(radius)
            if scaling:
                scales = []
                for endpoint in (start, end):
                    scale = tuple(float(item) for item in endpoint.matrix_world.to_scale())
                    if (not all(math.isfinite(item) and item > 0.0 for item in scale)
                            or max(scale)-min(scale) > 1e-6*max(1.0, max(scale))):
                        raise ValueError('Animated capsule radius requires positive uniform evaluated scale')
                    scales.append(sum(scale) / 3.0)
                if abs(scales[0] - scales[1]) > 1e-6*max(1.0, *scales):
                    raise ValueError('Capsule endpoint radius scales must agree')
                value *= sum(scales) / 2.0
            sm.validate_capsule_collider(start_value, end_value, value)
            starts.append(start_value)
            ends.append(end_value)
            radii.append(value)
    finally:
        scene.frame_set(math.floor(original), subframe=original-math.floor(original))
    return sm.validate_capsule_trajectories((starts, ends, radii), len(frames))


def _mesh_shape_action_token(shape_keys, animation, action):
    curves = w.action_curves(action, getattr(animation, 'action_slot', None))
    rows = []
    for curve in curves:
        if curve.modifiers or curve.mute or curve.lock:
            raise ValueError('Deforming collision shape-key curves must be editable, unmuted, and modifier-free')
        if not curve.data_path.endswith('.value'):
            raise ValueError('Deforming collision supports direct shape-key value animation only')
        rows.append((curve.data_path, curve.array_index,
                     curve.extrapolation,
                     tuple((float(key.co.x), float(key.co.y))
                           for key in curve.keyframe_points),
                     tuple((tuple(key.handle_left) if key.handle_left_type in {'FREE','ALIGNED'} else None,
                            tuple(key.handle_right) if key.handle_right_type in {'FREE','ALIGNED'} else None,
                            key.handle_left_type, key.handle_right_type, key.interpolation)
                           for key in curve.keyframe_points),
                     tuple((float(point.co.x), float(point.co.y))
                           for point in curve.sampled_points)))
    if not rows:
        raise ValueError('Deforming collision requires a direct shape-key Action')
    geometry=tuple((block.name,tuple(tuple(float(v) for v in point.co)
                                     for point in block.data))
                   for block in shape_keys.key_blocks)
    return (shape_keys.as_pointer(), action.as_pointer(), tuple(rows), geometry)


def _mesh_object_action_token(surface, animation, action):
    """Bind one direct object-transform Action for a moving mesh surface."""
    allowed = {
        surface.path_from_id('location'),
        surface.path_from_id('rotation_euler'),
        surface.path_from_id('rotation_quaternion'),
        surface.path_from_id('rotation_axis_angle'),
        surface.path_from_id('scale'),
    }
    curves = w.action_curves(action, getattr(animation, 'action_slot', None))
    rows = []
    for curve in curves:
        if curve.data_path not in allowed:
            raise ValueError('Moving collision mesh supports direct object transforms only')
        if curve.modifiers or curve.mute or curve.lock:
            raise ValueError('Moving collision mesh transform curves must be editable, unmuted, and modifier-free')
        rows.append((curve.data_path, curve.array_index,
                     curve.extrapolation,
                     tuple((float(key.co.x), float(key.co.y))
                           for key in curve.keyframe_points),
                     tuple((tuple(key.handle_left) if key.handle_left_type in {'FREE','ALIGNED'} else None,
                            tuple(key.handle_right) if key.handle_right_type in {'FREE','ALIGNED'} else None,
                            key.handle_left_type, key.handle_right_type, key.interpolation)
                           for key in curve.keyframe_points),
                     tuple((float(point.co.x), float(point.co.y))
                           for point in curve.sampled_points)))
    if not rows:
        raise ValueError('Moving collision mesh requires a direct object-transform Action')
    return (action.as_pointer(), tuple(rows))


def _mesh_collider_values(state, scene, rig, surface, deforming=False, moving=False):
    """Return one validated world-space triangle mesh and mutation token."""
    if surface is None:
        raise ValueError('Choose an arbitrary mesh collision surface')
    if surface == rig:
        raise ValueError('The animated rig cannot be its own collision mesh')
    if scene.objects.get(surface.name) is not surface:
        raise ValueError('The collision mesh must belong to the active scene')
    if surface.type != 'MESH' or len(surface.data.vertices) < 3 or not surface.data.polygons:
        raise ValueError('Choose a mesh collision surface with at least one face')
    if surface.parent or surface.constraints:
        raise ValueError('The collision mesh must be unparented without constraints')
    animation = surface.animation_data
    object_token = None
    if moving:
        if animation is None or animation.action is None:
            raise ValueError('Moving collision mesh requires a direct object-transform Action')
        if animation.drivers or len(animation.nla_tracks):
            raise ValueError('Moving collision mesh does not support drivers or NLA')
        object_token = _mesh_object_action_token(surface, animation, animation.action)
    elif animation and (animation.action or animation.drivers or len(animation.nla_tracks)):
        raise ValueError('The collision mesh object transform must be static without animation')
    if (getattr(surface, 'rigid_body', None) is not None
            or getattr(surface, 'rigid_body_constraint', None) is not None):
        raise ValueError('The collision mesh cannot use rigid-body simulation')
    if surface.modifiers:
        raise ValueError('The collision mesh cannot use modifiers; deforming geometry requires direct shape keys')
    shape_keys = surface.data.shape_keys
    shape_animation = shape_keys.animation_data if shape_keys else None
    shape_action = shape_animation.action if shape_animation else None
    if deforming:
        if shape_keys is None or len(shape_keys.key_blocks) < 2:
            raise ValueError('Deforming collision requires at least one shape key')
        if shape_animation is None or shape_action is None:
            raise ValueError('Deforming collision requires a direct shape-key Action')
        if shape_animation.drivers or len(shape_animation.nla_tracks):
            raise ValueError('Deforming collision shape keys do not support drivers or NLA')
        shape_token = _mesh_shape_action_token(shape_keys, shape_animation, shape_action)
    elif shape_animation and (shape_action or shape_animation.drivers
                              or len(shape_animation.nla_tracks)):
        raise ValueError('Enable Follow Deformation to use shape-key animation')
    matrix = surface.matrix_world.copy()
    points = [matrix @ vertex.co for vertex in surface.data.vertices]
    if not all(math.isfinite(value) for point in points for value in point):
        raise ValueError('Collision mesh coordinates must be finite')
    surface.data.calc_loop_triangles()
    triangles = []
    edge_counts = {}
    for loop_triangle in surface.data.loop_triangles:
        ids = tuple(loop_triangle.vertices)
        triangle = tuple(tuple(points[index]) for index in ids)
        triangles.append(triangle)
        for index in range(3):
            edge = tuple(sorted((ids[index], ids[(index + 1) % 3])))
            edge_counts[edge] = edge_counts.get(edge, 0) + 1
    topology = tuple(tuple(item.vertices) for item in surface.data.loop_triangles)
    triangles = (_sample_deforming_mesh(surface, topology, scene)
                 if shape_keys is not None else sm.validate_mesh_triangles(triangles))
    closed = bool(edge_counts and all(count == 2 for count in edge_counts.values()))
    geometry_token = (
        surface.data.as_pointer(),
        tuple(tuple(float(value) for value in vertex.co)
              for vertex in surface.data.vertices),
        tuple(tuple(item.vertices) for item in surface.data.loop_triangles),
    )
    if moving or deforming:
        token = (surface.as_pointer(), closed, bool(deforming), bool(moving), geometry_token,
                 shape_token if deforming else None,
                 object_token if moving else tuple(value for row in matrix for value in row))
    else:
        token = (surface.as_pointer(), tuple(value for row in matrix for value in row),
                 tuple(tuple(point) for point in points),
                 tuple(tuple(tuple(vertex) for vertex in triangle) for triangle in triangles),
                 closed, bool(deforming), False, shape_token if deforming else None,
                 None)
    prefix = ('MOVING_DEFORMING_MESH:' if moving and deforming else
              'MOVING_MESH:' if moving else
              'DEFORMING_MESH:' if deforming else 'STATIC_MESH:')
    return triangles, closed, (prefix
                              + surface.name), token


def _mesh_collider(state, scene, rig):
    return _mesh_collider_values(
        state, scene, rig, state.secondary_collision_mesh,
        bool(state.secondary_collision_mesh_deforming),
        bool(state.secondary_collision_mesh_moving))


def _sample_deforming_mesh(surface, topology, scene):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated = surface.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    try:
        mesh.calc_loop_triangles()
        evaluated_topology = tuple(tuple(item.vertices) for item in mesh.loop_triangles)
        if evaluated_topology != topology:
            raise ValueError('Deforming collision mesh topology changed during sampling')
        points = [evaluated.matrix_world @ vertex.co for vertex in mesh.vertices]
        triangles = [tuple(tuple(points[index]) for index in item.vertices)
                     for item in mesh.loop_triangles]
    finally:
        evaluated.to_mesh_clear()
    return sm.validate_mesh_triangles(triangles)


def _sphere_colliders(state, scene, rig):
    items = list(state.secondary_spheres)
    if len(items) > sm.MAX_SPHERE_COLLIDERS:
        raise ValueError(f'Secondary sphere set is limited to {sm.MAX_SPHERE_COLLIDERS} colliders')
    sources = ([(item.collider, item.radius, bool(item.moving), bool(item.scaling)) for item in items]
               if items else [(state.secondary_sphere_collider,
                               state.secondary_sphere_radius,
                               bool(state.secondary_sphere_moving),
                               bool(state.secondary_sphere_scaling))])
    records = []
    seen = set()
    for collider, radius, moving, scaling in sources:
        center, radius, surface, token = _sphere_collider_values(
            state, scene, rig, collider, radius, moving, scaling)
        if token[0] in seen:
            raise ValueError('Each secondary sphere-center object can appear only once')
        seen.add(token[0])
        records.append(dict(collider=collider, center=center, radius=radius,
                            moving=moving, scaling=scaling, surface=surface, token=token))
    if len(records) == 1:
        surface = records[0]['surface']
    elif any(item['moving'] or item['scaling'] for item in records):
        surface = 'SPHERES:' + '|'.join(
            ('MOVING:' if item['moving'] else 'STATIC:')
            + ('SCALING:' if item['scaling'] else '') + item['collider'].name
            for item in records)
    else:
        surface = 'STATIC_SPHERES:' + '|'.join(
            item['collider'].name for item in records)
    return records, surface, tuple(item['token'] for item in records)


def add_sphere_collider(obj, scene):
    state = obj.b4ml
    if busy(state):
        raise ValueError('Finish the active animation workflow before editing sphere colliders')
    if len(state.secondary_spheres) >= sm.MAX_SPHERE_COLLIDERS:
        raise ValueError(f'Secondary sphere set is limited to {sm.MAX_SPHERE_COLLIDERS} colliders')
    collider = state.secondary_sphere_collider
    _, radius, _, token = _sphere_collider_values(
        state, scene, obj, collider, state.secondary_sphere_radius,
        state.secondary_sphere_moving, state.secondary_sphere_scaling)
    if any(item.collider == collider for item in state.secondary_spheres):
        raise ValueError('This sphere-center object is already in the set')
    item = state.secondary_spheres.add()
    item.collider = collider
    item.radius = radius
    item.moving = bool(state.secondary_sphere_moving)
    item.scaling = bool(state.secondary_sphere_scaling)
    state.status = f'Added sphere collider {collider.name}'
    return dict(count=len(state.secondary_spheres), token=token)


def _geometry_bound_corners(collider):
    """Return validated local bound-box corners for supported geometry."""
    if collider is None or collider.type not in {'MESH', 'CURVE', 'SURFACE', 'META', 'FONT'}:
        raise ValueError('Sphere bounds require a geometric object')
    try:
        corners = [Vector(corner) for corner in collider.bound_box]
    except (AttributeError, ReferenceError, RuntimeError, TypeError, ValueError):
        raise ValueError('The sphere source has no readable geometric bounds') from None
    if len(corners) != 8 or not all(
            len(corner) == 3 and all(math.isfinite(float(value)) for value in corner)
            for corner in corners):
        raise ValueError('The sphere source has invalid geometric bounds')
    if len({tuple(corner) for corner in corners}) == 1:
        raise ValueError('The sphere source has no available geometric bounds')
    return corners


def _enclosing_float32(value):
    """Store a positive radius without rounding below its computed bound."""
    required = float(value)
    stored = float(np.float32(required))
    if stored < required:
        stored = float(np.nextafter(np.float32(stored), np.float32(np.inf)))
    _, stored = sm.validate_sphere_collider((0.0, 0.0, 0.0), stored)
    return required, stored


def fit_sphere_collider_radius(obj, scene, index=-1):
    """Snapshot an enclosing sphere radius from one collider's local bounds."""
    state = obj.b4ml
    if busy(state):
        raise ValueError('Finish the active animation workflow before fitting sphere colliders')
    if type(index) is not int or index < -1 or index >= len(state.secondary_spheres):
        raise ValueError('Choose the staged sphere or an existing sphere collider to fit')
    if index == -1:
        collider = state.secondary_sphere_collider
        radius = state.secondary_sphere_radius
        moving = bool(state.secondary_sphere_moving)
        scaling = bool(state.secondary_sphere_scaling)
    else:
        item = state.secondary_spheres[index]
        collider = item.collider
        radius = item.radius
        moving = bool(item.moving)
        scaling = bool(item.scaling)
    _sphere_collider_values(state, scene, obj, collider, radius, moving, scaling)
    try:
        corners = _geometry_bound_corners(collider)
    except ValueError as exc:
        raise ValueError(str(exc).replace('Sphere bounds require a geometric object',
                                          'Radius fitting requires a collider object with geometric bounds')
                                   .replace('sphere source', 'sphere collider')) from None
    if scaling:
        fitted = max(corner.length for corner in corners)
        scale = sum(collider.matrix_world.to_scale()) / 3.0
        world_fitted = max((collider.matrix_world.to_3x3() @ corner).length
                           for corner in corners)
        required = max(fitted, world_fitted / scale)
    else:
        basis = collider.matrix_world.to_3x3()
        fitted = max((basis @ corner).length for corner in corners)
        required = fitted
    required, stored = _enclosing_float32(required)
    if index == -1:
        state.secondary_sphere_radius = stored
        actual = float(state.secondary_sphere_radius)
    else:
        state.secondary_spheres[index].radius = stored
        actual = float(state.secondary_spheres[index].radius)
    if actual < required:
        if index == -1:
            state.secondary_sphere_radius = radius
        else:
            state.secondary_spheres[index].radius = radius
        raise RuntimeError('Stored sphere radius did not enclose the collider bounds')
    state.status = f'Fit sphere radius for {collider.name}: {actual:.6g}'
    return dict(collider=collider.name_full, radius=actual,
                basis=('LOCAL' if scaling else 'WORLD'))


def create_sphere_proxy_from_bounds(obj, scene):
    """Create and add an explicit sphere proxy around staged geometry bounds."""
    state = obj.b4ml
    if busy(state):
        raise ValueError('Finish the active animation workflow before creating sphere proxies')
    if len(state.secondary_spheres) >= sm.MAX_SPHERE_COLLIDERS:
        raise ValueError(f'Secondary sphere set is limited to {sm.MAX_SPHERE_COLLIDERS} colliders')
    source = state.secondary_sphere_collider
    if source is None or scene.objects.get(source.name) is not source:
        raise ValueError('Choose a geometric object in this scene to create a sphere proxy')
    corners = _geometry_bound_corners(source)
    world_corners = [source.matrix_world @ corner for corner in corners]
    center = sum(world_corners, Vector((0.0, 0.0, 0.0))) / len(world_corners)
    center, _ = sm.validate_sphere_collider(tuple(center), 1.0)
    required, stored = _enclosing_float32(
        max((corner - Vector(center)).length for corner in world_corners))

    previous = (state.secondary_sphere_collider, float(state.secondary_sphere_radius),
                bool(state.secondary_sphere_moving), bool(state.secondary_sphere_scaling))
    proxy = None
    added = False
    try:
        proxy = bpy.data.objects.new(f'{source.name} B4ML Sphere', None)
        proxy.empty_display_type = 'SPHERE'
        proxy.empty_display_size = stored
        proxy.matrix_world = Matrix.Translation(Vector(center))
        proxy['b4ml_sphere_proxy'] = True
        proxy['b4ml_sphere_source'] = source.name_full
        scene.collection.objects.link(proxy)
        item = state.secondary_spheres.add()
        added = True
        item.collider = proxy
        item.radius = stored
        item.moving = False
        item.scaling = False
        state.secondary_sphere_collider = proxy
        state.secondary_sphere_radius = stored
        state.secondary_sphere_moving = False
        state.secondary_sphere_scaling = False
        actual = float(item.radius)
        if actual < required:
            raise RuntimeError('Stored sphere proxy radius did not enclose the source bounds')
    except Exception:
        if added:
            state.secondary_spheres.remove(len(state.secondary_spheres) - 1)
        (state.secondary_sphere_collider, state.secondary_sphere_radius,
         state.secondary_sphere_moving, state.secondary_sphere_scaling) = previous
        if proxy is not None:
            bpy.data.objects.remove(proxy, do_unlink=True)
        raise
    state.status = f'Created sphere proxy for {source.name}: {actual:.6g}'
    return dict(source=source.name_full, collider=proxy.name_full,
                center=tuple(float(value) for value in center), radius=actual,
                count=len(state.secondary_spheres))


def remove_sphere_collider(obj, index):
    state = obj.b4ml
    if busy(state):
        raise ValueError('Finish the active animation workflow before editing sphere colliders')
    if type(index) is not int or not 0 <= index < len(state.secondary_spheres):
        raise ValueError('Choose an existing sphere collider to remove')
    name = state.secondary_spheres[index].collider
    state.secondary_spheres.remove(index)
    state.status = 'Removed sphere collider' + (': ' + name.name if name else '')
    return dict(count=len(state.secondary_spheres))


def clear_sphere_colliders(obj):
    state = obj.b4ml
    if busy(state):
        raise ValueError('Finish the active animation workflow before editing sphere colliders')
    count = len(state.secondary_spheres)
    state.secondary_spheres.clear()
    state.status = f'Cleared {count} sphere collider' + ('s' if count != 1 else '')
    return dict(removed=count)


def _set_selected(bone, value):
    if hasattr(bone, 'select'):
        bone.select = bool(value)
    else:
        bone.bone.select = bool(value)


def _eligible_chain_control(obj, bone, captured, curves, drivers, controls=None,
                            channel='rotation'):
    controls = set(w.profile_for_object(obj).controls) if controls is None else controls
    if bone.bone.use_deform and bone.name not in controls:
        return False, bone.name + ' is an unrecognized deform bone, not an animator control'
    category = rig_mapping.structural_category(bone.name)
    if category:
        return False, bone.name + ' is a ' + category + ' bone, not an animator control'
    if bone.name not in captured:
        return False, bone.name + ' is not present in every captured pose'
    data = bone.bone
    if getattr(data, 'hide', False) or getattr(data, 'hide_select', False):
        return False, bone.name + ' is hidden or not selectable'
    if channel == 'location':
        if w._channels(bone)['location'] != [0, 1, 2]:
            return False, 'Location is partially locked or connected on ' + bone.name
        prop, count = 'location', 3
    else:
        if not w._channels(bone)['rotation']:
            return False, 'Rotation is partially locked on ' + bone.name
        prop, count = _rotation_spec(bone)
    path = bone.path_from_id(prop)
    if path in drivers:
        return False, 'Rotation is driven on ' + bone.name
    try:
        group = _curve_group(curves, path, count, bone.name + ' rotation')
    except ValueError as exc:
        return False, str(exc)
    if group is None:
        return False, bone.name + ' has no animated ' + channel + ' curves in this candidate'
    return True, ''


def _selection_record(obj, candidate):
    active = obj.data.bones.active
    return {
        'schema': 2,
        'bone_signature': rig_mapping.bone_signature(obj),
        'candidate_name': candidate.name,
        'candidate_identity': _candidate_identity(obj, candidate),
        'candidate_token': flight._curve_token(obj, candidate),
        'selected': list(selected_controls(obj)),
        'active': active.name if active else None,
        'chain': bool(obj.b4ml.secondary_chain),
    }


def _read_selection_record(obj, candidate):
    text = obj.b4ml.secondary_selection_swap
    if not isinstance(text, str) or not text or len(text) > 1024 * 1024:
        raise ValueError('No previous secondary selection is available')
    try:
        record = json.loads(text)
    except (TypeError, ValueError, RecursionError) as exc:
        raise ValueError('Previous secondary selection is invalid') from exc
    keys = {'schema', 'bone_signature', 'candidate_name', 'candidate_identity', 'candidate_token',
            'selected', 'active', 'chain'}
    if (not isinstance(record, dict) or set(record) != keys
            or type(record['schema']) is not int or record['schema'] != 2):
        raise ValueError('Previous secondary selection has an invalid schema')
    if (not isinstance(record['bone_signature'], str)
            or record['bone_signature'] != rig_mapping.bone_signature(obj)):
        raise ValueError('Previous secondary selection belongs to different rig bones')
    if (not isinstance(record['candidate_name'], str)
            or record['candidate_name'] != candidate.name
            or not _valid_candidate_identity(record['candidate_identity'])
            or record['candidate_identity'] != _candidate_identity(obj, candidate)
            or not isinstance(record['candidate_token'], str)
            or record['candidate_token'] != flight._curve_token(obj, candidate)):
        raise ValueError('Previous secondary selection belongs to a different animation candidate')
    names = record['selected']
    if (not isinstance(names, list) or len(names) > len(obj.pose.bones)
            or any(not isinstance(name, str) or not name for name in names)
            or len(names) != len(set(names))
            or any(obj.pose.bones.get(name) is None for name in names)):
        raise ValueError('Previous secondary selection contains invalid controls')
    active = record['active']
    if active is not None and (not isinstance(active, str)
                               or obj.pose.bones.get(active) is None):
        raise ValueError('Previous active control is invalid')
    if type(record['chain']) is not bool:
        raise ValueError('Previous secondary chain mode is invalid')
    if record['chain']:
        mode = _chain_mode(obj.b4ml)
        if mode is None:
            raise ValueError('Previous secondary chain requires Local+Rotation or World+Location')
        channel = 'location' if mode == 'WORLD_LOCATION' else 'rotation'
        if len(names) < 2:
            raise ValueError('Previous secondary chain needs at least two controls')
        curves = w.action_curves(candidate, getattr(obj.animation_data, 'action_slot', None))
        drivers = ({curve.data_path for curve in obj.animation_data.drivers}
                   if obj.animation_data else set())
        controls = set(w.profile_for_object(obj).controls)
        # Check mutable eligibility before anchor signature validation so stale
        # locks, drivers, visibility, and curve state receive the precise reason.
        provisional = set(names)
        for name in names:
            valid, reason = _eligible_chain_control(
                obj, obj.pose.bones[name], provisional, curves, drivers, controls, channel)
            if not valid:
                raise ValueError('Previous secondary chain is no longer eligible: ' + reason)
        anchors = w.read_anchors(obj)
        captured = set(anchors[0][1]['pose'])
        for _, payload in anchors[1:]:
            captured.intersection_update(payload['pose'])
        for name in names:
            valid, reason = _eligible_chain_control(
                obj, obj.pose.bones[name], captured, curves, drivers, controls, channel)
            if not valid:
                raise ValueError('Previous secondary chain is no longer eligible: ' + reason)
        try:
            _chain_order(obj, names)
        except ValueError as exc:
            raise ValueError('Previous secondary chain is no longer valid: ' + str(exc)) from exc
    return record


def swap_selection(obj):
    """Atomically exchange current selection with the bound previous selection."""
    w.require_rig(obj)
    w._reject_nla(obj)
    if obj.mode != 'POSE':
        raise ValueError('Enter Pose Mode before swapping secondary controls')
    state = obj.b4ml
    if _busy(state):
        raise ValueError('Finish the active pose or correction first')
    candidate = state.candidate_action
    if (not candidate or not obj.animation_data
            or obj.animation_data.action != candidate):
        raise ValueError('Generate and select an animation candidate first')
    target = _read_selection_record(obj, candidate)
    current = _selection_record(obj, candidate)
    status_before = state.status
    record_before = state.secondary_selection_swap
    try:
        selected = set(target['selected'])
        for bone in obj.pose.bones:
            _set_selected(bone, bone.name in selected)
        obj.data.bones.active = (obj.data.bones.get(target['active'])
                                 if target['active'] else None)
        state.secondary_chain = target['chain']
        state.secondary_selection_swap = json.dumps(
            current, sort_keys=True, separators=(',', ':'), allow_nan=False)
        state.status = 'Swapped with the previous secondary-control selection'
    except BaseException:
        selected = set(current['selected'])
        for bone in obj.pose.bones:
            try:
                _set_selected(bone, bone.name in selected)
            except (AttributeError, ReferenceError, RuntimeError):
                pass
        try:
            obj.data.bones.active = (obj.data.bones.get(current['active'])
                                     if current['active'] else None)
            state.secondary_chain = current['chain']
            state.secondary_selection_swap = record_before
            state.status = status_before
        except (AttributeError, ReferenceError, RuntimeError):
            pass
        raise
    return {
        'schema': 1,
        'selected': list(target['selected']),
        'active': target['active'],
        'chain': target['chain'],
        'candidate_unchanged': True,
    }


def select_chain(obj, active_name, direction='CHILDREN', max_controls=4):
    """Select one eligible direct hierarchy from an explicit active control.

    This is bounded topology assistance for the deterministic chain solver. It
    does not infer hair, cloth, flesh, or any semantic secondary-part label.
    Selection and settings are changed only after the complete chain validates.
    """
    w.require_rig(obj)
    w._reject_nla(obj)
    if obj.mode != 'POSE':
        raise ValueError('Enter Pose Mode before selecting secondary controls')
    if direction not in _CHAIN_DIRECTIONS:
        raise ValueError('Secondary chain direction must be Parents or Children')
    if (isinstance(max_controls, bool) or not isinstance(max_controls, int)
            or not 2 <= max_controls <= _MAX_AUTO_CHAIN_CONTROLS):
        raise ValueError('Secondary chain length must be an integer from 2 to 32 controls')
    if not isinstance(active_name, str) or not active_name:
        raise ValueError('Choose an active pose control')
    state = obj.b4ml
    if _busy(state):
        raise ValueError('Finish the active pose or correction first')
    mode = _chain_mode(state)
    if mode is None:
        raise ValueError(
            'Direct chain selection requires Local space and Rotation or '
            'World space and Location')
    channel = 'location' if mode == 'WORLD_LOCATION' else 'rotation'
    if bpy.context.screen and bpy.context.screen.is_animation_playing:
        raise ValueError('Stop playback before selecting a secondary chain')
    candidate = state.candidate_action
    if (not candidate or not obj.animation_data
            or obj.animation_data.action != candidate):
        raise ValueError('Generate and select an animation candidate first')
    active = obj.pose.bones.get(active_name)
    if active is None:
        raise ValueError('Active pose control disappeared: ' + active_name)
    category = rig_mapping.structural_category(active.name)
    if category:
        raise ValueError('Active control cannot start a secondary chain: ' + active.name +
                         ' is a ' + category + ' bone, not an animator control')
    if getattr(active.bone, 'hide', False) or getattr(active.bone, 'hide_select', False):
        raise ValueError('Active control cannot start a secondary chain: ' + active.name +
                         ' is hidden or not selectable')
    if channel == 'location':
        if w._channels(active)['location'] != [0, 1, 2]:
            raise ValueError('Active control cannot start a secondary chain: Location is partially locked or connected on ' + active.name)
    elif not w._channels(active)['rotation']:
        raise ValueError('Active control cannot start a secondary chain: Rotation is partially locked on ' + active.name)

    anchors = w.read_anchors(obj)
    captured = set(anchors[0][1]['pose'])
    for _, payload in anchors[1:]:
        captured.intersection_update(payload['pose'])
    curves = w.action_curves(candidate, getattr(obj.animation_data, 'action_slot', None))
    drivers = ({curve.data_path for curve in obj.animation_data.drivers}
               if obj.animation_data else set())
    controls = set(w.profile_for_object(obj).controls)
    eligibility = {}

    def eligible(bone):
        if bone.name not in eligibility:
            eligibility[bone.name] = _eligible_chain_control(
                obj, bone, captured, curves, drivers, controls, channel)
        return eligibility[bone.name]

    valid, reason = eligible(active)
    if not valid:
        raise ValueError('Active control cannot start a secondary chain: ' + reason)
    chain = [active]
    if direction == 'PARENTS':
        current = active
        while len(chain) < max_controls and current.parent is not None:
            current = current.parent
            valid, _ = eligible(current)
            if not valid:
                break
            chain.append(current)
        chain.reverse()
    else:
        current = active
        while len(chain) < max_controls:
            children = []
            for child in current.children:
                valid, _ = eligible(child)
                if valid:
                    children.append(child)
            if len(children) > 1:
                raise ValueError('Active hierarchy branches at ' + current.name +
                                 '; select the intended direct chain manually')
            if not children:
                break
            current = children[0]
            chain.append(current)
    if len(chain) < 2:
        raise ValueError('No second eligible direct control was found from ' + active_name)
    names = [bone.name for bone in chain]
    if _chain_order(obj, names) != names:
        raise ValueError('Derived secondary controls did not form one direct chain')

    selection_before = selected_controls(obj)
    active_before = obj.data.bones.active
    chain_before = bool(state.secondary_chain)
    status_before = state.status
    swap_before = state.secondary_selection_swap
    previous_record = _selection_record(obj, candidate)
    previous_chain_preserved = True
    if previous_record['chain']:
        previous_names = previous_record['selected']
        try:
            if len(previous_names) < 2:
                raise ValueError('too few controls')
            for name in previous_names:
                valid, reason = eligible(obj.pose.bones[name])
                if not valid:
                    raise ValueError(reason)
            _chain_order(obj, previous_names)
        except ValueError:
            # The helper may be invoked precisely because the prior selection
            # cannot drive chain solving. Restore that selection with coupling
            # disabled rather than serializing an unsafe chain state.
            previous_record['chain'] = False
            previous_chain_preserved = False
    try:
        chosen = set(names)
        for bone in obj.pose.bones:
            _set_selected(bone, bone.name in chosen)
        obj.data.bones.active = active.bone
        state.secondary_chain = True
        state.secondary_selection_swap = json.dumps(
            previous_record, sort_keys=True, separators=(',', ':'), allow_nan=False)
        state.status = (f'Selected {len(names)} direct secondary controls from {active_name} '
                        f'toward {direction.lower()}')
    except BaseException:
        saved = set(selection_before)
        for bone in obj.pose.bones:
            try:
                _set_selected(bone, bone.name in saved)
            except (AttributeError, ReferenceError, RuntimeError):
                pass
        try:
            obj.data.bones.active = active_before
            state.secondary_chain = chain_before
            state.secondary_selection_swap = swap_before
            state.status = status_before
        except (AttributeError, ReferenceError, RuntimeError):
            pass
        raise
    return {
        'schema': 1,
        'direction': direction,
        'active_control': active_name,
        'controls': names,
        'control_count': len(names),
        'bounded_maximum': max_controls,
        'semantic_inference': False,
        'candidate_unchanged': True,
        'previous_chain_mode_preserved': previous_chain_preserved,
    }


def request(obj, scene):
    state = obj.b4ml
    impulse_velocity = list(state.secondary_impulse_velocity)
    selected = list(selected_controls(obj))
    stored_loads = _control_load_record(obj)
    control_loads = []
    for name in selected:
        if name not in stored_loads:
            continue
        load = stored_loads[name]
        row = dict(control=name, force=load['force'], mass=load['mass'])
        if load['offset'] != [0.0, 0.0, 0.0] or load['rotational_inertia'] != 1.0:
            row['offset'] = load['offset']
            row['rotational_inertia'] = load['rotational_inertia']
        control_loads.append(row)
    sphere_rows = []
    for item in state.secondary_spheres:
        row = dict(collider=(item.collider.name_full if item.collider else None),
                   radius=float(item.radius))
        if item.moving:
            row['moving'] = True
        if item.scaling:
            row['scaling'] = True
        sphere_rows.append(row)
    result = dict(
        controls=selected,
        space=state.secondary_space,
        rotation=bool(state.secondary_rotation),
        location=bool(state.secondary_location),
        chain=bool(state.secondary_chain),
        chain_propagation=float(state.secondary_chain_propagation),
        frequency=float(state.secondary_frequency),
        damping=float(state.secondary_damping),
        air_friction=float(state.secondary_air_friction),
        wind_velocity=list(state.secondary_wind_velocity),
        impulse_velocity=impulse_velocity,
        impulse_frame=(float(state.secondary_impulse_frame)
                       if any(value != 0.0 for value in impulse_velocity) else None),
        strength=float(state.secondary_strength),
        blend_frames=float(state.secondary_blend_frames),
        gravity_influence=float(state.secondary_gravity),
        gravity=list(scene.gravity) if scene.use_gravity else [0.0, 0.0, 0.0],
        external_acceleration=list(state.secondary_external_acceleration),
        self_collision=bool(state.secondary_self_collision),
        self_collision_radius=float(state.secondary_self_collision_radius),
        control_loads=control_loads,
        collision=bool(state.secondary_collision),
        collision_shape=state.secondary_collision_shape,
        collision_compound_capsule=bool(state.secondary_collision_compound_capsule),
        collision_compound_mesh=bool(state.secondary_collision_compound_mesh),
        collision_clearance=float(state.secondary_collision_clearance),
        restitution=float(state.secondary_restitution),
        surface_friction=float(state.secondary_surface_friction),
        collision_surface=(state.contact_surface.name_full if state.contact_surface else None),
         collision_sphere=(state.secondary_sphere_collider.name_full
                           if state.secondary_sphere_collider else None),
         collision_sphere_radius=float(state.secondary_sphere_radius),
         collision_sphere_continuous=bool(state.secondary_collision_continuous),
         collision_spheres=sphere_rows,
         collision_capsule_start=(state.secondary_capsule_start.name_full
                                  if state.secondary_capsule_start else None),
         collision_capsule_end=(state.secondary_capsule_end.name_full
                                  if state.secondary_capsule_end else None),
         collision_capsule_radius=float(state.secondary_capsule_radius),
         collision_capsule_moving=bool(state.secondary_capsule_moving),
         collision_capsule_scaling=bool(state.secondary_capsule_scaling),
         collision_capsule_continuous=bool(state.secondary_collision_continuous),
         collision_mesh=(state.secondary_collision_mesh.name_full
                         if state.secondary_collision_mesh else None),
         collision_mesh_deforming=bool(state.secondary_collision_mesh_deforming),
         collision_mesh_moving=bool(state.secondary_collision_mesh_moving),
         collision_mesh_volume_radius=float(state.secondary_collision_volume_radius),
         collision_mesh_continuous=bool(state.secondary_collision_continuous),
         support_plane_point=list(state.support_plane_point),
        support_plane_normal=list(state.support_plane_normal),
        fps=float(scene.render.fps),
        fps_base=float(scene.render.fps_base),
        anchors=[(float(item.frame), item.payload) for item in state.anchors],
    )
    if not state.secondary_spheres and state.secondary_sphere_moving:
        result['collision_sphere_moving'] = True
    if not state.secondary_spheres and state.secondary_sphere_scaling:
        result['collision_sphere_scaling'] = True
    return result


def _rotation_spec(bone):
    if bone.rotation_mode == 'QUATERNION':
        return 'rotation_quaternion', 4
    if bone.rotation_mode == 'AXIS_ANGLE':
        return 'rotation_axis_angle', 4
    return 'rotation_euler', 3


def _chain_order(obj, names):
    selected = set(names)
    if len(selected) < 2:
        raise ValueError('Coupled secondary motion needs at least two selected controls')
    children = {name: [] for name in selected}
    roots = []
    for name in selected:
        bone = obj.pose.bones.get(name)
        if bone is None:
            raise ValueError('Selected control disappeared: ' + name)
        parent = bone.parent
        if parent and parent.name in selected:
            children[parent.name].append(name)
        else:
            roots.append(name)
    if len(roots) != 1 or any(len(value) > 1 for value in children.values()):
        raise ValueError('Coupled secondary controls must form one unbranched direct parent-child chain')
    order = []
    current = roots[0]
    while current is not None:
        order.append(current)
        current = children[current][0] if children[current] else None
    if len(order) != len(selected):
        raise ValueError('Coupled secondary controls must form one unbranched direct parent-child chain')
    return order


def _curve_group(curves, path, count, label):
    group = [curves.find(path, index=index) for index in range(count)]
    if all(curve is None for curve in group):
        return None
    if any(curve is None for curve in group):
        raise ValueError(label + ' needs a complete curve group')
    if any(curve.lock or curve.mute or len(curve.modifiers) for curve in group):
        raise ValueError(label + ' curves must be editable, unmuted, and modifier-free')
    return group


def _sample(group, frames):
    return np.array([[curve.evaluate(frame) for curve in group] for frame in frames], dtype=float)


def _as_quaternions(mode, values):
    result = []
    for value in values:
        if mode == 'QUATERNION':
            q = Quaternion(value)
        elif mode == 'AXIS_ANGLE':
            axis = Vector(value[1:])
            if axis.length < 1e-10:
                if abs(value[0]) > 1e-10:
                    raise ValueError('Axis-angle curve contains a zero rotation axis')
                q = Quaternion()
            else:
                q = Quaternion(axis, value[0])
        else:
            q = Euler(value, mode).to_quaternion()
        result.append(tuple(q))
    return sm.normalize_quaternions(result)


def _from_quaternions(mode, quaternions, source):
    if mode == 'QUATERNION':
        result = np.asarray(quaternions, dtype=float).copy()
    elif mode == 'AXIS_ANGLE':
        rows = []
        for value in quaternions:
            axis, angle = Quaternion(value).to_axis_angle()
            rows.append((angle, *axis))
        result = np.asarray(rows, dtype=float)
    else:
        rows = []
        compatible = Euler(source[0], mode)
        for value in quaternions:
            compatible = Quaternion(value).to_euler(mode, compatible)
            rows.append(tuple(compatible))
        result = np.asarray(rows, dtype=float)
    # Priority endpoints are exact raw authored representations, including
    # Euler turns and quaternion signs.
    result[0] = source[0]
    result[-1] = source[-1]
    return result


def _angle(a, b):
    qa = Quaternion(a).normalized()
    qb = Quaternion(b).normalized()
    return 2.0 * math.acos(min(1.0, abs(qa.dot(qb))))


def _write_group_steps(curves, path, values, frames, first, last):
    for index in range(values.shape[1]):
        curve = curves.find(path, index=index)
        if curve is None:
            curve = curves.new(path, index=index)
        first_key=next((key for key in curve.keyframe_points
                        if abs(float(key.co.x)-first)<=1e-8),None)
        last_key=next((key for key in curve.keyframe_points
                       if abs(float(key.co.x)-last)<=1e-8),None)
        incoming=(first_key.handle_left_type,tuple(first_key.handle_left)) if first_key else None
        outgoing=(last_key.interpolation,last_key.handle_right_type,
                  tuple(last_key.handle_right)) if last_key else None
        for key_index in range(len(curve.keyframe_points)-1, -1, -1):
            frame = float(curve.keyframe_points[key_index].co.x)
            if first < frame < last:
                curve.keyframe_points.remove(curve.keyframe_points[key_index], fast=True)
        for sample_index, frame in enumerate(frames):
            key = curve.keyframe_points.insert(float(frame), float(values[sample_index, index]), options={'FAST'})
            if sample_index < len(frames)-1:
                key.interpolation = 'LINEAR'
        curve.update()
        if first_key is not None and incoming is not None:
            first_key.handle_left_type=incoming[0];first_key.handle_left=incoming[1]
        if last_key is not None and outgoing is not None:
            last_key.interpolation=outgoing[0];last_key.handle_right_type=outgoing[1]
            last_key.handle_right=outgoing[2]
        yield index


def _unchanged_generated(obj, action):
    return bool(action.get('b4ml_secondary_token') and
                action.get('b4ml_secondary_name') == action.name and
                action.get('b4ml_secondary_token') == flight._curve_token(obj, action) and
                not action.asset_data)


def restore(obj, scene):
    state = obj.b4ml
    if busy(state):
        raise ValueError('Finish the active correction first')
    output = state.secondary_output
    if (not state.secondary_input or output != state.candidate_action or
            not obj.animation_data or obj.animation_data.action != output):
        raise ValueError('Select the secondary-motion candidate and restore later corrections first')
    removable = _unchanged_generated(obj, output)
    slot = w._slot(obj.animation_data)
    w.assign_action(obj, state.secondary_input, slot)
    state.candidate_action = state.secondary_input
    state.secondary_input = None
    state.secondary_output = None
    state.secondary_metrics = ''
    scene.frame_set(scene.frame_current, subframe=scene.frame_subframe)
    state.status = 'Candidate restored before secondary motion'
    if output.users == 0:
        if removable:
            bpy.data.actions.remove(output)
        else:
            output.use_fake_user = True


def correction_steps(obj, scene):
    started = time.perf_counter()
    w.require_rig(obj)
    w._reject_nla(obj)
    state = obj.b4ml
    if busy(state, allow_secondary=True):
        raise ValueError('Finish the active pose or correction first')
    if bpy.context.screen and bpy.context.screen.is_animation_playing:
        raise ValueError('Stop playback before secondary motion')
    previous = state.candidate_action
    if not previous or not obj.animation_data or obj.animation_data.action != previous:
        raise ValueError('Generate and select an animation candidate first')
    if state.secondary_output and state.secondary_output != previous:
        raise ValueError('Select the last secondary-motion candidate or restore later corrections first')
    if state.secondary_output == previous and not state.secondary_input:
        raise ValueError('Retained secondary-motion input is missing')
    original = state.secondary_input if state.secondary_output == previous else previous
    raw = request(obj, scene)
    if not raw['controls']:
        raise ValueError('Select one or more pose controls for secondary motion')
    if not raw['rotation'] and not raw['location']:
        raise ValueError('Enable rotation or location secondary motion')
    if raw['fps'] <= 0 or raw['fps_base'] <= 0 or not np.isfinite((raw['fps'], raw['fps_base'])).all():
        raise ValueError('Scene frame rate must be positive and finite')
    dt = raw['fps_base'] / raw['fps']
    sm.validate_settings(frequency=raw['frequency'], damping=raw['damping'],
                         air_friction=raw['air_friction'], strength=raw['strength'],
                         blend_frames=raw['blend_frames'], dt=dt)
    if raw['space'] not in ('LOCAL', 'WORLD'):
        raise ValueError('Secondary simulation space must be Local or World')
    if not np.isfinite(raw['chain_propagation']) or not 0.0 <= raw['chain_propagation'] <= 1.0:
        raise ValueError('Secondary chain propagation must be between 0 and 1')
    chain_order = None
    world_location_chain_active = False
    if raw['chain']:
        if raw['space'] == 'LOCAL' and raw['rotation']:
            pass
        elif raw['space'] == 'WORLD' and raw['location']:
            world_location_chain_active = True
        else:
            raise ValueError('Coupled secondary motion requires Local+Rotation or World+Location')
        chain_order = _chain_order(obj, raw['controls'])
    self_collision_active = bool(raw['self_collision'])
    self_collision_effective = self_collision_active and raw['strength'] > 0.0
    if self_collision_active:
        if raw['space'] != 'WORLD' or not raw['location']:
            raise ValueError('Secondary self-collision requires World space and Location')
        if len(raw['controls']) < 2:
            raise ValueError('Secondary self-collision needs at least two selected controls')
        if raw['collision']:
            raise ValueError('Secondary self-collision and an external collider are mutually exclusive')
        sm.resolve_self_collision_positions(
            np.zeros((2, 3)), raw['self_collision_radius'], raw['collision_clearance'])
    external_active = any(value != 0.0 for value in raw['external_acceleration'])
    wind_active = any(value != 0.0 for value in raw['wind_velocity'])
    impulse_active = any(value != 0.0 for value in raw['impulse_velocity'])
    control_loads = {}
    for item in raw['control_loads']:
        acceleration = sm.control_load_acceleration(item['force'], item['mass'])
        offset = item.get('offset', [0.0, 0.0, 0.0])
        inertia = item.get('rotational_inertia', 1.0)
        _, offset, inertia = sm.validate_control_torque_settings(
            item['force'], offset, inertia)
        control_loads[item['control']] = dict(
            force=[float(value) for value in item['force']], mass=float(item['mass']),
            offset=[float(value) for value in offset], rotational_inertia=float(inertia),
            acceleration=[float(value) for value in acceleration])
    load_active = any(any(value != 0.0 for value in item['force'])
                      for item in control_loads.values())
    torque_controls = {name for name, item in control_loads.items()
                       if any(value != 0.0 for value in item['force'])
                       and any(value != 0.0 for value in item['offset'])}
    torque_active = bool(torque_controls)
    local_rotation_chain_torque_active = (
        raw['space'] == 'LOCAL' and raw['chain'] and raw['rotation']
        and not raw['location'] and torque_active
        and set(torque_controls) == set(chain_order or ()))
    if (raw['space'] == 'LOCAL' and raw['chain'] and torque_active
            and not local_rotation_chain_torque_active):
        raise ValueError(
            'Local rotational torque chains require an explicit contiguous chain, '
            'no Location channel, and a nonzero force-at-offset assignment on every '
            'chain control; use World space for the linear force component')
    if world_location_chain_active:
        if (self_collision_active or wind_active or impulse_active
                or (raw['collision'] and raw['collision_shape'] not in {
                    'PLANE', 'SPHERE', 'COMPOUND', 'CAPSULE', 'MESH', 'VOLUME'})):
            raise ValueError('World coupled location chains support one planar, a static or directly animated sphere set, a support-plus-sphere compound with one static or one moving capsule, or a capsule, static surface mesh, or exact static swept-volume collider, gravity, external acceleration, and explicit control loads')
        missing_loads = [name for name in chain_order if name not in control_loads]
        if missing_loads:
            raise ValueError('World coupled location chains require an explicit force/mass assignment for every chain control: ' + ', '.join(missing_loads))
    if raw['space'] == 'LOCAL' and (raw['gravity_influence'] or external_active
                                   or wind_active or impulse_active
                                   or (load_active and not local_rotation_chain_torque_active)
                                   or raw['collision'] or self_collision_active):
        raise ValueError('Secondary gravity, external acceleration, control loads, wind, impulse, and collision require World simulation space')
    if (raw['collision'] or self_collision_active or external_active or wind_active
            or impulse_active or (load_active and not local_rotation_chain_torque_active)) and not raw['location']:
        raise ValueError('Secondary external acceleration, control loads, wind, impulse, and collision require Location')
    if torque_active and not raw['rotation']:
        raise ValueError('Force-at-offset torque requires Rotation')
    if wind_active and raw['air_friction'] <= 0.0:
        raise ValueError('Secondary wind requires Air Friction above zero')
    sm.validate_world_settings(gravity=raw['gravity'],
        gravity_scale=raw['gravity_influence'], external_acceleration=raw['external_acceleration'],
        wind_velocity=raw['wind_velocity'],
        velocity_impulse=raw['impulse_velocity'],
        clearance=raw['collision_clearance'],
        restitution=raw['restitution'], surface_friction=raw['surface_friction'])
    if raw['collision_shape'] not in {'PLANE', 'SPHERE', 'COMPOUND', 'CAPSULE', 'MESH', 'VOLUME'}:
        raise ValueError('Secondary collision shape must be Planar, Sphere, Support + Spheres, Capsule, Mesh, or Closed Volume')
    if (raw['collision'] and raw['collision_shape'] != 'COMPOUND'
            and raw['collision_compound_mesh']):
        raise ValueError('Static compound mesh requires the Support + Spheres collider shape')
    collision_point = collision_normal = collision_triangles = collision_surface = collision_token = None
    collision_sphere_center = collision_sphere_radius = None
    collision_sphere_records = []
    collision_capsule_start = collision_capsule_end = collision_capsule_radius = None
    collision_capsule_trajectories = None
    collision_capsule_endpoint_objects = None
    moving_capsule_active = False
    scaling_capsule_active = False
    collision_capsule_continuous = False
    collision_mesh_triangles = None
    collision_mesh_trajectories = None
    collision_mesh_topology = None
    collision_mesh_deforming = False
    collision_mesh_moving = False
    collision_mesh_trajectory_active = False
    collision_mesh_closed = False
    collision_mesh_volume_radius = 0.0
    collision_mesh_continuous = False
    moving_sphere_active = False
    scaling_sphere_active = False
    moving_sphere_compound_active = False
    moving_sphere_set_compound_active = False
    mixed_moving_sphere_compound_active = False
    mixed_moving_sphere_set_compound_active = False
    moving_sphere_triple_compound_active = False
    mixed_moving_sphere_triple_compound_active = False
    moving_capsule_compound_active = False
    collision_sphere_continuous = False
    if raw['collision']:
        if raw['collision_shape'] in {'SPHERE', 'COMPOUND'}:
            collision_sphere_records, collision_surface, collision_token = _sphere_colliders(
                state, scene, obj)
            moving_sphere_active = any(item['moving'] for item in collision_sphere_records)
            scaling_sphere_active = any(item['scaling'] for item in collision_sphere_records)
            collision_sphere_continuous = bool(raw['collision_sphere_continuous'])
            moving_sphere_compound_active = bool(
                raw['collision_shape'] == 'COMPOUND'
                and moving_sphere_active
                and len(collision_sphere_records) == 1
                and all(item['moving'] for item in collision_sphere_records))
            moving_sphere_count = sum(bool(item['moving'])
                                      for item in collision_sphere_records)
            static_sphere_count = sum(
                not item['moving'] and not item['scaling']
                for item in collision_sphere_records)
            moving_sphere_set_compound_active = bool(
                raw['collision_shape'] == 'COMPOUND'
                and moving_sphere_count == 2
                and static_sphere_count == 0
                and len(collision_sphere_records) == 2
                and all(item['moving'] for item in collision_sphere_records))
            mixed_moving_sphere_compound_active = bool(
                raw['collision_shape'] == 'COMPOUND'
                and moving_sphere_count == 1
                and static_sphere_count >= 1
                and not any(item['scaling'] and not item['moving']
                            for item in collision_sphere_records))
            mixed_moving_sphere_set_compound_active = bool(
                raw['collision_shape'] == 'COMPOUND'
                and moving_sphere_count == 2
                and static_sphere_count >= 1
                and not any(item['scaling'] and not item['moving']
                            for item in collision_sphere_records))
            moving_sphere_triple_compound_active = bool(
                raw['collision_shape'] == 'COMPOUND'
                and moving_sphere_count == 3
                and static_sphere_count == 0
                and len(collision_sphere_records) == 3
                and all(item['moving'] for item in collision_sphere_records))
            mixed_moving_sphere_triple_compound_active = bool(
                raw['collision_shape'] == 'COMPOUND'
                and moving_sphere_count == 3
                and static_sphere_count >= 1
                and not any(item['scaling'] and not item['moving']
                            for item in collision_sphere_records))
            if raw['collision_shape'] == 'COMPOUND' and (
                    moving_sphere_active or scaling_sphere_active
                    or collision_sphere_continuous) and not (
                        moving_sphere_compound_active
                        or moving_sphere_set_compound_active
                        or mixed_moving_sphere_compound_active
                        or mixed_moving_sphere_set_compound_active
                        or moving_sphere_triple_compound_active
                        or mixed_moving_sphere_triple_compound_active):
                moving_capsule_requested = bool(
                    raw['collision_compound_capsule']
                    and raw['collision_capsule_moving']
                    and not moving_sphere_active
                    and not scaling_sphere_active)
                if not moving_capsule_requested:
                    raise ValueError(
                        'Support-plus-sphere compound collision supports static spheres, one to three moving spheres, or one moving capsule')
            if raw['collision_shape'] == 'COMPOUND' and (
                    moving_sphere_compound_active
                    or moving_sphere_set_compound_active
                    or mixed_moving_sphere_compound_active
                    or mixed_moving_sphere_set_compound_active
                    or moving_sphere_triple_compound_active
                    or mixed_moving_sphere_triple_compound_active) and (
                    raw['collision_compound_capsule'] or raw['collision_compound_mesh']):
                raise ValueError(
                    'Moving-sphere compound collision supports only moving spheres and the support surface')
            if raw['collision_shape'] == 'COMPOUND' and raw['collision_compound_mesh'] and (
                    raw['collision_mesh_deforming'] or raw['collision_mesh_moving']
                    or raw['collision_mesh_continuous']):
                raise ValueError(
                    'Support-plus-sphere compound mesh is limited to one static closed mesh')
            if len(collision_sphere_records) == 1 and not (moving_sphere_active or scaling_sphere_active):
                collision_sphere_center = collision_sphere_records[0]['center']
                collision_sphere_radius = collision_sphere_records[0]['radius']
            if raw['collision_shape'] == 'COMPOUND':
                if not world_location_chain_active:
                    raise ValueError(
                        'Support-plus-sphere compound collision requires a World coupled location chain')
                (collision_point, collision_normal, collision_triangles,
                 plane_surface, plane_token) = contacts._plane_surface(state, scene)
                collision_surface = 'COMPOUND:' + plane_surface
                collision_token = (plane_token, collision_token)
                if raw['collision_compound_capsule']:
                    (collision_capsule_start, collision_capsule_end,
                     collision_capsule_radius, capsule_surface,
                     capsule_token) = _capsule_collider(state, scene, obj)
                    moving_capsule_compound_active = bool(
                        raw['collision_capsule_moving']
                        and not moving_sphere_active)
                    if (raw['collision_capsule_scaling']
                            and not raw['collision_capsule_moving']):
                        raise ValueError(
                            'Support-plus-sphere compound does not support scaling-only capsule animation; enable endpoint motion')
                    if (raw['collision_capsule_moving']
                            or raw['collision_capsule_scaling']):
                        if not moving_capsule_compound_active:
                            raise ValueError(
                                'Support-plus-sphere compound moving capsule requires static spheres and no moving sphere')
                        collision_capsule_endpoint_objects = (
                            state.secondary_capsule_start,
                            state.secondary_capsule_end)
                    if (raw['collision_capsule_continuous']
                            and not moving_capsule_compound_active):
                        raise ValueError(
                            'Support-plus-sphere compound capsule is limited to static endpoints')
                    if moving_capsule_compound_active and raw['collision_compound_mesh']:
                        raise ValueError(
                            'Support-plus-sphere compound moving capsule does not combine with a compound mesh')
                    moving_capsule_active = moving_capsule_compound_active
                    scaling_capsule_active = bool(
                        moving_capsule_compound_active and raw['collision_capsule_scaling'])
                    collision_capsule_continuous = bool(raw['collision_capsule_continuous'])
                    collision_surface += ':' + capsule_surface
                    collision_token = (collision_token, capsule_token)
                if raw['collision_compound_mesh']:
                    (collision_mesh_triangles, collision_mesh_closed,
                     mesh_surface, mesh_token) = _mesh_collider_values(
                        state, scene, obj, state.secondary_collision_mesh,
                        False, False)
                    if not collision_mesh_closed:
                        raise ValueError(
                            'Support-plus-sphere compound mesh requires a closed mesh')
                    collision_surface += ':' + mesh_surface
                    collision_token = (collision_token, mesh_token)
        elif raw['collision_shape'] == 'CAPSULE':
            (collision_capsule_start, collision_capsule_end,
             collision_capsule_radius, collision_surface,
             collision_token) = _capsule_collider(state, scene, obj)
            if (world_location_chain_active
                    and raw['collision_capsule_scaling']
                    and not raw['collision_capsule_moving']):
                raise ValueError(
                    'World coupled location chains do not support scaling-only capsule animation; enable endpoint motion when capsule radius scaling is enabled')
            moving_capsule_active = bool(raw['collision_capsule_moving'])
            scaling_capsule_active = bool(raw['collision_capsule_scaling'])
            if moving_capsule_active or scaling_capsule_active:
                collision_capsule_endpoint_objects = (
                    state.secondary_capsule_start, state.secondary_capsule_end)
            collision_capsule_continuous = bool(raw['collision_capsule_continuous'])
        elif raw['collision_shape'] in {'MESH', 'VOLUME'}:
            (collision_mesh_triangles, collision_mesh_closed,
             collision_surface, collision_token) = _mesh_collider(state, scene, obj)
            if raw['collision_shape'] == 'VOLUME' and not collision_mesh_closed:
                raise ValueError('Closed volume collision requires a closed collision mesh')
            collision_mesh_deforming = bool(raw['collision_mesh_deforming'])
            collision_mesh_moving = bool(raw['collision_mesh_moving'])
            collision_mesh_trajectory_active = collision_mesh_deforming or collision_mesh_moving
            collision_mesh_volume_radius = (float(raw['collision_mesh_volume_radius'])
                                            if raw['collision_shape'] == 'VOLUME' else 0.0)
            collision_mesh_continuous = bool(raw['collision_mesh_continuous'])
            if collision_mesh_continuous and not collision_mesh_closed:
                raise ValueError('Continuous mesh collision requires a closed mesh')
            if world_location_chain_active and (
                    raw['collision_shape'] not in {'MESH', 'VOLUME'}
                    or (raw['collision_shape'] == 'MESH'
                        and collision_mesh_volume_radius > 0.0)
                    or (raw['collision_shape'] == 'VOLUME'
                        and (collision_mesh_volume_radius <= 0.0
                             or not collision_mesh_continuous))):
                raise ValueError(
                    'World coupled location chains support one static or sampled '
                    'moving/deforming mesh collider; volume mode requires a closed '
                    'continuous mesh')
            if collision_mesh_trajectory_active:
                surface = state.secondary_collision_mesh
                surface.data.calc_loop_triangles()
                collision_mesh_topology = tuple(
                    tuple(item.vertices) for item in surface.data.loop_triangles)
        else:
            collision_point, collision_normal, collision_triangles, collision_surface, collision_token = contacts._plane_surface(state, scene)
    anchors = w.read_anchors(obj)
    first, last = anchors[0][0], anchors[-1][0]
    if last <= first:
        raise ValueError('Secondary-motion interval must have positive duration')
    if (impulse_active and (not np.isfinite(raw['impulse_frame'])
                            or not first <= raw['impulse_frame'] < last)):
        raise ValueError('Secondary velocity impulse frame must be finite and precede the interval end')
    captured = set(anchors[0][1]['pose'])
    if not set(raw['controls']).issubset(captured):
        raise ValueError('Selected secondary controls must be present in every captured pose')
    priority_frames = [frame for frame, _ in anchors]
    frames = sorted(set(priority_frames) | {float(frame) for frame in range(math.ceil(first), math.floor(last)+1)}
                    | ({raw['impulse_frame']} if impulse_active else set()))
    if len(frames) > w.MAX_FRAMES + 2:
        raise ValueError('Secondary motion exceeds the frame limit')
    if len(frames) * len(raw['controls']) * 7 > w.MAX_KEYS:
        raise ValueError('Secondary motion exceeds the key budget')
    if collision_capsule_endpoint_objects is not None:
        collision_capsule_trajectories = _sample_capsule_trajectories(
            scene, collision_capsule_endpoint_objects[0],
            collision_capsule_endpoint_objects[1], raw['collision_capsule_radius'],
            frames, moving_capsule_active, scaling_capsule_active)
    slot = w._slot(obj.animation_data)
    original_frame = scene.frame_current + scene.frame_subframe
    original_pose = w.raw_pose(obj)
    def control_state(name):
        bone = obj.pose.bones[name]
        data = bone.bone
        return (name, bone.rotation_mode, w._channels(bone), data.parent.name if data.parent else None,
                tuple(value for row in data.matrix_local for value in row))
    control_signature = [control_state(name) for name in raw['controls']]
    original_token = flight._curve_token(obj, original)
    curves = w.action_curves(original, getattr(obj.animation_data, 'action_slot', None))
    drivers = {driver.data_path for driver in obj.animation_data.drivers}
    if raw['collision'] and raw['collision_shape'] == 'SPHERE':
        radius_paths = ([item.path_from_id('radius')
                         for item in state.secondary_spheres] if state.secondary_spheres else
                        [state.path_from_id('secondary_sphere_radius')])
        if any(curve.data_path in radius_paths for curve in curves) or any(
                path in drivers for path in radius_paths):
            raise ValueError('Secondary sphere radius must be static without keys or drivers')
    if raw['collision'] and raw['collision_shape'] == 'CAPSULE':
        capsule_radius_path = state.path_from_id('secondary_capsule_radius')
        if any(curve.data_path == capsule_radius_path for curve in curves) or capsule_radius_path in drivers:
            raise ValueError('Secondary capsule radius must be static without keys or drivers')
    envelope = sm.priority_envelope(frames, priority_frames, raw['blend_frames'])
    plans = []
    rotation_max = 0.0
    location_max = 0.0
    world_collision_samples = 0
    world_collision_sweep_samples = 0
    self_collision_samples = 0
    max_self_collision_penetration = 0.0
    max_raw_penetration = 0.0
    max_penetration_before = 0.0
    max_penetration_after = 0.0
    max_control_torque = 0.0
    max_control_angular_acceleration = 0.0
    candidate = None
    committed = False

    def select_action(action):
        if obj.animation_data.action != action or w._slot(obj.animation_data) != slot:
            w.assign_action(obj, action, slot)

    def current_collision_token():
        if raw['collision_shape'] in {'SPHERE', 'COMPOUND'}:
            sphere_token = _sphere_colliders(state, scene, obj)[2]
            if raw['collision_shape'] == 'COMPOUND':
                compound_token = (contacts._plane_surface(state, scene)[4], sphere_token)
                if raw['collision_compound_capsule']:
                    compound_token = (compound_token, _capsule_collider(state, scene, obj)[4])
                if raw['collision_compound_mesh']:
                    mesh_token = _mesh_collider_values(
                        state, scene, obj, state.secondary_collision_mesh,
                        False, False)[3]
                    compound_token = (compound_token, mesh_token)
                return compound_token
            return sphere_token
        if raw['collision_shape'] == 'CAPSULE':
            return _capsule_collider(state, scene, obj)[4]
        if raw['collision_shape'] in {'MESH', 'VOLUME'}:
            return _mesh_collider(state, scene, obj)[3]
        return contacts._plane_surface(state, scene)[4]

    def guard_collision():
        if collision_token is not None and current_collision_token() != collision_token:
            raise ValueError('Secondary collision surface changed during correction')

    def guard(full=False):
        if busy(state, allow_secondary=True):
            raise ValueError('Another pose or correction started during secondary motion')
        if state.candidate_action != previous or obj.animation_data.action not in (original, candidate):
            raise ValueError('Candidate changed during secondary motion')
        if request(obj, scene) != raw:
            raise ValueError('Secondary selection or settings changed during correction')
        if full and flight._curve_token(obj, original) != original_token:
            raise ValueError('Input animation changed during secondary motion')
        if [control_state(name) for name in raw['controls']] != control_signature:
            raise ValueError('Rig or selected control channels changed during secondary motion')
        guard_collision()
        if abs((scene.frame_current + scene.frame_subframe) - original_frame) > 1e-5:
            raise ValueError('Playhead changed during secondary motion')

    try:
        select_action(original)
        definitions = []
        for name in raw['controls']:
            bone = obj.pose.bones.get(name)
            if bone is None:
                raise ValueError('Selected control disappeared: ' + name)
            channels = w._channels(bone)
            definition = dict(name=name, mode=bone.rotation_mode)
            if raw['rotation']:
                if not channels['rotation']:
                    raise ValueError('Rotation is partially locked on selected control: ' + name)
                prop, count = _rotation_spec(bone)
                path = bone.path_from_id(prop)
                if path in drivers:
                    raise ValueError('Selected rotation is driven: ' + name)
                group = _curve_group(curves, path, count, name + ' rotation')
                if name in torque_controls and group is None:
                    raise ValueError('Force-at-offset torque requires complete editable rotation curves on every loaded control: ' + name)
                if group is not None:
                    definition['rotation_path'] = path
                    definition['rotation_source'] = _sample(group, frames)
            if raw['location']:
                path = bone.path_from_id('location')
                if path in drivers:
                    raise ValueError('Selected location is driven: ' + name)
                group = _curve_group(curves, path, 3, name + ' location')
                if (external_active or wind_active or impulse_active or load_active
                        or world_location_chain_active) and group is None:
                    raise ValueError('External acceleration, control loads, wind, and impulse require complete editable location curves on every selected control: ' + name)
                if group is not None:
                    if len(channels['location']) != 3:
                        raise ValueError('Location is partially locked or connected on selected control: ' + name)
                    definition['location_path'] = path
                    definition['location_source'] = _sample(group, frames)
            if len(definition) > 2:
                definitions.append(definition)
            yield dict(phase='Preparing selected controls', frame=first, total=len(raw['controls']))
        guard()
        yield dict(phase='Selected controls ready', frame=first, total=len(definitions))
        if not definitions:
            raise ValueError('Selected controls have no complete animated transform curves in this candidate')
        if self_collision_active and (len(definitions) != len(raw['controls'])
                                      or any('location_source' not in definition
                                             for definition in definitions)):
            raise ValueError('Secondary self-collision requires complete editable location curves on every selected control')

        if chain_order is not None:
            definitions_by_name = {definition['name']: definition for definition in definitions}
            chain_source = ('location_source' if world_location_chain_active
                            else 'rotation_source')
            if (set(definitions_by_name) != set(chain_order)
                    or any(chain_source not in definitions_by_name[name] for name in chain_order)):
                raise ValueError('Every coupled chain control needs a complete editable '
                                 + ('location' if world_location_chain_active else 'rotation')
                                 + ' curve group')
            definitions = [definitions_by_name[name] for name in chain_order]

        world_chain_report = None
        local_chain_report = None
        if raw['space'] == 'LOCAL':
            if local_rotation_chain_torque_active:
                for definition in definitions:
                    definition['world_rotations'] = []
                for frame in frames:
                    scene.frame_set(math.floor(frame), subframe=frame-math.floor(frame))
                    displayed = w.display_world(obj)
                    for definition in definitions:
                        definition['world_rotations'].append(tuple(
                            (displayed @ obj.pose.bones[definition['name']].matrix).to_quaternion()))
                    scene.frame_set(math.floor(original_frame), subframe=original_frame-math.floor(original_frame))
                    yield dict(phase='Sampling local torque orientations', frame=frame,
                               total=len(frames))
                    guard()
            if chain_order is not None:
                targets = np.stack([
                    _as_quaternions(definition['mode'], definition['rotation_source'])
                    for definition in definitions
                ], axis=1)
                if local_rotation_chain_torque_active:
                    angular_accelerations = []
                    inertias = []
                    for definition in definitions:
                        load = control_loads[definition['name']]
                        orientations = sm.normalize_quaternions(
                            np.asarray(definition['world_rotations'], dtype=float))
                        torques, angular_world = sm.control_load_angular_acceleration(
                            load['force'], load['offset'], load['rotational_inertia'],
                            orientations)
                        angular_local = np.asarray([
                            tuple(Quaternion(tuple(orientation)).inverted()
                                  @ Vector(vector))
                            for orientation, vector in zip(orientations, angular_world)
                        ], dtype=float)
                        definition['control_torques'] = torques
                        definition['control_angular_accelerations'] = angular_world
                        angular_accelerations.append(angular_local)
                        inertias.append(load['rotational_inertia'])
                        max_control_torque = max(
                            max_control_torque,
                            float(np.max(np.linalg.norm(torques, axis=1))))
                        max_control_angular_acceleration = max(
                            max_control_angular_acceleration,
                            float(np.max(np.linalg.norm(angular_world, axis=1))))
                    followed_chain, local_chain_report = sm.follow_forced_quaternion_chain(
                        targets, np.diff(frames), dt=dt, frequency=raw['frequency'],
                        damping=raw['damping'], air_friction=raw['air_friction'],
                        strength=raw['strength'], envelope=envelope,
                        propagation=raw['chain_propagation'], inertias=inertias,
                        angular_accelerations=np.stack(angular_accelerations, axis=1),
                        coupling_passes=(2 if len(chain_order) >= 3 else 1),
                        return_report=True)
                else:
                    followed_chain = sm.follow_quaternion_chain(
                        targets, np.diff(frames), dt=dt, frequency=raw['frequency'],
                        damping=raw['damping'], air_friction=raw['air_friction'],
                        strength=raw['strength'], envelope=envelope,
                        propagation=raw['chain_propagation'])
                for control_index, definition in enumerate(definitions):
                    source = definition['rotation_source']
                    followed = followed_chain[:, control_index, :]
                    output = _from_quaternions(definition['mode'], followed, source)
                    for index, frame in enumerate(frames):
                        if any(abs(frame-priority) < 1e-8 for priority in priority_frames):
                            output[index] = source[index]
                    rotation_max = max(rotation_max, max(
                        _angle(a, b) for a, b in zip(targets[:, control_index, :], followed)))
                    plans.append(dict(name=definition['name'], kind='rotation',
                                      path=definition['rotation_path'], values=output))
                    yield dict(phase='Simulating coupled rotation chain', frame=first,
                               total=len(definitions))
                guard()
            for definition in definitions:
                if 'rotation_source' in definition:
                    if chain_order is None:
                        source = definition['rotation_source']
                        targets = _as_quaternions(definition['mode'], source)
                        followed = sm.follow_quaternions(targets, np.diff(frames), dt=dt,
                            frequency=raw['frequency'], damping=raw['damping'],
                            air_friction=raw['air_friction'], strength=raw['strength'], envelope=envelope)
                        output = _from_quaternions(definition['mode'], followed, source)
                        for index, frame in enumerate(frames):
                            if any(abs(frame-priority) < 1e-8 for priority in priority_frames):
                                output[index] = source[index]
                        rotation_max = max(rotation_max, max(_angle(a, b) for a, b in zip(targets, followed)))
                        plans.append(dict(name=definition['name'], kind='rotation',
                                          path=definition['rotation_path'], values=output))
                if 'location_source' in definition:
                    source = definition['location_source']
                    output = sm.apply_vector_follow(source, frames, dt=dt,
                        frequency=raw['frequency'], damping=raw['damping'],
                        air_friction=raw['air_friction'], strength=raw['strength'],
                        blend_frames=raw['blend_frames'], envelope=envelope)
                    location_max = max(location_max, float(np.max(np.linalg.norm(output-source, axis=1))))
                    plans.append(dict(name=definition['name'], kind='location',
                                      path=definition['location_path'], values=output))
                yield dict(phase='Simulating local controls', frame=first, total=len(definitions))
            guard()
        else:
            world_matrix = obj.matrix_world.copy()
            for definition in definitions:
                definition['world_locations'] = []
                definition['world_rotations'] = []
                definition['world_scales'] = []
            for item in collision_sphere_records:
                item['centers'] = []
                item['radii'] = []
            if collision_mesh_trajectory_active:
                collision_mesh_trajectories = []
            for frame in frames:
                scene.frame_set(math.floor(frame), subframe=frame-math.floor(frame))
                guard_collision()
                if obj.matrix_world != world_matrix:
                    raise ValueError('Animated armature object transforms are not supported by world secondary motion')
                if collision_mesh_trajectory_active:
                    collision_mesh_trajectories.append(_sample_deforming_mesh(
                        state.secondary_collision_mesh, collision_mesh_topology, scene))
                for item in collision_sphere_records:
                    center = (item['collider'].matrix_world.translation.copy()
                              if item['moving'] else item['center'])
                    radius = item['radius']
                    if item['scaling']:
                        scale = tuple(float(value) for value in
                                      item['collider'].matrix_world.to_scale())
                        if (not all(math.isfinite(value) and value > 0.0 for value in scale)
                                or max(scale)-min(scale) > 1e-6*max(1.0, max(scale))):
                            raise ValueError('Animated sphere radius requires positive uniform evaluated scale')
                        radius *= sum(scale)/3.0
                    center, radius = sm.validate_sphere_collider(tuple(center), radius)
                    item['centers'].append(tuple(center))
                    item['radii'].append(radius)
                displayed = w.display_world(obj)
                for definition in definitions:
                    matrix = displayed @ obj.pose.bones[definition['name']].matrix
                    definition['world_locations'].append(tuple(matrix.translation))
                    definition['world_rotations'].append(tuple(matrix.to_quaternion()))
                    definition['world_scales'].append(tuple(matrix.to_scale()))
                scene.frame_set(math.floor(original_frame), subframe=original_frame-math.floor(original_frame))
                yield dict(phase='Sampling evaluated world controls', frame=frame, total=len(frames))
                guard()

            world_chain_report = None
            if world_location_chain_active:
                chain_locations = np.stack([
                    np.asarray(definition['world_locations'], dtype=float)
                    for definition in definitions
                ], axis=1)
                if raw['collision'] and raw['strength'] > 0.0:
                    for control_index, definition in enumerate(definitions):
                        for sample_index, frame in enumerate(frames):
                            if not any(abs(frame-priority) < 1e-8
                                       for priority in priority_frames):
                                continue
                            point = Vector(chain_locations[sample_index, control_index])
                            if raw['collision_shape'] in {'SPHERE', 'COMPOUND'}:
                                penetrations = []
                                for item in collision_sphere_records:
                                    sphere_center = (item['centers'][sample_index]
                                                     if moving_sphere_active
                                                     or scaling_sphere_active
                                                     else item['center'])
                                    sphere_radius = (item['radii'][sample_index]
                                                     if scaling_sphere_active
                                                     else item['radius'])
                                    penetrations.append(
                                        (point-Vector(sphere_center)).length
                                        - sphere_radius
                                        - raw['collision_clearance'])
                                priority_penetration = min(penetrations, default=0.0)
                                if raw['collision_shape'] == 'COMPOUND':
                                    projected = point-collision_normal * float(
                                        (point-collision_point).dot(collision_normal))
                                    plane_penetration = (
                                        (point-collision_point).dot(collision_normal)
                                        - raw['collision_clearance']
                                        if contacts._inside_surface(
                                            projected, collision_triangles)
                                        else 0.0)
                                    priority_penetration = min(
                                        priority_penetration, plane_penetration)
                                    if raw['collision_compound_capsule']:
                                        active_start = (collision_capsule_trajectories[0][sample_index]
                                                        if collision_capsule_trajectories is not None
                                                        else collision_capsule_start)
                                        active_end = (collision_capsule_trajectories[1][sample_index]
                                                      if collision_capsule_trajectories is not None
                                                      else collision_capsule_end)
                                        active_radius = (collision_capsule_trajectories[2][sample_index]
                                                         if collision_capsule_trajectories is not None
                                                         else collision_capsule_radius)
                                        closest = Vector(sm._capsule_closest(
                                            np.asarray(point),
                                            np.asarray(active_start),
                                            np.asarray(active_end)))
                                        priority_penetration = min(
                                            priority_penetration,
                                            (point-closest).length
                                            - active_radius
                                            - raw['collision_clearance'])
                                    if raw['collision_compound_mesh']:
                                        mesh_state = sm.mesh_collision_state(
                                            tuple(point), collision_mesh_triangles,
                                            raw['collision_clearance'],
                                            collision_mesh_closed)
                                        if mesh_state[0]:
                                            priority_penetration = min(
                                                priority_penetration,
                                                -float(mesh_state[3]))
                            elif raw['collision_shape'] == 'CAPSULE':
                                active_start = (collision_capsule_trajectories[0][sample_index]
                                                if collision_capsule_trajectories is not None
                                                else collision_capsule_start)
                                active_end = (collision_capsule_trajectories[1][sample_index]
                                              if collision_capsule_trajectories is not None
                                              else collision_capsule_end)
                                active_radius = (collision_capsule_trajectories[2][sample_index]
                                                 if collision_capsule_trajectories is not None
                                                 else collision_capsule_radius)
                                closest = Vector(sm._capsule_closest(
                                    np.asarray(point),
                                    np.asarray(active_start),
                                    np.asarray(active_end)))
                                priority_penetration = (
                                    (point-closest).length
                                    - active_radius
                                    - raw['collision_clearance'])
                            elif raw['collision_shape'] in {'MESH', 'VOLUME'}:
                                active_mesh = (collision_mesh_trajectories[sample_index]
                                               if collision_mesh_trajectory_active
                                               else collision_mesh_triangles)
                                mesh_state = sm.mesh_collision_state(
                                    tuple(point), active_mesh,
                                    raw['collision_clearance'], collision_mesh_closed,
                                    (tuple(chain_locations[sample_index,
                                           control_index]-np.asarray(point)),),
                                    collision_mesh_volume_radius)
                                priority_penetration = (
                                    -float(mesh_state[3]) if mesh_state[0] else 0.0)
                            else:
                                projected = point-collision_normal * float(
                                    (point-collision_point).dot(collision_normal))
                                priority_penetration = (
                                    (point-collision_point).dot(collision_normal)
                                    - raw['collision_clearance']
                                    if contacts._inside_surface(projected, collision_triangles)
                                    else 0.0)
                            if priority_penetration < -1e-6:
                                raise ValueError(
                                    'Secondary collision conflicts with an authored priority pose; '
                                    'adjust the collider, clearance, or priority pose')
                chain_masses = np.asarray([
                    control_loads[name]['mass'] for name in chain_order
                ], dtype=float)
                scene_acceleration = (np.asarray(raw['gravity'], dtype=float)
                                      * raw['gravity_influence']
                                      + np.asarray(raw['external_acceleration'], dtype=float))
                chain_accelerations = np.asarray([
                    np.asarray(control_loads[name]['acceleration'], dtype=float)
                    + scene_acceleration for name in chain_order
                ], dtype=float)
                followed_locations, world_chain_report = sm.follow_world_vector_chain(
                    chain_locations, np.diff(frames), dt=dt,
                    frequency=raw['frequency'], damping=raw['damping'],
                    air_friction=raw['air_friction'], strength=raw['strength'],
                    envelope=envelope, propagation=raw['chain_propagation'],
                    coupling_passes=(2 if len(chain_order) >= 3 else 1),
                    masses=chain_masses, accelerations=chain_accelerations,
                    collision_point=(tuple(collision_point)
                                     if raw['collision']
                                     and raw['collision_shape'] in {'PLANE', 'COMPOUND'}
                                     else None),
                    collision_normal=(tuple(collision_normal)
                                      if raw['collision']
                                      and raw['collision_shape'] in {'PLANE', 'COMPOUND'}
                                      else None),
                    clearance=raw['collision_clearance'],
                    restitution=raw['restitution'],
                    surface_friction=raw['surface_friction'],
                    collision_triangles=([
                        [tuple(vertex) for vertex in triangle]
                        for triangle in collision_triangles
                    ] if raw['collision'] and collision_triangles is not None else None),
                    collision_sphere_center=(tuple(collision_sphere_center)
                                             if raw['collision']
                                             and raw['collision_shape'] in {'SPHERE', 'COMPOUND'}
                                             and collision_sphere_center is not None
                                             else None),
                    collision_sphere_radius=(collision_sphere_radius
                                             if raw['collision']
                                             and raw['collision_shape'] in {'SPHERE', 'COMPOUND'}
                                             and collision_sphere_center is not None
                                             else None),
                    collision_spheres=([(item['center'], item['radius'])
                                       for item in collision_sphere_records
                                       if not item['moving'] and not item['scaling']]
                                       if raw['collision']
                                       and raw['collision_shape'] in {'SPHERE', 'COMPOUND'}
                                       and collision_sphere_records
                                       and any(not item['moving'] and not item['scaling']
                                               for item in collision_sphere_records)
                                       and (raw['collision_shape'] == 'COMPOUND'
                                            or not (moving_sphere_active or scaling_sphere_active))
                                       else None),
                    collision_sphere_trajectories=([(
                        (item['centers'] if item['moving'] or item['scaling']
                         else np.repeat(np.asarray(item['center'], dtype=float)[None, :],
                                        len(frames), axis=0)),
                        item['radii'] if item['scaling'] else item['radius'])
                        for item in collision_sphere_records
                        if (item['moving'] or item['scaling']
                            or raw['collision_shape'] == 'SPHERE')]
                        if raw['collision'] and raw['collision_shape'] in {'SPHERE', 'COMPOUND'}
                        and (moving_sphere_active or scaling_sphere_active) else None),
                    collision_sphere_continuous=(collision_sphere_continuous
                                                 if raw['collision']
                                                 and raw['collision_shape'] in {'SPHERE', 'COMPOUND'}
                                                 else False),
                    compound_plane_spheres=(raw['collision']
                                            and raw['collision_shape'] == 'COMPOUND'),
                     compound_static_capsule=(raw['collision']
                                              and raw['collision_shape'] == 'COMPOUND'
                                              and raw['collision_compound_capsule']
                                              and not moving_capsule_compound_active),
                     compound_moving_capsule=(raw['collision']
                                              and raw['collision_shape'] == 'COMPOUND'
                                              and moving_capsule_compound_active),
                    compound_static_mesh=(raw['collision']
                                          and raw['collision_shape'] == 'COMPOUND'
                                          and raw['collision_compound_mesh']),
                    collision_capsule_start=(tuple(collision_capsule_start)
                                             if raw['collision']
                                             and (raw['collision_shape'] == 'CAPSULE'
                                                  or (raw['collision_shape'] == 'COMPOUND'
                                                      and raw['collision_compound_capsule']))
                                             and collision_capsule_trajectories is None
                                             else None),
                    collision_capsule_end=(tuple(collision_capsule_end)
                                           if raw['collision']
                                           and (raw['collision_shape'] == 'CAPSULE'
                                                or (raw['collision_shape'] == 'COMPOUND'
                                                    and raw['collision_compound_capsule']))
                                           and collision_capsule_trajectories is None
                                           else None),
                    collision_capsule_radius=(collision_capsule_radius
                                              if raw['collision']
                                              and (raw['collision_shape'] == 'CAPSULE'
                                                   or (raw['collision_shape'] == 'COMPOUND'
                                                       and raw['collision_compound_capsule']))
                                              and collision_capsule_trajectories is None
                                              else None),
                     collision_capsule_trajectories=(
                         collision_capsule_trajectories
                         if raw['collision'] and (
                             raw['collision_shape'] == 'CAPSULE'
                             or (raw['collision_shape'] == 'COMPOUND'
                                 and moving_capsule_compound_active))
                         else None),
                     collision_capsule_continuous=(collision_capsule_continuous
                                                   if raw['collision']
                                                   and (raw['collision_shape'] == 'CAPSULE'
                                                        or (raw['collision_shape'] == 'COMPOUND'
                                                            and moving_capsule_compound_active))
                                                   else False),
                    collision_mesh_triangles=([ 
                        [tuple(vertex) for vertex in triangle]
                        for triangle in collision_mesh_triangles
                    ] if raw['collision']
                                           and (raw['collision_shape'] in {'MESH', 'VOLUME'}
                                                or (raw['collision_shape'] == 'COMPOUND'
                                                    and raw['collision_compound_mesh']))
                                           and not collision_mesh_trajectory_active
                                           else None),
                    collision_mesh_trajectories=(
                        collision_mesh_trajectories
                        if raw['collision']
                        and raw['collision_shape'] in {'MESH', 'VOLUME'}
                        and collision_mesh_trajectory_active
                        else None),
                    collision_mesh_closed=(collision_mesh_closed
                                           if raw['collision']
                                           and (raw['collision_shape'] in {'MESH', 'VOLUME'}
                                                or (raw['collision_shape'] == 'COMPOUND'
                                                    and raw['collision_compound_mesh']))
                                           else False),
                    collision_mesh_volume_radius=(collision_mesh_volume_radius
                                                  if raw['collision']
                                                  and raw['collision_shape'] in {'MESH', 'VOLUME'}
                                                  else 0.0),
                    collision_mesh_continuous=(collision_mesh_continuous
                                               if raw['collision']
                                               and raw['collision_shape'] in {'MESH', 'VOLUME'}
                                               else False))
                location_max = max(
                    location_max,
                    float(np.max(np.linalg.norm(followed_locations-chain_locations, axis=2))))
                world_collision_samples += world_chain_report['collision_samples']
                world_collision_sweep_samples += world_chain_report.get(
                    'continuous_collision_samples', 0)
                max_raw_penetration = max(
                    max_raw_penetration, world_chain_report['max_raw_penetration'])
                max_penetration_after = max(
                    max_penetration_after, world_chain_report['max_penetration_after'])

            for definition in definitions:
                locations = np.asarray(definition['world_locations'], dtype=float)
                rotations = sm.normalize_quaternions(definition['world_rotations'])
                definition['desired_locations'] = locations.copy()
                definition['desired_rotations'] = rotations.copy()
                if world_location_chain_active:
                    control_index = chain_order.index(definition['name'])
                    definition['desired_locations'] = followed_locations[:, control_index, :]
                if 'rotation_source' in definition:
                    load = control_loads.get(definition['name'])
                    if definition['name'] in torque_controls:
                        torques, angular = sm.control_load_angular_acceleration(
                            load['force'], load['offset'], load['rotational_inertia'], rotations)
                        definition['control_torques'] = torques
                        definition['control_angular_accelerations'] = angular
                        max_control_torque = max(
                            max_control_torque,
                            float(np.max(np.linalg.norm(torques, axis=1))))
                        max_control_angular_acceleration = max(
                            max_control_angular_acceleration,
                            float(np.max(np.linalg.norm(angular, axis=1))))
                        followed = sm.follow_forced_quaternions(
                            rotations, np.diff(frames), dt=dt,
                            frequency=raw['frequency'], damping=raw['damping'],
                            air_friction=raw['air_friction'], strength=raw['strength'],
                            envelope=envelope, angular_accelerations=angular)
                    else:
                        followed = sm.follow_quaternions(
                            rotations, np.diff(frames), dt=dt,
                            frequency=raw['frequency'], damping=raw['damping'],
                            air_friction=raw['air_friction'], strength=raw['strength'],
                            envelope=envelope)
                    definition['desired_rotations'] = followed
                    rotation_max = max(rotation_max, max(_angle(a, b) for a, b in zip(rotations, followed)))
                if 'location_source' in definition and not world_location_chain_active:
                    mask = None
                    if raw['collision']:
                        mask = [True] * len(locations)
                        for index, frame in enumerate(frames):
                            point = Vector(locations[index])
                            if raw['collision_shape'] == 'SPHERE':
                                inside = any(
                                    (point-Vector(item['centers'][index])).length-item['radii'][index]
                                    - raw['collision_clearance'] < -1e-6
                                    for item in collision_sphere_records)
                            elif raw['collision_shape'] == 'CAPSULE':
                                active_start = (collision_capsule_trajectories[0][index]
                                                 if collision_capsule_trajectories is not None
                                                 else np.asarray(collision_capsule_start, dtype=float))
                                active_end = (collision_capsule_trajectories[1][index]
                                               if collision_capsule_trajectories is not None
                                               else np.asarray(collision_capsule_end, dtype=float))
                                active_radius = (collision_capsule_trajectories[2][index]
                                                  if collision_capsule_trajectories is not None
                                                  else collision_capsule_radius)
                                closest = Vector(sm._capsule_closest(
                                    np.asarray(point, dtype=float),
                                    active_start, active_end))
                                inside = ((point-closest).length
                                          - active_radius
                                          - raw['collision_clearance'] < -1e-6)
                            elif raw['collision_shape'] in {'MESH', 'VOLUME'}:
                                active_mesh = (collision_mesh_trajectories[index]
                                               if collision_mesh_trajectory_active
                                               else collision_mesh_triangles)
                                inside = sm.mesh_collision_state(
                                    tuple(point), active_mesh,
                                    raw['collision_clearance'], collision_mesh_closed,
                                    (tuple(locations[index]-locations[max(0, index-1)]),),
                                    collision_mesh_volume_radius)[0]
                            else:
                                projected = point-collision_normal*(point-collision_point).dot(collision_normal)
                                inside = (contacts._inside_surface(projected, collision_triangles)
                                          and (point-collision_point).dot(collision_normal)
                                          < raw['collision_clearance']-1e-6)
                            if (raw['strength'] > 0.0 and inside
                                    and any(abs(frame-priority) < 1e-8
                                            for priority in priority_frames)):
                                raise ValueError('Secondary collision conflicts with an authored priority pose; adjust the collider, clearance, or priority pose')
                    load = control_loads.get(definition['name'])
                    control_acceleration = (load['acceleration'] if load else (0.0, 0.0, 0.0))
                    followed, world_report = sm.apply_world_vector_follow(
                        locations, frames, dt=dt, frequency=raw['frequency'],
                        damping=raw['damping'], air_friction=raw['air_friction'],
                        strength=raw['strength'], blend_frames=raw['blend_frames'],
                        gravity=raw['gravity'], gravity_scale=raw['gravity_influence'],
                        external_acceleration=raw['external_acceleration'],
                        control_acceleration=control_acceleration,
                        wind_velocity=raw['wind_velocity'],
                        velocity_impulse=raw['impulse_velocity'],
                        impulse_index=(frames.index(raw['impulse_frame'])
                                       if impulse_active else None),
                        collision_point=(tuple(collision_point)
                                         if collision_point is not None else None),
                        collision_normal=(tuple(collision_normal)
                                          if collision_normal is not None else None),
                        clearance=raw['collision_clearance'], restitution=raw['restitution'],
                        surface_friction=raw['surface_friction'], collision_mask=mask,
                        collision_triangles=[[tuple(vertex) for vertex in triangle] for triangle in collision_triangles] if collision_triangles is not None else None,
                        collision_sphere_center=(tuple(collision_sphere_center)
                                                 if collision_sphere_center is not None else None),
                        collision_sphere_radius=collision_sphere_radius,
                        collision_spheres=([(tuple(item['center']), item['radius'])
                                            for item in collision_sphere_records]
                                           if len(collision_sphere_records) > 1
                                           and not (moving_sphere_active or scaling_sphere_active) else None),
                         collision_sphere_trajectories=([
                            (item['centers'], item['radii'] if item['scaling'] else item['radius'])
                             for item in collision_sphere_records]
                             if moving_sphere_active or scaling_sphere_active else None),
                         collision_sphere_continuous=(collision_sphere_continuous
                                                      if raw['collision']
                                                      and raw['collision_shape'] == 'SPHERE'
                                                      else False),
                         collision_capsule_start=(tuple(collision_capsule_start)
                                                  if collision_capsule_start is not None
                                                  and collision_capsule_trajectories is None else None),
                         collision_capsule_end=(tuple(collision_capsule_end)
                                                if collision_capsule_end is not None
                                                and collision_capsule_trajectories is None else None),
                         collision_capsule_radius=(collision_capsule_radius
                                                   if collision_capsule_trajectories is None else None),
                         collision_capsule_trajectories=collision_capsule_trajectories,
                         collision_mesh_triangles=(None if collision_mesh_trajectory_active
                                                   else collision_mesh_triangles),
                         collision_mesh_trajectories=collision_mesh_trajectories,
                         collision_mesh_closed=collision_mesh_closed,
                         collision_mesh_volume_radius=collision_mesh_volume_radius,
                         collision_mesh_continuous=collision_mesh_continuous,
                         collision_capsule_continuous=collision_capsule_continuous,
                         envelope=envelope)
                    definition['desired_locations'] = followed
                    location_max = max(location_max, world_report['max_world_correction'])
                    world_collision_samples += world_report['collision_samples']
                    world_collision_sweep_samples += world_report.get(
                        'continuous_collision_samples', 0)
                    max_raw_penetration = max(max_raw_penetration, world_report['max_raw_penetration'])
                    max_penetration_before = max(max_penetration_before, world_report['max_penetration_before'])
                    max_penetration_after = max(max_penetration_after, world_report['max_penetration_after'])
                definition['local_locations'] = []
                definition['local_rotations'] = []

            if self_collision_effective:
                for sample_index, frame in enumerate(frames):
                    authored = any(abs(frame-priority) < 1e-8
                                   for priority in priority_frames)
                    points = np.stack([
                        (definition['world_locations'][sample_index]
                         if authored else definition['desired_locations'][sample_index])
                        for definition in definitions])
                    resolved, self_report = sm.resolve_self_collision_positions(
                        points, raw['self_collision_radius'], raw['collision_clearance'])
                    if authored and self_report['max_raw_penetration'] > 1e-8:
                        raise ValueError(
                            'Secondary self-collision conflicts with an authored priority pose; '
                            'adjust the self radius or clearance')
                    if not authored:
                        for control_index, definition in enumerate(definitions):
                            correction = float(np.linalg.norm(
                                resolved[control_index]-points[control_index]))
                            location_max = max(location_max, correction)
                            definition['desired_locations'][sample_index] = resolved[control_index]
                    if self_report['collision_pairs']:
                        self_collision_samples += 1
                        max_self_collision_penetration = max(
                            max_self_collision_penetration,
                            self_report['max_raw_penetration'])

            for sample_index, frame in enumerate(frames):
                scene.frame_set(math.floor(frame), subframe=frame-math.floor(frame))
                guard_collision()
                displayed = w.display_world(obj)
                inverse = displayed.inverted()
                sample_pose = w.raw_pose(obj)
                desired_pose_matrices = {}
                ordered_definitions = sorted(
                    definitions,
                    key=lambda definition: len(obj.pose.bones[definition['name']].parent_recursive))
                for definition in ordered_definitions:
                    desired = Matrix.LocRotScale(
                        Vector(definition['desired_locations'][sample_index]),
                        Quaternion(definition['desired_rotations'][sample_index]),
                        Vector(definition['world_scales'][sample_index]))
                    desired_pose_matrices[definition['name']] = inverse @ desired
                for definition in ordered_definitions:
                    pose_bone = obj.pose.bones[definition['name']]
                    desired_pose = desired_pose_matrices[definition['name']]
                    local = obj.convert_space(
                        pose_bone=pose_bone, matrix=desired_pose,
                        from_space='POSE', to_space='LOCAL')
                    definition['local_locations'].append(tuple(local.to_translation()))
                    definition['local_rotations'].append(tuple(local.to_quaternion()))
                    pose_bone.matrix = desired_pose
                    bpy.context.view_layer.update()
                w.restore_pose(obj, sample_pose)
                scene.frame_set(math.floor(original_frame), subframe=original_frame-math.floor(original_frame))
                yield dict(phase='Converting world motion through rig spaces', frame=frame, total=len(frames))
                guard()

            for definition in definitions:
                if 'rotation_source' in definition:
                    source = definition['rotation_source']
                    output = _from_quaternions(definition['mode'], definition['local_rotations'], source)
                    for index, frame in enumerate(frames):
                        if any(abs(frame-priority) < 1e-8 for priority in priority_frames):
                            output[index] = source[index]
                    plans.append(dict(name=definition['name'], kind='rotation',
                        path=definition['rotation_path'], values=output,
                        desired_world=definition['desired_rotations']))
                if 'location_source' in definition:
                    source = definition['location_source']
                    output = np.asarray(definition['local_locations'], dtype=float)
                    for index, frame in enumerate(frames):
                        if any(abs(frame-priority) < 1e-8 for priority in priority_frames):
                            output[index] = source[index]
                    plans.append(dict(name=definition['name'], kind='location',
                        path=definition['location_path'], values=output,
                        desired_world=definition['desired_locations']))
                yield dict(phase='Preparing editable world-space keys', frame=last, total=len(definitions))
                guard()
        if not plans:
            raise ValueError('Selected controls produced no secondary-motion channels')
        select_action(original)
        guard(full=True)
        candidate = original.copy()
        candidate.name = original.name + ' Secondary'
        candidate.use_fake_user = False
        w.assign_action(obj, candidate, slot)
        output_curves = w.action_curves(candidate, getattr(obj.animation_data, 'action_slot', None), ensure=True, obj=obj)
        curve_total = sum(plan['values'].shape[1] for plan in plans)
        curve_index = 0
        for plan in plans:
            for _ in _write_group_steps(output_curves, plan['path'], plan['values'],
                                        frames, first, last):
                curve_index += 1
                yield dict(phase='Writing editable secondary keys', frame=last,
                           total=curve_total, completed=curve_index)
        guard(full=True)
        yield dict(phase='Editable secondary keys written', frame=last, total=curve_total)
        if flight._curve_token(obj, original) != original_token:
            raise ValueError('Input animation changed during secondary motion')
        # Exact authored endpoints and finite generated samples are checked from
        # the published curves, independently of the arrays used to write them.
        for plan in plans:
            count = plan['values'].shape[1]
            group = _curve_group(output_curves, plan['path'], count, plan['name']+' '+plan['kind'])
            actual = _sample(group, frames)
            priority_indices = [index for index, frame in enumerate(frames)
                                if any(abs(frame-priority) < 1e-8 for priority in priority_frames)]
            if (not np.isfinite(actual).all()
                    or not np.allclose(actual[priority_indices], plan['values'][priority_indices], atol=1e-7)):
                raise ValueError('Published secondary-motion priority poses or samples changed')
            yield dict(phase='Verifying published secondary keys', frame=last, total=len(plans))
        guard(full=True)
        world_location_error = 0.0
        world_rotation_error = 0.0
        evaluated_sphere_penetration = 0.0
        evaluated_plane_penetration = 0.0
        evaluated_capsule_penetration = 0.0
        evaluated_mesh_penetration = 0.0
        evaluated_self_collision_penetration = 0.0
        if raw['space'] == 'WORLD':
            definitions_by_name = {definition['name']: definition for definition in definitions}
            for sample_index, frame in enumerate(frames):
                scene.frame_set(math.floor(frame), subframe=frame-math.floor(frame))
                guard_collision()
                live_sphere_centers = []
                actual_self_points = []
                for item in collision_sphere_records:
                    live_radius = item['radius']
                    if item['scaling']:
                        scale = tuple(float(value) for value in
                                      item['collider'].matrix_world.to_scale())
                        if (not all(math.isfinite(value) and value > 0.0 for value in scale)
                                or max(scale)-min(scale) > 1e-6*max(1.0, max(scale))):
                            raise ValueError('Animated sphere radius changed to nonuniform scale')
                        live_radius *= sum(scale)/3.0
                    live_center, live_radius = sm.validate_sphere_collider(
                        tuple(item['collider'].matrix_world.translation), live_radius)
                    sampled_center = Vector(item['centers'][sample_index])
                    if ((Vector(live_center)-sampled_center).length > 1e-8
                            or abs(live_radius-item['radii'][sample_index]) > 1e-8):
                        raise ValueError(
                            'Secondary collision surface changed after trajectory sampling')
                    live_sphere_centers.append((Vector(live_center), live_radius))
                displayed = w.display_world(obj)
                live_mesh = None
                if collision_mesh_trajectory_active:
                    live_mesh = _sample_deforming_mesh(
                        state.secondary_collision_mesh, collision_mesh_topology, scene)
                    if not np.allclose(live_mesh, collision_mesh_trajectories[sample_index],
                                       atol=1e-8, rtol=0.0):
                        raise ValueError('Secondary collision mesh changed after trajectory sampling')
                live_capsule = None
                if collision_capsule_trajectories is not None:
                    live_start = tuple(collision_capsule_endpoint_objects[0].matrix_world.translation)
                    live_end = tuple(collision_capsule_endpoint_objects[1].matrix_world.translation)
                    live_radius = float(raw['collision_capsule_radius'])
                    if scaling_capsule_active:
                        scales = []
                        for endpoint in collision_capsule_endpoint_objects:
                            scale = tuple(float(value) for value in endpoint.matrix_world.to_scale())
                            if (not all(math.isfinite(value) and value > 0.0 for value in scale)
                                    or max(scale)-min(scale) > 1e-6*max(1.0, max(scale))):
                                raise ValueError('Animated capsule radius changed to nonuniform scale')
                            scales.append(sum(scale) / 3.0)
                        if abs(scales[0] - scales[1]) > 1e-6*max(1.0, *scales):
                            raise ValueError('Capsule endpoint radius scales changed disagreement')
                        live_radius *= sum(scales) / 2.0
                    live_start, live_end, live_radius = sm.validate_capsule_collider(
                        live_start, live_end, live_radius)
                    sampled = (collision_capsule_trajectories[0][sample_index],
                               collision_capsule_trajectories[1][sample_index],
                               collision_capsule_trajectories[2][sample_index])
                    if (not np.allclose(live_start, sampled[0], atol=1e-8)
                            or not np.allclose(live_end, sampled[1], atol=1e-8)
                            or abs(live_radius-sampled[2]) > 1e-8):
                        raise ValueError('Secondary capsule surface changed after trajectory sampling')
                    live_capsule = (Vector(live_start), Vector(live_end), live_radius)
                for name, definition in definitions_by_name.items():
                    actual = displayed @ obj.pose.bones[name].matrix
                    if 'location_source' in definition:
                        if self_collision_effective:
                            actual_self_points.append(np.asarray(actual.translation, dtype=float))
                        error = (actual.translation-Vector(definition['desired_locations'][sample_index])).length
                        world_location_error = max(world_location_error, error)
                        if raw['collision'] and raw['collision_shape'] in {'SPHERE', 'COMPOUND'}:
                            evaluated_sphere_penetration = max(
                                evaluated_sphere_penetration,
                                max(live_radius+raw['collision_clearance']
                                    -(actual.translation-live_center).length
                                    for item, (live_center, live_radius) in zip(
                                        collision_sphere_records, live_sphere_centers)))
                            if raw['collision_shape'] == 'COMPOUND':
                                projected = actual.translation-collision_normal * float(
                                    (actual.translation-collision_point).dot(collision_normal))
                                if contacts._inside_surface(projected, collision_triangles):
                                    evaluated_plane_penetration = max(
                                        evaluated_plane_penetration,
                                        raw['collision_clearance']
                                        - float((actual.translation-collision_point).dot(
                                            collision_normal)))
                        if raw['collision'] and raw['collision_shape'] == 'PLANE':
                            projected = actual.translation-collision_normal * float(
                                (actual.translation-collision_point).dot(collision_normal))
                            if contacts._inside_surface(projected, collision_triangles):
                                evaluated_plane_penetration = max(
                                    evaluated_plane_penetration,
                                    raw['collision_clearance']
                                    - float((actual.translation-collision_point).dot(
                                        collision_normal)))
                    if 'rotation_source' in definition:
                        error = _angle(tuple(actual.to_quaternion()), definition['desired_rotations'][sample_index])
                        world_rotation_error = max(world_rotation_error, error)
                    if ('location_source' in definition and raw['collision']
                            and (raw['collision_shape'] == 'CAPSULE'
                                 or (raw['collision_shape'] == 'COMPOUND'
                                     and raw['collision_compound_capsule']))):
                        active_start = (live_capsule[0] if live_capsule is not None
                                        else Vector(collision_capsule_start))
                        active_end = (live_capsule[1] if live_capsule is not None
                                      else Vector(collision_capsule_end))
                        active_radius = (live_capsule[2] if live_capsule is not None
                                         else collision_capsule_radius)
                        closest = Vector(sm._capsule_closest(
                            np.asarray(actual.translation, dtype=float),
                            np.asarray(active_start, dtype=float),
                            np.asarray(active_end, dtype=float)))
                        evaluated_capsule_penetration = max(
                            evaluated_capsule_penetration,
                            active_radius + raw['collision_clearance']
                            - (actual.translation - closest).length)
                    if ('location_source' in definition and raw['collision']
                            and (raw['collision_shape'] in {'MESH', 'VOLUME'}
                                 or (raw['collision_shape'] == 'COMPOUND'
                                     and raw['collision_compound_mesh']))):
                        active_mesh = (live_mesh
                                       if collision_mesh_trajectory_active
                                       else collision_mesh_triangles)
                        mesh_state = sm.mesh_collision_state(
                            tuple(actual.translation), active_mesh,
                            raw['collision_clearance'], collision_mesh_closed,
                            volume_radius=collision_mesh_volume_radius)
                        evaluated_mesh_penetration = max(
                            evaluated_mesh_penetration, max(0.0, mesh_state[3]))
                if self_collision_effective:
                    _, self_report = sm.resolve_self_collision_positions(
                        np.asarray(actual_self_points, dtype=float),
                        raw['self_collision_radius'], raw['collision_clearance'])
                    evaluated_self_collision_penetration = max(
                        evaluated_self_collision_penetration,
                        self_report['max_raw_penetration'])
                scene.frame_set(math.floor(original_frame), subframe=original_frame-math.floor(original_frame))
                yield dict(phase='Verifying evaluated world controls', frame=frame, total=len(frames))
                guard()
            if world_location_error > 2e-4 or world_rotation_error > 2e-3:
                raise ValueError('Selected rig constraints cannot reproduce the requested world secondary motion')
            if raw['strength'] > 0.0 and evaluated_sphere_penetration > 1e-6:
                raise ValueError('Selected rig constraints cannot reproduce spherical collision clearance')
            if raw['strength'] > 0.0 and evaluated_plane_penetration > 1e-6:
                raise ValueError('Selected rig constraints cannot reproduce compound support clearance')
            if raw['strength'] > 0.0 and evaluated_capsule_penetration > 1e-6:
                raise ValueError('Selected rig constraints cannot reproduce capsule collision clearance')
            if raw['strength'] > 0.0 and evaluated_mesh_penetration > 1e-6:
                raise ValueError(
                    'Selected rig constraints cannot reproduce mesh collision clearance '
                    f'(max penetration {evaluated_mesh_penetration:.9g})')
            if raw['strength'] > 0.0 and evaluated_self_collision_penetration > 1e-6:
                raise ValueError('Selected rig constraints cannot reproduce self-collision clearance')
        chain_report = (world_chain_report if world_chain_report is not None
                        else local_chain_report)
        external_magnitude = float(np.linalg.norm(raw['external_acceleration']))
        wind_magnitude = float(np.linalg.norm(raw['wind_velocity']))
        impulse_magnitude = float(np.linalg.norm(raw['impulse_velocity']))
        reported_loads = []
        for name in sorted(control_loads):
            load = control_loads[name]
            row = dict(control=name, force=load['force'], mass=load['mass'],
                       acceleration=load['acceleration'],
                       acceleration_magnitude=float(np.linalg.norm(load['acceleration'])))
            if load['offset'] != [0.0, 0.0, 0.0] or load['rotational_inertia'] != 1.0:
                row['offset_local'] = load['offset']
                row['rotational_inertia'] = load['rotational_inertia']
                row['max_torque'] = (float(np.max(np.linalg.norm(
                    next(definition['control_torques'] for definition in definitions
                         if definition['name'] == name), axis=1)))
                    if name in torque_controls else 0.0)
                row['max_angular_acceleration'] = (float(np.max(np.linalg.norm(
                    next(definition['control_angular_accelerations'] for definition in definitions
                         if definition['name'] == name), axis=1)))
                    if name in torque_controls else 0.0)
            reported_loads.append(row)
        max_load_acceleration = max((item['acceleration_magnitude'] for item in reported_loads), default=0.0)
        sphere_active = raw['collision'] and raw['collision_shape'] in {'SPHERE', 'COMPOUND'}
        capsule_active = raw['collision'] and (
            raw['collision_shape'] == 'CAPSULE'
            or (raw['collision_shape'] == 'COMPOUND'
                and raw['collision_compound_capsule']))
        compound_capsule_active = raw['collision'] and raw['collision_shape'] == 'COMPOUND' and raw['collision_compound_capsule']
        compound_mesh_active = raw['collision'] and raw['collision_shape'] == 'COMPOUND' and raw['collision_compound_mesh']
        continuous_capsule_active = capsule_active and collision_capsule_continuous
        mesh_active = raw['collision'] and (
            raw['collision_shape'] in {'MESH', 'VOLUME'} or compound_mesh_active)
        volume_mesh_active = raw['collision'] and raw['collision_shape'] == 'VOLUME'
        continuous_mesh_active = mesh_active and collision_mesh_continuous
        deforming_mesh_active = mesh_active and collision_mesh_deforming
        moving_mesh_active = mesh_active and collision_mesh_moving
        exact_swept_volume_active = (continuous_mesh_active and volume_mesh_active
                                     and not deforming_mesh_active
                                     and not moving_mesh_active)
        bounded_swept_volume_active = (continuous_mesh_active and volume_mesh_active
                                       and collision_mesh_trajectory_active)
        continuous_sphere_active = (sphere_active and collision_sphere_continuous)
        multi_sphere = sphere_active and len(collision_sphere_records) > 1
        report_schema = 3
        if external_active:
            report_schema = 4
        if wind_active:
            report_schema = 5
        if impulse_active:
            report_schema = 6
        if load_active:
            report_schema = 7
        if torque_active:
            report_schema = 8
        if sphere_active:
            report_schema = 9
        if multi_sphere:
            report_schema = 10
        if moving_sphere_active:
            report_schema = 11
        if scaling_sphere_active:
            report_schema = 12
        if capsule_active:
            report_schema = (24 if moving_capsule_active else
                             23 if continuous_capsule_active else 13)
        if mesh_active:
            report_schema = 14
        if deforming_mesh_active:
            report_schema = 15
        if volume_mesh_active:
            report_schema = 16
        if continuous_mesh_active:
            report_schema = (21 if exact_swept_volume_active else
                             22 if bounded_swept_volume_active else
                             18 if deforming_mesh_active else 17)
        if moving_mesh_active and not bounded_swept_volume_active:
            report_schema = 20
        if self_collision_active:
            report_schema = 19
        if world_location_chain_active:
            report_schema = (40 if mixed_moving_sphere_triple_compound_active else
                             39 if moving_sphere_triple_compound_active else
                             38 if mixed_moving_sphere_set_compound_active else
                             37 if moving_sphere_set_compound_active else
                             36 if mixed_moving_sphere_compound_active else
                             35 if moving_capsule_compound_active else
                             34 if moving_sphere_compound_active else
                             32 if compound_mesh_active else
                             31 if raw['collision_shape'] == 'COMPOUND' and raw['collision'] else
                             30 if continuous_sphere_active else
                             29 if capsule_active and continuous_capsule_active else
                             28 if mesh_active and collision_mesh_trajectory_active else
                             27 if moving_capsule_active else
                             26 if moving_sphere_active or scaling_sphere_active else 25)
        if local_rotation_chain_torque_active:
            report_schema = 33
        report = dict(schema=report_schema,
                      backend=('implicit_selected_control_chain_angular_momentum_v1'
                               if local_rotation_chain_torque_active else
                                'implicit_selected_control_secondary_self_collision_v1' if self_collision_active else
                                  'implicit_selected_control_chain_location_mixed_moving_sphere_triple_set_compound_support_spheres_v1'
                                  if world_location_chain_active and mixed_moving_sphere_triple_compound_active else
                                  'implicit_selected_control_chain_location_moving_sphere_triple_set_compound_support_v1'
                                  if world_location_chain_active and moving_sphere_triple_compound_active else
                                  'implicit_selected_control_chain_location_mixed_moving_sphere_set_compound_support_spheres_v1'
                                 if world_location_chain_active and mixed_moving_sphere_set_compound_active else
                                 'implicit_selected_control_chain_location_moving_sphere_set_compound_support_v1'
                                 if world_location_chain_active and moving_sphere_set_compound_active else
                                 'implicit_selected_control_chain_location_mixed_moving_sphere_compound_support_spheres_v1'
                                 if world_location_chain_active and mixed_moving_sphere_compound_active else
                                'implicit_selected_control_chain_location_moving_capsule_compound_support_spheres_v1'
                                if world_location_chain_active and moving_capsule_compound_active else
                                'implicit_selected_control_chain_location_moving_sphere_compound_support_v1'
                                if world_location_chain_active and moving_sphere_compound_active else
                                 'implicit_selected_control_chain_location_compound_support_spheres_capsule_mesh_v1'
                                 if world_location_chain_active and compound_capsule_active
                                 and compound_mesh_active else
                                 'implicit_selected_control_chain_location_compound_support_spheres_mesh_v1'
                                 if world_location_chain_active and compound_mesh_active else
                                 'implicit_selected_control_chain_location_compound_support_spheres_capsule_v1'
                                 if world_location_chain_active and compound_capsule_active else
                                 'implicit_selected_control_chain_location_compound_support_spheres_v1'
                                 if world_location_chain_active and raw['collision_shape'] == 'COMPOUND'
                                 and raw['collision'] else
                                 'implicit_selected_control_chain_location_moving_deforming_mesh_v1'
                                 if world_location_chain_active and moving_mesh_active and deforming_mesh_active else
                                 'implicit_selected_control_chain_location_moving_mesh_v1'
                                 if world_location_chain_active and moving_mesh_active else
                                 'implicit_selected_control_chain_location_deforming_mesh_v1'
                                 if world_location_chain_active and deforming_mesh_active else
                                 'implicit_selected_control_chain_location_continuous_sphere_v1'
                                 if world_location_chain_active and continuous_sphere_active else
                                 'implicit_selected_control_chain_location_continuous_moving_capsule_v1'
                                 if world_location_chain_active and moving_capsule_active
                                 and continuous_capsule_active else
                                 'implicit_selected_control_chain_location_continuous_capsule_v1'
                                 if world_location_chain_active and capsule_active
                                 and continuous_capsule_active else
                                 'implicit_selected_control_chain_location_moving_capsule_v1'
                                 if world_location_chain_active and moving_capsule_active else
                                'implicit_selected_control_chain_location_moving_sphere_v1'
                                if world_location_chain_active
                                and (moving_sphere_active or scaling_sphere_active) else
                                'implicit_selected_control_chain_location_v1' if world_location_chain_active else
                                'implicit_selected_control_secondary_continuous_moving_capsule_v1' if moving_capsule_active and continuous_capsule_active else
                                'implicit_selected_control_secondary_moving_capsule_v1' if moving_capsule_active else
                                'implicit_selected_control_secondary_continuous_capsule_v1' if continuous_capsule_active else
                                'implicit_selected_control_secondary_exact_swept_volume_v1' if exact_swept_volume_active else
                                'implicit_selected_control_secondary_continuous_moving_deforming_swept_volume_v1' if bounded_swept_volume_active and moving_mesh_active and deforming_mesh_active else
                                'implicit_selected_control_secondary_continuous_moving_swept_volume_v1' if bounded_swept_volume_active and moving_mesh_active else
                                'implicit_selected_control_secondary_continuous_deforming_swept_volume_v1' if bounded_swept_volume_active and deforming_mesh_active else
                                'implicit_selected_control_chain_v1' if raw['chain'] else
                                'implicit_selected_control_secondary_continuous_moving_deforming_volume_v1' if continuous_mesh_active and moving_mesh_active and deforming_mesh_active and volume_mesh_active else
                                'implicit_selected_control_secondary_continuous_moving_deforming_mesh_v1' if continuous_mesh_active and moving_mesh_active and deforming_mesh_active else
                                'implicit_selected_control_secondary_continuous_moving_volume_v1' if continuous_mesh_active and moving_mesh_active and volume_mesh_active else
                                'implicit_selected_control_secondary_continuous_moving_mesh_v1' if continuous_mesh_active and moving_mesh_active else
                                'implicit_selected_control_secondary_moving_deforming_volume_v1' if moving_mesh_active and deforming_mesh_active and volume_mesh_active else
                                'implicit_selected_control_secondary_moving_deforming_mesh_v1' if moving_mesh_active and deforming_mesh_active else
                                'implicit_selected_control_secondary_moving_volume_v1' if moving_mesh_active and volume_mesh_active else
                                'implicit_selected_control_secondary_moving_mesh_v1' if moving_mesh_active else
                                'implicit_selected_control_secondary_continuous_deforming_volume_v1' if continuous_mesh_active and deforming_mesh_active and volume_mesh_active else
                                'implicit_selected_control_secondary_continuous_deforming_mesh_v1' if continuous_mesh_active and deforming_mesh_active else
                                'implicit_selected_control_secondary_continuous_volume_v1' if continuous_mesh_active and volume_mesh_active else
                                'implicit_selected_control_secondary_continuous_mesh_v1' if continuous_mesh_active else
                                'implicit_selected_control_secondary_volume_v1' if volume_mesh_active else
                                'implicit_selected_control_secondary_deforming_mesh_v1' if deforming_mesh_active else
                                'implicit_selected_control_secondary_mesh_v1' if mesh_active else
                                'implicit_selected_control_secondary_v12' if capsule_active else
                                'implicit_selected_control_secondary_v11' if scaling_sphere_active else
                               'implicit_selected_control_secondary_v10' if moving_sphere_active else
                               'implicit_selected_control_secondary_v9' if multi_sphere else
                               'implicit_selected_control_secondary_v8' if sphere_active else
                               'implicit_selected_control_secondary_v7' if torque_active else
                               'implicit_selected_control_secondary_v6' if load_active else
                               'implicit_selected_control_secondary_v5' if impulse_active else
                               'implicit_selected_control_secondary_v4' if wind_active else
                               'implicit_selected_control_secondary_v3' if external_active else
                               'implicit_selected_control_secondary_v2'),
                       deterministic_physics=True, learned=False, controls=raw['controls'],
                       chain=raw['chain'], chain_controls=chain_order or [],
                       chain_links=(len(chain_order)-1 if chain_order else 0),
                       chain_propagation=raw['chain_propagation'],
                       chain_mode=('WORLD_LOCATION' if world_location_chain_active
                                   else 'LOCAL_ROTATION' if raw['chain'] else None),
                       momentum_transfer=(chain_report is not None
                                          and raw['strength'] > 0.0),
                       momentum_conservation_error=(chain_report.get('momentum_conservation_error', 0.0)
                                                    if world_chain_report is not None else 0.0),
                       maximum_internal_impulse=(chain_report.get('maximum_internal_impulse', 0.0)
                                                 if world_chain_report is not None else 0.0),
                       angular_momentum_transfer=(local_chain_report is not None
                                                  and raw['strength'] > 0.0),
                       angular_momentum_conservation_error=(
                           local_chain_report.get('angular_momentum_residual', 0.0)
                           if local_chain_report is not None else 0.0),
                       maximum_internal_angular_impulse=(
                           local_chain_report.get('maximum_internal_angular_impulse', 0.0)
                           if local_chain_report is not None else 0.0),
                       coupled_samples=(chain_report['coupled_samples']
                                        if chain_report is not None else 0),
                       chain_coupling_passes=(chain_report.get('coupling_passes', 1)
                                             if chain_report is not None else 0),
                       chain_coupling_edges=(chain_report.get('coupling_edges', 0)
                                            if chain_report is not None else 0),
                      space=raw['space'], rotation=raw['rotation'], location=raw['location'], samples=len(frames),
                      curves=sum(plan['values'].shape[1] for plan in plans),
                      keys=sum(plan['values'].size for plan in plans),
                      first=first, last=last, frequency_hz=raw['frequency'],
                      damping_ratio=raw['damping'], air_friction=raw['air_friction'],
                      strength=raw['strength'], boundary_blend_frames=raw['blend_frames'],
                      gravity_influence=raw['gravity_influence'],
                       external_acceleration=raw['external_acceleration'],
                       external_acceleration_magnitude=external_magnitude,
                       control_loads=reported_loads,
                       loaded_controls=sum(1 for item in reported_loads
                                           if any(value != 0.0 for value in item['force'])),
                       max_control_load_acceleration=max_load_acceleration,
                      torque_controls=len(torque_controls),
                      max_control_torque=max_control_torque,
                      max_control_angular_acceleration=max_control_angular_acceleration,
                      wind_velocity=raw['wind_velocity'],
                      wind_velocity_magnitude=wind_magnitude,
                      wind_forcing_acceleration_magnitude=raw['air_friction'] * wind_magnitude,
                      impulse_velocity=raw['impulse_velocity'],
                      impulse_velocity_magnitude=impulse_magnitude,
                      impulse_frame=raw['impulse_frame'],
                      collision=raw['collision'],
                      collision_shape=raw['collision_shape'],
                      collision_plane=(collision_point is not None
                                       if raw['collision'] else False),
                       collision_compound=(raw['collision']
                                           and raw['collision_shape'] == 'COMPOUND'),
                       collision_compound_capsule=bool(compound_capsule_active),
                       collision_compound_mesh=bool(compound_mesh_active),
                       collision_surface=collision_surface, collision_clearance=raw['collision_clearance'],
                      self_collision=self_collision_active,
                      self_collision_radius=(raw['self_collision_radius']
                                             if self_collision_active else None),
                       collision_sphere_radius=(collision_sphere_records[0]['radius']
                                                if sphere_active and not multi_sphere
                                                and not (moving_sphere_active or scaling_sphere_active) else None),
                       collision_sphere_count=(len(collision_sphere_records)
                                               if sphere_active else 0),
                       collision_collider_count=(world_chain_report.get(
                           'collision_collider_count', len(collision_sphere_records))
                           if world_chain_report is not None and sphere_active
                           else len(collision_sphere_records) if sphere_active else 0),
                       collision_spheres=([dict(
                          collider=item['collider'].name_full, radius=item['radius'],
                          **({'moving': True} if item['moving'] else {}),
                           **({'scaling': True} if item['scaling'] else {}))
                           for item in collision_sphere_records] if sphere_active else []),
                       collision_capsule_start=(tuple(collision_capsule_start)
                                                if capsule_active else None),
                       collision_capsule_end=(tuple(collision_capsule_end)
                                              if capsule_active else None),
                       collision_capsule_radius=(collision_capsule_radius
                                                if capsule_active else None),
                       collision_capsule_moving=(moving_capsule_active
                                                if capsule_active else False),
                       collision_capsule_scaling=(scaling_capsule_active
                                                 if capsule_active else False),
                       collision_capsule_continuous=(continuous_capsule_active
                                                    if capsule_active else False),
                       collision_sphere_continuous=(continuous_sphere_active
                                                    if sphere_active else False),
                       collision_mesh=(raw['collision_mesh'] if mesh_active else None),
                       collision_mesh_triangles=(len(collision_mesh_triangles)
                                                if mesh_active else 0),
                       collision_mesh_closed=(collision_mesh_closed if mesh_active else False),
                       collision_mesh_deforming=(deforming_mesh_active if mesh_active else False),
                       collision_mesh_moving=(moving_mesh_active if mesh_active else False),
                       collision_mesh_volume_radius=(collision_mesh_volume_radius
                                                    if volume_mesh_active else None),
                       collision_mesh_continuous=(continuous_mesh_active if mesh_active else False),
                       collision_mesh_exact_swept_volume=(exact_swept_volume_active
                                                        if mesh_active else False),
                       collision_mesh_bounded_swept_volume=(bounded_swept_volume_active
                                                           if mesh_active else False),
                      restitution=raw['restitution'], surface_friction=raw['surface_friction'],
                      collision_samples=world_collision_samples,
                       continuous_collision_samples=(world_chain_report.get(
                           'continuous_collision_samples', world_collision_sweep_samples)
                                                     if world_chain_report is not None
                                                     else world_collision_sweep_samples),
                      max_raw_penetration=max_raw_penetration,
                      max_penetration_before=max_penetration_before,
                      max_penetration_after=(evaluated_self_collision_penetration
                                             if self_collision_active else
                                             evaluated_mesh_penetration if mesh_active and not compound_mesh_active else
                                             max(evaluated_sphere_penetration,
                                                 evaluated_plane_penetration
                                                 if raw['collision_shape'] == 'COMPOUND'
                                                 else 0.0,
                                                  evaluated_capsule_penetration
                                                  if compound_capsule_active else 0.0,
                                                  evaluated_mesh_penetration
                                                  if compound_mesh_active else 0.0)
                                              if sphere_active else
                                              evaluated_capsule_penetration if capsule_active
                                              else max_penetration_after),
                      max_world_location_error=world_location_error,
                      max_world_rotation_error_radians=world_rotation_error,
                      max_rotation_correction_radians=rotation_max,
                      max_location_correction=location_max,
                      priority_poses=len(priority_frames), priority_poses_preserved=True,
                      priority_endpoints_preserved=True, editable_linear_keys=True,
                      elapsed_ms=(time.perf_counter()-started)*1000)
        if sphere_active:
            report['max_desired_penetration_after'] = max_penetration_after
            report['collision_penetration_tolerance'] = 1e-6
            if raw['collision_shape'] == 'COMPOUND':
                report['collision_target_space'] = (
                    'static support plane plus static sphere set plus three evaluated moving spheres'
                    if mixed_moving_sphere_triple_compound_active else
                    'static support plane plus three evaluated direct moving spheres'
                    if moving_sphere_triple_compound_active else
                    'static support plane plus static sphere set plus two evaluated moving spheres'
                    if mixed_moving_sphere_set_compound_active else
                    'static support plane plus two evaluated direct moving spheres'
                    if moving_sphere_set_compound_active else
                    'static support plane plus static sphere set plus one evaluated moving sphere'
                    if mixed_moving_sphere_compound_active else
                    'static support plane plus one evaluated moving sphere'
                    if moving_sphere_compound_active else
                    'static support plane plus static sphere set plus static capsule plus static closed mesh'
                    if compound_capsule_active and compound_mesh_active else
                    'static support plane plus static sphere set plus static closed mesh'
                    if compound_mesh_active else
                    'static support plane plus static sphere set plus static capsule'
                    if compound_capsule_active else
                    'static support plane plus static sphere set')
        if capsule_active:
            report['max_desired_penetration_after'] = max_penetration_after
            report['collision_penetration_tolerance'] = 1e-6
            report['collision_target_space'] = (
                'static support plane plus static sphere set plus one evaluated moving capsule'
                if moving_capsule_compound_active else
                'static support plane plus static sphere set plus static capsule'
                if compound_capsule_active else
                'bounded continuous-time moving/deforming capsule'
                if (moving_capsule_active or scaling_capsule_active) and continuous_capsule_active else
                'bounded moving/deforming capsule'
                if moving_capsule_active or scaling_capsule_active else
                'bounded continuous-time static capsule'
                if continuous_capsule_active else
                'static capsule')
            if moving_capsule_active or scaling_capsule_active:
                report['relative_velocity_response'] = moving_capsule_active
                report['relative_radius_velocity_response'] = scaling_capsule_active
            if moving_capsule_compound_active and collision_capsule_continuous:
                report['continuous_collision_target_space'] = (
                    'bounded moving capsule sweep with support-plane and static-sphere projection')
        if mesh_active:
            report['max_desired_penetration_after'] = max_penetration_after
            report['collision_penetration_tolerance'] = 1e-6
            report['collision_target_space'] = ('static support plane plus static sphere set plus static capsule plus static closed mesh'
                                                if compound_capsule_active and compound_mesh_active else
                                                'static support plane plus static sphere set plus static closed mesh'
                                                if compound_mesh_active else
                                                'exact swept-sphere closed evaluated triangle volume'
                                                if exact_swept_volume_active else
                                                'bounded continuous-time closed moving deforming swept triangle volume'
                                                if bounded_swept_volume_active and moving_mesh_active and deforming_mesh_active else
                                                'bounded continuous-time closed moving swept triangle volume'
                                                if bounded_swept_volume_active and moving_mesh_active else
                                                'bounded continuous-time closed deforming swept triangle volume'
                                                if bounded_swept_volume_active and deforming_mesh_active else
                                                'continuous-time closed moving deforming triangle volume'
                                                if continuous_mesh_active and moving_mesh_active and deforming_mesh_active and volume_mesh_active else
                                                'continuous-time closed moving deforming triangle mesh'
                                                if continuous_mesh_active and moving_mesh_active and deforming_mesh_active else
                                                'continuous-time closed moving triangle volume'
                                                if continuous_mesh_active and moving_mesh_active and volume_mesh_active else
                                                'continuous-time closed moving triangle mesh'
                                                if continuous_mesh_active and moving_mesh_active else
                                                'continuous-time closed deforming triangle volume'
                                                if continuous_mesh_active and deforming_mesh_active and volume_mesh_active else
                                                'continuous-time closed evaluated triangle volume'
                                                if continuous_mesh_active and volume_mesh_active else
                                                'continuous-time closed deforming triangle mesh'
                                                if continuous_mesh_active and deforming_mesh_active else
                                                'continuous-time closed evaluated triangle mesh'
                                                if continuous_mesh_active else
                                                'closed evaluated triangle volume'
                                                if volume_mesh_active else
                                                'moving evaluated shape-key triangle mesh'
                                                if moving_mesh_active and deforming_mesh_active else
                                                'moving evaluated triangle mesh'
                                                if moving_mesh_active else
                                                'evaluated shape-key triangle mesh'
                                                if deforming_mesh_active else
                                                'static evaluated triangle mesh')
            report['collision_mesh_sample_count'] = (len(collision_mesh_trajectories)
                                                     if collision_mesh_trajectory_active else 1)
        if self_collision_active:
            report['self_collision_samples'] = self_collision_samples
            report['max_self_collision_penetration'] = max_self_collision_penetration
            report['self_collision_target_space'] = 'selected-control finite volumes'
            report['self_collision_penetration_tolerance'] = 1e-6
        if moving_sphere_active:
            report['moving_collision_spheres'] = sum(
                bool(item['moving']) for item in collision_sphere_records)
            report['collision_target_space'] = (
                'static support plane plus static sphere set plus three evaluated direct moving spheres'
                if mixed_moving_sphere_triple_compound_active else
                'static support plane plus three evaluated direct moving spheres'
                if moving_sphere_triple_compound_active else
                'static support plane plus static sphere set plus two evaluated direct moving spheres'
                if mixed_moving_sphere_set_compound_active else
                'static support plane plus two evaluated direct moving spheres'
                if moving_sphere_set_compound_active else
                'static support plane plus static sphere set plus one evaluated direct moving sphere'
                if mixed_moving_sphere_compound_active else
                'static support plane plus one evaluated direct moving sphere'
                if moving_sphere_compound_active else
                'evaluated direct object location')
            report['relative_velocity_response'] = True
        if continuous_sphere_active:
            report['continuous_collision_target_space'] = (
                'bounded analytic relative-motion sphere sweep')
        if scaling_sphere_active:
            report.setdefault('moving_collision_spheres', 0)
            report['scaling_collision_spheres'] = sum(
                bool(item['scaling']) for item in collision_sphere_records)
            report['collision_target_space'] = (
                'static support plane plus static sphere set plus three evaluated direct moving spheres and uniform scale'
                if mixed_moving_sphere_triple_compound_active else
                'static support plane plus three evaluated direct moving spheres and uniform scale'
                if moving_sphere_triple_compound_active else
                'static support plane plus static sphere set plus two evaluated direct moving spheres and uniform scale'
                if mixed_moving_sphere_set_compound_active else
                'static support plane plus two evaluated direct moving spheres and uniform scale'
                if moving_sphere_set_compound_active else
                'static support plane plus static sphere set plus one evaluated direct moving sphere and uniform scale'
                if mixed_moving_sphere_compound_active else
                'static support plane plus one evaluated direct moving sphere and uniform scale'
                if moving_sphere_compound_active else
                'evaluated direct object location and uniform scale')
            report['relative_radius_velocity_response'] = True
        if (moving_sphere_compound_active or moving_sphere_set_compound_active
                or mixed_moving_sphere_compound_active
                or mixed_moving_sphere_set_compound_active
                or moving_sphere_triple_compound_active
                or mixed_moving_sphere_triple_compound_active) and collision_sphere_continuous:
            report['continuous_collision_target_space'] = (
                'bounded analytic relative-motion moving sphere sweep with support-plane projection')
        if raw['strength'] == 0.0:
            report.update(
                collision_influence_active=False,
                collision_samples=0,
                continuous_collision_samples=0,
                max_raw_penetration=0.0,
                max_penetration_before=0.0,
                max_penetration_after=0.0,
                max_desired_penetration_after=0.0,
                max_rotation_correction_radians=0.0,
                max_location_correction=0.0)
            if 'relative_velocity_response' in report:
                report['relative_velocity_response'] = False
            if 'relative_radius_velocity_response' in report:
                report['relative_radius_velocity_response'] = False
            select_action(previous)
            state.secondary_metrics = json.dumps(report, allow_nan=False)
            scene.frame_set(
                math.floor(original_frame),
                subframe=original_frame-math.floor(original_frame))
            state.status = 'Secondary strength is zero; input animation retained unchanged'
            committed = True
            if candidate.users == 0:
                bpy.data.actions.remove(candidate)
            candidate = None
            return report
        report['collision_influence_active'] = bool(raw['collision'])
        candidate['b4ml_secondary'] = json.dumps(raw, allow_nan=False)
        candidate['b4ml_secondary_metrics'] = json.dumps(report, allow_nan=False)
        candidate['b4ml_secondary_name'] = candidate.name
        candidate['b4ml_secondary_token'] = flight._curve_token(obj, candidate)
        yield dict(phase='Finalizing secondary candidate', frame=last, total=1)
        guard(full=True)
        discard_previous = previous != original and _unchanged_generated(obj, previous)
        state.secondary_input = original
        state.secondary_output = candidate
        state.candidate_action = candidate
        state.secondary_metrics = candidate['b4ml_secondary_metrics']
        original.use_fake_user = True
        scene.frame_set(math.floor(original_frame), subframe=original_frame-math.floor(original_frame))
        state.status = f"Secondary motion ready on {len(raw['controls'])} selected controls"
        committed = True
        if previous != original and previous.users == 0:
            if discard_previous:
                bpy.data.actions.remove(previous)
            else:
                previous.use_fake_user = True
        return report
    finally:
        if not committed:
            select_action(previous)
            w.restore_pose(obj, original_pose)
            scene.frame_set(math.floor(original_frame), subframe=original_frame-math.floor(original_frame))
            if candidate and candidate.users == 0:
                bpy.data.actions.remove(candidate)


def start(obj, scene):
    if obj.as_pointer() in _JOBS or obj.b4ml.secondary_running:
        raise ValueError('Secondary motion is already running')
    if busy(obj.b4ml):
        raise ValueError('Finish the active pose or correction first')
    _JOBS[obj.as_pointer()] = dict(obj=obj, iterator=correction_steps(obj, scene))
    obj.b4ml.secondary_running = True
    obj.b4ml.secondary_progress = 'Preparing selected controls'
    return _JOBS[obj.as_pointer()]


def step(obj):
    job = _JOBS.get(obj.as_pointer())
    if job is None:
        raise InterruptedError('Secondary motion stopped')
    try:
        info = next(job['iterator'])
        obj.b4ml.secondary_progress = info['phase']
        return False
    except StopIteration:
        _JOBS.pop(obj.as_pointer(), None)
        obj.b4ml.secondary_running = False
        obj.b4ml.secondary_progress = ''
        return True
    except BaseException:
        abort(obj)
        raise


def abort(obj):
    job = _JOBS.pop(obj.as_pointer(), None)
    try:
        if job:
            job['iterator'].close()
    finally:
        obj.b4ml.secondary_running = False
        obj.b4ml.secondary_progress = ''
    return True


def solve(obj, scene):
    start(obj, scene)
    while not step(obj):
        pass
    return json.loads(obj.b4ml.secondary_metrics)


@bpy.app.handlers.persistent
def reset(*args):
    for job in list(_JOBS.values()):
        try:
            abort(job['obj'])
        except (ReferenceError, RuntimeError):
            pass
    _JOBS.clear()


@bpy.app.handlers.persistent
def reset_selection_swap(*args):
    for obj in bpy.data.objects:
        if hasattr(obj, 'b4ml'):
            try:
                obj.b4ml.secondary_selection_swap = ''
            except (AttributeError, ReferenceError, RuntimeError):
                pass


def register():
    for name in ('load_pre', 'undo_pre', 'redo_pre', 'save_pre'):
        handlers = getattr(bpy.app.handlers, name)
        if reset not in handlers:
            handlers.append(reset)
    for name in ('load_post', 'undo_post', 'redo_post'):
        handlers = getattr(bpy.app.handlers, name)
        if reset_selection_swap not in handlers:
            handlers.append(reset_selection_swap)


def unregister():
    reset()
    reset_selection_swap()
    for name in ('load_pre', 'undo_pre', 'redo_pre', 'save_pre'):
        handlers = getattr(bpy.app.handlers, name)
        if reset in handlers:
            handlers.remove(reset)
    for name in ('load_post', 'undo_post', 'redo_post'):
        handlers = getattr(bpy.app.handlers, name)
        if reset_selection_swap in handlers:
            handlers.remove(reset_selection_swap)
