"""Locate remaining preview stalls; run serially after other task-owned jobs."""
from pathlib import Path
import sys,json,os,time,hashlib,subprocess,cProfile,pstats
HERE=Path(__file__).resolve();TR=HERE.parent;ROOT=TR.parents[1];OUT=TR/'results/private-phase-profile-v1'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.write_text(json.dumps(d,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def host():
 import bpy,numpy as np
 sys.path.insert(0,str(ROOT));import b4artists_ml
 from b4artists_ml import workflow as w,contacts as c,rig_state as rs,temporal_preview as tp,temporal_generation as g
 b4artists_ml.register();reference=TR/'results/broader-shape-runtime-v1/rigify_default/reach_hold-smooth_both.blend';bpy.ops.wm.open_mainfile(filepath=str(reference),load_ui=False,use_scripts=False);scene=bpy.context.scene;ob=next(o for o in scene.objects if o.type=='ARMATURE' and o.b4ml.candidate_action);w.finish_preview(ob,scene,False)
 source=ob.animation_data.action;signature=c._action_signature(ob);modes=rs.mode_values(ob);anchors=[(a.frame,a.payload) for a in ob.b4ml.anchors];inventory={n:len(getattr(bpy.data,n)) for n in ('objects','armatures','scenes','actions')};expected=None;runs=[]
 def curves():return sorted((fc.data_path,fc.array_index,tuple((tuple(k.co),tuple(k.handle_left),tuple(k.handle_right),k.interpolation,k.handle_left_type,k.handle_right_type) for k in fc.keyframe_points)) for fc in w.action_curves(ob.animation_data.action,ob.animation_data.action_slot))
 for profiled in (False,True):
  scene.frame_set(1);ob.b4ml.temporal_smoothing=True;prof=cProfile.Profile() if profiled else None;ticks=[];at=time.perf_counter();tp.start(ob,scene);start_seconds=time.perf_counter()-at
  while ob.b4ml.temporal_running:
   before=ob.b4ml.temporal_progress;at=time.perf_counter();done=prof.runcall(tp.step,ob) if profiled else tp.step(ob);elapsed=time.perf_counter()-at;ticks.append(dict(index=len(ticks),before=before,after=ob.b4ml.temporal_progress if not done else 'publication_and_cleanup_complete',seconds=elapsed,done=done))
   if not done:assert ob.animation_data.action==source and c._action_signature(ob)==signature
  actual=curves()
  if expected is None:expected=actual
  else:assert actual==expected
  w.finish_preview(ob,scene,False);assert ob.animation_data.action==source and c._action_signature(ob)==signature and modes==rs.mode_values(ob) and anchors==[(a.frame,a.payload) for a in ob.b4ml.anchors];assert inventory=={n:len(getattr(bpy.data,n)) for n in inventory} and not g._LIVE and not g._OWNERS
  row=dict(profiled=profiled,start_seconds=start_seconds,ticks=ticks,total_seconds=start_seconds+sum(t['seconds'] for t in ticks),max_tick_seconds=max(t['seconds'] for t in ticks),p95_tick_seconds=float(np.percentile([t['seconds'] for t in ticks],95)),source_preserved=True,inventory_preserved=True,exact_between_runs=True)
  if prof is not None:
   stats=pstats.Stats(prof).stats;row['top_cumulative']=[dict(file=key[0],line=key[1],function=key[2],primitive_calls=v[0],calls=v[1],self_seconds=v[2],cumulative_seconds=v[3]) for key,v in sorted(stats.items(),key=lambda kv:kv[1][3],reverse=True)[:40]]
  runs.append(row);write(OUT/'progress.json',dict(runs_complete=len(runs),last_profiled=profiled));print(json.dumps({k:v for k,v in row.items() if k not in ('ticks','top_cumulative')}),flush=True)
 write(OUT/'report.json',dict(complete=True,runs=runs,reference_sha256=sha(reference),runtime_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (ROOT/'b4artists_ml').glob('*.py')},profiled_timings_are_diagnostic_only=True,ui_event_latency_measured=False,full_goal_complete=False))
def main():
 # Controller must additionally verify no other task-owned training/evaluation/host job is live.
 training=read(TR/'results/sequence-tangent-training-v1/active-process.json');assert training.get('all_complete') is True
 assert not OUT.exists();OUT.mkdir();plan=dict(script_sha256=sha(HERE),selection='Same default-Rigify reach_hold reference used by retained serialABBAbenchmark; one unprofiled and one cProfile pass. No production change.',max_seconds=300,profiled_timings_are_not_performance_qualification=True,controller_requires_no_concurrent_jobs=True);write(OUT/'plan.json',plan)
 old=read(TR/'results/private-production-benchmark-v1/report.json');assert all(sha(ROOT/n)==h for n,h in old['runtime_sha256'].items())
 with (OUT/'host.log').open('w') as log:p=subprocess.run(['X:/5.1.0/bforartists.exe','--background','--factory-startup','--disable-autoexec','--python',str(HERE),'--','host'],stdout=log,stderr=subprocess.STDOUT,env=dict(os.environ,OPENBLAS_NUM_THREADS='4',PYTHONDONTWRITEBYTECODE='1'),timeout=300)
 write(OUT/'process.json',dict(exit_code=p.returncode,log_sha256=sha(OUT/'host.log')));assert read(OUT/'report.json')['complete'];print(json.dumps(dict(assertions_passed=True,native_exit_code=p.returncode,native_exit_qualified=p.returncode==0)),flush=True)
if __name__=='__main__':
 if 'host' in sys.argv:host()
 else:main()
