"""Joint temporal coefficient learning through the actual source hierarchy.
SPDX-License-Identifier: GPL-2.0-or-later
"""
import numpy as np
from context_network import forward as network_forward
from sequence_kinematics import sequence_loss,forward
from sequence_data import semantic_output
from temporal_data import rotation_matrix
from temporal_model import evaluate


def statistics(windows):
    groups={}
    for i,w in enumerate(windows):groups.setdefault((w['clip'],w['gap'],w['context']),[]).append(i)
    weight=np.zeros(len(windows))
    for group in groups.values():weight[group]=1/(len(groups)*len(group))
    x=np.stack([w['x'] for w in windows]);mean=(x*weight[:,None]).sum(axis=0)
    std=np.maximum(np.sqrt(((x-mean)**2*weight[:,None]).sum(axis=0)),.1)
    return x,weight,mean,std


def coefficients(model,x):
    z=((np.asarray(x)-model['mean'])/model['std']).astype(np.float32)
    if model['kind']=='mlp':out=network_forward(model['params'],z)
    elif model['kind']=='ridge':out=np.c_[np.ones(len(z)),z]@model['coef']
    else:raise ValueError('Unknown sequence model')
    return out.reshape(len(z),4,-1)


def predict_local(model,w):
    c=coefficients(model,w['x'][None])[0]
    return w['baseline']+w['basis_functions']@c


def fit_ridge(windows,x,weight,mean,std,regularization):
    targets=[]
    for w in windows:
        b=w['basis_functions'];targets.append(np.linalg.solve(b.T@b+np.eye(4)*1e-6,b.T@(w['target_local']-w['baseline'])).ravel())
    z=np.c_[np.ones(len(x)),(x-mean)/std]
    gram=z.T@(z*weight[:,None])+regularization*np.eye(z.shape[1])
    coef=np.linalg.solve(gram,z.T@(np.asarray(targets)*weight[:,None]))
    return dict(kind='ridge',mean=mean,std=std,coef=coef)


def batch_loss(model,windows,skeleton,protocol):
    x=((np.stack([w['x'] for w in windows])-model['mean'])/model['std']).astype(np.float32)
    params=model['params'];hidden=np.tanh(x@params['w0']+params['b0']);out=hidden@params['w1']+params['b1']
    coeff=out.reshape(len(windows),4,-1);basis=np.stack([w['basis_functions'] for w in windows])
    local=np.stack([w['baseline'] for w in windows])+np.einsum('btk,bkf->btf',basis,coeff)
    offsets=np.stack([w['offsets'] for w in windows])[:,None];target=np.stack([w['target'] for w in windows]).reshape(len(windows),local.shape[1],17,9)
    rotation,_=rotation_matrix(target[...,3:])
    loss,grad=sequence_loss(local,offsets,skeleton[1],skeleton[2],target[...,:3],rotation,np.asarray([w['dt'] for w in windows]),
                            protocol['velocity_weight'],protocol['acceleration_weight'],protocol['rotation_weight'])
    delta=np.einsum('btk,btf->bkf',basis,grad).reshape(len(windows),-1)
    dh=(delta@params['w1'].T)*(1-hidden**2);reg=protocol['regularization']
    gradients=dict(w0=x.T@dh+reg*params['w0'],b0=dh.sum(axis=0),w1=hidden.T@delta+reg*params['w1'],b1=delta.sum(axis=0))
    loss+=.5*reg*sum(np.sum(params[k]**2) for k in ('w0','w1'))
    return float(loss),gradients


def evaluate_windows(windows,skeleton,kind,model=None):
    rows=[];max_edge=0.
    for index,w in enumerate(windows):
        if kind in ('linear','hermite'):pred=w[kind]
        else:
            local=w['baseline'] if kind=='fk_linear' else w['hermite_local'] if kind=='fk_hermite' else predict_local(model,w)
            p,_,_=forward(local,w['offsets'],skeleton[1]);parent=np.asarray(skeleton[1][1:]);length=np.linalg.norm(p[:,1:]-p[:,parent],axis=-1)
            max_edge=max(max_edge,float(abs(length-np.linalg.norm(w['offsets'][1:],axis=-1)).max()))
            pred=semantic_output(local,w['offsets'],skeleton)
        count=len(w['t']);d=dict(target=w['target'],baseline=w['hermite'],prediction=pred,t=w['t'],dt=np.full(count,w['dt']),gap=np.full(count,w['gap']),context=np.full(count,w['context']),window=np.full(count,index))
        rows.append((w['clip'],d))
    result=evaluate(rows,lambda d:d['prediction'])
    result['aggregate']['true_edge_length_max']=None if kind in ('linear','hermite') else max_edge
    return result


def acceptance(reports,protocol):
    a=reports['mlp']['aggregate'];others=[reports[k] for k in protocol['baselines']];g=protocol['gates']
    ratios={k:a[k]/max(min(r['aggregate'][k] for r in others),1e-12) for k in ('position','rotation','velocity','acceleration','length')}
    checks={k:ratios[k]<=((1-g['position_improvement_fraction']) if k=='position' else g[k+'_ratio_max']) for k in ratios}
    cohort=max(v['position']/max(min(r['cohorts'][key]['position'] for r in others),1e-12) for key,v in reports['mlp']['cohorts'].items())
    checks.update(cohorts=cohort<=g['cohort_position_ratio_max'],endpoint_position=a['endpoint_position']<=g['endpoint_position_max'],
                  endpoint_rotation=a['endpoint_rotation_matrix']<=g['endpoint_rotation_matrix_max'],true_edge_length=a['true_edge_length_max']<=g['true_edge_length_max'])
    return dict(passed=all(checks.values()),checks=checks,ratios=ratios,max_cohort_position_ratio=cohort)
