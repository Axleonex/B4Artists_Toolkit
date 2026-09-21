"""Persistent whole-body preview ownership and recoverable cooperative requests.
SPDX-License-Identifier: GPL-2.0-or-later
"""
import json,math,uuid
import bpy
import numpy as np
from mathutils import Matrix,Vector,Quaternion
from importlib.resources import files
from . import body_solver as solver,workflow as w,posing as p,rig_state as rs
from .body_model import decode_model
from . import balance
from .record_cache import RecordCopies

_LIVE={}
_JOBS={}
_RECORDS=RecordCopies()
TARGETS_V1=((0,'Pelvis'),(4,'Head'),(7,'Hand L'),(10,'Hand R'),(13,'Foot L'),(16,'Foot R'))
TARGETS_V2=((0,'Pelvis'),(2,'Chest'),(4,'Head'),(7,'Hand L'),(10,'Hand R'),(13,'Foot L'),(16,'Foot R'))
TARGETS=((0,'Pelvis'),(2,'Chest'),(3,'Neck'),(4,'Head'),(7,'Hand L'),(10,'Hand R'),(13,'Foot L'),(16,'Foot R'))
TARGETS_V3=((0,'Pelvis'),(1,'Spine'),(2,'Chest'),(3,'Neck'),(4,'Head'),(7,'Hand L'),(10,'Hand R'),(13,'Foot L'),(16,'Foot R'))
POLE_JOINTS={7:6,10:9,13:12,16:15}
MIRROR_PAIRS=(('Hand L','Hand R'),('Foot L','Foot R'))
POSE_ASSET_KEY='b4ml_semantic_target_pose_asset_v1'
POSE_ASSET_MAX_CHARS=65536


def _target_rows(record):
    version=record.get('controls_version',0)
    if (isinstance(version,int) and version>=6) or (isinstance(version,int) and version>=5 and record.get('torso_coupling_version')==1):return TARGETS_V3
    if isinstance(version,int) and version>=5:return TARGETS
    return TARGETS_V2 if isinstance(version,int) and version>=2 else TARGETS_V1


def target_supports_orientation(label):
    return any(index in solver.SUPPORTED_ORIENTATION_JOINTS and name==label
               for index,name in TARGETS_V3)


def target_orientation_version(label):
    if label=='Neck':return 5
    if label=='Chest':return 4
    return 1


def target_supports_pole(label):
    return any(index in POLE_JOINTS and name==label for index,name in TARGETS)


def _world_orientation(s,index):
    if index==0:q=s.pelvis_rotation
    elif index in solver.DISTRIBUTED_ORIENTATION_JOINTS:
        q=s.obj.pose.bones[solver.orientation_bone(s.binding,index)].matrix.to_quaternion()
    elif index in solver.ORIENTATION_JOINTS:
        q=s.orientations[solver.orientation_bone(s.binding,index)]
    else:q=s.obj.pose.bones[s.binding['names'][index]].matrix.to_quaternion()
    return s.world.to_quaternion()@q



def _plain(value):
    return json.loads(json.dumps(value,allow_nan=False))


def _export(s):
    data={n:getattr(s,n) for n in ('binding','source','source_modes','normalized','modes','switches','frame','slot','structure','scale','lengths')}
    for n in ('rest','baseline','basis','origin'):data[n]=getattr(s,n).tolist()
    data['balance_reference']=s.balance_reference.tolist()
    data['world']=[list(row) for row in s.world]
    data['q0']=[list(q) for q in s.q0]
    data['root_location']=list(s.root_location);data['pelvis_rotation']=list(s.pelvis_rotation)
    data['orientations']={n:list(q) for n,q in s.orientations.items()}
    return _plain(data)


def _decode(payload):
    return _RECORDS.read(payload)


class _ReadScope:
    """Borrow decoded data only during one read-only request traversal.

    Every read still compares the current serialized value. Completion writes
    use ordinary _read calls and therefore receive an independent mutable record.
    Scope exit releases the decoded data; a later tick gets a fresh mutable tree.
    """
    def __init__(self,obj):
        self.obj=obj;self.active=False;self.closed=False
        self.payload=None;self.record=None

    def __enter__(self):
        if self.active or self.closed:raise ValueError('Preview read scope cannot be reused')
        self.active=True;return self

    def __exit__(self,*args):
        self.active=False;self.closed=True;self.payload=None;self.record=None

    def read(self,obj):
        if not self.active or obj!=self.obj:raise ValueError('Preview read scope has no ownership of this rig')
        payload=obj.b4ml.body_payload
        if self.record is None or payload!=self.payload:
            # Publish a cached value only after successful decoding/validation.
            record=_decode(payload)
            self.payload=payload;self.record=record
        return self.record


def _read(obj,*,_scope=None):
    return _scope.read(obj) if _scope is not None else _decode(obj.b4ml.body_payload)


def _validate_record(obj,record):
    w.require_rig(obj);w._reject_nla(obj)
    d=record['session'];binding=solver.mapping(obj)
    if 'motion_transform' in record:
        saved=np.asarray(record['motion_transform'],dtype=float);current=np.asarray(w.motion_layer.transform(obj),dtype=float)
        if saved.shape!=(4,4) or not np.isfinite(saved).all() or not np.allclose(saved,current,atol=1e-7,rtol=0.):raise ValueError('Return the native motion layer to its saved transform before recovering')
    elif record.get('motion_offset',[0.,0.,0.])!=list(w.motion_layer.offset(obj)):
        raise ValueError('Return the native motion layer to its saved position before recovering')
    if d['binding']!=binding or d['structure']!=w._rest_signature(obj):raise ValueError('Rig changed; saved whole-body recovery needs the original rig')
    if d['world']!=[list(row) for row in obj.matrix_world]:raise ValueError('Return the rig object to its saved transform before recovering')
    ad=obj.animation_data;action=ad.action if ad else None
    if action!=obj.b4ml.body_source or (record['had_action'] and obj.b4ml.body_source is None):raise ValueError('Return to the source action before recovering this preview')
    if (w._slot(ad) if ad else '')!=d['slot']:raise ValueError('Return to the source action slot')
    for pose in (d['source'],d['normalized'],record['preview']):
        if set(pose)!=set(binding['controls']):raise ValueError('Invalid saved control set')
        for name,row in pose.items():
            pb=obj.pose.bones[name]
            if row['mode']!=pb.rotation_mode or row['channels']!=_plain(w._channels(pb)):raise ValueError('Restore the saved control modes and locks before recovery')
            for field,size in (('location',3),('scale',3),('rotation',4),('raw_rotation',4 if row['mode'] in ('QUATERNION','AXIS_ANGLE') else 3)):
                a=np.asarray(row[field],float)
                if a.shape!=(size,) or not np.isfinite(a).all():raise ValueError('Invalid saved control values')
    canonical=rs.canonical_modes(obj)
    if d['modes']!=canonical:raise ValueError('Invalid saved working modes')
    if {n:set(v) for n,v in d['source_modes'].items()}!={n:set(v) for n,v in canonical.items()}:raise ValueError('Invalid saved source modes')
    if any(not isinstance(v,(int,float)) or not math.isfinite(v) or not 0<=v<=1 for props in d['source_modes'].values() for v in props.values()):raise ValueError('Invalid source mode value')
    if len(d['frame'])!=2 or not all(math.isfinite(v) for v in d['frame']):raise ValueError('Invalid saved frame')
    return d


def _get(obj,*,_scope=None):
    key=obj.as_pointer();record=_read(obj,_scope=_scope)
    if key in _LIVE:
        s=_LIVE[key];s._validate();return s
    d=_validate_record(obj,record)
    if tuple(d['frame'])!=(bpy.context.scene.frame_current,bpy.context.scene.frame_subframe):raise ValueError('Return to the whole-body preview frame, or cancel it')
    if solver._SESSIONS.get(key) is not None:raise ValueError('Another solver owns this rig')
    s=solver.Session.__new__(solver.Session)
    s.balance_reference=None
    if 'balance_reference' in d:
        reference=np.asarray(d['balance_reference'],dtype=float)
        if reference.shape!=(17,4,4) or not np.isfinite(reference).all():raise ValueError('Invalid saved balance reference')
        s.balance_reference=reference
    for name in ('binding','source','source_modes','normalized','modes','switches','slot','structure','scale','lengths'):setattr(s,name,d[name])
    for name,shape in (('rest',(17,3)),('baseline',(17,3)),('basis',(3,3)),('origin',(3,))):
        a=np.asarray(d[name],float)
        if a.shape!=shape or not np.isfinite(a).all():raise ValueError('Invalid saved body frame')
        setattr(s,name,a)
    if not math.isfinite(s.scale) or s.scale<=1e-8:raise ValueError('Invalid saved body scale')
    if not np.allclose(s.basis.T@s.basis,np.eye(3),atol=1e-5) or np.linalg.det(s.basis)<0:raise ValueError('Invalid saved body axes')
    s.obj=obj;s.owner_key=key;s.closed=False;s.running=False;s.frame=tuple(d['frame']);s.world=Matrix(d['world'])
    s.action=obj.b4ml.body_source;s.root_location=Vector(d['root_location']);s.pelvis_rotation=Quaternion(d['pelvis_rotation'])
    s.q0=[Quaternion(q) for q in d['q0']];s.orientations={n:Quaternion(q) for n,q in d['orientations'].items()}
    if len(s.q0)!=len(s.binding['rotations']) or set(s.orientations)!=set(s.binding['effectors']):raise ValueError('Invalid saved rotation binding')
    vectors=[d['root_location'],d['pelvis_rotation'],*d['q0'],*d['orientations'].values()]
    for i,value in enumerate(vectors):
        a=np.asarray(value,float);size=3 if i==0 else 4
        if a.shape!=(size,) or not np.isfinite(a).all() or (i>0 and abs(np.linalg.norm(a)-1)>1e-4):raise ValueError('Invalid saved solver transform')
    if not set(s.binding['names'])<=set(s.lengths) or any(n not in obj.pose.bones or not math.isfinite(v) or v<=0 for n,v in s.lengths.items()):raise ValueError('Invalid saved bone lengths')
    s.params=decode_model(files(__package__).joinpath('models','context_pose_mlp_v1.npz').read_bytes())
    before=w.raw_pose(obj,s.binding['controls']);before_modes=rs.mode_values(obj)
    try:
        rs.restore_values(obj,s.modes);w.restore_pose(obj,record['preview']);p._update(obj)
        solver._SESSIONS[key]=s;s._validate();_LIVE[key]=s
    except Exception:
        solver._SESSIONS.pop(key,None);w.restore_pose(obj,before);rs.restore_values(obj,before_modes);raise
    return s


