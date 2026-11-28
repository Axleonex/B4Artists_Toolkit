"""Diagnostics operators: refresh and copy-to-clipboard."""

from __future__ import annotations

from ..i18n import T, F

import bpy

from .. import constants
from ..core import cache as cache_mod
from ..core import capabilities as cap_mod
from ..core import runtime as rts_mod
from ..core.context_resolver import AnimContextResolver
from ..core.helpers import redraw_notify
from ..core.logging import get_logger
from ..core.target_resolver import get_active_target

_log = get_logger(__name__)


def _build_diagnostics_text(context: bpy.types.Context) -> str:
    lines: list[str] = []
    lines.append(F('Anim Assist v{p0}', p0=f'{constants.ADDON_VERSION_STRING}'))
    lines.append(F('Blender {p0}', p0=f'{bpy.app.version_string}'))
    lines.append("")

    target = get_active_target(context)
    if target is not None:
        lines.append(F('Active Object: {p0}', p0=f'{target.obj.name}'))
        if target.bone_name:
            lines.append(F('Active Bone: {p0}', p0=f'{target.bone_name}'))
        if target.action:
            lines.append(
                F('Action: {p0} ({p1} fcurves)', p0=f'{target.action.name}', p1=f'{len(target.fcurves)}')
            )
        else:
            lines.append(T('Action: None'))
        lines.append(F('Linked: {p0}', p0=f'{target.is_linked}'))
    else:
        lines.append(T('Active Object: None'))

    lines.append("")

    ge = AnimContextResolver.get_graph_editor(context)
    ds = AnimContextResolver.get_dope_sheet(context)
    tl = AnimContextResolver.get_timeline(context)
    lines.append(F('Graph Editor: {p0}', p0=f"{(T('found') if ge else T('not found'))}"))
    lines.append(F('Dope Sheet: {p0}', p0=f"{(T('found') if ds else T('not found'))}"))
    lines.append(F('Timeline: {p0}', p0=f"{(T('found') if tl else T('not found'))}"))

    lines.append("")

    reg = cap_mod.get_registry()
    caps = reg.all_capabilities()
    lines.append(F('Capabilities ({p0}):', p0=f'{len(caps)}'))
    for name, available in sorted(caps.items()):
        lines.append(F('  {p0}: {p1}', p0=f'{name}', p1=f"{(T('OK') if available else T('UNAVAILABLE'))}"))

    lines.append("")

    cache = cache_mod.get_cache()
    lines.append(F('Selection history entries: {p0}', p0=f'{len(cache.selection_history)}'))
    lines.append(F('Last used tool: {p0}', p0=f"{cache.last_used_tool or T('(none)')}"))

    state = rts_mod.get_state()
    lines.append(F('Active tool: {p0}', p0=f"{state.active_tool_id or T('(none)')}"))
    lines.append(F('Batch processing: {p0}', p0=f'{state.is_batch_processing}'))

    return "\n".join(lines)


class AA_OT_copy_diagnostics(bpy.types.Operator):
    bl_idname = "anim_assist.copy_diagnostics"
    bl_label = "Copy Diagnostics"
    bl_description = "Copy diagnostics information to clipboard"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return getattr(context, "window_manager", None) is not None

    def execute(self, context: bpy.types.Context):
        wm = getattr(context, "window_manager", None)
        if wm is None:
            self.report({"ERROR"}, T('Window manager not available. Run this from the Bforartists interface, not a background script'))
            return {"CANCELLED"}

        try:
            text = _build_diagnostics_text(context)
        except Exception:
            _log.exception("Failed to build diagnostics text")
            self.report({"ERROR"}, T('Could not collect diagnostics. Details are in the system console (Window > Toggle System Console)'))
            return {"CANCELLED"}

        wm.clipboard = text
        self.report({"INFO"}, T('Diagnostics copied to clipboard'))
        return {"FINISHED"}


class AA_OT_refresh_diagnostics(bpy.types.Operator):
    bl_idname = "anim_assist.refresh_diagnostics"
    bl_label = "Refresh Diagnostics"
    bl_description = "Force refresh diagnostics display"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return getattr(context, "screen", None) is not None

    def execute(self, context: bpy.types.Context):
        redraw_notify(context)
        self.report({"INFO"}, T('Diagnostics refreshed'))
        return {"FINISHED"}