"""Reversible, contact-aware cleanup of copied animation candidates.

SPDX-License-Identifier: GPL-2.0-or-later

This module implements deterministic curve smoothing and conservative redundant
key removal. It does not use a learned model. The active input action is never
edited in place, and a candidate is published only after validation succeeds.
"""
import json
import math
import time

import bpy
import numpy as np
from mathutils import Vector

from . import body_proxy, curve_smoothing, flight, posing, quadruped_contacts
from . import workflow as w
from .rig_mapping import profile_for_object


_JOBS = {}


def _same_frame(a, b):
    return abs(float(a)-float(b)) <= max(1e-5, abs(float(b))*1e-7)


def selected_controls(obj):
    def selected(bone):
        return bool(getattr(bone, 'select', getattr(bone.bone, 'select', False)))
    return tuple(sorted(bone.name for bone in obj.pose.bones if selected(bone)))


def _contact_signature(obj):
    return tuple((item.name, bool(item.enabled), item.review_state, item.limb,
                   float(item.start), float(item.end), tuple(float(v) for v in item.offset),
                   tuple(float(v) for v in item.point),tuple(float(v) for v in item.rotation),
                   bool(item.lock_rotation),float(item.strength),float(item.blend),
                   bool(item.asymmetric_blend),float(item.blend_in),float(item.blend_out),
                   bool(item.prop_bound),getattr(item,'prop_target',None).as_pointer()
                   if getattr(item,'prop_target',None) else None,
                   tuple(float(v) for v in item.prop_point),
                   tuple(float(v) for v in item.prop_rotation))
                  for item in obj.b4ml.contacts)


def request(obj, rows=None):
    state = obj.b4ml
    rows = rows if rows is not None else w.read_anchors(obj)
    captured = tuple(sorted(rows[0][1]['pose']))
    controls = selected_controls(obj) if state.cleanup_scope == 'SELECTED' else captured
    return dict(
        scope=state.cleanup_scope,
        controls=list(controls),
        smooth=bool(state.cleanup_smooth),
        strength=float(state.cleanup_strength),
        reduce=bool(state.cleanup_reduce),
        tolerance=float(state.cleanup_tolerance),
        anchors=[float(frame) for frame, _ in rows],
        anchor_payloads=[json.dumps(payload, sort_keys=True,
                                    separators=(',', ':'), allow_nan=False)
                         for _, payload in rows],
        contacts=_contact_signature(obj),
    )


def _accepted_contact_controls(obj, first, last):
    accepted = {item.limb for item in obj.b4ml.contacts
                if item.enabled and item.review_state == 'ACCEPTED'
                and item.end >= first and item.start <= last}
    if not accepted:
        return set()
    profile = profile_for_object(obj)
    protected = set()

    def include(name):
        bone = obj.pose.bones.get(name)
        while bone is not None:
            protected.add(bone.name)
            bone = bone.parent
    if profile.family == 'quadruped':
        _, _, mapping = quadruped_contacts._mapping(obj)
        for limb in accepted:
            row = mapping.get(limb)
            if row:
                include(row['ik'])
                include(row['joint'])
    elif profile.family == 'humanoid':
        _, _, limbs = posing.bindings(obj)
        mapping = {row['id']: row for row in limbs}
        for limb in accepted:
            row = mapping.get(limb)
            if row:
                for name in row['fk']+row['joints']:
                    include(name)
                if row.get('ik'):
                    include(row['ik'])
                if row.get('pole'):
                    include(row['pole'])
    return body_proxy.dependency_bones(obj,protected)


