"""
ui_panel.py — Ghost Tool UI: viewport header menu, separate window, floating
toolbar, and the Timeline header strip.

Ghost Tool adds no tab to the 3D Viewport sidebar. Its home is the viewport
header: an on/off ghost toggle and a "Ghost Tool" dropdown next to the Pose
menu. The same grouped layout (show ghosts, onion skin, edit motion, compare,
physics, look, settings) also fills the floating toolbar and "Open in
Separate Window", a second viewport whose sidebar shows only Ghost Tool.
"""

from __future__ import annotations

import textwrap

import bpy

from .ghost_data import AnchorState, DiffReference, GhostStore
from .snapshot import SnapshotStore
from .easing_presets import PRESET_ENUM_ITEMS
from .utils import log, warn, debug, report_failure


# ---------------------------------------------------------------------------
# Easing Settings PropertyGroup (needed by panels)
# ---------------------------------------------------------------------------

class GhostToolEasingSettings(bpy.types.PropertyGroup):
    """Scene-level state for the easing preset selector."""

    active_preset: bpy.props.EnumProperty(
        name="Easing Preset",
        description="Select an easing curve feel to apply between keyframes",
        items=PRESET_ENUM_ITEMS,
        default="EASE_IN_OUT",
    )  # type: ignore[assignment]
    custom_left_x: bpy.props.FloatProperty(
        name="Left Handle X",
        description="Horizontal position of the left keyframe's outgoing handle (0 = at keyframe, 1 = at next keyframe)",
        default=0.33, min=0.0, max=1.0,
    )  # type: ignore[assignment]
    custom_left_y: bpy.props.FloatProperty(
        name="Left Handle Y",
        description="Vertical position of the left keyframe's outgoing handle (0 = flat, positive = overshoot)",
        default=0.0, min=-2.0, max=2.0,
    )  # type: ignore[assignment]
    custom_right_x: bpy.props.FloatProperty(
        name="Right Handle X",
        description="Horizontal position of the right keyframe's incoming handle (0 = at keyframe, -1 = at previous keyframe)",
        default=-0.33, min=-1.0, max=0.0,
    )  # type: ignore[assignment]
    custom_right_y: bpy.props.FloatProperty(
        name="Right Handle Y",
        description="Vertical position of the right keyframe's incoming handle (0 = flat, positive = overshoot)",
        default=0.0, min=-2.0, max=2.0,
    )  # type: ignore[assignment]


_HELP_TOPICS = {
    "overview": (
        "Ghost Tool Workflow",
        "Generate markers, drag them with Shift+G, then refine the resulting animation curves.",
        "Enable Ghost Tools, choose the marker range and subdivision level, and generate markers. "
        "Drag a marker to reshape motion, pin important markers, and use snapshots before larger edits.",
    ),
    "onion_skin": (
        "Onion Skin",
        "Show translucent mesh poses before and after the current frame.",
        "Use onion skins to compare silhouette, spacing, and overlap. Reduce the range or opacity "
        "when the viewport becomes crowded.",
    ),
    "motion_trails": (
        "Motion Trails",
        "Draw the path and timing spacing of animated motion through the viewport.",
        "Arc lines reveal trajectory shape. Spacing ticks reveal acceleration: dense marks indicate "
        "slower movement and wider gaps indicate faster movement.",
    ),
    "marker_placement": (
        "Marker Placement",
        "Choose which frames become editable ghost markers.",
        "Set the frame range and subdivision level before generating. Higher subdivision produces "
        "more editable inbetweens but also creates a denser viewport.",
    ),
    "marker_display": (
        "Marker Display",
        "Control marker colors, size, labels, arcs, and mesh visualization.",
        "Display settings change only viewport presentation; they do not alter animation data. "
        "Use simpler display modes when working with dense shots.",
    ),
    "marker_tools": (
        "Marker Tools",
        "Edit, select, pin, snapshot, ease, and apply physics-shaped motion.",
        "Drag Marker is the main editing action. Choose what happens on confirmation, use falloff "
        "to affect neighbors, and take a snapshot before stamping Physics Feel keys.",
    ),
    "export_import": (
        "Export and Import",
        "Save Ghost Tool marker and snapshot data or restore it later.",
        "Export before transferring a setup or making destructive changes. Import replaces or "
        "reconstructs tool state but does not replace a normal .blend backup.",
    ),
    "settings": (
        "Ghost Tool Settings",
        "Adjust interaction, performance, and viewport behavior for the current scene.",
        "Keep marker counts and display complexity modest for heavy rigs. Add-on-wide visual "
        "defaults and the extended-help switch live in the installed add-on preferences.",
    ),
    "snapshots": (
        "Saved Snapshots",
        "Capture restorable Ghost Tool states before experimenting.",
        "Restore a snapshot to return to its captured curve state, toggle its overlay for comparison, "
        "or delete snapshots that are no longer useful.",
    ),
    "motion_paths": (
        "Motion Paths",
        "Pin a path to any bone or object and watch it follow the playhead.",
        "Add pins the selected bones (Pose mode) or objects. Follow adds a grey path for "
        "whatever is selected. Paths sample the bone itself, so they work with markers off; "
        "turn Markers on to drag keys along a path. A bone path traces its head or its tail: "
        "click H/T in the list to switch. The cube button hides a path behind geometry. "
        "Split colours a path differently before the playhead; Glow marks the path selected "
        "in the list. Range and style apply to all paths; a path can take its own range "
        "in its settings (the colour swatch).",
    ),
}


