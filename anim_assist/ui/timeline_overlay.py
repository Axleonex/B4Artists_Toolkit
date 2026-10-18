"""Add-on-only Timeline tool band, using the supported pixel draw handler.

A collapsed Timeline receives space once when first enabled. The band covers
one header-height at the bottom of the WINDOW region; later resizing is never
repaired. The native scrub ruler and keyframe row stay at the top.
"""

import bpy
import blf
import gpu
import time
from types import SimpleNamespace
from gpu_extras.batch import batch_for_shader
from bpy.props import EnumProperty, IntProperty, StringProperty
from .timeline_catalog import ACTIONS, GROUPS, FAMILY, QUICK_LABELS, command_metadata
from . import timeline_config as model

# Short row labels; tooltips keep the full catalogue names. Distinct from the
# All tab, the Breakdown slider and the Reference popout they sit beside.
ROW_LABELS = {
    'COPY_KEYS': 'Copy', 'PASTE_KEYS': 'Paste', 'MIRROR_SELECTED': 'Mirror', 'BAKE_STEP': 'Bake Object',
    'TRAIL_SHOW': 'Show Trails', 'INBETWEEN': 'Inbetween', 'INBETWEENS': 'Distribute',
    'PUSH_PREV': 'Push Prev', 'PULL_PREV': 'Pull Prev', 'PULL_NEXT': 'Pull Next', 'PUSH_NEXT': 'Push Next',
    'ALL': 'All Keys', 'GROW_LEFT': 'Grow Left', 'GROW_RIGHT': 'Grow Right',
    'TYPE_KEYFRAME': 'Mark Key', 'TYPE_BREAKDOWN': 'Mark Breakdown', 'TYPE_EXTREME': 'Mark Extreme',
    'TYPE_HOLD': 'Mark Hold', 'REFERENCE': 'Set Reference', 'HANDLE_CLAMPED': 'Clamped',
    'HANDLE_VECTOR': 'Vector', 'HANDLE_FREE': 'Free', 'T80': '80%', 'T90': '90%', 'T110': '110%',
    'T120': '120%', 'SNAP': 'Snap', 'OPPOSITE': 'Opposite', 'MIRROR_ACTIVE': 'Mirror Active',
    'SWAP': 'Swap', 'SMART_BAKE': 'Smart Bake', 'REDUCE': 'Reduce', 'BAKE_CLEANUP': 'Bake Proxies',
    'PROXY_TRANSLATION': 'Location Proxy', 'PROXY_ORIENTATION': 'Rotation Proxy', 'PROXY_WORLD': 'Proxy World',
    'PROXY_PARENT': 'Proxy Parent', 'BAKE_PREVIEW': 'Bake Preview', 'BAKE_INTEGER': 'Whole Frames',
    'PROXY_BAKE': 'Proxy & Bake', 'TO_SPLINE': 'To Spline', 'TO_STEPPED': 'To Stepped', 'CLEANUP_ALL': 'Clean All Proxies',
    'TRAIL_REFRESH': 'Refresh', 'TRAIL_DIAGNOSE': 'Diagnose', 'TRAIL_HIDE': 'Hide Trails',
}

# All keeps its 12.9 row width: Hide Trails is not beside Show Trails there.
ALL_ROW_LABELS = {'TRAIL_SHOW': 'Trails'}

# Per workspace, saved with the file. Maximized views and extra windows of the
# same workspace share it (a Screen property would be lost in those).
STAGE_PROPERTY = "animassist_timeline_stage"


def current_stage(context):
    workspace = getattr(context, "workspace", None)
    stage = getattr(workspace, STAGE_PROPERTY, "ALL") if workspace else "ALL"
    return stage if stage in model.STAGE_IDS else "ALL"


def draw_stage_controls(layout, context, family=None):
    """Row stage selector for settings surfaces, plus a hidden-family note."""
    from . import timeline_strip as tools
    workspace = getattr(context, "workspace", None)
    screen = context.screen
    if workspace is None or not hasattr(workspace, STAGE_PROPERTY):
        return
    if screen is None or not any(tools.is_timeline(area) for area in screen.areas):
        # Opened from Preferences or another window: no row to stage here.
        layout.label(text="Open from a Timeline to change its row stage", icon="INFO")
        return
    layout.prop(workspace, STAGE_PROPERTY, text="Row Stage")
    if family:
        labels = {key: label for key, label, _actions in GROUPS}
        note = model.hidden_family_note(current_stage(context), family, labels.get(family, family))
        if note:
            layout.label(text=note, icon="INFO")


