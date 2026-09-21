"""Learned temporal coefficient regression with observed-only motion conditioning.
SPDX-License-Identifier: GPL-2.0-or-later
"""
import numpy as np
from motion_coverage import observed_features,fit_feature_normalization,squared_distance,evaluate_predictions
from sequence_model import statistics
from sequence_data import semantic_output
from sequence_kinematics import forward


def inputs(windows,variant):
    if variant=='raw_pose':return np.stack([w['x'] for w in windows])
    if variant=='motion_relative':return np.stack([observed_features(w) for w in windows])
    raise ValueError('Unknown observed feature variant')


def training_targets(windows):
    # Supervised labels are legal here only for the trainer's training partition.
    return np.stack([np.linalg.lstsq(w['basis_functions'],w['target_local']-w['baseline'],rcond=1e-10)[0].ravel() for w in windows])


def kernel(a,b,width):
    if not np.isfinite(width) or width<=0:raise ValueError('Positive finite kernel width required')
    return np.exp(-squared_distance(a,b)/(2*width**2))


def prepare(windows,variant):
    x=inputs(windows,variant);_,weights,_,_=statistics(windows);mean,std=fit_feature_normalization(x,weights)
    return (x-mean)/std,weights,mean,std,training_targets(windows)


def kernel_trials(z,weights,target,width,regularizations):
    scale=np.sqrt(weights*len(weights));gram=kernel(z,z,width)*scale[:,None]*scale[None,:]
    eigenvalues,vectors=np.linalg.eigh(gram);eigenvalues=np.maximum(eigenvalues,0.)
    projected=vectors.T@(target*scale[:,None])
    for reg in regularizations:
        if reg<=0:raise ValueError('Positive kernel regularization required')
        alpha=(vectors@(projected/(eigenvalues[:,None]+reg)))*scale[:,None]
        yield reg,alpha


def linear_fit(z,weights,target,reg):
    if reg<=0:raise ValueError('Positive linear regularization required')
    design=np.c_[np.ones(len(z)),z]
    return np.linalg.solve(design.T@(design*weights[:,None])+reg*np.eye(design.shape[1]),design.T@(target*weights[:,None]))


def infer_coefficients(model,windows):
    z=(inputs(windows,model['variant'])-model['mean'])/model['std']
    if not np.isfinite(z).all():raise ValueError('Nonfinite model observations')
    if model['kind']=='zero':return np.zeros((len(windows),4,141))
    if model['kind']=='linear':out=np.c_[np.ones(len(z)),z]@model['coef']
    elif model['kind']=='kernel':
        out=np.empty((len(z),564))
        for start in range(0,len(z),64):out[start:start+64]=kernel(z[start:start+64],model['centers'],model['width'])@model['alpha']
    else:raise ValueError('Unknown coefficient model')
    if not np.isfinite(out).all():raise ValueError('Nonfinite learned coefficients')
    return out.reshape(len(windows),4,141)


def evaluate_model(model,windows,skeleton):
    coefficients=infer_coefficients(model,windows);predictions=[];edge=0.
    for w,c in zip(windows,coefficients,strict=True):
        local=w['baseline']+w['basis_functions']@c;p,_,_=forward(local,w['offsets'],skeleton[1])
        lengths=np.linalg.norm(p[:,1:]-p[:,np.asarray(skeleton[1][1:])],axis=-1)
        edge=max(edge,float(abs(lengths-np.linalg.norm(w['offsets'][1:],axis=-1)).max()))
        predictions.append(semantic_output(local,w['offsets'],skeleton))
    report=evaluate_predictions(windows,predictions);report['aggregate']['true_edge_length_max']=edge
    return report


def save_model(path,model):
    values={k:np.array(v) if isinstance(v,str) else v for k,v in model.items()}
    np.savez_compressed(path,**values)


def load_model(path):
    with np.load(path,allow_pickle=False) as z:model={k:z[k] for k in z.files}
    for k in ('kind','variant'):model[k]=str(model[k])
    if 'width' in model:model['width']=float(model['width'])
    return model