def _extended_help_enabled(context: bpy.types.Context) -> bool:
    addons = getattr(getattr(context, "preferences", None), "addons", None)
    addon = addons.get("ghost_tool") if addons is not None else None
    prefs = getattr(addon, "preferences", None)
    return bool(getattr(prefs, "show_extended_help", True))


def _draw_help_icon(layout, context: bpy.types.Context, topic: str) -> None:
    if not _extended_help_enabled(context):
        return
    operator = layout.operator(
        "ghost_tool.show_help_popup",
        text="",
        icon='QUESTION',
        emboss=False,
    )
    operator.topic = topic


class GHOST_OT_show_help_popup(bpy.types.Operator):
    """Display extended help for a Ghost Tool panel."""

    bl_idname = "ghost_tool.show_help_popup"
    bl_label = "Ghost Tool Help"
    bl_description = "Show detailed help for this Ghost Tool section"
    bl_options = {'REGISTER', 'INTERNAL'}

    topic: bpy.props.StringProperty(
        name="Help Topic",
        description="Internal identifier of the Ghost Tool help topic to display",
        default="overview",
    )  # type: ignore[assignment]

    def invoke(self, context, event):
        if self.topic not in _HELP_TOPICS:
            self.report({'WARNING'}, "Help topic not found")
            return {'CANCELLED'}
        return context.window_manager.invoke_props_dialog(self, width=460)

    def draw(self, context):
        title, summary, details = _HELP_TOPICS[self.topic]
        layout = self.layout
        header = layout.box()
        header.label(text=title, icon='QUESTION')
        for line in textwrap.wrap(summary, width=62):
            header.label(text=line)
        body = layout.box()
        body.label(text="Details", icon='INFO')
        for line in textwrap.wrap(details, width=62):
            body.label(text=line)

    def execute(self, context):
        return {'FINISHED'}


class _GhostHelpPanelMixin:
    help_topic = "overview"

    def draw_header(self, context):
        _draw_help_icon(self.layout, context, self.help_topic)


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  SECTION 1 — THE GHOST TOOL LAYOUT  (one layout, three hosts)          ║
# ╚══════════════════════════════════════════════════════════════════════════╝
#
# Ghost Tool has no 3D Viewport sidebar tab. It lives in the viewport header:
# an on/off ghost toggle and a "Ghost Tool" dropdown next to the Pose menu.
# The same layout also fills the floating toolbar and a separate window (a
# second viewport whose sidebar shows only Ghost Tool), for when a dropdown
# that closes on click-away is not enough.
#
# Groups follow the order you work in: show ghosts, onion skin, edit motion,
# compare, physics, look, settings.


def _row_label(layout, text: str, icon: str = 'NONE') -> None:
    row = layout.row()
    row.enabled = False
    row.label(text=text, icon=icon)


def _draw_show_ghosts(layout, context) -> None:
    settings = context.scene.ghost_tool
    row = layout.row(align=True)
    row.scale_y = 1.3
    row.operator("ghost_tool.generate_ghosts", text="Show Markers", icon='GHOST_ENABLED')
    row.operator("ghost_tool.clear_ghosts", text="", icon='TRASH')
    _row_label(layout, "Location + rotation keys")

    col = layout.column(align=True)
    col.label(text="Frames")
    col.prop(settings, "ghost_range_mode", text="")
    if settings.ghost_range_mode == "AROUND_CURSOR":
        row = col.row(align=True)
        row.prop(settings, "ghosts_before", text="Before")
        row.prop(settings, "ghosts_after", text="After")
    elif settings.ghost_range_mode == "CUSTOM":
        row = col.row(align=True)
        row.prop(settings, "custom_range_start", text="Start")
        row.prop(settings, "custom_range_end", text="End")

    col = layout.column(align=True)
    col.label(text="Marker every")
    col.prop(settings, "ghost_mode", text="")
    if settings.ghost_mode == "FRAME_STEP":
        col.prop(settings, "frame_step", text="Frames")
    elif settings.ghost_mode == "SUBDIVISION":
        col.prop(settings, "subdivision_level", text="Detail", slider=True)

    col = layout.column(align=True)
    col.prop(settings, "live_point_ghosts", text="Update While Scrubbing", toggle=True,
             icon='PLAY' if settings.live_point_ghosts else 'PAUSE')
    if settings.live_point_ghosts or settings.live_mesh_ghosts:
        row = col.row(align=True)
        row.prop(settings, "live_freeze", text="Freeze", toggle=True,
                 icon='SNAP_ON' if settings.live_freeze else 'SNAP_OFF')
        row.prop(settings, "live_throttle_ms", text="Delay")


