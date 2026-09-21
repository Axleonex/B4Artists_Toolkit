"""Reversible limb posing with optional local learned bend suggestions.

Targets use world positions; control writes use evaluated parent/rest spaces.
Only animator transforms are written. Existing constraints/properties are retained.
"""
import json
import math
import time
import uuid
import bpy
from mathutils import Quaternion, Vector
from . import workflow as w
from .math_core import finite_vector, two_bone_positions
from .rig_mapping import profile_for_object
from . import rig_state as rs


def bindings(obj):
    profile = profile_for_object(obj)
    if profile.family != 'humanoid':
        raise ValueError('Assisted posing currently supports humanoids; use pose capture and interpolation for quadrupeds')
    if profile.missing or not profile.controls:
        raise ValueError('Assisted posing needs a complete mapped humanoid control rig')
    result = []
    for side in ('L', 'R'):
        for kind, parts in (('arm', ('upperarm', 'forearm', 'hand')), ('leg', ('thigh', 'shin', 'foot'))):
            fk = [profile.roles[f'{part}.fk-{side}'] for part in parts]
            row = dict(id=f'{kind}-{side}', fk=fk, joints=fk, mode='FK', ik='', pole='')
            if profile.name == 'BoneForge Control Rig':
                prop = obj.pose.bones.get('properties')
                key = f'IK_FK-{kind}-{side}'
                if prop is None or key not in prop:
                    raise ValueError('Missing BoneForge IK/FK property: ' + key)
                value = prop[key]
                row.update(joints=[f'{part}.def-{side}' for part in parts],
                           ik=f'{parts[1]}.ik-{side}', pole=f'{kind}.pole-{side}')
                row['mode'] = _mode(value, ik_value=1.)
                row['chain'] = [f'{part}.mch_ik-{side}' for part in parts[:2]]
            elif profile.name == 'Rigify Generated':
                stem = 'upper_arm' if kind == 'arm' else 'thigh'
                names = ('upper_arm', 'forearm', 'hand') if kind == 'arm' else parts
                prop = obj.pose.bones.get(f'{stem}_parent.{side}')
                if prop is None or 'IK_FK' not in prop:
                    raise ValueError('Missing Rigify IK/FK property')
                row.update(joints=[f'ORG-{part}.{side}' for part in names],
                           ik=f'{parts[2]}_ik.{side}',
                           pole=f'{stem}_ik_target.{side}' if prop.get('pole_vector', False) else '')
                row['mode'] = _mode(prop['IK_FK'], ik_value=0.)
                row['chain'] = [f'{stem}_ik.{side}', f'MCH-{names[1]}_ik.{side}']
            needed = row['fk'] + row['joints'] + ([row['ik']] if row['mode'] == 'IK' else [])
            if any(name not in obj.pose.bones for name in needed):
                raise ValueError('Incomplete limb adapter: ' + row['id'])
            if profile.name not in {'BoneForge Control Rig', 'Rigify Generated'}:
                upper, lower, end = (obj.pose.bones[n] for n in fk)
                if lower.parent != upper or end.parent != lower:
                    raise ValueError('Source skeleton needs a direct two-segment limb chain: ' + row['id'])
            result.append(row)
    root = 'torso' if profile.name == 'Rigify Generated' else profile.roles['hips']
    if profile.name in {'Mocap Humanoid','Unity Humanoid','Unreal Mannequin'}:
        # FBX can connect the pelvis to an ordinary root. Translate the first
        # unconnected ancestor without disconnecting bones or changing rest data.
        from dataclasses import replace
        translation=obj.pose.bones[root]
        while translation.bone.use_connect and translation.parent:
            translation=translation.parent
        root=translation.name
        ancestors=set();bone=obj.pose.bones[profile.roles['hips']].parent
        while bone:
            ancestors.add(bone.name);bone=bone.parent
        profile=replace(profile,controls=tuple(sorted(set(profile.controls)|ancestors)))
    return profile, root, result