def begin(obj,scene):
    if obj.b4ml.body_payload:raise ValueError('Resolve the existing whole-body preview first')
    if obj.b4ml.quadruped_payload:raise ValueError('Resolve the quadruped pose preview first')
    if bpy.context.screen and bpy.context.screen.is_animation_playing:raise ValueError('Stop playback before posing')
    s=solver.Session(obj);token=uuid.uuid4().hex;state=obj.b4ml
    state.body_source=s.action
    motion=w.motion_layer.transform(obj)
    record=dict(schema=1,controls_version=5,torso_coupling_version=1,target_origins={},target_matrices={},pole_display_origins={},pole_matrices={},motion_transform=[list(row) for row in motion],pole_origins={},token=token,had_action=s.action is not None,session=_export(s),preview=_plain(s.normalized),signature=None)
    state.body_payload=json.dumps(record,allow_nan=False);_LIVE[obj.as_pointer()]=s
    state.body_influence=1.;state.body_strength=1.;state.body_running=False
    try:
        # Retain artist settings between previews, but never bind stale controls
        # from a different adapter. Existing previews have an empty collection.
        names=list(dict.fromkeys(s.binding['rotations']+s.binding['effectors']))
        fields=('enabled','swing','twist_min','twist_max','space','use_bend_plane','bend_axis','bend_min','bend_max','bend_sideways','preset_provenance')
        saved={i.name:{n:getattr(i,n) for n in fields} for i in state.body_limits}
        joint_frames=solver.joint_frames.bind(obj,s.binding)
        if state.body_limit_control not in names:state.body_limit_control=s.binding['effectors'][0]
        state.body_limits.clear()
        for name in names:
            item=state.body_limits.add();item.name=name
            item.joint_available=name in joint_frames
            if name in saved:
                for field,value in saved[name].items():setattr(item,field,value)
        points=s.world_points(s.baseline)
        for index,label in _target_rows(record):
            item=state.body_targets.add();item.name=label;item.enabled=label not in {'Spine','Chest','Neck'}
            item.target=p._helper(obj,scene,token,'Body '+label,motion@Vector(points[index]),s.scale*.06)
            record['target_origins'][label]=list(item.target.location)
            item.target.empty_display_type='ARROWS';item.target.rotation_mode='QUATERNION'
            item.target.rotation_quaternion=motion.to_quaternion()@_world_orientation(s,index)
            target_matrix=Matrix.LocRotScale(item.target.location,item.target.rotation_quaternion,Vector((1.,1.,1.)))
            record['target_matrices'][label]=[list(row) for row in target_matrix]
            item.use_orientation=False;item.use_pole=False
            if index in POLE_JOINTS:
                middle=POLE_JOINTS[index];chain=solver.POLE_CHAINS[middle]
                axis=points[chain[2]]-points[chain[0]];axis/=np.linalg.norm(axis)
                bend=points[middle]-points[chain[0]];bend-=axis*np.dot(bend,axis)
                if np.linalg.norm(bend)<1e-6:
                    bend=s.basis[:,1].copy();bend-=axis*np.dot(bend,axis)
                    if np.linalg.norm(bend)<1e-6:
                        bend=np.eye(3)[np.argmin(np.abs(axis))];bend-=axis*np.dot(bend,axis)
                point=points[middle]+bend/np.linalg.norm(bend)*s.scale*.4
                item.pole=p._helper(obj,scene,token,'Body '+label+' pole',motion@Vector(point),s.scale*.08)
                item.pole.empty_display_type='CIRCLE';item.pole.empty_display_size=s.scale*.1
                item.pole_distance=.4
                record['pole_origins'][label]=point.tolist()
                record['pole_display_origins'][label]=list(item.pole.location)
                record['pole_matrices'][label]=[list(row) for row in Matrix.Translation(item.pole.location)]
        state.body_payload=json.dumps(record,allow_nan=False)
        state.status='Move pelvis, chest, neck, head, hand or foot targets; rotation and limb directions are optional'
    except Exception:
        finish(obj,scene,False);raise


def _reset_matrix(value, message):
    matrix=np.asarray(value,dtype=float)
    if matrix.shape!=(4,4) or not np.isfinite(matrix).all():
        raise ValueError(message)
    if not np.allclose(matrix[3],(0.,0.,0.,1.),atol=1e-8):
        raise ValueError(message)
    axes=matrix[:3,:3]
    if np.linalg.det(axes)<=0 or not np.allclose(axes.T@axes,np.eye(3),atol=1e-6):
        raise ValueError(message)
    return Matrix(matrix.tolist())


def _reset_affine(value, message):
    matrix=np.asarray(value,dtype=float)
    if matrix.shape!=(4,4) or not np.isfinite(matrix).all():
        raise ValueError(message)
    if not np.allclose(matrix[3],(0.,0.,0.,1.),atol=1e-8):
        raise ValueError(message)
    if np.linalg.det(matrix[:3,:3])<=1e-12:
        raise ValueError(message)
    return Matrix(matrix.tolist())


def _matched_motion_transform(obj,record,action):
    """Return the saved display transform only while the native layer still matches it."""
    message='Invalid saved motion transform for '+action
    saved=_reset_affine(record.get('motion_transform'),message)
    current=_reset_affine(w.motion_layer.transform(obj),'Invalid current motion transform for '+action)
    if not np.allclose(np.asarray(saved,float),np.asarray(current,float),atol=1e-7,rtol=0.):
        raise ValueError('Return the native motion layer to its preview-start transform before '+action)
    return saved


def _reset_quaternion(value, message):
    q=np.asarray(value,dtype=float)
    if q.shape!=(4,) or not np.isfinite(q).all() or abs(np.linalg.norm(q)-1.)>1e-4:
        raise ValueError(message)
    return Quaternion(q.tolist())


def _legacy_target_matrix(record,index,label):
    origin=np.asarray(record.get('target_origins',{}).get(label),dtype=float)
    if origin.shape!=(3,) or not np.isfinite(origin).all():
        raise ValueError('Invalid saved whole-body target')
    data=record.get('session')
    if not isinstance(data,dict):
        raise ValueError('Invalid saved whole-body target orientation')
    world=_reset_affine(data.get('world'),'Invalid saved whole-body target orientation')
    motion=_reset_affine(record.get('motion_transform'),'Invalid saved motion transform')
    if index==0:
        local=_reset_quaternion(data.get('pelvis_rotation'),'Invalid saved whole-body target orientation')
    elif index in solver.ORIENTATION_JOINTS:
        offset=solver.ORIENTATION_JOINTS.index(index)-1
        try:name=data['binding']['effectors'][offset]
        except (KeyError,IndexError,TypeError):
            raise ValueError('Invalid saved whole-body target orientation') from None
        local=_reset_quaternion(data.get('orientations',{}).get(name),
                                'Invalid saved whole-body target orientation')
    else:
        raise ValueError('Restart this older preview to reset the '+label+' target')
    orientation=motion.to_quaternion()@world.to_quaternion()@local
    return Matrix.LocRotScale(Vector(origin),orientation,Vector((1.,1.,1.)))


def _saved_target_matrix(record,index,label):
    value=record.get('target_matrices',{}).get(label)
    return (_reset_matrix(value,'Invalid saved whole-body target')
            if value is not None else _legacy_target_matrix(record,index,label))


def _saved_pole_matrix(record,label):
    value=record.get('pole_matrices',{}).get(label)
    if value is not None:
        return _reset_matrix(value,'Invalid saved pole target')
    origin=np.asarray(record.get('pole_display_origins',{}).get(label),dtype=float)
    if origin.shape!=(3,) or not np.isfinite(origin).all():
        raise ValueError('Invalid saved pole target')
    return Matrix.Translation(Vector(origin))


def _require_resettable_helper(helper,label,action='Reset'):
    if helper.parent is not None:
        raise ValueError(label+' helper is parented; remove the parent before '+action)
    if len(helper.constraints):
        raise ValueError(label+' helper has constraints; remove them before '+action)
    if helper.animation_data is not None:
        raise ValueError(label+' helper is animated or driven; clear its animation before '+action)
    values=(*helper.delta_location,*helper.delta_rotation_euler,*helper.delta_rotation_quaternion,
            *helper.delta_scale)
    if not np.isfinite(np.asarray(values,float)).all():
        raise ValueError(label+' helper has invalid delta transforms')
    if (not np.allclose(helper.delta_location,(0.,0.,0.),atol=1e-9)
            or not np.allclose(helper.delta_rotation_euler,(0.,0.,0.),atol=1e-9)
            or not np.allclose(helper.delta_rotation_quaternion,(1.,0.,0.,0.),atol=1e-9)
            or not np.allclose(helper.delta_scale,(1.,1.,1.),atol=1e-9)):
        raise ValueError(label+' helper has delta transforms; clear them before '+action)


def _restore_helper(helper,snapshot):
    mode,matrix=snapshot
    helper.rotation_mode=mode
    helper.matrix_world=matrix


def _cleanup_recovered_session(key,recovered):
    """Remove only the exact runtime owner reconstructed by the current operation."""
    if recovered is None:return
    if _LIVE.get(key) is recovered:_LIVE.pop(key,None)
    if solver._SESSIONS.get(key) is recovered:solver._SESSIONS.pop(key,None)
    recovered.closed=True


def _finish_recovered_helper(obj,key,recovered,pose_before,modes_before):
    """Preserve direct rig edits when a helper briefly rebuilds runtime state."""
    if recovered is None:return
    w.restore_pose(obj,pose_before);rs.restore_values(obj,modes_before);p._update(obj)
    _cleanup_recovered_session(key,recovered)


