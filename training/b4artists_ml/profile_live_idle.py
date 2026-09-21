"""Bounded actual-rig profile of unchanged Live Solve requests; no runtime changes."""
from pathlib import Path
import os,sys,json,time,subprocess,hashlib
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve();TAG=os.environ.get('B4ML_LIVE_PROFILE_TAG','v1')

def run():
 import bpy,numpy as np,cProfile,pstats,io
 sys.path[:0]=[str(ROOT),str(ROOT/'tests')]
 from test_b4artists_ml_body_live import LivePoseTests
 from b4artists_ml import body_preview as body,body_live as live,workflow as w
 LivePoseTests.setUpClass();helper=LivePoseTests();records=[]
 for label in ('boneforge','rigify_default'):
  ob,source,modes,action,keys=helper.fixture(label);body.solve(ob);live.start(ob,now=0.)
  measures={name:[] for name in ('_get','_request','_read')};originals={name:getattr(body,name) for name in measures}
  def wrapper(name,fn):
   def call(*args,**kwargs):
    start=time.perf_counter()
    try:return fn(*args,**kwargs)
    finally:measures[name].append((time.perf_counter()-start)*1000)
   return call
  times=[]
  try:
   for name,fn in originals.items():setattr(body,name,wrapper(name,fn))
   for i in range(100):
    start=time.perf_counter();assert live.tick(ob,now=(i+1)*.02)=='idle';times.append((time.perf_counter()-start)*1000)
  finally:
   for name,fn in originals.items():setattr(body,name,fn)
  profiler=cProfile.Profile();profiler.enable()
  for i in range(20):assert live.tick(ob,now=3.+i*.02)=='idle'
  profiler.disable();stream=io.StringIO();pstats.Stats(profiler,stream=stream).sort_stats('cumulative').print_stats(20)
  assert not body._JOBS and live._WATCHERS[ob.as_pointer()]['completed']==0
  body.finish(ob,bpy.context.scene,False);assert w.raw_pose(ob)==source and ob.animation_data.action==action and helper.keys(ob)==keys
  records.append(dict(rig=label,unchanged_requests=100,tick_p50_ms=float(np.median(times)),tick_p95_ms=float(np.percentile(times,95)),tick_max_ms=max(times),components_inclusive={n:dict(calls=len(v),total_ms=sum(v),mean_ms=float(np.mean(v))) for n,v in measures.items()},cprofile_top=stream.getvalue(),source_preserved=True))
 out=ROOT/f'training/b4artists_ml/results/live-idle-profile-{TAG}.json';out.write_text(json.dumps(dict(records=records,runtime_sha256={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'b4artists_ml').glob('*.py')},scope='Bounded actual-host unchanged-request profiling; independent from the real-window timing sample; no responsiveness acceptance implied.'),indent=2)+'\n');print(json.dumps(records),flush=True)
if __name__=='__main__':
 if '--host' in sys.argv:run()
 else:
  result=ROOT/f'training/b4artists_ml/results/live-idle-profile-{TAG}.json'
  if result.exists():raise RuntimeError('Evidence exists')
  start=time.perf_counter()
  with (ROOT/f'training/b4artists_ml/cache/live-idle-profile-{TAG}.log').open('w') as log:
   p=subprocess.run(['X:/5.1.0/bforartists.exe','--background','--factory-startup','--disable-autoexec','--python',str(HERE),'--','--host'],stdout=log,stderr=subprocess.STDOUT,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='4'),timeout=180)
  report=dict(exit_code=p.returncode,seconds=time.perf_counter()-start,result_present=result.exists());(ROOT/f'training/b4artists_ml/results/live-idle-profile-process-{TAG}.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