def _tool_action(kind, key):
    """Catalogue action for a tool control; '' for tabs, menus and utilities.

    Stage ids share the key space with actions (the All tab and Select All
    Visible are both 'ALL'), so only tool kinds may resolve to an action.
    """
    if kind not in {'ACTION', 'SLIDER', 'POPOUT', 'PRESET'}:
        return ''
    action = key.split(':', 1)[0]
    return action if action in ACTIONS else ''


def _family_labels(stage):
    labels = {key: label for key, label, _actions in GROUPS}
    return ", ".join(labels[family] for family in model.stage_families(stage))


def _stage_description(kind, stage):
    label = model.stage_label(stage)
    if kind == "STAGE_CYCLE":
        return (f"Stage: {label}. Click to choose a stage; Ctrl+Wheel cycles. "
                "Each stage has its own toolset, edited in Settings")
    if stage == "ALL":
        return "Show the All overview of every tool family. Ctrl+Wheel over the tabs cycles stages"
    return (f"{label} stage: its own {_family_labels(stage)} toolset, edited in Settings. "
            "Ctrl+Wheel over the tabs cycles stages")


def _tooltip_paragraphs(context, item):
    """Hover text for a row control as (text, role) paragraphs."""
    from . import timeline_strip as tools
    from .timeline_catalog import command_tooltip
    kind, key = item[0], item[1]
    action = key.split(':', 1)[0]
    if kind == 'ACTION' and action in ACTIONS:
        operator = tools._operator(action)
        operation = operator.get_rna_type().description if operator else 'Tool module unavailable'
        reason = tools._unavailable(context, tools._target(context), action)
        status = ''
        if action in {'OFFSET', 'OFFSET_MASK', 'OFFSET_SCENE_RANGE'}:
            from ..operators.anim_offset_ops import offset_session_status
            status = offset_session_status(context.scene) or ''
        return command_tooltip(action, operation, reason or '', status)
    if kind in {'SLIDER', 'POPOUT', 'PRESET'} and action in ACTIONS:
        operator = tools._operator(action)
        text = operator.get_rna_type().description if operator else ACTIONS[action][2]
        from ..constants import BREAKDOWN_ANCHOR_HINT
        lines = [(ACTIONS[action][2], 'TITLE'), (text.rstrip('.') + '.', 'BODY'),
                 (f'Works on: {command_metadata(action)[0]}.', 'DETAIL'),
                 ('Drag to preview; release to apply; Esc cancels. Right-click for tool settings.', 'DETAIL')]
        if action == 'DRAG':
            lines.append((BREAKDOWN_ANCHOR_HINT, 'DETAIL'))
        return lines
    text = ANIMASSIST_OT_overlay_control.description(context, SimpleNamespace(kind=kind, key=key))
    return [(text.rstrip('.') + '.', 'BODY')]


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
        if properties.kind in {'STAGE','STAGE_CYCLE','STAGE_ITEM'}:
            shown = current_stage(context) if properties.kind == 'STAGE_CYCLE' else properties.key
            return _stage_description('STAGE' if properties.kind == 'STAGE_ITEM' else properties.kind, shown)
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
            _stage_menu[context.window.as_pointer()] = context.area.as_pointer()
            context.area.tag_redraw()
            return {"FINISHED"}
        return {"FINISHED"}


class ANIMASSIST_MT_timeline_stage(bpy.types.Menu):
    bl_idname = "ANIMASSIST_MT_timeline_stage"
    bl_label = "Anim Assist Stage"
    bl_description = "Choose which stage toolset the Timeline row shows"

    def draw(self, context):
        workspace = getattr(context, "workspace", None)
        if workspace is not None and hasattr(workspace, STAGE_PROPERTY):
            self.layout.props_enum(workspace, STAGE_PROPERTY)


