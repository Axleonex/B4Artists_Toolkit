"""Persistent, reversible collection ownership for native character motion layers.

Internal component; not yet exposed by the released flight workflow.
SPDX-License-Identifier: GPL-2.0-or-later
"""
import json
import uuid
import bpy

_PREFIX = 'b4ml_motion_'
_RECORD = _PREFIX + 'record'
_GROUP = _PREFIX + 'group'
_INSTANCE = _PREFIX + 'instance'
_SCENE = _PREFIX + 'scene'
_TOKEN = _PREFIX + 'token'
_OWNER = _PREFIX + 'owner'
_RESULT_OWNER = 'b4ml_result_owner'
_RESULT_ACTION = 'b4ml_result_action'
_RESULT_SLOT = 'b4ml_result_slot'
_RESULT_POSE = 'b4ml_result_pose'
_RESULT_MODES = 'b4ml_result_modes'


def _source_key(i): return _PREFIX + 'source_' + str(i)
def _collection_key(i, j): return _PREFIX + 'collection_' + str(i) + '_' + str(j)
def _active_key(i): return _PREFIX + 'active_' + str(i)


def _local(value):
    return value is not None and not value.library and not value.override_library


def _read(owner):
    try:
        record = json.loads(owner[_RECORD])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError('Motion layer recovery record is missing or invalid') from exc
    if not isinstance(record, dict) or record.get('schema') != 1 or not isinstance(record.get('sources'), list) or not record['sources']:
        raise ValueError('Unsupported motion layer recovery record')
    if record.get('phase') not in ('preparing', 'active', 'kept') or not isinstance(record.get('token'), str):
        raise ValueError('Invalid motion layer ownership state')
    views = record.get('views')
    if not isinstance(views, list) or not views:
        raise ValueError('Invalid motion layer view recovery record')
    for view in views:
        if (not isinstance(view, dict) or not isinstance(view.get('name'), str)
                or not isinstance(view.get('selected'), list)
                or len(view['selected']) != len(record['sources'])
                or any(type(value) is not bool for value in view['selected'])):
            raise ValueError('Invalid motion layer view recovery record')
    if any(not isinstance(row, dict) for row in record['sources']):
        raise ValueError('Invalid motion layer source recovery record')
    return record


def _references(owner, record):
    scene = owner.get(_SCENE)
    if not isinstance(scene, bpy.types.Scene) or not _local(scene):
        raise ValueError('The original motion layer scene is missing or not editable')
    for i, _ in enumerate(record['views']):
        active = owner.get(_active_key(i))
        if active is not None and not isinstance(active, bpy.types.Object):
            raise ValueError('Invalid original active object reference')
    sources = []
    for i, row in enumerate(record['sources']):
        ob = owner.get(_source_key(i))
        if not isinstance(ob, bpy.types.Object) or not _local(ob):
            raise ValueError('A motion layer source object is missing or not editable')
        if ob.get(_OWNER) != owner:
            raise ValueError('Motion layer source ownership changed')
        links = []
        if not isinstance(row.get('links'), list) or not row['links']:
            raise ValueError('Invalid original collection record')
        for j, kind in enumerate(row['links']):
            collection = scene.collection if kind == 'root' else owner.get(_collection_key(i, j)) if kind == 'collection' else None
            if not isinstance(collection, bpy.types.Collection) or not _local(collection):
                raise ValueError('An original source collection is missing or not editable')
            links.append(collection)
        sources.append((ob, links))
    if len({ob.as_pointer() for ob, _ in sources}) != len(sources) or sources[0][0] != owner:
        raise ValueError('Invalid motion layer source set')
    return scene, sources


def _generated(owner, record):
    group, instance = owner.get(_GROUP), owner.get(_INSTANCE)
    if group is not None and (not isinstance(group, bpy.types.Collection) or group.get(_TOKEN) != record['token'] or group.get(_OWNER) != owner):
        raise ValueError('Generated motion collection ownership changed')
    if instance is not None and (not isinstance(instance, bpy.types.Object) or instance.get(_TOKEN) != record['token'] or instance.get(_OWNER) != owner):
        raise ValueError('Generated motion instance ownership changed')
    return group, instance


def find(owner):
    """Return this owner's generated instance, validating persisted references."""
    if not owner or _RECORD not in owner:
        return None
    record = _read(owner)
    _references(owner, record)
    _, instance = _generated(owner, record)
    return instance


