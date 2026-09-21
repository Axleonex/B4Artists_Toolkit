"""Known-anchor temporal windows; hidden poses never enter model features.
SPDX-License-Identifier: GPL-2.0-or-later
"""
from dataclasses import dataclass
import hashlib,json
import numpy as np
from bvh_data import parse_bvh
from context_data import NAMES,PARENTS
J=17;D=153


def rotation6(matrix):
    return np.concatenate((matrix[..., :,0],matrix[..., :,1]),axis=-1)


def rotation_matrix(values,fallback=None):
    values=np.asarray(values,dtype=float)
    if values.shape[-1]!=6 or not np.isfinite(values).all():raise ValueError('Expected finite 6D rotations')
    a=values[...,:3];b=values[...,3:];na=np.linalg.norm(a,axis=-1,keepdims=True)
    x=a/np.maximum(na,1e-12);y=b-x*np.sum(x*b,axis=-1,keepdims=True);ny=np.linalg.norm(y,axis=-1,keepdims=True)
    y/=np.maximum(ny,1e-12);matrix=np.stack((x,y,np.cross(x,y)),axis=-1)
    bad=(na[...,0]<1e-8)|(ny[...,0]<1e-8)
    if np.any(bad):
        base=np.broadcast_to(np.eye(3),matrix.shape) if fallback is None else np.broadcast_to(fallback,matrix.shape)
        matrix=np.where(bad[...,None,None],base,matrix)
    return matrix,bad


def quaternion(matrix):
    m=np.asarray(matrix,dtype=float);xx=m[...,0,0];yy=m[...,1,1];zz=m[...,2,2]
    lengths=np.sqrt(np.maximum(np.stack((1+xx+yy+zz,1+xx-yy-zz,1-xx+yy-zz,1-xx-yy+zz),axis=-1),0.))
    candidates=np.stack((np.stack((lengths[...,0]**2,m[...,2,1]-m[...,1,2],m[...,0,2]-m[...,2,0],m[...,1,0]-m[...,0,1]),axis=-1),
                         np.stack((m[...,2,1]-m[...,1,2],lengths[...,1]**2,m[...,1,0]+m[...,0,1],m[...,0,2]+m[...,2,0]),axis=-1),
                         np.stack((m[...,0,2]-m[...,2,0],m[...,1,0]+m[...,0,1],lengths[...,2]**2,m[...,2,1]+m[...,1,2]),axis=-1),
                         np.stack((m[...,1,0]-m[...,0,1],m[...,0,2]+m[...,2,0],m[...,2,1]+m[...,1,2],lengths[...,3]**2),axis=-1)),axis=-2)
    candidates/=2*np.maximum(lengths[..., :,None],1e-12)
    index=np.argmax(lengths,axis=-1);q=np.take_along_axis(candidates,index[...,None,None],axis=-2)[...,0,:]
    return q/np.linalg.norm(q,axis=-1,keepdims=True)


def quat_matrix(q):
    q=np.asarray(q,dtype=float);q=q/np.linalg.norm(q,axis=-1,keepdims=True);w,x,y,z=np.moveaxis(q,-1,0)
    return np.stack((1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w),2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w),2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)),axis=-1).reshape(q.shape[:-1]+(3,3))


def slerp(a,b,t):
    a=quaternion(a);b=quaternion(b);dot=np.sum(a*b,axis=-1,keepdims=True);b=np.where(dot<0,-b,b);dot=np.clip(abs(dot),0,1)
    theta=np.arccos(dot);denom=np.maximum(np.sin(theta),1e-12);t=np.asarray(t)[...,None,None]
    spherical=np.sin((1-t)*theta)/denom*a+np.sin(t*theta)/denom*b
    q=np.where(dot>.9995,a+(b-a)*t,spherical)
    return quat_matrix(q)


@dataclass
class TemporalMotion:
    points: np.ndarray
    rotations: np.ndarray
    frames: np.ndarray
    rest: np.ndarray
    reference: np.ndarray
    rest_pelvis_rotation: np.ndarray
    scale: float
    dt: float


def temporal_motion(motion,fps=30):
    if not np.isfinite(fps) or fps<=0:raise ValueError('Positive target frame rate required')
    points,rotations=motion.transforms();ids=[motion.names.index(n) for n in NAMES]
    points=points[:,ids];rotations=rotations[:,ids]
    rest=points[0];left=rest[11]-rest[14];up=(rest[5]+rest[8]-rest[11]-rest[14])*.5
    scale=float(np.linalg.norm(up));width=float(np.linalg.norm(left))
    if not np.isfinite([scale,width]).all() or min(scale,width)<1e-8:raise ValueError('Invalid rest reference scale or width')
    left/=width;up-=left*np.dot(up,left);height=float(np.linalg.norm(up))
    if not np.isfinite(height) or height<1e-8:raise ValueError('Degenerate rest reference axes')
    up/=height
    reference=np.stack((left,np.cross(up,left),up),axis=1)
    step=max(1,int(round(1/(fps*motion.frame_time))));frames=np.arange(1,len(points),step)
    rest_local=(rest-rest[0])@reference/scale
    return TemporalMotion(points[frames],rotations[frames],frames,rest_local,reference,rotations[0,0],scale,motion.frame_time*step)


