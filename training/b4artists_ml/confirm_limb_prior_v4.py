"""Fresh expansion confirmation after model-class and weight freeze.
SPDX-License-Identifier: GPL-2.0-or-later
"""
import json
import numpy as np
from train_limb_prior import ROOT,digest,load_rows,evaluate
from train_limb_prior_v3 import linear_predictor
from evaluate_limb_prior_v3 import read_model,part
from augment_limb import augment_rows,STRESS_RATIOS
from fetch_cmu_expansion import fetch

FROZEN='4439853b708d2aca99659e5e7a28f2eb0469660f3cef03fd78441ebab8fa1b45'


def selected_predictor(params):
    def predict(x):
        z=(x[:,3:]-params['mean'])/params['scale']
        phi=np.c_[np.ones(len(x)),z]
        if len(params['phase']):
            phi=np.c_[phi,np.cos(z@params['omega']+params['phase'])*np.sqrt(2/len(params['phase']))]
        return phi@params['coefficients']
    return predict


def main():
    out=ROOT/'results'
    if digest(out/'limb_prior_selected_v4.npz')!=FROZEN:raise ValueError('V4 differs from frozen candidate')
    protocol=dict(schema=1,model_sha256=FROZEN,clips=['29_01','29_03'],
        selected_before_download=True,scope='Original and retargeted limb reconstruction on walking and expressive gesturing',
        gates={'stress_vs_fixed':.9,'stress_vs_trained_mean':.9,'per_clip_increase_vs_fixed':.02},
        limits='Two clips from one new subject number; not broad generalization or visual-quality proof')
    (out/'confirmation_protocol_v4.json').write_text(json.dumps(protocol,indent=2)+'\n')
    manifest=fetch(True,FROZEN)
    models=read_model('limb_prior_selected_v4.npz');linear=read_model('limb_prior_linear_v4.npz')
    report=dict(protocol=protocol,manifest_sha256=digest(ROOT/'expansion_manifest.json'),limbs={})
    for kind in ('arm','leg'):
        p=part(linear,kind)
        predictors=dict(selected=selected_predictor(part(models,kind)),linear=linear_predictor(p),
            trained_mean=lambda x:np.tile(p['mean_output'],(len(x),1)),
            fixed_anatomical=lambda x:np.tile([0,1 if kind=='arm' else -1,0],(len(x),1)))
        original=load_rows(manifest,'confirmation',kind)
        stress=augment_rows(original,STRESS_RATIOS,include_original=False)
        metrics={split:{name:evaluate(data,fn) for name,fn in predictors.items()}
                 for split,data in (('original',original),('stress',stress))}
        score=metrics['stress']['selected']['clip_balanced_joint_error']
        gates=dict(vs_fixed=score<=metrics['stress']['fixed_anatomical']['clip_balanced_joint_error']*.9,
                   vs_mean=score<=metrics['stress']['trained_mean']['clip_balanced_joint_error']*.9,
                   per_clip=all(v['joint_error_fraction_mean']<=metrics['stress']['fixed_anatomical']['clips'][clip]['joint_error_fraction_mean']+.02 for clip,v in metrics['stress']['selected']['clips'].items()))
        report['limbs'][kind]=dict(metrics=metrics,gates=gates,quality_gate_passed=all(gates.values()))
        print(kind,{k:round(v['clip_balanced_joint_error'],6) for k,v in metrics['stress'].items()},gates,flush=True)
    (out/'limb_prior_confirmation_v4.json').write_text(json.dumps(report,indent=2)+'\n')
    print('COMBINED_RAW_BYTES',manifest['combined_raw_bytes'],flush=True)

if __name__=='__main__':main()
