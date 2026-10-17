"""Add-on-only Timeline tool band, using the supported pixel draw handler.

A collapsed Timeline receives space once when first enabled. The band covers
one header-height at the bottom of the WINDOW region; later resizing is never
repaired. The native scrub ruler and keyframe row stay at the top.
"""

import bpy
import blf
import gpu
import textwrap
import time
from types import SimpleNamespace
from gpu_extras.batch import batch_for_shader
from bpy.props import EnumProperty, IntProperty, StringProperty
from .timeline_catalog import ACTIONS, GROUPS, FAMILY, QUICK_LABELS, command_metadata
from . import timeline_config as model

# Per screen, so each workspace keeps its own stage; saved with the file.
STAGE_PROPERTY = "animassist_timeline_stage"


def current_stage(context):
    stage = getattr(context.screen, STAGE_PROPERTY, "ALL") if context.screen else "ALL"
    return stage if stage in model.STAGE_IDS else "ALL"


def draw_stage_controls(layout, context, family=None):
    """Row stage selector for settings surfaces, plus a hidden-family note."""
    if context.screen is None or not hasattr(context.screen, STAGE_PROPERTY):
        return
    layout.prop(context.screen, STAGE_PROPERTY, text="Row Stage")
    if family:
        labels = {key: label for key, label, _actions in GROUPS}
        note = model.hidden_family_note(current_stage(context), family, labels.get(family, family))
        if note:
            layout.label(text=note, icon="INFO")


def _family_labels(stage):
    labels = {key: label for key, label, _actions in GROUPS}
    return ", ".join(labels[family] for family in model.stage_families(stage))


def _stage_description(kind, stage):
    label = model.stage_label(stage)
    if kind == "STAGE_CYCLE":
        return (f"Stage: {label}. Click for the next stage; Ctrl+Wheel cycles. "
                "Stages filter this band only; saved layouts are unchanged")
    if stage == "ALL":
        return "Show every tool family in your active layout. Ctrl+Wheel over the tabs cycles stages"
    return (f"{label} stage: show only {_family_labels(stage)} tools from your active layout. "
            "Saved layouts are unchanged. Ctrl+Wheel over the tabs cycles stages")


def row_layout(width, height, row_height, at_top, clusters, measure):
    """Return bounded controls, shrinking quick selection into More on overflow."""
    gap, pad = row_height * .15, row_height * .35
    y = max(0, height - row_height) if at_top else 0
    button_height = max(1, min(height, row_height) - 4)
    families = [("MENU", key, label, actions) for key, label, actions in clusters]
    specs = [("SEARCH", "", "Search"), ("SETTINGS", "", "Settings")]
    minimum = sum(measure(label) + 2 * pad + gap for _, _, label, _ in families)
    minimum += sum(measure(label) + 2 * pad + gap for _, _, label in specs)
    more_width = measure("More") + 2 * pad + gap
    budget = max(0, width - minimum - more_width - 2 * gap)
    hidden = []
    for kind, key, label, actions in families:
        specs.append((kind, key, label))
        for action in actions:
            text = QUICK_LABELS.get(action, ACTIONS[action][2])
            cost = measure(text) + 2 * pad + gap
            if cost <= budget:
                specs.append(("ACTION", action, text))
                budget -= cost
            else:
                hidden.append(action)
    if hidden or minimum > width:
        specs.append(("MORE", "", "More"))
    # Extremely narrow Timeline: retain Search, Settings and More. All families
    # remain in More, rather than draw controls underneath clipped neighbours.
    if minimum + more_width > width:
        specs = [("SEARCH", "", "Find"), ("SETTINGS", "", "Set")]
        available = width - sum(measure(label)+2*pad+gap for _,_,label in specs)
        available -= measure("Tools")+2*pad+3*gap
        for _kind, _key, _label, actions in families:
            for action in actions:
                label = QUICK_LABELS.get(action, ACTIONS[action][2])
                cost = measure(label)+2*pad+gap
                if cost <= available:
                    specs.append(("ACTION", action, label))
                    available -= cost
        specs.append(("MORE", "", "Tools"))
    controls, x = [], gap
    for kind, key, label in specs:
        w = measure(label) + 2 * pad
        if x + w > width - gap:
            break
        controls.append((kind, key, label, (x, y + 2, w, button_height)))
        x += w + gap
    return controls


