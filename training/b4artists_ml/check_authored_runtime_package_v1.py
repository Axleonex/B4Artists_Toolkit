"""Exact-archive headless live, Keep and Discard smoke without UI claims."""
from pathlib import Path
import os,sys,json,zipfile,hashlib,time,subprocess
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve();TAG='authored-runtime-package-v1';OUT=ROOT/f'training/b4artists_ml/results/{TAG}.json';BASE=ROOT/f'training/b4artists_ml/cache/{TAG}'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def host():
 denied=[]
 def audit(event,args):
  if event in ('socket.connect','socket.connect_ex','socket.getaddrinfo','socket.sendto','subprocess.Popen','os.system'):
   denied.append(event);raise RuntimeError('Offline package check blocks '+event)
 sys.addaudithook(audit)
 import socket
 try:socket.getaddrinfo('offline-self-test.invalid',443)
 except RuntimeError:pass
 else:raise AssertionError('Offline guard did not intercept resolution')
 assert denied==['socket.getaddrinfo'];denied.clear()
 import bpy
 sys.path[:0]=[str(BASE),str(ROOT/'tests')]
 import b4artists_ml
 assert Path(b4artists_ml.__file__).resolve().parent==BASE/'b4artists_ml'
 from b4artists_ml import body_live as live,body_preview as body,workflow as w,rig_state as rs
 from test_b4artists_ml_body_live import LivePoseTests
 LivePoseTests.setUpClass();helper=LivePoseTests();records=[]
 for label in ['boneforge','rigify_default']:
  for keep in [False,True]:
   ob,source,modes,action,keys=helper.fixture(label);live.start(ob,now=0.);clock,times=helper.settle(ob,.14)
   target=ob.b4ml.body_targets['Head'].target;target.location.y+=.002;bpy.context.view_layer.update();clock+=.02;assert live.tick(ob,now=clock)=='queued';clock,times=helper.settle(ob,clock)
   record=body._read(ob);metrics=record['metrics'];assert metrics['pin_error']<2e-4 and metrics['length_error']<.002 and metrics['orientation_error_radians']<.001
   body.finish(ob,bpy.context.scene,keep)
   assert w.raw_pose(ob)==source and rs.mode_values(ob)==modes and ob.animation_data.action==action and helper.keys(ob)==keys
   assert len(ob.b4ml.anchors)==int(keep) and not body._JOBS and not live._WATCHERS
   assert not body._RECORDS._entries and body._RECORDS.retained_bytes==0
   assert not any(scene.name.startswith('B4ML private evaluation') for scene in bpy.data.scenes)
   records.append(dict(rig=label,keep=keep,source_preserved=True,metrics=metrics));print(json.dumps(dict(rig=label,keep=keep,passed=True)),flush=True)
 from b4artists_ml import contacts as contacts
 import numpy as np
 for profile in ('boneforge','rigify_basic','rigify_default'):
  reference=json.loads((ROOT/'training/b4artists_ml/results/humanoid-workflow-review-v6-runtime'/profile/'report.json').read_text());assert reference['full_humanoid_workflow_passed']
  bpy.ops.wm.open_mainfile(filepath=str(ROOT/reference['blend_path']),load_ui=False,use_scripts=False)
  ob=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE' and o.b4ml.candidate_action);scene=bpy.context.scene
  w.finish_preview(ob,scene,False);source=ob.animation_data.action;signature=contacts._action_signature(ob);modes=rs.mode_values(ob)
  assert bpy.ops.b4ml.temporal_preview('EXEC_DEFAULT')=={'FINISHED'};assert ob.b4ml.candidate_action
  metrics=contacts.solve(ob,scene);assert metrics['max_after']<=2e-4 and metrics['orientation_error_radians']<=.001
  w.finish_preview(ob,scene,True);w.restore_kept_source(ob,scene);assert ob.animation_data.action==source and contacts._action_signature(ob)==signature and rs.mode_values(ob)==modes
  records.append(dict(rig=profile,workflow='authored_motion_contacts_keep_restore',source_preserved=True,metrics=metrics));print(json.dumps(dict(rig=profile,authored_workflow_passed=True)),flush=True)
 assert not denied
 package_modules={name:str(Path(module.__file__).resolve()) for name,module in sys.modules.items() if name=='b4artists_ml' or name.startswith('b4artists_ml.') if getattr(module,'__file__',None)}
 assert all(Path(path).is_relative_to(BASE.resolve()) for path in package_modules.values())
 result=dict(passed=True,cases=7,package_modules=package_modules,offline_guard_self_test=True,denied_runtime_calls=denied,records=records,package_sha256=sha(ROOT/'releases/b4artists_ml_v0.18.0.zip'),runtime_sha256={p.relative_to(BASE).as_posix():sha(p) for p in (BASE/'b4artists_ml').glob('*.py')},ui_events_tested=False,scope='Exact extracted archive with Python outbound-network and process-launch calls denied, 4headless learned-live/Keep/Discard cases plus3registered authored-motion operator/contact/Keep/Restore cases. No UI input simulation or visual approval.')
 OUT.write_text(json.dumps(result,indent=2)+'\n')
def main():
 if OUT.exists() or BASE.exists():raise RuntimeError('Evidence already exists')
 archive=ROOT/'releases/b4artists_ml_v0.18.0.zip';meta=json.loads((ROOT/'docs/b4artists_ml/package-test-v0.18.0.json').read_text());assert sha(archive)==meta['sha256'];BASE.mkdir()
 with zipfile.ZipFile(archive) as z:
  assert all(not Path(n).is_absolute() and '..' not in Path(n).parts for n in z.namelist());z.extractall(BASE)
 log=ROOT/f'training/b4artists_ml/cache/{TAG}.log';start=time.perf_counter()
 with log.open('w') as stream:
  proc=subprocess.run(['X:/5.1.0/bforartists.exe','--background','--factory-startup','--disable-autoexec','--python',str(HERE),'--','--host'],stdout=stream,stderr=subprocess.STDOUT,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='4',B4ML_PACKAGE=str(BASE),B4ML_RUN_LABEL=TAG),timeout=500)
 receipt=dict(exit_code=proc.returncode,seconds=time.perf_counter()-start,log=log.relative_to(ROOT).as_posix());(OUT.parent/(TAG+'-process.json')).write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
if __name__=='__main__':
 if '--host' in sys.argv:host()
 else:main()
