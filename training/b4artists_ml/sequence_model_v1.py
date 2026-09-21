"""Original temporal-convolution research backbone, direct or denoising objective.
SPDX-License-Identifier: GPL-2.0-or-later
Untrained construction is not a functional animation model.
"""
import math
import torch
from torch import nn
WIDTH=128;D=153;CONDITION=394;DILATIONS=(1,2,4,8,16,32)
class Block(nn.Module):
 def __init__(self,dilation):
  super().__init__();self.norm=nn.LayerNorm(WIDTH);self.conv=nn.Conv1d(WIDTH,WIDTH,3,padding=dilation,dilation=dilation);self.ff1=nn.Linear(WIDTH,WIDTH*2);self.ff2=nn.Linear(WIDTH*2,WIDTH)
 def forward(self,x):
  z=self.norm(x);z=self.conv(z.transpose(1,2)).transpose(1,2);z=torch.nn.functional.silu(z);return x+self.ff2(torch.nn.functional.silu(self.ff1(z)))/math.sqrt(len(DILATIONS))
class SequenceModel(nn.Module):
 def __init__(self):
  super().__init__();self.input=nn.Linear(CONDITION+D+16,WIDTH);self.blocks=nn.ModuleList([Block(d) for d in DILATIONS]);self.norm=nn.LayerNorm(WIDTH);self.output=nn.Linear(WIDTH,D);nn.init.zeros_(self.output.weight);nn.init.zeros_(self.output.bias)
 def forward(self,condition,noisy,level):
  frequencies=torch.arange(1,9,dtype=condition.dtype,device=condition.device)*math.pi
  phase=level[:,None]*frequencies[None];embedding=torch.cat((torch.sin(phase),torch.cos(phase)),dim=-1)[:,None].expand(-1,condition.shape[1],-1)
  x=self.input(torch.cat((condition,noisy,embedding),dim=-1))
  for block in self.blocks:x=block(x)
  return self.output(self.norm(x))
