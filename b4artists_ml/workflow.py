"""Pose anchors and isolated action candidates. All bpy work stays on the main thread."""
import json
import hashlib
import math
import struct
import numpy as np
import bpy
from mathutils import Euler, Quaternion, Vector
from .math_core import blend_pose, finite_vector, timing_window, unit_quaternion
from .rigs import detect_rig  # Compatibility export for existing scripts/tests.
from .rig_mapping import profile_for_object
from . import rig_state as rs, motion_layer

MAX_FRAMES = 240
MAX_KEYS = 200000
MAX_ANCHOR_PAYLOAD_CHARS = 8 * 1024 * 1024


def require_rig(obj):
    if obj is None or obj.type != 'ARMATURE':
        raise ValueError("Select an armature or one of its bound meshes")
    if obj.library or obj.override_library or obj.data.library:
        raise ValueError("Use a local editable rig for this experimental build")
    if obj.mode == 'EDIT':
        raise ValueError("Switch to Object or Pose Mode")
    if obj.data.pose_position != 'POSE':
        raise ValueError("Switch the armature from Rest Position to Pose Position")
    return obj


def active_rig(context):
    obj = context.active_object
    if obj and obj.type == 'EMPTY':
        owner = motion_layer.source(obj, context.scene)
        if owner is not None: return owner
        obj = obj.get('b4ml_owner')
    if obj and isinstance(obj, bpy.types.Object) and obj.type == 'MESH':
        obj = obj.find_armature()
    if not obj or not isinstance(obj, bpy.types.Object) or obj.type != 'ARMATURE':return None
    if obj.name in context.view_layer.objects:return obj
    visible=motion_layer.find(obj)
    return obj if visible and visible.name in context.view_layer.objects else None


def display_world(obj):
    return motion_layer.transform(obj) @ obj.matrix_world


def _channels(bone):
    rotation_count = 4 if bone.rotation_mode in {'QUATERNION', 'AXIS_ANGLE'} else 3
    rotation_editable = (not any(bone.lock_rotation) and not
        (bone.rotation_mode in {'QUATERNION','AXIS_ANGLE'}
         and bone.lock_rotations_4d and bone.lock_rotation_w))
    return {"location": [i for i, lock in enumerate(bone.lock_location) if not lock and not bone.bone.use_connect],
            "scale": [i for i, lock in enumerate(bone.lock_scale) if not lock],
            # Quaternion/Euler conversions couple all axes. Do not evade a partial rotation lock.
            "rotation": list(range(rotation_count)) if rotation_editable else []}


def _rotation(bone):
    if bone.rotation_mode == 'QUATERNION':
        return tuple(bone.rotation_quaternion)
    if bone.rotation_mode == 'AXIS_ANGLE':
        angle, x, y, z = bone.rotation_axis_angle
        axis = Vector((x, y, z))
        if axis.length < 1e-10:
            if abs(angle) > 1e-10:
                raise ValueError(f"Invalid rotation axis: {bone.name}")
            return (1., 0., 0., 0.)
        return tuple(Quaternion(axis, angle))
    return tuple(bone.rotation_euler.to_quaternion())


def raw_pose(obj, names=None):
    result = {}
    for bone in obj.pose.bones:
        if names is not None and bone.name not in names:
            continue
        mode = bone.rotation_mode
        raw = (bone.rotation_quaternion if mode == 'QUATERNION' else
               bone.rotation_axis_angle if mode == 'AXIS_ANGLE' else bone.rotation_euler)
        result[bone.name] = {"mode": mode, "location": tuple(bone.location),
                             "scale": tuple(bone.scale), "rotation": _rotation(bone),
                             "raw_rotation": tuple(raw), "channels": _channels(bone)}
    return result


def restore_pose(obj, pose):
    for name, values in pose.items():
        bone = obj.pose.bones.get(name)
        if bone is None:
            continue
        bone.location = values["location"]
        bone.scale = values["scale"]
        bone.rotation_mode = values["mode"]
        if values["mode"] == 'QUATERNION':
            bone.rotation_quaternion = values["raw_rotation"]
        elif values["mode"] == 'AXIS_ANGLE':
            bone.rotation_axis_angle = values["raw_rotation"]
        else:
            bone.rotation_euler = values["raw_rotation"]


def _switches(obj):
    # Capture scalar rig properties, including BoneForge and Rigify IK/FK switches.
    return {bone.name: {k: v for k, v in bone.items()
                        if isinstance(v, (bool, int, float, str)) and not k.startswith('_')}
            for bone in obj.pose.bones if any(isinstance(v, (bool, int, float, str))
                                             for k, v in bone.items() if not k.startswith('_'))}


def _rest_signature(obj):
    bones=obj.data.bones
    if not bones:return {}
    matrices=np.empty((len(bones),4,4),dtype=np.float32)
    bones.foreach_get('matrix_local',matrices.ravel())
    # RNA flattens matrices by column; saved signatures use row order.
    values=matrices.transpose(0,2,1).reshape(len(bones),16).tolist()
    return {b.name: {"parent": b.parent.name if b.parent else None,
                     "rest": values[index]}
            for index,b in enumerate(bones)}


def _reject_nla(obj):
    ad = obj.animation_data
    if ad and (getattr(ad, "use_tweak_mode", False) or
               (ad.use_nla and any(not t.mute and any(not s.mute for s in t.strips) for t in ad.nla_tracks))):
        raise ValueError("Mute NLA tracks and leave Tweak Mode before generating a candidate")


def capture_anchor(obj, scene, selected_only=False, *, from_posing=False):
    require_rig(obj)
    if obj.b4ml.candidate_action or (obj.b4ml.posing_payload or obj.b4ml.body_payload or obj.b4ml.quadruped_payload) and not from_posing:
        raise ValueError('Keep or cancel assisted posing/the candidate before capturing')
    _reject_nla(obj)
    snapshot = None
    try:
        if not selected_only:
            snapshot = rs.normalize_fk(obj)
        return _capture_anchor(obj, scene, selected_only, from_posing=from_posing,
                               rig_modes=snapshot['normalized_modes'] if snapshot else None)
    finally:
        rs.restore_snapshot(obj, snapshot)


def _capture_anchor(obj, scene, selected_only=False, *, from_posing=False, rig_modes=None):
    require_rig(obj)
    if (obj.b4ml.posing_payload or obj.b4ml.body_payload or obj.b4ml.quadruped_payload) and not from_posing:
        raise ValueError("Keep or cancel assisted posing before capturing another anchor")
    if obj.b4ml.candidate_action:
        raise ValueError("Keep or discard the current candidate before capturing poses")
    _reject_nla(obj)
    profile = profile_for_object(obj)
    if selected_only:
        names = {b.name for b in obj.pose.bones if
                 getattr(b, "select", getattr(b.bone, "select", False))}
    else:
        names = set(profile.controls)
        if profile.name in {'Mocap Humanoid','Unity Humanoid','Unreal Mannequin'} and 'hips' in profile.roles:
            # Include root ancestry without requiring assisted-posing topology.
            # Ordinary capture remains available on partial/nonstandard profiles.
            ancestor=obj.pose.bones[profile.roles['hips']].parent
            while ancestor:
                names.add(ancestor.name);ancestor=ancestor.parent
    if not names:
        raise ValueError("No editable controls found. Select controls in Pose Mode and enable Selected Controls Only")
    invalid = [n for n in names if n.startswith(("DEF-", "ORG-", "MCH-")) or '.def-' in n or '.mch_' in n]
    if invalid:
        raise ValueError("Select animator controls, not deform or mechanism bones: " + ', '.join(invalid[:3]))
    pose = raw_pose(obj, names)
    if not any(v["channels"]["location"] or v["channels"]["scale"] or v["channels"]["rotation"] for v in pose.values()):
        raise ValueError("All selected control channels are locked")
    frame = _stored_anchor_frame(scene.frame_current + scene.frame_subframe)
    anchors = obj.b4ml.anchors
    if len(anchors) > 128:
        raise ValueError('This build supports at most 128 pose anchors')
    matches = [value for value in anchors if abs(value.frame-frame) < 1e-5]
    if len(matches) > 1:
        raise ValueError('Stored pose anchor is ambiguous')
    anchor = matches[0] if matches else None
    proposed_frames=[value.frame for value in anchors if value is not anchor]+[frame]
    if len(proposed_frames)>1 and max(proposed_frames)-min(proposed_frames)>MAX_FRAMES:
        raise ValueError(f"Limit this experimental preview to {MAX_FRAMES} frames")
    current_payload_chars = sum(len(value.payload) for value in anchors)
    if current_payload_chars > MAX_ANCHOR_PAYLOAD_CHARS:
        raise ValueError('Invalid pose anchor')
    normalized_first = (_earlier_insert_normalization(
        anchors, _read_anchor_rows(obj, 1), frame)
        if anchor is None and len(anchors) else None)
    incoming_timing = None
    if anchor is not None:
        if (not isinstance(anchor.payload, str) or not anchor.payload or
                len(anchor.payload) > MAX_ANCHOR_PAYLOAD_CHARS or
                sum(len(value.payload) for value in obj.b4ml.anchors)
                > MAX_ANCHOR_PAYLOAD_CHARS):
            raise ValueError('Invalid pose anchor')
        try:
            previous_payload = json.loads(anchor.payload)
        except (TypeError, ValueError, RecursionError) as exc:
            raise ValueError('Invalid pose anchor') from exc
        if not isinstance(previous_payload, dict):
            raise ValueError('Invalid pose anchor')
        incoming_timing = _validated_incoming_timing(previous_payload.get('incoming_timing'))
    payload = {"schema": 1, "pose": pose, "switches": _switches(obj), "rest": _rest_signature(obj)}
    if incoming_timing is not None:
        payload['incoming_timing'] = incoming_timing
    if rig_modes:
        payload['schema'] = 2
        payload['rig_modes'] = rig_modes
    text = json.dumps(payload, allow_nan=False)
    normalization_savings = ((len(normalized_first[1]) - len(normalized_first[2]))
                             if normalized_first else 0)
    proposed_payload_chars = (current_payload_chars - (len(anchor.payload) if anchor else 0)
                              + len(text) - normalization_savings)
    if proposed_payload_chars > MAX_ANCHOR_PAYLOAD_CHARS:
        raise ValueError('Pose anchors exceed the serialized payload limit')
    if anchor is None:
        if len(anchors) >= 128:
            raise ValueError("This build supports at most 128 pose anchors")
        anchor = anchors.add()
    anchor.frame = frame
    anchor.payload = text
    anchor.name = f"Frame {frame:g} - {len(pose)} controls"
    _apply_first_normalization(anchors, normalized_first)
    obj.b4ml.status = f"Captured {len(pose)} controls at frame {frame:g}"
    return len(pose)


