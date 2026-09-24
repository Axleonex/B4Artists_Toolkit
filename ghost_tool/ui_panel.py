"""
ui_panel.py — Ghost Tool UI: header strip, floating toolbar, and settings popovers.

Design philosophy:
    The primary control surface is a compact ICON STRIP that can live:
      1. Docked in the 3D Viewport's N-panel as a single compact row
      2. Appended to the Timeline / Dopesheet header for always-on access
      3. Popped out as a floating toolbar via a dedicated operator

    Every feature has a one-click icon button WITH a friendly text label.
    Detailed settings (colors, radii, ranges) are tucked into popovers
    so the strip stays clean but nothing is hidden.

    The goal is Grease-Pencil-onion-skinning simplicity with professional power.
"""

from __future__ import annotations

import textwrap

import bpy

from .ghost_data import AnchorState, DiffReference, GhostStore
from .snapshot import SnapshotStore
from .easing_presets import PRESET_ENUM_ITEMS
from .utils import log, warn, debug


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
# ║  SECTION 1 — THE GHOST STRIP  (compact icon + label toolbar)          ║
# ╚══════════════════════════════════════════════════════════════════════════╝

class GHOST_PT_strip(bpy.types.Panel):
    """Primary Ghost Tool strip — one-click access to every feature.

    This panel renders as a compact, icon-rich toolbar inside the
    N-panel sidebar.  It is designed to feel like a dedicated timeline
    tab for ghosting, not a buried settings menu.
    """

    bl_idname = "GHOST_PT_strip"
    bl_label = "Ghost Tool"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Ghost Tool"

    def draw_header(self, context: bpy.types.Context) -> None:
        """Draw the panel header with the master on/off toggle.

        Args:
            context: The current Blender context.
        """
        layout = self.layout
        scene = context.scene
        if hasattr(scene, 'ghost_tool'):
            # Master toggle (GHOST_ENABLED icon shows system is active)
            layout.prop(scene.ghost_tool, "is_active", text="", icon='GHOST_ENABLED')
        _draw_help_icon(layout, context, "overview")

    def draw(self, context: bpy.types.Context) -> None:
        """Draw the full ghost strip UI.

        Args:
            context: The current Blender context.
        """
        layout = self.layout
        scene = context.scene

        if not hasattr(scene, 'ghost_tool'):
            # The scene-level PropertyGroup is missing.  Show an actionable
            # button instead of a dead-end error so the user can fix it.
            box = layout.box()
            box.label(text="Ghost Tool not initialized", icon='ERROR')
            box.operator(
                "ghost_tool.initialize",
                text="Initialize Ghost Tool",
                icon='SETTINGS',
            )
            return

        settings = scene.ghost_tool
        try:
            store = GhostStore.get(scene)
        except Exception as exc:
            box = layout.box()
            box.label(text="Ghost Tool: initialization error", icon='ERROR')
            box.label(text=str(exc)[:80])
            return

        try:
            self._draw_main(context, layout, scene, settings, store)
        except Exception as exc:
            import traceback
            traceback.print_exc()
            box = layout.box()
            box.label(text="Ghost Tool: UI draw error", icon='ERROR')
            box.label(text=str(exc)[:80])

    def _draw_main(self, context, layout, scene, settings, store):

        # ══════════════════════════════════════════════════════
        # GHOST TOOLS — single master toggle that controls everything.
        # Turning OFF clears all ghosts. Turning ON enables the tool suite.
        # ══════════════════════════════════════════════════════
        row = layout.row(align=True)
        row.scale_y = 1.2
        icon = 'GHOST_ENABLED' if settings.is_active else 'GHOST_DISABLED'
        row.prop(
            settings, "is_active",
            text="Ghost Tools" if settings.is_active else "Ghost Tools (OFF)",
            icon=icon,
            toggle=True,
        )

        if not settings.is_active:
            return  # Everything hidden when tools are off

        layout.label(text="Generate → Drag → Refine", icon='INFO')
        status = layout.row(align=True)
        status.label(text=f"{len(store)} markers", icon='GHOST_ENABLED')
        status.label(text=f"{len(store.get_pinned())} pinned", icon='PINNED')


# ---------------------------------------------------------------------------
# Helper: shared poll for child panels (only show when Ghost Tools is ON)
# ---------------------------------------------------------------------------