def _draw_onion_skin(layout, context) -> None:
    settings = context.scene.ghost_tool
    row = layout.row(align=True)
    row.scale_y = 1.3
    row.operator("ghost_tool.generate_mesh_ghosts", text="Show Onion Skin", icon='MESH_DATA')
    row.operator("ghost_tool.clear_mesh_ghosts", text="", icon='TRASH')
    from .mesh_ghosts import pinned_ghost_sources
    pinned = pinned_ghost_sources(context.scene)
    if pinned:
        names = ", ".join(obj.name for obj in pinned[:3]) + (", ..." if len(pinned) > 3 else "")
        _row_label(layout, f"Following {names}", icon='PINNED')
    else:
        _row_label(layout, "Every mesh or curve of each selected character")

    row = layout.row(align=True)
    row.prop(settings, "mesh_ghost_mode", expand=True)
    row.prop(settings, "mesh_ghost_xray", text="", toggle=True, icon='XRAY')

    col = layout.column(align=True)
    col.label(text="Frames")
    col.prop(settings, "mesh_ghost_frame_mode", text="")
    if settings.mesh_ghost_frame_mode == 'KEYFRAMES':
        col.prop(settings, "mesh_ghost_keyframe_skip", text="Every")
        if settings.mesh_ghost_keyframe_skip == 'CUSTOM':
            col.prop(settings, "mesh_ghost_keyframe_skip_custom", text="Every Nth")
    else:
        col.prop(settings, "mesh_ghost_step", text="Step")
    row = col.row(align=True)
    row.prop(settings, "mesh_ghost_past_count", text="Before")
    row.prop(settings, "mesh_ghost_future_count", text="After")

    col = layout.column(align=True)
    col.label(text="Fade")
    col.prop(settings, "mesh_ghost_opacity", text="Opacity", slider=True)
    col.prop(settings, "mesh_ghost_falloff", text="")

    col = layout.column(align=True)
    row = col.row(align=True)
    row.prop(settings, "show_mesh_past", text="Before", toggle=True,
             icon='REW' if settings.show_mesh_past else 'BLANK1')
    row.prop(settings, "show_mesh_future", text="After", toggle=True,
             icon='FF' if settings.show_mesh_future else 'BLANK1')
    col.prop(settings, "mesh_ghost_past_color", text="Before")
    col.prop(settings, "mesh_ghost_future_color", text="After")

    col = layout.column(align=True)
    col.prop(settings, "ghost_outline_enabled", text="Outline", toggle=True, icon='MOD_SOLIDIFY')
    if settings.ghost_outline_enabled:
        col.prop(settings, "ghost_outline_width", text="Width")
        col.prop(settings, "ghost_outline_color", text="")
    layout.prop(settings, "live_mesh_ghosts", text="Update While Scrubbing", toggle=True,
                icon='PLAY' if settings.live_mesh_ghosts else 'PAUSE')


def _draw_edit_motion(layout, context) -> None:
    scene = context.scene
    settings = scene.ghost_tool
    store = GhostStore.get(scene)

    row = layout.row()
    row.scale_y = 1.4
    row.operator("ghost_tool.drag_ghost", text="Drag Marker  (Shift G)", icon='ORIENTATION_CURSOR')
    row = layout.row(align=True)
    row.operator("ghost_tool.select_ghost", text="Select", icon='RESTRICT_SELECT_OFF')
    row.operator("ghost_tool.box_select", text="Box Select", icon='SELECT_SET')

    col = layout.column(align=True)
    col.label(text="When you let go")
    col.prop(settings, "editing_mode", text="")
    if settings.editing_mode == 'RESHAPE':
        col.prop(settings, "curve_mode", text="")
    else:
        col.prop(settings, "smooth_neighbors_on_commit", text="Smooth Neighbours",
                 toggle=True, icon='MOD_SMOOTH')

    col = layout.column(align=True)
    col.label(text="Also move nearby frames")
    row = col.row(align=True)
    row.prop(settings, "sculpt_falloff_radius", text="Reach")
    sub = row.row(align=True)
    sub.enabled = settings.sculpt_falloff_radius > 0
    sub.prop(settings, "sculpt_falloff_curve", text="")

    if hasattr(scene, 'ghost_tool_easing'):
        easing = scene.ghost_tool_easing
        col = layout.column(align=True)
        col.label(text="Easing")
        col.prop(easing, "active_preset", text="")
        op = col.operator("ghost_tool.apply_easing", text="Apply Easing", icon='IPO_EASE_IN_OUT')
        op.preset = easing.active_preset
        if easing.active_preset == "CUSTOM":
            row = col.row(align=True)
            row.prop(easing, "custom_left_x", text="L.X")
            row.prop(easing, "custom_left_y", text="L.Y")
            row = col.row(align=True)
            row.prop(easing, "custom_right_x", text="R.X")
            row.prop(easing, "custom_right_y", text="R.Y")

    col = layout.column(align=True)
    col.label(text=f"Pinned markers: {len(store.get_pinned())}")
    row = col.row(align=True)
    row.operator("ghost_tool.pin_ghost", text="Pin", icon='PINNED')
    row.operator("ghost_tool.unpin_all", text="Unpin All", icon='UNPINNED')


def _draw_compare(layout, context) -> None:
    scene = context.scene
    settings = scene.ghost_tool
    snapshots = SnapshotStore.get(scene).get_all()

    col = layout.column(align=True)
    col.label(text=f"Snapshots ({len(snapshots)})")
    col.operator("ghost_tool.take_snapshot", text="Take Snapshot", icon='CAMERA_DATA')
    if not snapshots:
        _row_label(col, "Save a state before big edits")
    for snap in snapshots:
        row = col.row(align=True)
        op = row.operator("ghost_tool.toggle_snapshot", text="",
                          icon='HIDE_OFF' if snap.is_visible else 'HIDE_ON')
        op.snapshot_uid = snap.uid
        row.label(text=f"{snap.name}  ({len(snap.ghost_data)})")
        op = row.operator("ghost_tool.restore_snapshot", text="", icon='LOOP_BACK')
        op.snapshot_uid = snap.uid
        op = row.operator("ghost_tool.delete_snapshot", text="", icon='X')
        op.snapshot_uid = snap.uid

    col = layout.column(align=True)
    col.label(text="Compare to a pose")
    col.prop(settings, "show_diff_overlay", text="Colour Bones by Change", toggle=True,
             icon='HIDE_OFF' if settings.show_diff_overlay else 'HIDE_ON')
    row = col.row(align=True)
    row.operator("ghost_tool.pin_diff_reference", text="Set Reference", icon='PINNED')
    row.operator("ghost_tool.unpin_diff_reference", text="", icon='X')
    if settings.show_diff_overlay:
        diff_ref = DiffReference.get(scene)
        if diff_ref is None:
            _row_label(col, "No reference set", icon='INFO')
        else:
            is_stale = diff_ref.state == AnchorState.STALE
            col.label(text=f"Frame {diff_ref.anchor_frame}: {'stale' if is_stale else 'live'}",
                      icon='ERROR' if is_stale else 'CHECKMARK')
        col.prop(settings, "diff_max_distance", text="Max Distance")
        row = col.row(align=True)
        row.prop(settings, "diff_cool_color", text="")
        row.prop(settings, "diff_warm_color", text="")


