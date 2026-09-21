"""Pose-preserving limb proportion augmentation. SPDX-License-Identifier: GPL-2.0-or-later."""
import numpy as np

TRAIN_RATIOS=(.40,.45,.50,.55,.60,.65)
# Between training ratios, plus measured default BoneForge/Rigify proportions.
STRESS_RATIOS=(.425,.475,.525,.575,.625,.5232833,.537037,.5058792,.5414679)


def segments(x,y,g):
    """Recover unit segment directions from the normalized endpoint and bend label."""
    x=np.asarray(x,dtype=float);y=np.asarray(y,dtype=float);g=np.asarray(g,dtype=float)
    if (x.ndim!=2 or x.shape[1]!=7 or y.shape!=(len(x),3) or g.shape!=(len(x),4)
            or not all(np.isfinite(v).all() for v in (x,y,g))):
        raise ValueError('Invalid normalized limb samples')
    ratio=x[:,6:7];delta=x[:,3:6]
    distance=np.linalg.norm(delta,axis=1,keepdims=True)
    if np.any((ratio<=0)|(ratio>=1)) or np.any(distance<1e-8):
        raise ValueError('Degenerate normalized limb samples')
    axis=delta/distance
    along=(ratio**2-(1-ratio)**2+distance**2)/(2*distance)
    joint=along*axis+g[:,3:4]*y
    upper=joint/ratio;lower=(delta-joint)/(1-ratio)
    if not all(np.allclose(np.linalg.norm(v,axis=1),1,atol=1e-6) for v in (upper,lower)):
        raise ValueError('Inconsistent segment reconstruction')
    return upper,lower


def retarget(x,y,g,ratio):
    """Change only segment lengths; preserve upper/lower directions in the body frame."""
    if not np.isscalar(ratio) or not np.isfinite(ratio) or not 0<ratio<1:
        raise ValueError('Length ratio must be strictly between zero and one')
    upper,lower=segments(x,y,g)
    joint=upper*ratio;delta=joint+lower*(1-ratio)
    distance=np.linalg.norm(delta,axis=1,keepdims=True)
    axis=delta/np.maximum(distance,1e-12)
    plane=joint-axis*np.sum(joint*axis,axis=1,keepdims=True)
    height=np.linalg.norm(plane,axis=1,keepdims=True)
    valid=(distance[:,0]>1e-8)&(height[:,0]>.025)
    inputs=np.asarray(x).copy();inputs[:,3:6]=delta;inputs[:,6]=ratio
    outputs=plane/np.maximum(height,1e-12)
    geometry=np.concatenate((axis,height),axis=1)
    return inputs[valid],outputs[valid],geometry[valid]


def augment_rows(rows,ratios=TRAIN_RATIOS,include_original=True):
    output=[]
    for clip,x,y,g in rows:
        samples=[(x,y,g)] if include_original else []
        samples.extend(retarget(x,y,g,ratio) for ratio in ratios)
        if not samples:
            raise ValueError('Augmentation requires at least one ratio')
        output.append((clip,*(np.concatenate([v[i] for v in samples]) for i in range(3))))
    return output
