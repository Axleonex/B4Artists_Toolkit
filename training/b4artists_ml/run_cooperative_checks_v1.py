"""Run isolated actual-rig suites with bound source and explicit process status."""
from pathlib import Path
import os,sys,json,subprocess,time,hashlib
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve()
def host(module,label):
 import unittest,importlib
 sys.path[:0]=[str(ROOT),str(ROOT/'tests'),str(ROOT/'training/b4artists_ml')]
 suite=unittest.defaultTestLoader.loadTestsFromName(module)
 result=unittest.TextTestRunner(verbosity=2).run(suite)
 report=dict(passed=result.wasSuccessful(),tests=result.testsRun,failures=[(str(t),s) for t,s in result.failures],errors=[(str(t),s) for t,s in result.errors],runtime_sha256={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'b4artists_ml').glob('*.py')},test_sha256=hashlib.sha256((ROOT/'tests'/(module.split('.')[0]+'.py')).read_bytes()).hexdigest())
 (ROOT/f'training/b4artists_ml/results/{label}.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(passed=report['passed'],tests=result.testsRun)),flush=True)
 if not report['passed']:raise SystemExit(1)
if __name__=='__main__':
 if '--host' in sys.argv:
  i=sys.argv.index('--host');host(sys.argv[i+1],sys.argv[i+2])
 else:
  module,label=sys.argv[1:];out=ROOT/f'training/b4artists_ml/results/{label}.json'
  if out.exists():raise RuntimeError('Evidence already exists')
  log=ROOT/f'training/b4artists_ml/cache/{label}.log';start=time.perf_counter()
  with log.open('w') as stream:
   proc=subprocess.run(['X:/5.1.0/bforartists.exe','--background','--factory-startup','--disable-autoexec','--python',str(HERE),'--','--host',module,label],stdout=stream,stderr=subprocess.STDOUT,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='4',B4ML_RUN_LABEL=label),timeout=420)
  receipt=dict(exit_code=proc.returncode,seconds=time.perf_counter()-start,log=log.relative_to(ROOT).as_posix(),result_present=out.exists());(out.parent/(label+'-process.json')).write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
