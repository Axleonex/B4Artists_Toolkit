"""Shape-preserving position reference and actually learned trajectory corrections.
SPDX-License-Identifier: GPL-2.0-or-later
"""
import numpy as np
from context_network import initialize,forward,Adam
from kinematic_features_v20 import features
from semantic_predictor import predict_packed as old_predict
from semantic_motion_data import baseline
from shape_reference import reference as shape_reference
from trajectory_predictor import operators
from sequence_data import coefficients_basis
from sequence_model import statistics
from motion_coverage import fit_feature_normalization
from temporal_data import rotation_matrix


def observation_scale(observations):
    """Read only known poses, masks and physical timing; no minimum-motion floor."""
    p=np.asarray(observations.positions,dtype=float);r=np.asarray(observations.rotations,dtype=float)
    duration=float(observations.duration);dt=float(observations.dt)
    if p.shape!=(4,17,3) or r.shape!=(4,17,3,3) or not np.isfinite(p).all() or not np.isfinite(r).all() or not np.isfinite(duration) or not np.isfinite(dt) or dt<=0 or duration<dt:raise ValueError('Invalid observed motion scale')
    position=np.linalg.norm(p[1]-p[0],axis=-1)
    rotation=np.linalg.norm(r[1]-r[0],axis=(-1,-2))/np.sqrt(2.)
    if observations.context:
        position+=.5*duration/dt*(np.linalg.norm(p[0]-p[2],axis=-1)+np.linalg.norm(p[3]-p[1],axis=-1))
        rotation+=.5*duration/dt*(np.linalg.norm(r[0]-r[2],axis=(-1,-2))+np.linalg.norm(r[3]-r[1],axis=(-1,-2)))/np.sqrt(2.)
    return np.concatenate((np.repeat(position[:,None],3,axis=1),np.repeat(rotation[:,None],6,axis=1)),axis=1).ravel()


def reference(observations,t,kind):
    if kind not in ('linear','shape'):raise ValueError('Invalid reference baseline')
    return shape_reference(observations,t) if kind=='shape' else baseline(observations,t)


def residual_basis(t,continuity):
    if continuity not in ('C0','C1'):raise ValueError('Invalid correction continuity')
    t=np.asarray(t,dtype=float)
    if t.ndim!=1 or not np.isfinite(t).all() or np.any((t<0)|(t>1)):raise ValueError('Invalid correction query times')
    basis=coefficients_basis(t,1.)
    if continuity=='C1':basis*=4*t[:,None]*(1-t[:,None])
    return basis


def trajectory_terms(windows,spec):
    grams=[];rhs=[];constant=[];scales=[]
    for w in windows:
        op=operators(w,spec);b=op@residual_basis(w['t'],spec['continuity'])
        residual=np.asarray(w['target']-reference(w['observations'],w['t'],spec['baseline_kind']),dtype=float)
        if residual.shape!=(len(w['t']),153) or not np.isfinite(residual).all():raise ValueError('Invalid training trajectory labels')
        scales.append(observation_scale(w['observations']));y=op@residual;grams.append(b.T@b);rhs.append(b.T@y);constant.append(float(np.sum(y*y)))
    return np.asarray(grams),np.asarray(rhs),np.asarray(constant),np.asarray(scales)


def loss_and_grad(params,x,terms,weights,regularization):
    gram,rhs,constant,scale=terms;weights=np.asarray(weights,dtype=float)
    if weights.shape!=(len(x),) or not np.isfinite(weights).all() or np.any(weights<0) or weights.sum()<=0 or not np.isfinite(regularization) or regularization<0:raise ValueError('Invalid neural loss weights')
    weight=weights/weights.sum()/153
    hidden=np.tanh(x@params['w0']+params['b0']);c=(hidden@params['w1']+params['b1']).reshape(-1,4,153)*scale[:,None,:]
    gc=np.einsum('nkl,nlf->nkf',gram,c)
    per=np.sum(c*gc-2*c*rhs,axis=(1,2))+constant
    loss=.5*float(weight@per)+.5*regularization*sum(float(np.sum(params[k]**2)) for k in ['w0','w1'])
    delta=((gc-rhs)*scale[:,None,:]*weight[:,None,None]).reshape(-1,612);dh=(delta@params['w1'].T)*(1-hidden**2)
    grad=dict(w0=x.T@dh+regularization*params['w0'],b0=dh.sum(axis=0),w1=hidden.T@delta+regularization*params['w1'],b1=delta.sum(axis=0))
    return loss,grad