def _contact_definitions(obj, first, last, priorities):
    profile = profile_for_object(obj)
    if profile.family == 'quadruped':
        _, _, mapping = quadruped_contacts._mapping(obj)
        control = lambda row: (row['joint'], row['ik'])
    elif profile.family == 'humanoid':
        _, _, limbs = posing.bindings(obj)
        mapping = {row['id']: row for row in limbs}
        control = lambda row: (row['joints'][2], row['joints'][2])
    else:
        return []
    result = []
    for item in obj.b4ml.contacts:
        if not item.enabled or item.review_state != 'ACCEPTED' or item.limb not in mapping:
            continue
        start, end = max(first, float(item.start)), min(last, float(item.end))
        if end < start:
            continue
        row = mapping[item.limb]
        joint, orientation = control(row)
        frames = {start, end, (start+end)*.5}
        frames.update(frame for frame in priorities if start <= frame <= end)
        result.append(dict(name=item.name, limb=item.limb, joint=joint,
                           orientation=orientation, offset=tuple(item.offset),
                           lock_rotation=bool(item.lock_rotation), frames=tuple(sorted(frames))))
    return result


def _contact_sample_schedule(definitions):
    """Group contact probes by frame so the dependency graph evaluates once per frame."""
    by_frame = {}
    for definition_index, definition in enumerate(definitions):
        for frame in definition['frames']:
            by_frame.setdefault(float(frame), []).append((definition_index, definition))
    return tuple((frame, tuple(by_frame[frame])) for frame in sorted(by_frame))


def _contact_transform(obj, definition):
    world = w.display_world(obj)
    matrix = world @ obj.pose.bones[definition['joint']].matrix
    point = tuple(matrix @ Vector(definition['offset']))
    rotation = tuple((world @ obj.pose.bones[definition['orientation']].matrix).to_quaternion().normalized())
    return point, rotation


def _rotation_error(a, b):
    first = np.asarray(a, dtype=float)
    second = np.asarray(b, dtype=float)
    first /= np.linalg.norm(first)
    second /= np.linalg.norm(second)
    return 2.0*math.acos(min(1.0, abs(float(np.dot(first, second)))))


def _owned_curves(obj, pose, controls):
    owned = {}
    quaternion_paths = {}
    axis_angle = set()
    for name in controls:
        value = pose[name]
        bone = obj.pose.bones[name]
        for prop in ('location', 'scale'):
            path = bone.path_from_id(prop)
            for index in value['channels'][prop]:
                owned[(path, index)] = name
        if not value['channels']['rotation']:
            continue
        if value['mode'] == 'AXIS_ANGLE':
            axis_angle.add(name)
            continue
        prop = 'rotation_quaternion' if value['mode'] == 'QUATERNION' else 'rotation_euler'
        path = bone.path_from_id(prop)
        indices=value['channels']['rotation']
        count = 4 if prop == 'rotation_quaternion' else 3
        for index in indices:
            owned[(path, index)] = name
        if count == 4 and len(indices)==4:
            quaternion_paths[path] = name
    return owned, quaternion_paths, axis_angle


def _curve_state(curve):
    return (curve.extrapolation, curve.auto_smoothing, bool(curve.lock), bool(curve.mute),
            tuple((tuple(key.co), tuple(key.handle_left), tuple(key.handle_right),
                   key.handle_left_type, key.handle_right_type, key.interpolation,
                   key.easing, float(key.amplitude), float(key.back), float(key.period), key.type)
                  for key in curve.keyframe_points))


def _action_states(action, slot):
    return {(curve.data_path, curve.array_index): _curve_state(curve)
            for curve in w.action_curves(action, slot)}


def _rdp(times, values, tolerance, mandatory):
    """Return indices for a piecewise-linear fit bounded at original key times."""
    keep = set(mandatory) | {0, len(times)-1}
    boundaries = sorted(keep)
    for first, last in zip(boundaries, boundaries[1:]):
        stack = [(first, last)]
        while stack:
            left, right = stack.pop()
            if right-left <= 1:
                continue
            span = times[right]-times[left]
            estimated = values[left] + ((times[left+1:right]-times[left])/span)*(values[right]-values[left])
            errors = np.abs(values[left+1:right]-estimated)
            offset = int(np.argmax(errors))
            if float(errors[offset]) > tolerance:
                split = left+1+offset
                keep.add(split)
                stack.extend(((left, split), (split, right)))
    return keep


