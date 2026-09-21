"""Bounded integrated jump diagnostic; never a learned-quality qualification."""
from pathlib import Path
import os, sys, json, time, hashlib, subprocess, traceback
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve()
BASE=ROOT/'training/b4artists_ml/results/grounded-jump-diagnostic-v1'
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def dump(path,data): path.write_text(json.dumps(data,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def host(profile):
    sys.path[:0]=[str(ROOT),str(ROOT/'tests')]
    import bpy, numpy as np, b4artists_ml
    from b4artists_ml import workflow as w, posing as p, contacts as c, flight as f, support, motion_layer as m, rig_state as rs, temporal_preview as tp
    from test_b4artists_ml_contacts import fixture
    from test_b4artists_ml_flight import com
    out=BASE/profile; out.mkdir(exist_ok=False)
    report=dict(profile=profile,complete=False,learned=False,human_assessment=None,cascadeur_comparison=None,events=[])
    started=time.perf_counter()
    def event(stage,**values):
        report['events'].append(dict(stage=stage,**values));dump(out/'progress.json',report)
    try:
        b4artists_ml.register();ob,source,signature,modes=fixture(profile);scene=bpy.context.scene
        w.finish_preview(ob,scene,False)
        stand,crouch=[a.payload for a in ob.b4ml.anchors]
        ob.b4ml.anchors.clear();ob.b4ml.contacts.clear()
        for frame,payload in [(1,stand),(9,crouch),(15,stand),(33,stand),(39,crouch),(49,stand)]:
            a=ob.b4ml.anchors.add();a.frame=frame;a.payload=payload
        priorities=[(a.frame,a.payload) for a in ob.b4ml.anchors]
        scene.frame_start=1;scene.frame_end=49;scene.render.fps=30;scene.frame_set(1)
        source.use_fake_user=True
        ob.b4ml.interpolation_method='AUTHORED';ob.b4ml.temporal_smoothing=True
        at=time.perf_counter();ticks=[];tp.start(ob,scene)
        while ob.b4ml.temporal_running:
            tick=time.perf_counter();tp.step(ob);ticks.append(time.perf_counter()-tick)
            assert time.perf_counter()-started<900 and time.time()<1789053845
        event('authored_generation',seconds=time.perf_counter()-at,max_tick_seconds=max(ticks),p95_tick_seconds=float(np.percentile(ticks,95)))
        limbs={r['id']:r for r in p.bindings(ob)[2]}
        feet=['leg-L','leg-R']
        def feet_at(frame):
            c._frame(scene,float(frame));p._update(ob)
            return np.array([c._point(ob,limbs[limb],[0,0,0]) for limb in feet])
        targets=feet_at(1)
        scale=sum((ob.pose.bones[limbs['leg-L']['joints'][j+1]].head-ob.pose.bones[limbs['leg-L']['joints'][j]].head).length for j in (0,1))*ob.matrix_world.to_scale().x
        ground_frames=np.r_[np.arange(1,15.001,.25),np.arange(33,49.001,.25)]
        def ground_metrics():
            points=np.array([feet_at(frame) for frame in ground_frames])
            delta=points-targets
            return dict(max_normalized_contact_drift=float(np.max(np.linalg.norm(delta,axis=-1))/scale),max_normalized_below_initial_ankle_plane=float(max(0,-delta[:,:,2].min())/scale),points=points.tolist())
        before=ground_metrics();anchor_feet={str(frame):feet_at(frame).tolist() for frame,_ in priorities}
        c._frame(scene,1)
        for start,end in [(1,15),(33,49)]:
            for limb in feet:
                ob.b4ml.contact_limb=limb;item=c.capture(ob,scene);item.start=start;item.end=end;item.blend=0;item.strength=1
        requests=c.rows(ob);support.initialize(ob)
        row=ob.b4ml.flights.add();row.start=15;row.end=33;row.takeoff_blend=row.landing_blend=6;row.strength=1
        ob.b4ml.flight_backend='NATIVE';token=f._curve_token(ob);candidate=ob.b4ml.candidate_action
        try:
            f.solve(ob,scene)
        except ValueError as exc:
            report['grounded_transition_rejection']=str(exc)
        else:
            raise AssertionError('Expected documented grounded-transition incompatibility to remain visible')
        assert m.find(ob) is None and f._curve_token(ob)==token and ob.b4ml.candidate_action==candidate
        event('grounded_request',rejection=report['grounded_transition_rejection'],candidate_preserved=True)
        # A separate ungrounded diagnostic shows what the existing root-only join does.
        ob.b4ml.contacts.clear();at=time.perf_counter();ticks=[];f.start(ob,scene)
        while ob.b4ml.flight_running:
            tick=time.perf_counter();f.step(ob);ticks.append(time.perf_counter()-tick)
            assert time.perf_counter()-started<900 and time.time()<1789053845
        metrics=json.loads(ob.b4ml.flight_metrics);after=ground_metrics()
        anchor_error=max(float(np.max(np.abs(feet_at(frame)-anchor_feet[str(frame)]))) for frame,_ in priorities)
        assert anchor_error/scale<2e-4 and f._curve_token(ob)==token
        event('ungrounded_native_flight',seconds=time.perf_counter()-at,max_tick_seconds=max(ticks),p95_tick_seconds=float(np.percentile(ticks,95)),metrics=metrics)
        # Independent displayed COM samples include the native instance transform.
        def displayed_com(frame):
            point=com(ob,float(frame));instance=m.validate(ob)
            return point+np.array(instance.location)
        h=.125;dt=h/30
        jumps={}
        for frame in (15,33):
            left=(displayed_com(frame)-displayed_com(frame-h))/dt
            right=(displayed_com(frame+h)-displayed_com(frame))/dt
            jumps[str(frame)]=dict(left=left.tolist(),right=right.tolist(),difference=float(np.linalg.norm(right-left)))
        # Persist the failed requested contacts as metadata, not enabled unsupported state.
        notes=bpy.data.texts.new('READ ME - grounded jump diagnostic')
        notes.write('Experimental procedural diagnostic. The requested planted-foot takeoff/landing is rejected by the current solver. This saved animation shows the separate UNGROUNDED native velocity transition, not a successful grounded jump.\nFrames: stand1, crouch9, takeoff15, land33, crouch39, recover49;30fps.\nRequested contacts: '+json.dumps(requests)+'\nNo learned animation, collision/sole certification, human rating or Cascadeur comparison.\n')
        scene.frame_set(12);path=out/(profile+'-ungrounded-jump.blend');bpy.ops.wm.save_as_mainfile(filepath=str(path));assert path.stat().st_size<64*1024*1024
        assert [(a.frame,a.payload) for a in ob.b4ml.anchors]==priorities
        w.finish_preview(ob,scene,True);w.restore_kept_source(ob,scene)
        assert ob.animation_data.action==source and c._action_signature(ob)==signature and rs.mode_values(ob)==modes
        report.update(complete=True,grounded_workflow_passed=False,source_recovered=True,ground_frames=ground_frames.tolist(),foot_names=feet,leg_length_world=scale,before=before,after=after,priority_foot_max_error=anchor_error,com_join_secant_differences=jumps,blend=str(path.relative_to(ROOT)),blend_sha256=sha(path),runtime_sha256={str(p.relative_to(ROOT)):sha(p) for p in (ROOT/'b4artists_ml').glob('*.py')},script_sha256=sha(HERE))
    except BaseException:
        report['error']=traceback.format_exc()
    report['seconds']=time.perf_counter()-started;dump(out/'report.json',report)
    print(json.dumps({k:report.get(k) for k in ('profile','complete','grounded_workflow_passed','grounded_transition_rejection','source_recovered','error')}),flush=True)
def main():
    BASE.mkdir(exist_ok=False);rows=[]
    for profile in ('boneforge','rigify_basic','rigify_default'):
        log=BASE/(profile+'.log');start=time.perf_counter()
        with log.open('w',encoding='utf-8') as stream:
            run=subprocess.run(['X:/5.1.0/bforartists.exe','--background','--factory-startup','--disable-autoexec','--python',str(HERE),'--',profile],stdout=stream,stderr=subprocess.STDOUT,timeout=1000,env=dict(os.environ,OPENBLAS_NUM_THREADS='4',PYTHONDONTWRITEBYTECODE='1'))
        path=BASE/profile/'report.json';result=json.loads(path.read_text()) if path.exists() else {}
        row=dict(profile=profile,exit_code=run.returncode,complete=result.get('complete',False),error=result.get('error'),seconds=time.perf_counter()-start,log_sha256=sha(log));rows.append(row);dump(BASE/'processes.json',rows);print(json.dumps(row),flush=True)
        if not row['complete']:break
if __name__=='__main__':
    if '--' in sys.argv:host(sys.argv[sys.argv.index('--')+1])
    else:main()
