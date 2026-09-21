"""Synchronized semantic pose observations with explicit sparse masks.
SPDX-License-Identifier: GPL-2.0-or-later
"""
from dataclasses import dataclass
import hashlib
import json
import numpy as np
from bvh_data import parse_bvh

NAMES=('Hips','Spine','Spine1','Neck1','Head','LeftArm','LeftForeArm','LeftHand',
       'RightArm','RightForeArm','RightHand','LeftUpLeg','LeftLeg','LeftFoot','RightUpLeg','RightLeg','RightFoot')
ROLES=('pelvis','spine','chest','neck','head','upper_arm_L','elbow_L','wrist_L',
       'upper_arm_R','elbow_R','wrist_R','hip_L','knee_L','ankle_L','hip_R','knee_R','ankle_R')
PARENTS=(-1,0,1,2,3,2,5,6,2,8,9,0,11,12,0,14,15)
LIMBS=((5,6,7),(8,9,10),(11,12,13),(14,15,16))
TARGETS=(0,4,7,10,13,16)
JOINTS=len(NAMES)

@dataclass
class SemanticMotion:
    positions: np.ndarray
    rest: np.ndarray
    frames: np.ndarray
    origins: np.ndarray
    bases: np.ndarray
    scale: float


def semantic_motion(motion,stride=8):
    if not isinstance(stride,int) or stride<1:raise ValueError('Stride must be a positive integer')
    indices=[motion.names.index(n) for n in NAMES]
    world,rotations=motion.transforms()
    points=world[:,indices]
    hips=points[0,11]-points[0,14]
    up=(points[0,5]+points[0,8]-points[0,11]-points[0,14])*.5
    scale=float(np.linalg.norm(up))
    if scale<1e-8 or np.linalg.norm(hips)<scale*1e-5:raise ValueError('Degenerate semantic reference')
    left=hips/np.linalg.norm(hips);up-=left*np.dot(up,left)
    if np.linalg.norm(up)<scale*1e-5:raise ValueError('Degenerate torso reference')
    up/=np.linalg.norm(up)
    reference=np.stack((left,np.cross(up,left),up),axis=1)
    hip_rotations=rotations[:,indices[0]]
    # Only the explicitly supplied pelvis pose defines the moving coordinate frame.
    bases=hip_rotations@hip_rotations[0].T@reference
    origins=points[:,0].copy()
    local=np.einsum('fji,fkj->fki',bases,points-origins[:,None,:])/scale
    if not np.isfinite(local).all():raise ValueError('Nonfinite semantic pose')
    frames=np.arange(1,len(local),stride)  # Exclude artificial initial T-pose from labels.
    return SemanticMotion(local[frames],local[0],frames,origins[frames],bases[frames],scale)


def retarget_pose(pose,ratios):
    """Preserve each segment's direction and total limb length at new proportions."""
    out=np.asarray(pose,dtype=float).copy()
    ratios=np.asarray(ratios,dtype=float)
    if out.shape[-2:]!=(JOINTS,3) or ratios.shape!=(4,) or not np.isfinite(out).all() or not np.isfinite(ratios).all() or np.any((ratios<=0)|(ratios>=1)):
        raise ValueError('Invalid proportion request')
    for (root,joint,end),ratio in zip(LIMBS,ratios):
        upper=out[...,joint,:]-out[...,root,:]
        lower=out[...,end,:]-out[...,joint,:]
        a=np.linalg.norm(upper,axis=-1,keepdims=True);b=np.linalg.norm(lower,axis=-1,keepdims=True)
        if np.any(np.minimum(a,b)<1e-8):raise ValueError('Degenerate semantic limb')
        total=a+b
        out[...,joint,:]=out[...,root,:]+upper/a*(total*ratio)
        out[...,end,:]=out[...,joint,:]+lower/b*(total*(1-ratio))
    return out


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


def finish(residual,baseline,observations,mask):
    prediction=np.asarray(baseline)+np.asarray(residual).reshape(np.asarray(baseline).shape)
    return np.where(np.asarray(mask)[...,None],observations,prediction)


def examples(motion,seed,augment=True,mode='mixed'):
    """Build deterministic training/evaluation samples; baseline never equals a label frame."""
    rng=np.random.default_rng(seed)
    n=len(motion.positions)
    if mode not in ('mixed','neutral','prior'):raise ValueError('Unknown baseline mode')
    poses=[];rests=[];baselines=[];masks=[];frame_ids=[];baseline_frames=[]
    variants=(None,np.array([.45,.45,.55,.55]),np.array([.55,.55,.45,.45])) if augment else (None,)
    for ratios in variants:
        targets=motion.positions.copy();rest=motion.rest.copy()
        if ratios is not None:
            targets=retarget_pose(targets,ratios);rest=retarget_pose(rest,ratios)
        previous=np.maximum(np.arange(n)-rng.integers(2,10,size=n),0)
        use_prior=(rng.random(n)<.4) if mode=='mixed' else np.full(n,mode=='prior')
        use_prior&=np.arange(n)>previous
        baseline=np.where(use_prior[:,None,None],targets[previous],rest[None])
        mask=np.zeros((n,JOINTS),bool);mask[:,TARGETS]=rng.random((n,len(TARGETS)))<.8
        mask[:,0]=True
        # Alternate complete five-effector requests and sparse requests, with explicit mask.
        mask[np.arange(n)%3==0]=False
        mask[np.arange(n)%3==0,TARGETS[0]]=True
        for j in TARGETS[1:]:mask[np.arange(n)%3==0,j]=True
        poses.append(targets);rests.append(np.broadcast_to(rest,targets.shape));baselines.append(baseline);masks.append(mask)
        frame_ids.append(motion.frames);baseline_frames.append(np.where(use_prior,motion.frames[previous],0))
    target=np.concatenate(poses);rest=np.concatenate(rests);baseline=np.concatenate(baselines);mask=np.concatenate(masks)
    return dict(x=encode(rest,baseline,target,mask),target=target,rest=rest,baseline=baseline,mask=mask,
                frame=np.concatenate(frame_ids),baseline_frame=np.concatenate(baseline_frames))


def load_examples(directory,manifest,split,seed=20260906,augment=True,mode='mixed'):
    rows=[]
    for i,row in enumerate(manifest['files']):
        if row['split']!=split:continue
        path=directory/'cache'/(row['clip']+'.bvh');data=path.read_bytes()
        if hashlib.sha256(data).hexdigest()!=row['sha256']:raise ValueError('Changed data: '+row['clip'])
        motion=semantic_motion(parse_bvh(data.decode()))
        rows.append((row['clip'],examples(motion,seed+i,augment,mode)))
    return rows