class ANIMASSIST_OT_timeline_stage(bpy.types.Operator):
    bl_idname = "animassist.timeline_stage"
    bl_label = "Anim Assist Stage"
    bl_description = "Show one animation stage's tool families in the Timeline band"
    bl_options = {"INTERNAL"}
    stage: StringProperty(options={"HIDDEN", "SKIP_SAVE"})
    step: IntProperty(options={"HIDDEN", "SKIP_SAVE"})

    @classmethod
    def poll(cls, context):
        workspace = getattr(context, "workspace", None)
        return workspace is not None and hasattr(workspace, STAGE_PROPERTY)

    def execute(self, context):
        stage = model.next_stage(current_stage(context), self.step) if self.step else self.stage
        if stage not in model.STAGE_IDS:
            self.report({"WARNING"}, "Choose a known stage")
            return {"CANCELLED"}
        setattr(context.workspace, STAGE_PROPERTY, stage)  # update redraws Timelines
        return {"FINISHED"}


_handle = None
_epoch = object()
_keymaps = []
_initialized = set()
_hover = {}
# Window -> area pointer whose stage dropdown is open (drawn by this band, not a Blender menu,
# so it never opens over the stage button and a second click on the button closes it).
_stage_menu = {}
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
    stage = current_stage(context)
    labels={**QUICK_LABELS,**ROW_LABELS,**(ALL_ROW_LABELS if stage == 'ALL' else {})}
    items = model.toolbar_layout(context.region.width, usable_height, h, False,
                       record,GROUPS,labels,lambda text: blf.dimensions(0, text)[0],
                       stage)
    items = [(kind, key, label, (x, iy+y, w, ih)) for kind, key, label, (x, iy, w, ih) in items]
    return items, (0, y, context.region.width, min(h, context.region.height))


def _menu_open(context):
    window, area = context.window, context.area
    return bool(window and area and _stage_menu.get(window.as_pointer()) == area.as_pointer())


def _close_stage_menu(context):
    if context.window and _stage_menu.pop(context.window.as_pointer(), None):
        for area in context.window.screen.areas:
            area.tag_redraw()


def _menu_items(context, items, band):
    """Rects of the open stage dropdown: a list above the stage button, or one
    row of the five stages when the Timeline is too short for the list."""
    button = next((item for item in items if item[0] == 'STAGE_CYCLE'), None)
    if button is None:
        return []
    scale = context.preferences.system.ui_scale
    bx, _by, bw, bh = button[3]
    gap, pad = 2 * scale, 8 * scale
    blf.size(0, round(11 * scale))
    stages = [(key, label) for key, label, _families in model.STAGES]
    top = band[1] + band[3] + gap
    region_w, region_h = context.region.width, context.region.height
    if top + len(stages) * (bh + gap) <= region_h:
        width = max(bw, max(blf.dimensions(0, label)[0] for _key, label in stages) + 2 * pad)
        x = max(0, min(bx, region_w - width))
        return [('STAGE_ITEM', key, label, (x, top + (len(stages) - 1 - index) * (bh + gap), width, bh))
                for index, (key, label) in enumerate(stages)]
    result, x = [], bx
    for key, label in stages:
        width = blf.dimensions(0, label)[0] + 2 * pad
        result.append(('STAGE_ITEM', key, label, (x, top, width, bh)))
        x += width + gap
    shift = max(0, x - region_w)
    return [(kind, key, label, (rx - shift, ry, rw, rh)) for kind, key, label, (rx, ry, rw, rh) in result]


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
    gpu.state.blend_set('ALPHA')
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


# Key-type icons match the Dope Sheet: the theme's key colours (bright "selected"
# variants, readable on the row) and Blender's relative diamond sizes, so the type
# reads by shape and size as well as colour.
_KEY_ICONS = {
    'TYPE_KEYFRAME': ('keyframe_selected', 1.0, (1.0, .745, .196)),
    'TYPE_BREAKDOWN': ('keyframe_breakdown_selected', .85, (.353, .808, 1.0)),
    'TYPE_EXTREME': ('keyframe_extreme_selected', 1.2, (1.0, .631, .631)),
    'TYPE_HOLD': ('keyframe_moving_hold_selected', .925, (1.0, .937, .945)),
    'TYPE_JITTER': ('keyframe_jitter_selected', .8, (.529, 1.0, .361)),
}


def key_icon_style(context, action):
    """(fill RGB, border RGB, size factor) for a key-type icon, from the theme."""
    name, factor, fallback = _KEY_ICONS[action]
    try:
        anim = context.preferences.themes[0].common.anim
        fill = tuple(getattr(anim, name))[:3]
    except (AttributeError, IndexError, TypeError):
        fill = fallback
    try:
        border = tuple(context.preferences.themes[0].dopesheet_editor.keyframe_border)[:3]
    except (AttributeError, IndexError, TypeError):
        border = (0., 0., 0.)
    return fill, border, factor