def reset_target(obj, label):
    """Atomically restore one owned helper to its verified preview-start matrix."""
    state=obj.b4ml;key=obj.as_pointer()
    if key in _JOBS or state.body_running:
        raise ValueError('Finish or cancel the running solve before resetting a target')
    if state.body_live:
        raise ValueError('Stop Live Solve before resetting a target')
    record=_read(obj);rows={name:index for index,name in _target_rows(record)}
    if label not in rows:
        raise ValueError('Unknown whole-body target: '+label)
    index=rows[label];item=state.body_targets.get(label)
    if item is None or not p._owned(item.target,obj,record['token']):
        raise ValueError('Whole-body target is missing or replaced')
    target=item.target;pole=None
    if index in POLE_JOINTS:
        pole=item.pole
        if not p._owned(pole,obj,record['token']):
            raise ValueError('Pole target is missing or replaced')
    _require_resettable_helper(target,label)
    if pole is not None:_require_resettable_helper(pole,label+' pole')
    target_expected=_saved_target_matrix(record,index,label)
    pole_expected=_saved_pole_matrix(record,label) if pole is not None else None
    target_before=(target.rotation_mode,target.matrix_world.copy())
    pole_before=(pole.rotation_mode,pole.matrix_world.copy()) if pole is not None else None
    pole_distance_before=item.pole_distance
    pose_before=w.raw_pose(obj);modes_before=rs.mode_values(obj);status_before=state.status
    live_before=_LIVE.get(key);recovered=None
    try:
        session=_get(obj)
        if live_before is None:recovered=session
        target.rotation_mode='QUATERNION';target.matrix_world=target_expected
        if pole is not None:
            pole.rotation_mode='XYZ';pole.matrix_world=pole_expected;item.pole_distance=.4
        bpy.context.view_layer.update()
        if not np.allclose(np.asarray(target.matrix_world,float),
                           np.asarray(target_expected,float),atol=1e-7):
            raise ValueError(label+' helper could not be restored to its preview-start transform')
        if pole is not None and not np.allclose(np.asarray(pole.matrix_world,float),
                                                np.asarray(pole_expected,float),atol=1e-7):
            raise ValueError(label+' pole helper could not be restored to its preview-start transform')
    except BaseException:
        try:
            w.restore_pose(obj,pose_before);rs.restore_values(obj,modes_before);p._update(obj)
            _restore_helper(target,target_before)
            if pole is not None:
                _restore_helper(pole,pole_before);item.pole_distance=pole_distance_before
            bpy.context.view_layer.update();state.status=status_before
        finally:_cleanup_recovered_session(key,recovered)
        raise
    state.status=f'{label} helper reset to preview start; solve again if the request changed'
    _finish_recovered_helper(obj,key,recovered,pose_before,modes_before)
    orientation=(target_supports_orientation(label)
                 and record.get('controls_version',0)>=target_orientation_version(label))
    return dict(label=label,orientation=orientation,
                pole=pole is not None,controls_version=record.get('controls_version',0))


def _place_pole_from_current_bend(obj,label,direction,action):
    """Place one owned pole helper along or opposite the evaluated bend plane."""
    if direction not in (-1.,1.):raise ValueError('Invalid pole direction operation')
    state=obj.b4ml;key=obj.as_pointer()
    if key in _JOBS or state.body_running:
        raise ValueError('Finish or cancel the running solve before using '+action)
    if state.body_live:
        raise ValueError('Stop Live Solve before using '+action)
    record=_read(obj);rows={name:index for index,name in _target_rows(record)}
    if label not in rows:
        raise ValueError('Unknown whole-body target: '+label)
    index=rows[label]
    if index not in POLE_JOINTS:
        raise ValueError(label+' does not support pole alignment')
    item=state.body_targets.get(label)
    if item is None or not p._owned(item.target,obj,record['token']):
        raise ValueError('Whole-body target is missing or replaced')
    pole=item.pole
    if not p._owned(pole,obj,record['token']):
        raise ValueError('Pole target is missing or replaced')
    _require_resettable_helper(pole,label+' pole',action)
    matrix=np.asarray(pole.matrix_world,dtype=float)
    if matrix.shape!=(4,4) or not np.isfinite(matrix).all():
        raise ValueError(label+' pole helper has an invalid world transform')
    pole_before=(pole.rotation_mode,pole.matrix_world.copy());setting_before=item.pole_distance
    pose_before=w.raw_pose(obj);modes_before=rs.mode_values(obj);status_before=state.status
    live_before=_LIVE.get(key);recovered=None
    try:
        session=_get(obj)
        if live_before is None:
            recovered=session
            # Rehydrating a saved preview temporarily restores its captured
            # pose.  Pole operations are defined against the pose currently
            # visible to the animator, so put that pose back before sampling.
            w.restore_pose(obj,pose_before);rs.restore_values(obj,modes_before);p._update(obj)
        points=session.world_points(session.points())
        middle=POLE_JOINTS[index];chain=solver.POLE_CHAINS[middle]
        root,centre,end=(points[i] for i in chain)
        axis=end-root;axis_length=float(np.linalg.norm(axis))
        threshold=max(float(session.scale)*1e-5,1e-8)
        if not np.isfinite(axis_length) or axis_length<threshold:
            raise ValueError(label+' limb has no stable root-to-end axis for pole alignment')
        axis/=axis_length
        bend=centre-root;bend-=axis*np.dot(bend,axis)
        bend_length=float(np.linalg.norm(bend))
        if not np.isfinite(bend_length) or bend_length<threshold:
            raise ValueError(label+' limb is too straight to infer a stable bend direction')
        public_action='Align Bend' if direction>0 else 'Flip Side'
        motion=_matched_motion_transform(obj,record,public_action)
        inverse=motion.inverted()
        current=np.asarray(inverse@pole.matrix_world.translation,dtype=float)
        distance=float(np.linalg.norm(current-centre))
        if not np.isfinite(distance):
            raise ValueError(label+' pole helper has an invalid distance')
        distance=min(max(distance,float(session.scale)*.4),float(session.scale)*4.)
        expected_world=centre+bend/bend_length*distance*direction
        expected_display=motion@Vector(expected_world)
        pole.matrix_world.translation=expected_display
        bpy.context.view_layer.update()
        if (not np.allclose(np.asarray(pole.matrix_world.translation,float),
                            np.asarray(expected_display,float),atol=1e-7)):
            raise ValueError(label+' pole helper could not be aligned')
        aligned_bend,aligned_wanted=solver._pole_vectors(points,chain,expected_world)
        intended_bend=aligned_bend*direction
        error=float(np.arctan2(np.linalg.norm(np.cross(intended_bend,aligned_wanted)),
                               np.dot(intended_bend,aligned_wanted)))
        item.pole_distance=distance/float(session.scale)
    except BaseException:
        try:
            item.pole_distance=setting_before
            w.restore_pose(obj,pose_before);rs.restore_values(obj,modes_before);p._update(obj)
            _restore_helper(pole,pole_before)
            bpy.context.view_layer.update();state.status=status_before
        finally:_cleanup_recovered_session(key,recovered)
        raise
    relation='aligned to' if direction>0 else 'flipped opposite'
    state.status=f'{label} direction {relation} the current evaluated bend; solve again if it changed'
    _finish_recovered_helper(obj,key,recovered,pose_before,modes_before)
    return dict(label=label,middle_joint=middle,direction_error_radians=error,operation=action,
                distance=distance,enabled=bool(item.use_pole),
                controls_version=record.get('controls_version',0))


def align_pole_to_current_bend(obj,label):
    """Place one owned pole helper on the evaluated limb's current bend plane."""
    return _place_pole_from_current_bend(obj,label,1.,'Align')


def flip_pole_to_opposite_bend(obj,label):
    """Place one owned pole helper opposite the evaluated limb's current bend plane."""
    return _place_pole_from_current_bend(obj,label,-1.,'Flip')


def pole_bend_status(obj,label):
    """Read the current pole direction without changing the preview or source pose."""
    record=_read(obj);rows={name:index for index,name in _target_rows(record)}
    if label not in rows:raise ValueError('Unknown whole-body target: '+label)
    index=rows[label]
    if index not in POLE_JOINTS:raise ValueError(label+' does not support pole status')
    item=obj.b4ml.body_targets.get(label)
    if item is None or not p._owned(item.target,obj,record['token']):
        raise ValueError('Whole-body target is missing or replaced')
    if not p._owned(item.pole,obj,record['token']):
        raise ValueError('Pole target is missing or replaced')
    matrix=np.asarray(item.pole.matrix_world,dtype=float)
    if matrix.shape!=(4,4) or not np.isfinite(matrix).all():
        raise ValueError(label+' pole helper has an invalid world transform')
    key=obj.as_pointer();live_before=_LIVE.get(key);recovered=None
    pose_before=w.raw_pose(obj) if live_before is None else None
    modes_before=rs.mode_values(obj) if live_before is None else None
    try:
        session=_get(obj)
        if live_before is None:
            recovered=session
            w.restore_pose(obj,pose_before);rs.restore_values(obj,modes_before);p._update(obj)
        points=session.world_points(session.points())
        middle=POLE_JOINTS[index];chain=solver.POLE_CHAINS[middle]
        motion=_matched_motion_transform(obj,record,'Read Pole Status')
        current=np.asarray(motion.inverted()@item.pole.matrix_world.translation,float)
        bend,wanted=solver._pole_vectors(points,chain,current)
        bend_length=float(np.linalg.norm(bend));wanted_length=float(np.linalg.norm(wanted))
        threshold=max(float(session.scale)*1e-5,1e-8)
        if (not np.isfinite(bend_length) or not np.isfinite(wanted_length)
                or min(bend_length,wanted_length)<threshold):
            raise ValueError(label+' limb is too straight to report a stable bend direction')
        error=float(np.arctan2(np.linalg.norm(np.cross(bend,wanted)),np.dot(bend,wanted)))
        opposite=float(np.arctan2(np.linalg.norm(np.cross(-bend,wanted)),np.dot(-bend,wanted)))
        tolerance=math.radians(5.)
        if error<=tolerance:relation='aligned'
        elif opposite<=tolerance:relation='opposite'
        else:relation='off-plane'
        return dict(label=label,relation=relation,error_radians=error,
                    opposite_error_radians=opposite,
                    distance_body_scales=wanted_length/float(session.scale),
                    enabled=bool(item.use_pole),controls_version=record.get('controls_version',0))
    finally:
        _cleanup_recovered_session(key,recovered)
        if recovered is not None:
            w.restore_pose(obj,pose_before);rs.restore_values(obj,modes_before);p._update(obj)


