from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT),str(ROOT/'tests')]
import bpy,b4artists_ml
from test_b4artists_ml_flight import FlightTests,fixture,f,w
FlightTests.setUpClass();ob,*_=fixture();scene=bpy.context.scene;ob.b4ml.flight_backend='NATIVE'
f.start(ob,scene);f.step(ob);bone=ob.pose.bones['hips'];bone.location.x+=.125;expected=list(bone.location);error=None
try:f.step(ob)
except ValueError as exc:error=str(exc)
f.abort(ob)
report=dict(rejected=error is not None,error=error,edit_preserved=list(bone.location)==expected,expected=expected,actual=list(bone.location))
(ROOT/'training/b4artists_ml/results/native-external-pose-v1.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