def _mode(value, ik_value):
    if not isinstance(value, (float, int)) or not math.isfinite(value):
        raise ValueError('Invalid IK/FK setting')
    if abs(value - ik_value) < 1e-6:
        return 'IK'
    if abs(value - (1.-ik_value)) < 1e-6:
        return 'FK'
    raise ValueError('Choose fully FK or fully IK before posing; blended limbs are not supported yet')


def _update(obj):
    obj.update_tag(refresh={'OBJECT'})
    bpy.context.view_layer.update()


def _frame(scene):
    return scene.frame_current + scene.frame_subframe


def _matrix_values(matrix):
    return [float(v) for row in matrix for v in row]


def _check_space(obj):
    matrix = w.display_world(obj).to_3x3()
    lengths = [column.length for column in matrix.col]
    if min(lengths) < 1e-8 or matrix.determinant() <= 0:
        raise ValueError('Apply reflected or zero object scale before assisted posing')
    if max(lengths)/min(lengths) > 1.0001 or any(abs(matrix.col[i].dot(matrix.col[j])) > lengths[i]*lengths[j]*1e-4
                                              for i in range(3) for j in range(i)):
        raise ValueError('Assisted posing currently requires uniform object scale without shear')


def _check_controls(obj, names, property_name):
    ad = obj.animation_data
    for name in names:
        pb = obj.pose.bones[name]
        if (property_name == 'rotation'
                and (any(pb.lock_rotation)
                     or (pb.rotation_mode in {'QUATERNION','AXIS_ANGLE'}
                         and pb.lock_rotations_4d and pb.lock_rotation_w)
                     or not w._channels(pb)['rotation'])):
            raise ValueError('Rotation channels are locked: ' + name)
        if property_name == 'location' and len(w._channels(pb)['location']) != 3:
            raise ValueError('Location channels are locked or connected: ' + name)
        if any(not c.mute and c.influence > 0 for c in pb.constraints):
            raise ValueError('Constrained control requires a dedicated adapter: ' + name)
        paths = {pb.path_from_id(p) for p in ('location', 'scale', 'rotation_euler', 'rotation_quaternion', 'rotation_axis_angle')}
        if ad and any(fc.data_path in paths for fc in ad.drivers):
            raise ValueError('Driven control cannot be posed directly: ' + name)
        if any(not math.isfinite(v) or v <= 0 for v in pb.scale):
            raise ValueError('Use positive finite limb control scale: ' + name)


def _check_ik(obj, limbs):
    for row in limbs:
        if row['mode'] != 'IK':
            continue
        if '.fk-' in row['fk'][0]:
            raise ValueError('BoneForge assisted posing currently requires FK; its straight native IK chains need a dedicated adapter')
        chain = [obj.pose.bones.get(name) for name in row['chain']]
        if any(pb is None for pb in chain):
            raise ValueError('Missing IK mechanism for ' + row['id'])
        if any(pb.ik_stretch > 0 for pb in chain) and any(c.type == 'IK' and c.use_stretch and not c.mute
                                                         for pb in chain for c in pb.constraints):
            raise ValueError('Native IK stretch can change segment lengths: ' + row['id'] +
                             '. Use FK, or disable Stretch on its native IK constraints. Rigify IK Stretch alone is insufficient.')


def _helper(obj, scene, token, label, point, size):
    helper = bpy.data.objects.new('B4ML ' + label, None)
    helper['b4ml_owner'] = obj
    helper['b4ml_session'] = token
    scene.collection.objects.link(helper)
    helper.empty_display_type = 'SPHERE' if 'pole' not in label else 'PLAIN_AXES'
    helper.empty_display_size = size
    helper.show_in_front = True
    helper.location = point
    helper.hide_render = True
    return helper


