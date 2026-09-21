"""Small supervised temporal coefficient models on the shared observation schema.
SPDX-License-Identifier: GPL-2.0-or-later
Ridge and RBF-feature readouts are learned regression, not proprietary algorithms.
"""
import numpy as np
from temporal_data import rotation_matrix
from motion_coverage import rotation_log,fit_feature_normalization,squared_distance
from sequence_data import coefficients_basis
from sequence_model import statistics
from semantic_motion_data import baseline


def features(x,variant):
    x=np.array(x,dtype=float,copy=True)
    if x.shape!=(667,) or not np.isfinite(x).all() or x[-1]<=0 or x[-2]<x[-1] or any(v not in (0,1) for v in x[-4:-2]):raise ValueError('Invalid shared temporal observations')
    pose=x[:612].reshape(4,17,9);before,after=x[-4:-2]
    if not before:pose[2]=pose[0]
    if not after:pose[3]=pose[1]
    if variant=='raw':return x
    if variant!='motion':raise ValueError('Unknown temporal feature variant')
    rot,bad=rotation_matrix(pose[...,3:])
    if bad.any():raise ValueError('Invalid observed orientation')
    a,b,c,d=rot;pos=pose[...,:3];dt=x[-1]
    delta=np.r_[(pos[1]-pos[0]).ravel(),rotation_log(np.swapaxes(a,-1,-2)@b).ravel()]
    incoming=np.r_[((pos[0]-pos[2])/dt).ravel(),(-rotation_log(np.swapaxes(a,-1,-2)@c)/dt).ravel()]*before
    outgoing=np.r_[((pos[3]-pos[1])/dt).ravel(),(rotation_log(np.swapaxes(b,-1,-2)@d)/dt).ravel()]*after
    return np.r_[pose[0].ravel(),delta,incoming,outgoing,x[612:]]


def prepare(windows,variant):
    x=np.stack([features(w['x'],variant) for w in windows]);_,weights,_,_=statistics(windows)
    mean,std=fit_feature_normalization(x,weights)
    target=[]
    for w in windows:
        basis=coefficients_basis(w['t'],w['observations'].duration)
        target.append(np.linalg.solve(basis.T@basis+np.eye(4)*1e-6,basis.T@(w['target']-w['linear'])).ravel())
    return (x-mean)/std,weights,mean,std,np.asarray(target)


def design(model,z):
    if model['kind']=='ridge':return np.c_[np.ones(len(z)),z]
    if model['kind']=='rbf':return np.c_[np.ones(len(z)),np.exp(-squared_distance(z,model['centers'])/(2*model['width']**2))]
    raise ValueError('Unknown trained temporal model')


def fit(windows,experiment,seed):
    kind=experiment['kind'];variant=experiment['variant'];reg=experiment['regularization']
    if kind not in ('ridge','rbf') or not np.isfinite(reg) or reg<=0:raise ValueError('Invalid regression specification')
    z,weights,mean,std,target=prepare(windows,variant)
    model=dict(kind=kind,variant=variant,mean=mean,std=std)
    if kind=='rbf':
        count=min(experiment['centers'],len(z));ids=np.random.default_rng(seed).choice(len(z),count,replace=False,p=weights/weights.sum())
        model.update(centers=z[ids].copy(),width=float(experiment['width']))
    x=design(model,z)
    model['coef']=np.linalg.solve(x.T@(x*weights[:,None])+reg*np.eye(x.shape[1]),x.T@(target*weights[:,None]))
    return model


def predict_packed(model,observations,t):
    if model['kind']=='baseline':return baseline(observations,t,contextual=model['baseline']=='hermite')
    z=(features(observations.features(),model['variant'])-model['mean'])/model['std']
    coeff=(design(model,z[None])@model['coef']).reshape(4,153)
    out=baseline(observations,t)+coefficients_basis(t,observations.duration)@coeff
    if not np.isfinite(out).all():raise ValueError('Nonfinite temporal prediction')
    return out


def provider(model):
    def call(observations,t):
        value=predict_packed(model,observations,t).reshape(-1,17,9);rot,bad=rotation_matrix(value[...,3:])
        if bad.any():raise ValueError('Degenerate predicted rotation')
        return value[...,:3],rot
    return call


def save(path,model):
    np.savez_compressed(path,**{k:np.asarray(v) for k,v in model.items()})


def load(path):
    with np.load(path,allow_pickle=False) as z:out={k:z[k] for k in z.files}
    for key in ('kind','variant','baseline'):
        if key in out:out[key]=str(out[key])
    if out['kind']=='baseline':
        if out.get('baseline') not in ('linear','hermite'):raise ValueError('Invalid baseline')
        return out
    if out['kind'] not in ('ridge','rbf') or out.get('variant') not in ('raw','motion'):raise ValueError('Invalid temporal model kind')
    size=667 if out['variant']=='raw' else 514
    if out['mean'].shape!=(size,) or out['std'].shape!=(size,) or np.min(out['std'])<=0:raise ValueError('Invalid feature normalization')
    if out['kind']=='rbf':
        out['width']=float(out['width'])
        if out['centers'].ndim!=2 or out['centers'].shape[1]!=size or not 1<=len(out['centers'])<=128 or not np.isfinite(out['width']) or out['width']<=0:raise ValueError('Invalid RBF centers')
        size=len(out['centers'])
    if out['coef'].shape!=(size+1,612):raise ValueError('Invalid temporal readout')
    if any(not np.isfinite(v).all() for v in out.values() if isinstance(v,np.ndarray) and v.dtype.kind in 'fiu'):raise ValueError('Nonfinite model parameters')
    return out