_TIMING_EASINGS = frozenset(('LINEAR', 'SMOOTH', 'EASE_IN', 'EASE_OUT'))


def _validated_incoming_timing(value):
    """Return one destination-owned timing override or reject hostile saved data."""
    if value is None:
        return None
    if (not isinstance(value, dict) or
            set(value) not in ({'easing', 'bias'},
                               {'easing', 'bias', 'departure_hold', 'arrival_hold'})):
        raise ValueError('Invalid per-transition timing')
    easing = value.get('easing')
    bias = value.get('bias')
    departure_hold = value.get('departure_hold', 0.0)
    arrival_hold = value.get('arrival_hold', 0.0)
    if easing not in _TIMING_EASINGS:
        raise ValueError('Invalid per-transition timing')
    if (isinstance(bias, bool) or not isinstance(bias, (int, float)) or
            not math.isfinite(bias) or not -1 <= bias <= 1):
        raise ValueError('Invalid per-transition timing')
    try:
        timing_window(.5, departure_hold, arrival_hold)
    except ValueError as exc:
        raise ValueError('Invalid per-transition timing') from exc
    return {'easing': easing, 'bias': float(bias),
            'departure_hold': float(departure_hold),
            'arrival_hold': float(arrival_hold)}


def has_transition_timing_override(payload_text):
    """Safely classify one saved anchor for lightweight UI display."""
    if (not isinstance(payload_text, str) or not payload_text or
            len(payload_text) > MAX_ANCHOR_PAYLOAD_CHARS):
        return False
    try:
        payload = json.loads(payload_text)
        return (isinstance(payload, dict) and
                _validated_incoming_timing(payload.get('incoming_timing')) is not None)
    except (TypeError, ValueError, RecursionError):
        return False


def _earlier_insert_normalization(anchors, rows, inserted_frame):
    """Prepare removal of a dormant first-anchor timing record before earlier insertion."""
    if not rows or inserted_frame >= rows[0][0]:
        return None
    payload = dict(rows[0][1])
    if payload.pop('incoming_timing', None) is None:
        return None
    matches = [anchor for anchor in anchors if abs(anchor.frame-rows[0][0]) < 1e-5]
    if len(matches) != 1:
        raise ValueError('Stored pose anchor is ambiguous')
    return rows[0][0], matches[0].payload, json.dumps(payload, allow_nan=False)


def _apply_first_normalization(anchors, prepared):
    if prepared is None:
        return
    matches = [anchor for anchor in anchors if abs(anchor.frame-prepared[0]) < 1e-5]
    if len(matches) != 1:
        raise ValueError('Stored pose anchor is ambiguous')
    matches[0].payload = prepared[2]


def remove_anchor(obj, frame):
    """Remove one anchor and clear timing that would become dormant on the new first."""
    require_rig(obj)
    if obj.b4ml.candidate_action:
        raise ValueError('Keep or discard the candidate first')
    if isinstance(frame, bool) or not isinstance(frame, (int, float)) or not math.isfinite(frame):
        raise ValueError('Invalid pose anchor frame')
    rows = _read_anchor_rows(obj, minimum=1)
    match_indexes = [index for index, anchor in enumerate(obj.b4ml.anchors)
                     if abs(anchor.frame-frame) < 1e-5]
    if len(match_indexes) != 1:
        raise ValueError('No anchor on the current frame' if not match_indexes else
                         'Stored pose anchor is ambiguous')
    remaining_frames = [row_frame for row_frame, _payload in rows
                        if abs(row_frame-frame) >= 1e-5]
    normalized_first = None
    if remaining_frames:
        first_frame = min(remaining_frames)
        first = next(anchor for anchor in obj.b4ml.anchors
                     if abs(anchor.frame-first_frame) < 1e-5)
        payload = json.loads(first.payload)
        if payload.pop('incoming_timing', None) is not None:
            normalized_first = (first_frame, json.dumps(payload, allow_nan=False))
    obj.b4ml.anchors.remove(match_indexes[0])
    if normalized_first is not None:
        first = next(anchor for anchor in obj.b4ml.anchors
                     if abs(anchor.frame-normalized_first[0]) < 1e-5)
        first.payload = normalized_first[1]
    obj.b4ml.status = f'Removed anchor at frame {frame:g}'


def _read_anchor_rows(obj, minimum=2):
    if len(obj.b4ml.anchors) > 128:
        raise ValueError('This build supports at most 128 pose anchors')
    rows=[];payload_chars=0
    for anchor in obj.b4ml.anchors:
        if (not isinstance(anchor.payload,str) or not anchor.payload
                or len(anchor.payload)>MAX_ANCHOR_PAYLOAD_CHARS):
            raise ValueError('Invalid pose anchor')
        payload_chars+=len(anchor.payload)
        if payload_chars>MAX_ANCHOR_PAYLOAD_CHARS:
            raise ValueError('Invalid pose anchor')
        try:payload=json.loads(anchor.payload)
        except (TypeError,ValueError,RecursionError) as exc:raise ValueError('Invalid pose anchor') from exc
        if not isinstance(payload,dict):raise ValueError('Invalid pose anchor')
        _validated_incoming_timing(payload.get('incoming_timing'))
        rows.append((anchor.frame,payload))
    rows.sort(key=lambda row:row[0])
    if len(rows) < minimum:
        raise ValueError("Capture at least two poses on different frames" if minimum>1 else "Capture a pose anchor first")
    if rows[-1][0] - rows[0][0] > MAX_FRAMES:
        raise ValueError(f"Limit this experimental preview to {MAX_FRAMES} frames")
    rest = _rest_signature(obj)
    previous = None
    for frame, payload in rows:
        if not math.isfinite(frame) or previous is not None and frame <= previous:
            raise ValueError("Anchor frames must be finite and distinct")
        previous = frame
        if payload.get("schema") not in {1,2} or payload.get("rest") != rest:
            raise ValueError("Rig structure/rest pose changed; recapture the anchors")
        if payload.get('rig_modes') != rows[0][1].get('rig_modes'):
            raise ValueError('Mixed anchor rig-state formats; recapture all anchors with the same controls')
        if (payload.get('schema') == 2 or payload.get('rig_modes')) and (payload.get('schema') != 2 or payload.get('rig_modes') != rs.canonical_modes(obj)):
            raise ValueError('Unsupported anchor rig-mode mapping; recapture anchors')
        pose = payload.get("pose")
        if not isinstance(pose, dict) or not pose or not isinstance(payload.get('switches'),dict):
            raise ValueError("Invalid pose anchor")
        for name, value in pose.items():
            bone = obj.pose.bones.get(name)
            if (bone is None or not isinstance(value,dict)
                    or not {'mode','location','scale','rotation','raw_rotation','channels'}<=set(value)
                    or value["mode"] != bone.rotation_mode or value["channels"] != _channels(bone)):
                raise ValueError(f"Control or locks changed: {name}; recapture anchors")
            finite_vector(value["location"], 3)
            finite_vector(value["scale"], 3)
            unit_quaternion(value["rotation"])
            finite_vector(value["raw_rotation"], 4 if value["mode"] in {'QUATERNION', 'AXIS_ANGLE'} else 3)
        if payload["switches"] != rows[0][1]["switches"]:
            raise ValueError("Rig properties/IK-FK spaces changed between poses; keep them constant")
        blend_pose(rows[0][1]["pose"], pose, 0.)
    modes = rows[0][1].get('rig_modes', {})
    if rs.without_modes(rows[0][1]['switches'], modes) != rs.without_modes(_switches(obj), modes):
        raise ValueError("Current rig properties differ from anchors; restore the captured IK/FK settings")
    return rows


def read_anchors(obj):
    return _read_anchor_rows(obj,2)


def transition_timing(obj, destination_frame):
    """Read the optional timing override owned by one destination pose anchor."""
    if (isinstance(destination_frame, bool) or
            not isinstance(destination_frame, (int, float)) or
            not math.isfinite(destination_frame)):
        raise ValueError('Invalid transition destination frame')
    rows = _read_anchor_rows(obj, 1)
    matches = [payload for frame, payload in rows if abs(frame-destination_frame) < 1e-5]
    if len(matches) != 1:
        raise ValueError('Stored pose anchor is missing or ambiguous')
    return _validated_incoming_timing(matches[0].get('incoming_timing'))


def set_transition_timing(obj, destination_frame, enabled, easing='SMOOTH', bias=0.0,
                          departure_hold=0.0, arrival_hold=0.0):
    """Atomically set the transition arriving at a saved pose; source animation is untouched."""
    require_rig(obj);state=obj.b4ml
    if (state.candidate_action or state.posing_payload or state.body_payload or
            state.quadruped_payload or state.temporal_running or state.body_running or
            state.body_live or state.contact_running or state.contact_suggest_running or
            state.flight_running or state.secondary_running or state.cleanup_running):
        raise ValueError('Finish or cancel the active animation workflow before editing timing')
    if motion_layer.find(obj):
        raise ValueError('Restore the kept motion source before editing timing')
    _reject_nla(obj)
    if type(enabled) is not bool:
        raise ValueError('Invalid per-transition timing state')
    if (isinstance(destination_frame, bool) or
            not isinstance(destination_frame, (int, float)) or
            not math.isfinite(destination_frame)):
        raise ValueError('Invalid transition destination frame')
    record = _validated_incoming_timing({
        'easing': easing, 'bias': bias,
        'departure_hold': departure_hold, 'arrival_hold': arrival_hold,
    }) if enabled else None
    rows = _read_anchor_rows(obj, 2)
    indices = [index for index, (frame, _) in enumerate(rows)
               if abs(frame-destination_frame) < 1e-5]
    if len(indices) != 1:
        raise ValueError('Stored pose anchor is missing or ambiguous')
    if indices[0] == 0:
        raise ValueError('The first pose has no incoming transition')
    payload = dict(rows[indices[0]][1])
    if record is None:
        payload.pop('incoming_timing', None)
    else:
        payload['incoming_timing'] = record
    text = json.dumps(payload, allow_nan=False)
    target = next((anchor for anchor in state.anchors
                   if abs(anchor.frame-destination_frame) < 1e-5), None)
    if target is None:
        raise ValueError('Stored pose anchor is missing or ambiguous')
    payload_chars = sum(len(anchor.payload) for anchor in state.anchors)
    if payload_chars - len(target.payload) + len(text) > MAX_ANCHOR_PAYLOAD_CHARS:
        raise ValueError('Pose anchors exceed the serialized payload limit')
    target.payload = text
    state.status = (f'Transition into frame {destination_frame:g}: '
                    + (f'{record["easing"]}, bias {record["bias"]:+.2f}'
                       if record else 'uses global timing'))
    return record


