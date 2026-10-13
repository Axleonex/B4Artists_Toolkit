"""Timeline tools in the native TOOL_HEADER of a patched Bforartists host.

Unpatched hosts use the same controls in the existing Timeline header. No
Text Editor is created and no resize polling or private draw hook is used.
Marked, directly adjacent legacy strips are joined once during migration.
"""

import bpy
from math import ceil
from bpy.app.handlers import persistent
from bpy.props import StringProperty
from ..core.logging import get_logger
from .timeline_catalog import (
    ACTIONS as _ACTIONS, EXECUTE_ACTIONS, GROUPS, QUICK_GROUPS,
    command_description, command_metadata, QUICK_LABELS, search_actions,
    DEFAULT_QUICK_ACTIONS, quick_property_name, selected_quick_actions, quick_clusters,
)

_log = get_logger(__name__)
_MARKER = "animassist_timeline_toolbar"
_seen = set()
_owned = set()
_migration_attempted = set()
_legacy_candidates = set()
_capture_pending = False
_pending_user_action = set()
_registered = False
_force_reconcile = False


def is_timeline(area):
    return bool(area and area.type == "DOPESHEET_EDITOR"
                and area.spaces.active.mode == "TIMELINE")


def is_strip(area):
    """Recognize legacy ownership only; never mark or create new editors."""
    return bool(area and area.type == "TEXT_EDITOR"
                and area.spaces.active.text is not None
                and area.spaces.active.text.get(_MARKER) == 1)


def native_available():
    """Feature detection, including the host's safe native enable operation."""
    properties = bpy.types.SpaceDopeSheetEditor.bl_rna.properties
    if not all(name in properties for name in
               ("show_region_tool_header", "timeline_toolbar_hidden_by_user")):
        return False
    try:
        operation = bpy.ops.screen.timeline_toolbar_set.get_rna_type()
    except (RuntimeError, AttributeError):
        return False
    return all(name in operation.properties for name in ("enabled", "user_action"))


def native_visible(area):
    return (_enabled() and native_available() and is_timeline(area)
            and area.spaces.active.show_region_tool_header
            and any(r.type == "TOOL_HEADER" and r.height > 1 for r in area.regions))


def _enabled():
    from ..prefs import get_prefs
    prefs = get_prefs()
    return prefs is None or prefs.timeline_toolbar_row


def _target(context):
    return context.area if is_timeline(context.area) else None


def _window_region(area):
    return next(r for r in area.regions if r.type == "WINDOW")


def _operator(action):
    operator = getattr(bpy.ops.animassist, _ACTIONS[action][0])
    try:
        operator.get_rna_type()
    except (RuntimeError, AttributeError):
        return None
    return operator


def _switch_unavailable(context, action):
    from ..core.p8_properties import get_p8
    from ..operators.p8_switch_ops import _resolve_prop_owner, _get_prop_value
    settings = get_p8(context)
    obj = context.active_object
    if obj is None or settings is None or not settings.switch_prop_path:
        return "Configure an active object's rig property in Pose options"
    if obj.library and not obj.override_library:
        return "Use a local or overridden rig object"
    owner = _resolve_prop_owner(obj, settings.switch_bone_name)
    if owner is None:
        return "Choose an existing rig bone in Pose options"
    value = _get_prop_value(owner, settings.switch_prop_path)
    if not isinstance(value, (int, float)):
        return "Choose a writable numeric rig property; string enum properties are unsupported"
    if action == "SWITCH_BOOL" and value not in (0, 1):
        return "Choose a boolean rig property whose value is 0 or 1"
    if action == "SWITCH_INFLUENCE" and not 0 <= settings.switch_new_value <= 1:
        return "Set the rig influence target between 0 and 1 in Pose options"
    if action == "SWITCH_ENUM" and not float(settings.switch_new_value).is_integer():
        return "Set a whole-number rig target value in Pose options"
    path = settings.switch_prop_path
    if not (path.startswith('["') and path.endswith('"]')):
        try:
            if "." in path:
                parent_path, attribute = path.rsplit(".", 1)
                parent = owner.path_resolve(parent_path)
            else:
                parent, attribute = owner, path
            if parent.is_property_readonly(attribute):
                return "Choose a writable rig property in Pose options"
        except (AttributeError, ValueError, TypeError):
            return "Choose a supported rig property path in Pose options"
    return ""


