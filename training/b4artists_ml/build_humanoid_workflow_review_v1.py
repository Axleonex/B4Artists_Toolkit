"""Create actual-rig, editable crouch/recover review scenes through existing APIs.
This is a procedural workflow baseline, not an accepted learned model or UX rating.
"""
from pathlib import Path
import os,sys,json,time,subprocess,hashlib,traceback
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve();BASE=ROOT/'training/b4artists_ml/results/humanoid-workflow-review-v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def host(profile):
    import bpy,numpy as np
    sys.path[:0]=[str(ROOT),str(ROOT/'tests'),str(ROOT/'training/b4artists_ml')]
    import b4artists_ml
    from b4artists_ml import workflow as w,posing as p,contacts as c,body_solver as bs,rig_state as rs
    from test_b4artists_ml_contacts import fixture
    import temporal_cooperative_v1 as cooperative
    import semantic_predictor
    out=BASE/profile;out.mkdir(exist_ok=False);started=time.perf_counter();report=dict(profile=profile,complete=False,learned=False,full_goal_complete=False,independent_animator_assessment='unrated',events=[])
    def emit(**event):report['events'].append(event);(out/'progress.json').write_text(json.dumps(report,indent=2)+'\n')
    try:
        b4artists_ml.register();cooperative.register();ob,source,signature,modes=fixture(profile);scene=bpy.context.scene
        # Existing fixture authors a planted-foot crouch from1to11. Add its original
        # standing pose at21, preserving captured control modes/payload verbatim.
        w.finish_preview(ob,scene,False);assert ob.animation_data.action==source and c._action_signature(ob)==signature
        first=ob.b4ml.anchors[0];third=ob.b4ml.anchors.add();third.frame=21.;third.payload=first.payload
        for item in ob.b4ml.contacts:item.end=21.
        scene.frame_start=1;scene.frame_end=21;scene.render.fps=30;scene.frame_set(1);p._update(ob);binding=bs.mapping(ob,writable=False)
        original_payloads=[(a.frame,a.payload) for a in ob.b4ml.anchors];source.use_fake_user=True;source.name=profile+' original source'
        def points():
            p._update(ob);ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());return np.asarray([ev.matrix_world@ev.pose.bones[n].head for n in binding['names']])
        def sample():
            saved=(scene.frame_current,scene.frame_subframe);rows=[]
            for f in range(1,22):scene.frame_set(f);rows.append(points().tolist())
            scene.frame_set(saved[0],subframe=saved[1]);return rows
        at=time.perf_counter();w.preview(ob,scene);raw=ob.b4ml.candidate_action;raw.name=profile+' 01 authored interpolation';raw.use_fake_user=True;raw_points=sample();emit(stage='authored_interpolation',seconds=time.perf_counter()-at)
        w.finish_preview(ob,scene,False);assert ob.animation_data.action==source and c._action_signature(ob)==signature
        provider=semantic_predictor.provider(dict(kind='baseline',baseline='hermite'));ticks=[];at=time.perf_counter();job=cooperative.generate_steps(ob,provider,context=True);context_error=None;context_points=None;metrics=[]
        try:
            while True:
                tick=time.perf_counter()
                try:next(job)
                except StopIteration as done:samples,metrics=done.value;ticks.append(time.perf_counter()-tick);break
                ticks.append(time.perf_counter()-tick)
                assert time.perf_counter()-started<900 and time.time()<1788981845.
            assert ob.animation_data.action==source and c._action_signature(ob)==signature
            w.preview(ob,scene,pose_samples=samples);context_action=ob.b4ml.candidate_action;context_action.name=profile+' 02 contextual procedural';context_action.use_fake_user=True;context_points=sample()
        except (ValueError,RuntimeError,InterruptedError) as exc:
            context_error=str(exc);assert not ob.b4ml.candidate_action and ob.animation_data.action==source and c._action_signature(ob)==signature
        finally:job.close()
        emit(stage='contextual_procedural',seconds=time.perf_counter()-at,error=context_error,max_tick_seconds=max(ticks,default=0),ticks=len(ticks))
        # Preserve any context rejection and use the existing product baseline only
        # as an explicitly labelled independent contact-workflow comparison.
        if context_error:w.preview(ob,scene);contact_input='authored_interpolation'
        else:contact_input='contextual_procedural'
        at=time.perf_counter();contact_report=c.solve(ob,scene);corrected=ob.b4ml.candidate_action;corrected.name=profile+' 03 explicit foot contacts';corrected.use_fake_user=True;corrected_points=sample();assert contact_report['max_after']<2e-4
        emit(stage='explicit_contacts',seconds=time.perf_counter()-at,input=contact_input,max_before=contact_report['max_before'],max_after=contact_report['max_after'])
        assert [(a.frame,a.payload) for a in ob.b4ml.anchors]==original_payloads
        readme=bpy.data.texts.new('READ ME - humanoid workflow review')
        readme.write('Procedural crouch/recover workflow review; no learned quality or Cascadeur parity claim.\nFrames1/11/21are authored priorities. Scrub1to21on the active corrected candidate; foot contacts are explicit.\nActions preserve authored interpolation, any successful contextual procedural result, corrected output and original source.\nWith experimentalB4ArtistsML0.17.5enabled, Keep/Discard and Restore Source Animation remain available. Saved animation is editable without the addon.\nContext error: '+str(context_error)+'\nPlease assess foot sliding, knee motion, pose timing, correction effort and UI responsiveness. This script is not an animator rating.\n')
        scene.frame_set(11);bpy.context.view_layer.objects.active=ob;ob.select_set(True);ob.show_in_front=True
        for area in bpy.context.screen.areas:
            if area.type=='VIEW_3D':area.spaces.active.overlay.show_floor=True;area.spaces.active.region_3d.view_distance=4.;area.spaces.active.region_3d.view_location=ob.matrix_world.translation
        path=out/(profile+'-crouch-recover.blend');bpy.ops.wm.save_as_mainfile(filepath=str(path));assert path.stat().st_size<64*1024*1024
        w.finish_preview(ob,scene,True);w.restore_kept_source(ob,scene);assert ob.animation_data.action==source and c._action_signature(ob)==signature and rs.mode_values(ob)==modes
        report.update(complete=True,contextual_workflow_passed=context_error is None,context_error=context_error,contact_input=contact_input,contact_report=contact_report,source_restored=True,priorities_preserved=True,keep_restore_passed=True,active_candidate_saved=True,blend_path=path.relative_to(ROOT).as_posix(),blend_sha256=sha(path),frames=list(range(1,22)),joint_names=binding['names'],authored_interpolation_points=raw_points,contextual_points=context_points,corrected_points=corrected_points,projection_metrics=metrics,context_max_tick_seconds=max(ticks,default=0),context_p95_tick_seconds=float(np.percentile(ticks,95)) if ticks else None,seconds=time.perf_counter()-started,runtime_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (ROOT/'b4artists_ml').glob('*.py')},script_sha256=sha(HERE),limitations=['One controlled crouch/recover fixture per rig; not broad animation coverage.','Context uses original-source neighboring frames; empty/source-static context can disagree with authored motion.','No trained temporal weights, GUI-input automation or independent animator rating.','Saved artifact is an actual rig and editable candidate, not a rendered visual assessment.'])
    except BaseException:report.update(error=traceback.format_exc(),seconds=time.perf_counter()-started)
    (out/'report.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n');print(json.dumps({k:report.get(k) for k in ['profile','complete','contextual_workflow_passed','context_error','source_restored','error']}),flush=True)

def main():
    BASE.mkdir(exist_ok=False);processes=[]
    for profile in ['boneforge','rigify_basic','rigify_default']:
        log=BASE/(profile+'.log');at=time.perf_counter()
        with log.open('w') as stream:result=subprocess.run(['X:/5.1.0/bforartists.exe','--background','--factory-startup','--disable-autoexec','--python',str(HERE),'--',profile],stdout=stream,stderr=subprocess.STDOUT,timeout=1000,env=dict(os.environ,OPENBLAS_NUM_THREADS='4',PYTHONDONTWRITEBYTECODE='1'))
        path=BASE/profile/'report.json';d=json.loads(path.read_text()) if path.exists() else dict(complete=False,error='Missing report');row=dict(profile=profile,exit_code=result.returncode,seconds=time.perf_counter()-at,complete=d.get('complete',False),contextual_workflow_passed=d.get('contextual_workflow_passed'),error=d.get('error'),log_sha256=sha(log));processes.append(row);(BASE/'processes.json').write_text(json.dumps(processes,indent=2)+'\n');print(json.dumps(row),flush=True)
        if not row['complete']:break
if __name__=='__main__':
    if '--' in sys.argv:host(sys.argv[sys.argv.index('--')+1])
    else:main()
