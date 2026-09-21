"""Per-joint learned position and proper-rotation mixtures; local NumPy only.
SPDX-License-Identifier: GPL-2.0-or-later
"""
import numpy as np
from context_network import initialize, Adam
from curve_mixture_v23 import expert_predictions, curve_features, GRID, parent_model
from sequence_model import statistics
from motion_coverage import fit_feature_normalization
from trajectory_predictor import operators
from temporal_data import rotation_matrix, quaternion
EPSILON = 1e-6


def softmax(value):
    value=np.asarray(value,dtype=float)
    if value.shape[-1] not in (3,4) or not np.isfinite(value).all():raise ValueError('Finite three/four-expert logits required')
    e=np.exp(value-value.max(axis=-1,keepdims=True));return e/e.sum(axis=-1,keepdims=True)


def rotation_experts(predictions):
    values=np.asarray(predictions,dtype=float)
    if values.ndim!=3 or values.shape[0]!=4 or values.shape[2]!=153 or not np.isfinite(values).all():raise ValueError('Four finite trajectories required')
    matrices,bad=rotation_matrix(values[[0,1,3]].reshape(3,-1,17,9)[...,3:])
    if bad.any():raise ValueError('Degenerate expert rotation')
    q=quaternion(matrices);q=np.where(np.sum(q*q[:1],axis=-1,keepdims=True)<0,-q,q)
    return q


def rotation6_and_jacobian(q):
    w,x,y,z=np.moveaxis(q,-1,0);zero=np.zeros_like(w)
    values=np.stack((1-2*(y*y+z*z),2*(x*y+z*w),2*(x*z-y*w),2*(x*y-z*w),1-2*(x*x+z*z),2*(y*z+x*w)),axis=-1)
    jac=np.stack((np.stack((zero,zero,-4*y,-4*z),axis=-1),np.stack((2*z,2*y,2*x,2*w),axis=-1),np.stack((-2*y,2*z,-2*w,2*x),axis=-1),np.stack((-2*z,2*y,2*x,-2*w),axis=-1),np.stack((zero,-4*x,zero,-4*z),axis=-1),np.stack((2*x,2*w,2*z,2*y),axis=-1)),axis=-2)
    return values,jac


def rotation_mix(probabilities,experts):
    weight=(1-EPSILON)*probabilities;weight=weight.copy();weight[...,0]+=EPSILON
    value=np.einsum('njk,nktjc->ntjc',weight,experts);norm=np.linalg.norm(value,axis=-1,keepdims=True)
    if not np.isfinite(norm).all() or np.any(norm<EPSILON*.99):raise ValueError('Invalid quaternion mixture norm')
    unit=value/norm;rot,jac=rotation6_and_jacobian(unit)
    return rot,jac,unit,norm


def training_terms(window,predictions,spec):
    values=np.asarray(predictions,dtype=float)
    if values.shape!=(4,len(window['t']),153) or not np.isfinite(values).all():raise ValueError('Matched finite expert trajectories required')
    target=np.asarray(window['target'],dtype=float)
    if target.shape!=values.shape[1:] or not np.isfinite(target).all():raise ValueError('Finite separate training targets required')
    points=values.reshape(4,-1,17,9)[...,:3];truth=target.reshape(-1,17,9);op=operators(window,spec)
    delta=np.einsum('at,ktjc->kajc',op,points-points[2]);residual=np.einsum('at,tjc->ajc',op,truth[...,:3]-points[2])
    return dict(pg=np.einsum('kajc,lajc->jkl',delta,delta),pr=np.einsum('kajc,ajc->jk',delta,residual),pc=float(np.sum(residual**2)),q=rotation_experts(values),rg=op.T@op,rt=truth[...,3:].copy())


def assemble(terms,ids):
    selected=[terms[int(i)] for i in ids];n=len(selected)
    if not n:raise ValueError('Nonempty training batch required')
    frames=max(v['q'].shape[1] for v in selected)
    q=np.empty((n,3,frames,17,4));rt=np.empty((n,frames,17,6));rg=np.zeros((n,frames,frames))
    for i,row in enumerate(selected):
        size=row['q'].shape[1];q[i,:,:size]=row['q'];q[i,:,size:]=row['q'][:,-1:, :, :];rt[i,:size]=row['rt'];rt[i,size:]=row['rt'][-1];rg[i,:size,:size]=row['rg']
    return dict(pg=np.stack([v['pg'] for v in selected]),pr=np.stack([v['pr'] for v in selected]),pc=np.asarray([v['pc'] for v in selected]),q=q,rg=rg,rt=rt)


