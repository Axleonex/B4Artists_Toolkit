"""Research candidates: same source comparison fields, less reconstruction."""
import numpy as np
from b4artists_ml import temporal_generation as g,workflow as w,rig_state as rs,posing as p

def stream_pose_matches(obj,expected):
 bones=obj.pose.bones
 if len(bones)!=len(expected):return False
 for bone in bones:
  v=expected.get(bone.name)
  if v is None or bone.rotation_mode!=v['mode']:return False
  field='rotation_quaternion' if v['mode']=='QUATERNION' else 'rotation_axis_angle' if v['mode']=='AXIS_ANGLE' else 'rotation_euler'
  if tuple(bone.location)!=v['location'] or tuple(bone.scale)!=v['scale'] or tuple(getattr(bone,field))!=v['raw_rotation'] or w._rotation(bone)!=v['rotation']:return False
  channels=v['channels'];connected=bone.bone.use_connect
  if [i for i,lock in enumerate(bone.lock_location) if not lock and not connected]!=channels['location'] or [i for i,lock in enumerate(bone.lock_scale) if not lock]!=channels['scale']:return False
  if (not any(bone.lock_rotation) and not (bone.rotation_mode=='QUATERNION' and bone.lock_rotations_4d and bone.lock_rotation_w))!=channels['rotation']:return False
 return True

class BulkPose:
 def __init__(self,pose):
  self.pose=pose;self.names=tuple(pose);self.modes=tuple(pose[n]['mode'] for n in self.names);n=len(pose)
  self.expected={field:np.asarray([pose[name][field] for name in self.names],dtype=np.float64).reshape(n,3) for field in ('location','scale')}
  self.buffers={field:np.empty((n,width),dtype=dtype) if width>1 else np.empty(n,dtype=dtype) for field,width,dtype in [('location',3,float),('scale',3,float),('rotation_euler',3,float),('rotation_quaternion',4,float),('rotation_axis_angle',4,float),('lock_location',3,bool),('lock_scale',3,bool),('lock_rotation',3,bool),('lock_rotations_4d',1,bool),('lock_rotation_w',1,bool)]}
  self.raw={}
  for field,mode in [('rotation_quaternion','QUATERNION'),('rotation_axis_angle','AXIS_ANGLE'),('rotation_euler',None)]:
   ids=np.array([i for i,m in enumerate(self.modes) if (m==mode if mode else m not in ('QUATERNION','AXIS_ANGLE'))],dtype=np.intp)
   self.raw[field]=(ids,np.array([pose[self.names[i]]['raw_rotation'] for i in ids],dtype=float).reshape(len(ids),3 if mode is None else 4))
  self.location_allowed=np.array([[i in pose[name]['channels']['location'] for i in range(3)] for name in self.names],bool).reshape(n,3);self.scale_allowed=np.array([[i in pose[name]['channels']['scale'] for i in range(3)] for name in self.names],bool).reshape(n,3);self.rotation_allowed=np.array([pose[name]['channels']['rotation'] for name in self.names],bool);self.quaternion=np.array([m=='QUATERNION' for m in self.modes],bool)
 def matches(self,obj):
  bones=obj.pose.bones;live=tuple(bones)
  if len(live)!=len(self.names):return False
  if tuple(b.name for b in live)!=self.names:return self.pose==w.raw_pose(obj)
  if tuple(b.rotation_mode for b in live)!=self.modes:return False
  try:
   for field in ('location','scale'):
    buffer=self.buffers[field];bones.foreach_get(field,buffer.ravel())
    if not np.array_equal(buffer,self.expected[field]):return False
   for field,(ids,expected) in self.raw.items():
    if len(ids):
     buffer=self.buffers[field];bones.foreach_get(field,buffer.ravel())
     if not np.array_equal(buffer[ids],expected):return False
   for field in ('lock_location','lock_scale','lock_rotation','lock_rotations_4d','lock_rotation_w'):bones.foreach_get(field,self.buffers[field].ravel())
  except (AttributeError,TypeError,RuntimeError):
   # Unsupported batch reads retain the original complete comparison.
   return self.pose==w.raw_pose(obj)
  connected=np.fromiter((b.bone.use_connect for b in live),dtype=bool,count=len(live))
  if not np.array_equal(~self.buffers['lock_location']&~connected[:,None],self.location_allowed) or not np.array_equal(~self.buffers['lock_scale'],self.scale_allowed):return False
  rotation_allowed=~self.buffers['lock_rotation'].any(axis=1)&~(self.quaternion&self.buffers['lock_rotations_4d']&self.buffers['lock_rotation_w'])
  if not np.array_equal(rotation_allowed,self.rotation_allowed):return False
  # Retain derived quaternion comparison too: no assumption about RNA/Euler internals.
  return all(w._rotation(b)==self.pose[b.name]['rotation'] for b in live)

class StreamingVisibleState(g.VisibleState):
 def matches(self):
  return (self.frame==p._frame(self.scene) and stream_pose_matches(self.obj,self.pose) and self.modes==rs.mode_values(self.obj) and all(tuple(getattr(self.obj,n))==v for n,v in self.channels.items()))

class BulkVisibleState(g.VisibleState):
 def __init__(self,obj,scene):
  super().__init__(obj,scene);self.bulk=BulkPose(self.pose)
 def matches(self):
  return (self.frame==p._frame(self.scene) and self.bulk.matches(self.obj) and self.modes==rs.mode_values(self.obj) and all(tuple(getattr(self.obj,n))==v for n,v in self.channels.items()))