def copy_transition_timing(obj, source_frame):
    """Copy one interval's effective deterministic timing into this rig's clipboard."""
    require_rig(obj);state=obj.b4ml
    if state.interpolation_method != 'POSES':
        raise ValueError('Transition timing copy requires Pose Blending mode')
    if (state.candidate_action or state.posing_payload or state.body_payload or
            state.quadruped_payload or state.temporal_running or state.body_running or
            state.body_live or state.contact_running or state.contact_suggest_running or
            state.flight_running or state.secondary_running or state.cleanup_running):
        raise ValueError('Finish or cancel the active animation workflow before copying timing')
    if motion_layer.find(obj):
        raise ValueError('Restore the kept motion source before copying timing')
    _reject_nla(obj)
    if (isinstance(source_frame, bool) or
            not isinstance(source_frame, (int, float)) or
            not math.isfinite(source_frame)):
        raise ValueError('Invalid transition source frame')
    rows = _read_anchor_rows(obj, 2)
    indices = [index for index, (frame, _) in enumerate(rows)
               if abs(frame-source_frame) < 1e-5]
    if len(indices) != 1:
        raise ValueError('Stored pose anchor is missing or ambiguous')
    if indices[0] == 0:
        raise ValueError('The first pose has no incoming transition')
    stored = _validated_incoming_timing(rows[indices[0]][1].get('incoming_timing'))
    timing = stored or _validated_incoming_timing({
        'easing': state.easing, 'bias': float(state.timing_bias),
        'departure_hold': 0.0, 'arrival_hold': 0.0,
    })
    payload = {'schema': 1, 'source_frame': float(source_frame),
               'source': 'OVERRIDE' if stored else 'GLOBAL_SNAPSHOT',
               'timing': timing}
    text = json.dumps(payload, allow_nan=False, sort_keys=True)
    if len(text) > 1024:
        raise ValueError('Transition timing clipboard is too large')
    state.timing_clipboard = text
    state.status = (f'Copied transition into frame {source_frame:g}: '
                    f'{timing["easing"]}, bias {timing["bias"]:+.2f}')
    return payload


def paste_transition_timing(obj, destination_frame):
    """Apply the validated rig-local timing clipboard as an explicit destination override."""
    require_rig(obj);state=obj.b4ml
    if state.interpolation_method != 'POSES':
        raise ValueError('Transition timing paste requires Pose Blending mode')
    text = state.timing_clipboard
    if not isinstance(text, str) or not text or len(text) > 1024:
        raise ValueError('Copy transition timing before pasting')
    try:
        payload = json.loads(text)
    except (TypeError, ValueError, RecursionError) as exc:
        raise ValueError('Invalid transition timing clipboard') from exc
    if (not isinstance(payload, dict) or set(payload) !=
            {'schema', 'source_frame', 'source', 'timing'} or
            payload.get('schema') != 1 or
            payload.get('source') not in {'OVERRIDE', 'GLOBAL_SNAPSHOT'} or
            isinstance(payload.get('source_frame'), bool) or
            not isinstance(payload.get('source_frame'), (int, float)) or
            not math.isfinite(payload['source_frame'])):
        raise ValueError('Invalid transition timing clipboard')
    timing = _validated_incoming_timing(payload.get('timing'))
    if timing is None:
        raise ValueError('Invalid transition timing clipboard')
    result = set_transition_timing(
        obj, destination_frame, True, timing['easing'], timing['bias'],
        timing['departure_hold'], timing['arrival_hold'])
    state.status = (f'Pasted timing from frame {payload["source_frame"]:g} into '
                    f'frame {destination_frame:g}')
    return result


def reuse_anchor(obj,scene,source_frame):
    """Copy one validated local priority pose to the current frame without touching the rig or action."""
    require_rig(obj);state=obj.b4ml
    if state.temporal_running:
        raise ValueError('Finish or cancel motion generation before reusing a pose')
    if state.candidate_action or state.posing_payload or state.body_payload or state.quadruped_payload:
        raise ValueError('Keep or cancel the active preview before reusing a pose')
    if motion_layer.find(obj):raise ValueError('Restore the kept motion source before reusing a pose')
    _reject_nla(obj)
    if not isinstance(source_frame,(int,float)) or not math.isfinite(source_frame):
        raise ValueError('Invalid stored pose frame')
    rows=_read_anchor_rows(obj,1)
    matches=[payload for frame,payload in rows if abs(frame-source_frame)<1e-5]
    if len(matches)!=1:raise ValueError('Stored pose anchor is missing or ambiguous')
    frame=_stored_anchor_frame(scene.frame_current+scene.frame_subframe)
    if abs(frame-source_frame)<1e-5:raise ValueError('Choose a different frame for the reused pose')
    remaining=[value for value,_ in rows if abs(value-frame)>=1e-5]
    proposed=remaining+[frame]
    if max(proposed)-min(proposed)>MAX_FRAMES:
        raise ValueError(f"Limit this experimental preview to {MAX_FRAMES} frames")
    target=next((anchor for anchor in state.anchors if abs(anchor.frame-frame)<1e-5),None)
    normalized_first = (_earlier_insert_normalization(state.anchors, rows, frame)
                        if target is None else None)
    # Reuse transfers the pose. Incoming timing belongs to the destination
    # frame, so preserve an existing destination override rather than copying
    # or deleting it with the source pose.
    destination_payload=next((value for stored_frame,value in rows
                              if abs(stored_frame-frame)<1e-5),None)
    destination_timing=(_validated_incoming_timing(destination_payload.get('incoming_timing'))
                        if destination_payload is not None else None)
    payload=dict(matches[0]);payload.pop('incoming_timing',None)
    if destination_timing is not None:payload['incoming_timing']=destination_timing
    text=json.dumps(payload,allow_nan=False)
    payload_chars=sum(len(anchor.payload) for anchor in state.anchors)
    normalization_savings = ((len(normalized_first[1]) - len(normalized_first[2]))
                             if normalized_first else 0)
    if (payload_chars-(len(target.payload) if target else 0)+len(text)
            - normalization_savings > MAX_ANCHOR_PAYLOAD_CHARS):
        raise ValueError('Pose anchors exceed the serialized payload limit')
    if target is None:
        if len(state.anchors)>=128:raise ValueError('This build supports at most 128 pose anchors')
        target=state.anchors.add()
    target.frame=frame;target.payload=text
    target.name=f"Frame {frame:g} - {len(payload['pose'])} controls (reused from {source_frame:g})"
    _apply_first_normalization(state.anchors, normalized_first)
    state.status=f"Reused pose from frame {source_frame:g} at frame {frame:g}"
    return len(payload['pose'])


def _prepare_pose_retime(obj, scene, source_frame):
    """Validate one order-preserving priority-pose move without mutation."""
    require_rig(obj);state=obj.b4ml
    if state.interpolation_method != 'POSES':
        raise ValueError('Priority-pose retiming requires Pose Blending mode')
    if (state.candidate_action or state.posing_payload or state.body_payload or
            state.quadruped_payload or state.temporal_running or state.body_running or
            state.body_live or state.contact_running or state.contact_suggest_running or
            state.flight_running or state.secondary_running or state.cleanup_running):
        raise ValueError('Finish or cancel the active animation workflow before retiming a pose')
    if motion_layer.find(obj):
        raise ValueError('Restore the kept motion source before retiming a pose')
    _reject_nla(obj)
    if (isinstance(source_frame, bool) or
            not isinstance(source_frame, (int, float)) or
            not math.isfinite(source_frame)):
        raise ValueError('Invalid retime source frame')
    rows = _read_anchor_rows(obj, 2)
    indices = [index for index, (frame, _payload) in enumerate(rows)
               if abs(frame-source_frame) < 1e-5]
    if len(indices) != 1:
        raise ValueError('Stored pose anchor is missing or ambiguous')
    index = indices[0]
    stored_source = float(rows[index][0])
    targets = [anchor for anchor in state.anchors
               if abs(anchor.frame-stored_source) < 1e-5]
    if len(targets) != 1:
        raise ValueError('Stored pose anchor is missing or ambiguous')
    destination = _stored_anchor_frame(
        scene.frame_current + scene.frame_subframe)
    if abs(destination-stored_source) <= 1e-5:
        raise ValueError('Choose a different frame for the retimed pose')
    if index and destination <= rows[index-1][0] + 1e-5:
        raise ValueError('Keep the retimed pose after its previous saved pose')
    if index + 1 < len(rows) and destination >= rows[index+1][0] - 1e-5:
        raise ValueError('Keep the retimed pose before its following saved pose')
    proposed = [destination if row_index == index else frame
                for row_index, (frame, _payload) in enumerate(rows)]
    if proposed[-1] - proposed[0] > MAX_FRAMES:
        raise ValueError(f'Limit this experimental preview to {MAX_FRAMES} frames')
    target = targets[0]
    if not isinstance(target.name, str) or ' - ' not in target.name:
        raise ValueError('Invalid pose anchor display name')
    prefix, suffix = target.name.split(' - ', 1)
    valid_prefixes = {f'Frame {stored_source:g}', f'Frame {stored_source:.9g}'}
    if prefix not in valid_prefixes or not suffix:
        raise ValueError('Invalid pose anchor display name')
    return {
        'target': target,
        'source_frame': stored_source,
        'destination_frame': destination,
        'new_name': f'Frame {destination:.9g} - {suffix}',
        'payload': target.payload,
        'index': index,
    }


def retime_anchor_context(obj, scene, source_frame):
    """Return the exact from/to frames for the Priority Pose Retime dialog."""
    prepared = _prepare_pose_retime(obj, scene, source_frame)
    return {key: prepared[key] for key in
            ('source_frame', 'destination_frame', 'index')}


