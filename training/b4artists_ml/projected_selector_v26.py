"""Observed whole-interval selection trained on fitted position/rotation risk.
SPDX-License-Identifier: GPL-2.0-or-later
A selector is not a new trajectory generator: selected v20 proposals contain the
frozen learned residual; selected procedural proposals must stay labelled as such.
"""
import numpy as np
from context_network import initialize,Adam
from motion_coverage import fit_feature_normalization
from curve_mixture_v23 import expert_predictions,curve_features,GRID,parent_model
from projected_pool_v26 import combine,CANDIDATES,BASELINE_INDEX
from temporal_data import rotation_matrix


def softmax(value):
    value=np.asarray(value,dtype=float)
    if value.ndim!=2 or value.shape[1]!=12 or not np.isfinite(value).all():raise ValueError('Finite12-candidate logits required')
    p=np.exp(value-value.max(axis=1,keepdims=True));return p/p.sum(axis=1,keepdims=True)


def training_costs(identities,metrics):
    # Match the existing temporal selection criterion on actual fitted outputs.
    # Normalize by the best complete procedural control in each TRAINING cohort.
    # Neither this label matrix nor cohort/clip identity is available at inference.
    if len(identities)!=len(metrics) or not identities:raise ValueError('Matched nonempty training identities and metrics required')
    raw=np.asarray([[r['position']+.1*r['rotation'] for r in row] for row in metrics],dtype=float)
    if raw.shape!=(len(identities),12) or not np.isfinite(raw).all() or np.any(raw<0):raise ValueError('Invalid fitted training costs')
    groups={}
    for i,w in enumerate(identities):groups.setdefault((w['clip'],int(w['gap']),bool(w['context'])),[]).append(i)
    weight=np.zeros(len(raw));cost=np.empty_like(raw);denominators=[]
    for key,ids in groups.items():
        baseline=raw[np.ix_(ids,BASELINE_INDEX)].mean(axis=0);den=max(float(baseline.min()),1e-12)
        weight[ids]=1/(len(groups)*len(ids));cost[ids]=raw[ids]/den
        denominators.append(dict(clip=key[0],gap=key[1],context=key[2],windows=len(ids),normalizer=den))
    return cost,weight,denominators


def loss_and_grad(params,x,cost,weight,regularization):
    x=np.asarray(x,dtype=float);cost=np.asarray(cost,dtype=float);weight=np.asarray(weight,dtype=float)
    if x.ndim!=2 or x.shape[1]!=596 or not len(x) or cost.shape!=(len(x),12) or weight.shape!=(len(x),):raise ValueError('Invalid selector training shapes')
    if any(not np.isfinite(a).all() for a in (x,cost,weight)) or np.any(cost<0) or np.any(weight<0) or weight.sum()<=0 or not np.isfinite(regularization) or regularization<0:raise ValueError('Invalid selector training values')
    hidden=np.tanh(x@params['w0']+params['b0']);p=softmax(hidden@params['w1']+params['b1']);mass=weight/weight.sum()
    expected=np.sum(p*cost,axis=1)
    loss=float(mass@expected)+.5*regularization*sum(float(np.sum(params[k]**2)) for k in ('w0','w1'))
    delta=p*(cost-expected[:,None])*mass[:,None]
    dh=(delta@params['w1'].T)*(1-hidden**2)
    return loss,dict(w0=x.T@dh+regularization*params['w0'],b0=dh.sum(axis=0),w1=hidden.T@delta+regularization*params['w1'],b1=delta.sum(axis=0))


