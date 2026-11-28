"""Diagnostics sidebar panel."""

from __future__ import annotations

from ..i18n import T, F

import bpy

from .. import constants
from ..core import cache as cache_mod
from ..core import capabilities as cap_mod
from ..core import runtime as rts_mod
from ..core.context_resolver import AnimContextResolver
# --- EXPLAINER SYSTEM EXTENSION ---
from ..core.help_draw import draw_explainer_icon
from ..core.target_resolver import get_active_target
from ..core.timeline_utils import get_current_frame, get_effective_frame_range


def _get_prefs(context: bpy.types.Context):
    addons = getattr(getattr(context, "preferences", None), "addons", None)
    if addons is None:
        return None
    addon = addons.get(constants.ADDON_PACKAGE)
    if addon is None:
        return None
    return getattr(addon, "preferences", None)


class AA_PT_diagnostics(bpy.types.Panel):
    bl_label = "AnimAssist Diagnostics"
    bl_idname = "AA_PT_diagnostics"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "AnimAssist"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return True

    def draw(self, context: bpy.types.Context) -> None:
        layout = self.layout

        # --- EXPLAINER SYSTEM EXTENSION ---
        header = layout.row(align=True)
        header.label(text=F('v{p0}', p0=f'{constants.ADDON_VERSION_STRING}'), icon="INFO", translate=False)
        draw_explainer_icon(header, context, "panel.aa_pt_diagnostics")

        # Active target ---------------------------------------------------
        box = layout.box()
        row = box.row(align=True)
        row.label(text="Active Target", icon="OBJECT_DATA", text_ctxt='AnimAssist')
        draw_explainer_icon(row, context, "panel.aa_pt_diagnostics")
        target = get_active_target(context)
        if target is not None:
            box.label(text=F('Object: {p0}', p0=f'{target.obj.name}'), translate=False)
            if target.bone_name:
                box.label(text=F('Bone: {p0}', p0=f'{target.bone_name}'), translate=False)
            if target.action:
                box.label(text=F('Action: {p0}', p0=f'{target.action.name}'), translate=False)
                box.label(text=F('FCurves: {p0}', p0=f'{len(target.fcurves)}'), translate=False)
            else:
                box.label(text="Action: None", text_ctxt='AnimAssist')
            if target.is_linked:
                box.label(text="(Linked)", icon="LIBRARY_DATA_DIRECT", text_ctxt='AnimAssist')
        else:
            box.label(text="No active object", text_ctxt='AnimAssist')

        # Timeline --------------------------------------------------------
        box = layout.box()
        box.label(text="Timeline", icon="TIME", text_ctxt='AnimAssist')
        frame_range = get_effective_frame_range(context)
        box.label(text=F('Range: {p0} – {p1}', p0=f'{frame_range[0]}', p1=f'{frame_range[1]}'), translate=False)
        box.label(text=F('Current: {p0}', p0=f'{get_current_frame(context)}'), translate=False)

        # Editors ---------------------------------------------------------
        box = layout.box()
        box.label(text="Editors", icon="WINDOW", text_ctxt='AnimAssist')
        ge = AnimContextResolver.get_graph_editor(context)
        ds = AnimContextResolver.get_dope_sheet(context)
        tl = AnimContextResolver.get_timeline(context)
        row = box.row()
        row.label(text=F('Graph: {p0}', p0="\u2713" if ge else "\u2717"), translate=False)
        row.label(text=F('Dope: {p0}', p0="\u2713" if ds else "\u2717"), translate=False)
        row.label(text=F('Time: {p0}', p0="\u2713" if tl else "\u2717"), translate=False)

        # Capabilities ----------------------------------------------------
        reg = cap_mod.get_registry()
        caps = reg.all_capabilities()
        box = layout.box()
        box.label(text=F('Capabilities ({p0})', p0=f'{len(caps)}'), icon="CHECKMARK", translate=False)
        for name, available in sorted(caps.items()):
            row = box.row()
            row.label(text=name, translate=False)
            row.label(
                text=(T('OK') if available else T('N/A')),
                icon="CHECKMARK" if available else "CANCEL",
            translate=False)

        # Runtime / cache -------------------------------------------------
        box = layout.box()
        box.label(text="Runtime", icon="SYSTEM", text_ctxt='AnimAssist')
        state = rts_mod.get_state()
        box.label(text=F('Tool: {p0}', p0=f"{state.active_tool_id or '(none)'}"), translate=False)
        box.label(text=F('Batch: {p0}', p0=f'{state.is_batch_processing}'), translate=False)
        cache = cache_mod.get_cache()
        box.label(text=F('Selection history: {p0}', p0=f'{len(cache.selection_history)}'), translate=False)
        box.label(text=F('Last tool: {p0}', p0=f"{cache.last_used_tool or '(none)'}"), translate=False)

        last_target = cache.last_active_target
        if last_target:
            tgt_obj = last_target.get("object_name", "")
            tgt_bone = last_target.get("bone_name") or ""
            label = tgt_obj
            if tgt_bone:
                label += f" > {tgt_bone}"
            box.label(text=F('Last target: {p0}', p0=f'{label}'), translate=False)

        # Actions ---------------------------------------------------------
        row = layout.row(align=True)
        row.operator("anim_assist.refresh_diagnostics", icon="FILE_REFRESH")
        draw_explainer_icon(row, context, "op.anim_assist.refresh_diagnostics")
        row.operator("anim_assist.copy_diagnostics", icon="COPYDOWN")
        draw_explainer_icon(row, context, "op.anim_assist.copy_diagnostics")
