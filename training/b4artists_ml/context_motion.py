"""Context-preserving articulated baseline and supervised temporal residuals.
SPDX-License-Identifier: GPL-2.0-or-later
"""
import numpy as np
from temporal_data import rotation_matrix,rotation6,quaternion,quat_matrix,slerp
from kernel_motion import infer_coefficients
from sequence_kinematics import forward
from sequence_data import semantic_output
from motion_coverage import evaluate_predictions


def context_baseline(x,t):
    """Use only four known poses and timing. Quaternion Hermite is procedural."""
    x=np.asarray(x,dtype=float);t=np.asarray(t,dtype=float)
    if x.shape!=(637,) or not np.isfinite(x).all():raise ValueError('Expected finite observed 23-joint window')
    if t.ndim!=1 or not len(t) or not np.isfinite(t).all() or np.any((t<0)|(t>1)):raise ValueError('Query times must lie in [0,1]')
    before,after,duration,dt=x[-4:]
    if before not in (0,1) or after not in (0,1) or min(duration,dt)<=0:raise ValueError('Invalid context masks or observation timing')
    pose=x[:564].reshape(4,141);roots=pose[:,:3];rotation,bad=rotation_matrix(pose[:,3:].reshape(4,23,6))
    if bad.any():raise ValueError('Degenerate observed rotation')
    u=t[:,None];a,b=roots[:2];secant=(b-a)/duration
    va=(a-roots[2])/dt if before else secant;vb=(roots[3]-b)/dt if after else secant
    h00=2*u**3-3*u**2+1;h10=u**3-2*u**2+u;h01=-2*u**3+3*u**2;h11=u**3-u**2
    root=h00*a+h10*duration*va+h01*b+h11*duration*vb
    if not before and not after:
        root=a*(1-u)+b*u;orient=slerp(rotation[0],rotation[1],t)
    else:
        q=quaternion(rotation);qa=q[0];qb=np.where(np.sum(qa*q[1],axis=-1,keepdims=True)<0,-q[1],q[1])
        qp=np.where(np.sum(qa*q[2],axis=-1,keepdims=True)<0,-q[2],q[2]);qn=np.where(np.sum(qb*q[3],axis=-1,keepdims=True)<0,-q[3],q[3])
        # Project chord derivatives onto each quaternion's tangent plane.
        v0=(qa-qp)/dt if before else (qb-qa)/duration
        v1=(qn-qb)/dt if after else (qb-qa)/duration
        v0-=qa*np.sum(qa*v0,axis=-1,keepdims=True);v1-=qb*np.sum(qb*v1,axis=-1,keepdims=True)
        curve=h00[:,None]*qa+h10[:,None]*duration*v0+h01[:,None]*qb+h11[:,None]*duration*v1
        norm=np.linalg.norm(curve,axis=-1,keepdims=True)
        fallback=quaternion(slerp(rotation[0],rotation[1],t))
        curve=np.where(norm>1e-8,curve/np.maximum(norm,1e-12),fallback);orient=quat_matrix(curve)
    result=np.c_[root,rotation6(orient).reshape(len(t),-1)]
    # Retain observed priority values exactly, including their representation.
    result[t==0]=pose[0];result[t==1]=pose[1]
    return result


def contextual_windows(windows):
    return [dict(w,baseline=context_baseline(w['x'],w['t'])) for w in windows]


def evaluate_context(model,windows,skeleton):
    coefficients=None if model is None else infer_coefficients(model,windows)
    predictions=[];edge=0.
    for index,w in enumerate(windows):
        local=context_baseline(w['x'],w['t'])
        if coefficients is not None:local=local+w['basis_functions']@coefficients[index]
        p,_,_=forward(local,w['offsets'],skeleton[1])
        lengths=np.linalg.norm(p[:,1:]-p[:,np.asarray(skeleton[1][1:])],axis=-1)
        edge=max(edge,float(abs(lengths-np.linalg.norm(w['offsets'][1:],axis=-1)).max()))
        predictions.append(semantic_output(local,w['offsets'],skeleton))
    report=evaluate_predictions(windows,predictions);report['aggregate']['true_edge_length_max']=edge
    return report