def _draw_physics(layout, context) -> None:
    settings = context.scene.ghost_tool
    layout.operator("ghost_tool.physics_suggest", text="Suggest Physics Arc", icon='FORCE_FORCE')

    col = layout.column(align=True)
    col.prop(settings, "show_ballistic_preview", text="Show Throw Path", toggle=True, icon='FORCE_HARMONIC')
    if settings.show_ballistic_preview:
        row = col.row(align=True)
        row.prop(settings, "ballistic_gravity", text="Gravity")
        row.prop(settings, "ballistic_gravity_axis", text="")
        col.prop(settings, "ballistic_offset", text="Offset")

    col = layout.column(align=True)
    col.label(text="Physics feel")
    row = col.row(align=True)
    row.prop(settings, "archetype_active", text="")
    row.prop(settings, "show_archetype_preview", text="", toggle=True,
             icon='HIDE_OFF' if settings.show_archetype_preview else 'HIDE_ON')
    if settings.show_archetype_preview:
        row = col.row(align=True)
        row.prop(settings, "archetype_amplitude", text="Amplitude")
        row.prop(settings, "archetype_axis", text="")
        row = col.row(align=True)
        row.prop(settings, "archetype_start_frame", text="Start")
        row.prop(settings, "archetype_end_frame", text="End")
        col.operator("ghost_tool.archetype_bake", text="Stamp to Keys", icon='KEYFRAME_HLT')


def _draw_look(layout, context) -> None:
    scene = context.scene
    settings = scene.ghost_tool
    store = GhostStore.get(scene)

    col = layout.column(align=True)
    col.label(text="Colour markers by")
    col.prop(settings, "ghost_color_mode", text="")
    if settings.ghost_color_mode == "TIME":
        col.prop(settings, "ghost_past_color", text="Before")
        col.prop(settings, "ghost_future_color", text="After")
    elif settings.ghost_color_mode == "KEY_INBETWEEN":
        col.prop(settings, "ghost_key_color", text="Key")
        col.prop(settings, "ghost_inbetween_color", text="Inbetween")
    if settings.ghost_color_mode != "LEVEL":
        col.prop(settings, "ghost_fade_factor", text="Fade Distance", slider=True)
        col.prop(settings, "ghost_falloff_curve", text="")
        col.prop(settings, "ghost_min_alpha", text="Min Opacity", slider=True)

    col = layout.column(align=True)
    col.label(text="Show on the path")
    row = col.row(align=True)
    row.prop(settings, "show_arc_lines", text="Arc Lines", toggle=True, icon='CURVE_PATH')
    if settings.show_arc_lines:
        row.prop(settings, "arc_line_style", text="")
    col.prop(settings, "show_spacing_ticks", text="Spacing Ticks", toggle=True, icon='TIME')
    col.prop(settings, "show_acceleration_markers", text="Speed-up / Slow-down", toggle=True,
             icon='FORCE_TURBULENCE')
    col.prop(settings, "show_keyframe_markers", text="Keyframe Diamonds", toggle=True, icon='KEYFRAME_HLT')
    if settings.show_keyframe_markers:
        col.prop(settings, "keyframe_marker_color", text="")
    col.prop(settings, "show_key_bookends", text="Key Bookends", toggle=True, icon='KEYFRAME')
    if settings.show_key_bookends:
        col.prop(settings, "key_bookend_color", text="")
    col.prop(settings, "show_frame_numbers", text="Frame Numbers", toggle=True, icon='FONT_DATA')
    if settings.show_frame_numbers:
        col.prop(settings, "ghost_label_color", text="")
    col.prop(settings, "show_hover_frame_label", text="Frame Under Mouse", toggle=True, icon='FONT_DATA')
    if settings.show_hover_frame_label:
        col.prop(settings, "hover_highlight_color", text="")

    if settings.ghost_mode == "SUBDIVISION":
        row = layout.row(align=True)
        row.label(text="Levels")
        for level in range(1, 6):
            count = store.count_by_level(level)
            icon_lv = 'LAYER_ACTIVE' if settings.is_level_visible(level) else 'LAYER_USED'
            row.prop(settings, f"show_level_{level}", text=str(level), toggle=True,
                     icon=icon_lv if count > 0 else 'BLANK1')


def _draw_settings(layout, context) -> None:
    settings = context.scene.ghost_tool
    layout.prop(settings, "grab_radius", text="Grab Radius (px)", icon='CURSOR')
    col = layout.column(align=True)
    col.prop(settings, "use_custom_range", text="Limit to a Frame Range")
    if settings.use_custom_range:
        row = col.row(align=True)
        row.prop(settings, "custom_range_start", text="Start")
        row.prop(settings, "custom_range_end", text="End")
    row = layout.row(align=True)
    row.operator("ghost_tool.export_ghosts", text="Export", icon='EXPORT')
    row.operator("ghost_tool.import_ghosts", text="Import", icon='IMPORT')