def _theme(context):
    theme = context.preferences.themes[0]
    widgets = theme.user_interface.wcol_regular
    return tuple(theme.dopesheet_editor.space.header), widgets


def _quad(rect, color):
    x, y, w, h = rect
    shader = gpu.shader.from_builtin("UNIFORM_COLOR")
    batch = batch_for_shader(shader, "TRIS", {"pos": ((x, y), (x+w, y), (x+w, y+h),
                                                       (x, y), (x+w, y+h), (x, y+h))})
    shader.bind()
    shader.uniform_float("color", color)
    batch.draw(shader)


class ANIMASSIST_OT_overlay_control(bpy.types.Operator):
    bl_idname = "animassist.overlay_control"
    bl_label = "Anim Assist Timeline Tools"
    bl_options = {"INTERNAL"}
    kind: StringProperty(options={"HIDDEN", "SKIP_SAVE"})
    key: StringProperty(options={"HIDDEN", "SKIP_SAVE"})

    @classmethod
    def description(cls, context, properties):
        from . import timeline_strip as tools
        if properties.kind in {'STAGE','STAGE_CYCLE'}:
            return _stage_description(properties.kind, properties.key)
        action=properties.key.split(':',1)[0]
        if properties.kind in {'SLIDER','POPOUT','PRESET'} and action in ACTIONS:
            operator=tools._operator(action)
            text=operator.get_rna_type().description if operator else ACTIONS[action][2]
            scope=command_metadata(action)[0]
            from ..constants import BREAKDOWN_ANCHOR_HINT
            return text+'. '+scope+'. Drag to preview; release to apply; Esc cancels. Right-click for tool settings.'+((' '+BREAKDOWN_ANCHOR_HINT) if action=='DRAG' else '')
        if properties.kind == "ACTION" and properties.key in ACTIONS:
            return tools.ANIMASSIST_OT_timeline_tool.description(
                context, SimpleNamespace(action=properties.key))
        return {"SEARCH": "Find an animation tool; run it or pin a quick button",
                "SETTINGS": "Choose visible tools, slider modes, order and named layouts",
                "MORE": "All animation families and configured quick tools",
                "MENU": "Open this animation family's tools",
                "BAND": "Anim Assist tools; the remaining Timeline keeps its normal controls"}.get(properties.kind, "Anim Assist")

    def invoke(self, context, _event):
        from . import timeline_strip as tools
        if not tools.is_timeline(context.area):
            return {"CANCELLED"}
        if self.kind == "ACTION":
            return bpy.ops.animassist.timeline_tool("INVOKE_DEFAULT", action=self.key)
        if self.kind == "SEARCH":
            return bpy.ops.animassist.timeline_search("INVOKE_DEFAULT")
        if self.kind == "SETTINGS":
            return bpy.ops.animassist.toolbar_settings("INVOKE_DEFAULT")
        if self.kind == "MENU":
            return bpy.ops.wm.call_menu("INVOKE_DEFAULT", name=tools._menu_id(self.key))
        if self.kind == "MORE":
            return bpy.ops.wm.call_menu("INVOKE_DEFAULT", name="ANIMASSIST_MT_timeline_more")
        if self.kind == "STAGE":
            return bpy.ops.animassist.timeline_stage(stage=self.key)
        if self.kind == "STAGE_CYCLE":
            return bpy.ops.animassist.timeline_stage(step=1)
        return {"FINISHED"}


class ANIMASSIST_OT_timeline_stage(bpy.types.Operator):
    bl_idname = "animassist.timeline_stage"
    bl_label = "Anim Assist Stage"
    bl_description = "Show one animation stage's tool families in the Timeline band"
    bl_options = {"INTERNAL"}
    stage: StringProperty(options={"HIDDEN", "SKIP_SAVE"})
    step: IntProperty(options={"HIDDEN", "SKIP_SAVE"})

    @classmethod
    def poll(cls, context):
        return context.screen is not None and hasattr(context.screen, STAGE_PROPERTY)

    def execute(self, context):
        stage = model.next_stage(current_stage(context), self.step) if self.step else self.stage
        if stage not in model.STAGE_IDS:
            self.report({"WARNING"}, "Choose a known stage")
            return {"CANCELLED"}
        setattr(context.screen, STAGE_PROPERTY, stage)
        from . import timeline_strip as tools
        for area in context.screen.areas:
            if tools.is_timeline(area):
                area.tag_redraw()
        return {"FINISHED"}


