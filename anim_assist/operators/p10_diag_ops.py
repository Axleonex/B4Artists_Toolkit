# --- BATCH OPERATIONS AND AUTOMATION ---
"""Diagnostics and maintenance operators."""

from __future__ import annotations

from ..i18n import T, F

import bpy

from ..core.logging import get_logger
from ..core.p10_audit import log_operation

_log = get_logger(__name__)


class AA_OT_p10_system_diagnostics(bpy.types.Operator):
    """Run system diagnostics and display report."""
    bl_idname = "animassist.p10_system_diagnostics"
    bl_label = "System Diagnostics"
    bl_options = {'REGISTER'}

    def execute(self, context):
        from ..core import p10_diagnostics as diag
        report = diag.get_system_report()
        self.report({'INFO'}, F('Blender: {p0}', p0=f"{report.get('blender_version', '?')}"))
        rt = report.get("runtime", {})
        self.report({'INFO'}, F('Batch mode: {p0}', p0=f"{rt.get('is_batch_processing', False)}"))
        self.report({'INFO'}, F('Overlays: {p0}', p0=f"{rt.get('active_overlay_count', 0)}"))
        tr = report.get("tool_registry", {})
        self.report({'INFO'}, F('Registered tools: {p0}', p0=f"{tr.get('total_tools', 0)}"))
        self.report({'INFO'}, F('Dispatch commands: {p0}', p0=f"{len(report.get('dispatch_commands', []))}"))
        log_operation(self.bl_idname, True, "report generated")
        return {'FINISHED'}


class AA_OT_p10_leak_check(bpy.types.Operator):
    """Check for resource leaks."""
    bl_idname = "animassist.p10_leak_check"
    bl_label = "Leak Check"
    bl_options = {'REGISTER'}

    def execute(self, context):
        from ..core import p10_diagnostics as diag
        warnings = diag.run_leak_check()
        if warnings:
            for w in warnings:
                self.report({'WARNING'}, w)
            self.report({'WARNING'}, F('{p0} potential leak(s) found', p0=f'{len(warnings)}'))
        else:
            self.report({'INFO'}, T('No leaks detected'))
        log_operation(self.bl_idname, True, f"{len(warnings)} warnings")
        return {'FINISHED'}


class AA_OT_p10_stale_cleanup(bpy.types.Operator):
    """Remove stale handlers and invalidate caches."""
    bl_idname = "animassist.p10_stale_cleanup"
    bl_label = "Stale Cleanup"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        from ..core import p10_diagnostics as diag
        cleaned = diag.run_stale_cleanup()
        total = sum(cleaned.values())
        self.report({'INFO'}, F('Cleaned {p0} stale item(s)', p0=f'{total}'))
        log_operation(self.bl_idname, True, f"{total} items cleaned")
        return {'FINISHED'}


class AA_OT_p10_metadata_cleanup(bpy.types.Operator):
    """Clean orphaned scene metadata."""
    bl_idname = "animassist.p10_metadata_cleanup"
    bl_label = "Metadata Cleanup"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        from ..core import p10_diagnostics as diag
        cleaned = diag.run_metadata_cleanup(context)
        total = sum(cleaned.values())
        self.report({'INFO'}, F('Cleaned {p0} metadata item(s)', p0=f'{total}'))
        log_operation(self.bl_idname, True, f"{total} items cleaned")
        return {'FINISHED'}


class AA_OT_p10_rebuild_caches(bpy.types.Operator):
    """Force-rebuild all addon caches."""
    bl_idname = "animassist.p10_rebuild_caches"
    bl_label = "Rebuild Caches"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        from ..core import p10_diagnostics as diag
        results = diag.rebuild_all_caches(context)
        ok = sum(1 for v in results.values() if v)
        fail = sum(1 for v in results.values() if not v)
        self.report({'INFO'}, F('Caches rebuilt: {p0} ok, {p1} failed', p0=f'{ok}', p1=f'{fail}'))
        log_operation(self.bl_idname, fail == 0, f"{ok} ok / {fail} failed")
        return {'FINISHED'}


class AA_OT_p10_reset_ui(bpy.types.Operator):
    """Reset all UI panel states to defaults."""
    bl_idname = "animassist.p10_reset_ui"
    bl_label = "Reset UI State"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        from ..core import p10_diagnostics as diag
        count = diag.reset_ui_state(context)
        self.report({'INFO'}, F('UI state reset: {p0} section(s) cleared', p0=f'{count}'))
        log_operation(self.bl_idname, True, f"{count} sections reset")
        return {'FINISHED'}


class AA_OT_p10_validate_registration(bpy.types.Operator):
    """Validate that all expected classes are registered."""
    bl_idname = "animassist.p10_validate_registration"
    bl_label = "Validate Registration"
    bl_options = {'REGISTER'}

    def execute(self, context):
        from ..core import p10_diagnostics as diag
        issues = diag.validate_registration()
        if issues:
            for issue in issues:
                self.report({'WARNING'}, T(issue))
            self.report({'WARNING'}, F('{p0} registration issue(s)', p0=f'{len(issues)}'))
        else:
            self.report({'INFO'}, T('All registrations valid'))
        log_operation(self.bl_idname, len(issues) == 0, f"{len(issues)} issues")
        return {'FINISHED'}


CLASSES: tuple[type, ...] = (
    AA_OT_p10_system_diagnostics,
    AA_OT_p10_leak_check,
    AA_OT_p10_stale_cleanup,
    AA_OT_p10_metadata_cleanup,
    AA_OT_p10_rebuild_caches,
    AA_OT_p10_reset_ui,
    AA_OT_p10_validate_registration,
)
