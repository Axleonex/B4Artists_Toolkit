from pathlib import Path
import sys,json
import bpy,numpy as np
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT));from b4artists_ml import support,flight_math as fm
meta=json.loads((ROOT/'training/b4artists_ml/results/instance-flight-driver-fine-feasibility-v1.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'training/b4artists_ml/cache/instance-flight-driver-fine-feasibility-v1.blend'))
scene=bpy.data.scenes[meta['scene']];bpy.context.window.scene=scene;ob=bpy.data.objects[meta['source_rig']];inst=bpy.data.objects[meta['instance']]
# Read the saved name mapping instead of requiring registered add-on properties.
names=meta['bones']; mapped=[ob.pose.bones[n] for n in names]
def at(f):scene.frame_set(int(f),subframe=float(f-int(f)));bpy.context.view_layer.update()
ad=inst.animation_data;curves=ad.action.layers[0].strips[0].channelbag(ad.action_slot).fcurves
rows=[]
for f in [1.,15.25,15.5,31.,121.,220.75,241.]:
 at(f);ev=inst.evaluated_get(bpy.context.evaluated_depsgraph_get());u=(f-1)/240
 props=[float(inst['b4ml_residual_'+str(i)]) for i in range(3)]
 evaluated_props=[float(ev['b4ml_residual_'+str(i)]) for i in range(3)]
 curve_values=[float(curves.find('["b4ml_residual_'+str(i)+'"]').evaluate(f)) for i in range(3)]
 expected=np.array(props)+.5*np.array(scene.gravity)*100*(u*u-u)
 rows.append(dict(frame=f,props=props,evaluated_props=evaluated_props,curve_values=curve_values,location=list(inst.location),evaluated_location=list(ev.location),driver_difference=(np.array(ev.location)-expected).tolist(),driver_fcurves=[dict(modifiers=[m.type for m in fc.modifiers],keys=[list(k.co) for k in fc.keyframe_points],valid=fc.driver.is_valid) for fc in ad.drivers]))
(ROOT/'training/b4artists_ml/results/driver-residual-binding-v1.json').write_text(json.dumps(rows,indent=2)+'\n')
