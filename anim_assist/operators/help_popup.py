# --- EXPLAINER SYSTEM EXTENSION ---
"""Modal popup operator that renders a HelpEntry."""

from __future__ import annotations

from ..i18n import T, F, wrap_text

import bpy
from bpy.props import StringProperty
from bpy.types import Operator

from .. import constants
from ..core import help_registry
from ..core.logging import get_logger

_log = get_logger(__name__)

_WRAP_WIDTH = 64


class ANIMASSIST_OT_show_help_popup(Operator):
    """Display the long-form help description for an Anim Assist control."""

    bl_idname = "anim_assist.show_help_popup"
    bl_label = "Anim Assist Help"
    bl_description = "Show a detailed explanation for this control"
    bl_options = {"REGISTER", "INTERNAL"}

    help_id: StringProperty(  # type: ignore[valid-type]
        name="Help ID",
        description="Unique id of the help entry to display",
        default="",
     translation_context='AnimAssist')

    def invoke(self, context: bpy.types.Context, event: bpy.types.Event):
        entry = help_registry.get_help(self.help_id)
        if entry is None:
            self.report({"WARNING"}, F("No help entry for '{p0}'", p0=f'{self.help_id}'))
            return {"CANCELLED"}
        return context.window_manager.invoke_props_dialog(
            self, width=constants.HELP_POPUP_WIDTH
        )

    def draw(self, context: bpy.types.Context) -> None:
        entry = help_registry.get_help(self.help_id)
        layout = self.layout
        if entry is None:
            layout.label(text="Help entry not found", icon="ERROR", text_ctxt='AnimAssist')
            return

        header = layout.box()
        header.label(text=T(entry.label), icon=constants.HELP_ICON, translate=False)
        meta_row = header.row(align=True)
        meta_row.label(text=F("Category: {category}", category=T(entry.category)), translate=False)
        meta_row.label(text=F("Phase: {phase}", phase=entry.phase), translate=False)

        tip = layout.box()
        tip.label(text="Summary", icon="INFO", text_ctxt='AnimAssist')
        for line in wrap_text(T(entry.tooltip), width=_WRAP_WIDTH) or [""]:
            tip.label(text=line, translate=False)

        body = layout.box()
        body.label(text="Details", icon="TEXT", text_ctxt='AnimAssist')
        for paragraph in T(entry.description).split("\n\n"):
            paragraph = paragraph.strip()
            if not paragraph:
                body.separator()
                continue
            for line in wrap_text(paragraph, width=_WRAP_WIDTH):
                body.label(text=line, translate=False)
            body.separator(factor=0.4)

    def execute(self, context: bpy.types.Context):
        # Pure display operator — no side effects.
        return {"FINISHED"}


classes: tuple[type, ...] = (ANIMASSIST_OT_show_help_popup,)
