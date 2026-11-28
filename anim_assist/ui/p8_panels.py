# --- MATCHING AND SPACE SWITCHING PANELS ---
"""Sidebar panels for IK/FK matching, space switching, and animation compensation.

Panel placement:
    Dope Sheet — primary home (keyframe-centric workflow)
    Graph Editor — lightweight variant via make_editor_variants()
    View 3D — secondary for visual match tools (viewport-oriented)

Uses PanelAnatomyMixin section hooks:
    draw_primary   — match buttons, quick actions
    draw_scope     — channel filters, axis toggles, offset mode
    draw_advanced  — switch config, detection, batch, presets, history
    draw_destructive — (none; no destructive actions)
"""

from __future__ import annotations

from ..i18n import T, F

import bpy

from ..core.p8_properties import get_p8
from ..ui import ui_helpers as uh
from ..ui.panel_anatomy import PanelAnatomyMixin
from ..ui.editor_placement import (
    DopeSheetSidebarPanel,
    View3DSidebarPanel,
    make_editor_variants,
)


# ---------------------------------------------------------------------------
# Availability helpers
# ---------------------------------------------------------------------------

def _p8_available(context: bpy.types.Context) -> bool:
    return get_p8(context) is not None


def _has_active_object(context: bpy.types.Context) -> bool:
    return context.active_object is not None


# ---------------------------------------------------------------------------
# Main panel — Dope Sheet
# ---------------------------------------------------------------------------

