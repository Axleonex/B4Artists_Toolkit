"""Fresh contextual completion/refinement confirmation, frozen model and projector.
SPDX-License-Identifier: GPL-2.0-or-later
"""
import hashlib,json,urllib.request
from train_limb_prior import ROOT,digest
from fetch_cmu_subset import BASE
from context_data import load_examples
from context_projection import project_pose_newton
from evaluate_context_projection import evaluate,models

FROZEN='919de9c772a521d6531f692b8903d0392fb981bf79896f40a8ff893d746a6f96'
CLIPS=('75_02','75_03','75_11')


def main():
    out=ROOT/'results'
    if digest(out/'context_pose_mlp_v1.npz')!=FROZEN:raise ValueError('Context model differs from freeze')
    protocol=dict(schema=1,model_sha256=FROZEN,projector_sha256=digest(ROOT/'context_projection.py'),clips=CLIPS,
        source_selection='Previously unread subject-number 75 run/jump clips within remaining 60 MB raw-data budget',
        neutral_gate='At least 10% lower mean hidden-joint error than identically projected starting pose; no clip >0.02 torso units worse',
        prior_gate='No increase in mean hidden-joint error over identically projected prior pose; no clip >0.02 torso units worse',
        geometry_gate='All pins <=1e-8; at least 99% of samples reach maximum edge-length error <=0.001',
        limits='Three short clips from one subject number, no actor-identity or broad quality guarantee; no rig or visual acceptance')
    pp=out/'context_confirmation_protocol_v1.json'
    if pp.exists() and json.loads(pp.read_text())!=json.loads(json.dumps(protocol)):
        raise ValueError('Confirmation protocol changed; preserve prior evidence and version a new experiment')
    pp.write_text(json.dumps(protocol,indent=2)+'\n')
    original=json.loads((ROOT/'expansion_manifest.json').read_text())
    total=original['combined_raw_bytes'];mp=ROOT/'context_confirmation_manifest.json'
    expected={r['clip']:r for r in json.loads(mp.read_text())['files']} if mp.exists() else {}
    rows=[]
    for clip in CLIPS:
        path=ROOT/'cache'/(clip+'.bvh');url=BASE+f'data/{int(clip.split("_")[0]):03d}/{clip}.bvh'
        if path.exists():data=path.read_bytes()
        else:
            with urllib.request.urlopen(url,timeout=40) as response:data=response.read(60_000_000-total+1)
        total+=len(data);sha=hashlib.sha256(data).hexdigest()
        if total>60_000_000 or not data.lstrip().startswith(b'HIERARCHY'):raise ValueError('Raw data budget or format violation')
        if clip in expected and expected[clip]['sha256']!=sha:raise ValueError('Changed confirmation data')
        if not path.exists():path.write_bytes(data)
        rows.append(dict(clip=clip,split='confirmation',url=url,bytes=len(data),sha256=sha))
    manifest=dict(files=rows,combined_raw_bytes=total,frozen_model_sha256=FROZEN)
    mp.write_text(json.dumps(manifest,indent=2)+'\n')
    report=dict(protocol=protocol,manifest_sha256=digest(mp),combined_raw_bytes=total,modes={})
    for mode in ('neutral','prior'):
        rows=load_examples(ROOT,manifest,'confirmation',seed=20260908,augment=True,mode=mode)
        result=evaluate(rows,models(),limit=100000,projector=project_pose_newton)
        selected=result['mlp'];baseline=result['starting_pose']
        multiplier=.9 if mode=='neutral' else 1.
        gates=dict(mean_error=selected['hidden_joint_error']<=baseline['hidden_joint_error']*multiplier,
            per_clip=all(r['hidden_joint_error']<=baseline['clips'][clip]['hidden_joint_error']+.02 for clip,r in selected['clips'].items()),
            pins=all(r['pin_error']<=1e-8 for r in selected['clips'].values()),convergence=selected['convergence_fraction']>=.99)
        report['modes'][mode]=dict(metrics=result,gates=gates,passed=all(gates.values()))
        print(mode,{k:round(v['hidden_joint_error'],5) for k,v in result.items()},gates,flush=True)
    (out/'context_pose_confirmation_v1.json').write_text(json.dumps(report,indent=2)+'\n')
    print('TOTAL_RAW_BYTES',total,flush=True)

if __name__=='__main__':main()