def source(instance, scene):
    """Resolve a tagged visible instance to its source, including excluded sources."""
    if not instance or instance.type != 'EMPTY':
        return None
    owner = instance.get(_OWNER)
    if not isinstance(owner, bpy.types.Object) or owner.type != 'ARMATURE' or _RECORD not in owner:
        return None
    record = _read(owner)
    original_scene, _ = _references(owner, record)
    group, known = _generated(owner, record)
    return owner if scene == original_scene and instance == known and instance.instance_collection == group else None


def validate(owner):
    record = _read(owner)
    scene, sources = _references(owner, record)
    group, instance = _generated(owner, record)
    if record['phase'] == 'preparing' or group is None or instance is None:
        raise ValueError('Motion layer is incomplete; restore its original sources')
    if instance.instance_type != 'COLLECTION' or instance.instance_collection != group or group.name not in scene.collection.children:
        raise ValueError('Motion instance or evaluation collection changed')
    if instance.parent is not None:raise ValueError('Unparent the motion instance before continuing')
    _rigid_matrix(instance)
    if set(group.objects) != {ob for ob, _ in sources} or any(set(ob.users_collection) != {group} for ob, _ in sources):
        raise ValueError('Motion layer source membership changed')
    _check_generated_reuse(scene, sources, group, instance)
    for layer in scene.view_layers:
        child = layer.layer_collection.children.get(group.name)
        if child is None or not child.exclude:
            raise ValueError('Exclude the motion source collection in every view layer')
    return instance


def _discover(owner, scene):
    result = [owner]
    for ob in scene.objects:
        if ob.type == 'MESH' and ob.find_armature() == owner:
            result.append(ob)
    return result


def begin(owner, scene, *, objects=None, _after_move=None, _template=None):
    """Create identity instance ownership; callers author native trajectory channels.

    References, including original collections, are stored as IDs so renaming and
    .blend reload do not invalidate restoration. No rig transforms or actions change.
    _after_move is an internal fault-injection hook for transaction verification.
    """
    if not isinstance(owner, bpy.types.Object) or owner.type != 'ARMATURE' or not _local(owner) or not _local(owner.data):
        raise ValueError('Motion layers require a local editable armature')
    if not isinstance(scene, bpy.types.Scene) or not _local(scene) or owner.name not in scene.objects:
        raise ValueError('The rig must belong to the selected editable scene')
    if any(key.startswith(_PREFIX) for key in owner.keys()):
        raise ValueError('Restore the existing motion layer before creating another')
    sources = _discover(owner, scene) if objects is None else list(objects)
    if not sources or sources[0] != owner or len({ob.as_pointer() for ob in sources}) != len(sources):
        raise ValueError('Provide the owner once, followed by its character objects')
    for ob in sources:
        if not _local(ob) or (ob.data is not None and not _local(ob.data)):
            raise ValueError('Use local editable character objects')
        if ob.name not in scene.objects or set(ob.users_scene) != {scene}:
            raise ValueError('Motion layer sources must belong to only the selected scene')
        if _OWNER in ob or not ob.users_collection or any(not _local(c) for c in ob.users_collection):
            raise ValueError('A source is already managed or has no editable collection')
        if ob != owner and ob.type != 'MESH':
            raise ValueError('This motion layer adapter accepts an armature and character meshes')
    record = dict(schema=1, phase='preparing', token=uuid.uuid4().hex, sources=[], views=[])
    # Record every destination before creating or unlinking scene data.
    try:
        owner[_SCENE] = scene
        for i, ob in enumerate(sources):
            owner[_source_key(i)] = ob
            row = dict(links=[])
            for j, collection in enumerate(ob.users_collection):
                row['links'].append('root' if collection == scene.collection else 'collection')
                if collection != scene.collection: owner[_collection_key(i, j)] = collection
            record['sources'].append(row)
            ob[_OWNER] = owner
        for i, layer in enumerate(scene.view_layers):
            record['views'].append(dict(name=layer.name, selected=[ob.name in layer.objects and ob.select_get(view_layer=layer) for ob in sources]))
            if layer.objects.active is not None: owner[_active_key(i)] = layer.objects.active
        owner[_RECORD] = json.dumps(record)
        group = bpy.data.collections.new(owner.name + ' Motion Sources')
        group[_TOKEN] = record['token']; group[_OWNER] = owner; owner[_GROUP] = group
        scene.collection.children.link(group)
        instance = _copy_motion(_template) if _template is not None else bpy.data.objects.new(owner.name + ' Motion', None)
        instance.use_fake_user = False
        instance.name = owner.name + ' Motion'
        instance[_TOKEN] = record['token']; instance[_OWNER] = owner; owner[_INSTANCE] = instance
        if _template is not None:
            for action in _animation_actions(instance):
                action['b4ml_motion_generated']=record['token']
        instance.instance_type = 'COLLECTION'; instance.instance_collection = group
        scene.collection.objects.link(instance)
        for i, ob in enumerate(sources):
            group.objects.link(ob)
            for collection in tuple(ob.users_collection):
                if collection != group: collection.objects.unlink(ob)
            if _after_move is not None: _after_move(i)
        for layer in scene.view_layers:
            active = layer.objects.active
            layer.layer_collection.children[group.name].exclude = True
            if active in sources: layer.objects.active = instance
        record['phase'] = 'active'; owner[_RECORD] = json.dumps(record)
        return validate(owner)
    except BaseException:
        if _RECORD in owner:
            restore(owner)
        else:
            for ob in sources:
                if ob.get(_OWNER) == owner: del ob[_OWNER]
            for key in list(owner.keys()):
                if key.startswith(_PREFIX): del owner[key]
        raise


