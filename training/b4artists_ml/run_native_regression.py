"""Versioned native integration regression without overwriting suite-owned reports."""
from pathlib import Path
import sys,os,json,subprocess,time,hashlib,traceback
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve()
PREFIX=os.environ.get('B4ML_RUN_LABEL','native-integration-v1')

def host(suite):
    import unittest
    sys.path[:0]=[str(ROOT),str(ROOT/'tests')]
    try:
        import importlib
        if '.' not in suite:
            module=importlib.import_module(suite)
            classes=[v for v in vars(module).values() if isinstance(v,type) and issubclass(v,unittest.TestCase) and v.__module__==suite]
            cases=unittest.TestSuite()
            for cls in classes:
                if suite in ('test_b4artists_ml_bend_limits','test_b4artists_ml_joint_frames'):
                    cases.addTests(cls(n) for n in cls.__dict__ if n.startswith('test_'))
                else:cases.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(cls))
        else:cases=unittest.defaultTestLoader.loadTestsFromName(suite)
        result=unittest.TextTestRunner(verbosity=2).run(cases)
        report=dict(suite=suite,tests=result.testsRun,assertions_passed=result.wasSuccessful(),failures=[(t.id(),v) for t,v in result.failures],errors=[(t.id(),v) for t,v in result.errors],skipped=[(t.id(),v) for t,v in result.skipped])
    except BaseException:report=dict(suite=suite,tests=0,assertions_passed=False,error=traceback.format_exc())
    report['runtime_sha256']={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'b4artists_ml').glob('*.py')}
    (ROOT/f'training/b4artists_ml/results/{PREFIX}-{suite}.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)

def main():
    suites=os.environ.get('B4ML_SUITES','').split(',')
    if suites==['']:
        suites=[r['suite'] for r in json.loads((ROOT/'training/b4artists_ml/results/regression-v0.13.1.json').read_text())]
        suites+=['test_b4artists_ml_motion_layer','test_b4artists_ml_native_flight','test_b4artists_ml_support_math','test_b4artists_ml_balance_math','test_b4artists_ml_flight_math']
    rows=[]
    for suite in suites:
        output=ROOT/f'training/b4artists_ml/results/{PREFIX}-{suite}.json'
        if output.exists():raise RuntimeError('Evidence exists: '+str(output))
        log=ROOT/f'training/b4artists_ml/cache/{PREFIX}-{suite}.log';start=time.perf_counter()
        with log.open('w') as stream:
            p=subprocess.run(['X:/5.1.0/bforartists.exe','--background','--factory-startup','--disable-autoexec','--python',str(HERE),'--',suite],stdout=stream,stderr=subprocess.STDOUT,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='4'),timeout=900)
        row=json.loads(output.read_text()) if output.exists() else dict(suite=suite,tests=0,assertions_passed=False,error='Missing host report')
        row.update(host_exit=p.returncode,elapsed_seconds=time.perf_counter()-start,log=str(log.relative_to(ROOT)),sha256=hashlib.sha256(log.read_bytes()).hexdigest());rows.append(row)
        (ROOT/f'training/b4artists_ml/results/{PREFIX}-regression.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps({k:row[k] for k in ('suite','tests','assertions_passed','host_exit','elapsed_seconds')}),flush=True)
        if not row['assertions_passed']:break
if __name__=='__main__':
    if '--' in sys.argv:host(sys.argv[sys.argv.index('--')+1])
    else:main()