def loss_and_grad(params,x,terms,weights,regularization):
    x=np.asarray(x,dtype=float);weights=np.asarray(weights,dtype=float)
    if x.ndim!=2 or x.shape[1]!=596 or weights.shape!=(len(x),) or not np.isfinite(x).all() or not np.isfinite(weights).all() or np.any(weights<0) or weights.sum()<=0 or not np.isfinite(regularization) or regularization<0:raise ValueError('Invalid joint-mixture loss inputs')
    hidden=np.tanh(x@params['w0']+params['b0']);logits=(hidden@params['w1']+params['b1']).reshape(-1,17,7)
    pp=softmax(logits[...,:4]);rp=softmax(logits[...,4:]);normalizer=weights/weights.sum()/153
    gp=np.einsum('njkl,njl->njk',terms['pg'],pp)
    position=np.sum(pp*gp-2*pp*terms['pr'],axis=(1,2))+terms['pc']
    rotation,jac,unit,norm=rotation_mix(rp,terms['q']);error=rotation-terms['rt'];ge=np.einsum('ntu,nujf->ntjf',terms['rg'],error)
    rotation_loss=np.sum(error*ge,axis=(1,2,3));loss=.5*float(normalizer@(position+rotation_loss))+.5*regularization*sum(float(np.sum(params[k]**2)) for k in ('w0','w1'))
    dp=(gp-terms['pr'])*normalizer[:,None,None];pdelta=pp*(dp-np.sum(dp*pp,axis=-1,keepdims=True))
    dr=ge*normalizer[:,None,None,None];dq=np.einsum('ntjf,ntjfc->ntjc',dr,jac);ds=(dq-unit*np.sum(dq*unit,axis=-1,keepdims=True))/norm
    dw=np.einsum('ntjc,nktjc->njk',ds,terms['q'])*(1-EPSILON);rdelta=rp*(dw-np.sum(dw*rp,axis=-1,keepdims=True))
    delta=np.concatenate((pdelta,rdelta),axis=-1).reshape(-1,119);dh=(delta@params['w1'].T)*(1-hidden**2)
    grad=dict(w0=x.T@dh+regularization*params['w0'],b0=dh.sum(axis=0),w1=hidden.T@delta+regularization*params['w1'],b1=delta.sum(axis=0))
    return loss,grad


def objective(params,x,terms,weights,reg):
    value=0.;total=float(weights.sum())
    for start in range(0,len(x),128):
        ids=np.arange(start,min(start+128,len(x)));mass=float(weights[ids].sum());value+=mass/total*loss_and_grad(params,x[ids],assemble(terms,ids),weights[ids],0.)[0]
    return value+.5*reg*sum(float(np.sum(params[k]**2)) for k in ('w0','w1'))


def fit(windows,terms,parent,spec,seed):
    h,epochs,batch=(spec[k] for k in ('hidden','epochs','batch_size'));rate,reg=float(spec['learning_rate']),float(spec['regularization'])
    if any(type(v) is not int or v<=0 for v in (h,epochs,batch)) or h>128 or not np.isfinite(rate) or rate<=0 or not np.isfinite(reg) or reg<0:raise ValueError('Invalid joint-mixture fit specification')
    ip=np.asarray(spec['initial_position_probabilities'],dtype=float);ir=np.asarray(spec['initial_rotation_probabilities'],dtype=float)
    if ip.shape!=(4,) or ir.shape!=(3,) or not np.isfinite(ip).all() or not np.isfinite(ir).all() or min(ip.min(),ir.min())<=0 or abs(ip.sum()-1)>1e-12 or abs(ir.sum()-1)>1e-12:raise ValueError('Positive normalized initial strengths required')
    x=np.stack([w['gate_features'] for w in windows]);_,weights,_,_=statistics(windows);mean,std=fit_feature_normalization(x,weights);z=np.clip((x-mean)/std,-8,8)
    params=initialize(596,h,119,seed,dtype=np.float64);params['w1'][:]=0;params['b1'][:]=np.tile(np.r_[np.log(ip),np.log(ir)],17);before_hidden=params['w0'].copy()
    initial=objective(params,z,terms,weights,reg);optimizer=Adam(params,rate=rate);rng=np.random.default_rng(seed);history=[];backtracked=rejected=0
    for epoch in range(epochs):
        ids=rng.permutation(len(z))
        for start in range(0,len(ids),batch):
            ix=ids[start:start+batch];local=assemble(terms,ix);old,grad=loss_and_grad(params,z[ix],local,weights[ix],reg);norm=np.sqrt(sum(float(np.sum(v*v)) for v in grad.values()))
            if not np.isfinite(norm):raise ValueError('Nonfinite joint-mixture gradient')
            if norm>1:grad={k:v/norm for k,v in grad.items()}
            before={k:v.copy() for k,v in params.items()};optimizer.step(params,grad);direction={k:params[k]-before[k] for k in params};accepted=False
            for attempt in range(8):
                if attempt:
                    for k in params:params[k][:]=before[k]+direction[k]*.5**attempt
                candidate=loss_and_grad(params,z[ix],local,weights[ix],reg)[0]
                if np.isfinite(candidate) and candidate<=old:accepted=True;backtracked+=int(attempt>0);break
            if not accepted:
                for k in params:params[k][:]=before[k]
                rejected+=1
        if (epoch+1)%10==0 or epoch+1==epochs:
            value=objective(params,z,terms,weights,reg)
            if not np.isfinite(value):raise ValueError('Nonfinite joint-mixture objective')
            history.append(dict(epoch=epoch+1,objective=value));print(dict(event='joint_epoch',epoch=epoch+1,objective=value),flush=True)
    model=dict(kind='joint_curve_mixture_v24',mean=mean,std=std,**params);model.update({'parent_'+k:v.copy() if isinstance(v,np.ndarray) else v for k,v in parent.items()})
    return model,dict(initial_objective=initial,training_objective=history[-1]['objective'],epochs=history,hidden_feature_change=float(np.linalg.norm(params['w0']-before_hidden)),backtracked_steps=backtracked,rejected_steps=rejected,scope='Training-only joint mixture; features and learned expert come from group-excluded parents')


