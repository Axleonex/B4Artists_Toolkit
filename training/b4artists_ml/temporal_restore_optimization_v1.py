"""Research-only selective restoration; no cached source-validation decisions."""
import temporal_cooperative_v1 as cooperative
from temporal_projection import _frame,p

class SelectiveVisibleState(cooperative.VisibleState):
    def restore(self):
        if p._frame(self.scene)!=self.frame:_frame(self.scene,self.frame)
        for name,value in self.channels.items():
            if tuple(getattr(self.obj,name))!=value:setattr(self.obj,name,value)
        for name,value in self.pose.items():
            bone=self.obj.pose.bones.get(name)
            if bone is None:continue
            for field in ('location','scale'):
                if tuple(getattr(bone,field))!=tuple(value[field]):setattr(bone,field,value[field])
            field='rotation_quaternion' if value['mode']=='QUATERNION' else 'rotation_axis_angle' if value['mode']=='AXIS_ANGLE' else 'rotation_euler'
            if tuple(getattr(bone,field))!=tuple(value['raw_rotation']):setattr(bone,field,value['raw_rotation'])
        for name,properties in self.modes.items():
            bone=self.obj.pose.bones.get(name)
            if bone is not None:
                for key,value in properties.items():
                    if key in bone and bone[key]!=value:bone[key]=value
        # Keep one explicit final evaluation even if all values already match.
        # Structural, curve, pose, anchor and mode guards remain unchanged.
        p._update(self.obj)
