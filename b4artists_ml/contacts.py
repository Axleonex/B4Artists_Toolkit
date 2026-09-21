"""Cancellable contact correction of isolated FK animation candidates.

Only animator rotations are changed. Source and input candidate actions remain
untouched until an independently copied result passes evaluated-rig validation.
"""
import json,math,time
import bpy
from mathutils import Vector,Quaternion,Euler
from . import workflow as w,posing as p,rig_state as rs,contact_math as cm,contact_detection
from .math_core import two_bone_positions
from . import curve_smoothing
_JOBS={}
_SUGGEST_JOBS={}


class SourceInvalidatedError(ValueError):
    """A cooperative source edit must abort instead of selecting a fallback."""


def _row(item):
    blend_in=item.blend_in if item.asymmetric_blend else item.blend
    blend_out=item.blend_out if item.asymmetric_blend else item.blend
    prop=item.prop_target if item.prop_bound else None
    return dict(limb=item.limb,start=item.start,end=item.end,blend=item.blend,
        blend_in=blend_in,blend_out=blend_out,
        strength=item.strength,point=list(item.point),rotation=list(item.rotation),
        offset=list(item.offset),lock_rotation=item.lock_rotation,
        prop_bound=bool(item.prop_bound),prop_object=item.prop_name if item.prop_bound else '',
        prop_pointer=prop.name_full if prop else '',
        prop_identity=prop.as_pointer() if prop else 0,
        prop_point=list(item.prop_point),prop_rotation=list(item.prop_rotation),
        use_support=bool(item.use_support))


def rows(obj):
    return [_row(i) for i in obj.b4ml.contacts
            if i.enabled and i.review_state=='ACCEPTED']


def edit_interval(obj,scene,operation):
    """Inspect or atomically trim one authored/proposed contact interval."""
    if operation not in {'GO_BLEND_IN','GO_START','GO_END','GO_BLEND_OUT','SET_START','SET_END'}:
        raise ValueError('Unknown contact interval operation')
    state=obj.b4ml
    if not 0<=state.contact_index<len(state.contacts):
        raise ValueError('Choose a contact')
    if (state.contact_running or state.contact_suggest_running or state.flight_running or
            state.secondary_running or state.cleanup_running or state.temporal_running or
            state.body_payload or state.posing_payload or state.quadruped_payload):
        raise ValueError('Finish the active solve or posing preview first')
    item=state.contacts[state.contact_index]
    if operation in {'GO_BLEND_IN','GO_START','GO_END','GO_BLEND_OUT'}:
        from . import contact_visualization
        frame=contact_visualization.review_frame(item,operation)
        if not math.isfinite(frame):raise ValueError('Contact boundary must be finite')
        _frame(scene,frame)
        return frame
    w.require_rig(obj)
    candidate=state.candidate_action
    if not candidate or not obj.animation_data or obj.animation_data.action!=candidate:
        raise ValueError('Generate and select an interpolation candidate first')
    if not item.enabled or item.review_state=='REJECTED':
        raise ValueError('Enable and accept or propose this contact before trimming it')
    anchors=w.read_anchors(obj);first,last=anchors[0][0],anchors[-1][0]
    frame=p._frame(scene)
    proposed=_row(item);key='start' if operation=='SET_START' else 'end';proposed[key]=frame
    if proposed['start']>proposed['end']:
        raise ValueError('The contact start must not be after its end')
    request=[]
    for index,other in enumerate(state.contacts):
        if not other.enabled or other.review_state=='REJECTED':continue
        request.append(proposed if index==state.contact_index else _row(other))
    cm.validate(request,first,last)
    setattr(item,key,frame)
    state.status=f'Contact {"start" if key=="start" else "end"} set to frame {frame:g}'
    return frame


def _busy(state):
    return (state.contact_running or state.contact_suggest_running or state.flight_running or
            state.secondary_running or state.cleanup_running or state.temporal_running or
            state.body_payload or state.posing_payload or state.quadruped_payload)


def _evaluation_view_layer(scene,view_layer=None):
    if view_layer is not None:
        actual=scene.view_layers.get(view_layer.name)
        if actual is None or actual.as_pointer()!=view_layer.as_pointer():
            raise ValueError('The prop evaluation view layer changed')
        return view_layer
    if bpy.context.scene is scene and bpy.context.view_layer is not None:return bpy.context.view_layer
    return scene.view_layers[0]


def _platform_geometry(target):
    """Return validated local planar geometry for one rigid moving surface."""
    if target.type!='MESH' or len(target.data.vertices)<3 or not target.data.polygons:
        raise ValueError('Choose a planar mesh object with at least one face as the moving platform')
    if target.modifiers:
        raise ValueError('Moving Platform v1 does not support object modifiers')
    if target.data.shape_keys:
        raise ValueError('Moving Platform v1 does not support shape keys')
    data_animation=getattr(target.data,'animation_data',None)
    if data_animation and (data_animation.action or data_animation.drivers or len(data_animation.nla_tracks)):
        raise ValueError('Moving Platform v1 requires unanimated mesh data')
    points=[vertex.co.copy() for vertex in target.data.vertices]
    if not all(math.isfinite(value) for point in points for value in point):
        raise ValueError('Moving platform coordinates must be finite')
    origin=normal=None
    for polygon in target.data.polygons:
        ids=list(polygon.vertices)
        for index in range(1,len(ids)-1):
            a,b,c=(points[ids[value]] for value in (0,index,index+1));cross=(b-a).cross(c-a)
            if normal is None and cross.length>1e-10:origin=a;normal=cross.normalized()
    if normal is None:raise ValueError('Moving platform has no nondegenerate face')
    span=max((point-origin).length for point in points);tolerance=max(1e-6,span*1e-5)
    if any(abs((point-origin).dot(normal))>tolerance for point in points):
        raise ValueError('Moving platform mesh must be planar')
    target.data.calc_loop_triangles()
    triangles=[tuple(points[index] for index in triangle.vertices)
        for triangle in target.data.loop_triangles]
    if not triangles:raise ValueError('Moving platform has no triangulated surface')
    signature=(target.data.as_pointer(),tuple(tuple(point) for point in points),
        tuple(tuple(polygon.vertices) for polygon in target.data.polygons),
        tuple(tuple(triangle.vertices) for triangle in target.data.loop_triangles))
    return origin,normal,triangles,tolerance,signature


def _prop_object(obj,row,scene,view_layer=None,_validate_point=True):
    """Validate the bounded rigid prop/platform adapter and return its object."""
    if not row.get('prop_bound'):return None
    limb=row.get('limb');is_prop=limb in {'arm-L','arm-R'};is_platform=limb in {'leg-L','leg-R'}
    if not (is_prop or is_platform):
        raise ValueError('Moving targets support humanoid hands and feet only')
    if row.get('use_support'):
        raise ValueError('A moving-target contact cannot also be a support patch')
    name=row.get('prop_object','')
    if not name or row.get('prop_pointer')!=name:
        label='prop' if is_prop else 'platform'
        raise ValueError(f'The committed {label} is missing or was renamed; bind the contact again')
    target=bpy.data.objects.get(name)
    if target is None:raise ValueError('The bound contact target is missing')
    if target.as_pointer()!=row.get('prop_identity'):
        label='prop' if is_prop else 'platform'
        raise ValueError(f'The committed {label} identity changed; bind the contact again')
    if target==obj:raise ValueError('The character rig cannot be its own prop')
    if scene.objects.get(target.name) is not target:
        raise ValueError('The moving contact target must be linked to the character scene')
    if target.parent or target.constraints:
        raise ValueError('Moving contact targets must be unparented objects without constraints')
    if getattr(target,'rigid_body',None) is not None or getattr(target,'rigid_body_constraint',None) is not None:
        raise ValueError('Moving contact targets do not support rigid-body-owned transforms')
    view_layer=_evaluation_view_layer(scene,view_layer)
    if target.hide_viewport or target.hide_get(view_layer=view_layer) or not target.visible_get(view_layer=view_layer):
        raise ValueError('The bound prop must be visible in the character scene view layer')
    animation=target.animation_data
    if animation and (animation.drivers or len(animation.nla_tracks)):
        raise ValueError('Moving contact targets support direct object animation without drivers or NLA')
    action=animation.action if animation else None
    if action:
        curves=w.action_curves(action,getattr(animation,'action_slot',None))
        if any(curve.data_path in {'scale','delta_scale'} for curve in curves):
            raise ValueError('Prop Hold v1 does not support animated prop scale' if is_prop else
                'Moving platforms do not support animated scale')
        if any(curve.modifiers for curve in curves):
            raise ValueError('Moving contact targets do not support animation curve modifiers')
    point=Vector(row.get('prop_point',()))
    rotation=Quaternion(row.get('prop_rotation',()))
    matrix=target.matrix_world
    if (len(point)!=3 or len(rotation)!=4 or
            not all(math.isfinite(value) for value in (*point,*rotation)) or
            sum(value*value for value in rotation)<1e-16 or
            not all(math.isfinite(value) for line in matrix for value in line) or
            matrix.to_3x3().determinant()<1e-10):
        raise ValueError('The bound prop transform must be finite, invertible, and orientation preserving')
    axes=[matrix.to_3x3().col[index].normalized() for index in range(3)]
    if max(abs(axes[a].dot(axes[b])) for a,b in ((0,1),(0,2),(1,2)))>1e-5:
        raise ValueError('Moving contact targets do not support sheared transforms')
    if is_platform and _validate_point:
        origin,normal,triangles,tolerance,_=_platform_geometry(target)
        projected=point-normal*(point-origin).dot(normal)
        if abs((point-origin).dot(normal))>tolerance or not _inside_surface(projected,triangles):
            raise ValueError('The bound foot point must remain on the moving platform mesh')
    return target


