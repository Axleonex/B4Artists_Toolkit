"""Saved actual native backend: default Rigify, bound surface and addon-free playback."""
from pathlib import Path
import sys,os,json,subprocess,time,hashlib
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve();TAG=os.environ.get('B4ML_PLAYBACK_TAG','native-flight-playback-v1')

def sample(ob,mesh,instance):
 import bpy,numpy as np
 result={}
 for e in bpy.context.evaluated_depsgraph_get().object_instances:
  if not e.is_instance or not e.parent or e.parent.original!=instance:continue
  if e.object.original==ob:result['bones']=np.array([e.matrix_world@b.matrix for b in e.object.pose.bones]).tolist()
  if e.object.original==mesh:result['vertices']=[list(e.matrix_world@v.co) for v in e.object.data.vertices]
 assert set(result)=={'bones','vertices'}
 return result

def setup():
 import bpy,numpy as np
 from mathutils import Vector
 sys.path[:0]=[os.environ.get('B4ML_PACKAGE',str(ROOT)),str(ROOT/'tests')]
 import b4artists_ml
 from test_b4artists_ml_flight import FlightTests,fixture,w,f,p,support
 from b4artists_ml import motion_layer as m
 FlightTests.setUpClass();ob,source,sig,modes=fixture('rigify_default',True);scene=bpy.context.scene
 w.finish_preview(ob,scene,False);max(ob.b4ml.anchors,key=lambda v:v.frame).frame=61;w.preview(ob,scene);ob.b4ml.contacts.clear();ob.b4ml.flights.clear();scene.frame_set(1);f.add(ob,scene);scene.frame_set(31);ob.b4ml.flight_backend='NATIVE'
 names=[b.name for b in ob.data.bones if b.use_deform];verts=[]
 for name in names:
  point=ob.data.bones[name].head_local;verts.extend([point,point+Vector((.01,0,0)),point+Vector((0,.01,0))])
 data=bpy.data.meshes.new('Native playback skin');data.from_pydata(verts,[],[tuple(range(i,i+3)) for i in range(0,len(verts),3)]);mesh=bpy.data.objects.new('Native playback skin',data);scene.collection.objects.link(mesh);mesh.matrix_world=ob.matrix_world.copy();mesh.modifiers.new('Armature','ARMATURE').object=ob
 for i,name in enumerate(names):mesh.vertex_groups.new(name=name).add(list(range(i*3,i*3+3)),1.,'REPLACE')
 metrics=f.solve(ob,scene);instance=m.validate(ob);w.finish_preview(ob,scene,True)
 samples={}
 for frame in (1.,7.137,21.25,31.,50.713,61.):
  scene.frame_set(int(frame),subframe=frame%1);p._update(ob);samples[str(frame)]=sample(ob,mesh,instance)
 report=dict(passed=True,metrics=metrics,samples=samples,owner=ob.name,mesh=mesh.name,instance=instance.name,scene=scene.name,weighted_bones=len(names),module_sha256=hashlib.sha256((ROOT/'b4artists_ml/native_flight.py').read_bytes()).hexdigest())
 bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/f'training/b4artists_ml/cache/{TAG}.blend'))
 (ROOT/f'training/b4artists_ml/results/{TAG}-setup.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='samples'}),flush=True)

def verify():
 import bpy,numpy as np
 meta=json.loads((ROOT/f'training/b4artists_ml/results/{TAG}-setup.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(ROOT/f'training/b4artists_ml/cache/{TAG}.blend'),use_scripts=False)
 assert 'b4artists_ml' not in sys.modules
 bpy.context.window.scene=bpy.data.scenes[meta['scene']];scene=bpy.context.scene;ob=bpy.data.objects[meta['owner']];mesh=bpy.data.objects[meta['mesh']];instance=bpy.data.objects[meta['instance']];errors=[]
 for frame,expected in reversed(list(meta['samples'].items())):
  frame=float(frame);scene.frame_set(int(frame),subframe=frame%1);bpy.context.view_layer.update();got=sample(ob,mesh,instance)
  errors.append(max(float(np.max(np.abs(np.asarray(got[k])-np.asarray(expected[k])))) for k in got))
 assert max(errors)<2e-5;assert 'b4artists_ml' not in sys.modules
 report=dict(passed=True,addon_loaded=False,autoexec_enabled=bpy.context.preferences.filepaths.use_scripts_auto_execute,max_reload_error=max(errors),samples=len(errors),blend_sha256=hashlib.sha256((ROOT/f'training/b4artists_ml/cache/{TAG}.blend').read_bytes()).hexdigest())
 (ROOT/f'training/b4artists_ml/results/{TAG}-verify.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)

if __name__=='__main__':
 if '--' in sys.argv:(setup if sys.argv[-1]=='setup' else verify)()
 else:
  rows=[]
  for mode in ('setup','verify'):
   start=time.perf_counter()
   with (ROOT/f'training/b4artists_ml/cache/{TAG}-{mode}.log').open('w') as log:
    p=subprocess.run(['X:/5.1.0/bforartists.exe','--background','--factory-startup','--disable-autoexec','--python',str(HERE),'--',mode],stdout=log,stderr=subprocess.STDOUT,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='4'),timeout=240)
   rows.append(dict(stage=mode,exit_code=p.returncode,seconds=time.perf_counter()-start));print(rows[-1],flush=True)
   (ROOT/f'training/b4artists_ml/results/{TAG}-process.json').write_text(json.dumps(rows,indent=2)+'\n')
   if not (ROOT/f'training/b4artists_ml/results/{TAG}-{mode}.json').exists():break
