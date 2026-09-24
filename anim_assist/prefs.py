"""Addon preferences with module toggles and settings I/O hooks."""

from __future__ import annotations

import bpy
from bpy.props import BoolProperty, FloatProperty, IntProperty

from . import constants
from .core.logging import get_logger, set_level
# --- HELP SYSTEM INTEGRATION ---
from .core.help_draw import draw_explainer_icon
from .ui.help_browser import draw_help_browser

_log = get_logger(__name__)


def _update_pie_hotkey(self, _context: bpy.types.Context) -> None:
    from .ui import header_menus
    header_menus.set_pie_hotkey_active(self.pie_hotkey_enabled)


class AA_AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = constants.ADDON_PACKAGE

    debug_mode: BoolProperty(  # type: ignore[valid-type]
        name="Debug Mode",
        description="Enable verbose logging to the console",
        default=False,
        update=lambda self, _ctx: set_level(self.debug_mode),
    )

    performance_mode: BoolProperty(  # type: ignore[valid-type]
        name="Performance Mode",
        description="Reduce UI updates and diagnostics for better performance",
        default=False,
    )

    diagnostics_visible: BoolProperty(  # type: ignore[valid-type]
        name="Show Diagnostics Panel",
        description="Show the diagnostics panel in Properties > Scene > Anim Assist > Help & Diagnostics",
        default=False,
    )

    # --- HELP SYSTEM INTEGRATION ---
    show_explainer_help: BoolProperty(  # type: ignore[valid-type]
        name="Show Extended Help Popups",
        description=(
            "Show Anim Assist question-mark buttons that open detailed help popups; "
            "native Bforartists hover tooltips are unaffected"
        ),
        default=True,
    )
    compact_ui_mode: BoolProperty(  # type: ignore[valid-type]
        name="Compact UI Mode",
        description=(
            "Draw explainer icons without their neighbouring text labels to "
            "keep sidebar panels dense on small screens"
        ),
        default=False,
    )

    # Operator behaviour toggles (used by curve_tool_ops and anim_offset_ops).
    animassist_fast_offset: BoolProperty(  # type: ignore[valid-type]
        name="Fast Offset Mode",
        description="Only propagate Anim Offset on mouse release (faster for complex rigs)",
        default=False,
    )
    animassist_autokey_outside_margins: BoolProperty(  # type: ignore[valid-type]
        name="Auto-key Outside Margins",
        description="Auto-insert keys for frames outside the mask blend region during Anim Offset",
        default=False,
    )
    animassist_drag_sensitivity: IntProperty(  # type: ignore[valid-type]
        name="Drag Sensitivity",
        description="Mouse pixels needed to reach factor 1.0 in modal drag operators",
        default=200,
        min=10,
        max=2000,
    )

    # Key diagnostics defaults.
    p2_dense_min_gap: FloatProperty(  # type: ignore[valid-type]
        name="Dense Key Min Gap",
        description="Frames below this count as 'too dense' in the diagnostics scan",
        default=1.0,
        min=0.0,
    )
    p2_redundant_tolerance: FloatProperty(  # type: ignore[valid-type]
        name="Redundant Key Tolerance",
        description="Value tolerance for flagging a key as redundant (lies on a line)",
        default=1e-4,
        min=0.0,
    )
    p2_spike_ratio: FloatProperty(  # type: ignore[valid-type]
        name="Spike Ratio",
        description="Neighbour deviation ratio at which a key is flagged as a spike",
        default=4.0,
        min=1.0,
    )

    # Where Anim Assist appears (Properties > Scene > Anim Assist > Settings).
    pie_hotkey_enabled: BoolProperty(  # type: ignore[valid-type]
        name="Anim Assist Pie Menu Hotkey",
        description=(
            "Open the Anim Assist pie with a shortcut in the 3D Viewport, Graph Editor "
            "and Dope Sheet (Shift Alt D unless you change it)"
        ),
        default=False,
        update=_update_pie_hotkey,
    )
    header_menu_view3d: BoolProperty(  # type: ignore[valid-type]
        name="3D Viewport",
        description="Show the Anim Assist menu in the 3D Viewport header",
        default=True,
    )
    header_menu_graph: BoolProperty(  # type: ignore[valid-type]
        name="Graph Editor",
        description="Show the Anim Assist menu in the Graph Editor header",
        default=True,
    )
    header_menu_dopesheet: BoolProperty(  # type: ignore[valid-type]
        name="Dope Sheet",
        description="Show the Anim Assist menu in the Dope Sheet header",
        default=True,
    )

    # Feature module toggles.
    enable_selection: BoolProperty(name="Selection Tools", description="Enable keyframe and channel selection tools", default=True)  # type: ignore[valid-type]
    enable_keys: BoolProperty(name="Key Utilities", description="Enable key editing and metadata utilities", default=True)  # type: ignore[valid-type]
    enable_transform: BoolProperty(name="Transform Workflows", description="Enable transform and animation offset workflows", default=True)  # type: ignore[valid-type]
    enable_breakdown: BoolProperty(name="Breakdown Tools", description="Enable breakdown, inbetween, and pose comparison tools", default=True)  # type: ignore[valid-type]
    enable_trajectory: BoolProperty(name="Trajectory Tools", description="Enable trajectory overlays and arc diagnostics", default=True)  # type: ignore[valid-type]
    enable_retime: BoolProperty(name="Retime Tools", description="Enable keyframe timing, ripple, and time-warp tools", default=True)  # type: ignore[valid-type]
    enable_controls: BoolProperty(name="Temp Controls", description="Enable temporary proxy and rig control tools", default=True)  # type: ignore[valid-type]
    enable_matching: BoolProperty(name="Matching Workflows", description="Enable transform matching and IK/FK switching tools", default=True)  # type: ignore[valid-type]
    enable_layers: BoolProperty(name="Animation Layers", description="Enable the animation-layer workflow", default=True)  # type: ignore[valid-type]

    def draw(self, context: bpy.types.Context) -> None:
        layout = self.layout

        box = layout.box()
        box.label(text="General", icon='PREFERENCES')

        row = box.row(align=True)
        row.prop(self, "debug_mode")
        draw_explainer_icon(row, context, "pref.debug_mode")

        row = box.row(align=True)
        row.prop(self, "performance_mode")
        draw_explainer_icon(row, context, "pref.performance_mode")

        row = box.row(align=True)
        row.prop(self, "diagnostics_visible")
        draw_explainer_icon(row, context, "pref.diagnostics_visible")

        # --- EXPLAINER SYSTEM EXTENSION ---
        row = box.row(align=True)
        row.prop(self, "show_explainer_help")
        draw_explainer_icon(row, context, "pref.show_explainer_help")

        row = box.row(align=True)
        row.prop(self, "compact_ui_mode")
        draw_explainer_icon(row, context, "pref.compact_ui_mode")

        box = layout.box()
        box.label(text="Where Anim Assist Appears", icon='WINDOW')
        box.prop(self, "pie_hotkey_enabled")
        col = box.column(heading="Header menu in", align=True)
        col.prop(self, "header_menu_view3d")
        col.prop(self, "header_menu_graph")
        col.prop(self, "header_menu_dopesheet")

        box = layout.box()
        box.label(text="Modules", icon='PACKAGE')
        col = box.column(align=True)
        for key in constants.MODULE_KEYS:
            row = col.row(align=True)
            row.prop(self, f"enable_{key}")
            draw_explainer_icon(row, context, f"pref.enable_{key}")

        box = layout.box()
        box.label(text="Tool Behaviour", icon='TOOL_SETTINGS')

        row = box.row(align=True)
        row.prop(self, "animassist_fast_offset")
        draw_explainer_icon(row, context, "pref.animassist_fast_offset")

        row = box.row(align=True)
        row.prop(self, "animassist_autokey_outside_margins")
        draw_explainer_icon(row, context, "pref.animassist_autokey_outside_margins")

        row = box.row(align=True)
        row.prop(self, "animassist_drag_sensitivity")
        draw_explainer_icon(row, context, "pref.animassist_drag_sensitivity")

        box = layout.box()
        box.label(text="Key Diagnostics", icon='VIEWZOOM')

        row = box.row(align=True)
        row.prop(self, "p2_dense_min_gap")
        draw_explainer_icon(row, context, "pref.p2_dense_min_gap")

        row = box.row(align=True)
        row.prop(self, "p2_redundant_tolerance")
        draw_explainer_icon(row, context, "pref.p2_redundant_tolerance")

        row = box.row(align=True)
        row.prop(self, "p2_spike_ratio")
        draw_explainer_icon(row, context, "pref.p2_spike_ratio")

        box = layout.box()
        box.label(text="Settings", icon='FILE_FOLDER')
        row = box.row(align=True)
        row.operator("anim_assist.export_settings", icon='EXPORT')
        draw_explainer_icon(row, context, "op.anim_assist.export_settings")
        row.operator("anim_assist.import_settings", icon='IMPORT')
        draw_explainer_icon(row, context, "op.anim_assist.import_settings")

        # --- HELP SYSTEM INTEGRATION ---
        draw_help_browser(layout, context)


def get_prefs(context: bpy.types.Context | None = None) -> AA_AddonPreferences | None:
    """Return the addon preferences instance, or *None* if unavailable."""
    ctx = context or bpy.context
    addons = getattr(getattr(ctx, "preferences", None), "addons", None)
    if addons is None:
        return None
    addon = addons.get(constants.ADDON_PACKAGE)
    if addon is None:
        return None
    return getattr(addon, "preferences", None)
