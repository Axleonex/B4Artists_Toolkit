"""Temporary, dependency-closed host evaluation copies for contextual fitting.
SPDX-License-Identifier: GPL-2.0-or-later
"""
import json
import re
import bpy

_BONE = re.compile(r'(?:pose\.)?bones\[("(?:[^"\\]|\\.)*")\]')


def path_bones(path):
    return {json.loads(m.group(1)) for m in _BONE.finditer(path)}


def dependency_bones(obj, seeds):
    """Conservatively retain parent, constraint, B-bone and driver dependencies."""
    if obj.constraints or obj.parent:
        raise ValueError('Proxy requires an unparented rig without object constraints')
    names=set(seeds)
    drivers=[fc for owner in (obj,obj.data) if owner.animation_data for fc in owner.animation_data.drivers]
    while True:
        before=set(names)
        # An IK owner can write an ancestor already needed by another branch.
        for pb in obj.pose.bones:
            for c in pb.constraints:
                if c.type not in ('IK','SPLINE_IK'):continue
                ancestor=pb;chain=set();remaining=c.chain_count or len(obj.pose.bones)
                while ancestor and remaining:
                    chain.add(ancestor.name);ancestor=ancestor.parent;remaining-=1
                if chain & names:names.update(chain)
        for name in tuple(names):
            pb=obj.pose.bones.get(name)
            if pb is None:raise ValueError('Missing proxy dependency: '+name)
            if pb.parent:names.add(pb.parent.name)
            for field in ('bbone_custom_handle_start','bbone_custom_handle_end'):
                handle=getattr(pb,field,None)
                if handle:names.add(handle.name)
            for c in pb.constraints:
                # Include even muted/zero-influence constraints: drivers can enable them.
                for prop in c.bl_rna.properties:
                    if prop.type=='POINTER' and prop.identifier not in ('rna_type',):
                        target=getattr(c,prop.identifier,None)
                        if isinstance(target,bpy.types.Object) and target!=obj:
                            raise ValueError('External constraint target is not proxy-compatible')
                if getattr(c,'target',None)==obj:
                    sub=getattr(c,'subtarget','')
                    if sub:names.add(sub)
                if getattr(c,'pole_target',None)==obj:
                    sub=getattr(c,'pole_subtarget','')
                    if sub:names.add(sub)
                if getattr(c,'space_object',None)==obj:
                    sub=getattr(c,'space_subtarget','')
                    if sub:names.add(sub)
                for target in getattr(c,'targets',()):
                    if target.target and target.target!=obj:raise ValueError('External armature constraint target')
                    if target.target==obj and target.subtarget:names.add(target.subtarget)
                if c.type in ('IK','SPLINE_IK'):
                    ancestor=pb;remaining=c.chain_count or len(obj.pose.bones)
                    while ancestor and remaining:
                        names.add(ancestor.name);ancestor=ancestor.parent;remaining-=1
        for fc in drivers:
            owners=path_bones(fc.data_path)
            if owners and not owners & names:continue
            if not owners:raise ValueError('Object-level driver is not proxy-compatible')
            driver=fc.driver
            if driver.use_self or (driver.type=='SCRIPTED' and not driver.is_simple_expression):
                raise ValueError('Opaque driver dependencies are not proxy-compatible')
            for variable in driver.variables:
                if variable.type=='CONTEXT_PROP':raise ValueError('Context-dependent driver is not proxy-compatible')
                for target in variable.targets:
                    if target.id and target.id not in (obj,obj.data):raise ValueError('External driver target is not proxy-compatible')
                    if target.id in (obj,obj.data):
                        names.update(path_bones(target.data_path))
                        if target.bone_target:names.add(target.bone_target)
        if names==before:return names


