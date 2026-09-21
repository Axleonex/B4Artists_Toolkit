"""Training-only coverage audit; no fitting or new validation/asset access."""
from pathlib import Path
import json,hashlib,collections,time
import numpy as np
ROOT=Path(__file__).resolve().parents[2];TR=Path(__file__).resolve().parent

def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 path=TR/'results/sequence-corpus-v2/manifest.json';manifest=read(path);old=read(TR/'results/temporal-data-audit-v19.json');assert manifest['complete'] and manifest['partition']=='train'
 train={r['clip'] for r in read(TR/'temporal_training_manifest_v19.json')['files'] if r['split']=='train'};assert set(c['clip'] for c in manifest['clips'])==train
 windows=manifest['windows'];by_bucket=collections.defaultdict(list)
 for w in windows:by_bucket[w['bucket']].append(w)
 ids=np.triu_indices(17,1);shapes={};variation=0.;observed_counts=[]
 for item in manifest['files']:
  p=ROOT/item['path'];assert sha(p)==item['sha256']
  with np.load(p,allow_pickle=False) as z:
   condition=z['condition'];assert condition.shape[-1]==394
   rest=condition[:,0,340:391].reshape(-1,17,3).astype(float)
   distances=np.linalg.norm(rest[:,:,None,:]-rest[:,None,:,:],axis=-1)[:,ids[0],ids[1]]
   distances/=np.max(distances,axis=1,keepdims=True)
   for w in by_bucket[item['frames']]:
    shape=distances[w['index']];clip=w['clip']
    if clip in shapes:variation=max(variation,float(np.max(abs(shape-shapes[clip]))))
    else:shapes[clip]=shape.copy()
    masks=condition[w['index'],:,306:340]
    observed_counts.append(float(np.mean(masks)))
 groups=[]
 for clip,shape in sorted(shapes.items()):
  match=next((g for g in groups if np.max(abs(shape-g['shape']))<=1e-4),None)
  if match is None:groups.append(dict(shape=shape,clips=[clip]))
  else:match['clips'].append(clip)
 durations={r['clip']:r['motion_seconds'] for r in old['rows']};assert set(durations)==train
 report=dict(complete=True,train_only=True,new_validation_reads=False,confirmation_read=False,downloads=False,fitting=False,manifest_sha256=sha(path),script_sha256=sha(Path(__file__)),clips=len(train),catalog_groups=len({c.split('_')[0] for c in train}),distinct_motion_seconds=sum(durations.values()),clip_duration_seconds=dict(min=min(durations.values()),median=float(np.median(list(durations.values()))),max=max(durations.values())),windows=len(windows),windows_by_gap=dict(collections.Counter(str(w['gap']) for w in windows)),windows_by_context=dict(collections.Counter(str(w['context']) for w in windows)),windows_by_mask=dict(collections.Counter(w['mask_pattern'] for w in windows)),normalized_rest_shape_groups=[g['clips'] for g in groups],shape_group_tolerance=1e-4,shape_measure='All136pairwise17joint rest distances normalized by largest pair; independent of global rotation/translation/uniform scale. Converted source geometry, not original performer anatomy.',within_clip_shape_max_difference=variation,known_group_fraction=dict(min=min(observed_counts),median=float(np.median(observed_counts)),max=max(observed_counts)),conditioning_gaps=['Complete boundary poses required by current adapter','No explicit contact intent','No explicit style/movement intent','No force or angular-momentum conditioning'],full_goal_complete=False,recorded_at=time.time())
 out=TR/'results/sequence-coverage-audit-v1.json';assert not out.exists();out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k!='normalized_rest_shape_groups'}));print('Rest shape groups:',len(groups))
if __name__=='__main__':main()
