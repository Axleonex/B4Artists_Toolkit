"""Isolate the ready tick of a warmed live solve; profiling is not a latency gate."""
from pathlib import Path
import sys,os,json,time,hashlib,subprocess
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve();TAG='current-tick-profile-v25';OUT=ROOT/f'training/b4artists_ml/results/{TAG}.json'

def host():
    import bpy,numpy as np,cProfile,pstats,io
    sys.path[:0]=[str(ROOT),str(ROOT/'tests')]
    from test_b4artists_ml_body_live import LivePoseTests
    from b4artists_ml import body_live as live,body_preview as body,workflow as w,rig_state as rs
    meta=json.loads((ROOT/'docs/b4artists_ml/package-test-v0.17.4.json').read_text());current={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'b4artists_ml').glob('*.py')};assert current==meta['runtime_sha256']
    LivePoseTests.setUpClass();helper=LivePoseTests();records=[]
    for label in ['boneforge','rigify_default']:
        ob,source,modes,action,keys=helper.fixture(label);body.solve(ob);live.start(ob,now=0.)
        ob.b4ml.body_targets['Head'].target.location.y+=.002;bpy.context.view_layer.update()
        clock=0.;samples=[];hot=[];profile=cProfile.Profile();start=time.perf_counter()
        for tick in range(3000):
            clock+=.02;profile.clear();profile.enable();begin=time.perf_counter();status=live.tick(ob,now=clock);elapsed=(time.perf_counter()-begin)*1000;profile.disable();samples.append(dict(tick=tick,status=status,ms=elapsed))
            if len(hot)<5 or elapsed>hot[-1]['ms']:
                data=pstats.Stats(profile);calls=[]
                for (file,line,name),(primitive,total,self_time,cumulative,callers) in data.stats.items():
                    calls.append(dict(file=file,line=line,name=name,calls=total,self_ms=self_time*1000,cumulative_ms=cumulative*1000))
                job=body._JOBS.get(ob.as_pointer());iterator=job['iterator'].gi_yieldfrom if job else None;frame=iterator.gi_frame if iterator else None
                hot.append(dict(tick=tick,status=status,ms=elapsed,solver_yield_line=frame.f_lineno if frame else None,preparation_stage=frame.f_locals.get('stage') if frame else None,calls=sorted(calls,key=lambda x:x['cumulative_ms'],reverse=True)[:25]))
                hot=sorted(hot,key=lambda x:x['ms'],reverse=True)[:5]
            if status=='ready':break
        else:raise AssertionError('Active solve did not settle')
        profile.disable();seconds=time.perf_counter()-start;stream=io.StringIO();stats=pstats.Stats(profile,stream=stream).sort_stats('cumulative');stats.print_stats(40)
        calls=[]
        for (file,line,name),(primitive,total,self_time,cumulative,callers) in stats.stats.items():
            calls.append(dict(file=file,line=line,name=name,primitive_calls=primitive,total_calls=total,self_seconds=self_time,cumulative_seconds=cumulative))
        metrics=body._read(ob)['metrics'];assert metrics['pin_error']<2e-4 and metrics['length_error']<.002 and metrics['orientation_error_radians']<.001
        body.finish(ob,bpy.context.scene,False);assert w.raw_pose(ob)==source and rs.mode_values(ob)==modes and ob.animation_data.action==action and helper.keys(ob)==keys;assert not body._JOBS and not live._WATCHERS
        records.append(dict(rig=label,hot_ticks=hot,seconds_under_profiler=seconds,ticks=samples,p95_ms_under_profiler=float(np.percentile([x['ms'] for x in samples],95)),max_ms_under_profiler=max(x['ms'] for x in samples),metrics=metrics,source_preserved=True,top_cumulative=sorted(calls,key=lambda x:x['cumulative_seconds'],reverse=True)[:50],profile_text=stream.getvalue()))
        result=dict(passed=True,complete=len(records)==2,records=records,runtime_sha256={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'b4artists_ml').glob('*.py')},scope='One warmed changed-target solve per fixture, with cProfile reset for each tick; the main function report describes the final ready tick; hot_ticks records the five slowest profiled ticks and their yielded solver stage. Tick timings include profiling overhead. This identifies finalization cost centers, not an independent latency or human-usability acceptance test.')
        OUT.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(rig=label,seconds=seconds,p95_ms=records[-1]['p95_ms_under_profiler'],max_ms=records[-1]['max_ms_under_profiler'])),flush=True)
if __name__=='__main__':
    if '--host' in sys.argv:host()
    else:
        if OUT.exists():raise RuntimeError('Evidence already exists')
        start=time.perf_counter();log=ROOT/f'training/b4artists_ml/cache/{TAG}.log'
        with log.open('w') as stream:
            done=subprocess.run(['X:/5.1.0/bforartists.exe','--background','--factory-startup','--disable-autoexec','--python',str(HERE),'--','--host'],stdout=stream,stderr=subprocess.STDOUT,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='4',B4ML_RUN_LABEL=TAG),timeout=180)
        receipt=dict(exit_code=done.returncode,seconds=time.perf_counter()-start,log=log.relative_to(ROOT).as_posix());(OUT.parent/(TAG+'-process.json')).write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