def set_pole_distance(obj,label,distance_body_scales):
    """Move one owned pole helper radially while preserving its current direction."""
    if isinstance(distance_body_scales,bool):
        raise ValueError('Pole distance must be a finite number from 0.1 to 4.0 body scales')
    try:distance_body_scales=float(distance_body_scales)
    except (TypeError,ValueError):
        raise ValueError('Pole distance must be a finite number from 0.1 to 4.0 body scales') from None
    if not math.isfinite(distance_body_scales) or not .1<=distance_body_scales<=4.:
        raise ValueError('Pole distance must be a finite number from 0.1 to 4.0 body scales')
    state=obj.b4ml;key=obj.as_pointer();action='Set Distance'
    if key in _JOBS or state.body_running:
        raise ValueError('Finish or cancel the running solve before using '+action)
    if state.body_live:
        raise ValueError('Stop Live Solve before using '+action)
    record=_read(obj);rows={name:index for index,name in _target_rows(record)}
    if label not in rows:raise ValueError('Unknown whole-body target: '+label)
    index=rows[label]
    if index not in POLE_JOINTS:raise ValueError(label+' does not support pole distance')
    item=state.body_targets.get(label)
    if item is None or not p._owned(item.target,obj,record['token']):
        raise ValueError('Whole-body target is missing or replaced')
    pole=item.pole
    if not p._owned(pole,obj,record['token']):raise ValueError('Pole target is missing or replaced')
    _require_resettable_helper(pole,label+' pole',action)
    matrix=np.asarray(pole.matrix_world,dtype=float)
    if matrix.shape!=(4,4) or not np.isfinite(matrix).all():
        raise ValueError(label+' pole helper has an invalid world transform')
    pole_before=(pole.rotation_mode,pole.matrix_world.copy());setting_before=item.pole_distance
    pose_before=w.raw_pose(obj);modes_before=rs.mode_values(obj);status_before=state.status
    live_before=_LIVE.get(key);recovered=None
    try:
        session=_get(obj)
        if live_before is None:
            recovered=session
            w.restore_pose(obj,pose_before);rs.restore_values(obj,modes_before);p._update(obj)
        points=session.world_points(session.points());middle=POLE_JOINTS[index]
        centre=points[middle]
        motion=_matched_motion_transform(obj,record,action)
        inverse=motion.inverted();current=np.asarray(inverse@pole.matrix_world.translation,dtype=float)
        direction=current-centre;current_distance=float(np.linalg.norm(direction))
        threshold=max(float(session.scale)*1e-5,1e-8)
        if not np.isfinite(current_distance) or current_distance<threshold:
            raise ValueError(label+' pole helper is too close to the joint to preserve its direction')
        distance=float(session.scale)*distance_body_scales
        expected_world=centre+direction/current_distance*distance
        expected_display=motion@Vector(expected_world);pole.matrix_world.translation=expected_display
        bpy.context.view_layer.update()
        if not np.allclose(np.asarray(pole.matrix_world.translation,float),
                           np.asarray(expected_display,float),atol=1e-7):
            raise ValueError(label+' pole helper distance could not be applied')
        actual_world=np.asarray(inverse@pole.matrix_world.translation,dtype=float)
        actual_distance=float(np.linalg.norm(actual_world-centre))
        if not math.isfinite(actual_distance) or abs(actual_distance-distance)>max(threshold,1e-7):
            raise ValueError(label+' pole helper distance could not be verified')
        item.pole_distance=distance_body_scales
    except BaseException:
        try:
            item.pole_distance=setting_before
            w.restore_pose(obj,pose_before);rs.restore_values(obj,modes_before);p._update(obj)
            _restore_helper(pole,pole_before);bpy.context.view_layer.update();state.status=status_before
        finally:_cleanup_recovered_session(key,recovered)
        raise
    state.status=f'{label} pole distance set to {distance_body_scales:.2f} body scales; solve again if it changed'
    _finish_recovered_helper(obj,key,recovered,pose_before,modes_before)
    return dict(label=label,middle_joint=middle,distance_body_scales=distance_body_scales,
                distance=actual_distance,enabled=bool(item.use_pole),
                controls_version=record.get('controls_version',0))

def _mirror_reflection(record):
    """Return the displayed sagittal reflection from the verified saved body frame."""
    data=record.get('session')
    if not isinstance(data,dict):raise ValueError('Invalid saved body frame for target mirroring')
    basis=np.asarray(data.get('basis'),dtype=float)
    if (basis.shape!=(3,3) or not np.isfinite(basis).all()
            or not np.allclose(basis.T@basis,np.eye(3),atol=1e-5)
            or np.linalg.det(basis)<=0):
        raise ValueError('Invalid saved body frame for target mirroring')
    motion=_reset_affine(record.get('motion_transform'),'Invalid saved motion transform for target mirroring')
    linear=np.asarray(motion,float)[:3,:3];lengths=np.linalg.norm(linear,axis=0)
    if (min(lengths)<1e-8 or not np.allclose(lengths,lengths[0],rtol=1e-5,atol=1e-7)
            or not np.allclose((linear/lengths).T@(linear/lengths),np.eye(3),atol=1e-5)):
        raise ValueError('Target mirroring requires uniform-scale native motion axes without shear')
    frame=(linear/lengths)@basis
    if not np.allclose(frame.T@frame,np.eye(3),atol=2e-5) or np.linalg.det(frame)<=0:
        raise ValueError('Invalid displayed body frame for target mirroring')
    reflection=frame@np.diag((-1.,1.,1.))@frame.T
    return reflection


def _mirrored_target_matrix(current,source_start,destination_start,reflection):
    current=_reset_matrix(current,'Source helper has scale, shear, reflection or an invalid transform')
    source_rotation=np.asarray(source_start,float)[:3,:3]
    destination_rotation=np.asarray(destination_start,float)[:3,:3]
    current_rotation=np.asarray(current,float)[:3,:3]
    delta=current_rotation@source_rotation.T
    rotation=reflection@delta@reflection@destination_rotation
    location=(np.asarray(destination_start.translation,float)
              +reflection@(np.asarray(current.translation,float)-np.asarray(source_start.translation,float)))
    return _reset_matrix(Matrix.LocRotScale(Vector(location),Matrix(rotation.tolist()).to_quaternion(),
                                            Vector((1.,1.,1.))),
                         'Mirrored target transform is invalid')


def _mirrored_pole_matrix(current,source_start,destination_start,reflection):
    location=np.asarray(current.translation,float)
    if location.shape!=(3,) or not np.isfinite(location).all():
        raise ValueError('Source pole helper has an invalid position')
    destination=np.asarray(destination_start.translation,float)
    destination+=reflection@(location-np.asarray(source_start.translation,float))
    return Matrix.LocRotScale(Vector(destination),destination_start.to_quaternion(),Vector((1.,1.,1.)))


def mirror_targets(obj,direction):
    """Atomically mirror paired hand, foot and pole helper edits through the body frame."""
    state=obj.b4ml;key=obj.as_pointer()
    if direction not in {'LEFT_TO_RIGHT','RIGHT_TO_LEFT'}:
        raise ValueError('Unknown target mirror direction')
    if key in _JOBS or state.body_running:
        raise ValueError('Finish or cancel the running solve before mirroring targets')
    if state.body_live:
        raise ValueError('Stop Live Solve before mirroring targets')
    record=_read(obj);rows={name:index for index,name in _target_rows(record)}
    pairs=MIRROR_PAIRS if direction=='LEFT_TO_RIGHT' else tuple((right,left) for left,right in MIRROR_PAIRS)
    if any(source not in rows or destination not in rows for source,destination in pairs):
        raise ValueError('This saved preview does not contain the paired humanoid targets')
    reflection=_mirror_reflection(record);changes=[]
    for source_label,destination_label in pairs:
        source=state.body_targets.get(source_label);destination=state.body_targets.get(destination_label)
        if (source is None or destination is None
                or not p._owned(source.target,obj,record['token'])
                or not p._owned(destination.target,obj,record['token'])):
            raise ValueError('Whole-body mirror target is missing or replaced')
        _require_resettable_helper(source.target,source_label)
        _require_resettable_helper(destination.target,destination_label)
        source_start=_saved_target_matrix(record,rows[source_label],source_label)
        destination_start=_saved_target_matrix(record,rows[destination_label],destination_label)
        expected=_mirrored_target_matrix(source.target.matrix_world,source_start,destination_start,reflection)
        pole_expected=None
        if rows[source_label] in POLE_JOINTS:
            if (not p._owned(source.pole,obj,record['token'])
                    or not p._owned(destination.pole,obj,record['token'])):
                raise ValueError('Whole-body mirror pole is missing or replaced')
            _require_resettable_helper(source.pole,source_label+' pole')
            _require_resettable_helper(destination.pole,destination_label+' pole')
            pole_expected=_mirrored_pole_matrix(source.pole.matrix_world,
                _saved_pole_matrix(record,source_label),_saved_pole_matrix(record,destination_label),reflection)
        changes.append((destination_label,destination.target,destination.pole,expected,pole_expected))
    snapshots=[(target,(target.rotation_mode,target.matrix_world.copy()),
                pole,(pole.rotation_mode,pole.matrix_world.copy()) if pole is not None else None)
               for _,target,pole,_,_ in changes]
    pose_before=w.raw_pose(obj);modes_before=rs.mode_values(obj);status_before=state.status
    live_before=_LIVE.get(key);recovered=None
    try:
        session=_get(obj)
        if live_before is None:recovered=session
        for _,target,pole,expected,pole_expected in changes:
            target.rotation_mode='QUATERNION';target.matrix_world=expected
            if pole_expected is not None:
                pole.rotation_mode='XYZ';pole.matrix_world=pole_expected
        bpy.context.view_layer.update()
        for label,target,pole,expected,pole_expected in changes:
            if not np.allclose(np.asarray(target.matrix_world,float),np.asarray(expected,float),atol=1e-7):
                raise ValueError(label+' helper could not be mirrored')
            if pole_expected is not None and not np.allclose(np.asarray(pole.matrix_world,float),
                                                              np.asarray(pole_expected,float),atol=1e-7):
                raise ValueError(label+' pole helper could not be mirrored')
    except BaseException:
        try:
            w.restore_pose(obj,pose_before);rs.restore_values(obj,modes_before);p._update(obj)
            for target,target_before,pole,pole_before in snapshots:
                _restore_helper(target,target_before)
                if pole_before is not None:_restore_helper(pole,pole_before)
            bpy.context.view_layer.update();state.status=status_before
        finally:_cleanup_recovered_session(key,recovered)
        raise
    state.status=('Mirrored left targets to right' if direction=='LEFT_TO_RIGHT'
                  else 'Mirrored right targets to left')+'; solve again if active requests changed'
    _finish_recovered_helper(obj,key,recovered,pose_before,modes_before)
    return dict(direction=direction,targets=len(changes),poles=sum(pole is not None for _,_,pole,_,_ in changes),
                controls_version=record.get('controls_version',0))


