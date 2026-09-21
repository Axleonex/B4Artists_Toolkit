"""Convex planar targets for explicit static balance assistance."""
import math
import numpy as np
from .support_math import hull_2d


def inset_hull(points,margin):
    points=np.asarray(points,dtype=float)
    if points.ndim!=2 or points.shape[1]!=2 or not np.isfinite(points).all():
        raise ValueError('Expected finite planar support vertices')
    if not math.isfinite(margin) or margin<0:raise ValueError('Support inset must be nonnegative')
    hull=hull_2d(points)
    if len(hull)<3:raise ValueError('Static balance needs a support area, not a point or line')
    result=hull.copy()
    for a,b in zip(hull,np.roll(hull,-1,axis=0)):
        edge=b-a;normal=np.array((-edge[1],edge[0]));normal/=np.linalg.norm(normal)
        boundary=float(normal@a)+margin;out=[]
        for p,q in zip(result,np.roll(result,-1,axis=0)):
            dp=float(normal@p)-boundary;dq=float(normal@q)-boundary
            if dp>=0:out.append(p)
            if (dp>=0)!=(dq>=0):out.append(p+(q-p)*(dp/(dp-dq)))
        result=np.asarray(out,dtype=float).reshape(-1,2)
        if len(result)<3:raise ValueError('Support inset leaves no usable area; reduce it')
    result=hull_2d(result)
    area=abs(float(np.sum(result[:,0]*np.roll(result[:,1],-1)-result[:,1]*np.roll(result[:,0],-1))))*.5
    span=float(np.ptp(hull,axis=0).max())
    if len(result)<3 or area<=max(span*span*1e-12,1e-24):raise ValueError('Support inset leaves no usable area; reduce it')
    return result


def closest_in_hull(point,hull):
    p=np.asarray(point,dtype=float);h=np.asarray(hull,dtype=float)
    if p.shape!=(2,) or not np.isfinite(p).all() or h.ndim!=2 or h.shape[1]!=2 or len(h)<3 or not np.isfinite(h).all():
        raise ValueError('Invalid planar point or convex support hull')
    inside=True;candidates=[]
    for a,b in zip(h,np.roll(h,-1,axis=0)):
        edge=b-a;length=float(edge@edge)
        if length<=0:continue
        if edge[0]*(p-a)[1]-edge[1]*(p-a)[0]<0:inside=False
        candidates.append(a+edge*np.clip(float((p-a)@edge)/length,0.,1.))
    if inside:return p.copy()
    return min(candidates,key=lambda v:float(np.linalg.norm(v-p)))


def capture_point(com,velocity,gravity,origin,normal,u,v):
    """Return the planar linear-inverted-pendulum capture point.

    This is a bounded procedural estimate, not a force or contact solver.  The
    authored velocity is world-space and the support normal points into the
    support plane, matching ``support_math``'s gravity convention.
    """
    com=np.asarray(com,dtype=float);velocity=np.asarray(velocity,dtype=float)
    origin=np.asarray(origin,dtype=float);normal=np.asarray(normal,dtype=float)
    u=np.asarray(u,dtype=float);v=np.asarray(v,dtype=float)
    if any(a.shape!=(3,) or not np.isfinite(a).all() for a in (com,velocity,origin,normal,u,v)):
        raise ValueError('Capture-point inputs must be finite world-space vectors')
    normal_length=float(np.linalg.norm(normal));gravity=np.asarray(gravity,dtype=float)
    if gravity.shape!=(3,) or not np.isfinite(gravity).all():
        raise ValueError('Capture-point gravity must be a finite world-space vector')
    gravity_length=float(np.linalg.norm(gravity))
    if normal_length<1e-12 or gravity_length<1e-12:
        raise ValueError('Capture-point balance requires nonzero gravity and support normal')
    normal=normal/normal_length;gravity_direction=gravity/gravity_length
    if np.linalg.norm(gravity_direction+normal)>1e-6:
        raise ValueError('Capture-point balance requires gravity normal into the support plane')
    height=float((com-origin)@normal)
    if not math.isfinite(height) or height<=0:
        raise ValueError('Capture-point balance requires the COM above the support plane')
    time_constant=math.sqrt(height/gravity_length)
    projection=np.array(((com-origin)@u,(com-origin)@v),dtype=float)
    planar_velocity=np.array((velocity@u,velocity@v),dtype=float)
    point=projection+planar_velocity*time_constant
    if not np.isfinite(point).all():raise ValueError('Capture point exceeds numeric range')
    return point,time_constant,height,planar_velocity