def _validate_quaternions(curves, paths, first, last):
    rejected = set()
    for path in paths:
        group = [curves.find(path, index=index) for index in range(4)]
        if any(curve is None for curve in group):
            rejected.add(path)
            continue
        samples = []
        for curve in group:
            rows = np.array([tuple(key.co) for key in curve.keyframe_points
                             if (float(key.co.x) > first or _same_frame(key.co.x, first))
                             and (float(key.co.x) < last or _same_frame(key.co.x, last))], dtype=float)
            samples.append(rows)
        if (any(len(rows) < 2 for rows in samples)
                or any(not np.array_equal(rows[:, 0], samples[0][:, 0]) for rows in samples[1:])):
            rejected.add(path)
            continue
        values = np.stack([rows[:, 1] for rows in samples], axis=-1)
        norms = np.linalg.norm(values, axis=-1)
        if np.any(norms < 1e-8) or np.any(np.sum(values[:-1]*values[1:], axis=-1) <= 0):
            rejected.add(path)
    return rejected


def _reduce_linear(curve, first, last, priority, tolerance):
    points = curve.keyframe_points
    indices = [index for index, key in enumerate(points)
               if (float(key.co.x) > first or _same_frame(key.co.x, first))
               and (float(key.co.x) < last or _same_frame(key.co.x, last))]
    if len(indices) < 3:
        return 0, 0.0
    if not _same_frame(points[indices[0]].co.x, first) or not _same_frame(points[indices[-1]].co.x, last):
        return 0, 0.0
    # Removing a key is predictable only when every owned segment is linear.
    if any(points[index].interpolation != 'LINEAR' for index in indices[:-1]):
        return 0, 0.0
    times = np.array([float(points[index].co.x) for index in indices], dtype=float)
    values = np.array([float(points[index].co.y) for index in indices], dtype=float)
    if not np.isfinite(times).all() or not np.isfinite(values).all() or np.any(np.diff(times) <= 0):
        raise ValueError('Cleanup requires increasing finite key samples')
    mandatory = {local for local, frame in enumerate(times)
                 if any(_same_frame(frame, value) for value in priority)}
    for frame in priority:
        insertion=int(np.searchsorted(times,float(frame)))
        if 0 < insertion < len(times):
            mandatory.update((insertion-1,insertion))
    keep = _rdp(times, values, tolerance, mandatory)
    removed = [indices[local] for local in range(len(indices)) if local not in keep]
    if not removed:
        return 0, 0.0
    kept = sorted(keep)
    max_error = 0.0
    for left, right in zip(kept, kept[1:]):
        estimate = values[left] + ((times[left:right+1]-times[left])/(times[right]-times[left]))*(values[right]-values[left])
        max_error = max(max_error, float(np.max(np.abs(values[left:right+1]-estimate))))
    for index in reversed(removed):
        points.remove(points[index], fast=True)
    curve.update()
    return len(removed), max_error


def _smooth_curve(curve, first, last, strength):
    if strength <= 0:
        return 0, 0.0
    indices = [index for index, key in enumerate(curve.keyframe_points)
               if (float(key.co.x) > first or _same_frame(key.co.x, first))
               and (float(key.co.x) < last or _same_frame(key.co.x, last))]
    if len(indices) < 2:
        return 0, 0.0
    points = curve.keyframe_points
    rows = np.array([tuple(points[index].co) for index in indices], dtype=float)
    if (not _same_frame(rows[0, 0], first) or not _same_frame(rows[-1, 0], last)
            or np.any(np.diff(rows[:, 0]) <= 0)):
        return 0, 0.0
    if np.all(rows[:, 1] == rows[0, 1]):
        return 0, 0.0
    left, right = curve_smoothing.handles(rows[:, 0], rows[:, 1])
    maximum = 0.0
    for local, index in enumerate(indices):
        key = points[index]
        if local > 0:
            old = np.array(tuple(key.handle_left), dtype=float)
            target = left[local]
            value = old+(target-old)*strength
            maximum = max(maximum, float(np.linalg.norm(value-old)))
            key.handle_left_type = 'FREE'
            key.handle_left = value
        if local < len(indices)-1:
            old = np.array(tuple(key.handle_right), dtype=float)
            target = right[local]
            value = old+(target-old)*strength
            maximum = max(maximum, float(np.linalg.norm(value-old)))
            key.handle_right_type = 'FREE'
            key.handle_right = value
            key.interpolation = 'BEZIER'
    return 1, maximum