def _write_retimed_anchor(anchor, destination_frame, name):
    """Write one prepared move; the caller owns transaction rollback."""
    anchor.frame = destination_frame
    if float(anchor.frame) != destination_frame:
        raise ValueError('Stored retimed frame changed unexpectedly')
    anchor.name = name
    if anchor.name != name:
        raise ValueError('Stored retimed pose name changed unexpectedly')


def retime_anchor(obj, scene, source_frame, expected_destination=None):
    """Move one saved pose without recapture, reordering, or Action mutation."""
    prepared = _prepare_pose_retime(obj, scene, source_frame)
    if expected_destination is not None:
        expected = _stored_anchor_frame(expected_destination)
        if prepared['destination_frame'] != expected:
            raise ValueError('Timeline changed; reopen Priority Pose Retime')
    state = obj.b4ml
    target = prepared['target']
    old_frame = float(target.frame)
    old_name = target.name
    old_payload = target.payload
    old_status = state.status
    try:
        _write_retimed_anchor(
            target, prepared['destination_frame'], prepared['new_name'])
        if target.payload != old_payload:
            raise ValueError('Stored pose payload changed unexpectedly')
        state.status = (f'Retimed priority pose from frame '
                        f'{prepared["source_frame"]:.9g} to '
                        f'{prepared["destination_frame"]:.9g}')
    except Exception:
        target.frame = old_frame
        target.name = old_name
        target.payload = old_payload
        state.status = old_status
        raise
    return {
        'source_frame': prepared['source_frame'],
        'destination_frame': prepared['destination_frame'],
        'index': prepared['index'],
    }


def _anchor_collection_binding(state):
    """Bind dialog execution to collection identity, order, and exact contents."""
    rows = [(index, int(anchor.as_pointer()), float(anchor.frame).hex(),
             anchor.name, anchor.payload)
            for index, anchor in enumerate(state.anchors)]
    return hashlib.sha256(json.dumps(
        rows, ensure_ascii=False, separators=(',', ':')).encode('utf-8')).hexdigest()


def _prepare_ripple_retime(obj, scene, source_frame):
    """Prepare an all-or-nothing shift of one pose and every later pose."""
    require_rig(obj);state=obj.b4ml
    if state.interpolation_method != 'POSES':
        raise ValueError('Ripple retiming requires Pose Blending mode')
    if (state.candidate_action or state.posing_payload or state.body_payload or
            state.quadruped_payload or state.temporal_running or state.body_running or
            state.body_live or state.contact_running or state.contact_suggest_running or
            state.flight_running or state.secondary_running or state.cleanup_running):
        raise ValueError('Finish or cancel the active animation workflow before ripple retiming')
    if motion_layer.find(obj):
        raise ValueError('Restore the kept motion source before ripple retiming')
    _reject_nla(obj)
    if (isinstance(source_frame, bool) or
            not isinstance(source_frame, (int, float)) or
            not math.isfinite(source_frame)):
        raise ValueError('Invalid ripple source frame')
    rows = _read_anchor_rows(obj, 2)
    indices = [index for index, (frame, _payload) in enumerate(rows)
               if abs(frame-source_frame) < 1e-5]
    if len(indices) != 1:
        raise ValueError('Stored pose anchor is missing or ambiguous')
    index = indices[0]
    stored_source = float(rows[index][0])
    destination = _stored_anchor_frame(
        scene.frame_current + scene.frame_subframe)
    delta = destination-stored_source
    if abs(delta) <= 1e-5:
        raise ValueError('Choose a different frame for the ripple retime')
    frame_property = scene.bl_rna.properties['frame_current']
    frame_min = float(frame_property.hard_min)
    frame_max = float(frame_property.hard_max)
    targets = []
    for frame, _payload in rows:
        matches = [anchor for anchor in state.anchors
                   if abs(anchor.frame-frame) < 1e-5]
        if len(matches) != 1:
            raise ValueError('Stored pose anchor is missing or ambiguous')
        targets.append(matches[0])
    proposed = [float(frame) for frame, _payload in rows]
    items = []
    for row_index in range(index, len(rows)):
        old_frame = float(rows[row_index][0])
        new_frame = _stored_anchor_frame(old_frame+delta)
        if not frame_min <= new_frame <= frame_max:
            raise ValueError('Ripple result exceeds the Bforartists timeline frame range')
        target = targets[row_index]
        if not isinstance(target.name, str) or ' - ' not in target.name:
            raise ValueError('Invalid pose anchor display name')
        prefix, suffix = target.name.split(' - ', 1)
        if prefix not in {f'Frame {old_frame:g}', f'Frame {old_frame:.9g}'} or not suffix:
            raise ValueError('Invalid pose anchor display name')
        proposed[row_index] = new_frame
        items.append({
            'target': target, 'row_index': row_index,
            'old_frame': old_frame, 'new_frame': new_frame,
            'new_name': f'Frame {new_frame:.9g} - {suffix}',
        })
    if index and proposed[index] <= proposed[index-1] + 1e-5:
        raise ValueError('Keep the ripple range after its previous saved pose')
    for previous, current in zip(proposed, proposed[1:]):
        if current-previous <= 1e-5:
            raise ValueError('Ripple frames collide at Blender frame precision')
    if proposed[-1]-proposed[0] > MAX_FRAMES:
        raise ValueError(f'Limit this experimental preview to {MAX_FRAMES} frames')
    for row_index in range(index, len(rows)-1):
        old_step = rows[row_index+1][0]-rows[row_index][0]
        new_step = proposed[row_index+1]-proposed[row_index]
        tolerance = max(abs(old_step)*.01, math.ulp(old_step)*8)
        if abs(new_step-old_step) > tolerance:
            raise ValueError(
                'Ripple spacing cannot be preserved at Blender frame precision')
    snapshot = [(anchor, int(anchor.as_pointer()), float(anchor.frame),
                 anchor.name, anchor.payload)
                for anchor in state.anchors]
    return {
        'source_frame': stored_source,
        'destination_frame': destination,
        'delta': float(delta),
        'index': index,
        'moved_count': len(items),
        'items': items,
        'snapshot': snapshot,
        'binding': _anchor_collection_binding(state),
    }


def ripple_retime_context(obj, scene, source_frame):
    """Return a complete stale-dialog binding for Ripple Pose Retime."""
    prepared = _prepare_ripple_retime(obj, scene, source_frame)
    return {key: prepared[key] for key in
            ('source_frame', 'destination_frame', 'delta', 'moved_count', 'binding')}


def _validate_anchor_transaction(state, snapshot, items):
    if len(state.anchors) != len(snapshot):
        raise ValueError('Pose anchor collection changed during retiming')
    replacements = {int(item['target'].as_pointer()): item for item in items}
    for current, saved in zip(state.anchors, snapshot):
        anchor, pointer, old_frame, old_name, payload = saved
        if int(current.as_pointer()) != pointer:
            raise ValueError('Pose anchor collection changed during retiming')
        item = replacements.get(pointer)
        expected_frame = item['new_frame'] if item else old_frame
        expected_name = item['new_name'] if item else old_name
        if (float(current.frame) != expected_frame or current.name != expected_name or
                current.payload != payload):
            raise ValueError('Pose anchor changed unexpectedly during retiming')


def _restore_anchor_snapshot(state, snapshot):
    """Restore serialized anchor rows even if an RNA callback changed topology."""
    topology_matches = (
        len(state.anchors) == len(snapshot) and
        all(int(current.as_pointer()) == saved[1]
            for current, saved in zip(state.anchors, snapshot)))
    if topology_matches:
        for anchor, _pointer, frame, name, payload in reversed(snapshot):
            anchor.frame = frame
            anchor.name = name
            anchor.payload = payload
    else:
        state.anchors.clear()
        for _anchor, _pointer, frame, name, payload in snapshot:
            restored = state.anchors.add()
            restored.frame = frame
            restored.name = name
            restored.payload = payload
    expected = [(saved[2], saved[3], saved[4]) for saved in snapshot]
    actual = [(float(anchor.frame), anchor.name, anchor.payload)
              for anchor in state.anchors]
    if actual != expected:
        raise RuntimeError('Retiming rollback could not restore saved poses')


def ripple_retime(obj, scene, source_frame, expected_destination=None,
                  expected_binding=None):
    """Shift one priority pose and all later poses without rewriting payloads."""
    require_rig(obj)
    if (expected_binding is not None and
            _anchor_collection_binding(obj.b4ml) != expected_binding):
        raise ValueError('Saved poses changed; reopen Ripple Pose Retime')
    prepared = _prepare_ripple_retime(obj, scene, source_frame)
    if expected_destination is not None:
        expected = _stored_anchor_frame(expected_destination)
        if prepared['destination_frame'] != expected:
            raise ValueError('Timeline changed; reopen Ripple Pose Retime')
    if expected_binding is not None and prepared['binding'] != expected_binding:
        raise ValueError('Saved poses changed; reopen Ripple Pose Retime')
    state = obj.b4ml
    old_status = state.status
    write_items = (list(reversed(prepared['items']))
                   if prepared['delta'] > 0 else list(prepared['items']))
    try:
        for item in write_items:
            _write_retimed_anchor(
                item['target'], item['new_frame'], item['new_name'])
        _validate_anchor_transaction(
            state, prepared['snapshot'], prepared['items'])
        state.status = (
            f'Ripple-retimed {prepared["moved_count"]} priority poses by '
            f'{prepared["delta"]:+.9g} frames')
    except Exception as operation_error:
        try:
            _restore_anchor_snapshot(state, prepared['snapshot'])
            state.status = old_status
        except Exception as rollback_error:
            state.status = old_status
            raise RuntimeError(
                'Ripple retime failed and exact saved-pose rollback failed') from rollback_error
        raise operation_error
    return {key: prepared[key] for key in
            ('source_frame', 'destination_frame', 'delta', 'moved_count')}


