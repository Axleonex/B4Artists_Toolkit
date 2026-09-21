"""Actual Bforartists NumPy inference for research model pairs, no rig claim."""
from pathlib import Path
import sys,json,time,hashlib
import bpy,numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT/'training/b4artists_ml'),str(ROOT/'tests')]
from bvh_data import parse_bvh
from sequence_data import full_motion,known_window,coefficients_basis
from sequence_kinematics import forward
from kernel_motion import load_model
from context_gate import base_locals,predict_locals,gate_values
source=full_motion(parse_bvh((ROOT/'training/b4artists_ml/cache/07_01.bvh').read_text()));t=np.linspace(0,1,33);w=known_window(source,4,20,t,True);w['t']=t
observed={k:w[k] for k in ('x','t','baseline','basis_functions','offsets')};rows=[]
for label,base_path,gate_path in [('v6','results/kernel_motion_v3/selected.npz','results/context_gate_v6/selected_gate.npz'),('v8','results/motion_expansion_v8/expanded_base.npz','results/motion_expansion_v8/expanded_gate.npz')]:
 root=ROOT/'training/b4artists_ml';tick=time.perf_counter();base=load_model(root/base_path);gate=load_model(root/gate_path);load_ms=(time.perf_counter()-tick)*1000;times=[]
 for index in range(21):
  tick=time.perf_counter();baseline=base_locals(base,[observed]);local=predict_locals(gate,[observed],baseline)[0];positions,rotations,_=forward(local,observed['offsets'],source.parents);times.append((time.perf_counter()-tick)*1000)
 np.testing.assert_allclose(local[[0,-1]],observed['baseline'][[0,-1]],atol=1e-13)
 edges=np.linalg.norm(positions[:,1:]-positions[:,np.asarray(source.parents[1:])],axis=-1);error=float(np.max(np.abs(edges-np.linalg.norm(observed['offsets'][1:],axis=-1))));assert error<1e-12
 rows.append(dict(label=label,passed=True,load_ms=load_ms,first_inference_ms=times[0],warm_p95_ms=float(np.percentile(times[1:],95)),true_edge_error=error,gate_strengths=gate_values(gate,[observed]).tolist(),base_sha256=hashlib.sha256((root/base_path).read_bytes()).hexdigest(),gate_sha256=hashlib.sha256((root/gate_path).read_bytes()).hexdigest()))
record=dict(passed=True,host=bpy.app.version_string,numpy=np.__version__,rows=rows,scope='Research source-hierarchy inference only; no control-rig or mesh temporal application.');(ROOT/'training/b4artists_ml/results/context-gate-host-v1.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record),flush=True)
