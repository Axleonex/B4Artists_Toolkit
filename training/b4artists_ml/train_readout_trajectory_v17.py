"""Frozen training-only convex readout selection, then one validation candidate."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','4')
from pathlib import Path
import json,hashlib,time,argparse,platform
import numpy as np
import boundary_trajectory as predictor
from readout_trajectory import fit_readout
from semantic_projection import load_windows
from motion_coverage import evaluate_predictions
from temporal_model import selection
from sequence_model import acceptance
from crossfit_controller import grouped_folds
from train_boundary_trajectory_v16 import evaluate
ROOT=Path(__file__).resolve().parent

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.write_text(json.dumps(d,indent=2,allow_nan=False)+'\n')
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args()
    if not args.output.replace('_','').isalnum():raise ValueError('Simple unique output name required')
    out=ROOT/'results'/args.output;out.mkdir(exist_ok=False);start=time.perf_counter()
    experiment=json.loads((ROOT/'readout_trajectory_protocol_v17.json').read_text())
    protocol=json.loads((ROOT/'boundary_trajectory_protocol_v16.json').read_text());assert sha(ROOT/'boundary_trajectory_protocol_v16.json')==experiment['parent_protocol_sha256']
    for name,h in experiment['prior_models'].items():assert sha(ROOT/name)==h
    old=json.loads((ROOT/'results/boundary_trajectory_v16/report.json').read_text())
    for name,h in old['source_sha256'].items():assert sha(ROOT/name)==h
    sources=set(old['source_sha256'])|{'readout_trajectory.py','readout_trajectory_protocol_v17.json','train_readout_trajectory_v17.py'}
    hashes={n:sha(ROOT/n) for n in sorted(sources)}
    manifest=json.loads((ROOT/'results/boundary_trajectory_v16/manifest.json').read_text())
    write(out/'protocol.json',experiment);write(out/'manifest.json',manifest)
    train,skeleton=load_windows(ROOT,manifest,'train',protocol);assert len(train)==2912
    folds=grouped_folds(train,4);spec=old['frozen_selection']['experiment'];history=[]
    print(json.dumps(dict(event='training_ready',windows=len(train))),flush=True)
    for index,reg in enumerate(experiment['regularizations']):
        predictions=[None]*len(train);diagnostics=[]
        for fold,(training,testing) in enumerate(folds):
            parent=predictor.load(ROOT/f'results/boundary_trajectory_v16/trial_2_fold_{fold}.npz')
            model,diagnostic=fit_readout([train[i] for i in training],parent,spec,reg)
            predictor.save(out/f'trial_{index}_fold_{fold}.npz',model)
            for i in testing:predictions[i]=predictor.predict_packed(model,train[i]['observations'],train[i]['t'])
            diagnostics.append(diagnostic)
            print(json.dumps(dict(event='readout_fit',trial=index,fold=fold,diagnostic=diagnostic,seconds=time.perf_counter()-start)),flush=True)
        report=evaluate_predictions(train,predictions);row=dict(id=f'trial_{index}',regularization=reg,score=selection(report),report=report,training_diagnostics=diagnostics);history.append(row);write(out/'internal_trials.json',history)
        print(json.dumps(dict(event='internal_trial',id=row['id'],score=row['score'],position=report['aggregate']['position'])),flush=True)
    winner=min(history,key=lambda r:r['score']);parent=predictor.load(ROOT/'results/boundary_trajectory_v16/best_learned.npz')
    model,diag=fit_readout(train,parent,spec,winner['regularization']);predictor.save(out/'best_learned.npz',model)
    frozen=dict(id=winner['id'],regularization=winner['regularization'],sha256=sha(out/'best_learned.npz'),score=winner['score'],selection_split='training_only_grouped_out_of_fold',validation_loaded=False,confirmation_read=False,final_training_diagnostic=diag)
    write(out/'selection_frozen.json',frozen);print(json.dumps(dict(event='frozen',selection=frozen)),flush=True)
    validation,vs=load_windows(ROOT,manifest,'validation',protocol);assert len(validation)==480 and vs==skeleton
    reports={}
    for name in ['linear','hermite']:
        reports['projected_'+name]=evaluate(dict(kind='baseline',baseline=name),validation,skeleton,protocol)
        assert reports['projected_'+name]==old['baselines']['projected_'+name]
    learned=evaluate(model,validation,skeleton,protocol);gate=acceptance(dict(reports,mlp=learned),protocol)
    overall=min(list(reports.items())+[('learned',learned)],key=lambda p:selection(p[1]))[0]
    selected_model=model if overall=='learned' else dict(kind='baseline',baseline=overall.removeprefix('projected_'));predictor.save(out/'selected.npz',selected_model)
    assert all(sha(ROOT/n)==h for n,h in hashes.items());assert all(sha(ROOT/n)==h for n,h in experiment['prior_models'].items())
    report=dict(schema=17,status='research_only',full_goal_complete=False,protocol=protocol,experiment=experiment,source_sha256=hashes,frozen_selection=frozen,selection=dict(id=overall,learned=overall=='learned',sha256=sha(out/'selected.npz'),best_learned_sha256=frozen['sha256']),internal_trials=history,training_windows=len(train),validation_windows=len(validation),baselines=reports,best_learned_report=learned,gates=dict(best_learned=gate),runtime=dict(seconds=time.perf_counter()-start,python=platform.python_version(),numpy=np.__version__,blas_threads=os.environ['OPENBLAS_NUM_THREADS']),limitations=['Validation is previously exposed research data, not blind confirmation.','Frozen supervised hidden features inherited from matching v16 training folds.','Readout is learned; analytic fit alone establishes no quality, actual-rig, human or comparative acceptance.','No runtime changes or model promotion.'])
    write(out/'report.json',report);print(json.dumps(dict(event='complete',selection=report['selection'],gate=gate,seconds=report['runtime']['seconds'])),flush=True)
if __name__=='__main__':main()