def _ghost_active_poll(cls, context):
    """Only show child panels when Ghost Tools is active."""
    if not hasattr(context.scene, 'ghost_tool'):
        return False
    return context.scene.ghost_tool.is_active


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  CHILD PANEL 1 — ONION SKIN                                           ║
# ╚══════════════════════════════════════════════════════════════════════════╝

class GHOST_PT_onion_skin(_GhostHelpPanelMixin, bpy.types.Panel):
    """Onion Skin — transparent mesh pose silhouettes."""

    bl_idname = "GHOST_PT_onion_skin"
    bl_label = "Onion Skin"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Ghost Tool"
    bl_parent_id = "GHOST_PT_strip"
    help_topic = "onion_skin"

    @classmethod
    def poll(cls, context):
        return _ghost_active_poll(cls, context)

    def draw(self, context):
        layout = self.layout
        settings = context.scene.ghost_tool

        row = layout.row(align=True)
        row.scale_y = 1.2
        row.operator("ghost_tool.generate_mesh_ghosts", text="Generate", icon='MESH_DATA')
        row.operator("ghost_tool.clear_mesh_ghosts", text="Clear", icon='TRASH')

        # Display mode toggle (Solid / Wireframe)
        row = layout.row(align=True)
        row.prop(settings, "mesh_ghost_mode", expand=True)

        # Frame mode toggle (Frame Step / Keyframes Only)
        row = layout.row(align=True)
        row.label(text="Frames:")
        row.prop(settings, "mesh_ghost_frame_mode", text="")

        # Keyframe interval selector (only in KEYFRAMES mode)
        # Controls the stepped interval between ghost keyframes
        if settings.mesh_ghost_frame_mode == 'KEYFRAMES':
            row = layout.row(align=True)
            row.prop(settings, "mesh_ghost_keyframe_skip", text="Interval")
            if settings.mesh_ghost_keyframe_skip == 'CUSTOM':
                row.prop(settings, "mesh_ghost_keyframe_skip_custom", text="Every Nth")

        # Past / Future counts
        row = layout.row(align=True)
        row.prop(settings, "mesh_ghost_past_count", text="Past")
        row.prop(settings, "mesh_ghost_future_count", text="Future")

        # Step (only relevant in STEP mode) and opacity
        row = layout.column(align=True)
        sub = row.row(align=True)
        sub.enabled = (settings.mesh_ghost_frame_mode == 'STEP')
        sub.prop(settings, "mesh_ghost_step", text="Interval")
        row.prop(settings, "mesh_ghost_opacity", text="Opacity", slider=True)

        # Past / Future visibility
        row = layout.row(align=True)
        row.prop(settings, "show_mesh_past", text="Past", toggle=True,
                  icon='REW' if settings.show_mesh_past else 'BLANK1')
        row.prop(settings, "show_mesh_future", text="Future", toggle=True,
                  icon='FF' if settings.show_mesh_future else 'BLANK1')

        # Mesh ghost colors
        col = layout.column(align=True)
        col.prop(settings, "mesh_ghost_past_color", text="Past Color")
        col.prop(settings, "mesh_ghost_future_color", text="Future Color")

        # Outline controls
        row = layout.row(align=True)
        row.prop(settings, "ghost_outline_enabled", text="Outline", toggle=True, icon='MOD_SOLIDIFY')
        if settings.ghost_outline_enabled:
            row.prop(settings, "ghost_outline_width", text="Width")
            row2 = layout.row(align=True)
            row2.prop(settings, "ghost_outline_color", text="Outline Color")

        # Live / Snapshot mode toggle for mesh ghosts
        row = layout.row(align=True)
        if settings.live_mesh_ghosts:
            row.prop(settings, "live_mesh_ghosts", text="Live (follows playhead)",
                     toggle=True, icon='PLAY')
        else:
            row.prop(settings, "live_mesh_ghosts", text="Snapshot (frozen)",
                     toggle=True, icon='PAUSE')


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  CHILD PANEL 2 — MOTION TRAILS                                        ║
# ╚══════════════════════════════════════════════════════════════════════════╝