def begin(obj, scene):
    w.require_rig(obj)
    if obj.b4ml.body_payload or obj.b4ml.quadruped_payload:raise ValueError('Resolve the whole-body preview first')
    if obj.b4ml.posing_payload or obj.b4ml.candidate_action:
        raise ValueError('Keep or cancel the active preview first')
    w._reject_nla(obj)
    snapshot = None
    try:
        if rs.mode_values(obj) != rs.canonical_modes(obj):
            snapshot = rs.normalize_fk(obj)
        result = _begin_fk(obj, scene)
        if snapshot:
            data = json.loads(obj.b4ml.posing_payload)
            data['source_snapshot'] = snapshot
            obj.b4ml.posing_payload = json.dumps(data, allow_nan=False)
            obj.b4ml.status = 'FK preview matched from input IK; keeping saves an anchor and restores input'
        return result
    except Exception:
        if obj.b4ml.posing_payload:
            _cleanup(obj, json.loads(obj.b4ml.posing_payload))
        rs.restore_snapshot(obj, snapshot)
        raise


def _begin_fk(obj, scene):
    w.require_rig(obj)
    state = obj.b4ml
    if state.posing_payload or state.candidate_action:
        raise ValueError('Keep or cancel the active preview first')
    if bpy.context.screen and bpy.context.screen.is_animation_playing:
        raise ValueError('Stop playback before assisted posing')
    w._reject_nla(obj)
    _update(obj)
    _check_space(obj)
    profile, root, limbs = bindings(obj)
    _check_controls(obj, [root], 'location')
    _check_ik(obj, limbs)
    for row in limbs:
        _check_controls(obj, row['fk'] if row['mode'] == 'FK' else [], 'rotation')
        _check_controls(obj, [row['ik']] + ([row['pole']] if row['pole'] else []) if row['mode'] == 'IK' else [], 'location')
    _update(obj)
    pose = w.raw_pose(obj, profile.controls)
    token = uuid.uuid4().hex
    ad = obj.animation_data
    head = obj.pose.bones[profile.roles['head']].tail
    feet = sum((obj.pose.bones[profile.roles[f'foot.fk-{side}']].head for side in ('L','R')), Vector()) * .5
    reference_height = (w.display_world(obj).to_3x3() @ (head-feet)).length
    payload = dict(schema=1, frame=_frame(scene), token=token, pose=pose, reference_height=reference_height,
                   rest=w._rest_signature(obj), switches=w._switches(obj),
                   world=_matrix_values(w.display_world(obj)), root=root, limbs=limbs,
                   slot=w._slot(ad) if ad else '')
    for row in limbs:
        points = [obj.pose.bones[n].head.copy() for n in row['joints']]
        row['lengths'] = [(points[i+1]-points[i]).length for i in range(2)]
        if min(row['lengths']) < 1e-7:
            raise ValueError('Degenerate limb: ' + row['id'])
        row['end'] = tuple(w.display_world(obj) @ points[2])
        row['orientation'] = tuple(obj.pose.bones[row['fk'][2]].matrix.to_quaternion())
    state.posing_source = ad.action if ad else None
    state.posing_payload = json.dumps(payload, allow_nan=False)
    state.pose_offset = (0, 0, 0)
    state.pose_strength = 1.
    try:
        for row in limbs:
            upper, lower, end = [obj.pose.bones[n].head.copy() for n in row['joints']]
            item = state.pose_targets.add()
            item.name = row['id']
            size = sum(row['lengths']) * w.display_world(obj).to_scale().x * .06
            item.target = _helper(obj, scene, token, row['id'], w.display_world(obj) @ end, size)
            # FK pole hint follows the initial bend plane. Native IK retains the rig's own pole convention.
            pole = obj.pose.bones[row['pole']].head.copy() if row['mode'] == 'IK' and row['pole'] else lower
            if row['mode'] == 'FK':
                axis = (end-upper).normalized()
                direction = lower-upper-axis*(lower-upper).dot(axis)
                if direction.length < sum(row['lengths'])*1e-5:
                    direction = obj.pose.bones[row['fk'][0]].matrix.to_3x3().col[2].copy()
                    direction -= axis*direction.dot(axis)
                pole = lower + direction.normalized()*sum(row['lengths'])
            if row['mode'] == 'FK' or row['pole']:
                item.pole = _helper(obj, scene, token, row['id'] + ' pole', w.display_world(obj) @ pole, size*.7)
        state.status = 'Move targets, adjust pelvis offset, then Solve Pose'
    except Exception:
        _cleanup(obj, payload)
        raise
    return limbs


