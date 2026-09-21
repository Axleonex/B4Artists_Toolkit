"""Bounded procedural curve interpolation experiment; preserves unowned spans.
SPDX-License-Identifier: GPL-2.0-or-later
Keys are fixed. Harmonic tangents preserve scalar monotonicity and share one
incoming/outgoing derivative at interior keys. No learned parameters are used.
"""
import numpy as np
from b4artists_ml.temporal_math import harmonic_tangent

def tangents(times,values):
    x=np.asarray(times,dtype=float);y=np.asarray(values,dtype=float)
    if x.ndim!=1 or len(x)<2 or y.ndim<1 or y.shape[0]!=len(x) or not np.isfinite(x).all() or not np.isfinite(y).all() or np.any(np.diff(x)<=0):raise ValueError('Increasing finite samples required')
    h=np.diff(x);shape=(len(h),)+(1,)*(y.ndim-1);d=np.diff(y,axis=0)/h.reshape(shape);m=np.empty_like(y);m[0]=d[0];m[-1]=d[-1]
    for i in range(1,len(x)-1):m[i]=harmonic_tangent(d[i-1],d[i],h[i-1],h[i])
    if not np.isfinite(m).all():raise ValueError('Nonfinite tangent')
    return m

def handles(times,values):
    x=np.asarray(times,dtype=float);y=np.asarray(values,dtype=float)
    if y.ndim!=1:raise ValueError('One scalar FCurve required')
    m=tangents(x,y);h=np.diff(x);left=np.c_[x,y];right=left.copy()
    left[1:,0]-=h/3;left[1:,1]-=h*m[1:]/3
    right[:-1,0]+=h/3;right[:-1,1]+=h*m[:-1]/3
    return left,right

def smooth_copy(obj,action,first,last):
    from b4artists_ml import workflow as w
    import bpy
    rows=w.read_anchors(obj);owned=set();quats=[]
    for name,value in rows[0][1]['pose'].items():
        bone=obj.pose.bones[name]
        for prop in ('location','scale'):
            owned.update((bone.path_from_id(prop),i) for i in value['channels'][prop])
        if value['channels']['rotation']:
            if value['mode']=='AXIS_ANGLE':raise ValueError('Axis-angle continuity needs a separate adapter')
            prop='rotation_quaternion' if value['mode']=='QUATERNION' else 'rotation_euler';count=4 if prop=='rotation_quaternion' else 3
            owned.update((bone.path_from_id(prop),i) for i in range(count))
            if count==4:quats.append(bone.path_from_id(prop))
    identifier=w._slot(obj.animation_data);slot=next(s for s in action.slots if s.identifier==identifier);curves=w.action_curves(action,slot)
    plans={}
    for fc in curves:
        key=(fc.data_path,fc.array_index)
        if key not in owned:continue
        if fc.lock or fc.mute or len(fc.modifiers):raise ValueError('Curve is not freely editable')
        xy=np.array([list(k.co) for k in fc.keyframe_points]);x,y=xy.T
        indices=np.flatnonzero((x>=first)&(x<=last))
        if len(indices)<2 or x[indices[0]]!=first or x[indices[-1]]!=last:raise ValueError('Generated span endpoints must be keyed')
        selected=xy[indices];left,right=handles(selected[:,0],selected[:,1]);plans[key]=(selected,left,right,indices,xy)
    for path in quats:
        if not all((path,i) in plans for i in range(4)):raise ValueError('Complete quaternion curves required')
        times=[plans[(path,i)][0][:,0] for i in range(4)]
        if not all(np.array_equal(t,times[0]) for t in times):raise ValueError('Quaternion sample times disagree')
        q=np.stack([plans[(path,i)][0][:,1] for i in range(4)],axis=-1);norm=np.linalg.norm(q,axis=-1)
        if np.any(norm<1e-8) or np.any(np.sum(q[:-1]*q[1:],axis=-1)<=0):raise ValueError('Quaternion signs or turns need explicit continuous representation')
    candidate=action.copy();candidate.use_fake_user=False;candidate.name=action.name+' Shape curves'
    try:
        slot=next(s for s in candidate.slots if s.identifier==identifier);curves=w.action_curves(candidate,slot)
        for key,(selected,left,right,indices,xy) in plans.items():
            fc=curves.find(key[0],index=key[1])
            def state(k):return (tuple(k.co),tuple(k.handle_left),tuple(k.handle_right),k.handle_left_type,k.handle_right_type,k.interpolation)
            before=[state(k) for k in fc.keyframe_points]
            for local,index in enumerate(indices):
                k=fc.keyframe_points[int(index)]
                if local>0:k.handle_left_type='FREE';k.handle_left=left[local]
                if local<len(indices)-1:k.handle_right_type='FREE';k.handle_right=right[local];k.interpolation='BEZIER'
            # Coordinates and ordering are unchanged; all edited handles are
            # explicit FREE values. Recalculation would alter unowned AUTO sides.
            if not np.array_equal(np.array([list(k.co) for k in fc.keyframe_points]),xy):raise ValueError('Key sample changed')
            after=[state(k) for k in fc.keyframe_points]
            for i in range(len(before)):
                if i not in indices and before[i]!=after[i]:raise ValueError('Unowned key changed')
            i,j=int(indices[0]),int(indices[-1])
            if (i>0 and (before[i][1]!=after[i][1] or before[i][3]!=after[i][3])) or (j<len(before)-1 and (before[j][2]!=after[j][2] or before[j][4:]!=after[j][4:])):raise ValueError('Unowned boundary handle changed')
        return candidate,dict(curves=len(plans),keys=sum(len(v[0]) for v in plans.values()),quaternion_groups=len(quats),authored_coordinates_unchanged=True,method='componentwise harmonic cubic; procedural')
    except BaseException:
        if candidate.users==0:bpy.data.actions.remove(candidate)
        raise
