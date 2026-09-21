"""Fresh-process reload and recovery checks for broader cubic-contact references."""
from pathlib import Path
import sys,os,json,time,hashlib,subprocess,traceback
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve();BASE=ROOT/'training/b4artists_ml/results/broader-shape-reload-v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
def host(profile):
    import bpy,numpy as np
    sys.path[:0]=[str(ROOT)];import b4artists_ml
    from b4artists_ml import workflow as w,posing as p,contacts as c,rig_state as rs
    b4artists_ml.register();d=json.loads((ROOT/'training/b4artists_ml/results/broader-shape-workflow-v2'/profile/'report.json').read_text());assert d['complete'];result=dict(profile=profile,complete=False,cases=[])
    def signature(action,slot):return [(fc.data_path,fc.array_index,[(tuple(k.co),tuple(k.handle_left),tuple(k.handle_right),k.interpolation,k.handle_left_type,k.handle_right_type) for k in fc.keyframe_points]) for fc in w.action_curves(action,slot)]
    try:
        for case in d['cases']:
            r=next(v for v in case['variants'] if v['variant']=='smooth_both');assert r['complete'] and r['contact_gate_passed'] and r['priority_gate_passed'];path=ROOT/r['scene'];assert sha(path)==r['scene_sha256'];entry=dict(case=case['case'],scene=r['scene'],scene_sha256=sha(path))
            for keep in (False,True):
                bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False);scene=bpy.context.scene;ob=next(o for o in scene.objects if o.type=='ARMATURE' and o.b4ml.candidate_action);state=ob.b4ml;candidate=state.candidate_action;source=state.source_action;slot=next(s for s in source.slots if s.identifier==state.source_slot);before=signature(source,slot);modes=json.loads(state.before_modes or '{}');anchors=[(a.frame,a.payload) for a in state.anchors]
                def matrices(frame):
                    c._frame(scene,float(frame));p._update(ob);return np.array([np.array(w.display_world(ob)@ob.pose.bones[n].matrix) for n in w.read_anchors(ob)[0][1]['pose']])
                if not keep:
                    actual_priorities={f:matrices(f) for f,_ in w.read_anchors(ob)};max_p=0.;max_r=0.;checks=0;mapping={r['id']:r for r in p.bindings(ob)[2]}
                    for frame in np.linspace(1.,21.,1281):
                        c._frame(scene,float(frame));p._update(ob)
                        for request in c.rows(ob):
                            if not request['start']<=frame<=request['end']:continue
                            limb=mapping[request['limb']];length=sum((ob.pose.bones[limb['joints'][i+1]].head-ob.pose.bones[limb['joints'][i]].head).length for i in (0,1))*w.display_world(ob).to_scale().x
                            max_p=max(max_p,(c._point(ob,limb,request['offset'])-c.Vector(request['point'])).length/length);max_r=max(max_r,c._angle((w.display_world(ob)@ob.pose.bones[limb['joints'][2]].matrix).to_quaternion(),c.Quaternion(request['rotation'])));checks+=1
                    assert max_p<=2e-4 and max_r<=.001;entry.update(max_contact_drift=max_p,max_contact_rotation=max_r,contact_checks=checks,exact_saved_contact_metrics=max_p==r['max_contact_drift'] and max_r==r['max_contact_rotation']);assert entry['exact_saved_contact_metrics']
                w.finish_preview(ob,scene,keep)
                if keep:
                    assert ob.animation_data.action==candidate and state.kept_source==source;w.restore_kept_source(ob,scene)
                assert ob.animation_data.action==source and signature(source,slot)==before and rs.mode_values(ob)==modes and [(a.frame,a.payload) for a in state.anchors]==anchors
                if not keep:
                    w.preview(ob,scene);error=max(float(np.max(np.abs(matrices(f)-actual))) for f,actual in actual_priorities.items());assert error<=2e-4;entry['fresh_authored_priority_matrix_error']=error;w.finish_preview(ob,scene,False);assert ob.animation_data.action==source and signature(source,slot)==before
                entry['keep_restore_passed' if keep else 'discard_passed']=True
            assert sha(path)==entry['scene_sha256'];entry.update(complete=True,source_scene_unchanged=True);result['cases'].append(entry)
        result['complete']=True
    except BaseException:result['error']=traceback.format_exc()
    result.update(script_sha256=sha(HERE),runtime_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (ROOT/'b4artists_ml').glob('*.py')},independent_animator_rating='unrated');write(BASE/(profile+'.json'),result);print(json.dumps(result),flush=True)
def main():
    for profile in ('boneforge','rigify_basic','rigify_default'):
        d=json.loads((ROOT/'training/b4artists_ml/results/broader-shape-workflow-v2'/profile/'report.json').read_text());assert d['complete'] and all(next(v for v in c['variants'] if v['variant']=='smooth_both')['contact_gate_passed'] for c in d['cases'])
    BASE.mkdir(exist_ok=False);rows=[]
    for profile in ('boneforge','rigify_basic','rigify_default'):
        log=BASE/(profile+'.log');start=time.perf_counter()
        with log.open('w') as stream:child=subprocess.run(['X:/5.1.0/bforartists.exe','--background','--factory-startup','--disable-autoexec','--python',str(HERE),'--',profile],stdout=stream,stderr=subprocess.STDOUT,timeout=750,env=dict(os.environ,OPENBLAS_NUM_THREADS='4',PYTHONDONTWRITEBYTECODE='1'))
        d=json.loads((BASE/(profile+'.json')).read_text());rows.append(dict(profile=profile,complete=d['complete'],host_exit=child.returncode,seconds=time.perf_counter()-start,log_sha256=sha(log)));write(BASE/'processes.json',rows);print(rows[-1],flush=True)
        if not d['complete']:break
if __name__=='__main__':
    if '--' in sys.argv:host(sys.argv[sys.argv.index('--')+1])
    else:main()
