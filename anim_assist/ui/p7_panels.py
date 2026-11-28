# --- PROXY AND BAKE CONTROLS ---
"""Sidebar panels for proxy creation and baking in 3D Viewport and Dope Sheet.

Two panels:

1. **Proxy & Bake** — master proxy and bake controls in the 3D Viewport sidebar.
   Uses ``PanelAnatomyMixin`` for Primary -> Scope -> Advanced -> Destructive
   section ordering.

2. **Bake Settings** — lightweight child panel in the Dope Sheet with
   just the bake-range and channel settings.

Both use ``make_editor_variants`` where cross-editor cloning is needed.
"""

from __future__ import annotations

from ..i18n import T, F

import bpy

from ..core.p7_properties import get_p7
from ..core import p7_session as p7s
from . import ui_helpers as uh
from .editor_placement import (
    View3DSidebarPanel,
    DopeSheetSidebarPanel,
    make_editor_variants,
)
from .panel_anatomy import PanelAnatomyMixin


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _p7_available(context: bpy.types.Context) -> bool:
    return get_p7(context) is not None


def _has_active_session(context: bpy.types.Context) -> bool:
    p7 = get_p7(context)
    if p7 is None:
        return False
    return bool(p7.active_session_id) and p7s.get_session(p7.active_session_id) is not None


def _session_info_label(p7, session) -> str:
    return F("Session {session}  |  {objects} obj  {constraints} con",
             session=session.short_id, objects=len(session.created_objects), constraints=len(session.created_constraints))


# ---------------------------------------------------------------------------
# Parent panel: Proxy & Bake  (View3D primary)
# ---------------------------------------------------------------------------

