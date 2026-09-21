"""Fixed training-only projected comparison; no refit or development loading."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','4')
from pathlib import Path
import time,json,hashlib,copy
import numpy as np
import soft_selector_v27 as soft
import projected_selector_v26 as hard
import projected_pool_v26 as pool
import kinematic_trajectory_v20 as parent
from semantic_projection import load_windows,project_windows
from crossfit_controller import grouped_folds
from sequence_model import acceptance
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'results/soft-selector-training-v27.json'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    assert not OUT.exists();started=time.perf_counter();plan=read(ROOT/'soft_selector_plan_v27.json');protocol=read(ROOT/'projected_selector_protocol_v26.json');prior=read(ROOT/'results/projected_selector_v26/report.json');diagnosis=read(ROOT/'results/projected-pool-diagnostic-v26.json')
    assert plan['source_sha256']==sha(ROOT/'soft_selector_v27.py') and plan['model_sha256']==sha(ROOT/plan['model_path']) and plan['projection']==protocol['projection'] and plan['gates']==protocol['gates']
    assert read(ROOT/'results/soft-selector-checks-v27.json')['passed']
    for n,h in prior['source_sha256'].items():assert sha(ROOT/n)==h,n
    expansion=read(ROOT/'temporal_expansion_plan_v19.json')
    def guard():
        assert time.perf_counter()-started<plan['budgets']['training_diagnostic_seconds'] and time.time()<plan['deadline_unix']
        assert all(not (ROOT/'cache'/(n+'.bvh')).exists() for n in expansion['planned_splits']['confirmation'])
    guard();windows,skeleton=load_windows(ROOT,read(ROOT/'temporal_training_manifest_v19.json'),'train',protocol);assert len(windows)==7358
    frozen=soft.load(ROOT/plan['model_path']);owners={};models=[];membership=read(ROOT/'results/kinematic_trajectory_v20/folds.json')
    for fold,(train,test) in enumerate(grouped_folds(windows,4)):
        row=dict(training_clips=sorted({windows[i]['clip'] for i in train}),testing_clips=sorted({windows[i]['clip'] for i in test}));assert row==membership[fold]
        pm=parent.load(ROOT/f'results/kinematic_trajectory_v20/fold_{fold}.npz');m=copy.deepcopy(frozen)
        for k,v in pm.items():m['parent_'+k]=v
        models.append(m)
        for i in test:assert int(i) not in owners;owners[int(i)]=fold
    ids=[r['training_index'] for r in diagnosis['window_identity']];assert len(ids)==466 and len(set(ids))==466
    for i,row in zip(ids,diagnosis['window_identity']):
        w=windows[i];assert row['clip']==w['clip'] and row['gap']==w['gap'] and row['context']==w['context'] and row['frames']==w['frame'].tolist() and row['parent_fold']==owners[i]
    with np.load(ROOT/'results/projected_selector_v26/labels.npz',allow_pickle=False) as z:features=z['features'];costs=z['metrics']
    selected=[windows[i] for i in ids];metrics=[];edge={'soft':0.,'hard':0.};choices=[];feature_exact=True;max_label_delta=0.;metric_names=read(ROOT/'results/projected_selector_v26/label_manifest.json')['metric_order']
    print(json.dumps(dict(event='training_only_ready',windows=466,validation_loaded=False,refitting=False)),flush=True)
    for start in range(0,len(ids),16):
        guard();indexes=ids[start:start+16];rows=[windows[i] for i in indexes];raw={k:[] for k in ('hard','soft')};local_choices=[]
        for i,w in zip(indexes,rows):
            m=models[owners[i]];x=hard.curve_features(w['observations'],hard.expert_predictions(hard.parent_model(m),w['observations'],hard.GRID));np.testing.assert_array_equal(x,features[i])
            choice,_=hard.selection(m,w['observations']);local_choices.append(choice);raw['hard'].append(hard.predict_packed(m,w['observations'],w['t']));raw['soft'].append(soft.predict_packed(m,w['observations'],w['t']))
        measured={}
        for name in ('hard','soft'):
            predictions,geometry=project_windows(rows,raw[name],skeleton,plan['projection']);edge[name]=max(edge[name],geometry['true_edge_length_max']);measured[name]=[pool.metrics(w,p) for w,p in zip(rows,predictions)]
            assert edge[name]<=1e-6 and all(m['endpoint_position']<=1e-6 and m['endpoint_rotation_matrix']<=1e-6 and m['degenerate_rotations']==0 for m in measured[name])
        for i,choice,a,b in zip(indexes,local_choices,measured['hard'],measured['soft']):
            delta=float(np.max(abs(np.array([a[k] for k in metric_names])-costs[i,choice])));max_label_delta=max(max_label_delta,delta);assert delta<=1e-12,'Re-evaluated hard proposal differs from frozen training label'
            metrics.append([a,b]);choices.append(choice)
        OUT.write_text(json.dumps(dict(complete=False,training_only=True,processed=len(metrics),total=466,validation_loaded=False,seconds=time.perf_counter()-started),indent=2)+'\n');print(json.dumps(dict(event='projected',processed=len(metrics),total=466)),flush=True)
    reports={k:copy.deepcopy(v) for k,v in diagnosis['reports'].items() if k!='mlp'};reports['mlp']=pool.report(selected,metrics,[1]*len(ids),edge['soft']);hard_report=pool.report(selected,metrics,[0]*len(ids),edge['hard']);gates=acceptance(reports,protocol)
    guard();assert all(sha(ROOT/n)==h for n,h in prior['source_sha256'].items()) and sha(ROOT/plan['model_path'])==plan['model_sha256']
    result=dict(complete=True,training_only=True,validation_loaded=False,confirmation_read=False,refit=False,windows=466,training_indices=ids,reports=reports,hard_report=hard_report,soft_diagnostic_gates=gates,hard_label_max_absolute_difference=max_label_delta,exact_group_excluded_training_features=True,geometry_passed=True,metrics=metrics,model_sha256=plan['model_sha256'],source_sha256={p.name:sha(p) for p in [Path(__file__),ROOT/'soft_selector_v27.py',ROOT/'soft_selector_plan_v27.json']},seconds=time.perf_counter()-started,full_goal_complete=False,limitations=['Selector sees all training labels; group-excluded trajectory parents match original fitting. This is not independent quality.','One first window per466trainingcohorts; fixed temperature1; no parameter or architecture search.','Halfturn quaternion branch ambiguity is explicitly rejected; local soft probability behavior does not imply globally continuous rotations.'])
    content=json.dumps(result,indent=2,allow_nan=False)+'\n';assert len(content.encode())<=plan['budgets']['max_output_bytes'];OUT.write_text(content);print(json.dumps(dict(complete=True,windows=466,geometry_passed=True,gates=gates,seconds=result['seconds'])),flush=True)
if __name__=='__main__':main()
