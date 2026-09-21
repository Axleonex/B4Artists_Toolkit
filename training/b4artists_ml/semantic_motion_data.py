"""Training windows using the exact rest-calibrated real-rig observation schema.
SPDX-License-Identifier: GPL-2.0-or-later
Semantic edges may span several physical bones; no fixed-edge claim is made.
"""
from dataclasses import dataclass
import hashlib
import numpy as np
from rig_observations import encode,SCHEMA
from temporal_data import rotation6,quaternion,quat_matrix,slerp,validate_manifests
from context_data import NAMES
from bvh_data import parse_bvh


@dataclass(frozen=True)
class SemanticSequence:
    rest: np.ndarray
    rest_rotations: np.ndarray
    positions: np.ndarray
    rotations: np.ndarray
    frames: np.ndarray
    dt: float


def from_bvh(motion, fps=30.):
    if not np.isfinite(fps) or fps<=0:raise ValueError('Positive target frame rate required')
    if not np.isfinite(motion.frame_time) or motion.frame_time<=0:raise ValueError('Positive source sample time required')
    positions,rotations=motion.transforms();ids=[motion.names.index(n) for n in NAMES]
    step=max(1,int(round(1/(fps*motion.frame_time))))
    # The existing pinned corpus declares its artificial initial T pose. It is
    # calibration data, never a target or outside-gap motion observation.
    frames=np.arange(1,len(positions),step)
    if len(frames)<2:raise ValueError('Insufficient motion after the calibration pose')
    return SemanticSequence(positions[0,ids].copy(),rotations[0,ids].copy(),
        positions[frames][:,ids].copy(),rotations[frames][:,ids].copy(),frames,motion.frame_time*step)


def observe(sequence,start,end,*,context=True):
    if type(start) is not int or type(end) is not int or not 0<=start<end<len(sequence.positions):
        raise ValueError('Increasing valid observation indices required')
    if not isinstance(context,bool):raise ValueError('Explicit context availability required')
    if context and (start<1 or end+1>=len(sequence.positions)):raise ValueError('Outside-gap observations are unavailable')
    indices=[start,end,start-1 if context else start,end+1 if context else end]
    return encode(sequence.rest,sequence.rest_rotations,sequence.positions[indices],sequence.rotations[indices],
                  duration=(end-start)*sequence.dt,dt=sequence.dt,context=context)


def encode_targets(sequence,indices,observations):
    """Supervised-label conversion, separate from observed input construction."""
    indices=np.asarray(indices)
    if indices.ndim!=1 or indices.dtype.kind not in 'iu' or not len(indices) or np.any((indices<0)|(indices>=len(sequence.positions))):
        raise ValueError('Valid target indices required')
    points=(sequence.positions[indices]-observations.origin)@observations.basis/observations.scale
    rotations=observations.basis.T@sequence.rotations[indices]@np.swapaxes(observations.rest_alignment,-1,-2)
    if not np.isfinite(points).all() or not np.isfinite(rotations).all():raise ValueError('Nonfinite supervised targets')
    return np.concatenate((points,rotation6(rotations)),axis=-1).reshape(len(indices),153)


def baseline(observations,t,*,contextual=False):
    """Procedural baselines only: Cartesian Hermite and quaternion tangent curves."""
    t=np.asarray(t,dtype=float)
    points,rotations=observations.baseline(t)  # Shared validation and SLERP.
    if contextual and observations.context:
        u=t[:,None,None];duration=observations.duration;dt=observations.dt
        h00=2*u**3-3*u**2+1;h10=u**3-2*u**2+u;h01=-2*u**3+3*u**2;h11=u**3-u**2
        a,b,previous,following=observations.positions
        points=h00*a+h10*duration*(a-previous)/dt+h01*b+h11*duration*(following-b)/dt
        q=quaternion(observations.rotations);qa=q[0];qb=np.where(np.sum(qa*q[1],axis=-1,keepdims=True)<0,-q[1],q[1])
        qp=np.where(np.sum(qa*q[2],axis=-1,keepdims=True)<0,-q[2],q[2]);qn=np.where(np.sum(qb*q[3],axis=-1,keepdims=True)<0,-q[3],q[3])
        va=(qa-qp)/dt;vb=(qn-qb)/dt
        va-=qa*np.sum(qa*va,axis=-1,keepdims=True);vb-=qb*np.sum(qb*vb,axis=-1,keepdims=True)
        curve=h00*qa+h10*duration*va+h01*qb+h11*duration*vb
        norm=np.linalg.norm(curve,axis=-1,keepdims=True);fallback=quaternion(rotations)
        rotations=quat_matrix(np.where(norm>1e-8,curve/np.maximum(norm,1e-12),fallback))
    result=np.concatenate((points,rotation6(rotations)),axis=-1).reshape(len(t),153)
    anchors=np.concatenate((observations.positions[:2],rotation6(observations.rotations[:2])),axis=-1).reshape(2,153)
    result[t==0]=anchors[0];result[t==1]=anchors[1]
    return result


def window(sequence,start,end,*,context=True):
    observations=observe(sequence,start,end,context=context)
    indices=np.arange(start,end+1);t=np.arange(end-start+1)/(end-start)
    return dict(schema=SCHEMA,x=observations.features(),observations=observations,t=t,dt=sequence.dt,
        frame=sequence.frames[indices].copy(),gap=end-start,context=context,
        linear=baseline(observations,t),hermite=baseline(observations,t,contextual=True),
        target=encode_targets(sequence,indices,observations))


def load_windows(root,manifest,split,protocol):
    """Existing split ownership and checked bytes; no downloads or split rewriting."""
    validate_manifests([manifest]);windows=[]
    for index,row in enumerate(manifest['files']):
        if row['split']!=split:continue
        path=root/'cache'/(row['clip']+'.bvh')
        if hashlib.sha256(path.read_bytes()).hexdigest()!=row['sha256']:raise ValueError('Source motion checksum mismatch')
        sequence=from_bvh(parse_bvh(path.read_text()),protocol['target_fps']);rng=np.random.default_rng(protocol['seed']+index)
        maximum=protocol['training_windows_per_gap'] if split=='train' else protocol['evaluation_windows_per_gap']
        for gap in protocol['gaps']:
            eligible=np.arange(1,len(sequence.positions)-gap-1)
            starts=np.sort(rng.choice(eligible,min(maximum,len(eligible)),replace=False))
            for context in protocol['contexts']:
                for start in starts:
                    item=window(sequence,int(start),int(start)+gap,context=context);item['clip']=row['clip'];windows.append(item)
    if not windows:raise ValueError('No matching semantic motion windows')
    return windows