def _read(obj, scene):
    w.require_rig(obj)
    if not obj.b4ml.posing_payload:
        raise ValueError('Start assisted posing first')
    data = json.loads(obj.b4ml.posing_payload)
    if data.get('schema') != 1:
        raise ValueError('Unsupported posing session')
    if abs(_frame(scene)-data['frame']) > 1e-5:
        raise ValueError('Return to the starting frame, or cancel this posing session')
    modes = data.get('source_snapshot', {}).get('normalized_modes', {})
    if data['rest'] != w._rest_signature(obj) or rs.without_modes(data['switches'], modes) != rs.without_modes(w._switches(obj), modes):
        raise ValueError('Rig structure or properties changed; cancel and restart posing')
    if data['world'] != _matrix_values(w.display_world(obj)):
        raise ValueError('Rig object transform changed; cancel and restart posing')
    ad = obj.animation_data
    if (ad.action if ad else None) != obj.b4ml.posing_source or (w._slot(ad) if ad else '') != data['slot']:
        raise ValueError('Active animation changed; cancel and restart posing')
    for name, value in data['pose'].items():
        pb = obj.pose.bones.get(name)
        if pb is None or pb.rotation_mode != value['mode'] or w._channels(pb) != value['channels']:
            raise ValueError('Control modes or locks changed; cancel and restart posing')
    w._reject_nla(obj)
    if modes:
        current = rs.mode_values(obj)
        if current not in (modes, data['source_snapshot']['modes']):
            raise ValueError('IK/FK modes changed outside the posing session; cancel and restart')
        # Loading or evaluating the source action may restore its original mode values.
        # Explicit Solve re-enters the recorded FK working state at the same frame.
        rs.restore_values(obj, modes)
    return data


def _write_rotation(obj, name, matrix):
    pb = obj.pose.bones[name]
    local = obj.convert_space(pose_bone=pb, matrix=matrix, from_space='POSE', to_space='LOCAL')
    quat = local.to_quaternion()
    if pb.rotation_mode == 'QUATERNION':
        if quat.dot(pb.rotation_quaternion) < 0:
            quat.negate()
        pb.rotation_quaternion = quat
    elif pb.rotation_mode == 'AXIS_ANGLE':
        axis, angle = quat.to_axis_angle()
        pb.rotation_axis_angle = (angle, *axis)
    else:
        pb.rotation_euler = quat.to_euler(pb.rotation_mode, pb.rotation_euler)
    _update(obj)


def _translate(obj, name, delta):
    pb = obj.pose.bones[name]
    matrix = pb.matrix.copy()
    matrix.translation += delta
    local = obj.convert_space(pose_bone=pb, matrix=matrix, from_space='POSE', to_space='LOCAL')
    pb.location = local.to_translation()
    _update(obj)


def _aim(obj, name, current, desired):
    if min(current.length, desired.length) < 1e-9:
        raise ValueError('Degenerate limb direction')
    pb = obj.pose.bones[name]
    rotation = current.rotation_difference(desired)
    matrix = rotation.to_matrix().to_4x4() @ pb.matrix
    matrix.translation = pb.matrix.translation
    _write_rotation(obj, name, matrix)


def _owned(helper, obj, token):
    return helper is not None and helper.get('b4ml_owner') == obj and helper.get('b4ml_session') == token


