"""Research cache invariants plus existing live/record guards in real host."""
from pathlib import Path
import sys,os,json,time,subprocess,hashlib
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve();TAG='record-cache-check-v1'
def host(suite):
 sys.path[:0]=[str(ROOT),str(ROOT/'tests'),str(HERE.parent)]
 from record_cache_prototype_v1 import install,RecordCopies
 cache=install();a='{"schema":1,"nested":[[1,2]]}';x=cache(a);y=cache(a);assert x==y and x is not y and x['nested'][0] is not y['nested'][0];x['nested'][0][0]=9;assert cache(a)==y
 for i in range(8):cache(json.dumps(dict(schema=1,n=i)))
 assert len(cache.cache)==4 and a not in cache.cache
 before=list(cache.cache)
 for _ in range(2):
  try:cache('{')
  except json.JSONDecodeError:pass
  else:raise AssertionError('Invalid payload accepted')
 assert list(cache.cache)==before
 uncached=RecordCopies(cache.decode,payload_characters=2);assert uncached(a)==y and not uncached.cache
 uncached=RecordCopies(cache.decode,blob_bytes=1);assert uncached(a)==y and not uncached.cache
 cache.clear();assert not cache.cache
 import run_native_regression as runner
 runner.PREFIX=TAG;runner.host(suite)
 path=ROOT/f'training/b4artists_ml/results/{TAG}-{suite}.json';report=json.loads(path.read_text());report.update(research_cache=True,cache_invariants_passed=True,prototype_sha256=hashlib.sha256((HERE.parent/'record_cache_prototype_v1.py').read_bytes()).hexdigest(),cache_hits=cache.hits,cache_misses=cache.misses);path.write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':
 if '--host' in sys.argv:host(sys.argv[-1])
 else:
  rows=[]
  for suite in ['test_b4artists_ml_preview_reads','test_b4artists_ml_body_live']:
   path=ROOT/f'training/b4artists_ml/results/{TAG}-{suite}.json';assert not path.exists();log=ROOT/f'training/b4artists_ml/cache/{TAG}-{suite}.log';start=time.perf_counter()
   with log.open('w') as stream:proc=subprocess.run(['X:/5.1.0/bforartists.exe','--background','--factory-startup','--disable-autoexec','--python',str(HERE),'--','--host',suite],stdout=stream,stderr=subprocess.STDOUT,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='4',B4ML_RUN_LABEL=TAG),timeout=180)
   report=json.loads(path.read_text()) if path.exists() else dict(assertions_passed=False,error='Missing report');report.update(host_exit=proc.returncode,seconds=time.perf_counter()-start,log=log.relative_to(ROOT).as_posix());rows.append(report);(ROOT/f'training/b4artists_ml/results/{TAG}.json').write_text(json.dumps(dict(complete=len(rows)==2,passed=all(r['assertions_passed'] for r in rows),rows=rows),indent=2)+'\n');print(json.dumps(dict(suite=suite,passed=report['assertions_passed'],tests=report.get('tests'),host_exit=proc.returncode)),flush=True)
   if not report['assertions_passed']:break