def _pose_asset_frame(session,record,action):
    motion=_matched_motion_transform(session.obj,record,action)
    frame=np.asarray(motion.to_quaternion().to_matrix(),float)@np.asarray(session.basis,float)
    motion_scale=abs(float(np.linalg.det(np.asarray(motion.to_3x3(),float))))**(1./3.)
    if (frame.shape!=(3,3) or not np.isfinite(frame).all()
            or not np.allclose(frame.T@frame,np.eye(3),atol=1e-5)
            or np.linalg.det(frame)<=0 or not math.isfinite(motion_scale)
            or motion_scale<=1e-10):
        raise ValueError('Invalid semantic body frame for '+action)
    return frame,motion_scale


def _pose_asset_quaternion(matrix,message):
    matrix=np.asarray(matrix,float)
    if (matrix.shape!=(3,3) or not np.isfinite(matrix).all()
            or not np.allclose(matrix.T@matrix,np.eye(3),atol=1e-5)
            or np.linalg.det(matrix)<=0):
        raise ValueError(message)
    value=Matrix(matrix.tolist()).to_quaternion();value.normalize()
    if value.w<0:value.negate()
    return list(value)


def capture_pose_asset(obj,scene):
    """Save one verified whole-body target layout in rig-independent body coordinates."""
    state=obj.b4ml;key=obj.as_pointer()
    if key in _JOBS or state.body_running:
        raise ValueError('Finish or cancel the running solve before saving a pose asset')
    if state.body_live:
        raise ValueError('Stop Live Solve before saving a pose asset')
    record=_read(obj)
    if record.get('controls_version',0)<5:
        raise ValueError('Restart this older preview before saving a semantic pose asset')
    if record.get('signature') is None:
        raise ValueError('Solve the current targets before saving a pose asset')
    data=_validate_record(obj,record);prepared=[]
    for index,label in _target_rows(record):
        item=state.body_targets.get(label)
        if item is None or not p._owned(item.target,obj,record['token']):
            raise ValueError('Whole-body target is missing or replaced')
        _require_resettable_helper(item.target,label,'saving a pose asset')
        if item.use_orientation and not target_supports_orientation(label):
            raise ValueError(label+' does not support semantic pose rotation')
        start=_saved_target_matrix(record,index,label)
        current=_reset_matrix(item.target.matrix_world,label+' helper has an invalid transform')
        pole_data=None
        if index in POLE_JOINTS:
            if not p._owned(item.pole,obj,record['token']):raise ValueError('Pole target is missing or replaced')
            _require_resettable_helper(item.pole,label+' pole','saving a pose asset')
            pole_start=_saved_pole_matrix(record,label)
            pole_current=_reset_matrix(item.pole.matrix_world,label+' pole helper has an invalid transform')
            distance=float(item.pole_distance)
            if not math.isfinite(distance) or not .1<=distance<=4.:
                raise ValueError(label+' has an invalid pole distance')
            pole_data=(pole_start,pole_current,bool(item.use_pole),distance)
        prepared.append((index,label,item,start,current,pole_data))
    pose_before=w.raw_pose(obj);modes_before=rs.mode_values(obj);status_before=state.status
    asset_had=POSE_ASSET_KEY in scene;asset_before=scene.get(POSE_ASSET_KEY)
    live_before=_LIVE.get(key);recovered=None
    try:
        session=_get(obj)
        if live_before is None:recovered=session
        if _request(obj,session)[2]!=record['signature']:
            raise ValueError('Solve the current targets before saving a pose asset')
        frame,motion_scale=_pose_asset_frame(session,record,'saving a pose asset');rows=[]
        for index,label,item,start,current,pole_data in prepared:
            position=_asset_vector(np.asarray(current.translation-start.translation,float)@frame/(session.scale*motion_scale),
                label+' helper is too far from its preview start').tolist()
            relative=frame.T@np.asarray(current.to_3x3(),float)@np.asarray(start.to_3x3(),float).T@frame
            orientation=_pose_asset_quaternion(relative,label+' helper has an invalid orientation')
            row=dict(label=label,position_enabled=bool(item.enabled),position_delta=position,
                     orientation_enabled=bool(item.use_orientation),orientation_delta=orientation)
            if pole_data is not None:
                pole_start,pole_current,pole_enabled,distance=pole_data
                delta=_asset_vector(np.asarray(pole_current.translation-pole_start.translation,float)@frame/(session.scale*motion_scale),
                                    label+' pole is too far from its preview start',8.).tolist()
                row['pole']=dict(enabled=pole_enabled,delta=delta,distance=distance)
            rows.append(row)
        source_profile=str(session.binding['profile'])[:128]
        if not source_profile.strip():raise ValueError('Active rig adapter has no semantic profile')
        asset=dict(schema=1,representation='semantic_target_delta_body_v1',controls_version=record.get('controls_version',5),
                   source_profile=source_profile,targets=rows,learned=False,verified_solve=True)
        text=json.dumps(asset,allow_nan=False,separators=(',',':'))
        if len(text)>POSE_ASSET_MAX_CHARS:raise ValueError('Semantic pose asset exceeds the serialized size limit')
        scene[POSE_ASSET_KEY]=text
        if recovered is not None:
            w.restore_pose(obj,pose_before);rs.restore_values(obj,modes_before);p._update(obj)
            _cleanup_recovered_session(key,recovered);recovered=None
    except BaseException:
        try:
            w.restore_pose(obj,pose_before);rs.restore_values(obj,modes_before);p._update(obj)
            if asset_had:scene[POSE_ASSET_KEY]=asset_before
            elif POSE_ASSET_KEY in scene:del scene[POSE_ASSET_KEY]
            state.status=status_before
        finally:_cleanup_recovered_session(key,recovered)
        raise
    state.status='Saved verified semantic target pose for cross-rig reuse'
    return asset

def _read_pose_asset(scene):
    text=scene.get(POSE_ASSET_KEY)
    if not isinstance(text,str) or not text or len(text)>POSE_ASSET_MAX_CHARS:
        raise ValueError('Save a valid semantic target pose in this scene first')
    try:asset=json.loads(text)
    except (TypeError,ValueError,RecursionError) as exc:
        raise ValueError('Saved semantic target pose is invalid') from exc
    keys={'schema','representation','controls_version','source_profile','targets','learned','verified_solve'}
    if (not isinstance(asset,dict) or set(asset)!=keys or asset.get('schema')!=1
            or asset.get('representation')!='semantic_target_delta_body_v1'
            or asset.get('controls_version') not in {5,6} or asset.get('learned') is not False
            or asset.get('verified_solve') is not True
            or not isinstance(asset.get('source_profile'),str) or not asset['source_profile'].strip()
            or len(asset['source_profile'])>128 or not isinstance(asset.get('targets'),list)):
        raise ValueError('Saved semantic target pose is invalid')
    return asset


def _asset_vector(value,message,limit=4.):
    vector=np.asarray(value,float)
    if vector.shape!=(3,) or not np.isfinite(vector).all() or np.linalg.norm(vector)>limit:
        raise ValueError(message)
    return vector


