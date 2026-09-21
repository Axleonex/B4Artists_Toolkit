"""Local procedural trajectory math. SPDX-License-Identifier: GPL-2.0-or-later"""
import numpy as np


def validate_proposal_strength(value):
    """Validate the animator-facing procedural trajectory strength."""
    if (isinstance(value, (bool, np.bool_))
            or not isinstance(value, (int, float, np.integer, np.floating))):
        raise ValueError("Temporal proposal strength must be a finite number from zero to one")
    value = float(value)
    if not np.isfinite(value) or not 0.0 <= value <= 1.0:
        raise ValueError("Temporal proposal strength must be a finite number from zero to one")
    return value

def rotation6(matrix):
    return np.concatenate((matrix[..., :,0],matrix[..., :,1]),axis=-1)

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


def blend_proposal(baseline_points, baseline_rotations, proposal_points,
                   proposal_rotations, strength):
    """Blend a procedural proposal toward the deterministic endpoint baseline.

    The blend is deliberately host-independent and is not a learned model.
    Exact zero and one strengths return exact copies of their corresponding
    inputs so the animator can disable the proposal or preserve its full output
    without introducing floating-point drift.
    """
    strength = validate_proposal_strength(strength)
    baseline_points = np.asarray(baseline_points, dtype=float)
    proposal_points = np.asarray(proposal_points, dtype=float)
    baseline_rotations = np.asarray(baseline_rotations, dtype=float)
    proposal_rotations = np.asarray(proposal_rotations, dtype=float)
    if (baseline_points.ndim != 3 or baseline_points.shape[-2:] != (17, 3)
            or proposal_points.shape != baseline_points.shape
            or baseline_rotations.shape != (len(baseline_points), 17, 3, 3)
            or proposal_rotations.shape != baseline_rotations.shape
            or not all(np.isfinite(value).all() for value in (
                baseline_points, proposal_points, baseline_rotations,
                proposal_rotations))):
        raise ValueError("Temporal proposal arrays have invalid finite shapes")
    if strength == 0.0:
        return baseline_points.copy(), baseline_rotations.copy()
    if strength == 1.0:
        return proposal_points.copy(), proposal_rotations.copy()
    points = baseline_points + strength * (proposal_points - baseline_points)
    rotations = slerp(baseline_rotations, proposal_rotations, strength)
    if not np.isfinite(points).all() or not np.isfinite(rotations).all():
        raise ValueError("Temporal proposal blend became nonfinite")
    return points, rotations

def harmonic_tangent(left,right,hleft,hright):
    left=np.asarray(left,dtype=float);right=np.asarray(right,dtype=float)
    try:
        hleft=np.broadcast_to(np.asarray(hleft,dtype=float),left.shape)
        hright=np.broadcast_to(np.asarray(hright,dtype=float),left.shape)
    except ValueError:raise ValueError('Finite slopes and positive intervals required') from None
    if left.shape!=right.shape or not np.isfinite(left).all() or not np.isfinite(right).all() or not np.isfinite(hleft).all() or not np.isfinite(hright).all() or np.any(hleft<=0) or np.any(hright<=0):raise ValueError('Finite slopes and positive intervals required')
    out=np.zeros_like(left);same=(np.sign(left)==np.sign(right))&(left!=0)&(right!=0)
    w1=2*hright+hleft;w2=hright+2*hleft
    out[same]=(w1[same]+w2[same])/(w1[same]/left[same]+w2[same]/right[same])
    if not np.isfinite(out).all():raise ValueError('Nonfinite reference tangent')
    return out

class Trajectory:
    def __init__(self,observations,frames,*,rotation='slerp'):
        if rotation != 'slerp':raise ValueError('Unknown rotation comparison')
        frames=np.asarray(frames,dtype=float)
        if frames.ndim!=1 or len(frames)<2 or len(observations)!=len(frames)-1 or not np.isfinite(frames).all() or np.any(np.diff(frames)<=0):
            raise ValueError('Increasing authored frames and matching intervals required')
        self.rotation=rotation;self.frames=frames.copy();self.origin=observations[0].origin.copy();self.basis=observations[0].basis.copy();self.scale=observations[0].scale
        self.seconds=np.asarray([o.duration for o in observations])
        if not np.isfinite(self.seconds).all() or np.any(self.seconds<=0) or not np.allclose(self.seconds/np.diff(frames),self.seconds[0]/np.diff(frames)[0],rtol=1e-8,atol=1e-12):
            raise ValueError('Authored interval timing must use one frame rate')
        pairs=np.stack([o.world_points(o.positions[:2]) for o in observations])
        if not np.isfinite(pairs).all() or (len(pairs)>1 and not np.allclose(pairs[:-1,1],pairs[1:,0],rtol=0,atol=self.scale*2e-5)):
            raise ValueError('Adjacent authored observations disagree')
        # A fixed first-pose body basis makes componentwise shape preservation
        # equivariant to a common rigid transform and uniform character scale.
        self.positions=(np.concatenate((pairs[:,0],pairs[-1:,1]))-self.origin)@self.basis/self.scale
        secants=np.diff(self.positions,axis=0)/self.seconds[:,None,None]
        self.tangents=np.empty_like(self.positions);self.tangents[0]=secants[0];self.tangents[-1]=secants[-1]
        for j in range(1,len(frames)-1):self.tangents[j]=harmonic_tangent(secants[j-1],secants[j],self.seconds[j-1],self.seconds[j])
    def __call__(self,index,observed,t):
        if type(index) is not int or not 0<=index<len(self.seconds):raise ValueError('Valid explicit interval index required')
        _,rotations=observed.baseline(t)
        u=np.asarray(t,dtype=float)[:,None,None];a,b=self.positions[index:index+2];h=self.seconds[index]
        points=(2*u**3-3*u**2+1)*a+(u**3-2*u**2+u)*h*self.tangents[index]+(-2*u**3+3*u**2)*b+(u**3-u**2)*h*self.tangents[index+1]
        world=points*self.scale@self.basis.T+self.origin
        result=(world-observed.origin)@observed.basis/observed.scale
        result[np.asarray(t)==0]=observed.positions[0];result[np.asarray(t)==1]=observed.positions[1]
        if not np.isfinite(result).all():raise ValueError('Nonfinite authored trajectory')
        return result,rotations

def prepare(observations,frames,*,rotation='slerp'):
    return Trajectory(observations,frames,rotation=rotation)
