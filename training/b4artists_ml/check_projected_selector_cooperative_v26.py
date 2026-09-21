"""Run cooperative reference/source/lifecycle and action guards with the trained provider."""

from pathlib import Path

import os,sys,json,hashlib,time,subprocess

ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve();TAG='projected-selector-cooperative-v26';OUT=ROOT/f'training/b4artists_ml/results/{TAG}.json'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def host():

    import unittest

    sys.path[:0]=[str(ROOT),str(ROOT/'tests'),str(ROOT/'training/b4artists_ml')]

    import projected_selector_v26 as predictor

    import temporal_projection as projection

    import test_b4artists_ml_temporal_cooperative as cooperative_tests
    import test_b4artists_ml_temporal_cooperative_pipeline as pipeline_tests

    folder=ROOT/'training/b4artists_ml/results/projected_selector_v26';report=json.loads((folder/'report.json').read_text());complete=json.loads((folder/'complete.json').read_text())

    assert complete['complete'] and complete['report_sha256']==sha(folder/'report.json')

    digest=sha(folder/'best_learned.npz');assert digest==report['selection']['best_learned_sha256'];model=predictor.load(folder/'best_learned.npz')

    provider=predictor.provider(model);calls=[0];records=[]

    def observed_only(observations,t):calls[0]+=1;return provider(observations,t)

    # Test-local substitution only: production source and installed UI are unchanged.

    old=projection.procedural;projection.procedural=observed_only

    class CountingResult(unittest.TextTestResult):

        def startTest(self,test):self.before=calls[0];super().startTest(test)

        def stopTest(self,test):records.append(dict(test=test.id(),trained_provider_calls=calls[0]-self.before));super().stopTest(test)

    try:

        suite=unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromTestCase(cooperative_tests.CooperativeTemporalTests),unittest.defaultTestLoader.loadTestsFromTestCase(pipeline_tests.CooperativePipelineTests)])

        result=unittest.TextTestRunner(verbosity=2,resultclass=CountingResult).run(suite)

    finally:projection.procedural=old

    used=sum(r['trained_provider_calls']>0 for r in records)

    passed=result.wasSuccessful() and result.testsRun==25 and len(records)==25 and not result.skipped and used>=17

    proof=dict(complete=True,passed=passed,tests=result.testsRun,tests_using_trained_provider=used,total_provider_calls=calls[0],records=records,failures=[(t.id(),v) for t,v in result.failures],errors=[(t.id(),v) for t,v in result.errors],skipped=[(t.id(),v) for t,v in result.skipped],model_sha256=digest,quality_qualified=report['gates']['best_learned']['passed'],runtime_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (ROOT/'b4artists_ml').glob('*.py')},research_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in [HERE,ROOT/'training/b4artists_ml/projected_selector_v26.py',ROOT/'training/b4artists_ml/temporal_projection.py',ROOT/'tests/test_b4artists_ml_temporal_projection.py',ROOT/'tests/test_b4artists_ml_temporal_cooperative.py',ROOT/'tests/test_b4artists_ml_temporal_cooperative_pipeline.py',ROOT/'training/b4artists_ml/temporal_cooperative_v1.py',ROOT/'training/b4artists_ml/temporal_observer_steps_v1.py']},scope='Existing25native cooperative source-visible/lifecycle/action guards run with a test-local trained-provider substitution. Reference parity uses the same actual trained provider in synchronous and cooperative engines. Per-test counters distinguish model use from general pipeline guards. Covers stored priorities/subframes, explicit pins, unselected accessory/mesh, cancellation/fault rollback and Keep/save/reload/source restoration. No GUI input, independent animator judgment or release qualification.',full_goal_complete=False)

    OUT.write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(dict(passed=passed,tests=proof['tests'],tests_using_trained_provider=used,total_provider_calls=calls[0])),flush=True)

if __name__=='__main__':

    if '--host' in sys.argv:host()

    else:

        if OUT.exists():raise RuntimeError('Evidence exists')

        log=ROOT/f'training/b4artists_ml/cache/{TAG}.log';start=time.perf_counter()

        with log.open('w') as stream:

            process=subprocess.run(['X:/5.1.0/bforartists.exe','--background','--factory-startup','--disable-autoexec','--python',str(HERE),'--','--host'],stdout=stream,stderr=subprocess.STDOUT,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='4',B4ML_RUN_LABEL=TAG),timeout=900)

        receipt=dict(exit_code=process.returncode,seconds=time.perf_counter()-start,log=log.relative_to(ROOT).as_posix());(OUT.parent/(TAG+'-process.json')).write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)

