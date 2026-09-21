"""Reproducible flight workflow measurements. Run with Python; launches host cases.
SPDX-License-Identifier: GPL-2.0-or-later
"""
from pathlib import Path
import os,sys,json,time,hashlib,subprocess,traceback,platform,ctypes
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve()
RESULTS=ROOT/'training/b4artists_ml/results'
CACHE=ROOT/'training/b4artists_ml/cache'
PROTOCOL=ROOT/'docs/b4artists_ml/PERFORMANCE-FLIGHT-PROTOCOL-v1.md'

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def memory():
    if os.name!='nt':return None
    from ctypes import wintypes
    class Counters(ctypes.Structure):
        _fields_=[('cb',wintypes.DWORD),('PageFaultCount',wintypes.DWORD)]+[(k,ctypes.c_size_t) for k in ('PeakWorkingSetSize','WorkingSetSize','QuotaPeakPagedPoolUsage','QuotaPagedPoolUsage','QuotaPeakNonPagedPoolUsage','QuotaNonPagedPoolUsage','PagefileUsage','PeakPagefileUsage','PrivateUsage')]
    process=ctypes.WinDLL('kernel32',use_last_error=True).GetCurrentProcess;process.restype=wintypes.HANDLE
    get=ctypes.WinDLL('psapi',use_last_error=True).GetProcessMemoryInfo;get.argtypes=(wintypes.HANDLE,ctypes.POINTER(Counters),wintypes.DWORD);get.restype=wintypes.BOOL
    out=Counters();out.cb=ctypes.sizeof(out)
    if not get(process(),ctypes.byref(out),out.cb):raise ctypes.WinError(ctypes.get_last_error())
    return dict(working_set_bytes=out.WorkingSetSize,private_commit_bytes=out.PrivateUsage,process_peak_working_set_bytes=out.PeakWorkingSetSize)

