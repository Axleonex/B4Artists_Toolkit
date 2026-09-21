"""Read-only evaluated humanoid mass/support adapter and explicit saved settings.
SPDX-License-Identifier: GPL-2.0-or-later
"""
import json
import math
import time
import numpy as np
import bpy
from mathutils import Vector
from . import body_solver,posing
from . import support_math as sm

# An artist-editable starting distribution, NOT measured anthropometry.
# Each segment uses two evaluated endpoints, with an editable center fraction.
SEGMENTS=[('Lower Trunk',0,1,12.),('Middle Trunk',1,2,12.),
          ('Upper Trunk',2,3,18.),('Neck',3,4,2.),('Head',4,None,8.)]
for side,start in (('Left',5),('Right',8)):
    SEGMENTS.extend([(side+' Upper Arm',start,start+1,4.),(side+' Forearm',start+1,start+2,2.),
                     (side+' Hand',start+2,None,1.)])
for side,start in (('Left',11),('Right',14)):
    SEGMENTS.extend([(side+' Thigh',start,start+1,10.),(side+' Shin',start+1,start+2,5.),
                     (side+' Foot',start+2,None,2.)])

# Finite-volume starting estimates for the angular solver. Values are ellipsoid
# radius / evaluated segment length and remain directly editable by the artist.
INERTIA_RADII={'Lower Trunk':.34,'Middle Trunk':.32,'Upper Trunk':.30,'Neck':.20,'Head':.45}
for side in ('Left','Right'):
    INERTIA_RADII.update({side+' Upper Arm':.16,side+' Forearm':.14,side+' Hand':.24,
        side+' Thigh':.19,side+' Shin':.15,side+' Foot':.23})


def initialize(obj):
    body_solver.mapping(obj,writable=False) # Fail before changing saved settings.
    if obj.b4ml.mass_segments:return
    for name,a,b,weight in SEGMENTS:
        item=obj.b4ml.mass_segments.add();item.name=name;item.weight=weight;item.fraction=.5;item.inertia_radius=INERTIA_RADII[name]


def sample(obj,depsgraph):
    binding=body_solver.mapping(obj,writable=False)
    evaluated=obj.evaluated_get(depsgraph);names=binding['names'];world=evaluated.matrix_world
    heads=np.array([world@evaluated.pose.bones[n].head for n in names])
    tails=np.array([world@evaluated.pose.bones[n].tail for n in names])
    starts=[];ends=[]
    for name,a,b,weight in SEGMENTS:
        starts.append(heads[a]);ends.append(heads[b] if b is not None else tails[a])
    return binding,evaluated,np.array(starts),np.array(ends)


def analyze(obj,scene,depsgraph):
    started=time.perf_counter();state=obj.b4ml
    if state.body_running or state.contact_running or state.flight_running or state.secondary_running:raise ValueError('Wait for or cancel the active solve')
    items=list(state.mass_segments)
    if [i.name for i in items]!=[s[0] for s in SEGMENTS]:
        raise ValueError('Initialize a complete humanoid mass model before analysis')
    binding,evaluated,starts,ends=sample(obj,depsgraph)
    from . import workflow as w
    transform=w.motion_layer.transform(obj)
    starts=np.array([transform@Vector(point) for point in starts]);ends=np.array([transform@Vector(point) for point in ends])
    displayed=w.display_world(obj)
    com,centers,weights=sm.center_of_mass(starts,ends,[i.weight for i in items],[i.fraction for i in items])
    plane=sm.vector(state.support_plane_point);n,u,v=sm.plane_basis(state.support_plane_normal)
    tolerance=state.support_tolerance;frame=scene.frame_current+scene.frame_subframe
    limbs={r['id']:r for r in posing.bindings(obj)[2]};points=[];accepted=[];excluded=[]
    for index,item in enumerate(state.contacts):
        if not item.enabled or not item.use_support:continue
        reason=None
        if not all(math.isfinite(x) for x in (item.start,item.end,item.strength)) or item.start>item.end:
            raise ValueError('Invalid support contact interval')
        if not item.start<=frame<=item.end:reason='outside hold interval'
        elif item.strength<1.-1e-6:reason='contact strength below one'
        row=limbs.get(item.limb)
        if row is None:raise ValueError('Unsupported support limb')
        actual=sm.vector((displayed@evaluated.pose.bones[row['joints'][2]].matrix)@Vector(item.offset))
        point=sm.vector(item.point);drift=float(np.linalg.norm(actual-point))
        if reason is None and drift>tolerance:reason='evaluated contact drift exceeds tolerance'
        captured=np.asarray(item.rotation,dtype=float)
        q=np.asarray((displayed@evaluated.pose.bones[row['joints'][2]].matrix).to_quaternion(),dtype=float)
        if not np.isfinite(captured).all() or np.linalg.norm(captured)<1e-12:
            raise ValueError('Support contact rotation must be a valid quaternion')
        angle=2*math.acos(min(1.,abs(float(np.dot(captured/np.linalg.norm(captured),q/np.linalg.norm(q))))))
        if reason is None and angle>state.support_rotation_tolerance:reason='evaluated contact rotation exceeds tolerance'

        if reason is None and abs(float(np.dot(point-plane,n)))>tolerance:reason='contact off support plane'
        if reason:
            excluded.append(dict(index=index,limb=item.limb,reason=reason,drift=drift,rotation_error=angle));continue
        # Snap the tiny allowed plane error, keeping all patch vertices exactly coplanar.
        center=point-n*np.dot(point-plane,n)
        patch=sm.patch_vertices(center,n,item.support_width,item.support_length,item.support_heading)
        points.extend(patch);accepted.append(dict(index=index,limb=item.limb,drift=drift,rotation_error=angle))
    gravity=tuple(scene.gravity) if scene.use_gravity else (0.,0.,0.)
    result=sm.support_analysis(com,points,plane,n,gravity,tolerance)
    result.update(schema=1,frame=frame,rig=obj.name,profile=binding['profile'],
        mass_model='Artist-authored segment approximation; not measured anatomy',
        segments=[dict(name=item.name,weight=float(weight),fraction=float(item.fraction),inertia_radius=float(item.inertia_radius),
            start=a.tolist(),end=b.tolist(),center=center.tolist())
            for item,weight,a,b,center in zip(items,weights,starts,ends,centers)],
        contacts=accepted,excluded_contacts=excluded,gravity=list(gravity),
        seconds=time.perf_counter()-started)
    return result


def snapshot(obj,scene,depsgraph):
    result=analyze(obj,scene,depsgraph)
    obj.b4ml.support_report=json.dumps(result,allow_nan=False)
    return result
