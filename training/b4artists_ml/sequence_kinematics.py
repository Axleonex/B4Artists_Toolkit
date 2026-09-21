"""Differentiable full-ancestry rotations and forward kinematics for temporal learning.
SPDX-License-Identifier: GPL-2.0-or-later
"""
import numpy as np


def rotation_forward(v):
    a=v[...,:3];b=v[...,3:];na=np.linalg.norm(a,axis=-1,keepdims=True)
    x=a/np.maximum(na,1e-12);c=np.sum(x*b,axis=-1,keepdims=True);u=b-x*c;nu=np.linalg.norm(u,axis=-1,keepdims=True)
    if np.any(na<1e-8) or np.any(nu<1e-8) or not np.isfinite(v).all():raise ValueError('Degenerate learned rotation')
    y=u/nu;return np.stack((x,y,np.cross(x,y)),axis=-1),(x,y,b,c,na,nu)


def rotation_backward(g,cache):
    x,y,b,c,na,nu=cache
    gx=g[...,0]+np.cross(y,g[...,2]);gy=g[...,1]+np.cross(g[...,2],x)
    gu=(gy-y*np.sum(y*gy,axis=-1,keepdims=True))/nu
    gb=gu-x*np.sum(x*gu,axis=-1,keepdims=True)
    gx-=c*gu+b*np.sum(x*gu,axis=-1,keepdims=True)
    ga=(gx-x*np.sum(x*gx,axis=-1,keepdims=True))/na
    return np.concatenate((ga,gb),axis=-1)


def forward(local,offsets,parents):
    """local shape (...,3+6*joints), offsets broadcastable to (...,joints,3)."""
    local=np.asarray(local);joints=len(parents)
    if local.shape[-1]!=3+6*joints or parents[0]!=-1 or any(not 0<=p<i for i,p in enumerate(parents[1:],1)):raise ValueError('Invalid kinematic hierarchy')
    rotations,cache=rotation_forward(local[...,3:].reshape(local.shape[:-1]+(joints,6)))
    offsets=np.broadcast_to(offsets,local.shape[:-1]+(joints,3))
    positions=np.zeros(local.shape[:-1]+(joints,3));world=np.zeros(local.shape[:-1]+(joints,3,3))
    positions[...,0,:]=local[...,:3];world[...,0,:,:]=rotations[...,0,:,:]
    for j,p in enumerate(parents[1:],1):
        positions[...,j,:]=positions[...,p,:]+np.einsum('...ij,...j->...i',world[...,p,:,:],offsets[...,j,:])
        world[...,j,:,:]=world[...,p,:,:]@rotations[...,j,:,:]
    return positions,world,(rotations,world,offsets,cache,parents)


def backward(position_grad,rotation_grad,cache):
    rotations,world,offsets,rotation_cache,parents=cache
    gp=position_grad.copy();gr=rotation_grad.copy();gl=np.zeros_like(rotations)
    for j in range(len(parents)-1,0,-1):
        p=parents[j]
        gl[...,j,:,:]=np.swapaxes(world[...,p,:,:],-1,-2)@gr[...,j,:,:]
        gr[...,p,:,:]+=gr[...,j,:,:]@np.swapaxes(rotations[...,j,:,:],-1,-2)
        gr[...,p,:,:]+=gp[...,j,:,None]*offsets[...,j,None,:]
        gp[...,p,:]+=gp[...,j,:]
    gl[...,0,:,:]=gr[...,0,:,:]
    gv=rotation_backward(gl,rotation_cache).reshape(gp.shape[:-2]+(-1,))
    return np.concatenate((gp[...,0,:],gv),axis=-1)


def sequence_loss(local,offsets,parents,semantic,target_position,target_rotation,dt,velocity_weight=.01,acceleration_weight=.0001,rotation_weight=.1):
    """Whole windows are differentiated jointly; never join unrelated motion windows."""
    pos,rot,cache=forward(local,offsets,parents)
    selected=pos[...,semantic,:];selected_rot=rot[...,semantic,:,:]
    error=selected-target_position;re=selected_rot-target_rotation
    loss=.5*np.mean(error[:,1:-1]**2)+.5*rotation_weight*np.mean(re[:,1:-1]**2)
    gp=np.zeros_like(error);gr=np.zeros_like(re)
    gp[:,1:-1]=error[:,1:-1]/error[:,1:-1].size
    gr[:,1:-1]=rotation_weight*re[:,1:-1]/re[:,1:-1].size
    h=np.asarray(dt)[:,None,None,None]
    ve=np.diff(error,axis=1)/h;vg=velocity_weight*ve/ve.size/h
    gp[:,1:]+=vg;gp[:,:-1]-=vg;loss+=.5*velocity_weight*np.mean(ve**2)
    ae=np.diff(error,n=2,axis=1)/h**2;ag=acceleration_weight*ae/ae.size/h**2
    gp[:,2:]+=ag;gp[:,1:-1]-=2*ag;gp[:,:-2]+=ag;loss+=.5*acceleration_weight*np.mean(ae**2)
    fullp=np.zeros_like(pos);fullr=np.zeros_like(rot);fullp[...,semantic,:]=gp;fullr[...,semantic,:,:]=gr
    return float(loss),backward(fullp,fullr,cache)
