"""Frozen paired context diagnosis; no fitting or production changes."""
from pathlib import Path
from dataclasses import replace
import os,json,time,hashlib,collections
os.environ.setdefault('OPENBLAS_NUM_THREADS','4')
import numpy as np
import semantic_motion_data as semantic
from bvh_data import parse_bvh
from sequence_provider_v2 import Provider,observed_request
from kinematic_trajectory_v20 import predict_packed as control
ROOT=Path(__file__).resolve().parents[2];TR=Path(__file__).resolve().parent;OUT=TR/'results/sequence-context-audit-v2'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.write_text(json.dumps(d,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def errors(p,y,dt):
 e=(p-y).reshape(-1,17,9)[...,:3]
 return dict(position=float(np.linalg.norm(e[1:-1],axis=-1).mean()),velocity=float(np.sqrt(np.mean((np.diff(e,axis=0)/dt)**2))),acceleration=float(np.sqrt(np.mean((np.diff(e,n=2,axis=0)/dt**2)**2))))
def main():
 OUT.mkdir(exist_ok=False);begin=time.perf_counter();manifest_path=TR/'results/sequence-corpus-v2/manifest.json';manifest=read(manifest_path);frozen=read(TR/'results/sequence-development-v1/frozen-before-validation.json');models=[m for m in frozen['models'] if m['kind']=='direct'];assert len(models)==2
 source_manifest=read(TR/'temporal_training_manifest_v19.json');protocol=read(TR/'expanded_trajectory_protocol_v19.json');protected=read(TR/'temporal_expansion_plan_v19.json')['planned_splits']['confirmation']
 sources={n:sha(TR/n) for n in ('sequence_provider_v2.py','sequence_numpy_v1.py','sequence_conditioning_v1.py','sequence_packet_v2.py','semantic_motion_data.py','rig_observations.py','kinematic_trajectory_v20.py','train_sequence_corpus_v2.py')}
 plan=dict(script_sha256=sha(Path(__file__)),sources=sources,manifest_sha256=sha(manifest_path),models=models,selection='Request equivalence: all1926 boundary-mask training windows. Paired inference: earliest boundary-mask training start per clip/gap, all384 development pairs. Both frozen direct seeds; original true context, no context, stationary exterior counterfactual. No tuning.',metrics='Paired same-target interior mean Euclidean position and derivative RMS; diagnostic, not original qualification aggregation.',limits=dict(seconds=1200,deadline=1789053845.,downloads=0,fits=0),confirmation_read=False);write(OUT/'plan.json',plan)
 def budget():assert time.perf_counter()-begin<1200 and time.time()<1789053845.
 assert all(not (TR/'cache'/(n+'.bvh')).exists() for n in protected)
 byclip=collections.defaultdict(list)
 for w in manifest['windows']:
  if w['mask_pattern']=='boundary':byclip[w['clip']].append(w)
 buckets={}
 for f in manifest['files']:
  p=ROOT/f['path'];assert sha(p)==f['sha256']
  with np.load(p,allow_pickle=False) as z:buckets[f['frames']]={k:z[k] for k in ('condition','baseline','mask','target')}
 equivalence=dict(windows=0,condition_max_abs=0.,baseline_max_abs=0.,target_max_abs=0.,mask_exact=True);train=[]
 for row in source_manifest['files']:
  if row['split']!='train':continue
  budget();path=TR/'cache'/(row['clip']+'.bvh');assert sha(path)==row['sha256'];seq=semantic.from_bvh(parse_bvh(path.read_text()),30);index={int(f):i for i,f in enumerate(seq.frames)};choices={}
  for w in byclip[row['clip']]:
   k=int(w['context']);start=index[w['source_frames'][k]];end=start+w['gap'];o=semantic.observe(seq,start,end,context=w['context']);req,times=observed_request(o);cache=buckets[w['bucket']];i=w['index'];n=len(times)
   for name,value in (('condition',req['condition']),('baseline',req['baseline'].reshape(n,153))):
    delta=float(np.max(abs(value-cache[name][i])));equivalence[name+'_max_abs']=max(equivalence[name+'_max_abs'],delta);assert delta<2e-6,(name,delta,w)
   assert np.array_equal(req['mask'].reshape(n,153),cache['mask'][i]);ids=np.arange(start-k,end+k+1);target=semantic.encode_targets(seq,ids,o).astype(np.float32);delta=float(np.max(abs(target-cache['target'][i])));assert delta<2e-6;equivalence['target_max_abs']=max(equivalence['target_max_abs'],delta);equivalence['windows']+=1
   choices[w['gap']]=min(choices.get(w['gap'],start),start)
  for gap,start in sorted(choices.items()):
   w=semantic.window(seq,start,start+gap,context=True);w['clip']=row['clip'];train.append(w)
 assert equivalence['windows']==1926;write(OUT/'request-equivalence.json',equivalence);del buckets
 validation=semantic.load_windows(TR,source_manifest,'validation',protocol);assert len(validation)==768;pairs={}
 for w in validation:pairs.setdefault((w['clip'],tuple(w['frame'])),{})[w['context']]=w
 assert len(pairs)==384
 for p in pairs.values():assert set(p)=={False,True} and np.array_equal(p[False]['target'],p[True]['target'])
 groups={'train':[w for w in train],'development':[p[True] for p in pairs.values()]};providers={m['name']:Provider(ROOT/m['weights'],m['weights_sha256'],kind=m['kind'],seed=m['seed']) for m in models};summaries={};allrows=[]
 for split,windows in groups.items():
  for wi,w in enumerate(windows):
   budget();o=w['observations'];p=o.positions.copy();r=o.rotations.copy();p[2:]=p[:2];r[2:]=r[:2];no=replace(o,positions=p,rotations=r,context=False);neutral=replace(o,positions=p,rotations=r,context=True);cases={'none':no,'true':o,'stationary_exterior':neutral};row=dict(split=split,clip=w['clip'],gap=w['gap'],frames=w['frame'].tolist(),methods={})
   predictions={}
   for name in ('linear','shape',*providers):
    outputs={};scored={}
    for variant,ob in cases.items():
     out=control(dict(kind='baseline',baseline=name),ob,w['t']) if name in ('linear','shape') else providers[name].predict_packed(ob,w['t']);assert np.array_equal(out[[0,-1]],w['linear'][[0,-1]]);assert np.max(abs(out[[0,-1]]-w['target'][[0,-1]]))<1e-12;outputs[variant]=out;scored[variant]=errors(out,w['target'],w['dt'])
    def distance(a,b):return float(np.linalg.norm((a-b).reshape(-1,17,9)[1:-1,:,:3],axis=-1).mean())
    row['methods'][name]=dict(errors=scored,true_vs_none_displacement=distance(outputs['true'],outputs['none']),true_vs_stationary_displacement=distance(outputs['true'],outputs['stationary_exterior']))
   allrows.append(row)
   if wi%32==0:write(OUT/'progress.json',dict(split=split,completed=wi+1,total=len(windows),seconds=time.perf_counter()-begin))
  selected=[r for r in allrows if r['split']==split];summary={}
  for name in ('linear','shape',*providers):
   values=[r['methods'][name] for r in selected];summary[name]=dict(errors={v:{k:float(np.mean([q['errors'][v][k] for q in values])) for k in ('position','velocity','acceleration')} for v in cases},mean_true_vs_none_displacement=float(np.mean([q['true_vs_none_displacement'] for q in values])),mean_true_vs_stationary_displacement=float(np.mean([q['true_vs_stationary_displacement'] for q in values])),fraction_context_improves_position=float(np.mean([q['errors']['true']['position']<q['errors']['none']['position'] for q in values])))
  summaries[split]=dict(pairs=len(selected),methods=summary);print(json.dumps(dict(split=split,pairs=len(selected),methods={k:v['errors'] for k,v in summary.items()})),flush=True)
 for n,h in sources.items():assert sha(TR/n)==h
 assert all(not (TR/'cache'/(n+'.bvh')).exists() for n in protected)
 write(OUT/'paired-windows.json',allrows);report=dict(complete=True,request_equivalence=equivalence,groups=summaries,seconds=time.perf_counter()-begin,plan_sha256=sha(OUT/'plan.json'),rows_sha256=sha(OUT/'paired-windows.json'),models_changed=False,retraining=False,confirmation_read=False,full_goal_complete=False);write(OUT/'report.json',report);print(json.dumps(dict(complete=True,seconds=report['seconds'])),flush=True)
if __name__=='__main__':main()
