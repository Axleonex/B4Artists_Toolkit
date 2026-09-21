"""Local temporal residual inference, weighted training and cohort-balanced metrics.
SPDX-License-Identifier: GPL-2.0-or-later
"""
import numpy as np
from context_network import forward
from temporal_data import J, D, PARENTS, rotation_matrix


def feature_weights(rotation_weight=.1):
    return np.tile([1.,1.,1.,*([rotation_weight]*6)],J)


def residual_loss(params,x,target,baseline,envelope,weights,rotation_weight=.1,regularization=1e-5):
    """Direct envelope gradient avoids dividing near-anchor labels by tiny envelopes."""
    h=np.tanh(x@params['w0']+params['b0']);raw=h@params['w1']+params['b1']
    e=np.asarray(envelope)[:,None];w=np.asarray(weights)[:,None]*feature_weights(rotation_weight)
    normalizer=float(w.sum())
    if normalizer<=0 or not np.isfinite(normalizer):raise ValueError('Positive finite training mass required')
    error=baseline+e*raw-target
    delta=error*w/normalizer*e
    loss=.5*np.sum(error**2*w)/normalizer+.5*regularization*sum(np.sum(params[k]**2) for k in ('w0','w1'))
    dh=(delta@params['w1'].T)*(1-h**2)
    gradients=dict(w0=x.T@dh+regularization*params['w0'],b0=dh.sum(axis=0),w1=h.T@delta+regularization*params['w1'],b1=delta.sum(axis=0))
    return float(loss),gradients


def predict(model,d):
    x=((d['x']-model['mean'])/model['std']).astype(np.float32)
    if model['kind']=='mlp':raw=forward(model['params'],x)
    elif model['kind']=='ridge':raw=np.c_[np.ones(len(x)),x]@model['coef']
    else:raise ValueError('Unknown temporal model')
    result=d['baseline']+d['envelope'][:,None]*raw
    if not np.isfinite(result).all():raise ValueError('Nonfinite temporal prediction')
    return result


def training_arrays(rows):
    arrays=[];weights=[]
    for _,d in rows:
        interior=(d['t']>0)&(d['t']<1)
        w=np.zeros(len(d['t']))
        cohorts=sorted(set(zip(d['gap'].tolist(),d['context'].tolist())))
        for gap,context in cohorts:
            mask=interior&(d['gap']==gap)&(d['context']==context)
            w[mask]=1/(len(rows)*len(cohorts)*mask.sum())
        arrays.append({k:d[k][interior] for k in ('x','target','baseline','envelope')})
        weights.append(w[interior])
    data={k:np.concatenate([d[k] for d in arrays]).astype(np.float32) for k in arrays[0]}
    data['weights']=np.concatenate(weights).astype(np.float32)
    return data


def standardize(data):
    x=data['x'].astype(float);w=data['weights'].astype(float);w/=w.sum()
    mean=np.sum(x*w[:,None],axis=0)
    std=np.maximum(np.sqrt(np.sum((x-mean)**2*w[:,None],axis=0)),.1)
    return mean,std


def fit_ridge(data,mean,std,regularization):
    z=(data['x']-mean)/std
    design=np.c_[np.ones(len(z)),z]*data['envelope'][:,None]
    w=data['weights'].astype(float);w/=w.sum()
    gram=design.T@(design*w[:,None]);rhs=design.T@((data['target']-data['baseline'])*w[:,None])
    gram+=regularization*np.eye(gram.shape[0])
    return dict(kind='ridge',mean=mean,std=std,coef=np.linalg.solve(gram,rhs))


