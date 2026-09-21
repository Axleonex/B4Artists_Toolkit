"""Load original frozen buckets and append observed-only tangent features in RAM."""
from pathlib import Path
import json,hashlib,time,collections
import numpy as np
from bvh_data import parse_bvh
import semantic_motion_data as semantic
from sequence_packet_v2 import packet
from sequence_tangent_context_v1 import build
TR=Path(__file__).resolve().parent

def augment(data,manifest,*,max_seconds=600):
 start=time.perf_counter();byframes={row['frames']:d for row,d in zip(manifest['files'],data,strict=True)};groups=collections.defaultdict(list);count=0;before={}
 def sha_array(a):return hashlib.sha256(a.tobytes()).hexdigest()
 for n,d in byframes.items():
  before[n]={k:sha_array(v) for k,v in d.items()};d['tangent']=np.empty((*d['condition'].shape[:2],272),np.float32)
 for w in manifest['windows']:groups[w['clip']].append(w)
 patterns=json.loads((TR/'sequence_corpus_plan_v2.json').read_text())['data']['mask_patterns']
 for clip,rows in groups.items():
  assert time.perf_counter()-start<max_seconds and time.time()<1789053845.
  path=TR/'cache'/(clip+'.bvh');assert hashlib.sha256(path.read_bytes()).hexdigest()==rows[0]['clip_sha256'];seq=semantic.from_bvh(parse_bvh(path.read_text()),30);index={int(f):i for i,f in enumerate(seq.frames)}
  for row in rows:
   a=index[row['source_frames'][int(row['context'])]];p=packet(seq,a,a+row['gap'],context=row['context'],pattern=patterns.index(row['mask_pattern']));assert seq.frames[p['indices']].tolist()==row['source_frames'];req=p['request'];d=byframes[row['bucket']];i=row['index'];assert np.array_equal(req['condition'],d['condition'][i]);value=build(req['times'],req['observed'],p['mask'],req['rest']);d['tangent'][i]=value['tangent_context'];count+=1
 for n,d in byframes.items():
  assert all(sha_array(d[k])==h for k,h in before[n].items());old=d['condition'];d['condition']=np.concatenate((old,d.pop('tangent')),axis=-1);assert np.array_equal(d['condition'][...,:394],old) and np.isfinite(d['condition']).all()
 assert count==5778
 return dict(windows=count,seconds=time.perf_counter()-start,original_arrays_unchanged=True,array_bytes=sum(v.nbytes for d in data for v in d.values()))