class GHOST_PT_motion_trails(_GhostHelpPanelMixin, bpy.types.Panel):
    """Motion Trails — dots tracking bone paths through space."""

    bl_idname = "GHOST_PT_motion_trails"
    bl_label = "Motion Trails"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Ghost Tool"
    bl_parent_id = "GHOST_PT_strip"
    help_topic = "motion_trails"

    @classmethod
    def poll(cls, context):
        return _ghost_active_poll(cls, context)

    def draw(self, context):
        layout = self.layout
        settings = context.scene.ghost_tool

        layout.label(text="Motion paths on bones", icon='INFO')

        # Generate / Clear point ghosts
        row = layout.row(align=True)
        row.scale_y = 1.2
        row.operator("ghost_tool.generate_ghosts", text="Generate", icon='ADD')
        row.operator("ghost_tool.clear_ghosts", text="Clear", icon='TRASH')

        # Live / Snapshot mode toggle for bone markers
        row = layout.row(align=True)
        if settings.live_point_ghosts:
            row.prop(settings, "live_point_ghosts", text="Live (follows playhead)",
                     toggle=True, icon='PLAY')
        else:
            row.prop(settings, "live_point_ghosts", text="Snapshot (frozen)",
                     toggle=True, icon='PAUSE')

        # Show freeze + throttle when any live mode is active
        if settings.live_point_ghosts or settings.live_mesh_ghosts:
            row2 = layout.row(align=True)
            row2.prop(settings, "live_freeze", text="Freeze", toggle=True,
                      icon='SNAP_ON' if settings.live_freeze else 'SNAP_OFF')
            row2.prop(settings, "live_throttle_ms", text="Delay")


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  CHILD PANEL 3 — MARKER PLACEMENT                                     ║
# ╚══════════════════════════════════════════════════════════════════════════╝

class GHOST_PT_marker_placement(_GhostHelpPanelMixin, bpy.types.Panel):
    """Marker Placement — distribution mode and temporal range."""

    bl_idname = "GHOST_PT_marker_placement"
    bl_label = "Marker Placement"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Ghost Tool"
    bl_parent_id = "GHOST_PT_strip"
    help_topic = "marker_placement"

    @classmethod
    def poll(cls, context):
        return _ghost_active_poll(cls, context)

    def draw(self, context):
        layout = self.layout
        settings = context.scene.ghost_tool

        # Mode selector: SUBDIVISION, FRAME_STEP, KEYFRAMES_ONLY
        row = layout.row(align=True)
        row.label(text="Placement:")
        row.prop(settings, "ghost_mode", text="")

        # Mode-specific controls
        if settings.ghost_mode == "SUBDIVISION":
            row = layout.row(align=True)
            row.label(text="", icon='MOD_SUBSURF')
            row.prop(settings, "subdivision_level", text="Detail Level", slider=True)
        elif settings.ghost_mode == "FRAME_STEP":
            row = layout.row(align=True)
            row.prop(settings, "frame_step", text="Every N Frames")

        # Range mode
        range_box = layout.box()
        row = range_box.row(align=True)
        row.label(text="Range:", icon='PREVIEW_RANGE')
        row.prop(settings, "ghost_range_mode", text="")

        if settings.ghost_range_mode == "AROUND_CURSOR":
            row = range_box.row(align=True)
            row.prop(settings, "ghosts_before", text="Before")
            row.prop(settings, "ghosts_after", text="After")
        elif settings.ghost_range_mode == "CUSTOM":
            row = range_box.row(align=True)
            row.prop(settings, "custom_range_start", text="Start")
            row.prop(settings, "custom_range_end", text="End")


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  CHILD PANEL 4 — MARKER DISPLAY  (collapsed by default)               ║
# ╚══════════════════════════════════════════════════════════════════════════╝

