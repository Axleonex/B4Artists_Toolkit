"""Native rendered source isolation and fresh-process layer playback."""
from pathlib import Path
import sys,os,json,time,subprocess,hashlib
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve()
BLEND=ROOT/'training/b4artists_ml/cache/motion-layer-render-v2.blend'
META=ROOT/'training/b4artists_ml/results/motion-layer-render-v2.json'
def configure(scene):
 import bpy,math
 scene.render.engine='BLENDER_WORKBENCH';scene.render.resolution_x=128;scene.render.resolution_y=64;scene.render.resolution_percentage=100
 scene.display.shading.light='FLAT';scene.display.shading.color_type='SINGLE';scene.display.shading.single_color=(1,0,0);scene.display.shading.background_type='WORLD';scene.display.shading.show_shadows=False;scene.display.shading.show_cavity=False;scene.display.shading.show_specular_highlight=False
 scene.world=bpy.data.worlds.new('Black test world');scene.world.color=(0,0,0);scene.render.film_transparent=True
 cam=bpy.data.objects.new('Render acceptance camera',bpy.data.cameras.new('Render acceptance camera'));scene.collection.objects.link(cam);cam.location=(2,-8,.5);cam.rotation_euler=(math.pi/2,0,0);cam.data.type='ORTHO';cam.data.ortho_scale=8;scene.camera=cam
 scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA'
def render(scene,label):
 import bpy,numpy as np
 path=ROOT/f'training/b4artists_ml/cache/motion-layer-render-{label}-v2.png';scene.render.filepath=str(path);bpy.ops.render.render(write_still=True)
 image=bpy.data.images.load(str(path),check_existing=False);pixels=np.array(image.pixels[:]).reshape((64,128,4));bpy.data.images.remove(image)
 mask=pixels[:,:,3]>.5
 return dict(left_pixels=int(mask[:,:64].sum()),right_pixels=int(mask[:,64:].sum()),path=str(path.relative_to(ROOT)),sha256=hashlib.sha256(path.read_bytes()).hexdigest())
def setup():
 import bpy,numpy as np
 sys.path[:0]=[str(ROOT),str(ROOT/'tests')]
 from test_b4artists_ml_motion_layer import fixture,geometry
 from b4artists_ml import motion_layer as m
 owner,mesh,scene,*_=fixture();configure(scene);before=render(scene,'source')
 instance=m.begin(owner,scene);instance.location=(4,0,0);instance.keyframe_insert('location',frame=1);instance.keyframe_insert('location',frame=11);m.keep(owner)
 bpy.context.view_layer.update();after=render(scene,'instance');assert before['left_pixels']>20 and before['right_pixels']==0 and after['left_pixels']==0 and after['right_pixels']>20
 scene.frame_set(6);bpy.context.view_layer.update();expected=geometry(mesh,instance).tolist()
 report=dict(passed=True,source_render=before,instance_render=after,owner=owner.name,mesh=mesh.name,scene=scene.name,instance=instance.name,expected_geometry=expected,module_sha256=hashlib.sha256((ROOT/'b4artists_ml/motion_layer.py').read_bytes()).hexdigest())
 META.write_text(json.dumps(report,indent=2)+'\n');bpy.ops.wm.save_as_mainfile(filepath=str(BLEND));print(json.dumps(report),flush=True)
def verify():
 import bpy,numpy as np
 meta=json.loads(META.read_text());bpy.ops.wm.open_mainfile(filepath=str(BLEND),use_scripts=False);scene=bpy.data.scenes[meta['scene']];bpy.context.window.scene=scene
 owner=bpy.data.objects[meta['owner']];mesh=bpy.data.objects[meta['mesh']];instance=bpy.data.objects[meta['instance']];assert 'b4artists_ml' not in sys.modules
 scene.frame_set(6);bpy.context.view_layer.update();got=None
 for entry in bpy.context.evaluated_depsgraph_get().object_instances:
  if entry.is_instance and entry.parent and entry.parent.original==instance and entry.object.original==mesh:got=np.array([entry.matrix_world@v.co for v in entry.object.data.vertices])
 np.testing.assert_array_equal(got,np.array(meta['expected_geometry']));after=render(scene,'reloaded');assert after['left_pixels']==0 and after['right_pixels']>20
 result=dict(passed=True,addon_loaded=False,max_reload_difference=0.,render=after,blend_sha256=hashlib.sha256(BLEND.read_bytes()).hexdigest(),scope='Native rendering and saved geometry for the internal ownership component; flight and pose UI are not integrated yet.')
 (ROOT/'training/b4artists_ml/results/motion-layer-native-render-reload-v2.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
def main():
 if META.exists() or BLEND.exists():raise RuntimeError('Evidence exists')
 rows=[]
 for mode in ('setup','verify'):
  started=time.perf_counter()
  with (ROOT/f'training/b4artists_ml/cache/motion-layer-render-{mode}-v2.log').open('w') as f:
   p=subprocess.run(['X:/5.1.0/bforartists.exe','--background','--factory-startup','--disable-autoexec','--python',str(HERE),'--','--'+mode],stdout=f,stderr=subprocess.STDOUT,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='4'),timeout=120)
  rows.append(dict(stage=mode,exit_code=p.returncode,elapsed_seconds=time.perf_counter()-started));print(json.dumps(rows[-1]),flush=True)
  if not META.exists():break
 (ROOT/'training/b4artists_ml/results/motion-layer-render-process-v2.json').write_text(json.dumps(rows,indent=2)+'\n')
if __name__=='__main__':
 if '--setup' in sys.argv:setup()
 elif '--verify' in sys.argv:verify()
 else:main()