def _derivative_jump(curve, first, last):
    keys=sorted(curve.keyframe_points,key=lambda key:float(key.co.x))
    maximum = 0.0
    for index in range(1,len(keys)-1):
        previous,key,following=keys[index-1:index+2]
        frame=float(key.co.x)
        if not first<frame<last:continue
        left_dx=(float(key.handle_left.x)-frame
                 if previous.interpolation=='BEZIER'
                 else frame-float(previous.co.x))
        left_dy=(float(key.handle_left.y)-float(key.co.y)
                 if previous.interpolation=='BEZIER'
                 else float(key.co.y)-float(previous.co.y))
        right_dx=(float(key.handle_right.x)-frame
                  if key.interpolation=='BEZIER'
                  else float(following.co.x)-frame)
        right_dy=(float(key.handle_right.y)-float(key.co.y)
                  if key.interpolation=='BEZIER'
                  else float(following.co.y)-float(key.co.y))
        if abs(left_dx)<1e-12 or abs(right_dx)<1e-12:continue
        left=left_dy/left_dx
        right=right_dy/right_dx
        maximum = max(maximum, abs(right-left))
    return maximum


def _unchanged_generated(obj, action):
    return bool(action and action.get('b4ml_cleanup_token')
                and action.get('b4ml_cleanup_name') == action.name
                and action.get('b4ml_cleanup_token') == flight._curve_token(obj, action)
                and not action.asset_data)


def restore(obj, scene):
    state = obj.b4ml
    if state.cleanup_running or state.flight_running or state.contact_running or state.secondary_running:
        raise ValueError('Finish the active correction first')
    output = state.cleanup_output
    if (not state.cleanup_input or output != state.candidate_action
            or not obj.animation_data or obj.animation_data.action != output):
        raise ValueError('Select the cleanup candidate and restore later corrections first')
    removable = _unchanged_generated(obj, output)
    slot = w._slot(obj.animation_data)
    w.assign_action(obj, state.cleanup_input, slot)
    state.candidate_action = state.cleanup_input
    state.cleanup_input = None
    state.cleanup_output = None
    state.cleanup_metrics = ''
    scene.frame_set(scene.frame_current, subframe=scene.frame_subframe)
    state.status = 'Candidate restored before animation cleanup'
    if output.users == 0:
        if removable:
            bpy.data.actions.remove(output)
        else:
            output.use_fake_user = True


