"""Endpoint-only prior selected by held-out training subjects; independent v2 experiment.

V1 test results motivated this representation and must no longer be called blind.
Fresh confirmation data is loaded only by the separate frozen-model evaluator.
"""
import json
import time
import numpy as np
from train_limb_prior import ROOT,SEED,FEATURES,BANDWIDTHS,RIDGES,digest,features,evaluate,weighted_fit,load_rows


def fit(rows,bandwidth,ridge):
    x=np.concatenate([r[1][:,3:] for r in rows]);y=np.concatenate([r[2] for r in rows])
    weights=np.concatenate([np.full(len(r[1]),1/(len(rows)*len(r[1]))) for r in rows])
    mean=np.sum(x*weights[:,None],axis=0)
    scale=np.maximum(np.sqrt(np.sum((x-mean)**2*weights[:,None],axis=0)),0.05)
    rng=np.random.default_rng(SEED)
    omega=rng.normal(size=(4,FEATURES))/bandwidth;phase=rng.uniform(0,2*np.pi,FEATURES)
    coef=weighted_fit(features(x,mean,scale,omega,phase),y,weights,ridge)
    return dict(mean=mean,scale=scale,omega=omega,phase=phase,coefficients=coef,
                input_min=x.min(axis=0),input_max=x.max(axis=0))


def predictor(params):
    def predict(x):
        return features(x[:,3:],params['mean'],params['scale'],params['omega'],params['phase'])@params['coefficients']
    return predict


def main():
    start=time.perf_counter()
    manifest=json.loads((ROOT/'data_manifest.json').read_text())
    arrays={};report=dict(schema=2,seed=SEED,features=FEATURES,manifest_sha256=digest(ROOT/'data_manifest.json'),
        representation='Endpoint minus limb root / total length (3), upper/total length (1), reflected right to left; body-root features removed',
        selection='Mean of leave-one-training-subject-out clip-balanced errors; no v1 test or confirmation used for parameter selection',
        v1_test_status='Previously observed diagnostic set, not blind confirmation',limbs={})
    for kind in ('arm','leg'):
        rows=load_rows(manifest,'train',kind)
        subjects=sorted(set(r[0].split('_')[0] for r in rows))
        trials=[]
        for bandwidth in BANDWIDTHS:
            for ridge in RIDGES:
                folds={}
                for subject in subjects:
                    tr=[r for r in rows if not r[0].startswith(subject+'_')]
                    va=[r for r in rows if r[0].startswith(subject+'_')]
                    metric=evaluate(va,predictor(fit(tr,bandwidth,ridge)))
                    folds[subject]=metric['clip_balanced_joint_error']
                trials.append(dict(bandwidth=bandwidth,ridge=ridge,subject_errors=folds,
                                   subject_balanced_error=float(np.mean(list(folds.values())))))
        selected=min(trials,key=lambda r:r['subject_balanced_error'])
        params=fit(rows,selected['bandwidth'],selected['ridge'])
        arrays.update({kind+'_'+name:value for name,value in params.items()})
        report['limbs'][kind]=dict(selection=selected,trials=trials,
            validation=evaluate(load_rows(manifest,'validation',kind),predictor(params)))
        print(kind,'selected',selected,flush=True)
    path=ROOT/'results'/'limb_prior_rff_v2.npz'
    np.savez_compressed(path,**arrays)
    report.update(model_sha256=digest(path),model_bytes=path.stat().st_size,training_wall_seconds=time.perf_counter()-start)
    (ROOT/'results'/'limb_prior_selection_v2.json').write_text(json.dumps(report,indent=2)+'\n')
    print('V2 FROZEN',report['model_sha256'],'SECONDS',round(report['training_wall_seconds'],2),flush=True)

if __name__=='__main__':
    main()
