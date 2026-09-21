"""Reproduce completion-record corruption on released and fixed actual rigs."""
from pathlib import Path
import sys,os,json,hashlib,zipfile,subprocess,time
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve();OUT=ROOT/'training/b4artists_ml/results/finalization-fault-comparison-v1.json';BASE=ROOT/'training/b4artists_ml/cache/cooperative-package-v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def host(variant):
 package=BASE if variant=='released' else ROOT
 sys.path[:0]=[str(package),str(ROOT/'tests')]
 os.environ['B4ML_PACKAGE']=str(package)
 import bpy,b4artists_ml
 from unittest.mock import patch
 from b4artists_ml import body_preview as body,workflow as w,rig_state as rs
 from test_b4artists_ml_body_live import LivePoseTests
 assert Path(b4artists_ml.__file__).resolve().parent==package/'b4artists_ml'
 LivePoseTests.setUpClass();helper=LivePoseTests();rows=[]
 for rig in ['boneforge','rigify_default']:
  ob,source,modes,action,keys=helper.fixture(rig);body.solve(ob);before=w.raw_pose(ob);payload=ob.b4ml.body_payload
  ob.b4ml.body_targets['Head'].target.location.y+=.002;bpy.context.view_layer.update();body.start(ob);request=body._request;fired=[];error=None
  def malformed(*args,**kwargs):
   fired.append(True);ob.b4ml.body_payload='{';return request(*args,**kwargs)
  try:
   with patch.object(body,'_request',malformed):
    try:
     for _ in range(3000):
      if body.step(ob):raise AssertionError('Invalid record accepted')
     else:raise AssertionError('Solve did not settle')
    except json.JSONDecodeError:error='JSONDecodeError'
   restored=w.raw_pose(ob)==before;empty=not body._JOBS and not ob.b4ml.body_running
   assert fired and error=='JSONDecodeError' and empty
   if variant=='released':assert not restored
   else:assert restored
   row=dict(rig=rig,variant=variant,error=error,verified_preview_restored=restored,jobs_empty=empty)
  finally:ob.b4ml.body_payload=payload;body.finish(ob,bpy.context.scene,False)
  assert w.raw_pose(ob)==source and rs.mode_values(ob)==modes and ob.animation_data.action==action and helper.keys(ob)==keys
  row['source_and_keys_preserved_after_cleanup']=True;rows.append(row)
 result=dict(passed=True,rows=rows,runtime_sha256={p.relative_to(package).as_posix():sha(p) for p in (package/'b4artists_ml').glob('*.py')});(OUT.parent/f'finalization-fault-{variant}-v1.json').write_text(json.dumps(result,indent=2)+'\n')
def main():
 if OUT.exists():raise RuntimeError('Evidence already exists')
 with zipfile.ZipFile(ROOT/'releases/b4artists_ml_v0.17.3.zip') as z:assert all(z.read(n)==(BASE/n).read_bytes() for n in z.namelist())
 rows=[]
 for variant in ['released','current']:
  log=ROOT/f'training/b4artists_ml/cache/finalization-fault-{variant}-v1.log';start=time.perf_counter()
  with log.open('w') as stream:
   proc=subprocess.run(['X:/5.1.0/bforartists.exe','--background','--factory-startup','--disable-autoexec','--python',str(HERE),'--','--host',variant],stdout=stream,stderr=subprocess.STDOUT,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='4'),timeout=180)
  path=OUT.parent/f'finalization-fault-{variant}-v1.json';assert path.exists();report=json.loads(path.read_text());assert report['passed'];rows.append(dict(variant=variant,report=report,host_exit=proc.returncode,seconds=time.perf_counter()-start,log=log.relative_to(ROOT).as_posix()));OUT.write_text(json.dumps(dict(passed=len(rows)==2,complete=len(rows)==2,rows=rows),indent=2)+'\n');print(json.dumps(dict(variant=variant,passed=True,host_exit=proc.returncode)),flush=True)
if __name__=='__main__':
 if '--host' in sys.argv:host(sys.argv[sys.argv.index('--host')+1])
 else:main()
