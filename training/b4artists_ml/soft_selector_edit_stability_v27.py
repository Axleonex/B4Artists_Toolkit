"""Same frozen endpoint-edit probes for soft and hard readouts."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','4')
from pathlib import Path
import json,time,hashlib
import numpy as np
import soft_selector_v27 as soft
import projected_selector_v26 as hard
from selector_edit_stability_v26 import edited,distances
from semantic_projection import load_windows
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'results/soft-selector-edit-stability-v27.json'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    assert not OUT.exists();started=time.perf_counter();plan=read(ROOT/'soft_selector_edit_plan_v27.json');base=read(ROOT/'results/projected-selector-edit-stability-v26.json');folder=ROOT/'results/soft_selector_v27';report=read(folder/'report.json');complete=read(folder/'complete.json')
    assert complete['complete'] and complete['report_sha256']==sha(folder/'report.json');assert sha(Path(__file__))==plan['source_sha256'] and sha(ROOT/'results/projected-selector-edit-stability-v26.json')==plan['prior_probe_sha256']
    model=soft.load(folder/'best_learned.npz');assert sha(folder/'best_learned.npz')==plan['model_sha256'];windows,_=load_windows(ROOT,read(ROOT/'temporal_training_manifest_v19.json'),'validation',report['protocol']);representatives={}
    for w in windows:representatives.setdefault((w['clip'],w['gap'],bool(w['context'])),w)
    assert len(representatives)==96 and len(windows)==768;query=np.linspace(0,1,9);records=[];sources=dict(report['source_sha256']);sources[Path(__file__).name]=sha(Path(__file__))
    for key,w in representatives.items():
        o=w['observations'];source=o.positions.copy();prob=soft.probabilities(model,o);before=soft.predict_packed(model,o,query)[1:-1];hard_before=hard.predict_packed(model,o,query)[1:-1]
        for size in plan['sizes']:
            for axis in range(3):
                for sign in (-1,1):
                    old=base['rows'][len(records)];assert (old['clip'],old['gap'],old['context'],old['edit_size'],old['axis'],old['sign'])==(*key,size,axis,sign) and old['frames']==w['frame'].tolist()
                    changed=edited(o,axis,sign*size);new_prob=soft.probabilities(model,changed);value=soft.predict_packed(model,changed,query)[1:-1];hard_value=hard.predict_packed(model,changed,query)[1:-1]
                    hard_change=distances(hard_value,hard_before);assert hard_change==old['total_change'],'Frozen hard-readout diagnostic changed'
                    experts=hard.expert_predictions(hard.parent_model(model),changed,query);fixed=soft.blend(experts,prob,query)[1:-1]
                    change=distances(value,before);weight_change=distances(value,fixed)
                    records.append(dict(clip=key[0],gap=key[1],context=key[2],frames=w['frame'].tolist(),edit_size=size,axis=axis,sign=sign,soft_change=change,hard_change=hard_change,probability_change_l1=float(abs(new_prob-prob).sum()),soft_weight_change_only=weight_change,soft_position_max_amplification=change['position_max']/size,hard_position_max_amplification=old['position_max_amplification'],top_probability_changed=bool(prob.argmax()!=new_prob.argmax())))
                    assert time.perf_counter()-started<plan['max_seconds'] and time.time()<plan['deadline_unix']
        np.testing.assert_array_equal(o.positions,source)
    assert len(records)==1728;groups=[]
    for size in plan['sizes']:
        rows=[r for r in records if r['edit_size']==size];soft_amp=[r['soft_position_max_amplification'] for r in rows];hard_amp=[r['hard_position_max_amplification'] for r in rows]
        groups.append(dict(edit_size=size,cases=len(rows),soft_position_amplification_p95=float(np.percentile(soft_amp,95)),soft_position_amplification_max=max(soft_amp),hard_position_amplification_p95=float(np.percentile(hard_amp,95)),hard_position_amplification_max=max(hard_amp),soft_rotation_change_max=max(r['soft_change']['rotation_max_radians'] for r in rows),hard_rotation_change_max=max(r['hard_change']['rotation_max_radians'] for r in rows),top_probability_changes=sum(r['top_probability_changed'] for r in rows)))
    for n,h in sources.items():assert sha(ROOT/n)==h,n
    result=dict(complete=True,cases=1728,cohorts=96,groups=groups,rows=records,model_sha256=plan['model_sha256'],source_sha256=sources,plan_sha256=sha(ROOT/'soft_selector_edit_plan_v27.json'),prior_hard_probes_reproduced_exactly=True,confirmation_read=False,quality_qualification=False,full_goal_complete=False,seconds=time.perf_counter()-started,limitations=['Raw proposals only; actual rig correction and displayed animation are not measured.','Same first representative from each exposed cohort and rigid endpoint translations only; no arbitrary rotation/control edit coverage.','Quaternion mixture is locally continuous away from reference hemisphere boundaries; these finite probes cannot prove global continuity.','Frozen probabilities are reused without refitting; no result-selected temperature or altered acceptance gate.'])
    OUT.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n');print(json.dumps(dict(complete=True,cases=1728,groups=groups)),flush=True)
if __name__=='__main__':main()
