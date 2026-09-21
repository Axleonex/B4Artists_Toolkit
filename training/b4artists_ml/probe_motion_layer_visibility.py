"""Inspect collection-instance source visibility and edit access in a disposable scene."""
from pathlib import Path
import bpy,json
ROOT=Path(__file__).resolve().parents[2]
meta=json.loads((ROOT/'training/b4artists_ml/results/instance-flight-driver-direct-60-fine-feasibility-v1.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'training/b4artists_ml/cache/instance-flight-driver-direct-60-fine-feasibility-v1.blend'),use_scripts=False)
scene=bpy.data.scenes[meta['scene']];bpy.context.window.scene=scene
ob=bpy.data.objects[meta['source_rig']];mesh=bpy.data.objects[meta['mesh']];inst=bpy.data.objects[meta['instance']]
scene.frame_set(31);bpy.context.view_layer.update()
def inspect(label):
 dep=bpy.context.evaluated_depsgraph_get();rows=[]
 for entry in dep.object_instances:
  if entry.object.original in (ob,mesh):rows.append(dict(object=entry.object.original.name,is_instance=entry.is_instance,show_self=entry.show_self,parent=entry.parent.original.name if entry.parent else None))
 return dict(label=label,original_hide=[ob.hide_get(),mesh.hide_get()],original_visible=[ob.visible_get(),mesh.visible_get()],source_in_view_layer=ob.name in bpy.context.view_layer.objects,entries=rows)
rows=[inspect('before')]
ob.hide_set(True);mesh.hide_set(True);bpy.context.view_layer.update();rows.append(inspect('source_hidden_per_view_layer'))
bpy.context.view_layer.objects.active=ob;ob.select_set(True)
try:
 result=bpy.ops.object.mode_set(mode='POSE');mode=dict(result=sorted(result),mode=ob.mode);bpy.ops.object.mode_set(mode='OBJECT')
except Exception as e:mode=dict(error=str(e))
ob.hide_set(False);mesh.hide_set(False);bpy.context.view_layer.update();rows.append(inspect('restored'))
report=dict(rows=rows,pose_mode_on_hidden_source=mode,source_world=list(ob.matrix_world.translation),instance_world=list(inst.matrix_world.translation),scene_saved=False)
(ROOT/'training/b4artists_ml/results/motion-layer-visibility-v1.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