class ANIMASSIST_PT_p7_proxy_bake(PanelAnatomyMixin, View3DSidebarPanel):
    """Proxy creation, baking, and session management controls."""

    bl_category = "Rig"
    bl_order = 30
    bl_idname = "ANIMASSIST_PT_p7_proxy_bake"
    bl_label = "Proxy & Bake"

    # ---- Primary: locator tools, proxy creation, quick bake ----

    def draw_primary(self, context: bpy.types.Context) -> None:
        layout = self.layout
        p7 = get_p7(context)
        if p7 is None:
            layout.label(text="Proxy/bake properties unavailable.", icon="ERROR", text_ctxt='AnimAssist')
            return

        # Session status.
        if _has_active_session(context):
            session = p7s.get_session(p7.active_session_id)
            box = layout.box()
            row = box.row(align=True)
            row.label(text=_session_info_label(p7, session), icon="KEYINGSET", translate=False)
            row.operator("animassist.p7_show_session_info", text="", icon="INFO")
        else:
            layout.label(text="No active session", icon="INFO", text_ctxt='AnimAssist')

        uh.separator(layout)

        # --- Locator Tools ---
        uh.section_header(layout, "Locator Tools", icon="EMPTY_AXIS")

        row = layout.row(align=True)
        uh.explained_op(
            row, context,
            "animassist.p7_create_locator",
            text="Locator",
            icon="EMPTY_AXIS",
            help_id="op.animassist.p7_create_locator",
        )
        uh.explained_op(
            row, context,
            "animassist.p7_create_locator_average",
            text="Average",
            icon="PIVOT_MEDIAN",
            help_id="op.animassist.p7_create_locator_average",
        )
        row = layout.row(align=True)
        uh.explained_op(
            row, context,
            "animassist.p7_create_locator_cursor",
            text="At Cursor",
            icon="PIVOT_CURSOR",
            help_id="op.animassist.p7_create_locator_cursor",
        )

        col2 = layout.column(align=True)
        col2.operator("animassist.p7_parent_locator", text="Parent Locator", icon="LINKED", text_ctxt='AnimAssist')
        col2.operator("animassist.p7_constrain_target_to_locator",
                      text="Target Follows Locator", icon="CONSTRAINT", text_ctxt='AnimAssist')
        col2.operator("animassist.p7_constrain_locator_to_target",
                      text="Locator Follows Target", icon="CONSTRAINT_BONE", text_ctxt='AnimAssist')

        row3 = layout.row(align=True)
        row3.operator("animassist.p7_match_target_to_locator",
                       text="Snap T→L", icon="SNAP_ON", text_ctxt='AnimAssist')
        row3.operator("animassist.p7_match_locator_to_target",
                       text="Snap L→T", icon="SNAP_ON", text_ctxt='AnimAssist')

        row4 = layout.row(align=True)
        row4.operator("animassist.p7_bake_locator_from_target",
                       text="Bake L←T", icon="KEYFRAME_HLT", text_ctxt='AnimAssist')
        row4.operator("animassist.p7_bake_target_from_locator",
                       text="Bake T←L", icon="KEYFRAME_HLT", text_ctxt='AnimAssist')

        uh.separator(layout)

        # --- Proxy Creation ---
        uh.section_header(layout, "Create Proxy", icon="OUTLINER_OB_EMPTY")

        layout.prop(p7, "proxy_type", text="")

        row5 = layout.row(align=True)
        row5.prop(p7, "proxy_size", text="Size", text_ctxt='AnimAssist')
        row5.prop(p7, "proxy_color", text="")

        row6 = layout.row(align=True)
        row6.prop(p7, "auto_constrain", text="Auto", text_ctxt='AnimAssist')
        row6.prop(p7, "proxy_mode", text="")

        uh.explained_op(
            layout, context,
            "animassist.p7_create_proxy",
            text="Create Proxy",
            icon="ADD",
            help_id=f"op.animassist.p7_create_proxy.{p7.proxy_type}",
        )

        row7 = layout.column(align=True)
        uh.explained_op(
            row7, context,
            "animassist.p7_quick_proxy",
            text="Quick Proxy",
            icon="SHADERFX",
            help_id="op.animassist.p7_quick_proxy",
        )
        uh.explained_op(
            row7, context,
            "animassist.p7_temp_pivot",
            text="Pivot",
            icon="PIVOT_INDIVIDUAL",
            help_id="op.animassist.p7_temp_pivot",
        )

        uh.separator(layout)

        # --- Quick Bake ---
        uh.section_header(layout, "Bake", icon="ACTION")

        row8 = layout.row(align=True)
        uh.explained_op(
            row8, context,
            "animassist.p7_smart_bake",
            text="Smart Bake",
            icon="MOD_SIMPLIFY",
            help_id="op.animassist.p7_smart_bake",
        )
        uh.explained_op(
            row8, context,
            "animassist.p7_bake_range",
            text="Bake Range",
            icon="PREVIEW_RANGE",
            help_id="op.animassist.p7_bake_range",
        )

        row9 = layout.row(align=True)
        row9.operator("animassist.p7_bake_preview", text="Preview", icon="PLAY", text_ctxt='AnimAssist')
        row9.operator("animassist.p7_bake_preserve_timing",
                       text="Preserve", icon="TIME", text_ctxt='AnimAssist')
        layout.operator("animassist.p7_bake_selected_channels",
                        text="Selected Channels", icon="ANIM", text_ctxt='AnimAssist')

        row10 = layout.column(align=True)
        row10.operator("animassist.p7_reduce_keys", text="Reduce Keys",
                        icon="IPO_EASE_IN_OUT", text_ctxt='AnimAssist')
        row10.operator("animassist.p7_bake_step", text="Bake Step",
                        icon="KEYTYPE_JITTER_VEC", text_ctxt='AnimAssist')

    # ---- Scope: bake range and channels ----

    def draw_scope(self, context: bpy.types.Context) -> None:
        layout = self.layout
        p7 = get_p7(context)
        if p7 is None:
            return

        body, expanded = uh.subsection(
            layout, context,
            "p7_proxy_bake", "bake_settings",
            "Bake Settings",
            icon="PREFERENCES",
            default_open=False,
        )
        if not expanded:
            return

        body.prop(p7, "bake_range_mode", text="Range", text_ctxt='AnimAssist')

        if p7.bake_range_mode == "CUSTOM":
            row = body.row(align=True)
            row.prop(p7, "bake_range_start", text="Start", text_ctxt='AnimAssist')
            row.prop(p7, "bake_range_end", text="End", text_ctxt='AnimAssist')

        body.prop(p7, "bake_channels", text="Channels", text_ctxt='AnimAssist')
        body.prop(p7, "bake_step", text="Step", text_ctxt='AnimAssist')

        body.separator(factor=0.5)
        body.prop(p7, "smart_bake_tolerance", text="Smart Tolerance", text_ctxt='AnimAssist')
        body.prop(p7, "preserve_timing", text="Preserve Timing", text_ctxt='AnimAssist')

    # ---- Advanced: display, proxy helpers, session tools ----

    def draw_advanced(self, context: bpy.types.Context) -> None:
        layout = self.layout
        p7 = get_p7(context)
        if p7 is None:
            return

        body, expanded = uh.subsection(
            layout, context,
            "p7_proxy_bake", "advanced",
            "Advanced",
            icon="PREFERENCES",
            default_open=False,
        )
        if not expanded:
            return

        # Display controls.
        body.label(text="Display", icon="HIDE_OFF", text_ctxt='AnimAssist')
        row = body.row(align=True)
        row.operator("animassist.p7_toggle_display", text="Toggle Display",
                      icon="HIDE_OFF", text_ctxt='AnimAssist')
        row.operator("animassist.p7_set_proxy_color", text="Color", icon="COLOR", text_ctxt='AnimAssist')

        row2 = body.row(align=True)
        row2.prop(p7, "show_proxy_names", text="Show Names", text_ctxt='AnimAssist')
        row2.operator("animassist.p7_toggle_collection", text="Collection",
                       icon="OUTLINER_COLLECTION", text_ctxt='AnimAssist')

        body.separator(factor=0.5)

        # Proxy helpers.
        body.label(text="Proxy Helpers", icon="TOOL_SETTINGS", text_ctxt='AnimAssist')
        row3 = body.row(align=True)
        row3.operator("animassist.p7_zero_proxy", text="Zero", icon="EMPTY_AXIS", text_ctxt='AnimAssist')
        row3.operator("animassist.p7_recenter_proxy", text="Recenter",
                       icon="SNAP_ON", text_ctxt='AnimAssist')
        row3.operator("animassist.p7_rename_proxy", text="Rename",
                       icon="SORTALPHA", text_ctxt='AnimAssist')

        row4 = body.row(align=True)
        row4.operator("animassist.p7_apply_offset", text="Apply Offset",
                       icon="TRACKING_FORWARDS", text_ctxt='AnimAssist')
        row4.operator("animassist.p7_switch_proxy_mode", text="Mode",
                       icon="ARROW_LEFTRIGHT", text_ctxt='AnimAssist')

        row5 = body.row(align=True)
        row5.operator("animassist.p7_mute_constraints", text="Mute",
                       icon="HIDE_ON", text_ctxt='AnimAssist')
        row5.operator("animassist.p7_lock_target", text="Lock Target",
                       icon="LOCKED", text_ctxt='AnimAssist')

        body.separator(factor=0.5)

        # Batch tools.
        body.label(text="Batch Tools", icon="GROUP", text_ctxt='AnimAssist')
        row6 = body.row(align=True)
        uh.explained_op(
            row6, context,
            "animassist.p7_batch_create_proxies",
            text="Batch Create",
            icon="ADD",
            help_id="op.animassist.p7_batch_create_proxies",
        )
        row6.operator("animassist.p7_bake_selected", text="Bake Sel.",
                       icon="RESTRICT_SELECT_OFF", text_ctxt='AnimAssist')

        row7 = body.row(align=True)
        row7.operator("animassist.p7_mirror_proxy", text="Mirror", icon="MOD_MIRROR", text_ctxt='AnimAssist')
        row7.operator("animassist.p7_check_setup", text="Check Setup",
                       icon="ERROR", text_ctxt='AnimAssist')

        body.separator(factor=0.5)

        # Utility.
        body.label(text="Session", icon="KEYINGSET", text_ctxt='AnimAssist')
        row8 = body.row(align=True)
        row8.operator("animassist.p7_list_sessions", text="List",
                       icon="LINENUMBERS_ON", text_ctxt='AnimAssist')
        row8.operator("animassist.p7_reconnect_session", text="Reconnect",
                       icon="RECOVER_LAST", text_ctxt='AnimAssist')
        row8.operator("animassist.p7_export_session", text="Export",
                       icon="EXPORT", text_ctxt='AnimAssist')

        body.separator(factor=0.5)
        body.operator("animassist.p7_validate_session", text="Validate Session",
                       icon="CHECKMARK", text_ctxt='AnimAssist')

    # ---- Destructive: cleanup operations ----

    def draw_destructive(self, context: bpy.types.Context) -> None:
        layout = self.layout
        p7 = get_p7(context)
        if p7 is None:
            return

        body = uh.danger_box(layout, context, label="Cleanup")

        row = body.column(align=True)
        uh.explained_op(
            row, context,
            "animassist.p7_cleanup_session",
            text="Cleanup Session",
            icon="TRASH",
            help_id="op.animassist.p7_cleanup_session",
        )
        row.operator("animassist.p7_remove_proxy", text="Remove Proxy", icon="X", text_ctxt='AnimAssist')

        row2 = body.row(align=True)
        row2.operator("animassist.p7_remove_constraints", text="Strip Constraints",
                       icon="UNLINKED", text_ctxt='AnimAssist')

        body.separator(factor=0.5)

        row3 = body.column(align=True)
        uh.explained_op(
            row3, context,
            "animassist.p7_one_click_proxy_bake",
            text="1-Click Proxy+Bake",
            icon="PLAY",
            help_id="op.animassist.p7_one_click_proxy_bake",
        )
        uh.explained_op(
            row3, context,
            "animassist.p7_one_click_cleanup",
            text="1-Click Cleanup",
            icon="PLAY",
            help_id="op.animassist.p7_one_click_cleanup",
        )

        body.separator(factor=0.5)
        row4 = body.column(align=True)
        row4.operator("animassist.p7_auto_cleanup", text="Auto Cleanup",
                       icon="FILE_REFRESH", text_ctxt='AnimAssist')
        row4.operator("animassist.p7_cleanup_all", text="Purge All", icon="CANCEL", text_ctxt='AnimAssist')

        # Safety-hatch operators for session recovery.
        body.separator(factor=0.5)
        row5 = body.column(align=True)
        row5.operator("animassist.p7_purge_artifacts", text="Purge Artifacts",
                       icon="ERROR", text_ctxt='AnimAssist')
        row5.operator("animassist.p7_recover_session", text="Recover",
                       icon="RECOVER_LAST", text_ctxt='AnimAssist')


