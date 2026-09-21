"""Cross-fitted convex controller with observed-context-dependent fallback.
SPDX-License-Identifier: GPL-2.0-or-later
"""
import numpy as np
from crossfit_controller import simplex,training_targets
from context_gate import gate_inputs,evaluate_gate
from context_motion import context_baseline
from motion_coverage import fit_feature_normalization
from sequence_model import statistics
from kernel_motion import kernel


def prior_values(windows, prior):
    prior=np.asarray(prior,dtype=float)
    if prior.shape!=(2,) or not np.isfinite(prior).all() or np.any((prior<0)|(prior>1)):
        raise ValueError('Root/body contextual priors must be finite in [0,1]')
    rows=np.zeros((len(windows),2,2))
    for i,w in enumerate(windows):
        flags=np.asarray(w['x'])[-4:-2]
        if not np.all(np.isin(flags,(0,1))):raise ValueError('Binary context availability required')
        if np.any(flags):rows[i,:,1]=prior
    return rows.reshape(-1,4)


def prepare(windows,base,variant,prior):
    x=gate_inputs(windows,variant);_,weight,_,_=statistics(windows)
    mean,std=fit_feature_normalization(x,weight)
    targets=training_targets(windows,base)-prior_values(windows,prior)
    return (x-mean)/std,weight,mean,std,targets


def strengths(model,windows):
    x=gate_inputs(windows,str(model['variant']));z=(x-model['mean'])/model['std']
    if not np.isfinite(z).all():raise ValueError('Nonfinite observations')
    values=prior_values(windows,model['context_prior'])
    for i in range(0,len(z),64):
        values[i:i+64]+=kernel(z[i:i+64],model['centers'],float(model['width']))@model['alpha']
    values=simplex(values.reshape(-1,2,2))
    for i,w in enumerate(windows):
        if not np.any(np.asarray(w['x'])[-4:-2]):values[i,:,1]=0.
    return values


def predict(model,windows,base):
    out=[]
    for w,a,g in zip(windows,base,strengths(model,windows),strict=True):
        line=w['baseline'];context=context_baseline(w['x'],w['t']);result=line.copy()
        for index,sl in enumerate((slice(0,3),slice(3,None))):
            result[:,sl]+=g[index,0]*(a-line)[:,sl]+g[index,1]*(context-line)[:,sl]
        out.append(result)
    return out


def evaluate_controller(model,windows,base,skeleton):
    return evaluate_gate(None,windows,predict(model,windows,base),skeleton)
