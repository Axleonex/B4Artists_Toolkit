"""Observe native key insertion and exact contact-validation failure locals."""
from pathlib import Path
import sys,json,traceback
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT),str(ROOT/'tests'),str(ROOT/'training/b4artists_ml')]
import bpy
import b4artists_ml
from b4artists_ml import contacts as c,workflow as w
from test_b4artists_ml_contacts import fixture
import temporal_cooperative_v1 as cooperative
import semantic_predictor
out=ROOT/'training/b4artists_ml/results/contact-key-insertion-diagnosis-v1.json';assert not out.exists();result={}
a=bpy.data.actions.new('Local insertion probe');slot=a.slots.new('OBJECT','Probe');layer=a.layers.new('Probe');strip=layer.strips.new(type='KEYFRAME');bag=strip.channelbag(slot,ensure=True);fc=bag.fcurves.new('location',index=0)
for f,v in [(7.625,1.),(7.62890625,2.)]:fc.keyframe_points.insert(f,v,options={'FAST'})
fc.update();result['insert_probe']=[list(k.co) for k in fc.keyframe_points]
b4artists_ml.register();cooperative.register();ob,source,signature,modes=fixture('boneforge');scene=bpy.context.scene;w.finish_preview(ob,scene,False);third=ob.b4ml.anchors.add();third.frame=21.;third.payload=ob.b4ml.anchors[0].payload
for item in ob.b4ml.contacts:item.end=21.
samples,_=cooperative.generate_samples(ob,semantic_predictor.provider(dict(kind='baseline',baseline='hermite')),context=True);w.preview(ob,scene,pose_samples=samples)
observations=[]
def trace(frame,event,arg):
    if event=='exception' and frame.f_code.co_name=='correction_steps' and Path(frame.f_code.co_filename).resolve()==Path(c.__file__).resolve():
        exc=arg[1]
        if isinstance(exc,ValueError) and str(exc).startswith('Evaluated contact failed'):
            local=frame.f_locals;candidate=local.get('candidate');f=local.get('frame');record=dict(error=str(exc),frame=f,is_key=f in local.get('key_frames',set()),refinements=len(local.get('_refinements',())),curve_samples=[])
            if candidate and f is not None:
                for (path,index),points in local.get('samples',{}).items():
                    curve=w.action_curves(candidate,getattr(ob.animation_data,'action_slot',None)).find(path,index=index)
                    expected=[(x,y) for x,y in points if abs(x-f)<.02];actual=[list(k.co) for k in curve.keyframe_points if abs(k.co.x-f)<.02]
                    if expected:record['curve_samples'].append(dict(path=path,index=index,expected=expected,actual=actual))
            observations.append(record)
    return trace
sys.settrace(trace)
try:c.solve(ob,scene);result['contact_succeeded']=True
except Exception as exc:result['contact_succeeded']=False;result['error']=str(exc)
finally:sys.settrace(None)
result['failures']=observations;result['complete']=True;out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(insert_probe=result['insert_probe'],contact_succeeded=result['contact_succeeded'],failures=len(observations))),flush=True)
