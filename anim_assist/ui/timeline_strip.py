"""A native editor strip above Timeline, identified by an owned Text datablock.

Timeline has no second header region. A small Text editor split supplies the
extra row; its buttons invoke existing operators in the Timeline below it.
Private hook: TEXT_HT_header.draw._draw_funcs, initialized by Header.append.
Checked: Blender 5.1.2 stand-in, 2026-10-12. If unavailable, keep native shortcuts.
"""

import bpy
from math import ceil
from time import monotonic
from bpy.props import StringProperty
from ..core.logging import get_logger
from .timeline_catalog import (
    ACTIONS as _ACTIONS, EXECUTE_ACTIONS, GROUPS, QUICK_GROUPS,
    command_description, command_metadata, QUICK_LABELS,
    DEFAULT_QUICK_ACTIONS, quick_property_name, selected_quick_actions, quick_clusters,
)

_log = get_logger(__name__)
_MARKER = "animassist_timeline_toolbar"
_original_draw = None
_failed_splits: dict[int, tuple] = {}


def _layout_signature(area):
    header = next((r for r in area.regions if r.type == "HEADER"), None)
    return (area.x, area.y, area.width, area.height,
            header.height if header else 0, bpy.context.preferences.system.ui_scale)


def _remember_failure(area):
    # Retry after resizing or a transient unavailable screen operator. A failed
    # split must not blacklist this Timeline for the rest of the session.
    _failed_splits[area.as_pointer()] = (_layout_signature(area), monotonic() + 5.0)


def _retry_blocked(area):
    failed = _failed_splits.get(area.as_pointer())
    return bool(failed and failed[0] == _layout_signature(area)
                and monotonic() < failed[1])


def _row_height(area):
    scale = max(0.5, bpy.context.preferences.system.ui_scale)
    header = next((r for r in area.regions if r.type == "HEADER"), None)
    return max(header.height if header else 0, ceil(24 * scale)) + ceil(4 * scale)


def _timeline_min_height(area):
    scale = max(0.5, bpy.context.preferences.system.ui_scale)
    header = next((r for r in area.regions if r.type == "HEADER"), None)
    # Leave a frame ruler AND an editable key region below the native header.
    return (header.height if header else 0) + ceil(48 * scale)


def _fit_strip(window, screen, strip, target):
    desired = max(_row_height(target), _row_height(strip))
    border = ceil(4 * max(0.5, bpy.context.preferences.system.ui_scale))
    minimum = desired + _timeline_min_height(target) + border
    combined = strip.height + target.height + (strip.y - target.y - target.height)
    if (combined < minimum or abs(strip.height - desired) > border
            or target.height < _timeline_min_height(target)):
        # area_move polls the screen's actual mouse region, so it cannot be
        # driven reliably from a timer. Rejoin this owned pair and let the next
        # tick split it again. The surviving Timeline keeps its native state.
        # If the whole pair was collapsed, keep a usable Timeline until enlarged.
        _remove_strip(window, screen, strip)
        return True
    return False

def is_strip(area):
    return (area.type == "TEXT_EDITOR"
            and area.spaces.active.text is not None
            and area.spaces.active.text.get(_MARKER) == 1)


def is_timeline(area):
    return area.type == "DOPESHEET_EDITOR" and area.spaces.active.mode == "TIMELINE"


def timeline_below(screen, strip):
    if screen is None or strip is None or not is_strip(strip):
        return None
    # Native editor borders grow with UI scale. A fixed four-pixel threshold
    # misses a 150% border and causes _sync to create duplicate owned rows.
    scale = max(0.5, bpy.context.preferences.system.ui_scale)
    edge = ceil(2 * scale)
    border = ceil(4 * scale)
    return next((a for a in screen.areas if is_timeline(a)
                 and abs(a.x - strip.x) <= edge
                 and abs(a.width - strip.width) <= edge
                 and abs(a.y + a.height - strip.y) <= border), None)


