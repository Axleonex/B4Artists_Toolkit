"""Measure native driver time/translation precision without rig fitting."""
from pathlib import Path
import bpy, numpy as np, json
scene=bpy.context.scene
rows={}
for kind in ('frame','scene_time','factored'):
 ob=bpy.data.objects.new(kind,None);scene.collection.objects.link(ob)
 fc=ob.driver_add('location',2);fc.keyframe_points.clear();d=fc.driver;d.type='SCRIPTED'
 if kind=='scene_time':
  for name,path in [('f','frame_current'),('s','frame_subframe')]:
   v=d.variables.new();v.name=name;v.type='SINGLE_PROP';v.targets[0].id_type='SCENE';v.targets[0].id=scene;v.targets[0].data_path=path
  t='(f+s+frame*0)'
 else:t='frame'
 d.expression=f'-4.905*100*((({t}-1)/240)**2-(({t}-1)/240))' if kind!='factored' else '-4.905/576*(frame-1)*(frame-241)'
 rows[kind]=ob
out={}
for phase in (0.,.137):
 frames=np.arange(1+phase,241+1e-7,.25);samples={k:[] for k in rows};truth=[];actual_frames=[]
 for frame in frames:
  scene.frame_set(int(frame),subframe=frame%1);bpy.context.view_layer.update()
  actual_frames.append(float(scene.frame_current_final))
  for k,ob in rows.items():samples[k].append(float(ob.evaluated_get(bpy.context.evaluated_depsgraph_get()).location.z))
  u=(frame-1)/240;truth.append(-490.5*(u*u-u))
 steps=np.diff(actual_frames)/24
 out[str(phase)]={k:dict(actual_time_acceleration_p95=float(np.percentile(np.abs(2*np.diff(np.diff(v)/steps)/(steps[1:]+steps[:-1])+9.81),95)),frame_time_max_error=float(np.max(np.abs(np.array(actual_frames)-frames))),max_position_error=float(np.max(np.abs(np.array(v)-truth))),acceleration_p95=float(np.percentile(np.abs(np.diff(v,n=2)/(.25/24)**2+9.81),95)),valid=rows[k].animation_data.drivers[0].driver.is_valid) for k,v in samples.items()}
path=Path(__file__).parent/'results/native-time-precision-v3.json';path.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out),flush=True)
