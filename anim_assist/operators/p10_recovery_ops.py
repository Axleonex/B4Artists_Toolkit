# --- BATCH OPERATIONS AND AUTOMATION ---
"""Recovery snapshot operators."""

from __future__ import annotations

from ..i18n import T, F

import bpy
from bpy.props import IntProperty, StringProperty

from ..core.logging import get_logger
from ..core.p10_audit import log_operation
from ..core.helpers import confirm_dialog

_log = get_logger(__name__)


class AA_OT_p10_take_snapshot(bpy.types.Operator):
    """Take a recovery snapshot of current addon state."""
    bl_idname = "animassist.p10_take_snapshot"
    bl_label = "Take Snapshot"
    bl_options = {'REGISTER'}

    label: StringProperty(name="Label", default="", translation_context='AnimAssist')  # type: ignore[valid-type]

    def execute(self, context):
        from ..core import p10_recovery as recovery
        idx = recovery.take_snapshot(context, self.label)
        log_operation(self.bl_idname, True, f"snapshot #{idx}")
        self.report({'INFO'}, F('Snapshot taken: #{p0}', p0=f'{idx}'))
        return {'FINISHED'}


class AA_OT_p10_restore_snapshot(bpy.types.Operator):
    """Restore addon state from a recovery snapshot."""
    bl_idname = "animassist.p10_restore_snapshot"
    bl_label = "Restore Snapshot"
    bl_options = {'REGISTER', 'UNDO'}

    index: IntProperty(name="Index", default=0, translation_context='AnimAssist')  # type: ignore[valid-type]

    def execute(self, context):
        from ..core import p10_recovery as recovery
        if recovery.restore_snapshot(context, self.index):
            log_operation(self.bl_idname, True, f"restored #{self.index}")
            self.report({'INFO'}, F('Snapshot #{p0} restored', p0=f'{self.index}'))
            return {'FINISHED'}
        else:
            log_operation(self.bl_idname, False, f"index {self.index} invalid")
            self.report({'ERROR'}, F('Could not restore snapshot #{p0}. Pick another snapshot or take a new one', p0=f'{self.index}'))
            return {'CANCELLED'}


class AA_OT_p10_clear_snapshots(bpy.types.Operator):
    """Clear all recovery snapshots."""
    bl_idname = "animassist.p10_clear_snapshots"
    bl_label = "Clear Snapshots"
    bl_options = {'REGISTER'}

    def invoke(self, context, event):  # type: ignore[no-untyped-def]
        return confirm_dialog(self, context, event, 'Delete all recovery snapshots? You will not be able to restore from them. This cannot be undone.')

    def execute(self, context):
        from ..core import p10_recovery as recovery
        recovery.clear_snapshots()
        log_operation(self.bl_idname, True, "all cleared")
        self.report({'INFO'}, T('All snapshots cleared'))
        return {'FINISHED'}


class AA_OT_p10_list_snapshots(bpy.types.Operator):
    """List recovery snapshots in the info area."""
    bl_idname = "animassist.p10_list_snapshots"
    bl_label = "List Snapshots"
    bl_options = {'REGISTER'}

    def execute(self, context):
        from ..core import p10_recovery as recovery
        snaps = recovery.list_snapshots()
        if not snaps:
            self.report({'INFO'}, T('No snapshots stored'))
        else:
            for s in snaps:
                self.report({'INFO'}, F('  [{p0}] {p1} ({p2} props)', p0=f"{s['index']}", p1=f"{s['label']}", p2=f"{s['property_count']}"))
            self.report({'INFO'}, F('{p0} snapshot(s) total', p0=f'{len(snaps)}'))
        return {'FINISHED'}


CLASSES: tuple[type, ...] = (
    AA_OT_p10_take_snapshot,
    AA_OT_p10_restore_snapshot,
    AA_OT_p10_clear_snapshots,
    AA_OT_p10_list_snapshots,
)
