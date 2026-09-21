"""Explicit segment COM and geometric static support estimates; no host mutation.
SPDX-License-Identifier: GPL-2.0-or-later
"""
import math
import numpy as np


def vector(value):
    a=np.asarray(value,dtype=float)
    if a.shape!=(3,) or not np.isfinite(a).all():
        raise ValueError('Expected a finite world-space vector')
    return a


def center_of_mass(starts,ends,masses,fractions):
    a=np.asarray(starts,dtype=float);b=np.asarray(ends,dtype=float)
    m=np.asarray(masses,dtype=float);f=np.asarray(fractions,dtype=float)
    if (a.ndim!=2 or a.shape[1:]!=(3,) or not len(a) or b.shape!=a.shape
        or m.shape!=(len(a),) or f.shape!=m.shape
        or not all(np.isfinite(v).all() for v in (a,b,m,f))
        or np.any(m<0) or np.any((f<0)|(f>1)) or not np.any(m>0)):
        raise ValueError('Mass model needs finite nonnegative weights and segment fractions in [0, 1]')
    # Normalize by maximum first, avoiding overflow for large valid relative weights.
    weights=m/m.max();weights/=weights.sum()
    centers=a*(1-f[:,None])+b*f[:,None]
    com=(centers*weights[:,None]).sum(axis=0)
    if not np.isfinite(com).all():raise ValueError('Mass model exceeds numeric range')
    return com,centers,weights


def plane_basis(normal):
    n=vector(normal);length=float(np.linalg.norm(n))
    if not math.isfinite(length) or length<1e-12:raise ValueError('Support normal must be nonzero')
    n=n/length
    # Project world X, with world Y fallback when X is nearly parallel to the normal.
    seed=np.array((1.,0.,0.)) if abs(n[0])<.9 else np.array((0.,1.,0.))
    u=seed-n*np.dot(seed,n);u/=np.linalg.norm(u)
    return n,u,np.cross(n,u)


def patch_vertices(center,normal,width,length,heading):
    if not all(math.isfinite(v) for v in (width,length,heading)) or min(width,length)<0:
        raise ValueError('Support patch dimensions must be finite and nonnegative')
    n,u,v=plane_basis(normal);c=vector(center)
    x=math.cos(heading)*u+math.sin(heading)*v
    y=-math.sin(heading)*u+math.cos(heading)*v
    return np.array([c+sx*width*.5*x+sy*length*.5*y for sx,sy in ((-1,-1),(1,-1),(1,1),(-1,1))])


def hull_2d(points):
    points=sorted(set(map(tuple,points)))
    if len(points)<2:return np.asarray(points,dtype=float).reshape(-1,2)
    def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
    def half(seq):
        out=[]
        for pt in seq:
            while len(out)>1 and cross(out[-2],out[-1],pt)<=0:out.pop()
            out.append(pt)
        return out
    return np.array(half(points)[:-1]+half(points[::-1])[:-1],dtype=float)


def support_analysis(com,points,plane_point,normal,gravity,tolerance=1e-5):
    c=vector(com);origin=vector(plane_point);g=vector(gravity);n,u,v=plane_basis(normal)
    pts=np.asarray(points,dtype=float).reshape(-1,3)
    if not np.isfinite(pts).all() or not math.isfinite(tolerance) or tolerance<=0:
        raise ValueError('Support points and positive tolerance must be finite')
    result=dict(status='NO_SUPPORT',com=c.tolist(),projection=None,margin=None,hull=[],
                plane_height=float(np.dot(c-origin,n)),normal=n.tolist(),static_only=True)
    norm=float(np.linalg.norm(g))
    if not math.isfinite(norm):raise ValueError('Gravity exceeds numeric range')
    if norm<1e-12:result['status']='ZERO_GRAVITY';return result
    direction=g/norm;denom=float(np.dot(direction,n))
    if denom>=-1e-8:result['status']='GRAVITY_NOT_INTO_PLANE';return result
    projection=c-direction*np.dot(c-origin,n)/denom
    result['projection']=projection.tolist()
    result['gravity_normal_aligned']=bool(np.linalg.norm(direction+n)<1e-6)
    if result['plane_height'] < -tolerance:
        result['status']='COM_BELOW_PLANE';return result
    if not len(pts):return result
    if np.max(np.abs((pts-origin)@n))>tolerance:
        raise ValueError('Support points must lie on the authored plane within tolerance')
    # Work relative to the first point to reduce cancellation far from world origin.
    anchor=pts[0];coords=np.column_stack(((pts-anchor)@u,(pts-anchor)@v))
    hull=hull_2d(coords);q=np.array((np.dot(projection-anchor,u),np.dot(projection-anchor,v)))
    result['hull']=(anchor+hull[:,0,None]*u+hull[:,1,None]*v).tolist()
    distances=[];inside=len(hull)>=3
    for i,a in enumerate(hull):
        b=hull[(i+1)%len(hull)];edge=b-a;squared=float(edge@edge)
        t=np.clip(float((q-a)@edge)/squared,0.,1.) if squared else 0.
        distances.append(float(np.linalg.norm(q-(a+t*edge))))
        if len(hull)>=3 and edge[0]*(q-a)[1]-edge[1]*(q-a)[0]<0:inside=False
    distance=min(distances)
    result['margin']=distance if inside else -distance
    if len(hull)<3:result['status']='DEGENERATE_SUPPORT'
    elif distance<=tolerance:result['status']='SUPPORT_BOUNDARY'
    elif not inside:result['status']='OUTSIDE_SUPPORT'
    else:result['status']='INSIDE_SUPPORT'
    # Inclined planes require friction/contact-force analysis, which is not provided.
    if not result['gravity_normal_aligned']:result['status']='INCLINED_GEOMETRY_ONLY'
    return result