_handle = None
_epoch = object()
_keymaps = []
_initialized = set()
_hover = {}
_hover_started = {}


def _items(context):
    from ..prefs import get_prefs, timeline_record
    header = next((r for r in context.area.regions if r.type == "HEADER"), None)
    scale = context.preferences.system.ui_scale
    h = max(28 * scale, header.height if header else 0)
    blf.size(0, round(11 * scale))
    # The native scrub ruler and keyframe summary row are always drawn at the
    # top of the canvas, whichever side the header is on. Anchor the band at
    # the bottom so it never hides or intercepts clicks on keyframes. Markers
    # use a bottom strip; sit above it when the canvas has room for both.
    usable_height = context.region.height
    space = context.space_data
    markers = bool(context.scene.timeline_markers) and getattr(space, "show_markers", True)
    marker_strip = 42 * scale if markers else 0
    keys_at_top = 46 * scale
    y = marker_strip if usable_height - keys_at_top - h >= marker_strip else 0
    try: record=timeline_record(get_prefs(context))
    except ValueError: record=model.recommended(ACTIONS)
    labels={**QUICK_LABELS,'COPY_KEYS':'Copy','PASTE_KEYS':'Paste',
            'MIRROR_SELECTED':'Mirror','BAKE_STEP':'Bake Object','TRAIL_SHOW':'Trails'}
    items = model.toolbar_layout(context.region.width, usable_height, h, False,
                       record,GROUPS,labels,lambda text: blf.dimensions(0, text)[0],
                       current_stage(context))
    items = [(kind, key, label, (x, iy+y, w, ih)) for kind, key, label, (x, iy, w, ih) in items]
    return items, (0, y, context.region.width, min(h, context.region.height))


def _inside(rect, location):
    x, y, w, h = rect
    return x <= location[0] < x+w and y <= location[1] < y+h


_COLORS={'tween':(.25,.8,.8,1),'timing':(1,.72,.25,1),'curves':(.4,.75,1,1),
         'keys':(1,.8,.35,1),'pose':(.8,.6,1,1),'bake':(1,.6,.3,1),'motion':(.5,.85,.5,1)}


def _text(rect,text,color,scale,font=11,left=False):
    x,y,w,h=rect
    blf.size(0,round(font*scale)); blf.color(0,*color)
    tw,th=blf.dimensions(0,text)
    blf.position(0,x+3*scale if left else x+(w-tw)/2,y+(h-th)/2+1,0)
    blf.draw(0,text)


def _glyph(rect,action,color):
    x,y,w,h=rect; cx=x+w/2; cy=y+h/2; r=min(w,h)*.28
    shader=gpu.shader.from_builtin('UNIFORM_COLOR')
    if action in {'SEARCH','SETTINGS','MORE'}:
        if action=='MORE':
            for dx in (-r,0,r): _quad((cx+dx-1,cy-1,2,2),color)
        else:
            import math
            positions=[(cx+math.cos(i*math.pi/4)*r,cy+math.sin(i*math.pi/4)*r) for i in range(9)]
            if action=='SEARCH': positions.extend(((cx+r*.7,cy-r*.7),(cx+r*1.5,cy-r*1.5)))
            batch=batch_for_shader(shader,'LINE_STRIP',{'pos':positions})
            shader.bind(); shader.uniform_float('color',color); batch.draw(shader)
            if action=='SETTINGS':
                for i in range(4):
                    dx=math.cos(i*math.pi/2)*r; dy=math.sin(i*math.pi/2)*r
                    _quad((cx+dx-2,cy+dy-2,4,4),color)
        return
    positions=((cx,cy+r),(cx+r,cy),(cx,cy-r),(cx,cy+r),(cx,cy-r),(cx-r,cy))
    if action.startswith('NUDGE_'):
        sign=-1 if action=='NUDGE_LEFT' else 1
        positions=((cx+sign*r,cy),(cx-sign*r,cy+r),(cx-sign*r,cy-r))
    elif action in {'COPY_KEYS','PASTE_KEYS','BAKE_STEP'}:
        positions=((cx-r,cy-r),(cx+r,cy-r),(cx+r,cy+r),
                   (cx-r,cy-r),(cx+r,cy+r),(cx-r,cy+r))
    batch=batch_for_shader(shader,'TRIS',{'pos':positions})
    shader.bind(); shader.uniform_float('color',color); batch.draw(shader)
    if action=='COPY_KEYS': _quad((cx-r/2,cy-r/2,r,r),(.12,.12,.12,1))


