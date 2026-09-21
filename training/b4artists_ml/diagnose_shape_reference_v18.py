"""Training-only shape/reference diagnosis; no validation, tuning or downloads."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','4')
from pathlib import Path
import json,hashlib,time
import numpy as np
from semantic_motion_data import load_windows
from shape_reference import reference
from boundary_trajectory import observation_scale,residual_basis
from motion_coverage import evaluate_predictions
ROOT=Path(__file__).resolve().parent

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    out=ROOT/'results/shape-reference-diagnostic-v18.json';assert not out.exists();start=time.perf_counter()
    protocol=json.loads((ROOT/'boundary_trajectory_protocol_v16.json').read_text());manifest_path=ROOT/'results/boundary_trajectory_v16/manifest.json';manifest=json.loads(manifest_path.read_text())
    rows=load_windows(ROOT,manifest,'train',protocol);assert len(rows)==2912
    predictions=dict(linear=[],hermite=[],shape_reference=[],shape_oracle_C0=[],shape_oracle_C1=[]);diagnostic=[]
    for w in rows:
        candidate=reference(w['observations'],w['t']);predictions['linear'].append(w['linear']);predictions['hermite'].append(w['hermite']);predictions['shape_reference'].append(candidate)
        scale=observation_scale(w['observations'])
        for mode in ['C0','C1']:
            b=residual_basis(w['t'],mode);coef=np.linalg.lstsq(b,w['target']-candidate,rcond=None)[0];coef[:,scale==0]=0.;predictions['shape_oracle_'+mode].append(candidate+b@coef)
        o=w['observations'];a,b=o.positions[:2];target=w['target'].reshape(-1,17,9)[...,:3];lo=np.minimum(a,b);hi=np.maximum(a,b)
        outside=np.maximum(np.maximum(lo-target,target-hi),0)
        linear=w['linear'].reshape(-1,17,9)[...,:3];hermite=w['hermite'].reshape(-1,17,9)[...,:3];shaped=candidate.reshape(-1,17,9)[...,:3]
        pe=lambda x:float(np.mean(np.linalg.norm(x-target,axis=-1)))
        diagnostic.append(dict(clip=w['clip'],gap=w['gap'],context=w['context'],start_source_frame=int(w['frame'][0]),end_source_frame=int(w['frame'][-1]),line_position=pe(linear),hermite_position=pe(hermite),shape_position=pe(shaped),hermite_excursion_max=float(np.max(np.linalg.norm(hermite-linear,axis=-1))),target_outside_component_fraction=float(np.mean(outside>1e-8)),target_outside_distance_mean=float(np.mean(np.linalg.norm(outside,axis=-1)))))
    reports={k:evaluate_predictions(rows,v) for k,v in predictions.items()}
    # Previously saved control equality verifies identical training windows/metrics.
    prior=json.loads((ROOT/'results/temporal-coverage-audit-v1.json').read_text())
    for name in ['linear','hermite']:assert reports[name]['aggregate']==prior['aggregates'][name]
    groups={}
    for name,report in reports.items():
        groups[name]={}
        for gap in protocol['gaps']:
            for context in protocol['contexts']:
                suffix=f'/gap{gap}/context{int(context)}';parts=[v for k,v in report['cohorts'].items() if k.endswith(suffix)]
                groups[name][suffix[1:]]={k:float(np.mean([r[k] for r in parts])) for k in ['position','rotation','velocity','acceleration']}
    context=[r for r in diagnostic if r['context']]
    result=dict(scope='Training-only raw reference diagnosis; no validation/confirmation motion loaded. Shape reference is procedural. Label-access oracles diagnose temporal capacity only and cannot be inference providers.',windows=len(rows),aggregates={k:v['aggregate'] for k,v in reports.items()},gap_context=groups,context_windows=len(context),context_shape_position_better_fraction=float(np.mean([r['shape_position']<r['hermite_position'] for r in context])),mean_target_outside_component_fraction=float(np.mean([r['target_outside_component_fraction'] for r in context])),worst_hermite_excess_training=sorted(context,key=lambda r:r['hermite_position']-r['line_position'],reverse=True)[:20],source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in [Path(__file__),ROOT/'shape_reference.py',ROOT/'semantic_motion_data.py',ROOT/'boundary_trajectory_protocol_v16.json',manifest_path]},full_goal_complete=False,seconds=time.perf_counter()-start)
    out.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['gap_context','source_sha256','worst_hermite_excess_training']}),flush=True)
if __name__=='__main__':main()