def hides_native_shortcuts(context):
    """Hide originals only after the strip is present and actually paired."""
    return (context.area is not None and is_timeline(context.area)
            and any(is_strip(a) and timeline_below(context.screen, a) == context.area
                    for a in context.screen.areas))


def _enabled():
    from ..prefs import get_prefs
    prefs = get_prefs()
    return prefs is None or prefs.timeline_toolbar_row


def _operator(action):
    return getattr(bpy.ops.animassist, _ACTIONS[action][0])


def _window_region(area):
    return next(r for r in area.regions if r.type == "WINDOW")


def _unavailable(context, target, action):
    if target is None:
        return "Place this toolbar directly above a Timeline"
    with context.temp_override(area=target, region=_window_region(target)):
        selected_actions = {"NEIGHBORS", "FRAME", "EASE", "AMPLIFY", "SMOOTH"}
        if action in selected_actions or action.startswith(("HANDLE_", "TYPE_", "NUDGE_")):
            if action in selected_actions:
                from ..operators.curve_tool_ops import _editable_fcurves
                curves = _editable_fcurves(context)
            else:
                from ..operators.keymanager_ops import _visible_fcurves
                curves = _visible_fcurves(context)
            if not any(k.select_control_point for fc in curves for k in fc.keyframe_points):
                return "Select editable keys on an animated object"
        if action in {"INBETWEEN", "INBETWEENS"}:
            from ..operators.p3_inbetween_ops import _selected_frames
            obj = context.active_object
            if obj is None or len(_selected_frames(obj)) < 2:
                return "Select two bounding keys with a gap"
        if action == "OFFSET" and not context.scene.anim_assist.anim_offset_active:
            from ..operators.anim_offset_ops import _object_fcurves
            if not _object_fcurves(context):
                return "Select an object with editable Action curves"
        # A running Offset session can always be finished through its fixed
        # More entry, even after the active object is deselected.
        if action == "OFFSET" and context.scene.anim_assist.anim_offset_active:
            return ""
        if not _operator(action).poll():
            return command_metadata(action)[1]
    return ""


class ANIMASSIST_OT_timeline_tool(bpy.types.Operator):
    """Use an Anim Assist action in the Timeline directly below this toolbar"""

    bl_idname = "animassist.timeline_tool"
    bl_label = "Timeline Tool"
    bl_options = {"INTERNAL"}

    action: StringProperty(options={"HIDDEN", "SKIP_SAVE"})

    @classmethod
    def poll(cls, context):
        if timeline_below(context.screen, context.area) is None:
            cls.poll_message_set("Place this toolbar directly above a Timeline")
            return False
        return True

    @classmethod
    def description(cls, context, properties):
        action = properties.action
        if action not in _ACTIONS:
            return cls.__doc__
        description = command_description(action, _operator(action).get_rna_type().description)
        reason = _unavailable(context, timeline_below(context.screen, context.area), action)
        if action in {"OFFSET", "OFFSET_MASK", "OFFSET_SCENE_RANGE"}:
            from ..operators.anim_offset_ops import offset_session_status
            status = offset_session_status(context.scene)
            if status:
                description += f" Active session: {status}."
        return description + (f" Unavailable: {reason}." if reason else "")

    def invoke(self, context, _event):
        return self.execute(context)

    def execute(self, context):
        target = timeline_below(context.screen, context.area)
        if target is None or self.action not in _ACTIONS:
            self.report({"WARNING"}, "This toolbar needs a Timeline directly below")
            return {"CANCELLED"}
        try:
            reason = _unavailable(context, target, self.action)
            if reason:
                self.report({"WARNING"}, reason)
                return {"CANCELLED"}
            with context.temp_override(area=target, region=_window_region(target)):
                operator = _operator(self.action)
                if (self.action == "OFFSET" and context.scene.anim_assist.anim_offset_active
                        and not operator.poll()):
                    context.scene.anim_assist.anim_offset_active = False
                    return {"FINISHED"}
                if not operator.poll():
                    self.report({"WARNING"}, "Select editable animation for this Timeline tool")
                    return {"CANCELLED"}
                # Fixed nudges run immediately; INVOKE preserves other modal tools.
                # Explicitly enable undo for the Python call. Otherwise nested
                # UI dispatch edits data without a redoable target undo step.
                # The existing target owns that step; the wrapper has no UNDO.
                mode = "EXEC_DEFAULT" if self.action in EXECUTE_ACTIONS else "INVOKE_DEFAULT"
                result = operator(mode, True, **_ACTIONS[self.action][1])
            return {"CANCELLED"} if "CANCELLED" in result else {"FINISHED"}
        except (RuntimeError, ReferenceError) as exc:
            self.report({"WARNING"}, str(exc))
            return {"CANCELLED"}


