"""Known-pose kinematics expressed relative to decoder motion amplitudes.
SPDX-License-Identifier: GPL-2.0-or-later
No targets, hidden motion, corpus statistics or new observations enter this map.
"""
import numpy as np
from semantic_predictor import features as absolute_features
from temporal_data import rotation_matrix

def scales(x):
    x=np.array(x,dtype=float,copy=True)
    # Shared input/mask/orientation validation, before deriving amplitudes.
    absolute=absolute_features(x,'motion')
    if not np.isfinite(absolute).all():raise ValueError('Nonfinite observed velocity')
    p=x[:612].reshape(4,17,9);before,after=x[-4:-2];duration,dt=x[-2:]
    if not before:p[2]=p[0]
    if not after:p[3]=p[1]
    rotations,bad=rotation_matrix(p[...,3:])
    if bad.any():raise ValueError('Invalid observed rotations')
    points=p[...,:3];ratio=duration/dt
    if not np.isfinite(ratio):raise ValueError('Unrepresentable time ratio')
    position=np.linalg.norm(points[1]-points[0],axis=-1)+.5*ratio*(before*np.linalg.norm(points[0]-points[2],axis=-1)+after*np.linalg.norm(points[3]-points[1],axis=-1))
    rotation=(np.linalg.norm(rotations[1]-rotations[0],axis=(-1,-2))+.5*ratio*(before*np.linalg.norm(rotations[0]-rotations[2],axis=(-1,-2))+after*np.linalg.norm(rotations[3]-rotations[1],axis=(-1,-2))))/np.sqrt(2.)
    if not np.isfinite(position).all() or not np.isfinite(rotation).all():raise ValueError('Nonfinite motion amplitude')
    return absolute,np.r_[np.repeat(position,3),np.repeat(rotation,3)]

def features(x,variant='motion'):
    if variant!='motion':raise ValueError('Only normalized motion features are defined')
    absolute,amplitude=scales(x);result=absolute.copy();duration=float(np.asarray(x)[-2])
    for section,factor in [(slice(153,255),1.),(slice(255,357),duration),(slice(357,459),duration)]:
        numerator=absolute[section]*factor
        result[section]=np.divide(numerator,amplitude,out=np.zeros(102),where=amplitude>0)
    # Keep34 explicit magnitudes: the network can recover all original motion
    # features and still distinguish large reaches/strides from small ones.
    result=np.r_[result,amplitude[:51:3],amplitude[51::3]]
    if not np.isfinite(result).all():raise ValueError('Nonfinite normalized motion features')
    return result