def fit(x,cost,weight,parent,spec,seed):
    hidden,epochs,batch=(spec[k] for k in ('hidden','epochs','batch_size'));rate=float(spec['learning_rate']);reg=float(spec['regularization'])
    if any(type(v) is not int or v<=0 for v in (hidden,epochs,batch)) or hidden>128 or not np.isfinite(rate) or rate<=0 or not np.isfinite(reg) or reg<0:raise ValueError('Invalid selector training specification')
    mean,std=fit_feature_normalization(x,weight);z=np.clip((x-mean)/std,-8.,8.)
    params=initialize(596,hidden,12,seed,dtype=np.float64);params['w1'][:]=0.;params['b1'][:]=0.
    old=params['w0'].copy();initial=loss_and_grad(params,z,cost,weight,reg)[0]
    optimizer=Adam(params,rate=rate);rng=np.random.default_rng(seed);history=[];backtracked=rejected=0
    for epoch in range(epochs):
        ids=rng.permutation(len(z))
        for start in range(0,len(ids),batch):
            ix=ids[start:start+batch];before_loss,grad=loss_and_grad(params,z[ix],cost[ix],weight[ix],reg)
            norm=np.sqrt(sum(float(np.sum(v*v)) for v in grad.values()))
            if not np.isfinite(norm):raise ValueError('Nonfinite selector gradient')
            if norm>1:grad={k:v/norm for k,v in grad.items()}
            before={k:v.copy() for k,v in params.items()};optimizer.step(params,grad)
            direction={k:params[k]-before[k] for k in params};accepted=False
            for attempt in range(8):
                if attempt:
                    for k in params:params[k][:]=before[k]+direction[k]*.5**attempt
                candidate=loss_and_grad(params,z[ix],cost[ix],weight[ix],reg)[0]
                if np.isfinite(candidate) and candidate<=before_loss:
                    accepted=True;backtracked+=int(attempt>0);break
            if not accepted:
                for k in params:params[k][:]=before[k]
                rejected+=1
        if (epoch+1)%10==0 or epoch+1==epochs:
            value=loss_and_grad(params,z,cost,weight,reg)[0]
            if not np.isfinite(value):raise ValueError('Nonfinite selector objective')
            history.append(dict(epoch=epoch+1,objective=value))
    model=dict(kind='projected_selector_v26',mean=mean,std=std,**params)
    model.update({'parent_'+k:v.copy() if isinstance(v,np.ndarray) else v for k,v in parent.items()})
    p=softmax(np.tanh(z@params['w0']+params['b0'])@params['w1']+params['b1']);choice=p.argmax(axis=1)
    return model,dict(initial_objective=initial,training_objective=history[-1]['objective'],epochs=history,hidden_feature_change=float(np.linalg.norm(params['w0']-old)),backtracked_steps=backtracked,rejected_steps=rejected,argmax_training_cost=float(np.sum(weight*cost[np.arange(len(cost)),choice])/weight.sum()),choice_histogram=np.bincount(choice,minlength=12).tolist(),scope='Training-label fit and fixed argmax deployment diagnostic; not validation quality')


def selection(model,observations):
    fixed=expert_predictions(parent_model(model),observations,GRID)
    x=curve_features(observations,fixed)
    from kinematic_trajectory_v20 import observation_scale
    if not np.any(observation_scale(observations)):
        # Preserve the established exact stationary reference even when two
        # mathematically identical procedural evaluations differ by one ULP.
        probabilities=np.zeros(12);probabilities[7]=1.;return 7,probabilities
    z=np.clip((x-model['mean'])/model['std'],-8.,8.)
    probabilities=softmax((np.tanh(z@model['w0']+model['b0'])@model['w1']+model['b1'])[None])[0]
    return int(probabilities.argmax()),probabilities


def predict_packed(model,observations,t):
    from kinematic_trajectory_v20 import predict_packed as parent_predict
    if model['kind']=='baseline':return parent_predict(model,observations,t)
    if model['kind']!='projected_selector_v26':raise ValueError('Invalid selector representation')
    values=expert_predictions(parent_model(model),observations,t)
    return combine(values,selection(model,observations)[0])


def provider(model):
    def call(observations,t):
        value=predict_packed(model,observations,t).reshape(-1,17,9);rotation,bad=rotation_matrix(value[...,3:])
        if bad.any():raise ValueError('Degenerate selected orientation')
        return value[...,:3],rotation
    return call


def save(path,model):np.savez_compressed(path,**{k:np.asarray(v) for k,v in model.items()})


def load(path):
    with np.load(path,allow_pickle=False) as archive:model={k:archive[k] for k in archive.files}
    text=('kind','parent_kind','parent_baseline_kind','parent_continuity')
    for k in text:
        if k not in model or model[k].shape!=():raise ValueError('Missing scalar representation')
        model[k]=str(model[k])
    expected={'kind','mean','std','w0','b0','w1','b1'}|{'parent_'+k for k in ('kind','baseline_kind','continuity','mean','std','w0','b0','w1','b1')}
    if set(model)!=expected or model['kind']!='projected_selector_v26' or model['parent_kind']!='kinematic_mlp_v20' or model['parent_baseline_kind'] not in ('linear','shape') or model['parent_continuity'] not in ('C0','C1'):raise ValueError('Invalid selector parameter keys or representation')
    for prefix,inputs,outputs in (('',596,12),('parent_',548,612)):
        if model[prefix+'mean'].shape!=(inputs,) or model[prefix+'std'].shape!=(inputs,) or np.any(model[prefix+'std']<=0):raise ValueError('Invalid normalization')
        w0=model[prefix+'w0']
        if w0.ndim!=2 or w0.shape[0]!=inputs or not 1<=w0.shape[1]<=128:raise ValueError('Invalid hidden shape')
        h=w0.shape[1]
        if model[prefix+'b0'].shape!=(h,) or model[prefix+'w1'].shape!=(h,outputs) or model[prefix+'b1'].shape!=(outputs,):raise ValueError('Invalid readout')
    if any(not np.isfinite(v).all() for k,v in model.items() if k not in text):raise ValueError('Nonfinite model')
    return model
