"""Saved native-layer body preview and edited target recovery in a disposable scene."""
from pathlib import Path
import sys,json,tempfile
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT),str(ROOT/'tests')]
import bpy,numpy as np,b4artists_ml
from mathutils import Vector
from b4artists_ml import workflow as w,motion_layer as m,body_preview as b,posing as p
from test_b4artists_ml_contacts import fixture
b4artists_ml.register();ob,source,sig,modes=fixture('boneforge',True);scene=bpy.context.scene;source_name=source.name
instance=m.begin(ob,scene);instance.location=(4,-2,3);p._update(ob);w.finish_preview(ob,scene,True);b.begin(ob,scene)
hand=ob.b4ml.body_targets['Hand L'].target;pelvis=ob.b4ml.body_targets['Pelvis'].target
hand.location+=(pelvis.location-hand.location).normalized()*.03;ob.b4ml.body_influence=.3;b.solve(ob)
record=json.loads(ob.b4ml.body_payload);metrics=record['metrics'];name=ob.name;scene_name=scene.name
path=ROOT/'training/b4artists_ml/cache/native-saved-body-v3.blend';bpy.ops.wm.save_as_mainfile(filepath=str(path));bpy.ops.wm.open_mainfile(filepath=str(path),use_scripts=False)
ob=bpy.data.objects[name];bpy.context.window.scene=bpy.data.scenes[scene_name];scene=bpy.context.scene
assert m.find(ob) is not None;b.finish(ob,scene,True)
assert len(ob.b4ml.anchors)==3 and not ob.b4ml.body_payload
w.restore_kept_source(ob,scene);assert ob.animation_data.action.name==source_name;assert m.find(ob) is None
report=dict(passed=True,metrics=metrics,edited_hand_target=True,saved_reload_keep=True,source_restored=True,retained_motion_results=len(m.results(ob)),scope='One transformed BoneForge fixture with translated native layer; no independent animator judgment.')
(ROOT/'training/b4artists_ml/results/native-saved-body-v3.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
