"""Native staged dialogs for toolbar presentation and tool-specific options."""
import copy
import json
import bpy
from bpy.props import StringProperty, EnumProperty, FloatProperty, IntProperty, BoolProperty, CollectionProperty
from . import timeline_config as model
from .timeline_catalog import ACTIONS, FAMILY, GROUPS

_editors={}
_tool_editors={}
_MODES=(('HIDDEN','Hidden','Keep this tool in Search and More',0),
        ('BUTTON','Button','Invoke the existing action directly',1),
        ('POPOUT','Popout slider','Press and drag to reveal a temporary slider',2),
        ('INLINE','Inline slider','Keep the slider visible in the row',3))
_LABELS=(('LABEL','Label','Show the tool name'),('ICON','Icon','Use a compact tool glyph; hover for its name'))


def _modes(self,context): return _MODES if self.action in model.SLIDERS else _MODES[:2]


def _family_update(self,context):
    candidates=[i for i,x in enumerate(self.entries) if x.family==self.family]
    if candidates: self.active_index=candidates[0]


def record(context):
    from ..prefs import get_prefs,timeline_record
    return timeline_record(get_prefs(context))


def write(context,data):
    from ..prefs import get_prefs
    from ..operators.timeline_slider_ops import busy
    if busy(): raise ValueError('Finish or cancel the active slider first')
    prefs=get_prefs(context)
    if prefs is None: raise ValueError('Enable Anim Assist in preferences')
    prefs.timeline_layouts_json=model.encode(data,ACTIONS)


def editor(context): return _editors.get(context.window.as_pointer())


def staged_record(context):
    active=editor(context)
    return active.serialize() if active else record(context)


def sync_editor(context,data):
    active=editor(context)
    if active: active.populate(data)


class AA_ToolbarEntry(bpy.types.PropertyGroup):
    action: StringProperty(options={'HIDDEN'})
    family: StringProperty(options={'HIDDEN'})
    mode: EnumProperty(name='Display',description='How this tool appears in the Timeline row',items=_modes,default=1)
    label_mode: EnumProperty(name='Label',description='Choose a name or compact tool glyph',items=_LABELS,default='LABEL')
    width: FloatProperty(name='Slider Width',description='Track width in logical pixels',default=120,min=80,max=240)


class AA_UL_toolbar_tools(bpy.types.UIList):
    def draw_item(self,context,layout,data,item,icon,active_data,active_propname,index=0):
        row=layout.row(align=True)
        row.label(text=item.name)
        row.prop(item,'mode',text='')
        row.prop(item,'label_mode',text='')

    def filter_items(self,context,data,propname):
        return ([self.bitflag_filter_item if item.family==data.family else 0 for item in getattr(data,propname)],[])


