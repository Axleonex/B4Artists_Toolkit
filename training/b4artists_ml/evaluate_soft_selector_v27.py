"""Prospectively fixed soft readout evaluation; no training or config search."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','4')
from pathlib import Path
import argparse,time,json,hashlib,copy,platform
import numpy as np
import soft_selector_v27 as predictor
from semantic_projection import load_windows,project_windows
from motion_coverage import evaluate_predictions
from sequence_model import acceptance
ROOT=Path(__file__).resolve().parent

def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args();assert args.output.replace('_','').isalnum()
    out=ROOT/'results'/args.output;assert not out.exists();started=time.perf_counter()
    plan=read(ROOT/'soft_selector_plan_v27.json');protocol=read(ROOT/'projected_selector_protocol_v26.json');parent=read(ROOT/'results/projected_selector_v26/report.json');diagnostic=read(ROOT/'results/soft-selector-training-v27.json');checks=read(ROOT/'results/soft-selector-checks-v27.json')
    assert diagnostic['complete'] and diagnostic['geometry_passed'] and diagnostic['training_only'] and not diagnostic['validation_loaded'] and checks['passed']
    for n,h in checks['source_sha256'].items():assert sha(ROOT.parents[1]/n)==h,n
    for n,h in diagnostic['source_sha256'].items():assert sha(ROOT/n)==h,n
    for n,h in parent['source_sha256'].items():assert sha(ROOT/n)==h,n
    assert plan['source_sha256']==sha(ROOT/'soft_selector_v27.py')==diagnostic['source_sha256']['soft_selector_v27.py'] and plan['model_sha256']==sha(ROOT/plan['model_path'])
    assert plan['projection']==protocol['projection'] and plan['gates']==protocol['gates']
    expansion=read(ROOT/'temporal_expansion_plan_v19.json')
    def guard():
        assert time.perf_counter()-started<plan['budgets']['development_seconds'] and time.time()<plan['deadline_unix']
        assert all(not (ROOT/'cache'/(n+'.bvh')).exists() for n in expansion['planned_splits']['confirmation'])
    sources={n:sha(ROOT/n) for n in ['soft_selector_v27.py','soft_selector_plan_v27.json','evaluate_soft_selector_v27.py','results/soft-selector-training-v27.json','results/soft-selector-checks-v27.json']}
    guard();out.mkdir();write(out/'protocol.json',dict(protocol,readout_experiment=plan));(out/'best_learned.npz').write_bytes((ROOT/plan['model_path']).read_bytes());digest=sha(out/'best_learned.npz');model=predictor.load(out/'best_learned.npz')
    frozen=dict(id='soft_probability_quaternion_readout_v27',sha256=digest,refit=False,new_training=False,validation_loaded=False,confirmation_read=False,source_sha256=sources,parent_report_sha256=sha(ROOT/'results/projected_selector_v26/report.json'));write(out/'selection_frozen.json',frozen)
    print(json.dumps(dict(event='frozen',model_sha256=digest,new_training=False)),flush=True)
    windows,skeleton=load_windows(ROOT,read(ROOT/'temporal_training_manifest_v19.json'),'validation',protocol);assert len(windows)==768
    old=set(protocol['old_validation_clips']);new=set(protocol['new_validation_clips']);parts={'old_validation':[w for w in windows if w['clip'] in old],'new_validation':[w for w in windows if w['clip'] in new]};assert len(parts['old_validation'])==480 and len(parts['new_validation'])==288
    reports={};all_windows=[];all_pred=[];edges=[];probabilities=[]
    for part,rows in parts.items():
        guard();raw=[predictor.predict_packed(model,w['observations'],w['t']) for w in rows];projected,geometry=project_windows(rows,raw,skeleton,plan['projection']);score=evaluate_predictions(rows,projected);score['aggregate']['true_edge_length_max']=geometry['true_edge_length_max'];score['projection']=geometry
        # Unchanged source, inputs and projector retain the exact frozen controls.
        reports[part]={n:copy.deepcopy(parent['partition_reports'][part][n]) for n in protocol['baselines']};reports[part]['mlp']=score;all_windows+=rows;all_pred+=projected;edges.append(geometry['true_edge_length_max'])
        for w in rows:
            p=predictor.probabilities(model,w['observations']);probabilities.append(dict(clip=w['clip'],gap=w['gap'],context=bool(w['context']),probabilities=p.tolist(),position_weights=p.reshape(4,3).sum(axis=1).tolist(),rotation_weights=p.reshape(4,3).sum(axis=0).tolist()))
        print(json.dumps(dict(event='evaluated',partition=part,position=score['aggregate']['position'])),flush=True)
    combined=evaluate_predictions(all_windows,all_pred);combined['aggregate']['true_edge_length_max']=max(edges);reports['combined']={n:copy.deepcopy(parent['partition_reports']['combined'][n]) for n in protocol['baselines']};reports['combined']['mlp']=combined
    gates={part:acceptance(values,protocol) for part,values in reports.items()};guard();assert all(sha(ROOT/n)==h for n,h in sources.items()) and all(sha(ROOT/n)==h for n,h in parent['source_sha256'].items())
    write(out/'probabilities.json',probabilities)
    result=dict(schema=27,status='research_only',full_goal_complete=False,confirmation_read=False,new_training=False,refit=False,protocol=dict(protocol,readout_experiment=plan),source_sha256=sources,model_files={f'results/{args.output}/best_learned.npz':digest},selection=dict(id='soft_probability_quaternion_readout_v27',learned=True,best_learned_sha256=digest),frozen_selection=frozen,training_source='results/projected_selector_v26',training_diagnostic_path='results/soft-selector-training-v27.json',validation_windows=768,validation_windows_by_partition={p:len(v) for p,v in parts.items()},partition_reports=reports,development_gates=gates,gates=dict(best_learned=dict(passed=all(g['passed'] for g in gates.values()),partitions=gates)),retained_controls=dict(parent_report_sha256=sha(ROOT/'results/projected_selector_v26/report.json'),original_three_controls_byte_unchanged=True,reason='Same frozen observations, sampling, source and projector; v26complete reproduction independently verified.'),runtime=dict(seconds=time.perf_counter()-started,python=platform.python_version(),numpy=np.__version__,blas_threads=os.environ['OPENBLAS_NUM_THREADS']),limitations=['Frozen v26learned probabilities receive a new soft readout; weights were not retrained for mixture-output loss.','Quaternion hemisphere alignment is locally continuous away from antipodal boundaries; near-zero mixtures reject.','Both development sets are exposed; no confirmation, animator judgment or release qualification here.'])
    write(out/'report.json',result);size=sum(p.stat().st_size for p in out.rglob('*') if p.is_file());assert size<=plan['budgets']['max_output_bytes'];write(out/'complete.json',dict(complete=True,report_sha256=sha(out/'report.json'),generated_bytes=size));print(json.dumps(dict(event='complete',gates=gates,bytes=size)),flush=True)
if __name__=='__main__':main()
