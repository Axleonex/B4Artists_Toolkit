"""Fresh subject confirmation, after v2 freeze; never used by training selection."""
import hashlib
import json
import platform
import time
import urllib.request
import numpy as np
from train_limb_prior import ROOT,digest,load_rows,evaluate,features
from train_limb_prior_v2 import predictor
from fetch_cmu_subset import BASE

CLIPS=('02_01','02_03','02_04','02_06','14_07','14_37','45_01')
FROZEN='59704e21ce7185697d48a62df60455aefaee8b7580f65496877d6bb39c8f073d'
LIMIT=30_000_000


def main():
    out=ROOT/'results'
    model_path=out/'limb_prior_rff_v2.npz'
    if digest(model_path)!=FROZEN:
        raise ValueError('V2 differs from the pre-confirmation frozen model')
    original=json.loads((ROOT/'data_manifest.json').read_text())
    if set(CLIPS)&{r['clip'] for r in original['files']}:
        raise ValueError('Confirmation overlaps previous data')
    protocol=dict(schema=1,model_sha256=FROZEN,clips=list(CLIPS),
        scope='Single-frame elbow/knee direction reconstruction only',
        quality_gate='At least 10% lower clip-balanced joint error than each fixed, mean and linear baseline, with no clip worse than fixed by more than 0.02 total limb lengths',
        download_limit_bytes=LIMIT)
    (out/'confirmation_protocol_v2.json').write_text(json.dumps(protocol,indent=2)+'\n')
    manifest_path=ROOT/'confirmation_manifest.json'
    previous=json.loads(manifest_path.read_text()) if manifest_path.exists() else None
    expected={r['clip']:r for r in previous['files']} if previous else {}
    rows=[];total=original['total_bytes']
    for clip in CLIPS:
        path=ROOT/'cache'/(clip+'.bvh')
        url=BASE+f'data/{int(clip.split("_")[0]):03d}/{clip}.bvh'
        if path.exists():
            data=path.read_bytes()
        else:
            with urllib.request.urlopen(url,timeout=40) as response:
                data=response.read(LIMIT-total+1)
        total+=len(data)
        sha=hashlib.sha256(data).hexdigest()
        if total>LIMIT:
            raise ValueError('Combined data download limit exceeded')
        if clip in expected and sha!=expected[clip]['sha256']:
            raise ValueError('Confirmation checksum differs')
        if not data.lstrip().startswith(b'HIERARCHY'):
            raise ValueError('Invalid confirmation data')
        if not path.exists():
            path.write_bytes(data)
        rows.append(dict(clip=clip,split='confirmation',url=url,bytes=len(data),sha256=sha))
    manifest=dict(schema=1,files=rows,total_combined_bytes=total,original_manifest_sha256=digest(ROOT/'data_manifest.json'),
                  frozen_model_sha256=FROZEN)
    manifest_path.write_text(json.dumps(manifest,indent=2)+'\n')
    with np.load(model_path,allow_pickle=False) as loaded:
        v2={k:loaded[k] for k in loaded.files}
    with np.load(out/'limb_prior_rff_v1.npz',allow_pickle=False) as loaded:
        v1={k:loaded[k] for k in loaded.files}
    report=dict(protocol=protocol,confirmation_manifest_sha256=digest(manifest_path),
                total_data_bytes=total,hardware=platform.processor(),limbs={})
    for kind in ('arm','leg'):
        params={k[len(kind)+1:]:v for k,v in v2.items() if k.startswith(kind+'_')}
        old={k[len(kind)+1:]:v for k,v in v1.items() if k.startswith(kind+'_')}
        pred=predictor(params)
        predictors=dict(fixed_anatomical=lambda x:np.tile([0,1 if kind=='arm' else -1,0],(len(x),1)),
            trained_mean=lambda x:np.tile(old['mean_output'],(len(x),1)),
            linear_v1=lambda x:np.c_[np.ones(len(x)),(x-old['mean'])/old['scale']]@old['linear_coefficients'],
            rff_v1=lambda x:features(x,old['mean'],old['scale'],old['omega'],old['phase'])@old['coefficients'],
            rff_v2=pred)
        data=load_rows(manifest,'confirmation',kind)
        metrics={name:evaluate(data,fn) for name,fn in predictors.items()}
        score=metrics['rff_v2']['clip_balanced_joint_error']
        aggregate=all(score<=metrics[name]['clip_balanced_joint_error']*0.9 for name in ('fixed_anatomical','trained_mean','linear_v1'))
        per_clip=all(row['joint_error_fraction_mean']<=metrics['fixed_anatomical']['clips'][clip]['joint_error_fraction_mean']+0.02
                     for clip,row in metrics['rff_v2']['clips'].items())
        batch=data[0][1][:4]
        start=time.perf_counter();pred(batch);first=time.perf_counter()-start
        times=[]
        for _ in range(100):
            start=time.perf_counter();pred(batch);times.append((time.perf_counter()-start)*1000)
        report['limbs'][kind]=dict(metrics=metrics,aggregate_gate=aggregate,per_clip_gate=per_clip,
            quality_gate_passed=aggregate and per_clip,
            warm_inference_ms_median=float(np.median(times)),warm_inference_ms_p95=float(np.percentile(times,95)),
            first_measured_inference_ms=first*1000,
            latency_scope='4-limb array batch after module/model loading and evaluation; not cold start or viewport latency')
        print(kind,{k:round(v['clip_balanced_joint_error'],5) for k,v in metrics.items()},
              'GATE',aggregate and per_clip,flush=True)
    report['deployment']='Research only until quality, rig projection, domain and workflow validation pass'
    (out/'limb_prior_confirmation_v2.json').write_text(json.dumps(report,indent=2)+'\n')
    print('COMBINED_DATA_BYTES',total,flush=True)

if __name__=='__main__':
    main()
