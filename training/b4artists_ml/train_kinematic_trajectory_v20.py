"""Observed-only input conditioning; fixed training and separate holdout guards."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','4')
from pathlib import Path
import json,hashlib,time,argparse,platform
import numpy as np
import kinematic_trajectory_v20 as predictor
from kinematic_readout_v20 import fit_readout
from semantic_projection import load_windows,project_windows
from motion_coverage import evaluate_predictions
from temporal_model import selection
from sequence_model import acceptance
from crossfit_controller import grouped_folds
from fetch_cmu_temporal_v19 import PLAN_SHA,sha,read,write,require
ROOT=Path(__file__).resolve().parent

def evaluate_partition(model,windows,skeleton,protocol):
    predictions=[predictor.predict_packed(model,w['observations'],w['t']) for w in windows]
    projected,metrics=project_windows(windows,predictions,skeleton,protocol['projection'])
    report=evaluate_predictions(windows,projected);report['aggregate']['true_edge_length_max']=metrics['true_edge_length_max'];report['projection']=metrics
    return projected,report

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args()
    require(args.output.replace('_','').isalnum(),'Simple unique output name required')
    out=ROOT/'results'/args.output;out.mkdir(exist_ok=False);start=time.perf_counter()
    protocol=read(ROOT/'kinematic_trajectory_protocol_v20.json');old=read(ROOT/'results/expanded_trajectory_v19/report.json')
    require(protocol['gates']==old['protocol']['gates'] and protocol['projection']==old['protocol']['projection'] and protocol['experiments']==old['protocol']['experiments'],'Frozen comparison changed')
    for name,h in protocol['source_manifests'].items():require(sha(ROOT/name)==h,'Data plan/manifest changed')
    require(sha(ROOT/'expanded_trajectory_protocol_v19.json')==protocol['prior_protocol_sha256'],'Prior protocol changed')
    require(sha(ROOT/'results/expanded_trajectory_v19/best_learned.npz')==protocol['prior_model_sha256'],'Prior model changed')
    for name,h in old['source_sha256'].items():require(sha(ROOT/name)==h,'Prior research source changed')
    sources=set(old['source_sha256'])|{'kinematic_trajectory_protocol_v20.json','train_kinematic_trajectory_v20.py','kinematic_features_v20.py','kinematic_trajectory_v20.py','kinematic_readout_v20.py','check_kinematic_features_v20.py','check_kinematic_trajectory_v20.py'};hashes={n:sha(ROOT/n) for n in sorted(sources)}
    plan=read(ROOT/'temporal_expansion_plan_v19.json');require(all(not (ROOT/'cache'/(c+'.bvh')).exists() for c in plan['planned_splits']['confirmation']),'Fresh confirmation already present')
    manifest=read(ROOT/'temporal_training_manifest_v19.json');write(out/'protocol.json',protocol);write(out/'manifest.json',manifest)
    previous_manifest=read(ROOT/'results/boundary_trajectory_v16/manifest.json');require(manifest['files'][:len(previous_manifest['files'])]==previous_manifest['files'],'Original sample indexing changed')
    train,skeleton=load_windows(ROOT,manifest,'train',protocol);require(len(train)==protocol['expected_training_windows'],'Unexpected train windows');folds=grouped_folds(train,4);spec=protocol['experiments'][0]
    oof=[None]*len(train);diagnostics=[];fold_records=[]
    print(json.dumps(dict(event='training_ready',windows=len(train))),flush=True)
    for fold,(training,testing) in enumerate(folds):
        rows=[train[i] for i in training];hidden,d=predictor.fit(rows,spec,protocol['seed']);model,rd=fit_readout(rows,hidden,spec,protocol['readout_regularization']);predictor.save(out/f'fold_{fold}.npz',model)
        for i in testing:oof[i]=predictor.predict_packed(model,train[i]['observations'],train[i]['t'])
        diagnostics.append(dict(hidden=d,readout=rd));fold_records.append(dict(training_clips=sorted({train[i]['clip'] for i in training}),testing_clips=sorted({train[i]['clip'] for i in testing})))
        print(json.dumps(dict(event='fold_complete',fold=fold,hidden_initial=d['initial_objective'] if 'initial_objective' in d else None,seconds=time.perf_counter()-start)),flush=True)
    internal=dict(learned=evaluate_predictions(train,oof),shape_reference=evaluate_predictions(train,[predictor.shape_reference(w['observations'],w['t']) for w in train]),diagnostics=diagnostics);write(out/'internal_diagnostic.json',internal);write(out/'folds.json',fold_records)
    hidden,d=predictor.fit(train,spec,protocol['seed']);model,rd=fit_readout(train,hidden,spec,protocol['readout_regularization']);predictor.save(out/'best_learned.npz',model)
    model_sha=sha(out/'best_learned.npz');frozen=dict(id='kinematic548_shape64_C0_exact_readout_0.01',sha256=model_sha,selection_split='single_prospectively_fixed_configuration',plan_sha256=PLAN_SHA,validation_loaded=False,confirmation_read=False,final_hidden_diagnostic=d,final_readout_diagnostic=rd);write(out/'selection_frozen.json',frozen)
    print(json.dumps(dict(event='frozen',sha256=model_sha,seconds=time.perf_counter()-start)),flush=True)
    validation,vs=load_windows(ROOT,manifest,'validation',protocol);require(vs==skeleton,'Validation hierarchy changed')
    old_clips=set(protocol['old_validation_clips']);new_clips=set(protocol['new_validation_clips']);require(not old_clips&new_clips,'Validation clip overlap')
    parts={'old_validation':[w for w in validation if w['clip'] in old_clips],'new_validation':[w for w in validation if w['clip'] in new_clips]}
    require(len(parts['old_validation'])==480 and sum(map(len,parts.values()))==len(validation),'Validation sampling changed');reports={p:{} for p in [*parts,'combined']}
    for name,m in [(f'projected_{b}',dict(kind='baseline',baseline=b)) for b in ['linear','hermite','shape']]+[('mlp',model)]:
        all_windows=[];all_predictions=[];edges=[]
        for part,windows in parts.items():
            predictions,scored=evaluate_partition(m,windows,skeleton,protocol);reports[part][name]=scored;all_windows+=windows;all_predictions+=predictions;edges.append(scored['aggregate']['true_edge_length_max'])
            if name!='mlp':require(scored==old['partition_reports'][part][name],'Baseline/window regression')
        combined=evaluate_predictions(all_windows,all_predictions);combined['aggregate']['true_edge_length_max']=max(edges);reports['combined'][name]=combined
        print(json.dumps(dict(event='evaluated',name=name,position={p:reports[p][name]['aggregate']['position'] for p in reports},seconds=time.perf_counter()-start)),flush=True)
    gates={p:acceptance(reports[p],protocol) for p in reports};overall=min(reports['combined'].items(),key=lambda p:selection(p[1]))[0]
    selected=model if overall=='mlp' else dict(kind='baseline',baseline=overall.removeprefix('projected_'));predictor.save(out/'selected.npz',selected)
    require(all(sha(ROOT/n)==h for n,h in hashes.items()),'Research sources changed during fit')
    report=dict(schema=20,status='research_only',full_goal_complete=False,plan_sha256=PLAN_SHA,model_files={f'results/{args.output}/best_learned.npz':model_sha},confirmation_read=False,protocol=protocol,source_sha256=hashes,frozen_selection=frozen,selection=dict(id=overall,learned=overall=='mlp',sha256=sha(out/'selected.npz'),best_learned_sha256=model_sha),internal_diagnostic=internal,training_windows=len(train),validation_windows=len(validation),validation_windows_by_partition={p:len(w) for p,w in parts.items()},baselines={k:v for k,v in reports['combined'].items() if k!='mlp'},best_learned_report=reports['combined']['mlp'],partition_reports=reports,development_gates=gates,gates=dict(best_learned=dict(passed=all(g['passed'] for g in gates.values()),partitions=gates)),runtime=dict(seconds=time.perf_counter()-start,python=platform.python_version(),numpy=np.__version__,blas_threads=os.environ['OPENBLAS_NUM_THREADS']),limitations=['Both validation partitions are exposed development data; this model froze before either was loaded in this experiment.','All three partitions must pass; larger data cannot dilute old regressions.','Catalog IDs are not guaranteed independent actors; duplicate83_01 was excluded against protected122_01.','No sealed confirmation opened and no temporal weights promoted.'])
    write(out/'report.json',report)
    if report['gates']['best_learned']['passed']:
        write(out/'confirmation_selection.json',dict(confirmation_loaded=False,plan_sha256=PLAN_SHA,model_files=report['model_files'],development_report=f'results/{args.output}/report.json',development_report_sha256=sha(out/'report.json')))
    print(json.dumps(dict(event='complete',selection=report['selection'],gates=gates,seconds=report['runtime']['seconds'])),flush=True)
if __name__=='__main__':main()