def _button(layout, context, target, action, text="", icon="NONE", depress=False):
    row = layout.row(align=True)
    row.enabled = not _unavailable(context, target, action)
    row.operator_context = "INVOKE_DEFAULT"
    op = row.operator("animassist.timeline_tool", text=text, icon=icon, depress=depress)
    op.action = action


def _menu_id(key):
    return f"ANIMASSIST_MT_timeline_{key}"


def _build_menu(key, label, actions):
    def draw(self, context):
        target = timeline_below(context.screen, context.area)
        for action in actions:
            if action is None:
                self.layout.separator()
            else:
                _button(self.layout, context, target, action, _ACTIONS[action][2])
        self.layout.separator()
        self.layout.operator("animassist.open_home", text="Open Anim Assist Panel", icon="PROPERTIES")

    name = _menu_id(key)
    return type(name, (bpy.types.Menu,), {"bl_idname": name, "bl_label": label, "draw": draw})


_menus = [_build_menu(*group) for group in GROUPS]
_registered_menus = []


class ANIMASSIST_MT_timeline_tools(bpy.types.Menu):
    bl_label = "Anim Assist Tools"
    bl_description = "All seven animation families in their permanent order"

    def draw(self, context):
        for key, label, _actions in GROUPS:
            self.layout.menu(_menu_id(key), text=label)


class ANIMASSIST_MT_timeline_more(bpy.types.Menu):
    bl_label = "More Anim Assist Shortcuts"
    bl_description = "All original quick commands; the pause icon indicates an active Action Offset session"

    def draw(self, context):
        target = timeline_below(context.screen, context.area)
        for key, label, actions in QUICK_GROUPS:
            self.layout.separator()
            self.layout.label(text=label)
            for action in actions:
                active = action == "OFFSET" and context.scene.anim_assist.anim_offset_active
                _button(self.layout, context, target, action, _ACTIONS[action][2],
                        icon="PAUSE" if active else "NONE", depress=active)
        self.layout.separator()
        self.layout.menu("ANIMASSIST_MT_timeline_tools", text="All Tools")


_menus.extend([ANIMASSIST_MT_timeline_tools, ANIMASSIST_MT_timeline_more])


class ANIMASSIST_OT_reset_timeline_quick_defaults(bpy.types.Operator):
    bl_idname = "animassist.reset_timeline_quick_defaults"
    bl_label = "Reset All Quick Buttons to Defaults"
    bl_description = "Restore the 13 default quick buttons across all seven families"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        from ..prefs import get_prefs
        prefs = get_prefs(context)
        if prefs is None:
            self.report({"WARNING"}, "Enable Anim Assist in add-on preferences first")
            return {"CANCELLED"}
        for action in _ACTIONS:
            setattr(prefs, quick_property_name(action), action in DEFAULT_QUICK_ACTIONS)
        return {"FINISHED"}


class ANIMASSIST_PT_timeline_quick_settings(bpy.types.Panel):
    bl_label = "Timeline Quick Tools"
    bl_space_type = "TEXT_EDITOR"
    bl_region_type = "HEADER"
    bl_ui_units_x = 22

    def draw(self, context):
        from ..prefs import get_prefs, draw_timeline_quick_settings
        prefs = get_prefs(context)
        if prefs is None:
            self.layout.label(text="Enable Anim Assist in add-on preferences", icon="INFO")
        else:
            draw_timeline_quick_settings(self.layout, context, prefs)