def cleanup_steps(obj, scene):
    started = time.perf_counter()
    w.require_rig(obj)
    w._reject_nla(obj)
    state = obj.b4ml
    if (state.body_payload or state.posing_payload or state.quadruped_payload
            or state.flight_running or state.contact_running or state.contact_suggest_running
            or state.secondary_running):
        raise ValueError('Finish the active pose or correction first')
    if bpy.context.screen and bpy.context.screen.is_animation_playing:
        raise ValueError('Stop playback before animation cleanup')
    previous = state.candidate_action
    if not previous or not obj.animation_data or obj.animation_data.action != previous:
        raise ValueError('Generate and select an animation candidate first')
    if state.cleanup_output and state.cleanup_output != previous:
        raise ValueError('Select the last cleanup candidate or restore later corrections first')
    if state.cleanup_output == previous and not state.cleanup_input:
        raise ValueError('Retained cleanup input is missing')
    original = state.cleanup_input if state.cleanup_output == previous else previous
    rows = w.read_anchors(obj)
    raw = request(obj, rows)
    pose = rows[0][1]['pose']
    captured = set(pose)
    controls = set(raw['controls'])
    if not controls:
        raise ValueError('Select one or more captured pose controls for cleanup')
    if not controls.issubset(captured):
        raise ValueError('Cleanup controls must be present in every captured pose')
    if not raw['smooth'] and not raw['reduce']:
        raise ValueError('Enable smoothing, redundant-key removal, or both')
    if not math.isfinite(raw['strength']) or not 0 <= raw['strength'] <= 1:
        raise ValueError('Cleanup strength must be between zero and one')
    if not math.isfinite(raw['tolerance']) or raw['tolerance'] < 0:
        raise ValueError('Key tolerance must be finite and nonnegative')
    first, last = raw['anchors'][0], raw['anchors'][-1]
    protected = _accepted_contact_controls(obj, first, last)
    editable = controls-protected
    if not editable:
        raise ValueError('All requested controls are protected by accepted contacts')
    owned, quaternion_paths, axis_angle = _owned_curves(obj, pose, editable)
    if not owned:
        raise ValueError('Requested controls have no editable captured channels')
    slot = w._slot(obj.animation_data)
    original_token = flight._curve_token(obj, original)
    source_curves = w.action_curves(original, getattr(obj.animation_data, 'action_slot', None))
    original_states = _action_states(original, getattr(obj.animation_data, 'action_slot', None))
    keys_before = sum(len(curve.keyframe_points) for curve in source_curves)
    derivative_jump_before = max((_derivative_jump(curve, first, last) for curve in source_curves
                                  if (curve.data_path, curve.array_index) in owned), default=0.0)
    original_frame = scene.frame_current+scene.frame_subframe
    original_pose = w.raw_pose(obj)
    contact_definitions = _contact_definitions(obj, first, last, tuple(raw['anchors']))
    contact_schedule = _contact_sample_schedule(contact_definitions)
    contact_sample_total = sum(len(definitions) for _, definitions in contact_schedule)
    contact_before = {}
    candidate = None
    committed = False

    def guard(full=False):
        if state.candidate_action != previous or obj.animation_data.action not in (original, candidate):
            raise ValueError('Candidate changed during animation cleanup')
        if request(obj) != raw:
            raise ValueError('Cleanup selection, settings, anchors, or contacts changed during cleanup')
        if full and flight._curve_token(obj, original) != original_token:
            raise ValueError('Input animation changed during cleanup')
        if (candidate is not None and candidate.get('b4ml_cleanup_token')
                and flight._curve_token(obj, candidate) != candidate['b4ml_cleanup_token']):
            raise ValueError('Cleanup candidate changed after validation')
        if abs(scene.frame_current+scene.frame_subframe-original_frame) > 1e-5:
            raise ValueError('Playhead changed during animation cleanup')

    try:
        if obj.animation_data.action != original:
            w.assign_action(obj, original, slot)
        sampled_before = 0
        for frame, definitions in contact_schedule:
            scene.frame_set(math.floor(frame), subframe=frame-math.floor(frame))
            for definition_index, definition in definitions:
                contact_before[(definition_index, frame)] = _contact_transform(obj, definition)
            sampled_before += len(definitions)
            scene.frame_set(math.floor(original_frame), subframe=original_frame-math.floor(original_frame))
            yield dict(phase='Sampling accepted contacts before cleanup',
                       completed=sampled_before, total=contact_sample_total)
            guard()
        candidate = original.copy()
        candidate.name = original.name+' Cleanup'
        candidate.use_fake_user = False
        candidate_slot = next((item for item in candidate.slots if item.identifier == slot), None)
        curves = w.action_curves(candidate, candidate_slot)
        rejected_quaternions = _validate_quaternions(curves, quaternion_paths, first, last)
        curve_total = sum((curve.data_path, curve.array_index) in owned for curve in curves)
        rewritten = removed = skipped_locked = skipped_unsupported = 0
        max_reduction_error = max_handle_delta = 0.0
        priority = tuple(raw['anchors'])
        completed = 0
        for curve in curves:
            key = (curve.data_path, curve.array_index)
            if key not in owned:
                continue
            completed += 1
            if (curve.lock or curve.mute or len(curve.modifiers) or len(curve.sampled_points)):
                skipped_locked += 1
                yield dict(phase='Skipping protected curve constraints', completed=completed, total=curve_total)
                guard()
                continue
            if curve.data_path in rejected_quaternions:
                skipped_unsupported += 1
                yield dict(phase='Skipping unsafe quaternion group', completed=completed, total=curve_total)
                guard()
                continue
            if raw['reduce'] and curve.data_path not in quaternion_paths:
                count, error = _reduce_linear(curve, first, last, priority, raw['tolerance'])
                removed += count
                max_reduction_error = max(max_reduction_error, error)
            if raw['smooth']:
                count, delta = _smooth_curve(curve, first, last, raw['strength'])
                rewritten += count
                max_handle_delta = max(max_handle_delta, delta)
            yield dict(phase='Cleaning editable control curves', completed=completed, total=curve_total)
            guard()
        guard(full=True)
        candidate_states = _action_states(candidate, candidate_slot)
        keys_after = sum(len(curve.keyframe_points) for curve in curves)
        if keys_before-keys_after != removed:
            raise ValueError('Cleanup key-count validation failed')
        derivative_jump_after = max((_derivative_jump(curve, first, last) for curve in curves
                                     if (curve.data_path, curve.array_index) in owned), default=0.0)
        for key, before in original_states.items():
            if key not in owned and candidate_states.get(key) != before:
                raise ValueError('Cleanup changed an unselected or contact-protected curve')
        for key in owned:
            curve = curves.find(key[0], index=key[1])
            if curve is None:
                continue
            for frame in priority:
                source_curve = source_curves.find(key[0], index=key[1])
                if source_curve is None:
                    continue
                if abs(float(curve.evaluate(frame))-float(source_curve.evaluate(frame))) > 1e-8:
                    raise ValueError('Cleanup changed an authored priority pose')
        w.assign_action(obj, candidate, slot)
        candidate['b4ml_cleanup_token'] = flight._curve_token(obj, candidate)
        max_contact_drift = 0.0
        max_contact_rotation_drift = 0.0
        contact_samples = 0
        for frame, definitions in contact_schedule:
            scene.frame_set(math.floor(frame), subframe=frame-math.floor(frame))
            for definition_index, definition in definitions:
                point, rotation = _contact_transform(obj, definition)
                before_point, before_rotation = contact_before[(definition_index, frame)]
                max_contact_drift = max(max_contact_drift,
                                        float(np.linalg.norm(np.asarray(point)-np.asarray(before_point))))
                if definition['lock_rotation']:
                    max_contact_rotation_drift = max(max_contact_rotation_drift,
                                                     _rotation_error(rotation, before_rotation))
                contact_samples += 1
            scene.frame_set(math.floor(original_frame), subframe=original_frame-math.floor(original_frame))
            yield dict(phase='Verifying accepted contacts after cleanup',
                       completed=contact_samples, total=contact_sample_total)
            guard()
        if max_contact_drift > 2e-6 or max_contact_rotation_drift > 2e-5:
            raise ValueError('Cleanup changed an accepted contact; narrow the selected controls')
        report = dict(schema=1, backend='contact_aware_curve_cleanup_v1', learned=False,
                      scope=raw['scope'], requested_controls=sorted(controls),
                      cleaned_controls=sorted(editable), protected_contact_controls=sorted(controls & protected),
                      curves_considered=curve_total, curves_smoothed=rewritten,
                      keys_before=keys_before, keys_after=keys_after, keys_removed=removed,
                      skipped_constrained_curves=skipped_locked,
                      skipped_unsupported_curves=skipped_unsupported,
                      axis_angle_controls_skipped=sorted(axis_angle),
                      smoothing=raw['smooth'], strength=raw['strength'],
                      reduction=raw['reduce'], tolerance=raw['tolerance'],
                      max_reduction_error=max_reduction_error,
                      max_handle_delta=max_handle_delta,
                      max_scalar_derivative_jump_before=derivative_jump_before,
                      max_scalar_derivative_jump_after=derivative_jump_after,
                      quaternion_groups_validated=len(quaternion_paths)-len(rejected_quaternions),
                      priority_poses=len(priority), priority_poses_preserved=True,
                      accepted_contacts=len(contact_definitions), contact_samples=contact_samples,
                      contact_sample_frames=len(contact_schedule),
                      contact_frame_evaluations=2*len(contact_schedule),
                      max_contact_position_drift=max_contact_drift,
                      max_contact_rotation_drift_radians=max_contact_rotation_drift,
                      contacts_preserved=True, source_action_unchanged=True,
                      elapsed_ms=(time.perf_counter()-started)*1000)
        candidate['b4ml_cleanup_request'] = json.dumps(raw, allow_nan=False)
        candidate['b4ml_cleanup_metrics'] = json.dumps(report, allow_nan=False)
        candidate['b4ml_cleanup_name'] = candidate.name
        yield dict(phase='Finalizing cleanup candidate', completed=curve_total, total=curve_total)
        guard(full=True)
        discard_previous = previous != original and _unchanged_generated(obj, previous)
        state.cleanup_input = original
        state.cleanup_output = candidate
        state.candidate_action = candidate
        state.cleanup_metrics = candidate['b4ml_cleanup_metrics']
        original.use_fake_user = True
        scene.frame_set(math.floor(original_frame), subframe=original_frame-math.floor(original_frame))
        state.status = f'Animation cleanup ready: {removed} redundant keys removed'
        committed = True
        if previous != original and previous.users == 0:
            if discard_previous:
                bpy.data.actions.remove(previous)
            else:
                previous.use_fake_user = True
        return report
    finally:
        if not committed:
            if obj.animation_data and obj.animation_data.action != previous:
                w.assign_action(obj, previous, slot)
            w.restore_pose(obj, original_pose)
            scene.frame_set(math.floor(original_frame), subframe=original_frame-math.floor(original_frame))
            if candidate and candidate.users == 0:
                bpy.data.actions.remove(candidate)