def solve(obj, scene):
    started = time.perf_counter()
    _update(w.require_rig(obj))
    data = _read(obj, scene)
    state = obj.b4ml
    strength = state.pose_strength
    offset = Vector(finite_vector(tuple(state.pose_offset), 3)) * strength
    inverse = w.display_world(obj).inverted()
    _check_ik(obj, data['limbs'])
    requests = []
    for row in data['limbs']:
        item = state.pose_targets.get(row['id'])
        if item is None:
            raise ValueError('Missing target settings; cancel and restart posing')
        if not item.enabled:
            continue
        if not _owned(item.target, obj, data['token']) or ((row['mode'] == 'FK' or row['pole']) and not _owned(item.pole, obj, data['token'])):
            raise ValueError('A pose target was deleted or replaced; cancel and restart posing')
        target = Vector(finite_vector(tuple(item.target.matrix_world.translation), 3))
        target = Vector(row['end']).lerp(target, strength)
        pole = inverse @ item.pole.matrix_world.translation if item.pole else Vector((0,0,0))
        finite_vector(tuple(pole), 3)
        _check_controls(obj, row['fk'] if row['mode'] == 'FK' else [], 'rotation')
        _check_controls(obj, [row['ik']] + ([row['pole']] if row['pole'] else []) if row['mode'] == 'IK' else [], 'location')
        requests.append((row, inverse @ target, pole))
    _check_controls(obj, [data['root']], 'location')
    before = w.raw_pose(obj, data['pose'])
    result = []
    try:
        # Reset to the captured pose so repeated solves do not accumulate drift.
        w.restore_pose(obj, data['pose'])
        _update(obj)
        if strength == 0.:
            state.status = 'Target strength is zero; starting pose restored'
            state.pose_metrics = json.dumps(dict(limbs=[], elapsed_ms=(time.perf_counter()-started)*1000))
            return []
        _translate(obj, data['root'], inverse.to_3x3() @ offset)
        learned_basis = None
        if state.learned_bend_strength > 0 and any(state.pose_targets[r['id']].learn_bend for r, _, _ in requests):
            from . import learned
            limbs = {r['id']: r for r in data['limbs']}
            landmarks = [tuple(obj.pose.bones[limbs[key]['joints'][0]].head)
                         for key in ('leg-L', 'leg-R', 'arm-L', 'arm-R')]
            learned_basis = learned.anatomical_basis(*landmarks)
        for row, target, pole in requests:
            names = row['fk'] if row['mode'] == 'FK' else row['joints']
            root = obj.pose.bones[names[0]].head.copy()
            bend_source = 'authored pole'
            if learned_basis is not None and state.pose_targets[row['id']].learn_bend:
                kind, side = row['id'].split('-')
                direction, bend_source = learned.direction(kind, tuple(root), tuple(target),
                                                          row['lengths'], learned_basis, side)
                if direction is not None:
                    axis = (target-root).normalized()
                    current = pole-root-axis*(pole-root).dot(axis)
                    suggested = Vector(direction)
                    if current.length < sum(row['lengths'])*1e-7:
                        current = suggested.copy()
                    current.normalize()
                    angle = math.atan2(axis.dot(current.cross(suggested)), current.dot(suggested))
                    blended = Quaternion(axis, angle*state.learned_bend_strength) @ current
                    pole = root+blended*sum(row['lengths'])
            joint, end = two_bone_positions(tuple(root), tuple(target), tuple(pole), *row['lengths'], state.max_bend)
            joint, end = Vector(joint), Vector(end)
            if row['mode'] == 'FK':
                upper, lower, effector = (obj.pose.bones[n] for n in names)
                _aim(obj, upper.name, lower.head-upper.head, joint-upper.head)
                _aim(obj, lower.name, effector.head-lower.head, end-lower.head)
                rotation = Quaternion(row['orientation']).to_matrix().to_4x4()
                rotation.translation = effector.head
                _write_rotation(obj, effector.name, rotation)
            else:
                if row['pole']:
                    _translate(obj, row['pole'], pole-obj.pose.bones[row['pole']].head)
                for _ in range(4):
                    delta = end-obj.pose.bones[row['joints'][2]].head
                    if delta.length < sum(row['lengths'])*1e-6:
                        break
                    _translate(obj, row['ik'], delta)

            points = [obj.pose.bones[n].head.copy() for n in row['joints']]
            error = (w.display_world(obj).to_3x3() @ (points[2]-target)).length
            residual = (points[2]-end).length / sum(row['lengths'])
            stretch = max(abs((points[i+1]-points[i]).length/row['lengths'][i]-1.) for i in range(2))
            if residual > 2e-4:
                raise ValueError('Rig could not reach the clamped target; pose restored: ' + row['id'])
            if stretch > .002:
                raise ValueError('Rig introduced limb stretch; pose restored: ' + row['id'])
            result.append(dict(limb=row['id'], mode=row['mode'], bend_source=bend_source, error=error,
                               normalized_error=error/max(data['reference_height'], 1e-8), residual=residual,
                               clamped=(end-target).length > sum(row['lengths'])*1e-5, stretch=stretch))
        elapsed = (time.perf_counter()-started)*1000
        state.status = f"Solved {len(result)} limbs in {elapsed:.1f} ms; max target error {max((r['error'] for r in result), default=0.):.5g} world units"
        if any(r['clamped'] or r['residual'] > 1e-4 for r in result):
            state.status += ' (reach/bend or rig limits)'
        learned_count = sum(r['bend_source'] == 'learned' for r in result)
        fallback_count = sum(r['bend_source'] not in ('learned', 'authored pole') for r in result)
        if learned_count or fallback_count:
            state.status += f'; learned bends {learned_count}, geometric fallbacks {fallback_count}'
        state.pose_metrics = json.dumps(dict(limbs=result, elapsed_ms=elapsed), allow_nan=False)
        return result
    except Exception:
        w.restore_pose(obj, before)
        _update(obj)
        raise


