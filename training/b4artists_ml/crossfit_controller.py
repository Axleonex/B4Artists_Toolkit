"""Observed-only convex motion controller, trained on group-excluded predictions.
SPDX-License-Identifier: GPL-2.0-or-later
"""
import numpy as np
from context_gate import gate_inputs
from context_motion import context_baseline
from motion_coverage import fit_feature_normalization, evaluate_predictions
from kernel_motion import kernel
from sequence_model import statistics
from sequence_kinematics import forward
from sequence_data import semantic_output


def grouped_folds(windows, count=4):
    groups = sorted({w['clip'].split('_')[0] for w in windows})
    if type(count) is not int or not 2 <= count <= len(groups):
        raise ValueError('At least one complete catalog group per fold required')
    assignment = {g:i % count for i,g in enumerate(groups)}
    return [(np.array([i for i,w in enumerate(windows) if assignment[w['clip'].split('_')[0]] != fold]),
             np.array([i for i,w in enumerate(windows) if assignment[w['clip'].split('_')[0]] == fold]))
            for fold in range(count)]


def simplex(values):
    values = np.asarray(values, dtype=float)
    if values.shape[-1] != 2 or not np.isfinite(values).all():
        raise ValueError('Finite two-component blend strengths required')
    clipped = np.maximum(values, 0.)
    edge = np.clip((values[...,0]-values[...,1]+1.)*.5, 0., 1.)
    return np.where((clipped.sum(axis=-1)>1.)[...,None], np.stack((edge,1.-edge),axis=-1), clipped)


def fit_blend(a, b, target):
    # Exact least squares on a 2D simplex: feasible interior or one of its edges.
    a=np.asarray(a).ravel(); b=np.asarray(b).ravel(); y=np.asarray(target).ravel()
    design=np.stack((a,b),axis=1)
    if not np.isfinite(design).all() or not np.isfinite(y).all():
        raise ValueError('Nonfinite training blend target')
    candidates=[]; interior=np.linalg.lstsq(design,y,rcond=1e-10)[0]
    if np.min(interior)>=0 and np.sum(interior)<=1: candidates.append(interior)
    for origin,direction in ((np.array([0.,0.]),np.array([1.,0.])),
                             (np.array([0.,0.]),np.array([0.,1.])),
                             (np.array([0.,1.]),np.array([1.,-1.]))):
        delta=design@direction; den=float(delta@delta)
        t=float(np.clip(delta@(y-design@origin)/den,0.,1.)) if den>1e-16 else 0.
        candidates.append(origin+t*direction)
    return min(candidates,key=lambda c:float(np.sum((design@c-y)**2)))


def training_targets(windows, base):
    rows=[]
    for w,pred in zip(windows,base,strict=True):
        line=w['baseline']; context=context_baseline(w['x'],w['t'])
        row=[]
        for sl in (slice(0,3),slice(3,None)):
            row.extend(fit_blend((pred-line)[1:-1,sl],(context-line)[1:-1,sl],(w['target_local']-line)[1:-1,sl]))
        rows.append(row)
    return np.asarray(rows)


def prepare(windows, base, variant):
    x=gate_inputs(windows,variant); _,weight,_,_=statistics(windows)
    mean,std=fit_feature_normalization(x,weight)
    return (x-mean)/std,weight,mean,std,training_targets(windows,base)


def strengths(model, windows):
    x=gate_inputs(windows,str(model['variant'])); z=(x-model['mean'])/model['std']
    if not np.isfinite(z).all(): raise ValueError('Nonfinite motion observations')
    result=np.empty((len(z),4))
    for i in range(0,len(z),64):
        result[i:i+64]=kernel(z[i:i+64],model['centers'],float(model['width'])) @ model['alpha']
    result=simplex(result.reshape(-1,2,2))
    for i,w in enumerate(windows):
        if not np.any(np.asarray(w['x'])[-4:-2]): result[i,:,1]=0.
    return result


def predict(model, windows, base):
    values=strengths(model,windows); out=[]
    for w,a,g in zip(windows,base,values,strict=True):
        line=w['baseline']; contextual=context_baseline(w['x'],w['t']); result=line.copy()
        for index,sl in enumerate((slice(0,3),slice(3,None))):
            result[:,sl]+=g[index,0]*(a-line)[:,sl]+g[index,1]*(contextual-line)[:,sl]
        out.append(result)
    return out


def evaluate_controller(model, windows, base, skeleton):
    predictions=[];edge=0.
    for w,local in zip(windows,predict(model,windows,base),strict=True):
        positions,_,_=forward(local,w['offsets'],skeleton[1])
        lengths=np.linalg.norm(positions[:,1:]-positions[:,np.asarray(skeleton[1][1:])],axis=-1)
        edge=max(edge,float(np.max(abs(lengths-np.linalg.norm(w['offsets'][1:],axis=-1)))))
        predictions.append(semantic_output(local,w['offsets'],skeleton))
    report=evaluate_predictions(windows,predictions)
    report['aggregate']['true_edge_length_max']=edge
    return report
