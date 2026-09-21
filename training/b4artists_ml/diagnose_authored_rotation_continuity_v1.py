"""Measure actual saved-action derivatives around the authored crouch priority.
This is a limited numerical diagnostic, not visual assessment or a pass gate.
"""
from pathlib import Path
import sys,json,math,hashlib,subprocess,time,os,traceback
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve();BASE=ROOT/'training/b4artists_ml/results/authored-rotation-continuity-v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def host(profile):
    import bpy,numpy as np
    sys.path.insert(0,str(ROOT));import b4artists_ml
    from b4artists_ml import workflow as w,posing as p,body_solver as bs
    b4artists_ml.register();d=json.loads((ROOT/'training/b4artists_ml/results/humanoid-workflow-review-v6-runtime'/profile/'report.json').read_text());path=ROOT/d['blend_path'];assert d['full_humanoid_workflow_passed'] and sha(path)==d['blend_sha256'];result=dict(profile=profile,complete=False,source_scene_sha256=sha(path),rows=[])
    try:
        bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False);scene=bpy.context.scene;ob=next(o for o in scene.objects if o.type=='ARMATURE' and o.b4ml.candidate_action);binding=bs.mapping(ob,writable=False);original=ob.animation_data.action;slot=w._slot(ob.animation_data)
        def sample(frame):
            scene.frame_set(math.floor(frame),subframe=frame-math.floor(frame));p._update(ob);ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());world=ev.matrix_world
            return np.array([world@ev.pose.bones[n].head for n in binding['names']]),[(world@ev.pose.bones[n].matrix).to_quaternion() for n in binding['names']]
        def omega(a,b,dt):
            rows=[]
            for qa,qb in zip(a,b):
                q=(qb@qa.conjugated()).normalized()
                if q.w<0:q.negate()
                v=np.array((q.x,q.y,q.z));length=np.linalg.norm(v);rows.append(v*(2*math.atan2(length,q.w)/max(length,1e-15)/dt))
            return np.array(rows)
        for label,suffix in [('authored_blend',' 01 authored interpolation'),('body_trajectory',' 02 authored procedural'),('contact_corrected',' 03 explicit foot contacts')]:
            action=bpy.data.actions.get(profile+suffix);assert action;w.assign_action(ob,action,slot)
            for eps in (.25,.125,.0625):
                left,qa=sample(11-eps);at,qb=sample(11);right,qc=sample(11+eps);dt=eps/(scene.render.fps/scene.render.fps_base)
                angular_jump=np.linalg.norm(omega(qb,qc,dt)-omega(qa,qb,dt),axis=-1);velocity_jump=np.linalg.norm((right-at)/dt-(at-left)/dt,axis=-1)
                result['rows'].append(dict(action=label,epsilon_frames=eps,max_angular_velocity_jump_rad_s=float(angular_jump.max()),angular_joint=binding['names'][int(angular_jump.argmax())],max_joint_velocity_jump_world_s=float(velocity_jump.max()),pelvis_velocity_jump_world_s=float(velocity_jump[0])))
        w.assign_action(ob,original,slot);assert sha(path)==d['blend_sha256'];result.update(complete=True,pass_gate_applied=False,visual_assessment='unrated',scope='Finite difference derivatives around authored frame11 only; does not measure full animation continuity.')
    except BaseException:result['error']=traceback.format_exc()
    (BASE/(profile+'.json')).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
def main():
    BASE.mkdir(exist_ok=False);rows=[]
    for profile in ('boneforge','rigify_basic','rigify_default'):
        log=BASE/(profile+'.log');at=time.perf_counter()
        with log.open('w') as stream:child=subprocess.run(['X:/5.1.0/bforartists.exe','--background','--factory-startup','--disable-autoexec','--python',str(HERE),'--',profile],stdout=stream,stderr=subprocess.STDOUT,timeout=240,env=dict(os.environ,OPENBLAS_NUM_THREADS='4',PYTHONDONTWRITEBYTECODE='1'))
        d=json.loads((BASE/(profile+'.json')).read_text());rows.append(dict(profile=profile,complete=d['complete'],host_exit=child.returncode,seconds=time.perf_counter()-at,log_sha256=sha(log)));(BASE/'processes.json').write_text(json.dumps(rows,indent=2)+'\n');print(rows[-1],flush=True)
        if not d['complete']:break
if __name__=='__main__':
    if '--' in sys.argv:host(sys.argv[sys.argv.index('--')+1])
    else:main()
