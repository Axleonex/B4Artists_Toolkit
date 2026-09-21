"""Shifted-time native playback acceptance with script autoexecution disabled."""
from pathlib import Path
import sys,os,json,subprocess,time,hashlib
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve()
PREFIX='instance-flight-driver-direct-60-fine'
BLEND=ROOT/f'training/b4artists_ml/cache/{PREFIX}-feasibility-v1.blend'
META=ROOT/f'training/b4artists_ml/results/{PREFIX}-feasibility-v1.json'
PARAMS=ROOT/'training/b4artists_ml/results/native-flight-playback-params-v1.json'
OUT=ROOT/'training/b4artists_ml/results/native-flight-playback-validation-v1.json'
def prepare():
 import bpy,numpy as np
 sys.path.insert(0,str(ROOT));import b4artists_ml
 b4artists_ml.register();from b4artists_ml import support,flight,workflow
 meta=json.loads(META.read_text());bpy.ops.wm.open_mainfile(filepath=str(BLEND),use_scripts=False)
 ob=bpy.data.objects[meta['source_rig']];scene=bpy.data.scenes[meta['scene']];bpy.context.window.scene=scene
 binding=support.body_solver.mapping(ob,writable=False);weights=[x.weight for x in ob.b4ml.mass_segments];fractions=[x.fraction for x in ob.b4ml.mass_segments]
 values=[]
 for frame in (1,61):
  scene.frame_set(frame);bpy.context.view_layer.update();_,_,a,b=support.sample(ob,bpy.context.evaluated_depsgraph_get());values.append(flight.center_of_mass(a,b,weights,fractions)[0].tolist())
 scale=sum(float(np.linalg.norm(b[i]-a[i])) for i in range(3))
 params=dict(names=binding['names'],segments=support.SEGMENTS,weights=weights,fractions=fractions,endpoints=values,scale=scale,gravity=list(scene.gravity),fps=scene.render.fps/scene.render.fps_base,blend_sha256=hashlib.sha256(BLEND.read_bytes()).hexdigest())
 PARAMS.write_text(json.dumps(params,indent=2)+'\n')
def verify():
 import bpy,numpy as np
 sys.path.insert(0,str(ROOT/'training/b4artists_ml'))
 from probe_instance_flight_driver_direct_60_fine import sample
 meta=json.loads(META.read_text());params=json.loads(PARAMS.read_text())
 assert 'b4artists_ml' not in sys.modules
 bpy.context.preferences.filepaths.use_scripts_auto_execute=False
 bpy.ops.wm.open_mainfile(filepath=str(BLEND),use_scripts=False);scene=bpy.data.scenes[meta['scene']];bpy.context.window.scene=scene
 ob=bpy.data.objects[meta['source_rig']];mesh=bpy.data.objects[meta['mesh']];inst=bpy.data.objects[meta['instance']]
 simple=[fc.driver.is_simple_expression for fc in inst.animation_data.drivers];assert len(simple)==3 and all(simple)
 lookup={name:i for i,name in enumerate(meta['bones'])};mapped=[lookup[n] for n in params['names']]
 weights=np.array(params['weights']);weights=weights/weights.sum();fractions=np.array(params['fractions']);start,end=np.array(params['endpoints']);g=np.array(params['gravity']);duration=60/params['fps']
 def at(f):
  scene.frame_set(int(f),subframe=float(f-int(f)));bpy.context.view_layer.update();got=sample(bpy,np,ob,mesh,inst,meta['bones'])
  heads=got['heads'][mapped];tails=got['tails'][mapped]
  a=np.array([heads[i] for _,i,j,w in params['segments']]);b=np.array([heads[j] if j is not None else tails[i] for _,i,j,w in params['segments']]);com=np.sum((a+(b-a)*fractions[:,None])*weights[:,None],axis=0)
  u=(f-1)/60;target=start*(1-u)+end*u+.5*g*duration**2*(u*u-u)
  return got,com,float(np.linalg.norm(com-target))/params['scale']
 phases=[]
 for offset in (0.,.137):
  frames=np.arange(1.+offset,61.+1e-6,.25);positions=[];errors=[]
  for f in frames:
   got,com,error=at(float(f));positions.append(com);errors.append(error)
  acc=np.linalg.norm(np.diff(np.array(positions),n=2,axis=0)/(.25/params['fps'])**2-g,axis=1)
  row=dict(offset_frames=offset,samples=len(frames),max_com_error=max(errors),acceleration_error_p95=float(np.percentile(acc,95)))
  row['passed']=row['max_com_error']<=2e-4 and row['acceleration_error_p95']<.1;phases.append(row)
 # Seek out of order to ensure evaluation is not relying on previous sample state.
 order=[50.25,1.,31.,7.5,61.,20.+1/3];recovery=[]
 for f in order:
  a,_,_=at(f);at(2.);b,_,_=at(f);difference=max(float(np.max(np.abs(a[k]-b[k]))) for k in ('bones','mesh'));assert difference==0;recovery.append(difference)
 replay=[]
 for row in meta['playback']:
  got,_,_=at(row['frame']);replay.append(max(float(np.max(np.abs(got[k]-np.array(row[k])))) for k in ('bones','mesh')))
 passed=all(x['passed'] for x in phases) and max(replay)==0 and 'b4artists_ml' not in sys.modules
 result=dict(passed=passed,phases=phases,random_seek_max_difference=max(recovery),saved_playback_max_difference=max(replay),simple_expressions=simple,autoexec_enabled=bpy.context.preferences.filepaths.use_scripts_auto_execute,addon_loaded='b4artists_ml' in sys.modules,blend_sha256=hashlib.sha256(BLEND.read_bytes()).hexdigest(),scope='One transformed default Rigify with synthetic mesh; native saved playback, shifted timing and stateless seeking. Does not certify production layer ownership, posing/contact integration, keep/discard or export.')
 assert not result['autoexec_enabled'];OUT.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
def main():
 if PARAMS.exists() or OUT.exists():raise RuntimeError('Evidence exists')
 rows=[]
 for mode in ('prepare','verify'):
  started=time.perf_counter()
  with (ROOT/f'training/b4artists_ml/cache/native-flight-playback-{mode}-v1.log').open('w') as f:
   p=subprocess.run(['X:/5.1.0/bforartists.exe','--background','--factory-startup','--disable-autoexec','--python',str(HERE),'--','--'+mode],stdout=f,stderr=subprocess.STDOUT,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='4'),timeout=90)
  rows.append(dict(stage=mode,host_exit=p.returncode,elapsed_seconds=time.perf_counter()-started));print(json.dumps(rows[-1]),flush=True)
  if not PARAMS.exists():break
 (OUT.parent/'native-flight-playback-process-v1.json').write_text(json.dumps(rows,indent=2)+'\n')
if __name__=='__main__':
 if '--prepare' in sys.argv:prepare()
 elif '--verify' in sys.argv:verify()
 else:main()
