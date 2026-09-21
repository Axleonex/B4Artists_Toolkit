"""Complete fixed fitted-risk data generation, fit and guarded development test."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','4')
from pathlib import Path
import argparse,time,json,platform
import numpy as np
import projected_selector_v26 as predictor
import projected_pool_v26 as pool
import kinematic_trajectory_v20 as parent_predictor
from semantic_projection import load_windows,project_windows
from crossfit_controller import grouped_folds
from motion_coverage import evaluate_predictions
from temporal_model import selection as selection_score
from sequence_model import acceptance
from fetch_cmu_temporal_v19 import sha,read,write,require
ROOT=Path(__file__).resolve().parent
METRICS=('position','root','rotation','length','velocity','acceleration','endpoint_position','endpoint_rotation_matrix','degenerate_rotations')

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args()
    require(args.output.replace('_','').isalnum(),'Simple unique output name required')
    out=ROOT/'results'/args.output;out.mkdir(exist_ok=False);(out/'chunks').mkdir();started=time.perf_counter()
    protocol=read(ROOT/'projected_selector_protocol_v26.json');plan=read(ROOT/'projected_selector_plan_v26.json')
    require(sha(ROOT/'projected_selector_protocol_v26.json')==plan['protocol_sha256'],'Prospective protocol changed')
    old=read(ROOT/'results/kinematic_trajectory_v20/report.json')
    require(sha(ROOT/'results/kinematic_trajectory_v20/report.json')==protocol['parent_report_sha256'],'Parent report changed')
    require(protocol['gates']==old['protocol']['gates'] and protocol['projection']==old['protocol']['projection'],'Original gates or projection changed')
    frozen_inputs={**protocol['source_manifests'],**protocol['parent_files'],**protocol['diagnostic_files']}
    for p,h in frozen_inputs.items():require(sha(ROOT/p)==h,'Frozen input changed:'+p)
    checks=read(ROOT/'results/projected-selector-checks-v26.json')
    require(checks['passed'] and len(checks['checks'])==12 and sha(ROOT/'results/projected-selector-checks-v26.json')==protocol['prefit_checks_sha256'],'Pre-fit checks changed or failed')
    for p,h in {**old['source_sha256'],**checks['source_sha256']}.items():require(sha(ROOT/p)==h,'Checked source changed:'+p)
    names=set(old['source_sha256'])|set(checks['source_sha256'])|{'projected_pool_plan_v26.json','projected_selector_plan_v26.json','projected_selector_protocol_v26.json','train_projected_selector_v26.py','semantic_projection.py','crossfit_controller.py','motion_coverage.py','sequence_model.py'}
    sources={n:sha(ROOT/n) for n in sorted(names)}
    expansion=read(ROOT/'temporal_expansion_plan_v19.json')
    def sealed():require(all(not (ROOT/'cache'/(c+'.bvh')).exists() for c in expansion['planned_splits']['confirmation']),'Fresh confirmation already present')
    def budget():
        require(time.perf_counter()-started<protocol['budgets']['max_seconds_per_complete_run'],'Complete-run wall budget reached; checkpoint without restarting')
        require(time.time()<1788981845.,'Authorized goal deadline reached')
    def emit(**event):
        event['elapsed_seconds']=time.perf_counter()-started
        with (out/'events.jsonl').open('a') as stream:stream.write(json.dumps(event)+'\n')
        print(json.dumps(event),flush=True)
    sealed();write(out/'protocol.json',protocol);manifest=read(ROOT/'temporal_training_manifest_v19.json');write(out/'manifest.json',manifest)
    train,skeleton=load_windows(ROOT,manifest,'train',protocol);require(len(train)==7358,'Training count changed')
    models=[];owner={};membership=[];folds=read(ROOT/'results/kinematic_trajectory_v20/folds.json')
    require(sha(ROOT/'results/kinematic_trajectory_v20/folds.json')==protocol['parent_folds_sha256'],'Parent folds changed')
    for fold,(training,testing) in enumerate(grouped_folds(train,4)):
        record=dict(training_clips=sorted({train[i]['clip'] for i in training}),testing_clips=sorted({train[i]['clip'] for i in testing}))
        require(record==folds[fold],'Parent membership changed')
        require(not ({c.split('_')[0] for c in record['training_clips']}&{c.split('_')[0] for c in record['testing_clips']}),'Parent group leakage')
        for i in testing:require(int(i) not in owner,'Duplicate training owner');owner[int(i)]=fold
        path=ROOT/f'results/kinematic_trajectory_v20/fold_{fold}.npz';models.append(parent_predictor.load(path));membership.append(dict(fold=fold,model_sha256=sha(path),**record))
    require(len(owner)==len(train),'Unowned training rows');write(out/'parent_membership.json',membership)
    identities=[dict(index=i,clip=w['clip'],gap=w['gap'],context=bool(w['context']),frames=w['frame'].tolist(),parent_fold=owner[i]) for i,w in enumerate(train)]
    write(out/'window_identity.json',identities);features=np.empty((len(train),596));measured=np.empty((len(train),12,len(METRICS)));chunk_records=[];edge=0.
    require(2*(features.nbytes+measured.nbytes)+8*1024*1024<=protocol['budgets']['max_output_bytes'],'Projected labels exceed preflight output budget')
    emit(event='training_only_ready',windows=len(train),candidates=12,validation_loaded=False)
    for start in range(0,len(train),16):
        budget();rows=train[start:start+16];batch=time.perf_counter();indexes=range(start,start+len(rows))
        experts=[pool.expert_predictions(models[owner[i]],w['observations'],w['t']) for i,w in zip(indexes,rows)]
        for i,w in zip(indexes,rows):features[i]=predictor.curve_features(w['observations'],predictor.expert_predictions(models[owner[i]],w['observations'],predictor.GRID))
        for candidate in range(12):
            raw=[pool.combine(e,candidate) for e in experts];projected,geometry=project_windows(rows,raw,skeleton,protocol['projection']);edge=max(edge,geometry['true_edge_length_max'])
            for i,w,pred in zip(indexes,rows,projected):
                m=pool.metrics(w,pred);require(m['endpoint_position']<=1e-6 and m['endpoint_rotation_matrix']<=1e-6 and m['degenerate_rotations']==0,'Training proposal priority/rotation failure')
                measured[i,candidate]=[m[k] for k in METRICS]
        chunk=out/f'chunks/{start:05d}.npz';end=start+len(rows)
        np.savez_compressed(chunk,features=features[start:end],metrics=measured[start:end],indices=np.arange(start,end))
        chunk_records.append(dict(start=start,end=end,path=chunk.relative_to(out).as_posix(),sha256=sha(chunk),bytes=chunk.stat().st_size))
        write(out/'projection_progress.json',dict(complete=False,processed=end,total=len(train),training_only=True,validation_loaded=False,source_sha256=sources,chunks=chunk_records,seconds=time.perf_counter()-started))
        if start==0 or end%64==0 or end==len(train):emit(event='projected_training_labels',processed=end,total=len(train),batch_seconds=time.perf_counter()-batch)
    require(np.isfinite(features).all() and np.isfinite(measured).all() and edge<=1e-6,'Invalid fitted labels or features')
    np.savez_compressed(out/'labels.npz',features=features,metrics=measured)
    write(out/'label_manifest.json',dict(complete=True,training_windows=len(train),features=596,candidates=12,metric_order=list(METRICS),true_edge_length_max=edge,chunks=chunk_records,labels_sha256=sha(out/'labels.npz'),source_sha256=sources,hidden_labels_only_in_costs=True))
    costs=[[dict(zip(METRICS,values)) for values in row] for row in measured]
    cost,weight,denominators=predictor.training_costs(identities,costs);write(out/'cost_normalizers.json',denominators)
    parent_path=ROOT/'results/kinematic_trajectory_v20/best_learned.npz';require(sha(parent_path)==protocol['prior_model_sha256'],'Parent changed');parent=parent_predictor.load(parent_path)
    budget();model,diagnostic=predictor.fit(features,cost,weight,parent,protocol['selector_training'],protocol['seed']);predictor.save(out/'best_learned.npz',model)
    for k,v in parent.items():np.testing.assert_array_equal(model['parent_'+k],v)
    require(diagnostic['training_objective']<diagnostic['initial_objective'] and diagnostic['hidden_feature_change']>0,'No learned improvement')
    model_sha=sha(out/'best_learned.npz');frozen=dict(id='projected_selector_596_32_12_v26',sha256=model_sha,selection_split='single_prospectively_fixed_configuration',validation_loaded=False,confirmation_read=False,training_diagnostic=diagnostic,parent_sha256=sha(parent_path),labels_sha256=sha(out/'labels.npz'))
    write(out/'selection_frozen.json',frozen);emit(event='frozen',sha256=model_sha,diagnostic=diagnostic)
    budget();validation,vs=load_windows(ROOT,manifest,'validation',protocol);require(vs==skeleton,'Validation hierarchy changed')
    old_clips=set(protocol['old_validation_clips']);new_clips=set(protocol['new_validation_clips']);require(not old_clips&new_clips,'Validation overlap')
    parts={'old_validation':[w for w in validation if w['clip'] in old_clips],'new_validation':[w for w in validation if w['clip'] in new_clips]}
    require(len(parts['old_validation'])==480 and len(parts['new_validation'])==288 and len(validation)==768,'Validation sampling changed')
    reports={p:{} for p in [*parts,'combined']};choice_rows=[]
    for name,m in [(f'projected_{b}',dict(kind='baseline',baseline=b)) for b in ['linear','hermite','shape']]+[('mlp',model)]:
        all_windows=[];all_predictions=[];edges=[]
        for part,windows in parts.items():
            budget();raw=[predictor.predict_packed(m,w['observations'],w['t']) for w in windows]
            projected,geometry=project_windows(windows,raw,skeleton,protocol['projection']);scored=evaluate_predictions(windows,projected)
            scored['aggregate']['true_edge_length_max']=geometry['true_edge_length_max'];scored['projection']=geometry;reports[part][name]=scored
            all_windows+=windows;all_predictions+=projected;edges.append(geometry['true_edge_length_max'])
            if name!='mlp':require(scored==old['partition_reports'][part][name],'Baseline/window regression')
            else:
                for w in windows:
                    choice,prob=predictor.selection(m,w['observations']);p,r=pool.CANDIDATES[choice]
                    choice_rows.append(dict(clip=w['clip'],gap=w['gap'],context=bool(w['context']),choice=choice,position=pool.POSITIONS[p],rotation=pool.ROTATIONS[r],uses_frozen_learned_expert=p==3 or r==2,probabilities=prob.tolist()))
        combined=evaluate_predictions(all_windows,all_predictions);combined['aggregate']['true_edge_length_max']=max(edges);reports['combined'][name]=combined
        emit(event='evaluated',name=name,position={p:reports[p][name]['aggregate']['position'] for p in reports})
    gates={p:acceptance(reports[p],protocol) for p in reports};overall=min(reports['combined'].items(),key=lambda p:selection_score(p[1]))[0]
    require(all(sha(ROOT/n)==h for n,h in sources.items()),'Sources changed during training')
    require(all(sha(ROOT/n)==h for n,h in frozen_inputs.items()),'Frozen data, parent or diagnostic changed during training');sealed();budget()
    write(out/'choices.json',choice_rows)
    report=dict(schema=26,status='research_only',full_goal_complete=False,model_files={f'results/{args.output}/best_learned.npz':model_sha},confirmation_read=False,protocol=protocol,source_sha256=sources,frozen_selection=frozen,selection=dict(id=overall,learned=overall=='mlp',best_learned_sha256=model_sha),training_diagnostic=diagnostic,training_windows=len(train),validation_windows=len(validation),validation_windows_by_partition={p:len(w) for p,w in parts.items()},baselines={k:v for k,v in reports['combined'].items() if k!='mlp'},best_learned_report=reports['combined']['mlp'],partition_reports=reports,development_gates=gates,gates=dict(best_learned=dict(passed=all(g['passed'] for g in gates.values()),partitions=gates)),label_artifacts=dict(manifest_sha256=sha(out/'label_manifest.json'),labels_sha256=sha(out/'labels.npz'),identity_sha256=sha(out/'window_identity.json')),learned_proposal_usage=dict(windows=sum(r['uses_frozen_learned_expert'] for r in choice_rows),total=len(choice_rows),note='Indicates selected learned-expert components; procedural selections remain procedural.'),runtime=dict(seconds=time.perf_counter()-started,python=platform.python_version(),numpy=np.__version__,blas_threads=os.environ['OPENBLAS_NUM_THREADS']),limitations=['Training costs see hidden training labels; inference features and proposal construction do not.','Parent predictions are group-excluded; the selector itself sees all training labels. This is not independent selector validation.','Expected-risk training differs from deterministic argmax deployment; deployed gates remain decisive.','Selected procedural proposals are not learned trajectory generation. Selected v20components use frozen learned residuals.','Both development partitions are exposed. No confirmation or runtime promotion occurs in this script; complete original workflow and usability requirements remain.'])
    write(out/'report.json',report)
    size=sum(p.stat().st_size for p in out.rglob('*') if p.is_file());require(size<=protocol['budgets']['max_output_bytes'],'Generated output budget exceeded')
    if report['gates']['best_learned']['passed']:write(out/'confirmation_selection.json',dict(confirmation_loaded=False,model_files=report['model_files'],development_report=f'results/{args.output}/report.json',development_report_sha256=sha(out/'report.json')))
    write(out/'complete.json',dict(complete=True,report_sha256=sha(out/'report.json'),generated_bytes=size))
    emit(event='complete',selection=report['selection'],gates=gates,generated_bytes=size)
if __name__=='__main__':main()