def strengths(model,observations,predictions=None):
    if predictions is None:predictions=expert_predictions(parent_model(model),observations,GRID)
    z=np.clip((curve_features(observations,predictions)-model['mean'])/model['std'],-8,8);logits=(np.tanh(z@model['w0']+model['b0'])@model['w1']+model['b1']).reshape(17,7)
    return softmax(logits[:,:4]),softmax(logits[:,4:])


def predict_packed(model,observations,t):
    if model['kind']=='baseline':
        from curve_mixture_v23 import predict_packed as baseline
        return baseline(model,observations,t)
    if model['kind']!='joint_curve_mixture_v24':raise ValueError('Invalid joint-mixture kind')
    parent=parent_model(model);predictions=expert_predictions(parent,observations,t);fixed=predictions if np.array_equal(np.asarray(t),GRID) else expert_predictions(parent,observations,GRID);pp,rp=strengths(model,observations,fixed)
    values=np.asarray(predictions).reshape(4,-1,17,9);out=values[3].copy();ref=values[2,...,:3];out[...,:3]=ref+np.einsum('jk,ktjc->tjc',pp,values[...,:3]-ref)
    out[...,3:]=rotation_mix(rp[None],rotation_experts(predictions)[None])[0][0]
    priorities=(np.asarray(t)==0)|(np.asarray(t)==1);out[priorities]=values[3,priorities]
    if not np.isfinite(out).all():raise ValueError('Nonfinite joint prediction')
    return out.reshape(-1,153)


def provider(model):
    def call(observations,t):
        values=predict_packed(model,observations,t).reshape(-1,17,9);rot,bad=rotation_matrix(values[...,3:])
        if bad.any():raise ValueError('Degenerate joint-mixture output')
        return values[...,:3],rot
    return call


def save(path,model):np.savez_compressed(path,**{k:np.asarray(v) for k,v in model.items()})


def load(path):
    with np.load(path, allow_pickle=False) as archive: model = {k:archive[k] for k in archive.files}
    text_keys = ('kind', 'parent_kind', 'parent_baseline_kind', 'parent_continuity')
    for k in text_keys:
        if k not in model or model[k].shape != (): raise ValueError('Missing scalar model representation')
        model[k] = str(model[k])
    expected = {'kind', 'mean', 'std', 'w0', 'b0', 'w1', 'b1'} | {'parent_' + k for k in ('kind', 'baseline_kind', 'continuity', 'mean', 'std', 'w0', 'b0', 'w1', 'b1')}
    if set(model) != expected or model['kind'] != 'joint_curve_mixture_v24' or model['parent_kind'] != 'kinematic_mlp_v20' or model['parent_baseline_kind'] not in ('linear', 'shape') or model['parent_continuity'] not in ('C0', 'C1'):
        raise ValueError('Invalid mixture parameter keys or representation')
    for prefix, outputs, inputs in (('', 119, 596), ('parent_', 612, 548)):
        if model[prefix + 'mean'].shape != (inputs,) or model[prefix + 'std'].shape != (inputs,) or np.any(model[prefix + 'std'] <= 0): raise ValueError('Invalid model normalization')
        w0 = model[prefix + 'w0']
        if w0.ndim != 2 or w0.shape[0] != inputs or not 1 <= w0.shape[1] <= 128: raise ValueError('Invalid hidden shape')
        h = w0.shape[1]
        if model[prefix + 'b0'].shape != (h,) or model[prefix + 'w1'].shape != (h, outputs) or model[prefix + 'b1'].shape != (outputs,): raise ValueError('Invalid model readout')
    if any(not np.isfinite(v).all() for k,v in model.items() if k not in text_keys): raise ValueError('Nonfinite model parameters')
    return model
