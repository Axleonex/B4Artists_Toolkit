"""Serial verification of the actual integrated comparator against preserved legacy source."""
from pathlib import Path
import os,sys,json,time,hashlib,subprocess,statistics
HERE=Path(__file__).resolve();TR=HERE.parent;ROOT=TR.parents[1];OUT=TR/'results/visible-state-integrated-workflow-v1'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.write_text(json.dumps(d,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def host():
 import bpy,numpy as np
 from types import SimpleNamespace
 from unittest.mock import patch
 sys.path[:0]=[str(ROOT),str(TR)];import b4artists_ml
 from b4artists_ml import workflow as w,temporal_generation as g,temporal_preview as tp,contacts as c,rig_state as rs
 import ast
 BulkPose=g._PoseComparison;BulkVisibleState=g.VisibleState
 legacy_path=TR/'results/visible-state-production-baseline-v1/temporal_generation.py'
 assert sha(legacy_path)=='cd995e038498182ef49f6dd79aded25252a4744dea81b439f9fd1f37eb884b73'
 tree=ast.parse(legacy_path.read_text(encoding='utf-8-sig'))
 cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='VisibleState')
 namespace=dict(vars(g));exec(compile(ast.Module(body=[cls],type_ignores=[]),str(legacy_path),'exec'),namespace)
 LegacyVisibleState=namespace['VisibleState']
 b4artists_ml.register();ref=TR/'results/broader-shape-runtime-v1/rigify_default/reach_hold-smooth_both.blend';bpy.ops.wm.open_mainfile(filepath=str(ref),load_ui=False,use_scripts=False);scene=bpy.context.scene;obj=next(o for o in scene.objects if o.type=='ARMATURE' and o.b4ml.candidate_action);w.finish_preview(obj,scene,False);source=obj.animation_data.action;original=LegacyVisibleState
 expected=w.raw_pose(obj);bulk=BulkPose(expected);bones=list(obj.pose.bones)
 class Collection:
  def __init__(self,rows,error=None):self.rows=rows;self.error=error
  def __len__(self):return len(self.rows)
  def __iter__(self):return iter(self.rows)
  def foreach_get(self,*args):
   if self.error:raise self.error('Batch reads unavailable')
   obj.pose.bones.foreach_get(*args)
 edges=[]
 for label,rows,error in [('normal',bones,None),('reordered',list(reversed(bones)),None),('removed',bones[:-1],None),('unsupported_type',bones,TypeError),('unsupported_runtime',bones,RuntimeError),('unsupported_attribute',bones,AttributeError)]:
  fake=SimpleNamespace(pose=SimpleNamespace(bones=Collection(rows,error)));a=(expected==w.raw_pose(fake));b=bulk.matches(fake);assert a==b;(edges.append(dict(case=label,legacy=a,bulk=b)))
 empty=SimpleNamespace(pose=SimpleNamespace(bones=Collection([],None)));assert BulkPose({}).matches(empty)==(w.raw_pose(empty)=={})
 # Nonfinite/invalid channels must never become accepted source changes.
 bone=bones[0];oldmode=bone.rotation_mode;oldloc=bone.location.copy();bone.rotation_mode='QUATERNION';start=g.VisibleState(obj,scene);fast=BulkVisibleState(obj,scene);bone.location.x=float('nan');assert not start.matches() and not fast.matches();bone.location=oldloc;bone.rotation_mode=oldmode
 write(OUT/'edge-checks.json',dict(passed=True,cases=edges,empty_pose=True,nan_rejected=True))
 # Reload the unchanged fixture after destructive-in-memory edge cases.
 bpy.ops.wm.open_mainfile(filepath=str(ref),load_ui=False,use_scripts=False);scene=bpy.context.scene;obj=next(o for o in scene.objects if o.type=='ARMATURE' and o.b4ml.candidate_action);w.finish_preview(obj,scene,False);source=obj.animation_data.action;signature=c._action_signature(obj);modes=rs.mode_values(obj);anchors=[(a.frame,a.payload) for a in obj.b4ml.anchors];inventory={n:len(getattr(bpy.data,n)) for n in ('objects','armatures','scenes','actions')}
 def curves():return sorted((fc.data_path,fc.array_index,tuple((tuple(k.co),tuple(k.handle_left),tuple(k.handle_right),k.interpolation,k.handle_left_type,k.handle_right_type) for k in fc.keyframe_points)) for fc in w.action_curves(obj.animation_data.action,obj.animation_data.action_slot))
 output=None;runs=[]
 for index,name in enumerate(('legacy','bulk','bulk','legacy')):
  scene.frame_set(1);obj.b4ml.temporal_smoothing=True;ticks=[]
  with patch.object(g,'VisibleState',original if name=='legacy' else BulkVisibleState):
   at=time.perf_counter();tp.start(obj,scene);setup=time.perf_counter()-at
   while obj.b4ml.temporal_running:
    at=time.perf_counter();done=tp.step(obj);ticks.append(time.perf_counter()-at)
    if not done:assert obj.animation_data.action==source and c._action_signature(obj)==signature
  values=curves()
  if output is None:output=values
  else:assert output==values
  w.finish_preview(obj,scene,False);assert obj.animation_data.action==source and c._action_signature(obj)==signature and rs.mode_values(obj)==modes and anchors==[(a.frame,a.payload) for a in obj.b4ml.anchors];assert inventory=={n:len(getattr(bpy.data,n)) for n in inventory} and not g._LIVE and not g._OWNERS
  row=dict(index=index,variant=name,seconds=setup+sum(ticks),setup_seconds=setup,ticks=len(ticks),max_tick=max(ticks),p95_tick=float(np.percentile(ticks,95)),exact_curves=True,source_preserved=True,inventory_preserved=True);runs.append(row);write(OUT/'progress.json',dict(runs=runs));print(json.dumps(row),flush=True)
 medians={name:statistics.median(r['seconds'] for r in runs if r['variant']==name) for name in ('legacy','bulk')};ratio=medians['bulk']/medians['legacy'];plan=read(OUT/'plan.json');write(OUT/'report.json',dict(complete=True,runs=runs,median_seconds=medians,ratio=ratio,performance_gate_passed=ratio<=plan['end_to_end_ratio_max'],exact_output=True,source_preserved=True,production_changed=True,runtime_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (ROOT/'b4artists_ml').glob('*.py')},full_goal_complete=False,plan_sha256=sha(OUT/'plan.json')))
