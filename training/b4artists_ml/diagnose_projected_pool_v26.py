"""Training-only fitted proposal coverage; oracle results are not inference."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','4')
from pathlib import Path
import time,json,hashlib
import numpy as np
import projected_pool_v26 as pool
import kinematic_trajectory_v20 as parent
from semantic_projection import load_windows,project_windows
from crossfit_controller import grouped_folds
from sequence_model import acceptance
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'results/projected-pool-diagnostic-v26.json'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    assert not OUT.exists();started=time.perf_counter()
    plan=read(ROOT/'projected_pool_plan_v26.json');protocol=read(ROOT/'curve_mixture_protocol_v23.json')
    assert plan['projection']==protocol['projection'] and plan['gates_unchanged']==protocol['gates']
    for p,h in {**plan['source_manifests'],**plan['parent_files']}.items():assert sha(ROOT/p)==h,p
    expansion=read(ROOT/'temporal_expansion_plan_v19.json')
    def sealed():assert all(not (ROOT/'cache'/(c+'.bvh')).exists() for c in expansion['planned_splits']['confirmation'])
    sealed();sources={p:sha(ROOT/p) for p in ['projected_pool_v26.py','diagnose_projected_pool_v26.py','projected_pool_plan_v26.json','semantic_projection.py','curve_mixture_v23.py','curve_features_v23.py','kinematic_trajectory_v20.py','temporal_model.py','crossfit_controller.py']}
    windows,skeleton=load_windows(ROOT,read(ROOT/'temporal_training_manifest_v19.json'),'train',protocol)
    assert len(windows)==7358
    owner={};membership=[];recorded=read(ROOT/'results/kinematic_trajectory_v20/folds.json')
    models=[]
    for fold,(training,testing) in enumerate(grouped_folds(windows,4)):
        record=dict(training_clips=sorted({windows[i]['clip'] for i in training}),testing_clips=sorted({windows[i]['clip'] for i in testing}))
        assert record==recorded[fold]
        assert not ({c.split('_')[0] for c in record['training_clips']}&{c.split('_')[0] for c in record['testing_clips']})
        for i in testing:assert int(i) not in owner;owner[int(i)]=fold
        path=ROOT/f'results/kinematic_trajectory_v20/fold_{fold}.npz';models.append(parent.load(path));membership.append(dict(fold=fold,model_sha256=sha(path),**record))
    ids=[];seen=set()
    for i,w in enumerate(windows):
        key=(w['clip'],w['gap'],w['context'])
        if key not in seen:ids.append(i);seen.add(key)
    assert len(owner)==len(windows) and len(ids)<=plan['budgets']['max_diagnostic_windows']
    selected=[windows[i] for i in ids];scores=[];edge=0.;times=[]
    print(json.dumps(dict(event='training_only_ready',training_windows=len(windows),diagnostic_windows=len(ids),validation_loaded=False)),flush=True)
    for start in range(0,len(ids),16):
        assert time.perf_counter()-started<plan['budgets']['max_wall_seconds'],'Diagnostic budget reached; do not restart automatically'
        indexes=ids[start:start+16];rows=[windows[i] for i in indexes];batch=time.perf_counter()
        experts=[pool.expert_predictions(models[owner[i]],w['observations'],w['t']) for i,w in zip(indexes,rows)]
        local=[[] for _ in rows]
        for candidate in range(12):
            raw=[pool.combine(e,candidate) for e in experts]
            projected,geometry=project_windows(rows,raw,skeleton,protocol['projection']);edge=max(edge,geometry['true_edge_length_max'])
            for w,pred,m in zip(rows,projected,local):
                value=pool.metrics(w,pred);assert value['endpoint_position']<=1e-6 and value['endpoint_rotation_matrix']<=1e-6 and value['degenerate_rotations']==0
                m.append(value)
        scores+=local;times.append(time.perf_counter()-batch)
        partial=dict(complete=False,training_only=True,validation_loaded=False,confirmation_read=False,processed=len(scores),total=len(ids),elapsed_seconds=time.perf_counter()-started,source_sha256=sources)
        OUT.write_text(json.dumps(partial,indent=2)+'\n');print(json.dumps(dict(event='projected',processed=len(scores),total=len(ids),batch_seconds=times[-1],estimated_full_training_seconds=float(np.mean(times)/16*len(windows)))),flush=True)
    choices=np.asarray([[m['position'] for m in row] for row in scores]).argmin(axis=1)
    reports={f'projected_{name}':pool.report(selected,scores,np.full(len(ids),index),edge) for name,index in zip(('linear','hermite','shape'),pool.BASELINE_INDEX)}
    reports['mlp']=pool.report(selected,scores,choices,edge)
    gates=acceptance(reports,protocol);hist=np.bincount(choices,minlength=12)
    assert all(sha(ROOT/p)==h for p,h in sources.items());sealed()
    output=dict(complete=True,training_only=True,validation_loaded=False,confirmation_read=False,oracle_not_deployable=True,full_goal_complete=False,source_sha256=sources,plan_sha256=sha(ROOT/'projected_pool_plan_v26.json'),training_windows=len(windows),diagnostic_windows=len(ids),candidate_names=[dict(position=pool.POSITIONS[p],rotation=pool.ROTATIONS[r]) for p,r in pool.CANDIDATES],parent_membership=membership,window_identity=[dict(training_index=i,clip=w['clip'],gap=w['gap'],context=bool(w['context']),frames=w['frame'].tolist(),parent_fold=owner[i]) for i,w in zip(ids,selected)],metrics=scores,oracle_choices=choices.tolist(),oracle_choice_histogram=hist.tolist(),oracle_uses_learned_positions=int(hist[9:].sum()),reports=reports,diagnostic_gates=gates,edge_max=edge,batch_seconds=times,seconds=time.perf_counter()-started,estimated_full_training_projection_seconds=float(np.mean(times)/16*len(windows)),interpretation='First sampled window from each training cohort only. Hidden training labels select fitted position-error minimum. This measures proposal coverage and computational cost; it is not a learned selector, independent quality test or release gate. Coupled rotation/velocity costs remain visible.')
    content=json.dumps(output,indent=2)+'\n';assert len(content.encode())<=plan['budgets']['max_saved_bytes'];OUT.write_text(content)
    print(json.dumps(dict(event='complete',windows=len(ids),gates=gates,choice_histogram=hist.tolist(),learned_position_choices=output['oracle_uses_learned_positions'],estimated_full_training_seconds=output['estimated_full_training_projection_seconds'],seconds=output['seconds'])),flush=True)
if __name__=='__main__':main()
