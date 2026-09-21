"""Compare isolated shape curves and contacts on fixed native humanoid scenes."""
from pathlib import Path
import sys,json,math,hashlib,subprocess,time,os,traceback
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve();BASE=ROOT/'training/b4artists_ml/results/shape-curve-workflow-v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def host(profile):
    import bpy,numpy as np
    sys.path[:0]=[str(ROOT),str(ROOT/'training/b4artists_ml')];import b4artists_ml
    from b4artists_ml import workflow as w,posing as p,body_solver as bs,contacts as c,rig_state as rs
    from shape_curve_v1 import smooth_copy
    b4artists_ml.register();d=json.loads((ROOT/'training/b4artists_ml/results/humanoid-workflow-review-v6-runtime'/profile/'report.json').read_text());path=ROOT/d['blend_path'];assert d['full_humanoid_workflow_passed'] and sha(path)==d['blend_sha256'];out=BASE/profile;out.mkdir();result=dict(profile=profile,complete=False,source_scene_sha256=sha(path),rows=[])
    try:
        bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False);scene=bpy.context.scene;ob=next(o for o in scene.objects if o.type=='ARMATURE' and o.b4ml.candidate_action);binding=bs.mapping(ob,writable=False);state=ob.b4ml;original=state.candidate_action;source=state.source_action;slot=w._slot(ob.animation_data);source_slot=state.source_slot
        def action_signature(action):
            selected=next(s for s in action.slots if s.identifier==slot);return [(fc.data_path,fc.array_index,[(tuple(k.co),tuple(k.handle_left),tuple(k.handle_right),k.interpolation,k.handle_left_type,k.handle_right_type) for k in fc.keyframe_points]) for fc in w.action_curves(action,selected)]
        source_signature=action_signature(source);original_signature=action_signature(original);payloads=[(a.frame,a.payload) for a in state.anchors]
        def sample(frame):
            c._frame(scene,float(frame));p._update(ob);ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());world=ev.matrix_world
            return np.array([world@ev.pose.bones[n].head for n in binding['names']]),[(world@ev.pose.bones[n].matrix).to_quaternion() for n in binding['names']]
        def matrices(frame):
            sample(frame);return np.array([np.array(w.display_world(ob)@ob.pose.bones[n].matrix) for n in w.read_anchors(ob)[0][1]['pose']])
        priorities={frame:matrices(frame) for frame,_ in w.read_anchors(ob)}
        def omega(a,b,dt):
            out=[]
            for qa,qb in zip(a,b):
                q=(qb@qa.conjugated()).normalized()
                if q.w<0:q.negate()
                v=np.array((q.x,q.y,q.z));n=np.linalg.norm(v);out.append(v*(2*math.atan2(n,q.w)/max(n,1e-15)/dt))
            return np.array(out)
        def inspect():
            max_p=0.;max_r=0.;worst_frame=0.;lo=float('inf');hi=-float('inf')
            for frame in np.linspace(1.,21.,1281):
                points,_=sample(frame);lo=min(lo,float(points[0,2]));hi=max(hi,float(points[0,2]));mapping={r['id']:r for r in p.bindings(ob)[2]}
                for request in c.rows(ob):
                    row=mapping[request['limb']];reference=sum((ob.pose.bones[row['joints'][i+1]].head-ob.pose.bones[row['joints'][i]].head).length for i in (0,1))*w.display_world(ob).to_scale().x
                    error=(c._point(ob,row,request['offset'])-c.Vector(request['point'])).length/reference
                    if error>max_p:max_p=error;worst_frame=float(frame)
                    max_r=max(max_r,c._angle((w.display_world(ob)@ob.pose.bones[row['joints'][2]].matrix).to_quaternion(),c.Quaternion(request['rotation'])))
            errors=[float(np.max(np.abs(matrices(frame)-expected))) for frame,expected in priorities.items()];derivatives=[]
            for eps in (.25,.125,.0625,.03125,.015625):
                left,qa=sample(11-eps);at,qb=sample(11);right,qc=sample(11+eps);dt=eps/(scene.render.fps/scene.render.fps_base);angular=np.linalg.norm(omega(qb,qc,dt)-omega(qa,qb,dt),axis=-1);velocity=np.linalg.norm((right-at)/dt-(at-left)/dt,axis=-1)
                derivatives.append(dict(epsilon_frames=eps,max_angular_velocity_jump_rad_s=float(angular.max()),angular_joint=binding['names'][int(angular.argmax())],pelvis_velocity_jump_world_s=float(velocity[0]),max_joint_velocity_jump_world_s=float(velocity.max())))
            return dict(contact_checks=2562,max_contact_drift=max_p,contact_worst_frame=worst_frame,max_contact_rotation=max_r,max_priority_matrix_error=max(errors),pelvis_z_range=hi-lo,derivatives=derivatives,contact_gate_passed=max_p<=2e-4 and max_r<=.001,priority_gate_passed=max(errors)<=2e-4)
        baseline=inspect();result['baseline']=baseline
        for variant in ('smooth_corrected','smooth_then_contacts','smooth_both'):
            record=dict(variant=variant,complete=False);at=time.perf_counter();candidate=None
            try:
                w.assign_action(ob,original,slot);state.candidate_action=original;state.contact_input=None;state.contact_output=None;state.contact_metrics=''
                starting=original if variant=='smooth_corrected' else bpy.data.actions[profile+' 02 authored procedural']
                candidate,shape=smooth_copy(ob,starting,1.,21.);w.assign_action(ob,candidate,slot);state.candidate_action=candidate
                record['shape_before']=shape
                if variant!='smooth_corrected':record['contact_solve']=c.solve(ob,scene);candidate=state.candidate_action
                if variant=='smooth_both':
                    candidate,shape=smooth_copy(ob,candidate,1.,21.);w.assign_action(ob,candidate,slot);state.candidate_action=candidate;record['shape_after']=shape
                record.update(inspect());record['complete']=True
                assert action_signature(source)==source_signature and action_signature(original)==original_signature and [(a.frame,a.payload) for a in state.anchors]==payloads
                if record['contact_gate_passed'] and record['priority_gate_passed']:
                    if 'b4ml_contact_metrics' in candidate:del candidate['b4ml_contact_metrics']
                    state.contact_metrics='';state.contact_input=None;state.contact_output=None;candidate.use_fake_user=True;candidate.name=profile+' '+variant+' research'
                    text=bpy.data.texts.new('READ ME - shape curve research');text.write('Procedural research curve comparison. Authored samples preserved; contacts checked at1281times. No learned-motion or human visual qualification.\n'+json.dumps(record,indent=2))
                    scene.frame_set(11);saved=out/(variant+'.blend');bpy.ops.wm.save_as_mainfile(filepath=str(saved));record['scene']=saved.relative_to(ROOT).as_posix();record['scene_sha256']=sha(saved)
            except (ValueError,RuntimeError) as exc:record['error']=str(exc)
            record['seconds']=time.perf_counter()-at;result['rows'].append(record);(out/'progress.json').write_text(json.dumps(result,indent=2)+'\n')
        w.assign_action(ob,original,slot);state.candidate_action=original;state.contact_input=None;state.contact_output=None;w.finish_preview(ob,scene,False)
        assert ob.animation_data.action==source and action_signature(source)==source_signature and action_signature(original)==original_signature and sha(path)==d['blend_sha256'];result.update(complete=True,source_preserved=True,runtime_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (ROOT/'b4artists_ml').glob('*.py')},script_sha256=sha(HERE),shape_source_sha256=sha(ROOT/'training/b4artists_ml/shape_curve_v1.py'),human_rating='unrated',full_goal_complete=False)
    except BaseException:result['error']=traceback.format_exc()
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(profile=profile,complete=result['complete'],rows=[{k:r.get(k) for k in ('variant','complete','contact_gate_passed','priority_gate_passed','max_contact_drift','error')} for r in result['rows']],error=result.get('error'))),flush=True)
def main():
    BASE.mkdir(exist_ok=False);rows=[]
    for profile in ('boneforge','rigify_basic','rigify_default'):
        log=BASE/(profile+'.log');at=time.perf_counter()
        with log.open('w') as stream:child=subprocess.run(['X:/5.1.0/bforartists.exe','--background','--factory-startup','--disable-autoexec','--python',str(HERE),'--',profile],stdout=stream,stderr=subprocess.STDOUT,timeout=750,env=dict(os.environ,OPENBLAS_NUM_THREADS='4',PYTHONDONTWRITEBYTECODE='1'))
        d=json.loads((BASE/profile/'report.json').read_text());rows.append(dict(profile=profile,complete=d['complete'],host_exit=child.returncode,seconds=time.perf_counter()-at,log_sha256=sha(log)));(BASE/'processes.json').write_text(json.dumps(rows,indent=2)+'\n');print(rows[-1],flush=True)
        if not d['complete']:break
if __name__=='__main__':
    if '--' in sys.argv:host(sys.argv[sys.argv.index('--')+1])
    else:main()
