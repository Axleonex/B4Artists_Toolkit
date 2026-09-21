"""Bridge sequence research inference to the protected semantic benchmark schema.
SPDX-License-Identifier: GPL-2.0-or-later
No automatic downloads, host registration or qualified model is supplied.
"""
import hashlib,zipfile
from pathlib import Path
import numpy as np
from sequence_conditioning_v1 import request,restore_observations
from sequence_numpy_v1 import forward,sample
from temporal_data import rotation6,rotation_matrix,slerp
from semantic_motion_data import baseline

def load_weights(path,expected_sha256):
 path=Path(path)
 if path.stat().st_size>5*1024**2 or hashlib.sha256(path.read_bytes()).hexdigest()!=expected_sha256:raise ValueError('Weight identity mismatch')
 shapes={'input.weight':(128,563),'input.bias':(128,),'norm.weight':(128,),'norm.bias':(128,),'output.weight':(153,128),'output.bias':(153,)}
 for i in range(6):
  for key,shape in {'norm.weight':(128,),'norm.bias':(128,),'conv.weight':(128,128,3),'conv.bias':(128,),'ff1.weight':(256,128),'ff1.bias':(256,),'ff2.weight':(128,256),'ff2.bias':(128,)}.items():shapes[f'blocks.{i}.'+key]=shape
 with zipfile.ZipFile(path) as z:
  if len(z.infolist())!=len(shapes) or sum(i.file_size for i in z.infolist())>5*1024**2:raise ValueError('Unexpected weight archive')
 with np.load(path,allow_pickle=False) as z:
  if set(z.files)!=set(shapes):raise ValueError('Unexpected parameter set')
  weights={k:z[k] for k in z.files}
 for k,v in weights.items():
  if v.dtype!=np.float32 or v.shape!=shapes[k] or not np.isfinite(v).all():raise ValueError('Invalid parameter:'+k)
  v.setflags(write=False)
 return weights

def observed_request(o):
 duration=float(o.duration);dt=float(o.dt)
 if o.schema!='b4ml-semantic-observations-v1' or not np.isfinite([duration,dt]).all() or dt<=0 or duration<dt or not isinstance(o.context,(bool,np.bool_)):raise ValueError('Unsupported observations')
 ratio=duration/dt
 if ratio>127:raise ValueError('Sequence length exceeds model budget')
 interior=np.arange(1,int(np.floor(ratio))+1)*dt;interior=interior[interior<duration-1e-9*dt];times=np.r_[0.,interior,duration]
 if o.context:times=np.r_[-dt,times,duration+dt]
 if len(times)>128:raise ValueError('Sequence context exceeds model budget')
 known=np.zeros((len(times),17,9));mask=np.zeros((len(times),17,2),bool)
 locations=[(1 if o.context else 0,0),(-2 if o.context else -1,1)]
 if o.context:locations += [(0,2),(-1,3)]
 for index,source in locations:known[index]=np.concatenate((o.positions[source],rotation6(o.rotations[source])),axis=-1);mask[index]=True
 return request(times,known,mask,o.rest),times

class Provider:
 def __init__(self,path,expected_sha256,*,kind,seed=20260909):
  if kind not in ('direct','diffusion'):raise ValueError('Unknown sequence objective')
  self.weights=load_weights(path,expected_sha256);self.kind=kind;self.seed=seed;self._cache=None
 def predict_packed(self,o,t):
  t=np.asarray(t,dtype=float)
  if t.ndim!=1 or not np.isfinite(t).all() or np.any((t<0)|(t>1)):raise ValueError('Invalid query times')
  req,times=observed_request(o);n=4 if o.context else 2
  # Identical authored observations express a default hold. Movement from a
  # hold requires another authored pose or future explicit intent conditioning.
  if np.array_equal(o.positions[:n],np.broadcast_to(o.positions[0],o.positions[:n].shape)) and np.array_equal(o.rotations[:n],np.broadcast_to(o.rotations[0],o.rotations[:n].shape)):return baseline(o,t)
  digest=hashlib.sha256()
  for key in ('condition','observed','mask','times'):digest.update(req[key].tobytes())
  key=digest.hexdigest()
  if self._cache is None or self._cache[0]!=key:
   cond=req['condition'][None];m=req['mask'][None].reshape(1,len(times),153)
   residual=forward(self.weights,cond,np.zeros((1,len(times),153),np.float32),np.zeros(1,np.float32)) if self.kind=='direct' else sample(self.weights,cond,m,seed=self.seed)
   packed=restore_observations(req['baseline']+residual[0].reshape(len(times),17,9),req);rot,bad=rotation_matrix(packed[...,3:])
   if bad.any():raise ValueError('Generated rotation is degenerate')
   self._cache=(key,packed.copy(),rot.copy())
  _,packed,rot=self._cache;query=t*o.duration;points=np.empty((len(t),17,3));angles=np.empty((len(t),17,3,3))
  for j in range(17):
   for axis in range(3):points[:,j,axis]=np.interp(query,times,packed[:,j,axis])
  indices=np.clip(np.searchsorted(times,query,side='right')-1,0,len(times)-2)
  for index in np.unique(indices):
   rows=np.flatnonzero(indices==index);u=(query[rows]-times[index])/(times[index+1]-times[index]);angles[rows]=slerp(rot[index],rot[index+1],u)
  result=np.concatenate((points,rotation6(angles)),axis=-1).reshape(len(t),153);anchors=np.concatenate((o.positions[:2],rotation6(o.rotations[:2])),axis=-1).reshape(2,153);result[t==0]=anchors[0];result[t==1]=anchors[1]
  return result