class ANIMASSIST_OT_toolbar_settings(bpy.types.Operator):
    bl_idname='animassist.toolbar_settings'
    bl_label='Toolbar Settings'
    bl_description='Choose visible tools, inline or popout sliders, labels and order'
    family: EnumProperty(name='Family',description='Choose which animation family to configure',
        items=[(key,label,'Configure '+label) for key,label,_ in GROUPS],default='tween',update=_family_update)
    entries: CollectionProperty(type=AA_ToolbarEntry)
    active_index: IntProperty(default=0)

    def populate(self,data):
        self._record=copy.deepcopy(data)
        self.entries.clear()
        for action in data['active']['order']:
            if action not in ACTIONS: continue
            tool=data['active']['tools'][action]
            entry=self.entries.add(); entry.name=ACTIONS[action][2]; entry.action=action
            entry.family=FAMILY[action][0]
            entry.mode=tool['mode']; entry.label_mode=tool['label_mode']; entry.width=tool['width']
        _family_update(self,None)

    def serialize(self):
        data=copy.deepcopy(self._record)
        data['active']['order']=[entry.action for entry in self.entries]+[
            key for key in data['active']['order'] if key not in ACTIONS]
        for entry in self.entries:
            data['active']['tools'][entry.action].update(mode=entry.mode,label_mode=entry.label_mode,width=entry.width)
        return model.validate(data,ACTIONS)

    def invoke(self,context,event):
        from ..operators.timeline_slider_ops import busy
        if busy():
            self.report({'WARNING'},'Finish or cancel the active slider first'); return {'CANCELLED'}
        try: self.populate(record(context))
        except ValueError as exc:
            if editor(context) is self: _editors.pop(context.window.as_pointer(),None)
            self.report({'WARNING'},str(exc)); return {'CANCELLED'}
        _editors[context.window.as_pointer()]=self
        return context.window_manager.invoke_props_dialog(self,width=560)

    def draw(self,context):
        layout=self.layout
        layout.label(text='Layout: '+self._record['active']['name']+(' *' if model.modified(self.serialize(),ACTIONS) else ''))
        layout.prop(self,'family')
        layout.template_list('AA_UL_toolbar_tools','',self,'entries',self,'active_index',rows=8)
        if 0<=self.active_index<len(self.entries):
            entry=self.entries[self.active_index]
            row=layout.row(align=True)
            for direction,label in ((-1,'Move Up'),(1,'Move Down')):
                op=row.operator('animassist.toolbar_reorder',text=label); op.direction=direction
            op=row.operator('animassist.tool_settings',text='Tool Settings'); op.action=entry.action
            if entry.action in model.SLIDERS: layout.prop(entry,'width')
        layout.operator('animassist.restore_toolbar',text='Restore Recommended Layout')
        layout.label(text='Hidden tools remain available in Search and More.')

    def execute(self,context):
        try: write(context,self.serialize())
        except ValueError as exc:
            if editor(context) is self: _editors.pop(context.window.as_pointer(),None)
            self.report({'WARNING'},str(exc)); return {'CANCELLED'}
        _editors.pop(context.window.as_pointer(),None)
        return {'FINISHED'}

    def cancel(self,context):
        if editor(context) is self: _editors.pop(context.window.as_pointer(),None)


class ANIMASSIST_OT_toolbar_reorder(bpy.types.Operator):
    bl_idname='animassist.toolbar_reorder'
    bl_label='Move Toolbar Tool'
    bl_description='Move the selected tool within its animation family'
    bl_options={'INTERNAL'}
    direction: IntProperty(options={'HIDDEN','SKIP_SAVE'})
    def execute(self,context):
        current=editor(context)
        if current and 0<=current.active_index<len(current.entries):
            indexes=[i for i,e in enumerate(current.entries) if e.family==current.family]
            position=indexes.index(current.active_index)
            target=position+self.direction
            if 0<=target<len(indexes):
                current.entries.move(current.active_index,indexes[target]); current.active_index=indexes[target]
        return {'FINISHED'}


class ANIMASSIST_OT_restore_toolbar(bpy.types.Operator):
    bl_idname='animassist.restore_toolbar'
    bl_label='Restore Recommended Layout'
    bl_description='Restore the two-slider recommended layout; keep your saved layouts'
    def execute(self,context):
        data=staged_record(context); model.load(data,'recommended',ACTIONS)
        if editor(context): sync_editor(context,data)
        else: write(context,data)
        return {'FINISHED'}