_settings_classes = [ANIMASSIST_OT_reset_timeline_quick_defaults,
                     ANIMASSIST_PT_timeline_quick_settings]


def _draw_toolbar(self, context):
    layout = self.layout
    target = timeline_below(context.screen, context.area)
    if target is None:
        layout.label(text="Place above a Timeline", icon="INFO")
    from ..prefs import get_prefs
    layout.popover(panel="ANIMASSIST_PT_timeline_quick_settings", text="", icon="PREFERENCES")
    for key, label, actions in quick_clusters(selected_quick_actions(get_prefs(context))):
        layout.separator()
        row = layout.row(align=True)
        row.menu(_menu_id(key), text=label)
        for action in actions:
            active = action == "OFFSET" and context.scene.anim_assist.anim_offset_active
            _button(row, context, target, action, QUICK_LABELS.get(action, _ACTIONS[action][2]),
                    icon="PAUSE" if active else "MOUSE_MOVE" if action == "DRAG" else "NONE",
                    depress=active)


def _text_header(self, context):
    if context.area and is_strip(context.area):
        _draw_toolbar(self, context)
    elif _original_draw is not None:
        _original_draw(self, context)


def _marker_text():
    text = next((t for t in bpy.data.texts if t.get(_MARKER) == 1), None)
    if text is None:
        text = bpy.data.texts.new(".AnimAssist Timeline Toolbar")
        text[_MARKER] = 1
    text.use_fake_user = True  # Keep the saved screen's marker across file reopen.
    return text


def _split(window, screen, area):
    row_height = _row_height(area)
    border = ceil(4 * max(0.5, bpy.context.preferences.system.ui_scale))
    # Blender creates the upper copy only when factor > .5. Keep the original
    # Timeline in the lower half, with its native header, view and key settings.
    minimum = max(row_height + _timeline_min_height(area) + border,
                  2 * (row_height + border) + 1)
    if area.width < 240:
        return False
    if area.height < minimum:
        return False  # Never consume the frame ruler and editable key region.
    before = {a.as_pointer() for a in screen.areas}
    with bpy.context.temp_override(window=window, area=area):
        result = bpy.ops.screen.area_split(
            direction="HORIZONTAL", factor=(area.height - row_height - border) / area.height)
    if "FINISHED" not in result:
        _remember_failure(area)
        return False
    # Native horizontal split retains the original lower area and creates upper.
    # New geometry is zero until redraw; never use those dimensions for pairing.
    strip = next(a for a in screen.areas if a.as_pointer() not in before)
    strip.type = "TEXT_EDITOR"
    space = strip.spaces.active
    space.text = _marker_text()
    space.show_region_header = True
    space.show_region_footer = False
    space.show_region_ui = False
    space.show_line_numbers = False
    space.show_syntax_highlight = False
    space.show_line_highlight = False
    strip.tag_redraw()
    area.tag_redraw()
    return True