class ANIMASSIST_PT_p8_matching(PanelAnatomyMixin, DopeSheetSidebarPanel):
    """IK/FK matching and space switching controls for animation compensation."""

    bl_category = "Rig"
    bl_order = 10
    bl_idname = "ANIMASSIST_PT_p8_matching"
    bl_label = "Match & Switch"

    # ── Primary: match buttons, quick actions ─────────────────────────

    def draw_primary(self, context: bpy.types.Context) -> None:
        layout = self.layout
        p8 = get_p8(context)
        if not _p8_available(context) or not _has_active_object(context):
            uh.draw_context_warning(layout, "Select an object or bone to use matching tools")
            return

        # ── Quick match ──
        uh.section_header(layout, "Quick Match", icon="SNAP_ON")
        # Most match buttons need a second selected object; without one they
        # grey out silently, so say what they are waiting for.
        if len(getattr(context, "selected_objects", None) or ()) < 2:
            layout.label(text="Select target, then this object", icon="INFO", text_ctxt='AnimAssist')
        uh.explained_op(
            layout, context,
            "animassist.p8_quick_match",
            text="Quick Match", icon="SNAP_ON",
            help_id="op.animassist.p8_quick_match",
        )

        row = layout.row(align=True)
        uh.explained_op(
            row, context,
            "animassist.p8_match_to_world",
            text="World", icon="WORLD",
            help_id="op.animassist.p8_match_to_world",
        )
        uh.explained_op(
            row, context,
            "animassist.p8_match_to_parent",
            text="Parent", icon="BONE_DATA",
            help_id="op.animassist.p8_match_to_parent",
        )
        uh.explained_op(
            row, context,
            "animassist.p8_match_to_target",
            text="Target", icon="TRACKER",
            help_id="op.animassist.p8_match_to_target",
        )

        uh.separator(layout)

        # ── Channel-filtered match ──
        uh.section_header(layout, "Channel Match", icon="CON_TRANSLIKE")
        row = layout.row(align=True)
        uh.explained_op(
            row, context,
            "animassist.p8_match_location",
            text="Loc", icon="CON_LOCLIKE",
            help_id="op.animassist.p8_match_location",
        )
        uh.explained_op(
            row, context,
            "animassist.p8_match_rotation",
            text="Rot", icon="CON_ROTLIKE",
            help_id="op.animassist.p8_match_rotation",
        )
        uh.explained_op(
            row, context,
            "animassist.p8_match_scale",
            text="Scale", icon="CON_SIZELIKE",
            help_id="op.animassist.p8_match_scale",
        )

        row = layout.row(align=True)
        uh.explained_op(
            row, context,
            "animassist.p8_match_trs",
            text="Full TRS",
            help_id="op.animassist.p8_match_trs",
        )
        uh.explained_op(
            row, context,
            "animassist.p8_match_axis_filtered",
            text="Axis Filter",
            help_id="op.animassist.p8_match_axis_filtered",
        )

        row = layout.row(align=True)
        uh.explained_op(
            row, context,
            "animassist.p8_match_with_offset",
            text="With Offset",
            help_id="op.animassist.p8_match_with_offset",
        )
        uh.explained_op(
            row, context,
            "animassist.p8_match_without_offset",
            text="No Offset",
            help_id="op.animassist.p8_match_without_offset",
        )

        uh.separator(layout)

        # ── Space switch compensation ──
        uh.section_header(layout, "Space Switch", icon="CON_CHILDOF")
        row = layout.row(align=True)
        uh.explained_op(
            row, context,
            "animassist.p8_compensate_single",
            text="Compensate", icon="KEYFRAME",
            help_id="op.animassist.p8_compensate_single",
        )
        uh.explained_op(
            row, context,
            "animassist.p8_compensate_multi",
            text="Multi-Frame", icon="KEYFRAME_HLT",
            help_id="op.animassist.p8_compensate_multi",
        )

        row = layout.row(align=True)
        uh.explained_op(
            row, context,
            "animassist.p8_switch_enum",
            text="Enum",
            help_id="op.animassist.p8_switch_enum",
        )
        uh.explained_op(
            row, context,
            "animassist.p8_switch_bool",
            text="Bool",
            help_id="op.animassist.p8_switch_bool",
        )
        uh.explained_op(
            row, context,
            "animassist.p8_switch_influence",
            text="Influence",
            help_id="op.animassist.p8_switch_influence",
        )

    # ── Scope: channel filters, axis toggles ──────────────────────────

    def draw_scope(self, context: bpy.types.Context) -> None:
        layout = self.layout
        p8 = get_p8(context)
        if p8 is None:
            return

        body, expanded = uh.subsection(
            layout, context,
            "p8_matching", "filters",
            "Match Settings",
            icon="FILTER",
            default_open=True,
        )
        if not expanded:
            return

        uh.explained_prop(
            body, context, p8, "match_channels", text="Channels",
            help_id="prop.p8_match_channels",
        )

        row = body.row(align=True)
        row.label(text="Axes:", text_ctxt='AnimAssist')
        row.prop(p8, "match_axis", text="")
        uh.draw_explainer_icon(row, context, "prop.p8_match_axis")

        uh.explained_prop(
            body, context, p8, "maintain_offset",
            help_id="op.animassist.p8_match_with_offset",
        )

        uh.separator(body)

        # Compensation settings
        uh.explained_prop(
            body, context, p8, "auto_compensate",
            help_id="prop.p8_auto_compensate",
        )
        uh.explained_prop(
            body, context, p8, "auto_key_switch",
            help_id="prop.p8_auto_key_switch",
        )
        uh.explained_prop(
            body, context, p8, "respect_locks",
            help_id="prop.p8_respect_locks",
        )
        uh.explained_prop(
            body, context, p8, "respect_drivers",
            help_id="prop.p8_respect_drivers",
        )

    # ── Advanced: switch config, detection, batch, presets, history ────

    def draw_advanced(self, context: bpy.types.Context) -> None:
        layout = self.layout
        p8 = get_p8(context)
        if p8 is None:
            return

        # ── Switch Configuration ──
        body, expanded = uh.subsection(
            layout, context,
            "p8_matching", "switch_config",
            "Switch Configuration",
            icon="PROPERTIES",
            default_open=False,
        )
        if expanded:
            body.prop(p8, "switch_bone_name", text="Bone", text_ctxt='AnimAssist')
            body.prop(p8, "switch_prop_path", text="Property", text_ctxt='AnimAssist')
            body.prop(p8, "switch_kind", text="Type", text_ctxt='AnimAssist')
            body.prop(p8, "switch_new_value", text="Value", text_ctxt='AnimAssist')

            uh.separator(body)
            body.prop(p8, "comp_range", text="Range", text_ctxt='AnimAssist')
            if p8.comp_range == "CUSTOM":
                row = body.row(align=True)
                row.prop(p8, "comp_range_start", text="Start", text_ctxt='AnimAssist')
                row.prop(p8, "comp_range_end", text="End", text_ctxt='AnimAssist')

            uh.separator(body)
            row = body.row(align=True)
            uh.explained_op(
                row, context,
                "animassist.p8_bake_switch_range",
                text="Bake Range", icon="RENDER_ANIMATION",
                help_id="op.animassist.p8_bake_switch_range",
            )
            uh.explained_op(
                row, context,
                "animassist.p8_bake_switch_preview",
                text="Bake Preview", icon="RENDER_ANIMATION",
                help_id="op.animassist.p8_bake_switch_preview",
            )

            uh.separator(body)
            uh.explained_op(
                body, context,
                "animassist.p8_toggle_preview",
                text="Switch Preview" if not p8.switch_preview else "Exit Preview",
                icon="HIDE_OFF" if not p8.switch_preview else "HIDE_ON",
                help_id="op.animassist.p8_toggle_preview",
            )
            uh.explained_op(
                body, context,
                "animassist.p8_restore_switch",
                text="Restore Previous", icon="LOOP_BACK",
                help_id="op.animassist.p8_restore_switch",
            )

        # ── Rig Detection ──
        body, expanded = uh.subsection(
            layout, context,
            "p8_matching", "detection",
            "Rig Detection",
            icon="VIEWZOOM",
            default_open=False,
        )
        if expanded:
            uh.explained_op(
                body, context,
                "animassist.p8_detect_all",
                text="Detect All Patterns", icon="VIEWZOOM",
                help_id="op.animassist.p8_detect_all",
            )
            row = body.row(align=True)
            uh.explained_op(
                row, context,
                "animassist.p8_detect_space_enums",
                text="Enums",
                help_id="op.animassist.p8_detect_space_enums",
            )
            uh.explained_op(
                row, context,
                "animassist.p8_detect_influence_patterns",
                text="Influence",
                help_id="op.animassist.p8_detect_influence_patterns",
            )

            from ..operators.p8_detect_ops import get_cached_patterns
            patterns = get_cached_patterns()
            if patterns:
                body.label(text=F('{p0} pattern(s) found:', p0=f'{len(patterns)}'), translate=False)
                body.prop(p8, "detected_pattern_index", text="Select", text_ctxt='AnimAssist')
                uh.explained_op(
                    body, context,
                    "animassist.p8_apply_detected_pattern",
                    text="Apply Pattern", icon="IMPORT",
                    help_id="op.animassist.p8_apply_detected_pattern",
                )

        # ── Batch & Advanced Matching ──
        body, expanded = uh.subsection(
            layout, context,
            "p8_matching", "batch",
            "Batch & Advanced",
            icon="GROUP",
            default_open=False,
        )
        if expanded:
            uh.explained_op(
                body, context,
                "animassist.p8_batch_switch",
                text="Batch Switch Selected", icon="GROUP",
                help_id="op.animassist.p8_batch_switch",
            )
            uh.explained_op(
                body, context,
                "animassist.p8_match_selected_to_active",
                text="Match Selected → Active",
                help_id="op.animassist.p8_match_selected_to_active",
            )

            row = body.row(align=True)
            uh.explained_op(
                row, context,
                "animassist.p8_match_visual_matrix",
                text="Visual", icon="HIDE_OFF",
                help_id="op.animassist.p8_match_visual_matrix",
            )
            uh.explained_op(
                row, context,
                "animassist.p8_match_local_matrix",
                text="Local", icon="ORIENTATION_LOCAL",
                help_id="op.animassist.p8_match_local_matrix",
            )
            uh.explained_op(
                body, context,
                "animassist.p8_match_opposite",
                text="Match Opposite Side", icon="MOD_MIRROR",
                help_id="op.animassist.p8_match_opposite",
            )

            uh.separator(body)
            uh.explained_op(
                body, context,
                "animassist.p8_switch_marker",
                text="Place Switch Marker", icon="MARKER",
                help_id="op.animassist.p8_switch_marker",
            )
            uh.explained_op(
                body, context,
                "animassist.p8_repeat_last_switch",
                text="Repeat Last Switch", icon="FILE_REFRESH",
                help_id="op.animassist.p8_repeat_last_switch",
            )

        # ── Contact Preservation ──
        body, expanded = uh.subsection(
            layout, context,
            "p8_matching", "contact",
            "Contact Preservation",
            icon="BONE_DATA",
            default_open=False,
        )
        if expanded:
            uh.explained_prop(
                body, context, p8, "contact_preserve",
                help_id="prop.p8_contact_preserve",
            )
            uh.explained_prop(
                body, context, p8, "contact_mask",
                text="Mask",
                help_id="prop.p8_contact_mask",
            )
            uh.explained_op(
                body, context,
                "animassist.p8_contact_mask_from_selection",
                text="Mask from Selection", icon="RESTRICT_SELECT_OFF",
                help_id="op.animassist.p8_contact_mask_from_selection",
            )
            uh.explained_op(
                body, context,
                "animassist.p8_contact_preserve_match",
                text="Contact Match", icon="SNAP_ON",
                help_id="op.animassist.p8_contact_preserve_match",
            )

        # ── Switch Presets ──
        body, expanded = uh.subsection(
            layout, context,
            "p8_matching", "presets",
            "Switch Presets",
            icon="PRESET",
            default_open=False,
        )
        if expanded:
            body.prop(p8, "switch_preset_name", text="Name", text_ctxt='AnimAssist')
            row = body.row(align=True)
            uh.explained_op(
                row, context,
                "animassist.p8_save_switch_preset",
                text="Save", icon="FILE_TICK",
                help_id="op.animassist.p8_save_switch_preset",
            )
            uh.explained_op(
                row, context,
                "animassist.p8_load_switch_preset",
                text="Load", icon="FILE_FOLDER",
                help_id="op.animassist.p8_load_switch_preset",
            )
            uh.explained_op(
                row, context,
                "animassist.p8_delete_switch_preset",
                text="Delete", icon="TRASH",
                help_id="op.animassist.p8_delete_switch_preset",
            )

        # ── History & Navigation ──
        body, expanded = uh.subsection(
            layout, context,
            "p8_matching", "history",
            "Switch History",
            icon="TIME",
            default_open=False,
        )
        if expanded:
            row = body.row(align=True)
            uh.explained_op(
                row, context,
                "animassist.p8_nav_prev_switch",
                text="", icon="TRIA_LEFT",
                help_id="op.animassist.p8_nav_prev_switch",
            )
            uh.explained_op(
                row, context,
                "animassist.p8_nav_next_switch",
                text="", icon="TRIA_RIGHT",
                help_id="op.animassist.p8_nav_next_switch",
            )
            uh.explained_op(
                row, context,
                "animassist.p8_clear_history",
                text="Clear", icon="X",
                help_id="op.animassist.p8_clear_history",
            )

        # ── IK Chain Resolver ──
        body, expanded = uh.subsection(
            layout, context,
            "p8_matching", "chain_resolver",
            "IK Chain Resolver",
            icon="LINKED",
            default_open=False,
        )
        if expanded:
            # Detection buttons
            row = body.row(align=True)
            uh.explained_op(
                row, context,
                "animassist.p8_detect_chains",
                text="Detect All", icon="VIEWZOOM",
                help_id="op.animassist.p8_detect_chains",
            )
            uh.explained_op(
                row, context,
                "animassist.p8_detect_chain_for_bone",
                text="From Bone", icon="BONE_DATA",
                help_id="op.animassist.p8_detect_chain_for_bone",
            )

            row = body.row(align=True)
            uh.explained_op(
                row, context,
                "animassist.p8_find_bone_chains",
                text="Involving Bone", icon="GROUP_BONE",
                help_id="op.animassist.p8_find_bone_chains",
            )
            uh.explained_op(
                row, context,
                "animassist.p8_chain_summary",
                text="Summary", icon="INFO",
                help_id="op.animassist.p8_chain_summary",
            )

            uh.separator(body)

            # Settings
            uh.explained_prop(
                body, context, p8, "chain_include_muted",
                help_id="prop.p8_chain_include_muted",
            )
            uh.explained_prop(
                body, context, p8, "chain_highlight_members",
                help_id="prop.p8_chain_highlight_members",
            )
            uh.explained_prop(
                body, context, p8, "chain_auto_detect",
                help_id="prop.p8_chain_auto_detect",
            )

            # Chain results (populated after detection)
            from ..operators.p8_chain_ops import get_cached_chains
            chains = get_cached_chains()
            if chains:
                uh.separator(body)
                body.label(
                    text=F('{p0} chain(s) detected:', p0=f'{len(chains)}'),
                    icon="LINKED",
                translate=False)

                # Navigation
                row = body.row(align=True)
                nav_prev = row.operator(
                    "animassist.p8_chain_nav",
                    text="", icon="TRIA_LEFT",
                )
                nav_prev.direction = -1

                idx = p8.chain_selected_index if p8 else 0
                idx = min(idx, len(chains) - 1)
                chain = chains[idx]
                row.label(
                    text=F('{p0}/{p1}: {p2} → {p3}', p0=f'{idx + 1}', p1=f'{len(chains)}', p2=f'{chain.tip_bone}', p3=f'{chain.root_bone}'),
                translate=False)

                nav_next = row.operator(
                    "animassist.p8_chain_nav",
                    text="", icon="TRIA_RIGHT",
                )
                nav_next.direction = 1

                # Chain detail box
                box = body.box()
                col = box.column(align=True)
                col.label(text=F('Tip: {p0}', p0=f'{chain.tip_bone}'), icon="PMARKER_ACT", translate=False)
                col.label(text=F('Root: {p0}', p0=f'{chain.root_bone}'), icon="PMARKER", translate=False)
                col.label(text=F('Bones: {p0}', p0=f'{chain.length}'), icon="BONE_DATA", translate=False)
                col.label(
                    text=F('Active: {p0}', p0=T('Yes') if chain.is_active else T('No')),
                    icon="CHECKMARK" if chain.is_active else "X",
                translate=False)
                ci = chain.constraint_info
                if ci.target_object:
                    col.label(
                        text=F("Target: {target}", target=ci.target_object + (f".{ci.target_bone}" if ci.target_bone else "")),
                        icon="TRACKER",
                    translate=False)
                if ci.pole_object:
                    col.label(
                        text=F("Pole: {target}", target=ci.pole_object + (f".{ci.pole_bone}" if ci.pole_bone else "")),
                        icon="EMPTY_ARROWS",
                    translate=False)
                col.label(
                    text=F('Influence: {p0}', p0=f'{ci.influence:.2f}'),
                    icon="CON_KINEMATIC",
                translate=False)

                # Member list
                if len(chain.bone_names) <= 12:
                    col.label(text="Members:", icon="GROUP_BONE", text_ctxt='AnimAssist')
                    for bname in chain.bone_names:
                        col.label(text=F('  {p0}', p0=f'{bname}'), translate=False)

                uh.separator(body)

                # Action buttons
                row = body.row(align=True)
                uh.explained_op(
                    row, context,
                    "animassist.p8_select_chain_bones",
                    text="Select Chain", icon="RESTRICT_SELECT_OFF",
                    help_id="op.animassist.p8_select_chain_bones",
                )
                uh.explained_op(
                    row, context,
                    "animassist.p8_chain_to_match",
                    text="Chain → Match", icon="SNAP_ON",
                    help_id="op.animassist.p8_chain_to_match",
                )

            # Cache management
            uh.separator(body)
            uh.explained_op(
                body, context,
                "animassist.p8_invalidate_chain_cache",
                text="Clear Cache", icon="FILE_REFRESH",
                help_id="op.animassist.p8_invalidate_chain_cache",
            )

        # ── Reports & Diagnostics ──
        body, expanded = uh.subsection(
            layout, context,
            "p8_matching", "reports",
            "Reports",
            icon="INFO",
            default_open=False,
        )
        if expanded:
            uh.explained_op(
                body, context,
                "animassist.p8_compensation_report",
                text="Compensation Report", icon="TEXT",
                help_id="op.animassist.p8_compensation_report",
            )
            uh.explained_op(
                body, context,
                "animassist.p8_unsupported_warning",
                text="Check Setup", icon="ERROR",
                help_id="op.animassist.p8_unsupported_warning",
            )
            uh.explained_op(
                body, context,
                "animassist.p8_debug_diagnostics",
                text="Debug Diagnostics", icon="CONSOLE",
                help_id="op.animassist.p8_debug_diagnostics",
            )


