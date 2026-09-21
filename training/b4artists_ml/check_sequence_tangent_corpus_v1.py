"""Verify tangent conditioning on every frozen training packet, without fitting."""
from pathlib import Path
import json,hashlib,time,collections,os
os.environ.setdefault('OPENBLAS_NUM_THREADS','4')
import numpy as np
import semantic_motion_data as semantic
from sequence_packet_v2 import packet
from sequence_tangent_context_v1 import build
from bvh_data import parse_bvh
TR=Path(__file__).resolve().parent;ROOT=TR.parents[1];OUT=TR/'results/sequence-tangent-corpus-v1'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 OUT.mkdir(exist_ok=False);start=time.perf_counter();manifest=read(TR/'results/sequence-corpus-v2/manifest.json');groups=collections.defaultdict(list)
 for w in manifest['windows']:groups[w['clip']].append(w)
 plan=dict(script_sha256=sha(Path(__file__)),manifest_sha256=sha(TR/'results/sequence-corpus-v2/manifest.json'),feature_sha256=sha(TR/'sequence_tangent_context_v1.py'),selection='All5778original training packets with unchanged masks and frames; no labels as features',max_seconds=600,no_training=True,no_downloads=True,validation_read=False,confirmation_read=False)
 (OUT/'plan.json').write_text(json.dumps(plan,indent=2)+'\n');rows=[];maximum=0.;count=0;patterns=collections.Counter();max_known_error=0.
 for clip,windows in groups.items():
  assert time.perf_counter()-start<600 and time.time()<1789053845.;path=TR/'cache'/(clip+'.bvh');assert sha(path)==windows[0]['clip_sha256'];seq=semantic.from_bvh(parse_bvh(path.read_text()),30);frame_index={int(f):i for i,f in enumerate(seq.frames)}
  for w in windows:
   offset=int(w['context']);a=frame_index[w['source_frames'][offset]];b=a+w['gap'];pattern=['boundary','middle_full_pose','partial_body'].index(w['mask_pattern']) if w['mask_pattern'] in ['boundary','middle_full_pose','partial_body'] else None
   if pattern is None:
    names=read(TR/'sequence_corpus_plan_v2.json')['data']['mask_patterns'];pattern=names.index(w['mask_pattern'])
   p=packet(seq,a,b,context=w['context'],pattern=pattern);assert seq.frames[p['indices']].tolist()==w['source_frames'];req=p['request'];result=build(req['times'],req['observed'],p['mask'],req['rest']);assert np.array_equal(result['condition'][:,:394],req['condition']);assert np.array_equal(result['request']['observed'][req['mask']],req['observed'][req['mask']]);features=result['tangent_context'];maximum=max(maximum,float(np.max(abs(features))));assert np.isfinite(features).all();patterns[w['mask_pattern']]+=1;count+=1
  rows.append(dict(clip=clip,windows=len(windows)));print(json.dumps(dict(clips=len(rows),windows=count,seconds=time.perf_counter()-start)),flush=True) if len(rows)%20==0 else None
 assert count==5778 and len(rows)==78;protected=read(TR/'temporal_expansion_plan_v19.json')['planned_splits']['confirmation'];assert all(not (TR/'cache'/(n+'.bvh')).exists() for n in protected);assert sha(TR/'sequence_tangent_context_v1.py')==plan['feature_sha256']
 report=dict(complete=True,windows=count,clips=len(rows),patterns=dict(patterns),condition_prefix_exact=True,known_observations_exact=True,finite=True,max_absolute_feature=maximum,seconds=time.perf_counter()-start,plan_sha256=sha(OUT/'plan.json'),no_training=True,validation_read=False,confirmation_read=False,full_goal_complete=False)
 (OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
if __name__=='__main__':main()