def keep(owner):
    """Retain a validated native layer and its recoverable source ownership."""
    instance = validate(owner); record = _read(owner)
    record['phase'] = 'kept'; owner[_RECORD] = json.dumps(record)
    return instance


def _check_generated_reuse(scene, sources, group, instance):
    """Fail before destructive cleanup when user data depends on generated IDs."""
    generated={value for value in (instance,group) if value is not None}
    if group is not None:
        if group.children:
            raise ValueError('Move child collections out of the motion sources before restoring')
        if any(ob not in {source for source, _ in sources} for ob in group.objects):
            raise ValueError('Move additional objects out of the motion source collection before restoring')
        if any(ob != instance and ob.instance_collection == group for ob in bpy.data.objects if ob.type == 'EMPTY'):
            raise ValueError('Another instance uses the motion sources; resolve it before restoring')
    if group is not None:
        parents = list(bpy.data.collections) + [s.collection for s in bpy.data.scenes]
        if any(parent != scene.collection and group.name in parent.children for parent in parents):
            raise ValueError('Another collection links the motion sources; resolve it before restoring')
    if instance is not None and set(instance.users_collection) != {scene.collection}:
        raise ValueError('The motion instance has changed collection links; resolve them before restoring')
    if instance is not None and instance.children:
        raise ValueError('Unparent user objects from the motion instance before restoring')
    if instance is not None:
        driver_owners = set()
        for prop in bpy.data.bl_rna.properties:
            if prop.type != 'COLLECTION':
                continue
            try:
                driver_owners.update(item for item in getattr(bpy.data, prop.identifier)
                                     if hasattr(item, 'animation_data'))
            except (AttributeError, TypeError):
                continue
        for owner in tuple(driver_owners):
            node_tree = getattr(owner, 'node_tree', None)
            if node_tree is not None:
                driver_owners.add(node_tree)
        for ob in bpy.data.objects:
            if ob != instance and any(getattr(constraint, 'target', None) == instance
                                      for constraint in ob.constraints):
                raise ValueError('An unrelated constraint targets the motion instance; resolve it before restoring')
            if (ob != instance and ob.type == 'ARMATURE'
                    and any(getattr(constraint, 'target', None) == instance
                            for bone in ob.pose.bones for constraint in bone.constraints)):
                raise ValueError('An unrelated pose constraint targets the motion instance; resolve it before restoring')
            if ob != instance and any(
                    getattr(constraint,field,None)==instance
                    for constraint in ob.constraints
                    for field in ('space_object','pole_target')):
                raise ValueError('An unrelated constraint references the motion instance; resolve it before restoring')
            if (ob != instance and ob.type=='ARMATURE' and any(
                    getattr(constraint,field,None)==instance
                    or any(getattr(target,'target',None)==instance
                           for target in getattr(constraint,'targets',()))
                    for bone in ob.pose.bones for constraint in bone.constraints
                    for field in ('target','space_object','pole_target'))):
                raise ValueError('An unrelated pose constraint references the motion instance; resolve it before restoring')
            if ob != instance and any(
                    getattr(modifier, prop.identifier, None) in generated
                    for modifier in ob.modifiers
                    for prop in modifier.bl_rna.properties
                    if prop.type == 'POINTER'):
                raise ValueError('An unrelated modifier targets generated motion data; resolve it before restoring')
            if ob != instance and any(
                    modifier[key] in generated
                    for modifier in ob.modifiers if modifier.type == 'NODES'
                    for key in modifier.keys()
                    if isinstance(modifier[key],bpy.types.ID)):
                raise ValueError('An unrelated modifier socket targets generated motion data; resolve it before restoring')
            if ob.type == 'CAMERA' and ob.data.dof.focus_object == instance:
                raise ValueError('An unrelated camera focuses on the motion instance; resolve it before restoring')
            if any(getattr(target,'target',None)==instance
                   for constraint in ob.constraints
                   for target in getattr(constraint,'targets',())):
                raise ValueError('An unrelated multi-target constraint uses the motion instance; resolve it before restoring')
        for owner in driver_owners:
            ad = owner.animation_data
            if owner != instance and ad and any(
                    target.id in generated
                    for curve in ad.drivers
                    for variable in curve.driver.variables
                    for target in variable.targets):
                raise ValueError('An unrelated driver targets the motion instance; resolve it before restoring')


