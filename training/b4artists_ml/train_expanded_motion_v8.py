"""Reproducible expanded learning with prospective untouched confirmation."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','4')
from pathlib import Path
import argparse,json,time,hashlib
from sequence_data import load_windows
from sequence_model import evaluate_windows,acceptance
from temporal_data import validate_manifests
from temporal_model import selection
from train_temporal_motion import restore
from kernel_motion import prepare as prepare_base,kernel_trials,save_model,load_model,evaluate_model
from context_gate import prepare as prepare_gate,base_locals,evaluate_gate
from context_motion import evaluate_context
from fetch_cmu_temporal_v8 import fetch
ROOT=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--output',default='motion_expansion_v8');parser.add_argument('--reproduce',action='store_true');args=parser.parse_args()
 if not args.output.replace('_','').isalnum():raise ValueError('Simple unique output name required')
 out=ROOT/'results'/args.output;out.mkdir(exist_ok=False);start=time.perf_counter();p=json.loads((ROOT/'motion_expansion_protocol_v8.json').read_text());assert p['expansion_plan_sha256']==sha(ROOT/'temporal_expansion_plan_v8.json')
 prior=json.loads((ROOT/'results/training_manifest_v4.json').read_text());extra=json.loads((ROOT/'temporal_expansion_manifest_v8.json').read_text());combined=dict(files=prior['files']+[r for r in extra['files'] if r['split']!='confirmation'])
 validate_manifests([combined]);(out/'protocol.json').write_text(json.dumps(p,indent=2)+'\n');(out/'training_validation_manifest.json').write_text(json.dumps(combined,indent=2)+'\n')
 train,sk=load_windows(ROOT,combined,'train',p);val,vsk=load_windows(ROOT,combined,'validation',p);assert sk==vsk
 old_clips={r['clip'] for r in prior['files'] if r['split']=='validation'};oldval=[w for w in val if w['clip'] in old_clips];newval=[w for w in val if w['clip'] not in old_clips]
 old_base=load_model(ROOT/'results/kernel_motion_v3/selected.npz');old_gate=load_model(ROOT/'results/context_gate_v6/selected_gate.npz');ridge=restore(ROOT/'results/sequence_motion_v2/ridge.npz')
 z,weight,mean,std,target=prepare_base(train,'raw_pose');_,alpha=next(kernel_trials(z,weight,target,.25,[10.]));base=dict(kind='kernel',variant='raw_pose',mean=mean,std=std,centers=z,width=.25,alpha=alpha);save_model(out/'expanded_base.npz',base)
 contextual=[w for w in train if w['context']];training_base=base_locals(base,contextual);z,weight,mean,std,target=prepare_gate(contextual,training_base,'compact');_,alpha=next(kernel_trials(z,weight,target,2.,[.1]));gate=dict(kind='context_gate_v1',variant='compact',mean=mean,std=std,centers=z,width=2.,alpha=alpha,control_sha256=sha(out/'expanded_base.npz'));save_model(out/'expanded_gate.npz',gate)
 def report(windows,b,g):
  rows={k:evaluate_windows(windows,sk,k,ridge if k=='ridge' else None) for k in p['baselines'] if k not in ('context_fk','v3_control')};rows['context_fk']=evaluate_context(None,windows,sk);rows['v3_control']=evaluate_model(old_base,windows,sk);rows['v6_reference']=evaluate_gate(old_gate,windows,base_locals(old_base,windows),sk);rows['mlp']=evaluate_gate(g,windows,base_locals(b,windows),sk);return rows
 candidate=report(val,base,gate);old_candidate=report(oldval,base,gate);new_candidate=report(newval,base,gate)
 current=candidate['v6_reference'];old_current=old_candidate['v6_reference'];protect=all(old_candidate['mlp']['aggregate'][k]<=old_current['aggregate'][k]*1.02 for k in ('position','rotation'))
 selected='expanded' if selection(candidate['mlp'])<selection(current) and protect else 'v6_control'
 selected_base,selected_gate=(base,gate) if selected=='expanded' else (old_base,old_gate)
 model_paths=[out/'expanded_base.npz',out/'expanded_gate.npz'] if selected=='expanded' else [ROOT/'results/kernel_motion_v3/selected.npz',ROOT/'results/context_gate_v6/selected_gate.npz']
 frozen=dict(selected=selected,confirmation_loaded=False,plan_sha256=sha(ROOT/'temporal_expansion_plan_v8.json'),protocol_sha256=sha(ROOT/'motion_expansion_protocol_v8.json'),training_validation_manifest_sha256=sha(out/'training_validation_manifest.json'),model_files={str(v.relative_to(ROOT)):sha(v) for v in model_paths},source_sha256={v.name:sha(v) for v in ROOT.glob('*.py')},skeleton=dict(names=sk[0],parents=sk[1],semantic=sk[2]),reproduction=args.reproduce)
 frozen_path=out/'selection_frozen.json';frozen_path.write_text(json.dumps(frozen,indent=2)+'\n');print(json.dumps(dict(event='selected_before_confirmation',selected=selected,old_validation_protection=protect,expanded_score=selection(candidate['mlp']),incumbent_score=selection(current))),flush=True)
 if not args.reproduce:extra=fetch(frozen_path)
 else:
  extra=json.loads((ROOT/'temporal_expansion_manifest_v8.json').read_text());assert extra['confirmation_selection_sha256']
 confirmation_rows=[r for r in extra['files'] if r['split']=='confirmation'];assert len(confirmation_rows)==3;validate_manifests([combined,dict(files=confirmation_rows)])
 confirmation,csk=load_windows(ROOT,dict(files=confirmation_rows),'confirmation',p);assert csk==sk
 confirm=report(confirmation,selected_base,selected_gate)
 validation=candidate if selected=='expanded' else report(val,selected_base,selected_gate)
 observed_manifest=json.loads((ROOT/'context_confirmation_manifest.json').read_text());observed,osk=load_windows(ROOT,observed_manifest,'confirmation',p);assert osk==sk;observed_report=report(observed,selected_base,selected_gate)
 result=dict(status='research_only',full_goal_complete=False,selection=frozen,expanded_candidate_validation=candidate,expanded_candidate_old_validation=old_candidate,expanded_candidate_new_validation=new_candidate,validation=validation,confirmation=confirm,observed_development=observed_report,gates=dict(validation=acceptance(validation,p),untouched_confirmation=acceptance(confirm,p),observed_development=acceptance(observed_report,p)),seconds=time.perf_counter()-start,windows=dict(train=len(train),validation=len(val),confirmation=len(confirmation)),downloaded_bytes=extra['additional_raw_bytes'],confirmation_first_selection_sha256=extra['confirmation_selection_sha256'],confirmation_is_fresh=not args.reproduce,limits=['No rig/mesh temporal workflow or human/Cascadeur comparison','Dataset subject labels do not prove actor independence','Exact file IDs/content hashes disjoint; semantic near-duplicates are not ruled out','Repetition of confirmation is reproduction, never a second blind study'])
 (out/'report.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(event='complete',selected=selected,gates=result['gates'],seconds=result['seconds'])),flush=True)
if __name__=='__main__':main()