class GHOST_PT_marker_display(_GhostHelpPanelMixin, bpy.types.Panel):
    """Marker Display — colors, arcs, fading, visual styling."""

    bl_idname = "GHOST_PT_marker_display"
    bl_label = "Marker Display"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Ghost Tool"
    bl_parent_id = "GHOST_PT_strip"
    help_topic = "marker_display"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return _ghost_active_poll(cls, context)

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        settings = scene.ghost_tool
        store = GhostStore.get(scene)

        # Color mode
        row = layout.row(align=True)
        row.label(text="Color:")
        row.prop(settings, "ghost_color_mode", text="")

        # Fade factor (for non-LEVEL modes)
        if settings.ghost_color_mode != "LEVEL":
            row = layout.row(align=True)
            row.prop(settings, "ghost_fade_factor", text="Fade Distance", slider=True)

            row = layout.row(align=True)
            row.label(text="Falloff:")
            row.prop(settings, "ghost_falloff_curve", text="")

            row = layout.row(align=True)
            row.prop(settings, "ghost_min_alpha", text="Min Opacity", slider=True)

        # User-configurable colors per mode
        if settings.ghost_color_mode == "TIME":
            column = layout.column(align=True)
            column.prop(settings, "ghost_past_color", text="Past")
            column.prop(settings, "ghost_future_color", text="Future")
        elif settings.ghost_color_mode == "KEY_INBETWEEN":
            column = layout.column(align=True)
            column.prop(settings, "ghost_key_color", text="Key")
            column.prop(settings, "ghost_inbetween_color", text="Inbetween")

        # Label color
        if settings.show_frame_numbers:
            row = layout.row(align=True)
            row.prop(settings, "ghost_label_color", text="Label Color")

        # Arc lines
        row = layout.row(align=True)
        row.prop(settings, "show_arc_lines", text="Arc Lines", toggle=True, icon='CURVE_PATH')
        if settings.show_arc_lines:
            row.prop(settings, "arc_line_style", text="")

        # Keyframe markers + hover highlights
        row = layout.row(align=True)
        row.prop(settings, "show_keyframe_markers", text="Key Diamonds", toggle=True, icon='KEYFRAME_HLT')
        row.prop(settings, "show_hover_frame_label", text="Hover Label", toggle=True, icon='FONT_DATA')

        row = layout.row(align=True)
        row.enabled = settings.show_keyframe_markers
        row.prop(settings, "keyframe_marker_color", text="Key Color")

        row = layout.row(align=True)
        row.prop(settings, "show_key_bookends", text="Key Bookends", toggle=True, icon='KEYFRAME')
        row2 = layout.row(align=True)
        row2.enabled = settings.show_key_bookends
        row2.prop(settings, "key_bookend_color", text="Bookend Color")

        row = layout.row(align=True)
        row.enabled = settings.show_hover_frame_label
        row.prop(settings, "hover_highlight_color", text="Hover Color")

        # Spacing ticks + frame numbers
        row = layout.row(align=True)
        row.prop(settings, "show_spacing_ticks", text="Spacing", toggle=True, icon='TIME')
        row.prop(settings, "show_frame_numbers", text="Frame #", toggle=True, icon='FONT_DATA')
        row.prop(settings, "show_acceleration_markers", text="Accel", toggle=True, icon='FORCE_TURBULENCE')

        # Per-level visibility (only relevant for subdivision mode)
        if settings.ghost_mode == "SUBDIVISION":
            row = layout.row(align=True)
            row.label(text="Levels:")
            for level in range(1, 6):
                count = store.count_by_level(level)
                icon_lv = 'LAYER_ACTIVE' if settings.is_level_visible(level) else 'LAYER_USED'
                row.prop(
                    settings, f"show_level_{level}",
                    text=str(level), toggle=True,
                    icon=icon_lv if count > 0 else 'BLANK1',
                )


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  CHILD PANEL 5 — MARKER TOOLS                                         ║
# ╚══════════════════════════════════════════════════════════════════════════╝

