"""Training-mean articulated controller; only training sees projection targets.
SPDX-License-Identifier: GPL-2.0-or-later
"""
import numpy as np
from motion_coverage import observed_features,fit_feature_normalization,evaluate_predictions
from kernel_motion import infer_coefficients,kernel,kernel_trials
from sequence_model import statistics
from sequence_kinematics import forward
from sequence_data import semantic_output
from context_motion import context_baseline


def gate_inputs(windows,variant):
    if variant=='raw_pose':return np.stack([w['x'] for w in windows])
    if variant!='compact':raise ValueError('Unknown context gate feature schema')
    rows=[]
    for w in windows:
        v=observed_features(w);rotation_stats=[]
        for start in (138,207,276):
            lengths=np.linalg.norm(v[start:start+69].reshape(23,3),axis=-1)
            rotation_stats.extend((float(lengths.mean()),float(lengths.max())))
        root=v[345:354].reshape(3,3);duration=v[-2];chord=root[0]/duration
        # Root secant and measured incoming/outgoing velocities, root angular
        # observations and global angular summaries are all known at query time.
        rows.append(np.r_[root.ravel(),root[1]-chord,root[2]-chord,v[138:141],v[207:210],v[276:279],rotation_stats,v[-4:]])
    return np.stack(rows)


def base_locals(control,windows):
    coef=infer_coefficients(control,windows)
    return [w['baseline']+w['basis_functions']@c for w,c in zip(windows,coef,strict=True)]


def training_targets(windows,base):
    targets=[]
    for w,a in zip(windows,base,strict=True):
        contextual=context_baseline(w['x'],w['t']);difference=contextual-a;residual=w['target_local']-a;row=[]
        for sl in [slice(0,3)]+[slice(3+6*j,3+6*(j+1)) for j in range(23)]:
            d=difference[1:-1,sl];y=residual[1:-1,sl];den=float(np.sum(d*d))
            row.append(float(np.clip(np.sum(d*y)/den,0,1)) if den>1e-16 else 0.)
        targets.append(row)
    return np.asarray(targets)


def prepare(windows,base,variant):
    x=gate_inputs(windows,variant);_,weight,_,_=statistics(windows);mean,std=fit_feature_normalization(x,weight)
    return (x-mean)/std,weight,mean,std,training_targets(windows,base)


def gate_values(model,windows):
    x=gate_inputs(windows,str(model['variant']));z=(x-model['mean'])/model['std']
    if not np.isfinite(z).all():raise ValueError('Nonfinite context gate observations')
    values=np.empty((len(z),24))
    for start in range(0,len(z),64):values[start:start+64]=kernel(z[start:start+64],model['centers'],float(model['width']))@model['alpha']
    if not np.isfinite(values).all():raise ValueError('Nonfinite learned context strengths')
    return np.clip(values+model['target_mean'],0.,1.)


def predict_locals(model,windows,base):
    gates=gate_values(model,windows);result=[]
    for w,a,g in zip(windows,base,gates,strict=True):
        contextual=context_baseline(w['x'],w['t']);b=a.copy()
        b[:,:3]+=g[0]*(contextual[:,:3]-a[:,:3])
        for j in range(23):
            sl=slice(3+6*j,3+6*(j+1));b[:,sl]+=g[j+1]*(contextual[:,sl]-a[:,sl])
        result.append(b)
    return result


def evaluate_gate(model,windows,base,skeleton):
    locals=base if model is None else predict_locals(model,windows,base);predictions=[];edge=0.
    for w,local in zip(windows,locals,strict=True):
        p,_,_=forward(local,w['offsets'],skeleton[1]);lengths=np.linalg.norm(p[:,1:]-p[:,np.asarray(skeleton[1][1:])],axis=-1)
        edge=max(edge,float(abs(lengths-np.linalg.norm(w['offsets'][1:],axis=-1)).max()));predictions.append(semantic_output(local,w['offsets'],skeleton))
    report=evaluate_predictions(windows,predictions);report['aggregate']['true_edge_length_max']=edge;return report
