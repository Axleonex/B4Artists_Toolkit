"""Native flight strength and multiple authored interval qualification."""
from pathlib import Path
import sys,json,traceback
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT),str(ROOT/'tests')]
import bpy
from test_b4artists_ml_flight import FlightTests,fixture,f,w,c,p,rs
from b4artists_ml import motion_layer as m
FlightTests.setUpClass();rows=[]
for label,strength,intervals in [('boneforge',0.,1),('boneforge',.5,1),('rigify_default',0.,1),('rigify_default',.5,1),('boneforge',1.,5),('boneforge',1.,16),('rigify_default',1.,16)]:
    ob,source,sig,modes=fixture(label,True);scene=bpy.context.scene
    if intervals>1:
        w.finish_preview(ob,scene,False);payload=ob.b4ml.anchors[0].payload;ob.b4ml.anchors.clear()
        for i in range(intervals+1):
            a=ob.b4ml.anchors.add();a.frame=1+i*10/intervals;a.payload=payload;a.name='Hop '+str(i)
        w.preview(ob,scene);ob.b4ml.flights.clear()
        for i in range(intervals):
            a=ob.b4ml.flights.add();a.start=1+i*10/intervals;a.end=1+(i+1)*10/intervals
    ob.b4ml.flight_backend='NATIVE'
    for row in ob.b4ml.flights:row.strength=strength
    before=c._action_signature(ob);counts=(set(bpy.data.actions.keys()),set(bpy.data.objects.keys()),set(bpy.data.collections.keys()));result=dict(rig=label,strength=strength,intervals=intervals,passed=False)
    try:
        metrics=f.solve(ob,scene);assert metrics['max_after']<2e-4
        assert c._action_signature(ob)==before
        result.update(passed=True,max_com_error=metrics['max_after'],acceleration_error=max(r['acceleration_error_p95'] for r in metrics['intervals']),drivers=len(m.find(ob).animation_data.drivers))
        f.restore(ob,scene)
    except Exception as exc:result['error']=str(exc)
    result['cleanup']=(set(bpy.data.actions.keys()),set(bpy.data.objects.keys()),set(bpy.data.collections.keys()))==counts and m.find(ob) is None
    w.finish_preview(ob,scene,False);result['source_preserved']=ob.animation_data.action==source and c._action_signature(ob)==sig and rs.mode_values(ob)==modes
    rows.append(result);print(json.dumps(result),flush=True)
(ROOT/'training/b4artists_ml/results/native-options-v2.json').write_text(json.dumps(rows,indent=2)+'\n')
