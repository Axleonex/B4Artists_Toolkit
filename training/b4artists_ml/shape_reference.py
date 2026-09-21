"""Procedural position reference for learned residual experiments; not ML.
SPDX-License-Identifier: GPL-2.0-or-later
Harmonic interior slopes follow the mathematical PCHIP definition documented by
SciPy/Fritsch-Butland. No SciPy runtime dependency or source code is used.
"""
import numpy as np
from semantic_motion_data import baseline

def harmonic_tangent(left,right,hleft,hright):
    left=np.asarray(left,dtype=float);right=np.asarray(right,dtype=float)
    if left.shape!=right.shape or not np.isfinite(left).all() or not np.isfinite(right).all() or not np.isfinite([hleft,hright]).all() or min(hleft,hright)<=0:raise ValueError('Finite slopes and positive intervals required')
    out=np.zeros_like(left);same=(np.sign(left)==np.sign(right))&(left!=0)&(right!=0)
    w1=2*hright+hleft;w2=hright+2*hleft
    out[same]=(w1+w2)/(w1/left[same]+w2/right[same])
    if not np.isfinite(out).all():raise ValueError('Nonfinite reference tangent')
    return out

def reference(observations,t):
    # Baseline validates queries and preserves the existing quaternion behavior.
    out=baseline(observations,t,contextual=True)
    if not observations.context:return out
    a,b,previous,following=observations.positions;duration=observations.duration;dt=observations.dt
    secant=(b-a)/duration
    incoming=harmonic_tangent((a-previous)/dt,secant,dt,duration)
    outgoing=harmonic_tangent(secant,(following-b)/dt,duration,dt)
    u=np.asarray(t)[:,None,None]
    points=(2*u**3-3*u**2+1)*a+(u**3-2*u**2+u)*duration*incoming+(-2*u**3+3*u**2)*b+(u**3-u**2)*duration*outgoing
    out=out.reshape(-1,17,9);out[...,:3]=points
    out[np.asarray(t)==0,:,:3]=a;out[np.asarray(t)==1,:,:3]=b
    return out.reshape(-1,153)