def _pose_spacing_scale_base(obj, pivot_frame):
    """Validate factor-independent dialog state for later-pose scaling."""
    require_rig(obj);state=obj.b4ml
    if state.interpolation_method != 'POSES':
        raise ValueError('Pose spacing scaling requires Pose Blending mode')
    if (state.candidate_action or state.posing_payload or state.body_payload or
            state.quadruped_payload or state.temporal_running or state.body_running or
            state.body_live or state.contact_running or state.contact_suggest_running or
            state.flight_running or state.secondary_running or state.cleanup_running):
        raise ValueError('Finish or cancel the active animation workflow before scaling pose spacing')
    if motion_layer.find(obj):
        raise ValueError('Restore the kept motion source before scaling pose spacing')
    _reject_nla(obj)
    if (isinstance(pivot_frame, bool) or
            not isinstance(pivot_frame, (int, float)) or
            not math.isfinite(pivot_frame)):
        raise ValueError('Invalid pose-spacing pivot frame')
    rows = _read_anchor_rows(obj, 2)
    indices = [index for index, (frame, _payload) in enumerate(rows)
               if abs(frame-pivot_frame) < 1e-5]
    if len(indices) != 1:
        raise ValueError('Stored pose anchor is missing or ambiguous')
    index = indices[0]
    if index == len(rows)-1:
        raise ValueError('Choose a pivot with at least one later saved pose')
    pivot = _stored_anchor_frame(rows[index][0])
    targets = []
    for frame, _payload in rows:
        matches = [anchor for anchor in state.anchors
                   if abs(anchor.frame-frame) < 1e-5]
        if len(matches) != 1:
            raise ValueError('Stored pose anchor is missing or ambiguous')
        targets.append(matches[0])
    for row_index in range(index+1, len(rows)):
        old_frame = _stored_anchor_frame(rows[row_index][0])
        target = targets[row_index]
        if not isinstance(target.name, str) or ' - ' not in target.name:
            raise ValueError('Invalid pose anchor display name')
        prefix, suffix = target.name.split(' - ', 1)
        if prefix not in {f'Frame {old_frame:g}', f'Frame {old_frame:.9g}'} or not suffix:
            raise ValueError('Invalid pose anchor display name')
    snapshot = [(anchor, int(anchor.as_pointer()), float(anchor.frame),
                 anchor.name, anchor.payload) for anchor in state.anchors]
    return {'pivot_frame': pivot, 'index': index, 'rows': rows,
            'targets': targets, 'moved_count': len(rows)-index-1,
            'snapshot': snapshot, 'binding': _anchor_collection_binding(state)}


def _prepare_pose_spacing_scale(obj, pivot_frame, factor):
    """Prepare proportional retiming of every priority pose after one pivot."""
    if (isinstance(factor, bool) or not isinstance(factor, (int, float)) or
            not math.isfinite(factor) or not .25 <= factor <= 4.):
        raise ValueError('Pose spacing scale must be from 0.25 through 4.0')
    base = _pose_spacing_scale_base(obj, pivot_frame)
    rows=base['rows'];targets=base['targets'];index=base['index'];pivot=base['pivot_frame']
    frame_property = bpy.types.Scene.bl_rna.properties['frame_current']
    frame_min = float(frame_property.hard_min)
    frame_max = float(frame_property.hard_max)
    proposed = [float(frame) for frame, _payload in rows]
    items = []
    for row_index in range(index+1, len(rows)):
        old_frame = _stored_anchor_frame(rows[row_index][0])
        ideal_frame = pivot+(old_frame-pivot)*float(factor)
        new_frame = _stored_anchor_frame(ideal_frame)
        if not frame_min <= new_frame <= frame_max:
            raise ValueError('Scaled poses exceed the Bforartists timeline frame range')
        target = targets[row_index]
        _prefix, suffix = target.name.split(' - ', 1)
        proposed[row_index] = new_frame
        items.append({'target': target, 'row_index': row_index,
                      'old_frame': old_frame, 'new_frame': new_frame,
                      'new_name': f'Frame {new_frame:.9g} - {suffix}'})
    if all(item['new_frame'] == item['old_frame'] for item in items):
        raise ValueError('Choose a scale that changes a stored pose frame')
    for previous, current in zip(proposed, proposed[1:]):
        if current-previous <= 1e-5:
            raise ValueError('Scaled pose frames collide at Blender frame precision')
    if proposed[-1]-proposed[0] > MAX_FRAMES:
        raise ValueError(f'Limit this experimental preview to {MAX_FRAMES} frames')
    for row_index in range(index, len(rows)-1):
        ideal_step = (rows[row_index+1][0]-rows[row_index][0])*float(factor)
        actual_step = proposed[row_index+1]-proposed[row_index]
        tolerance = max(abs(ideal_step)*.01, math.ulp(ideal_step)*8)
        if abs(actual_step-ideal_step) > tolerance:
            raise ValueError('Scaled pose spacing cannot be preserved at Blender frame precision')
    for row_index in range(index+1, len(rows)):
        ideal_offset = (rows[row_index][0]-pivot)*float(factor)
        actual_offset = proposed[row_index]-pivot
        tolerance = max(abs(ideal_offset)*.01, math.ulp(ideal_offset)*8)
        if abs(actual_offset-ideal_offset) > tolerance:
            raise ValueError('Scaled pose spacing cannot be preserved at Blender frame precision')
    return {'pivot_frame': pivot, 'factor': float(factor),
            'moved_count': len(items), 'items': items,
            'snapshot': base['snapshot'], 'binding': base['binding']}


def pose_spacing_scale_context(obj, pivot_frame):
    prepared = _pose_spacing_scale_base(obj, pivot_frame)
    return {key: prepared[key] for key in
            ('pivot_frame', 'moved_count', 'binding')}


def scale_pose_spacing(obj, pivot_frame, factor, expected_binding=None):
    """Scale later saved-pose frames around a fixed pivot without changing timing data."""
    require_rig(obj)
    if (expected_binding is not None and
            _anchor_collection_binding(obj.b4ml) != expected_binding):
        raise ValueError('Saved poses changed; reopen Scale Later Pose Spacing')
    prepared = _prepare_pose_spacing_scale(obj, pivot_frame, factor)
    if expected_binding is not None and prepared['binding'] != expected_binding:
        raise ValueError('Saved poses changed; reopen Scale Later Pose Spacing')
    state = obj.b4ml;old_status=state.status
    write_items = (list(reversed(prepared['items']))
                   if prepared['factor'] > 1. else list(prepared['items']))
    try:
        for item in write_items:
            _write_retimed_anchor(item['target'], item['new_frame'], item['new_name'])
        _validate_anchor_transaction(state, prepared['snapshot'], prepared['items'])
        state.status = (f'Scaled {prepared["moved_count"]} later priority pose'
                        f'{"s" if prepared["moved_count"] != 1 else ""} by '
                        f'{prepared["factor"]:.9g}x')
    except Exception as operation_error:
        try:
            _restore_anchor_snapshot(state, prepared['snapshot'])
            state.status=old_status
        except Exception as rollback_error:
            state.status=old_status
            raise RuntimeError(
                'Pose spacing scale failed and exact saved-pose rollback failed') from rollback_error
        raise operation_error
    return {key: prepared[key] for key in ('pivot_frame','factor','moved_count')}


def _prepare_pose_spacing_equalize(obj, pivot_frame, interval):
    """Prepare constant spacing for every priority pose after one fixed pivot."""
    if (isinstance(interval, bool) or not isinstance(interval, (int, float)) or
            not math.isfinite(interval) or not .25 <= interval <= MAX_FRAMES):
        raise ValueError(
            f'Equal pose interval must be from 0.25 through {MAX_FRAMES} frames')
    base = _pose_spacing_scale_base(obj, pivot_frame)
    rows=base['rows'];targets=base['targets'];index=base['index'];pivot=base['pivot_frame']
    stored_interval = _stored_anchor_frame(interval)
    if abs(stored_interval-float(interval)) > max(abs(float(interval))*.01,
                                                  math.ulp(float(interval))*8):
        raise ValueError('Equal pose interval cannot be stored at Blender frame precision')
    frame_property = bpy.types.Scene.bl_rna.properties['frame_current']
    frame_min = float(frame_property.hard_min)
    frame_max = float(frame_property.hard_max)
    proposed = [float(frame) for frame, _payload in rows]
    items = []
    for step, row_index in enumerate(range(index+1, len(rows)), start=1):
        old_frame = _stored_anchor_frame(rows[row_index][0])
        ideal_frame = pivot+float(interval)*step
        new_frame = _stored_anchor_frame(ideal_frame)
        if not frame_min <= new_frame <= frame_max:
            raise ValueError('Equalized poses exceed the Bforartists timeline frame range')
        target = targets[row_index]
        _prefix, suffix = target.name.split(' - ', 1)
        proposed[row_index] = new_frame
        items.append({'target': target, 'row_index': row_index,
                      'old_frame': old_frame, 'new_frame': new_frame,
                      'new_name': f'Frame {new_frame:.9g} - {suffix}'})
    if all(item['new_frame'] == item['old_frame'] for item in items):
        raise ValueError('Later saved poses already use this interval')
    for previous, current in zip(proposed, proposed[1:]):
        if current-previous <= 1e-5:
            raise ValueError('Equalized pose frames collide at Blender frame precision')
    if proposed[-1]-proposed[0] > MAX_FRAMES:
        raise ValueError(f'Limit this experimental preview to {MAX_FRAMES} frames')
    for row_index in range(index, len(rows)-1):
        actual_step = proposed[row_index+1]-proposed[row_index]
        tolerance = max(abs(float(interval))*.01, math.ulp(float(interval))*8)
        if abs(actual_step-float(interval)) > tolerance:
            raise ValueError(
                'Equal pose spacing cannot be preserved at Blender frame precision')
    items = [item for item in items if item['new_frame'] != item['old_frame']]
    return {'pivot_frame': pivot, 'interval': float(interval),
            'moved_count': len(items), 'items': items,
            'snapshot': base['snapshot'], 'binding': base['binding']}


def pose_spacing_equalize_context(obj, pivot_frame):
    """Return the default interval and stale-dialog binding for equal spacing."""
    prepared = _pose_spacing_scale_base(obj, pivot_frame)
    first_later = prepared['rows'][prepared['index']+1][0]
    return {'pivot_frame': prepared['pivot_frame'],
            'interval': float(first_later-prepared['pivot_frame']),
            'affected_count': prepared['moved_count'],
            'binding': prepared['binding']}