# ---------------------------------------------------------------------------
# Dope Sheet panel: lightweight bake settings
# ---------------------------------------------------------------------------

class ANIMASSIST_PT_p7_bake_ds(DopeSheetSidebarPanel):
    """Bake range and channel settings in the Dope Sheet."""

    bl_category = "Rig"
    bl_order = 20
    bl_idname = "ANIMASSIST_PT_p7_bake_ds"
    bl_label = "Bake"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context: bpy.types.Context) -> None:
        layout = self.layout
        p7 = get_p7(context)
        if p7 is None:
            layout.label(text="Proxy/bake properties unavailable.", icon="ERROR", text_ctxt='AnimAssist')
            return

        # Session status.
        if _has_active_session(context):
            session = p7s.get_session(p7.active_session_id)
            layout.label(text=_session_info_label(p7, session), icon="KEYINGSET", translate=False)

        range_label=T({'SCENE':'Scene','ACTION':'Action','CUSTOM':'Custom','SELECTION':'Selection','PREVIEW':'Preview'}.get(p7.bake_range_mode,p7.bake_range_mode))
        layout.label(text=F('Range: {p0}', p0=range_label), translate=False)
        for op, label in (("p7_smart_bake", "Smart Bake"), ("p7_bake_range", "Bake Range"), ("p7_bake_preview", "Preview Bake")):
            layout.operator(f"animassist.{op}", text=label, text_ctxt='AnimAssist')
        header, body = layout.panel("aa_key_bake_options", default_closed=True)
        header.label(text="Bake Options", text_ctxt='AnimAssist')
        if body:
            body.prop(p7, "bake_range_mode", text="Range", text_ctxt='AnimAssist')
            if p7.bake_range_mode == "CUSTOM":
                body.prop(p7, "bake_range_start", text="Start", text_ctxt='AnimAssist')
                body.prop(p7, "bake_range_end", text="End", text_ctxt='AnimAssist')
            body.prop(p7, "bake_channels", text="Channels", text_ctxt='AnimAssist')
            body.prop(p7, "bake_step", text="Step", text_ctxt='AnimAssist')
            body.prop(p7, "smart_bake_tolerance", text="Tolerance", text_ctxt='AnimAssist')


# ---------------------------------------------------------------------------
# Cross-editor variants
# ---------------------------------------------------------------------------

# The View3D panel is the primary location — no clone needed.
# Build a Graph Editor variant of the Dope Sheet bake panel.
_GE_BAKE = make_editor_variants(
    ANIMASSIST_PT_p7_bake_ds, ["GRAPH_EDITOR"]
)


CLASSES: tuple[type, ...] = (
    ANIMASSIST_PT_p7_proxy_bake,
    ANIMASSIST_PT_p7_bake_ds,
    *(_GE_BAKE or ()),
)
