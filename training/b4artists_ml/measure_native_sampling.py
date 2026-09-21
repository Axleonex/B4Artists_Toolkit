"""Counterbalanced source-sampling comparison against archived v0.14.1."""
from pathlib import Path
import sys,os,json,time,subprocess,hashlib,traceback
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve();TAG='native-sampling-comparison-v1'
def host(label):
 import bpy,numpy as np
 sys.path[:0]=[str(ROOT),str(ROOT/'tests')]
 from test_b4artists_ml_flight import FlightTests,fixture,f,w,c,p,rs
 from b4artists_ml import native_flight as native,motion_layer as m
 FlightTests.setUpClass();ob,source,sig,modes=fixture(label,True);scene=bpy.context.scene
 w.finish_preview(ob,scene,False);max(ob.b4ml.anchors,key=lambda a:a.frame).frame=61;w.preview(ob,scene);ob.b4ml.flights.clear();scene.frame_set(1);f.add(ob,scene);scene.frame_set(31);p._update(ob);ob.b4ml.flight_backend='NATIVE'
 current=native.correction_steps;baseline=ROOT/'training/b4artists_ml/cache/native_flight_before_sampling.py';legacy={'__name__':'b4artists_ml._sampling_baseline','__package__':'b4artists_ml'};exec(compile(baseline.read_text(),str(baseline),'exec'),legacy)
 report=dict(rig=label,passed=False,runs=[],baseline_sha256=hashlib.sha256(baseline.read_bytes()).hexdigest(),current_sha256=hashlib.sha256((ROOT/'b4artists_ml/native_flight.py').read_bytes()).hexdigest());dest=ROOT/f'training/b4artists_ml/results/{TAG}-{label}.json';assert not dest.exists();expected=None
 def persist():dest.write_text(json.dumps(report,indent=2)+'\n')
 try:
  order=('baseline','current','current','baseline') if label=='boneforge' else ('current','baseline','baseline','current')
  for kind in order:
   native.correction_steps=legacy['correction_steps'] if kind=='baseline' else current
   ticks=[];start=time.perf_counter();f.start(ob,scene)
   while True:
    tick=time.perf_counter();done=f.step(ob);ticks.append((time.perf_counter()-tick)*1000)
    if done:break
   elapsed=time.perf_counter()-start;instance=m.validate(ob)
   curves=w.action_curves(instance.animation_data.action,getattr(instance.animation_data,'action_slot',None))
   channels=[(fc.data_path,fc.array_index,[(list(k.co),list(k.handle_left),list(k.handle_right),k.interpolation) for k in fc.keyframe_points]) for fc in curves]
   drivers=[(fc.data_path,fc.array_index,fc.driver.expression) for fc in instance.animation_data.drivers]
   signature=json.dumps([channels,drivers],sort_keys=True)
   if expected is None:expected=signature
   assert signature==expected,'Generated native channels differ from archived implementation'
   metrics=json.loads(ob.b4ml.flight_metrics)
   report['runs'].append(dict(kind=kind,seconds=elapsed,step_p95_ms=float(np.percentile(ticks,95)),step_max_ms=max(ticks),steps=len(ticks),max_com_error=metrics['max_after'],acceleration_error=max(v['acceleration_error_p95'] for v in metrics['intervals']),channel_sha256=hashlib.sha256(signature.encode()).hexdigest()))
   f.restore(ob,scene);persist();print(json.dumps(report['runs'][-1]),flush=True)
  w.finish_preview(ob,scene,False);assert ob.animation_data.action==source and c._action_signature(ob)==sig and rs.mode_values(ob)==modes
  report['source_restored']=True;report['exact_channel_parity']=True
  means={kind:float(np.mean([v['seconds'] for v in report['runs'] if v['kind']==kind])) for kind in ('baseline','current')};report['mean_seconds']=means;report['reduction_percent']=100*(1-means['current']/means['baseline']);report['passed']=True
 except BaseException:report['error']=traceback.format_exc()
 finally:native.correction_steps=current;persist()
def main():
 rows=[]
 for label in ('boneforge','rigify_default'):
  dest=ROOT/f'training/b4artists_ml/results/{TAG}-{label}.json';assert not dest.exists();start=time.perf_counter()
  with (ROOT/f'training/b4artists_ml/cache/{TAG}-{label}.log').open('w') as out:
   result=subprocess.run(['X:/5.1.0/bforartists.exe','--background','--factory-startup','--disable-autoexec','--python',str(HERE),'--',label],cwd=ROOT,stdout=out,stderr=subprocess.STDOUT,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='4'),timeout=420)
  record=json.loads(dest.read_text()) if dest.exists() else dict(passed=False,error='Missing host report');record.update(host_exit=result.returncode,elapsed_seconds=time.perf_counter()-start);rows.append(record)
  (ROOT/f'training/b4artists_ml/results/{TAG}-process.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps({k:v for k,v in record.items() if k!='runs'}),flush=True)
if __name__=='__main__':
 if '--' in sys.argv:host(sys.argv[-1])
 else:main()
