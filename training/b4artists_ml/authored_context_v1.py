"""Procedural authored-pose trajectory experiment; no learned-motion claim.
SPDX-License-Identifier: GPL-2.0-or-later
Only positions at authored priorities determine position tangents. Source motion
outside the intervals is used solely in the explicit source-rotation comparator.
"""
import numpy as np
from shape_reference import harmonic_tangent
from semantic_predictor import provider

class Trajectory:
    def __init__(self,observations,frames,*,rotation='source'):
        if rotation not in ('source','slerp'):raise ValueError('Unknown rotation comparison')
        frames=np.asarray(frames,dtype=float)
        if frames.ndim!=1 or len(frames)<2 or len(observations)!=len(frames)-1 or not np.isfinite(frames).all() or np.any(np.diff(frames)<=0):
            raise ValueError('Increasing authored frames and matching intervals required')
        self.rotation=rotation;self.frames=frames.copy();self.origin=observations[0].origin.copy();self.basis=observations[0].basis.copy();self.scale=observations[0].scale
        self.seconds=np.asarray([o.duration for o in observations])
        if not np.isfinite(self.seconds).all() or np.any(self.seconds<=0) or not np.allclose(self.seconds/np.diff(frames),self.seconds[0]/np.diff(frames)[0],rtol=1e-8,atol=1e-12):
            raise ValueError('Authored interval timing must use one frame rate')
        pairs=np.stack([o.world_points(o.positions[:2]) for o in observations])
        if not np.isfinite(pairs).all() or (len(pairs)>1 and not np.allclose(pairs[:-1,1],pairs[1:,0],rtol=0,atol=self.scale*2e-5)):
            raise ValueError('Adjacent authored observations disagree')
        # A fixed first-pose body basis makes componentwise shape preservation
        # equivariant to a common rigid transform and uniform character scale.
        self.positions=(np.concatenate((pairs[:,0],pairs[-1:,1]))-self.origin)@self.basis/self.scale
        secants=np.diff(self.positions,axis=0)/self.seconds[:,None,None]
        self.tangents=np.empty_like(self.positions);self.tangents[0]=secants[0];self.tangents[-1]=secants[-1]
        for j in range(1,len(frames)-1):self.tangents[j]=harmonic_tangent(secants[j-1],secants[j],self.seconds[j-1],self.seconds[j])
        self.source=provider(dict(kind='baseline',baseline='hermite'))
    def __call__(self,index,observed,t):
        if type(index) is not int or not 0<=index<len(self.seconds):raise ValueError('Valid explicit interval index required')
        _,rotations=observed.baseline(t)
        if self.rotation=='source':_,rotations=self.source(observed,t)
        u=np.asarray(t,dtype=float)[:,None,None];a,b=self.positions[index:index+2];h=self.seconds[index]
        points=(2*u**3-3*u**2+1)*a+(u**3-2*u**2+u)*h*self.tangents[index]+(-2*u**3+3*u**2)*b+(u**3-u**2)*h*self.tangents[index+1]
        world=points*self.scale@self.basis.T+self.origin
        result=(world-observed.origin)@observed.basis/observed.scale
        result[np.asarray(t)==0]=observed.positions[0];result[np.asarray(t)==1]=observed.positions[1]
        if not np.isfinite(result).all():raise ValueError('Nonfinite authored trajectory')
        return result,rotations

def prepare(observations,frames,*,rotation='source'):
    return Trajectory(observations,frames,rotation=rotation)
