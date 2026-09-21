"""Measure fresh reconstruction from current actual-preview JSON records."""
from pathlib import Path
import os,sys,json,time,hashlib,subprocess
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve();TAG='record-copy-v1';OUT=ROOT/f'training/b4artists_ml/results/{TAG}.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def host():
 import bpy,numpy as np,copy,pickle,marshal
 sys.path[:0]=[str(ROOT),str(ROOT/'tests')]
 from test_b4artists_ml_body_live import LivePoseTests
 from b4artists_ml import body_preview as body,workflow as w,rig_state as rs
 meta=json.loads((ROOT/'docs/b4artists_ml/package-test-v0.17.4.json').read_text());current={p.relative_to(ROOT).as_posix():sha(p) for p in (ROOT/'b4artists_ml').glob('*.py')};assert current==meta['runtime_sha256'];LivePoseTests.setUpClass();helper=LivePoseTests();rows=[]
 for label in ['boneforge','rigify_default','rigify_basic','metarig_basic','metarig_default']:
  ob,source,modes,action,keys=helper.fixture(label);payload=ob.b4ml.body_payload;record=body._decode(payload);before=w.raw_pose(ob);encoding={};blobs={}
  for name,encode in [('pickle',lambda:pickle.dumps(record,protocol=5)),('marshal',lambda:marshal.dumps(record))]:
   start=time.perf_counter();blobs[name]=encode();encoding[name]=dict(ms=(time.perf_counter()-start)*1000,bytes=len(blobs[name]))
  functions={'json_decode':lambda:body._decode(payload),'deepcopy_validated_tree':lambda:copy.deepcopy(record),'pickle_local_copy':lambda:pickle.loads(blobs['pickle']),'marshal_local_copy':lambda:marshal.loads(blobs['marshal'])};samples={k:[] for k in functions};bone=next(iter(record['session']['source']))
  for name,fn in functions.items():
   first=fn();second=fn();assert first==second==record and first is not second and first['session']['source'][bone]['location'] is not second['session']['source'][bone]['location'];first['session']['source'][bone]['location'][0]=12345.;first['signature']={'changed':True};assert second==record and fn()==record
  names=list(functions)
  for run in range(5):
   order=names if run%2==0 else list(reversed(names))
   for name in order:
    for _ in range(40):
     start=time.perf_counter();value=functions[name]();elapsed=(time.perf_counter()-start)*1000;samples[name].append(elapsed)
    assert value==record
  assert ob.b4ml.body_payload==payload and w.raw_pose(ob)==before
  body.finish(ob,bpy.context.scene,False);assert w.raw_pose(ob)==source and rs.mode_values(ob)==modes and ob.animation_data.action==action and helper.keys(ob)==keys
  scored={name:dict(calls=len(values),p50_ms=float(np.median(values)),p95_ms=float(np.percentile(values,95)),max_ms=max(values),samples_ms=values) for name,values in samples.items()}
  row=dict(rig=label,payload_characters=len(payload),payload_utf8_bytes=len(payload.encode()),payload_sha256=hashlib.sha256(payload.encode()).hexdigest(),encoding=encoding,methods=scored,independent_mutable_records=True,nested_mutation_isolated=True,payload_unchanged=True,source_recovered=True);rows.append(row)
  report=dict(passed=True,complete=len(rows)==5,rows=rows,runtime_sha256=current,harness_sha256=sha(HERE),plan_sha256=sha(ROOT/'training/b4artists_ml/record_copy_plan_v1.json'),scope='Actual-preview reconstruction microbenchmark only; binary blobs generated locally from validated primitive JSON and never accepted externally. No runtime cache or complete-solve/UI performance qualification.',full_goal_complete=False)
  OUT.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(rig=label,bytes=row['payload_utf8_bytes'],p50_ms={n:v['p50_ms'] for n,v in scored.items()})),flush=True)
if __name__=='__main__':
 if '--host' in sys.argv:host()
 else:
  assert not OUT.exists();start=time.perf_counter();log=ROOT/f'training/b4artists_ml/cache/{TAG}.log'
  with log.open('w') as stream:done=subprocess.run(['X:/5.1.0/bforartists.exe','--background','--factory-startup','--disable-autoexec','--python',str(HERE),'--','--host'],stdout=stream,stderr=subprocess.STDOUT,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='4',B4ML_RUN_LABEL=TAG),timeout=180)
  receipt=dict(exit_code=done.returncode,seconds=time.perf_counter()-start,log=log.relative_to(ROOT).as_posix());(OUT.parent/(TAG+'-process.json')).write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