def fit(windows,spec,seed):
    hidden=spec['hidden'];epochs=spec['epochs'];batch=spec['batch_size'];rate=float(spec['learning_rate']);reg=float(spec['regularization'])
    if any(type(v) is not int or v<=0 for v in [hidden,epochs,batch]) or hidden>128 or not np.isfinite(rate) or rate<=0 or not np.isfinite(reg) or reg<0:raise ValueError('Invalid neural training specification')
    x=np.stack([features(w['x'],'motion') for w in windows]);_,weights,_,_=statistics(windows);mean,std=fit_feature_normalization(x,weights)
    z=np.clip((x-mean)/std,-8.,8.);terms=trajectory_terms(windows,spec)
    params=initialize(548,hidden,612,seed,dtype=np.float64);params['w1'][:]=0.;params['b1'][:]=0.
    optimizer=Adam(params,rate=rate);rng=np.random.default_rng(seed);history=[];backtracked=0;rejected=0
    initial=loss_and_grad(params,z,terms,weights,reg)[0]
    for epoch in range(epochs):
        ids=rng.permutation(len(z))
        for start in range(0,len(ids),batch):
            ix=ids[start:start+batch];batch_terms=tuple(t[ix] for t in terms);before_loss,grad=loss_and_grad(params,z[ix],batch_terms,weights[ix],reg)
            norm=np.sqrt(sum(float(np.sum(v*v)) for v in grad.values()))
            if not np.isfinite(norm):raise ValueError('Nonfinite neural gradient')
            if norm>1:grad={k:v/norm for k,v in grad.items()}
            before={k:v.copy() for k,v in params.items()};optimizer.step(params,grad)
            direction={k:params[k]-before[k] for k in params};accepted=False
            for attempt in range(8):
                if attempt:
                    for k in params:params[k][:]=before[k]+direction[k]*.5**attempt
                candidate=loss_and_grad(params,z[ix],batch_terms,weights[ix],reg)[0]
                if np.isfinite(candidate) and candidate<=before_loss:
                    accepted=True;backtracked+=int(attempt>0);break
            if not accepted:
                for k in params:params[k][:]=before[k]
                rejected+=1
        if (epoch+1)%10==0 or epoch+1==epochs:
            value=loss_and_grad(params,z,terms,weights,reg)[0]
            if not np.isfinite(value):raise ValueError('Nonfinite training objective')
            history.append(dict(epoch=epoch+1,objective=value))
    model=dict(kind='kinematic_mlp_v20',baseline_kind=spec['baseline_kind'],continuity=spec['continuity'],mean=mean,std=std,**params)
    return model,dict(initial_objective=initial,training_objective=history[-1]['objective'],epochs=history,backtracked_steps=backtracked,rejected_steps=rejected,hidden_feature_change=float(np.linalg.norm(params['w0']-initialize(548,hidden,612,seed,dtype=np.float64)['w0'])))


def predict_packed(model,observations,t):
    if model['kind']=='baseline':return shape_reference(observations,t) if model['baseline']=='shape' else old_predict(model,observations,t)
    z=np.clip((features(observations.features(),'motion')-model['mean'])/model['std'],-8.,8.)
    coeff=forward(model,z[None]).reshape(4,153)*observation_scale(observations)[None,:]
    out=reference(observations,t,model['baseline_kind'])+residual_basis(t,model['continuity'])@coeff
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
        if out['baseline'] not in ['linear','hermite','shape']:raise ValueError('Invalid baseline')
        return out
    if out['kind']!='kinematic_mlp_v20':raise ValueError('Invalid neural model kind')
    for key in ('baseline_kind','continuity'):out[key]=str(out[key])
    if out['baseline_kind'] not in ('linear','shape') or out['continuity'] not in ('C0','C1'):raise ValueError('Invalid boundary model representation')
    if set(out)!={'kind','baseline_kind','continuity','mean','std','w0','b0','w1','b1'}:raise ValueError('Invalid neural parameter keys')
    if out['mean'].shape!=(548,) or out['std'].shape!=(548,) or np.any(out['std']<=0):raise ValueError('Invalid neural normalization')
    if out['w0'].ndim!=2 or out['w0'].shape[0]!=548 or not 1<=out['w0'].shape[1]<=128:raise ValueError('Invalid neural hidden shape')
    h=out['w0'].shape[1]
    if out['b0'].shape!=(h,) or out['w1'].shape!=(h,612) or out['b1'].shape!=(612,):raise ValueError('Invalid neural readout shape')
    if any(not np.isfinite(v).all() for k,v in out.items() if k not in ('kind','baseline_kind','continuity')):raise ValueError('Nonfinite neural parameter')
    return out