class GHOST_PT_marker_tools(_GhostHelpPanelMixin, bpy.types.Panel):
    """Marker Tools — drag, select, easing, pin, snapshot, physics."""

    bl_idname = "GHOST_PT_marker_tools"
    bl_label = "Marker Tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Ghost Tool"
    bl_parent_id = "GHOST_PT_strip"
    help_topic = "marker_tools"

    @classmethod
    def poll(cls, context):
        return _ghost_active_poll(cls, context)

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        settings = scene.ghost_tool
        store = GhostStore.get(scene)

        # -- Editing Mode --
        row = layout.row(align=True)
        row.label(text="On confirm:")
        row.prop(settings, "editing_mode", text="")

        # -- Smooth neighbors toggle (only relevant for INSERT_KEY) --
        row = layout.row(align=True)
        row.enabled = settings.editing_mode == 'INSERT_KEY'
        row.prop(settings, "smooth_neighbors_on_commit", text="Smooth Neighbors",
                 toggle=True, icon='MOD_SMOOTH')

        # -- Sculpt Falloff --
        row = layout.row(align=True)
        row.prop(settings, "sculpt_falloff_radius", text="Falloff")
        sub = row.row(align=True)
        sub.enabled = settings.sculpt_falloff_radius > 0
        sub.prop(settings, "sculpt_falloff_curve", text="")

        # -- Drag Mode --
        row = layout.row(align=True)
        row.scale_y = 1.2
        row.operator("ghost_tool.drag_ghost", text="Drag Marker", icon='ORIENTATION_CURSOR')
        sub = layout.row(align=True)
        sub.enabled = (settings.editing_mode == 'RESHAPE')
        sub.label(text="Curve:")
        sub.prop(settings, "curve_mode", text="")
        if settings.editing_mode != 'RESHAPE':
            sub.label(text="(reshape only)")

        # -- Select Marker --
        row = layout.row(align=True)
        row.scale_y = 1.2
        row.operator("ghost_tool.select_ghost", text="Select Marker", icon='RESTRICT_SELECT_OFF')

        # -- Box Select --
        row = layout.row(align=True)
        row.scale_y = 1.2
        row.operator("ghost_tool.box_select", text="Box Select", icon='SELECT_SET')

        # -- Easing --
        row = layout.row(align=True)
        row.scale_y = 1.2
        if hasattr(scene, 'ghost_tool_easing'):
            row.prop(scene.ghost_tool_easing, "active_preset", text="")
            op = row.operator("ghost_tool.apply_easing", text="Apply Easing", icon='IPO_EASE_IN_OUT')
            op.preset = scene.ghost_tool_easing.active_preset
        else:
            row.operator("ghost_tool.apply_easing", text="Apply Easing", icon='IPO_EASE_IN_OUT')

        # -- Pin / Unpin --
        row = layout.row(align=True)
        row.scale_y = 1.2
        row.operator("ghost_tool.pin_ghost", text="Pin Marker", icon='PINNED')
        row.operator("ghost_tool.unpin_all", text="Unpin All", icon='UNPINNED')
        pinned_count = len(store.get_pinned())
        if pinned_count > 0:
            row.label(text=f"({pinned_count})")

        # -- Snapshot --
        row = layout.row(align=True)
        row.scale_y = 1.2
        row.operator("ghost_tool.take_snapshot", text="Snapshot", icon='CAMERA_DATA')
        snap_store = SnapshotStore.get(scene)
        snap_count = len(snap_store.get_all())
        if snap_count > 0:
            row.label(text=f"({snap_count} saved)")

        # -- Physics Suggest --
        row = layout.row(align=True)
        row.scale_y = 1.2
        row.operator("ghost_tool.physics_suggest", text="Physics Arc", icon='FORCE_FORCE')

        # -- Ballistic Preview --
        row = layout.row(align=True)
        row.prop(settings, "show_ballistic_preview", text="Ballistic Preview",
                 toggle=True, icon='FORCE_HARMONIC')
        if settings.show_ballistic_preview:
            column = layout.column(align=True)
            preview_row = column.row(align=True)
            preview_row.prop(settings, "ballistic_gravity", text="Gravity")
            preview_row.prop(settings, "ballistic_gravity_axis", text="")
            column.prop(settings, "ballistic_offset", text="Offset")

        # ── Physics Feel ────────────────────────────────────────────────────
        # Archetype generator: select a physics-feel curve, preview the
        # displacement overlay, then stamp keyframes onto the active channel.
        layout.separator()
        layout.label(text="Physics Feel", icon='IPO_ELASTIC')

        # Archetype selector row
        row = layout.row(align=True)
        row.prop(settings, "archetype_active", text="")

        # Preview toggle — activates the cyan overlay in the viewport
        row.prop(
            settings,
            "show_archetype_preview",
            text="Preview",
            toggle=True,
            icon='HIDE_OFF' if settings.show_archetype_preview else 'HIDE_ON',
        )

        # Expanded controls when preview is on
        if settings.show_archetype_preview:
            column = layout.column(align=True)

            # Amplitude and axis on one row
            amp_row = column.row(align=True)
            amp_row.prop(settings, "archetype_amplitude", text="Amplitude")
            amp_row.prop(settings, "archetype_axis", text="")

            # Frame range
            frame_row = column.row(align=True)
            frame_row.prop(settings, "archetype_start_frame", text="Start")
            frame_row.prop(settings, "archetype_end_frame", text="End")

            # Stamp button — primary action
            stamp_row = column.row(align=True)
            stamp_row.scale_y = 1.3
            stamp_row.operator(
                "ghost_tool.archetype_bake",
                text="Stamp to Keys",
                icon='KEYFRAME_HLT',
            )

        # ── Visual Diff ─────────────────────────────────────────────────────
        # Warm/cool per-bone overlay comparing the current pose against a
        # pinned reference frame.  Pin stores the pose; the overlay colors
        # bones by how far they have moved from it.
        layout.separator()
        layout.label(text="Visual Diff", icon='ARROW_LEFTRIGHT')

        diff_row = layout.row(align=True)
        diff_row.prop(
            settings,
            "show_diff_overlay",
            text="Diff Overlay",
            toggle=True,
            icon='HIDE_OFF' if settings.show_diff_overlay else 'HIDE_ON',
        )

        pin_row = layout.row(align=True)
        pin_row.operator("ghost_tool.pin_diff_reference", text="Pin Reference", icon='PINNED')
        pin_row.operator("ghost_tool.unpin_diff_reference", text="Unpin", icon='UNPINNED')

        if settings.show_diff_overlay:
            diff_col = layout.column(align=True)
            diff_ref = DiffReference.get(scene)
            if diff_ref is None:
                diff_col.label(text="No reference pinned", icon='INFO')
            else:
                is_stale = diff_ref.state == AnchorState.STALE
                diff_col.label(
                    text=f"Frame {diff_ref.anchor_frame}: {'stale' if is_stale else 'live'}",
                    icon='ERROR' if is_stale else 'CHECKMARK',
                )
            diff_col.prop(settings, "diff_max_distance", text="Max Distance")
            color_row = diff_col.row(align=True)
            color_row.prop(settings, "diff_cool_color", text="")
            color_row.prop(settings, "diff_warm_color", text="")


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  CHILD PANEL 6 — EXPORT / IMPORT                                      ║
# ╚══════════════════════════════════════════════════════════════════════════╝