class ANIMASSIST_OT_tool_settings(bpy.types.Operator):
    bl_idname='animassist.tool_settings'
    bl_label='Animation Tool Settings'
    bl_description='Configure this tool’s display, slider range, defaults and drag behavior'
    action: StringProperty(options={'HIDDEN','SKIP_SAVE'})
    mode: EnumProperty(name='Display',description='How this tool appears in the row',items=_modes,default=1)
    label_mode: EnumProperty(name='Label',description='Choose name or compact glyph',items=_LABELS,default='LABEL')
    width: FloatProperty(name='Slider Width',description='Track width in logical pixels',default=120,min=80,max=240)
    range_min: FloatProperty(name='Minimum',description='Lower display and numeric adjustment bound')
    range_max: FloatProperty(name='Maximum',description='Upper display and numeric adjustment bound')
    default: FloatProperty(name='Default',description='Starting amount; changing it does not change animation')
    sensitivity: FloatProperty(name='Sensitivity',description='Pixels needed to traverse a popout slider range',default=200,min=10,max=2000)
    precision: IntProperty(name='Precision',description='Decimal places shown in slider readouts',default=1,min=0,max=4)
    snap_enabled: BoolProperty(name='Snap Amount',description='Round slider values to the configured step')
    snap_step: FloatProperty(name='Snap Step',description='Step in this tool’s displayed units',default=1,min=.0001)
    overshoot_enabled: BoolProperty(name='Custom Range / Overshoot',description='Use your configured range rather than the standard display range')
    presets_text: StringProperty(name='Presets',description='Comma-separated amounts; at most 12, inside the configured range')

    def invoke(self,context,event):
        if self.action not in ACTIONS: return {'CANCELLED'}
        from ..operators.timeline_slider_ops import busy
        if busy():
            self.report({'WARNING'},'Finish or cancel the active slider first'); return {'CANCELLED'}
        self._tool=copy.deepcopy(staged_record(context)['active']['tools'][self.action])
        for field,value in self._tool.items():
            if field=='presets': self.presets_text=', '.join(f'{v:g}' for v in value)
            elif field!='action' and hasattr(self,field): setattr(self,field,value)
        _tool_editors[context.window.as_pointer()]=self
        return context.window_manager.invoke_props_dialog(self,width=430)

    def draw(self,context):
        layout=self.layout
        layout.label(text=ACTIONS[self.action][2])
        layout.prop(self,'mode'); layout.prop(self,'label_mode')
        if self.action in model.SLIDERS:
            unit=model.SLIDERS[self.action][1]
            layout.prop(self,'width')
            layout.prop(self,'default',text=f'Default ({unit})')
            layout.prop(self,'overshoot_enabled')
            low,high=model.SLIDERS[self.action][3:5]
            layout.label(text=f'Standard range: {low:g} to {high:g}{unit}')
            row=layout.row(align=True); row.enabled=self.overshoot_enabled
            row.prop(self,'range_min',text=f'Min ({unit})'); row.prop(self,'range_max',text=f'Max ({unit})')
            layout.prop(self,'sensitivity'); layout.prop(self,'precision')
            layout.prop(self,'snap_enabled')
            row=layout.row(); row.enabled=self.snap_enabled; row.prop(self,'snap_step',text=f'Step ({unit})')
            layout.prop(self,'presets_text')
        layout.separator()
        layout.label(text='Masks, targets and anchors are scene-specific.')
        op=layout.operator('wm.call_panel',text='Scene Tool Options')
        op.name='ANIMASSIST_PT_timeline_options_'+FAMILY[self.action][0]

    def execute(self,context):
        try:
            data=staged_record(context); tool=copy.deepcopy(self._tool)
            for field in tool:
                if field=='presets': tool[field]=[float(x.strip()) for x in self.presets_text.split(',') if x.strip()]
                elif field!='action' and hasattr(self,field): tool[field]=getattr(self,field)
            data['active']['tools'][self.action]=model.validate_tool(self.action,tool)
            if editor(context): sync_editor(context,data)
            else: write(context,data)
            _tool_editors.pop(context.window.as_pointer(),None)
            return {'FINISHED'}
        except ValueError as exc:
            _tool_editors.pop(context.window.as_pointer(),None)
            self.report({'WARNING'},str(exc)); return {'CANCELLED'}

    def cancel(self,context):
        if _tool_editors.get(context.window.as_pointer()) is self:
            _tool_editors.pop(context.window.as_pointer(),None)


CLASSES=(AA_ToolbarEntry,AA_UL_toolbar_tools,ANIMASSIST_OT_toolbar_settings,
         ANIMASSIST_OT_toolbar_reorder,ANIMASSIST_OT_restore_toolbar,ANIMASSIST_OT_tool_settings)


def register():
    for cls in CLASSES: bpy.utils.register_class(cls)


def unregister():
    _editors.clear()
    _tool_editors.clear()
    for cls in reversed(CLASSES):
        if cls.is_registered: bpy.utils.unregister_class(cls)