def features(motion,start,end,t,context=True):
    t=np.asarray(t,dtype=float)
    if t.ndim!=1 or not np.isfinite(t).all() or np.any((t<0)|(t>1)):raise ValueError('Query times must lie in [0,1]')
    if not isinstance(start,int) or not isinstance(end,int) or not 0<=start<end<len(motion.points):raise ValueError('Invalid observed interval')
    if context and (start<1 or end+1>=len(motion.points)):raise ValueError('Outside-gap context is unavailable')
    if not np.isfinite(motion.dt) or motion.dt<=0:raise ValueError('Invalid motion time step')
    if not np.isfinite(motion.scale) or motion.scale<=0:raise ValueError('Invalid motion scale')
    if not all(np.isfinite(a).all() for a in (motion.rest,motion.reference,motion.rest_pelvis_rotation)):raise ValueError('Nonfinite static reference')
    indices=[start,end,start-1 if context else start,end+1 if context else end]
    observed=motion.points[indices];rotations=motion.rotations[indices]
    if not np.isfinite(observed).all() or not np.isfinite(rotations).all():raise ValueError('Observed poses must be finite')
    origin=motion.points[start,0].copy();basis=motion.rotations[start,0]@motion.rest_pelvis_rotation.T@motion.reference
    positions=(observed-origin)@basis/motion.scale
    matrices=np.einsum('ij,fkjl->fkil',basis.T,rotations)
    packed=np.concatenate((positions,rotation6(matrices)),axis=-1).reshape(4,D)
    duration=(end-start)*motion.dt;a,b=positions[:2]
    line=a[None]*(1-t[:,None,None])+b[None]*t[:,None,None]
    if context:
        va=(a-positions[2])/motion.dt;vb=(positions[3]-b)/motion.dt;u=t[:,None,None]
        curve=(2*u**3-3*u**2+1)*a+(u**3-2*u**2+u)*duration*va+(-2*u**3+3*u**2)*b+(u**3-u**2)*duration*vb
    else:curve=line.copy()
    orient=rotation6(slerp(matrices[0],matrices[1],t))
    linear=np.concatenate((line,orient),axis=-1).reshape(len(t),D)
    baseline=np.concatenate((curve,orient),axis=-1).reshape(len(t),D)
    static=np.r_[packed.ravel(),motion.rest.ravel(),float(context),float(context),duration,motion.dt]
    x=np.c_[np.broadcast_to(static,(len(t),len(static))),t]
    return dict(x=x,baseline=baseline,linear=linear,envelope=(4*t*(1-t))**2,origin=origin,basis=basis)


def labels(motion,indices,origin,basis):
    points=(motion.points[indices]-origin)@basis/motion.scale
    rotations=np.einsum('ij,fkjl->fkil',basis.T,motion.rotations[indices])
    return np.concatenate((points,rotation6(rotations)),axis=-1).reshape(len(indices),D)


def windows(motion,protocol,split,seed):
    rng=np.random.default_rng(seed);blocks=[];window=0
    maximum=protocol['training_windows_per_gap'] if split=='train' else protocol['evaluation_windows_per_gap']
    for gap in protocol['gaps']:
        available=np.arange(1,len(motion.points)-gap-1)
        starts=np.sort(rng.choice(available,min(maximum,len(available)),replace=False))
        for context in protocol['contexts']:
            for start in starts:
                start=int(start);end=start+gap;indices=np.arange(start,end+1);t=np.arange(gap+1)/gap
                d=features(motion,start,end,t,context);d['target']=labels(motion,indices,d.pop('origin'),d.pop('basis'))
                d.update(frame=motion.frames[indices],window=np.full(gap+1,window),gap=np.full(gap+1,gap),context=np.full(gap+1,context),dt=np.full(gap+1,motion.dt),t=t)
                blocks.append(d);window+=1
    if not blocks:raise ValueError('No eligible temporal windows')
    return {k:np.concatenate([d[k] for d in blocks]) for k in blocks[0]}


def load_split(root,manifest,split,protocol):
    rows=[]
    for index,row in enumerate(manifest['files']):
        if row['split']!=split:continue
        path=root/'cache'/(row['clip']+'.bvh')
        if hashlib.sha256(path.read_bytes()).hexdigest()!=row['sha256']:raise ValueError('Motion cache checksum mismatch: '+row['clip'])
        motion=temporal_motion(parse_bvh(path.read_text()),protocol['target_fps'])
        d=windows(motion,protocol,split,protocol['seed']+index);rows.append((row['clip'],d))
    if not rows:raise ValueError('Empty temporal split')
    return rows


def validate_manifests(manifests):
    seen={};hashes={}
    for manifest in manifests:
        for row in manifest['files']:
            for key,table in ((row['clip'],seen),(row['sha256'],hashes)):
                if key in table:raise ValueError('Duplicate or cross-split motion identity: '+row['clip'])
                table[key]=row['split']
    return seen
