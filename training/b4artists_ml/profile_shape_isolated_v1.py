"""Serial native timing; no addon edits, training or visual responsiveness claim."""
from pathlib import Path
import sys,os,json,time,hashlib,subprocess,cProfile,pstats,traceback
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve();BASE=ROOT/'training/b4artists_ml/results/shape-isolated-profile-v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.write_text(json.dumps(d,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def host():
 import bpy,numpy as np
 sys.path.insert(0,str(ROOT));import b4artists_ml
 from b4artists_ml import workflow as w,contacts as c,rig_state as rs,temporal_preview as tp,curve_smoothing as cs
 b4artists_ml.register()
 reference=ROOT/'training/b4artists_ml/results/broader-shape-runtime-v1/rigify_default/reach_hold-smooth_both.blend'
 started=time.perf_counter();bpy.ops.wm.open_mainfile(filepath=str(reference),load_ui=False,use_scripts=False);load_s=time.perf_counter()-started
 scene=bpy.context.scene;ob=next(o for o in scene.objects if o.type=='ARMATURE' and o.b4ml.candidate_action);w.finish_preview(ob,scene,False)
 source=ob.animation_data.action;sig=c._action_signature(ob);modes=rs.mode_values(ob);anchors=[(a.frame,a.payload) for a in ob.b4ml.anchors];inventory=len(bpy.data.actions)
 runtime={p.relative_to(ROOT).as_posix():sha(p) for p in (ROOT/'b4artists_ml').glob('*.py')}
 report=dict(complete=False,rig='rigify_default',case='reach_hold',scene_sha256=sha(reference),runtime_sha256=runtime,script_sha256=sha(HERE),host_version=bpy.app.version_string,python=sys.version,numpy=np.__version__,processors=os.cpu_count(),openblas=os.getenv('OPENBLAS_NUM_THREADS'),load_seconds=load_s,method='One native process; serial off/on/on/off then one profiled on run. First run is first invocation, not verified OS-cold. No concurrent task-owned host jobs. Timings exclude assertion overhead; no viewport UI events tested.',runs=[],ui_responsiveness_qualified=False)
 original_publish=tp._publish;original_preview=w.preview;original_smooth=cs.smooth_copy;timing={}
 def wrap(key,fn):
  def call(*args,**kwargs):
   t=time.perf_counter()
   try:return fn(*args,**kwargs)
   finally:timing[key]=timing.get(key,0.)+time.perf_counter()-t
  return call
 tp._publish=wrap('publication_seconds',original_publish);w.preview=wrap('candidate_write_seconds',original_preview);cs.smooth_copy=wrap('smoothing_seconds',original_smooth)
 try:
  for index,enabled in enumerate((False,True,True,False,True)):
   assert time.time()<1789053845.;assert ob.animation_data.action==source and c._action_signature(ob)==sig
   scene.frame_set(1);ob.b4ml.temporal_smoothing=enabled;timing.clear();ticks=[];profiler=cProfile.Profile() if index==4 else None
   if profiler:profiler.enable()
   started=time.perf_counter();tp.start(ob,scene);start_seconds=time.perf_counter()-started
   while ob.b4ml.temporal_running:
    before=ob.b4ml.temporal_progress;t=time.perf_counter();done=tp.step(ob);elapsed=time.perf_counter()-t
    ticks.append(dict(seconds=elapsed,phase_before=before,phase_after=ob.b4ml.temporal_progress,done=done))
    if not done:assert ob.animation_data.action==source and c._action_signature(ob)==sig
   if profiler:
    profiler.disable();profiler.dump_stats(str(BASE/'profile.pstats'));stats=pstats.Stats(profiler)
    functions=[dict(file=k[0],line=k[1],function=k[2],primitive_calls=v[0],calls=v[1],own_seconds=v[2],cumulative_seconds=v[3]) for k,v in stats.stats.items()]
    write(BASE/'profile-functions.json',sorted(functions,key=lambda r:r['cumulative_seconds'],reverse=True))
   candidate=ob.b4ml.candidate_action;assert candidate and candidate!=source
   candidate_slots=w.action_curves(candidate,ob.animation_data.action_slot);curve_count=len(candidate_slots);keys=sum(len(f.keyframe_points) for f in candidate_slots)
   w.finish_preview(ob,scene,False)
   assert ob.animation_data.action==source and c._action_signature(ob)==sig and rs.mode_values(ob)==modes and len(bpy.data.actions)==inventory and [(a.frame,a.payload) for a in ob.b4ml.anchors]==anchors
   row=dict(index=index,smoothing=enabled,profiled=profiler is not None,start_seconds=start_seconds,measured_work_seconds=start_seconds+sum(t['seconds'] for t in ticks),max_tick_seconds=max(t['seconds'] for t in ticks),p95_tick_seconds=float(np.percentile([t['seconds'] for t in ticks],95)),ticks=ticks,timed_sections=dict(timing),source_preserved=True,temporary_actions_recovered=True,curves=curve_count,keys=keys)
   report['runs'].append(row);write(BASE/'report.json',report);print(json.dumps({k:v for k,v in row.items() if k!='ticks'}),flush=True)
  assert runtime=={p.relative_to(ROOT).as_posix():sha(p) for p in (ROOT/'b4artists_ml').glob('*.py')};report['complete']=True;write(BASE/'report.json',report)
 finally:
  tp._publish=original_publish;w.preview=original_preview;cs.smooth_copy=original_smooth

def main():
 BASE.mkdir(exist_ok=False);start=time.perf_counter();log=BASE/'host.log'
 with log.open('w') as out:
  proc=subprocess.run(['X:/5.1.0/bforartists.exe','--background','--factory-startup','--disable-autoexec','--python',str(HERE),'--','host'],stdout=out,stderr=subprocess.STDOUT,env=dict(os.environ,OPENBLAS_NUM_THREADS='4',PYTHONDONTWRITEBYTECODE='1'),timeout=600)
 report=json.loads((BASE/'report.json').read_text());receipt=dict(native_exit_code=proc.returncode,seconds=time.perf_counter()-start,complete=report['complete'],log_sha256=sha(log),script_sha256=sha(HERE));write(BASE/'process.json',receipt);print(json.dumps(receipt),flush=True)
 assert report['complete'] and len(report['runs'])==5
if __name__=='__main__':
 if '--' in sys.argv:host()
 else:main()