def equalize_pose_spacing(obj, pivot_frame, interval, expected_binding=None):
    """Place later saved poses at one constant interval without changing pose data."""
    require_rig(obj)
    if (expected_binding is not None and
            _anchor_collection_binding(obj.b4ml) != expected_binding):
        raise ValueError('Saved poses changed; reopen Equalize Later Pose Spacing')
    prepared = _prepare_pose_spacing_equalize(obj, pivot_frame, interval)
    if expected_binding is not None and prepared['binding'] != expected_binding:
        raise ValueError('Saved poses changed; reopen Equalize Later Pose Spacing')
    state=obj.b4ml;old_status=state.status
    expands = prepared['items'][-1]['new_frame'] > prepared['items'][-1]['old_frame']
    write_items = (list(reversed(prepared['items']))
                   if expands else list(prepared['items']))
    try:
        for item in write_items:
            _write_retimed_anchor(item['target'], item['new_frame'], item['new_name'])
        _validate_anchor_transaction(state, prepared['snapshot'], prepared['items'])
        state.status = (
            f'Equalized {prepared["moved_count"]} later priority pose'
            f'{"s" if prepared["moved_count"] != 1 else ""} to '
            f'{prepared["interval"]:.9g}-frame spacing')
    except Exception as operation_error:
        try:
            _restore_anchor_snapshot(state, prepared['snapshot'])
            state.status=old_status
        except Exception as rollback_error:
            state.status=old_status
            raise RuntimeError(
                'Pose spacing equalize failed and exact saved-pose rollback failed') from rollback_error
        raise operation_error
    return {key: prepared[key] for key in ('pivot_frame','interval','moved_count')}


def breakdown_context(obj, scene):
    """Return the adjacent authored poses and natural blend at the playhead."""
    require_rig(obj)
    frame = _stored_anchor_frame(scene.frame_current + scene.frame_subframe)
    rows = _read_anchor_rows(obj, 2)
    if any(abs(anchor_frame-frame) < 1e-5 for anchor_frame, _ in rows):
        raise ValueError('The current frame already has a pose anchor')
    previous = [row for row in rows if row[0] < frame]
    following = [row for row in rows if row[0] > frame]
    if not previous or not following:
        raise ValueError('Choose a frame strictly between two saved poses')
    left, right = previous[-1], following[0]
    natural = (frame-left[0]) / (right[0]-left[0])
    return {'frame': float(frame), 'left': left, 'right': right,
            'natural_blend': float(natural)}


def _complete_blended_pose(obj, pose, reference):
    """Add a mode-native raw rotation representation to a blended pose."""
    result = {}
    for name, values in pose.items():
        row = dict(values)
        mode = row['mode']
        quaternion = Quaternion(unit_quaternion(row['rotation']))
        if mode == 'QUATERNION':
            raw = tuple(quaternion)
        elif mode == 'AXIS_ANGLE':
            axis, angle = quaternion.to_axis_angle()
            raw = (angle, *axis)
        else:
            compatible = Euler(reference[name]['raw_rotation'], mode)
            raw = tuple(quaternion.to_euler(mode, compatible))
        row['raw_rotation'] = raw
        result[name] = row
    return result


def _effective_interval_timing(state, right):
    """Return the timing that shaped the original immutable transition."""
    return _validated_incoming_timing(right.get('incoming_timing')) or {
        'easing': state.easing, 'bias': float(state.timing_bias),
        'departure_hold': 0.0, 'arrival_hold': 0.0,
    }


def _blend_interval_pose(left, right, fraction, timing):
    """Sample one validated transition without reading or mutating Blender state."""
    return blend_pose(
        left['pose'], right['pose'], fraction,
        timing['easing'], timing['bias'],
        timing['departure_hold'], timing['arrival_hold'])


def _stored_anchor_frame(value):
    """Round a proposed frame to the float representation used by RNA properties."""
    try:
        stored = struct.unpack('<f', struct.pack('<f', float(value)))[0]
    except (OverflowError, struct.error, TypeError, ValueError) as exc:
        raise ValueError('Invalid inbetween frame') from exc
    if not math.isfinite(stored):
        raise ValueError('Invalid inbetween frame')
    return float(stored)


def _prepare_inbetween_series(obj, scene, count):
    """Prepare an all-or-nothing series from one pre-insertion transition."""
    require_rig(obj);state=obj.b4ml
    if state.interpolation_method != 'POSES':
        raise ValueError('Procedural inbetweens require Pose Blending mode')
    if (state.candidate_action or state.posing_payload or state.body_payload or
            state.quadruped_payload or state.temporal_running or state.body_running or
            state.body_live or state.contact_running or state.contact_suggest_running or
            state.flight_running or state.secondary_running or state.cleanup_running):
        raise ValueError('Finish or cancel the active animation workflow before creating inbetweens')
    if motion_layer.find(obj):
        raise ValueError('Restore the kept motion source before creating inbetweens')
    _reject_nla(obj)
    if type(count) is not int or not 1 <= count <= 8:
        raise ValueError('Inbetween count must be between one and eight')
    context = breakdown_context(obj, scene)
    left_frame, left = context['left']
    right_frame, right = context['right']
    if len(state.anchors) + count > 128:
        raise ValueError('This build supports at most 128 pose anchors')
    timing = _effective_interval_timing(state, right)
    existing_frames = [frame for frame, _payload in _read_anchor_rows(obj, 2)]
    frames = []
    for index in range(1, count + 1):
        proposed = left_frame + (right_frame-left_frame) * index / (count + 1)
        stored = _stored_anchor_frame(proposed)
        if not left_frame + 1e-5 < stored < right_frame - 1e-5:
            raise ValueError('This transition is too narrow at Blender frame precision')
        if any(abs(stored-frame) <= 1e-5 for frame in existing_frames + frames):
            raise ValueError('Generated inbetween frames are ambiguous at Blender frame precision')
        frames.append(stored)
    ideal_step = (right_frame-left_frame) / (count + 1)
    stored_steps = [
        current-previous for previous, current in zip(
            [left_frame] + frames, frames + [right_frame])]
    uniform_tolerance = max(
        abs(ideal_step) * .01, math.ulp(ideal_step) * 8)
    if any(abs(step-ideal_step) > uniform_tolerance for step in stored_steps):
        raise ValueError(
            'Generated inbetween frames cannot remain evenly spaced at Blender frame precision')
    prepared = []
    for index, frame in enumerate(frames, 1):
        fraction = (frame-left_frame) / (right_frame-left_frame)
        pose = _complete_blended_pose(
            obj, _blend_interval_pose(left, right, fraction, timing), left['pose'])
        payload = {'schema': left['schema'], 'pose': pose,
                   'switches': left['switches'], 'rest': left['rest']}
        if left.get('rig_modes'):
            payload['rig_modes'] = left['rig_modes']
        payload_text = json.dumps(payload, allow_nan=False)
        prepared.append({
            'frame': frame,
            'payload': payload_text,
            'name': (f'Frame {frame:g} - {len(pose)} controls '
                     f'(procedural inbetween {index}/{count})'),
            'fraction': float(fraction),
        })
    if (sum(len(anchor.payload) for anchor in state.anchors)
            + sum(len(item['payload']) for item in prepared)
            > MAX_ANCHOR_PAYLOAD_CHARS):
        raise ValueError('Pose anchors exceed the serialized payload limit')
    return {
        'left_frame': left_frame, 'right_frame': right_frame,
        'timing': dict(timing), 'items': prepared,
    }


def _write_inbetween_anchor(state, item):
    """Append one already-validated item; the caller owns transaction rollback."""
    anchor = state.anchors.add()
    anchor.frame = item['frame']
    if float(anchor.frame) != item['frame']:
        raise ValueError('Stored inbetween frame changed unexpectedly')
    anchor.payload = item['payload']
    anchor.name = item['name']


def create_inbetween_series(obj, scene, count):
    """Bake 1..8 editable priority samples from one immutable transition."""
    prepared = _prepare_inbetween_series(obj, scene, count)
    state = obj.b4ml
    original_count = len(state.anchors)
    previous_status = state.status
    try:
        for item in prepared['items']:
            _write_inbetween_anchor(state, item)
        state.status = (
            f"Created {count} procedural inbetween"
            f"{'s' if count != 1 else ''} from "
            f"{prepared['left_frame']:g} to {prepared['right_frame']:g}")
    except Exception:
        while len(state.anchors) > original_count:
            state.anchors.remove(len(state.anchors)-1)
        state.status = previous_status
        raise
    return {
        'count': count,
        'frames': [item['frame'] for item in prepared['items']],
        'fractions': [item['fraction'] for item in prepared['items']],
        'left_frame': prepared['left_frame'],
        'right_frame': prepared['right_frame'],
        'timing': prepared['timing'],
    }


def create_breakdown_anchor(obj, scene, blend, selected_only=False):
    """Create one editable priority pose between adjacent anchors without editing the Action."""
    require_rig(obj);state=obj.b4ml
    if state.interpolation_method != 'POSES':
        raise ValueError('Breakdown poses require Pose Blending mode')
    if (state.candidate_action or state.posing_payload or state.body_payload or
            state.quadruped_payload or state.temporal_running or state.body_running or
            state.body_live or state.contact_running or state.contact_suggest_running or
            state.flight_running or state.secondary_running or state.cleanup_running):
        raise ValueError('Finish or cancel the active animation workflow before creating a breakdown')
    if motion_layer.find(obj):
        raise ValueError('Restore the kept motion source before creating a breakdown')
    _reject_nla(obj)
    if (isinstance(blend, bool) or not isinstance(blend, (int, float)) or
            not math.isfinite(blend) or not 0 <= blend <= 1):
        raise ValueError('Breakdown blend must be between zero and one')
    if type(selected_only) is not bool:
        raise ValueError('Invalid selected-controls state')
    context = breakdown_context(obj, scene)
    left_frame, left = context['left']
    right_frame, right = context['right']
    natural = context['natural_blend']
    effective_timing = _effective_interval_timing(state, right)
    natural_pose = _blend_interval_pose(left, right, natural, effective_timing)
    requested_pose = blend_pose(left['pose'], right['pose'], float(blend), 'LINEAR')
    if selected_only:
        selected = {name for name in requested_pose
                    if getattr(obj.pose.bones[name], 'select',
                               getattr(obj.pose.bones[name].bone, 'select', False))}
        if not selected:
            raise ValueError('Select at least one captured animator control')
        for name in selected:
            natural_pose[name] = requested_pose[name]
        pose = natural_pose
    else:
        selected = set(requested_pose)
        pose = requested_pose
    pose = _complete_blended_pose(obj, pose, left['pose'])
    payload = {'schema': left['schema'], 'pose': pose,
               'switches': left['switches'], 'rest': left['rest']}
    if left.get('rig_modes'):
        payload['rig_modes'] = left['rig_modes']
    text = json.dumps(payload, allow_nan=False)
    if len(state.anchors) >= 128:
        raise ValueError('This build supports at most 128 pose anchors')
    if sum(len(anchor.payload) for anchor in state.anchors) + len(text) > MAX_ANCHOR_PAYLOAD_CHARS:
        raise ValueError('Pose anchors exceed the serialized payload limit')
    anchor = state.anchors.add()
    anchor.frame = context['frame']
    if float(anchor.frame) != context['frame']:
        state.anchors.remove(len(state.anchors)-1)
        raise ValueError('Stored breakdown frame changed unexpectedly')
    anchor.payload = text
    scope = f'{len(selected)} selected controls' if selected_only else 'all controls'
    anchor.name = (f"Frame {context['frame']:g} - {len(pose)} controls "
                   f"(breakdown {float(blend):.0%}, {scope})")
    state.status = (f"Created {scope} breakdown at frame {context['frame']:g}: "
                    f"{float(blend):.0%} from {left_frame:g} to {right_frame:g}")
    return {'frame': context['frame'], 'left_frame': left_frame,
            'right_frame': right_frame, 'natural_blend': natural,
            'requested_blend': float(blend), 'selected_controls': sorted(selected)}


