"""Observed-motion features and explicitly oracle-only representation diagnostics.
SPDX-License-Identifier: GPL-2.0-or-later
"""
import numpy as np
from temporal_data import rotation_matrix,quaternion
from sequence_data import semantic_output
from temporal_model import evaluate


def rotation_log(matrix):
    q=quaternion(matrix);q=np.where(q[...,:1]<0,-q,q)
    v=q[...,1:];norm=np.linalg.norm(v,axis=-1,keepdims=True)
    angle=2*np.arctan2(norm,np.maximum(q[...,:1],0))
    return v*np.where(norm>1e-8,angle/np.maximum(norm,1e-12),2.)


def observed_features(window):
    """Read only serialized observed poses/static offsets/masks/time, never target arrays."""
    x=np.asarray(window['x'],dtype=float)
    if x.shape!=(637,) or not np.isfinite(x).all():raise ValueError('Expected finite observed 23-joint window')
    poses=x[:564].reshape(4,141);roots=poses[:,:3];rotation,bad=rotation_matrix(poses[:,3:].reshape(4,23,6))
    if bad.any():raise ValueError('Degenerate observed rotation')
    dt=x[-1];duration=x[-2]
    if dt<=0 or duration<=0:raise ValueError('Positive observation timing required')
    before,after=x[-4:-2]
    if before not in (0,1) or after not in (0,1):raise ValueError('Context masks must be binary')
    a,b,c,d=rotation
    delta=rotation_log(np.swapaxes(a,-1,-2)@b)
    incoming=-rotation_log(np.swapaxes(a,-1,-2)@c)/dt*before
    outgoing=rotation_log(np.swapaxes(b,-1,-2)@d)/dt*after
    # Missing context is explicitly suppressed even if unused slots contain other finite poses.
    root=np.r_[roots[1]-roots[0],(roots[0]-roots[2])/dt*before,(roots[3]-roots[1])/dt*after]
    return np.r_[poses[0,3:],delta.ravel(),incoming.ravel(),outgoing.ravel(),root,x[564:633],before,after,duration,dt]


def fit_feature_normalization(x,weights):
    weights=np.asarray(weights,dtype=float);weights=weights/weights.sum()
    mean=(x*weights[:,None]).sum(axis=0);std=np.maximum(np.sqrt(((x-mean)**2*weights[:,None]).sum(axis=0)),.1)
    return mean,std


def squared_distance(a,b):
    """Mean squared standardized feature distance; bounded block callers avoid big temporaries."""
    if a.ndim!=2 or b.ndim!=2 or a.shape[1]!=b.shape[1]:raise ValueError('Feature dimensions differ')
    return np.maximum((np.sum(a*a,axis=1)[:,None]+np.sum(b*b,axis=1)[None]-2*a@b.T)/a.shape[1],0.)


def oracle_coefficients(window):
    """Uses hidden labels. Diagnostic fit only; forbidden as an inference feature."""
    b=window['basis_functions'];target=window['target_local']-window['baseline']
    return np.linalg.lstsq(b,target,rcond=1e-10)[0]


def evaluate_predictions(windows,predictions):
    rows=[]
    for index,(w,pred) in enumerate(zip(windows,predictions,strict=True)):
        n=len(w['t']);rows.append((w['clip'],dict(prediction=pred,target=w['target'],baseline=w['hermite'],t=w['t'],dt=np.full(n,w['dt']),gap=np.full(n,w['gap']),context=np.full(n,w['context']),window=np.full(n,index))))
    return evaluate(rows,lambda d:d['prediction'])


def representation_diagnostic(windows,skeleton):
    predictions=[]
    for w in windows:
        local=w['baseline']+w['basis_functions']@oracle_coefficients(w)
        predictions.append(semantic_output(local,w['offsets'],skeleton))
    result=evaluate_predictions(windows,predictions)
    result['label']='Hidden-label least-squares diagnostic; not deployable prediction, not an optimized semantic-error lower bound'
    return result
