"""Verify full cleanup after the observed long native-flight numerical rejection."""
from pathlib import Path
import sys,os,json,time,subprocess,hashlib
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve();TAG='native-long-recovery-sampling-v1'
def host(label):
    import bpy
    sys.path[:0]=[str(ROOT),str(ROOT/'tests')]
    from test_b4artists_ml_flight import FlightTests,fixture,f,w,c,p,rs
    from b4artists_ml import motion_layer as m
    FlightTests.setUpClass();ob,source,sig,modes=fixture(label);scene=bpy.context.scene
    w.finish_preview(ob,scene,False);max(ob.b4ml.anchors,key=lambda a:a.frame).frame=241;w.preview(ob,scene);ob.b4ml.flights.clear();scene.frame_set(1);f.add(ob,scene);scene.frame_set(121);p._update(ob);ob.b4ml.flight_backend='NATIVE'
    actions=set(bpy.data.actions.keys());objects=set(bpy.data.objects.keys());collections=set(bpy.data.collections.keys());pose=w.raw_pose(ob);candidate=ob.b4ml.candidate_action;before=c._action_signature(ob);current_modes=rs.mode_values(ob);frame=p._frame(scene);error=None;metrics=None
    try:metrics=f.solve(ob,scene)
    except ValueError as exc:
        error=str(exc);assert 'acceleration error' in error,error
    else:f.restore(ob,scene)
    assert set(bpy.data.actions.keys())==actions
    assert set(bpy.data.objects.keys())==objects and set(bpy.data.collections.keys())==collections
    assert ob.animation_data.action==candidate and c._action_signature(ob)==before and w.raw_pose(ob)==pose and rs.mode_values(ob)==current_modes and p._frame(scene)==frame
    assert m.find(ob) is None and not ob.b4ml.flight_running and ob.b4ml.flight_output is None
    w.finish_preview(ob,scene,False)
    assert ob.animation_data.action==source and c._action_signature(ob)==sig and rs.mode_values(ob)==modes
    record=dict(rig=label,span=240,recovery_passed=True,numerical_generation_passed=metrics is not None,error=error,source_restored=True,action_object_collection_counts_unchanged=True,runtime_sha256={q.relative_to(ROOT).as_posix():hashlib.sha256(q.read_bytes()).hexdigest() for q in (ROOT/'b4artists_ml').glob('*.py')})
    (ROOT/f'training/b4artists_ml/results/{TAG}-{label}.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record),flush=True)
def main():
    rows=[]
    for label in ('boneforge','rigify_default'):
        dest=ROOT/f'training/b4artists_ml/results/{TAG}-{label}.json';assert not dest.exists();t=time.perf_counter()
        with (ROOT/f'training/b4artists_ml/cache/{TAG}-{label}.log').open('w') as stream:
            p=subprocess.run(['X:/5.1.0/bforartists.exe','--background','--factory-startup','--disable-autoexec','--python',str(HERE),'--',label],stdout=stream,stderr=subprocess.STDOUT,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='4'),timeout=400)
        record=json.loads(dest.read_text()) if dest.exists() else dict(rig=label,recovery_passed=False,missing_report=True)
        record.update(host_exit=p.returncode,seconds=time.perf_counter()-t);rows.append(record);print({k:v for k,v in record.items() if k!='runtime_sha256'},flush=True)
        (ROOT/f'training/b4artists_ml/results/{TAG}-process.json').write_text(json.dumps(rows,indent=2)+'\n')
if __name__=='__main__':
    if '--' in sys.argv:host(sys.argv[-1])
    else:main()
