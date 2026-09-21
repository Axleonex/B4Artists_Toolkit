"""Profile next-step costs; profiling overhead is not a performance benchmark."""
from pathlib import Path
import os,sys,json,time,subprocess,hashlib
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve();TAG='temporal-cooperative-profile-v1'
OUT=ROOT/f'training/b4artists_ml/results/{TAG}.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def host():
    import cProfile,pstats
    sys.path[:0]=[str(ROOT),str(ROOT/'tests'),str(ROOT/'training/b4artists_ml')]
    from test_b4artists_ml_temporal_cooperative import CooperativeTemporalTests
    import temporal_cooperative_v1 as c
    import temporal_projection as ref
    CooperativeTemporalTests.setUpClass();helper=CooperativeTemporalTests();obj,_=helper.fixture('rigify_default')
    before=helper.visible(obj);inventory=helper.inventory();steps=c.generate_steps(obj,ref.procedural,context=True)
    profiler=cProfile.Profile();rows=[];last='start';last_frame=None
    try:
        while True:
            started=time.perf_counter();profiler.enable()
            try:progress=next(steps)
            except StopIteration as done:result=done.value;break
            finally:profiler.disable()
            rows.append(dict(from_phase=last,to_phase=progress['phase'],frame=progress['frame'],ms=(time.perf_counter()-started)*1000));last=progress['phase'];last_frame=progress['frame']
            assert helper.visible(obj)==before
    finally:steps.close();c.unregister()
    assert helper.visible(obj)==before and helper.inventory()==inventory
    stats=pstats.Stats(profiler);functions=[]
    for (file,line,name),(primitive,total,self_seconds,cumulative,callers) in stats.stats.items():
        functions.append(dict(file=file,line=line,name=name,primitive_calls=primitive,total_calls=total,self_seconds=self_seconds,cumulative_seconds=cumulative))
    functions.sort(key=lambda x:-x['cumulative_seconds'])
    proof=dict(complete=True,source_preserved=True,scope='Instrumented default-Rigify context-enabled short interval; diagnostic profiling overhead and concurrent training, not benchmark acceptance.',rows=rows,functions=functions,source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in [HERE,ROOT/'training/b4artists_ml/temporal_cooperative_v1.py',ROOT/'tests/test_b4artists_ml_temporal_cooperative.py']},frames=len(result[0]),runtime_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (ROOT/'b4artists_ml').glob('*.py')},full_goal_complete=False)
    OUT.write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(dict(complete=True,steps=len(rows),slowest=sorted(rows,key=lambda x:-x['ms'])[:5],functions=functions[:12])),flush=True)
if __name__=='__main__':
    if '--host' in sys.argv:host()
    else:
        assert not OUT.exists();log=ROOT/f'training/b4artists_ml/cache/{TAG}.log';started=time.perf_counter()
        with log.open('w') as stream:
            p=subprocess.run(['X:/5.1.0/bforartists.exe','--background','--factory-startup','--disable-autoexec','--python',str(HERE),'--','--host'],stdout=stream,stderr=subprocess.STDOUT,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='4'),timeout=900)
        result=dict(exit_code=p.returncode,seconds=time.perf_counter()-started,log=log.relative_to(ROOT).as_posix());(OUT.parent/(TAG+'-process.json')).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
