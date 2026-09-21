"""Training-only cohort tail-risk objective; frozen v27 soft readout unchanged.
SPDX-License-Identifier: GPL-2.0-or-later
Labels measure separately projected experts, so this expected-risk objective is a
surrogate for the projected soft blend. Actual original development gates decide.
"""
import copy
import numpy as np
from context_network import Adam
from projected_selector_v26 import softmax,load,save
from projected_pool_v26 import BASELINE_INDEX
from soft_selector_v27 import probabilities,predict_packed,provider


def normalize_costs(identities,position,rotation):
    p=np.asarray(position,dtype=float);r=np.asarray(rotation,dtype=float)
    if not identities or p.shape!=(len(identities),12) or r.shape!=p.shape or any(not np.isfinite(a).all() or np.any(a<0) for a in (p,r)):raise ValueError('Finite nonnegative matched candidate costs required')
    groups={}
    for i,w in enumerate(identities):groups.setdefault((w['clip'],int(w['gap']),bool(w['context'])),[]).append(i)
    gi=np.empty(len(p),dtype=int);pn=np.empty_like(p);rn=np.empty_like(r);records=[]
    for g,(key,ids) in enumerate(groups.items()):
        dp=max(float(p[np.ix_(ids,BASELINE_INDEX)].mean(axis=0).min()),1e-12)
        dr=max(float(r[np.ix_(ids,BASELINE_INDEX)].mean(axis=0).min()),1e-12)
        pn[ids]=p[ids]/dp;rn[ids]=r[ids]/dr;gi[ids]=g
        records.append(dict(clip=key[0],gap=key[1],context=key[2],windows=len(ids),position_denominator=dp,rotation_denominator=dr))
    return pn,rn,gi,records


def loss_and_grad(params,x,position,rotation,group,regularization=.0001,penalty=10.):
    x=np.asarray(x,dtype=float);p=np.asarray(position,dtype=float);r=np.asarray(rotation,dtype=float);group=np.asarray(group)
    if x.ndim!=2 or x.shape[1]!=596 or not len(x) or p.shape!=(len(x),12) or r.shape!=p.shape or group.shape!=(len(x),) or not np.issubdtype(group.dtype,np.integer):raise ValueError('Invalid tail-risk training shapes')
    if any(not np.isfinite(a).all() for a in (x,p,r)) or np.any(p<0) or np.any(r<0) or np.any(group<0) or group.max()>=len(group) or not np.isfinite(regularization) or regularization<0 or not np.isfinite(penalty) or penalty<0:raise ValueError('Invalid tail-risk training values')
    counts=np.bincount(group);ng=len(counts)
    if np.any(counts==0):raise ValueError('Training group indices must be contiguous')
    hidden=np.tanh(x@params['w0']+params['b0']);prob=softmax(hidden@params['w1']+params['b1'])
    ep=np.sum(prob*p,axis=1);er=np.sum(prob*r,axis=1)
    gp=np.bincount(group,weights=ep,minlength=ng)/counts;gr=np.bincount(group,weights=er,minlength=ng)/counts
    hp=np.maximum(gp-1.,0.);hr=np.maximum(gr-1.02,0.)
    objective=float(np.mean(gp+.1*gr+penalty*(hp*hp+hr*hr)))+.5*regularization*sum(float(np.sum(params[k]**2)) for k in ('w0','w1'))
    dc=((1.+2.*penalty*hp[group])[:,None]*p+(.1+2.*penalty*hr[group])[:,None]*r)/(ng*counts[group,None])
    delta=prob*(dc-np.sum(prob*dc,axis=1,keepdims=True));dh=(delta@params['w1'].T)*(1.-hidden**2)
    grad=dict(w0=x.T@dh+regularization*params['w0'],b0=dh.sum(axis=0),w1=hidden.T@delta+regularization*params['w1'],b1=delta.sum(axis=0))
    diagnostic=dict(mean_position=float(gp.mean()),max_position=float(gp.max()),mean_rotation=float(gr.mean()),max_rotation=float(gr.max()),position_groups_above_one=int(np.sum(gp>1.)),rotation_groups_above_1_02=int(np.sum(gr>1.02)))
    return objective,grad,diagnostic


def fit(features,position,rotation,group,initial_model,spec,guard=lambda:None):
    if spec!={'epochs':200,'learning_rate':.002,'regularization':.0001,'penalty':10.,'backtracks':8,'hidden':32}:raise ValueError('Only the frozen v28 specification is implemented')
    model=copy.deepcopy(initial_model)
    if model['w0'].shape!=(596,32):raise ValueError('Frozen32hidden warm start required')
    z=np.clip((np.asarray(features,dtype=float)-model['mean'])/model['std'],-8.,8.)
    params={k:model[k] for k in ('w0','b0','w1','b1')};start={k:v.copy() for k,v in params.items()};opt=Adam(params,rate=spec['learning_rate'])
    def measure():return loss_and_grad(params,z,position,rotation,group,spec['regularization'],spec['penalty'])
    initial,_,initial_diag=measure();history=[];rejected=backtracked=0
    for epoch in range(spec['epochs']):
        guard();value,grad,_=measure();norm=np.sqrt(sum(float(np.sum(v*v)) for v in grad.values()))
        if not np.isfinite(norm):raise ValueError('Nonfinite training gradient')
        if norm>1.:grad={k:v/norm for k,v in grad.items()}
        before={k:v.copy() for k,v in params.items()};opt.step(params,grad);direction={k:params[k]-before[k] for k in params};accepted=False
        for attempt in range(spec['backtracks']):
            for k in params:params[k][:]=before[k]+direction[k]*.5**attempt
            new,_,detail=measure()
            if np.isfinite(new) and new<=value:accepted=True;backtracked+=int(attempt>0);break
        if not accepted:
            for k in params:params[k][:]=before[k]
            rejected+=1;new,_,detail=measure()
        if (epoch+1)%10==0:history.append(dict(epoch=epoch+1,objective=new,**detail))
    final,_,final_diag=measure()
    if final>=initial or not any(np.any(params[k]!=start[k]) for k in params):raise ValueError('No learned training improvement')
    return model,dict(initial_objective=initial,training_objective=final,initial=initial_diag,final=final_diag,history=history,rejected_steps=rejected,backtracked_steps=backtracked,hidden_feature_change=float(np.linalg.norm(params['w0']-start['w0'])),scope='In-sample expected expert risk; not actual projected blend quality or independent validation')
