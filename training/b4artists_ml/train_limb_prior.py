"""Reproducible independent random-Fourier ridge limb prior. No external ML service.

Selection uses validation clips only. Test clips are evaluated after model freeze.
Loss balances clips rather than giving long recordings disproportionate influence.
"""
import hashlib
import json
import platform
import time
from pathlib import Path
import numpy as np
from bvh_data import parse_bvh, limb_samples

ROOT=Path(__file__).resolve().parent
SEED=20260906
FEATURES=256
BANDWIDTHS=(0.5,1.0,2.0,4.0)
RIDGES=(1e-5,1e-4,1e-3,1e-2)

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def load_rows(manifest,split,kind):
    rows=[]
    for row in manifest['files']:
        if row['split']!=split:
            continue
        path=ROOT/'cache'/(row['clip']+'.bvh')
        if digest(path)!=row['sha256']:
            raise ValueError('Motion checksum differs: '+row['clip'])
        x,y,g=limb_samples(parse_bvh(path.read_text()))[kind]
        rows.append((row['clip'],x,y,g))
    return rows

def project(predicted,axis):
    plane=predicted-axis*np.sum(predicted*axis,axis=1,keepdims=True)
    length=np.linalg.norm(plane,axis=1,keepdims=True)
    # A deterministic perpendicular for degenerate predictions, counted in evidence.
    pick=np.eye(3)[np.argmin(np.abs(axis),axis=1)]
    fallback=np.cross(axis,pick)
    fallback/=np.maximum(np.linalg.norm(fallback,axis=1,keepdims=True),1e-12)
    return np.where(length>1e-8,plane/np.maximum(length,1e-8),fallback)

def features(x,mean,scale,omega,phase):
    z=(x-mean)/scale
    return np.concatenate((np.ones((len(x),1)),z,
        np.cos(z@omega+phase)*np.sqrt(2/len(phase))),axis=1)

def evaluate(rows,predict):
    clips={}
    for clip,x,y,g in rows:
        raw=predict(x)
        pred=project(raw,g[:,:3])
        errors=np.linalg.norm(pred-y,axis=1)*g[:,3]
        angles=np.rad2deg(np.arccos(np.clip(np.sum(pred*y,axis=1),-1,1)))
        clips[clip]=dict(samples=len(x),joint_error_fraction_mean=float(np.mean(errors)),
            joint_error_fraction_p95=float(np.percentile(errors,95)),
            bend_angle_degrees_mean=float(np.mean(angles)))
    return dict(clip_balanced_joint_error=float(np.mean([r['joint_error_fraction_mean'] for r in clips.values()])),
                clip_balanced_angle_degrees=float(np.mean([r['bend_angle_degrees_mean'] for r in clips.values()])),clips=clips)

def weighted_fit(phi,y,weights,ridge):
    lhs=phi.T@(phi*weights[:,None])
    penalty=np.full(phi.shape[1],ridge);penalty[0]=1e-10
    lhs.flat[::len(lhs)+1]+=penalty
    return np.linalg.solve(lhs,phi.T@(y*weights[:,None]))