class GHOST_PT_export_import(_GhostHelpPanelMixin, bpy.types.Panel):
    """Export / Import — save and load ghost data."""

    bl_idname = "GHOST_PT_export_import"
    bl_label = "Export / Import"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Ghost Tool"
    bl_parent_id = "GHOST_PT_strip"
    help_topic = "export_import"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return _ghost_active_poll(cls, context)

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)
        row.operator("ghost_tool.export_ghosts", text="Export", icon='EXPORT')
        row.operator("ghost_tool.import_ghosts", text="Import", icon='IMPORT')


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  SECTION 2 — SETTINGS POPOVER  (detailed tuning, opened from strip)   ║
# ╚══════════════════════════════════════════════════════════════════════════╝

class GHOST_PT_settings(_GhostHelpPanelMixin, bpy.types.Panel):
    """Detailed settings panel — frame range, grab radius, custom easing.

    This sub-panel holds the "deep" controls that don't need to be
    visible all the time but should be one click away.
    """

    bl_idname = "GHOST_PT_settings"
    bl_label = "Settings"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Ghost Tool"
    bl_parent_id = "GHOST_PT_strip"
    help_topic = "settings"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        """Only show the Settings sub-panel when Ghost Tool is initialized."""
        return hasattr(context.scene, 'ghost_tool')

    def draw(self, context: bpy.types.Context) -> None:
        """Draw the detailed settings sub-panel.

        Args:
            context: The current Blender context.
        """
        layout = self.layout
        scene = context.scene

        if not hasattr(scene, 'ghost_tool'):
            return

        settings = scene.ghost_tool

        # Grab radius
        layout.prop(settings, "grab_radius", text="Grab Radius (px)", icon='CURSOR')

        layout.separator()

        # Frame range
        box = layout.box()
        box.label(text="Frame Range", icon='PREVIEW_RANGE')
        box.prop(settings, "use_custom_range", text="Use Custom Range")
        if settings.use_custom_range:
            row = box.row(align=True)
            row.prop(settings, "custom_range_start", text="Start")
            row.prop(settings, "custom_range_end", text="End")

        layout.separator()

        # Custom easing tangent inputs
        if hasattr(scene, 'ghost_tool_easing'):
            easing = scene.ghost_tool_easing
            if easing.active_preset == "CUSTOM":
                box = layout.box()
                box.label(text="Custom Tangent Handles", icon='HANDLETYPE_FREE_VEC')
                row = box.row(align=True)
                row.prop(easing, "custom_left_x", text="L.X")
                row.prop(easing, "custom_left_y", text="L.Y")
                row = box.row(align=True)
                row.prop(easing, "custom_right_x", text="R.X")
                row.prop(easing, "custom_right_y", text="R.Y")


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  SECTION 3 — SNAPSHOT MANAGER  (sub-panel with list)                   ║
# ╚══════════════════════════════════════════════════════════════════════════╝

