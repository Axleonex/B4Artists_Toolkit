"""Counterbalanced finalization tick work against immutable 0.17.3; no profiler."""
from pathlib import Path
import os,sys,json,time,subprocess,zipfile,hashlib
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve();TAG='v1'
BASE=ROOT/f'training/b4artists_ml/cache/finalization-benchmark-base-{TAG}'
OUT=ROOT/f'training/b4artists_ml/results/finalization-benchmark-{TAG}.json'

def host(label,variant,number):
 import numpy as np,bpy
 sys.path[:0]=[os.environ['B4ML_PACKAGE'],str(ROOT/'tests')]
 import b4artists_ml
 from b4artists_ml import body_live as live,body_preview as body,workflow as w,rig_state as rs
 from test_b4artists_ml_body_live import LivePoseTests
 package=Path(b4artists_ml.__file__).resolve().parent;assert package.parent==Path(os.environ['B4ML_PACKAGE']).resolve()
 LivePoseTests.setUpClass();helper=LivePoseTests();ob,source,modes,action,keys=helper.fixture(label)
 clock=0.;live.start(ob,now=clock)
 def settle():
  nonlocal clock
  samples=[];statuses=[];started=time.perf_counter()
  for _ in range(3000):
   clock+=.02;begin=time.perf_counter();result=live.tick(ob,now=clock);samples.append((time.perf_counter()-begin)*1000);statuses.append(result)
   if result in ('ready','idle'):
    return dict(ticks=len(samples),seconds=time.perf_counter()-started,p95_ms=float(np.percentile(samples,95)),max_ms=max(samples),ready_tick_ms=samples[-1],first_active_tick_ms=next(ms for ms,status in zip(samples,statuses) if status=='solving'),samples=samples,statuses=statuses)
  raise AssertionError('Fit did not finish')
 first=settle();first_pose=w.raw_pose(ob);first_signature=body._read(ob)['signature']
 target=ob.b4ml.body_targets['Head'].target;target.location.y+=.002;bpy.context.view_layer.update();second=settle()
 second_pose=w.raw_pose(ob);record=body._read(ob);metrics={k:record['metrics'][k] for k in ('pin_error','length_error','orientation_error_radians','evaluations','iterations','solve_attempts')}
 assert metrics['pin_error']<2e-4 and metrics['length_error']<.002 and metrics['orientation_error_radians']<.001
 idle=[]
 for _ in range(100):
  clock+=.02;start=time.perf_counter();assert live.tick(ob,now=clock)=='idle';idle.append((time.perf_counter()-start)*1000)
 assert live._WATCHERS[ob.as_pointer()]['completed']==2 and not body._JOBS
 body.finish(ob,bpy.context.scene,True)
 assert w.raw_pose(ob)==source and rs.mode_values(ob)==modes and ob.animation_data.action==action and helper.keys(ob)==keys
 assert len(ob.b4ml.anchors)==1 and not live._WATCHERS and not body._JOBS
 result=dict(rig=label,variant=variant,number=number,first_fit=first,second_fit=second,idle=dict(count=100,p50_ms=float(np.median(idle)),p95_ms=float(np.percentile(idle,95)),max_ms=max(idle)),first_pose=first_pose,second_pose=second_pose,first_signature=first_signature,second_signature=record['signature'],metrics=metrics,source_preserved=True,runtime_sha256={p.relative_to(package.parent).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in package.glob('*.py')})
 path=ROOT/f'training/b4artists_ml/results/finalization-benchmark-{TAG}-{label}-{number}-{variant}.json';path.write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:result[k] for k in ('rig','variant','number','first_fit','second_fit','idle','metrics')}),flush=True)

