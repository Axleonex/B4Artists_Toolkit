"""Expanded-data proportion model. All choices use training/validation only.
SPDX-License-Identifier: GPL-2.0-or-later
"""
import json,time
import numpy as np
from train_limb_prior import ROOT,BANDWIDTHS,RIDGES,digest,load_rows,evaluate
from train_limb_prior_v2 import fit,predictor
from train_limb_prior_v3 import fit_linear,linear_predictor
from augment_limb import augment_rows,TRAIN_RATIOS,STRESS_RATIOS


def main():
    start=time.perf_counter()
    original=json.loads((ROOT/'data_manifest.json').read_text())
    expansion=json.loads((ROOT/'expansion_manifest.json').read_text())
    files=original['files']+expansion['files']
    if len({r['clip'] for r in files})!=len(files):raise ValueError('Overlapping expansion')
    snapshot=dict(files=[r for r in files if r['split'] in ('train','validation')])
    snapshot_path=ROOT/'results'/'training_manifest_v4.json'
    snapshot_path.write_text(json.dumps(snapshot,indent=2)+'\n')
    manifest=snapshot
    arrays={};baseline_arrays={};report=dict(schema=4,training_ratios=TRAIN_RATIOS,validation_ratios=STRESS_RATIOS,
        selection='Select hyperparameters by clip-balanced original+retargeted validation error. Select RFF only if at least 10% better than equally trained linear model.',
        training_manifest_sha256=digest(snapshot_path),
        confirmation_status='New subject-number 29 clips not loaded by training; all earlier test sets diagnostic only',limbs={})
    for kind in ('arm','leg'):
        training=augment_rows(load_rows(manifest,'train',kind),TRAIN_RATIOS)
        validation=augment_rows(load_rows(manifest,'validation',kind),STRESS_RATIOS)
        rff_trials=[];best=None
        for bandwidth in BANDWIDTHS:
            for ridge in RIDGES:
                params=fit(training,bandwidth,ridge)
                score=evaluate(validation,predictor(params))['clip_balanced_joint_error']
                rff_trials.append(dict(bandwidth=bandwidth,ridge=ridge,error=score))
                if best is None or score<best[0]:best=(score,params,bandwidth,ridge)
        linear_trials=[];best_linear=None
        for ridge in RIDGES:
            params=fit_linear(training,ridge)
            score=evaluate(validation,linear_predictor(params))['clip_balanced_joint_error']
            linear_trials.append(dict(ridge=ridge,error=score))
            if best_linear is None or score<best_linear[0]:best_linear=(score,params,ridge)
        nonlinear=best[0]<=best_linear[0]*.9
        params=best[1]
        if not nonlinear:
            linear=best_linear[1]
            params=dict(mean=linear['mean'],scale=linear['scale'],coefficients=linear['coefficients'],
                        omega=np.empty((4,0)),phase=np.empty((0,)),input_min=best[1]['input_min'],input_max=best[1]['input_max'])
        arrays.update({kind+'_'+k:v for k,v in params.items()})
        baseline_arrays.update({kind+'_'+k:v for k,v in best_linear[1].items()})
        report['limbs'][kind]=dict(selected='rff' if nonlinear else 'linear',rff_trials=rff_trials,linear_trials=linear_trials,
            best_rff_error=best[0],best_linear_error=best_linear[0],training_samples=sum(len(r[1]) for r in training))
        print(kind,report['limbs'][kind]['selected'],'RFF',best[0],'LINEAR',best_linear[0],flush=True)
    out=ROOT/'results'
    np.savez_compressed(out/'limb_prior_selected_v4.npz',**arrays)
    np.savez_compressed(out/'limb_prior_linear_v4.npz',**baseline_arrays)
    report.update(model_sha256=digest(out/'limb_prior_selected_v4.npz'),training_wall_seconds=time.perf_counter()-start)
    (out/'limb_prior_selection_v4.json').write_text(json.dumps(report,indent=2)+'\n')
    print('V4 FROZEN',report['model_sha256'],'SECONDS',round(report['training_wall_seconds'],2),flush=True)

if __name__=='__main__':main()
