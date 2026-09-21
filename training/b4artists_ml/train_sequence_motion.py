"""Local full-sequence training; outputs remain research artifacts until gates pass.
SPDX-License-Identifier: GPL-2.0-or-later
"""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','4')
import argparse,hashlib,json,time,platform
from pathlib import Path
import numpy as np
from context_network import initialize,Adam
from temporal_data import validate_manifests
from temporal_model import selection
from sequence_data import load_windows
from sequence_model import statistics,fit_ridge,batch_loss,evaluate_windows,acceptance
from train_temporal_motion import save,restore

ROOT=Path(__file__).resolve().parent

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',default='sequence_motion_v2');args=parser.parse_args()
    if not args.output.replace('_','').isalnum():raise ValueError('Use a simple unique output directory')
    output=ROOT/'results'/args.output;output.mkdir(exist_ok=False);started=time.perf_counter()
    p=json.loads((ROOT/'sequence_protocol_v2.json').read_text());manifests=[]
    for row in p['manifests']:
        path=ROOT/row['path']
        if digest(path)!=row['sha256']:raise ValueError('Source manifest mismatch')
        manifests.append(json.loads(path.read_text()))
    validate_manifests(manifests)
    provenance={name:digest(ROOT/name) for name in ('sequence_protocol_v2.json','sequence_data.py','sequence_kinematics.py','sequence_model.py','train_sequence_motion.py','context_network.py','temporal_data.py','temporal_model.py','train_temporal_motion.py','bvh_data.py','context_data.py')}
    (output/'protocol.json').write_text(json.dumps(p,indent=2)+'\n')
    train,skeleton=load_windows(ROOT,manifests[0],'train',p);validation,vs=load_windows(ROOT,manifests[0],'validation',p)
    if vs!=skeleton:raise ValueError('Validation topology mismatch')
    x,weight,mean,std=statistics(train)
    print(json.dumps(dict(event='data_ready',train_windows=len(train),validation_windows=len(validation),inputs=x.shape[1],joints=len(skeleton[0]),seconds=time.perf_counter()-started)),flush=True)
    validation_report={name:evaluate_windows(validation,skeleton,name) for name in p['baselines'] if name!='ridge'}
    ridge_trials=[];best_score=float('inf');best_reg=None
    for reg in p['ridge_trials']:
        model=fit_ridge(train,x,weight,mean,std,reg);report=evaluate_windows(validation,skeleton,'ridge',model);score=selection(report)
        ridge_trials.append(dict(regularization=reg,score=score));print(json.dumps(dict(event='ridge',**ridge_trials[-1])),flush=True)
        if score<best_score:best_score=score;best_reg=reg;save(output/'ridge.npz',model);validation_report['ridge']=report
    params=initialize(x.shape[1],p['hidden_units'],p['terms']*train[0]['baseline'].shape[-1],p['seed']);params['w1'][:]=0
    model=dict(kind='mlp',mean=mean,std=std,params=params);optimizer=Adam(params,p['learning_rate'])
    validation_report['mlp']=evaluate_windows(validation,skeleton,'mlp',model)
    best_score=selection(validation_report['mlp']);best_epoch=0;history=[dict(epoch=0,score=best_score,loss=None,seconds=time.perf_counter()-started)]
    save(output/'mlp.npz',model);print(json.dumps(dict(event='epoch',**history[-1])),flush=True)
    groups={gap:{} for gap in p['gaps']}
    for i,w in enumerate(train):groups[w['gap']].setdefault((w['clip'],w['context']),[]).append(i)
    rng=np.random.default_rng(p['seed']);steps=int(np.ceil(len(train)/p['batch_size']));clipped=0
    for epoch in range(1,p['max_epochs']+1):
        losses=[]
        for step in range(steps):
            gap=p['gaps'][(step+(epoch-1)*steps)%len(p['gaps'])];cohorts=list(groups[gap].values())
            indices=[rng.choice(cohorts[i]) for i in rng.integers(0,len(cohorts),p['batch_size'])]
            loss,grad=batch_loss(model,[train[i] for i in indices],skeleton,p)
            if not np.isfinite(loss):raise ValueError('Sequence training diverged')
            norm=np.sqrt(sum(np.sum(g*g) for g in grad.values()))
            if norm>p['gradient_norm_max']:
                grad={k:g*(p['gradient_norm_max']/norm) for k,g in grad.items()};clipped+=1
            optimizer.step(params,grad);losses.append(loss)
        if epoch==1 or epoch%p['validate_every']==0:
            report=evaluate_windows(validation,skeleton,'mlp',model);score=selection(report)
            entry=dict(epoch=epoch,loss=float(np.mean(losses)),score=score,seconds=time.perf_counter()-started);history.append(entry)
            print(json.dumps(dict(event='epoch',**entry)),flush=True)
            if score<best_score:best_score=score;best_epoch=epoch;save(output/'mlp.npz',model);validation_report['mlp']=report
            if epoch-best_epoch>=p['patience_epochs']:break
    # Save last trained weights too, including when the zero-residual model wins.
    save(output/'last_trained.npz',model)
    frozen=dict(best_epoch=best_epoch,ridge_regularization=best_reg,mlp_sha256=digest(output/'mlp.npz'),ridge_sha256=digest(output/'ridge.npz'),last_trained_sha256=digest(output/'last_trained.npz'),
                source_sha256=provenance,selection_split='validation',observed_development_loaded=False,skeleton=dict(names=skeleton[0],parents=skeleton[1],semantic=skeleton[2]))
    (output/'selection.json').write_text(json.dumps(frozen,indent=2)+'\n');print(json.dumps(dict(event='selection_frozen',best_epoch=best_epoch)),flush=True)
    mlp=restore(output/'mlp.npz');ridge=restore(output/'ridge.npz')
    reloaded=evaluate_windows(validation,skeleton,'mlp',mlp)
    if abs(selection(reloaded)-selection(validation_report['mlp']))>1e-8:raise ValueError('Saved model does not reproduce validation')
    development,ds=load_windows(ROOT,manifests[1],'confirmation',p)
    if ds!=skeleton:raise ValueError('Observed-development topology mismatch')
    development_report={name:evaluate_windows(development,skeleton,name,ridge if name=='ridge' else None) for name in p['baselines']}
    development_report['mlp']=evaluate_windows(development,skeleton,'mlp',mlp)
    result=dict(schema=2,status='research_only',goal_status='active_incomplete',protocol=p,selection=frozen,training_history=history,ridge_history=ridge_trials,
                validation=validation_report,observed_development=development_report,
                gates=dict(validation=acceptance(validation_report,p),observed_development=acceptance(development_report,p)),
                runtime=dict(seconds=time.perf_counter()-started,python=platform.python_version(),numpy=np.__version__,platform=platform.platform(),blas_threads=os.environ['OPENBLAS_NUM_THREADS'],gradient_clipped_steps=clipped),
                counts=dict(training_windows=len(train),validation_windows=len(validation),observed_development_windows=len(development),parameters=sum(v.size for v in params.values())),
                limitations=['No new blind confirmation data','Source BVH hierarchy is not a finished BoneForge/Rigify adapter','No contacts, style, partial edits or multiple interior priority poses in model inputs',
                             'Hard endpoint values do not guarantee cross-window derivative continuity','No animator or Cascadeur comparison','No release or runtime integration'])
    (output/'report.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(event='complete',seconds=result['runtime']['seconds'],best_epoch=best_epoch,gates=result['gates'])),flush=True)

if __name__=='__main__':main()
