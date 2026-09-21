"""Frozen2x2 component diagnosis; no fitting or fresh confirmation access."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','4')
from pathlib import Path
import json,time
import numpy as np
import curve_mixture_v23 as p23
import joint_mixture_v24 as p24
from semantic_projection import load_windows,project_windows
from motion_coverage import evaluate_predictions
from sequence_model import acceptance
from fetch_cmu_temporal_v19 import sha,read,write,require
ROOT=Path(__file__).resolve().parent

def main():
 out=ROOT/'results/crossed-components-v25.json';require(not out.exists(),'Evidence exists');start=time.perf_counter();plan=read(ROOT/'crossed_components_plan_v25.json');protocol=read(ROOT/'joint_mixture_protocol_v24.json')
 folders={'v23':'curve_mixture_v23','v24':'joint_mixture_v24'};modules={'v23':p23,'v24':p24};reports={k:read(ROOT/'results'/v/'report.json') for k,v in folders.items()};models={};sources={Path(__file__).name:sha(Path(__file__)),'crossed_components_plan_v25.json':sha(ROOT/'crossed_components_plan_v25.json')}
 for name,folder in folders.items():
  path=ROOT/'results'/folder/'best_learned.npz';require(sha(path)==plan['models'][folder]==reports[name]['selection']['best_learned_sha256'],'Frozen model changed');models[name]=modules[name].load(path)
  for n,h in reports[name]['source_sha256'].items():require(sha(ROOT/n)==h,'Frozen implementation changed');sources[n]=h
 for n,h in protocol['source_manifests'].items():require(sha(ROOT/n)==h,'Frozen data manifest changed')
 expansion=read(ROOT/'temporal_expansion_plan_v19.json')
 def sealed():require(all(not (ROOT/'cache'/(c+'.bvh')).exists() for c in expansion['planned_splits']['confirmation']),'Confirmation exposed')
 sealed();manifest=read(ROOT/'temporal_training_manifest_v19.json');windows,skeleton=load_windows(ROOT,manifest,'validation',protocol);old=set(protocol['old_validation_clips']);new=set(protocol['new_validation_clips']);parts={'old_validation':[w for w in windows if w['clip'] in old],'new_validation':[w for w in windows if w['clip'] in new]};require(len(parts['old_validation'])==480 and len(parts['new_validation'])==288,'Sampling changed')
 raw={name:{part:[modules[name].predict_packed(model,w['observations'],w['t']) for w in rows] for part,rows in parts.items()} for name,model in models.items()};raw_reports={};projected={}
 for name in models:
  raw_reports[name]={part:evaluate_predictions(rows,raw[name][part]) for part,rows in parts.items()};raw_reports[name]['combined']=evaluate_predictions(sum(parts.values(),[]),sum(raw[name].values(),[]));projected[name]={part:r['mlp'] for part,r in reports[name]['partition_reports'].items()}
 for position,rotation in [('v23','v24'),('v24','v23')]:
  name=position+'_position_'+rotation+'_rotation';raw_reports[name]={};projected[name]={};all_raw=[];all_projected=[];all_rows=[];edges=[]
  for part,rows in parts.items():
   values=[]
   for a,b in zip(raw[position][part],raw[rotation][part]):
    v=a.copy().reshape(-1,17,9);v[...,3:]=b.reshape(-1,17,9)[...,3:];values.append(v.reshape(-1,153))
   scored=evaluate_predictions(rows,values)
   for group in ['aggregate','cohorts']:
    keys=[None] if group=='aggregate' else scored[group]
    for key in keys:
     row=scored[group] if key is None else scored[group][key];pr=raw_reports[position][part][group] if key is None else raw_reports[position][part][group][key];rr=raw_reports[rotation][part][group] if key is None else raw_reports[rotation][part][group][key]
     require(row['position']==pr['position'] and row['rotation']==rr['rotation'],'Component substitution altered non-donor raw scores')
   raw_reports[name][part]=scored;pred,metrics=project_windows(rows,values,skeleton,protocol['projection']);scored=evaluate_predictions(rows,pred);scored['aggregate']['true_edge_length_max']=metrics['true_edge_length_max'];scored['projection']=metrics;projected[name][part]=scored;all_raw+=values;all_projected+=pred;all_rows+=rows;edges.append(metrics['true_edge_length_max'])
  raw_reports[name]['combined']=evaluate_predictions(all_rows,all_raw);scored=evaluate_predictions(all_rows,all_projected);scored['aggregate']['true_edge_length_max']=max(edges);projected[name]['combined']=scored
  print(json.dumps(dict(event='crossed_complete',method=name,seconds=time.perf_counter()-start)),flush=True)
 gates={name:{part:acceptance(dict(reports['v23']['partition_reports'][part],mlp=scored),protocol) for part,scored in values.items()} for name,values in projected.items()};cohorts=[]
 for part in parts:
  for key in projected['v23'][part]['cohorts']:
   controls={b:reports['v23']['partition_reports'][part][b]['cohorts'][key]['position'] for b in protocol['baselines']};den=min(controls.values());ratios={n:p[part]['cohorts'][key]['position']/den for n,p in projected.items()};interaction=ratios['v24']-ratios['v24_position_v23_rotation']-ratios['v23_position_v24_rotation']+ratios['v23']
   cohorts.append(dict(partition=part,cohort=key,projected_position_ratios=ratios,interaction_ratio=interaction,raw_position={n:p[part]['cohorts'][key]['position'] for n,p in raw_reports.items()},raw_rotation={n:p[part]['cohorts'][key]['rotation'] for n,p in raw_reports.items()}))
 summary={n:dict(failed_cohorts=sum(row['projected_position_ratios'][n]>1.1 for row in cohorts),new_failures_vs_v23=[row['cohort'] for row in cohorts if row['projected_position_ratios'][n]>1.1 and row['projected_position_ratios']['v23']<=1.1],gates=gates[n]) for n in projected}
 require(all(sha(ROOT/n)==h for n,h in sources.items()),'Sources changed');sealed()
 result=dict(complete=True,scope='Exposed development controlled2x2 diagnostic; not a fitted or independently qualified candidate',source_sha256=sources,model_sha256=plan['models'],prior_report_sha256={v:sha(ROOT/'results'/v/'report.json') for v in folders.values()},raw_reports=raw_reports,projected_reports=projected,summary=summary,cohorts=cohorts,raw_donor_invariance_passed=True,confirmation_accessed=False,seconds=time.perf_counter()-start,full_goal_complete=False)
 write(out,result);print(json.dumps(dict(complete=True,failed_cohorts={n:s['failed_cohorts'] for n,s in summary.items()},seconds=result['seconds'])),flush=True)
if __name__=='__main__':main()
