"""One prospectively fixed v28training run and original development evaluation."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','4')
from pathlib import Path
import argparse,time,json,hashlib,copy,platform
import numpy as np
import tail_risk_selector_v28 as predictor
from semantic_projection import load_windows,project_windows
from motion_coverage import evaluate_predictions
from sequence_model import acceptance
ROOT=Path(__file__).resolve().parent

def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args();assert args.output.replace('_','').isalnum()
    out=ROOT/'results'/args.output;assert not out.exists();started=time.perf_counter()
    plan=read(ROOT/'tail_risk_plan_v28.json');protocol=read(ROOT/'projected_selector_protocol_v26.json');parent=read(ROOT/'results/projected_selector_v26/report.json');checks=read(ROOT/'results/tail-risk-checks-v28.json')
    assert checks['passed'] and checks['tests']==7
    for name,h in plan['source_sha256'].items():assert sha(ROOT.parents[1]/name)==h,name
    for name,h in plan['input_sha256'].items():assert sha(ROOT/name)==h,name
    for name,h in parent['source_sha256'].items():assert sha(ROOT/name)==h,name
    assert plan['projection']==protocol['projection'] and plan['gates']==protocol['gates']
    expansion=read(ROOT/'temporal_expansion_plan_v19.json')
    def guard():
        assert time.perf_counter()-started<plan['budgets']['complete_run_seconds'] and time.time()<plan['deadline_unix']
        assert all(not (ROOT/'cache'/(n+'.bvh')).exists() for n in expansion['planned_splits']['confirmation'])
    guard();out.mkdir();write(out/'protocol.json',dict(protocol,tail_risk_experiment=plan))
    labels=ROOT/'results/projected_selector_v26/labels.npz';identities=read(ROOT/'results/projected_selector_v26/window_identity.json');manifest=read(ROOT/'results/projected_selector_v26/label_manifest.json')
    assert manifest['labels_sha256']==sha(labels) and manifest['complete'] and manifest['training_windows']==7358
    with np.load(labels,allow_pickle=False) as data:features=data['features'];measured=data['metrics']
    assert features.shape==(7358,596) and measured.shape==(7358,12,len(manifest['metric_order'])) and len(identities)==7358
    train_clips={r['clip'] for r in identities};development=set(protocol['old_validation_clips'])|set(protocol['new_validation_clips']);assert not train_clips&development
    pidx=manifest['metric_order'].index('position');ridx=manifest['metric_order'].index('rotation');position,rotation,group,normalizers=predictor.normalize_costs(identities,measured[...,pidx],measured[...,ridx]);write(out/'normalizers.json',normalizers)
    initial=predictor.load(ROOT/'results/projected_selector_v26/best_learned.npz')
    print(json.dumps(dict(event='training_only',windows=7358,cohorts=len(normalizers),validation_loaded=False)),flush=True)
    model,diagnostic=predictor.fit(features,position,rotation,group,initial,plan['training'],guard)
    for k,v in initial.items():
        if k.startswith('parent_') or k in ['mean','std']:np.testing.assert_array_equal(model[k],v)
    predictor.save(out/'best_learned.npz',model);digest=sha(out/'best_learned.npz');assert digest!=sha(ROOT/'results/projected_selector_v26/best_learned.npz')
    sources={n:sha(ROOT.parents[1]/n) for n in plan['source_sha256']};sources['training/b4artists_ml/tail_risk_plan_v28.json']=sha(ROOT/'tail_risk_plan_v28.json')
    frozen=dict(id='tail_risk_soft_selector_v28',sha256=digest,new_training=True,validation_loaded=False,confirmation_read=False,source_sha256=sources,parent_model_sha256=sha(ROOT/'results/projected_selector_v26/best_learned.npz'),labels_sha256=sha(labels),training_diagnostic=diagnostic);write(out/'selection_frozen.json',frozen)
    print(json.dumps(dict(event='frozen',sha256=digest,training_seconds=time.perf_counter()-started,diagnostic=diagnostic)),flush=True)
    guard();windows,skeleton=load_windows(ROOT,read(ROOT/'temporal_training_manifest_v19.json'),'validation',protocol);assert len(windows)==768
    old=set(protocol['old_validation_clips']);new=set(protocol['new_validation_clips']);parts={'old_validation':[w for w in windows if w['clip'] in old],'new_validation':[w for w in windows if w['clip'] in new]};assert len(parts['old_validation'])==480 and len(parts['new_validation'])==288
    reports={};all_windows=[];all_pred=[];edges=[];probabilities=[]
    for part,rows in parts.items():
        guard();raw=[predictor.predict_packed(model,w['observations'],w['t']) for w in rows];projected,geometry=project_windows(rows,raw,skeleton,plan['projection']);score=evaluate_predictions(rows,projected);score['aggregate']['true_edge_length_max']=geometry['true_edge_length_max'];score['projection']=geometry
        reports[part]={n:copy.deepcopy(parent['partition_reports'][part][n]) for n in protocol['baselines']};reports[part]['mlp']=score;all_windows+=rows;all_pred+=projected;edges.append(geometry['true_edge_length_max'])
        for w in rows:
            p=predictor.probabilities(model,w['observations']);probabilities.append(dict(clip=w['clip'],gap=w['gap'],context=bool(w['context']),probabilities=p.tolist(),position_weights=p.reshape(4,3).sum(axis=1).tolist(),rotation_weights=p.reshape(4,3).sum(axis=0).tolist()))
        print(json.dumps(dict(event='evaluated',partition=part,position=score['aggregate']['position'])),flush=True)
    combined=evaluate_predictions(all_windows,all_pred);combined['aggregate']['true_edge_length_max']=max(edges);reports['combined']={n:copy.deepcopy(parent['partition_reports']['combined'][n]) for n in protocol['baselines']};reports['combined']['mlp']=combined
    gates={part:acceptance(values,protocol) for part,values in reports.items()};guard()
    assert all(sha(ROOT.parents[1]/n)==h for n,h in sources.items()) and all(sha(ROOT/n)==h for n,h in parent['source_sha256'].items()) and all(sha(ROOT/n)==h for n,h in plan['input_sha256'].items())
    write(out/'probabilities.json',probabilities)
    result=dict(schema=28,status='research_only',full_goal_complete=False,confirmation_read=False,new_training=True,protocol=dict(protocol,tail_risk_experiment=plan),source_sha256=sources,model_files={f'results/{args.output}/best_learned.npz':digest},selection=dict(id='tail_risk_soft_selector_v28',learned=True,best_learned_sha256=digest),frozen_selection=frozen,training_source='results/projected_selector_v26/labels.npz',training_diagnostic=diagnostic,training_windows=7358,validation_windows=768,validation_windows_by_partition={p:len(v) for p,v in parts.items()},partition_reports=reports,development_gates=gates,gates=dict(best_learned=dict(passed=all(g['passed'] for g in gates.values()),partitions=gates)),retained_controls=dict(parent_report_sha256=sha(ROOT/'results/projected_selector_v26/report.json'),original_three_controls_byte_unchanged=True,reason='Same frozen observations, sampling, source and projector; complete v26reproduction verified.'),runtime=dict(seconds=time.perf_counter()-started,python=platform.python_version(),numpy=np.__version__,blas_threads=os.environ['OPENBLAS_NUM_THREADS']),limitations=['Training expert costs are a surrogate for actual projected soft blend.','Warm-started v26selector sees only the same training labels; group-excluded frozen parent labels preserve their original membership.','Quaternion blending and its hemisphere boundaries remain unchanged.','Both development sets are exposed; no fresh confirmation, independent animator or release qualification.'])
    write(out/'report.json',result);size=sum(p.stat().st_size for p in out.rglob('*') if p.is_file());assert size<=plan['budgets']['max_output_bytes'];write(out/'complete.json',dict(complete=True,report_sha256=sha(out/'report.json'),generated_bytes=size));print(json.dumps(dict(event='complete',gates=gates,bytes=size)),flush=True)
if __name__=='__main__':main()
