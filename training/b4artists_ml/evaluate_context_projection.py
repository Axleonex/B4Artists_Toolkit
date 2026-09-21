"""Evaluate learned completion plus identical geometric projection for all baselines.
SPDX-License-Identifier: GPL-2.0-or-later
"""
import json,time
import numpy as np
from train_limb_prior import ROOT,digest
from context_data import load_examples,finish,JOINTS
from context_network import forward
from context_projection import project_pose,project_pose_newton
from train_context_pose import metrics


def models():
    with np.load(ROOT/'results/context_pose_mlp_v1.npz',allow_pickle=False) as a:mlp={k:a[k] for k in a.files}
    with np.load(ROOT/'results/context_pose_linear_v1.npz',allow_pickle=False) as a:linear={k:a[k] for k in a.files}
    return dict(starting_pose=lambda x:np.zeros((len(x),JOINTS*3)),
        linear=lambda x:np.c_[np.ones(len(x)),(x-linear['mean'])/linear['scale']]@linear['coefficients'],
        mlp=lambda x:forward(mlp,((x-mlp['mean'])/mlp['scale']).astype(np.float32)))


def evaluate(rows,predictors,limit=64,projector=project_pose):
    output={name:{} for name in predictors}
    for clip,full in rows:
        ids=np.linspace(0,len(full['x'])-1,min(limit,len(full['x'])),dtype=int)
        d={k:v[ids] for k,v in full.items()}
        for name,predict in predictors.items():
            started=time.perf_counter()
            raw=finish(predict(d['x']),d['baseline'],d['target'],d['mask'])
            projected,stats=projector(raw,d['rest'],d['target'],d['mask'])
            elapsed=time.perf_counter()-started
            residual=(projected-d['baseline']).reshape(len(ids),-1)
            score=metrics([(clip,d)],lambda _:residual)['clips'][clip]
            output[name][clip]=dict(**score,converged=int(stats['converged'].sum()),
                max_length_error=float(stats['max_length_error'].max()),pin_error=float(stats['pin_error'].max()),
                elapsed_ms=elapsed*1000,iterations=stats['iterations'],frames=d['frame'].tolist())
    return {name:dict(clips=clips,hidden_joint_error=float(np.mean([v['hidden_joint_error'] for v in clips.values()])),
        convergence_fraction=sum(v['converged'] for v in clips.values())/sum(v['samples'] for v in clips.values())) for name,clips in output.items()}


def main():
    manifest=json.loads((ROOT/'results/training_manifest_v4.json').read_text())
    report=dict(model_sha256=digest(ROOT/'results/context_pose_mlp_v1.npz'),sample_limit_per_clip=64,
        scope='Validation only, identical reference-length/pin projection applied to all models; no rig evaluation',modes={})
    for mode in ('neutral','prior'):
        rows=load_examples(ROOT,manifest,'validation',seed=20260907,augment=True,mode=mode)
        report['modes'][mode]=evaluate(rows,models(),projector=project_pose_newton)
        print(mode,{k:dict(error=round(v['hidden_joint_error'],5),convergence=round(v['convergence_fraction'],4)) for k,v in report['modes'][mode].items()},flush=True)
    (ROOT/'results/context_projection_validation_newton_v1.json').write_text(json.dumps(report,indent=2)+'\n')

if __name__=='__main__':main()