def _parts(rect,label,scale):
    blf.size(0,round(11*scale))
    return model.slider_parts(rect,label,lambda s:blf.dimensions(0,s)[0],scale)


def _track(rect,value,tool,color):
    x,y,w,h=rect; cy=y+h/2
    fraction=min(1,max(0,(value-tool['range_min'])/(tool['range_max']-tool['range_min'])))
    _quad((x,cy-2,w,4),(.15,.15,.15,1))
    _quad((x,cy-2,w*fraction,4),color)
    _quad((x+w*fraction-3,cy-5,6,10),color)


def _slider_controls(context,event,item,scale):
    from ..prefs import get_prefs,timeline_record
    from ..operators import timeline_slider_ops as sliders
    kind,action,label,rect=item
    tool=model.effective_tool(action,timeline_record(get_prefs(context))['active']['tools'][action])
    track,value_rect,reset_rect=_parts(rect,label,scale)
    if kind=='POPOUT': track=(rect[0],rect[1],120*scale,rect[3])
    point=(event.mouse_region_x,event.mouse_region_y)
    value=sliders.last_value(context.window,context.area,action,tool['default'])
    if kind=='SLIDER' and _inside(value_rect,point):
        return bpy.ops.animassist.slider_value('INVOKE_DEFAULT',True,action=action,value=value)
    if kind=='SLIDER' and _inside(reset_rect,point):
        result=bpy.ops.animassist.timeline_slider('EXEC_DEFAULT',action=action,value=tool['default'])
        if 'FINISHED' in result: bpy.ops.ed.undo_push(message='Reset '+model.SLIDERS[action][0])
        return result
    return bpy.ops.animassist.timeline_slider('INVOKE_DEFAULT',True,action=action,
        mode='INLINE' if kind=='SLIDER' else 'POPOUT',track_x=track[0],track_y=track[1],track_width=track[2])


