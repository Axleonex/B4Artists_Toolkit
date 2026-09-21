"""Batched length projection for semantic poses, with immovable explicit pins.
SPDX-License-Identifier: GPL-2.0-or-later
This enforces edge lengths only, not anatomical angle limits, balance or collision.
"""
import numpy as np
from context_data import PARENTS,JOINTS


def project_pose(prediction,rest,observations,mask,tolerance=1e-3,iterations=200):
    position=np.asarray(prediction,dtype=float).copy();rest=np.asarray(rest,dtype=float)
    observations=np.asarray(observations,dtype=float);mask=np.asarray(mask,dtype=bool)
    single=position.ndim==2
    if single:position=position[None];rest=rest[None];observations=observations[None];mask=mask[None]
    if position.shape[1:]!=(JOINTS,3) or rest.shape!=position.shape or observations.shape!=position.shape or mask.shape!=position.shape[:2]:
        raise ValueError('Incompatible projection shapes')
    if not isinstance(iterations,int) or iterations<1 or not np.isfinite(tolerance) or tolerance<=0:
        raise ValueError('Invalid projection budget or tolerance')
    if not all(np.isfinite(v).all() for v in (position,rest,observations)):
        raise ValueError('Nonfinite projection input')
    edges=[(parent,child) for child,parent in enumerate(PARENTS) if parent>=0]
    lengths=np.stack([np.linalg.norm(rest[:,c]-rest[:,p],axis=1) for p,c in edges],axis=1)
    if np.any(lengths<1e-8):raise ValueError('Degenerate reference edge')
    inverse_mass=(~mask).astype(float)
    position=np.where(mask[...,None],observations,position)
    max_error=np.full(len(position),np.inf)
    for step in range(iterations):
        order=range(len(edges)) if step%2==0 else reversed(range(len(edges)))
        for i in order:
            parent,child=edges[i]
            delta=position[:,child]-position[:,parent]
            distance=np.linalg.norm(delta,axis=1)
            fallback=(rest[:,child]-rest[:,parent])/lengths[:,i,None]
            axis=np.where((distance>1e-10)[:,None],delta/np.maximum(distance[:,None],1e-10),fallback)
            total=inverse_mass[:,parent]+inverse_mass[:,child]
            correction=axis*((distance-lengths[:,i])/np.maximum(total,1))[:,None]
            position[:,parent]+=correction*inverse_mass[:,parent,None]
            position[:,child]-=correction*inverse_mass[:,child,None]
        actual=np.stack([np.linalg.norm(position[:,c]-position[:,p],axis=1) for p,c in edges],axis=1)
        max_error=np.max(np.abs(actual/lengths-1),axis=1)
        if np.all(max_error<=tolerance):break
    pin_error=np.max(np.where(mask,np.linalg.norm(position-observations,axis=2),0),axis=1)
    result=dict(converged=(max_error<=tolerance),max_length_error=max_error,pin_error=pin_error,iterations=step+1)
    return (position[0] if single else position),result


def project_pose_newton(prediction,rest,observations,mask,tolerance=1e-3,iterations=60):
    """Warm-started damped least-squares length projection with per-pose line search."""
    initial,initial_stats=project_pose(prediction,rest,observations,mask,tolerance,min(10,iterations))
    single=np.asarray(initial).ndim==2
    position=np.asarray(initial)[None].copy() if single else np.asarray(initial).copy()
    rest=np.asarray(rest,dtype=float);observations=np.asarray(observations,dtype=float);mask=np.asarray(mask,dtype=bool)
    if single:rest=rest[None];observations=observations[None];mask=mask[None]
    edges=[(p,c) for c,p in enumerate(PARENTS) if p>=0]
    lengths=np.stack([np.linalg.norm(rest[:,c]-rest[:,p],axis=1) for p,c in edges],axis=1)
    free=(~mask).astype(float)
    damping=np.full(len(position),1e-6)
    def residual(points):
        return np.stack([np.linalg.norm(points[:,c]-points[:,p],axis=1) for p,c in edges],axis=1)-lengths
    error=residual(position)
    for step in range(iterations):
        active=np.max(np.abs(error/lengths),axis=1)>tolerance
        if not active.any():break
        jacobian=np.zeros((len(position),len(edges),JOINTS*3))
        for i,(parent,child) in enumerate(edges):
            delta=position[:,child]-position[:,parent]
            distance=np.linalg.norm(delta,axis=1,keepdims=True)
            direction=delta/np.maximum(distance,1e-10)
            jacobian[:,i,parent*3:parent*3+3]=-direction*free[:,parent,None]
            jacobian[:,i,child*3:child*3+3]=direction*free[:,child,None]
        system=jacobian@np.swapaxes(jacobian,1,2)+np.eye(len(edges))[None]*damping[:,None,None]
        dual=np.linalg.solve(system,error[...,None])[...,0]
        change=-np.einsum('nei,ne->ni',jacobian,dual).reshape(position.shape)
        limit=np.max(lengths,axis=1)*.2
        magnitude=np.max(np.linalg.norm(change,axis=2),axis=1)
        change*=np.minimum(1,limit/np.maximum(magnitude,1e-10))[:,None,None]
        old_score=np.sum(error*error,axis=1);accepted=np.zeros(len(position),bool)
        for fraction in (1.,.5,.25,.125):
            candidate=np.where(mask[...,None],observations,position+change*fraction)
            candidate_error=residual(candidate)
            take=active&~accepted&(np.sum(candidate_error*candidate_error,axis=1)<old_score)
            position[take]=candidate[take];error[take]=candidate_error[take];accepted|=take
        damping=np.where(accepted,np.maximum(damping*.5,1e-8),np.minimum(damping*10,1.))
    max_error=np.max(np.abs(error/lengths),axis=1)
    pin_error=np.max(np.where(mask,np.linalg.norm(position-observations,axis=2),0),axis=1)
    stats=dict(converged=max_error<=tolerance,max_length_error=max_error,pin_error=pin_error,
               iterations=initial_stats['iterations']+step+1)
    return (position[0] if single else position),stats
