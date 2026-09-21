"""Fixed whole-interval proposals for projected training-risk investigation.
SPDX-License-Identifier: GPL-2.0-or-later
"""
import numpy as np
from curve_mixture_v23 import expert_predictions
from temporal_model import _window_metrics
POSITIONS=('linear','hermite','shape','v20')
ROTATIONS=('linear','hermite','v20')
ROTATION_INDEX=(0,1,3)
CANDIDATES=tuple((p,r) for p in range(4) for r in range(3))
BASELINE_INDEX=(0,4,7)


def combine(experts, candidate):
    values=np.asarray(experts,dtype=float)
    if values.ndim!=3 or values.shape[0]!=4 or values.shape[2]!=153 or not np.isfinite(values).all():
        raise ValueError('Four finite matched semantic proposals required')
    if type(candidate) is not int or not 0<=candidate<len(CANDIDATES):raise ValueError('Invalid candidate index')
    values=values.reshape(4,-1,17,9)
    if not np.array_equal(values[1,...,3:],values[2,...,3:]):raise ValueError('Shape/Hermite rotation equivalence changed')
    p,r=CANDIDATES[candidate];out=values[ROTATION_INDEX[r]].copy();out[...,:3]=values[p,...,:3]
    return out.reshape(-1,153)


def metrics(window,prediction):
    return _window_metrics(dict(target=window['target'],baseline=window['hermite'],t=window['t'],dt=np.full(len(window['t']),window['dt'])),prediction)


def report(windows, rows, choices, edge):
    if len(windows)!=len(rows) or len(rows)!=len(choices):raise ValueError('Matching diagnostic rows required')
    cohorts={};endp=endr=0.;bad=queries=0
    for w,group,index in zip(windows,rows,choices):
        m=group[int(index)];key=f"{w['clip']}/gap{int(w['gap'])}/context{int(w['context'])}"
        cohorts.setdefault(key,[]).append(m);endp=max(endp,m['endpoint_position']);endr=max(endr,m['endpoint_rotation_matrix']);bad+=m['degenerate_rotations'];queries+=len(w['t'])
    names=('position','root','rotation','length','velocity','acceleration')
    means={k:{name:float(np.mean([m[name] for m in values])) for name in names} for k,values in cohorts.items()}
    aggregate={name:float(np.mean([m[name] for m in means.values()])) for name in names}
    aggregate.update(endpoint_position=endp,endpoint_rotation_matrix=endr,degenerate_rotations=bad,queries=queries,true_edge_length_max=edge)
    return dict(aggregate=aggregate,cohorts=means)