class GHOST_PT_snapshot_manager(_GhostHelpPanelMixin, bpy.types.Panel):
    """Snapshot management sub-panel — list, toggle, restore, delete."""

    bl_idname = "GHOST_PT_snapshot_manager"
    bl_label = "Saved Snapshots"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Ghost Tool"
    bl_parent_id = "GHOST_PT_strip"
    help_topic = "snapshots"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        """Only show the Snapshots sub-panel when Ghost Tool is initialized."""
        return hasattr(context.scene, 'ghost_tool')

    def draw(self, context: bpy.types.Context) -> None:
        """Draw the snapshot list.

        Args:
            context: The current Blender context.
        """
        layout = self.layout
        scene = context.scene
        snap_store = SnapshotStore.get(scene)
        snapshots = snap_store.get_all()

        if not snapshots:
            layout.label(text="No snapshots yet — click Snapshot above")
            return

        for snap in snapshots:
            box = layout.box()
            row = box.row(align=True)

            # Visibility eye icon
            icon = 'HIDE_OFF' if snap.is_visible else 'HIDE_ON'
            op = row.operator("ghost_tool.toggle_snapshot", text="", icon=icon)
            op.snapshot_uid = snap.uid

            # Name and ghost count
            row.label(text=f"{snap.name}  ({len(snap.ghost_data)})")

            # Restore and delete
            op = row.operator("ghost_tool.restore_snapshot", text="", icon='LOOP_BACK')
            op.snapshot_uid = snap.uid
            op = row.operator("ghost_tool.delete_snapshot", text="", icon='X')
            op.snapshot_uid = snap.uid


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  SECTION 4 — FLOATING TOOLBAR OPERATOR                                ║
# ╚══════════════════════════════════════════════════════════════════════════╝

class GHOST_OT_floating_toolbar(bpy.types.Operator):
    """Pop out the Ghost Tool strip as a floating toolbar dialog.

    This creates a detached popup containing the full icon strip.
    Useful for animators who want the ghost controls floating over
    the viewport without the N-panel open.
    """

    bl_idname = "ghost_tool.floating_toolbar"
    bl_label = "Ghost Tool — Floating Toolbar"
    bl_options = {'REGISTER'}

    def execute(self, context: bpy.types.Context) -> set[str]:
        """Show the floating toolbar.

        Args:
            context: The current Blender context.

        Returns:
            set[str]: {'FINISHED'}.
        """
        return context.window_manager.invoke_popup(self, width=320)

    def draw(self, context: bpy.types.Context) -> None:
        """Draw the floating toolbar contents (mirrors the strip).

        Args:
            context: The current Blender context.
        """
        layout = self.layout
        scene = context.scene

        if not hasattr(scene, 'ghost_tool'):
            box = layout.box()
            box.label(text="Ghost Tool not initialized", icon='ERROR')
            box.operator(
                "ghost_tool.initialize",
                text="Initialize Ghost Tool",
                icon='SETTINGS',
            )
            return

        settings = scene.ghost_tool
        store = GhostStore.get(scene)

        # ── Master toggle ──
        row = layout.row(align=True)
        row.scale_y = 1.8
        icon = 'GHOST_ENABLED' if settings.is_active else 'GHOST_DISABLED'
        row.prop(
            settings, "is_active",
            text="  GHOSTS ON" if settings.is_active else "  GHOSTS OFF",
            icon=icon,
            toggle=True,
        )
        if len(store) > 0:
            row.label(text=f" {len(store)}")

        layout.separator()

        # ── Generate / Clear ──
        row = layout.row(align=True)
        row.scale_y = 1.3
        row.operator("ghost_tool.generate_ghosts", text="Generate", icon='ADD')
        row.operator("ghost_tool.clear_ghosts", text="Clear", icon='TRASH')

        # ── Subdivision slider ──
        row = layout.row(align=True)
        row.prop(settings, "subdivision_level", text="Detail Level", slider=True)

        layout.separator()

        # ── Tool buttons (2 columns) ──
        grid = layout.grid_flow(columns=2, align=True, even_columns=True)
        grid.scale_y = 1.2

        grid.operator("ghost_tool.drag_ghost", text="Drag Marker", icon='ORIENTATION_CURSOR')
        grid.operator("ghost_tool.box_select", text="Box Select", icon='SELECT_SET')
        grid.operator("ghost_tool.pin_ghost", text="Pin Marker", icon='PINNED')
        grid.operator("ghost_tool.take_snapshot", text="Snapshot", icon='CAMERA_DATA')
        grid.operator("ghost_tool.unpin_all", text="Unpin All", icon='UNPINNED')
        grid.operator("ghost_tool.physics_suggest", text="Physics Arc", icon='FORCE_FORCE')

        if hasattr(scene, 'ghost_tool_easing'):
            op = grid.operator("ghost_tool.apply_easing", text="Apply Easing", icon='IPO_EASE_IN_OUT')
            op.preset = scene.ghost_tool_easing.active_preset

        layout.separator()

        # ── Display toggles ──
        row = layout.row(align=True)
        row.prop(settings, "show_arc_lines", text="Arc", toggle=True, icon='CURVE_PATH')
        row.prop(settings, "show_spacing_ticks", text="Spacing", toggle=True, icon='TIME')

        # Level toggles
        row = layout.row(align=True)
        for level in range(1, 6):
            row.prop(settings, f"show_level_{level}", text=str(level), toggle=True)

        layout.separator()

        # ── Export / Import ──
        row = layout.row(align=True)
        row.operator("ghost_tool.export_ghosts", text="Export", icon='EXPORT')
        row.operator("ghost_tool.import_ghosts", text="Import", icon='IMPORT')

    def invoke(self, context: bpy.types.Context, event: bpy.types.Event) -> set[str]:
        """Invoke the popup.

        Args:
            context: The current Blender context.
            event: The triggering event.

        Returns:
            set[str]: Popup result.
        """
        return context.window_manager.invoke_popup(self, width=320)


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  SECTION 5 — TIMELINE / DOPESHEET HEADER EXTENSION                    ║
# ╚══════════════════════════════════════════════════════════════════════════╝

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

        # Ghost count
        if len(store) > 0:
            row.label(text=f" {len(store)}")

    # Pop-out button (opens floating toolbar for full controls)
    row.separator(factor=0.5)
    row.operator("ghost_tool.floating_toolbar", text="", icon='WINDOW')


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  SECTION 6 — 3D VIEWPORT HEADER EXTENSION                             ║
# ╚══════════════════════════════════════════════════════════════════════════╝

