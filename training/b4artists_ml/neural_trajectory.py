"""Local learned temporal features using the verified trajectory objective.
SPDX-License-Identifier: GPL-2.0-or-later
"""
import numpy as np
from context_network import initialize,forward,Adam
from semantic_predictor import features,predict_packed as old_predict
from semantic_motion_data import baseline
from trajectory_predictor import operators
from sequence_data import coefficients_basis
from sequence_model import statistics
from motion_coverage import fit_feature_normalization
from temporal_data import rotation_matrix


def trajectory_terms(windows,spec):
    grams=[];rhs=[];constant=[]
    for w in windows:
        op=operators(w,spec);b=op@coefficients_basis(w['t'],w['observations'].duration)
        residual=np.asarray(w['target']-w['linear'],dtype=float)
        if residual.shape!=(len(w['t']),153) or not np.isfinite(residual).all():raise ValueError('Invalid training trajectory labels')
        y=op@residual;grams.append(b.T@b);rhs.append(b.T@y);constant.append(float(np.sum(y*y)))
    return np.asarray(grams),np.asarray(rhs),np.asarray(constant)


def loss_and_grad(params,x,terms,weights,regularization):
    gram,rhs,constant=terms;weights=np.asarray(weights,dtype=float)
    if weights.shape!=(len(x),) or not np.isfinite(weights).all() or np.any(weights<0) or weights.sum()<=0 or not np.isfinite(regularization) or regularization<0:raise ValueError('Invalid neural loss weights')
    weight=weights/weights.sum()/153
    hidden=np.tanh(x@params['w0']+params['b0']);c=(hidden@params['w1']+params['b1']).reshape(-1,4,153)
    gc=np.einsum('nkl,nlf->nkf',gram,c)
    per=np.sum(c*gc-2*c*rhs,axis=(1,2))+constant
    loss=.5*float(weight@per)+.5*regularization*sum(float(np.sum(params[k]**2)) for k in ['w0','w1'])
    delta=((gc-rhs)*weight[:,None,None]).reshape(-1,612);dh=(delta@params['w1'].T)*(1-hidden**2)
    grad=dict(w0=x.T@dh+regularization*params['w0'],b0=dh.sum(axis=0),w1=hidden.T@delta+regularization*params['w1'],b1=delta.sum(axis=0))
    return loss,grad


def fit(windows,spec,seed):
    hidden=spec['hidden'];epochs=spec['epochs'];batch=spec['batch_size'];rate=float(spec['learning_rate']);reg=float(spec['regularization'])
    if any(type(v) is not int or v<=0 for v in [hidden,epochs,batch]) or hidden>128 or not np.isfinite(rate) or rate<=0 or not np.isfinite(reg) or reg<0:raise ValueError('Invalid neural training specification')
    x=np.stack([features(w['x'],'motion') for w in windows]);_,weights,_,_=statistics(windows);mean,std=fit_feature_normalization(x,weights)
    z=np.clip((x-mean)/std,-8.,8.);terms=trajectory_terms(windows,spec)
    params=initialize(514,hidden,612,seed,dtype=np.float64);params['w1'][:]=0.;params['b1'][:]=0.
    optimizer=Adam(params,rate=rate);rng=np.random.default_rng(seed);history=[]
    initial=loss_and_grad(params,z,terms,weights,reg)[0]
    for epoch in range(epochs):
        ids=rng.permutation(len(z))
        for start in range(0,len(ids),batch):
            ix=ids[start:start+batch];_,grad=loss_and_grad(params,z[ix],tuple(t[ix] for t in terms),weights[ix],reg)
            norm=np.sqrt(sum(float(np.sum(v*v)) for v in grad.values()))
            if not np.isfinite(norm):raise ValueError('Nonfinite neural gradient')
            if norm>1:grad={k:v/norm for k,v in grad.items()}
            optimizer.step(params,grad)
        if (epoch+1)%10==0 or epoch+1==epochs:
            value=loss_and_grad(params,z,terms,weights,reg)[0]
            if not np.isfinite(value):raise ValueError('Nonfinite training objective')
            history.append(dict(epoch=epoch+1,objective=value))
    model=dict(kind='trajectory_mlp_v14',mean=mean,std=std,**params)
    return model,dict(initial_objective=initial,training_objective=history[-1]['objective'],epochs=history,hidden_feature_change=float(np.linalg.norm(params['w0']-initialize(514,hidden,612,seed,dtype=np.float64)['w0'])))


def predict_packed(model,observations,t):
    if model['kind']=='baseline':return old_predict(model,observations,t)
    z=np.clip((features(observations.features(),'motion')-model['mean'])/model['std'],-8.,8.)
    coeff=forward(model,z[None]).reshape(4,153)
    out=baseline(observations,t)+coefficients_basis(t,observations.duration)@coeff
    if not np.isfinite(out).all():raise ValueError('Nonfinite neural prediction')
    return out


def provider(model):
    def call(observations,t):
        value=predict_packed(model,observations,t).reshape(-1,17,9);rotation,bad=rotation_matrix(value[...,3:])
        if bad.any():raise ValueError('Degenerate neural rotation')
        return value[...,:3],rotation
    return call


def save(path,model):np.savez_compressed(path,**{k:np.asarray(v) for k,v in model.items()})

def load(path):
    with np.load(path,allow_pickle=False) as z:out={k:z[k] for k in z.files}
    out['kind']=str(out['kind'])
    if out['kind']=='baseline':
        out['baseline']=str(out['baseline'])
        if out['baseline'] not in ['linear','hermite']:raise ValueError('Invalid baseline')
        return out
    if out['kind']!='trajectory_mlp_v14':raise ValueError('Invalid neural model kind')
    if set(out)!={'kind','mean','std','w0','b0','w1','b1'}:raise ValueError('Invalid neural parameter keys')
    if out['mean'].shape!=(514,) or out['std'].shape!=(514,) or np.any(out['std']<=0):raise ValueError('Invalid neural normalization')
    if out['w0'].ndim!=2 or out['w0'].shape[0]!=514 or not 1<=out['w0'].shape[1]<=128:raise ValueError('Invalid neural hidden shape')
    h=out['w0'].shape[1]
    if out['b0'].shape!=(h,) or out['w1'].shape!=(h,612) or out['b1'].shape!=(612,):raise ValueError('Invalid neural readout shape')
    if any(not np.isfinite(v).all() for k,v in out.items() if k!='kind'):raise ValueError('Nonfinite neural parameter')
    return out
