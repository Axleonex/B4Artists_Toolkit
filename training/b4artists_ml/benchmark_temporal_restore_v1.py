"""Counterbalanced native test of selective temporal state restoration."""
from pathlib import Path
import os,sys,json,time,hashlib,subprocess
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve();TAG='temporal-restore-benchmark-v1';OUT=ROOT/f'training/b4artists_ml/results/{TAG}.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def host():
    import numpy as np
    sys.path[:0]=[str(ROOT),str(ROOT/'tests'),str(ROOT/'training/b4artists_ml')]
    from test_b4artists_ml_temporal_cooperative import CooperativeTemporalTests
    import temporal_cooperative_v1 as c
    import temporal_projection as ref
    from temporal_restore_optimization_v1 import SelectiveVisibleState
    plan=json.loads((ROOT/'training/b4artists_ml/temporal_restore_optimization_plan_v1.json').read_text())
    assert sha(ROOT/'training/b4artists_ml/temporal_cooperative_v1.py')==plan['baseline_sha256']
    assert sha(ROOT/'training/b4artists_ml/temporal_restore_optimization_v1.py')==plan['candidate_sha256']
    CooperativeTemporalTests.setUpClass();helper=CooperativeTemporalTests();original=c.VisibleState;records=[]
    try:
        for index,(label,context) in enumerate((p,k) for p in plan['profiles'] for k in plan['contexts']):
            obj,_=helper.fixture(label);before=helper.visible(obj);inventory=helper.inventory();fixture=[]
            order=['baseline','candidate','candidate','baseline'] if index%2==0 else ['candidate','baseline','baseline','candidate']
            for variant in order:
                c.VisibleState=original if variant=='baseline' else SelectiveVisibleState
                job=c.generate_steps(obj,ref.procedural,context=context);ticks=[];phases=[]
                try:
                    while True:
                        start=time.perf_counter()
                        try:progress=next(job)
                        except StopIteration as done:result=done.value;ticks.append((time.perf_counter()-start)*1000);phases.append(['complete',None]);break
                        ticks.append((time.perf_counter()-start)*1000);phases.append([progress['phase'],progress['frame']]);assert helper.visible(obj)==before
                finally:job.close()
                assert helper.visible(obj)==before and helper.inventory()==inventory and not c._LIVE and not c._OWNERS
                samples,metrics=result;deterministic=[{k:v for k,v in row.items() if k not in ('elapsed_ms','proxy_init_ms')} for row in metrics]
                row=dict(profile=label,context=context,variant=variant,samples_sha256=digest(samples),metrics_sha256=digest(deterministic),phases=phases,tick_ms=ticks,max_tick_ms=max(ticks),total_active_ms=sum(ticks),source_restored=True)
                fixture.append(row);records.append(row)
                OUT.write_text(json.dumps(dict(complete=False,records=records),indent=2)+'\n');print(json.dumps({k:row[k] for k in ('profile','context','variant','max_tick_ms','total_active_ms')}),flush=True)
            assert len({x['samples_sha256'] for x in fixture})==1,'Sample mismatch'
            assert len({x['metrics_sha256'] for x in fixture})==1,'Deterministic solver metric mismatch'
            assert all(x['phases']==fixture[0]['phases'] for x in fixture),'Solver step sequence changed'
    finally:c.VisibleState=original;c.unregister()
    comparisons=[]
    for label in plan['profiles']:
        for context in plan['contexts']:
            groups={v:[x for x in records if x['profile']==label and x['context']==context and x['variant']==v] for v in ('baseline','candidate')}
            def mean(variant,key):return float(np.mean([x[key] for x in groups[variant]]))
            comparisons.append(dict(profile=label,context=context,maximum_tick_ratio=mean('candidate','max_tick_ms')/mean('baseline','max_tick_ms'),active_work_ratio=mean('candidate','total_active_ms')/mean('baseline','total_active_ms'),baseline_maximum_tick_mean=mean('baseline','max_tick_ms'),candidate_maximum_tick_mean=mean('candidate','max_tick_ms')))
    default=[x for x in comparisons if x['profile']=='rigify_default'];gates=dict(default_worst_tick=float(np.mean([x['maximum_tick_ratio'] for x in default]))<=.9,default_active_work=float(np.mean([x['active_work_ratio'] for x in default]))<=1.,no_fixture_regression=all(x['maximum_tick_ratio']<=1.05 and x['active_work_ratio']<=1.05 for x in comparisons))
    result=dict(complete=True,passed=all(gates.values()),gates=gates,comparisons=comparisons,records=records,exact_samples_metrics_and_phases=True,source_preserved=True,plan=plan,full_goal_complete=False,full_responsiveness=all(x['max_tick_ms']<=50 for x in records if x['variant']=='candidate'),scope='24counterbalanced research-host runs with two concurrent training jobs; no runtime or model promotion.',source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in [HERE,ROOT/'training/b4artists_ml/temporal_cooperative_v1.py',ROOT/'training/b4artists_ml/temporal_restore_optimization_v1.py',ROOT/'tests/test_b4artists_ml_temporal_cooperative.py']})
    OUT.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(complete=True,passed=result['passed'],gates=gates,comparisons=comparisons)),flush=True)
if __name__=='__main__':
    if '--host' in sys.argv:host()
    else:
        assert not OUT.exists();log=ROOT/f'training/b4artists_ml/cache/{TAG}.log';start=time.perf_counter()
        with log.open('w') as stream:
            process=subprocess.run(['X:/5.1.0/bforartists.exe','--background','--factory-startup','--disable-autoexec','--python',str(HERE),'--','--host'],stdout=stream,stderr=subprocess.STDOUT,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='4'),timeout=900)
        receipt=dict(exit_code=process.returncode,seconds=time.perf_counter()-start,log=log.relative_to(ROOT).as_posix());(OUT.parent/(TAG+'-process.json')).write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