def action_curves(action, slot=None, ensure=False, obj=None):
    if hasattr(action, "fcurves") and (getattr(action, "is_action_legacy", False) or not hasattr(action, "slots")):
        return action.fcurves
    if not action.slots and ensure:
        slot = action.slots.new(id_type='OBJECT', name=obj.name)
    if slot is None:
        if len(action.slots) != 1:
            raise ValueError("Choose an active action slot before generating")
        slot = action.slots[0]
    if len(action.layers) > 1:
        raise ValueError("Multiple action layers are not supported in this build")
    layer = action.layers[0] if action.layers else (action.layers.new('B4ML') if ensure else None)
    if layer is None:
        return ()
    if len(layer.strips) > 1:
        raise ValueError("Multiple action strips are not supported in this build")
    strip = layer.strips[0] if layer.strips else (layer.strips.new(type='KEYFRAME') if ensure else None)
    if strip is None:
        return ()
    bag = strip.channelbag(slot, ensure=ensure)
    return bag.fcurves if bag else ()


def _slot(ad):
    slot = getattr(ad, 'action_slot', None)
    return slot.identifier if slot else ''


def assign_action(obj, action, identifier=''):
    obj.animation_data_create()
    obj.animation_data.action = action
    if action and identifier and hasattr(action, 'slots'):
        slot = next((s for s in action.slots if s.identifier == identifier), None)
        if slot is None:
            raise ValueError("Original action slot is missing")
        obj.animation_data.action_slot = slot


class _ValidatedPoseSamples:
    """One-use ownership transfer for a detached, generation-validated buffer."""
    __slots__ = ('_samples',)

    def __init__(self, samples):
        self._samples = samples

    @property
    def consumed(self):
        return self._samples is None

    def consume(self):
        if self._samples is None:
            raise ValueError('Validated projected samples were already consumed')
        samples = self._samples
        self._samples = None
        return samples


def _validated_pose_samples(obj, rows, frames, supplied):
    """Detach complete projected samples before any action or viewport mutation."""
    import copy
    transferred = isinstance(supplied, _ValidatedPoseSamples)
    if transferred:
        supplied = supplied.consume()
    if not isinstance(supplied, dict) or any(type(f) not in (float,int) or not math.isfinite(f) for f in supplied):
        raise ValueError('Expected a finite frame-to-pose mapping')
    if set(supplied)!=set(frames):raise ValueError('Projected samples must cover every preview frame')
    # A private packet already owns a detached deep copy. It is consumed once,
    # then fully revalidated against the live source rig before any mutation.
    result=supplied if transferred else copy.deepcopy(supplied);reference=rows[0][1]['pose']
    for values in result.values():
        if not isinstance(values,dict) or values.keys()!=reference.keys():
            raise ValueError('Projected samples must retain the captured controls')
        for name,value in values.items():
            expected=reference[name]
            if value.get('mode')!=expected['mode'] or value.get('channels')!=expected['channels']:
                raise ValueError('Projected sample control modes or locks differ: '+name)
            finite_vector(value['location'],3);finite_vector(value['scale'],3)
            q=Quaternion(unit_quaternion(value['rotation']))
            raw=finite_vector(value['raw_rotation'],4 if value['mode'] in {'QUATERNION','AXIS_ANGLE'} else 3)
            if value['mode']=='QUATERNION':raw_q=Quaternion(unit_quaternion(raw))
            elif value['mode']=='AXIS_ANGLE':
                axis=Vector(raw[1:])
                if axis.length<1e-10 and abs(raw[0])>1e-10:raise ValueError('Invalid projected rotation axis')
                raw_q=Quaternion(axis,raw[0]) if axis.length>1e-10 else Quaternion()
            else:raw_q=Euler(raw,value['mode']).to_quaternion()
            if abs(q.dot(raw_q))<1.-1e-6:raise ValueError('Projected raw rotation is inconsistent')
    for frame,payload in rows:
        if json.loads(json.dumps(result[frame]))!=json.loads(json.dumps(payload['pose'])):
            raise ValueError('Projected samples must preserve exact authored priorities')
    return result


def preview(obj, scene, easing='SMOOTH', *, timing_bias=0.0, pose_samples=None,
            _validated_rows=None):
    require_rig(obj)
    state = obj.b4ml
    if state.posing_payload or state.body_payload or state.quadruped_payload:
        raise ValueError('Keep or cancel assisted posing before interpolating')
    if state.candidate_action:
        raise ValueError("Keep or discard the current candidate first")
    if motion_layer.find(obj):raise ValueError('Restore the kept motion source before generating another candidate')
    _reject_nla(obj)
    # Temporal publication already owns a freshly validated anchor snapshot.
    # Reuse it only through this private path so public callers still validate.
    # Validate timing before creating or assigning a candidate action.
    # Projected samples own their timing already and therefore accept only the
    # neutral remap through this deterministic publication API.
    if (isinstance(timing_bias, bool) or not isinstance(timing_bias, (int, float)) or
            not math.isfinite(timing_bias) or not -1 <= timing_bias <= 1):
        raise ValueError('Timing bias must be between minus one and one')
    if pose_samples is not None and timing_bias != 0:
        raise ValueError('Projected samples already define timing; use neutral timing bias')
    rows = read_anchors(obj) if _validated_rows is None else _validated_rows
    segment_timing = []
    segment_overrides = []
    for _, destination in rows[1:]:
        override = _validated_incoming_timing(destination.get('incoming_timing'))
        segment_overrides.append(override is not None)
        segment_timing.append(override or {
            'easing': easing, 'bias': float(timing_bias),
            'departure_hold': 0.0, 'arrival_hold': 0.0,
        })
    override_count = sum(segment_overrides)
    if pose_samples is not None and override_count:
        raise ValueError('Projected samples already define timing; remove per-transition overrides')
    first, last = rows[0][0], rows[-1][0]
    frames = sorted({f for f, _ in rows} | {float(f) for f in range(math.ceil(first), math.floor(last)+1)})
    names = set(rows[0][1]["pose"])
    mode_key_budget = sum(len(props) for props in rows[0][1].get('rig_modes',{}).values())*4
    if len(frames)*len(names)*10 + mode_key_budget > MAX_KEYS:
        raise ValueError("Preview exceeds the key budget; select fewer controls or a shorter interval")
    projected = _validated_pose_samples(obj, rows, frames, pose_samples) if pose_samples is not None else None
    ad = obj.animation_data
    source = ad.action if ad else None
    source_slot = _slot(ad) if ad else ''
    if ad and (ad.action_blend_type not in {'REPLACE', 'COMBINE'} or abs(ad.action_influence-1.) > 1e-6):
        raise ValueError("Use a full-influence Replace or Combine action without NLA for this build")
    modes = rows[0][1].get('rig_modes', {})
    mode_paths = rs.property_paths(obj, modes)
    original_modes = rs.mode_values(obj) if modes else {}
    if ad and any(fc.data_path in mode_paths for fc in ad.drivers):
        raise ValueError('Driven IK/FK mode cannot be overridden in a candidate')
    paths = {obj.pose.bones[n].path_from_id(prop) for n in names for prop in
             ('location', 'rotation_quaternion', 'rotation_euler', 'rotation_axis_angle', 'scale')}
    if ad and any(fc.data_path in paths for fc in ad.drivers):
        raise ValueError("Selected transform channels are driven; select animator controls instead")
    if source:
        source_curves = action_curves(source, getattr(ad, 'action_slot', None))
        if any(fc.data_path in paths | mode_paths.keys() and (fc.lock or fc.mute or len(fc.modifiers)) for fc in source_curves):
            raise ValueError("Selected curves contain locks, muting or modifiers; remove these from the input candidate first")
        switch_paths = {obj.pose.bones[n].path_from_id() + '[' + json.dumps(k, ensure_ascii=False) + ']'
                        for n, props in rows[0][1]['switches'].items() for k in props}
        if any(fc.data_path in switch_paths - mode_paths.keys() for fc in source_curves):
            raise ValueError("Animated rig properties require a future rig-state solver; use constant IK/FK settings")
    source_mode_boundaries = {}
    for path in mode_paths:
        fc = next((c for c in source_curves if c.data_path == path), None) if source else None
        value = rs.property_paths(obj, original_modes)[path]
        source_mode_boundaries[path] = (fc.evaluate(first-1) if fc else value, fc.evaluate(last+1) if fc else value)
    before = raw_pose(obj)
    before_text = json.dumps(before, allow_nan=False)
    candidate = None
    try:
        candidate = source.copy() if source else bpy.data.actions.new('B4ML Candidate')
        candidate.name = (source.name if source else obj.name) + ' - B4ML Preview'
        candidate.use_fake_user = False
        assign_action(obj, candidate, source_slot)
        curves = action_curves(candidate, getattr(obj.animation_data, 'action_slot', None), ensure=True, obj=obj)
        if hasattr(candidate, 'slots') and len(candidate.slots) == 1:
            obj.animation_data.action_slot = candidate.slots[0]
        samples = {}
        segment = 0
        compatible = {name: Euler(rows[0][1]['pose'][name]['raw_rotation'], obj.pose.bones[name].rotation_mode)
                      for name in names if obj.pose.bones[name].rotation_mode not in {'QUATERNION', 'AXIS_ANGLE'}}
        previous_quaternions = {}
        priority_frames = {frame for frame, _ in rows}
        for frame in frames:
            while segment + 1 < len(rows)-1 and frame > rows[segment+1][0]:
                segment += 1
            fa, a = rows[segment]
            fb, b = rows[segment+1]
            timing = segment_timing[segment]
            values = (projected[frame] if projected is not None else
                      blend_pose(a['pose'], b['pose'], (frame-fa)/(fb-fa),
                                 timing['easing'], timing['bias'],
                                 timing['departure_hold'], timing['arrival_hold']))
            for name, value in values.items():
                bone = obj.pose.bones[name]
                for prop in ('location', 'scale'):
                    for index in value['channels'][prop]:
                        samples.setdefault((bone.path_from_id(prop), index), []).append((frame, value[prop][index]))
                if value['channels']['rotation']:
                    mode = value['mode']
                    q = Quaternion(value['rotation'])
                    previous_q = previous_quaternions.get(name)
                    if previous_q is not None and q.dot(previous_q) < 0:
                        q.negate()
                    previous_quaternions[name] = q.copy()
                    if mode == 'QUATERNION':
                        prop, rotation = 'rotation_quaternion', tuple(q)
                    elif mode == 'AXIS_ANGLE':
                        axis, angle = q.to_axis_angle()
                        prop, rotation = 'rotation_axis_angle', (angle, *axis)
                    else:
                        euler = q.to_euler(mode, compatible[name])
                        compatible[name] = euler
                        prop, rotation = 'rotation_euler', tuple(euler)
                    if projected is not None and frame in priority_frames:
                        # Preserve authored Euler turns and raw quaternion signs at
                        # priorities, rather than reconstructing equivalent rotations.
                        rotation = value['raw_rotation']
                        previous_quaternions[name] = Quaternion(value['rotation'])
                        if mode not in {'QUATERNION','AXIS_ANGLE'}:
                            compatible[name] = Euler(rotation,mode)
                    for index, number in enumerate(rotation):
                        samples.setdefault((bone.path_from_id(prop), index), []).append((frame, number))
        for (path, index), points in samples.items():
            fc = curves.find(path, index=index)
            if fc is None:
                fc = curves.new(path, index=index)
            for key_index in range(len(fc.keyframe_points)-1, -1, -1):
                if first <= fc.keyframe_points[key_index].co.x <= last:
                    fc.keyframe_points.remove(fc.keyframe_points[key_index], fast=True)
            for frame, value in points:
                key = fc.keyframe_points.insert(frame, value, options={'FAST'})
                key.interpolation = 'LINEAR'
            fc.update()
        for path, value in mode_paths.items():
            fc = curves.find(path, index=0) or curves.new(path, index=0)
            for i in range(len(fc.keyframe_points)-1, -1, -1):
                if first <= fc.keyframe_points[i].co.x <= last:
                    fc.keyframe_points.remove(fc.keyframe_points[i], fast=True)
            start_value, end_value = source_mode_boundaries[path]
            for frame, number in ((first-1,start_value),(first,value),(last,value),(last+1,end_value)):
                key = fc.keyframe_points.insert(frame, number, options={'FAST'})
                key.interpolation = 'CONSTANT'
            fc.update()
        candidate['b4ml_backend'] = 'projected_semantic_motion_v1' if projected is not None else ('deterministic_slerp_v2_fk' if modes else 'deterministic_slerp_v1')
        if projected is not None:
            for key in ('b4ml_timing_easing', 'b4ml_timing_bias', 'b4ml_transition_timing'):
                if key in candidate:
                    del candidate[key]
        else:
            candidate['b4ml_timing_easing'] = easing
            candidate['b4ml_timing_bias'] = float(timing_bias)
            candidate['b4ml_transition_timing'] = json.dumps([
                {'destination_frame': float(rows[index+1][0]),
                 'easing': timing['easing'], 'bias': timing['bias'],
                 'departure_hold': timing['departure_hold'],
                 'arrival_hold': timing['arrival_hold'],
                 'override': segment_overrides[index]}
                for index, timing in enumerate(segment_timing)
            ], sort_keys=True, separators=(',', ':'), allow_nan=False)
        state.before_modes = json.dumps(original_modes, allow_nan=False)
        state.source_action = source
        state.source_slot = source_slot
        state.before_pose = before_text
        state.candidate_action = candidate
        timing_note = (f' {override_count} transition override'
                       f'{"s" if override_count != 1 else ""}.' if projected is None and override_count else
                       (f' Timing bias {timing_bias:+.2f}.'
                        if projected is None and abs(timing_bias) > 1e-9 else ''))
        state.status = (f'Preview: {len(frames)} frames, {len(names)} controls.'
                        f'{timing_note} Original action preserved.')
        scene.frame_set(scene.frame_current, subframe=scene.frame_subframe)
        return len(frames), len(samples)
    except BaseException:
        assign_action(obj, source, source_slot)
        restore_pose(obj, before)
        rs.restore_values(obj, original_modes)
        state.before_modes = ''
        state.candidate_action = None
        state.source_action = None
        state.before_pose = ''
        state.source_slot = ''
        if candidate and candidate.users == 0:
            bpy.data.actions.remove(candidate)
        raise


