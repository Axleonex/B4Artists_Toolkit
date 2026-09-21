"""Small fresh confirmation after linear candidate freeze; remaining original 30 MB budget.
SPDX-License-Identifier: GPL-2.0-or-later
"""
import hashlib
import json
import urllib.request
import numpy as np
from train_limb_prior import ROOT,digest,load_rows,evaluate
from train_limb_prior_v3 import linear_predictor
from evaluate_limb_prior_v3 import read_model,part
from augment_limb import augment_rows,STRESS_RATIOS
from fetch_cmu_subset import BASE

FROZEN='73189e76dfea754c9115f74ae638b5e81f3775b34cf347f95c11efa89f9a18c7'
CLIPS=('74_08','78_12')


def main():
    out=ROOT/'results'
    path=out/'limb_prior_linear_runtime_v2.npz'
    if digest(path)!=FROZEN:
        raise ValueError('Candidate differs from frozen linear weights')
    original=json.loads((ROOT/'data_manifest.json').read_text())
    previous=json.loads((ROOT/'confirmation_manifest.json').read_text())
    if set(CLIPS)&{r['clip'] for r in original['files']+previous['files']}:
        raise ValueError('Fresh clips overlap earlier data')
    protocol=dict(schema=1,model_sha256=FROZEN,clips=list(CLIPS),
        descriptions=['lifting up','running without a ball'],
        selection_reason='Different subject numbers and actions, sized to remaining download budget; no motion values inspected before freeze',
        limits='Two short clips only; separate subject numbers do not prove separate people',
        gates={'stress_vs_fixed':.9,'stress_vs_trained_mean':.9,'per_clip_increase_vs_fixed':.02},
        download_limit_bytes=30_000_000)
    (out/'linear_confirmation_protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    mp=ROOT/'proportion_confirmation_manifest.json'
    expected={r['clip']:r for r in json.loads(mp.read_text())['files']} if mp.exists() else {}
    total=previous['total_combined_bytes'];rows=[]
    for clip in CLIPS:
        cache=ROOT/'cache'/(clip+'.bvh')
        url=BASE+f'data/{int(clip.split("_")[0]):03d}/{clip}.bvh'
        if cache.exists():
            data=cache.read_bytes()
        else:
            with urllib.request.urlopen(url,timeout=40) as response:
                data=response.read(30_000_000-total+1)
        total+=len(data);sha=hashlib.sha256(data).hexdigest()
        if total>30_000_000 or not data.lstrip().startswith(b'HIERARCHY'):
            raise ValueError('Data budget or format violation')
        if clip in expected and expected[clip]['sha256']!=sha:
            raise ValueError('Pinned confirmation content changed')
        if not cache.exists():cache.write_bytes(data)
        rows.append(dict(clip=clip,split='confirmation',url=url,bytes=len(data),sha256=sha))
    manifest=dict(files=rows,total_combined_bytes=total,frozen_model_sha256=FROZEN)
    mp.write_text(json.dumps(manifest,indent=2)+'\n')
    models=read_model('limb_prior_linear_v3.npz')
    report=dict(protocol=protocol,manifest_sha256=digest(mp),limbs={})
    for kind in ('arm','leg'):
        p=part(models,kind)
        predictors=dict(linear=linear_predictor(p),trained_mean=lambda x:np.tile(p['mean_output'],(len(x),1)),
                        fixed_anatomical=lambda x:np.tile([0,1 if kind=='arm' else -1,0],(len(x),1)))
        original=load_rows(manifest,'confirmation',kind)
        stress=augment_rows(original,STRESS_RATIOS,include_original=False)
        metrics={split:{name:evaluate(data,fn) for name,fn in predictors.items()}
                 for split,data in (('original',original),('stress',stress))}
        score=metrics['stress']['linear']['clip_balanced_joint_error']
        gates=dict(vs_fixed=score<=metrics['stress']['fixed_anatomical']['clip_balanced_joint_error']*.9,
                   vs_mean=score<=metrics['stress']['trained_mean']['clip_balanced_joint_error']*.9,
                   per_clip=all(v['joint_error_fraction_mean']<=metrics['stress']['fixed_anatomical']['clips'][clip]['joint_error_fraction_mean']+.02 for clip,v in metrics['stress']['linear']['clips'].items()))
        report['limbs'][kind]=dict(metrics=metrics,gates=gates,quality_gate_passed=all(gates.values()))
        print(kind,{k:round(v['clip_balanced_joint_error'],6) for k,v in metrics['stress'].items()},gates,flush=True)
    (out/'linear_proportion_confirmation.json').write_text(json.dumps(report,indent=2)+'\n')
    print('TOTAL_RAW_BYTES',total,flush=True)

if __name__=='__main__':
    main()
