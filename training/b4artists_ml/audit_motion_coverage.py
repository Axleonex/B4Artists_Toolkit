"""Audit frozen V2 representation and input coverage without fitting an inference model."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','4')
import json,hashlib
from pathlib import Path
import numpy as np
from sequence_data import load_windows
from sequence_model import statistics
from motion_coverage import observed_features,fit_feature_normalization,squared_distance,representation_diagnostic
ROOT=Path(__file__).resolve().parent

def main():
    protocol=json.loads((ROOT/'sequence_protocol_v2.json').read_text());path=ROOT/'results/training_manifest_v4.json'
    if hashlib.sha256(path.read_bytes()).hexdigest()!=protocol['manifests'][0]['sha256']:raise ValueError('Manifest mismatch')
    manifest=json.loads(path.read_text());train,skeleton=load_windows(ROOT,manifest,'train',protocol);val,vs=load_windows(ROOT,manifest,'validation',protocol)
    if skeleton!=vs:raise ValueError('Topology mismatch')
    _,weight,_,_=statistics(train);x=np.stack([observed_features(w) for w in train]);v=np.stack([observed_features(w) for w in val]);mean,std=fit_feature_normalization(x,weight)
    x=(x-mean)/std;v=(v-mean)/std
    nearest=[]
    for start in range(0,len(v),64):
        dist=squared_distance(v[start:start+64],x)
        for row,values in zip(val[start:start+64],dist):
            eligible=np.array([w['gap']==row['gap'] and w['context']==row['context'] for w in train]);values=np.where(eligible,values,np.inf);idx=int(values.argmin())
            nearest.append(dict(clip=row['clip'],gap=row['gap'],context=row['context'],start_frame=int(row['frame'][0]),nearest_clip=train[idx]['clip'],nearest_frame=int(train[idx]['frame'][0]),rms_distance=float(np.sqrt(values[idx]))))
    result=dict(schema=1,status='diagnostic_only',features=len(mean),training_windows=len(train),validation_windows=len(val),
                oracle_train=representation_diagnostic(train,skeleton),oracle_validation=representation_diagnostic(val,vs),nearest_observed=nearest,
                note='Oracle uses hidden labels only for capacity diagnosis. Neighbor inputs use known poses/rest/timing only; distance does not prove semantic similarity or person-disjointness.')
    output=ROOT/'results/motion_coverage_v3';output.mkdir(exist_ok=False);(output/'audit.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(output=str(output),oracle_train=result['oracle_train']['aggregate'],oracle_validation=result['oracle_validation']['aggregate'],distance_percentiles=np.percentile([n['rms_distance'] for n in nearest],[0,50,90,100]).tolist())),flush=True)

if __name__=='__main__':main()