def _prop_signature(obj,request,scene,view_layer=None):
    def scalar_rna(value):
        result=[]
        for definition in value.bl_rna.properties:
            if definition.identifier=='rna_type' or definition.type in {'POINTER','COLLECTION'}:continue
            current=getattr(value,definition.identifier)
            if getattr(definition,'is_array',False):current=tuple(current)
            elif isinstance(current,set):current=tuple(sorted(current))
            result.append((definition.identifier,current))
        return tuple(result)
    result={}
    for row in request:
        target=_prop_object(obj,row,scene,view_layer)
        if target is None:continue
        animation=target.animation_data;action=animation.action if animation else None
        slot=getattr(animation,'action_slot',None) if animation else None
        curves=w.action_curves(action,slot) if action else []
        curve_signature=[(curve.data_path,curve.array_index,curve.lock,curve.mute,curve.extrapolation,
            [(tuple(key.co),tuple(key.handle_left),tuple(key.handle_right),key.handle_left_type,
              key.handle_right_type,key.interpolation,key.easing,key.amplitude,key.back,key.period)
             for key in curve.keyframe_points],
            [tuple(point.co) for point in curve.sampled_points]) for curve in curves]
        action_structure=None
        if action and hasattr(action,'layers'):
            layer=action.layers[0] if action.layers else None
            strip=layer.strips[0] if layer and layer.strips else None
            bag=strip.channelbag(slot) if strip and slot else None
            action_structure=(
                layer.as_pointer() if layer else None,scalar_rna(layer) if layer else None,
                strip.as_pointer() if strip else None,scalar_rna(strip) if strip else None,
                bag.as_pointer() if bag else None,scalar_rna(bag) if bag else None)
        geometry=_platform_geometry(target)[4] if row.get('limb') in {'leg-L','leg-R'} else None
        result[(row['prop_object'],row['limb'],row['start'],row['end'],tuple(row['prop_point']))]=(
            target.as_pointer(),target.name_full,target.type,target.rotation_mode,
            tuple(value for line in target.matrix_world for value in line),
            action.as_pointer() if action else None,
            (getattr(animation,'action_blend_type',None),getattr(animation,'action_extrapolation',None),
             getattr(animation,'action_influence',None),getattr(animation,'use_nla',None),
             slot.as_pointer() if slot and hasattr(slot,'as_pointer') else None,
             getattr(slot,'identifier',None),getattr(animation,'action_slot_handle',None)) if animation else None,
            action_structure,curve_signature,geometry)
    return result


def _serialized_contacts(request):
    """Remove volatile runtime identities from durable Action metadata."""
    return [{key:value for key,value in row.items()
             if key not in {'prop_pointer','prop_identity'}} for row in request]


def _resolved_contact(obj,row,scene,view_layer=None):
    """Resolve one immutable request into the evaluated world target."""
    if not row.get('prop_bound'):return row
    target=_prop_object(obj,row,scene,view_layer);matrix=target.matrix_world
    resolved=dict(row)
    resolved['point']=list(matrix@Vector(row['prop_point']))
    resolved['rotation']=list((matrix.to_quaternion()@Quaternion(row['prop_rotation'])).normalized())
    return resolved


def edit_prop_binding(obj,scene,operation,view_layer=None):
    """Atomically bind or clear one explicit humanoid moving-target relation."""
    if operation not in {'BIND_PROP','CLEAR_PROP','BIND_SURFACE','CLEAR_SURFACE'}:
        raise ValueError('Unknown moving-target binding operation')
    state=obj.b4ml
    if not 0<=state.contact_index<len(state.contacts):raise ValueError('Choose a contact')
    if _busy(state):raise ValueError('Finish the active solve or posing preview first')
    item=state.contacts[state.contact_index]
    surface_operation=operation in {'BIND_SURFACE','CLEAR_SURFACE'}
    allowed={'leg-L','leg-R'} if surface_operation else {'arm-L','arm-R'}
    if item.limb not in allowed:
        raise ValueError('Choose a humanoid foot contact' if surface_operation else 'Choose a humanoid hand contact')
    if operation in {'CLEAR_PROP','CLEAR_SURFACE'}:
        if not item.prop_bound:raise ValueError('The selected contact is not bound to a moving target')
        resolved=_resolved_contact(obj,_row(item),scene,view_layer)
        item.point=resolved['point'];item.rotation=resolved['rotation']
        item.prop_bound=False;item.prop_object=None;item.prop_target=None;item.prop_name=''
        state.status=('Foot contact' if surface_operation else 'Hand contact')+' fixed at its current world-space target'
        return None
    w.require_rig(obj)
    candidate=state.candidate_action
    if not candidate or not obj.animation_data or obj.animation_data.action!=candidate:
        raise ValueError('Generate and select an interpolation candidate first')
    if not item.enabled or item.review_state=='REJECTED':
        raise ValueError('Enable and accept or propose this hand contact before binding it')
    if item.use_support:raise ValueError('Disable support-patch use before binding a moving contact target')
    target=item.prop_object
    if target is None:raise ValueError('Choose a moving platform first' if surface_operation else 'Choose a prop object first')
    probe=dict(_row(item),prop_bound=True,prop_object=target.name_full,
        prop_pointer=target.name_full,prop_identity=target.as_pointer())
    _prop_object(obj,probe,scene,view_layer,_validate_point=not surface_operation)
    p._update(obj);p._check_space(obj)
    _,_,limbs=p.bindings(obj);row=next((value for value in limbs if value['id']==item.limb),None)
    if row is None:raise ValueError('The selected rig does not expose that humanoid hand')
    matrix=w.display_world(obj)@obj.pose.bones[row['joints'][2]].matrix
    point=matrix@Vector(item.offset);rotation=matrix.to_quaternion().normalized()
    inverse=target.matrix_world.inverted_safe()
    local_point=inverse@point
    local_rotation=(target.matrix_world.to_quaternion().inverted()@rotation).normalized()
    if not all(math.isfinite(value) for value in (*local_point,*local_rotation)):
        raise ValueError('The prop-relative hand target is not finite')
    if surface_operation:
        origin,normal,triangles,_,_=_platform_geometry(target)
        projected=local_point-normal*(local_point-origin).dot(normal)
        world_distance=((target.matrix_world@local_point)-(target.matrix_world@projected)).length
        if world_distance>max(state.support_tolerance,1e-6) or not _inside_surface(projected,triangles):
            raise ValueError('Place the captured foot on the selected moving platform before binding')
        local_point=projected
    item.point=point;item.rotation=rotation
    item.prop_point=local_point;item.prop_rotation=local_rotation;item.prop_target=target
    item.prop_name=target.name_full;item.prop_bound=True
    state.status=('Foot contact bound to '+target.name+' in moving-platform space' if surface_operation else
        'Hand contact bound to '+target.name+' in prop-local space')
    return target


def _contact_signature(obj):
    return [dict(name=i.name,enabled=i.enabled,review_state=i.review_state,limb=i.limb,start=i.start,end=i.end,
        blend=i.blend,asymmetric_blend=i.asymmetric_blend,blend_in=i.blend_in,blend_out=i.blend_out,
        strength=i.strength,point=list(i.point),rotation=list(i.rotation),offset=list(i.offset),
        lock_rotation=i.lock_rotation,use_support=i.use_support,support_width=i.support_width,
        support_length=i.support_length,support_heading=i.support_heading,confidence=i.confidence,
        provenance=i.provenance,reason=i.reason,prop_bound=i.prop_bound,
        prop_object=i.prop_object.name_full if i.prop_object else '',
        prop_target=i.prop_target.name_full if i.prop_target else '',prop_name=i.prop_name,prop_point=list(i.prop_point),
        prop_rotation=list(i.prop_rotation)) for i in obj.b4ml.contacts]


def capture(obj,scene):
    w.require_rig(obj)
    if obj.b4ml.flight_running or obj.b4ml.contact_running or obj.b4ml.secondary_running or obj.b4ml.cleanup_running or obj.b4ml.body_payload or obj.b4ml.posing_payload or obj.b4ml.quadruped_payload:raise ValueError('Finish the active solve or posing preview first')
    if len(obj.b4ml.contacts)>=32:raise ValueError('Limit a candidate to 32 contacts')
    p._update(obj);p._check_space(obj)
    _,_,limbs=p.bindings(obj);limb=obj.b4ml.contact_limb
    row=next(r for r in limbs if r['id']==limb);matrix=w.display_world(obj)@obj.pose.bones[row['joints'][2]].matrix
    if not all(math.isfinite(v) for row in matrix for v in row):raise ValueError('Contact transform must be finite')
    offset=Vector(obj.b4ml.contact_offset);point=matrix@offset
    item=obj.b4ml.contacts.add();item.name=f'{limb} contact {len(obj.b4ml.contacts)}';item.limb=limb
    item.start=p._frame(scene);item.end=item.start;item.point=point;item.rotation=matrix.to_quaternion();item.offset=offset
    item.review_state='ACCEPTED';item.confidence=1.;item.provenance='MANUAL';item.reason='Captured by the animator at the current frame'
    obj.b4ml.contact_index=len(obj.b4ml.contacts)-1
    obj.b4ml.status='Contact captured in world space; set its interval and blend'
    return item