def _row_icon(entry, is_active: bool) -> str:
    """Kind icon of a path row; the active bone's or object's row gets a dot instead."""
    if is_active:
        return 'RADIOBUT_ON'
    if entry.vertex_index >= 0:
        return 'VERTEXSEL'
    return 'BONE_DATA' if entry.bone_name else 'OBJECT_DATA'


class GHOST_UL_paths(bpy.types.UIList):
    bl_idname = "GHOST_UL_paths"

    def filter_items(self, context, data, propname):
        """List order and visibility come from motion_paths.list_rows: top-level paths, then each
        folder with its paths; a collapsed folder's paths are filtered out."""
        from .motion_paths import list_rows
        count = len(getattr(data, propname))
        flags, order = [0] * count, [0] * count
        for position, (index, shown) in enumerate(list_rows(data)):
            flags[index] = self.bitflag_filter_item if shown else 0
            order[index] = position   # Blender wants each item's new position, indexed by the item
        return flags, order

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        from .motion_paths import active_entry_index, entry_is_missing, folder_rows
        row = layout.row(align=True)
        row.prop(item, "checked", text="")
        if item.is_folder:
            fold = row.operator("ghost_tool.paths_toggle_folder", text="", emboss=False,
                                icon='RIGHTARROW' if item.collapsed else 'DOWNARROW_HLT')
            fold.index = index
            op = row.operator("ghost_tool.paths_toggle_visible", text="", emboss=False,
                              icon='HIDE_OFF' if item.visible else 'HIDE_ON')
            op.action, op.index = 'ONE', index
            row.prop(item, "object_name", text="", emboss=False, icon='FILE_FOLDER')
            rm = row.operator("ghost_tool.paths_remove", text="", icon='X', emboss=False)
            rm.index = index
            return
        if item.folder and item.folder in folder_rows(data):
            row.label(text="", icon='BLANK1')   # indent: this path is in the folder above it
        op = row.operator("ghost_tool.paths_toggle_visible", text="", emboss=False,
                          icon='HIDE_OFF' if item.visible else 'HIDE_ON')
        op.action, op.index = 'ONE', index
        swatch = row.operator("ghost_tool.paths_set_color", text="", icon='COLOR', emboss=False)
        swatch.index = index
        missing = entry_is_missing(item)
        sub = row.row(); sub.enabled = not missing
        sub.label(text=item.label + ("  (missing)" if missing else ""),
                  icon=_row_icon(item, index == active_entry_index(context)))
        if item.bone_name:
            flip = row.row(align=True)
            flip.operator_context = 'EXEC_DEFAULT'   # one click flips; no dialog
            anchor = flip.operator("ghost_tool.paths_set_color", text="T" if item.anchor == 'TAIL' else "H",
                                   emboss=False)
            anchor.index, anchor.anchor = index, 'HEAD' if item.anchor == 'TAIL' else 'TAIL'
        front = row.operator("ghost_tool.paths_toggle_front", text="", emboss=False,
                             icon='XRAY' if item.in_front else 'MESH_CUBE')
        front.action, front.index = 'ONE', index
        rm = row.operator("ghost_tool.paths_remove", text="", icon='X', emboss=False)
        rm.index = index


class GHOST_MT_paths_checked(bpy.types.Menu):
    bl_idname = "GHOST_MT_paths_checked"
    bl_label = "Checked"
    bl_description = "Actions on the checked rows of the motion path list"

    def draw(self, context):
        layout = self.layout
        for action, label, icon in (('SHOW', "Show", 'HIDE_OFF'), ('HIDE', "Hide", 'HIDE_ON'),
                                    ('RESET_RANGE', "Reset Range", 'LOOP_BACK'), ('REMOVE', "Remove", 'X')):
            layout.operator("ghost_tool.paths_checked_action", text=label, icon=icon).action = action
        layout.menu("GHOST_MT_paths_move_to", icon='FILE_FOLDER')
        layout.separator()
        layout.operator("ghost_tool.paths_apply_to_checked", text="Apply to Checked with Range",
                        icon='PASTEDOWN').include_range = True


class GHOST_MT_paths_move_to(bpy.types.Menu):
    bl_idname = "GHOST_MT_paths_move_to"
    bl_label = "Move to Folder"
    bl_description = "Move the checked paths into a folder, or to the top level"

    def draw(self, context):
        layout = self.layout
        op = layout.operator("ghost_tool.paths_checked_action", text="Top Level", icon='TRIA_UP')
        op.action, op.folder = 'MOVE', ""
        for entry in context.scene.ghost_tool.motion_paths:
            if entry.is_folder:
                op = layout.operator("ghost_tool.paths_checked_action", text=entry.object_name, icon='FILE_FOLDER')
                op.action, op.folder = 'MOVE', entry.folder_key


def _range_props(settings) -> tuple[str, ...]:
    """The frame fields the chosen range mode needs."""
    if settings.paths_range_mode == 'AROUND_CURSOR':
        return ("paths_before", "paths_after")
    if settings.paths_range_mode == 'CUSTOM':
        return ("custom_range_start", "custom_range_end")
    return ()