def _remove_strip(window, screen, strip):
    target = timeline_below(screen, strip)
    if target is None:
        target = _timeline_above(screen, strip)
    if target is None:
        # Do not join or overwrite an unrelated editor after manual rearrangement.
        strip.spaces.active.text = None
        strip.tag_redraw()
        return
    with bpy.context.temp_override(window=window, screen=screen, area=target):
        # Source survives the join. Keep Timeline (including view and key settings).
        bpy.ops.screen.area_join(
            source_xy=(target.x + target.width // 2, target.y + target.height // 2),
            target_xy=(strip.x + strip.width // 2, strip.y + strip.height // 2))


def _timeline_above(screen, strip):
    """Recognize an inverted owned pair left by older split geometry."""
    scale = max(0.5, bpy.context.preferences.system.ui_scale)
    return next((a for a in screen.areas if is_timeline(a)
                 and abs(a.x - strip.x) <= ceil(2 * scale)
                 and abs(a.width - strip.width) <= ceil(2 * scale)
                 and abs(strip.y + strip.height - a.y) <= ceil(4 * scale)), None)


def _sync():
    try:
        windows = list(bpy.context.window_manager.windows)
        enabled = _enabled() and _original_draw is not None
        if not enabled:
            # Screen overrides also restore owned strips in inactive workspaces.
            if windows:
                for screen in bpy.data.screens:
                    if screen.is_temporary or screen.show_fullscreen:
                        continue
                    strip = next((a for a in screen.areas if is_strip(a)), None)
                    if strip:
                        _remove_strip(windows[0], screen, strip)
                        return 0.2
            _failed_splits.clear()
        else:
            for window in windows:
                screen = window.screen
                if screen.is_temporary or screen.show_fullscreen:
                    continue
                # Wait for native redraw after a split before looking for a pair.
                if any(is_strip(a) and a.width == 0 for a in screen.areas):
                    return 0.2
                for strip in list(screen.areas):
                    if not is_strip(strip) or _retry_blocked(strip):
                        continue
                    try:
                        target = timeline_below(screen, strip)
                        if target is None and _timeline_above(screen, strip) is not None:
                            # Rejoin only the owned, directly adjacent inverted
                            # pair; the next tick recreates the row above it.
                            _remove_strip(window, screen, strip)
                            return 0.2
                        if target is not None and _fit_strip(window, screen, strip, target):
                            return 0.2
                    except (RuntimeError, ReferenceError, StopIteration) as exc:
                        _remember_failure(strip)
                        _log.warning("Timeline toolbar size update deferred: %s", exc)
                for area in screen.areas:
                    if not is_timeline(area) or _retry_blocked(area):
                        continue
                    if any(is_strip(a) and timeline_below(screen, a) == area
                           for a in screen.areas):
                        continue
                    try:
                        if _split(window, screen, area):
                            return 0.2
                    except (RuntimeError, ReferenceError, StopIteration) as exc:
                        _remember_failure(area)
                        _log.warning("Timeline toolbar kept in native header: %s", exc)
    except (RuntimeError, ReferenceError, AttributeError) as exc:
        _log.warning("Timeline toolbar layout update deferred: %s", exc)
    return 1.0


def _initialize_draw_funcs(self, context):
    pass


def register():
    global _original_draw
    bpy.utils.register_class(ANIMASSIST_OT_timeline_tool)
    for cls in _settings_classes:
        bpy.utils.register_class(cls)
    for menu in _menus:
        bpy.utils.register_class(menu)
        _registered_menus.append(menu)
    header = bpy.types.TEXT_HT_header
    header.append(_initialize_draw_funcs)
    header.remove(_initialize_draw_funcs)
    funcs = getattr(header.draw, "_draw_funcs", None)
    if funcs:
        _original_draw = funcs[0]
        funcs[0] = _text_header
    else:
        _log.warning("Text header hook unavailable; keeping native Timeline toolbar")
    if not bpy.app.background and not bpy.app.timers.is_registered(_sync):
        bpy.app.timers.register(_sync, first_interval=0.25, persistent=True)


def unregister():
    global _original_draw
    if bpy.app.timers.is_registered(_sync):
        bpy.app.timers.unregister(_sync)
    windows = list(bpy.context.window_manager.windows)
    if windows:
        for screen in bpy.data.screens:
            if screen.is_temporary or screen.show_fullscreen:
                continue
            for strip in list(screen.areas):
                if is_strip(strip):
                    try:
                        _remove_strip(windows[0], screen, strip)
                    except (RuntimeError, ReferenceError) as exc:
                        _log.warning("Could not join Timeline toolbar: %s", exc)
    funcs = getattr(bpy.types.TEXT_HT_header.draw, "_draw_funcs", [])
    if funcs and funcs[0] is _text_header:
        funcs[0] = _original_draw
    _original_draw = None
    _failed_splits.clear()
    for menu in reversed(_registered_menus):
        bpy.utils.unregister_class(menu)
    _registered_menus.clear()
    for cls in reversed(_settings_classes):
        bpy.utils.unregister_class(cls)
    bpy.utils.unregister_class(ANIMASSIST_OT_timeline_tool)
