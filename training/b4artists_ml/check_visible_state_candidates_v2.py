"""Differential source-edit checks and serial matcher microbenchmarks."""
from pathlib import Path
import sys,os,json,time,hashlib,subprocess,statistics
HERE=Path(__file__).resolve();TR=HERE.parent;ROOT=TR.parents[1];OUT=TR/'results/visible-state-candidates-v2'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def host():
 import bpy
 from unittest.mock import patch
 sys.path[:0]=[str(ROOT),str(TR)];import b4artists_ml
 from b4artists_ml import workflow as w,temporal_generation as g
 from visible_state_candidates_v1 import StreamingVisibleState,BulkVisibleState
 b4artists_ml.register();ref=TR/'results/broader-shape-runtime-v1/rigify_default/reach_hold-smooth_both.blend';bpy.ops.wm.open_mainfile(filepath=str(ref),load_ui=False,use_scripts=False);scene=bpy.context.scene;obj=next(o for o in scene.objects if o.type=='ARMATURE' and o.b4ml.candidate_action);w.finish_preview(obj,scene,False);original=g.VisibleState;classes={'legacy':original,'stream':StreamingVisibleState,'bulk':BulkVisibleState};bones=list(obj.pose.bones)[:8]
 modes=['XYZ','XZY','YXZ','YZX','ZXY','ZYX','QUATERNION','AXIS_ANGLE']
 for bone,mode in zip(bones,modes):
  bone.rotation_mode=mode;bone.rotation_euler=(.1,.2,.3);bone.rotation_quaternion=(1,.1,.2,.3);bone.rotation_axis_angle=(.2,0,1,0);bone.lock_location=(False,False,False);bone.lock_scale=(False,False,False);bone.lock_rotation=(False,False,False);bone.lock_rotations_4d=False;bone.lock_rotation_w=False
 records=[]
 def verdict(state):
  try:return bool(state.matches())
  except (ValueError,ArithmeticError):return False
 def trial(label,getter,setter,value):
  before=getter();states={n:cl(obj,scene) for n,cl in classes.items()};assert all(verdict(s) for s in states.values()),label
  setter(value);result={n:verdict(s) for n,s in states.items()};assert len(set(result.values()))==1,(label,result);records.append(dict(case=label,results=result));setter(before)
 def vector_case(label,owner,field,index):
  getter=lambda:tuple(getattr(owner,field));value=list(getter());value[index]=not value[index] if isinstance(value[index],bool) else value[index]+.125;trial(label,getter,lambda v:setattr(owner,field,v),value)
 for bone,mode in zip(bones,modes):
  for field,index in [('location',0),('scale',1),('rotation_euler',0),('rotation_quaternion',1),('rotation_axis_angle',0),('lock_location',1),('lock_scale',2),('lock_rotation',1)]:vector_case(mode+'/'+field,bone,field,index)
  trial(mode+'/four_dimensional_lock',lambda:bone.lock_rotations_4d,lambda v:setattr(bone,'lock_rotations_4d',v),True)
  bone.lock_rotations_4d=True;trial(mode+'/w_lock',lambda:bone.lock_rotation_w,lambda v:setattr(bone,'lock_rotation_w',v),True);bone.lock_rotations_4d=False
  trial(mode+'/rotation_mode',lambda:bone.rotation_mode,lambda v:setattr(bone,'rotation_mode',v),'XYZ' if mode!='XYZ' else 'ZYX')
 for field in g._CHANNELS:vector_case('object/'+field,obj,field,0)
 trial('object/frame',lambda:scene.frame_current,lambda v:scene.frame_set(v),scene.frame_current+1)
 # Direct equivalence on an actual named mode property, if present.
 state=original(obj,scene)
 for name,props in state.modes.items():
  if props:
   key=next(iter(props));bone=obj.pose.bones[name];v=bone[key];trial('rig_mode/'+name+'/'+key,lambda:bone[key],lambda x:bone.__setitem__(key,x),not v if isinstance(v,bool) else v+.125);break
 # Mutation invalidates even a warmed bulk buffer; returned cache arrays are private.
 state=BulkVisibleState(obj,scene);assert state.matches();bone=bones[0];v=bone.location.copy();bone.location.x+=.125;assert not state.matches();bone.location=v;assert state.matches()
 # A rename/reorder route must preserve original dictionary semantics.
 trial('bone_rename',lambda:bones[0].name,lambda v:setattr(bones[0],'name',v),bones[0].name+'_temporary')
 # Full Transaction guards remain the authoritative rejection surface.
 for label,cls in classes.items():
  with patch.object(g,'VisibleState',cls):
   tx=g.Transaction(obj,scene);g._OWNERS[tx.key]=tx;tx.guard();old=obj.location.copy();obj.location.x+=.125
   try:
    try:tx.guard();raise AssertionError('Edited source accepted')
    except ValueError:pass
   finally:obj.location=old
   tx.guard();g._OWNERS.pop(tx.key)
 # Microbenchmarks use unchanged state and alternate order; no tolerance comparisons.
 states={n:cl(obj,scene) for n,cl in classes.items()};times={n:[] for n in classes}
 for name in ('legacy','stream','bulk','bulk','stream','legacy'):
  at=time.perf_counter()
  for _ in range(100):assert states[name].matches()
  times[name].append((time.perf_counter()-at)/100)
 medians={n:statistics.median(v) for n,v in times.items()};report=dict(complete=True,cases=records,differential_cases=len(records),all_match=True,transaction_rejections=3,warm_cache_edit_rejected=True,bones=len(obj.pose.bones),seconds_per_match=times,median_seconds=medians,ratios={n:v/medians['legacy'] for n,v in medians.items()},source_sha256={n:sha(TR/n) for n in ('visible_state_candidates_v1.py','check_visible_state_candidates_v2.py')},production_changed=False,full_goal_complete=False);(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='cases'}),flush=True)
def main():
 OUT.mkdir(exist_ok=False)
 with (OUT/'host.log').open('w') as log:p=subprocess.run(['X:/5.1.0/bforartists.exe','--background','--factory-startup','--disable-autoexec','--python',str(HERE),'--','host'],stdout=log,stderr=subprocess.STDOUT,env=dict(os.environ,OPENBLAS_NUM_THREADS='4',PYTHONDONTWRITEBYTECODE='1'),timeout=180)
 (OUT/'process.json').write_text(json.dumps(dict(exit_code=p.returncode))+'\n');report=OUT/'report.json'
 if not report.exists():print((OUT/'host.log').read_text());raise SystemExit(1)
 print(json.dumps({k:v for k,v in json.loads(report.read_text()).items() if k!='cases'}));print('Native exit',p.returncode)
if __name__=='__main__':
 if 'host' in sys.argv:host()
 else:main()