def main():
 if OUT.exists() or BASE.exists():raise RuntimeError('Evidence already exists')
 archive=ROOT/'releases/b4artists_ml_v0.17.3.zip'
 assert hashlib.sha256(archive.read_bytes()).hexdigest()=='f9ae572c42f4f89d52f7d96b4190dbfa7928a50fd8010d728fa20ba2146e7aa4'
 BASE.mkdir()
 with zipfile.ZipFile(archive) as z:
  assert all(not Path(n).is_absolute() and '..' not in Path(n).parts for n in z.namelist());z.extractall(BASE)
 rows=[]
 for label in ('boneforge','rigify_default','rigify_basic','metarig_basic','metarig_default'):
  order=('base','current','current','base') if label in ('boneforge','rigify_default') else ('base','current')
  for number,variant in enumerate(order):
   path=ROOT/f'training/b4artists_ml/results/finalization-benchmark-{TAG}-{label}-{number}-{variant}.json';log=ROOT/f'training/b4artists_ml/cache/finalization-benchmark-{TAG}-{label}-{number}-{variant}.log'
   package=BASE if variant=='base' else ROOT;start=time.perf_counter()
   with log.open('w') as stream:
    proc=subprocess.run(['X:/5.1.0/bforartists.exe','--background','--factory-startup','--disable-autoexec','--python',str(HERE),'--','--host',label,variant,str(number)],stdout=stream,stderr=subprocess.STDOUT,env=dict(os.environ,B4ML_PACKAGE=str(package),PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='4'),timeout=180)
   row=json.loads(path.read_text()) if path.exists() else dict(rig=label,variant=variant,number=number,missing_result=True)
   row.update(host_exit=proc.returncode,wall_seconds=time.perf_counter()-start,log=str(log.relative_to(ROOT)),log_sha256=hashlib.sha256(log.read_bytes()).hexdigest());rows.append(row)
   OUT.write_text(json.dumps(dict(complete=False,rows=rows),indent=2)+'\n');print(json.dumps({k:row[k] for k in ('rig','variant','number','host_exit','wall_seconds')}),flush=True)
   if row.get('missing_result'):raise RuntimeError('Missing benchmark result')
 comparisons=[]
 for label in ('boneforge','rigify_default','rigify_basic','metarig_basic','metarig_default'):
  group=[r for r in rows if r['rig']==label];base=[r for r in group if r['variant']=='base'];current=[r for r in group if r['variant']=='current']
  parity=all(all(r[k]==base[0][k] for k in ('first_pose','second_pose','first_signature','second_signature','metrics')) for r in group)
  def avg(rows,field):return sum(r[fit][field] for r in rows for fit in ('first_fit','second_fit'))/(2*len(rows))
  first_ratio=avg(current,'first_active_tick_ms')/avg(base,'first_active_tick_ms')
  ready_ratio=avg(current,'ready_tick_ms')/avg(base,'ready_tick_ms')
  max_ratio=avg(current,'max_ms')/avg(base,'max_ms')
  total_ratio=avg(current,'seconds')/avg(base,'seconds')
  required=label=='rigify_default'
  comparisons.append(dict(rig=label,exact_pose_signature_metrics_parity=parity,first_active_tick_ratio=first_ratio,ready_tick_ratio=ready_ratio,ready_tick_ms=dict(baseline=avg(base,'ready_tick_ms'),current=avg(current,'ready_tick_ms')),max_tick_ratio=max_ratio,total_cpu_ratio=total_ratio,first_active_tick_ms=dict(baseline=avg(base,'first_active_tick_ms'),current=avg(current,'first_active_tick_ms')),max_tick_ms=dict(baseline=avg(base,'max_ms'),current=avg(current,'max_ms')),speed_gate_required=required,speed_gate_passed=ready_ratio<=.75 and max_ratio<=.80 and total_ratio<=1.10 if required else None,source_preserved=all(r['source_preserved'] for r in group)))
 passed=all(c['exact_pose_signature_metrics_parity'] and c['source_preserved'] and (not c['speed_gate_required'] or c['speed_gate_passed']) for c in comparisons)
 OUT.write_text(json.dumps(dict(complete=True,passed=passed,comparisons=comparisons,rows=rows,baseline_package_sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),scope='Counterbalanced archived/current/current/archived headless active-tick work measurements on BoneForge/default Rigify, and baseline/current on the remaining three profiles. A deterministic logical clock avoids input timing variation; real UI queue latency and human usability remain unverified. No profiler. Host shutdown crashes are recorded separately.'),indent=2)+'\n');print(json.dumps(dict(passed=passed,comparisons=comparisons)),flush=True)
if __name__=='__main__':
 if '--host' in sys.argv:
  i=sys.argv.index('--host');host(sys.argv[i+1],sys.argv[i+2],int(sys.argv[i+3]))
 else:main()
