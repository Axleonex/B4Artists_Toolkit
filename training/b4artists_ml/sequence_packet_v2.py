"""Sequence windows in the same rest-calibrated representation as native rigs.
SPDX-License-Identifier: GPL-2.0-or-later
"""
import numpy as np
import semantic_motion_data as semantic
from sequence_conditioning_v1 import request

def packet(sequence,start,end,*,context,pattern=0):
 if pattern not in (0,1,2):raise ValueError('Unknown observation pattern')
 observed=semantic.observe(sequence,start,end,context=context);lo=start-1 if context else start;hi=end+1 if context else end;ids=np.arange(lo,hi+1);gap=end-start
 target=semantic.encode_targets(sequence,ids,observed).reshape(len(ids),17,9)
 mask=np.zeros((len(ids),17,2),bool);mask[[0,-1]]=True
 if context:mask[[1,-2]]=True
 offset=int(context)
 if pattern==1:mask[offset+gap//2]=True
 elif pattern==2:
  mask[offset+gap//3,[0,7,13],0]=True;mask[offset+2*gap//3,[4,10,16],1]=True
 req=request(np.arange(len(ids))*sequence.dt,target,mask,observed.rest)
 return dict(request=req,target=target,indices=ids,observations=observed,mask=mask)