def _draw():
    context = bpy.context
    from . import timeline_strip as tools
    if not tools.is_timeline(context.area) or not tools._enabled():
        return
    if context.region.height < 8:
        return
    items, band = _items(context)
    background, widgets = _theme(context)
    scale = context.preferences.system.ui_scale
    from ..prefs import get_prefs,timeline_record
    from ..operators import timeline_slider_ops as sliders
    try: record=timeline_record(get_prefs(context))
    except ValueError: record=model.recommended(ACTIONS)
    active=sliders.feedback(context.window,context.area)
    stage=current_stage(context)
    old_blend = gpu.state.blend_get()
    try:
        gpu.state.blend_set("ALPHA")
        _quad(band, (*background[:3], 1))
        hover = _hover.get(context.window.as_pointer())
        for kind, key, label, rect in items:
            action=key.split(':',1)[0]
            highlighted = hover == (context.area.as_pointer(), kind, key)
            reason = tools._unavailable(context, context.area, action) if action in ACTIONS else ""
            color = widgets.inner_sel if highlighted else widgets.inner
            _quad(rect,tuple(color) if kind!='MENU' else (*background[:3],1))
            text_color = widgets.text_sel if highlighted else widgets.text
            ink=(*text_color[:3],.45 if reason else 1)
            accent=_COLORS.get(FAMILY[action][0] if action in FAMILY else key,ink)
            if kind in {'STAGE','STAGE_CYCLE'}:
                current = kind=='STAGE_CYCLE' or key==stage
                if current and kind=='STAGE' and not highlighted:
                    _quad(rect,tuple(widgets.inner_sel))
                if current and key!='ALL':
                    # Underline in the colour of the stage's first family.
                    _quad((rect[0]+3*scale,rect[1]+2*scale,rect[2]-6*scale,2*scale),
                          _COLORS[model.stage_families(key)[0]])
                _text(rect,label,(*widgets.text_sel[:3],1) if current or highlighted else ink,scale)
                continue
            if kind=='SLIDER':
                tool=model.effective_tool(action,record['active']['tools'][action])
                value=active.value if active and active.action==action else sliders.last_value(context.window,context.area,action,tool['default'])
                track,value_rect,reset_rect=_parts(rect,label,scale)
                if label: _text((rect[0],rect[1],track[0]-rect[0],rect[3]),label,ink,scale,left=True)
                _track(track,value,tool,(*accent[:3],ink[3]))
                unit=model.SLIDERS[action][1]
                number=f'{value:.{tool["precision"]}f}' if abs(value)<10000 else f'{value:.3g}'
                _text(value_rect,number+unit,ink,scale,font=9)
                _text(reset_rect,'R',ink,scale,font=9)
            elif not label:
                _glyph(rect,action if action else kind,(*accent[:3],ink[3]))
            else:
                _text(rect,label,(*accent[:3],ink[3]) if kind=='MENU' else ink,scale)
                if kind=='POPOUT': _quad((rect[0]+3*scale,rect[1]+2*scale,rect[2]-6*scale,1*scale),accent)
        # Thin separator on the edge facing the animation canvas.
        _quad((band[0], band[1]+band[3]-1, band[2], 1), (*widgets.outline[:3], 1))
        if active and active.mode=='POPOUT' and active._moved:
            width=min(280*scale,context.region.width); height=min(44*scale,context.region.height)
            x=max(0,min(active.track_x,context.region.width-width))
            y=band[1]-height-4*scale if band[1]>height else band[1]+band[3]+4*scale
            y=max(0,min(y,context.region.height-height))
            accent=_COLORS[FAMILY[active.action][0]]
            _quad((x,y,width,height),(*background[:3],1))
            _quad((x,y,width,1),accent)
            _text((x+5*scale,y+23*scale,width-10*scale,18*scale),model.SLIDERS[active.action][0],(*widgets.text[:3],1),scale,left=True)
            _track((x+10*scale,y+5*scale,max(1,width-70*scale),16*scale),active.value,active._tool,accent)
            _text((x+width-60*scale,y+3*scale,55*scale,20*scale),f'{active.value:.{active._tool["precision"]}f}'+model.SLIDERS[active.action][1],(*widgets.text[:3],1),scale,font=10)
        if not active and hover and time.monotonic() - _hover_started.get(context.window.as_pointer(), float("inf")) > .6:
            item = next((item for item in items if (item[0], item[1]) == hover[1:]), None)
            if item:
                description = ANIMASSIST_OT_overlay_control.description(
                    context, SimpleNamespace(kind=item[0], key=item[1]))
                font = round(11 * scale)
                blf.size(0, font)
                wrap = max(12, min(85, int((context.region.width-20*scale)/(6*scale))))
                lines = textwrap.wrap(description, wrap)[:3]
                if lines:
                    width = min(context.region.width, max(blf.dimensions(0, line)[0] for line in lines)+16*scale)
                    height = min(context.region.height, (len(lines)*15+12)*scale)
                    x = max(0, min(item[3][0], context.region.width-width))
                    y = band[1]-height-4*scale if band[1] > height else band[1]+band[3]+4*scale
                    y = max(0, min(y, context.region.height-height))
                    _quad((x, y, width, height), (.06, .06, .06, .97))
                    blf.color(0, .95, .95, .95, 1)
                    for index, line in enumerate(lines):
                        blf.position(0, x+8*scale, y+height-(index+1)*15*scale, 0)
                        blf.draw(0, line)
    finally:
        gpu.state.blend_set(old_blend)