def _plane_surface(state,scene):
    surface=state.contact_surface
    if surface is None:
        point=Vector(state.support_plane_point);normal=Vector(state.support_plane_normal)
        if not all(math.isfinite(v) for v in (*point,*normal)) or normal.length<1e-8:raise ValueError('The explicit support plane must be finite with a nonzero normal')
        normal.normalize();return point,normal,None,'AUTHORED_PLANE',None
    if surface.type!='MESH' or len(surface.data.vertices)<3 or not surface.data.polygons:raise ValueError('Choose a planar mesh object with at least one face as the contact surface')
    data_animation=getattr(surface.data,'animation_data',None)
    if (surface.constraints or surface.modifiers or surface.parent or surface.data.shape_keys
            or getattr(surface,'rigid_body',None) is not None
            or getattr(surface,'rigid_body_constraint',None) is not None
            or (data_animation and (data_animation.action or data_animation.drivers or data_animation.nla_tracks))
            or (surface.animation_data and (surface.animation_data.action or surface.animation_data.drivers or surface.animation_data.nla_tracks))):
        raise ValueError('The first contact-surface adapter supports only an unparented, static planar mesh without constraints, modifiers, or rigid-body ownership')
    matrix=surface.matrix_world.copy();points=[matrix@v.co for v in surface.data.vertices]
    if not all(math.isfinite(v) for point in points for v in point):raise ValueError('Contact surface coordinates must be finite')
    origin=None;normal=None
    for poly in surface.data.polygons:
        ids=list(poly.vertices)
        for i in range(1,len(ids)-1):
            a,b,c=(points[ids[j]] for j in (0,i,i+1));n=(b-a).cross(c-a)
            if n.length>1e-10:origin=a;normal=n.normalized();break
        if normal is not None:break
    if normal is None:raise ValueError('Contact surface has no nondegenerate face')
    span=max((point-origin).length for point in points);tolerance=max(1e-6,span*1e-5)
    if any(abs((point-origin).dot(normal))>tolerance for point in points):raise ValueError('Contact surface must be planar')
    gravity=Vector(scene.gravity) if scene.use_gravity else Vector((0,0,-1))
    if gravity.length and normal.dot(gravity)>0:normal.negate()
    # Blender's loop triangulation respects concave polygon boundaries; a fan
    # from vertex zero can fill a concave notch that is outside the surface.
    surface.data.calc_loop_triangles()
    triangles=[tuple(points[index] for index in triangle.vertices)
               for triangle in surface.data.loop_triangles]
    topology=tuple(tuple(int(index) for index in polygon.vertices)
                   for polygon in surface.data.polygons)
    triangulation=tuple(tuple(int(index) for index in triangle.vertices)
                        for triangle in surface.data.loop_triangles)
    token=(surface.as_pointer(),tuple(v for row in matrix for v in row),
           tuple(tuple(p) for p in points),topology,triangulation)
    return origin,normal,triangles,'STATIC_PLANAR_MESH:'+surface.name,token


def _inside_surface(point,triangles,tolerance=1e-6):
    if triangles is None:return True
    for a,b,c in triangles:
        v0=b-a;v1=c-a;v2=point-a
        d00=v0.dot(v0);d01=v0.dot(v1);d11=v1.dot(v1);d20=v2.dot(v0);d21=v2.dot(v1);den=d00*d11-d01*d01
        if abs(den)<1e-14:continue
        u=(d11*d20-d01*d21)/den;v=(d00*d21-d01*d20)/den
        if u>=-tolerance and v>=-tolerance and u+v<=1+tolerance:return True
    return False


def _sample_frames(first,last):
    frames={float(first),float(last)};frames.update(map(float,range(math.ceil(first),math.floor(last)+1)))
    return sorted(frames)


def _suggestion_adapter(obj, offset):
    """Map evaluated contact points without converting the rig's native modes."""
    from .rigs import detect_rig
    if detect_rig(obj.data.bones.keys()).family == 'quadruped':
        from . import quadruped_contacts as qc
        _, body, mapping = qc._mapping(obj)
        for row in mapping.values():
            matrix = qc._joint_matrix(obj, row)
            row['offset'] = matrix.inverted() @ (w.display_world(obj) @ obj.pose.bones[row['joint']].tail) + offset
        return 'quadruped', body, mapping
    _, _, limbs = p.bindings(obj)
    mapping = {row['id']: dict(row, offset=offset.copy()) for row in limbs
               if row['id'] in ('leg-L', 'leg-R')}
    if len(mapping) != 2:
        raise ValueError('The selected rig does not expose both humanoid legs')
    return 'humanoid', None, mapping


def _suggestion_observation(obj, family, body, row):
    if family == 'quadruped':
        from . import quadruped_contacts as qc
        return (qc._point(obj, row, row['offset']), qc._control_rotation(obj, row),
                qc._reference(obj, body, row))
    matrix = w.display_world(obj) @ obj.pose.bones[row['joints'][2]].matrix
    lengths = [(obj.pose.bones[row['joints'][i+1]].head -
                obj.pose.bones[row['joints'][i]].head).length for i in (0, 1)]
    return matrix @ row['offset'], matrix.to_quaternion(), sum(lengths)*w.display_world(obj).to_scale().x


