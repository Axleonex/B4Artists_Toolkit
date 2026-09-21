"""Joint trajectory SQP research; immutable priorities, dense actual-rig checks."""
from pathlib import Path
import os,sys,json,time,hashlib,subprocess,traceback
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve()
BASE=ROOT/'training/b4artists_ml/results/coupled-trajectory-v1'
MAX_ITERATIONS=16;PROFILE='boneforge';DEADLINE=1789053845

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,d):p.write_text(json.dumps(d,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def host():
    sys.path[:0]=[str(ROOT)]
    import bpy,numpy as np,b4artists_ml
    from mathutils import Vector,Quaternion
    from b4artists_ml import workflow as w,posing as p,contacts as c,body_solver as bs,support,flight as f,motion_layer as m
    from b4artists_ml.support_math import center_of_mass
    started=time.perf_counter();report=dict(complete=False,qualified=False,profile=PROFILE,iterations=[],method='joint_frame_SQP_with_temporal_regularization',learned=False,script_sha256=sha(HERE))
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
        # Source authoring is preserved independently of the solver's pose metric.
        for i in fixed:
            c._frame(scene,float(frames[i]));res,errors,_=observe(bases[i],X0[i]);assert max(errors['com'],errors['contact'])<2e-4 and errors['orientation']<.001
        D1=np.diff(np.eye(49),axis=0)*30;D2=np.diff(np.eye(49),n=2,axis=0)*900
        A=.05*np.eye(49)+.001*(D1.T@D1)+.00001*(D2.T@D2);Ai=np.linalg.inv(A[np.ix_(free,free)])
        def objective(x):return float(.05*np.sum((x-X0)**2)+.001*np.sum((D1@x)**2)+.00001*np.sum((D2@x)**2))
        def all_errors(x,derivatives=False):
            residuals=[];jacobians=[];metrics=[]
            for i in free:
                budget();base=bases[i];c._frame(scene,base['frame']);r,metric,_=observe(base,x[i]);residuals.append(r);metrics.append(metric)
                if derivatives:
                    jac=np.empty((len(r),dim))
                    for j in range(dim):
                        v=x[i].copy();v[j]+=.001;plus=observe(base,v)[0];jac[:,j]=(plus-r)/.001
                    jacobians.append(jac)
                w.restore_pose(ob,base['raw']);p._update(ob)
                assert raw_equal(w.raw_pose(ob),base['raw'])
            return residuals,jacobians,metrics
        damping=1e-5
        for iteration in range(MAX_ITERATIONS):
            at=time.perf_counter();residuals,J,metrics=all_errors(X,True);r=np.concatenate(residuals);gradient=(A@X-.05*X0)[free];unconstrained=-Ai@gradient
            sizes=[len(v) for v in residuals];offset=np.r_[0,np.cumsum(sizes)];S=np.zeros((len(r),len(r)))
            for i in range(len(free)):
                for j in range(i,len(free)):
                    block=Ai[i,j]*(J[i]@J[j].T);S[offset[i]:offset[i+1],offset[j]:offset[j+1]]=block
                    if i!=j:S[offset[j]:offset[j+1],offset[i]:offset[i+1]]=block.T
            rhs=-r-np.concatenate([j@u for j,u in zip(J,unconstrained)])
            multipliers=np.linalg.solve(S+damping*np.eye(len(r)),rhs)
            force=np.stack([j.T@multipliers[offset[i]:offset[i+1]] for i,j in enumerate(J)])
            step=unconstrained+Ai@force
            largest=max(1.,float(np.max(np.linalg.norm(step[:,:3],axis=1)))/.05,float(np.max(np.linalg.norm(step[:,3:].reshape(-1,3),axis=1)))/.15);step/=largest
            score=objective(X)+10000*float(r@r);accepted=False;chosen=None
            for fraction in (1.,.5,.25,.125):
                trial=X.copy();trial[free]+=fraction*step;newres,_,newmetrics=all_errors(trial);nr=np.concatenate(newres);newscore=objective(trial)+10000*float(nr@nr)
                if newscore<score:
                    X=trial;accepted=True;chosen=newmetrics;damping=max(1e-7,damping*.5);break
            if not accepted:damping=min(.1,damping*10)
            row=dict(iteration=iteration,accepted=accepted,objective=objective(X),old_merit=score,new_merit=newscore,max_com=max(m['com'] for m in (chosen or metrics)),max_contact=max(m['contact'] for m in (chosen or metrics)),max_orientation=max(m['orientation'] for m in (chosen or metrics)),seconds=time.perf_counter()-at,damping=damping)
            report['iterations'].append(row);np.savez(BASE/'latest-trajectory.npz',frames=frames,values=X,source_values=X0);persist();print(json.dumps(row),flush=True)
        assert np.array_equal(X[fixed],X0[fixed])
        tangents=np.empty_like(X);tangents[0]=X[1]-X[0];tangents[-1]=X[-1]-X[-2];tangents[1:-1]=(X[2:]-X[:-2])/2
        def at_frame(frame):
            j=min(47,int(frame)-1);u=frame-frames[j]
            return (2*u**3-3*u*u+1)*X[j]+(u**3-2*u*u+u)*tangents[j]+(-2*u**3+3*u*u)*X[j+1]+(u**3-u*u)*tangents[j+1]
        dense=[];dense_frames=sorted(set([i/4 for i in range(4,197)]+[15-2**(-j) for j in range(1,8)]+[33+2**(-j) for j in range(1,8)]))
        for frame in dense_frames:
            budget();base,_=sample_base(frame);x=at_frame(frame);r,metric,points=observe(base,x)
            dense.append(dict(frame=frame,**metric,world_points=points.tolist(),control_quaternions={n:list(ob.pose.bones[n].matrix.to_quaternion()) for n in controls}))
            w.restore_pose(ob,base['raw']);p._update(ob);assert raw_equal(w.raw_pose(ob),base['raw'])
        c._frame(scene,initial_frame);w.restore_pose(ob,initial_pose);p._update(ob)
        assert raw_equal(w.raw_pose(ob),initial_pose) and f._curve_token(ob)==token and actions==set(bpy.data.actions.keys()) and objects==set(bpy.data.objects.keys()) and sha(blend)==src['blend_sha256']
        report.update(complete=True,dense=dense,dense_max={key:max(r[key] for r in dense) for key in ('com','contact','orientation')},source_preserved=True,priorities_unchanged=True,controls=controls,runtime_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (ROOT/'b4artists_ml').glob('*.py')},limits='No anatomical force, collision or human qualification. Smoothness objective uses local rotation-vector coordinates; independent world-orientation checks remain required.')
    except BaseException:report['error']=traceback.format_exc()
    report['seconds']=time.perf_counter()-started;persist();print(json.dumps({k:report.get(k) for k in ('complete','dense_max','seconds','error')}),flush=True)
def main():
    BASE.mkdir(exist_ok=False);log=BASE/'host.log';at=time.perf_counter()
    with log.open('w',encoding='utf-8') as stream:run=subprocess.run(['X:/5.1.0/bforartists.exe','--background','--factory-startup','--disable-autoexec','--python',str(HERE),'--','host'],stdout=stream,stderr=subprocess.STDOUT,timeout=1000,env=dict(os.environ,OPENBLAS_NUM_THREADS='4',PYTHONDONTWRITEBYTECODE='1'))
    d=json.loads((BASE/'report.json').read_text()) if (BASE/'report.json').exists() else {};result=dict(exit_code=run.returncode,complete=d.get('complete',False),error=d.get('error'),seconds=time.perf_counter()-at,log_sha256=sha(log));dump(BASE/'process.json',result);print(json.dumps(result),flush=True)
if __name__=='__main__':
    if '--' in sys.argv:host()
    else:main()
