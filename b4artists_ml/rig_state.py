"""Explicit rig-mode conversion and reversible state for generated humanoids.

No rig constructors or external add-ons are imported. Native IK constraints and
mechanism transforms are never edited; evaluated joints are matched onto FK controls.
"""
import json
import math
import bpy
from .rig_mapping import profile_for_object


def mode_bindings(obj):
    profile = profile_for_object(obj)
    result = []
    if profile.family != 'humanoid' or profile.name not in {'BoneForge Control Rig', 'Rigify Generated'} or profile.missing:
        return result
    for side in ('L', 'R'):
        for kind, parts in (('arm', ('upperarm','forearm','hand')), ('leg', ('thigh','shin','foot'))):
            fk = [profile.roles[f'{part}.fk-{side}'] for part in parts]
            if profile.name == 'BoneForge Control Rig':
                prop, key, value = 'properties', f'IK_FK-{kind}-{side}', 0.
                joints = [f'{part}.def-{side}' for part in parts]
            else:
                stem = 'upper_arm' if kind == 'arm' else 'thigh'
                prop, key, value = f'{stem}_parent.{side}', 'IK_FK', 1.
                stems = ('upper_arm','forearm','hand') if kind == 'arm' else parts
                joints = [f'ORG-{part}.{side}' for part in stems]
            if prop not in obj.pose.bones or key not in obj.pose.bones[prop] or any(n not in obj.pose.bones for n in fk+joints):
                raise ValueError('Incomplete generated humanoid rig-state mapping')
            result.append(dict(property_bone=prop, key=key, fk_value=value, controls=fk, joints=joints))
    return result


def mode_values(obj):
    result = {}
    for row in mode_bindings(obj):
        result.setdefault(row['property_bone'], {})[row['key']] = obj.pose.bones[row['property_bone']][row['key']]
    return result


def canonical_modes(obj):
    result = {}
    for row in mode_bindings(obj):
        result.setdefault(row['property_bone'], {})[row['key']] = row['fk_value']
    return result


def property_paths(obj, values):
    return {obj.pose.bones[name].path_from_id() + '[' + json.dumps(key, ensure_ascii=False) + ']': value
            for name, props in values.items() for key, value in props.items()}


def without_modes(values, modes):
    return {name: {key:value for key,value in props.items() if key not in modes.get(name,{})}
            for name,props in values.items() if any(key not in modes.get(name,{}) for key in props)}


def restore_values(obj, values):
    for name, props in values.items():
        pb = obj.pose.bones.get(name)
        if pb:
            for key, value in props.items():
                if key in pb:
                    pb[key] = value
    obj.update_tag(refresh={'OBJECT'})
    bpy.context.view_layer.update()


def normalize_fk(obj):
    """Match the current evaluated pose to FK; caller owns restoring the snapshot.

    Returns the original editable transforms/modes and the canonical modes. Failure
    restores the input state. This operation writes no animation keys.
    """
    from . import workflow as w
    rows = mode_bindings(obj)
    if not rows:
        return None
    profile = profile_for_object(obj)
    bpy.context.view_layer.update()
    before = dict(pose=w.raw_pose(obj, profile.controls), modes=mode_values(obj))
    targets = {n: obj.pose.bones[j].matrix.copy() for r in rows for n,j in zip(r['controls'],r['joints'])}
    origin = next(iter(targets.values())).translation
    reference = max(1e-8, max((matrix.translation-origin).length for matrix in targets.values()))
    desired_modes = {}
    for row in rows:
        desired_modes.setdefault(row['property_bone'], {})[row['key']] = row['fk_value']
        pb = obj.pose.bones[row['property_bone']]
        path = pb.path_from_id() + '[' + json.dumps(row['key']) + ']'
        if obj.animation_data and any(fc.data_path == path for fc in obj.animation_data.drivers):
            raise ValueError('Driven IK/FK mode cannot be normalized')
        value = pb[row['key']]
        if not isinstance(value, (int,float)) or not math.isfinite(value) or not 0 <= value <= 1:
            raise ValueError('Invalid IK/FK mode')
        if abs(value-row['fk_value']) < 1e-7:
            continue
        for name in row['controls']:
            bone = obj.pose.bones[name]
            if (any(bone.lock_rotation)
                    or (bone.rotation_mode in {'QUATERNION','AXIS_ANGLE'}
                        and bone.lock_rotations_4d and bone.lock_rotation_w)
                    or not w._channels(bone)['rotation']
                    or any(not c.mute and c.influence for c in bone.constraints)):
                raise ValueError('FK matching requires unlocked, unconstrained rotations: ' + name)
            paths = {bone.path_from_id(p) for p in ('location','scale','rotation_euler','rotation_quaternion','rotation_axis_angle')}
            if obj.animation_data and any(fc.data_path in paths for fc in obj.animation_data.drivers):
                raise ValueError('FK matching cannot overwrite driven controls: ' + name)
    try:
        restore_values(obj, desired_modes)
        for row in rows:
            if abs(before['modes'][row['property_bone']][row['key']]-row['fk_value']) < 1e-7:
                continue
            for name in row['controls']:
                pb = obj.pose.bones[name]
                local = obj.convert_space(pose_bone=pb, matrix=targets[name], from_space='POSE', to_space='LOCAL')
                loc, rotation, scale = local.decompose()
                channels = w._channels(pb)
                for i in range(3):
                    if i in channels['location']:
                        pb.location[i] = loc[i]
                    elif abs(pb.location[i]-loc[i]) > 2e-5*reference:
                        raise ValueError('Pose requires moving a locked/connected FK control: ' + name)
                    if i in channels['scale']:
                        pb.scale[i] = scale[i]
                    elif abs(pb.scale[i]-scale[i]) > 2e-5:
                        raise ValueError('Pose requires changing locked FK scale: ' + name)
                if pb.rotation_mode == 'QUATERNION':
                    if rotation.dot(pb.rotation_quaternion) < 0:
                        rotation.negate()
                    pb.rotation_quaternion = rotation
                elif pb.rotation_mode == 'AXIS_ANGLE':
                    axis, angle = rotation.to_axis_angle()
                    pb.rotation_axis_angle = (angle,*axis)
                else:
                    pb.rotation_euler = rotation.to_euler(pb.rotation_mode, pb.rotation_euler)
                obj.update_tag(refresh={'OBJECT'})
                bpy.context.view_layer.update()
        max_position = 0.
        for row in rows:
            for name, joint in zip(row['controls'], row['joints']):
                actual, target = obj.pose.bones[joint].matrix, targets[name]
                error = (actual.translation-target.translation).length
                max_position = max(max_position, error)
                angle = actual.to_quaternion().rotation_difference(target.to_quaternion()).angle
                angle = min(angle, abs(2*math.pi-angle))
                scale_error = max(abs(a-b)/max(abs(b),1e-8) for a,b in zip(actual.to_scale(),target.to_scale()))
                if error > 2e-4*reference or angle > .001 or scale_error > 2e-4:
                    raise ValueError('FK conversion failed evaluated-pose verification: ' + joint)
        before['normalized_modes'] = desired_modes
        before['max_position_error'] = max_position
        before['normalized_position_error'] = max_position/reference
        return before
    except Exception:
        w.restore_pose(obj, before['pose'])
        restore_values(obj, before['modes'])
        raise


def restore_snapshot(obj, snapshot):
    if snapshot:
        from .workflow import restore_pose
        restore_pose(obj, snapshot['pose'])
        restore_values(obj, snapshot['modes'])
