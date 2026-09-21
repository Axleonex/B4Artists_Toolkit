"""Dense continuity diagnostic: alternate ankle constraints and measured COM correction.
No production solver, action, native driver or saved input is edited.
"""
from pathlib import Path
import os,sys,json,time,hashlib,subprocess,traceback
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve()
INPUT=ROOT/'training/b4artists_ml/results/grounded-jump-diagnostic-v1'
BASE=ROOT/'training/b4artists_ml/results/coupled-ground-continuity-v2'
FRAMES=sorted(set([i/4 for i in range(4,61)]+[i/4 for i in range(132,197)]+[15-2**(-i) for i in range(1,9)]+[33+2**(-i) for i in range(1,9)]))
MAX_ITERATIONS=24
TOLERANCE=2e-4

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(path,data):path.write_text(json.dumps(data,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def host(profile):
    sys.path[:0]=[str(ROOT),str(ROOT/'tests')]
    import bpy,numpy as np,b4artists_ml
    from mathutils import Vector,Quaternion
    from b4artists_ml import workflow as w,posing as p,contacts as c,support,flight as f,motion_layer as m
    from b4artists_ml.support_math import center_of_mass
    source_report=json.loads((INPUT/profile/'report.json').read_text());blend=ROOT/source_report['blend']
    assert sha(blend)==source_report['blend_sha256']
    out=BASE/profile;out.mkdir(exist_ok=False);started=time.perf_counter()
    report=dict(profile=profile,complete=False,qualified=False,method='alternating_ankle_ik_and_measured_com_translation',learned=False,frames=FRAMES,samples=[],input_blend_sha256=sha(blend),script_sha256=sha(HERE))
    def persist():dump(out/'report.json',report)
    try:
        b4artists_ml.register();bpy.ops.wm.open_mainfile(filepath=str(blend),use_scripts=False)
        rigs=[o for o in bpy.data.objects if o.type=='ARMATURE' and o.b4ml.candidate_action]
        assert len(rigs)==1,len(rigs)
        ob=rigs[0];scene=bpy.context.scene;initial_frame=p._frame(scene);initial_pose=w.raw_pose(ob)
        assert m.find(ob) is not None
        action_token=f._curve_token(ob);actions=set(bpy.data.actions.keys());objects=set(bpy.data.objects.keys())
        profile_info,root,limbs=p.bindings(ob);legs=[r for r in limbs if r['id'] in ('leg-L','leg-R')]
        assert len(legs)==2 and all(r['mode']=='FK' for r in legs)
        binding=support.body_solver.mapping(ob,writable=False);names=binding['names']
        masses=[i.weight for i in ob.b4ml.mass_segments];fractions=[i.fraction for i in ob.b4ml.mass_segments]
        def current_com():
            p._update(ob);ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());world=w.display_world(ob)
            heads=np.array([world@ev.pose.bones[n].head for n in names]);tails=np.array([world@ev.pose.bones[n].tail for n in names])
            a=np.array([heads[i] for _,i,j,_ in support.SEGMENTS]);b=np.array([heads[j] if j is not None else tails[i] for _,i,j,_ in support.SEGMENTS])
            return center_of_mass(a,b,masses,fractions)[0],float(sum(np.linalg.norm(b[i]-a[i]) for i in range(3)))
        c._frame(scene,1);p._update(ob);requests={}
        for leg in legs:
            matrix=w.display_world(ob)@ob.pose.bones[leg['joints'][2]].matrix
            requests[leg['id']]=dict(point=list(matrix.translation),rotation=list(matrix.to_quaternion()),offset=[0,0,0],lock_rotation=True)
        reference_feet=np.array([requests[x]['point'] for x in ('leg-L','leg-R')])
        np.testing.assert_allclose(reference_feet,np.array(source_report['before']['points'])[0],atol=2e-5)
        def raw_equal(a,b):
            return a.keys()==b.keys() and all(all(a[n][k]==b[n][k] for k in ('mode','location','scale','raw_rotation','channels')) for n in a)
        for frame in FRAMES:
            assert time.perf_counter()-started<900 and time.time()<1789053845
            c._frame(scene,frame);p._update(ob);before=w.raw_pose(ob);target,com_scale=current_com()
            lengths={leg['id']:[(ob.pose.bones[leg['joints'][i+1]].head-ob.pose.bones[leg['joints'][i]].head).length for i in (0,1)] for leg in legs}
            leg_scale=sum(lengths[legs[0]['id']])*ob.matrix_world.to_scale().x
            record=dict(frame=frame,passed=False,trace=[],target_com=target.tolist(),input_control_quaternions={n:list(ob.pose.bones[n].matrix.to_quaternion()) for leg in legs for n in leg["fk"]});at=time.perf_counter();poles={leg['id']:None for leg in legs};translation=np.zeros(3)
            def errors():
                actual,_=current_com();foot=0.;angle=0.;stretch=0.
                for leg in legs:
                    req=requests[leg['id']];matrix=w.display_world(ob)@ob.pose.bones[leg['joints'][2]].matrix
                    foot=max(foot,float(np.linalg.norm(np.array(matrix.translation)-req['point']))/leg_scale)
                    angle=max(angle,c._angle(matrix.to_quaternion(),Quaternion(req['rotation'])))
                    for i,length in enumerate(lengths[leg['id']]):
                        stretch=max(stretch,abs((ob.pose.bones[leg['joints'][i+1]].head-ob.pose.bones[leg['joints'][i]].head).length/length-1))
                return dict(com=float(np.linalg.norm(actual-target))/com_scale,contact=foot,orientation=angle,stretch=stretch),target-actual
            try:
                for iteration in range(MAX_ITERATIONS+1):
                    error,residual=errors();record['trace'].append(dict(iteration=iteration,**error))
                    if error['com']<=TOLERANCE and error['contact']<=TOLERANCE and error['orientation']<=.001 and error['stretch']<=.002:
                        record['passed']=True;break
                    if frame in (1,9,15,33,39,49):raise ValueError('Priority pose does not satisfy the requested constraints; never move it')
                    if iteration==MAX_ITERATIONS:break
                    # Alternation is a feasibility experiment, not a temporal solver.
                    # First pin the feet; subsequent COM residual translations receive
                    # another ankle projection before their joint errors are assessed.
                    delta=residual.copy()
                    length=np.linalg.norm(delta);limit=.05*leg_scale
                    if length>limit:delta*=limit/length
                    translation+=delta
                    if np.linalg.norm(translation)>.3*leg_scale:raise ValueError('Bounded pelvis correction exhausted')
                    p._translate(ob,root,w.display_world(ob).inverted().to_3x3()@Vector(delta))
                    for leg in legs:
                        _,_,poles[leg['id']]=c._solve_limb(ob,leg,requests[leg['id']],1.,poles[leg['id']])
                record.update(final=record['trace'][-1],root_correction=translation.tolist(),world_points=[list(w.display_world(ob)@ob.pose.bones[n].head) for n in names],control_quaternions={n:list(ob.pose.bones[n].matrix.to_quaternion()) for leg in legs for n in leg['fk']})
            except Exception as exc:record.update(error_type=type(exc).__name__,error=str(exc))
            finally:
                w.restore_pose(ob,before);p._update(ob);assert raw_equal(w.raw_pose(ob),before)
            record['seconds']=time.perf_counter()-at;record['pose_restored']=True;report['samples'].append(record);persist()
        c._frame(scene,initial_frame);w.restore_pose(ob,initial_pose);p._update(ob)
        assert f._curve_token(ob)==action_token and set(bpy.data.actions.keys())==actions and set(bpy.data.objects.keys())==objects
        assert raw_equal(w.raw_pose(ob),initial_pose) and sha(blend)==source_report['blend_sha256']
        report.update(complete=True,passed_samples=sum(s['passed'] for s in report['samples']),all_samples_passed=all(s['passed'] for s in report['samples']),source_channels_restored=True,actions_and_objects_unchanged=True,semantic_names=names,runtime_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (ROOT/'b4artists_ml').glob('*.py')},limitations=['Framewise feasibility only; no action output or temporal continuity qualification.','Extended-leg priority poses can cause near-boundary velocity singularities.','Existing analytical leg projection; full anatomical limits, collisions, contact forces, toe roll and human assessment are not solved.'])
    except BaseException:report['error']=traceback.format_exc()
    report['seconds']=time.perf_counter()-started;persist();print(json.dumps({k:report.get(k) for k in ('profile','complete','passed_samples','all_samples_passed','error')}),flush=True)
def main():
    BASE.mkdir(exist_ok=False);rows=[]
    for profile in ('boneforge','rigify_basic','rigify_default'):
        log=BASE/(profile+'.log');at=time.perf_counter()
        with log.open('w',encoding='utf-8') as stream:
            result=subprocess.run(['X:/5.1.0/bforartists.exe','--background','--factory-startup','--disable-autoexec','--python',str(HERE),'--',profile],stdout=stream,stderr=subprocess.STDOUT,timeout=1000,env=dict(os.environ,OPENBLAS_NUM_THREADS='4',PYTHONDONTWRITEBYTECODE='1'))
        path=BASE/profile/'report.json';report=json.loads(path.read_text()) if path.exists() else {}
        row=dict(profile=profile,exit_code=result.returncode,complete=report.get('complete',False),passed_samples=report.get('passed_samples'),error=report.get('error'),seconds=time.perf_counter()-at,log_sha256=sha(log));rows.append(row);dump(BASE/'processes.json',rows);print(json.dumps(row),flush=True)
        if not row['complete']:break
if __name__=='__main__':
    if '--' in sys.argv:host(sys.argv[sys.argv.index('--')+1])
    else:main()