def apply_pose_asset(obj,scene):
    """Apply the scene pose asset to current helpers without changing the rig pose."""
    state=obj.b4ml;key=obj.as_pointer()
    if key in _JOBS or state.body_running:
        raise ValueError('Finish or cancel the running solve before applying a pose asset')
    if state.body_live:
        raise ValueError('Stop Live Solve before applying a pose asset')
    asset=_read_pose_asset(scene);record=_read(obj)
    if record.get('controls_version',0)<5:
        raise ValueError('Restart this older preview before applying a semantic pose asset')
    _validate_record(obj,record)
    expected_rows=list(_target_rows(record));expected_labels=[label for _,label in expected_rows]
    rows=asset['targets']
    if len(rows)!=len(expected_rows) or any(not isinstance(row,dict) for row in rows):
        raise ValueError('Saved semantic target pose has an incompatible target set')
    labels=[row.get('label') for row in rows]
    if labels!=expected_labels or len(set(labels))!=len(labels):
        raise ValueError('Saved semantic target pose has an incompatible target set')
    prepared=[]
    for (index,label),row in zip(expected_rows,rows):
        required={'label','position_enabled','position_delta','orientation_enabled','orientation_delta'}
        expected=required|({'pole'} if index in POLE_JOINTS else set())
        if set(row)!=expected or not isinstance(row['position_enabled'],bool) or not isinstance(row['orientation_enabled'],bool):
            raise ValueError('Saved semantic target pose contains invalid '+label+' settings')
        if label=='Pelvis' and not row['position_enabled']:
            raise ValueError('Saved semantic target pose must keep Pelvis position enabled')
        if row['orientation_enabled'] and not target_supports_orientation(label):
            raise ValueError('Saved semantic target pose requests unsupported '+label+' rotation')
        delta=_asset_vector(row['position_delta'],'Saved semantic target pose contains invalid '+label+' position')
        relative=_reset_quaternion(row['orientation_delta'],
                                   'Saved semantic target pose contains invalid '+label+' orientation')
        item=state.body_targets.get(label)
        if item is None or not p._owned(item.target,obj,record['token']):
            raise ValueError('Whole-body target is missing or replaced')
        _require_resettable_helper(item.target,label,'applying a pose asset')
        _reset_matrix(item.target.matrix_world,label+' helper has an invalid transform')
        start=_saved_target_matrix(record,index,label);pole_data=None
        if index in POLE_JOINTS:
            pole=row['pole']
            if (not isinstance(pole,dict) or set(pole)!={'enabled','delta','distance'}
                    or not isinstance(pole.get('enabled'),bool) or isinstance(pole.get('distance'),bool)):
                raise ValueError('Saved semantic target pose contains invalid '+label+' pole settings')
            try:distance=float(pole['distance'])
            except (KeyError,TypeError,ValueError):
                raise ValueError('Saved semantic target pose contains invalid '+label+' pole distance') from None
            if not math.isfinite(distance) or not .1<=distance<=4.:
                raise ValueError('Saved semantic target pose contains invalid '+label+' pole distance')
            pole_delta=_asset_vector(pole.get('delta'),
                'Saved semantic target pose contains invalid '+label+' pole position',8.)
            if not p._owned(item.pole,obj,record['token']):raise ValueError('Pole target is missing or replaced')
            _require_resettable_helper(item.pole,label+' pole','applying a pose asset')
            _reset_matrix(item.pole.matrix_world,label+' pole helper has an invalid transform')
            pole_start=_saved_pole_matrix(record,label)
            pole_data=(pole_start,pole_delta,pole['enabled'],distance)
        prepared.append((item,start,delta,relative,pole_data,row['position_enabled'],row['orientation_enabled']))
    snapshots=[(item,item.enabled,item.use_orientation,item.use_pole,item.pole_distance,
                (item.target.rotation_mode,item.target.matrix_world.copy()),
                (item.pole.rotation_mode,item.pole.matrix_world.copy()) if item.pole else None)
               for item,*_ in prepared]
    pose_before=w.raw_pose(obj);modes_before=rs.mode_values(obj);status_before=state.status
    payload_before=state.body_payload;live_before=_LIVE.get(key);recovered=None
    try:
        session=_get(obj)
        if live_before is None:recovered=session
        frame,motion_scale=_pose_asset_frame(session,record,'applying a pose asset');changes=[]
        for item,start,delta,relative,pole_data,position_enabled,orientation_enabled in prepared:
            start_rotation=np.asarray(start.to_3x3(),float)
            location=np.asarray(start.translation,float)+frame@(delta*session.scale*motion_scale)
            rotation=frame@np.asarray(relative.to_matrix(),float)@frame.T@start_rotation
            target_matrix=_reset_matrix(Matrix.LocRotScale(Vector(location),
                Matrix(rotation.tolist()).to_quaternion(),Vector((1.,1.,1.))),
                'Saved semantic target pose produced an invalid '+item.name+' transform')
            pole_matrix=None;pole_settings=None
            if pole_data is not None:
                pole_start,pole_delta,pole_enabled,distance=pole_data
                pole_location=np.asarray(pole_start.translation,float)+frame@(pole_delta*session.scale*motion_scale)
                pole_matrix=Matrix.LocRotScale(Vector(pole_location),pole_start.to_quaternion(),Vector((1.,1.,1.)))
                pole_settings=(pole_enabled,distance)
            changes.append((item,target_matrix,position_enabled,orientation_enabled,pole_matrix,pole_settings))
        for item,target_matrix,position_enabled,orientation_enabled,pole_matrix,pole_settings in changes:
            item.target.rotation_mode='QUATERNION';item.target.matrix_world=target_matrix
            item.enabled=position_enabled;item.use_orientation=orientation_enabled
            if pole_settings is not None:
                item.pole.rotation_mode='XYZ';item.pole.matrix_world=pole_matrix
                item.use_pole,item.pole_distance=pole_settings
        bpy.context.view_layer.update()
        for item,target_matrix,_,_,pole_matrix,_ in changes:
            if not np.allclose(np.asarray(item.target.matrix_world,float),np.asarray(target_matrix,float),atol=1e-7):
                raise ValueError(item.name+' helper could not apply the semantic pose asset')
            if pole_matrix is not None and not np.allclose(np.asarray(item.pole.matrix_world,float),np.asarray(pole_matrix,float),atol=1e-7):
                raise ValueError(item.name+' pole helper could not apply the semantic pose asset')
        record['signature']=None
        state.body_payload=json.dumps(record,allow_nan=False)
        target_profile=session.binding['profile']
        if recovered is not None:
            w.restore_pose(obj,pose_before);rs.restore_values(obj,modes_before);p._update(obj)
            _cleanup_recovered_session(key,recovered);recovered=None
    except BaseException:
        try:
            w.restore_pose(obj,pose_before);rs.restore_values(obj,modes_before);p._update(obj)
            for item,enabled,orientation,pole_enabled,distance,target_before,pole_before in snapshots:
                item.enabled=enabled;item.use_orientation=orientation;item.use_pole=pole_enabled;item.pole_distance=distance
                _restore_helper(item.target,target_before)
                if pole_before is not None:_restore_helper(item.pole,pole_before)
            bpy.context.view_layer.update();state.body_payload=payload_before;state.status=status_before
        finally:_cleanup_recovered_session(key,recovered)
        raise
    state.status='Applied semantic target pose from '+asset['source_profile']+'; solve before keeping'
    return dict(schema=1,source_profile=asset['source_profile'],target_profile=target_profile,
                targets=len(prepared),cross_rig=asset['source_profile']!=target_profile)

def _limit_semantics(obj, session):
    """Return control -> canonical role using the verified active adapter."""
    profile, _, limbs = p.bindings(obj)
    allowed = set(session.binding['rotations'] + session.binding['effectors'])
    result = {control: role for role, control in profile.roles.items() if control in allowed}
    for row in limbs:
        kind, side = row['id'].split('-')
        roles = (('upperarm', 'forearm', 'hand') if kind == 'arm'
                 else ('thigh', 'shin', 'foot'))
        for control, role in zip(row['fk'], roles):
            if control in allowed:
                result[control] = f'{role}.fk-{side}'
    return result


def apply_limit_preset(obj, preset=solver.limits.PRESET_ID):
    """Apply one explicit preset to semantically mapped preview controls."""
    if obj.as_pointer() in _JOBS or obj.b4ml.body_running:
        raise ValueError('Finish or cancel the running solve before applying a joint-limit preset')
    key=obj.as_pointer();live_before=_LIVE.get(key);recovered=None
    pose_before=w.raw_pose(obj) if live_before is None else None
    modes_before=rs.mode_values(obj) if live_before is None else None
    try:
        session = _get(obj)
        if live_before is None:
            recovered=session
            w.restore_pose(obj,pose_before);rs.restore_values(obj,modes_before);p._update(obj)
        state = obj.b4ml
        semantics = _limit_semantics(obj, session)
        applied = []
        skipped = []
        for item in state.body_limits:
            values = solver.limits.preset_values(
                semantics.get(item.name), item.joint_available, preset=preset)
            if values is None:
                skipped.append(item.name)
                continue
            for field in ('enabled', 'space', 'swing', 'twist_min', 'twist_max', 'use_bend_plane'):
                setattr(item, field, values[field])
            item.preset_provenance = values['provenance']
            applied.append(dict(control=item.name, semantic_role=values['semantic_role'],
                                space=values['space'], provenance=values['provenance']))
        if not applied:
            raise ValueError('The active rig adapter exposes no controls for this joint-limit preset')
        state.status = (f'Applied {solver.limits.PRESET_LABEL} to {len(applied)} controls; '
                        f'{len(skipped)} unmapped controls unchanged')
        return dict(schema=1, preset=preset, label=solver.limits.PRESET_LABEL,
                    provenance=solver.limits.PRESET_PROVENANCE,
                    profile=session.binding['profile'], applied=applied, skipped=skipped,
                    learned=False, clinical_anatomy=False)
    finally:
        _cleanup_recovered_session(key,recovered)
        if recovered is not None:
            w.restore_pose(obj,pose_before);rs.restore_values(obj,modes_before);p._update(obj)


