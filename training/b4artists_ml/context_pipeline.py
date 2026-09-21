"""Callable, mutation-free sparse body completion research backend.
SPDX-License-Identifier: GPL-2.0-or-later
Coordinates are in the supplied pelvis frame, normalized by reference torso length.
This is not yet a BoneForge/Rigify control-space adapter or a released add-on API.
"""
import hashlib,io,time
import numpy as np
from context_data import JOINTS,encode,finish
from context_network import forward
from context_projection import project_pose_newton

MODEL_SHA256='919de9c772a521d6531f692b8903d0392fb981bf79896f40a8ff893d746a6f96'


def decode_model(data):
    if len(data)>200000 or hashlib.sha256(data).hexdigest()!=MODEL_SHA256:
        raise ValueError('Unrecognized contextual model checksum')
    shapes=dict(mean=(170,),scale=(170,),w0=(170,128),b0=(128,),w1=(128,51),b1=(51,))
    with np.load(io.BytesIO(data),allow_pickle=False) as archive:
        if set(archive.files)!=set(shapes):raise ValueError('Invalid contextual model contents')
        params={}
        for key,shape in shapes.items():
            value=archive[key]
            if value.shape!=shape or value.dtype.kind!='f' or not np.isfinite(value).all():raise ValueError('Invalid contextual model array')
            value.setflags(write=False);params[key]=value
    if np.any(params['scale']<=0):raise ValueError('Invalid normalization scale')
    return params


def complete_pose(params,rest,baseline,observations,mask,learned_influence=1.):
    started=time.perf_counter()
    if not np.isfinite(learned_influence) or not 0<=learned_influence<=1:
        raise ValueError('Learned influence must be between zero and one')
    rest=np.asarray(rest,dtype=float);baseline=np.asarray(baseline,dtype=float)
    observations=np.asarray(observations,dtype=float);mask=np.asarray(mask,dtype=bool)
    if rest.shape!=(JOINTS,3) or baseline.shape!=rest.shape or observations.shape!=rest.shape or mask.shape!=(JOINTS,):
        raise ValueError('Expected one semantic 17-joint pose')
    if not mask[0] or not np.allclose(rest[0],0,atol=1e-8) or not np.allclose(baseline[0],0,atol=1e-8) or not np.allclose(observations[0],0,atol=1e-8):
        raise ValueError('Supply a fixed pelvis frame with its origin at joint zero')
    # Missing targets may be NaN. Never inspect their hidden values or pass them to projection.
    safe_observations=np.where(mask[:,None],observations,baseline)
    x=encode(rest,baseline,safe_observations,mask)[None]
    if learned_influence:
        residual=forward(params,((x-params['mean'])/params['scale']).astype(np.float32))[0]*learned_influence
    else:residual=np.zeros(JOINTS*3)
    raw=finish(residual,baseline,safe_observations,mask)
    result,stats=project_pose_newton(raw,rest,safe_observations,mask)
    if not stats['converged'][0]:raise ValueError('Pose constraints did not converge; input poses remain untouched')
    return result,dict(model_sha256=MODEL_SHA256,learned_influence=learned_influence,
        max_length_error=float(stats['max_length_error'][0]),max_pin_error=float(stats['pin_error'][0]),
        projection_iterations=stats['iterations'],elapsed_ms=(time.perf_counter()-started)*1000)
