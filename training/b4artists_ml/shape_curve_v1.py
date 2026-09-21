"""Isolated procedural FCurve interpolation experiment; not a runtime feature.
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
        if x[0]!=first or x[-1]!=last or np.any((x<first)|(x>last)):raise ValueError('Research adapter requires an isolated generated span')
        left,right=handles(x,y);plans[key]=(xy,left,right)
    for path in quats:
        if not all((path,i) in plans for i in range(4)):raise ValueError('Complete quaternion curves required')
        times=[plans[(path,i)][0][:,0] for i in range(4)]
        if not all(np.array_equal(t,times[0]) for t in times):raise ValueError('Quaternion sample times disagree')
        q=np.stack([plans[(path,i)][0][:,1] for i in range(4)],axis=-1);norm=np.linalg.norm(q,axis=-1)
        if np.any(norm<1e-8) or np.any(np.sum(q[:-1]*q[1:],axis=-1)<=0):raise ValueError('Quaternion signs or turns need explicit continuous representation')
    candidate=action.copy();candidate.use_fake_user=False;candidate.name=action.name+' Shape curves'
    try:
        slot=next(s for s in candidate.slots if s.identifier==identifier);curves=w.action_curves(candidate,slot)
        for key,(xy,left,right) in plans.items():
            fc=curves.find(key[0],index=key[1])
            for i,k in enumerate(fc.keyframe_points):
                k.handle_left_type='FREE';k.handle_right_type='FREE';k.interpolation='BEZIER';k.handle_left=left[i];k.handle_right=right[i]
            fc.keyframe_points.sort();fc.keyframe_points.handles_recalc()
            if not np.array_equal(np.array([list(k.co) for k in fc.keyframe_points]),xy):raise ValueError('Key sample changed')
        return candidate,dict(curves=len(plans),keys=sum(len(v[0]) for v in plans.values()),quaternion_groups=len(quats),authored_coordinates_unchanged=True,method='componentwise harmonic cubic; procedural')
    except BaseException:
        if candidate.users==0:bpy.data.actions.remove(candidate)
        raise