def train():
    started=time.perf_counter()
    manifest=json.loads((ROOT/'data_manifest.json').read_text())
    clip_ids=[r['clip'] for r in manifest['files']]
    if len(set(clip_ids))!=len(clip_ids):
        raise ValueError('Overlapping clip splits')
    out=ROOT/'results';out.mkdir(exist_ok=True)
    arrays={};report=dict(schema=1,seed=SEED,random_features=FEATURES,
        model='Independent random Fourier features plus linear terms, clip-balanced ridge regression',
        selection='Minimize clip-balanced normalized joint error on validation; test excluded until freeze',
        manifest_sha256=digest(ROOT/'data_manifest.json'),stride=8,excluded_first_frame=True,
        excluded_near_straight_height_fraction=0.025,
        normalization='Hip midpoint origin, left hip axis, projected shoulder-up axis; right reflected to left; total limb length units',
        hardware=platform.processor(),python=platform.python_version(),numpy=np.__version__,limbs={})
    for kind in ('arm','leg'):
        train_rows=load_rows(manifest,'train',kind)
        val_rows=load_rows(manifest,'validation',kind)
        x=np.concatenate([r[1] for r in train_rows]);y=np.concatenate([r[2] for r in train_rows])
        weights=np.concatenate([np.full(len(r[1]),1/(len(train_rows)*len(r[1]))) for r in train_rows])
        mean=np.sum(x*weights[:,None],axis=0)
        scale=np.maximum(np.sqrt(np.sum((x-mean)**2*weights[:,None],axis=0)),0.02)
        rng=np.random.default_rng(SEED)
        omega0=rng.normal(size=(7,FEATURES));phase=rng.uniform(0,2*np.pi,FEATURES)
        trials=[];best=None
        for bandwidth in BANDWIDTHS:
            omega=omega0/bandwidth
            phi=features(x,mean,scale,omega,phase)
            for ridge in RIDGES:
                coefficients=weighted_fit(phi,y,weights,ridge)
                metric=evaluate(val_rows,lambda v:features(v,mean,scale,omega,phase)@coefficients)
                score=metric['clip_balanced_joint_error']
                trials.append(dict(bandwidth=bandwidth,ridge=ridge,validation_error=score))
                if best is None or score<best[0]:
                    best=(score,bandwidth,ridge,omega.copy(),coefficients.copy())
        score,bandwidth,ridge,omega,coefficients=best
        # Freeze everything before loading held-out test rows.
        mean_output=np.sum(y*weights[:,None],axis=0)
        linear_phi=np.concatenate((np.ones((len(x),1)),(x-mean)/scale),axis=1)
        linear_trials=[]
        for reg in RIDGES:
            fit=weighted_fit(linear_phi,y,weights,reg)
            metric=evaluate(val_rows,lambda v:np.c_[np.ones(len(v)),(v-mean)/scale]@fit)
            linear_trials.append((metric['clip_balanced_joint_error'],reg,fit))
        _,linear_ridge,linear_coef=min(linear_trials,key=lambda v:v[0])
        params=dict(mean=mean,scale=scale,omega=omega,phase=phase,coefficients=coefficients,
                    input_min=x.min(axis=0),input_max=x.max(axis=0),mean_output=mean_output,
                    linear_coefficients=linear_coef)
        arrays.update({kind+'_'+name:value for name,value in params.items()})
        predictors={
            'fixed_anatomical':lambda v,k=kind:np.tile([0,1 if k=='arm' else -1,0],(len(v),1)),
            'trained_mean':lambda v:np.tile(mean_output,(len(v),1)),
            'linear':lambda v:np.c_[np.ones(len(v)),(v-mean)/scale]@linear_coef,
            'rff':lambda v:features(v,mean,scale,omega,phase)@coefficients}
        evaluations={}
        for split,rows in (('validation',val_rows),('test',load_rows(manifest,'test',kind))):
            evaluations[split]={name:evaluate(rows,pred) for name,pred in predictors.items()}
        report['limbs'][kind]=dict(training_samples=len(x),bandwidth=bandwidth,ridge=ridge,
            linear_ridge=linear_ridge,selection_trials=trials,evaluations=evaluations)
        print(kind,'selected',bandwidth,ridge,'test errors',
            {name:round(value['clip_balanced_joint_error'],5) for name,value in evaluations['test'].items()},flush=True)
    # Store numeric arrays only: loading must use allow_pickle=False.
    model_path=out/'limb_prior_rff_v1.npz'
    np.savez_compressed(model_path,**arrays)
    report.update(model_sha256=digest(model_path),model_bytes=model_path.stat().st_size,
                  training_wall_seconds=time.perf_counter()-started,
                  limitations=['Single-frame bend prior only; no spine/head prediction or temporal motion',
                    'Small subset with few subjects and capture-specific shoulder offsets',
                    'Test subjects 16 and 35 held out; test 13_20 shares subject 13 with training',
                    'Error reconstructs the joint using known lengths and endpoints; no orientation/contact/visual quality evidence',
                    'No direct Cascadeur comparison; no claim of whole-body completion'])
    (out/'limb_prior_evaluation_v1.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('MODEL',model_path,'BYTES',report['model_bytes'],'SECONDS',round(report['training_wall_seconds'],2),flush=True)

if __name__=='__main__':
    train()
