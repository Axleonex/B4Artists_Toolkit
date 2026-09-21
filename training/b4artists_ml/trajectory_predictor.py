"""Learn coefficients by minimizing trajectories and finite-difference motion error.
SPDX-License-Identifier: GPL-2.0-or-later
The observation representation, model format and runtime predictor are v12-compatible.
"""
import numpy as np
from semantic_predictor import features,design,predict_packed,provider,save,load
from motion_coverage import fit_feature_normalization
from sequence_data import coefficients_basis
from sequence_model import statistics


def operators(w,spec):
    t=np.asarray(w['t'],dtype=float);dt=float(w['dt'])
    if t.ndim!=1 or len(t)<3 or not np.isfinite(t).all() or not np.isfinite(dt) or dt<=0 or not np.allclose(np.diff(t)*w['observations'].duration,dt,rtol=1e-7,atol=1e-12):
        raise ValueError('Uniform finite trajectory samples required')
    values=[1.,float(spec['velocity_weight']),float(spec['acceleration_weight'])]
    if any(not np.isfinite(v) or v<0 for v in values):raise ValueError('Finite nonnegative motion loss weights required')
    identity=np.eye(len(t));out=[]
    for order,value in enumerate(values):
        if value:out.append(np.diff(identity,n=order,axis=0)/dt**order*np.sqrt(value/(len(t)-order)))
    return np.concatenate(out)


def normal_system(phi,windows,weights,spec):
    phi=np.asarray(phi,dtype=float);weights=np.asarray(weights,dtype=float)
    if phi.ndim!=2 or phi.shape[0]!=len(windows) or weights.shape!=(len(windows),) or not np.isfinite(phi).all() or not np.isfinite(weights).all() or np.any(weights<0) or weights.sum()<=0:raise ValueError('Invalid weighted trajectory design')
    reg=float(spec['regularization'])
    if not np.isfinite(reg) or reg<=0:raise ValueError('Positive finite regularization required')
    size=phi.shape[1];h=reg*np.eye(size*4);rhs=np.zeros((size*4,153));groups={}
    for i,w in enumerate(windows):
        t=np.asarray(w['t'],dtype=float);key=(t.tobytes(),float(w['dt']),float(w['observations'].duration))
        groups.setdefault(key,[]).append(i)
    for ids in groups.values():
        w=windows[ids[0]];op=operators(w,spec);basis=coefficients_basis(w['t'],w['observations'].duration);b=op@basis
        residual=np.stack([windows[i]['target']-windows[i]['linear'] for i in ids])
        if residual.shape!=(len(ids),len(w['t']),153) or not np.isfinite(residual).all():raise ValueError('Invalid training trajectory labels')
        x=phi[ids];weight=weights[ids]
        gram=x.T@(x*weight[:,None]);h+=np.einsum('ab,kl->akbl',gram,b.T@b).reshape(size*4,size*4)
        target=np.einsum('kt,ntf->nkf',b.T@op,residual)
        rhs+=np.einsum('na,n,nkf->akf',x,weight,target).reshape(size*4,153)
    return h,rhs


def objective(coef,phi,windows,weights,spec):
    c=np.asarray(coef,dtype=float).reshape(phi.shape[1],4,153)
    value=float(spec['regularization'])*float(np.sum(c*c))
    for x,w,weight in zip(phi,windows,weights,strict=True):
        b=coefficients_basis(w['t'],w['observations'].duration)
        error=w['linear']+b@np.einsum('a,akf->kf',x,c)-w['target']
        value+=float(weight)*float(np.sum((operators(w,spec)@error)**2))
    return value


def fit(windows,spec,seed):
    if spec.get('kind')!='rbf' or spec.get('variant')!='motion':raise ValueError('Frozen experiment requires motion RBF features')
    count=spec['centers'];width=float(spec['width'])
    if type(count) is not int or not 1<=count<=128 or not np.isfinite(width) or width<=0:raise ValueError('Invalid centers or width')
    x=np.stack([features(w['x'],'motion') for w in windows]);_,weights,_,_=statistics(windows)
    mean,std=fit_feature_normalization(x,weights);z=(x-mean)/std
    ids=np.random.default_rng(seed).choice(len(z),min(count,len(z)),replace=False,p=weights/weights.sum())
    model=dict(kind='rbf',variant='motion',mean=mean,std=std,centers=z[ids].copy(),width=width)
    phi=design(model,z);h,rhs=normal_system(phi,windows,weights,spec)
    coef=np.linalg.solve(h,rhs);model['coef']=coef.reshape(phi.shape[1],612)
    diagnostic=dict(training_objective=objective(coef,phi,windows,weights,spec),zero_objective=objective(np.zeros_like(coef),phi,windows,weights,spec),normal_residual=float(np.max(abs(h@coef-rhs))))
    if not np.isfinite(model['coef']).all() or diagnostic['training_objective']>diagnostic['zero_objective']+1e-8:raise ValueError('Trajectory fit failed deterministic objective check')
    return model,diagnostic
