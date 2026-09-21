"""Reproducible shared-schema corpus audit; no data acquisition or learning."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','4')
from pathlib import Path
import argparse,json,hashlib,time
import numpy as np
import semantic_motion_data as semantic
from sequence_data import load_windows as legacy_windows
from temporal_data import rotation_matrix,rotation6
ROOT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--label',required=True);args=parser.parse_args()
    if not args.label.replace('-','').isalnum():raise ValueError('Simple unique label required')
    out=ROOT/'results'/('semantic-observations-'+args.label+'.json')
    if out.exists():raise RuntimeError('Audit evidence exists')
    protocol=json.loads((ROOT/'semantic_observation_protocol_v11.json').read_text())
    assert all(sha(ROOT/n)==h for n,h in protocol['source_manifests'].items())
    prior=json.loads((ROOT/'results/training_manifest_v4.json').read_text());extra=json.loads((ROOT/'temporal_expansion_manifest_v8.json').read_text())
    manifest=dict(files=prior['files']+[r for r in extra['files'] if r['split']!='confirmation'])
    report=dict(protocol_sha256=sha(ROOT/'semantic_observation_protocol_v11.json'),runtime_sha256={n:sha(ROOT/n) for n in ('rig_observations.py','semantic_motion_data.py','sequence_data.py','temporal_data.py','bvh_data.py')},partitions={},model_fitted=False,new_downloads=False,full_goal_complete=False)
    start=time.perf_counter()
    for split in protocol['partitions']:
        windows=semantic.load_windows(ROOT,manifest,split,protocol);legacy,_=legacy_windows(ROOT,manifest,split,protocol)
        assert len(windows)==len(legacy)
        error=0.;endpoint=0.;features=hashlib.sha256();targets=hashlib.sha256();identities=hashlib.sha256()
        for w,old in zip(windows,legacy,strict=True):
            assert (w['clip'],w['gap'],w['context'])==(old['clip'],old['gap'],old['context'])
            assert np.array_equal(w['frame'],old['frame']) and np.all(w['frame']>0)
            assert w['x'].shape==(667,) and np.isfinite(w['x']).all() and np.isfinite(w['target']).all()
            old_values=old['target'].reshape(-1,17,9);rot,bad=rotation_matrix(old_values[...,3:]);assert not bad.any()
            calibrated=rot@np.swapaxes(w['observations'].rest_alignment,-1,-2)
            equivalent=np.concatenate((old_values[...,:3],rotation6(calibrated)),axis=-1).reshape(-1,153)
            error=max(error,float(np.max(abs(equivalent-w['target']))))
            endpoint=max(endpoint,float(np.max(abs(w['linear'][[0,-1]]-w['target'][[0,-1]]))),float(np.max(abs(w['hermite'][[0,-1]]-w['target'][[0,-1]]))))
            features.update(w['x'].astype('<f8').tobytes());targets.update(w['target'].astype('<f8').tobytes())
            identities.update(json.dumps([w['clip'],w['gap'],w['context'],w['frame'].tolist()]).encode())
        assert error<1e-11 and endpoint<1e-11
        report['partitions'][split]=dict(windows=len(windows),clips=sorted({w['clip'] for w in windows}),feature_sha256=features.hexdigest(),target_sha256=targets.hexdigest(),identity_sha256=identities.hexdigest(),legacy_target_calibration_max_error=error,endpoint_max_error=endpoint,input_features=667,output_features=153)
        out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(split=split,windows=len(windows),max_calibration_error=error,seconds=time.perf_counter()-start)),flush=True)
    report.update(passed=True,complete=True,seconds=time.perf_counter()-start)
    out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(passed=True,seconds=report['seconds'])),flush=True)
if __name__=='__main__':main()
