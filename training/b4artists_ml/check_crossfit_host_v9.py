"""Actual-host research-model inference; no rig or mesh performance claim."""
from pathlib import Path
import sys,json,time,hashlib
import bpy,numpy as np
ROOT=Path(__file__).resolve().parents[2];TR=ROOT/'training/b4artists_ml'
sys.path.insert(0,str(TR))
from bvh_data import parse_bvh
from sequence_data import full_motion,known_window
from sequence_kinematics import forward
from kernel_motion import load_model
from context_gate import base_locals
from crossfit_controller import predict,strengths
source=full_motion(parse_bvh((TR/'cache/07_01.bvh').read_text()))
t=np.linspace(0,1,33);w=known_window(source,4,20,t,True);w['t']=t
base_path=TR/'results/motion_expansion_v8/expanded_base.npz';gate_path=TR/'results/crossfit_controller_v9/selected_gate.npz'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
tick=time.perf_counter();base=load_model(base_path);gate=load_model(gate_path);load_ms=(time.perf_counter()-tick)*1000
assert str(gate['control_sha256'])==sha(base_path)
times=[]
for _ in range(21):
    tick=time.perf_counter();local=predict(gate,[w],base_locals(base,[w]))[0]
    positions,rotations,_=forward(local,w['offsets'],source.parents)
    times.append((time.perf_counter()-tick)*1000)
np.testing.assert_allclose(local[[0,-1]],w['baseline'][[0,-1]],atol=1e-13)
edges=np.linalg.norm(positions[:,1:]-positions[:,np.asarray(source.parents[1:])],axis=-1)
error=float(np.max(abs(edges-np.linalg.norm(w['offsets'][1:],axis=-1))));assert error<1e-12
report=dict(passed=True,scope='Research inference on source hierarchy only; no actual-rig temporal application or end-to-end latency.',host=bpy.app.version_string,numpy=np.__version__,load_ms=load_ms,first_inference_ms=times[0],warm_p95_ms=float(np.percentile(times[1:],95)),true_edge_error=error,blend_strengths=strengths(gate,[w]).tolist(),base_sha256=sha(base_path),gate_sha256=sha(gate_path))
(TR/'results/crossfit-host-v9.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
