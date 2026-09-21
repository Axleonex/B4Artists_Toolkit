"""Actual-rig differential contact/COM feasibility; research only."""
from pathlib import Path
import os,sys,json,time,hashlib,subprocess,traceback
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve()
INPUT=ROOT/'training/b4artists_ml/results/grounded-jump-diagnostic-v1'
BASE=ROOT/'training/b4artists_ml/results/ground-velocity-feasibility-v1'
EPSILONS=(.001,.0005,.00025)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,d):p.write_text(json.dumps(d,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def host(profile):
    sys.path[:0]=[str(ROOT)]
    import bpy,numpy as np,b4artists_ml
    from mathutils import Vector,Quaternion
    from b4artists_ml import workflow as w,posing as p,contacts as c,body_solver as bs,support,flight as f,motion_layer as m
    from b4artists_ml.support_math import center_of_mass
    d=json.loads((INPUT/profile/'report.json').read_text());blend=ROOT/d['blend'];assert sha(blend)==d['blend_sha256']
    out=BASE/profile;out.mkdir(exist_ok=False);start=time.perf_counter();report=dict(profile=profile,complete=False,qualified=False,rows=[],script_sha256=sha(HERE))
    def persist():dump(out/'report.json',report)
    try:
        b4artists_ml.register();bpy.ops.wm.open_mainfile(filepath=str(blend),use_scripts=False)
        rigs=[o for o in bpy.data.objects if o.type=='ARMATURE' and o.b4ml.candidate_action];assert len(rigs)==1
        ob=rigs[0];scene=bpy.context.scene;initial_frame=p._frame(scene);initial_pose=w.raw_pose(ob);token=f._curve_token(ob)
        action_names=set(bpy.data.actions.keys());object_names=set(bpy.data.objects.keys())
        binding=bs.mapping(ob);names=binding['names'];root=binding['root'];legs=[r for r in p.bindings(ob)[2] if r['id'] in ('leg-L','leg-R')]
        all_controls=list(dict.fromkeys(binding['rotations']+binding['effectors']))
        leg_controls=list(dict.fromkeys([n for leg in legs for n in leg['fk']]))
        masses=[i.weight for i in ob.b4ml.mass_segments];fractions=[i.fraction for i in ob.b4ml.mass_segments]
        def com_and_scale():
            p._update(ob);ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());world=w.display_world(ob)
            heads=np.array([world@ev.pose.bones[n].head for n in names]);tails=np.array([world@ev.pose.bones[n].tail for n in names])
            a=np.array([heads[i] for _,i,j,_ in support.SEGMENTS]);b=np.array([heads[j] if j is not None else tails[i] for _,i,j,_ in support.SEGMENTS])
            return center_of_mass(a,b,masses,fractions)[0],float(sum(np.linalg.norm(b[i]-a[i]) for i in range(3)))
        endpoint_com={}
        for frame in (15,33):c._frame(scene,frame);endpoint_com[frame]=com_and_scale()[0]
        duration=18/30;average=(endpoint_com[33]-endpoint_com[15])/duration;gravity=np.array(scene.gravity)
        def raw_equal(a,b):return a.keys()==b.keys() and all(all(a[n][k]==b[n][k] for k in ('mode','location','scale','raw_rotation','channels')) for n in a)
        for frame in (15,33):
            c._frame(scene,frame);p._update(ob);before=w.raw_pose(ob);origin,trunk=com_and_scale()
            wanted=average+gravity*duration*(.5 if frame==33 else -.5)
            foot_reference=[(w.display_world(ob)@ob.pose.bones[leg['joints'][2]].matrix).to_quaternion() for leg in legs]
            leg_scale=sum((ob.pose.bones[legs[0]['joints'][i+1]].head-ob.pose.bones[legs[0]['joints'][i]].head).length for i in (0,1))*ob.matrix_world.to_scale().x
            for label,controls in [('legs',leg_controls),('whole_body',all_controls)]:
                q0=[bs._quat(ob.pose.bones[n]) for n in controls];size=3+3*len(controls);probes=0
                def apply(x):
                    nonlocal probes
                    w.restore_pose(ob,before);p._update(ob)
                    p._translate(ob,root,w.display_world(ob).inverted().to_3x3()@Vector(x[:3]*trunk))
                    for index,(name,q) in enumerate(zip(controls,q0)):
                        v=Vector(x[3+3*index:6+3*index]);angle=v.length
                        delta=Quaternion(v/angle,angle) if angle>1e-12 else Quaternion()
                        bs._set_quat(ob.pose.bones[name],q@delta)
                    p._update(ob);probes+=1
                def observe():
                    com,_=com_and_scale();values=[*(com/trunk)]
                    for leg,reference in zip(legs,foot_reference):
                        matrix=w.display_world(ob)@ob.pose.bones[leg['joints'][2]].matrix
                        values.extend(np.array(matrix.translation)/leg_scale)
                        q=reference.rotation_difference(matrix.to_quaternion())
                        if q.w<0:q.negate()
                        values.extend([2*q.x,2*q.y,2*q.z])
                    return np.array(values)
                zero=np.zeros(size);apply(zero);y0=observe();target=np.r_[wanted/trunk,np.zeros(12)];jacobians=[]
                row=dict(frame=frame,variant=label,controls=controls,desired_com_velocity=wanted.tolist(),epsilon_results=[])
                for epsilon in EPSILONS:
                    jac=np.empty((15,size))
                    for j in range(size):
                        assert time.perf_counter()-start<900 and time.time()<1789053845
                        x=zero.copy();x[j]=epsilon;apply(x);plus=observe();x[j]=-epsilon;apply(x);minus=observe();jac[:,j]=(plus-minus)/(2*epsilon)
                    jacobians.append(jac);solution,_,rank,singular=np.linalg.lstsq(jac,target,rcond=1e-4);residual=jac@solution-target
                    group=np.linalg.norm(solution[3:].reshape(-1,3),axis=1);worst=int(np.argmax(group))
                    result=dict(epsilon=epsilon,rank=int(rank),singular_values=singular.tolist(),residual_norm=float(np.linalg.norm(residual)),normalized_com_velocity_error=float(np.linalg.norm(residual[:3])),normalized_contact_velocity_error=float(np.linalg.norm(residual[3:])),root_world_velocity=(solution[:3]*trunk).tolist(),max_local_rotation_rate=float(group[worst]),max_rate_control=controls[worst],solution=solution.tolist(),finite_step_checks=[])
                    for seconds in (1/30,1/120,1/480):
                        apply(solution*seconds);actual=(observe()-y0)/seconds
                        result['finite_step_checks'].append(dict(seconds=seconds,com_velocity_error=float(np.linalg.norm(actual[:3]-target[:3])),contact_velocity_error=float(np.linalg.norm(actual[3:]-target[3:]))))
                    row['epsilon_results'].append(result)
                row.update(derivative_difference_max=[float(np.max(np.abs(jacobians[i+1]-jacobians[i]))) for i in (0,1)],evaluations=probes)
                w.restore_pose(ob,before);p._update(ob);assert raw_equal(w.raw_pose(ob),before)
                row['source_restored']=True;report['rows'].append(row);persist()
        c._frame(scene,initial_frame);w.restore_pose(ob,initial_pose);p._update(ob)
        assert raw_equal(w.raw_pose(ob),initial_pose) and f._curve_token(ob)==token and action_names==set(bpy.data.actions.keys()) and object_names==set(bpy.data.objects.keys()) and sha(blend)==d['blend_sha256']
        report.update(complete=True,source_channels_restored=True,actions_and_objects_unchanged=True,runtime_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (ROOT/'b4artists_ml').glob('*.py')})
    except BaseException:report['error']=traceback.format_exc()
    report['seconds']=time.perf_counter()-start;persist();print(json.dumps({k:report.get(k) for k in ('profile','complete','seconds','error')}),flush=True)
def main():
    BASE.mkdir(exist_ok=False);rows=[]
    for profile in ('boneforge','rigify_basic','rigify_default'):
        log=BASE/(profile+'.log');start=time.perf_counter()
        with log.open('w',encoding='utf-8') as stream:result=subprocess.run(['X:/5.1.0/bforartists.exe','--background','--factory-startup','--disable-autoexec','--python',str(HERE),'--',profile],stdout=stream,stderr=subprocess.STDOUT,timeout=1000,env=dict(os.environ,OPENBLAS_NUM_THREADS='4',PYTHONDONTWRITEBYTECODE='1'))
        path=BASE/profile/'report.json';d=json.loads(path.read_text()) if path.exists() else {};row=dict(profile=profile,exit_code=result.returncode,complete=d.get('complete',False),error=d.get('error'),seconds=time.perf_counter()-start,log_sha256=sha(log));rows.append(row);dump(BASE/'processes.json',rows);print(json.dumps(row),flush=True)
        if not row['complete']:break
if __name__=='__main__':
    if '--' in sys.argv:host(sys.argv[sys.argv.index('--')+1])
    else:main()