def _draw_motion_paths(layout, context) -> None:
    settings = context.scene.ghost_tool
    row = layout.row(align=True)
    row.scale_y = 1.2
    row.operator("ghost_tool.paths_add_selected", text="Add Path for Selected", icon='ADD')
    row = layout.row(align=True)
    row.label(text=f"Motion paths · {sum(1 for e in settings.motion_paths if not e.is_folder)}")
    row.operator("ghost_tool.paths_toggle_visible", text="All on").action = 'ALL_ON'
    row.operator("ghost_tool.paths_toggle_visible", text="All off").action = 'ALL_OFF'
    row.operator("ghost_tool.paths_clear", text="", icon='TRASH')
    row = layout.row(align=True)
    row.operator("ghost_tool.paths_toggle_front", text="All in front", icon='XRAY').action = 'ALL_ON'
    row.operator("ghost_tool.paths_toggle_front", text="All behind", icon='MESH_CUBE').action = 'ALL_OFF'
    row = layout.row(align=True)
    row.operator("ghost_tool.paths_add_folder", text="Add Folder", icon='NEWFOLDER')
    row.operator("ghost_tool.paths_apply_to_checked", text="Apply to Checked", icon='PASTEDOWN')
    row.menu("GHOST_MT_paths_checked", text="Checked")
    layout.template_list("GHOST_UL_paths", "", settings, "motion_paths", settings, "motion_paths_index", rows=4, maxrows=8)
    col = layout.column(align=True)
    col.label(text="Range")
    col.prop(settings, "paths_range_mode", text="")
    fields = _range_props(settings)
    if fields:
        row = col.row(align=True)
        for name, label in zip(fields, ("Before", "After") if fields[0] == "paths_before" else ("Start", "End")):
            row.prop(settings, name, text=label)
    col.prop(settings, "paths_step", text="Every")
    col = layout.column(align=True)
    col.label(text="Style")
    col.prop(settings, "paths_style", expand=True)
    row = layout.row(align=True)
    row.prop(settings, "paths_show_markers", text="Markers", toggle=True)
    row.prop(settings, "paths_show_key_dots", text="Key dots", toggle=True)
    row.prop(settings, "paths_show_frame_numbers", text="Frame #", toggle=True)
    row.prop(settings, "paths_active_glow", text="Glow", toggle=True)


#: (key, label, icon, draw function, help topic, open by default)
GHOST_SECTIONS: tuple = (
    ("show", "Show Ghosts", 'GHOST_ENABLED', _draw_show_ghosts, "marker_placement", True),
    ("onion", "Onion Skin", 'MESH_DATA', _draw_onion_skin, "onion_skin", False),
    ("paths", "Motion Paths", 'CURVE_PATH', _draw_motion_paths, "motion_paths", False),
    ("edit", "Edit Motion", 'ORIENTATION_CURSOR', _draw_edit_motion, "marker_tools", False),
    ("compare", "Compare", 'ARROW_LEFTRIGHT', _draw_compare, "snapshots", False),
    ("physics", "Physics", 'FORCE_FORCE', _draw_physics, "marker_tools", False),
    ("look", "Look", 'HIDE_OFF', _draw_look, "marker_display", False),
    ("settings", "Settings", 'PREFERENCES', _draw_settings, "settings", False),
)


def draw_ghost_tool(layout, context, prefix: str) -> None:
    """The whole Ghost Tool layout: status or welcome, then the collapsible groups."""
    scene = context.scene
    if not hasattr(scene, 'ghost_tool'):
        box = layout.box()
        box.label(text="Ghost Tool not initialized", icon='ERROR')
        box.operator("ghost_tool.initialize", text="Initialize Ghost Tool", icon='SETTINGS')
        return
    settings = scene.ghost_tool
    try:
        store = GhostStore.get(scene)
    except Exception as exc:
        box = layout.box()
        box.label(text="Ghost Tool: initialization error", icon='ERROR')
        box.label(text=str(exc)[:80])
        return

    if not settings.is_active:
        _row_label(layout, "Trace your animation's path")
        _row_label(layout, "and drag it to reshape motion")
        row = layout.row()
        row.scale_y = 1.5
        row.prop(settings, "is_active", text="Turn On Ghosts", toggle=True, icon='GHOST_ENABLED')
        return

    row = layout.row(align=True)
    row.label(text=f"{len(store)} markers, {len(store.get_pinned())} pinned", icon='GHOST_ENABLED')
    _draw_help_icon(row, context, "overview")
    for key, label, icon, draw, topic, is_open in GHOST_SECTIONS:
        header, body = layout.panel(f"ghost_tool_{prefix}_{key}", default_closed=not is_open)
        header.label(text=label, icon=icon)
        _draw_help_icon(header, context, topic)
        if body is None:
            continue
        try:
            draw(body, context)
        except Exception as exc:
            warn(f"Ghost Tool: could not draw {label}: {exc}")
            body.label(text="This section could not draw", icon='ERROR')


class GHOST_PT_paths_popover(bpy.types.Panel):
    bl_idname = "GHOST_PT_paths_popover"
    bl_label = "Motion Paths"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'HEADER'
    bl_ui_units_x = 18   # 3.6 rows carry a checkbox and an indent; at 14 names were cut to "Rig › ..."

    def draw(self, context):
        _draw_motion_paths(self.layout, context)


class GHOST_PT_header_menu(bpy.types.Panel):
    """The Ghost Tool dropdown in the 3D Viewport header."""

    bl_idname = "GHOST_PT_header_menu"
    bl_label = "Ghost Tool"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'HEADER'
    bl_ui_units_x = 14

    def draw(self, context: bpy.types.Context) -> None:
        draw_ghost_tool(self.layout, context, "menu")
        layout = self.layout
        layout.separator()
        layout.operator("ghost_tool.open_window", icon='WINDOW')


