"""Training-only diagnosis; oracle labels are never an inference model.
SPDX-License-Identifier: GPL-2.0-or-later
"""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','4')
from pathlib import Path
import json, hashlib, time
import numpy as np
from bvh_data import parse_bvh
from semantic_motion_data import from_bvh, observe, encode_targets, SemanticSequence
from semantic_projection import load_windows
from semantic_predictor import features
from boundary_trajectory import load, predict_packed, residual_basis, observation_scale
from crossfit_controller import grouped_folds
from motion_coverage import evaluate_predictions
from sequence_kinematics import forward
from temporal_data import rotation_matrix
ROOT=Path(__file__).resolve().parent

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def pack(p):return {k:v['aggregate'] for k,v in p.items()}
def main():
    out=ROOT/'results/temporal-coverage-audit-v1.json'
    if out.exists():raise FileExistsError(out)
    start=time.perf_counter()
    protocol=json.loads((ROOT/'boundary_trajectory_protocol_v16.json').read_text())
    manifest_path=ROOT/'results/boundary_trajectory_v16/manifest.json'
    manifest=json.loads(manifest_path.read_text())
    models=[ROOT/'results/boundary_trajectory_v16/best_learned.npz']+[ROOT/f'results/boundary_trajectory_v16/trial_2_fold_{i}.npz' for i in range(4)]
    hashes={p.relative_to(ROOT).as_posix():sha(p) for p in models+[manifest_path,Path(__file__)]}
    windows,skeleton=load_windows(ROOT,manifest,'train',protocol)
    assert len(windows)==2912
    source=[];rests=[];roundtrip=0.;rotation_error=0.;equivariance=0.;label_equivariance=0.;initial_error=0.
    angle=.713;c=np.cos(angle);s=np.sin(angle)
    # Proper arbitrary rigid transform plus uniform scale: same normalized observations/labels.
    q=np.array([[c,0,s],[s*s,c,-s*c],[-s*c,s,c*c]])
    np.testing.assert_allclose(q.T@q,np.eye(3),atol=1e-14)
    shift=np.array([13.,-7.,4.]);factor=2.3
    for row in manifest['files']:
        if row['split']!='train':continue
        path=ROOT/'cache'/(row['clip']+'.bvh');assert sha(path)==row['sha256']
        motion=parse_bvh(path.read_text());seq=from_bvh(motion,protocol['target_fps'])
        selected=[w for w in windows if w['clip']==row['clip']]
        covered={int(f) for w in selected for f in w['frame']}
        intervals={(int(w['frame'][0]),int(w['frame'][-1])) for w in selected}
        source.append(dict(clip=row['clip'],catalog_group=row['clip'].split('_')[0],source_frames=len(motion.values),source_fps=1/motion.frame_time,effective_fps=1/seq.dt,motion_seconds=(len(seq.positions)-1)*seq.dt,windows=len(selected),unique_intervals=len(intervals),covered_frames=len(covered),motion_frames=len(seq.positions),covered_fraction=len(covered)/len(seq.positions),source_sha256=row['sha256']))
        o=observe(seq,1,min(33,len(seq.positions)-2),context=True)
        indices=np.arange(1,min(33,len(seq.positions)-2)+1)
        y=encode_targets(seq,indices,o).reshape(-1,17,9);rr,bad=rotation_matrix(y[...,3:]);assert not bad.any()
        roundtrip=max(roundtrip,float(np.max(abs(o.world_points(y[...,:3])-seq.positions[indices]))))
        rotation_error=max(rotation_error,float(np.max(abs(o.world_rotations(rr)-seq.rotations[indices]))))
        transformed=SemanticSequence(seq.rest@q.T*factor+shift,q@seq.rest_rotations,seq.positions@q.T*factor+shift,q@seq.rotations,seq.frames,seq.dt)
        other=observe(transformed,1,min(33,len(seq.positions)-2),context=True)
        equivariance=max(equivariance,float(np.max(abs(o.features()-other.features()))))
        label_equivariance=max(label_equivariance,float(np.max(abs(encode_targets(seq,indices,o)-encode_targets(transformed,indices,other)))))
        rests.append(o.rest)
    # Check that the full physical initializer and semantic observations share coordinates at known priorities.
    for w in windows:
        p,r,_=forward(w['projection_initial'][[0,-1]],w['offsets'],skeleton[1])
        initial_error=max(initial_error,float(np.max(abs(p[:,skeleton[2]]-w['observations'].positions[:2]))))
    assert max(roundtrip,rotation_error,equivariance,label_equivariance,initial_error)<1e-8
    print(json.dumps(dict(event='coordinates_checked',clips=len(source),roundtrip=roundtrip,initial_error=initial_error)),flush=True)
    selected=load(models[0]);predictions=dict(linear=[],hermite=[],learned_fit=[],learned_excluded_group=[],oracle_C0=[],oracle_C1=[])
    for w in windows:
        predictions['linear'].append(w['linear']);predictions['hermite'].append(w['hermite'])
        predictions['learned_fit'].append(predict_packed(selected,w['observations'],w['t']))
        scale=observation_scale(w['observations'])
        for mode in ['C0','C1']:
            b=residual_basis(w['t'],mode)
            # LABEL-ACCESS ORACLE: lower bound on basis reconstruction, not a usable predictor.
            residual=w['target']-w['hermite'];coeff=np.linalg.lstsq(b,residual,rcond=None)[0]
            coeff[:,scale==0]=0.
            predictions['oracle_'+mode].append(w['hermite']+b@coeff)
    x=np.stack([features(w['x'],'motion') for w in windows]);oof=[None]*len(windows);folds=[]
    for fold,(training,testing) in enumerate(grouped_folds(windows,4)):
        m=load(models[fold+1]);z=(x-m['mean'])/m['std'];zs=np.clip(z,-8,8)
        near=[]
        for begin in range(0,len(testing),64):
            ids=testing[begin:begin+64];a=zs[ids];b=zs[training]
            d=np.maximum(0,np.sum(a*a,axis=1)[:,None]+np.sum(b*b,axis=1)[None,:]-2*a@b.T)/x.shape[1]
            near.extend(np.sqrt(d.min(axis=1)).tolist())
        for i in testing:oof[i]=predict_packed(m,windows[i]['observations'],windows[i]['t'])
        folds.append(dict(fold=fold,train_windows=len(training),test_windows=len(testing),test_groups=sorted({windows[i]['clip'].split('_')[0] for i in testing}),feature_clipped_fraction=float(np.mean(abs(z[testing])>8)),test_windows_with_clipped_features=float(np.mean(np.any(abs(z[testing])>8,axis=1))),nearest_training_normalized_rms_median=float(np.median(near)),nearest_training_normalized_rms_p95=float(np.percentile(near,95))))
    predictions['learned_excluded_group']=oof
    reports={name:evaluate_predictions(windows,pred) for name,pred in predictions.items()}
    # Exact replay of saved training-only selection; protects against changed loader/metric behavior.
    old=json.loads((ROOT/'results/boundary_trajectory_v16/internal_trials.json').read_text())[2]['report']
    assert reports['learned_excluded_group']==old
    groups={}
    for name,report in reports.items():
        groups[name]={}
        for gap in protocol['gaps']:
            for context in protocol['contexts']:
                suffix=f'/gap{gap}/context{int(context)}';cohorts=[v for k,v in report['cohorts'].items() if k.endswith(suffix)]
                groups[name][suffix[1:]]={k:float(np.mean([r[k] for r in cohorts])) for k in ['position','rotation','velocity','acceleration']}
    assert all(sha(ROOT/p)==h for p,h in hashes.items())
    report=dict(scope='Training-only post-selection diagnostic. No validation or confirmation motion loaded; no model trained, tuned or promoted. Oracle uses hidden labels strictly for representation diagnosis and cannot be used as inference.',source_sha256=hashes,windows=len(windows),clips=len(source),catalog_groups=len({r['catalog_group'] for r in source}),unique_intervals=sum(r['unique_intervals'] for r in source),source_motion_seconds=sum(r['motion_seconds'] for r in source),rest_shapes_unique_at_1e_6=len({np.round(r,6).tobytes() for r in rests}),sources=source,coordinates=dict(position_roundtrip_max=roundtrip,rotation_roundtrip_max=rotation_error,rigid_scale_feature_error_max=equivariance,rigid_scale_label_error_max=label_equivariance,physical_initializer_priority_error_max=initial_error,passed=True),aggregates=pack(reports),gap_context=groups,fold_feature_shift=folds,full_goal_complete=False,seconds=time.perf_counter()-start)
    out.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ['sources','source_sha256','gap_context']}),flush=True)
if __name__=='__main__':main()