def start(obj, scene):
    if obj.as_pointer() in _JOBS or obj.b4ml.cleanup_running:
        raise ValueError('Animation cleanup is already running')
    if obj.b4ml.contact_suggest_running:
        raise ValueError('Finish the active contact suggestion first')
    _JOBS[obj.as_pointer()] = dict(obj=obj, iterator=cleanup_steps(obj, scene))
    obj.b4ml.cleanup_running = True
    obj.b4ml.cleanup_progress = 'Preparing copied animation'
    return _JOBS[obj.as_pointer()]


def step(obj):
    job = _JOBS.get(obj.as_pointer())
    if job is None:
        raise InterruptedError('Animation cleanup stopped')
    try:
        info = next(job['iterator'])
        obj.b4ml.cleanup_progress = info['phase']
        return False
    except StopIteration:
        _JOBS.pop(obj.as_pointer(), None)
        obj.b4ml.cleanup_running = False
        obj.b4ml.cleanup_progress = ''
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
        obj.b4ml.cleanup_running = False
        obj.b4ml.cleanup_progress = ''
    return True


def solve(obj, scene):
    start(obj, scene)
    while not step(obj):
        pass
    return json.loads(obj.b4ml.cleanup_metrics)


@bpy.app.handlers.persistent
def reset(*args):
    for job in list(_JOBS.values()):
        try:
            abort(job['obj'])
        except (ReferenceError, RuntimeError):
            pass
    _JOBS.clear()


def register():
    for name in ('load_pre', 'undo_pre', 'redo_pre', 'save_pre'):
        handlers = getattr(bpy.app.handlers, name)
        if reset not in handlers:
            handlers.append(reset)


def unregister():
    reset()
    for name in ('load_pre', 'undo_pre', 'redo_pre', 'save_pre'):
        handlers = getattr(bpy.app.handlers, name)
        if reset in handlers:
            handlers.remove(reset)