# Windows opened by "Open in Separate Window" (their sidebars show Ghost Tool).
_ghost_windows: set[int] = set()


class GHOST_PT_window(bpy.types.Panel):
    """Ghost Tool in the sidebar of its own separate window only."""

    bl_idname = "GHOST_PT_window"
    bl_label = "Ghost Tool"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Ghost Tool"

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        window = getattr(context, "window", None)
        return window is not None and window.as_pointer() in _ghost_windows

    def draw_header(self, context: bpy.types.Context) -> None:
        if hasattr(context.scene, 'ghost_tool'):
            self.layout.prop(context.scene.ghost_tool, "is_active", text="", icon='GHOST_ENABLED')

    def draw(self, context: bpy.types.Context) -> None:
        draw_ghost_tool(self.layout, context, "window")


class GHOST_OT_open_window(bpy.types.Operator):
    """Open Ghost Tool in its own window that stays open while you work"""

    bl_idname = "ghost_tool.open_window"
    bl_label = "Open in Separate Window"
    bl_description = (
        "Open a separate viewport window with Ghost Tool in its sidebar. It stays "
        "open while you work; move it anywhere, or to a second monitor"
    )
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return context.window is not None and context.screen is not None

    def execute(self, context: bpy.types.Context) -> set[str]:
        area = context.area if context.area and context.area.type == 'VIEW_3D' else next(
            (a for a in context.screen.areas if a.type == 'VIEW_3D'), None)
        if area is None:
            return report_failure(self, "No 3D Viewport to open the window from",
                                  "Open a 3D Viewport and try again")
        before = set(context.window_manager.windows[:])
        region = next((r for r in area.regions if r.type == 'WINDOW'), None)
        try:
            with context.temp_override(window=context.window, screen=context.screen, area=area, region=region):
                bpy.ops.screen.area_dupli('INVOKE_DEFAULT')
        except Exception as exc:
            return report_failure(self, "Could not open a new window", "Use Window > New Window instead", exc)
        new = [w for w in context.window_manager.windows if w not in before]
        if not new:
            return report_failure(self, "Could not open a new window", "Use Window > New Window instead")
        window = new[0]
        _ghost_windows.add(window.as_pointer())
        view = next((a for a in window.screen.areas if a.type == 'VIEW_3D'), None)
        if view is not None:
            view.spaces.active.show_region_ui = True

            def _select_tab():
                ui = next((r for r in view.regions if r.type == 'UI'), None)
                try:
                    if ui is not None:
                        ui.active_panel_category = "Ghost Tool"
                except Exception:
                    return 0.1  # the tab exists after the first redraw
                return None

            bpy.app.timers.register(_select_tab, first_interval=0.05)
        return {'FINISHED'}


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  SECTION 4 — FLOATING TOOLBAR OPERATOR                                ║
# ╚══════════════════════════════════════════════════════════════════════════╝

class GHOST_OT_floating_toolbar(bpy.types.Operator):
    """Pop out the Ghost Tool layout as a floating panel under the mouse."""

    bl_idname = "ghost_tool.floating_toolbar"
    bl_label = "Ghost Tool — Floating Toolbar"
    bl_options = {'REGISTER'}

    def execute(self, context: bpy.types.Context) -> set[str]:
        return context.window_manager.invoke_popup(self, width=320)

    def draw(self, context: bpy.types.Context) -> None:
        draw_ghost_tool(self.layout, context, "popup")


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  SECTION 5 — TIMELINE / DOPESHEET HEADER EXTENSION                    ║
# ╚══════════════════════════════════════════════════════════════════════════╝

def _slow_label(refresh_ms: float) -> str:
    """Warning text for the header strip when a path refresh took over 200 ms."""
    return "paths are slow — reduce range" if refresh_ms > 200.0 else ""


def _draw_paths_segment(row, settings) -> None:
    row.separator(factor=0.5)
    row.prop(settings, "paths_enabled", text="Paths", icon='CURVE_PATH', toggle=True)
    row.operator("ghost_tool.paths_add_selected", text="Add", icon='BONE_DATA')
    row.prop(settings, "paths_follow_selection", text="Follow", icon='RESTRICT_SELECT_OFF', toggle=True)
    row.popover(panel="GHOST_PT_paths_popover", text="", icon='DOWNARROW_HLT')
    from .motion_paths import last_refresh_ms
    slow = _slow_label(last_refresh_ms())
    if slow:
        row.label(text=slow, icon='ERROR')


