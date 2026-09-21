"""Frozen-protocol local CPU temporal research; never modifies the released add-on.
SPDX-License-Identifier: GPL-2.0-or-later
"""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','4')
import argparse,hashlib,json,platform,time
from pathlib import Path
import numpy as np
from temporal_data import load_split,validate_manifests
from temporal_model import training_arrays,standardize,fit_ridge,predict,evaluate,selection,gates,residual_loss
from context_network import initialize,Adam

ROOT=Path(__file__).resolve().parent

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def save(path,model):
    values=dict(kind=np.array(model['kind']),mean=model['mean'],std=model['std'])
    values.update(model['params'] if model['kind']=='mlp' else dict(coef=model['coef']))
    np.savez_compressed(path,**values)

def restore(path):
    with np.load(path,allow_pickle=False) as z:
        model=dict(kind=str(z['kind']),mean=z['mean'],std=z['std'])
        if model['kind']=='mlp':model['params']={k:z[k] for k in ('w0','b0','w1','b1')}
        else:model['coef']=z['coef']
    return model

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',default='temporal_query_v1');args=parser.parse_args()
    if not args.output.replace('_','').isalnum():raise ValueError('Use a simple unique research output name')
    output=ROOT/'results'/args.output
    output.mkdir(exist_ok=False)
    start=time.perf_counter();protocol_path=ROOT/'temporal_protocol_v1.json';protocol=json.loads(protocol_path.read_text())
    manifests=[]
    for row in protocol['manifests']:
        path=ROOT/row['path']
        if digest(path)!=row['sha256']:raise ValueError('Source manifest changed')
        manifests.append(json.loads(path.read_text()))
    validate_manifests(manifests)
    provenance={p.name:digest(p) for p in [protocol_path,*[ROOT/name for name in ('temporal_data.py','temporal_model.py','train_temporal_motion.py','context_network.py','bvh_data.py','context_data.py')]]}
    (output/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    train=load_split(ROOT,manifests[0],'train',protocol);validation=load_split(ROOT,manifests[0],'validation',protocol)
    data=training_arrays(train);mean,std=standardize(data)
    print(json.dumps(dict(event='data_ready',train_clips=len(train),validation_clips=len(validation),training_queries=len(data['x']),seconds=time.perf_counter()-start)),flush=True)
    baseline={key:evaluate(validation,lambda d,k=key:d[k]) for key in ('linear','baseline')}
    validation_report=dict(linear=baseline['linear'],hermite=baseline['baseline'])
    ridge_history=[];best_ridge=None;best_score=float('inf')
    for reg in protocol['ridge_trials']:
        candidate=fit_ridge(data,mean,std,reg);report=evaluate(validation,lambda d:predict(candidate,d));score=selection(report)
        ridge_history.append(dict(regularization=reg,score=score));print(json.dumps(dict(event='ridge',regularization=reg,score=score)),flush=True)
        if score<best_score:best_score=score;best_ridge=candidate;validation_report['ridge']=report;ridge_reg=reg
    save(output/'ridge.npz',best_ridge)
    params=initialize(protocol['input_features'],protocol['hidden_units'],protocol['output_features'],protocol['seed'])
    optimizer=Adam(params,protocol['learning_rate']);rng=np.random.default_rng(protocol['seed'])
    z=((data['x']-mean)/std).astype(np.float32);best_score=float('inf');history=[];best_epoch=0
    model=dict(kind='mlp',mean=mean,std=std,params=params)
    for epoch in range(1,protocol['max_epochs']+1):
        losses=[]
        for begin in range(0,len(z),protocol['batch_size']):
            # Random independent batches; explicit weights balance clips, gaps and context conditions.
            if begin==0:order=rng.permutation(len(z))
            idx=order[begin:begin+protocol['batch_size']]
            loss,grad=residual_loss(params,z[idx],data['target'][idx],data['baseline'][idx],data['envelope'][idx],data['weights'][idx],protocol['rotation_loss_weight'])
            if not np.isfinite(loss):raise ValueError('Training diverged')
            optimizer.step(params,grad);losses.append(loss)
        if epoch==1 or epoch%5==0:
            report=evaluate(validation,lambda d:predict(model,d));score=selection(report)
            entry=dict(epoch=epoch,loss=float(np.mean(losses)),score=score,seconds=time.perf_counter()-start);history.append(entry)
            print(json.dumps(dict(event='epoch',**entry)),flush=True)
            if score<best_score:
                best_score=score;best_epoch=epoch;save(output/'mlp.npz',model);validation_report['mlp']=report
            if epoch-best_epoch>=protocol['patience_epochs']:break
    frozen=dict(mlp_sha256=digest(output/'mlp.npz'),ridge_sha256=digest(output/'ridge.npz'),best_epoch=best_epoch,ridge_regularization=ridge_reg,
                selection_split='validation',confirmation_loaded=False,source_sha256=provenance)
    (output/'selection.json').write_text(json.dumps(frozen,indent=2)+'\n')
    print(json.dumps(dict(event='selection_frozen',**frozen)),flush=True)
    # Confirmation motion is parsed only after selection and weights have been persisted.
    mlp=restore(output/'mlp.npz');ridge=restore(output/'ridge.npz')
    confirmation=load_split(ROOT,manifests[1],'confirmation',protocol)
    confirmation_report=dict(linear=evaluate(confirmation,lambda d:d['linear']),hermite=evaluate(confirmation,lambda d:d['baseline']),
                             ridge=evaluate(confirmation,lambda d:predict(ridge,d)),mlp=evaluate(confirmation,lambda d:predict(mlp,d)))
    # Reload equivalence protects reproducibility and the saved model's evaluation evidence.
    reloaded=evaluate(validation,lambda d:predict(mlp,d))
    if abs(selection(reloaded)-selection(validation_report['mlp']))>1e-8:raise ValueError('Reloaded model differs from selection')
    sample=confirmation[0][1];first=time.perf_counter();predict(mlp,sample);cold=time.perf_counter()-first;latencies=[]
    for _ in range(20):
        before=time.perf_counter();predict(mlp,sample);latencies.append(time.perf_counter()-before)
    result=dict(schema=1,status='research_only',goal_status='active_incomplete',protocol=protocol,selection=frozen,training_history=history,ridge_history=ridge_history,
                validation=validation_report,confirmation=confirmation_report,
                gates=dict(validation=gates(validation_report,protocol),confirmation=gates(confirmation_report,protocol)),
                runtime=dict(python=platform.python_version(),numpy=np.__version__,platform=platform.platform(),processor=platform.processor(),
                             blas_threads=os.environ.get('OPENBLAS_NUM_THREADS'),sample_queries=len(sample['x']),first_timed_batch_seconds=cold,
                             warm_batch_p50_seconds=float(np.median(latencies)),warm_batch_p95_seconds=float(np.percentile(latencies,95)),
                             total_seconds=time.perf_counter()-start,training_arrays_bytes=sum(a.nbytes for a in data.values())),
                limits=['No runtime add-on integration or character-rig projection','No contact/style/partial-body input conditioning',
                        'Confirmation clips previously inspected in pose research; not newly blind','No subject-disjoint or large-corpus generalization evidence',
                        'No animator or Cascadeur comparison','Position/orientation raw outputs need consistent kinematic reconstruction'])
    (output/'report.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(event='complete',output=str(output),gates=result['gates'],seconds=result['runtime']['total_seconds'])),flush=True)

if __name__=='__main__':main()
