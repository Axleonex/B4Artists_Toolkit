"""Counterbalanced native test of selective temporal state restoration."""
from pathlib import Path
import os,sys,json,time,hashlib,subprocess
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve();TAG='temporal-observer-benchmark-v1';OUT=ROOT/f'training/b4artists_ml/results/{TAG}.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def host():
    import numpy as np
    sys.path[:0]=[str(ROOT),str(ROOT/'tests'),str(ROOT/'training/b4artists_ml')]
    from test_b4artists_ml_temporal_cooperative import CooperativeTemporalTests
    import temporal_cooperative_v1 as c
    import temporal_projection as ref
    import importlib.util
    spec=importlib.util.spec_from_file_location("temporal_observer_baseline",ROOT/"training/b4artists_ml/results/temporal-observer-baseline-v1/temporal_cooperative_v1.py")
    baseline=importlib.util.module_from_spec(spec);spec.loader.exec_module(baseline)
    plan=json.loads((ROOT/'training/b4artists_ml/temporal_observer_plan_v1.json').read_text())
    assert sha(ROOT/plan['baseline'])==plan['baseline_sha256']
    assert sha(ROOT/'training/b4artists_ml/temporal_cooperative_v1.py')==plan['candidate_sha256']
    assert sha(ROOT/'training/b4artists_ml/temporal_observer_steps_v1.py')==plan['sampler_sha256']
    CooperativeTemporalTests.setUpClass();helper=CooperativeTemporalTests();records=[]
    try:
        for index,(label,context) in enumerate((p,k) for p in plan['profiles'] for k in plan['contexts']):
            obj,_=helper.fixture(label);before=helper.visible(obj);inventory=helper.inventory();fixture=[]
            order=['baseline','candidate','candidate','baseline'] if index%2==0 else ['candidate','baseline','baseline','candidate']
            for variant in order:
                engine=baseline if variant=='baseline' else c
                job=engine.generate_steps(obj,ref.procedural,context=context);ticks=[];phases=[]
                try:
                    while True:
                        start=time.perf_counter()
                        try:progress=next(job)
                        except StopIteration as done:result=done.value;ticks.append((time.perf_counter()-start)*1000);phases.append(['complete',None]);break
                        ticks.append((time.perf_counter()-start)*1000);phases.append([progress['phase'],progress['frame']]);assert helper.visible(obj)==before
                finally:job.close()
                assert helper.visible(obj)==before and helper.inventory()==inventory and not engine._LIVE and not engine._OWNERS
                samples,metrics=result;deterministic=[{k:v for k,v in row.items() if k not in ('elapsed_ms','proxy_init_ms')} for row in metrics]
                row=dict(profile=label,context=context,variant=variant,samples_sha256=digest(samples),metrics_sha256=digest(deterministic),phases=phases,tick_ms=ticks,max_tick_ms=max(ticks),total_active_ms=sum(ticks),source_restored=True)
                fixture.append(row);records.append(row)
                OUT.write_text(json.dumps(dict(complete=False,records=records),indent=2)+'\n');print(json.dumps({k:row[k] for k in ('profile','context','variant','max_tick_ms','total_active_ms')}),flush=True)
            assert len({x['samples_sha256'] for x in fixture})==1,'Sample mismatch'
            assert len({x['metrics_sha256'] for x in fixture})==1,'Deterministic solver metric mismatch'
            filtered=[[p for p in x['phases'] if p[0]!='observed_pose'] for x in fixture]
            assert all(x==filtered[0] for x in filtered),'Solver step sequence changed'
    finally:c.unregister();baseline.unregister()
    comparisons=[]
    for label in plan['profiles']:
        for context in plan['contexts']:
            groups={v:[x for x in records if x['profile']==label and x['context']==context and x['variant']==v] for v in ('baseline','candidate')}
            def mean(variant,key):return float(np.mean([x[key] for x in groups[variant]]))
            comparisons.append(dict(profile=label,context=context,maximum_tick_ratio=mean('candidate','max_tick_ms')/mean('baseline','max_tick_ms'),active_work_ratio=mean('candidate','total_active_ms')/mean('baseline','total_active_ms'),baseline_maximum_tick_mean=mean('baseline','max_tick_ms'),candidate_maximum_tick_mean=mean('candidate','max_tick_ms')))
    default=[x for x in comparisons if x['profile']=='rigify_default'];gates=dict(default_worst_tick=float(np.mean([x['maximum_tick_ratio'] for x in default]))<=.9,bounded_scheduling_overhead=all(x['active_work_ratio']<=1.25 for x in comparisons),no_fixture_tick_regression=all(x['maximum_tick_ratio']<=1.05 for x in comparisons))
    result=dict(complete=True,passed=all(gates.values()),gates=gates,comparisons=comparisons,records=records,exact_samples_metrics_and_filtered_phases=True,source_preserved=True,plan=plan,full_goal_complete=False,full_responsiveness=all(x['max_tick_ms']<=50 for x in records if x['variant']=='candidate'),scope='24counterbalanced research-host runs with two concurrent training jobs; no runtime or model promotion.',source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in [HERE,ROOT/'training/b4artists_ml/temporal_cooperative_v1.py',ROOT/'training/b4artists_ml/temporal_observer_steps_v1.py',ROOT/'tests/test_b4artists_ml_temporal_cooperative.py']})
    OUT.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(complete=True,passed=result['passed'],gates=gates,comparisons=comparisons)),flush=True)
if __name__=='__main__':
    if '--host' in sys.argv:host()
    else:
        assert not OUT.exists();log=ROOT/f'training/b4artists_ml/cache/{TAG}.log';start=time.perf_counter()
        with log.open('w') as stream:
            process=subprocess.run(['X:/5.1.0/bforartists.exe','--background','--factory-startup','--disable-autoexec','--python',str(HERE),'--','--host'],stdout=stream,stderr=subprocess.STDOUT,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='4'),timeout=900)
        receipt=dict(exit_code=process.returncode,seconds=time.perf_counter()-start,log=log.relative_to(ROOT).as_posix());(OUT.parent/(TAG+'-process.json')).write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
