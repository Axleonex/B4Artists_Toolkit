"""One fixed supervised mixture fit; two unchanged development guards stay explicit."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','4')
from pathlib import Path
import json,time,argparse,platform
import numpy as np
import joint_mixture_v24 as predictor
import kinematic_trajectory_v20 as parent_predictor
from semantic_projection import load_windows,project_windows
from motion_coverage import evaluate_predictions
from temporal_model import selection
from sequence_model import acceptance
from crossfit_controller import grouped_folds
from fetch_cmu_temporal_v19 import sha,read,write,require
ROOT=Path(__file__).resolve().parent


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args()
    require(args.output.replace('_','').isalnum(),'Simple unique output name required')
    out=ROOT/'results'/args.output;out.mkdir(exist_ok=False);start=time.perf_counter()
    protocol=read(ROOT/'joint_mixture_protocol_v24.json');old_path=ROOT/'results/kinematic_trajectory_v20/report.json';old=read(old_path)
    require(sha(old_path)==protocol['parent_report_sha256'],'Parent report changed')
    require(protocol['gates']==old['protocol']['gates'] and protocol['projection']==old['protocol']['projection'],'Frozen comparison changed')
    for name,h in protocol['source_manifests'].items():require(sha(ROOT/name)==h,'Data plan/manifest changed')
    require(sha(ROOT/'kinematic_trajectory_protocol_v20.json')==protocol['prior_protocol_sha256'],'Parent protocol changed')
    for name,h in protocol['parent_files'].items():require(sha(ROOT/name)==h,'Parent artifact changed')
    require(sha(ROOT/'results/kinematic_trajectory_v20/folds.json')==protocol['parent_folds_sha256'],'Parent folds changed')
    for name,h in old['source_sha256'].items():require(sha(ROOT/name)==h,'Prior source changed')
    require(sha(ROOT/'results/joint-mixture-checks-v24.json')==protocol['prefit_checks_sha256'],'Pre-fit checks changed')
    checks=read(ROOT/'results/joint-mixture-checks-v24.json');require(checks['passed'],'Pre-fit checks failed')
    for name,h in checks['source_sha256'].items():require(sha(ROOT/name)==h,'Checked implementation changed')
    require(sha(ROOT/'joint_mixture_plan_v24.json')==protocol['joint_plan_sha256'],'Prospective joint plan changed')
    require(sha(ROOT/'curve_confidence_plan_v23.json')==protocol['curve_plan_sha256'],'Original feature plan changed')
    for name,h in protocol['diagnostic_prior_reports'].items():require(sha(ROOT/'results'/name/'report.json')==h,'Prior diagnostic changed')
    sources=set(old['source_sha256'])|{'mixture_trajectory_protocol_v21.json','train_mixture_trajectory_v21.py','mixture_trajectory_v21.py','check_mixture_trajectory_v21.py','curve_confidence_plan_v23.json','curve_mixture_protocol_v23.json','curve_mixture_v23.py','curve_features_v23.py','check_curve_mixture_v23.py','train_curve_mixture_v23.py','joint_mixture_plan_v24.json','joint_mixture_protocol_v24.json','joint_mixture_v24.py','check_joint_mixture_v24.py','train_joint_mixture_v24.py'}
    hashes={n:sha(ROOT/n) for n in sorted(sources)}
    plan=read(ROOT/'temporal_expansion_plan_v19.json')
    def sealed():require(all(not (ROOT/'cache'/(c+'.bvh')).exists() for c in plan['planned_splits']['confirmation']),'Fresh confirmation already present')
    sealed();manifest=read(ROOT/'temporal_training_manifest_v19.json');write(out/'protocol.json',protocol);write(out/'manifest.json',manifest)
    train,skeleton=load_windows(ROOT,manifest,'train',protocol);require(len(train)==protocol['expected_training_windows'],'Unexpected training count')
    folds=grouped_folds(train,4);recorded=read(ROOT/'results/kinematic_trajectory_v20/folds.json');spec=protocol['gate_training'];terms=[None]*len(train);membership=[]
    print(json.dumps(dict(event='training_ready',windows=len(train))),flush=True)
    for fold,(training,testing) in enumerate(folds):
        record=dict(training_clips=sorted({train[i]['clip'] for i in training}),testing_clips=sorted({train[i]['clip'] for i in testing}))
        require(record==recorded[fold],'Fold membership changed')
        require(not ({c.split('_')[0] for c in record['training_clips']}&{c.split('_')[0] for c in record['testing_clips']}),'Parent group leakage')
        path=ROOT/f'results/kinematic_trajectory_v20/fold_{fold}.npz';parent=parent_predictor.load(path)
        for i in testing:
            require(terms[i] is None,'Duplicate training prediction owner')
            w=train[i];terms[i]=predictor.training_terms(w,predictor.expert_predictions(parent,w['observations'],w['t']),spec)
            w['gate_features']=predictor.curve_features(w['observations'],predictor.expert_predictions(parent,w['observations'],predictor.GRID))
        membership.append(dict(fold=fold,model_sha256=sha(path),windows=len(testing),**record))
        print(json.dumps(dict(event='group_excluded_parent_complete',fold=fold,seconds=time.perf_counter()-start)),flush=True)
    require(all(a is not None for a in terms),'Unowned training row');write(out/'parent_membership.json',membership)
    parent_path=ROOT/'results/kinematic_trajectory_v20/best_learned.npz';require(sha(parent_path)==protocol['prior_model_sha256'],'Full parent changed');parent=parent_predictor.load(parent_path)
    features=np.stack([w['gate_features'] for w in train]);require(features.shape==(7358,596) and np.isfinite(features).all(),'Invalid training curve features')
    write(out/'feature_audit.json',dict(rows=len(train),columns=596,original_columns=548,added_columns=48,finite=True,new_nonnegative=bool(np.all(features[:,548:]>=0)),new_min=float(features[:,548:].min()),new_max=float(features[:,548:].max()),parent_ownership='Exact same group-excluded parent as the training trajectory; no hidden target data in feature function'))
    model,diagnostic=predictor.fit(train,terms,parent,spec,protocol['seed']);predictor.save(out/'best_learned.npz',model)
    for k,v in parent.items():np.testing.assert_array_equal(model['parent_'+k],v)
    require(diagnostic['training_objective']<diagnostic['initial_objective'] and diagnostic['hidden_feature_change']>0,'No learned fitting improvement')
    model_sha=sha(out/'best_learned.npz');frozen=dict(id='joint_mixture_596_32_119_v24',sha256=model_sha,selection_split='single_prospectively_fixed_configuration',validation_loaded=False,confirmation_read=False,training_diagnostic=diagnostic,parent_sha256=sha(parent_path))
    write(out/'selection_frozen.json',frozen)
    print(json.dumps(dict(event='frozen',sha256=model_sha,diagnostic=diagnostic,seconds=time.perf_counter()-start)),flush=True)
    validation,vs=load_windows(ROOT,manifest,'validation',protocol);require(vs==skeleton,'Validation hierarchy changed')
    old_clips=set(protocol['old_validation_clips']);new_clips=set(protocol['new_validation_clips']);require(not old_clips&new_clips,'Validation overlap')
    parts={'old_validation':[w for w in validation if w['clip'] in old_clips],'new_validation':[w for w in validation if w['clip'] in new_clips]}
    require(len(parts['old_validation'])==480 and sum(map(len,parts.values()))==len(validation),'Validation sampling changed')
    reports={p:{} for p in [*parts,'combined']};weight_rows=[]
    for name,m in [(f'projected_{b}',dict(kind='baseline',baseline=b)) for b in ['linear','hermite','shape']]+[('mlp',model)]:
        all_windows=[];all_predictions=[];edges=[]
        for part,windows in parts.items():
            raw=[predictor.predict_packed(m,w['observations'],w['t']) for w in windows]
            projected,metrics=project_windows(windows,raw,skeleton,protocol['projection'])
            scored=evaluate_predictions(windows,projected);scored['aggregate']['true_edge_length_max']=metrics['true_edge_length_max'];scored['projection']=metrics
            reports[part][name]=scored;all_windows+=windows;all_predictions+=projected;edges.append(metrics['true_edge_length_max'])
            if name!='mlp':require(scored==old['partition_reports'][part][name],'Baseline/window regression')
            else:
                for w in windows:
                    pp,rp=predictor.strengths(m,w['observations']);weight_rows.append(dict(clip=w['clip'],gap=w['gap'],context=w['context'],position_strengths=pp.tolist(),rotation_strengths=rp.tolist()))
        combined=evaluate_predictions(all_windows,all_predictions);combined['aggregate']['true_edge_length_max']=max(edges);reports['combined'][name]=combined
        print(json.dumps(dict(event='evaluated',name=name,position={p:reports[p][name]['aggregate']['position'] for p in reports},seconds=time.perf_counter()-start)),flush=True)
    gates={p:acceptance(reports[p],protocol) for p in reports};overall=min(reports['combined'].items(),key=lambda p:selection(p[1]))[0]
    require(all(sha(ROOT/n)==h for n,h in hashes.items()),'Sources changed during fit');sealed()
    report=dict(schema=24,status='research_only',full_goal_complete=False,model_files={f'results/{args.output}/best_learned.npz':model_sha},confirmation_read=False,protocol=protocol,source_sha256=hashes,frozen_selection=frozen,selection=dict(id=overall,learned=overall=='mlp',best_learned_sha256=model_sha),training_diagnostic=diagnostic,training_windows=len(train),validation_windows=len(validation),validation_windows_by_partition={p:len(w) for p,w in parts.items()},baselines={k:v for k,v in reports['combined'].items() if k!='mlp'},best_learned_report=reports['combined']['mlp'],partition_reports=reports,development_gates=gates,gates=dict(best_learned=dict(passed=all(g['passed'] for g in gates.values()),partitions=gates)),runtime=dict(seconds=time.perf_counter()-start,python=platform.python_version(),numpy=np.__version__,blas_threads=os.environ['OPENBLAS_NUM_THREADS']),limitations=['Both validation partitions are exposed development data; weights freeze before loading either in this experiment.','Gate labels are training labels; group-excluded parent predictions do not constitute independent validation of the gate.','All three partitions must pass without dilution; no confirmation or temporal model promotion.','Joint position blending and proper quaternion rotations can still be worse than the best expert; hemisphere selection does not guarantee C1 continuity or full intent-aware learned motion.'])
    write(out/'expert_strengths.json',dict(position_expert_order=['linear','hermite','shape','v20'],rotation_expert_order=['linear','hermite','v20'],rows=weight_rows));write(out/'report.json',report)
    if report['gates']['best_learned']['passed']:write(out/'confirmation_selection.json',dict(confirmation_loaded=False,model_files=report['model_files'],development_report=f'results/{args.output}/report.json',development_report_sha256=sha(out/'report.json')))
    print(json.dumps(dict(event='complete',selection=report['selection'],gates=gates,seconds=report['runtime']['seconds'])),flush=True)
if __name__=='__main__':main()