class ANIMASSIST_OT_timeline_overlay_events(bpy.types.Operator):
    bl_idname = "animassist.timeline_overlay_events"
    bl_label = "Anim Assist Timeline Row Input"
    bl_options = {"INTERNAL"}

    @classmethod
    def poll(cls, context):
        from . import timeline_strip as tools
        return tools.is_timeline(context.area) and bool(context.region) and context.region.type == "WINDOW" and tools._enabled()

    def invoke(self, context, event):
        items, band = _items(context)
        point = (event.mouse_region_x, event.mouse_region_y)
        hit = _inside(band, point)
        found = next((item for item in items if _inside(item[3], point)), None) if hit else None
        pointer = context.window.as_pointer()
        hover = (context.area.as_pointer(), found[0], found[1]) if found else None
        if _hover.get(pointer) != hover:
            _hover[pointer] = hover
            _hover_started[pointer] = time.monotonic()
            context.area.tag_redraw()
            if hover:
                epoch, window, expected = _epoch, context.window, hover
                def tooltip_redraw():
                    if epoch is _epoch:
                        try:
                            if _hover.get(window.as_pointer()) == expected:
                                for area in window.screen.areas:
                                    if area.as_pointer() == expected[0]:
                                        area.tag_redraw()
                        except ReferenceError:
                            pass
                    return None
                bpy.app.timers.register(tooltip_redraw, first_interval=.65)
        if event.type == "MOUSEMOVE" or not hit:
            return {"CANCELLED", "PASS_THROUGH"}
        if (event.type in {'WHEELUPMOUSE','WHEELDOWNMOUSE'} and event.ctrl and found
                and found[0] in {'STAGE','STAGE_CYCLE'}):
            bpy.ops.animassist.timeline_stage(step=1 if event.type=='WHEELDOWNMOUSE' else -1)
            return {'FINISHED'}
        if event.type=='RIGHTMOUSE' and found:
            action=found[1].split(':',1)[0]
            if action in ACTIONS:
                bpy.ops.animassist.tool_settings('INVOKE_DEFAULT',action=action)
                return {'FINISHED'}
        if event.type == "LEFTMOUSE" and found:
            action=found[1].split(':',1)[0]
            from . import timeline_strip as tools
            reason=tools._unavailable(context,context.area,action) if action in ACTIONS else ''
            if reason:
                self.report({'WARNING'},reason)
            elif found[0] in {'SLIDER','POPOUT'}:
                _slider_controls(context,event,found,context.preferences.system.ui_scale)
            elif found[0]=='PRESET':
                value=float(found[1].split(':',1)[1])
                result=bpy.ops.animassist.timeline_slider('EXEC_DEFAULT',action=action,value=value)
                if 'FINISHED' in result: bpy.ops.ed.undo_push(message='Preset '+model.SLIDERS[action][0])
            else:
                bpy.ops.animassist.overlay_control("INVOKE_DEFAULT", kind=found[0], key=found[1])
            context.area.tag_redraw()
        return {"FINISHED"}


class ANIMASSIST_OT_clear_timeline_hover(bpy.types.Operator):
    bl_idname = "animassist.clear_timeline_hover"
    bl_label = "Clear Timeline Tool Hover"
    bl_options = {"INTERNAL"}

    @classmethod
    def poll(cls, context):
        from . import timeline_strip as tools
        if not context.window or not _hover.get(context.window.as_pointer()):
            return False
        return not (tools.is_timeline(context.area) and context.region
                    and context.region.type == "WINDOW")

    def invoke(self, context, _event):
        _hover.pop(context.window.as_pointer(), None)
        for area in context.window.screen.areas:
            area.tag_redraw()
        return {"CANCELLED", "PASS_THROUGH"}


def _start_windows():
    if _handle is None:
        return None
    from . import timeline_strip as tools
    from ..prefs import get_prefs, timeline_record
    prefs = get_prefs()
    if prefs and not prefs.timeline_layouts_json:
        timeline_record(prefs, initialize=True)
    if prefs and not prefs.timeline_canvas_row_initialized:
        # Before 12.6.1, False meant "use the existing header", not hide tools.
        # Apply the new visible placement once; later explicit hiding persists.
        prefs.timeline_toolbar_row = True
        prefs.timeline_canvas_row_initialized = True
    for window in bpy.context.window_manager.windows:
        if tools._enabled():
            for area in window.screen.areas:
                if not tools.is_timeline(area):
                    continue
                pointer = area.spaces.active.as_pointer()
                if pointer in _initialized:
                    continue
                _initialized.add(pointer)
                # One attempt on first encounter; never repair later resizes.
                minimum = round(112 * bpy.context.preferences.system.ui_scale)
                if area.height < minimum:
                    above = any(a != area and abs(a.y-(area.y+area.height+1)) <= 3
                                and a.x <= area.x+area.width/2 < a.x+a.width
                                for a in window.screen.areas)
                    if above:
                        with bpy.context.temp_override(window=window, area=area):
                            if not bpy.ops.screen.area_move.poll():
                                continue
                            bpy.ops.screen.area_move(x=area.x+area.width//2,
                                                     y=area.y+area.height,
                                                     delta=minimum-area.height)
                area.tag_redraw()
    # Window discovery only: existing Timeline sizes are never revisited.
    return 1.0


def _view_menu(self, context):
    from . import timeline_strip as tools
    from ..prefs import get_prefs
    if tools.is_timeline(context.area):
        prefs = get_prefs(context)
        if prefs:
            self.layout.separator()
            self.layout.prop(prefs, "timeline_toolbar_row", text="Show Anim Assist Tool Row")
            if hasattr(context.screen, STAGE_PROPERTY):
                self.layout.prop_menu_enum(context.screen, STAGE_PROPERTY, text="Anim Assist Stage")
            self.layout.menu("ANIMASSIST_MT_timeline_tools", text="Anim Assist Tools")


