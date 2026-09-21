"""Reopen completed native authored-context scenes and check editable recovery."""
from pathlib import Path
import sys,os,json,time,hashlib,subprocess,traceback
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve();BASE=ROOT/'training/b4artists_ml/results/authored-review-reload-v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def host(profile):
    import bpy,numpy as np
    sys.path[:0]=[str(ROOT),str(ROOT/'training/b4artists_ml')]
    import b4artists_ml
    from b4artists_ml import workflow as w,posing as p,contacts as c,body_solver as bs,rig_state as rs
    b4artists_ml.register();source=ROOT/'training/b4artists_ml/results/humanoid-workflow-review-v5-slerp'/profile;report=json.loads((source/'report.json').read_text());scene_path=ROOT/report['blend_path'];assert report['full_humanoid_workflow_passed'] and sha(scene_path)==report['blend_sha256'];result=dict(profile=profile,complete=False,scene_sha256=sha(scene_path),visual_rating='unrated')
    def signature(action,slot):
        return [(f.data_path,f.array_index,f.lock,f.mute,[(tuple(k.co),tuple(k.handle_left),tuple(k.handle_right),k.interpolation) for k in f.keyframe_points]) for f in w.action_curves(action,slot)]
    try:
        for keep in (False,True):
            bpy.ops.wm.open_mainfile(filepath=str(scene_path),load_ui=False,use_scripts=False);scene=bpy.context.scene;ob=next(o for o in scene.objects if o.type=='ARMATURE' and o.b4ml.candidate_action);state=ob.b4ml;candidate=state.candidate_action;original=state.source_action;assert ob.animation_data.action==candidate and original
            slot=next(s for s in original.slots if s.identifier==state.source_slot);expected_signature=signature(original,slot);modes=json.loads(state.before_modes or '{}');binding=bs.mapping(ob,writable=False)
            if not keep:
                samples=[]
                for frame in report['frames']:
                    scene.frame_set(frame);p._update(ob);ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());samples.append([list(ev.matrix_world@ev.pose.bones[n].head) for n in binding['names']])
                error=float(np.max(np.abs(np.asarray(samples)-np.asarray(report['corrected_points']))));assert error<2e-5
                max_position=0.;max_rotation=0.
                for frame in np.linspace(1.,21.,321):
                    c._frame(scene,float(frame));p._update(ob);mapping={r['id']:r for r in p.bindings(ob)[2]}
                    for request in c.rows(ob):
                        row=mapping[request['limb']];reference=sum((ob.pose.bones[row['joints'][i+1]].head-ob.pose.bones[row['joints'][i]].head).length for i in (0,1))*w.display_world(ob).to_scale().x
                        max_position=max(max_position,(c._point(ob,row,request['offset'])-c.Vector(request['point'])).length/reference)
                        max_rotation=max(max_rotation,c._angle((w.display_world(ob)@ob.pose.bones[row['joints'][2]].matrix).to_quaternion(),c.Quaternion(request['rotation'])))
                assert max_position<=2e-4 and max_rotation<=.001
                result.update(saved_sample_max_component_error=error,contact_checks=642,max_contact_drift=max_position,max_contact_rotation=max_rotation)
            w.finish_preview(ob,scene,keep)
            if keep:
                assert ob.animation_data.action==candidate;assert state.kept_source==original;w.restore_kept_source(ob,scene)
            assert ob.animation_data.action==original and signature(original,slot)==expected_signature and rs.mode_values(ob)==modes and not state.candidate_action
            result['keep_restore_passed' if keep else 'discard_passed']=True
        assert sha(scene_path)==report['blend_sha256'];result.update(complete=True,source_scene_unchanged=True,runtime_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (ROOT/'b4artists_ml').glob('*.py')})
    except BaseException:result['error']=traceback.format_exc()
    (BASE/(profile+'.json')).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
def main():
    for profile in ('boneforge','rigify_basic','rigify_default'):
        d=json.loads((ROOT/'training/b4artists_ml/results/humanoid-workflow-review-v5-slerp'/profile/'report.json').read_text());assert d['full_humanoid_workflow_passed']
    BASE.mkdir(exist_ok=False);rows=[]
    for profile in ('boneforge','rigify_basic','rigify_default'):
        log=BASE/(profile+'.log');at=time.perf_counter()
        with log.open('w') as stream:child=subprocess.run(['X:/5.1.0/bforartists.exe','--background','--factory-startup','--disable-autoexec','--python',str(HERE),'--',profile],stdout=stream,stderr=subprocess.STDOUT,timeout=500,env=dict(os.environ,OPENBLAS_NUM_THREADS='4',PYTHONDONTWRITEBYTECODE='1'))
        d=json.loads((BASE/(profile+'.json')).read_text());row=dict(profile=profile,complete=d['complete'],host_exit=child.returncode,seconds=time.perf_counter()-at,log_sha256=sha(log));rows.append(row);(BASE/'processes.json').write_text(json.dumps(rows,indent=2)+'\n');print(row,flush=True)
        if not d['complete']:break
if __name__=='__main__':
    if '--' in sys.argv:host(sys.argv[sys.argv.index('--')+1])
    else:main()