def _request(obj,s,*,_scope=None):
    # Newly created or script-moved helpers need evaluated world transforms even
    # before a viewport redraw; otherwise valid pins can be read at the origin.
    bpy.context.view_layer.update()
    record=_read(obj,_scope=_scope);state=obj.b4ml;motion=w.motion_layer.transform(obj);inverse=motion.inverted();inverse_rotation=np.asarray(inverse.to_3x3(),float);targets=s.world_points(s.baseline);mask=np.zeros(17,bool);intent=[];rotations={};poles={};rotation_intent=[];pole_intent=[]
    for index,label in _target_rows(record):
        item=state.body_targets.get(label)
        if item is None or not p._owned(item.target,obj,record['token']):raise ValueError('Whole-body target is missing or replaced')
        displayed=np.asarray(item.target.matrix_world.translation,float)
        origin=record.get('target_origins',{}).get(label)
        point=targets[index]+inverse_rotation@(displayed-np.asarray(origin,float)) if origin is not None else np.asarray(inverse@Vector(displayed),float)
        if not np.isfinite(point).all():raise ValueError('Invalid target position')
        mask[index]=item.enabled
        if item.enabled:intent.append([index,(displayed if origin is not None else point).tolist()])
        targets[index]+=(point-targets[index])*state.body_strength
        if item.use_orientation and index not in solver.SUPPORTED_ORIENTATION_JOINTS:
            raise ValueError(label+' does not support rotation targets')
        if item.use_pole and index not in POLE_JOINTS:
            raise ValueError(label+' does not support pole targets')
        if item.use_orientation or item.use_pole:
            if not isinstance(record.get('controls_version'),int) or record['controls_version']<1:raise ValueError('Finish this older preview and start a new one for rotation/pole controls')
        if (item.use_orientation and index in solver.DISTRIBUTED_ORIENTATION_JOINTS
                and record.get('controls_version',0)<target_orientation_version(label)):
            raise ValueError('Finish this older preview and start a new one for '+label.lower()+' rotation controls')
        if item.use_orientation:
            matrix=np.array(item.target.matrix_world.to_3x3());lengths=np.linalg.norm(matrix,axis=0)
            if not np.isfinite(matrix).all() or min(lengths)<1e-8 or np.linalg.det(matrix)<=0 or not np.allclose((matrix/lengths).T@(matrix/lengths),np.eye(3),atol=1e-5):raise ValueError('Rotation targets require non-reflected axes without shear')
            q=motion.to_quaternion().inverted()@item.target.matrix_world.to_quaternion()
            if q.w<0:q.negate()
            rotation_intent.append([index,list(q)])
            start=motion.to_quaternion().inverted()@_saved_target_matrix(record,index,label).to_quaternion()
            if start.w<0:start.negate()
            rotations[index]=list(start.slerp(q,state.body_strength))
        if item.use_pole:
            if index not in POLE_JOINTS or not p._owned(item.pole,obj,record['token']):raise ValueError('Pole target is missing or replaced')
            displayed_pole=np.asarray(item.pole.matrix_world.translation,float)
            initial=np.asarray(record['pole_origins'][label],float)
            origin=record.get('pole_display_origins',{}).get(label)
            pole=initial+inverse_rotation@(displayed_pole-np.asarray(origin,float)) if origin is not None else np.asarray(inverse@Vector(displayed_pole),float)
            if initial.shape!=(3,) or not np.isfinite(initial).all() or not np.isfinite(pole).all():raise ValueError('Invalid pole target')
            pole_intent.append([POLE_JOINTS[index],(displayed_pole if origin is not None else pole).tolist()])
            if state.body_strength>0:poles[POLE_JOINTS[index]]=initial+(pole-initial)*state.body_strength
    if not mask[0]:raise ValueError('Pelvis must remain pinned')
    # Compare authored inputs, not reconstructed hidden points whose float precision
    # can differ after JSON reload. Only active helper positions affect this request.
    signature=_plain(dict(helpers=intent,mask=mask.tolist(),influence=state.body_influence,strength=state.body_strength))
    if rotation_intent:signature['orientations']=rotation_intent
    if pole_intent:signature['poles']=pole_intent
    rotation_limits={}
    for item in state.body_limits:
        if item.enabled:
            if item.name in rotation_limits:raise ValueError('Duplicate joint limit control')
            rotation_limits[item.name]=dict(swing=item.swing,twist_min=item.twist_min,twist_max=item.twist_max)
            if item.space=='JOINT':rotation_limits[item.name]['space']='JOINT'
            if item.use_bend_plane:rotation_limits[item.name]['bend']=dict(axis=item.bend_axis,minimum=item.bend_min,maximum=item.bend_max,sideways=item.bend_sideways)
    rotation_limits=solver.limits.validate(rotation_limits,set(s.binding['rotations']+s.binding['effectors']))
    if rotation_limits:signature['joint_limits']=rotation_limits
    balance_request=balance.request(obj,bpy.context.scene)
    if balance_request is not None:signature['balance']=balance_request
    return targets,mask,signature,rotations,poles


def calibrate_bend_axis(obj):
    """Copy only the visible pose's forward swing direction into one limit."""
    if obj.as_pointer() in _JOBS or obj.b4ml.body_running:raise ValueError('Finish or cancel the running solve before calibrating')
    key=obj.as_pointer();live_before=_LIVE.get(key);recovered=None
    pose_before=w.raw_pose(obj) if live_before is None else None
    modes_before=rs.mode_values(obj) if live_before is None else None
    try:
        s=_get(obj)
        if live_before is None:
            recovered=s;w.restore_pose(obj,pose_before);rs.restore_values(obj,modes_before);p._update(obj)
        item=obj.b4ml.body_limits.get(obj.b4ml.body_limit_control)
        if item is None:raise ValueError('Choose a joint-limit control')
        if item.name not in s.binding['rotations']+s.binding['effectors']:raise ValueError('Unsupported limit control')
        if item.space=='JOINT':
            pair=solver.joint_frames.bind(obj,s.binding).get(item.name)
            if pair is None:raise ValueError('No verified skeletal joint frame for this control')
            q=solver.joint_frames.rotation(obj,pair,solver.joint_frames.rest_relative(obj,pair))
        else:q=solver._quat(obj.pose.bones[item.name])
        vector=solver.limits.swing_vector(q)
        if np.linalg.norm(vector)<math.radians(5):raise ValueError('Bend the chosen joint at least 5 degrees from its rest pose before calibrating')
        item.bend_axis=math.atan2(float(vector[1]),float(vector[0]))
        obj.b4ml.status='Forward bend axis captured; solve again to apply changed limits'
        return item.bend_axis
    finally:_cleanup_recovered_session(key,recovered)


def start(obj, *, _live=False, iterations=None):
    if obj.b4ml.body_live and not _live:raise ValueError('Stop Live Solve before starting a manual solve')
    if obj.as_pointer() in _JOBS:raise ValueError('A solve is already running')
    s=_get(obj);targets,mask,signature,rotations,poles=_request(obj,s)
    default_budget=100 if signature.get('balance') else 80 if rotations or poles or signature.get('joint_limits') else 50
    if iterations is None:budget=default_budget
    elif type(iterations) is not int or not 1<=iterations<=100:raise ValueError('Invalid solve iteration budget')
    else:budget=iterations
    options=dict(learned_influence=obj.b4ml.body_influence,orientations_world=rotations,pole_targets=poles,rotation_limits=signature.get('joint_limits'),balance=signature.get('balance'))
    def attempts():
        try:
            result=yield from s.solve_steps(targets,mask,iterations=budget,**options)
            result['solve_attempts']=1
        except solver.ProjectionError as error:
            if iterations is not None or budget!=50 or not error.retryable:raise
            # The failed generator has restored the preceding preview. Expose a
            # cancellation boundary before spending a second, bounded fit budget.
            yield dict(phase='retry',iteration=0,total_iterations=100)
            if _request(obj,s)[2]!=signature:raise ValueError('Targets changed during solving; solve again')
            result=yield from s.solve_steps(targets,mask,iterations=100,**options)
            result['solve_attempts']=2
            result['elapsed_ms']+=error.elapsed_ms
            result['evaluations']+=error.evaluations
        return result
    iterator=attempts()
    # Retain a valid immutable record for failure recovery even if a handler
    # damages the public payload after the solver has returned its result.
    _JOBS[obj.as_pointer()]=dict(obj=obj,iterator=iterator,signature=signature,rollback_payload=obj.b4ml.body_payload)
    obj.b4ml.body_running=True;obj.b4ml.body_progress='Preparing whole-body solve'


def step(obj,*,_scope=None):
    key=obj.as_pointer();job=_JOBS.get(key)
    if job is None:raise InterruptedError('Whole-body solve was stopped')
    try:
        progress=next(job['iterator'])
        obj.b4ml.body_progress=f"Solving pose: {progress['iteration']}/{progress['total_iterations']}"
        return False
    except StopIteration as done:
        try:
            s=_get(obj,_scope=_scope)
            if _request(obj,s,_scope=_scope)[2]!=job['signature']:raise ValueError('Targets changed during solving; solve again')
            record=_read(obj);record['preview']=_plain(w.raw_pose(obj,s.binding['controls']));record['signature']=job['signature']
            record['metrics']={k:v for k,v in done.value.items() if k!='points'}
            obj.b4ml.body_payload=json.dumps(record,allow_nan=False)
            obj.b4ml.status=f"Whole-body preview ready; pin error {done.value['pin_error']:.3g} body units"
            if done.value.get('balance'):
                m=done.value['balance'];kind='Dynamic' if m.get('dynamic') else 'Static'
                obj.b4ml.status=f"{kind} balance preview; COM error {m['com_error']:.3g}, margin {m['after_margin']:.4g}"
        except Exception:
            record=_decode(job['rollback_payload']);w.restore_pose(obj,record['preview']);p._update(obj);raise
        finally:
            _JOBS.pop(key,None);obj.b4ml.body_running=False;obj.b4ml.body_progress=''
        return True
    except BaseException:
        abort(obj);raise


def solve(obj, *, iterations=None):
    start(obj, iterations=iterations)
    while not step(obj):pass


def project_coupled_torso_target(obj, desired_spine_delta_world,
                                 max_control_radians=.12):
    """Project one desired Spine direction into the actual mapped torso chart.

    This is target preflight, not a solve or an implicit correction.  It probes
    the current reversible preview with bounded control deltas, restores the
    exact preview pose, and returns reachable displayed Pelvis/Spine/Chest
    targets plus the measured correction.  The caller must explicitly present
    those targets to :func:`solve`; all normal coupled-solver gates still apply.
    """
    if obj.as_pointer() in _JOBS or obj.b4ml.body_running:
        raise ValueError('Finish the running whole-body solve before projecting a torso target')
    desired=np.asarray(desired_spine_delta_world,dtype=float)
    if desired.shape!=(3,) or not np.isfinite(desired).all() or np.linalg.norm(desired)<1e-8:
        raise ValueError('Expected a finite nonzero Spine direction')
    if (isinstance(max_control_radians,bool) or
            not isinstance(max_control_radians,(int,float)) or
            not math.isfinite(max_control_radians) or
            not 0<max_control_radians<=.25):
        raise ValueError('Invalid torso projection bound')
    key=obj.as_pointer();pose_before=w.raw_pose(obj);modes_before=rs.mode_values(obj)
    live_before=_LIVE.get(key);recovered=None
    s=_get(obj)
    if live_before is None:recovered=s
    record=_read(obj);controls=solver.coupled_torso_controls(s.binding)
    slots={name:s.binding['rotations'].index(name) for name in controls}
    epsilon=1e-3
    zero=np.zeros(3+3*len(s.q0));baseline=s.world_points(s.points())[:3]
    jacobian=np.empty((3,3*len(controls)),dtype=float)
    try:
        for column,name in enumerate(controls):
            for axis in range(3):
                trial=zero.copy();trial[3+slots[name]*3+axis]=epsilon
                s._apply(trial)
                jacobian[:,column*3+axis]=(s.world_points(s.points())[1]-baseline[1])/epsilon
        s._apply(zero)
        update=np.linalg.lstsq(jacobian,desired,rcond=1e-6)[0]
        vectors=update.reshape(-1,3)
        largest=float(np.max(np.linalg.norm(vectors,axis=1),initial=0.))
        if largest>max_control_radians:update*=max_control_radians/largest
        best=None
        for fraction in (1.,.5,.25,.125):
            trial=zero.copy()
            for column,name in enumerate(controls):
                slot=slots[name]
                trial[3+slot*3:6+slot*3]=update[column*3:column*3+3]*fraction
            s._apply(trial)
            points=s.world_points(s.points())[:3]
            actual=points[1]-baseline[1]
            progress=float(np.dot(actual,desired)/max(np.dot(desired,desired),1e-15))
            alignment=float(np.dot(actual,desired)/max(np.linalg.norm(actual)*np.linalg.norm(desired),1e-15))
            score=alignment*max(0.,min(progress,1.))
            if np.linalg.norm(actual)>1e-7 and (best is None or score>best[0]):
                best=(score,fraction,points.copy(),actual.copy(),trial.copy(),alignment,progress)
        if best is None or best[5]<=0:
            raise solver.CoupledTorsoError('Desired Spine direction has no verified mapped torso response')
        points=best[2];actual=best[3]
        motion=w.motion_layer.transform(obj)
        displayed=[list(motion@Vector(point)) for point in points]
        return dict(
            schema=1,
            controls=controls,
            desired_spine_delta_world=desired.tolist(),
            actual_spine_delta_world=actual.tolist(),
            correction_world=(actual-desired).tolist(),
            alignment=best[5],
            progress=best[6],
            line_search_fraction=best[1],
            max_control_radians=float(max_control_radians),
            displayed_targets=displayed,
            chest_follow_world=(points[2]-baseline[2]).tolist(),
            parameter_norm=float(np.linalg.norm(best[4])),
            jacobian_norm=float(np.linalg.norm(jacobian)),
        )
    finally:
        w.restore_pose(obj,pose_before);rs.restore_values(obj,modes_before);p._update(obj)
        _cleanup_recovered_session(key,recovered)
        if _plain(w.raw_pose(obj))!=_plain(pose_before):
            raise ValueError('Torso target projection failed to restore the preview pose')


