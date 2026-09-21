"""Explicit authored-motion context for future sequence experiments.
SPDX-License-Identifier: GPL-2.0-or-later
Research only: these features require newly trained weights. No model is shipped.
"""
import numpy as np
from sequence_conditioning_v1 import request
from temporal_data import rotation_matrix,quaternion
SCHEMA='b4ml-observed-tangent-context-v1'
EXTRA=272
CONDITION=666

def rotation_vector(matrix):
    """Shortest world-space relative rotation, with deterministic pi convention."""
    q=quaternion(matrix)
    q=np.where(q[...,:1]<0,-q,q)
    v=q[...,1:];length=np.linalg.norm(v,axis=-1,keepdims=True)
    angle=2*np.arctan2(length,np.maximum(q[...,:1],0))
    return v*np.where(length>1e-8,angle/np.maximum(length,1e-12),2.)

def build(times,observed,mask,rest):
    """Append per-joint position/rotation tangent deviations and availability.

    For each unknown interval, subtract its secant from the incoming/outgoing
    authored secants and multiply by interval duration. Values encode curvature
    in canonical position units / radians, not frame-rate-dependent differences.
    Missing exterior observations produce zero vectors and zero availability.
    Each joint's position and orientation use their own observation mask.
    All hidden payloads are erased by request() before this computation.
    """
    req=request(times,observed,mask,rest)
    t=req['times'];known=req['observed'];m=np.asarray(mask)
    extra=np.zeros((len(t),17,16),dtype=np.float64)
    for joint in range(17):
        for kind in (0,1):
            ids=np.flatnonzero(m[:,joint,kind]);sample_t=t[ids]
            if kind==0:
                values=known[ids,joint,:3]
                changes=np.diff(values,axis=0)
            else:
                values,bad=rotation_matrix(known[ids,joint,3:])
                if bad.any():raise ValueError('Invalid observed rotations')
                changes=rotation_vector(values[1:]@np.swapaxes(values[:-1],-1,-2))
            spans=np.diff(sample_t);secants=changes/spans[:,None]
            interval=np.clip(np.searchsorted(ids,np.arange(len(t)),side='right')-1,0,len(ids)-2)
            offset=kind*8
            for k in range(len(ids)-1):
                rows=np.flatnonzero(interval==k)
                if k>0:
                    extra[rows,joint,offset:offset+3]=(secants[k-1]-secants[k])*spans[k]
                    extra[rows,joint,offset+6]=1.
                if k+1<len(secants):
                    extra[rows,joint,offset+3:offset+6]=(secants[k+1]-secants[k])*spans[k]
                    extra[rows,joint,offset+7]=1.
    if not np.isfinite(extra).all() or np.max(abs(extra))>np.finfo(np.float32).max:
        raise ValueError('Nonfinite or unrepresentable tangent context')
    extra=extra.reshape(len(t),EXTRA).astype(np.float32)
    condition=np.concatenate((req['condition'],extra),axis=-1)
    assert condition.shape==(len(t),CONDITION)
    extra.setflags(write=False);condition.setflags(write=False)
    return dict(request=req,tangent_context=extra,condition=condition,schema=SCHEMA)
