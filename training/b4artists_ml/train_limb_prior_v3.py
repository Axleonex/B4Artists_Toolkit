"""Train proportion-augmented limb priors with subject-number-separated selection.
SPDX-License-Identifier: GPL-2.0-or-later
"""
import json
import time
import numpy as np
from train_limb_prior import ROOT,SEED,BANDWIDTHS,RIDGES,digest,evaluate,weighted_fit,load_rows
from train_limb_prior_v2 import fit,predictor
from augment_limb import augment_rows,TRAIN_RATIOS,STRESS_RATIOS


def fit_linear(rows,ridge):
    x=np.concatenate([r[1][:,3:] for r in rows]);y=np.concatenate([r[2] for r in rows])
    weights=np.concatenate([np.full(len(r[1]),1/(len(rows)*len(r[1]))) for r in rows])
    mean=np.sum(x*weights[:,None],axis=0)
    scale=np.maximum(np.sqrt(np.sum((x-mean)**2*weights[:,None],axis=0)),.05)
    phi=np.c_[np.ones(len(x)),(x-mean)/scale]
    return dict(mean=mean,scale=scale,coefficients=weighted_fit(phi,y,weights,ridge),
                mean_output=np.sum(y*weights[:,None],axis=0))


def linear_predictor(p):
    return lambda x:np.c_[np.ones(len(x)),(x[:,3:]-p['mean'])/p['scale']]@p['coefficients']


def main():
    start=time.perf_counter()
    manifest=json.loads((ROOT/'data_manifest.json').read_text())
    arrays={};linear_arrays={}
    report=dict(schema=3,seed=SEED,training_ratios=list(TRAIN_RATIOS),stress_ratios=list(STRESS_RATIOS),
        augmentation='Preserve body-frame upper and lower segment directions; recompute endpoint and bend-plane labels at each new ratio',
        selection='Leave-one-training-subject-number-out; clip-balanced error on original and stress proportions',
        previous_test_status='V1 test and V2 confirmation are observed diagnostics, not blind validation for V3',
        manifest_sha256=digest(ROOT/'data_manifest.json'),limbs={})
    for kind in ('arm','leg'):
        original=load_rows(manifest,'train',kind)
        training=augment_rows(original,TRAIN_RATIOS)
        stress=augment_rows(original,STRESS_RATIOS)
        subjects=sorted(set(r[0].split('_')[0] for r in original))
        trials=[]
        for bandwidth in BANDWIDTHS:
            for ridge in RIDGES:
                fold_scores={}
                for subject in subjects:
                    tr=[r for r in training if not r[0].startswith(subject+'_')]
                    va=[r for r in stress if r[0].startswith(subject+'_')]
                    fold_scores[subject]=evaluate(va,predictor(fit(tr,bandwidth,ridge)))['clip_balanced_joint_error']
                trials.append(dict(bandwidth=bandwidth,ridge=ridge,subject_errors=fold_scores,
                                   subject_balanced_error=float(np.mean(list(fold_scores.values())))))
        selected=min(trials,key=lambda r:r['subject_balanced_error'])
        params=fit(training,selected['bandwidth'],selected['ridge'])
        linear_trials=[]
        for ridge in RIDGES:
            scores=[]
            for subject in subjects:
                tr=[r for r in training if not r[0].startswith(subject+'_')]
                va=[r for r in stress if r[0].startswith(subject+'_')]
                scores.append(evaluate(va,linear_predictor(fit_linear(tr,ridge)))['clip_balanced_joint_error'])
            linear_trials.append(dict(ridge=ridge,subject_balanced_error=float(np.mean(scores))))
        selected_linear=min(linear_trials,key=lambda r:r['subject_balanced_error'])
        linear=fit_linear(training,selected_linear['ridge'])
        arrays.update({kind+'_'+k:v for k,v in params.items()})
        linear_arrays.update({kind+'_'+k:v for k,v in linear.items()})
        report['limbs'][kind]=dict(original_samples=sum(len(r[1]) for r in original),
            augmented_samples=sum(len(r[1]) for r in training),selection=selected,trials=trials,
            linear_selection=selected_linear,linear_trials=linear_trials)
        print(kind,'SELECTION',selected,'LINEAR',selected_linear,flush=True)
    out=ROOT/'results'
    np.savez_compressed(out/'limb_prior_rff_v3.npz',**arrays)
    np.savez_compressed(out/'limb_prior_linear_v3.npz',**linear_arrays)
    runtime={}
    for kind in ('arm','leg'):
        for key in ('mean','scale','coefficients'):
            runtime[kind+'_'+key]=linear_arrays[kind+'_'+key]
        for key in ('input_min','input_max'):
            runtime[kind+'_'+key]=arrays[kind+'_'+key]
        runtime[kind+'_omega']=np.empty((4,0));runtime[kind+'_phase']=np.empty((0,))
    np.savez_compressed(out/'limb_prior_linear_runtime_v2.npz',**runtime)
    report.update(linear_runtime_sha256=digest(out/'limb_prior_linear_runtime_v2.npz'),model_sha256=digest(out/'limb_prior_rff_v3.npz'),
        linear_sha256=digest(out/'limb_prior_linear_v3.npz'),training_wall_seconds=time.perf_counter()-start)
    (out/'limb_prior_selection_v3.json').write_text(json.dumps(report,indent=2)+'\n')
    print('V3 FROZEN',report['model_sha256'],'SECONDS',round(report['training_wall_seconds'],2),flush=True)

if __name__=='__main__':
    main()
