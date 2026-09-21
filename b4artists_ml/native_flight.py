"""Native instance-space COM flight; source rig evaluation stays at its origin.
SPDX-License-Identifier: GPL-2.0-or-later
"""
import json,math,time
import numpy as np
import bpy
from mathutils import Matrix,Vector
from . import workflow as w,posing as p,contacts,support,flight_math as fm,motion_layer as m,rig_state as rs,angular_math as am,collision_math as cm
from .support_math import center_of_mass



def _segment_geometry(evaluated,names,world=None):
    """Sample the already validated mapping; retain host arithmetic exactly.

    Mapping/rest/input changes are checked at every cooperative boundary. Fit
    samples need only mass segments; full deformation is checked separately.
    """
    world=evaluated.matrix_world if world is None else world
    heads=np.array([world@evaluated.pose.bones[n].head for n in names])
    tail_indices={i for _,i,j,_ in support.SEGMENTS if j is None}
    tails={i:world@evaluated.pose.bones[names[i]].tail for i in tail_indices}
    starts=np.array([heads[i] for _,i,j,_ in support.SEGMENTS])
    ends=np.array([heads[j] if j is not None else tails[i] for _,i,j,_ in support.SEGMENTS])
    hints=np.array([np.asarray((world@evaluated.pose.bones[names[i]].matrix).to_3x3(),dtype=float)[:,0]
        for _,i,j,_ in support.SEGMENTS])
    return starts,ends,hints


def _segment_points(evaluated,names):
    return _segment_geometry(evaluated,names)[:2]


