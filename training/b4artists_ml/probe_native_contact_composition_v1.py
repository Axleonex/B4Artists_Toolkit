from pathlib import Path
import sys,json,traceback,hashlib
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT),str(ROOT/'tests')]
import bpy,b4artists_ml
from b4artists_ml import flight as f,contacts as c,workflow as w,motion_layer as m
from test_b4artists_ml_momentum import MomentumHostTests
b4artists_ml.register();ob,*_=MomentumHostTests().fixture();scene=bpy.context.scene
ob.b4ml.flights[0].takeoff_blend=ob.b4ml.flights[0].landing_blend=2
scene.frame_set(1);item=c.capture(ob,scene);item.start=1;item.end=2;item.blend=0
f.solve(ob,scene);token=f._curve_token(ob)
try:
 c.solve(ob,scene);report=dict(contact_completed=True)
except Exception as exc:
 report=dict(contact_completed=False,error_type=type(exc).__name__,error=str(exc),traceback=traceback.format_exc(),source_candidate_unchanged=f._curve_token(ob)==token,native_layer_retained=m.find(ob) is not None)
report['runtime_sha256']={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'b4artists_ml').glob('*.py')}
(ROOT/'training/b4artists_ml/results/native-contact-composition-prefit-v1.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