def main():
 assert read(TR/'results/visible-state-candidates-v2/report.json')['all_match'];assert all(r['assertions_passed'] for r in read(TR/'results/visible-state-production-focused-v2-regression.json'));OUT.mkdir(exist_ok=False);write(OUT/'plan.json',dict(script_sha256=sha(HERE),runtime_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (ROOT/'b4artists_ml').glob('*.py')},selection='Actual integrated VisibleState versus preserved legacy class; original exact-output and five-percent performance gate retained.',end_to_end_ratio_max=.95,order=['legacy','bulk','bulk','legacy'],invariants='Same guard boundaries, exact full candidate curves and source/inventory recovery',max_seconds=300,concurrent_task_jobs=False))
 with (OUT/'host.log').open('w') as log:p=subprocess.run(['X:/5.1.0/bforartists.exe','--background','--factory-startup','--disable-autoexec','--python',str(HERE),'--','host'],stdout=log,stderr=subprocess.STDOUT,env=dict(os.environ,OPENBLAS_NUM_THREADS='4',PYTHONDONTWRITEBYTECODE='1'),timeout=300)
 write(OUT/'process.json',dict(exit_code=p.returncode,log_sha256=sha(OUT/'host.log')))
 if not (OUT/'report.json').exists():print((OUT/'host.log').read_text());raise SystemExit(1)
 print(json.dumps(read(OUT/'report.json')));print('Native exit',p.returncode)
if __name__=='__main__':
 if 'host' in sys.argv:host()
 else:main()
