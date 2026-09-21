"""Training-only objective concentration; no independent gate validation claim."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','4')
from pathlib import Path
import json,time
import numpy as np
import mixture_trajectory_v21 as mixture
import kinematic_trajectory_v20 as parent
from semantic_projection import load_windows
from crossfit_controller import grouped_folds
from fetch_cmu_temporal_v19 import sha,read,write,require
ROOT=Path(__file__).resolve().parent

def main():
 out=ROOT/'results/mixture-training-diagnosis-v22.json';require(not out.exists(),'Evidence exists');start=time.perf_counter()
 protocol=read(ROOT/'mixture_trajectory_protocol_v21.json');report=read(ROOT/'results/mixture_trajectory_v21/report.json');manifest=read(ROOT/'temporal_training_manifest_v19.json')
 for n,h in protocol['source_manifests'].items():require(sha(ROOT/n)==h,'Manifest changed')
 for n,h in report['source_sha256'].items():require(sha(ROOT/n)==h,'Source changed')
 model=mixture.load(ROOT/'results/mixture_trajectory_v21/best_learned.npz');train,_=load_windows(ROOT,manifest,'train',protocol);folds=grouped_folds(train,4);recorded=read(ROOT/'results/kinematic_trajectory_v20/folds.json');groups={}
 for fold,(training,testing) in enumerate(folds):
  require(dict(training_clips=sorted({train[i]['clip'] for i in training}),testing_clips=sorted({train[i]['clip'] for i in testing}))==recorded[fold],'Fold changed')
  path=ROOT/f'results/kinematic_trajectory_v20/fold_{fold}.npz';require(sha(path)==protocol['parent_files'][path.relative_to(ROOT).as_posix()],'Parent changed');pm=parent.load(path)
  for i in testing:
   w=train[i];pred=mixture.expert_predictions(pm,w['observations'],w['t']);gate=mixture.blend(pred,mixture.strengths(model,w['observations']),w['t']);all_predictions=pred+[gate]
   target=w['target'].reshape(-1,17,9)[...,:3];op=mixture.operators(w,protocol['gate_training'])
   errors=[a.reshape(-1,17,9)[...,:3]-target for a in all_predictions]
   mse=[float(np.mean(e**2)) for e in errors];loss=[float(np.sum((op@e.reshape(-1,51))**2)/51) for e in errors]
   key=f"{w['clip']}/gap{w['gap']}/context{int(w['context'])}";groups.setdefault(key,[]).append(dict(position_mse=mse,trajectory_loss=loss))
  print(json.dumps(dict(event='training_fold_diagnosed',fold=fold,seconds=time.perf_counter()-start)),flush=True)
 rows=[]
 for key,values in sorted(groups.items()):
  mse=np.mean([v['position_mse'] for v in values],axis=0);loss=np.mean([v['trajectory_loss'] for v in values],axis=0)
  rows.append(dict(cohort=key,windows=len(values),position_mse=mse.tolist(),trajectory_loss=loss.tolist(),best_procedural_position_mse=float(min(mse[:3]))))
 total=sum(r['trajectory_loss'][-1] for r in rows)
 for r in rows:r['gate_loss_share']=r['trajectory_loss'][-1]/total
 top=sorted(rows,key=lambda r:-r['gate_loss_share']);n=len(rows)
 result=dict(scope='Training-only cohort diagnostics using group-excluded parent predictions. The gate saw these labels, so its results are in-sample.',methods=['linear','hermite','shape','v20','v21_gate'],training_windows=len(train),cohorts=n,largest_quarter_loss_share=sum(r['gate_loss_share'] for r in top[:int(np.ceil(n/4))]),largest_tenth_loss_share=sum(r['gate_loss_share'] for r in top[:int(np.ceil(n/10))]),baseline_position_mse_quantiles=np.quantile([r['best_procedural_position_mse'] for r in rows],[0,.1,.25,.5,.75,.9,1]).tolist(),rows=rows,source_sha256={Path(__file__).name:sha(Path(__file__))},parent_report_sha256=sha(ROOT/'results/mixture_trajectory_v21/report.json'),confirmation_accessed=False,seconds=time.perf_counter()-start)
 write(out,result);print(json.dumps({k:v for k,v in result.items() if k!='rows'}),flush=True)
if __name__=='__main__':main()
