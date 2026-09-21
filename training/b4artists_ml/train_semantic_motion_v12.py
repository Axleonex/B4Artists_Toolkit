"""Frozen shared-schema temporal regression with identically projected controls."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','4')
from pathlib import Path
import json,hashlib,time,argparse,platform
import numpy as np
import semantic_predictor as predictor
from semantic_projection import load_windows,project_windows
from motion_coverage import evaluate_predictions
from temporal_model import selection
from sequence_model import acceptance
ROOT=Path(__file__).resolve().parent

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.write_text(json.dumps(d,indent=2,allow_nan=False)+'\n')

def evaluate(model,windows,skeleton,protocol):
    predictions=[predictor.predict_packed(model,w['observations'],w['t']) for w in windows]
    projected,metrics=project_windows(windows,predictions,skeleton,protocol['projection'])
    report=evaluate_predictions(windows,projected);report['aggregate']['true_edge_length_max']=metrics['true_edge_length_max']
    report['projection']=metrics
    return report

def main():
    args=argparse.ArgumentParser();args.add_argument('--output',required=True);args=args.parse_args()
    if not args.output.replace('_','').isalnum():raise ValueError('Simple unique output name required')
    out=ROOT/'results'/args.output;out.mkdir(exist_ok=False);start=time.perf_counter()
    protocol=json.loads((ROOT/'semantic_motion_protocol_v12.json').read_text())
    for name,h in protocol['source_manifests'].items():assert sha(ROOT/name)==h
    prior=json.loads((ROOT/'results/training_manifest_v4.json').read_text());extra=json.loads((ROOT/'temporal_expansion_manifest_v8.json').read_text())
    manifest=dict(files=prior['files']+[row for row in extra['files'] if row['split']!='confirmation'])
    source_names=['semantic_motion_protocol_v12.json','semantic_projection.py','semantic_predictor.py','train_semantic_motion_v12.py','semantic_motion_data.py','rig_observations.py','sequence_kinematics.py','sequence_data.py','sequence_model.py','motion_coverage.py','temporal_data.py','temporal_model.py','bvh_data.py','context_data.py','context_network.py']
    source={name:sha(ROOT/name) for name in source_names};write(out/'protocol.json',protocol);write(out/'manifest.json',manifest)
    train,skeleton=load_windows(ROOT,manifest,'train',protocol);validation,vs=load_windows(ROOT,manifest,'validation',protocol);assert vs==skeleton
    assert len(train)==2912 and len(validation)==480
    print(json.dumps(dict(event='data_ready',training_windows=len(train),validation_windows=len(validation),seconds=time.perf_counter()-start)),flush=True)
    reports={};best_model=None;best_score=float('inf');best_id=None;best_learned=None;best_learned_score=float('inf');best_learned_report=None;history=[]
    for name in ('linear','hermite'):
        model=dict(kind='baseline',baseline=name);report=evaluate(model,validation,skeleton,protocol);reports['projected_'+name]=report;score=selection(report)
        print(json.dumps(dict(event='projected_baseline',name=name,position=report['aggregate']['position'],score=score,seconds=time.perf_counter()-start)),flush=True)
        if score<best_score:best_score=score;best_model=model;best_id='projected_'+name
    for index,experiment in enumerate(protocol['experiments']):
        model=predictor.fit(train,experiment,protocol['seed']);identifier='trial_'+str(index)
        try:report=evaluate(model,validation,skeleton,protocol)
        except ValueError as exc:
            history.append(dict(id=identifier,experiment=experiment,valid=False,error=str(exc)));continue
        score=selection(report);row=dict(id=identifier,experiment=experiment,valid=True,score=score,report=report);history.append(row)
        predictor.save(out/(identifier+'.npz'),model)
        print(json.dumps(dict(event='trial',id=identifier,position=report['aggregate']['position'],score=score,seconds=time.perf_counter()-start)),flush=True)
        if score<best_learned_score:
            best_learned_score=score;best_learned=identifier;best_learned_report=report;predictor.save(out/'best_learned.npz',model)
        if score<best_score:best_score=score;best_model=model;best_id=identifier
        write(out/'trials.json',history)
    predictor.save(out/'selected.npz',best_model);loaded=predictor.load(out/'selected.npz')
    for key in best_model:np.testing.assert_array_equal(best_model[key],loaded[key])
    selected_report=reports[best_id] if best_id in reports else next(row['report'] for row in history if row['id']==best_id)
    selected_gate=acceptance(dict(reports,mlp=selected_report),protocol)
    learned_gate=acceptance(dict(reports,mlp=best_learned_report),protocol) if best_learned_report is not None else dict(passed=False)
    assert all(sha(ROOT/name)==h for name,h in source.items()),'Experiment source changed while fitting'
    selected=dict(id=best_id,learned=best_model['kind']!='baseline',score=best_score,sha256=sha(out/'selected.npz'),best_learned_id=best_learned,best_learned_sha256=sha(out/'best_learned.npz') if best_learned else None,selection_split='validation',confirmation_read=False)
    write(out/'selection.json',selected)
    report=dict(schema=12,status='research_only',full_goal_complete=False,protocol=protocol,source_sha256=source,skeleton=skeleton,selection=selected,training_windows=len(train),validation_windows=len(validation),baselines=reports,trials=history,selected_report=selected_report,best_learned_report=best_learned_report,gates=dict(selected=selected_gate,best_learned=learned_gate),runtime=dict(seconds=time.perf_counter()-start,python=platform.python_version(),numpy=np.__version__,platform=platform.platform(),blas_threads=os.environ['OPENBLAS_NUM_THREADS']),limitations=['Validation selection is not blind confirmation.','Physical corpus projection starts only from known anchors; it is not an animator assessment.','No new data downloaded and no artifact promoted into the add-on.','Actual-rig learned candidate behavior, responsive UI, partial-body/style contacts, human usability and Cascadeur comparison remain separate requirements.'])
    write(out/'report.json',report)
    print(json.dumps(dict(event='complete',selected=selected,gates=report['gates'],seconds=report['runtime']['seconds'])),flush=True)
if __name__=='__main__':main()