def _key_icon(rect, context, action, alpha):
    fill, border, factor = key_icon_style(context, action)
    x, y, w, h = rect
    cx, cy = x + w / 2, y + h / 2
    r = min(w, h) * .30 * factor
    gpu.state.blend_set('ALPHA')  # text drawing can leave blending off; faded icons need it
    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    for radius, color in ((r + 1.5, (*border, alpha)), (r, (*fill, alpha))):
        positions = ((cx, cy + radius), (cx + radius, cy), (cx, cy - radius),
                     (cx, cy + radius), (cx, cy - radius), (cx - radius, cy))
        batch = batch_for_shader(shader, 'TRIS', {'pos': positions})
        shader.bind(); shader.uniform_float('color', color); batch.draw(shader)


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
            action=_tool_action(kind,key)
            highlighted = hover == (context.area.as_pointer(), kind, key)
            reason = tools._unavailable(context, context.area, action) if action else ""
            color = widgets.inner_sel if highlighted else widgets.inner
            _quad(rect,tuple(color) if kind!='MENU' else (*background[:3],1))
            text_color = widgets.text_sel if highlighted else widgets.text
            ink=(*text_color[:3],.45 if reason else 1)
            accent=_COLORS.get(FAMILY[action][0] if action in FAMILY else key,ink)
            if kind in {'STAGE','STAGE_CYCLE'}:
                shown = stage if kind=='STAGE_CYCLE' else key
                current = kind=='STAGE_CYCLE' or key==stage
                if current and kind=='STAGE' and not highlighted:
                    _quad(rect,tuple(widgets.inner_sel))
                if current and shown!='ALL':
                    # Underline in the colour of the stage's first family.
                    _quad((rect[0]+3*scale,rect[1]+2*scale,rect[2]-6*scale,2*scale),
                          _COLORS[model.stage_families(shown)[0]])
                text_rect=rect
                blf.size(0,round(11*scale))
                arrow=0
                if kind=='STAGE_CYCLE' and rect[2]>=blf.dimensions(0,label)[0]+(model.STAGE_ARROW+8)*scale:
                    arrow=model.STAGE_ARROW*scale
                    text_rect=(rect[0],rect[1],rect[2]-arrow,rect[3])
                ink_text=(*widgets.text_sel[:3],1) if current or highlighted else ink
                _text(text_rect,label,ink_text,scale)
                if arrow:
                    # Dropdown arrow: three stacked bars narrowing downward.
                    ax=rect[0]+rect[2]-arrow*.6; ay=rect[1]+rect[3]/2
                    for row,half in enumerate((3,2,1)):
                        _quad((ax-half*scale,ay+(1-row)*scale,2*half*scale,scale),ink_text)
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
            elif not label and action in _KEY_ICONS:
                _key_icon(rect,context,action,ink[3])
            elif not label:
                _glyph(rect,action if action else kind,(*accent[:3],ink[3]))
            else:
                _text(rect,label,(*accent[:3],ink[3]) if kind=='MENU' else ink,scale)
                if kind=='POPOUT': _quad((rect[0]+3*scale,rect[1]+2*scale,rect[2]-6*scale,1*scale),accent)
        if _menu_open(context):
            menu = _menu_items(context, items, band)
            if menu:
                xs = [r[0] for *_k, r in menu]; ys = [r[1] for *_k, r in menu]
                x1 = max(r[0] + r[2] for *_k, r in menu); y1 = max(r[1] + r[3] for *_k, r in menu)
                _quad((min(xs) - 2 * scale, min(ys) - 2 * scale, x1 - min(xs) + 4 * scale, y1 - min(ys) + 4 * scale),
                      (.08, .08, .08, .97))
                for _kind, key, label, rect in menu:
                    lit = key == stage or hover == (context.area.as_pointer(), 'STAGE_ITEM', key)
                    _quad(rect, tuple(widgets.inner_sel) if lit else tuple(widgets.inner))
                    if key == stage and key != 'ALL':
                        _quad((rect[0] + 3 * scale, rect[1] + 2 * scale, rect[2] - 6 * scale, 2 * scale),
                              _COLORS[model.stage_families(key)[0]])
                    _text(rect, label, (*(widgets.text_sel if lit else widgets.text)[:3], 1), scale)
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
        if not active and hover and not _menu_open(context) and time.monotonic() - _hover_started.get(context.window.as_pointer(), float("inf")) > .6:
            item = next((item for item in items if (item[0], item[1]) == hover[1:]), None)
            if item:
                paragraphs = _tooltip_paragraphs(context, item)
                blf.size(0, round(11 * scale))
                line_h, pad = 15 * scale, 7 * scale
                lines, width, height = model.fit_tooltip(
                    paragraphs, context.region.width, context.region.height,
                    lambda text: blf.dimensions(0, text)[0], scale, line_h, pad, 420 * scale)
                if lines:
                    x = max(0, min(item[3][0], context.region.width-width))
                    # The playhead is drawn over add-on drawing; keep the box clear of it.
                    try:
                        head = context.region.view2d.view_to_region(context.scene.frame_current, 0, clip=False)[0]
                    except (AttributeError, TypeError):
                        head = None
                    if head is not None and x - 3*scale <= head <= x + width + 3*scale:
                        right, left = head + 4*scale, head - 4*scale - width
                        if right + width <= context.region.width:
                            x = right
                        elif left >= 0:
                            x = left
                    above, below = band[1], context.region.height-band[1]-band[3]
                    if above >= height + 4*scale or above >= below:
                        y = band[1]-height-4*scale
                    else:
                        y = band[1]+band[3]+4*scale
                    y = max(0, min(y, context.region.height-height))
                    _quad((x, y, width, height), (.06, .06, .06, .97))
                    colors = {'TITLE': (1, 1, 1, 1), 'BODY': (.92, .92, .92, 1),
                              'DETAIL': (.70, .70, .70, 1), 'WARNING': (1, .72, .35, 1)}
                    for index, (line, role) in enumerate(lines):
                        blf.color(0, *colors.get(role, colors['BODY']))
                        blf.position(0, x+pad, y+height-pad-(index+1)*line_h+4*scale, 0)
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
        pointer = context.window.as_pointer()
        menu = _menu_items(context, items, band) if _menu_open(context) else []
        in_menu = next((item for item in menu if _inside(item[3], point)), None)
        found = in_menu or (next((item for item in items if _inside(item[3], point)), None) if hit else None)
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
        if menu and event.type == "ESC":
            _close_stage_menu(context)
            return {"FINISHED"}
        if menu and event.type in {"LEFTMOUSE", "RIGHTMOUSE"}:
            # While open: pick a stage, or close on any other click in this Timeline
            # (including the stage button itself) without acting on what is underneath.
            _close_stage_menu(context)
            if in_menu and event.type == "LEFTMOUSE":
                bpy.ops.animassist.timeline_stage(stage=in_menu[1])
            return {"FINISHED"}
        if event.type == "ESC":
            return {"CANCELLED", "PASS_THROUGH"}
        if event.type == "MOUSEMOVE" or not hit:
            return {"CANCELLED", "PASS_THROUGH"}
        if (event.type in {'WHEELUPMOUSE','WHEELDOWNMOUSE'} and event.ctrl and found
                and found[0] in {'STAGE','STAGE_CYCLE'}):
            bpy.ops.animassist.timeline_stage(step=1 if event.type=='WHEELDOWNMOUSE' else -1)
            return {'FINISHED'}
        if event.type=='RIGHTMOUSE' and found:
            action=_tool_action(found[0],found[1])
            if action:
                bpy.ops.animassist.tool_settings('INVOKE_DEFAULT',action=action)
                return {'FINISHED'}
        if event.type == "LEFTMOUSE" and found and found[0] == 'STAGE_CYCLE':
            _stage_menu[pointer] = context.area.as_pointer()  # one click opens; stays open
            context.area.tag_redraw()
            return {"FINISHED"}
        if event.type == "LEFTMOUSE" and found:
            action=_tool_action(found[0],found[1])
            from . import timeline_strip as tools
            reason=tools._unavailable(context,context.area,action) if action else ''
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
        if not context.window:
            return False
        pointer = context.window.as_pointer()
        if not (_hover.get(pointer) or _stage_menu.get(pointer)):
            return False
        return not (tools.is_timeline(context.area) and context.region
                    and context.region.type == "WINDOW")

    def invoke(self, context, event):
        _hover.pop(context.window.as_pointer(), None)
        if event.type == "LEFTMOUSE":
            _stage_menu.pop(context.window.as_pointer(), None)
        for area in context.window.screen.areas:
            area.tag_redraw()
        return {"CANCELLED", "PASS_THROUGH"}