def _unavailable(context, target, action):
    if target is None:
        return "Use an animation tool from a Timeline"
    operator = _operator(action)
    if operator is None:
        return "Enable the corresponding Anim Assist tool module"
    try:
        with context.temp_override(area=target, region=_window_region(target)):
            selected_actions = {"NEIGHBORS", "FRAME", "EASE", "AMPLIFY", "SMOOTH"}
            if action in selected_actions or action.startswith(("HANDLE_", "TYPE_", "NUDGE_")):
                if action in selected_actions:
                    from ..operators.curve_tool_ops import _editable_fcurves
                    curves = _editable_fcurves(context)
                elif action.startswith(("TYPE_", "NUDGE_")):
                    from ..operators.keymanager_ops import _object_fcurves
                    curves = _object_fcurves(context)
                else:
                    from ..operators.keymanager_ops import _visible_fcurves
                    curves = _visible_fcurves(context)
                if not any(k.select_control_point for fc in curves for k in fc.keyframe_points):
                    return "Select editable keys on an animated object"
            if action == "COPY_KEYS":
                from ..core.context_utils import iter_selected_keys
                if next(iter_selected_keys(context), None) is None:
                    return "Select editable keys to copy"
            if action == "PASTE_KEYS":
                from ..core.key_utils import clipboard_size
                if not clipboard_size():
                    return "Copy keys into the Anim Assist clipboard first"
            if action in {"BOOKMARK_RECALL", "BOOKMARK_REMOVE"}:
                settings = context.scene.anim_assist
                if not 0 <= settings.active_bookmark_index < len(settings.bookmarks):
                    return "Choose an existing reference bookmark in Curves options"
            if action.startswith("SWITCH_"):
                reason = _switch_unavailable(context, action)
                if reason:
                    return reason
            if action == "MIRROR_RANGE":
                scene = context.scene
                start = scene.frame_preview_start if scene.use_preview_range else scene.frame_start
                if start < 0:
                    return "Use a nonnegative preview/playback range for Mirror Range"
            if action in {"INBETWEEN", "INBETWEENS"}:
                from ..operators.p3_inbetween_ops import _selected_frames
                obj = context.active_object
                if obj is None or len(_selected_frames(obj)) < 2:
                    return "Select two bounding keys with a gap"
            if action == "OFFSET":
                if context.scene.anim_assist.anim_offset_active:
                    return ""
                from ..operators.anim_offset_ops import _object_fcurves
                if not _object_fcurves(context):
                    return "Select an object with editable Action curves"
            if not operator.poll():
                return command_metadata(action)[1]
    except (RuntimeError, ReferenceError, StopIteration) as exc:
        _log.debug("Timeline prerequisite unavailable: %s", exc)
        return "Open an editable Timeline and select the required animation"
    return ""


def _arguments(context, action):
    arguments = dict(_ACTIONS[action][1])
    settings = context.scene.anim_assist
    if action == "BOOKMARK_RECALL":
        arguments["index"] = settings.active_bookmark_index
    elif action == "BOOKMARK_ADD":
        arguments["name"] = f"Reference {settings.reference_frame}"
    elif action == "MIRROR_RANGE":
        scene = context.scene
        arguments.update(start_frame=scene.frame_preview_start if scene.use_preview_range else scene.frame_start,
                         end_frame=scene.frame_preview_end if scene.use_preview_range else scene.frame_end)
    elif action == "PASTE_KEYS":
        from ..prefs import get_prefs
        prefs = get_prefs(context)
        arguments["frame_offset"] = prefs.timeline_paste_offset if prefs else 0.0
    elif action in {"SWITCH_ENUM", "SWITCH_INFLUENCE"}:
        from ..core.p8_properties import get_p8
        value = get_p8(context).switch_new_value
        arguments["value" if action == "SWITCH_ENUM" else "influence"] = int(value) if action == "SWITCH_ENUM" else value
    return arguments


