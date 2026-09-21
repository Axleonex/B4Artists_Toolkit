"""Frozen V3 proportion stress evaluation. Existing clips are diagnostic, not newly blind.
SPDX-License-Identifier: GPL-2.0-or-later
"""
import json
import numpy as np
from train_limb_prior import ROOT,digest,load_rows,evaluate
from train_limb_prior_v2 import predictor
from train_limb_prior_v3 import linear_predictor
from augment_limb import augment_rows,STRESS_RATIOS

FROZEN='1c8d2b82916b4dd7c61c2e9629ae5e5a7566f6b0748284803c4ae23fd65db29b'


def read_model(name):
    with np.load(ROOT/'results'/name,allow_pickle=False) as archive:
        return {k:archive[k] for k in archive.files}


def part(model,kind):
    return {k[len(kind)+1:]:v for k,v in model.items() if k.startswith(kind+'_')}


def main():
    out=ROOT/'results'
    if digest(out/'limb_prior_rff_v3.npz')!=FROZEN:
        raise ValueError('V3 differs from the frozen selection')
    protocol=dict(schema=1,model_sha256=FROZEN,ratios=list(STRESS_RATIOS),
        scope='Retargeted per-limb direction reconstruction; not observed motion by people with those proportions',
        evidence_status='Reused V2 confirmation clips; no training overlap, but not newly blind for V3',
        gates={'stress_mean_vs_fixed':0.90,'stress_mean_vs_augmented_linear':0.90,
               'original_mean_vs_v2':1.10,'per_clip_absolute_increase_vs_fixed':0.02})
    (out/'proportion_protocol_v3.json').write_text(json.dumps(protocol,indent=2)+'\n')
    new=read_model('limb_prior_rff_v3.npz');old=read_model('limb_prior_rff_v2.npz')
    linear=read_model('limb_prior_linear_v3.npz')
    manifest=json.loads((ROOT/'confirmation_manifest.json').read_text())
    report=dict(protocol=protocol,manifest_sha256=digest(ROOT/'confirmation_manifest.json'),limbs={})
    for kind in ('arm','leg'):
        lp=part(linear,kind)
        predictions=dict(rff_v3=predictor(part(new,kind)),rff_v2_unbounded_diagnostic=predictor(part(old,kind)),
                         linear_augmented=linear_predictor(lp),
                         trained_mean_augmented=lambda x:np.tile(lp['mean_output'],(len(x),1)),
                         fixed_anatomical=lambda x:np.tile([0,1 if kind=='arm' else -1,0],(len(x),1)))
        original=load_rows(manifest,'confirmation',kind)
        stress=augment_rows(original,STRESS_RATIOS,include_original=False)
        metrics={split:{name:evaluate(data,fn) for name,fn in predictions.items()}
                 for split,data in (('original',original),('stress',stress))}
        by_ratio={str(ratio):{name:evaluate(augment_rows(original,(ratio,),include_original=False),fn)['clip_balanced_joint_error']
                             for name,fn in predictions.items()} for ratio in STRESS_RATIOS}
        score=metrics['stress']['rff_v3']['clip_balanced_joint_error']
        checks=dict(vs_fixed=score<=metrics['stress']['fixed_anatomical']['clip_balanced_joint_error']*.9,
                    vs_linear=score<=metrics['stress']['linear_augmented']['clip_balanced_joint_error']*.9,
                    original_retained=metrics['original']['rff_v3']['clip_balanced_joint_error']<=metrics['original']['rff_v2_unbounded_diagnostic']['clip_balanced_joint_error']*1.1,
                    per_clip=all(r['joint_error_fraction_mean']<=metrics['stress']['fixed_anatomical']['clips'][clip]['joint_error_fraction_mean']+.02 for clip,r in metrics['stress']['rff_v3']['clips'].items()))
        report['limbs'][kind]=dict(metrics=metrics,by_ratio=by_ratio,gates=checks,quality_gate_passed=all(checks.values()))
        print(kind,'STRESS',{k:round(v['clip_balanced_joint_error'],5) for k,v in metrics['stress'].items()},
              'ORIGINAL',round(metrics['original']['rff_v3']['clip_balanced_joint_error'],5),'GATES',checks,flush=True)
    (out/'limb_prior_stress_v3.json').write_text(json.dumps(report,indent=2)+'\n')

if __name__=='__main__':
    main()
