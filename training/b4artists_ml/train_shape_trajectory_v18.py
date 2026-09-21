"""One fixed learned reference experiment; grouped diagnostics before validation."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','4')
from pathlib import Path
import json,hashlib,time,argparse,platform
import numpy as np
import shape_trajectory as predictor
from shape_readout import fit_readout
from semantic_projection import load_windows,project_windows
from motion_coverage import evaluate_predictions
from temporal_model import selection
from sequence_model import acceptance
from crossfit_controller import grouped_folds
ROOT=Path(__file__).resolve().parent

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.write_text(json.dumps(d,indent=2,allow_nan=False)+'\n')
def evaluate(model,windows,skeleton,protocol):
    pred=[predictor.predict_packed(model,w['observations'],w['t']) for w in windows];projected,metrics=project_windows(windows,pred,skeleton,protocol['projection']);report=evaluate_predictions(windows,projected);report['aggregate']['true_edge_length_max']=metrics['true_edge_length_max'];report['projection']=metrics;return report

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args()
    if not args.output.replace('_','').isalnum():raise ValueError('Simple unique output name required')
    out=ROOT/'results'/args.output;out.mkdir(exist_ok=False);start=time.perf_counter()
    protocol=json.loads((ROOT/'shape_trajectory_protocol_v18.json').read_text());old=json.loads((ROOT/'results/readout_trajectory_v17/report.json').read_text())
    assert protocol['gates']==old['protocol']['gates'] and protocol['projection']==old['protocol']['projection']
    for name,h in protocol['source_manifests'].items():assert sha(ROOT/name)==h
    assert sha(ROOT/'boundary_trajectory_protocol_v16.json')==protocol['prior_protocol_sha256']
    assert sha(ROOT/'results/readout_trajectory_v17/best_learned.npz')==protocol['prior_model_sha256']
    for name,h in old['source_sha256'].items():assert sha(ROOT/name)==h
    sources=set(old['source_sha256'])|{'shape_reference.py','shape_trajectory.py','shape_readout.py','shape_trajectory_protocol_v18.json','train_shape_trajectory_v18.py'};hashes={n:sha(ROOT/n) for n in sorted(sources)}
    manifest=json.loads((ROOT/'results/boundary_trajectory_v16/manifest.json').read_text());write(out/'protocol.json',protocol);write(out/'manifest.json',manifest)
    train,skeleton=load_windows(ROOT,manifest,'train',protocol);assert len(train)==2912;folds=grouped_folds(train,4);spec=protocol['experiments'][0];assert len(protocol['experiments'])==1
    oof=[None]*len(train);diagnostics=[];fold_records=[]
    print(json.dumps(dict(event='training_ready',windows=len(train))),flush=True)
    for fold,(training,testing) in enumerate(folds):
        rows=[train[i] for i in training];hidden,d=predictor.fit(rows,spec,protocol['seed']);model,rd=fit_readout(rows,hidden,spec,protocol['readout_regularization']);predictor.save(out/f'fold_{fold}.npz',model)
        for i in testing:oof[i]=predictor.predict_packed(model,train[i]['observations'],train[i]['t'])
        diagnostics.append(dict(hidden=d,readout=rd));fold_records.append(dict(training_clips=sorted({train[i]['clip'] for i in training}),testing_clips=sorted({train[i]['clip'] for i in testing})))
        print(json.dumps(dict(event='fold_complete',fold=fold,hidden=d,readout=rd,seconds=time.perf_counter()-start)),flush=True)
    internal=dict(learned=evaluate_predictions(train,oof),shape_reference=evaluate_predictions(train,[predictor.shape_reference(w['observations'],w['t']) for w in train]),diagnostics=diagnostics);write(out/'internal_diagnostic.json',internal);write(out/'folds.json',fold_records)
    hidden,d=predictor.fit(train,spec,protocol['seed']);model,rd=fit_readout(train,hidden,spec,protocol['readout_regularization']);predictor.save(out/'best_learned.npz',model)
    frozen=dict(id='shape64_C0_exact_readout_0.01',sha256=sha(out/'best_learned.npz'),selection_split='single_prospectively_fixed_configuration',validation_loaded=False,confirmation_read=False,final_hidden_diagnostic=d,final_readout_diagnostic=rd);write(out/'selection_frozen.json',frozen)
    print(json.dumps(dict(event='frozen',selection=frozen)),flush=True)
    validation,vs=load_windows(ROOT,manifest,'validation',protocol);assert len(validation)==480 and vs==skeleton;reports={}
    for name in ['linear','hermite','shape']:
        reports['projected_'+name]=evaluate(dict(kind='baseline',baseline=name),validation,skeleton,protocol)
        if name!='shape':assert reports['projected_'+name]==old['baselines']['projected_'+name]
        print(json.dumps(dict(event='control',name=name,position=reports['projected_'+name]['aggregate']['position'])),flush=True)
    learned=evaluate(model,validation,skeleton,protocol);gate=acceptance(dict(reports,mlp=learned),protocol)
    overall=min(list(reports.items())+[('learned',learned)],key=lambda p:selection(p[1]))[0]
    selected=model if overall=='learned' else dict(kind='baseline',baseline=overall.removeprefix('projected_'));predictor.save(out/'selected.npz',selected)
    assert all(sha(ROOT/n)==h for n,h in hashes.items())
    report=dict(schema=18,status='research_only',full_goal_complete=False,protocol=protocol,source_sha256=hashes,frozen_selection=frozen,selection=dict(id=overall,learned=overall=='learned',sha256=sha(out/'selected.npz'),best_learned_sha256=frozen['sha256']),internal_diagnostic=internal,training_windows=len(train),validation_windows=len(validation),baselines=reports,best_learned_report=learned,gates=dict(best_learned=gate),runtime=dict(seconds=time.perf_counter()-start,python=platform.python_version(),numpy=np.__version__,blas_threads=os.environ['OPENBLAS_NUM_THREADS']),limitations=['Previously exposed validation is research data, not blind confirmation.','Shape reference is procedural; learned model must beat all three controls.','Within-interval component bounds do not prove global motion continuity, anatomy or physical plausibility.','Source core unchanged and no model promoted by this script.'])
    write(out/'report.json',report);print(json.dumps(dict(event='complete',selection=report['selection'],gate=gate,seconds=report['runtime']['seconds'])),flush=True)
if __name__=='__main__':main()