def _animation_actions(obj):
    ad = obj.animation_data
    if ad is None:
        return []
    result = []
    if ad.action is not None:
        result.append(ad.action)
    for track in ad.nla_tracks:
        for strip in track.strips:
            if strip.action is not None and strip.action not in result:
                result.append(strip.action)
    return result


def restore(owner):
    """Restore original memberships and remove only this layer's generated objects.

    Original collection deletion or foreign generated-data ownership fails before
    mutation. Additional user collection links are preserved. Source actions,
    transforms, data and unrelated scene objects are never rewritten or deleted.
    """
    record = _read(owner); scene, sources = _references(owner, record)
    group, instance = _generated(owner, record)
    _check_generated_reuse(scene, sources, group, instance)
    # Link all originals before removing any managed links.
    for ob, collections in sources:
        for collection in collections:
            if collection not in ob.users_collection: collection.objects.link(ob)
    if group is not None:
        for ob, _ in sources:
            if ob.name in group.objects: group.objects.unlink(ob)
    for i, view in enumerate(record['views']):
        layer = scene.view_layers.get(view['name'])
        if layer is None: continue  # User-renamed/deleted view layers keep their selection.
        layer.update()  # Relinked sources must be evaluated before restoring active selection.
        for j, (ob, _) in enumerate(sources):
            if ob.name in layer.objects: ob.select_set(view['selected'][j], view_layer=layer)
        active = owner.get(_active_key(i))
        if active is not None and active.name in layer.objects: layer.objects.active = active
    if instance is not None:
        actions = _animation_actions(instance)
        owned = [action for action in actions
                 if action.get('b4ml_motion_generated') == record['token']
                 and not action.use_fake_user and not action.asset_data]
        # Keep user-authored/shared actions; only remove this layer's disposable output.
        for action in actions:
            if action not in owned:
                action.use_fake_user = True
        bpy.data.objects.remove(instance, do_unlink=True)
        for action in owned:
            if action.users == 0:
                bpy.data.actions.remove(action)
    if group is not None: bpy.data.collections.remove(group)
    for ob, _ in sources:
        if ob.get(_OWNER) == owner: del ob[_OWNER]
    for key in list(owner.keys()):
        if key.startswith(_PREFIX): del owner[key]
    return owner


def _copy_motion(instance):
    """Copy native animation, retaining driver settings and remapping self-targets."""
    copy = instance.copy()
    copied_actions = []
    try:
        if copy.animation_data:
            action_map = {}
            def private_action(action):
                if action is None:
                    return None
                key = action.as_pointer()
                if key not in action_map:
                    action_map[key] = action.copy()
                    copied_actions.append(action_map[key])
                return action_map[key]
            if copy.animation_data.action:
                copy.animation_data.action = private_action(copy.animation_data.action)
            for track in copy.animation_data.nla_tracks:
                for strip in track.strips:
                    strip.action = private_action(strip.action)
            for fc in copy.animation_data.drivers:
                for variable in fc.driver.variables:
                    for target in variable.targets:
                        if target.id == instance: target.id = copy
        for key in list(copy.keys()):
            if key.startswith(_PREFIX) or key.startswith('b4ml_result_'): del copy[key]
        return copy
    except BaseException:
        bpy.data.objects.remove(copy, do_unlink=True)
        for action in copied_actions:
            if action.users == 0: bpy.data.actions.remove(action)
        raise


