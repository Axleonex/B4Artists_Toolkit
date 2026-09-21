"""Strict BVH position decoding and anatomical limb features for training.

Channel rotations follow their declared intrinsic order. Bone offsets are in the
parent frame. Units cancel under limb-length normalization. No marker/finger inference.
"""
from dataclasses import dataclass
import re
import numpy as np

@dataclass
class Motion:
    names: list
    parents: list
    offsets: np.ndarray
    channels: list
    values: np.ndarray
    frame_time: float

    def positions(self):
        return self.transforms()[0]

    def transforms(self):
        frames=len(self.values)
        rotations=np.zeros((frames,len(self.names),3,3))
        positions=np.zeros((frames,len(self.names),3))
        cursor=0
        for j,(parent,channels) in enumerate(zip(self.parents,self.channels)):
            rotation=np.broadcast_to(np.eye(3),(frames,3,3)).copy()
            translation=np.broadcast_to(self.offsets[j],(frames,3)).copy()
            for channel in channels:
                value=self.values[:,cursor];cursor+=1
                axis='XYZ'.index(channel[0])
                if channel.endswith('position'):
                    translation[:,axis]+=value
                else:
                    angle=np.deg2rad(value);c,s=np.cos(angle),np.sin(angle)
                    matrix=np.broadcast_to(np.eye(3),(frames,3,3)).copy()
                    a,b=((1,2),(2,0),(0,1))[axis]
                    matrix[:,a,a]=matrix[:,b,b]=c
                    matrix[:,a,b]=-s;matrix[:,b,a]=s
                    rotation=rotation@matrix
            if parent<0:
                positions[:,j]=translation
                rotations[:,j]=rotation
            else:
                positions[:,j]=positions[:,parent]+np.einsum('fij,fj->fi',rotations[:,parent],translation)
                rotations[:,j]=rotations[:,parent]@rotation
        return positions,rotations


def parse_bvh(text):
    header,body=text.split('MOTION',1)
    tokens=re.findall(r'[^\s{}]+|[{}]',header)
    i=0;names=[];parents=[];offsets=[];channels=[]
    def take(expected=None):
        nonlocal i
        if i >= len(tokens):
            raise ValueError('Truncated BVH hierarchy')
        result=tokens[i];i+=1
        if expected is not None and result!=expected:
            raise ValueError(f'Expected {expected}, got {result}')
        return result
    def joint(parent):
        kind=take()
        if kind=='End':
            take('Site');name=names[parent]+'__end'
        elif kind in {'ROOT','JOINT'}:
            name=take()
        else:
            raise ValueError('Unexpected joint type')
        index=len(names);names.append(name);parents.append(parent);offsets.append(None);channels.append([])
        take('{');take('OFFSET');offsets[index]=[float(take()) for _ in range(3)]
        if kind!='End':
            take('CHANNELS');count=int(take())
            if not 0 <= count <= 6:
                raise ValueError('Invalid BVH channel count')
            channels[index]=[take() for _ in range(count)]
            allowed={axis+suffix for axis in 'XYZ' for suffix in ('rotation','position')}
            if any(c not in allowed for c in channels[index]) or len(set(channels[index]))!=count:
                raise ValueError('Invalid BVH channels')
        while i < len(tokens) and tokens[i]!='}':
            joint(index)
        take('}')
    take('HIERARCHY');joint(-1)
    if i!=len(tokens) or len(set(names))!=len(names) or not np.isfinite(offsets).all():
        raise ValueError('Unexpected hierarchy contents')
    match=re.fullmatch(r'\s*Frames:\s*(\d+)\s*Frame Time:\s*([0-9.eE+-]+)\s*(.*)',body,re.S)
    if not match:
        raise ValueError('Invalid BVH motion header')
    frames=int(match[1]);dt=float(match[2]);count=sum(map(len,channels))
    values=np.fromstring(match[3],sep=' ')
    if len(values)!=frames*count or frames<2 or not np.isfinite(values).all() or not 0<dt<1:
        raise ValueError('Invalid BVH frame data')
    return Motion(names,parents,np.asarray(offsets),channels,values.reshape(frames,count),dt)


def limb_samples(motion,stride=8):
    # Exclude the conversion's artificial T pose, then sample 15 Hz from 120 Hz data.
    if not isinstance(stride, int) or stride < 1:
        raise ValueError('Stride must be a positive integer')
    points=motion.positions()[1::stride]
    index={n:i for i,n in enumerate(motion.names)}
    at=lambda name:points[:,index[name]]
    origin=(at('LeftUpLeg')+at('RightUpLeg'))*.5
    left=at('LeftUpLeg')-at('RightUpLeg')
    left/=np.linalg.norm(left,axis=1,keepdims=True)
    up=(at('LeftArm')+at('RightArm'))*.5-origin
    up-=left*np.sum(up*left,axis=1,keepdims=True)
    up/=np.linalg.norm(up,axis=1,keepdims=True)
    back=np.cross(up,left)
    basis=np.stack((left,back,up),axis=2)
    result={}
    for kind,parts in (('arm',('Arm','ForeArm','Hand')),('leg',('UpLeg','Leg','Foot'))):
        inputs=[];outputs=[];geometry=[]
        for side in ('Left','Right'):
            root,joint,end=(at(side+part) for part in parts)
            upper=np.linalg.norm(joint-root,axis=1,keepdims=True)
            lower=np.linalg.norm(end-joint,axis=1,keepdims=True)
            total=upper+lower
            local_root=np.einsum('fji,fj->fi',basis,root-origin)/total
            delta=np.einsum('fji,fj->fi',basis,end-root)/total
            bend=np.einsum('fji,fj->fi',basis,joint-root)/total
            axis=delta/np.maximum(np.linalg.norm(delta,axis=1,keepdims=True),1e-8)
            plane=bend-axis*np.sum(bend*axis,axis=1,keepdims=True)
            height=np.linalg.norm(plane,axis=1,keepdims=True)
            # Mirror right to left so both sides share a learned anatomical prior.
            if side=='Right':
                local_root[:,0]*=-1;delta[:,0]*=-1;plane[:,0]*=-1;axis[:,0]*=-1
            valid=(height[:,0]>.025)&np.isfinite(local_root).all(axis=1)&(total[:,0]>1e-6)
            x=np.concatenate((local_root,delta,upper/total),axis=1)
            y=plane/np.maximum(height,1e-8)
            inputs.append(x[valid]);outputs.append(y[valid])
            geometry.append(np.concatenate((axis,height),axis=1)[valid])
        result[kind]=(np.concatenate(inputs),np.concatenate(outputs),np.concatenate(geometry))
    return result
