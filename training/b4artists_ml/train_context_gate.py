"""Frozen supervised context-controller experiment; no automatic promotion."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','4')
from pathlib import Path
import argparse,json,time,hashlib
import numpy as np
from sequence_data import load_windows
from sequence_model import evaluate_windows,acceptance
from temporal_data import validate_manifests
from temporal_model import selection
from train_temporal_motion import restore
from kernel_motion import save_model,load_model
from context_motion import evaluate_context
from context_gate import base_locals,prepare,kernel_trials,evaluate_gate
ROOT=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--output',default='context_gate_v6');args=parser.parse_args()
 if not args.output.replace('_','').isalnum():raise ValueError('Simple unique output name required')
 out=ROOT/'results'/args.output;out.mkdir(exist_ok=False);start=time.perf_counter();p=json.loads((ROOT/'context_gate_protocol_v6.json').read_text());manifests=[]
 for row in p['manifests']:
  path=ROOT/row['path'];assert sha(path)==row['sha256'];manifests.append(json.loads(path.read_text()))
 validate_manifests(manifests);(out/'protocol.json').write_text(json.dumps(p,indent=2)+'\n')
 train,skeleton=load_windows(ROOT,manifests[0],'train',p);train=[w for w in train if w['context']];val,vs=load_windows(ROOT,manifests[0],'validation',p);assert skeleton==vs
 ridge=restore(ROOT/'results/sequence_motion_v2/ridge.npz');control_path=ROOT/'results/kernel_motion_v3/selected.npz';control=load_model(control_path);old=json.loads((ROOT/'results/kernel_motion_v3/report.json').read_text());train_base=base_locals(control,train);val_base=base_locals(control,val)
 reports={k:evaluate_windows(val,skeleton,k,ridge if k=='ridge' else None) for k in p['baselines'] if k not in ('context_fk','v3_control')}
 for k,report in reports.items():assert report==old['validation'][k],k
 reports['context_fk']=evaluate_context(None,val,skeleton);reports['v3_control']=evaluate_gate(None,val,val_base,skeleton);assert reports['v3_control']==old['validation']['mlp']
 best_score=selection(reports['v3_control']);best='v3_control';best_model=None;reports['mlp']=reports['v3_control'];history=[]
 print(json.dumps(dict(event='baseline',incumbent_score=best_score,context_training_windows=len(train))),flush=True)
 for variant in p['feature_variants']:
  z,weight,mean,std,target=prepare(train,train_base,variant)
  for width in p['kernel_widths']:
   for reg,alpha in kernel_trials(z,weight,target,width,p['kernel_regularization']):
    model=dict(kind='context_gate_v1',variant=variant,mean=mean,std=std,centers=z,width=width,alpha=alpha,control_sha256=sha(control_path));report=evaluate_gate(model,val,val_base,skeleton);score=selection(report);identifier=f'{variant}_{width}_{reg}'
    history.append(dict(id=identifier,score=score,aggregate=report['aggregate']));print(json.dumps(dict(event='trial',id=identifier,score=score)),flush=True)
    if score<best_score:best_score=score;best=identifier;best_model=model;reports['mlp']=report;save_model(out/'selected_gate.npz',model)
 frozen=dict(selected=best,new_model_selected=best_model is not None,gate_sha256=sha(out/'selected_gate.npz') if best_model is not None else None,control_sha256=sha(control_path),development_loaded=False,skeleton=dict(names=skeleton[0],parents=skeleton[1],semantic=skeleton[2]),source_sha256={q.name:sha(q) for q in ROOT.glob('*.py')},protocol_sha256=sha(ROOT/'context_gate_protocol_v6.json'))
 (out/'selection.json').write_text(json.dumps(frozen,indent=2)+'\n')
 if best_model is not None:best_model=load_model(out/'selected_gate.npz')
 assert evaluate_gate(best_model,val,val_base,skeleton)==reports['mlp']
 dev,ds=load_windows(ROOT,manifests[1],'confirmation',p);assert ds==skeleton;dev_base=base_locals(control,dev)
 development={k:evaluate_windows(dev,skeleton,k,ridge if k=='ridge' else None) for k in p['baselines'] if k not in ('context_fk','v3_control')};development['context_fk']=evaluate_context(None,dev,skeleton);development['v3_control']=evaluate_gate(None,dev,dev_base,skeleton);development['mlp']=evaluate_gate(best_model,dev,dev_base,skeleton)
 gates=dict(validation=acceptance(reports,p),observed_development=acceptance(development,p));result=dict(status='research_only',full_goal_complete=False,selection=frozen,protocol=p,validation=reports,observed_development=development,candidates=history,gates=gates,seconds=time.perf_counter()-start,limits=['Previously observed validation/development; no fresh blind confirmation','No actual-rig temporal integration','Only the context controller is new; frozen V3 base remains an explicit inference dependency'])
 (out/'report.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(event='complete',selected=best,gates=gates,seconds=result['seconds'])),flush=True)
if __name__=='__main__':main()
