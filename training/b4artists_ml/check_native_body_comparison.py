from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT),str(ROOT/'tests')]
import bpy,b4artists_ml
from b4artists_ml import workflow as w,motion_layer as m,body_preview as b,posing as p,body_solver as solver
from test_b4artists_ml_contacts import fixture
b4artists_ml.register();rows=[]
original_steps=solver.Session.solve_steps
budget=50
def controlled(self,*args,**kwargs):
    kwargs["iterations"]=budget
    return original_steps(self,*args,**kwargs)
solver.Session.solve_steps=controlled
for native,budget in ((False,50),(True,50),(False,100),(True,100)):
    influence=.3
    ob,*_=fixture('boneforge',True);scene=bpy.context.scene
    if native:instance=m.begin(ob,scene);instance.location=(4,-2,3);p._update(ob)
    w.finish_preview(ob,scene,True);b.begin(ob,scene);ob.b4ml.body_influence=influence
    hand=ob.b4ml.body_targets["Hand L"].target;pelvis=ob.b4ml.body_targets["Pelvis"].target
    hand.location+=(pelvis.location-hand.location).normalized()*.03
    try:
        b.solve(ob);rows.append(dict(native=native,influence=influence,iteration_budget=budget,passed=True,metrics=json.loads(ob.b4ml.body_payload)['metrics']))
    except Exception as exc:rows.append(dict(native=native,influence=influence,iteration_budget=budget,passed=False,error=str(exc)))
    b.finish(ob,scene,False)
(ROOT/'training/b4artists_ml/results/native-body-comparison-v3.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(rows),flush=True)
