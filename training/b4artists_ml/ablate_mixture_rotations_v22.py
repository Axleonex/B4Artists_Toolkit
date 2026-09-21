"""Diagnostic projected procedural positions with frozen learned rotations."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','4')
from pathlib import Path
import json,time
import numpy as np
import kinematic_trajectory_v20 as predictor
from semantic_projection import load_windows,project_windows
from motion_coverage import evaluate_predictions
from sequence_model import acceptance
from fetch_cmu_temporal_v19 import sha,read,write,require
ROOT=Path(__file__).resolve().parent

def main():
 out=ROOT/'results/mixture-rotation-ablation-v22.json';require(not out.exists(),'Evidence exists');start=time.perf_counter()
 protocol=read(ROOT/'mixture_trajectory_protocol_v21.json');prior=read(ROOT/'results/mixture_trajectory_v21/report.json')
 for n,h in protocol['source_manifests'].items():require(sha(ROOT/n)==h,'Manifest changed')
 for n,h in prior['source_sha256'].items():require(sha(ROOT/n)==h,'Source changed')
 path=ROOT/'results/kinematic_trajectory_v20/best_learned.npz';require(sha(path)==protocol['prior_model_sha256'],'Parent changed');model=predictor.load(path)
 manifest=read(ROOT/'temporal_training_manifest_v19.json');windows,skeleton=load_windows(ROOT,manifest,'validation',protocol);old=set(protocol['old_validation_clips']);new=set(protocol['new_validation_clips']);parts={'old_validation':[w for w in windows if w['clip'] in old],'new_validation':[w for w in windows if w['clip'] in new]};require(sum(map(len,parts.values()))==len(windows),'Partition changed')
 report=dict(scope='Exposed development diagnostic ablations, not independently qualified candidates or pure procedural controls. No training, selection, retuning or confirmation access.',projection=protocol['projection'],methods={},source_sha256={Path(__file__).name:sha(Path(__file__))},parent_sha256=sha(path),prior_report_sha256=sha(ROOT/'results/mixture_trajectory_v21/report.json'),confirmation_accessed=False)
 for kind in ['linear','hermite','shape']:
  methods={};all_windows=[];all_predictions=[];edges=[]
  for part,rows in parts.items():
   raw=[]
   for w in rows:
    a=predictor.predict_packed(dict(kind='baseline',baseline=kind),w['observations'],w['t']).reshape(-1,17,9);b=predictor.predict_packed(model,w['observations'],w['t']).reshape(-1,17,9);a[...,3:]=b[...,3:];raw.append(a.reshape(-1,153))
   pred,metrics=project_windows(rows,raw,skeleton,protocol['projection']);scored=evaluate_predictions(rows,pred);scored['aggregate']['true_edge_length_max']=metrics['true_edge_length_max'];scored['projection']=metrics;methods[part]=scored;all_windows+=rows;all_predictions+=pred;edges.append(metrics['true_edge_length_max'])
  combined=evaluate_predictions(all_windows,all_predictions);combined['aggregate']['true_edge_length_max']=max(edges);methods['combined']=combined
  gates={part:acceptance(dict(prior['partition_reports'][part],mlp=scored),protocol) for part,scored in methods.items()}
  report['methods'][kind+'_position_v20_rotation']=dict(partition_reports=methods,diagnostic_gates=gates)
  print(json.dumps(dict(event='ablation_complete',kind=kind,gates=gates,seconds=time.perf_counter()-start)),flush=True)
 report.update(seconds=time.perf_counter()-start,complete=True);write(out,report)
if __name__=='__main__':main()