def results(owner):
    """Saved editable alternatives; unlinked carriers persist through fake users."""
    return [ob for ob in bpy.data.objects if ob.get(_RESULT_OWNER) == owner]


def check_result(owner, result):
    if (not isinstance(result, bpy.types.Object) or result.type != 'EMPTY'
            or not _local(result) or result.get(_RESULT_OWNER) != owner
            or result.users_collection or result.instance_collection is not None):
        raise ValueError('Choose an intact saved motion result for this rig')
    action = result.get(_RESULT_ACTION)
    if action is not None and (not isinstance(action, bpy.types.Action) or not _local(action)):
        raise ValueError('Saved motion pose action is missing or not editable')
    from . import workflow as w
    pose = json.loads(result.get(_RESULT_POSE, '{}'))
    if set(pose) != set(owner.pose.bones.keys()): raise ValueError('Saved motion rig structure changed')
    if result.get('b4ml_result_rest') != json.dumps(w._rest_signature(owner), sort_keys=True):
        raise ValueError('Saved motion rest pose changed')
    slot = result.get(_RESULT_SLOT, '')
    if action and slot and hasattr(action, 'slots') and not any(s.identifier == slot for s in action.slots):
        raise ValueError('Saved motion action slot is missing')
    return result


def archive(owner):
    """Preserve complete native motion plus pose action, then restore source links."""
    from . import workflow as w, rig_state as rs
    instance = validate(owner)
    result = _copy_motion(instance)
    pose_action = None
    try:
        result.name = owner.name + ' - Saved Motion'
        result.instance_collection = None; result.instance_type = 'NONE'; result.use_fake_user = True
        result[_RESULT_OWNER] = owner
        if owner.animation_data and owner.animation_data.action:
            pose_action = owner.animation_data.action.copy()
            result[_RESULT_ACTION] = pose_action
        result[_RESULT_SLOT] = w._slot(owner.animation_data)
        result[_RESULT_POSE] = json.dumps(w.raw_pose(owner))
        result[_RESULT_MODES] = json.dumps(rs.mode_values(owner))
        result['b4ml_result_rest'] = json.dumps(w._rest_signature(owner), sort_keys=True)
        check_result(owner, result)
        restore(owner)
        return result
    except BaseException:
        actions = _animation_actions(result)
        bpy.data.objects.remove(result, do_unlink=True)
        for action in [*actions, pose_action]:
            if action and action.users == 0: bpy.data.actions.remove(action)
        raise


def reactivate(owner, scene, result):
    """Create an independent editable layer; workflow restores its pose candidate."""
    return begin(owner, scene, _template=check_result(owner, result))


def _rigid_matrix(instance):
    matrix=instance.matrix_world.copy();rotation=matrix.to_quaternion().to_matrix()
    if any(abs(matrix[i][j]-rotation[i][j])>1e-6 for i in range(3) for j in range(3)) or matrix.to_3x3().determinant()<0:
        raise ValueError('Native motion layers require a rigid transform without scale, shear or reflection')
    if instance.instance_collection and instance.instance_collection.instance_offset.length>1e-8:
        raise ValueError('Restore the motion source collection instance offset before authoring')
    return matrix


def transform(owner):
    """Displayed rigid transform shared by every native-layer-aware workflow."""
    from mathutils import Matrix
    instance=find(owner)
    if instance is None:return Matrix.Identity(4)
    if instance.parent is not None:raise ValueError('Unparent the motion instance before continuing')
    return _rigid_matrix(instance)


def offset(owner):
    """Legacy translation view; callers that cannot consume rotation fail closed."""
    from mathutils import Vector
    matrix=transform(owner)
    if any(abs(matrix[i][j]-(1. if i==j else 0.))>1e-6 for i in range(3) for j in range(3)):
        raise ValueError('This authoring operation requires restoring the rotated native motion layer first')
    return matrix.translation.copy()
