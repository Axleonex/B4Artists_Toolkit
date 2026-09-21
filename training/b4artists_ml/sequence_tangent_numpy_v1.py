"""NumPy inference for inert exported temporal-convolution weights.
SPDX-License-Identifier: GPL-2.0-or-later
Research only; weights are not bundled in the addon.
"""
import math
import numpy as np
DILATIONS=(1,2,4,8,16,32)
def silu(x):return x/(1+np.exp(-np.clip(x,-80,80)))
def linear(x,w,p):return x@w[p+'.weight'].T+w[p+'.bias']
def norm(x,w,p):
 mean=x.mean(axis=-1,keepdims=True);var=((x-mean)**2).mean(axis=-1,keepdims=True)
 return (x-mean)/np.sqrt(var+1e-5)*w[p+'.weight']+w[p+'.bias']
def forward(w,condition,noisy,level):
 c=np.asarray(condition,dtype=np.float32);noise=np.asarray(noisy,dtype=np.float32);lev=np.asarray(level,dtype=np.float32)
 if c.ndim!=3 or c.shape[-1]!=666 or noise.shape!=(*c.shape[:2],153) or lev.shape!=(len(c),) or not all(np.isfinite(a).all() for a in (c,noise,lev)):raise ValueError('Invalid inference inputs')
 phase=lev[:,None]*(np.arange(1,9,dtype=np.float32)[None]*np.float32(math.pi));embedding=np.concatenate((np.sin(phase),np.cos(phase)),axis=-1);embedding=np.broadcast_to(embedding[:,None],(*c.shape[:2],16))
 x=linear(np.concatenate((c,noise,embedding),axis=-1),w,'input')
 for index,dilation in enumerate(DILATIONS):
  p='blocks.'+str(index);z=norm(x,w,p+'.norm');padded=np.pad(z,((0,0),(dilation,dilation),(0,0)));kernel=w[p+'.conv.weight'];out=np.zeros_like(z)+w[p+'.conv.bias']
  for k in range(3):out+=padded[:,k*dilation:k*dilation+z.shape[1]]@kernel[:,:,k].T
  x=x+linear(silu(linear(silu(out),w,p+'.ff1')),w,p+'.ff2')/np.float32(math.sqrt(len(DILATIONS)))
 result=linear(norm(x,w,'norm'),w,'output')
 if not np.isfinite(result).all():raise ValueError('Nonfinite model output')
 return result