# ---------------------------------------------------------------------------
# View 3D lightweight panel (visual match tools)
# ---------------------------------------------------------------------------

class ANIMASSIST_PT_p8_match_v3d(PanelAnatomyMixin, View3DSidebarPanel):
    """Visual matching controls for transform operations in the 3D Viewport."""

    bl_category = "Rig"
    bl_order = 40
    bl_idname = "ANIMASSIST_PT_p8_match_v3d"
    bl_label = "Transform Match"

    def draw_primary(self, context: bpy.types.Context) -> None:
        layout = self.layout
        p8 = get_p8(context)
        if not _has_active_object(context):
            uh.draw_context_warning(layout, "Select an object or bone")
            return

        uh.section_header(layout, "Quick Match", icon="SNAP_ON")
        uh.explained_op(
            layout, context,
            "animassist.p8_quick_match",
            text="Quick Match", icon="SNAP_ON",
            help_id="op.animassist.p8_quick_match",
        )

        row = layout.row(align=True)
        uh.explained_op(
            row, context,
            "animassist.p8_match_to_world",
            text="World", icon="WORLD",
            help_id="op.animassist.p8_match_to_world",
        )
        uh.explained_op(
            row, context,
            "animassist.p8_match_to_parent",
            text="Parent", icon="BONE_DATA",
            help_id="op.animassist.p8_match_to_parent",
        )
        uh.explained_op(
            row, context,
            "animassist.p8_match_to_target",
            text="Target", icon="TRACKER",
            help_id="op.animassist.p8_match_to_target",
        )

        uh.separator(layout)

        row = layout.row(align=True)
        uh.explained_op(
            row, context,
            "animassist.p8_match_location",
            text="Loc", icon="CON_LOCLIKE",
            help_id="op.animassist.p8_match_location",
        )
        uh.explained_op(
            row, context,
            "animassist.p8_match_rotation",
            text="Rot", icon="CON_ROTLIKE",
            help_id="op.animassist.p8_match_rotation",
        )
        uh.explained_op(
            row, context,
            "animassist.p8_match_scale",
            text="Scale", icon="CON_SIZELIKE",
            help_id="op.animassist.p8_match_scale",
        )

        uh.explained_op(
            layout, context,
            "animassist.p8_match_opposite",
            text="Match Opposite Side", icon="MOD_MIRROR",
            help_id="op.animassist.p8_match_opposite",
        )

    def draw_scope(self, context: bpy.types.Context) -> None:
        layout = self.layout
        p8 = get_p8(context)
        if p8 is None:
            return

        body, expanded = uh.subsection(
            layout, context,
            "p8_match_v3d", "settings",
            "Settings",
            icon="FILTER",
            default_open=False,
        )
        if not expanded:
            return

        uh.explained_prop(body, context, p8, "match_channels", text="Channels",
                          help_id="prop.p8_match_channels")
        row = body.row(align=True)
        row.label(text="Axes:", text_ctxt='AnimAssist')
        row.prop(p8, "match_axis", text="")
        uh.explained_prop(body, context, p8, "maintain_offset",
                          help_id="op.animassist.p8_match_with_offset")
        uh.explained_prop(body, context, p8, "respect_locks",
                          help_id="prop.p8_respect_locks")


# ---------------------------------------------------------------------------
# Cross-editor variants — Graph Editor
# ---------------------------------------------------------------------------

_DS_CLASSES: tuple[type, ...] = (
    ANIMASSIST_PT_p8_matching,
)

_GE_VARIANTS = make_editor_variants(
    ANIMASSIST_PT_p8_matching,
    ["GRAPH_EDITOR"],
)

CLASSES: tuple[type, ...] = (
    *_DS_CLASSES,
    ANIMASSIST_PT_p8_match_v3d,
    *(_GE_VARIANTS or ()),
)