@bpy.app.handlers.persistent
def _load_post(_unused):
    global _epoch
    _epoch = object()
    _hover.clear()
    _hover_started.clear()
    _initialized.clear()


_CLASSES = (ANIMASSIST_OT_overlay_control, ANIMASSIST_OT_timeline_stage,
            ANIMASSIST_OT_timeline_overlay_events, ANIMASSIST_OT_clear_timeline_hover)


def _stage_update(screen, _context):
    # Dropdowns (Settings, gear popover, View menu) change the stage outside the
    # band; redraw this screen's Timelines so the row follows immediately.
    from . import timeline_strip as tools
    for area in screen.areas:
        if tools.is_timeline(area):
            area.tag_redraw()


def _stage_items():
    return [(key, label, "Show every tool family in the active layout" if families is None
             else f"Show only {_family_labels(key)} tools")
            for key, label, families in model.STAGES]


def register():
    global _handle, _epoch
    _epoch = object()
    for cls in _CLASSES:
        bpy.utils.register_class(cls)
    setattr(bpy.types.Screen, STAGE_PROPERTY, EnumProperty(
        name="Anim Assist Stage", description="Tool families the Timeline band shows in this workspace",
        items=_stage_items(), default="ALL", update=_stage_update))
    if not bpy.app.background:
        _handle = bpy.types.SpaceDopeSheetEditor.draw_handler_add(_draw, (), "WINDOW", "POST_PIXEL")
        bpy.types.DOPESHEET_MT_view.append(_view_menu)
        config = bpy.context.window_manager.keyconfigs.addon
        if config:
            screen = config.keymaps.new(name="Screen", space_type="EMPTY", region_type="WINDOW")
            item = screen.keymap_items.new(ANIMASSIST_OT_clear_timeline_hover.bl_idname,
                                           type="MOUSEMOVE", value="ANY")
            _keymaps.append((screen, item))
            for name in ("Dopesheet", "Dopesheet Generic"):
                keymap = config.keymaps.new(name=name, space_type="DOPESHEET_EDITOR", region_type="WINDOW")                for event_type in ("MOUSEMOVE", "LEFTMOUSE", "RIGHTMOUSE", "MIDDLEMOUSE", "WHEELUPMOUSE", "WHEELDOWNMOUSE"):
                    item = keymap.keymap_items.new(ANIMASSIST_OT_timeline_overlay_events.bl_idname,
                                                  type=event_type, value="ANY" if event_type=="MOUSEMOVE" else "PRESS", any=True)
                    _keymaps.append((keymap, item))
        bpy.app.handlers.load_post.append(_load_post)
        from ..operators.timeline_slider_ops import cancel_active
        bpy.app.handlers.load_pre.append(cancel_active)
        bpy.app.handlers.undo_pre.append(cancel_active)
        bpy.app.timers.register(_start_windows, first_interval=.1, persistent=True)


def unregister():
    global _handle, _epoch
    _epoch = object()
    from ..operators.timeline_slider_ops import cancel_active
    cancel_active(finalize=True)
    for handlers in (bpy.app.handlers.load_pre,bpy.app.handlers.undo_pre):
        if cancel_active in handlers: handlers.remove(cancel_active)
    if _handle is not None:
        bpy.types.SpaceDopeSheetEditor.draw_handler_remove(_handle, "WINDOW")
        _handle = None
        bpy.types.DOPESHEET_MT_view.remove(_view_menu)
        if _load_post in bpy.app.handlers.load_post:
            bpy.app.handlers.load_post.remove(_load_post)
        if bpy.app.timers.is_registered(_start_windows):
            bpy.app.timers.unregister(_start_windows)
    _initialized.clear()
    _hover.clear()
    _hover_started.clear()
    for keymap, item in _keymaps:
        keymap.keymap_items.remove(item)
    _keymaps.clear()
    if hasattr(bpy.types.Screen, STAGE_PROPERTY):
        delattr(bpy.types.Screen, STAGE_PROPERTY)
    for cls in reversed(_CLASSES):
        if "bl_rna" in cls.__dict__:
            bpy.utils.unregister_class(cls)
