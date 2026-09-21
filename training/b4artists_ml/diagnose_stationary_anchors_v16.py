"""Controlled unchanged-anchor diagnostic; no trained-model modification."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','4')
from pathlib import Path
from dataclasses import replace
import json,hashlib
import numpy as np
import semantic_predictor as old
import boundary_trajectory as neural
from semantic_projection import load_windows
from motion_coverage import rotation_log
from temporal_data import rotation_matrix
ROOT=Path(__file__).resolve().parent

def main():
    folder=ROOT/'results/boundary_trajectory_v16';protocol=json.loads((folder/'protocol.json').read_text());manifest=json.loads((folder/'manifest.json').read_text());train,_=load_windows(ROOT,manifest,'train',protocol)
    sample={}
    for w in train:sample.setdefault(w['clip'],w['observations'])
    models={}
    for version,loader,name in [('v16',neural,'boundary_trajectory_v16')]:
        path=ROOT/'results'/name/'best_learned.npz';models[version]=(loader,loader.load(path),hashlib.sha256(path.read_bytes()).hexdigest())
    rows=[]
    for clip,base in sample.items():
        for gap in protocol['gaps']:
            for context in [False,True]:
                o=replace(base,positions=np.repeat(base.positions[:1],4,axis=0),rotations=np.repeat(base.rotations[:1],4,axis=0),duration=gap*base.dt,context=context)
                t=np.linspace(0,1,gap+1)
                for version,(api,m,digest) in models.items():
                    packed=api.predict_packed(m,o,t);np.testing.assert_array_equal(packed,neural.reference(o,t,m['baseline_kind']));output=packed.reshape(-1,17,9);rot,bad=rotation_matrix(output[...,3:]);assert not bad.any()
                    p=float(np.max(np.linalg.norm(output[...,:3]-o.positions[0],axis=-1)))
                    angle=float(np.max(np.linalg.norm(rotation_log(np.swapaxes(o.rotations[0],-1,-2)@rot),axis=-1)))
                    rows.append(dict(clip=clip,gap=gap,context=context,model=version,position_drift=p,rotation_drift_radians=angle))
    summary={}
    for version in models:
        r=[v for v in rows if v['model']==version];summary[version]=dict(cases=len(r),position_max=max(v['position_drift'] for v in r),position_median=float(np.median([v['position_drift'] for v in r])),rotation_max=max(v['rotation_drift_radians'] for v in r))
    report=dict(scope='Controlled stationary anchors/context built from one training pose per clip; diagnostic output before physical projection. No hidden motion labels, no fitting, no validation or confirmation, no gate/model changes.',rows=rows,summary=summary,model_sha256={k:v[2] for k,v in models.items()},source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),interpretation='Every prediction equals its stationary procedural baseline exactly; maximum reported position/rotation deviation includes floating-point baseline reconstruction. This does not establish general motion quality.')
    (ROOT/'results/stationary-anchors-v16.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n');print(json.dumps(summary),flush=True)
if __name__=='__main__':main()
