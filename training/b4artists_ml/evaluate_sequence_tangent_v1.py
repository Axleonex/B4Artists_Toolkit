"""Evaluate four frozen sequence fits under the original protected comparison."""
from pathlib import Path
import os,time,json,hashlib
os.environ.setdefault('OPENBLAS_NUM_THREADS','4')
import numpy as np
from sequence_tangent_provider_v1 import Provider
from semantic_projection import load_windows,project_windows
from motion_coverage import evaluate_predictions
from sequence_model import acceptance
from kinematic_trajectory_v20 import predict_packed as baseline_predict
ROOT=Path(__file__).resolve().parents[2];TR=Path(__file__).resolve().parent;BASE=TR/'results/sequence-tangent-development-v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def write(p,d):p.write_text(json.dumps(d,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def main():
 plan_path=TR/'sequence_tangent_evaluation_plan_v1.json';plan=read(plan_path);protocol=read(TR/plan['reference_protocol']);old=read(TR/plan['reference_report']);assert sha(TR/plan['reference_protocol'])==plan['reference_protocol_sha256'] and sha(TR/plan['reference_report'])==plan['reference_report_sha256']
 for n,h in plan['sources'].items():assert sha(TR/n)==h,n
 assert protocol['gates']==old['protocol']['gates'] and protocol['projection']==old['protocol']['projection'] and protocol['baselines']==old['protocol']['baselines'];assert read(TR/'results/sequence-tangent-training-v1/active-process.json').get('all_complete') is True
 processes=read(TR/'results/sequence-tangent-training-v1/processes.json');assert len(processes)==2 and all(r['exit_code']==0 for r in processes);models=[]
 for item in plan['models']:
  name='tangent-'+item['kind']+'-'+str(item['seed']);report_path=TR/'results/sequence-tangent-training-v1'/name.removeprefix('tangent-')/'report.json';r=read(report_path);assert r['complete'] and r['completed_epochs']==60 and not r['validation_read'] and not r['confirmation_read'] and r['cpu_export_max_abs_error']<5e-5 and r['plan_sha256']==plan['training_plan_sha256'];assert sha(ROOT/r['weights'])==r['weights_sha256'];models.append(dict(name=name,**item,weights=r['weights'],weights_sha256=r['weights_sha256'],report_sha256=sha(report_path)))
 protected=read(TR/'temporal_expansion_plan_v19.json')['planned_splits']['confirmation'];assert all(not (TR/'cache'/(n+'.bvh')).exists() for n in protected)
 BASE.mkdir(exist_ok=False);start=time.perf_counter();frozen=dict(models=models,plan_sha256=sha(plan_path),script_sha256=sha(Path(__file__)),validation_loaded=False,confirmation_read=False,recorded_at=time.time());write(BASE/'frozen-before-validation.json',frozen)
 manifest=read(TR/'temporal_training_manifest_v19.json');assert sha(TR/'temporal_training_manifest_v19.json')==protocol['source_manifests']['temporal_training_manifest_v19.json'];windows,skeleton=load_windows(TR,manifest,'validation',protocol)
 old_ids=set(protocol['old_validation_clips']);new_ids=set(protocol['new_validation_clips']);assert not old_ids&new_ids;parts={'old_validation':[w for w in windows if w['clip'] in old_ids],'new_validation':[w for w in windows if w['clip'] in new_ids]};assert len(parts['old_validation'])==480 and len(parts['new_validation'])==288 and sum(map(len,parts.values()))==len(windows)
 reports={p:{} for p in (*parts,'combined')};identities={p:[dict(clip=w['clip'],gap=w['gap'],context=w['context'],frames=w['frame'].tolist()) for w in rows] for p,rows in parts.items()};write(BASE/'window-identities.json',identities)
 methods=[dict(name='projected_'+b,baseline=b) for b in ('linear','hermite','shape')]+models
 errors={}
 for method in methods:
  name=method['name'];provider=None if 'baseline' in method else Provider(ROOT/method['weights'],method['weights_sha256'],kind=method['kind'],seed=method['seed']);all_windows=[];all_output=[];edges=[];outdir=BASE/name;outdir.mkdir()
  try:
   for part,rows in parts.items():
    predictions=[];output=[];fitting=[];edge=0.;inference_seconds=0.;projection_seconds=0.
    for offset in range(0,len(rows),16):
     assert time.time()<plan['deadline_unix'];batch=rows[offset:offset+16];at=time.perf_counter();proposal=[baseline_predict(dict(kind='baseline',baseline=method['baseline']),w['observations'],w['t']) if provider is None else provider.predict_packed(w['observations'],w['t']) for w in batch];inference_seconds+=time.perf_counter()-at
     for w,p in zip(batch,proposal):assert np.isfinite(p).all() and np.array_equal(p[[0,-1]],w['linear'][[0,-1]])
     at=time.perf_counter();values,metric=project_windows(batch,proposal,skeleton,protocol['projection']);projection_seconds+=time.perf_counter()-at;output+=values;edge=max(edge,metric['true_edge_length_max']);fitting.append(metric['position_fit_error'])
     np.savez_compressed(outdir/(part+'-'+str(offset)+'.npz'),**{str(i):v for i,v in enumerate(values)});write(BASE/'progress.json',dict(method=name,partition=part,windows_completed=offset+len(batch),partition_windows=len(rows),seconds=time.perf_counter()-start))
    scored=evaluate_predictions(rows,output);scored['aggregate']['true_edge_length_max']=edge;scored['projection']=dict(true_edge_length_max=edge,position_fit_error=float(np.mean(fitting)));reports[part][name]=scored
    if provider is None:assert scored==old['partition_reports'][part][name],'Protected baseline report changed: '+name+'/'+part
    write(outdir/(part+'-metrics.json'),scored);write(outdir/(part+'-timings.json'),dict(inference_seconds=inference_seconds,projection_seconds=projection_seconds));all_windows+=rows;all_output+=output;edges.append(edge);print(json.dumps(dict(method=name,partition=part,position=scored['aggregate']['position'],seconds=time.perf_counter()-start)),flush=True)
   combined=evaluate_predictions(all_windows,all_output);combined['aggregate']['true_edge_length_max']=max(edges);reports['combined'][name]=combined
   if provider is None:assert combined==old['partition_reports']['combined'][name]
   write(outdir/'combined-metrics.json',combined)
  except (ValueError,ArithmeticError,AssertionError) as exc:
   if provider is None:raise
   errors[name]=repr(exc);write(outdir/'failed-candidate.json',dict(error=repr(exc),quality_qualified=False));print(json.dumps(dict(method=name,failed=repr(exc))),flush=True)
 gates={}
 for model in models:
  name=model['name']
  if name in errors:
   gates[name]={p:dict(passed=False,error=errors[name]) for p in reports};continue
  gates[name]={p:acceptance({**{b:reports[p][b] for b in protocol['baselines']},'mlp':reports[p][name]},protocol) for p in reports}
 families={kind:all(gates['tangent-'+kind+'-'+str(seed)][p]['passed'] for seed in (20260909,20260910) for p in reports) for kind in ('direct',)}
 assert all(not (TR/'cache'/(n+'.bvh')).exists() for n in protected)
 for n,h in plan['sources'].items():assert sha(TR/n)==h
 report=dict(complete=True,models=models,partition_reports=reports,development_gates=gates,failed_candidates=errors,family_passes=families,protected_baselines_match=True,validation_windows=768,confirmation_read=False,full_goal_complete=False,runtime_promoted=False,seconds=time.perf_counter()-start,plan_sha256=sha(plan_path),frozen_sha256=sha(BASE/'frozen-before-validation.json'));write(BASE/'report.json',report);print(json.dumps(dict(complete=True,family_passes=families,seconds=report['seconds'])),flush=True)
if __name__=='__main__':main()
