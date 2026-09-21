"""Stratify frozen failures without fitting or changing development acceptance."""
from pathlib import Path
import json,hashlib,collections,time
import numpy as np
from semantic_motion_data import load_windows
ROOT=Path(__file__).resolve().parents[2];TR=Path(__file__).resolve().parent;BASE=TR/'results/sequence-generalization-audit-v1'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.write_text(json.dumps(d,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def shape(rest):
 r=np.asarray(rest).reshape(17,3);i,j=np.triu_indices(17,1);d=np.linalg.norm(r[:,None]-r[None,:],axis=-1)[i,j];return d/d.max()
def main():
 manifest_path=TR/'results/sequence-corpus-v2/manifest.json';manifest=read(manifest_path);diag_path=TR/'results/sequence-projection-diagnosis-v1/report.json';diag=read(diag_path);assert manifest['complete'] and diag['complete']
 BASE.mkdir(exist_ok=False);plan=dict(source_manifest_sha256=sha(manifest_path),diagnosis_sha256=sha(diag_path),script_sha256=sha(Path(__file__)),selection='All original development cohorts; seen-shape classification based only on normalized pairwise rest distances and frozen1e-4tolerance from prior coverage audit.',reference='Fixed strongest combined procedural control: shape. Group values are equally weighted cohort means, not replacements for original frame-weighted acceptance.',no_training=True,no_downloads=True,confirmation_read=False);write(BASE/'plan.json',plan)
 train_shapes={};groups=collections.defaultdict(list)
 for w in manifest['windows']:groups[w['bucket']].append(w)
 for row in manifest['files']:
  needed=[w for w in groups[row['frames']] if w['clip'] not in train_shapes]
  if not needed:continue
  p=ROOT/row['path'];assert sha(p)==row['sha256']
  with np.load(p,allow_pickle=False) as z:condition=z['condition']
  for w in needed:train_shapes.setdefault(w['clip'],shape(condition[w['index'],0,340:391]))
 assert len(train_shapes)==78
 protocol=read(TR/'expanded_trajectory_protocol_v19.json');windows=load_windows(TR,read(TR/'temporal_training_manifest_v19.json'),'validation',protocol);assert len(windows)==768
 clips={}
 for w in windows:
  clip=w['clip']
  if clip in clips:continue
  value=shape(w['observations'].rest);dist={c:float(np.max(abs(value-r))) for c,r in train_shapes.items()};nearest=min(dist,key=dist.get);matches=sorted(c for c,v in dist.items() if v<=1e-4)
  clips[clip]=dict(shape_seen=bool(matches),nearest_train_clip=nearest,nearest_shape_max_difference=dist[nearest],matching_training_clips=matches)
 methods=diag['raw_and_projected']['combined'];cohorts=methods['projected_shape']['raw']['cohorts'];assert len(cohorts)==96
 keys={'all':list(cohorts)}
 for state in (True,False):keys['seen_shape' if state else 'novel_shape']=[k for k in cohorts if clips[k.split('/')[0]]['shape_seen']==state]
 for gap in (8,16,32):keys['gap'+str(gap)]=[k for k in cohorts if '/gap'+str(gap)+'/' in k]
 for context in (0,1):keys['context'+str(context)]=[k for k in cohorts if k.endswith('/context'+str(context))]
 reports={}
 for group,selected in keys.items():
  assert selected
  baseline={stage:{metric:float(np.mean([methods['projected_shape'][stage]['cohorts'][k][metric] for k in selected])) for metric in ('position','rotation','velocity','acceleration')} for stage in ('raw','projected')}
  values={}
  for name in methods:
   if name.startswith('projected_'):continue
   values[name]={stage:{metric:float(np.mean([methods[name][stage]['cohorts'][k][metric] for k in selected]))/max(baseline[stage][metric],1e-12) for metric in baseline[stage]} for stage in baseline}
  reports[group]=dict(cohorts=len(selected),clips=len({k.split('/')[0] for k in selected}),baseline=baseline,ratios=values)
 assert all(not (TR/'cache'/(n+'.bvh')).exists() for n in read(TR/'temporal_expansion_plan_v19.json')['planned_splits']['confirmation'])
 result=dict(complete=True,clip_shape_classification=clips,groups=reports,plan_sha256=sha(BASE/'plan.json'),models_changed=False,acceptance_changed=False,no_training=True,no_downloads=True,confirmation_read=False,full_goal_complete=False);write(BASE/'report.json',result)
 print(json.dumps(dict(complete=True,shape_groups={k:dict(cohorts=reports[k]['cohorts'],clips=reports[k]['clips'],raw_position_ratios={n:v['raw']['position'] for n,v in reports[k]['ratios'].items()}) for k in ('seen_shape','novel_shape')},timing={k:{n:v['raw']['position'] for n,v in reports[k]['ratios'].items()} for k in ('gap8','gap16','gap32')})),flush=True)
if __name__=='__main__':main()
