"""Constraint-preserving reconstruction of the frozen joint trajectory; research only."""
from pathlib import Path
import os,sys,json,time,hashlib,subprocess,traceback
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve()
BASE=ROOT/'training/b4artists_ml/results/coupled-trajectory-reconstruction-v2'
MAX_ITERATIONS=16;PROFILE='boneforge';DEADLINE=1789053845

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,d):p.write_text(json.dumps(d,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def host():
    sys.path[:0]=[str(ROOT)]
    import bpy,numpy as np,b4artists_ml
    from mathutils import Vector,Quaternion
    from b4artists_ml import workflow as w,posing as p,contacts as c,body_solver as bs,support,flight as f,motion_layer as m
    from b4artists_ml.support_math import center_of_mass
    started=time.perf_counter();report=dict(complete=False,qualified=False,profile=PROFILE,iterations=[],method='adaptive_projection_of_frozen_joint_trajectory',learned=False,script_sha256=sha(HERE))
    def persist():dump(BASE/'report.json',report)
    try:
        src=json.loads((ROOT/'training/b4artists_ml/results/grounded-jump-diagnostic-v1'/PROFILE/'report.json').read_text());blend=ROOT/src['blend'];assert sha(blend)==src['blend_sha256']
        b4artists_ml.register();bpy.ops.wm.open_mainfile(filepath=str(blend),use_scripts=False)
        rigs=[o for o in bpy.data.objects if o.type=='ARMATURE' and o.b4ml.candidate_action];assert len(rigs)==1
        ob=rigs[0];scene=bpy.context.scene;initial_frame=p._frame(scene);initial_pose=w.raw_pose(ob);token=f._curve_token(ob);actions=set(bpy.data.actions.keys());objects=set(bpy.data.objects.keys())
        binding=bs.mapping(ob);names=binding['names'];root=binding['root'];controls=list(dict.fromkeys(binding['rotations']+binding['effectors']))
        legs=[r for r in p.bindings(ob)[2] if r['id'] in ('leg-L','leg-R')]
        masses=[i.weight for i in ob.b4ml.mass_segments];fractions=[i.fraction for i in ob.b4ml.mass_segments]
        def budget():
            if time.perf_counter()-started>900 or time.time()>DEADLINE:raise TimeoutError('Frozen trajectory research budget exhausted')
        def raw_equal(a,b):return a.keys()==b.keys() and all(all(a[n][k]==b[n][k] for k in ('mode','location','scale','raw_rotation','channels')) for n in a)
        def geom():
            p._update(ob);ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());world=w.display_world(ob)
            heads=np.array([world@ev.pose.bones[n].head for n in names]);tails=np.array([world@ev.pose.bones[n].tail for n in names])
            a=np.array([heads[i] for _,i,j,_ in support.SEGMENTS]);b=np.array([heads[j] if j is not None else tails[i] for _,i,j,_ in support.SEGMENTS])
            return center_of_mass(a,b,masses,fractions)[0],heads,float(sum(np.linalg.norm(b[i]-a[i]) for i in range(3)))
        c._frame(scene,1);com0,_,trunk=geom();root_origin=np.array(w.display_world(ob)@ob.pose.bones[root].head)
        qref=[bs._quat(ob.pose.bones[n]) for n in controls]
        feet=[dict(point=np.array((w.display_world(ob)@ob.pose.bones[r['joints'][2]].matrix).translation),rotation=(w.display_world(ob)@ob.pose.bones[r['joints'][2]].matrix).to_quaternion()) for r in legs]
        leg_scale=src['leg_length_world'];frames=np.arange(1.,50.);fixed=np.array([0,8,14,32,38,48]);free=np.array([i for i in range(49) if i not in fixed]);dim=3+3*len(controls)
        bases=[];X0=[]
        def rotvec(q):
            if q.w<0:q.negate()
            v=np.array([q.x,q.y,q.z]);n=np.linalg.norm(v)
            return v*(2*np.arctan2(n,q.w)/n) if n>1e-12 else v*2
        def sample_base(frame):
            c._frame(scene,float(frame));p._update(ob);raw=w.raw_pose(ob);com,points,_=geom()
            rootpos=(np.array(w.display_world(ob)@ob.pose.bones[root].head)-root_origin)/trunk
            x=np.r_[rootpos,np.concatenate([rotvec(q.rotation_difference(bs._quat(ob.pose.bones[n]))) for n,q in zip(controls,qref)])]
            return dict(frame=float(frame),raw=raw,com=com,rootpos=rootpos,points=points),x
        for frame in frames:
            base,x=sample_base(frame);bases.append(base);X0.append(x)
        X0=np.array(X0);X=X0.copy()
        def apply(base,x):
            w.restore_pose(ob,base['raw']);p._update(ob)
            p._translate(ob,root,w.display_world(ob).inverted().to_3x3()@Vector((x[:3]-base['rootpos'])*trunk))
            for j,(name,q) in enumerate(zip(controls,qref)):
                v=Vector(x[3+3*j:6+3*j]);angle=v.length;delta=Quaternion(v/angle,angle) if angle>1e-12 else Quaternion()
                bs._set_quat(ob.pose.bones[name],q@delta)
            p._update(ob)
        def observe(base,x):
            apply(base,x);com,points,_=geom();res=list((com-base['com'])/trunk);contact=0.;orientation=0.
            if base['frame']<=15 or base['frame']>=33:
                for leg,target in zip(legs,feet):
                    matrix=w.display_world(ob)@ob.pose.bones[leg['joints'][2]].matrix;offset=(np.array(matrix.translation)-target['point'])/leg_scale
                    q=target['rotation'].rotation_difference(matrix.to_quaternion())
                    if q.w<0:q.negate()
                    angle=np.array([2*q.x,2*q.y,2*q.z]);res.extend(offset);res.extend(angle)
                    contact=max(contact,float(np.linalg.norm(offset)));orientation=max(orientation,float(np.linalg.norm(angle)))
            return np.array(res),dict(com=float(np.linalg.norm(res[:3])),contact=contact,orientation=orientation),points

        original=ROOT/'training/b4artists_ml/results/coupled-trajectory-v1'
        original_report=json.loads((original/'report.json').read_text());assert original_report['complete'] and original_report['source_preserved']
        with np.load(original/'latest-trajectory.npz',allow_pickle=False) as archive:
            X=archive['values'].copy();np.testing.assert_allclose(archive['source_values'],X0,rtol=0,atol=2e-6)
        assert np.array_equal(X[fixed],X0[fixed])
        report['input_trajectory_sha256']=sha(original/'latest-trajectory.npz')
        def interpolate(times,values,frame):
            j=min(len(times)-2,max(0,int(np.searchsorted(times,frame,side='right')-1)))
            spans=np.diff(times);slopes=np.diff(values,axis=0)/spans[:,None]
            def tangent(i):
                if i==0:return slopes[0]
                if i==len(times)-1:return slopes[-1]
                return (spans[i]*slopes[i-1]+spans[i-1]*slopes[i])/(spans[i-1]+spans[i])
            h=spans[j];u=(frame-times[j])/h
            return (2*u**3-3*u*u+1)*values[j]+(u**3-2*u*u+u)*h*tangent(j)+(-2*u**3+3*u*u)*values[j+1]+(u**3-u*u)*h*tangent(j+1)
        pins=set(frames[fixed]);projection_records=[]
        def project(frame,seed):
            budget();base,_=sample_base(frame);x=seed.copy();trace=[]
            try:
                for iteration in range(9):
                    r,metric,_=observe(base,x);trace.append(metric)
                    if metric['com']<=2e-5 and metric['contact']<=2e-5 and metric['orientation']<=1e-4:break
                    if frame in pins:raise ValueError('Never move an authored priority in reconstruction')
                    if iteration==8:raise ValueError('Projection iteration limit exceeded')
                    jac=np.empty((len(r),dim))
                    for k in range(dim):
                        v=x.copy();v[k]+=.0005;jac[:,k]=(observe(base,v)[0]-r)/.0005
                    delta=-jac.T@np.linalg.solve(jac@jac.T+1e-8*np.eye(len(r)),r)
                    factor=max(1.,float(np.linalg.norm(delta[:3]))/.025,float(np.max(np.linalg.norm(delta[3:].reshape(-1,3),axis=1)))/.1);delta/=factor
                    accepted=False
                    for fraction in (1.,.5,.25,.125):
                        trial=x+fraction*delta;rr=observe(base,trial)[0]
                        if rr@rr<r@r:x=trial;accepted=True;break
                    if not accepted:raise ValueError('Reconstruction projection stalled')
                projection_records.append(dict(frame=frame,iterations=iteration,final=metric,max_coordinate_change=float(np.max(np.abs(x-seed)))))
                return x
            finally:
                w.restore_pose(ob,base['raw']);p._update(ob);assert raw_equal(w.raw_pose(ob),base['raw'])
        values={float(frame):project(float(frame),interpolate(frames,X,float(frame))) for frame in np.arange(1.,49.001,.25)}
        report['projection_records']=projection_records;report['passes']=[];last_checks=[]
        for refinement in range(4):
            times=np.array(sorted(values));V=np.array([values[t] for t in times]);np.savez(BASE/'latest-reconstruction.npz',frames=times,values=V)
            queries=set(times)
            for a,b in zip(times,times[1:]):queries.update(a+(b-a)*u for u in (.25,.5,.75))
            queries.update(15-2**(-j) for j in range(1,8));queries.update(33+2**(-j) for j in range(1,8))
            failures=[];checks=[]
            for frame in sorted(queries):
                budget();base,_=sample_base(frame);seed=interpolate(times,V,frame)
                try:
                    _,metric,points=observe(base,seed)
                    checks.append(dict(frame=frame,**metric,control_quaternions={n:list(ob.pose.bones[n].matrix.to_quaternion()) for n in controls}))
                    if metric['com']>2e-4 or metric['contact']>2e-4 or metric['orientation']>.001:failures.append(frame)
                finally:w.restore_pose(ob,base['raw']);p._update(ob);assert raw_equal(w.raw_pose(ob),base['raw'])
            last_checks=checks
            row=dict(refinement=refinement,knots=len(times),samples=len(checks),failed_samples=len(failures),max_errors={key:max(r[key] for r in checks) for key in ('com','contact','orientation')})
            report['passes'].append(row);persist();print(json.dumps(row),flush=True)
            if not failures:break
            additions=set(failures)-set(values)
            if refinement==3 or len(values)+len(additions)>512:report['bounded_refinement_exhausted']=True;break
            if not additions:raise ValueError('Existing projected knot fails validation')
            for frame in sorted(additions):values[frame]=project(frame,interpolate(times,V,frame))
        for i in fixed:np.testing.assert_array_equal(values[float(frames[i])],X0[i])
        c._frame(scene,initial_frame);w.restore_pose(ob,initial_pose);p._update(ob)
        assert raw_equal(w.raw_pose(ob),initial_pose) and f._curve_token(ob)==token and actions==set(bpy.data.actions.keys()) and objects==set(bpy.data.objects.keys()) and sha(blend)==src['blend_sha256']
        report.update(complete=True,dense=last_checks,dense_max=report['passes'][-1]['max_errors'],sampled_constraints_passed=not report['passes'][-1]['failed_samples'],source_preserved=True,priorities_unchanged=True,controls=controls,runtime_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (ROOT/'b4artists_ml').glob('*.py')},limits='Sampled constraints only; no analytic continuous bounds, angular momentum, force/collision or human qualification. Dense world-orientation rates remain a separate gate.')
    except BaseException:report['error']=traceback.format_exc()
    report['seconds']=time.perf_counter()-started;persist();print(json.dumps({k:report.get(k) for k in ('complete','sampled_constraints_passed','dense_max','seconds','error')}),flush=True)
def main():
    BASE.mkdir(exist_ok=False);log=BASE/'host.log';at=time.perf_counter()
    with log.open('w',encoding='utf-8') as stream:run=subprocess.run(['X:/5.1.0/bforartists.exe','--background','--factory-startup','--disable-autoexec','--python',str(HERE),'--','host'],stdout=stream,stderr=subprocess.STDOUT,timeout=1000,env=dict(os.environ,OPENBLAS_NUM_THREADS='4',PYTHONDONTWRITEBYTECODE='1'))
    d=json.loads((BASE/'report.json').read_text()) if (BASE/'report.json').exists() else {};result=dict(exit_code=run.returncode,complete=d.get('complete',False),error=d.get('error'),seconds=time.perf_counter()-at,log_sha256=sha(log));dump(BASE/'process.json',result);print(json.dumps(result),flush=True)
if __name__=='__main__':
    if '--' in sys.argv:host()
    else:main()
