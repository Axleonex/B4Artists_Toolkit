"""Build frozen training-only sequence buckets; no validation or downloads."""
from pathlib import Path
import hashlib,json,time,os
import numpy as np
from bvh_data import parse_bvh
import semantic_motion_data as semantic
from sequence_packet_v2 import packet
from sequence_conditioning_v1 import request
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve();TR=HERE.parent;BASE=TR/'results/sequence-corpus-v2'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.write_text(json.dumps(d,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def main():
 plan_path=TR/'sequence_corpus_plan_v2.json';plan=json.loads(plan_path.read_text());manifest_path=TR/plan['source_manifest']['path'];assert sha(manifest_path)==plan['source_manifest']['sha256'];source=json.loads(manifest_path.read_text())['files'];source=[r for r in source if r['split']=='train'];assert len({r['sha256'] for r in source})==len(source)
 protected=json.loads((TR/'temporal_expansion_plan_v19.json').read_text())['planned_splits']['confirmation'];assert all(not (TR/'cache'/(n+'.bvh')).exists() for n in protected)
 BASE.mkdir(exist_ok=False);buckets={};windows=[];clips=[];started=time.perf_counter();memory=0
 for ci,row in enumerate(source):
  assert time.time()<plan['deadline_unix'];path=TR/'cache'/(row['clip']+'.bvh');assert sha(path)==row['sha256'];motion=semantic.from_bvh(parse_bvh(path.read_text()),30);rng=np.random.default_rng(plan['data']['sampling_seed']+ci);count=0
  for gi,gap in enumerate(plan['data']['gaps']):
   available=np.arange(1,len(motion.positions)-gap-1)
   if not len(available):continue
   starts=np.sort(rng.choice(available,min(plan['data']['windows_per_gap_per_clip'],len(available)),replace=False))
   for context in plan['data']['contexts']:
    for wi,start in enumerate(starts):
     start=int(start);end=start+gap;pattern=(ci+wi+gi+int(context))%3;encoded=packet(motion,start,end,context=context,pattern=pattern);req=encoded['request'];target=encoded['target'];ids=encoded['indices'];n=len(ids);item=dict(condition=req['condition'],baseline=req['baseline'].reshape(n,153),target=target.reshape(n,153).astype(np.float32),mask=req['mask'].reshape(n,153),dt=np.array(motion.dt,dtype=np.float32))
     memory+=sum(v.nbytes for v in item.values());assert memory<=plan['data']['uncompressed_array_byte_cap'];index=len(buckets.setdefault(n,[]));buckets[n].append(item);windows.append(dict(clip=row['clip'],clip_sha256=row['sha256'],gap=gap,context=context,mask_pattern=plan['data']['mask_patterns'][pattern],source_frames=motion.frames[ids].tolist(),bucket=n,index=index));count+=1
  clips.append(dict(clip=row['clip'],sha256=row['sha256'],source_motion_frames=len(motion.positions),dt=motion.dt,windows=count));write(BASE/'progress.json',dict(clips=len(clips),windows=len(windows),array_bytes=memory,seconds=time.perf_counter()-started));print(json.dumps(dict(clip=row['clip'],windows=count,completed_clips=len(clips))),flush=True)
 files=[];bytes_written=0
 for n,items in sorted(buckets.items()):
  arrays={key:np.stack([item[key] for item in items]) for key in items[0]};assert all(np.isfinite(v).all() for v in arrays.values());path=BASE/f'frames-{n}.npz';np.savez_compressed(path,**arrays);bytes_written+=path.stat().st_size;assert bytes_written<=plan['data']['cache_byte_cap'];files.append(dict(path=path.relative_to(ROOT).as_posix(),sha256=sha(path),bytes=path.stat().st_size,frames=n,windows=len(items),array_bytes=sum(a.nbytes for a in arrays.values())))
 assert all(not (TR/'cache'/(n+'.bvh')).exists() for n in protected)
 result=dict(complete=True,partition='train',clips=clips,clip_count=len(clips),window_count=len(windows),windows=windows,files=files,source_manifest_sha256=sha(manifest_path),plan_sha256=sha(plan_path),script_sha256=sha(HERE),conditioning_sha256=sha(TR/'sequence_conditioning_v1.py'),packet_sha256=sha(TR/'sequence_packet_v2.py'),semantic_encoder_sha256=sha(TR/'semantic_motion_data.py'),array_bytes=memory,cache_bytes=bytes_written,seconds=time.perf_counter()-started,validation_read=False,confirmation_read=False,full_goal_complete=False)
 write(BASE/'manifest.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ('clips','windows','files')}),flush=True)
if __name__=='__main__':main()
