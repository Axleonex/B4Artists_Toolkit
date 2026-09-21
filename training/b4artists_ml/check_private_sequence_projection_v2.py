"""Research: solve on a private rig without exposing intermediate source poses.
No addon runtime edit or public controller replacement. Lifecycle/UI integration
and broader rig qualification are intentionally not claimed by this experiment.
"""
from pathlib import Path
import os,sys,json,time,hashlib,subprocess
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve();BASE=ROOT/'training/b4artists_ml/results/private-sequence-projection-v2'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.write_text(json.dumps(d,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def host(profile,case_name):
 global BASE
 BASE=BASE/(profile+'-'+case_name);BASE.mkdir(exist_ok=False)
 sys.path[:0]=[str(ROOT),str(ROOT/'training/b4artists_ml')];import bpy,numpy as np
 import b4artists_ml
 from b4artists_ml import workflow as w,temporal_generation as gen,temporal_math,body_proxy,contacts as c,rig_state as rs
 b4artists_ml.register();scene_path=ROOT/'training/b4artists_ml/results/broader-shape-runtime-v1'/profile/(case_name+'-smooth_both.blend');bpy.ops.wm.open_mainfile(filepath=str(scene_path),load_ui=False,use_scripts=False);scene=bpy.context.scene;ob=next(o for o in scene.objects if o.type=='ARMATURE' and o.b4ml.candidate_action);w.finish_preview(ob,scene,False);source=ob.animation_data.action;sig=c._action_signature(ob);before=w.raw_pose(ob);modes=rs.mode_values(ob);frame=scene.frame_current;inventory=(len(bpy.data.objects),len(bpy.data.armatures),len(bpy.data.scenes),len(bpy.data.actions));results=[]
 def unchanged():return ob.animation_data.action==source and c._action_signature(ob)==sig and w.raw_pose(ob)==before and rs.mode_values(ob)==modes and scene.frame_current==frame
 def count():return (len(bpy.data.objects),len(bpy.data.armatures),len(bpy.data.scenes),len(bpy.data.actions))
 at=time.perf_counter();baseline,metrics=gen.generate_samples(ob,lambda o,t:o.baseline(t),context=False,prepare_predictor=temporal_math.prepare);control_s=time.perf_counter()-at;assert unchanged() and count()==inventory;print(json.dumps(dict(control_seconds=control_s,frames=len(baseline))),flush=True)
 original_transaction=gen.Transaction
 class PrivateTransaction(original_transaction):
  def pause(self,progress,cancel_requested):
   # This private object is never shown or editable by the animator. Original
   # source checks run before/after each externally returned work chunk.
   yield progress
   if cancel_requested is not None and cancel_requested():raise InterruptedError('Private work cancelled')
 def run(case):
  at=time.perf_counter();guard=original_transaction(ob,scene);key=ob.as_pointer();assert key not in gen._OWNERS;gen._OWNERS[key]=guard;proxy=None;iterator=None;ticks=[];result=None;edited=None;external_steps=0;row=None
  try:
   guard.guard();proxy=body_proxy.EvaluationProxy(ob,[p.name for p in ob.pose.bones]);private=proxy.obj;w.assign_action(private,source,w._slot(ob.animation_data));layer=proxy.scene.view_layers[0]
   def context():return bpy.context.temp_override(scene=proxy.scene,view_layer=layer,object=private,active_object=private,selected_objects=[private],selected_editable_objects=[private])
   # Raw generator is deliberate in this bounded headless experiment. A product
   # controller must own private-context close and host lifecycle cancellation.
   iterator=gen._generate_steps(private,lambda o,t:o.baseline(t),context=False,prepare_predictor=temporal_math.prepare)
   while True:
    tick=time.perf_counter();guard.guard();done=False;advanced=False
    with context():
     gen.Transaction=PrivateTransaction
     try:
      while not advanced or time.perf_counter()-tick<.02:
       try:next(iterator);advanced=True
       except StopIteration as stop:result=stop.value;done=True;break
     finally:gen.Transaction=original_transaction
    guard.guard();ticks.append(time.perf_counter()-tick);external_steps+=1;assert unchanged()
    if case=='cancel' and external_steps==2:break
    if case=='source_edit' and external_steps==2:
     scene.frame_set(frame+2);edited=w.raw_pose(ob)
     try:guard.guard()
     except ValueError:break
     else:raise AssertionError('Changed source was not rejected')
    if done:break
   row=dict(case=case,seconds=time.perf_counter()-at,public_chunks=len(ticks),max_chunk_seconds=max(ticks),p95_chunk_seconds=float(np.percentile(ticks,95)),result=result,edited=edited)
   return row
  finally:
   gen.Transaction=original_transaction
   if iterator is not None and proxy is not None:
    with bpy.context.temp_override(scene=proxy.scene,view_layer=proxy.scene.view_layers[0],object=proxy.obj,active_object=proxy.obj):iterator.close()
   if proxy is not None:proxy.close()
   gen._OWNERS.pop(key,None)
   if row is not None:row.update(seconds=time.perf_counter()-at,cleanup_included=True,chunk_includes_both_guards=True)
 report=dict(complete=False,profile=profile,reference_case=case_name,control_seconds=control_s,source_scene_sha256=sha(scene_path),runtime_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (ROOT/'b4artists_ml').glob('*.py')},script_sha256=sha(HERE),cases=results,scope='Headless full-copy private projection experiment. GPU corpus training overlaps; timings are exploratory. No GUI/lifecycle controller qualification or runtime edits.')
 for case in ('complete','cancel','source_edit'):
  row=run(case);result=row.pop('result');edited=row.pop('edited');assert count()==inventory
  if case=='complete':
   samples,metrics=result;assert samples.keys()==baseline.keys();maximum=0.;same=True
   for f in baseline:
    assert samples[f].keys()==baseline[f].keys()
    for name,value in baseline[f].items():
     other=samples[f][name];assert value['mode']==other['mode'] and value['channels']==other['channels']
     for field in ('location','scale','rotation','raw_rotation'):
      error=float(np.max(abs(np.array(value[field])-np.array(other[field]))));maximum=max(maximum,error);same=same and error==0
   row.update(max_channel_difference=maximum,exact_samples=same,source_preserved=unchanged(),inventory_preserved=True)
   # Always record equivalence evidence before deciding whether publication is safe.
   if maximum<=1e-8:
    w.preview(ob,scene,pose_samples=samples);assert ob.b4ml.candidate_action;w.finish_preview(ob,scene,False);assert unchanged() and count()==inventory;row['preview_discard_passed']=True
   else:row['preview_discard_passed']=False
  elif case=='cancel':assert unchanged();row.update(source_preserved=True,inventory_preserved=True)
  else:
   assert scene.frame_current==frame+2 and w.raw_pose(ob)==edited and ob.animation_data.action==source and c._action_signature(ob)==sig;row.update(newer_edit_preserved=True,inventory_preserved=True);scene.frame_set(frame);assert unchanged()
  results.append(row);write(BASE/'report.json',report);print(json.dumps(row),flush=True)
 report['complete']=True;report['equivalence_passed']=results[0]['max_channel_difference']<=1e-8;write(BASE/'report.json',report)
def main():
 BASE.mkdir(exist_ok=False);processes=[]
 for profile,case in [('boneforge','reach_hold'),('boneforge','root_yaw'),('rigify_basic','reach_hold'),('rigify_basic','root_yaw'),('rigify_default','root_yaw')]:
  log=BASE/(profile+'-'+case+'.log');at=time.perf_counter()
  with log.open('w') as out:p=subprocess.run(['X:/5.1.0/bforartists.exe','--background','--factory-startup','--disable-autoexec','--python',str(HERE),'--',profile,case],stdout=out,stderr=subprocess.STDOUT,timeout=300,env=dict(os.environ,OPENBLAS_NUM_THREADS='4',PYTHONDONTWRITEBYTECODE='1'))
  report=json.loads((BASE/(profile+'-'+case)/'report.json').read_text());row=dict(profile=profile,case=case,exit_code=p.returncode,seconds=time.perf_counter()-at,log_sha256=sha(log),complete=report['complete'],equivalence_passed=report['equivalence_passed']);processes.append(row);write(BASE/'processes.json',processes);print(json.dumps(row),flush=True);assert report['complete']
if __name__=='__main__':
 if '--' in sys.argv:host(*sys.argv[sys.argv.index('--')+1:])
 else:main()
