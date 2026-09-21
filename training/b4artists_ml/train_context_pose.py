"""Train an independent contextual sparse-body network and linear ablations.
SPDX-License-Identifier: GPL-2.0-or-later
"""
import json,time,platform
import numpy as np
from train_limb_prior import ROOT,digest
from context_data import load_examples,finish,JOINTS,PARENTS,LIMBS
from context_network import initialize,forward,loss_and_grad,Adam

SEED=20260906


def merge(rows):
    data={k:np.concatenate([r[1][k] for r in rows]) for k in rows[0][1]}
    data['weights']=np.concatenate([np.full(len(d['x']),1/(len(rows)*len(d['x']))) for _,d in rows])
    return data


def metrics(rows,predict):
    results={}
    for clip,d in rows:
        pred=finish(predict(d['x']),d['baseline'],d['target'],d['mask'])
        if not np.isfinite(pred).all():raise ValueError('Nonfinite contextual prediction')
        errors=np.linalg.norm(pred-d['target'],axis=-1)
        hidden=~d['mask'];pin=errors[d['mask']]
        bone_errors=[]
        for child,parent in enumerate(PARENTS):
            if parent<0:continue
            reference=np.linalg.norm(d['rest'][:,child]-d['rest'][:,parent],axis=-1)
            actual=np.linalg.norm(pred[:,child]-pred[:,parent],axis=-1)
            bone_errors.extend(np.abs(actual/reference-1).tolist())
        results[clip]=dict(samples=len(pred),hidden_joint_error=float(np.mean(errors[hidden])),
            elbow_error=float(np.mean(errors[:,[6,9]])),knee_error=float(np.mean(errors[:,[12,15]])),
            max_pin_error=float(np.max(pin)),mean_length_change=float(np.mean(bone_errors)),
            p95_length_change=float(np.percentile(bone_errors,95)))
    return dict(hidden_joint_error=float(np.mean([v['hidden_joint_error'] for v in results.values()])),
                elbow_error=float(np.mean([v['elbow_error'] for v in results.values()])),
                knee_error=float(np.mean([v['knee_error'] for v in results.values()])),clips=results)


def fit_linear(data,mean,scale,ridge,local_only=False):
    phi=np.c_[np.ones(len(data['x'])),(data['x']-mean)/scale]
    residual=(data['target']-data['baseline']).reshape(len(phi),-1)
    coef=np.zeros((phi.shape[1],JOINTS*3))
    # Controlled linear ablation: same rest and baseline; only own effector observed
    # when predicting an elbow/knee. Other body outputs retain the same context.
    local_end={6:7,9:10,12:13,15:16}
    for joint in range(JOINTS):
        weights=data['weights']*(~data['mask'][:,joint])
        if np.sum(weights)==0:continue
        columns=np.arange(phi.shape[1])
        if local_only and joint in local_end:
            end=local_end[joint]
            columns=np.r_[np.arange(1+JOINTS*6),1+JOINTS*6+np.arange(end*3,end*3+3),1+JOINTS*9+end]
        a=phi[:,columns]
        lhs=a.T@(a*weights[:,None]);lhs.flat[::len(lhs)+1]+=ridge
        rhs=a.T@(residual[:,joint*3:joint*3+3]*weights[:,None])
        coef[np.ix_(columns,np.arange(joint*3,joint*3+3))]=np.linalg.solve(lhs,rhs)
    return coef