def _cleanup(obj, data):
    if _owned(bpy.context.active_object, obj, data['token']):
        visible = w.motion_layer.find(obj) or obj
        bpy.context.view_layer.objects.active = visible
        visible.select_set(True)
    # Scan by ownership as a partially-created helper may not have a property pointer yet.
    for helper in list(bpy.data.objects):
        if _owned(helper, obj, data['token']):
            bpy.data.objects.remove(helper, do_unlink=True)
    obj.b4ml.pose_targets.clear()
    obj.b4ml.posing_payload = ''
    obj.b4ml.posing_source = None
    obj.b4ml.pose_metrics = ''


def finish(obj, scene, keep=False):
    if not obj.b4ml.posing_payload:
        raise ValueError('No assisted pose to resolve')
    if keep:
        data = _read(obj, scene)
        solve(obj, scene)
        # Persist the editable result as an anchor before releasing its recovery snapshot.
        w.capture_anchor(obj, scene, False, from_posing=True)
        rs.restore_snapshot(obj, data.get('source_snapshot'))
        _cleanup(obj, data)
        obj.b4ml.status = ('Saved FK anchor and restored input rig; capture another frame to interpolate' if data.get('source_snapshot') else
                          'Kept solved pose as an anchor; capture another frame to interpolate')
    else:
        data = json.loads(obj.b4ml.posing_payload)
        ad = obj.animation_data
        compatible = data['rest'] == w._rest_signature(obj) and all(
            obj.pose.bones.get(name) and obj.pose.bones[name].rotation_mode == value['mode']
            for name, value in data['pose'].items())
        restore = compatible and (ad.action if ad else None) == obj.b4ml.posing_source
        if restore:
            frame = data['frame']
            scene.frame_set(math.floor(frame), subframe=frame-math.floor(frame))
            if data.get('source_snapshot'):
                rs.restore_snapshot(obj, data['source_snapshot'])
            else:
                w.restore_pose(obj, data['pose'])
            _update(obj)
        if not restore and data.get('source_snapshot'):
            rs.restore_values(obj, data['source_snapshot']['modes'])
            scene.frame_set(scene.frame_current, subframe=scene.frame_subframe)
        _cleanup(obj, data)
        obj.b4ml.status = ('Cancelled assisted posing; original animation keys retained' if restore else
                          'Removed targets; changed rig or animation retained without restoring incompatible transforms')
