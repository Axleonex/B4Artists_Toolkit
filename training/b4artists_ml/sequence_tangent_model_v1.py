"""Controlled extension of the existing sequence backbone; research only."""
import torch
from torch import nn
from sequence_model_v1 import SequenceModel as BaseModel,WIDTH
class SequenceModel(BaseModel):
 def __init__(self):
  super().__init__()
  prior=self.input
  self.input=nn.Linear(835,WIDTH)
  with torch.no_grad():
   self.input.weight.zero_()
   self.input.weight[:,:394].copy_(prior.weight[:,:394])
   self.input.weight[:,666:].copy_(prior.weight[:,394:])
   self.input.bias.copy_(prior.bias)
