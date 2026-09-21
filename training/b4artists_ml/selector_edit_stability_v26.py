"""Observed anchor edits: raw proposal sensitivity, not projected quality."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','4')
from pathlib import Path
from dataclasses import replace
import json,hashlib,time
import numpy as np
import projected_selector_v26 as selector
import projected_pool_v26 as pool
from semantic_projection import load_windows
ROOT=Path(__file__).resolve().parent

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def edited(observed,axis,delta):
    if type(axis)!=int or not 0<=axis<3 or not np.isfinite(delta):raise ValueError('Finite rigid endpoint edit required')
    # Move every joint of the second authored pose together. Its joint lengths,
    # orientations and the other known poses stay unchanged. No target is read.
    positions=observed.positions.copy();positions[1,:,axis]+=delta
    return replace(observed,positions=positions)

def distances(a,b):
    a=a.reshape(-1,17,9);b=b.reshape(-1,17,9)
    p=np.linalg.norm(a[...,:3]-b[...,:3],axis=-1)
    from temporal_data import rotation_matrix
    ra,ba=rotation_matrix(a[...,3:]);rb,bb=rotation_matrix(b[...,3:])
    assert not ba.any() and not bb.any()
    angle=np.arccos(np.clip((np.trace(np.swapaxes(ra,-1,-2)@rb,axis1=-2,axis2=-1)-1)/2,-1,1))
    return dict(position_mean=float(p.mean()),position_max=float(p.max()),rotation_mean_radians=float(angle.mean()),rotation_max_radians=float(angle.max()))

def main():
    started=time.perf_counter();plan=read(ROOT/'selector_edit_stability_plan_v26.json')
    out=ROOT/'results/projected-selector-edit-stability-v26.json';assert not out.exists()
    folder=ROOT/'results/projected_selector_v26';complete=read(folder/'complete.json');report=read(folder/'report.json')
    assert complete['complete'] and sha(folder/'report.json')==complete['report_sha256']
    digest=sha(folder/'best_learned.npz');assert digest==report['selection']['best_learned_sha256']
    for n,h in report['source_sha256'].items():assert sha(ROOT/n)==h,n
    assert sha(Path(__file__))==plan['source_sha256']
    model=selector.load(folder/'best_learned.npz');parent=selector.parent_model(model)
    windows,_=load_windows(ROOT,read(ROOT/'temporal_training_manifest_v19.json'),'validation',report['protocol'])
    representatives={}
    for w in windows:representatives.setdefault((w['clip'],w['gap'],bool(w['context'])),w)
    assert len(representatives)==96 and len(windows)==768
    rows=[];query=np.linspace(0,1,9)
    for key,w in representatives.items():
        o=w['observations'];before=o.positions.copy();choice,prob=selector.selection(model,o)
        original=selector.predict_packed(model,o,query)[1:-1]
        for size in plan['edit_sizes_body_reference']:
            for axis in range(3):
                for sign in (-1,1):
                    changed=edited(o,axis,sign*size);next_choice,next_prob=selector.selection(model,changed)
                    experts=selector.expert_predictions(parent,changed,query)
                    actual=pool.combine(experts,next_choice)[1:-1];fixed=pool.combine(experts,choice)[1:-1]
                    total=distances(actual,original);switch=distances(actual,fixed)
                    rows.append(dict(clip=key[0],gap=key[1],context=key[2],frames=w['frame'].tolist(),edit_size=size,axis=axis,sign=sign,original_choice=choice,edited_choice=next_choice,changed_choice=choice!=next_choice,original_probability_margin=float(np.sort(prob)[-1]-np.sort(prob)[-2]),edited_probability_margin=float(np.sort(next_prob)[-1]-np.sort(next_prob)[-2]),total_change=total,selection_change_only=switch,position_max_amplification=total['position_max']/size))
                    assert time.perf_counter()-started<plan['max_seconds'] and time.time()<plan['deadline_unix']
        np.testing.assert_array_equal(o.positions,before)
    groups=[]
    for size in plan['edit_sizes_body_reference']:
        group=[r for r in rows if r['edit_size']==size];amplifications=[r['position_max_amplification'] for r in group]
        groups.append(dict(edit_size=size,cases=len(group),changed_choices=sum(r['changed_choice'] for r in group),position_max_amplification_p95=float(np.percentile(amplifications,95)),position_max_amplification_max=max(amplifications),selection_only_position_max=max(r['selection_change_only']['position_max'] for r in group),selection_only_rotation_max_radians=max(r['selection_change_only']['rotation_max_radians'] for r in group)))
    assert len(rows)==1728
    for n,h in report['source_sha256'].items():assert sha(ROOT/n)==h,n
    result=dict(complete=True,scope=plan['scope'],cases=len(rows),cohorts=96,groups=groups,rows=rows,model_sha256=digest,report_sha256=sha(folder/'report.json'),source_sha256=sha(Path(__file__)),plan_sha256=sha(ROOT/'selector_edit_stability_plan_v26.json'),seconds=time.perf_counter()-started,quality_gates_unchanged=True,qualification=False,full_goal_complete=False,confirmation_read=False,limitations=['Raw proposal stability diagnostic only; no actual-rig or physical-projection correction is measured.','Only rigid translation of one endpoint at the first existing window of each exposed development cohort is covered. Rotation edits and arbitrary controls are not covered.','Difference from retaining the original candidate isolates discrete selection changes; it is not a trained alternative or quality baseline.','No new pass threshold, refitting or model promotion.'])
    out.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n');print(json.dumps(dict(complete=True,cases=len(rows),groups=groups)),flush=True)
if __name__=='__main__':main()
