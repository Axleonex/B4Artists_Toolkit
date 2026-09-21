"""Research-only lifecycle owner for private-rig sequence projection.
SPDX-License-Identifier: GPL-2.0-or-later
Uses the unchanged generator code with an isolated global dictionary for the
transaction dependency. This avoids process-global monkeypatching; production
integration must replace it with an explicit shared generator dependency.
"""
import time,types
import bpy
from b4artists_ml import temporal_generation as generation,body_proxy,workflow as w
class PrivateTransaction(generation.Transaction):
 def pause(self,progress,cancel_requested):
  yield progress
  if cancel_requested is not None and cancel_requested():raise InterruptedError('Private work cancelled')

def private_generator(*args,**kwargs):
 function=generation._generate_steps
 scope=dict(function.__globals__);scope['Transaction']=PrivateTransaction
 isolated=types.FunctionType(function.__code__,scope,function.__name__,function.__defaults__);isolated.__kwdefaults__=function.__kwdefaults__
 return isolated(*args,**kwargs)

class PrivateSequenceJob:
 def __init__(self,obj,predictor,*,chunk_seconds=.02,**options):
  if not 0<=chunk_seconds<=.1:raise ValueError("Invalid private chunk budget")
  self.chunk_seconds=chunk_seconds
  if obj.as_pointer() in generation._OWNERS:raise ValueError('Source already owned')
  self.obj=obj;self.scene=bpy.context.scene;self.key=obj.as_pointer();self.guard=generation.Transaction(obj,self.scene);self.proxy=body_proxy.EvaluationProxy(obj,(),defer=True);self.preparation=None;self.iterator=None;self.predictor=predictor;self.options=options;self.closed=False;self.running=False;self.reason=None;self.last_chunk_seconds=0
  generation._OWNERS[self.key]=self.guard;generation._LIVE[id(self)]=self;generation.register()
  try:
   self.guard.guard();self.preparation=self.proxy.prepare_steps(obj,[p.name for p in obj.pose.bones])
  except BaseException:self.close();raise
 def __iter__(self):return self
 def context(self):
  layer=self.proxy.scene.view_layers[0]
  return bpy.context.temp_override(scene=self.proxy.scene,view_layer=layer,object=self.proxy.obj,active_object=self.proxy.obj,selected_objects=[self.proxy.obj],selected_editable_objects=[self.proxy.obj])
 def __next__(self):
  if self.reason is not None:raise InterruptedError(self.reason)
  if self.closed:raise StopIteration
  started=time.perf_counter();self.running=True;finished=False;answer=None
  try:
   self.guard.guard()
   if self.preparation is not None:
    try:phase=next(self.preparation);progress=dict(phase='private_'+phase)
    except StopIteration:
     self.preparation=None;w.assign_action(self.proxy.obj,self.obj.animation_data.action,w._slot(self.obj.animation_data));self.iterator=private_generator(self.proxy.obj,self.predictor,**self.options);progress=dict(phase='private_ready')
   else:
    advanced=False
    with self.context():
     while not advanced or time.perf_counter()-started<self.chunk_seconds:
      try:progress=next(self.iterator);advanced=True
      except StopIteration as done:answer=done.value;finished=True;break
   self.guard.guard()
  except BaseException:
   self.running=False;self.close();raise
  finally:
   self.running=False;self.last_chunk_seconds=time.perf_counter()-started
  if self.reason is not None:
   self.close();raise InterruptedError(self.reason)
  if finished:
   self.close();raise StopIteration(answer)
  return progress
 def close(self):
  if self.closed:return
  if self.running:raise RuntimeError('Cannot close private work during its step')
  try:
   if self.iterator is not None:
    with self.context():self.iterator.close()
   if self.preparation is not None:self.preparation.close()
  finally:
   self.proxy.close();self.closed=True;generation._LIVE.pop(id(self),None)
   if generation._OWNERS.get(self.key) is self.guard:generation._OWNERS.pop(self.key,None)
 def cancel(self,reason='Private generation cancelled'):
  self.reason=reason
  if not self.running:self.close()