class ANIMASSIST_OT_close_stage_menu(bpy.types.Operator):
    bl_idname = "animassist.close_stage_menu"
    bl_label = "Close Anim Assist Stage List"
    bl_options = {"INTERNAL"}

    @classmethod
    def poll(cls, context):
        return bool(context.window and _stage_menu.get(context.window.as_pointer()))

    def invoke(self, context, _event):
        _close_stage_menu(context)
        return {"FINISHED"}


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
            if hasattr(context.workspace, STAGE_PROPERTY):
                self.layout.prop_menu_enum(context.workspace, STAGE_PROPERTY, text="Anim Assist Stage")
            self.layout.menu("ANIMASSIST_MT_timeline_tools", text="Anim Assist Tools")


@bpy.app.handlers.persistent
def _load_post(_unused):
    global _epoch
    _epoch = object()
    _hover.clear()
    _stage_menu.clear()
    _hover_started.clear()
    _initialized.clear()


_CLASSES = (ANIMASSIST_OT_overlay_control, ANIMASSIST_MT_timeline_stage, ANIMASSIST_OT_timeline_stage,
            ANIMASSIST_OT_close_stage_menu,
            ANIMASSIST_OT_timeline_overlay_events, ANIMASSIST_OT_clear_timeline_hover)


def _stage_update(workspace, _context):
    # Tabs, Toolbar Settings and the View menu all set the stage; redraw every
    # Timeline showing this workspace so the row follows immediately.
    from . import timeline_strip as tools, timeline_settings
    timeline_settings.on_stage_changed(workspace)
    manager = getattr(bpy.context, "window_manager", None)
    for window in getattr(manager, "windows", ()):
        if window.workspace == workspace:
            for area in window.screen.areas:
                if tools.is_timeline(area):
                    area.tag_redraw()