def main():
    started=time.perf_counter()
    manifest_path=ROOT/'results'/'training_manifest_v4.json'
    manifest=json.loads(manifest_path.read_text())
    training=load_examples(ROOT,manifest,'train',seed=SEED,augment=True,mode='mixed')
    validation={mode:load_examples(ROOT,manifest,'validation',seed=SEED+1,augment=True,mode=mode) for mode in ('neutral','prior')}
    data=merge(training);x=data['x'];weights=data['weights']
    mean=np.sum(x*weights[:,None],axis=0);scale=np.maximum(np.sqrt(np.sum((x-mean)**2*weights[:,None],axis=0)),.1)
    z=((x-mean)/scale).astype(np.float32)
    target=(data['target']-data['baseline']).reshape(len(x),-1).astype(np.float32)
    hidden=np.repeat(~data['mask'],3,axis=1).astype(np.float32)
    report=dict(schema=1,seed=SEED,input_features=170,output_features=51,hidden_units=128,
        representation='17 synchronized joints; explicit observed position mask, reference skeleton, and neutral/strictly-earlier starting pose; supplied pelvis translation/orientation',
        training_manifest_sha256=digest(manifest_path),training_samples=len(x),numpy=np.__version__,python=platform.python_version(),
        hardware=platform.processor(),selection='Mean neutral and prior validation hidden-joint error; no diagnostic/confirmation values used',
        units='Reference torso length; no direct comparison to earlier total-limb-length metrics',linear_trials=[],epochs=[])
    def score(fn):
        vals={mode:metrics(rows,fn) for mode,rows in validation.items()}
        return float(np.mean([v['hidden_joint_error'] for v in vals.values()])),vals
    best_linear=None
    for ridge in (1e-4,1e-3,1e-2):
        coef=fit_linear(data,mean,scale,ridge)
        value,vals=score(lambda v:np.c_[np.ones(len(v)),(v-mean)/scale]@coef)
        report['linear_trials'].append(dict(ridge=ridge,error=value))
        if best_linear is None or value<best_linear[0]:best_linear=(value,coef.copy(),ridge,vals)
    ablation=fit_linear(data,mean,scale,best_linear[2],local_only=True)
    _,ablation_metrics=score(lambda v:np.c_[np.ones(len(v)),(v-mean)/scale]@ablation)
    report['validation_linear']=best_linear[3];report['validation_local_linear']=ablation_metrics
    _,base_metrics=score(lambda v:np.zeros((len(v),JOINTS*3)))
    report['validation_starting_pose']=base_metrics
    params=initialize(170,128,51,SEED);optimizer=Adam(params,.001)
    rng=np.random.default_rng(SEED)
    best=None;steps=max(1,int(np.ceil(len(x)/256)))
    for epoch in range(1,101):
        losses=[]
        for _ in range(steps):
            ids=rng.choice(len(x),256,p=weights)
            loss,gradient=loss_and_grad(params,z[ids],target[ids],hidden[ids])
            optimizer.step(params,gradient);losses.append(loss)
        if epoch%5==0 or epoch==1:
            value,vals=score(lambda v:forward(params,((v-mean)/scale).astype(np.float32)))
            report['epochs'].append(dict(epoch=epoch,training_loss=float(np.mean(losses)),validation_error=value))
            if best is None or value<best[0]:best=(value,{k:v.copy() for k,v in params.items()},epoch,vals)
            print('epoch',epoch,'validation',round(value,6),'linear',round(best_linear[0],6),flush=True)
            if epoch-best[2]>=25:break
    out=ROOT/'results'
    np.savez_compressed(out/'context_pose_mlp_v1.npz',mean=mean,scale=scale,**best[1])
    np.savez_compressed(out/'context_pose_linear_v1.npz',mean=mean,scale=scale,coefficients=best_linear[1],local_coefficients=ablation)
    report.update(selected_epoch=best[2],validation_mlp=best[3],model_sha256=digest(out/'context_pose_mlp_v1.npz'),
        linear_sha256=digest(out/'context_pose_linear_v1.npz'),training_wall_seconds=time.perf_counter()-started,
        limitations=['No rig constraint projection, joint limits or physics','Visible pins are copied exactly in coordinate output, not validated rig controls',
        'No hand orientation or animator pole observations yet','Current experiment is static completion, not learned inbetweening',
        'No new blind confirmation or visual acceptance yet'])
    (out/'context_pose_training_v1.json').write_text(json.dumps(report,indent=2)+'\n')
    print('CONTEXT FROZEN',report['model_sha256'],'BEST_EPOCH',best[2],'SECONDS',round(report['training_wall_seconds'],2),flush=True)

if __name__=='__main__':main()
