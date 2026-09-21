"""Transactional source-collection exclusion and original-rig editing feasibility."""
from pathlib import Path
import bpy,json,sys,numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'training/b4artists_ml'))
from probe_instance_flight_driver_direct_60_fine import sample
meta=json.loads((ROOT/'training/b4artists_ml/results/instance-flight-driver-direct-60-fine-feasibility-v1.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'training/b4artists_ml/cache/instance-flight-driver-direct-60-fine-feasibility-v1.blend'),use_scripts=False)
scene=bpy.data.scenes[meta['scene']];bpy.context.window.scene=scene
ob=bpy.data.objects[meta['source_rig']];mesh=bpy.data.objects[meta['mesh']];inst=bpy.data.objects[meta['instance']];group=inst.instance_collection
sources=(ob,mesh);memberships={o:tuple(o.users_collection) for o in sources};world=ob.matrix_world.copy();active=bpy.context.view_layer.objects.active
scene.frame_set(31);bpy.context.view_layer.update();before=sample(bpy,np,ob,mesh,inst,meta['bones']);changed=False;linked=False
report=dict(passed=False,scene_saved=False,source_collection_names={o.name:[c.name for c in v] for o,v in memberships.items()})
try:
 bpy.context.view_layer.objects.active=inst
 scene.collection.children.link(group);linked=True
 for o in sources:
  for collection in tuple(o.users_collection):
   if collection!=group:collection.objects.unlink(o)
 bpy.context.view_layer.update()
 for layer in scene.view_layers:layer.layer_collection.children[group.name].exclude=True
 bpy.context.view_layer.update();after=sample(bpy,np,ob,mesh,inst,meta['bones'])
 entries=[]
 for e in bpy.context.evaluated_depsgraph_get().object_instances:
  if e.object.original in sources:entries.append(dict(name=e.object.original.name,is_instance=e.is_instance,show_self=e.show_self))
 assert len(entries)==2 and all(e['is_instance'] and e['show_self'] for e in entries)
 assert not any(o.name in bpy.context.view_layer.objects for o in sources)
 difference=max(float(np.max(np.abs(before[k]-after[k]))) for k in ('bones','mesh'));assert difference==0
 # Mutate an animator control through direct RNA while its source is excluded.
 bone=ob.pose.bones['upper_arm_fk.L'];print('CONTROL_MODE '+bone.rotation_mode,flush=True);rotation=bone.rotation_quaternion.copy();bone.rotation_quaternion=(rotation @ __import__('mathutils').Quaternion((1,0,0),.1));changed=True
 ob.update_tag(refresh={'OBJECT'});bpy.context.view_layer.update();posed=sample(bpy,np,ob,mesh,inst,meta['bones'])
 pose_delta=float(np.max(np.abs(posed['mesh']-after['mesh'])));assert pose_delta>1e-5
 bone.rotation_quaternion=rotation;changed=False;ob.update_tag(refresh={'OBJECT'});bpy.context.view_layer.update();restored=sample(bpy,np,ob,mesh,inst,meta['bones'])
 restore_error=max(float(np.max(np.abs(restored[k]-after[k]))) for k in ('bones','mesh'));assert restore_error<2e-5
 report.update(excluded_sources_remain_evaluated=True,originals_absent_from_view_layer=True,instance_entries=entries,max_geometry_difference_on_rehousing=difference,native_control_edit_mesh_delta=pose_delta,pose_restore_error=restore_error,source_world_unchanged=ob.matrix_world==world)
finally:
 if changed:bone.rotation_quaternion=rotation
 if linked:
  for layer in scene.view_layers:layer.layer_collection.children[group.name].exclude=False
 for o,collections in memberships.items():
  for collection in collections:
   if collection not in o.users_collection:collection.objects.link(o)
  for collection in tuple(o.users_collection):
   if collection not in collections:collection.objects.unlink(o)
 if linked:scene.collection.children.unlink(group)
 bpy.context.view_layer.update();bpy.context.view_layer.objects.active=active
 assert all(set(o.users_collection)==set(v) for o,v in memberships.items())
 assert ob.matrix_world==world
 report['membership_recovery']=True
report['passed']=True
report['scope']='One disposable generated Rigify fixture; per-view-layer exclusion and direct control editing. Render output, persistent ownership/reload, animator selection, world-space helper adaptation, multi-character behavior and complete preview lifecycle still need product integration.'
(ROOT/'training/b4artists_ml/results/motion-layer-collection-ownership-v2.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