def project_coupled_torso_orientation(obj, axis_world, spine_radians,
                                       chest_radians,
                                       max_control_radians=.12):
    """Return exactly reachable paired Spine/Chest orientation targets.

    Desired semantic rotations are projected through a finite-difference chart
    of the mapped torso controls.  The current preview pose is restored before
    return; callers still submit the returned targets to the strict solver.
    """
    if obj.as_pointer() in _JOBS or obj.b4ml.body_running:
        raise ValueError('Finish the running whole-body solve before projecting torso orientation')
    axis=np.asarray(axis_world,dtype=float)
    angles=np.asarray((spine_radians,chest_radians),dtype=float)
    if (axis.shape!=(3,) or not np.isfinite(axis).all() or np.linalg.norm(axis)<1e-8
            or angles.shape!=(2,) or not np.isfinite(angles).all()
            or np.max(np.abs(angles))>.25):
        raise ValueError('Invalid coupled torso orientation request')
    axis/=np.linalg.norm(axis)
    if (isinstance(max_control_radians,bool) or
            not isinstance(max_control_radians,(int,float)) or
            not math.isfinite(max_control_radians) or
            not 0<max_control_radians<=.25):
        raise ValueError('Invalid torso orientation projection bound')
    key=obj.as_pointer();pose_before=w.raw_pose(obj);modes_before=rs.mode_values(obj)
    live_before=_LIVE.get(key);recovered=None
    s=_get(obj)
    if live_before is None:recovered=s
    controls=solver.coupled_torso_controls(s.binding)
    slots={name:s.binding['rotations'].index(name) for name in controls}
    epsilon=1e-3
    zero=np.zeros(3+3*len(s.q0));motion=w.motion_layer.transform(obj)
    display_rotation=motion.to_quaternion()@s.world.to_quaternion()
    names=(solver.orientation_bone(s.binding,1),solver.orientation_bone(s.binding,2))

    def orientations():
        return [display_rotation@s.obj.pose.bones[name].matrix.to_quaternion() for name in names]

    baseline=orientations();jacobian=np.empty((6,3*len(controls)),dtype=float)
    target=np.concatenate((axis*angles[0],axis*angles[1]))
    try:
        for column,name in enumerate(controls):
            for component in range(3):
                trial=zero.copy();trial[3+slots[name]*3+component]=epsilon
                s._apply(trial)
                moved=orientations()
                jacobian[:,column*3+component]=np.concatenate([
                    solver._rotation_delta_vector(base,current)
                    for base,current in zip(baseline,moved)
                ])/epsilon
        s._apply(zero)
        update=np.linalg.lstsq(jacobian,target,rcond=1e-6)[0]
        vectors=update.reshape(-1,3)
        largest=float(np.max(np.linalg.norm(vectors,axis=1),initial=0.))
        if largest>max_control_radians:update*=max_control_radians/largest
        best=None
        for fraction in (1.,.5,.25,.125):
            trial=zero.copy()
            for column,name in enumerate(controls):
                slot=slots[name]
                trial[3+slot*3:6+slot*3]=update[column*3:column*3+3]*fraction
            s._apply(trial)
            current=orientations()
            actual=np.concatenate([
                solver._rotation_delta_vector(base,value)
                for base,value in zip(baseline,current)
            ])
            residual=float(np.linalg.norm(target-actual))
            progress=float(np.dot(actual,target)/max(np.dot(target,target),1e-15))
            if progress>0 and (best is None or residual<best[0]):
                best=(residual,fraction,current,actual,trial.copy(),s.world_points(s.points())[:3].copy(),progress)
        if best is None:
            raise solver.CoupledTorsoError('Desired torso orientation has no verified mapped-control response')
        return dict(
            schema=1,
            controls=controls,
            desired_rotation_vectors=target.tolist(),
            actual_rotation_vectors=best[3].tolist(),
            correction_rotation_vectors=(best[3]-target).tolist(),
            residual_radians=best[0],
            progress=best[6],
            line_search_fraction=best[1],
            max_control_radians=float(max_control_radians),
            displayed_targets=[list(motion@Vector(point)) for point in best[5]],
            displayed_orientations=[list(value) for value in best[2]],
            parameter_norm=float(np.linalg.norm(best[4])),
            jacobian_norm=float(np.linalg.norm(jacobian)),
        )
    finally:
        w.restore_pose(obj,pose_before);rs.restore_values(obj,modes_before);p._update(obj)
        _cleanup_recovered_session(key,recovered)
        if _plain(w.raw_pose(obj))!=_plain(pose_before):
            raise ValueError('Torso orientation projection failed to restore the preview pose')


def abort(obj):
    job=_JOBS.pop(obj.as_pointer(),None)
    try:
        if job is not None:job['iterator'].close()
    finally:
        obj.b4ml.body_running=False;obj.b4ml.body_progress=''
        obj.b4ml.status='Solve cancelled; previous preview restored'


def finish(obj,scene,keep=False):
    from . import body_live
    body_live.stop(obj)
    if obj.as_pointer() in _JOBS:abort(obj)
    record=_read(obj);d=_validate_record(obj,record)
    if keep:
        if _plain(w.raw_pose(obj,record['preview'].keys()))!=record['preview']:
            raise ValueError('Pose controls changed after solving; solve again before keeping')
        s=_get(obj)
        if record['signature'] is None or _request(obj,s)[2]!=record['signature']:raise ValueError('Solve the current targets before keeping')
        w._capture_anchor(obj,scene,False,from_posing=True,rig_modes=s.modes or None)
    scene.frame_set(int(d['frame'][0]),subframe=d['frame'][1])
    w.restore_pose(obj,d['source']);rs.restore_values(obj,d['source_modes'])
    s=_LIVE.pop(obj.as_pointer(),None)
    if s:s.closed=True
    solver._SESSIONS.pop(obj.as_pointer(),None)
    if p._owned(bpy.context.active_object,obj,record['token']):
        visible=w.motion_layer.find(obj) or obj; bpy.context.view_layer.objects.active=visible;visible.select_set(True)
    for helper in list(bpy.data.objects):
        if p._owned(helper,obj,record['token']):bpy.data.objects.remove(helper,do_unlink=True)
    obj.b4ml.body_targets.clear();obj.b4ml.body_payload='';obj.b4ml.body_source=None
    obj.b4ml.body_running=False;obj.b4ml.body_progress=''
    _RECORDS.clear()
    obj.b4ml.status='Saved whole-body pose anchor and restored source' if keep else 'Cancelled whole-body preview and restored source'


@bpy.app.handlers.persistent
def reset_runtime(*args):
    _RECORDS.clear()
    from . import body_live
    body_live.stop_all()
    for job in list(_JOBS.values()):
        try:abort(job['obj'])
        except (ReferenceError,RuntimeError):pass
    _JOBS.clear();_LIVE.clear();solver._SESSIONS.clear()


@bpy.app.handlers.persistent
def before_save(*args):
    _RECORDS.clear()
    from . import body_live
    body_live.stop_all()
    for job in list(_JOBS.values()):abort(job['obj'])


def register():
    from . import body_live
    for name in ('load_post','undo_post','redo_post'):
        handlers=getattr(bpy.app.handlers,name)
        if body_live.after_restore not in handlers:handlers.append(body_live.after_restore)
    for name in ('load_pre','undo_pre','redo_pre'):
        handlers=getattr(bpy.app.handlers,name)
        if reset_runtime not in handlers:handlers.append(reset_runtime)
    if before_save not in bpy.app.handlers.save_pre:bpy.app.handlers.save_pre.append(before_save)


def unregister():
    from . import body_live
    before_save()
    for obj in list(bpy.data.objects):
        if hasattr(obj,'b4ml') and obj.b4ml.body_payload:
            scene=next(iter(obj.users_scene),bpy.context.scene)
            with bpy.context.temp_override(scene=scene,view_layer=scene.view_layers[0]):
                finish(obj,scene,False)
    reset_runtime()
    for name in ('load_pre','undo_pre','redo_pre'):
        handlers=getattr(bpy.app.handlers,name)
        if reset_runtime in handlers:handlers.remove(reset_runtime)
    if before_save in bpy.app.handlers.save_pre:bpy.app.handlers.save_pre.remove(before_save)
    for name in ('load_post','undo_post','redo_post'):
        handlers=getattr(bpy.app.handlers,name)
        if body_live.after_restore in handlers:handlers.remove(body_live.after_restore)