def suggestion_steps(obj,scene):
    state=obj.b4ml;started=time.perf_counter();w.require_rig(obj);w._reject_nla(obj)
    if state.contact_running or state.flight_running or state.secondary_running or state.cleanup_running or state.body_payload or state.posing_payload or state.quadruped_payload:raise ValueError('Finish the active solve or posing preview first')
    candidate=state.candidate_action
    if not candidate or not obj.animation_data or obj.animation_data.action!=candidate:raise ValueError('Generate and select an interpolation candidate first')
    if state.contact_output==candidate:raise ValueError('Restore the candidate before contact correction, then suggest contacts')
    anchors=w.read_anchors(obj);first,last=anchors[0][0],anchors[-1][0]
    frames=sorted(set(_sample_frames(first,last)) | {frame for frame,_ in anchors})
    if len(frames)>w.MAX_FRAMES+2:raise ValueError('Contact suggestion exceeds the frame limit')
    # Flush pending object transforms before freezing the surface token. Later
    # differences are then real in-flight edits rather than depsgraph latency.
    original_frame=p._frame(scene);p._update(obj)
    # Freeze inexpensive scene inputs before the first cooperative yield.
    # A later snapshot could silently accept edits made during preparation.
    world=tuple(v for row in obj.matrix_world for v in row)
    anchor_signature=[(item.frame,item.payload) for item in state.anchors]
    fps=scene.render.fps/scene.render.fps_base
    if not math.isfinite(fps) or fps<=0:raise ValueError('Scene frame rate must be positive')
    plane,normal,triangles,surface_name,surface_token=_plane_surface(state,scene)
    offset=Vector(state.contact_offset)
    if not all(math.isfinite(v) for v in offset):raise ValueError('Contact offset must be finite')
    settings_signature=(state.contact_surface.as_pointer() if state.contact_surface else None,tuple(state.support_plane_point),tuple(state.support_plane_normal),tuple(offset),state.contact_suggest_distance,state.contact_suggest_speed,state.contact_suggest_min_frames,state.contact_suggest_gap_frames)
    action_signature=_action_signature(obj);contact_signature=_contact_signature(obj)
    accepted_rows=rows(obj)
    original_pose=w.raw_pose(obj);original_modes=rs.mode_values(obj);rest=w._rest_signature(obj)
    yield dict(phase='Preparing contact surface',frame=original_frame,total=len(frames))
    yield dict(phase='Protecting rig state',frame=original_frame,total=len(frames))
    family,body,mapping=_suggestion_adapter(obj,offset)
    observations={limb:[] for limb in mapping}
    yield dict(phase='Preparing rig mapping',frame=original_frame,total=len(frames))
    def restore():
        _frame(scene,original_frame);w.restore_pose(obj,original_pose);rs.restore_values(obj,original_modes);p._update(obj)
    def restore_sample():
        # Sampling changes only the playhead. frame_set reevaluates the untouched
        # action at the original frame; the full pose/mode restore remains in the
        # finalizer for cancellation, errors and completion.
        _frame(scene,original_frame)
    def guard():
        if state.candidate_action!=candidate or not obj.animation_data or obj.animation_data.action!=candidate:raise ValueError('Candidate changed during contact suggestion')
        if _action_signature(obj)!=action_signature:raise ValueError('Input action changed during contact suggestion')
        if _contact_signature(obj)!=contact_signature:raise ValueError('Contacts changed during contact suggestion')
        if w._rest_signature(obj)!=rest:raise ValueError('Rig changed during contact suggestion')
        current_settings=(state.contact_surface.as_pointer() if state.contact_surface else None,tuple(state.support_plane_point),tuple(state.support_plane_normal),tuple(state.contact_offset),state.contact_suggest_distance,state.contact_suggest_speed,state.contact_suggest_min_frames,state.contact_suggest_gap_frames)
        if current_settings!=settings_signature:raise ValueError('Contact suggestion settings changed during suggestion')
        if surface_token is not None and _plane_surface(state,scene)[4]!=surface_token:raise ValueError('Contact surface changed during suggestion')
        if tuple(v for row in obj.matrix_world for v in row)!=world:raise ValueError('Rig transform changed during contact suggestion')
        if [(item.frame,item.payload) for item in state.anchors]!=anchor_signature:raise ValueError('Priority poses changed during contact suggestion')
        if scene.render.fps/scene.render.fps_base!=fps:raise ValueError('Frame rate changed during contact suggestion')
        if abs(p._frame(scene)-original_frame)>1e-5:raise ValueError('Playhead changed during contact suggestion')
        if family=='quadruped':
            from . import quadruped_pose as qp
            qp._require_ik(obj,list(mapping.values()))
    try:
        for frame in frames:
            # scene.frame_set() evaluates the action and dependencies. A second
            # view-layer update here repeated the full Rigify evaluation.
            guard();_frame(scene,frame);p._check_space(obj)
            if family=='quadruped':
                from . import quadruped_pose as qp
                qp._require_ik(obj,list(mapping.values()))
            for limb in observations:
                row=mapping[limb]
                point,rotation,reference=_suggestion_observation(obj,family,body,row)
                if reference<=1e-8 or not all(math.isfinite(v) for v in (*point,*rotation,reference)):raise ValueError('Evaluated foot contact data must be finite and nondegenerate')
                signed=(point-plane).dot(normal);projected=point-normal*signed
                observations[limb].append(dict(frame=frame,point=point.copy(),projected=projected,rotation=rotation.copy(),reference=reference,distance=abs(signed)/reference,inside=_inside_surface(projected,triangles)))
            restore_sample();yield dict(phase='Sampling contact motion',frame=frame,total=len(frames))
        guard()
        if w._rest_signature(obj)!=rest:raise ValueError('Rig changed during contact suggestion')
        suggestions=[];priority_frames={frame for frame,_ in anchors}
        for limb,samples in observations.items():
            for index,sample in enumerate(samples):
                speeds=[]
                for other in (index-1,index+1):
                    if not 0<=other<len(samples):continue
                    dt=abs(samples[other]['frame']-sample['frame'])/fps
                    delta=samples[other]['point']-sample['point'];tangent=delta-normal*delta.dot(normal)
                    speeds.append(tangent.length/max(dt*(sample['reference']+samples[other]['reference'])*.5,1e-12))
                sample['speed']=max(speeds,default=0.)
            spans=[dict(span,kind='low surface speed') for span in contact_detection.detect_intervals(samples,state.contact_suggest_distance,state.contact_suggest_speed,state.contact_suggest_min_frames,state.contact_suggest_gap_frames)]
            by_frame={s['frame']:s for s in samples};priority_holds=[]
            for (start,_),(end,_) in zip(anchors,anchors[1:]):
                if end-start<state.contact_suggest_min_frames-1:continue
                a=by_frame[start];b=by_frame[end];reference=(a['reference']+b['reference'])*.5
                if not (a['inside'] and b['inside'] and a['distance']<=state.contact_suggest_distance and b['distance']<=state.contact_suggest_distance):continue
                if (a['point']-b['point']).length/reference>2e-4:continue
                held=[s for s in samples if start<=s['frame']<=end]
                if len(held)<state.contact_suggest_min_frames:continue
                distance_ratio=max(a['distance'],b['distance'])/state.contact_suggest_distance
                priority_holds.append(dict(start=start,end=end,samples=held,sample_count=len(held),max_distance=max(s['distance'] for s in held),max_speed=max(s['speed'] for s in held),confidence=max(0.,min(.95,1.-.5*distance_ratio)),kind='matching grounded priority poses'))
            merged=[]
            for hold in priority_holds:
                if merged and abs(merged[-1]['end']-hold['start'])<1e-6:
                    previous=merged[-1];previous['end']=hold['end'];previous['samples'].extend(hold['samples'][1:]);previous['sample_count']=len(previous['samples']);previous['max_distance']=max(previous['max_distance'],hold['max_distance']);previous['max_speed']=max(previous['max_speed'],hold['max_speed']);previous['confidence']=min(previous['confidence'],hold['confidence'])
                else:merged.append(hold)
            priority_holds=merged
            # Matching authored endpoints are stronger intent evidence than
            # low-speed samples and deliberately capture foot sliding that the
            # correction is meant to remove.
            spans=[span for span in spans if not any(
                span['start']<=hold['end'] and hold['start']<=span['end']
                for hold in priority_holds)]+priority_holds
            for span in spans:
                blend=min(2.,max(0.,(span['end']-span['start'])*.25))
                proposed=dict(limb=limb,start=span['start'],end=span['end'],
                              blend=blend,blend_in=blend,blend_out=blend,strength=1.)
                conflict=False
                for accepted_row in accepted_rows:
                    if accepted_row['limb']!=limb:continue
                    accepted_in,accepted_out=cm.blends(accepted_row)
                    a=max(first,accepted_row['start']-accepted_in,
                          proposed['start']-proposed['blend_in'])
                    b=min(last,accepted_row['end']+accepted_out,
                          proposed['end']+proposed['blend_out'])
                    if a<b or (a==b and cm.weight(accepted_row,a)>0
                               and cm.weight(proposed,a)>0):
                        conflict=True;break
                if conflict:continue
                points=[s['projected'] for s in span['samples']];priorities=[s for s in span['samples'] if s['frame'] in priority_frames]
                center=priorities[0]['point'].copy() if priorities else sum(points,Vector((0,0,0)))/len(points)
                # A correction cannot move authored priority poses. Reject a
                # heuristic hold whose fixed point would require doing so.
                if any((s['point']-center).length/s['reference']>2e-4 for s in priorities):continue
                middle=priorities[0] if priorities else span['samples'][len(span['samples'])//2]
                lock_rotation=all(_angle(s['rotation'],middle['rotation'])<=.001 for s in priorities)
                suggestions.append(dict(limb=limb,start=span['start'],end=span['end'],blend=blend,strength=1.,point=center,rotation=middle['rotation'],offset=mapping[limb]['offset'].copy(),lock_rotation=lock_rotation,confidence=span['confidence'],reason=f"{span['sample_count']} samples near {surface_name}; evidence: {span['kind']}; max distance {span['max_distance']:.3g} and speed {span['max_speed']:.3g} reference units/s; priority poses {'agree' if priorities else 'not inside hold'}"))
        for limb in mapping:
            ordered=sorted((row for row in suggestions if row['limb']==limb),
                           key=lambda row:(row['start'],row['end']))
            for previous,current in zip(ordered,ordered[1:]):
                gap=max(0.,current['start']-previous['end'])
                total=previous['blend']+current['blend']
                if total>gap and total>0.:
                    scale=gap/total
                    previous['blend']*=scale;current['blend']*=scale
        if suggestions:
            cm.validate(accepted_rows+suggestions,first,last)
        accepted=sum(i.review_state=='ACCEPTED' for i in state.contacts)
        if accepted+len(suggestions)>32:raise ValueError('Suggested contacts would exceed the 32-contact limit; narrow the interval or thresholds')
        if _action_signature(obj)!=action_signature:raise ValueError('Input action changed during contact suggestion')
        guard()
        # Keep classification and Blender property publication in separate UI
        # callbacks.  Cancellation here is still source- and contact-neutral.
        yield dict(phase='Reviewing contact suggestions',frame=original_frame,total=len(suggestions))
        guard()
        for index in range(len(state.contacts)-1,-1,-1):
            if state.contacts[index].review_state!='ACCEPTED':state.contacts.remove(index)
        for row in sorted(suggestions,key=lambda r:(r['start'],r['limb'])):
            item=state.contacts.add();item.name=f"Suggested {row['limb']} {row['start']:g}-{row['end']:g}";item.limb=row['limb'];item.start=row['start'];item.end=row['end'];item.blend=row['blend'];item.strength=row['strength'];item.point=row['point'];item.rotation=row['rotation'];item.offset=row['offset'];item.lock_rotation=row['lock_rotation'];item.review_state='PROPOSED';item.confidence=row['confidence'];item.provenance=surface_name;item.reason=row['reason']
        state.contact_index=max(0,accepted if suggestions else min(state.contact_index,len(state.contacts)-1))
        report=dict(schema=1,backend='scene_contact_suggestions_v1',surface=surface_name,frames=len(frames),suggestions=len(suggestions),accepted_preserved=accepted,thresholds=dict(distance_leg_fraction=state.contact_suggest_distance,speed_leg_lengths_per_second=state.contact_suggest_speed,min_frames=state.contact_suggest_min_frames,gap_frames=state.contact_suggest_gap_frames),elapsed_ms=(time.perf_counter()-started)*1000,provisional=True)
        report.update(family=family,limbs=list(mapping),learned=False,gait_inference=False)
        if family=='quadruped':
            report['backend']='scene_paw_contact_suggestions_v1'
            report['thresholds']['distance_body_to_paw_fraction']=report['thresholds'].pop('distance_leg_fraction')
            report['thresholds']['speed_body_to_paw_lengths_per_second']=report['thresholds'].pop('speed_leg_lengths_per_second')
        state.contact_suggestion_report=json.dumps(report,allow_nan=False);state.status=f'{len(suggestions)} provisional foot contacts found; review each before correction'
        return report
    finally:restore()


def suggest_start(obj,scene):
    if obj.as_pointer() in _SUGGEST_JOBS:raise ValueError('Contact suggestion is already running')
    iterator=suggestion_steps(obj,scene);_SUGGEST_JOBS[obj.as_pointer()]=dict(obj=obj,iterator=iterator)
    obj.b4ml.contact_suggest_running=True;obj.b4ml.contact_suggest_progress='Preparing contact suggestion'


def suggest_step(obj):
    job=_SUGGEST_JOBS.get(obj.as_pointer())
    if job is None:raise InterruptedError('Contact suggestion stopped')
    try:
        info=next(job['iterator']);obj.b4ml.contact_suggest_progress=f"{info['phase']}: frame {info['frame']:g}";return False
    except StopIteration:
        _SUGGEST_JOBS.pop(obj.as_pointer(),None);obj.b4ml.contact_suggest_running=False;obj.b4ml.contact_suggest_progress='';return True
    except BaseException:suggest_abort(obj);raise


def suggest_abort(obj):
    job=_SUGGEST_JOBS.pop(obj.as_pointer(),None)
    try:
        if job:job['iterator'].close()
    finally:obj.b4ml.contact_suggest_running=False;obj.b4ml.contact_suggest_progress=''


def suggest(obj,scene):
    suggest_start(obj,scene)
    while not suggest_step(obj):pass
    return json.loads(obj.b4ml.contact_suggestion_report)


def restore_before_contacts(obj,scene):
    state=obj.b4ml
    if state.flight_running or state.contact_running or state.secondary_running or state.cleanup_running:raise ValueError('Finish or cancel the active correction first')
    if not state.contact_input or state.contact_output!=state.candidate_action or not obj.animation_data or obj.animation_data.action!=state.contact_output:raise ValueError('Select the corrected contact candidate first')
    w.assign_action(obj,state.contact_input,w._slot(obj.animation_data));state.candidate_action=state.contact_input
    state.contact_input=None;state.contact_output=None;state.contact_metrics=''
    _frame(scene,p._frame(scene));state.status='Interpolation candidate restored before contact correction'


def _frame(scene,frame):scene.frame_set(math.floor(frame),subframe=frame-math.floor(frame))


def _action_signature(obj,action=None):
    action=obj.animation_data.action if action is None else action
    def primitive(value):
        if isinstance(value,(str,bool,int,float)):return value
        try:return tuple(value)
        except TypeError:return None
    def modifier_signature(modifier):
        values=[]
        for prop in modifier.bl_rna.properties:
            if prop.identifier=='rna_type' or prop.is_readonly:continue
            value=primitive(getattr(modifier,prop.identifier,None))
            if value is not None:values.append((prop.identifier,value))
        return tuple(values)
    return [(f.data_path,f.array_index,f.lock,f.mute,f.extrapolation,
             tuple(modifier_signature(modifier) for modifier in f.modifiers),
             [(tuple(k.co),tuple(k.handle_left),tuple(k.handle_right),k.interpolation,
               k.handle_left_type,k.handle_right_type,k.easing,k.amplitude,k.back,k.period)
              for k in f.keyframe_points],
             [tuple(point.co) for point in f.sampled_points])
            for f in w.action_curves(action,getattr(obj.animation_data,'action_slot',None))]


def _point(obj,row,offset):return (w.display_world(obj)@obj.pose.bones[row['joints'][2]].matrix)@Vector(offset)


def _angle(a,b):return 2*math.acos(min(1.,abs(a.normalized().dot(b.normalized()))))


def _solve_limb(obj,row,request,amount,pole_hint=None):
    bones=[obj.pose.bones[n] for n in row['joints']]
    before=[b.head.copy() for b in bones];lengths=[(before[i+1]-before[i]).length for i in (0,1)]
    matrix=w.display_world(obj)@bones[2].matrix
    old_q=matrix.to_quaternion();desired=old_q.slerp(Quaternion(request['rotation']),amount) if request['lock_rotation'] else old_q
    target=_point(obj,row,request['offset']).lerp(Vector(request['point']),amount)
    # Retain exact authored control values when the contact is already met.
    # Re-solving an identical endpoint can perturb the bend plane and leak
    # through interpolation into the following unowned span.
    reference=max(sum(lengths)*w.display_world(obj).to_scale().x,1e-8)
    if (_point(obj,row,request['offset'])-target).length/reference<=1e-7 and _angle(old_q,desired)<=1e-6:
        return target,desired,pole_hint
    # Contact offset is expressed in the evaluated joint's local units.
    offset_world=desired.to_matrix()@Vector([a*b for a,b in zip(matrix.to_scale(),request['offset'])])
    head_target=w.display_world(obj).inverted()@(target-offset_world)
    axis=(head_target-before[0]).normalized();source_rotation=obj.pose.bones[row['fk'][0]].matrix.to_quaternion()
    normal=(before[1]-before[0]).cross(before[2]-before[1])
    if normal.length/max(lengths[0]*lengths[1],1e-8)>1e-4:
        normal.normalize();pole_hint=source_rotation.inverted()@normal
    else:
        if pole_hint is None:pole_hint=Vector((0,0,1))
        normal=source_rotation@pole_hint
    bend=axis.cross(normal)
    if bend.length<1e-8:
        bend=source_rotation@Vector((1,0,0));bend-=axis*bend.dot(axis)
    pole=before[0]+bend.normalized()*sum(lengths)
    joint,end=map(Vector,two_bone_positions(tuple(before[0]),tuple(head_target),tuple(pole),*lengths))
    if (end-head_target).length/max(sum(lengths),1e-8)>2e-4:raise ValueError('Contact is unreachable without moving the body: '+row['id'])
    p._aim(obj,row['fk'][0],bones[1].head-bones[0].head,joint-bones[0].head)
    p._aim(obj,row['fk'][1],bones[2].head-bones[1].head,end-bones[1].head)
    actual=bones[2].matrix.to_quaternion();desired_arm=w.display_world(obj).to_quaternion().inverted()@desired
    control=obj.pose.bones[row['fk'][2]]
    rotation=(desired_arm@actual.inverted()@control.matrix.to_quaternion()).to_matrix().to_4x4();rotation.translation=control.head
    p._write_rotation(obj,control.name,rotation)
    after=[b.head.copy() for b in bones]
    if max(abs((after[i+1]-after[i]).length/lengths[i]-1) for i in (0,1))>.002:raise ValueError('Contact fit changed limb length')
    return target,desired,pole_hint


def _flight_intervals(obj,anchors,request):
    """Read generated flight boundaries, never the user's next-flight settings.

    Native layers own their metadata; root-curve results own action metadata.
    Older native archives have sufficient interval/transition metrics to recover
    timing without mutating them or guessing from the current panel fields.
    """
    from . import flight_math as fm
    native=w.motion_layer.find(obj);raw=None
    try:
        if native is not None and native.get('b4ml_native_flight'):
            if 'b4ml_flight' in native:raw=json.loads(native['b4ml_flight'])['flights']
            else:
                metrics=json.loads(native['b4ml_flight_metrics'])
                raw=[dict(start=r['start'],end=r['end'],strength=r['strength'],takeoff_blend=0.,landing_blend=0.) for r in metrics['intervals']]
                for span in metrics.get('transitions',[]):
                    key='landing_blend' if span['landing'] else 'takeoff_blend'
                    matches=[r for r in raw if (r['end']==span['start'] if span['landing'] else r['start']==span['end'])]
                    if len(matches)!=1 or matches[0][key]!=0:raise ValueError('Ambiguous transition metadata')
                    matches[0][key]=span['end']-span['start']
        elif obj.b4ml.flight_output:
            raw=json.loads(obj.b4ml.flight_output['b4ml_flight'])['flights']
        else:return []
        if not isinstance(raw,list) or not all(isinstance(r,dict) for r in raw):raise ValueError('Invalid flight metadata')
        intervals=fm.validate(raw,[f for f,_ in anchors],request)
        fm.transition_spans(intervals,[f for f,_ in anchors],request)
        return intervals
    except (KeyError,TypeError,AttributeError,json.JSONDecodeError) as exc:
        raise ValueError('Generated flight metadata is missing or invalid; restore the flight before applying contacts') from exc


def _host_correction_steps(obj,scene,_extra_frames=(),_refinements=(),_started=None,_anchors=None,_flight=None,_expected_out=None,_view_layer=None):
    state=obj.b4ml;evaluation_view_layer=_evaluation_view_layer(scene,_view_layer)
    w.require_rig(obj);w._reject_nla(obj)
    if state.flight_running:raise ValueError('Finish flight correction first')
    if state.secondary_running or state.cleanup_running:raise ValueError('Finish secondary motion or animation cleanup first')
    if state.body_payload or state.posing_payload or state.quadruped_payload:raise ValueError('Finish assisted posing first')
    previous=state.candidate_action
    if not previous or not obj.animation_data or obj.animation_data.action!=previous:raise ValueError('Generate and select an interpolation candidate first')
    if state.contact_output==previous and not state.contact_input:raise ValueError('Retained contact input is missing; generate a new candidate')
    original=state.contact_input if state.contact_output==previous and state.contact_input else previous
    anchors=w.read_anchors(obj) if _anchors is None else _anchors;first,last=anchors[0][0],anchors[-1][0]
    shape_mode=original.get('b4ml_backend')==curve_smoothing.BACKEND
    flight_intervals=_flight_intervals(obj,anchors,rows(obj)) if _flight is None else _flight
    request=cm.validate(rows(obj),first,last);prop_signature=_prop_signature(obj,request,scene,evaluation_view_layer)
    if any((row['start']>first and row['blend_in']<=0.)
           or (row['end']<last and row['blend_out']<=0.) for row in request):
        raise ValueError('Contacts inside the candidate need positive entry and exit blends')
    frames=cm.sample_frames(request,[f for f,_ in anchors],first,last)
    if any(not math.isfinite(f) or not first<=f<=last for f in _extra_frames):raise ValueError('Invalid adaptive contact sample')
    frames=sorted(set(frames)|set(_extra_frames))
    original_frame=p._frame(scene);original_pose=w.raw_pose(obj);original_modes=rs.mode_values(obj);slot=w._slot(obj.animation_data)
    rest=w._rest_signature(obj);request_signature=rows(obj)
    anchor_signature=[(item.frame,item.payload) for item in state.anchors]
    w.assign_action(obj,original,slot)
    try:signature=_action_signature(obj)
    finally:w.assign_action(obj,previous,slot)
    # Validate between every pair of fitted keys.  A failed midpoint becomes a
    # fitted key on the next pass, which recursively checks its two half-sized
    # intervals. Shape-aware curves also check the quarter points because cubic
    # extrema need more than one interior observation.
    check_frames=sorted(set(frames)|{a+(b-a)*t for a,b in zip(frames,frames[1:]) for t in ((.25,.5,.75) if shape_mode else (.5,))});key_frames=set(frames)
    _,_,limbs=p.bindings(obj);mapping={r['id']:r for r in limbs};selected={r['limb'] for r in request}
    names={n for limb in selected for n in mapping[limb]['fk']}
    if not names.issubset(anchors[0][1]['pose']):raise ValueError('Capture all three controls of each contact limb in every anchor')
    if len(frames)*len(names)*4>w.MAX_KEYS:raise ValueError('Contact correction exceeds the key budget')
    intervals={name:[(max(first,r['start']-r['blend_in']),min(last,r['end']+r['blend_out'])) for r in request if name in mapping[r['limb']]['fk']] for name in names}
    samples={};expected={};priority={f for f,_ in anchors};priority_matrices={};candidate=None;candidate_signature=None;committed=False
    started=time.perf_counter() if _started is None else _started;max_before=0.;max_after=0.;drift_before=0.;drift_after=0.;orientation_error=0.;checks=0
    def restore_input():
        w.assign_action(obj,previous,slot);_frame(scene,original_frame);w.restore_pose(obj,original_pose);rs.restore_values(obj,original_modes);p._update(obj)
    def guard():
        if state.candidate_action!=previous or obj.animation_data.action not in (previous,candidate):raise ValueError('Candidate changed during contact correction')
        if (original.get('b4ml_backend')==curve_smoothing.BACKEND)!=shape_mode:raise ValueError('Candidate smoothing mode changed during correction')
        if rows(obj)!=request_signature or w._rest_signature(obj)!=rest:raise ValueError('Contacts or rig changed during correction')
        if [(item.frame,item.payload) for item in state.anchors]!=anchor_signature:raise ValueError('Priority poses changed during contact correction')
        if candidate_signature is not None and _action_signature(obj,candidate)!=candidate_signature:raise ValueError('Contact candidate changed after validation')
        if _prop_signature(obj,request_signature,scene,evaluation_view_layer)!=prop_signature:raise ValueError('Bound prop changed during contact correction')
        if _flight is None and _flight_intervals(obj,anchors,request_signature)!=flight_intervals:raise ValueError('Generated flight changed during contact correction')
        if abs(p._frame(scene)-original_frame)>1e-5:raise ValueError('Playhead changed during contact correction')
    try:
        compatible={};previous_quaternions={};pole_hints={}
        for frame in check_frames:
            guard();w.assign_action(obj,original,slot);_frame(scene,frame);p._update(obj);p._check_space(obj)
            _,_,current=p.bindings(obj);mapping={r['id']:r for r in current}
            if any(mapping[limb]['mode']!='FK' for limb in selected):raise ValueError('Contact correction requires a normalized FK candidate')
            p._check_controls(obj,names,'rotation')
            matrices=[w.display_world(obj)]+[obj.pose.bones[n].matrix for limb in selected for n in mapping[limb]['joints']]
            if not all(math.isfinite(v) for m in matrices for row in m for v in row):raise ValueError('Evaluated contact transforms must be finite')
            if frame in priority:priority_matrices[frame]={n:obj.pose.bones[n].matrix.copy() for n in anchors[0][1]['pose']}
            expected[frame]=[]
            for r in request:
                amount=cm.weight(r,frame)
                if amount==0:continue
                resolved=_resolved_contact(obj,r,scene,evaluation_view_layer)
                row=mapping[r['limb']];matrix=w.display_world(obj)@obj.pose.bones[row['joints'][2]].matrix
                target=(matrix@Vector(r['offset'])).lerp(Vector(resolved['point']),amount)
                desired=matrix.to_quaternion().slerp(Quaternion(resolved['rotation']),amount) if r['lock_rotation'] else matrix.to_quaternion()
                reference=max(sum((obj.pose.bones[row['joints'][i+1]].head-obj.pose.bones[row['joints'][i]].head).length for i in (0,1))*w.display_world(obj).to_scale().x,1e-8)
                error=(_point(obj,row,r['offset'])-target).length/reference;max_before=max(max_before,error)
                if r['start']<=frame<=r['end']:drift_before=max(drift_before,(_point(obj,row,r['offset'])-Vector(resolved['point'])).length/reference)
                if frame in priority:
                    if error>2e-4 or _angle(matrix.to_quaternion(),desired)>.001:raise ValueError(f'Contact conflicts with priority pose at frame {frame:g}: '+r['limb'])
                elif frame in key_frames:
                    key=(r['limb'],r['start'],r['end'])
                    try:target,desired,pole_hints[key]=_solve_limb(obj,row,resolved,amount,pole_hints.get(key))
                    except ValueError as exc:raise ValueError(f'{exc} at frame {frame:g}') from exc
                expected[frame].append((row,r,target.copy(),desired.copy(),reference,
                                        Vector(resolved['point']).copy()))
            for name in names:
                if frame not in key_frames or not any(a<=frame<=b for a,b in intervals[name]):continue
                bone=obj.pose.bones[name];q=Quaternion(w._rotation(bone))
                if name in previous_quaternions and previous_quaternions[name].dot(q)<0:q.negate()
                previous_quaternions[name]=q.copy()
                if bone.rotation_mode=='QUATERNION':prop='rotation_quaternion';value=tuple(q)
                elif bone.rotation_mode=='AXIS_ANGLE':
                    axis,angle=q.to_axis_angle();prop='rotation_axis_angle';value=(angle,*axis)
                else:
                    e=q.to_euler(bone.rotation_mode,compatible.get(name,bone.rotation_euler));compatible[name]=e;prop='rotation_euler';value=tuple(e)
                for index,v in enumerate(value):samples.setdefault((bone.path_from_id(prop),index),[]).append((frame,v))
            restore_input();yield dict(phase='Fitting contacts',frame=frame,total=len(frames))
        guard();w.assign_action(obj,original,slot)
        if _action_signature(obj)!=signature:raise ValueError('Input action changed during contact correction')
        candidate=original.copy();candidate.name=original.name+' Contacts';candidate.use_fake_user=False
        w.assign_action(obj,candidate,slot)
        curves=w.action_curves(candidate,getattr(obj.animation_data,'action_slot',None),ensure=True,obj=obj)
        path_intervals={obj.pose.bones[name].path_from_id(prop):intervals[name] for name in names for prop in ('rotation_quaternion','rotation_euler','rotation_axis_angle')}
        retained=sum(sum(not ((fc.data_path,fc.array_index) in samples and any(a<=k.co.x<=b for a,b in path_intervals[fc.data_path])) for k in fc.keyframe_points) for fc in curves)
        if retained+sum(map(len,samples.values()))>w.MAX_KEYS:raise ValueError('Corrected candidate exceeds the total key budget')
        for (path,index),points in samples.items():
            fc=curves.find(path,index=index) or curves.new(path,index=index)
            if fc.lock or fc.mute or len(fc.modifiers):raise ValueError('Contact rotation curves contain locks, muting or modifiers')
            boundaries={value for interval in path_intervals[path] for value in interval}
            boundary_state={}
            for boundary in boundaries:
                existing=next((key for key in fc.keyframe_points
                               if abs(float(key.co.x)-boundary)<=1e-8),None)
                if existing is not None:
                    boundary_state[boundary]=dict(
                        is_start=any(abs(boundary-start_frame)<=1e-8
                                     for start_frame,_ in path_intervals[path]),
                        is_end=any(abs(boundary-end_frame)<=1e-8
                                   for _,end_frame in path_intervals[path]),
                        interpolation=existing.interpolation,
                        left_type=existing.handle_left_type,
                        left=tuple(existing.handle_left),
                        right_type=existing.handle_right_type,
                        right=tuple(existing.handle_right))
            if len(boundary_state)!=len(boundaries):
                raise ValueError(
                    'Contact correction requires existing keys at blend interval boundaries')
            for i in range(len(fc.keyframe_points)-1,-1,-1):
                if any(a<=fc.keyframe_points[i].co.x<=b for a,b in path_intervals[path]):fc.keyframe_points.remove(fc.keyframe_points[i],fast=True)
            # Native insert() merges nearby times, which can overwrite distinct
            # adaptive samples. Allocate exact samples, then sort once; retained
            # keys outside the owned intervals keep their original data.
            start=len(fc.keyframe_points);fc.keyframe_points.add(len(points))
            for index,(frame,v) in enumerate(points,start):
                key=fc.keyframe_points[index];key.co=(frame,v);key.interpolation='LINEAR'
            # FCurve.update() also deduplicates close times. These two operations
            # provide ordering/handles without dropping distinct adaptive keys.
            fc.keyframe_points.sort();fc.keyframe_points.handles_recalc()
            for boundary,saved in boundary_state.items():
                existing=next((key for key in fc.keyframe_points
                               if abs(float(key.co.x)-boundary)<=1e-8),None)
                if existing is None:
                    raise ValueError('Contact correction lost an interval boundary key')
                if saved['is_start']:
                    existing.handle_left_type=saved['left_type']
                    existing.handle_left=saved['left']
                if saved['is_end']:
                    existing.interpolation=saved['interpolation']
                    existing.handle_right_type=saved['right_type']
                    existing.handle_right=saved['right']
        if shape_mode:
            # Check cubic output before accepting it or choosing adaptive keys.
            # Only contact limb curves belong to this correction; keep all other
            # animation, including any later flight/body edits, unchanged.
            linear_candidate=candidate
            # Source anchors were validated before the dependency-closed proxy
            # was built. Reuse that snapshot: a proxy intentionally has a
            # reduced rest signature, so re-reading its copied anchors would
            # reject valid shape-aware correction and force the full-rig path.
            candidate,_=curve_smoothing.smooth_copy(obj,linear_candidate,first,last,names=names,_validated_rows=anchors)
            w.assign_action(obj,candidate,slot)
            if linear_candidate.users==0:bpy.data.actions.remove(linear_candidate)
        candidate_signature=_action_signature(obj,candidate)
        refine=[];failed_error=0.;failed_orientation=0.
        for frame in check_frames:
            _frame(scene,frame);p._update(obj)
            for row,r,target,desired,reference,resolved_point in expected[frame]:
                error=(_point(obj,row,r['offset'])-target).length/reference
                orientation=_angle((w.display_world(obj)@obj.pose.bones[row['joints'][2]].matrix).to_quaternion(),desired)
                if error>2e-4 or orientation>.001:
                    if frame in key_frames or len(_refinements)>=4:raise ValueError(f'Evaluated contact failed at frame {frame:g}: {row["id"]}, position={error:.6g}, orientation={orientation:.6g}')
                    refine.append(frame);failed_error=max(failed_error,error);failed_orientation=max(failed_orientation,orientation)
                max_after=max(max_after,error);orientation_error=max(orientation_error,orientation);checks+=1
                if r['start']<=frame<=r['end']:drift_after=max(drift_after,(_point(obj,row,r['offset'])-resolved_point).length/reference)
            if frame in priority_matrices:
                for name,matrix in priority_matrices[frame].items():
                    actual=obj.pose.bones[name].matrix
                    if max(abs(a-b) for ra,rb in zip(matrix,actual) for a,b in zip(ra,rb))>2e-4:raise ValueError('Contact correction changed an authored priority pose')
            _frame(scene,original_frame);yield dict(phase='Checking contacts',frame=frame,total=len(frames))
            guard()
        w.assign_action(obj,original,slot)
        if _action_signature(obj)!=signature:raise ValueError('Input action changed during contact correction')
        if refine:
            history=(*_refinements,dict(added_frames=sorted(set(refine)),position_error=failed_error,orientation_error=failed_orientation))
            restore_input()
            if candidate.users==0:bpy.data.actions.remove(candidate)
            candidate=None
            report=yield from _host_correction_steps(obj,scene,sorted(key_frames|set(refine)),history,started,anchors,flight_intervals,_expected_out,evaluation_view_layer)
            committed=True;return report
        w.assign_action(obj,candidate,slot);_frame(scene,original_frame)
        report=dict(backend=('geometric_contact_projection_shape_v1' if shape_mode else 'geometric_contact_projection_v1'),frames=len(frames),validation_frames=len(check_frames),contacts=len(request),checks=checks,max_before=max_before,max_after=max_after,elapsed_ms=(time.perf_counter()-started)*1000,priority_poses=len(priority),contact_drift_before=drift_before,contact_drift_after=drift_after,orientation_error_radians=orientation_error,sample_interval_frames=.25,validation_max_interval_frames=max(b-a for a,b in zip(check_frames,check_frames[1:])),position_units='fraction of evaluated two-segment limb length',adaptive_refinements=list(_refinements),bend_policy='input limb plane normal with transported straight-limb fallback',prop_relative_contacts=sum(bool(r.get('prop_bound')) and r['limb'].startswith('arm-') for r in request),prop_objects=sorted({r['prop_object'] for r in request if r.get('prop_bound') and r['limb'].startswith('arm-')}),prop_target_space='evaluated object-local',moving_surface_contacts=sum(bool(r.get('prop_bound')) and r['limb'].startswith('leg-') for r in request),moving_surface_objects=sorted({r['prop_object'] for r in request if r.get('prop_bound') and r['limb'].startswith('leg-')}),moving_surface_target_space='evaluated planar-mesh object-local')
        candidate['b4ml_contacts']=json.dumps(_serialized_contacts(request),allow_nan=False);candidate['b4ml_contact_metrics']=json.dumps(report,allow_nan=False)
        if _expected_out is not None:
            _expected_out.clear();_expected_out.update(
                frames={frame:[dict(request=dict(r),target=tuple(target),desired=tuple(desired),reference=reference) for _,r,target,desired,reference,_ in values] for frame,values in expected.items()},
                priority={frame:{name:tuple(tuple(value for value in matrix[row]) for row in range(4)) for name,matrix in matrices.items()} for frame,matrices in priority_matrices.items()})
        state.candidate_action=candidate;state.contact_input=original;state.contact_output=candidate
        state.contact_metrics=json.dumps(report);state.status=f'Contact drift {drift_before:.3g} -> {drift_after:.3g}; fit error {max_after:.3g} limb units';committed=True
        # Keep the unmodified input as an editable alternative. It is never deleted.
        original.use_fake_user=True
        return report
    finally:
        if not committed:
            restore_input()
            if candidate and candidate.users==0:bpy.data.actions.remove(candidate)


def _verify_evaluator_steps(obj,scene,candidate,expected,priority_matrices):
    """Evaluate proxy targets on a complete private rig without re-solving."""
    frames=sorted(expected['frames']);selected={row['request']['limb'] for values in expected['frames'].values() for row in values}
    max_after=drift_after=orientation_error=0.;checks=0
    w.assign_action(obj,candidate,w._slot(obj.animation_data))
    yield dict(phase='Activating complete-rig candidate',frame=p._frame(scene),total=len(frames))
    for frame in frames:
        # scene.frame_set evaluates the overridden private view layer. Calling
        # view_layer.update again repeated the same 706-bone dependency graph.
        _frame(scene,frame);_,_,limbs=p.bindings(obj);mapping={r['id']:r for r in limbs}
        matrices=[w.display_world(obj)]+[obj.pose.bones[n].matrix for limb in selected for n in mapping[limb]['joints']]
        if not all(math.isfinite(v) for m in matrices for row in m for v in row):raise ValueError('Proxy contact result contains non-finite transforms')
        for value in expected['frames'][frame]:
            r=value['request'];row=mapping[r['limb']];target=Vector(value['target']);desired=Quaternion(value['desired']);reference=value['reference']
            error=(_point(obj,row,r['offset'])-target).length/reference
            orientation=_angle((w.display_world(obj)@obj.pose.bones[row['joints'][2]].matrix).to_quaternion(),desired)
            if error>2e-4 or orientation>.001:raise ValueError(f'Proxy contact result differs on the complete rig at frame {frame:g}: {row["id"]}, position={error:.6g}, orientation={orientation:.6g}')
            max_after=max(max_after,error);orientation_error=max(orientation_error,orientation);checks+=1
            if r['start']<=frame<=r['end']:drift_after=max(drift_after,(_point(obj,row,r['offset'])-Vector(r['point'])).length/reference)
        for name,values in priority_matrices.get(frame,{}).items():
            actual=obj.pose.bones[name].matrix
            if max(abs(a-b) for ra,rb in zip(values,actual) for a,b in zip(ra,rb))>2e-4:raise ValueError('Proxy contact result changed an authored priority pose')
        yield dict(phase='Checking complete rig',frame=frame,total=len(frames))
    return dict(complete_rig_validation_frames=len(frames),complete_rig_checks=checks,complete_rig_max_after=max_after,complete_rig_contact_drift_after=drift_after,complete_rig_orientation_error_radians=orientation_error)


def _proxy_correction_steps(obj,scene):
    """Run dense fitting on a private dependency-closed rig, then verify on source."""
    from .body_proxy import EvaluationProxy
    started=time.perf_counter();state=obj.b4ml;w.require_rig(obj);w._reject_nla(obj)
    if state.flight_running:raise ValueError('Finish flight correction first')
    if state.secondary_running or state.cleanup_running:raise ValueError('Finish secondary motion or animation cleanup first')
    if state.body_payload or state.posing_payload or state.quadruped_payload:raise ValueError('Finish assisted posing first')
    previous=state.candidate_action
    if not previous or not obj.animation_data or obj.animation_data.action!=previous:raise ValueError('Generate and select an interpolation candidate first')
    if state.contact_output==previous and not state.contact_input:raise ValueError('Retained contact input is missing; generate a new candidate')
    original=state.contact_input if state.contact_output==previous and state.contact_input else previous
    anchors=w.read_anchors(obj);first,last=anchors[0][0],anchors[-1][0];request=cm.validate(rows(obj),first,last)
    shape_mode=original.get('b4ml_backend')==curve_smoothing.BACKEND;flight_intervals=_flight_intervals(obj,anchors,request)
    frames=cm.sample_frames(request,[f for f,_ in anchors],first,last);source_rest=w._rest_signature(obj);request_signature=rows(obj)
    anchor_signature=[(item.frame,item.payload) for item in state.anchors]
    original_signature=_action_signature(obj,original);original_fake_user=bool(original.use_fake_user);original_frame=p._frame(scene);original_pose=w.raw_pose(obj);original_modes=rs.mode_values(obj);slot=w._slot(obj.animation_data)
    yield dict(phase='Validating contact request',frame=original_frame,total=4)
    yield dict(phase='Validating anchors and contacts',frame=p._frame(scene),total=4)
    yield dict(phase='Capturing source state',frame=original_frame,total=4)
    profile,root,limbs=p.bindings(obj);seeds=set(profile.controls)|set(anchors[0][1]['pose'])|{root}
    for row in limbs:seeds.update(row['fk']);seeds.update(row['joints'])
    proxy=None;verifier=None;scratch=None;candidate=None;candidate_signature=None;committed=False;proxy_init_ms=0.;verification_init_ms=0.;proxy_bones=0;expected={};source_priority={};host_inner=None;verify_inner=None
    def restore_source():
        w.assign_action(obj,previous,slot);_frame(scene,original_frame);w.restore_pose(obj,original_pose);rs.restore_values(obj,original_modes);p._update(obj)
    def source_guard(expected_action=previous, expected_candidate_signature=None):
        if state.candidate_action!=previous or not obj.animation_data or obj.animation_data.action!=expected_action:raise SourceInvalidatedError('Candidate changed during contact correction')
        if _action_signature(obj,original)!=original_signature:raise SourceInvalidatedError('Input action changed during contact correction')
        signature_to_check=(expected_candidate_signature
                            if expected_candidate_signature is not None
                            else candidate_signature)
        if (signature_to_check is not None
                and _action_signature(obj,candidate)!=signature_to_check):raise SourceInvalidatedError('Contact candidate changed after validation')
        if rows(obj)!=request_signature or w._rest_signature(obj)!=source_rest:raise SourceInvalidatedError('Contacts or rig changed during contact correction')
        if [(item.frame,item.payload) for item in state.anchors]!=anchor_signature:raise SourceInvalidatedError('Priority poses changed during contact correction')
        if _flight_intervals(obj,anchors,request_signature)!=flight_intervals:raise SourceInvalidatedError('Generated flight changed during contact correction')
        if abs(p._frame(scene)-original_frame)>1e-5:raise SourceInvalidatedError('Playhead changed during contact correction')
    guard=dict(previous=previous,check=source_guard)
    try:
        source_guard();yield dict(phase='Mapping contact dependencies',frame=original_frame,total=4)
        prepared=time.perf_counter();proxy=EvaluationProxy(obj,seeds,defer=True);iterator=proxy.prepare_steps(obj,seeds)
        try:
            for stage in iterator:
                source_guard();yield dict(phase='Preparing contact evaluator '+stage,frame=original_frame,total=6)
        finally:iterator.close()
        proxy_init_ms=(time.perf_counter()-prepared)*1000.;proxy_bones=len(proxy.obj.pose.bones)
        discrepancy=max(max(abs(a-b) for ra,rb in zip(obj.pose.bones[n].matrix,proxy.obj.pose.bones[n].matrix) for a,b in zip(ra,rb)) for n in proxy.needed)
        if discrepancy>2e-5:raise ValueError('Contact evaluation copy differs from the original rig')
        w.assign_action(proxy.obj,previous,w._slot(proxy.obj.animation_data));proxy.obj.b4ml.candidate_action=previous
        host_inner=_host_correction_steps(proxy.obj,proxy.scene,_started=started,_anchors=anchors,_flight=flight_intervals,_expected_out=expected)
        layer=proxy.scene.view_layers[0]
        while True:
            try:
                with bpy.context.temp_override(scene=proxy.scene,view_layer=layer,object=proxy.obj,active_object=proxy.obj,selected_objects=[proxy.obj],selected_editable_objects=[proxy.obj]):info=next(host_inner)
            except StopIteration as stop:
                proxy_report=stop.value;break
            source_guard();yield info
        scratch=proxy.obj.b4ml.candidate_action;candidate=scratch.copy();candidate.name=scratch.name
        proxy.obj.animation_data.action=None;proxy.obj.b4ml.candidate_action=None;proxy.obj.b4ml.contact_output=None
        proxy.close();proxy=None
        if scratch.users==0:bpy.data.actions.remove(scratch);scratch=None
        prepared=time.perf_counter();verifier=EvaluationProxy(obj,set(obj.pose.bones.keys()),defer=True);iterator=verifier.prepare_steps(obj,set(obj.pose.bones.keys()),preserve_all=True)
        try:
            for stage in iterator:
                source_guard();yield dict(phase='Preparing complete-rig check '+stage,frame=original_frame,total=6)
        finally:iterator.close()
        verification_init_ms=(time.perf_counter()-prepared)*1000.
        discrepancy=max(max(abs(a-b) for ra,rb in zip(obj.pose.bones[n].matrix,verifier.obj.pose.bones[n].matrix) for a,b in zip(ra,rb)) for n in verifier.needed)
        if discrepancy>2e-5:raise ValueError('Complete-rig evaluation copy differs from the original rig')
        layer=verifier.scene.view_layers[0];w.assign_action(verifier.obj,original,w._slot(verifier.obj.animation_data))
        source_guard();yield dict(phase='Preparing complete-rig priority action',frame=original_frame,total=1)
        for frame,_ in anchors:
            with bpy.context.temp_override(scene=verifier.scene,view_layer=layer,object=verifier.obj,active_object=verifier.obj,selected_objects=[verifier.obj],selected_editable_objects=[verifier.obj]):
                _frame(verifier.scene,frame);p._update(verifier.obj)
                source_priority[frame]={name:tuple(tuple(value for value in verifier.obj.pose.bones[name].matrix[row]) for row in range(4)) for name in anchors[0][1]['pose']}
            source_guard();yield dict(phase='Capturing complete-rig priorities',frame=frame,total=len(anchors))
        boundary_frames=set(source_priority)
        for r in request:boundary_frames.update((r['start'],r['end'],max(first,r['start']-r['blend_in']),min(last,r['end']+r['blend_out'])))
        complete_frames={frame for frame in expected['frames'] if abs(frame*2-round(frame*2))<1e-6 or frame in boundary_frames}
        complete_expected=dict(expected);complete_expected['frames']={frame:expected['frames'][frame] for frame in sorted(complete_frames)}
        candidate_signature=_action_signature(obj,candidate)
        verify_inner=_verify_evaluator_steps(verifier.obj,verifier.scene,candidate,complete_expected,source_priority)
        while True:
            try:
                with bpy.context.temp_override(scene=verifier.scene,view_layer=layer,object=verifier.obj,active_object=verifier.obj,selected_objects=[verifier.obj],selected_editable_objects=[verifier.obj]):info=next(verify_inner)
            except StopIteration as stop:
                actual=stop.value;break
            source_guard();yield info
        source_guard();yield dict(phase='Finalizing complete-rig check',frame=original_frame,total=1)
        verifier.obj.animation_data.action=None;verifier.close();verifier=None
        source_guard()
        # Cleanup and report serialization both touch large Rigify data blocks.
        # Give them separate callbacks so neither combines into one UI hitch.
        yield dict(phase='Finalizing verified metrics',frame=original_frame,total=1)
        source_guard()
        # The guard, action signature, report assembly and ID-property writes all
        # touch large Rigify data. Keep each in its own modal callback so their
        # costs cannot accumulate into a single visible pause.
        yield dict(phase='Validating verified source',frame=original_frame,total=3)
        if _action_signature(obj,original)!=original_signature:raise SourceInvalidatedError('Input action changed during contact correction')
        yield dict(phase='Assembling verified metrics',frame=original_frame,total=3)
        report=dict(proxy_report);report.update(actual);report['max_after']=max(report['max_after'],actual['complete_rig_max_after']);report['contact_drift_after']=max(report['contact_drift_after'],actual['complete_rig_contact_drift_after']);report['orientation_error_radians']=max(report['orientation_error_radians'],actual['complete_rig_orientation_error_radians'])
        report.update(backend=proxy_report['backend']+'_proxy_v1',elapsed_ms=(time.perf_counter()-started)*1000.,evaluation_backend='dependency_closed_proxy',verification_backend='complete_rig_proxy',full_rig_bones=len(obj.pose.bones),evaluation_bones=proxy_bones,proxy_init_ms=proxy_init_ms,verification_init_ms=verification_init_ms,complete_rig_validation=True,complete_rig_validation_interval_frames=.5)
        yield dict(phase='Serializing verified metrics',frame=original_frame,total=3)
        candidate['b4ml_contacts']=json.dumps(_serialized_contacts(request),allow_nan=False);candidate['b4ml_contact_metrics']=json.dumps(report,allow_nan=False)
        source_guard();yield dict(phase='Publishing verified contacts',frame=original_frame,total=2)
        source_guard()
        # source_guard proves the playhead is already at original_frame. Setting
        # it again forces a full 706-bone depsgraph evaluation and creates a UI
        # hitch without changing state.
        w.assign_action(obj,candidate,slot)
        # Publication remains rollback-safe until this second boundary passes.
        # Cancelling here restores the previous action and removes the scratch.
        yield dict(phase='Committing verified contacts',frame=original_frame,total=2)
        source_guard(candidate,candidate_signature)
        state.candidate_action=candidate;state.contact_input=original;state.contact_output=candidate
        state.contact_metrics=json.dumps(report);state.status=f'Contact drift {report["contact_drift_before"]:.3g} -> {report["contact_drift_after"]:.3g}; fit error {report["max_after"]:.3g} limb units';original.use_fake_user=True;committed=True
        return report
    finally:
        if verify_inner:verify_inner.close()
        if host_inner:host_inner.close()
        if proxy:
            if proxy.obj and proxy.obj.animation_data:proxy.obj.animation_data.action=None
            proxy.close()
        if verifier:
            if verifier.obj and verifier.obj.animation_data:verifier.obj.animation_data.action=None
            verifier.close()
        if scratch and scratch.users==0:bpy.data.actions.remove(scratch)
        if not committed:
            restore_source()
            original.use_fake_user=original_fake_user
            if candidate and candidate.users==0:bpy.data.actions.remove(candidate)


def correction_steps(obj,scene,_extra_frames=(),_refinements=(),_started=None):
    # Small and externally constrained rigs avoid proxy construction overhead or
    # fall back to the original evaluated-host implementation.
    evaluation_view_layer=_evaluation_view_layer(scene)
    if (_extra_frames or _refinements or _started is not None or len(obj.pose.bones)<128 or
            any(row.get('prop_bound') for row in rows(obj))):
        return (yield from _host_correction_steps(obj,scene,_extra_frames,_refinements,_started,_view_layer=evaluation_view_layer))
    try:
        return (yield from _proxy_correction_steps(obj,scene))
    except SourceInvalidatedError:
        raise
    except ValueError:
        # The source is restored by the proxy path before this fallback starts.
        return (yield from _host_correction_steps(obj,scene))


def start(obj,scene):
    if obj.b4ml.flight_running:raise ValueError('Finish flight correction first')
    if obj.b4ml.secondary_running or obj.b4ml.cleanup_running:raise ValueError('Finish secondary motion or animation cleanup first')
    if obj.as_pointer() in _JOBS:raise ValueError('Contact correction is already running')
    iterator=correction_steps(obj,scene);_JOBS[obj.as_pointer()]=dict(obj=obj,iterator=iterator)
    obj.b4ml.contact_running=True;obj.b4ml.contact_progress='Preparing contact correction'


def step(obj):
    job=_JOBS.get(obj.as_pointer())
    if job is None:raise InterruptedError('Contact correction stopped')
    # Keep individual UI callbacks comfortably below the 50 ms product gate.
    # Cheap dependency/driver/constraint yields may share a callback; object
    # copies, scene creation and edit-bone pruning remain hard yield boundaries.
    deadline=time.perf_counter()+.018
    try:
        while True:
            info=next(job['iterator']);obj.b4ml.contact_progress=f"{info['phase']}: frame {info['frame']:g}"
            phase=info['phase']
            hard_boundary=phase.startswith(('Validating','Capturing','Mapping','Finalizing','Activating','Assembling','Serializing','Publishing','Committing')) or (
                phase.startswith('Preparing') and phase.rsplit(' ',1)[-1] in {'copy','scene','prune','action'})
            if hard_boundary or time.perf_counter()>=deadline:return False
    except StopIteration:
        _JOBS.pop(obj.as_pointer(),None);obj.b4ml.contact_running=False;obj.b4ml.contact_progress='';return True
    except BaseException:abort(obj);raise


def abort(obj):
    job=_JOBS.pop(obj.as_pointer(),None)
    try:
        if job:job['iterator'].close()
    finally:obj.b4ml.contact_running=False;obj.b4ml.contact_progress=''


def solve(obj,scene):
    start(obj,scene)
    while not step(obj):pass
    return json.loads(obj.b4ml.contact_metrics)


@bpy.app.handlers.persistent
def reset(*args):
    for job in list(_JOBS.values()):
        try:abort(job['obj'])
        except (ReferenceError,RuntimeError):pass
    _JOBS.clear()
    for job in list(_SUGGEST_JOBS.values()):
        try:suggest_abort(job['obj'])
        except (ReferenceError,RuntimeError):pass
    _SUGGEST_JOBS.clear()


def register():
    for name in ('load_pre','undo_pre','redo_pre','save_pre'):
        handlers=getattr(bpy.app.handlers,name)
        if reset not in handlers:handlers.append(reset)


def unregister():
    reset()
    for name in ('load_pre','undo_pre','redo_pre','save_pre'):
        handlers=getattr(bpy.app.handlers,name)
        if reset in handlers:handlers.remove(reset)
