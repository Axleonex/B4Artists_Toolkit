"""Exercise private preparation, lifecycle cleanup, edits and successful publication."""
from pathlib import Path
import os,sys,time,json,hashlib,subprocess
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve();BASE=ROOT/'training/b4artists_ml/results/private-sequence-lifecycle-v2'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
def host():
 sys.path[:0]=[str(ROOT),str(HERE.parent)];import bpy
 import b4artists_ml
 from b4artists_ml import workflow as w,temporal_generation as gen,temporal_math,contacts as c,rig_state as rs
 from private_sequence_job_v2 import PrivateSequenceJob
 b4artists_ml.register();records=[]
 reference=ROOT/'training/b4artists_ml/results/broader-shape-runtime-v1/rigify_basic/reach_hold-smooth_both.blend'
 def setup():
  bpy.ops.wm.open_mainfile(filepath=str(reference),load_ui=False,use_scripts=False);scene=bpy.context.scene;ob=next(o for o in scene.objects if o.type=='ARMATURE' and o.b4ml.candidate_action);w.finish_preview(ob,scene,False)
  return ob,scene
 def inventory():return (len(bpy.data.objects),len(bpy.data.armatures),len(bpy.data.scenes),len(bpy.data.actions))
 def signature(ob,scene):return (ob.animation_data.action.as_pointer(),c._action_signature(ob),w.raw_pose(ob),rs.mode_values(ob),scene.frame_current,scene.frame_subframe)
 def new(ob,chunk_seconds=.02):return PrivateSequenceJob(ob,lambda o,t:o.baseline(t),context=False,prepare_predictor=temporal_math.prepare,chunk_seconds=chunk_seconds)
 for phase in ('private_copy','private_scene','private_prune','private_ready','observing','derivatives'):
  for action in ('cancel','lifecycle'):
   ob,scene=setup();before=signature(ob,scene);counts=inventory();job=new(ob,chunk_seconds=0);found=False
   for _ in range(2000):
    try:progress=next(job)
    except StopIteration:break
    assert signature(ob,scene)==before
    if progress['phase']==phase:found=True;break
   assert found,phase
   if action=='cancel':job.cancel()
   else:gen.before_host_change()
   assert job.closed and not gen._LIVE and not gen._OWNERS and inventory()==counts and signature(ob,scene)==before
   try:next(job)
   except InterruptedError:pass
   else:raise AssertionError('Cancelled work resumed')
   records.append(dict(phase=phase,action=action,source_preserved=True,temporary_data_recovered=True));write(BASE/'progress.json',records)
 ob,scene=setup();before=signature(ob,scene);counts=inventory();job=new(ob)
 for _ in range(4):next(job)
 scene.frame_set(scene.frame_current+2);changed=signature(ob,scene)
 try:next(job)
 except ValueError:pass
 else:raise AssertionError('Source edit accepted')
 assert job.closed and signature(ob,scene)==changed and inventory()==counts;records.append(dict(action='source_edit',newer_edit_preserved=True,temporary_data_recovered=True))
 ob,scene=setup();before=signature(ob,scene);counts=inventory();job=new(ob)
 for _ in range(4):next(job)
 saved=BASE/'paused-save.blend';bpy.ops.wm.save_as_mainfile(filepath=str(saved));assert job.closed and inventory()==counts and signature(ob,scene)==before
 bpy.ops.wm.open_mainfile(filepath=str(saved),load_ui=False,use_scripts=False);assert not any(o.name.startswith('B4ML temporary evaluator') for o in bpy.data.objects) and not gen._LIVE and not gen._OWNERS;records.append(dict(action='actual_save_reload',temporary_data_recovered=True,paused_work_not_resumed=True))
 ob,scene=setup();before=signature(ob,scene);counts=inventory();job=new(ob);ticks=[];started=time.perf_counter()
 while True:
  at=time.perf_counter()
  try:next(job)
  except StopIteration as done:samples,metrics=done.value;ticks.append(time.perf_counter()-at);break
  ticks.append(time.perf_counter()-at);assert signature(ob,scene)==before
 assert job.closed and not gen._LIVE and not gen._OWNERS and inventory()==counts and signature(ob,scene)==before
 w.preview(ob,scene,pose_samples=samples);w.finish_preview(ob,scene,False);assert signature(ob,scene)==before and inventory()==counts
 records.append(dict(action='complete_preview_discard',source_preserved=True,temporary_data_recovered=True,frames=len(samples),seconds=time.perf_counter()-started,max_step_seconds=max(ticks)))
 result=dict(complete=True,records=records,cases=len(records),script_sha256=sha(HERE),job_sha256=sha(HERE.parent/'private_sequence_job_v2.py'),runtime_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (ROOT/'b4artists_ml').glob('*.py')},scope='Headless research lifecycle owner, including actual save/reload; no GUI undo/redo events or addon integration. Native shared callback invoked separately from actual UI events.',host_exit_qualified=False);write(BASE/'report.json',result);print(json.dumps(dict(complete=True,cases=len(records))),flush=True)
def main():
 BASE.mkdir(exist_ok=False);log=BASE/'host.log';at=time.perf_counter()
 with log.open('w') as out:p=subprocess.run(['X:/5.1.0/bforartists.exe','--background','--factory-startup','--disable-autoexec','--python',str(HERE),'--','host'],stdout=out,stderr=subprocess.STDOUT,env=dict(os.environ,OPENBLAS_NUM_THREADS='4',PYTHONDONTWRITEBYTECODE='1'),timeout=240)
 write(BASE/'process.json',dict(exit_code=p.returncode,seconds=time.perf_counter()-at,log_sha256=sha(log)));print(json.dumps(dict(exit_code=p.returncode,seconds=time.perf_counter()-at)),flush=True)
 assert json.loads((BASE/'report.json').read_text())['complete']
if __name__=='__main__':
 if '--' in sys.argv:host()
 else:main()
