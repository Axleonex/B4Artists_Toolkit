"""Frozen local contextual pose inference; no training or online dependencies.
SPDX-License-Identifier: GPL-2.0-or-later
"""
import hashlib,io
import numpy as np
JOINTS=17
MODEL_SHA256='919de9c772a521d6531f692b8903d0392fb981bf79896f40a8ff893d746a6f96'

def encode(rest,baseline,observations,mask):
    rest=np.asarray(rest,dtype=float);baseline=np.asarray(baseline,dtype=float)
    observations=np.asarray(observations,dtype=float);mask=np.asarray(mask,dtype=bool)
    if rest.shape[-2:]!=(JOINTS,3) or baseline.shape!=rest.shape or observations.shape!=rest.shape or mask.shape!=rest.shape[:-1]:
        raise ValueError('Incompatible contextual pose shapes')
    visible=np.where(mask[...,None],observations,0.)
    if not all(np.isfinite(v).all() for v in (rest,baseline,visible)):raise ValueError('Nonfinite visible pose input')
    shape=rest.shape[:-2]
    return np.concatenate((rest.reshape(*shape,JOINTS*3),baseline.reshape(*shape,JOINTS*3),
                           visible.reshape(*shape,JOINTS*3),mask.astype(float)),axis=-1)



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



def forward(params,x):
    return np.tanh(x@params['w0']+params['b0'])@params['w1']+params['b1']
