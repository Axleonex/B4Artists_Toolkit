"""Exact-archive headless live, Keep and Discard smoke without UI claims."""
from pathlib import Path
import os,sys,json,zipfile,hashlib,time,subprocess
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve();TAG='cooperative-package-v1';OUT=ROOT/f'training/b4artists_ml/results/{TAG}.json';BASE=ROOT/f'training/b4artists_ml/cache/{TAG}'
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
   assert not any(scene.name.startswith('B4ML private evaluation') for scene in bpy.data.scenes)
   records.append(dict(rig=label,keep=keep,source_preserved=True,metrics=metrics));print(json.dumps(dict(rig=label,keep=keep,passed=True)),flush=True)
 assert not denied
 result=dict(passed=True,cases=4,offline_guard_self_test=True,denied_runtime_calls=denied,records=records,package_sha256=sha(ROOT/'releases/b4artists_ml_v0.17.3.zip'),runtime_sha256={p.relative_to(BASE).as_posix():sha(p) for p in (BASE/'b4artists_ml').glob('*.py')},ui_events_tested=False,scope='Exact extracted archive with Python outbound-network and process-launch calls denied, headless live-step API with two edits and Keep/Discard. No UI input simulation or visual approval.')
 OUT.write_text(json.dumps(result,indent=2)+'\n')
def main():
 if OUT.exists() or BASE.exists():raise RuntimeError('Evidence already exists')
 archive=ROOT/'releases/b4artists_ml_v0.17.3.zip';meta=json.loads((ROOT/'docs/b4artists_ml/package-test-v0.17.3.json').read_text());assert sha(archive)==meta['sha256'];BASE.mkdir()
 with zipfile.ZipFile(archive) as z:
  assert all(not Path(n).is_absolute() and '..' not in Path(n).parts for n in z.namelist());z.extractall(BASE)
 log=ROOT/f'training/b4artists_ml/cache/{TAG}.log';start=time.perf_counter()
 with log.open('w') as stream:
  proc=subprocess.run(['X:/5.1.0/bforartists.exe','--background','--factory-startup','--disable-autoexec','--python',str(HERE),'--','--host'],stdout=stream,stderr=subprocess.STDOUT,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='4',B4ML_PACKAGE=str(BASE),B4ML_RUN_LABEL=TAG),timeout=180)
 receipt=dict(exit_code=proc.returncode,seconds=time.perf_counter()-start,log=log.relative_to(ROOT).as_posix());(OUT.parent/(TAG+'-process.json')).write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
if __name__=='__main__':
 if '--host' in sys.argv:host()
 else:main()
