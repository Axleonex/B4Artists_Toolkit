"""Freeze expanded temporal experiment; audit training only before any fit."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','4')
from pathlib import Path
import copy,json,hashlib,time
import numpy as np
from fetch_cmu_temporal_v19 import PLAN_SHA,sha,read,write,require
from bvh_data import parse_bvh
from semantic_motion_data import from_bvh,observe,encode_targets,SemanticSequence
from sequence_data import full_motion
from temporal_data import validate_manifests,rotation_matrix
ROOT=Path(__file__).resolve().parent

def main():
    plan_path=ROOT/'temporal_expansion_plan_v19.json';require(sha(plan_path)==PLAN_SHA,'Frozen plan changed');plan=read(plan_path)
    acquired=read(ROOT/'temporal_expansion_manifest_v19.json');require(acquired['plan_sha256']==PLAN_SHA and not acquired['confirmation_accessed'],'Unexpected acquisition state')
    require(all(x['status'] in ('complete','excluded') for x in acquired['files']),'Acquisition incomplete')
    require(len(acquired['files'])==54 and sum(x['status']=='complete' for x in acquired['files'])==53,'Unexpected clip count')
    require(all(not (ROOT/'cache'/(c+'.bvh')).exists() for c in plan['planned_splits']['confirmation']),'Confirmation must remain absent')
    previous=read(ROOT/'results/shape_trajectory_v18/report.json');protocol=copy.deepcopy(previous['protocol'])
    old=read(ROOT/'results/boundary_trajectory_v16/manifest.json');manifest=copy.deepcopy(old)
    manifest['files']+=copy.deepcopy([x for x in acquired['files'] if x['status']=='complete'])
    validate_manifests([manifest]);require(manifest['files'][:len(old['files'])]==old['files'],'Original indices changed')
    require(not set(x['sha256'] for x in manifest['files'] if x['split']=='train')&set(x['sha256'] for x in manifest['files'] if x['split']!='train'),'Cross-split content leak')
    sources=[];skeleton=None;excluded=[];roundtrip=0.;equivariance=0.;rotation_error=0.
    c=np.cos(.713);s=np.sin(.713);q=np.array([[c,0,s],[s*s,c,-s*c],[-s*c,s,c*c]]);shift=np.array([13.,-7.,4.]);factor=2.3
    for row in manifest['files']:
        if row['split']!='train':continue
        p=ROOT/'cache'/(row['clip']+'.bvh');require(sha(p)==row['sha256'],'Training checksum mismatch')
        try:
            motion=parse_bvh(p.read_text());seq=from_bvh(motion,30);full=full_motion(motion,30)
            identity=(full.names,full.parents,full.semantic)
            if skeleton is None:skeleton=identity
            require(skeleton==identity,'Unsupported source hierarchy')
            require(np.isfinite(motion.values).all(),'Nonfinite motion')
            counts={str(g):min(protocol['training_windows_per_gap'],max(0,len(seq.positions)-g-2))*len(protocol['contexts']) for g in protocol['gaps']}
            require(sum(counts.values())>0,'No eligible intervals')
        except (ValueError,IndexError) as error:
            require(row['clip'] in plan['planned_splits']['train'],'Existing training corpus unexpectedly failed')
            row['split']='excluded_train';row['eligibility_error']=str(error);excluded.append(dict(clip=row['clip'],reason=str(error)));continue
        end=min(33,len(seq.positions)-2);o=observe(seq,1,end,context=True);indices=np.arange(1,end+1)
        target=encode_targets(seq,indices,o).reshape(-1,17,9);rr,bad=rotation_matrix(target[...,3:]);require(not bad.any(),'Invalid target orientations')
        roundtrip=max(roundtrip,float(np.max(abs(o.world_points(target[...,:3])-seq.positions[indices]))))
        rotation_error=max(rotation_error,float(np.max(abs(o.world_rotations(rr)-seq.rotations[indices]))))
        transformed=SemanticSequence(seq.rest@q.T*factor+shift,q@seq.rest_rotations,seq.positions@q.T*factor+shift,q@seq.rotations,seq.frames,seq.dt)
        other=observe(transformed,1,end,context=True);equivariance=max(equivariance,float(np.max(abs(o.features()-other.features()))),float(np.max(abs(encode_targets(seq,indices,o)-encode_targets(transformed,indices,other)))))
        sources.append(dict(clip=row['clip'],new=row['clip'] in plan['planned_splits']['train'],catalog_group=row['clip'].split('_')[0],motion_seconds=(len(seq.positions)-1)*seq.dt,motion_frames=len(seq.positions),windows_by_gap=counts,windows=sum(counts.values()),source_sha256=row['sha256']))
    require(max(roundtrip,rotation_error,equivariance)<1e-8,'Coordinate regression')
    require(manifest['files'][:len(old['files'])]==old['files'],'Old manifest changed')
    dest=ROOT/'temporal_training_manifest_v19.json';require(not dest.exists(),'Manifest already frozen');write(dest,manifest)
    report=dict(passed=True,plan_sha256=PLAN_SHA,training_only=True,validation_parsed=False,confirmation_accessed=False,source_clips=len(sources),new_source_clips=sum(x['new'] for x in sources),catalog_groups=len(set(x['catalog_group'] for x in sources)),distinct_motion_seconds=sum(x['motion_seconds'] for x in sources),windows=sum(x['windows'] for x in sources),position_roundtrip_max=roundtrip,rotation_roundtrip_max=rotation_error,rigid_scale_equivariance_max=equivariance,excluded=excluded,acquisition_exclusions=[x for x in acquired['files'] if x['status']=='excluded'],rows=sources,old_manifest_rows_unchanged=True,old_row_count=len(old['files']),manifest_sha256=sha(dest),source_sha256={Path(__file__).name:sha(Path(__file__))})
    write(ROOT/'results/temporal-data-audit-v19.json',report)
    protocol.update(schema=19,scope='Fixed v18 learned architecture retrained on expanded distinct motion; isolate coverage effects without a hyperparameter search',source_manifests={'temporal_training_manifest_v19.json':sha(dest),'temporal_expansion_plan_v19.json':PLAN_SHA,'temporal_expansion_manifest_v19.json':sha(ROOT/'temporal_expansion_manifest_v19.json')},runtime='Local NumPy float64; previously bounded public data acquisition complete; no runtime downloads or external services',selection='One configuration identical to v18, four catalog-prefix-excluded training diagnostics and one full-training fit. No selection using old/new validation. Exact readout0.01 fixed in prior training-only research.',holdouts='Preserve original validation windows. New validation remains unopened until model freeze. Evaluate all unchanged gates separately on old validation, new validation and combined set. Sealed six-clip confirmation only opens if all three pass, with immutable model/report/plan receipts.',prior_model_sha256=previous['selection']['best_learned_sha256'],prior_protocol_sha256=sha(ROOT/'shape_trajectory_protocol_v18.json'),v19_no_grid=True,plan_sha256=PLAN_SHA,expected_training_windows=report['windows'],old_validation_clips=[x['clip'] for x in old['files'] if x['split']=='validation'],new_validation_clips=plan['planned_splits']['validation'],data_audit_sha256=sha(ROOT/'results/temporal-data-audit-v19.json'))
    for stale in ['v18_no_grid','training_only_diagnostic_sha256']:protocol.pop(stale,None)
    require(protocol['gates']==previous['protocol']['gates'] and protocol['experiments']==previous['protocol']['experiments'] and protocol['baselines']==previous['protocol']['baselines'],'Model or gate changed')
    write(ROOT/'expanded_trajectory_protocol_v19.json',protocol)
    print(json.dumps({k:v for k,v in report.items() if k not in ['rows','source_sha256']}),flush=True)
if __name__=='__main__':main()