def _window_metrics(d,pred):
    target=d['target'].reshape(-1,J,9);pred=pred.reshape(-1,J,9)
    pos=pred[...,:3];truth=target[...,:3]
    base_rotation,_=rotation_matrix(d['baseline'].reshape(-1,J,9)[...,3:])
    rotation,bad=rotation_matrix(pred[...,3:],base_rotation)
    gt,_=rotation_matrix(target[...,3:])
    relative=np.einsum('...ji,...jk->...ik',rotation,gt)
    angle=np.arccos(np.clip((np.trace(relative,axis1=-2,axis2=-1)-1)/2,-1,1))
    interior=(d['t']>0)&(d['t']<1);ends=~interior
    error=np.linalg.norm(pos-truth,axis=-1)
    parents=np.asarray(PARENTS[1:]);length=lambda p:np.linalg.norm(p[:,1:]-p[:,parents],axis=-1)
    true_length=length(truth)
    if np.any(true_length<1e-8):raise ValueError('Degenerate target segment')
    dt=float(d['dt'][0])
    if not np.allclose(d['dt'],dt) or not dt>0:raise ValueError('Inconsistent window dt')
    return dict(position=float(error[interior].mean()),root=float(error[interior,0].mean()),
                rotation=float(angle[interior].mean()),length=float((abs(length(pos)-true_length)/true_length)[interior].mean()),
                velocity=float(np.linalg.norm(np.diff(pos-truth,axis=0)/dt,axis=-1).mean()),
                acceleration=float(np.linalg.norm(np.diff(pos-truth,n=2,axis=0)/dt**2,axis=-1).mean()),
                endpoint_position=float(error[ends].max()),endpoint_rotation_matrix=float(abs(rotation[ends]-gt[ends]).max()),
                degenerate_rotations=int(bad.sum()))


def evaluate(rows,predictor):
    cohorts={};endpoint_position=0.;endpoint_rotation=0.;degenerate=0;queries=0
    for clip,d in rows:
        prediction=predictor(d)
        if prediction.shape!=d['target'].shape or not np.isfinite(prediction).all():raise ValueError('Invalid evaluation prediction')
        for window in np.unique(d['window']):
            mask=d['window']==window;wd={k:v[mask] for k,v in d.items()}
            if not np.all(np.diff(wd['t'])>0) or wd['t'][0]!=0 or wd['t'][-1]!=1:raise ValueError('Unordered or incomplete temporal window')
            m=_window_metrics(wd,prediction[mask]);key=f"{clip}/gap{int(wd['gap'][0])}/context{int(wd['context'][0])}"
            endpoint_position=max(endpoint_position,m.pop('endpoint_position'))
            endpoint_rotation=max(endpoint_rotation,m.pop('endpoint_rotation_matrix'))
            degenerate+=m.pop('degenerate_rotations');queries+=int(mask.sum())
            cohorts.setdefault(key,[]).append(m)
    means={key:{k:float(np.mean([w[k] for w in group])) for k in group[0]} for key,group in cohorts.items()}
    aggregate={k:float(np.mean([v[k] for v in means.values()])) for k in next(iter(means.values()))}
    aggregate.update(endpoint_position=endpoint_position,endpoint_rotation_matrix=endpoint_rotation,degenerate_rotations=degenerate,queries=queries)
    return dict(aggregate=aggregate,cohorts=means)


def selection(report):
    a=report['aggregate'];return a['position']+.1*a['rotation']


def gates(reports,protocol):
    a=reports['mlp']['aggregate'];others=[reports[k] for k in ('linear','hermite','ridge')];g=protocol['gates']
    best={k:min(r['aggregate'][k] for r in others) for k in ('position','rotation','velocity','length')}
    ratios={k:a[k]/max(best[k],1e-12) for k in best}
    cohort_ratio=max(v['position']/max(min(r['cohorts'][key]['position'] for r in others),1e-12) for key,v in reports['mlp']['cohorts'].items())
    checks=dict(position=ratios['position']<=1-g['position_improvement_fraction'],rotation=ratios['rotation']<=g['rotation_ratio_max'],
                velocity=ratios['velocity']<=g['velocity_ratio_max'],length=ratios['length']<=g['length_ratio_max'],
                cohorts=cohort_ratio<=g['cohort_position_ratio_max'],endpoint_position=a['endpoint_position']<=g['endpoint_position_max'],
                endpoint_rotation=a['endpoint_rotation_matrix']<=g['endpoint_rotation_matrix_max'])
    return dict(passed=all(checks.values()),checks=checks,ratios=ratios,max_cohort_position_ratio=cohort_ratio)
