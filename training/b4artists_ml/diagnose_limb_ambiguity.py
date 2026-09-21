"""Find cross-clip near-matching inputs with different bend labels in training only.
SPDX-License-Identifier: GPL-2.0-or-later
This is an ambiguity diagnostic, not proof of an irreducible error bound.
"""
import json
import numpy as np
from train_limb_prior import ROOT,load_rows


def main():
    manifest=json.loads((ROOT/'results'/'training_manifest_v4.json').read_text())
    report=dict(scope='Training clips only, original proportions, nearest cross-clip input to each sampled query',
        interpretation='Near-input disagreements motivate richer conditioning or multiple plausible completions; they do not establish exact ambiguity or a theoretical lower bound',limbs={})
    for kind in ('arm','leg'):
        rows=load_rows(manifest,'train',kind)
        x=np.concatenate([r[1][:,3:] for r in rows]);y=np.concatenate([r[2] for r in rows])
        g=np.concatenate([r[3] for r in rows])
        clips=np.concatenate([np.full(len(r[1]),i) for i,r in enumerate(rows)])
        # Ratio is dimensionless like normalized endpoint coordinates. No test-based tuning.
        ids=np.linspace(0,len(x)-1,min(len(x),2000),dtype=int)
        bank_norm=np.sum(x*x,axis=1)
        pairs=[];close=0
        for start in range(0,len(ids),128):
            q=ids[start:start+128]
            d=np.maximum(np.sum(x[q]*x[q],axis=1)[:,None]+bank_norm[None,:]-2*x[q]@x.T,0)
            d[clips[q,None]==clips[None,:]]=np.inf
            near=np.argmin(d,axis=1)
            for a,b in zip(q,near):
                endpoint=float(np.linalg.norm(x[a,:3]-x[b,:3]))
                ratio=float(abs(x[a,3]-x[b,3]))
                if endpoint<.025 and ratio<.01:
                    close+=1
                    angle=float(np.rad2deg(np.arccos(np.clip(y[a]@y[b],-1,1))))
                    if angle>60 and min(g[a,3],g[b,3])>.1:
                        pairs.append(dict(clip_a=rows[int(clips[a])][0],clip_b=rows[int(clips[b])][0],
                            endpoint_distance_fraction=endpoint,ratio_difference=ratio,bend_angle_difference_degrees=angle,
                            input_a=x[a].tolist(),input_b=x[b].tolist(),bend_a=y[a].tolist(),bend_b=y[b].tolist()))
        pairs.sort(key=lambda p:p['endpoint_distance_fraction'])
        report['limbs'][kind]=dict(training_samples=len(x),queries=len(ids),close_cross_clip_pairs=close,
                                  disagreeing_bent_pairs=len(pairs),examples=pairs[:10])
        print(kind,len(ids),'queries',close,'near pairs',len(pairs),'large label disagreements',flush=True)
    (ROOT/'results'/'limb_input_ambiguity.json').write_text(json.dumps(report,indent=2)+'\n')

if __name__=='__main__':main()