class EvaluationProxy:
    """Owns a private rig copy; caller must close it, including on cancellation."""
    def __init__(self,source,seeds,*,defer=False,preserve_all=False):
        self.obj=None;self.data=None;self.scene=None
        self.needed=None
        if not defer:
            for _ in self.prepare_steps(source,seeds,preserve_all=preserve_all):pass

    def prepare_steps(self,source,seeds,*,preserve_all=False):
        """Prepare once, yielding only with the original host context restored.

        The owner must close this iterator and proxy on cancellation. Copies are
        private scratch data until preparation completes; never evaluate them early.
        """
        if self.needed is not None:raise ValueError('Evaluation copy preparation already started')
        try:
            if preserve_all:
                if source.constraints or source.parent:raise ValueError('Proxy requires an unparented rig without object constraints')
                self.needed=set(source.pose.bones.keys())
                drivers=[fc for owner in (source,source.data) if owner.animation_data for fc in owner.animation_data.drivers]
                for index,fc in enumerate(drivers):
                    owners=path_bones(fc.data_path)
                    if not owners:raise ValueError('Object-level driver is not proxy-compatible')
                    driver=fc.driver
                    if driver.use_self or (driver.type=='SCRIPTED' and not driver.is_simple_expression):raise ValueError('Opaque driver dependencies are not proxy-compatible')
                    for variable in driver.variables:
                        if variable.type=='CONTEXT_PROP':raise ValueError('Context-dependent driver is not proxy-compatible')
                        for target in variable.targets:
                            if target.id and target.id not in (source,source.data):raise ValueError('External driver target is not proxy-compatible')
                    # Driver dependency inspection can trigger RNA resolution on
                    # first access.  Yield after each driver so a heavy Rigify
                    # driver cannot monopolize one UI timer invocation.
                    if index:yield 'dependencies'
                for index,pb in enumerate(source.pose.bones):
                    for c in pb.constraints:
                        for prop in c.bl_rna.properties:
                            if prop.type=='POINTER' and prop.identifier!='rna_type':
                                target=getattr(c,prop.identifier,None)
                                if isinstance(target,bpy.types.Object) and target!=source:raise ValueError('External constraint target is not proxy-compatible')
                        for target in getattr(c,'targets',()):
                            if target.target and target.target!=source:raise ValueError('External armature constraint target')
                    if index and index%8==0:yield 'dependencies'
            else:self.needed=dependency_bones(source,seeds)
            yield 'dependencies'
            self.obj=source.copy()
            shared_data=preserve_all and not (source.data.animation_data and len(source.data.animation_data.drivers))
            if shared_data:self.data=None
            else:self.data=source.data.copy();self.obj.data=self.data
            self.obj.name='B4ML temporary evaluator'
            yield 'copy'
            for key in list(self.obj.keys()):
                if key.startswith('b4ml_motion_') or key.startswith('b4ml_result_'):del self.obj[key]
            self.obj.use_fake_user=False
            if self.data:self.data.use_fake_user=False
            # Preview payloads/targets belong only to the original rig.
            if hasattr(self.obj,'b4ml'):
                self.obj.b4ml.body_payload='';self.obj.b4ml.body_source=None
                self.obj.b4ml.posing_payload='';self.obj.b4ml.body_targets.clear()
            for owner in (self.obj,self.data):
                if owner is None:continue
                ad=owner.animation_data
                if not ad:continue
                ad.action=None
                for index,fc in enumerate(list(ad.drivers)):
                    if index and index%64==0:yield 'drivers'
                    if not path_bones(fc.data_path) & self.needed:
                        ad.drivers.remove(fc);continue
                    for variable in fc.driver.variables:
                        for target in variable.targets:
                            if target.id==source:target.id=self.obj
                            elif target.id==source.data and self.data is not None:target.id=self.data
            yield 'drivers'
            self.muted_constraints=0
            for index,pb in enumerate(self.obj.pose.bones):
                if index and index%64==0:yield 'constraints'
                for c in pb.constraints:
                    if pb.name not in self.needed:
                        c.mute=True;self.muted_constraints+=1
                    if getattr(c,'target',None)==source:c.target=self.obj
                    if getattr(c,'pole_target',None)==source:c.pole_target=self.obj
                    if getattr(c,'space_object',None)==source:c.space_object=self.obj
                    for target in getattr(c,'targets',()):
                        if target.target==source:target.target=self.obj
            yield 'constraints'
            self.obj.hide_render=True
            original_scene=bpy.context.scene
            self.scene=bpy.data.scenes.new('B4ML private evaluation')
            self.scene.render.fps=original_scene.render.fps
            self.scene.render.fps_base=original_scene.render.fps_base
            self.scene.frame_set(original_scene.frame_current,subframe=original_scene.frame_subframe)
            self.scene.collection.objects.link(self.obj)
            layer=self.scene.view_layers[0];layer.objects.active=self.obj
            self.obj.select_set(True,view_layer=layer)
            yield 'scene'
            if not preserve_all:
                with bpy.context.temp_override(scene=self.scene,view_layer=layer,object=self.obj,active_object=self.obj,selected_objects=[self.obj],selected_editable_objects=[self.obj]):
                    try:
                        bpy.ops.object.mode_set(mode='EDIT')
                        for bone in list(self.data.edit_bones):
                            if bone.name not in self.needed:self.data.edit_bones.remove(bone)
                    finally:
                        if self.obj.mode!='OBJECT':bpy.ops.object.mode_set(mode='OBJECT')
            yield 'prune'
            self.update()
        except BaseException:
            self.close();raise

    def update(self):
        self.obj.update_tag(refresh={'OBJECT'})
        self.scene.view_layers[0].update()

    def close(self):
        if self.obj is not None:
            bpy.data.objects.remove(self.obj,do_unlink=True);self.obj=None
        if self.data is not None:
            bpy.data.armatures.remove(self.data);self.data=None
        if self.scene is not None:
            bpy.data.scenes.remove(self.scene);self.scene=None
