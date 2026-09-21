"""Full ancestor-chain temporal windows, known observations separated from labels.
SPDX-License-Identifier: GPL-2.0-or-later
"""
from dataclasses import dataclass
import hashlib
import numpy as np
from bvh_data import parse_bvh
from temporal_data import temporal_motion,features,labels,rotation6,slerp,NAMES
from sequence_kinematics import forward


@dataclass
class SequenceMotion:
    semantic_motion: object
    names: tuple
    parents: tuple
    semantic: tuple
    offsets: np.ndarray
    local_rotation: np.ndarray


def full_motion(source,fps=30):
    sem=temporal_motion(source,fps);ids=set()
    for name in NAMES:
        i=source.names.index(name)
        while i>=0:ids.add(i);i=source.parents[i]
    ids=sorted(ids);lookup={old:new for new,old in enumerate(ids)}
    for i in ids[1:]:
        if any(c.endswith('position') for c in source.channels[i]):raise ValueError('Animated non-root translation is unsupported')
    parents=tuple(-1 if source.parents[i]<0 else lookup[source.parents[i]] for i in ids)
    _,world=source.transforms();world=world[sem.frames][:,ids];local=world.copy()
    for j,p in enumerate(parents[1:],1):local[:,j]=np.swapaxes(world[:,p],-1,-2)@world[:,j]
    return SequenceMotion(sem,tuple(source.names[i] for i in ids),parents,tuple(lookup[source.names.index(n)] for n in NAMES),source.offsets[ids]/sem.scale,local)


def coefficients_basis(t,duration,terms=4):
    t=np.asarray(t);u=2*t-1
    polynomials=np.stack((np.ones_like(u),u,(3*u*u-1)/2,(5*u**3-3*u)/2),axis=-1)
    if terms!=4:raise ValueError('Protocol fixes four temporal coefficients')
    return polynomials*(4*t*(1-t)*duration**2)[:,None]


def known_window(motion,start,end,t,context):
    sem=motion.semantic_motion;d=features(sem,start,end,t,context)
    indices=[start,end,start-1 if context else start,end+1 if context else end]
    local=motion.local_rotation[indices].copy()
    if not np.isfinite(local).all():raise ValueError('Nonfinite observed local rotation')
    local[:,0]=np.einsum('ij,fjk->fik',d['basis'].T,local[:,0])
    roots=(sem.points[indices,0]-d['origin'])@d['basis']/sem.scale
    packed=np.concatenate((roots,rotation6(local).reshape(4,-1)),axis=-1)
    t=np.asarray(t);duration=(end-start)*sem.dt
    root_line=roots[0]*(1-t[:,None])+roots[1]*t[:,None]
    lerp_rotation=rotation6(slerp(local[0],local[1],t)).reshape(len(t),-1)
    linear_local=np.c_[root_line,lerp_rotation]
    hermite_local=np.c_[d['baseline'].reshape(len(t),17,9)[:,0,:3],lerp_rotation]
    x=np.r_[packed.ravel(),motion.offsets.ravel(),float(context),float(context),duration,sem.dt]
    return dict(x=x,baseline=linear_local,hermite_local=hermite_local,offsets=motion.offsets,
                basis_functions=coefficients_basis(t,duration),origin=d['origin'],basis=d['basis'],linear=d['linear'],hermite=d['baseline'])


def target_window(motion,indices,origin,basis):
    sem=motion.semantic_motion;local=motion.local_rotation[indices].copy()
    local[:,0]=np.einsum('ij,fjk->fik',basis.T,local[:,0])
    root=(sem.points[indices,0]-origin)@basis/sem.scale
    return np.c_[root,rotation6(local).reshape(len(indices),-1)],labels(sem,indices,origin,basis)


def load_windows(root,manifest,split,protocol):
    windows=[];skeleton=None
    for index,row in enumerate(manifest['files']):
        if row['split']!=split:continue
        path=root/'cache'/(row['clip']+'.bvh')
        if hashlib.sha256(path.read_bytes()).hexdigest()!=row['sha256']:raise ValueError('Source motion checksum mismatch')
        motion=full_motion(parse_bvh(path.read_text()),protocol['target_fps'])
        identity=(motion.names,motion.parents,motion.semantic)
        if skeleton is not None and identity!=skeleton:raise ValueError('Inconsistent source topology')
        skeleton=identity;sem=motion.semantic_motion;rng=np.random.default_rng(protocol['seed']+index)
        maximum=protocol['training_windows_per_gap'] if split=='train' else protocol['evaluation_windows_per_gap']
        for gap in protocol['gaps']:
            eligible=np.arange(1,len(sem.points)-gap-1);starts=np.sort(rng.choice(eligible,min(maximum,len(eligible)),replace=False))
            for context in protocol['contexts']:
                for start in starts:
                    start=int(start);end=start+gap;indices=np.arange(start,end+1);t=np.arange(gap+1)/gap
                    d=known_window(motion,start,end,t,context)
                    local,target=target_window(motion,indices,d.pop('origin'),d.pop('basis'))
                    d.update(target_local=local,target=target,t=t,dt=sem.dt,gap=gap,context=context,clip=row['clip'],frame=sem.frames[indices])
                    windows.append(d)
    if not windows:raise ValueError('No sequence windows')
    return windows,skeleton


def semantic_output(local,offsets,skeleton):
    _,parents,semantic=skeleton;p,r,_=forward(local,offsets,parents)
    return np.concatenate((p[...,semantic,:],rotation6(r[...,semantic,:,:])),axis=-1).reshape(local.shape[:-1]+(153,))
