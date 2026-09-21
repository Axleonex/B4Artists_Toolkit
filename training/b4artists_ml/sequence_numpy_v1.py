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
 if c.ndim!=3 or c.shape[-1]!=394 or noise.shape!=(*c.shape[:2],153) or lev.shape!=(len(c),) or not all(np.isfinite(a).all() for a in (c,noise,lev)):raise ValueError('Invalid inference inputs')
 phase=lev[:,None]*(np.arange(1,9,dtype=np.float32)[None]*np.float32(math.pi));embedding=np.concatenate((np.sin(phase),np.cos(phase)),axis=-1);embedding=np.broadcast_to(embedding[:,None],(*c.shape[:2],16))
 x=linear(np.concatenate((c,noise,embedding),axis=-1),w,'input')
 for index,dilation in enumerate(DILATIONS):
  p='blocks.'+str(index);z=norm(x,w,p+'.norm');padded=np.pad(z,((0,0),(dilation,dilation),(0,0)));kernel=w[p+'.conv.weight'];out=np.zeros_like(z)+w[p+'.conv.bias']
  for k in range(3):out+=padded[:,k*dilation:k*dilation+z.shape[1]]@kernel[:,:,k].T
  x=x+linear(silu(linear(silu(out),w,p+'.ff1')),w,p+'.ff2')/np.float32(math.sqrt(len(DILATIONS)))
 result=linear(norm(x,w,'norm'),w,'output')
 if not np.isfinite(result).all():raise ValueError('Nonfinite model output')
 return result

def alpha_schedule(steps=256):
 t=np.arange(steps+1,dtype=np.float64)/steps;a=np.cos((t+.008)/1.008*np.pi/2)**2;a/=a[0]
 beta=np.clip(1-a[1:]/a[:-1],0,.999)
 return np.cumprod(1-beta).astype(np.float32)

def sample(w,condition,mask,*,seed=20260909,steps=20):
 c=np.asarray(condition,dtype=np.float32);m=np.asarray(mask,dtype=bool)
 if m.shape!=(*c.shape[:2],153):raise ValueError('Mask shape mismatch')
 if type(steps)!=int or not 2<=steps<=256:raise ValueError('Invalid denoising step count')
 schedule=alpha_schedule();indices=np.round(np.linspace(255,0,steps)).astype(int);x=np.random.default_rng(seed).normal(size=m.shape).astype(np.float32);x[m]=0
 for k,index in enumerate(indices):
  clean=forward(w,c,x,np.full(len(c),index/255,dtype=np.float32));clean[m]=0
  if k==len(indices)-1:return clean
  a=schedule[index];b=schedule[indices[k+1]];epsilon=(x-np.sqrt(a)*clean)/np.sqrt(1-a);x=np.sqrt(b)*clean+np.sqrt(1-b)*epsilon;x[m]=0
 raise AssertionError('Unreachable')
