"""Research-only contact solver validates cubic curves before publishing.
Derived from runtime correction_steps; tolerances and four-refinement cap unchanged.
No runtime monkeypatching or addon promotion.
"""
import math,json,time,bpy
from b4artists_ml.contacts import (w,p,rs,cm,_flight_intervals,rows,_action_signature,_frame,_solve_limb,_point,_angle,Vector,Quaternion)
from shape_curve_v4 import smooth_copy

def correction_steps(obj,scene,_extra_frames=(),_refinements=(),_started=None):
    state=obj.b4ml;w.require_rig(obj);w._reject_nla(obj)
    if state.flight_running:raise ValueError('Finish flight correction first')
    if state.body_payload or state.posing_payload:raise ValueError('Finish assisted posing first')
    previous=state.candidate_action
    if not previous or not obj.animation_data or obj.animation_data.action!=previous:raise ValueError('Generate and select an interpolation candidate first')
    if state.contact_output==previous and not state.contact_input:raise ValueError('Retained contact input is missing; generate a new candidate')
    original=state.contact_input if state.contact_output==previous and state.contact_input else previous
    anchors=w.read_anchors(obj);first,last=anchors[0][0],anchors[-1][0]
    flight_intervals=_flight_intervals(obj,anchors,rows(obj))
    request=cm.validate(rows(obj),first,last);frames=cm.sample_frames(request,[f for f,_ in anchors],first,last)
    if any(not math.isfinite(f) or not first<=f<=last for f in _extra_frames):raise ValueError('Invalid adaptive contact sample')
    frames=sorted(set(frames)|set(_extra_frames))
    original_frame=p._frame(scene);original_pose=w.raw_pose(obj);original_modes=rs.mode_values(obj);slot=w._slot(obj.animation_data)
    rest=w._rest_signature(obj);request_signature=rows(obj)
    w.assign_action(obj,original,slot)
    try:signature=_action_signature(obj)
    finally:w.assign_action(obj,previous,slot)
    check_frames=sorted(set(frames)|{a+(b-a)*t for a,b in zip(frames,frames[1:]) for t in (.25,.5,.75)});key_frames=set(frames)
    _,_,limbs=p.bindings(obj);mapping={r['id']:r for r in limbs};selected={r['limb'] for r in request}
    names={n for limb in selected for n in mapping[limb]['fk']}
    if not names.issubset(anchors[0][1]['pose']):raise ValueError('Capture all three controls of each contact limb in every anchor')
    if len(frames)*len(names)*4>w.MAX_KEYS:raise ValueError('Contact correction exceeds the key budget')
    intervals={name:[(max(first,r['start']-r['blend']),min(last,r['end']+r['blend'])) for r in request if name in mapping[r['limb']]['fk']] for name in names}
    samples={};expected={};priority={f for f,_ in anchors};priority_matrices={};candidate=None;committed=False
    started=time.perf_counter() if _started is None else _started;max_before=0.;max_after=0.;drift_before=0.;drift_after=0.;orientation_error=0.;checks=0
    def restore_input():
        w.assign_action(obj,previous,slot);_frame(scene,original_frame);w.restore_pose(obj,original_pose);rs.restore_values(obj,original_modes);p._update(obj)
    def guard():
        if state.candidate_action!=previous or obj.animation_data.action not in (previous,candidate):raise ValueError('Candidate changed during contact correction')
        if rows(obj)!=request_signature or w._rest_signature(obj)!=rest:raise ValueError('Contacts or rig changed during correction')
        if _flight_intervals(obj,anchors,request_signature)!=flight_intervals:raise ValueError('Generated flight changed during contact correction')
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
                row=mapping[r['limb']];matrix=w.display_world(obj)@obj.pose.bones[row['joints'][2]].matrix
                target=(matrix@Vector(r['offset'])).lerp(Vector(r['point']),amount)
                desired=matrix.to_quaternion().slerp(Quaternion(r['rotation']),amount) if r['lock_rotation'] else matrix.to_quaternion()
                reference=max(sum((obj.pose.bones[row['joints'][i+1]].head-obj.pose.bones[row['joints'][i]].head).length for i in (0,1))*w.display_world(obj).to_scale().x,1e-8)
                error=(_point(obj,row,r['offset'])-target).length/reference;max_before=max(max_before,error)
                if r['start']<=frame<=r['end']:drift_before=max(drift_before,(_point(obj,row,r['offset'])-Vector(r['point'])).length/reference)
                if frame in priority:
                    if error>2e-4 or _angle(matrix.to_quaternion(),desired)>.001:raise ValueError(f'Contact conflicts with priority pose at frame {frame:g}: '+r['limb'])
                elif frame in key_frames:
                    key=(r['limb'],r['start'],r['end'])
                    target,desired,pole_hints[key]=_solve_limb(obj,row,r,amount,pole_hints.get(key))
                expected[frame].append((row,r,target.copy(),desired.copy(),reference))
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
        # Validate the actual cubic output, so adaptive refinement sees its error.
        linear_candidate=candidate
        candidate,shape_report=smooth_copy(obj,linear_candidate,first,last)
        w.assign_action(obj,candidate,slot)
        if linear_candidate.users==0:bpy.data.actions.remove(linear_candidate)
        refine=[];failed_error=0.;failed_orientation=0.
        for frame in check_frames:
            _frame(scene,frame);p._update(obj)
            for row,r,target,desired,reference in expected[frame]:
                error=(_point(obj,row,r['offset'])-target).length/reference
                orientation=_angle((w.display_world(obj)@obj.pose.bones[row['joints'][2]].matrix).to_quaternion(),desired)
                if error>2e-4 or orientation>.001:
                    if frame in key_frames or len(_refinements)>=4:raise ValueError(f'Evaluated contact failed at frame {frame:g}: {row["id"]}, position={error:.6g}, orientation={orientation:.6g}')
                    refine.append(frame);failed_error=max(failed_error,error);failed_orientation=max(failed_orientation,orientation)
                max_after=max(max_after,error);orientation_error=max(orientation_error,orientation);checks+=1
                if r['start']<=frame<=r['end']:drift_after=max(drift_after,(_point(obj,row,r['offset'])-Vector(r['point'])).length/reference)
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
            report=yield from correction_steps(obj,scene,sorted(key_frames|set(refine)),history,started)
            committed=True;return report
        w.assign_action(obj,candidate,slot);_frame(scene,original_frame)
        report=dict(backend='research_shape_aware_contact_projection_v1',frames=len(frames),validation_frames=len(check_frames),contacts=len(request),checks=checks,max_before=max_before,max_after=max_after,elapsed_ms=(time.perf_counter()-started)*1000,priority_poses=len(priority),contact_drift_before=drift_before,contact_drift_after=drift_after,orientation_error_radians=orientation_error,sample_interval_frames=.125,validation_max_interval_frames=max(b-a for a,b in zip(check_frames,check_frames[1:])),position_units='fraction of evaluated two-segment limb length',adaptive_refinements=list(_refinements),bend_policy='input limb plane normal with transported straight-limb fallback')
        candidate['b4ml_contacts']=json.dumps(request,allow_nan=False);candidate['b4ml_contact_metrics']=json.dumps(report,allow_nan=False)
        state.candidate_action=candidate;state.contact_input=original;state.contact_output=candidate
        state.contact_metrics=json.dumps(report);state.status=f'Contact drift {drift_before:.3g} -> {drift_after:.3g}; fit error {max_after:.3g} limb units';committed=True
        # Keep the unmodified input as an editable alternative. It is never deleted.
        original.use_fake_user=True
        return report
    finally:
        if not committed:
            restore_input()
            if candidate and candidate.users==0:bpy.data.actions.remove(candidate)

def solve(obj,scene):
    steps=correction_steps(obj,scene)
    try:
        while True:
            try:next(steps)
            except StopIteration as done:return done.value
    finally:steps.close()
