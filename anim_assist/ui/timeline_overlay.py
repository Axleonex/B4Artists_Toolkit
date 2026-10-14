"""Add-on-only Timeline tool band, using the supported pixel draw handler.

A collapsed Timeline receives space once when first enabled. The band covers
one header-height of the WINDOW region; later resizing is never repaired.
"""

import bpy
import blf
import gpu
import textwrap
import time
from types import SimpleNamespace
from gpu_extras.batch import batch_for_shader
from bpy.props import StringProperty
from .timeline_catalog import ACTIONS, GROUPS, QUICK_LABELS, quick_clusters, selected_quick_actions


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
        if properties.kind == "ACTION" and properties.key in ACTIONS:
            return tools.ANIMASSIST_OT_timeline_tool.description(
                context, SimpleNamespace(action=properties.key))
        return {"SEARCH": "Find an animation tool; run it or pin a quick button",
                "SETTINGS": "Choose which one-click tools appear beside each family",
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
            return bpy.ops.wm.call_panel("INVOKE_DEFAULT", name="ANIMASSIST_PT_timeline_quick_settings")
        if self.kind == "MENU":
            return bpy.ops.wm.call_menu("INVOKE_DEFAULT", name=tools._menu_id(self.key))
        if self.kind == "MORE":
            return bpy.ops.wm.call_menu("INVOKE_DEFAULT", name="ANIMASSIST_MT_timeline_more")
        return {"FINISHED"}


_handle = None
_epoch = object()
_keymaps = []
_initialized = set()
_hover = {}
_hover_started = {}


def _items(context):
    from ..prefs import get_prefs
    header = next((r for r in context.area.regions if r.type == "HEADER"), None)
    scale = context.preferences.system.ui_scale
    h = max(24 * scale, header.height if header else 0)
    blf.size(0, round(11 * scale))
    top = bool(header and header.y > context.region.y)
    # Bforartists draws its frame indicator after pixel callbacks. Preserve
    # the native scrub ruler at the top, so it cannot cover an action button.
    ruler = 24 * scale if top else 0
    usable_height = max(0, context.region.height-ruler)
    items = row_layout(context.region.width, usable_height, h, top,
                       quick_clusters(selected_quick_actions(get_prefs(context))),
                       lambda text: blf.dimensions(0, text)[0])
    y = max(0, usable_height-h) if top else 0
    return items, (0, y, context.region.width, min(h, context.region.height))


def _inside(rect, location):
    x, y, w, h = rect
    return x <= location[0] < x+w and y <= location[1] < y+h


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
    old_blend = gpu.state.blend_get()
    try:
        gpu.state.blend_set("ALPHA")
        _quad(band, (*background[:3], 1))
        hover = _hover.get(context.window.as_pointer())
        for kind, key, label, rect in items:
            highlighted = hover == (context.area.as_pointer(), kind, key)
            reason = tools._unavailable(context, context.area, key) if kind == "ACTION" else ""
            color = widgets.inner_sel if highlighted else widgets.inner
            _quad(rect, tuple(color))
            text_color = widgets.text_sel if highlighted else widgets.text
            blf.size(0, round(11 * scale))
            blf.color(0, *text_color[:3], .45 if reason else 1)
            tw, th = blf.dimensions(0, label)
            x, y, w, h = rect
            blf.position(0, x + (w-tw)/2, y + (h-th)/2 + 1, 0)
            blf.draw(0, label)
        # Thin separator, respecting top and bottom header placement.
        _quad((band[0], band[1], band[2], 1), (*widgets.outline[:3], 1))
        if hover and time.monotonic() - _hover_started.get(context.window.as_pointer(), float("inf")) > .6:
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
        if event.type == "LEFTMOUSE" and found:
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
    from ..prefs import get_prefs
    prefs = get_prefs()
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
            self.layout.menu("ANIMASSIST_MT_timeline_tools", text="Anim Assist Tools")


@bpy.app.handlers.persistent
def _load_post(_unused):
    global _epoch
    _epoch = object()
    _hover.clear()
    _hover_started.clear()
    _initialized.clear()


_CLASSES = (ANIMASSIST_OT_overlay_control, ANIMASSIST_OT_timeline_overlay_events,
            ANIMASSIST_OT_clear_timeline_hover)


def register():
    global _handle, _epoch
    _epoch = object()
    for cls in _CLASSES:
        bpy.utils.register_class(cls)
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
        bpy.app.timers.register(_start_windows, first_interval=.1, persistent=True)


def unregister():
    global _handle, _epoch
    _epoch = object()
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
    for cls in reversed(_CLASSES):
        if "bl_rna" in cls.__dict__:
            bpy.utils.unregister_class(cls)