class ANIMASSIST_OT_timeline_tool(bpy.types.Operator):
    """Use an Anim Assist action in this Timeline"""
    bl_idname = "animassist.timeline_tool"
    bl_label = "Timeline Tool"
    bl_options = {"INTERNAL"}
    action: StringProperty(options={"HIDDEN", "SKIP_SAVE"})

    @classmethod
    def poll(cls, context):
        if not is_timeline(context.area):
            cls.poll_message_set("Use this tool from a Timeline")
            return False
        return True

    @classmethod
    def description(cls, context, properties):
        action = properties.action
        if action not in _ACTIONS:
            return cls.__doc__
        operator = _operator(action)
        description = command_description(action, operator.get_rna_type().description if operator else "Tool module unavailable")
        reason = _unavailable(context, _target(context), action)
        if action in {"OFFSET", "OFFSET_MASK", "OFFSET_SCENE_RANGE"}:
            from ..operators.anim_offset_ops import offset_session_status
            status = offset_session_status(context.scene)
            if status:
                description += f" Active session: {status}."
        return description + (f" Unavailable: {reason}." if reason else "")

    def invoke(self, context, _event):
        return self.execute(context)

    def execute(self, context):
        target = _target(context)
        if target is None or self.action not in _ACTIONS:
            self.report({"WARNING"}, "Choose a known Timeline tool")
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
                # The existing target owns undo and modal lifetime. This wrapper
                # does not add an undo step or create a second modal handler.
                mode = "EXEC_DEFAULT" if self.action in EXECUTE_ACTIONS else "INVOKE_DEFAULT"
                result = operator(mode, True, **_arguments(context, self.action))
            return {"CANCELLED"} if "CANCELLED" in result else {"FINISHED"}
        except (RuntimeError, ReferenceError, AttributeError) as exc:
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
        for action in actions:
            if action is None:
                self.layout.separator()
            else:
                _button(self.layout, context, _target(context), action, _ACTIONS[action][2])
        self.layout.separator()
        self.layout.operator("animassist.open_home", text="Open Anim Assist Panel", icon="PROPERTIES")
    name = _menu_id(key)
    return type(name, (bpy.types.Menu,), {"bl_idname": name, "bl_label": label, "draw": draw})


_menus = [_build_menu(*group) for group in GROUPS]


class ANIMASSIST_MT_timeline_tools(bpy.types.Menu):
    bl_label = "Anim Assist Tools"
    bl_description = "All seven animation families in their permanent order"

    def draw(self, context):
        for key, label, _actions in GROUPS:
            self.layout.menu(_menu_id(key), text=label)