def finish_preview(obj, scene, keep=False):
    require_rig(obj)
    state = obj.b4ml
    if state.body_payload or state.posing_payload or state.quadruped_payload:raise ValueError('Finish or cancel the active pose preview first')
    if state.flight_running:raise ValueError("Finish or cancel flight correction first")
    if state.contact_running:raise ValueError("Finish or cancel contact correction first")
    if state.secondary_running:raise ValueError("Finish or cancel secondary motion first")
    if state.cleanup_running:raise ValueError("Finish or cancel animation cleanup first")
    candidate = state.candidate_action
    if not candidate:
        raise ValueError("No candidate to keep or discard")
    if not obj.animation_data or obj.animation_data.action != candidate:
        raise ValueError("Active action changed. Select the B4ML candidate action before resolving its preview")
    native = motion_layer.find(obj)
    if native:
        motion_layer.validate(obj)
        if keep: motion_layer.keep(obj)
        else: motion_layer.restore(obj)
    if keep:
        if state.source_action:
            state.source_action.use_fake_user = True
        candidate.name = candidate.name.replace(' - B4ML Preview', ' - B4ML')
        candidate.use_fake_user = True
        state.kept_action = candidate
        state.kept_source = state.source_action
        state.kept_slot = state.source_slot
        state.kept_pose = state.before_pose
        state.kept_modes = state.before_modes
    else:
        before = json.loads(state.before_pose)
        assign_action(obj, state.source_action, state.source_slot)
        restore_pose(obj, before)
        rs.restore_values(obj, json.loads(state.before_modes or '{}'))
        scene.frame_set(scene.frame_current, subframe=scene.frame_subframe)
    state.source_action = None
    state.candidate_action = None
    state.before_pose = ''
    state.before_modes = ''
    state.source_slot = ''
    state.contact_input = None
    state.contact_output = None
    state.flight_input = None
    state.flight_output = None
    state.flight_metrics = ''
    state.secondary_input = None
    state.secondary_output = None
    state.secondary_metrics = ''
    state.cleanup_input = None
    state.cleanup_output = None
    state.cleanup_metrics = ''
    state.status = 'Candidate kept as a separate action' if keep else 'Original animation restored'
    if not keep and candidate.users == 0:
        bpy.data.actions.remove(candidate)


def restore_kept_source(obj, scene):
    require_rig(obj)
    state = obj.b4ml
    if state.candidate_action or state.posing_payload or state.body_payload or state.quadruped_payload or state.secondary_running or state.cleanup_running:
        raise ValueError('Resolve the current preview first')
    if not state.kept_action or not obj.animation_data or obj.animation_data.action != state.kept_action:
        raise ValueError('Select the last kept candidate before restoring its source')
    if motion_layer.find(obj): motion_layer.archive(obj)
    assign_action(obj, state.kept_source, state.kept_slot)
    restore_pose(obj, json.loads(state.kept_pose))
    rs.restore_values(obj, json.loads(state.kept_modes or '{}'))
    scene.frame_set(scene.frame_current, subframe=scene.frame_subframe)
    state.kept_action = None
    state.kept_source = None
    state.kept_slot = state.kept_pose = state.kept_modes = ''
    state.status = 'Original action and input rig modes restored; candidate remains available'


def preview_motion_result(obj, scene, result):
    """Preview a saved complete native result while retaining the current input."""
    require_rig(obj); state = obj.b4ml
    if (state.candidate_action or state.posing_payload or state.body_payload or state.quadruped_payload
            or state.flight_running or state.contact_running or state.secondary_running or state.cleanup_running or motion_layer.find(obj)):
        raise ValueError('Resolve the current preview before restoring a motion result')
    motion_layer.check_result(obj, result)
    source = obj.animation_data.action if obj.animation_data else None
    slot = _slot(obj.animation_data); pose = raw_pose(obj); modes = rs.mode_values(obj)
    action = result.get(motion_layer._RESULT_ACTION)
    if action is None: raise ValueError('Saved motion has no pose action to preview')
    candidate = action.copy(); candidate.name = obj.name + ' - B4ML Preview'
    try:
        assign_action(obj, candidate, result.get(motion_layer._RESULT_SLOT, ''))
        saved_pose = json.loads(result[motion_layer._RESULT_POSE])
        for name, values in saved_pose.items(): obj.pose.bones[name].rotation_mode = values['mode']
        restore_pose(obj, saved_pose); rs.restore_values(obj, json.loads(result[motion_layer._RESULT_MODES]))
        motion_layer.reactivate(obj, scene, result)
        state.source_action = source; state.source_slot = slot
        state.before_pose = json.dumps(pose); state.before_modes = json.dumps(modes)
        state.candidate_action = candidate
        scene.frame_set(scene.frame_current, subframe=scene.frame_subframe)
        state.status = 'Saved motion restored as an editable preview'
        return candidate
    except BaseException:
        if motion_layer.find(obj): motion_layer.restore(obj)
        assign_action(obj, source, slot)
        for name, values in pose.items(): obj.pose.bones[name].rotation_mode = values['mode']
        restore_pose(obj, pose); rs.restore_values(obj, modes)
        state.source_action = None; state.candidate_action = None; state.before_pose = state.before_modes = state.source_slot = ''
        if candidate.users == 0: bpy.data.actions.remove(candidate)
        raise
