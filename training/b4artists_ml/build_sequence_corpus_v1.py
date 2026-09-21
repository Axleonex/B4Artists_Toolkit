"""Build frozen training-only sequence buckets; no validation or downloads."""
from pathlib import Path
import hashlib,json,time,os
import numpy as np
from bvh_data import parse_bvh
import temporal_data as td
from sequence_conditioning_v1 import request
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve();TR=HERE.parent;BASE=TR/'results/sequence-corpus-v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.write_text(json.dumps(d,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def main():
 plan_path=TR/'sequence_corpus_plan_v1.json';plan=json.loads(plan_path.read_text());manifest_path=TR/plan['source_manifest']['path'];assert sha(manifest_path)==plan['source_manifest']['sha256'];source=json.loads(manifest_path.read_text())['files'];source=[r for r in source if r['split']=='train'];assert len({r['sha256'] for r in source})==len(source)
 protected=json.loads((TR/'temporal_expansion_plan_v19.json').read_text())['planned_splits']['confirmation'];assert all(not (TR/'cache'/(n+'.bvh')).exists() for n in protected)
 BASE.mkdir(exist_ok=False);buckets={};windows=[];clips=[];started=time.perf_counter();memory=0
 for ci,row in enumerate(source):
  assert time.time()<plan['deadline_unix'];path=TR/'cache'/(row['clip']+'.bvh');assert sha(path)==row['sha256'];motion=td.temporal_motion(parse_bvh(path.read_text()),30);rng=np.random.default_rng(plan['data']['sampling_seed']+ci);count=0
  for gi,gap in enumerate(plan['data']['gaps']):
   available=np.arange(1,len(motion.points)-gap-1)
   if not len(available):continue
   starts=np.sort(rng.choice(available,min(plan['data']['windows_per_gap_per_clip'],len(available)),replace=False))
   for context in plan['data']['contexts']:
    for wi,start in enumerate(starts):
     start=int(start);end=start+gap;lo=start-1 if context else start;hi=end+1 if context else end;ids=np.arange(lo,hi+1);t=np.arange(gap+1)/gap;observed=td.features(motion,start,end,t,context);target=td.labels(motion,ids,observed['origin'],observed['basis']).reshape(len(ids),17,9);mask=np.zeros((len(ids),17,2),bool);mask[[0,-1]]=True
     if context:mask[[1,-2]]=True
     pattern=(ci+wi+gi+int(context))%3;offset=int(context)
     if pattern==1:mask[offset+gap//2]=True
     elif pattern==2:
      mask[offset+gap//3,[0,7,13],0]=True;mask[offset+2*gap//3,[4,10,16],1]=True
     req=request(np.arange(len(ids))*motion.dt,target,mask,motion.rest);n=len(ids);item=dict(condition=req['condition'],baseline=req['baseline'].reshape(n,153),target=target.reshape(n,153).astype(np.float32),mask=req['mask'].reshape(n,153),dt=np.array(motion.dt,dtype=np.float32))
     memory+=sum(v.nbytes for v in item.values());assert memory<=plan['data']['uncompressed_array_byte_cap'];index=len(buckets.setdefault(n,[]));buckets[n].append(item);windows.append(dict(clip=row['clip'],clip_sha256=row['sha256'],gap=gap,context=context,mask_pattern=plan['data']['mask_patterns'][pattern],source_frames=motion.frames[ids].tolist(),bucket=n,index=index));count+=1
  clips.append(dict(clip=row['clip'],sha256=row['sha256'],source_motion_frames=len(motion.points),dt=motion.dt,windows=count));write(BASE/'progress.json',dict(clips=len(clips),windows=len(windows),array_bytes=memory,seconds=time.perf_counter()-started));print(json.dumps(dict(clip=row['clip'],windows=count,completed_clips=len(clips))),flush=True)
 files=[];bytes_written=0
 for n,items in sorted(buckets.items()):
  arrays={key:np.stack([item[key] for item in items]) for key in items[0]};assert all(np.isfinite(v).all() for v in arrays.values());path=BASE/f'frames-{n}.npz';np.savez_compressed(path,**arrays);bytes_written+=path.stat().st_size;assert bytes_written<=plan['data']['cache_byte_cap'];files.append(dict(path=path.relative_to(ROOT).as_posix(),sha256=sha(path),bytes=path.stat().st_size,frames=n,windows=len(items),array_bytes=sum(a.nbytes for a in arrays.values())))
 assert all(not (TR/'cache'/(n+'.bvh')).exists() for n in protected)
 result=dict(complete=True,partition='train',clips=clips,clip_count=len(clips),window_count=len(windows),windows=windows,files=files,source_manifest_sha256=sha(manifest_path),plan_sha256=sha(plan_path),script_sha256=sha(HERE),conditioning_sha256=sha(TR/'sequence_conditioning_v1.py'),array_bytes=memory,cache_bytes=bytes_written,seconds=time.perf_counter()-started,validation_read=False,confirmation_read=False,full_goal_complete=False)
 write(BASE/'manifest.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ('clips','windows','files')}),flush=True)
if __name__=='__main__':main()
