from pathlib import Path
import json
import bpy
out=Path.cwd()/'training/b4artists_ml/results/contact-key-api-probe-v1.json';assert not out.exists();rows=[]
for mode in ['insert_update','add_update','add_sort_handles']:
 a=bpy.data.actions.new(mode);slot=a.slots.new('OBJECT','Probe');layer=a.layers.new('Probe');strip=layer.strips.new(type='KEYFRAME');bag=strip.channelbag(slot,ensure=True);fc=bag.fcurves.new('location',index=0)
 pairs=[(7.625,1.),(7.62890625,2.)]
 if mode.startswith('insert'):
  for f,v in pairs:fc.keyframe_points.insert(f,v,options={'FAST'}).interpolation='LINEAR'
 else:
  fc.keyframe_points.add(2)
  for k,pair in zip(fc.keyframe_points,pairs):k.co=pair;k.interpolation='LINEAR'
 before=[list(k.co) for k in fc.keyframe_points]
 if mode.endswith('update'):fc.update()
 else:fc.keyframe_points.sort();fc.keyframe_points.handles_recalc()
 rows.append(dict(mode=mode,before=before,after=[list(k.co) for k in fc.keyframe_points],evaluated=[fc.evaluate(t) for t in [7.625,7.626953125,7.62890625]]))
out.write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(rows),flush=True)
