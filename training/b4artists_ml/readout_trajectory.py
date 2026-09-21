"""Exact convex readout fit on frozen, supervised-trained hidden features.
SPDX-License-Identifier: GPL-2.0-or-later
The same trajectory loss is solved analytically; the parent model stays immutable.
"""
import numpy as np
from semantic_predictor import features
from sequence_model import statistics
from boundary_trajectory import trajectory_terms,loss_and_grad

def fit_readout(windows,parent,spec,regularization):
    if not np.isfinite(regularization) or regularization<=0:raise ValueError('Positive finite regularization required')
    model={k:v.copy() if isinstance(v,np.ndarray) else v for k,v in parent.items()}
    x=np.stack([features(w['x'],'motion') for w in windows]);z=np.clip((x-model['mean'])/model['std'],-8,8)
    _,weights,_,_=statistics(windows);terms=trajectory_terms(windows,spec)
    gram,rhs,constant,scales=terms
    h=np.c_[np.tanh(z@model['w0']+model['b0']),np.ones(len(z))];width=h.shape[1];weight=weights/weights.sum()/153
    penalty=np.ones((width,4));penalty[-1]=0.;penalty=np.diag(penalty.ravel()*regularization)
    result=np.empty((width,4,153));groups={}
    for channel in range(153):groups.setdefault(scales[:,channel].tobytes(),[]).append(channel)
    before=loss_and_grad(model,z,terms,weights,regularization)[0]
    for channels in groups.values():
        scale=scales[:,channels[0]]
        matrix=np.einsum('n,nh,nj,nkl->hkjl',weight*scale**2,h,h,gram,optimize=True).reshape(width*4,width*4)+penalty
        target=np.einsum('n,nh,nkf->hkf',weight*scale,h,rhs[:,:,channels],optimize=True).reshape(width*4,len(channels))
        # A zero-amplitude channel has no data term and an unregularized bias.
        if not np.any(scale):coefficient=np.zeros_like(target)
        else:coefficient=np.linalg.solve(matrix,target)
        result[:,:,channels]=coefficient.reshape(width,4,len(channels))
    model['w1']=result[:-1].reshape(width-1,612);model['b1']=result[-1].reshape(612)
    after,grad=loss_and_grad(model,z,terms,weights,regularization)
    stationarity=max(float(np.max(abs(grad[k]))) for k in ['w1','b1'])
    if not np.isfinite(after) or after>before+1e-10 or stationarity>1e-7:raise AssertionError('Exact readout objective/stationarity failure')
    return model,dict(before_objective=before,after_objective=after,readout_gradient_max=stationarity,regularization=regularization,linear_systems=len(groups),hidden_features_unchanged=bool(np.array_equal(parent['w0'],model['w0']) and np.array_equal(parent['b0'],model['b0'])))
