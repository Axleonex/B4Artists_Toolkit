"""Frozen contextual residual learning comparison, research only."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','4')
from pathlib import Path
import argparse,json,time,hashlib,shutil
import numpy as np
from sequence_data import load_windows
from sequence_model import evaluate_windows,acceptance
from temporal_data import validate_manifests
from temporal_model import selection
from train_temporal_motion import restore
from kernel_motion import prepare,kernel_trials,save_model,load_model,evaluate_model
from context_motion import contextual_windows,evaluate_context
ROOT=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--output',default='context_motion_v5');args=parser.parse_args()
 if not args.output.replace('_','').isalnum():raise ValueError('Simple unique output name required')
 out=ROOT/'results'/args.output;out.mkdir(exist_ok=False);start=time.perf_counter();p=json.loads((ROOT/'context_motion_protocol_v5.json').read_text());manifests=[]
 for row in p['manifests']:
  path=ROOT/row['path'];assert sha(path)==row['sha256'];manifests.append(json.loads(path.read_text()))
 validate_manifests(manifests);(out/'protocol.json').write_text(json.dumps(p,indent=2)+'\n')
 train,skeleton=load_windows(ROOT,manifests[0],'train',p);val,vs=load_windows(ROOT,manifests[0],'validation',p);assert skeleton==vs
 ridge=restore(ROOT/'results/sequence_motion_v2/ridge.npz');control=load_model(ROOT/'results/kernel_motion_v3/selected.npz');old=json.loads((ROOT/'results/kernel_motion_v3/report.json').read_text())
 reports={k:evaluate_windows(val,skeleton,k,ridge if k=='ridge' else None) for k in p['baselines'] if k not in ('context_fk','v3_control')}
 for k,report in reports.items():assert report==old['validation'][k],k
 reports['context_fk']=evaluate_context(None,val,skeleton);reports['v3_control']=evaluate_model(control,val,skeleton);assert reports['v3_control']==old['validation']['mlp']
 best=min(('context_fk','v3_control'),key=lambda k:selection(reports[k]));best_score=selection(reports[best]);reports['mlp']=reports[best];new_learner_selected=False;learned=best=='v3_control';selected_context=best=='context_fk'
 z,weight,mean,std,target=prepare(contextual_windows(train),'raw_pose')
 if selected_context:save_model(out/'selected.npz',dict(kind='zero',variant='raw_pose',mean=mean,std=std,baseline='quaternion_hermite_v1'))
 else:shutil.copyfile(ROOT/'results/kernel_motion_v3/selected.npz',out/'selected.npz')
 history=[];print(json.dumps(dict(event='baseline',context=reports['context_fk']['aggregate'],incumbent=best)),flush=True)
 for width in p['kernel_widths']:
  for reg,alpha in kernel_trials(z,weight,target,width,p['kernel_regularization']):
   model=dict(kind='kernel',variant='raw_pose',mean=mean,std=std,centers=z,width=width,alpha=alpha,baseline='quaternion_hermite_v1');report=evaluate_context(model,val,skeleton);score=selection(report);identifier=f'context_kernel_{width}_{reg}'
   history.append(dict(id=identifier,score=score,aggregate=report['aggregate']));print(json.dumps(dict(event='trial',id=identifier,score=score)),flush=True)
   if score<best_score:best_score=score;best=identifier;reports['mlp']=report;selected_context=True;learned=True;new_learner_selected=True;save_model(out/'selected.npz',model)
 frozen=dict(selected=best,selected_sha256=sha(out/'selected.npz'),learned=learned,new_learner_selected=new_learner_selected,contextual_baseline=selected_context,development_loaded=False,skeleton=dict(names=skeleton[0],parents=skeleton[1],semantic=skeleton[2]),source_sha256={str(q.relative_to(ROOT)):sha(q) for q in ROOT.glob('*.py')},protocol_sha256=sha(ROOT/'context_motion_protocol_v5.json'))
 (out/'selection.json').write_text(json.dumps(frozen,indent=2)+'\n');model=load_model(out/'selected.npz')
 infer=evaluate_context if selected_context else evaluate_model;assert infer(model,val,skeleton)==reports['mlp']
 dev,ds=load_windows(ROOT,manifests[1],'confirmation',p);assert ds==skeleton
 development={k:evaluate_windows(dev,skeleton,k,ridge if k=='ridge' else None) for k in p['baselines'] if k not in ('context_fk','v3_control')};development['context_fk']=evaluate_context(None,dev,skeleton);development['v3_control']=evaluate_model(control,dev,skeleton);development['mlp']=infer(model,dev,skeleton)
 gates=dict(validation=acceptance(reports,p),observed_development=acceptance(development,p));result=dict(status='research_only',full_goal_complete=False,selection=frozen,protocol=p,validation=reports,observed_development=development,candidates=history,gates=gates,seconds=time.perf_counter()-start,learned=learned,new_learner_selected=new_learner_selected,limits=['Previously observed validation/development; no fresh blind confirmation','No actual-rig temporal integration','Contextual Hermite is procedural; only the fitted residual is learned'])
 (out/'report.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(event='complete',selected=best,learned=learned,gates=gates,seconds=result['seconds'])),flush=True)
if __name__=='__main__':main()
