"""Observed-only sequence requests. Research code; no shipped temporal model.
SPDX-License-Identifier: GPL-2.0-or-later
"""
import numpy as np
from temporal_data import rotation6,rotation_matrix,slerp
J=17;D=153;CONDITION=394

def expanded_mask(mask):
 return np.concatenate((np.repeat(mask[...,:1],3,axis=-1),np.repeat(mask[...,1:],6,axis=-1)),axis=-1)

def request(times,observed,mask,rest):
 t=np.array(times,dtype=np.float64,copy=True);y=np.array(observed,dtype=np.float64,copy=True);m=np.array(mask,copy=True);r=np.array(rest,dtype=np.float64,copy=True)
 if t.ndim!=1 or not 2<=len(t)<=128 or not np.isfinite(t).all() or np.any(np.diff(t)<=0):raise ValueError('Two to128 strictly increasing finite times required')
 if y.shape!=(len(t),J,9) or m.shape!=(len(t),J,2) or m.dtype!=np.bool_ or r.shape!=(J,3) or not np.isfinite(r).all():raise ValueError('Invalid sequence fields')
 if not m[[0,-1]].all():raise ValueError('Complete boundary context required by this research adapter')
 expanded=expanded_mask(m)
 if not np.isfinite(y[expanded]).all():raise ValueError('Observed values must be finite')
 clean=np.where(expanded,y,0.);baseline=np.empty_like(clean)
 for joint in range(J):
  ids=np.flatnonzero(m[:,joint,0])
  for axis in range(3):baseline[:,joint,axis]=np.interp(t,t[ids],clean[ids,joint,axis])
  ids=np.flatnonzero(m[:,joint,1]);rot,bad=rotation_matrix(clean[ids,joint,3:])
  if np.any(bad):raise ValueError('Degenerate observed orientation')
  # Observations must encode rotation columns rather than arbitrary six scalars.
  if not np.allclose(rotation6(rot),clean[ids,joint,3:],atol=1e-6,rtol=0):raise ValueError('Observed orientation is not orthonormal')
  for k in range(len(ids)-1):
   a,b=ids[k:k+2];u=(t[a:b+1]-t[a])/(t[b]-t[a]);baseline[a:b+1,joint,3:]=rotation6(slerp(rot[k][None],rot[k+1][None],u))[:,0]
 baseline[expanded]=clean[expanded]
 relative=t-t[0];duration=relative[-1];timing=np.c_[relative/duration,relative,np.full(len(t),duration)]
 condition=np.c_[baseline.reshape(len(t),D),clean.reshape(len(t),D),m.reshape(len(t),34).astype(float),np.broadcast_to(r.ravel(),(len(t),51)),timing]
 assert condition.shape==(len(t),CONDITION) and np.isfinite(condition).all()
 result={'condition':condition.astype(np.float32),'baseline':baseline.astype(np.float32),'observed':clean,'mask':expanded,'times':t,'rest':r}
 for a in result.values():a.setflags(write=False)
 return result

def restore_observations(proposal,req):
 p=np.array(proposal,dtype=float,copy=True)
 if p.shape!=req['observed'].shape or not np.isfinite(p).all():raise ValueError('Invalid generated sequence')
 p[req['mask']]=req['observed'][req['mask']]
 return p