def _draw_viewport_header_extension(self, context: bpy.types.Context) -> None:
    """Append a minimal ghost toggle to the 3D Viewport header.

    Sits next to the overlay/gizmo dropdowns for quick access.

    Args:
        self: The header panel instance.
        context: The current Blender context.
    """
    scene = context.scene
    if not hasattr(scene, 'ghost_tool'):
        return

    settings = scene.ghost_tool
    layout = self.layout

    row = layout.row(align=True)
    icon = 'GHOST_ENABLED' if settings.is_active else 'GHOST_DISABLED'
    row.prop(settings, "is_active", text="", icon=icon, toggle=True)

    # Pop-out for full toolbar
    row.operator("ghost_tool.floating_toolbar", text="", icon='WINDOW')


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

CLASSES: tuple[type, ...] = (
    GhostToolEasingSettings,
    GHOST_OT_show_help_popup,
    GHOST_PT_strip,
    GHOST_PT_onion_skin,
    GHOST_PT_motion_trails,
    GHOST_PT_marker_placement,
    GHOST_PT_marker_display,
    GHOST_PT_marker_tools,
    GHOST_PT_export_import,
    GHOST_PT_settings,
    GHOST_PT_snapshot_manager,
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

    # Append to 3D Viewport header
    try:
        bpy.types.VIEW3D_HT_header.append(_draw_viewport_header_extension)
        _header_appends.append(
            (bpy.types.VIEW3D_HT_header, _draw_viewport_header_extension)
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
# Test 1: N-panel strip
# >>> # Open 3D Viewport → N → Ghost Tool tab
# >>> # Should see: big on/off toggle, generate/clear, tool icons, display toggles
#
# Test 2: Timeline header
# >>> # Open Timeline or Dopesheet editor
# >>> # Ghost toggle icon should appear in the header bar on the right
# >>> # Click it — ghosts toggle on/off
#
# Test 3: Floating toolbar
# >>> bpy.ops.ghost_tool.floating_toolbar('INVOKE_DEFAULT')
# >>> # A popup window should appear with the full icon grid
#
# Test 4: 3D Viewport header
# >>> # Small ghost icon should appear in the 3D viewport header
# >>> # Next to the overlay/gizmo buttons