def host_case():
    script_ready=time.time()
    sys.path[:0]=[str(ROOT),str(ROOT/'tests')]
    import numpy as np
    import bpy
    import test_b4artists_ml_flight as t
    f,w,c,p,rs=t.f,t.w,t.c,t.p,t.rs
    label=os.environ['B4ML_PERF_RIG'];span=int(os.environ['B4ML_PERF_SPAN']);tag=os.environ['B4ML_PERF_TAG']
    dest=RESULTS/f'{tag}-{label}-{span}.json'
    report=dict(schema=1,rig=label,span_frames=span,script_ready_epoch=script_ready,host=bpy.app.version_string,build_hash=bpy.app.build_hash.decode(),python=platform.python_version(),numpy=np.__version__,platform=platform.platform(),processor=platform.processor(),logical_cpus=os.cpu_count(),script_sha256=sha(HERE),protocol_sha256=sha(PROTOCOL),runs=[],passed=False)
    def persist():dest.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    def actions():return [dict(name=a.name,users=a.users,fake_user=a.use_fake_user) for a in bpy.data.actions if 'b4ml_flight' in a]
    try:
        t.FlightTests.setUpClass();started=time.perf_counter();ob,source,sig,modes=t.fixture(label);scene=bpy.context.scene
        if span!=10:
            w.finish_preview(ob,scene,False)
            max(ob.b4ml.anchors,key=lambda a:a.frame).frame=1+span
            w.preview(ob,scene);ob.b4ml.flights.clear();scene.frame_set(1);f.add(ob,scene)
        scene.frame_set(1+span//2);p._update(ob)
        report['fixture_seconds']=time.perf_counter()-started
        prepared=memory();report['prepared_memory']=prepared
        original=ob.b4ml.candidate_action;sampled=[prepared,memory()];persist()
        for index in range(3):
            steps=[];started=time.perf_counter();f.start(ob,scene)
            while True:
                tick=time.perf_counter();done=f.step(ob);steps.append((time.perf_counter()-tick)*1000)
                if len(steps)%20==0:sampled.append(memory())
                if done:break
            elapsed=time.perf_counter()-started;sampled.append(memory());metrics=json.loads(ob.b4ml.flight_metrics)
            assert metrics['max_after']<2e-4 and ob.b4ml.flight_input==original
            report['runs'].append(dict(index=index,kind='first_flight_after_fixture' if index==0 else 'warm',elapsed_seconds=elapsed,step_p95_ms=float(np.percentile(steps,95)),step_max_ms=max(steps),step_count=len(steps),steps_ms=steps,memory=memory(),flight_actions=actions(),max_com_error=metrics['max_after'],sample_divisions=metrics['sample_divisions']))
            persist();print('PERF_RUN '+json.dumps({k:v for k,v in report['runs'][-1].items() if k not in ('steps_ms','flight_actions')}),flush=True)
        original=ob.b4ml.candidate_action;pose=w.raw_pose(ob);signature=c._action_signature(ob);all_actions=set(bpy.data.actions.keys());frame=p._frame(scene)
        steps=[];f.start(ob,scene)
        while True:
            tick=time.perf_counter();done=f.step(ob);steps.append((time.perf_counter()-tick)*1000)
            if done:raise AssertionError('Cancellation probe completed before fitting phase')
            if set(bpy.data.actions.keys())!=all_actions:break
        tick=time.perf_counter();f.abort(ob);abort_ms=(time.perf_counter()-tick)*1000
        assert not ob.b4ml.flight_running and ob.animation_data.action==original
        assert w.raw_pose(ob)==pose and c._action_signature(ob)==signature and p._frame(scene)==frame
        assert set(bpy.data.actions.keys())==all_actions
        report['cancellation']=dict(abort_ms=abort_ms,preceding_step_max_ms=max(steps),cooperative_estimate_ms=max(steps)+abort_ms,recovery=True)
        unused=[a for a in actions() if a['users']==0]
        report['unused_superseded_flight_actions']=unused
        w.finish_preview(ob,scene,False)
        assert ob.animation_data.action==source and c._action_signature(ob)==sig and rs.mode_values(ob)==modes
        report['source_recovery']=True;report['after_discard_flight_actions']=actions()
        growth=max(m['working_set_bytes'] for m in sampled)-prepared['working_set_bytes'] if prepared else None
        report['sampled_working_set_growth_bytes']=growth
        budget={10:10,60:45,240:180}[span]
        report['budgets']=dict(solve=all(r['elapsed_seconds']<=budget for r in report['runs']),step_p95=all(r['step_p95_ms']<=100 for r in report['runs']),step_max=all(r['step_max_ms']<=250 for r in report['runs']),abort=abort_ms<=100,memory=growth is not None and growth<=256*1024**2,unused_actions=len(unused)==0)
        report['passed']=all(report['budgets'].values());report['measurement_completed']=True
    except BaseException as exc:
        report.update(error=str(exc),traceback=traceback.format_exc(),measurement_completed=False)
    finally:
        persist();print('PERF_CASE '+json.dumps({k:v for k,v in report.items() if k!='runs'}),flush=True)

def main():
    tag='flight-performance-v1';cases=[]
    for label in ('boneforge','rigify_default'):
        for span in (10,60,240):
            name=f'{tag}-{label}-{span}';dest=RESULTS/f'{name}.json'
            if dest.exists():raise RuntimeError(f'Refusing to overwrite existing evidence: {dest}')
            env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='4',B4ML_PERF_RIG=label,B4ML_PERF_SPAN=str(span),B4ML_PERF_TAG=tag)
            launched=time.time();started=time.perf_counter();timeout=False
            with (CACHE/f'{name}.log').open('w',encoding='utf-8') as log:
                try:result=subprocess.run(['X:/5.1.0/bforartists.exe','--background','--factory-startup','--python',str(HERE),'--','--host-case'],env=env,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,timeout=600);code=result.returncode
                except subprocess.TimeoutExpired:code=None;timeout=True
            data=json.loads(dest.read_text(encoding='utf-8')) if dest.exists() else {}
            case=dict(rig=label,span_frames=span,exit_code=code,timeout=timeout,elapsed_seconds=time.perf_counter()-started,launch_to_script_ready_seconds=data.get('script_ready_epoch',launched)-launched if data else None,artifact=str(dest.relative_to(ROOT)),sha256=sha(dest) if dest.exists() else None,measurement_completed=data.get('measurement_completed',False),budgets=data.get('budgets'))
            cases.append(case);print(json.dumps(case),flush=True)
            (RESULTS/f'{tag}-process.json').write_text(json.dumps(dict(cases=cases,script_sha256=sha(HERE),protocol_sha256=sha(PROTOCOL)),indent=2)+'\n',encoding='utf-8')

if __name__=='__main__':
    if '--host-case' in sys.argv:host_case()
    else:main()