def correction_steps(obj,scene):
    from . import flight as f
    w.require_rig(obj);w._reject_nla(obj);state=obj.b4ml
    if state.body_payload or state.posing_payload or state.quadruped_payload or state.contact_running:raise ValueError('Finish the active pose or contact correction first')
    if bpy.context.screen and bpy.context.screen.is_animation_playing:raise ValueError('Stop playback before flight correction')
    action=state.candidate_action
    if not action or not obj.animation_data or obj.animation_data.action!=action:raise ValueError('Generate and select an interpolation candidate first')
    if state.contact_output:raise ValueError('Restore Before Contacts before editing flight')
    if state.flight_output or m.find(obj):raise ValueError('Restore Before Flight before generating another native layer')
    anchors=w.read_anchors(obj);priorities=[v[0] for v in anchors];raw=f.request(obj,scene)
    intervals=fm.validate(raw['flights'],priorities,raw['contacts'])
    transitions=fm.transition_spans(intervals,priorities,raw['contacts'])
    collision_intervals=[row for row in intervals if row.get('collision_strength',0.)>0]
    contact_impulse_intervals=[row for row in intervals if row.get('contact_impulse_strength',0.)>0]
    support_intervals=[row for row in intervals if row.get('collision_strength',0.)>0 or row.get('contact_impulse_strength',0.)>0]
    if support_intervals:
        collision_point,collision_normal,collision_triangles,collision_surface,collision_token=contacts._plane_surface(state,scene)
        collision_point=np.asarray(collision_point,dtype=float);collision_normal=np.asarray(collision_normal,dtype=float)
    else:
        collision_point=collision_normal=collision_triangles=collision_surface=collision_token=None
    if [v['name'] for v in raw['masses']]!=[v[0] for v in support.SEGMENTS]:raise ValueError('Initialize the humanoid mass model first')
    weights=[v['weight'] for v in raw['masses']];fractions=[v['fraction'] for v in raw['masses']];radii=[v['inertia_radius'] for v in raw['masses']]
    if not np.isfinite([raw['fps'],raw['fps_base']]).all() or min(raw['fps'],raw['fps_base'])<=0:raise ValueError('A positive frame rate is required')
    dt=raw['fps_base']/raw['fps'];gravity=np.asarray(raw['gravity'],float)
    if not np.isfinite(gravity).all():raise ValueError('Scene gravity must be finite')
    if max(priorities)-min(priorities)>w.MAX_FRAMES:raise ValueError('Native flight exceeds the candidate frame budget')
    binding=support.body_solver.mapping(obj,writable=False);names=sorted(set(binding['names'])|{b.name for b in obj.data.bones if b.use_deform})
    initial_frame=p._frame(scene);world=obj.matrix_world.copy();rest=w._rest_signature(obj);pose=w.raw_pose(obj);modes=rs.mode_values(obj);token=f._curve_token(obj);backend=state.flight_backend
    instance=None;committed=False;at_checkpoint=False;return_frame=initial_frame;began=time.perf_counter();cache={};mass_cache={};report_rows=[];max_before=0.;max_after=0.;max_basis=0.;max_rigid=0.
    def guard():
        nonlocal return_frame
        if p._frame(scene)!=initial_frame:
            return_frame=p._frame(scene);raise ValueError('Playhead changed during native flight correction')
        if w.raw_pose(obj)!=pose or rs.mode_values(obj)!=modes:raise ValueError('Pose controls or rig modes changed during native flight correction')
        if obj.animation_data.action!=action or state.candidate_action!=action:raise ValueError('Candidate changed during native flight correction')
        if obj.matrix_world!=world or p._frame(scene)!=initial_frame:raise ValueError('Playhead or object transform changed during native flight correction')
        if f.request(obj,scene)!=raw or state.flight_backend!=backend or w._rest_signature(obj)!=rest:raise ValueError('Flight settings or rig changed during correction')
        if support_intervals and contacts._plane_surface(state,scene)[4]!=collision_token:raise ValueError('Collision surface changed during correction')
        if f._curve_token(obj)!=token:raise ValueError('Input animation changed during native flight correction')
        if instance is not None:m.validate(obj)
    def frame_at(frame):
        contacts._frame(scene,float(frame));bpy.context.view_layer.update()
        if obj.matrix_world!=world:raise ValueError('Animated armature object transforms are not supported by native flight')
        if (list(scene.gravity) if scene.use_gravity else [0.,0.,0.])!=raw['gravity']:raise ValueError('Animated gravity requires a different flight model')
    def rewind():
        contacts._frame(scene,initial_frame)
        # Sampling never writes source channels; restore any original unkeyed values.
        changed=False
        for name,v in pose.items():
            bone=obj.pose.bones[name];prop='rotation_quaternion' if v['mode']=='QUATERNION' else 'rotation_axis_angle' if v['mode']=='AXIS_ANGLE' else 'rotation_euler'
            for key,value in (('location',v['location']),('scale',v['scale']),(prop,v['raw_rotation'])):
                if tuple(getattr(bone,key))!=tuple(value):setattr(bone,key,value);changed=True
        if changed:p._update(obj)
    def measured(evaluated):
        a,b,hints=_segment_geometry(evaluated,binding['names'])
        com,centers,normalized=center_of_mass(a,b,weights,fractions)
        scale=max(float(sum(np.linalg.norm(b[i]-a[i]) for i in range(3))),1e-8)
        orientations=am.segment_orientations(a,b,hints);principal=am.segment_principal_inertia(a,b,radii);lengths=np.linalg.norm(b-a,axis=1)
        return com,scale,centers,normalized,orientations,principal,lengths
    def sample_mass(frame):
        frame_at(frame)
        return measured(obj.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    def mass_at(frame):
        if frame not in mass_cache:mass_cache[frame]=sample_mass(frame)
        return mass_cache[frame]
    def sample_source(frame, *, deformation=True):
        frame_at(frame)
        evaluated=obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
        if frame not in mass_cache:mass_cache[frame]=measured(evaluated)
        com,scale,centers,normalized,*_=mass_cache[frame]
        matrices=None
        if deformation:
            matrices=np.array([evaluated.matrix_world@evaluated.pose.bones[n].matrix for n in names])
            if not np.isfinite(matrices).all():raise ValueError('Nonfinite evaluated rig')
        return com,scale,matrices
    def source_com(frame):
        if frame not in cache:cache[frame]=mass_at(frame)[0]
        return cache[frame]
    def target(row,frame,source):
        u=(frame-row['start'])/(row['end']-row['start'])
        return source+(fm.trajectory(row['a'],row['b'],[u],row['duration'],gravity)[0]-source)*row['strength']
    try:
        rewind();at_checkpoint=True
        yield dict(phase='Validating native flight inputs',frame=initial_frame,total=len(intervals));guard();at_checkpoint=False
        for row in intervals:
            row['a']=source_com(row['start']);row['b']=source_com(row['end']);row['scale']=sample_source(row['start'],deformation=False)[1];row['duration']=(row['end']-row['start'])*dt
            row['times']=sorted({row['start'],row['end']}|{i/2 for i in range(math.ceil(row['start']*2),math.floor(row['end']*2)+1)}|{a for a in priorities if row['start']<a<row['end']})
            row['values']={}
            rewind();at_checkpoint=True
            yield dict(phase='Preparing native flight interval',frame=row['start'],total=len(intervals));guard();at_checkpoint=False
            for left,right in zip(row['times'],row['times'][1:]):
                if right-left<1e-5:raise ValueError('Flight keys exceed stable frame precision')
                for frame in (left,left+(right-left)/3,left+2*(right-left)/3,right):
                    if frame not in row['values']:
                        source=source_com(frame);u=(frame-row['start'])/(row['end']-row['start'])
                        row['values'][frame]=(row['a']*(1-u)+row['b']*u-source)*row['strength']
                        error=float(np.linalg.norm(target(row,frame,source)-source))/row['scale'];max_before=max(max_before,error)
                        if frame in priorities and error>2e-4:raise ValueError('Gravity arc conflicts with a priority pose')
                rewind();at_checkpoint=True
                yield dict(phase='Fitting native COM flight',frame=right,total=len(row['times']));guard();at_checkpoint=False
            angular_strength=row.get('angular_momentum_strength',0.)
            if angular_strength:
                if any(row['start']<frame<row['end'] for frame in priorities):
                    raise ValueError('Split angular momentum intervals at every authored priority pose')
                count=max(5,int(math.ceil((row['end']-row['start'])*4))+1)
                angular_frames=np.linspace(row['start'],row['end'],count).tolist()
                centers=[];orientations=[];principal=[]
                for frame in angular_frames:
                    sample=mass_at(frame);centers.append(sample[2]);orientations.append(sample[4]);principal.append(sample[5]);rewind();at_checkpoint=True
                    yield dict(phase='Sampling angular momentum',frame=frame,total=len(angular_frames));guard();at_checkpoint=False
                centers=np.asarray(centers);orientations=np.asarray(orientations);principal=np.asarray(principal)
                seconds=(np.asarray(angular_frames)-row['start'])*dt
                row['angular_frames']=angular_frames
                row['angular_source_com']=np.asarray([source_com(frame) for frame in angular_frames])
                row['angular']=am.refine(centers,weights,seconds,angular_strength,orientations=orientations,principal_inertia=principal)
                quaternions=[]
                for rotation in row['angular']['rotations']:
                    q=Matrix(rotation.tolist()).to_quaternion()
                    if quaternions and q.dot(quaternions[-1])<0:q.negate()
                    quaternions.append(q)
                row['angular_quaternions']=quaternions;row['angular_pivot_values']={};row['angular_pivot_controls']={}
                rewind();at_checkpoint=True
                yield dict(phase='Solving angular momentum',frame=row['end'],total=len(intervals));guard();at_checkpoint=False
                def pivot_at(frame,index,u):
                    q=np.asarray(quaternions[index])*(1-u)+np.asarray(quaternions[index+1])*u;q/=np.linalg.norm(q)
                    rotation=np.asarray(Matrix(Quaternion(q).to_matrix()).to_3x3(),dtype=float)
                    source=source_com(frame)
                    return source-rotation@source
                from mathutils import Quaternion
                for index,(left,right) in enumerate(zip(angular_frames,angular_frames[1:])):
                    frames=(left,left+(right-left)/3,left+2*(right-left)/3,right)
                    values=[pivot_at(frame,index,u) for frame,u in zip(frames,(0.,1/3,2/3,1.))]
                    row['angular_pivot_values'][left]=values[0];row['angular_pivot_values'][right]=values[-1]
                    row['angular_pivot_controls'][(left,right)]=fm.cubic_controls(values)
                    rewind();at_checkpoint=True
                    yield dict(phase='Fitting angular COM pivot',frame=right,total=len(angular_frames));guard();at_checkpoint=False
                rewind();at_checkpoint=True
                yield dict(phase='Fitting angular momentum',frame=row['end'],total=len(intervals));guard();at_checkpoint=False
            if row.get('collision_strength',0.):
                from mathutils import Quaternion
                count=max(2,int(math.ceil((row['end']-row['start'])*4))+1)
                frames=np.linspace(row['start'],row['end'],count).tolist();values={};required=[];remaining=[];participants=[];clearance=row['collision_clearance']*row['scale'];safety_margin=row['scale']*5e-4
                def planned_rotation(frame):
                    if row.get('angular') is None or row['angular']['effective_strength']<=0:return np.eye(3)
                    angular_frames=row['angular_frames'];index=min(max(int(np.searchsorted(angular_frames,frame)-1),0),len(angular_frames)-2)
                    left,right=angular_frames[index:index+2];u=(frame-left)/(right-left)
                    q=np.asarray(row['angular_quaternions'][index])*(1-u)+np.asarray(row['angular_quaternions'][index+1])*u;q/=np.linalg.norm(q)
                    return np.asarray(Matrix(Quaternion(q).to_matrix()).to_3x3(),dtype=float)
                for frame in frames:
                    sample=mass_at(frame);source=sample[0];rotation=planned_rotation(frame);wanted=target(row,frame,source)
                    centers=(rotation@(sample[2]-source).T).T+wanted;orientations=np.einsum('ij,njk->nik',rotation,sample[4])
                    projected=centers-((centers-collision_point)@collision_normal)[:,None]*collision_normal
                    inside=[contacts._inside_surface(Vector(point),collision_triangles) for point in projected]
                    base=cm.correction(centers,orientations,sample[6],radii,collision_point,collision_normal,clearance,0.,inside)
                    effective_clearance=clearance if frame in (row['start'],row['end']) else clearance+safety_margin
                    result=cm.correction(centers,orientations,sample[6],radii,collision_point,collision_normal,effective_clearance,row['collision_strength'],inside)
                    if frame in (row['start'],row['end']):
                        if base['required_lift']/row['scale']>2e-4:
                            raise ValueError(f'Planar collision response conflicts with authored priority pose at frame {frame:g} ({base["required_lift"]/row["scale"]:.6g} body lengths; participating_segments={base["participating_segments"]}); adjust the plane, clearance, or priority pose')
                        result['vector']=np.zeros(3);result['applied_lift']=0.
                    values[frame]=result['vector'];required.append(base['required_lift']);remaining.append(max(0.,base['required_lift']-result['applied_lift']));participants.append(base['participating_segments'])
                    rewind();at_checkpoint=True
                    yield dict(phase='Fitting planar collision response',frame=frame,total=len(frames));guard();at_checkpoint=False
                row['collision']=dict(start=row['start'],end=row['end'],times=frames,values=values,strength=0.,duration=row['duration'],linear=True,
                    required=required,remaining=remaining,participants=participants,surface=collision_surface,clearance=clearance,safety_margin=safety_margin)
        # Fit boundary derivatives on the appropriate side of each authored pose.
        # One-sided second-order differences avoid crossing an authored key corner.
        def published_correction_derivatives(row,landing):
            left,right=(row['times'][-2],row['times'][-1]) if landing else (row['times'][0],row['times'][1])
            width=right-left;samples=[row['values'][v] for v in (left,left+width/3,left+2*width/3,right)]
            a,b=fm.cubic_controls(samples)
            if landing:
                velocity=3*(samples[3]-b)/width/dt
                acceleration=6*(samples[3]-2*b+a)/width**2/dt**2
                u=1.
            else:
                velocity=3*(a-samples[0])/width/dt
                acceleration=6*(samples[0]-2*a+b)/width**2/dt**2
                u=0.
            velocity+=.5*gravity*row['duration']*(2*u-1)*row['strength']
            acceleration+=gravity*row['strength']
            collision=row.get('collision')
            if collision:
                times=collision['times'];a_frame,b_frame=(times[-2],times[-1]) if landing else (times[0],times[1])
                slope=(collision['values'][b_frame]-collision['values'][a_frame])/(b_frame-a_frame)/dt
                velocity+=slope
            return velocity,acceleration
        def collision_value(row,frame):
            collision=row.get('collision')
            if not collision or frame<row['start'] or frame>row['end']:return np.zeros(3)
            times=collision['times'];values=collision['values'];index=int(np.searchsorted(times,frame))
            if index<=0:return values[times[0]]
            if index>=len(times):return values[times[-1]]
            left,right=times[index-1:index+1];u=(frame-left)/(right-left)
            return values[left]*(1-u)+values[right]*u
        def published_target(row,frame,source):return target(row,frame,source)+collision_value(row,frame)
        for span in transitions:
            row=intervals[span['flight_index']];boundary=row['end'] if span['landing'] else row['start']
            h=min(.125,(row['end']-row['start'])/8,(span['end']-span['start'])/8)
            span['match_acceleration']=bool(row.get('match_acceleration'));velocity_h=min(h,1/32) if span['match_acceleration'] else h
            direction=1 if span['landing'] else -1
            def derivative(function,side):
                return side*(-3*function(boundary)+4*function(boundary+side*velocity_h)-function(boundary+side*2*velocity_h))/(2*velocity_h*dt)
            def second_derivative(function,side):
                return (2*function(boundary)-5*function(boundary+side*h)+4*function(boundary+side*2*h)-function(boundary+side*3*h))/(h*dt)**2
            outside=derivative(source_com,direction)
            if span['match_acceleration']:
                published_velocity,published_acceleration=published_correction_derivatives(row,span['landing'])
                inside=derivative(source_com,-direction)+published_velocity
            else:
                published_acceleration=None;inside=derivative(lambda frame:published_target(row,frame,source_com(frame)),-direction)
            impulse_strength=max(row.get('collision_strength',0.),row.get('contact_impulse_strength',0.))
            span['impulse_strength']=impulse_strength
            unconstrained_velocity=inside-outside;span['collision_impulse_velocity']=np.zeros(3)
            if span['landing'] and impulse_strength:
                impulse=cm.contact_transition_delta(unconstrained_velocity,collision_normal,impulse_strength)
                span['velocity']=impulse['corrected'];span['collision_impulse_velocity']=impulse['absorbed'];span['collision_normal']=impulse['normal']
            else:span['velocity']=unconstrained_velocity
            span['duration']=(span['end']-span['start'])*dt
            span['h']=h;span['velocity_h']=velocity_h;span['scale']=row['scale'];span['before_full_jump']=float(np.linalg.norm(unconstrained_velocity));span['before_jump']=float(np.linalg.norm(span['velocity']))
            if span['match_acceleration']:
                outside_acceleration=second_derivative(source_com,direction)
                inside_acceleration=second_derivative(source_com,-direction)+published_acceleration
                unconstrained_acceleration=inside_acceleration-outside_acceleration;span['collision_impulse_acceleration']=np.zeros(3)
                if span['landing'] and impulse_strength:
                    impulse=cm.contact_transition_delta(unconstrained_acceleration,collision_normal,impulse_strength)
                    span['acceleration']=impulse['corrected'];span['collision_impulse_acceleration']=impulse['absorbed']
                else:span['acceleration']=unconstrained_acceleration
                span['before_full_acceleration_jump']=float(np.linalg.norm(unconstrained_acceleration));span['before_acceleration_jump']=float(np.linalg.norm(span['acceleration']))
                spline=fm.transition_c2_spline(span['duration'],span['velocity'],span['acceleration'],span['landing'])
                span['spline']=spline;span['times']=[span['start']+(span['end']-span['start'])*u for u in spline['knots']]
                span['values']=dict(zip(span['times'],spline['values']))
                span['controls']={(span['times'][i],span['times'][i+1]):(spline['right'][i],spline['left'][i]) for i in range(3)}
            else:
                span['acceleration']=np.zeros(3);span['before_acceleration_jump']=None;span['before_full_acceleration_jump']=None;span['collision_impulse_acceleration']=np.zeros(3);span['times']=[span['start'],span['end']]
                left,right=span['start'],span['end'];frames=[left,left+(right-left)/3,left+2*(right-left)/3,right]
                span['values']=dict(zip(frames,fm.transition_offset([0,1/3,2/3,1],span['duration'],span['velocity'],span['landing'])))
            span['strength']=0.
            rewind();at_checkpoint=True
            yield dict(phase='Fitting COM transitions',frame=boundary,total=len(transitions));guard();at_checkpoint=False
        curve_rows=intervals+transitions+[row['collision'] for row in intervals if row.get('collision')]
        angular_rows=[row for row in intervals if row.get('angular') is not None and row['angular']['effective_strength']>0]
        total_keys=(sum(len(r['times']) for r in curve_rows)*3
                    + sum(len(row['angular_frames'])*7 for row in angular_rows))
        if total_keys>w.MAX_KEYS:raise ValueError('Native flight exceeds the key budget')
        instance=m.begin(obj,scene);owned_action=None
        for index,row in enumerate(curve_rows):
            for frame in row['times']:
                for axis in range(3):
                    prop=f'b4ml_residual_{index}_{axis}';instance[prop]=float(row['values'][frame][axis]);instance.keyframe_insert(data_path='["'+prop+'"]',frame=frame)
                    if owned_action is None:
                        owned_action=instance.animation_data.action
                        owned_action['b4ml_motion_generated']=m._read(obj)['token']
            curves=w.action_curves(instance.animation_data.action,getattr(instance.animation_data,'action_slot',None))
            for axis in range(3):
                fc=curves.find(f'["b4ml_residual_{index}_{axis}"]');keys={float(k.co.x):k for k in fc.keyframe_points};times=sorted(keys)
                if 'controls' in row:
                    for key in keys.values():key.handle_left_type=key.handle_right_type='FREE'
                if row.get('linear'):
                    for key in keys.values():key.interpolation='LINEAR'
                    fc.update();continue
                for left,right in zip(row['times'],row['times'][1:]):
                    if 'controls' in row:a,b=row['controls'][(left,right)]
                    else:a,b=fm.cubic_controls([row['values'][v] for v in (left,left+(right-left)/3,left+2*(right-left)/3,right)])
                    ka=f._key_at(keys,times,left);kb=f._key_at(keys,times,right)
                    if 'controls' not in row:ka.handle_right_type=kb.handle_left_type='FREE'
                    ka.interpolation='BEZIER'
                    ka.handle_right=(left+(right-left)/3,float(a[axis]));kb.handle_left=(left+2*(right-left)/3,float(b[axis]))
                fc.update()
        if angular_rows:
            instance.rotation_mode='QUATERNION';previous=None
            for angular_index,row in enumerate(angular_rows):
                for frame,quaternion in zip(row['angular_frames'],row['angular_quaternions']):
                    if previous is not None and quaternion.dot(previous)<0:quaternion.negate()
                    instance.rotation_quaternion=quaternion;instance.keyframe_insert('rotation_quaternion',frame=frame);previous=quaternion.copy()
                    pivot=row['angular_pivot_values'][frame]
                    for axis in range(3):
                        prop=f'b4ml_angular_pivot_{angular_index}_{axis}';instance[prop]=float(pivot[axis]);instance.keyframe_insert(data_path='["'+prop+'"]',frame=frame)
            curves=w.action_curves(instance.animation_data.action,getattr(instance.animation_data,'action_slot',None))
            for axis in range(4):
                fc=curves.find('rotation_quaternion',index=axis)
                if fc is None:raise ValueError('Host did not create editable angular rotation curves')
                for key in fc.keyframe_points:key.interpolation='LINEAR'
                fc.update()
            for angular_index,row in enumerate(angular_rows):
                for axis in range(3):
                    fc=curves.find(f'["b4ml_angular_pivot_{angular_index}_{axis}"]')
                    if fc is None:raise ValueError('Host did not create editable angular pivot curves')
                    keys={float(key.co.x):key for key in fc.keyframe_points};times=sorted(keys)
                    for left,right in zip(row['angular_frames'],row['angular_frames'][1:]):
                        a,b=row['angular_pivot_controls'][(left,right)];ka=f._key_at(keys,times,left);kb=f._key_at(keys,times,right)
                        ka.handle_right_type=kb.handle_left_type='FREE';ka.interpolation='BEZIER'
                        ka.handle_right=(left+(right-left)/3,float(a[axis]));kb.handle_left=(left+2*(right-left)/3,float(b[axis]))
                    fc.update()
        for axis in range(3):
            fc=instance.driver_add('location',axis);fc.keyframe_points.clear();driver=fc.driver;driver.type='SCRIPTED';specs=[]
            for index,row in enumerate(curve_rows):
                u=f'((frame-{row["start"]!r})/{(row["end"]-row["start"])!r})';g=.5*float(gravity[axis])*row['duration']**2*row['strength']
                specs.append((f'["b4ml_residual_{index}_{axis}"]',lambda name,row=row,u=u,g=g:f'({name}+{g!r}*({u}**2-{u}) if {row["start"]!r}<=frame<={row["end"]!r} else 0)'))
            for angular_index,row in enumerate(angular_rows):
                specs.append((f'["b4ml_angular_pivot_{angular_index}_{axis}"]',lambda name,row=row:f'({name} if {row["start"]!r}<=frame<={row["end"]!r} else 0)'))
            terms=[]
            for index,(path,expression_for) in enumerate(specs):
                variable=driver.variables.new();variable.name=f'r{index}';variable.type='SINGLE_PROP';variable.targets[0].id=instance;variable.targets[0].data_path=path
                terms.append(expression_for(variable.name))
            expression='+'.join(terms);driver.expression=expression
            if driver.expression!=expression:
                # Keep each interval in a small native driver; one final sum
                # avoids the host's expression-length cap without Python callbacks.
                for variable in list(driver.variables):driver.variables.remove(variable)
                for index,(path,expression_for) in enumerate(specs):
                    prop=f'b4ml_flight_term_{index}_{axis}';instance[prop]=0.
                    part=instance.driver_add(f'["{prop}"]');part.keyframe_points.clear();part.driver.type='SCRIPTED'
                    variable=part.driver.variables.new();variable.name=f'r{index}';variable.type='SINGLE_PROP'
                    variable.targets[0].id=instance;variable.targets[0].data_path=path
                    term=expression_for(variable.name);part.driver.expression=term
                    if part.driver.expression!=term:raise ValueError('Flight interval exceeds this host driver expression limit')
                    variable=driver.variables.new();variable.name=f'v{index}';variable.type='SINGLE_PROP'
                    variable.targets[0].id=instance;variable.targets[0].data_path=f'["{prop}"]'
                driver.expression='+'.join(f'v{index}' for index in range(len(terms)))
        instance.animation_data.action['b4ml_motion_generated']=m._read(obj)['token']
        instance['b4ml_native_flight']=True
        instance['b4ml_flight']=json.dumps(dict(flights=raw['flights']),allow_nan=False)
        for row in intervals:
            entry,exit=fm.endpoint_velocities(row['a'],row['b'],row['duration'],gravity)
            metric=dict(start=row['start'],end=row['end'],strength=row['strength'],duration_seconds=row['duration'],ballistic_entry_velocity=entry.tolist(),ballistic_exit_velocity=exit.tolist())
            phase_errors=[]
            for phase in (0.,.137):
                frames=np.arange(row['start']+phase,row['end']+1e-7,.25);positions=[];desired=[]
                for frame in frames:
                    source,scale,before=sample_source(float(frame));wanted=published_target(row,float(frame),source);actual=None;after=None
                    for e in bpy.context.evaluated_depsgraph_get().object_instances:
                        if e.is_instance and e.parent and e.parent.original==instance and e.object.original==obj:
                            heads=np.array([e.matrix_world@e.object.pose.bones[n].head for n in binding['names']]);tails=np.array([e.matrix_world@e.object.pose.bones[n].tail for n in binding['names']])
                            a=np.array([heads[i] for _,i,j,weight in support.SEGMENTS]);b=np.array([heads[j] if j is not None else tails[i] for _,i,j,weight in support.SEGMENTS]);actual=center_of_mass(a,b,weights,fractions)[0]
                            after=np.array([e.matrix_world@e.object.pose.bones[n].matrix for n in names]);break
                    if actual is None:raise ValueError('Native character instance is missing from evaluation')
                    error=float(np.linalg.norm(actual-wanted))/row['scale'];max_after=max(max_after,error)
                    rotation=np.asarray(instance.matrix_world.to_3x3(),dtype=float)
                    expected=before.copy();expected[:,:3,:3]=np.einsum('ij,njk->nik',rotation,before[:,:3,:3]);expected[:,:3,3]=(rotation@(before[:,:3,3]-source).T).T+wanted
                    lengths=np.linalg.norm(expected[:,:3,:3],axis=1);basis=float(np.max(np.linalg.norm(after[:,:3,:3]-expected[:,:3,:3],axis=1)/np.maximum(lengths,1e-8)));max_basis=max(max_basis,basis)
                    rigid=float(np.max(np.linalg.norm(after[:,:3,3]-expected[:,:3,3],axis=1)))/row['scale'];max_rigid=max(max_rigid,rigid)
                    if max(error,basis,rigid)>2e-4:raise ValueError('Native flight fails COM or deformation preservation')
                    positions.append(actual);desired.append(wanted)
                    rewind();at_checkpoint=True
                    yield dict(phase='Checking native COM flight',frame=float(frame),total=len(frames));guard();at_checkpoint=False
                if len(positions)>=3:
                    acceleration=np.diff(positions,n=2,axis=0)/(.25*dt)**2
                    expected=np.tile(gravity,(len(acceleration),1)) if row['strength']==1. and not row.get('collision') else np.diff(desired,n=2,axis=0)/(.25*dt)**2
                    error=float(np.percentile(np.linalg.norm(acceleration-expected,axis=1),95));phase_errors.append(error)
                    if error>=.1:raise ValueError(f'Native flight acceleration error {error:.6g} exceeds 0.1; shorten or retime the flight')
            metric['acceleration_error_p95']=max(phase_errors,default=0.)
            if row.get('angular') is not None:
                displayed=[];displayed_orientations=[];displayed_principal=[]
                for frame in row['angular_frames']:
                    frame_at(frame);found=None
                    for item in bpy.context.evaluated_depsgraph_get().object_instances:
                        if item.is_instance and item.parent and item.parent.original==instance and item.object.original==obj:
                            a,b,hints=_segment_geometry(item.object,binding['names'],item.matrix_world)
                            found=(center_of_mass(a,b,weights,fractions)[1],am.segment_orientations(a,b,hints),am.segment_principal_inertia(a,b,radii));break
                    if found is None:raise ValueError('Native character instance is missing during angular checking')
                    displayed.append(found[0]);displayed_orientations.append(found[1]);displayed_principal.append(found[2])
                    rewind();at_checkpoint=True
                    yield dict(phase='Checking angular momentum',frame=frame,total=len(row['angular_frames']));guard();at_checkpoint=False
                actual_data=am.measure(displayed,weights,(np.asarray(row['angular_frames'])-row['start'])*dt,displayed_orientations,displayed_principal)
                variation,target_momentum=am.variation(actual_data['momentum']);before_variation=row['angular']['before_variation']
                before_orbital=am.variation(row['angular']['before_orbital_momentum'])[0];after_orbital=am.variation(actual_data['orbital_momentum'])[0]
                before_spin=am.variation(row['angular']['before_spin_momentum'])[0];after_spin=am.variation(actual_data['spin_momentum'])[0]
                metric['angular_momentum']=dict(model='artist-mass solid ellipsoid segments; orbital plus intrinsic spin',before_variation=before_variation,after_variation=variation,improvement=0. if before_variation<=1e-12 else 1-variation/before_variation,before_orbital_variation=before_orbital,after_orbital_variation=after_orbital,before_spin_variation=before_spin,after_spin_variation=after_spin,target=target_momentum.tolist(),peak_correction_radians=row['angular']['peak_angle'],effective_strength=row['angular']['effective_strength'],endpoint_rotation_error=row['angular']['endpoint_error'])
            if row.get('collision'):
                collision=row['collision'];before_penetration=[];after_penetration=[]
                check_frames=sorted(set(collision['times'])|{float(frame) for frame in np.arange(row['start']+.137,row['end'],.25)})
                for frame in check_frames:
                    frame_at(frame);found=None
                    for item in bpy.context.evaluated_depsgraph_get().object_instances:
                        if item.is_instance and item.parent and item.parent.original==instance and item.object.original==obj:
                            a,b,hints=_segment_geometry(item.object,binding['names'],item.matrix_world)
                            displayed_centers=center_of_mass(a,b,weights,fractions)[1];displayed_orientations=am.segment_orientations(a,b,hints);lengths=np.linalg.norm(b-a,axis=1)
                            projected=displayed_centers-((displayed_centers-collision_point)@collision_normal)[:,None]*collision_normal
                            inside=[contacts._inside_surface(Vector(point),collision_triangles) for point in projected]
                            found=cm.correction(displayed_centers,displayed_orientations,lengths,radii,collision_point,collision_normal,collision['clearance'],0.,inside)
                            correction=collision_value(row,frame);before=cm.correction(displayed_centers-correction,displayed_orientations,lengths,radii,collision_point,collision_normal,collision['clearance'],0.,inside);break
                    if found is None:raise ValueError('Native character instance is missing during collision checking')
                    before_penetration.append(before['required_lift']);after_penetration.append(found['required_lift'])
                    expected=max(0.,before['required_lift']-float(np.dot(correction,collision_normal)))
                    if abs(found['required_lift']-expected)>row['scale']*2e-4:
                        raise ValueError('Planar collision response fails its editable translation curve')
                    if row['collision_strength']>=1.-1e-8 and found['required_lift']>row['scale']*2e-4:
                        raise ValueError('Planar collision response fails its predicted clearance; reduce strength or edit the flight')
                    rewind();at_checkpoint=True
                    yield dict(phase='Checking planar collision response',frame=frame,total=len(check_frames));guard();at_checkpoint=False
                metric['collision_response']=dict(model='whole-character translation against static plane using artist-radius solid ellipsoid segments',surface=collision['surface'],strength=row['collision_strength'],clearance_world=collision['clearance'],sample_frames=.25,
                    interpolation_safety_margin_world=collision['safety_margin'],verification_phase_offset_frames=.137,max_penetration_before=max(before_penetration,default=0.),max_penetration_after=max(after_penetration,default=0.),participating_segments=max(collision['participants'],default=0),priority_poses_preserved=True)
            report_rows.append(metric)
        transition_metrics=[]
        def displayed_com(frame):
            frame_at(frame)
            for item in bpy.context.evaluated_depsgraph_get().object_instances:
                if item.is_instance and item.parent and item.parent.original==instance and item.object.original==obj:
                    heads=np.array([item.matrix_world@item.object.pose.bones[n].head for n in binding['names']])
                    tails=np.array([item.matrix_world@item.object.pose.bones[n].tail for n in binding['names']])
                    a=np.array([heads[i] for _,i,j,_ in support.SEGMENTS])
                    b=np.array([heads[j] if j is not None else tails[i] for _,i,j,_ in support.SEGMENTS])
                    return center_of_mass(a,b,weights,fractions)[0]
            raise ValueError('Native character instance is missing during transition checking')
        for span in transitions:
            boundary=span['start'] if span['landing'] else span['end'];h=span['h'];velocity_h=span['velocity_h']
            def velocity(side):
                return side*(-3*displayed_com(boundary)+4*displayed_com(boundary+side*velocity_h)-displayed_com(boundary+side*2*velocity_h))/(2*velocity_h*dt)
            def acceleration(side):
                return (2*displayed_com(boundary)-5*displayed_com(boundary+side*h)+4*displayed_com(boundary+side*2*h)-displayed_com(boundary+side*3*h))/(h*dt)**2
            positive_velocity=velocity(1);rewind();at_checkpoint=True
            yield dict(phase='Checking COM forward speed',frame=boundary,total=len(transitions));guard();at_checkpoint=False
            negative_velocity=velocity(-1);jump_vector=positive_velocity-negative_velocity;full_jump=float(np.linalg.norm(jump_vector))
            if 'collision_normal' in span:
                normal_jump=float(np.dot(jump_vector,span['collision_normal']));jump=float(np.linalg.norm(jump_vector-normal_jump*span['collision_normal']))
            else:normal_jump=None;jump=full_jump
            if jump/span['scale']>.02 or (span['before_jump']/span['scale']>.02 and jump>span['before_jump']*.1):
                index=curve_rows.index(span);curves=w.action_curves(instance.animation_data.action,getattr(instance.animation_data,'action_slot',None));side=1 if span['landing'] else -1
                measured=[]
                for axis in range(3):
                    fc=curves.find(f'["b4ml_residual_{index}_{axis}"]')
                    measured.append(float(side*(-3*fc.evaluate(boundary)+4*fc.evaluate(boundary+side*velocity_h)-fc.evaluate(boundary+side*2*velocity_h))/(2*velocity_h*dt)))
                raise ValueError(f'Velocity transition fails boundary continuity ({jump/span["scale"]:.6g} tangential body units/s, {full_jump/span["scale"]:.6g} full, after {span["before_jump"]/span["scale"]:.6g}; landing={span["landing"]}; match_acceleration={span["match_acceleration"]}; requested={span["velocity"].tolist()}; measured_curve={measured}; acceleration={span["acceleration"].tolist()}); lengthen its span or retime the flight')
            rewind();at_checkpoint=True
            yield dict(phase='Checking COM boundary speed',frame=boundary,total=len(transitions));guard();at_checkpoint=False
            # Also inspect intermediate displayed COM and the join to untouched motion.
            max_error=0.
            for u in (0.,.137,.5,.863,1.):
                frame=span['start']+(span['end']-span['start'])*u
                correction=fm.transition_c2_values(span['spline'],[u])[0] if span['match_acceleration'] else fm.transition_offset([u],span['duration'],span['velocity'],span['landing'])[0]
                wanted=source_com(frame)+correction
                max_error=max(max_error,float(np.linalg.norm(displayed_com(frame)-wanted))/span['scale'])
            rewind();at_checkpoint=True
            yield dict(phase='Checking COM transition path',frame=boundary,total=len(transitions));guard();at_checkpoint=False
            outer=span['end'] if span['landing'] else span['start'];side=-1 if span['landing'] else 1
            def displacement(frame):return displayed_com(frame)-source_com(frame)
            outer_speed=float(np.linalg.norm(side*(-3*displacement(outer)+4*displacement(outer+side*velocity_h)-displacement(outer+side*2*velocity_h))/(2*velocity_h*dt)))
            outer_acceleration=float(np.linalg.norm((2*displacement(outer)-5*displacement(outer+side*h)+4*displacement(outer+side*2*h)-displacement(outer+side*3*h))/(h*dt)**2)) if span['match_acceleration'] else None
            rewind();at_checkpoint=True
            yield dict(phase='Checking COM outer boundary',frame=outer,total=len(transitions));guard();at_checkpoint=False
            if span['match_acceleration']:
                positive_acceleration=acceleration(1);rewind();at_checkpoint=True
                yield dict(phase='Checking COM forward acceleration',frame=boundary,total=len(transitions));guard();at_checkpoint=False
                acceleration_jump_vector=positive_acceleration-acceleration(-1);full_acceleration_jump=float(np.linalg.norm(acceleration_jump_vector))
                if 'collision_normal' in span:
                    normal_acceleration_jump=float(np.dot(acceleration_jump_vector,span['collision_normal']));acceleration_jump=float(np.linalg.norm(acceleration_jump_vector-normal_acceleration_jump*span['collision_normal']))
                else:normal_acceleration_jump=None;acceleration_jump=full_acceleration_jump
            else:acceleration_jump=full_acceleration_jump=normal_acceleration_jump=None
            if max_error>2e-4 or outer_speed/span['scale']>.02 or (outer_acceleration is not None and outer_acceleration/span['scale']>.1):
                raise ValueError(f'Velocity transition fails displayed COM or outer continuity (path={max_error:.6g} body units; outer speed={outer_speed/span["scale"]:.6g} body units/s; outer acceleration={None if outer_acceleration is None else outer_acceleration/span["scale"]} body units/s^2; landing={span["landing"]}); lengthen its span')
            if acceleration_jump is not None and (acceleration_jump/span['scale']>.1 or (span['before_acceleration_jump']/span['scale']>.1 and acceleration_jump>span['before_acceleration_jump']*.1)):
                raise ValueError(f'Acceleration transition fails boundary continuity ({acceleration_jump/span["scale"]:.6g} body units/s^2 after {span["before_acceleration_jump"]/span["scale"]:.6g}; outer={outer_acceleration/span["scale"]:.6g}); lengthen its span or retime the flight')
            transition_metric=dict(start=span['start'],end=span['end'],landing=span['landing'],match_acceleration=span['match_acceleration'],before_jump=span['before_jump'],before_full_jump=span['before_full_jump'],after_jump=jump,after_full_jump=full_jump,normalized_jump=jump/span['scale'],normalized_full_jump=full_jump/span['scale'],normal_impulse_jump=normal_jump,before_acceleration_jump=span['before_acceleration_jump'],before_full_acceleration_jump=span['before_full_acceleration_jump'],after_acceleration_jump=acceleration_jump,after_full_acceleration_jump=full_acceleration_jump,normalized_acceleration_jump=None if acceleration_jump is None else acceleration_jump/span['scale'],normalized_full_acceleration_jump=None if full_acceleration_jump is None else full_acceleration_jump/span['scale'],normal_impulse_acceleration_jump=normal_acceleration_jump,max_com_error=max_error,outer_speed_correction=outer_speed,outer_acceleration_correction=outer_acceleration,velocity_correction=span['velocity'].tolist(),acceleration_correction=span['acceleration'].tolist(),collision_impulse_velocity=span['collision_impulse_velocity'].tolist(),collision_impulse_acceleration=span['collision_impulse_acceleration'].tolist(),velocity_sample_step_frames=velocity_h,acceleration_sample_step_frames=h)
            if 'collision_normal' in span:
                row=intervals[span['flight_index']];penetration=[];participants=[]
                limb_bindings={item['id']:item for item in p.bindings(obj)[2]}
                held=[contact for contact in raw['contacts'] if contact['strength']>0 and abs(contact['start']-row['end'])<=1e-8 and contact['end']>=span['end']-1e-8 and contact['limb'] in ('leg-L','leg-R')]
                if row.get('contact_impulse_strength',0.) and not held:
                    raise ValueError('Landing contact impulse requires a held foot contact beginning at landing and covering the transition')
                check_frames=sorted({float(frame) for frame in np.arange(span['start'],span['end']+1e-7,.25)}|{span['start'],span['end']})
                for frame in check_frames:
                    frame_at(frame);found=None
                    for item in bpy.context.evaluated_depsgraph_get().object_instances:
                        if item.is_instance and item.parent and item.parent.original==instance and item.object.original==obj:
                            values=[]
                            for contact in held:
                                limb=limb_bindings[contact['limb']];point=np.asarray(item.matrix_world@item.object.pose.bones[limb['joints'][2]].head,dtype=float)
                                projected=point-float(np.dot(point-collision_point,collision_normal))*collision_normal
                                if contacts._inside_surface(Vector(projected),collision_triangles):values.append(max(0.,-float(np.dot(point-collision_point,collision_normal))))
                            found=dict(required_lift=max(values,default=0.),participating_segments=len(values));break
                    if found is None:raise ValueError('Native character instance is missing during contact-transition checking')
                    penetration.append(found['required_lift']);participants.append(found['participating_segments'])
                    rewind();at_checkpoint=True
                    yield dict(phase='Checking contact transition clearance',frame=frame,total=len(check_frames));guard();at_checkpoint=False
                transition_metric['collision_impulse']=dict(model='frictionless bounded normal impulse with tangential continuity; held-foot correction remains delegated to the following contact stage',surface=collision_surface,strength=span['impulse_strength'],normal=span['collision_normal'].tolist(),absorbed_velocity=span['collision_impulse_velocity'].tolist(),absorbed_acceleration=span['collision_impulse_acceleration'].tolist(),pre_contact_max_penetration=max(penetration,default=0.),pre_contact_max_penetration_body_fraction=max(penetration,default=0.)/span['scale'],participating_contacts=max(participants,default=0),priority_poses_preserved=True,contact_stage_required=True)
            transition_metrics.append(transition_metric)
            rewind();at_checkpoint=True
            yield dict(phase='Checking COM transitions',frame=boundary,total=len(transitions));guard();at_checkpoint=False
        for frame in sorted(set(priorities)|{r['start']-.25 for r in curve_rows}|{r['end']+.25 for r in curve_rows}):
            if any(r['start']<frame<r['end'] for r in curve_rows) and frame not in priorities:continue
            frame_at(frame)
            angle=2*math.acos(min(1.,abs(float(instance.matrix_world.to_quaternion().w))))
            if np.linalg.norm(instance.location)>2e-5 or angle>2e-5:raise ValueError('Native flight changes a priority pose or outside interval')
            rewind();at_checkpoint=True
            yield dict(phase='Checking authored flight boundaries',frame=frame,total=len(priorities));guard();at_checkpoint=False
        rewind();guard()
        if collision_intervals:backend_name='native_instance_com_angular_collision_v3' if angular_rows else 'native_instance_com_collision_v1'
        elif contact_impulse_intervals:backend_name='native_instance_com_angular_contact_impulse_v4' if angular_rows else 'native_instance_com_contact_impulse_v4'
        else:backend_name='native_instance_com_angular_v2' if angular_rows else 'native_instance_com_v1'
        report=dict(backend=backend_name,intervals=report_rows,transitions=transition_metrics,max_before=max_before,max_after=max_after,relative_basis_error=max_basis,rigid_translation_error=max_rigid,elapsed_ms=(time.perf_counter()-began)*1000,gravity=raw['gravity'],fps=raw['fps'],fps_base=raw['fps_base'],priority_poses=len(priorities),fit_interval_frames=.5,angular_sample_frames=.25 if angular_rows else None,collision_sample_frames=.25 if collision_intervals else None,units='position errors normalized by trunk length; acceleration in world units/s^2; angular momentum from artist-mass finite ellipsoid segments; collision clearance in world units')
        state.flight_input=action;state.flight_output=action;state.flight_metrics=json.dumps(report,allow_nan=False);instance['b4ml_flight_metrics']=state.flight_metrics
        state.status='Native COM flight preview ready; original rig channels preserved';committed=True
        return report
    finally:
        # At a yielded boundary the host belongs to the animator again. Preserve
        # newer input on direct cancellation as well as on guard rejection.
        if at_checkpoint:
            current=p._frame(scene)
            pose=w.raw_pose(obj);modes=rs.mode_values(obj)
            if current!=initial_frame:return_frame=current
        if not committed and instance is not None and m.find(obj):m.restore(obj)
        rewind()
        if at_checkpoint:rs.restore_values(obj,modes);p._update(obj)
        if return_frame!=initial_frame:contacts._frame(scene,return_frame)
        if at_checkpoint:w.restore_pose(obj,pose);p._update(obj)
