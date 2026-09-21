"""Broaden procedural curve research on actual humanoid rigs; no learned claims."""
from pathlib import Path
import sys,os,json,time,math,hashlib,subprocess,traceback,copy
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve();BASE=ROOT/'training/b4artists_ml/results/broader-shape-workflow-v2'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def write(path,data):path.write_text(json.dumps(data,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def host(profile):
    import bpy,numpy as np
    from mathutils import Vector,Quaternion
    sys.path[:0]=[str(ROOT),str(ROOT/'tests'),str(ROOT/'training/b4artists_ml')]
    import b4artists_ml
    from b4artists_ml import workflow as w,posing as p,contacts as c,body_solver as bs,rig_state as rs,temporal_preview as tp
    from test_b4artists_ml_contacts import BUILDERS
    from shape_curve_v4 import smooth_copy
    import shape_aware_contacts_v1 as shaped_contacts
    b4artists_ml.register();out=BASE/profile;out.mkdir();report=dict(profile=profile,complete=False,cases=[],runtime_sha256={f.relative_to(ROOT).as_posix():sha(f) for f in (ROOT/'b4artists_ml').glob('*.py')},script_sha256=sha(HERE),shape_sha256=sha(ROOT/'training/b4artists_ml/shape_curve_v4.py'),shape_contact_sha256=sha(ROOT/'training/b4artists_ml/shape_aware_contacts_v1.py'),human_rating='unrated',full_goal_complete=False)
    for case in ('reach_hold','root_yaw'):
        result=dict(case=case,complete=False,variants=[]);started=time.perf_counter()
        try:
            bpy.context.window.scene=bpy.data.scenes.new(profile+' '+case);scene=bpy.context.scene;scene.frame_start=1;scene.frame_end=21;scene.render.fps=30
            ob=BUILDERS[profile]();bpy.context.view_layer.objects.active=ob;p._update(ob);state=ob.b4ml
            root=p.bindings(ob)[1];scene.frame_set(1);ob.pose.bones[root].keyframe_insert('location',frame=1);ob.pose.bones[root].keyframe_insert('location',frame=21)
            source=ob.animation_data.action;source.use_fake_user=True;source.name=profile+' '+case+' Source';sig=c._action_signature(ob);modes=rs.mode_values(ob)
            w.capture_anchor(ob,scene)
            if case=='reach_hold':
                scene.frame_set(9);limbs=p.begin(ob,scene);row=next(r for r in limbs if r['id']=='arm-L');a,b,d=[ob.pose.bones[n].head.copy() for n in row['joints']];length=(b-a).length+(d-b).length;direction=(d-a).normalized()
                state.pose_targets['arm-L'].target.location+=w.display_world(ob).to_3x3()@(-direction*.18*length+Vector((0,0,.15*length)))
                state.pose_strength=1.;result['authoring']=p.solve(ob,scene);assert not any(r['clamped'] for r in result['authoring']);p.finish(ob,scene,True)
                hold=state.anchors.add();hold.frame=12.;hold.payload=state.anchors[1].payload
                end=state.anchors.add();end.frame=21.;end.payload=state.anchors[0].payload
            else:
                limbs=p.begin(ob,scene);leg=next(r for r in limbs if r['id']=='leg-L');length=sum((ob.pose.bones[leg['joints'][i+1]].head-ob.pose.bones[leg['joints'][i]].head).length for i in (0,1))
                state.pose_offset=w.display_world(ob).to_3x3()@Vector((0,0,-.08*length))
                for item in state.pose_targets:item.enabled=item.name.startswith('leg')
                result['authoring']=p.solve(ob,scene);assert not any(r['clamped'] for r in result['authoring']);p.finish(ob,scene,True)
                initial=json.loads(state.anchors[0].payload);assert 'root' in initial['pose'];value=initial['pose']['root'];assert value['mode']=='QUATERNION'
                for frame,angle in ((11,math.pi/4),(21,math.pi/2)):
                    payload=copy.deepcopy(initial);q=Quaternion((0,0,1),angle)@Quaternion(value['raw_rotation']);payload['pose']['root']['rotation']=list(q);payload['pose']['root']['raw_rotation']=list(q)
                    anchor=state.anchors.add();anchor.frame=frame;anchor.payload=json.dumps(payload)
            assert c._action_signature(ob)==sig and rs.mode_values(ob)==modes
            anchors=[(a.frame,a.payload) for a in state.anchors];binding=bs.mapping(ob,writable=False)
            def sample(frame):
                c._frame(scene,float(frame));p._update(ob);ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());world=ev.matrix_world
                return np.array([world@ev.pose.bones[n].head for n in binding['names']]),[(world@ev.pose.bones[n].matrix).to_quaternion() for n in binding['names']]
            def matrices(frame):
                sample(frame);return np.array([np.array(w.display_world(ob)@ob.pose.bones[n].matrix) for n in w.read_anchors(ob)[0][1]['pose']])
            w.preview(ob,scene);priorities={f:matrices(f) for f,_ in w.read_anchors(ob)}
            requests=[('leg-L',1.,21.),('leg-R',1.,21.),('arm-L',9.,12.)] if case=='reach_hold' else [(limb,start,end) for start,end in ((1.,3.),(19.,21.)) for limb in ('leg-L','leg-R')]
            for limb,start,end in requests:
                # Final turn contacts are captured at21, initial at1, hold at9.
                sample(21. if case=='root_yaw' and start==19. else start);state.contact_limb=limb;item=c.capture(ob,scene);item.start=start;item.end=end;item.blend=0.;item.strength=1.;item.lock_rotation=True
            w.finish_preview(ob,scene,False);assert ob.animation_data.action==source and c._action_signature(ob)==sig
            scene.frame_set(1);ticks=[];tp.start(ob,scene)
            while state.temporal_running:
                tick=time.perf_counter();done=tp.step(ob);ticks.append(time.perf_counter()-tick)
                if not done:assert ob.animation_data.action==source and c._action_signature(ob)==sig
                assert time.time()<1788981845.
            raw=state.candidate_action;raw.name=profile+' '+case+' Body';raw.use_fake_user=True;slot=w._slot(ob.animation_data)
            result['generation']=dict(ticks=len(ticks),max_tick_s=max(ticks),p95_tick_s=float(np.percentile(ticks,95)))
            def omega(a,b,dt):
                output=[]
                for qa,qb in zip(a,b):
                    q=(qb@qa.conjugated()).normalized()
                    if q.w<0:q.negate()
                    v=np.array((q.x,q.y,q.z));n=np.linalg.norm(v);output.append(v*(2*math.atan2(n,q.w)/max(n,1e-15)/dt))
                return np.array(output)
            def inspect():
                maximum=0.;rotation=0.;checks=0;mapping={r['id']:r for r in p.bindings(ob)[2]};derivatives=[]
                for frame in np.linspace(1.,21.,1281):
                    sample(frame)
                    for request in c.rows(ob):
                        if not request['start']<=frame<=request['end']:continue
                        row=mapping[request['limb']];length=sum((ob.pose.bones[row['joints'][i+1]].head-ob.pose.bones[row['joints'][i]].head).length for i in (0,1))*w.display_world(ob).to_scale().x
                        maximum=max(maximum,(c._point(ob,row,request['offset'])-Vector(request['point'])).length/length);rotation=max(rotation,c._angle((w.display_world(ob)@ob.pose.bones[row['joints'][2]].matrix).to_quaternion(),Quaternion(request['rotation'])));checks+=1
                priority=max(float(np.max(np.abs(matrices(f)-expected))) for f,expected in priorities.items())
                for f in sorted(priorities)[1:-1]:
                    for eps in (.0625,.03125,.015625):
                        left,qa=sample(f-eps);at,qb=sample(f);right,qc=sample(f+eps);dt=eps/30.;angular=np.linalg.norm(omega(qb,qc,dt)-omega(qa,qb,dt),axis=-1)
                        derivatives.append(dict(frame=f,epsilon=eps,max_angular_jump_rad_s=float(angular.max()),joint=binding['names'][int(angular.argmax())],pelvis_velocity_jump_world_s=float(np.linalg.norm((right[0]-at[0])/dt-(at[0]-left[0])/dt))))
                return dict(max_contact_drift=maximum,max_contact_rotation=rotation,contact_checks=checks,max_priority_matrix_error=priority,contact_gate_passed=maximum<=2e-4 and rotation<=.001,priority_gate_passed=priority<=2e-4,derivatives=derivatives)
            for variant in ('baseline','smooth_both'):
                row=dict(variant=variant,complete=False);at=time.perf_counter()
                try:
                    w.assign_action(ob,raw,slot);state.candidate_action=raw;state.contact_input=None;state.contact_output=None;state.contact_metrics=''
                    if variant=='smooth_both':
                        candidate,info=smooth_copy(ob,raw,1.,21.);w.assign_action(ob,candidate,slot);state.candidate_action=candidate;row['shape_before']=info
                    row['contact_solve']=(shaped_contacts.solve if variant=='smooth_both' else c.solve)(ob,scene)
                    row.update(inspect());row['complete']=True
                    if row['contact_gate_passed'] and row['priority_gate_passed']:
                        candidate=state.candidate_action;candidate.use_fake_user=True;candidate.name=profile+' '+case+' '+variant
                        if 'b4ml_contact_metrics' in candidate:del candidate['b4ml_contact_metrics']
                        state.contact_input=None;state.contact_output=None;state.contact_metrics='';scene.frame_set(11)
                        text=bpy.data.texts.new('READ ME '+case+' '+variant);text.write('Procedural research. Skeleton fixture; no mesh or independent animator qualification. Mechanical root-yaw reference is not a completed natural turning gait. Contact and priority metrics:\n'+json.dumps(row,indent=2))
                        saved=out/(case+'-'+variant+'.blend');bpy.ops.wm.save_as_mainfile(filepath=str(saved));row['scene']=saved.relative_to(ROOT).as_posix();row['scene_sha256']=sha(saved)
                except (ValueError,RuntimeError) as exc:row['error']=str(exc)
                row['seconds']=time.perf_counter()-at;result['variants'].append(row);write(out/'progress.json',result)
            assert [(a.frame,a.payload) for a in state.anchors]==anchors
            w.finish_preview(ob,scene,True);w.restore_kept_source(ob,scene);assert ob.animation_data.action==source and c._action_signature(ob)==sig and rs.mode_values(ob)==modes
            result.update(complete=True,source_restored=True,anchor_payloads_unchanged=True,priority_frames=sorted(priorities),contact_requests=requests)
        except BaseException:result['error']=traceback.format_exc()
        result['seconds']=time.perf_counter()-started;report['cases'].append(result);write(out/'report.json',report)
    report['complete']=all(r['complete'] for r in report['cases']);write(out/'report.json',report);print(json.dumps(dict(profile=profile,complete=report['complete'],cases=[dict(case=r['case'],complete=r['complete'],error=r.get('error'),variants=[{k:v.get(k) for k in ('variant','complete','contact_gate_passed','priority_gate_passed','error','max_contact_drift')} for v in r['variants']]) for r in report['cases']])),flush=True)
def main():
    BASE.mkdir(exist_ok=False);rows=[]
    for profile in ('boneforge','rigify_basic','rigify_default'):
        log=BASE/(profile+'.log');at=time.perf_counter()
        with log.open('w') as stream:child=subprocess.run(['X:/5.1.0/bforartists.exe','--background','--factory-startup','--disable-autoexec','--python',str(HERE),'--',profile],stdout=stream,stderr=subprocess.STDOUT,timeout=1200,env=dict(os.environ,OPENBLAS_NUM_THREADS='4',PYTHONDONTWRITEBYTECODE='1'))
        report=json.loads((BASE/profile/'report.json').read_text());row=dict(profile=profile,complete=report['complete'],host_exit=child.returncode,seconds=time.perf_counter()-at,log_sha256=sha(log));rows.append(row);write(BASE/'processes.json',rows);print(row,flush=True)
if __name__=='__main__':
    if '--' in sys.argv:host(sys.argv[sys.argv.index('--')+1])
    else:main()