def _stage_items():
    # Explicit, permanent numbers: the .blend stores the number, so reordering
    # STAGES later must not change saved stages.
    return [(key, label, "The All overview of every tool family" if families is None
             else f"The {label} toolset: {_family_labels(key)}", model.STAGE_NUMBERS[key])
            for key, label, families in model.STAGES]


def register():
    global _handle, _epoch
    _epoch = object()
    for cls in _CLASSES:
        bpy.utils.register_class(cls)
    setattr(bpy.types.WorkSpace, STAGE_PROPERTY, EnumProperty(
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
            item = screen.keymap_items.new(ANIMASSIST_OT_clear_timeline_hover.bl_idname,
                                           type="LEFTMOUSE", value="PRESS", any=True)
            _keymaps.append((screen, item))
            # Esc closes an open stage list from anywhere in the window.
            item = screen.keymap_items.new(ANIMASSIST_OT_close_stage_menu.bl_idname, type="ESC", value="PRESS")
            _keymaps.append((screen, item))
            for name in ("Dopesheet", "Dopesheet Generic"):
                keymap = config.keymaps.new(name=name, space_type="DOPESHEET_EDITOR", region_type="WINDOW")
                for event_type in ("MOUSEMOVE", "LEFTMOUSE", "RIGHTMOUSE", "MIDDLEMOUSE", "WHEELUPMOUSE", "WHEELDOWNMOUSE"):
                    item = keymap.keymap_items.new(ANIMASSIST_OT_timeline_overlay_events.bl_idname,
                                                  type=event_type, value="ANY" if event_type=="MOUSEMOVE" else "PRESS", any=True)
                    _keymaps.append((keymap, item))
                item = keymap.keymap_items.new(ANIMASSIST_OT_timeline_overlay_events.bl_idname,
                                              type="ESC", value="PRESS")
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
    _stage_menu.clear()
    _hover_started.clear()
    for keymap, item in _keymaps:
        keymap.keymap_items.remove(item)
    _keymaps.clear()
    if hasattr(bpy.types.WorkSpace, STAGE_PROPERTY):
        delattr(bpy.types.WorkSpace, STAGE_PROPERTY)
    for cls in reversed(_CLASSES):
        if "bl_rna" in cls.__dict__:
            bpy.utils.unregister_class(cls)