def _draw_timeline_header_extension(self, context: bpy.types.Context) -> None:
    """Append a compact ghost toggle strip to the Timeline/Dopesheet header.

    This function is appended to Blender's built-in header draw lists
    so Ghost Tool controls are always visible when animating.

    Args:
        self: The header panel instance.
        context: The current Blender context.
    """
    scene = context.scene
    if not hasattr(scene, 'ghost_tool'):
        return

    settings = scene.ghost_tool
    store = GhostStore.get(scene)
    layout = self.layout

    # Separator from Blender's built-in header items
    layout.separator_spacer()

    # Compact ghost strip in the header
    row = layout.row(align=True)

    # On/off toggle — the most important button
    icon = 'GHOST_ENABLED' if settings.is_active else 'GHOST_DISABLED'
    row.prop(settings, "is_active", text="", icon=icon, toggle=True)

    # Only show the rest when ghosts are active
    if settings.is_active:
        # Generate / Clear
        row.operator("ghost_tool.generate_ghosts", text="", icon='ADD')
        row.operator("ghost_tool.clear_ghosts", text="", icon='TRASH')

        # Subdivision level (compact)
        sub = row.row(align=True)
        sub.scale_x = 0.6
        sub.prop(settings, "subdivision_level", text="")

        row.separator(factor=0.5)

        # Drag mode
        row.operator("ghost_tool.drag_ghost", text="", icon='ORIENTATION_CURSOR')

        # Pin
        row.operator("ghost_tool.pin_ghost", text="", icon='PINNED')

        # Snapshot
        row.operator("ghost_tool.take_snapshot", text="", icon='CAMERA_DATA')

        # Display toggles
        row.separator(factor=0.5)
        row.prop(settings, "show_arc_lines", text="", icon='CURVE_PATH', toggle=True)
        row.prop(settings, "show_spacing_ticks", text="", icon='TIME', toggle=True)

        # Mesh onion skin toggle
        row.separator(factor=0.5)
        icon_mesh = 'MOD_MESHDEFORM' if settings.show_mesh_ghosts else 'MESH_DATA'
        row.prop(settings, "show_mesh_ghosts", text="", icon=icon_mesh, toggle=True)
        _draw_paths_segment(row, settings)

        # Ghost count
        if len(store) > 0:
            row.label(text=f" {len(store)}")

    # Pop-out button (opens floating toolbar for full controls)
    row.separator(factor=0.5)
    row.operator("ghost_tool.floating_toolbar", text="", icon='WINDOW')


def _draw_graph_header_extension(self, context: bpy.types.Context) -> None:
    """Ghost toggle plus the motion-path segment in the Graph Editor header."""
    scene = context.scene
    if not hasattr(scene, 'ghost_tool'):
        return
    settings = scene.ghost_tool
    layout = self.layout
    layout.separator_spacer()
    row = layout.row(align=True)
    row.prop(settings, "is_active", text="", icon='GHOST_ENABLED' if settings.is_active else 'GHOST_DISABLED', toggle=True)
    if settings.is_active:
        _draw_paths_segment(row, settings)


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  SECTION 6 — 3D VIEWPORT HEADER EXTENSION                             ║
# ╚══════════════════════════════════════════════════════════════════════════╝

def _draw_viewport_header_menu(self, context: bpy.types.Context) -> None:
    """Ghost on/off toggle and the "Ghost Tool" dropdown, after the Pose menu."""
    scene = context.scene
    if not hasattr(scene, 'ghost_tool'):
        return
    settings = scene.ghost_tool
    row = self.layout.row(align=True)
    row.prop(settings, "is_active", text="",
             icon='GHOST_ENABLED' if settings.is_active else 'GHOST_DISABLED', toggle=True)
    row.popover(panel="GHOST_PT_header_menu", text="Ghost Tool")


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

CLASSES: tuple[type, ...] = (
    GhostToolEasingSettings,
    GHOST_OT_show_help_popup,
    GHOST_UL_paths,
    GHOST_MT_paths_checked,
    GHOST_MT_paths_move_to,
    GHOST_PT_paths_popover,
    GHOST_PT_header_menu,
    GHOST_PT_window,
    GHOST_OT_open_window,
    GHOST_OT_floating_toolbar,
)

# Track header appends for clean unregistration
_header_appends: list[tuple] = []


def register() -> None:
    """Register all UI classes and header extensions."""
    for cls in CLASSES:
        bpy.utils.register_class(cls)

    bpy.types.Scene.ghost_tool_easing = bpy.props.PointerProperty(
        type=GhostToolEasingSettings,
        name="Ghost Tool Easing Settings",
    )

    # Append to Timeline header
    try:
        bpy.types.DOPESHEET_HT_header.append(_draw_timeline_header_extension)
        _header_appends.append(
            (bpy.types.DOPESHEET_HT_header, _draw_timeline_header_extension)
        )
    except Exception as exc:
        warn(f"Could not append to Dopesheet header: {exc}")

    # Graph Editor header: ghost toggle + motion-path segment
    try:
        bpy.types.GRAPH_HT_header.append(_draw_graph_header_extension)
        _header_appends.append(
            (bpy.types.GRAPH_HT_header, _draw_graph_header_extension)
        )
    except Exception as exc:
        warn(f"Could not append to Graph Editor header: {exc}")

    # 3D Viewport header: toggle + "Ghost Tool" dropdown after the Pose menu
    try:
        bpy.types.VIEW3D_MT_editor_menus.append(_draw_viewport_header_menu)
        _header_appends.append(
            (bpy.types.VIEW3D_MT_editor_menus, _draw_viewport_header_menu)
        )
    except Exception as exc:
        warn(f"Could not append to 3D Viewport header: {exc}")

    log("UI panels and header strips registered.")


def unregister() -> None:
    """Unregister all UI classes and remove header extensions."""
    # Remove header appends first
    for header_cls, func in _header_appends:
        try:
            header_cls.remove(func)
        except Exception as exc:
            warn(f"Warning removing header append: {exc}")
    _header_appends.clear()

    if hasattr(bpy.types.Scene, 'ghost_tool_easing'):
        del bpy.types.Scene.ghost_tool_easing

    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)

    log("UI panels and header strips unregistered.")


# ---------------------------------------------------------------------------
# Test notes
# ---------------------------------------------------------------------------
#
# tests/test_ghost_header_ui.py covers the header menu, the separate window,
# rotation markers and the onion-skin sources headless.
