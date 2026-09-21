"""Training-only grouped selection of trajectory loss; one frozen validation candidate."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','4')
from pathlib import Path
import json,hashlib,time,argparse,platform
import numpy as np
import trajectory_predictor as predictor
from semantic_projection import load_windows,project_windows
from motion_coverage import evaluate_predictions
from temporal_model import selection
from sequence_model import acceptance
from crossfit_controller import grouped_folds
ROOT=Path(__file__).resolve().parent

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.write_text(json.dumps(d,indent=2,allow_nan=False)+'\n')
def evaluate(model,windows,skeleton,protocol):
    predictions=[predictor.predict_packed(model,w['observations'],w['t']) for w in windows]
    projected,metrics=project_windows(windows,predictions,skeleton,protocol['projection'])
    report=evaluate_predictions(windows,projected);report['aggregate']['true_edge_length_max']=metrics['true_edge_length_max'];report['projection']=metrics
    return report

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args()
    if not args.output.replace('_','').isalnum():raise ValueError('Simple unique output name required')
    out=ROOT/'results'/args.output;out.mkdir(exist_ok=False);start=time.perf_counter()
    protocol=json.loads((ROOT/'trajectory_motion_protocol_v13.json').read_text())
    for name,h in protocol['source_manifests'].items():assert sha(ROOT/name)==h
    prior=json.loads((ROOT/'results/training_manifest_v4.json').read_text());extra=json.loads((ROOT/'temporal_expansion_manifest_v8.json').read_text())
    manifest=dict(files=prior['files']+[r for r in extra['files'] if r['split']!='confirmation'])
    old=json.loads((ROOT/'results/semantic_motion_v12/report.json').read_text())
    assert protocol['gates']==old['protocol']['gates'] and protocol['projection']==old['protocol']['projection']
    source_names=list(old['source_sha256'])+['trajectory_predictor.py','trajectory_motion_protocol_v13.json','train_trajectory_motion_v13.py','crossfit_controller.py']
    source={name:sha(ROOT/name) for name in source_names};write(out/'protocol.json',protocol);write(out/'manifest.json',manifest)
    train,skeleton=load_windows(ROOT,manifest,'train',protocol);assert len(train)==2912
    folds=grouped_folds(train,protocol['folds']);fold_record=[]
    for training,testing in folds:
        a=sorted({train[i]['clip'] for i in training});b=sorted({train[i]['clip'] for i in testing})
        assert not ({v.split('_')[0] for v in a}&{v.split('_')[0] for v in b})
        fold_record.append(dict(training_clips=a,testing_clips=b,training_windows=len(training),testing_windows=len(testing)))
    write(out/'folds.json',fold_record);history=[]
    print(json.dumps(dict(event='training_ready',windows=len(train),folds=len(folds))),flush=True)
    for index,spec in enumerate(protocol['experiments']):
        prediction=[None]*len(train);diagnostics=[]
        for fold,(training,testing) in enumerate(folds):
            m,d=predictor.fit([train[i] for i in training],spec,protocol['seed'])
            predictor.save(out/('trial_'+str(index)+'_fold_'+str(fold)+'.npz'),m)
            for i in testing:prediction[i]=predictor.predict_packed(m,train[i]['observations'],train[i]['t'])
            diagnostics.append(d)
            print(json.dumps(dict(event='internal_fit',trial=index,fold=fold,diagnostic=d,seconds=time.perf_counter()-start)),flush=True)
        assert all(v is not None for v in prediction)
        report=evaluate_predictions(train,prediction);row=dict(id='trial_'+str(index),experiment=spec,score=selection(report),report=report,training_diagnostics=diagnostics);history.append(row)
        write(out/'internal_trials.json',history)
        print(json.dumps(dict(event='internal_trial',id=row['id'],score=row['score'],position=report['aggregate']['position'])),flush=True)
    winner=min(history,key=lambda r:r['score']);model,diagnostic=predictor.fit(train,winner['experiment'],protocol['seed']);predictor.save(out/'best_learned.npz',model)
    frozen=dict(id=winner['id'],experiment=winner['experiment'],sha256=sha(out/'best_learned.npz'),selection_split='training_only_grouped_out_of_fold',score=winner['score'],final_training_diagnostic=diagnostic,validation_loaded=False,confirmation_read=False)
    write(out/'selection_frozen.json',frozen)
    print(json.dumps(dict(event='model_frozen',selection=frozen)),flush=True)
    validation,vs=load_windows(ROOT,manifest,'validation',protocol);assert len(validation)==480 and vs==skeleton
    reports={}
    for name in ['linear','hermite']:
        reports['projected_'+name]=evaluate(dict(kind='baseline',baseline=name),validation,skeleton,protocol)
        assert reports['projected_'+name]==old['baselines']['projected_'+name],'Unchanged projected control differs from v12'
        print(json.dumps(dict(event='control',name=name,position=reports['projected_'+name]['aggregate']['position'])),flush=True)
    learned=evaluate(model,validation,skeleton,protocol);gate=acceptance(dict(reports,mlp=learned),protocol)
    overall=min(list(reports.items())+[('learned',learned)],key=lambda pair:selection(pair[1]))[0]
    selected_model=model if overall=='learned' else dict(kind='baseline',baseline=overall.removeprefix('projected_'))
    predictor.save(out/'selected.npz',selected_model)
    loaded=predictor.load(out/'best_learned.npz')
    for key in model:np.testing.assert_array_equal(model[key],loaded[key])
    assert all(sha(ROOT/name)==h for name,h in source.items()),'Frozen source changed during experiment'
    selected=dict(id=overall,learned=overall=='learned',sha256=sha(out/'selected.npz'),best_learned_id=winner['id'],best_learned_sha256=frozen['sha256'],selection_split='training-only for learned specification; validation compares fixed candidate with controls',confirmation_read=False)
    report=dict(schema=13,status='research_only',full_goal_complete=False,protocol=protocol,source_sha256=source,selection=selected,frozen_selection=frozen,internal_trials=history,training_windows=len(train),validation_windows=len(validation),baselines=reports,best_learned_report=learned,gates=dict(best_learned=gate),runtime=dict(seconds=time.perf_counter()-start,python=platform.python_version(),numpy=np.__version__,platform=platform.platform(),blas_threads=os.environ['OPENBLAS_NUM_THREADS']),limitations=['Catalog-group folds are not proven independent actors.','Rotation6 trajectory loss is a linear surrogate, not geodesic or dynamics-aware training.','Validation has prior research exposure and is not blind confirmation.','No artifact promoted; actual-rig, human, physics, partial-body and comparative requirements remain separate.'])
    write(out/'selection.json',selected);write(out/'report.json',report)
    print(json.dumps(dict(event='complete',selection=selected,gate=gate,seconds=report['runtime']['seconds'])),flush=True)
if __name__=='__main__':main()
