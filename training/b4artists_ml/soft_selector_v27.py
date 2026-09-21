"""Research soft readout of the frozen v26 learned probability model.
SPDX-License-Identifier: GPL-2.0-or-later
This is a new readout, not newly trained weights. Quaternion alignment is locally
continuous away from antipodal hemisphere boundaries; no global continuity claim.
"""
import numpy as np
import projected_selector_v26 as selector
from projected_pool_v26 import combine,ROTATION_INDEX
from curve_mixture_v23 import expert_predictions,parent_model
from temporal_data import rotation_matrix,rotation6,quaternion,quat_matrix
load=selector.load


def probabilities(model,observations):
    # Fixed temperature1 and the exact frozen feature/normalization network.
    # The stationary policy returns its established exact procedural reference.
    return selector.selection(model,observations)[1]


def blend(experts,probability,t):
    values=np.asarray(experts,dtype=float);probability=np.asarray(probability,dtype=float);t=np.asarray(t,dtype=float)
    if t.ndim!=1 or values.shape!=(4,len(t),153) or not np.isfinite(values).all() or not np.isfinite(t).all() or np.any((t<0)|(t>1)):
        raise ValueError('Four finite matched proposals and bounded query times required')
    if probability.shape!=(12,) or not np.isfinite(probability).all() or np.any(probability<0) or abs(float(probability.sum())-1.)>1e-12:
        raise ValueError('Twelve finite normalized nonnegative probabilities required')
    if np.count_nonzero(probability)==1 and probability.max()==1.:
        out=combine(values,int(probability.argmax())).copy();endpoints=(t==0.)|(t==1.);out[endpoints]=values[0,endpoints];return out
    packed=values.reshape(4,-1,17,9)
    if not np.array_equal(packed[1,...,3:],packed[2,...,3:]):raise ValueError('Shape/Hermite rotation equivalence changed')
    weights=probability.reshape(4,3);position_weight=weights.sum(axis=1);rotation_weight=weights.sum(axis=0)
    out=np.empty_like(packed[0]);out[...,:3]=np.einsum('c,ctjd->tjd',position_weight,packed[...,:3])
    matrices,bad=rotation_matrix(packed[list(ROTATION_INDEX),...,3:])
    if bad.any():raise ValueError('Degenerate rotation expert')
    q=quaternion(matrices);reference=q[1]
    q=np.where(np.sum(q*reference,axis=-1,keepdims=True)<0.,-q,q)
    mixed=np.einsum('c,ctjd->tjd',rotation_weight,q);norm=np.linalg.norm(mixed,axis=-1,keepdims=True)
    if not np.isfinite(norm).all() or np.any(norm<1e-8):raise ValueError('Ambiguous quaternion mixture')
    out[...,3:]=rotation6(quat_matrix(mixed/norm))
    # Endpoints are explicit priorities; avoid normalization roundoff there.
    endpoints=(t==0.)|(t==1.);out[endpoints]=packed[0,endpoints]
    return out.reshape(-1,153)


def predict_packed(model,observations,t):
    if model['kind']=='baseline':return selector.predict_packed(model,observations,t)
    if model['kind']!='projected_selector_v26':raise ValueError('Frozen v26selector weights required')
    from kinematic_trajectory_v20 import observation_scale
    if not np.any(observation_scale(observations)):return selector.predict_packed(model,observations,t)
    return blend(expert_predictions(parent_model(model),observations,t),probabilities(model,observations),t)


def provider(model):
    def call(observations,t):
        packed=predict_packed(model,observations,t).reshape(-1,17,9);rot,bad=rotation_matrix(packed[...,3:])
        if bad.any():raise ValueError('Degenerate soft proposal rotation')
        return packed[...,:3],rot
    return call