class ANIMASSIST_MT_timeline_more(bpy.types.Menu):
    bl_label = "More Anim Assist Shortcuts"
    bl_description = "Original quick commands and all animation families"

    def draw(self, context):
        for _key, label, actions in QUICK_GROUPS:
            self.layout.separator()
            self.layout.label(text=label)
            for action in actions:
                active = action == "OFFSET" and context.scene.anim_assist.anim_offset_active
                _button(self.layout, context, _target(context), action, _ACTIONS[action][2],
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


class ANIMASSIST_OT_timeline_pin(bpy.types.Operator):
    bl_idname = "animassist.timeline_pin"
    bl_label = "Toggle Quick Button"
    bl_description = "Add or remove this tool's one-click button beside its family"
    bl_options = {"INTERNAL"}
    action: StringProperty(options={"HIDDEN", "SKIP_SAVE"})

    def execute(self, context):
        from ..prefs import get_prefs
        prefs = get_prefs(context)
        if prefs is None or self.action not in _ACTIONS:
            self.report({"WARNING"}, "Enable Anim Assist and choose a known tool")
            return {"CANCELLED"}
        name = quick_property_name(self.action)
        setattr(prefs, name, not getattr(prefs, name))
        return {"FINISHED"}


class ANIMASSIST_OT_timeline_search(bpy.types.Operator):
    bl_idname = "animassist.timeline_search"
    bl_label = "Search Animation Tools"
    bl_description = "Find a Timeline tool by name; run it or pin its one-click button"
    bl_options = {"INTERNAL"}
    query: StringProperty(name="Search", description="Find tools by name, family or animation concept",
                          options={"TEXTEDIT_UPDATE", "SKIP_SAVE"})

    @classmethod
    def poll(cls, context):
        if not is_timeline(context.area):
            cls.poll_message_set("Search these tools from a Timeline")
            return False
        return True

    def invoke(self, context, _event):
        return context.window_manager.invoke_popup(self, width=620)

    def draw(self, context):
        from ..prefs import get_prefs
        self.layout.prop(self, "query", text="", icon="VIEWZOOM")
        prefs = get_prefs(context)
        selected = selected_quick_actions(prefs)
        matches = search_actions(self.query)
        if not self.query.strip():
            matches = tuple(action for action in _ACTIONS if action in selected) or DEFAULT_QUICK_ACTIONS
            self.layout.label(text="Quick tools shown. Type to search the full catalogue.")
        if not matches:
            self.layout.label(text="No matching animation tools", icon="INFO")
        for action in matches[:16]:
            row = self.layout.row(align=True)
            _button(row, context, _target(context), action, _ACTIONS[action][2])
            pin = row.row(align=True)
            pin.enabled = prefs is not None
            op = pin.operator("animassist.timeline_pin", text="",
                              icon="PINNED" if action in selected else "UNPINNED",
                              depress=action in selected)
            op.action = action
        if len(matches) > 16:
            self.layout.label(text=f"{len(matches)} matches; refine the search to see more")

    def execute(self, context):
        return {"FINISHED"}


class ANIMASSIST_PT_timeline_quick_settings(bpy.types.Panel):
    bl_label = "Timeline Quick Tools"
    bl_space_type = "DOPESHEET_EDITOR"
    bl_region_type = "HEADER"
    bl_ui_units_x = 22

    def draw(self, context):
        from ..prefs import get_prefs, draw_timeline_quick_settings
        prefs = get_prefs(context)
        if prefs is None:
            self.layout.label(text="Enable Anim Assist in add-on preferences", icon="INFO")
        else:
            draw_timeline_quick_settings(self.layout, context, prefs)


# These secondary controls edit existing settings; the primary action remains
# immediate and each target's native Adjust Last Operation stays available.
_OPTION_FIELDS = {
    "tween": (("anim_assist_p3", ("mode", "mask_location", "mask_rotation", "mask_scale", "mask_custom", "inbetween_count")),),
    "curves": (("anim_assist", ("reference_frame",)),),
    "timing": (("anim_assist_p6", ("anchor_mode", "pivot_frame", "range_mode", "range_start", "range_end", "offset_frames", "ripple_delta", "insert_frames", "modal_snap", "modal_show_header")),),
    "keys": (),
    "pose": (("anim_assist_p9", ("mirror_axis", "mirror_space", "mirror_location", "mirror_rotation", "mirror_scale", "respect_locks", "respect_drivers", "auto_key_mirror")),
             ("anim_assist_p8", ("match_channels", "match_axis", "maintain_offset", "respect_locks", "respect_drivers", "auto_key_switch", "switch_bone_name", "switch_prop_path", "switch_new_value", "comp_range", "comp_range_start", "comp_range_end"))),
    "bake": (("anim_assist_p7", ("bake_range_mode", "bake_range_start", "bake_range_end", "bake_step", "bake_channels", "smart_bake_tolerance")),),
    "motion": (("anim_assist_p5", ("scope_mode", "custom_start", "custom_end", "sample_step", "space_mode")),),
}


def _build_options(key, label, _actions):
    def draw(self, context):
        layout = self.layout
        layout.label(text=f"{label} options")
        for attribute, names in _OPTION_FIELDS[key]:
            settings = getattr(context.scene, attribute, None)
            if settings is None:
                layout.label(text="Enable this tool module to edit its settings", icon="INFO")
                continue
            for name in names:
                layout.prop(settings, name)
            layout.separator()
        if key == "curves":
            settings = context.scene.anim_assist
            layout.template_list("UI_UL_list", "reference_bookmarks", settings, "bookmarks",
                                 settings, "active_bookmark_index", rows=3)
            index = settings.active_bookmark_index
            if 0 <= index < len(settings.bookmarks):
                layout.prop(settings.bookmarks[index], "name")
                layout.prop(settings.bookmarks[index], "frame")
            for action in ("BOOKMARK_ADD", "BOOKMARK_RECALL", "BOOKMARK_REMOVE"):
                _button(layout, context, _target(context), action, _ACTIONS[action][2])
            layout.label(text="Recall changes the reference; the playhead stays put.")
        elif key == "keys":
            from ..prefs import get_prefs
            prefs = get_prefs(context)
            if prefs:
                layout.prop(prefs, "timeline_paste_offset")
            layout.label(text="Paste matches Action names and curve paths.")
            layout.label(text="Paste uses copied times plus offset, not the playhead.")
        elif key == "pose":
            layout.label(text="Mirror Range uses the preview/playback range.")
        elif key == "motion":
            mask = context.scene.anim_assist.mask
            for name in ("enabled", "start_frame", "end_frame", "blend_left", "blend_right"):
                layout.prop(mask, name)
        layout.separator()
        layout.label(text="Drag feedback appears in the header or status bar.")
        layout.label(text="Use Adjust Last Operation for completed tool options.")
    name = f"ANIMASSIST_PT_timeline_options_{key}"
    return type(name, (bpy.types.Panel,), {"bl_label": f"{label} Options",
                "bl_space_type": "DOPESHEET_EDITOR", "bl_region_type": "HEADER",
                "bl_ui_units_x": 24, "draw": draw})


_settings_classes = [ANIMASSIST_OT_reset_timeline_quick_defaults, ANIMASSIST_OT_timeline_pin,
                     ANIMASSIST_OT_timeline_search, ANIMASSIST_PT_timeline_quick_settings]
_settings_classes.extend(_build_options(*group) for group in GROUPS)


def _draw_toolbar(self, context):
    layout = self.layout
    target = _target(context)
    if target is None:
        return
    from ..prefs import get_prefs
    layout.operator("animassist.timeline_search", text="Search", icon="VIEWZOOM")
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
        row.popover(panel=f"ANIMASSIST_PT_timeline_options_{key}", text="", icon="TRIA_DOWN")


class ANIMASSIST_HT_timeline_tools(bpy.types.Header):
    bl_label = "Anim Assist Timeline Toolbar"
    bl_space_type = "DOPESHEET_EDITOR"
    bl_region_type = "TOOL_HEADER"

    @classmethod
    def poll(cls, context):
        return is_timeline(context.area) and _enabled()

    def draw(self, context):
        if self.poll(context):
            _draw_toolbar(self, context)


def _legacy_target(screen, strip):
    scale = max(0.5, bpy.context.preferences.system.ui_scale)
    edge, border = ceil(2 * scale), ceil(4 * scale)
    return next((area for area in screen.areas if is_timeline(area)
                 and abs(area.x - strip.x) <= edge
                 and abs(area.width - strip.width) <= edge
                 and (abs(area.y + area.height - strip.y) <= border
                      or abs(strip.y + strip.height - area.y) <= border)), None)


def _capture_legacy_candidates():
    """Only editors present on enable/load are eligible for migration."""
    screens = getattr(bpy.data, "screens", None)
    if screens is None:
        return False  # addon_utils.enable supplies _RestrictData during register.
    _legacy_candidates.clear()
    _migration_attempted.clear()
    _legacy_candidates.update(area.as_pointer() for screen in screens
                              for area in screen.areas if is_strip(area))
    return True


def _migrate_legacy(window, screen):
    for strip in list(screen.areas):
        if not is_strip(strip):
            continue
        pointer = strip.as_pointer()
        if pointer not in _legacy_candidates or pointer in _migration_attempted:
            continue
        if strip.width == 0 or strip.height == 0 or any(
                is_timeline(area) and (area.width == 0 or area.height == 0)
                for area in screen.areas):
            continue  # Initial layout has not supplied trustworthy geometry yet.
        # Freeze the first valid assessment, including the decision to leave an
        # unpaired strip alone. Moving it later must never trigger a timer join.
        _migration_attempted.add(pointer)
        target = _legacy_target(screen, strip)
        if target is None:
            # A moved legacy editor is not ours to repurpose or join.
            continue
        try:
            with bpy.context.temp_override(window=window, screen=screen, area=target):
                result = bpy.ops.screen.area_join(
                    source_xy=(target.x + target.width // 2, target.y + target.height // 2),
                    target_xy=(strip.x + strip.width // 2, strip.y + strip.height // 2))
            if "FINISHED" in result:
                _seen.discard(target.spaces.active.as_pointer())
                return True
        except (RuntimeError, ReferenceError) as exc:
            _log.warning("Legacy Timeline toolbar migration could not complete: %s", exc)
    return False


def _apply_inactive_timeline_choice(screens):
    """An explicit global choice includes cached Timeline spaces in other editors."""
    if not native_available():
        return
    for screen in screens:
        for area in screen.areas:
            active = area.spaces.active
            for space in area.spaces:
                if (space == active or space.type != "DOPESHEET_EDITOR"
                        or space.mode != "TIMELINE"):
                    continue
                try:
                    # The host RNA setter finds this space's own region list.
                    # This is an explicit user choice, so marking/clearing the
                    # native user-hide flag is intended. No active area changes.
                    space.show_region_tool_header = _enabled()
                except (RuntimeError, ReferenceError, TypeError) as exc:
                    _log.warning("Cached Timeline toolbar choice could not be applied: %s", exc)


def reconcile_preferences():
    """Explicit preference changes may show/hide; ordinary resizing never does."""
    global _force_reconcile
    _force_reconcile = True
    screens = getattr(bpy.data, "screens", None)
    if screens is None:
        return  # The first unrestricted lifecycle callback queues the choice.
    _apply_inactive_timeline_choice(screens)
    # Inactive workspace Timelines receive this explicit choice when opened,
    # while ordinary workspace switching still respects their native hide flag.
    _pending_user_action.update(area.spaces.active.as_pointer()
        for screen in screens for area in screen.areas if is_timeline(area))


@persistent
def _load_post(_unused):
    global _force_reconcile, _capture_pending
    _seen.clear()
    _owned.clear()
    _capture_pending = True
    _pending_user_action.clear()
    # Saved explicit native hiding is honored. Only an actual preference change
    # is an instruction to reveal an already hidden row.
    _force_reconcile = False


def _sync():
    """Observe lifecycle only. Never enforce geometry or reverse a manual hide."""
    global _force_reconcile, _capture_pending
    if not _registered:
        return None
    screens = getattr(bpy.data, "screens", None)
    if screens is None:
        return 1.0
    if _capture_pending:
        if not _capture_legacy_candidates():
            return 1.0
        _capture_pending = False
    force = _force_reconcile
    _force_reconcile = False
    try:
        live = {area.spaces.active.as_pointer() for screen in screens
                for area in screen.areas if is_timeline(area)}
        if force:
            # A preference callback may have run under _RestrictData. Reconcile
            # cached spaces here too, without treating load/disable as user intent.
            _apply_inactive_timeline_choice(screens)
            _pending_user_action.update(live)
        _seen.intersection_update(live)
        _owned.intersection_update(live)
        _pending_user_action.intersection_update(live)
        for window in bpy.context.window_manager.windows:
            screen = window.screen
            if (not screen.is_temporary and not screen.show_fullscreen
                    and _migrate_legacy(window, screen)):
                _force_reconcile = force
                return 0.25
            for area in screen.areas:
                if not is_timeline(area):
                    continue
                if area.width == 0 or area.height == 0:
                    continue  # Wait for initial native geometry, not a resize repair.
                pointer = area.spaces.active.as_pointer()
                user_action = force or pointer in _pending_user_action
                if pointer in _seen and not user_action:
                    continue
                _seen.add(pointer)
                _pending_user_action.discard(pointer)
                if not native_available():
                    area.tag_redraw()
                    continue
                _owned.add(pointer)
                if area.spaces.active.timeline_toolbar_hidden_by_user and not user_action:
                    continue
                try:
                    with bpy.context.temp_override(window=window, screen=screen, area=area,
                                                   region=_window_region(area)):
                        result = bpy.ops.screen.timeline_toolbar_set(
                            enabled=_enabled(), user_action=user_action)
                    if "FINISHED" not in result:
                        _log.warning("Native Timeline toolbar could not change visibility")
                except (RuntimeError, ReferenceError, StopIteration) as exc:
                    _log.warning("Native Timeline toolbar unavailable in this screen: %s", exc)
    except (RuntimeError, ReferenceError, AttributeError) as exc:
        _log.warning("Timeline lifecycle update deferred: %s", exc)
    return 1.0


def register():
    global _registered, _capture_pending
    bpy.utils.register_class(ANIMASSIST_OT_timeline_tool)
    for cls in _settings_classes + _menus:
        bpy.utils.register_class(cls)
    if native_available():
        bpy.utils.register_class(ANIMASSIST_HT_timeline_tools)
    # Registration runs under restricted data/context. Capture legacy editors
    # only in the first unrestricted callback after enable/load.
    _capture_pending = True
    _registered = True
    if _load_post not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(_load_post)
    if not bpy.app.background and not bpy.app.timers.is_registered(_sync):
        bpy.app.timers.register(_sync, first_interval=0.1, persistent=True)


def _hide_native_rows():
    manager = getattr(bpy.context, "window_manager", None)
    windows = list(getattr(manager, "windows", ()))
    screens = getattr(bpy.data, "screens", None)
    if not windows or screens is None:
        return
    ordinary = next((window for window in windows
                     if not window.screen.is_temporary and not window.screen.show_fullscreen), None)
    for screen in screens:
        owner = next((window for window in windows if window.screen == screen), None)
        # Active windows use their own implicit screen, including maximized
        # editors. Only ordinary inactive workspaces receive a screen override.
        if owner is None and (ordinary is None or screen.is_temporary or screen.show_fullscreen):
            continue
        for area in screen.areas:
            if not (is_timeline(area) and (area.spaces.active.as_pointer() in _owned
                    or area.spaces.active.show_region_tool_header)):
                continue
            try:
                override = {"window": owner or ordinary, "area": area,
                            "region": _window_region(area)}
                if owner is None:
                    override["screen"] = screen
                with bpy.context.temp_override(**override):
                    bpy.ops.screen.timeline_toolbar_set(enabled=False, user_action=False)
                area.tag_redraw()
            except (RuntimeError, ReferenceError, StopIteration, TypeError) as exc:
                _log.warning("Native Timeline toolbar could not be hidden: %s", exc)


def unregister():
    global _registered, _force_reconcile, _capture_pending
    _registered = False
    try:
        if bpy.app.timers.is_registered(_sync):
            bpy.app.timers.unregister(_sync)
        if _load_post in bpy.app.handlers.load_post:
            bpy.app.handlers.load_post.remove(_load_post)
        if native_available():
            _hide_native_rows()
    except (RuntimeError, ReferenceError, AttributeError, TypeError) as exc:
        _log.warning("Native Timeline toolbar cleanup context unavailable: %s", exc)
    finally:
        # A rejected window/screen override must never leave operators, menus,
        # panels or the Header registered and break the next enable operation.
        _seen.clear()
        _owned.clear()
        _migration_attempted.clear()
        _legacy_candidates.clear()
        _pending_user_action.clear()
        _force_reconcile = False
        _capture_pending = False
        classes = [ANIMASSIST_HT_timeline_tools, *reversed(_settings_classes + _menus),
                   ANIMASSIST_OT_timeline_tool]
        for cls in classes:
            if getattr(cls, "is_registered", False):
                try:
                    bpy.utils.unregister_class(cls)
                except (RuntimeError, ReferenceError, TypeError) as exc:
                    _log.warning("Could not unregister Timeline toolbar class %s: %s", cls.__name__, exc)
