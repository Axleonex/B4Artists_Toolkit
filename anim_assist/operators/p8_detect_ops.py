"""Rig pattern detection, preset management, and diagnostics operators."""

from __future__ import annotations

from ..i18n import T, F

import bpy
import json
from ..core.p8_properties import get_p8
from ..core import p8_switch_detect as det
from ..core import p8_switch_history as hist
from ..core.logging import get_logger
from ..core.helpers import report_failure

_log = get_logger(__name__)


# ---------------------------------------------------------------------------
# Module-level cached detection results
# ---------------------------------------------------------------------------

_cached_patterns: list[det.SwitchPattern] = []


def get_cached_patterns() -> list[det.SwitchPattern]:
    """Return a copy of the cached patterns list."""
    return list(_cached_patterns)


def clear_cached_patterns() -> None:
    """Clear the cached patterns."""
    _cached_patterns.clear()


# ---------------------------------------------------------------------------
# Module-level switch presets (saved as JSON on scene custom property)
# ---------------------------------------------------------------------------

_PRESET_KEY = "anim_assist_p8_switch_presets"


def _get_presets(context: bpy.types.Context) -> dict[str, dict]:
    """Load presets from scene custom property."""
    scene = context.scene
    preset_json = scene.get(_PRESET_KEY, "{}")
    try:
        return json.loads(preset_json)
    except (json.JSONDecodeError, TypeError):
        return {}


def _save_presets(context: bpy.types.Context, presets: dict[str, dict]) -> None:
    """Save presets to scene custom property."""
    scene = context.scene
    scene[_PRESET_KEY] = json.dumps(presets)


# ---------------------------------------------------------------------------
# Operators: Detection
# ---------------------------------------------------------------------------

class AA_OT_p8_detect_space_enums(bpy.types.Operator):
    """Detect custom space enum properties on the active object."""
    bl_idname = "animassist.p8_detect_space_enums"
    bl_label = "Detect Space Enums"
    bl_description = "Detect custom space enum properties on the active object."
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return context.active_object is not None

    def execute(self, context: bpy.types.Context):
        obj = context.active_object
        if obj is None:
            self.report({"ERROR"}, T('No active object. Select an object and try again'))
            return {"CANCELLED"}

        try:
            patterns = det.detect_space_enums(obj)
            _cached_patterns.clear()
            _cached_patterns.extend(patterns)
            count = len(patterns)
            self.report({"INFO"}, F('Found {p0} space enum pattern(s)', p0=f'{count}'))
            return {"FINISHED"}
        except Exception as e:
            _log.exception("detect_space_enums failed")
            report_failure(self, "Detection failed", "Select an armature with IK/FK constraints and try again", e)
            return {"CANCELLED"}


class AA_OT_p8_detect_parent_patterns(bpy.types.Operator):
    """Detect common parent-switch boolean patterns on the active object."""
    bl_idname = "animassist.p8_detect_parent_patterns"
    bl_label = "Detect Parent Patterns"
    bl_description = "Detect common parent-switch boolean patterns on the active object."
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return context.active_object is not None

    def execute(self, context: bpy.types.Context):
        obj = context.active_object
        if obj is None:
            self.report({"ERROR"}, T('No active object. Select an object and try again'))
            return {"CANCELLED"}

        try:
            patterns = det.detect_bool_patterns(obj)
            # Extend cache and deduplicate by (obj_name, bone_name, prop_path)
            seen = {(p.obj_name, p.bone_name, p.prop_path) for p in _cached_patterns}
            before_count = len(_cached_patterns)
            for pat in patterns:
                key = (pat.obj_name, pat.bone_name, pat.prop_path)
                if key not in seen:
                    _cached_patterns.append(pat)
                    seen.add(key)
            added = len(_cached_patterns) - before_count
            self.report({"INFO"}, F('Added {p0} parent pattern(s) (total: {p1})', p0=f'{added}', p1=f'{len(_cached_patterns)}'))
            return {"FINISHED"}
        except Exception as e:
            _log.exception("detect_parent_patterns failed")
            report_failure(self, "Detection failed", "Select an armature with IK/FK constraints and try again", e)
            return {"CANCELLED"}


class AA_OT_p8_detect_influence_patterns(bpy.types.Operator):
    """Detect constraint influence switch patterns on the active object."""
    bl_idname = "animassist.p8_detect_influence_patterns"
    bl_label = "Detect Influence Patterns"
    bl_description = "Detect constraint influence switch patterns on the active object."
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return context.active_object is not None

    def execute(self, context: bpy.types.Context):
        obj = context.active_object
        if obj is None:
            self.report({"ERROR"}, T('No active object. Select an object and try again'))
            return {"CANCELLED"}

        try:
            patterns = det.detect_influence_patterns(obj)
            # Extend cache and deduplicate
            seen = {(p.obj_name, p.bone_name, p.prop_path) for p in _cached_patterns}
            before_count = len(_cached_patterns)
            for pat in patterns:
                key = (pat.obj_name, pat.bone_name, pat.prop_path)
                if key not in seen:
                    _cached_patterns.append(pat)
                    seen.add(key)
            added = len(_cached_patterns) - before_count
            self.report({"INFO"}, F('Added {p0} influence pattern(s) (total: {p1})', p0=f'{added}', p1=f'{len(_cached_patterns)}'))
            return {"FINISHED"}
        except Exception as e:
            _log.exception("detect_influence_patterns failed")
            report_failure(self, "Detection failed", "Select an armature with IK/FK constraints and try again", e)
            return {"CANCELLED"}


class AA_OT_p8_detect_custom_props(bpy.types.Operator):
    """Detect generic custom property switch patterns on the active object."""
    bl_idname = "animassist.p8_detect_custom_props"
    bl_label = "Detect Custom Properties"
    bl_description = "Detect generic custom property switch patterns on the active object."
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return context.active_object is not None

    def execute(self, context: bpy.types.Context):
        obj = context.active_object
        if obj is None:
            self.report({"ERROR"}, T('No active object. Select an object and try again'))
            return {"CANCELLED"}

        try:
            patterns = det.detect_custom_props(obj)
            # Extend cache and deduplicate
            seen = {(p.obj_name, p.bone_name, p.prop_path) for p in _cached_patterns}
            before_count = len(_cached_patterns)
            for pat in patterns:
                key = (pat.obj_name, pat.bone_name, pat.prop_path)
                if key not in seen:
                    _cached_patterns.append(pat)
                    seen.add(key)
            added = len(_cached_patterns) - before_count
            self.report({"INFO"}, F('Added {p0} custom property pattern(s) (total: {p1})', p0=f'{added}', p1=f'{len(_cached_patterns)}'))
            return {"FINISHED"}
        except Exception as e:
            _log.exception("detect_custom_props failed")
            report_failure(self, "Detection failed", "Select an armature with IK/FK constraints and try again", e)
            return {"CANCELLED"}


class AA_OT_p8_detect_all(bpy.types.Operator):
    """Run all rig pattern detectors at once on the active object."""
    bl_idname = "animassist.p8_detect_all"
    bl_label = "Detect All Patterns"
    bl_description = "Run all rig pattern detectors at once on the active object."
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return context.active_object is not None

    def execute(self, context: bpy.types.Context):
        obj = context.active_object
        if obj is None:
            self.report({"ERROR"}, T('No active object. Select an object and try again'))
            return {"CANCELLED"}

        try:
            patterns = det.detect_all_patterns(obj)
            _cached_patterns.clear()
            _cached_patterns.extend(patterns)
            count = len(patterns)
            self.report({"INFO"}, F('Found {p0} pattern(s) across all detectors', p0=f'{count}'))
            return {"FINISHED"}
        except Exception as e:
            _log.exception("detect_all_patterns failed")
            report_failure(self, "Detection failed", "Select an armature with IK/FK constraints and try again", e)
            return {"CANCELLED"}


# ---------------------------------------------------------------------------
# Operators: Apply Detected Pattern
# ---------------------------------------------------------------------------

class AA_OT_p8_apply_detected_pattern(bpy.types.Operator):
    """Apply the selected detected pattern to the switch settings."""
    bl_idname = "animassist.p8_apply_detected_pattern"
    bl_label = "Apply Detected Pattern"
    bl_description = "Apply the selected detected pattern to the switch settings."
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        p8 = get_p8(context)
        return p8 is not None and len(_cached_patterns) > 0

    def execute(self, context: bpy.types.Context):
        p8 = get_p8(context)
        if p8 is None:
            self.report({"ERROR"}, T('Matching settings are not initialised. Run First Run Setup from Properties > Scene > Anim Assist > Setup'))
            return {"CANCELLED"}

        if not _cached_patterns:
            self.report({"ERROR"}, T('No patterns detected yet. Run Detect first'))
            return {"CANCELLED"}

        idx = min(p8.detected_pattern_index, len(_cached_patterns) - 1)
        if idx < 0:
            self.report({"ERROR"}, T('Select a detected pattern in the list first'))
            return {"CANCELLED"}

        pattern = _cached_patterns[idx]

        try:
            p8.switch_prop_path = pattern.prop_path
            p8.switch_bone_name = pattern.bone_name
            # Map detected kind to switch_kind enum
            kind_map = {
                "ENUM": "ENUM",
                "BOOL": "BOOL",
                "INFLUENCE": "INFLUENCE",
                "CUSTOM_PROP": "CUSTOM",
            }
            p8.switch_kind = kind_map.get(pattern.kind, "CUSTOM")
            self.report({"INFO"}, F('Applied pattern: {p0}', p0=f'{pattern.display_label()}'))
            return {"FINISHED"}
        except Exception as e:
            _log.exception("apply_detected_pattern failed")
            report_failure(self, "Failed to apply pattern", "Undo (Ctrl+Z) and try again", e)
            return {"CANCELLED"}


# ---------------------------------------------------------------------------
# Operators: Switch Presets
# ---------------------------------------------------------------------------

class AA_OT_p8_save_switch_preset(bpy.types.Operator):
    """Save the current switch configuration as a named preset."""
    bl_idname = "animassist.p8_save_switch_preset"
    bl_label = "Save Switch Preset"
    bl_description = "Save the current switch configuration as a named preset."
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return get_p8(context) is not None

    def execute(self, context: bpy.types.Context):
        p8 = get_p8(context)
        if p8 is None:
            self.report({"ERROR"}, T('Matching settings are not initialised. Run First Run Setup from Properties > Scene > Anim Assist > Setup'))
            return {"CANCELLED"}

        name = p8.switch_preset_name.strip()
        if not name:
            self.report({"ERROR"}, T('Enter a preset name first'))
            return {"CANCELLED"}

        try:
            preset = {
                "prop_path": p8.switch_prop_path,
                "bone_name": p8.switch_bone_name,
                "kind": p8.switch_kind,
                "new_value": p8.switch_new_value,
            }
            # Load existing presets
            presets = _get_presets(context)
            presets[name] = preset
            _save_presets(context, presets)
            self.report({"INFO"}, F("Saved switch preset '{p0}'", p0=f'{name}'))
            return {"FINISHED"}
        except Exception as e:
            _log.exception("save_switch_preset failed")
            report_failure(self, "Failed to save preset", "Undo (Ctrl+Z) and try again", e)
            return {"CANCELLED"}


class AA_OT_p8_load_switch_preset(bpy.types.Operator):
    """Load a named switch preset and apply it to the current settings."""
    bl_idname = "animassist.p8_load_switch_preset"
    bl_label = "Load Switch Preset"
    bl_description = "Load a named switch preset and apply it to the current settings."
    bl_options = {"REGISTER", "UNDO"}

    preset_name: bpy.props.StringProperty(  # type: ignore[valid-type]
        name="Preset Name",
        description="Name of the preset to load",
        default="",
     translation_context='AnimAssist')

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return get_p8(context) is not None

    def execute(self, context: bpy.types.Context):
        p8 = get_p8(context)
        if p8 is None:
            self.report({"ERROR"}, T('Matching settings are not initialised. Run First Run Setup from Properties > Scene > Anim Assist > Setup'))
            return {"CANCELLED"}

        preset_name = self.preset_name.strip()
        if not preset_name:
            self.report({"ERROR"}, T('Enter a preset name first'))
            return {"CANCELLED"}

        try:
            presets = _get_presets(context)
            if preset_name not in presets:
                self.report({"ERROR"}, F("Preset '{p0}' not found. Pick one from the list or save it first", p0=f'{preset_name}'))
                return {"CANCELLED"}

            preset = presets[preset_name]
            p8.switch_prop_path = preset.get("prop_path", "")
            p8.switch_bone_name = preset.get("bone_name", "")
            p8.switch_kind = preset.get("kind", "ENUM")
            p8.switch_new_value = float(preset.get("new_value", 0.0))
            self.report({"INFO"}, F("Loaded switch preset '{p0}'", p0=f'{preset_name}'))
            return {"FINISHED"}
        except Exception as e:
            _log.exception("load_switch_preset failed")
            report_failure(self, "Failed to load preset", "Undo (Ctrl+Z) and try again", e)
            return {"CANCELLED"}


class AA_OT_p8_delete_switch_preset(bpy.types.Operator):
    """Delete a named switch preset."""
    bl_idname = "animassist.p8_delete_switch_preset"
    bl_label = "Delete Switch Preset"
    bl_description = "Delete a named switch preset."
    bl_options = {"REGISTER", "UNDO"}

    preset_name: bpy.props.StringProperty(  # type: ignore[valid-type]
        name="Preset Name",
        description="Name of the preset to delete",
        default="",
     translation_context='AnimAssist')

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return get_p8(context) is not None

    def execute(self, context: bpy.types.Context):
        preset_name = self.preset_name.strip()
        if not preset_name:
            self.report({"ERROR"}, T('Enter a preset name first'))
            return {"CANCELLED"}

        try:
            presets = _get_presets(context)
            if preset_name not in presets:
                self.report({"ERROR"}, F("Preset '{p0}' not found. Pick one from the list or save it first", p0=f'{preset_name}'))
                return {"CANCELLED"}

            del presets[preset_name]
            _save_presets(context, presets)
            self.report({"INFO"}, F("Deleted switch preset '{p0}'", p0=f'{preset_name}'))
            return {"FINISHED"}
        except Exception as e:
            _log.exception("delete_switch_preset failed")
            report_failure(self, "Failed to delete preset", "Undo (Ctrl+Z) and try again", e)
            return {"CANCELLED"}


# ---------------------------------------------------------------------------
# Operators: Reports and Diagnostics
# ---------------------------------------------------------------------------

class AA_OT_p8_compensation_report(bpy.types.Operator):
    """Generate and display a compensation operation report."""
    bl_idname = "animassist.p8_compensation_report"
    bl_label = "Compensation Report"
    bl_description = "Generate and display a compensation operation report."
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
            # Get the last switch event from history
            last_event = hist.get_last_event()
            if last_event is None:
                self.report({"WARNING"}, T('No compensation history available'))
                return {"CANCELLED"}

            lines: list[str] = []
            lines.append(T('=== COMPENSATION REPORT ==='))
            lines.append("")
            lines.append(F('Frame: {p0}', p0=f'{last_event.frame}'))
            target = last_event.bone_name or last_event.obj_name
            lines.append(F('Target: {p0}', p0=f'{target}'))
            lines.append(F('Property: {p0}', p0=f'{last_event.prop_path}'))
            lines.append(F('Old Value: {p0}', p0=f'{last_event.old_value}'))
            lines.append(F('New Value: {p0}', p0=f'{last_event.new_value}'))
            lines.append("")

            # Add history context
            all_events = hist.get_history()
            if all_events:
                lines.append(F('Total switch events in history: {p0}', p0=f'{len(all_events)}'))
                lines.append(F('Unique frames with switches: {p0}', p0=f'{len(hist.get_unique_frames())}'))
            lines.append("")

            text = "\n".join(lines)
            wm.clipboard = text
            self.report({"INFO"}, T('Compensation report copied to clipboard'))
            return {"FINISHED"}
        except Exception as e:
            _log.exception("compensation_report failed")
            report_failure(self, "Report generation failed", "Undo (Ctrl+Z) and try again", e)
            return {"CANCELLED"}


class AA_OT_p8_unsupported_warning(bpy.types.Operator):
    """Check for and report unsupported rig setups."""
    bl_idname = "animassist.p8_unsupported_warning"
    bl_label = "Unsupported Setup Warning"
    bl_description = "Check for and report unsupported rig setups."
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return context.active_object is not None

    def execute(self, context: bpy.types.Context):
        obj = context.active_object
        if obj is None:
            self.report({"ERROR"}, T('No active object. Select an object and try again'))
            return {"CANCELLED"}

        try:
            warnings: list[str] = []

            # Check for animation data
            if obj.animation_data is None or obj.animation_data.action is None:
                warnings.append(T('• No animation data or action assigned'))

            # Check for complex constraint stacks
            def _count_constraints(obj_or_bone):
                return len(obj_or_bone.constraints)

            obj_con_count = _count_constraints(obj)
            if obj_con_count > 5:
                warnings.append(F('• Object has {p0} constraints (complex stack)', p0=f'{obj_con_count}'))

            bone_con_count = 0
            if hasattr(obj, "pose") and obj.pose:
                for bone in obj.pose.bones:
                    bone_con_count += _count_constraints(bone)
                if bone_con_count > 20:
                    warnings.append(F('• Armature bones have {p0} total constraints (very complex)', p0=f'{bone_con_count}'))

            # Check for drivers on transform channels
            def _check_drivers(obj_or_bone, name):
                if not hasattr(obj_or_bone, "animation_data"):
                    return []
                anim_data = obj_or_bone.animation_data
                if not anim_data or not anim_data.drivers:
                    return []
                found = []
                for driver in anim_data.drivers:
                    if any(x in driver.data_path for x in ["location", "rotation", "scale"]):
                        found.append(driver.data_path)
                return found

            obj_drivers = _check_drivers(obj, obj.name)
            if obj_drivers:
                warnings.append(F('• Object has {p0} driver(s) on transform channels', p0=f'{len(obj_drivers)}'))

            if hasattr(obj, "pose") and obj.pose:
                for bone in obj.pose.bones:
                    bone_drivers = _check_drivers(bone, bone.name)
                    if bone_drivers:
                        warnings.append(F("• Bone '{p0}' has driver(s) on transform channels", p0=f'{bone.name}'))

            # Check for locked transforms
            def _check_locks(obj_or_bone, name):
                locks = []
                if hasattr(obj_or_bone, "lock_location"):
                    if any(obj_or_bone.lock_location):
                        locks.append(T('location'))
                if hasattr(obj_or_bone, "lock_rotation"):
                    if any(obj_or_bone.lock_rotation):
                        locks.append(T('rotation'))
                if hasattr(obj_or_bone, "lock_scale"):
                    if any(obj_or_bone.lock_scale):
                        locks.append(T('scale'))
                return locks

            obj_locks = _check_locks(obj, obj.name)
            if obj_locks:
                warnings.append(F('• Object has locked channels: {p0}', p0=f"{', '.join(obj_locks)}"))

            if hasattr(obj, "pose") and obj.pose:
                lock_count = 0
                for bone in obj.pose.bones:
                    bone_locks = _check_locks(bone, bone.name)
                    if bone_locks:
                        lock_count += 1
                if lock_count > 0:
                    warnings.append(F('• {p0} bone(s) have locked channels', p0=f'{lock_count}'))

            if warnings:
                msg = F('Potential issues found:\n{p0}', p0="\n".join(warnings))
                self.report({"WARNING"}, msg)
            else:
                self.report({"INFO"}, T('No obvious setup issues detected'))

            return {"FINISHED"}
        except Exception as e:
            _log.exception("unsupported_warning failed")
            report_failure(self, "Check failed", "Undo (Ctrl+Z) and try again", e)
            return {"CANCELLED"}


class AA_OT_p8_debug_diagnostics(bpy.types.Operator):
    """Run detailed custom-rig debug diagnostics and copy to clipboard."""
    bl_idname = "animassist.p8_debug_diagnostics"
    bl_label = "Debug Diagnostics"
    bl_description = "Run detailed custom-rig debug diagnostics and copy to clipboard."
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return (context.active_object is not None and
                getattr(context, "window_manager", None) is not None)

    def execute(self, context: bpy.types.Context):
        wm = getattr(context, "window_manager", None)
        if wm is None:
            self.report({"ERROR"}, T('Window manager not available. Run this from the Bforartists interface, not a background script'))
            return {"CANCELLED"}

        obj = context.active_object
        if obj is None:
            self.report({"ERROR"}, T('No active object. Select an object and try again'))
            return {"CANCELLED"}

        try:
            lines: list[str] = []
            lines.append(T('=== SWITCH DETECTION DEBUG DIAGNOSTICS ==='))
            lines.append("")
            lines.append(F('Object: {p0}', p0=f'{obj.name}'))
            lines.append(F('Type: {p0}', p0=f'{obj.type}'))
            lines.append("")

            # Run all detectors
            patterns = det.detect_all_patterns(obj)
            lines.append(F('Detected Patterns: {p0}', p0=f'{len(patterns)}'))
            for i, pat in enumerate(patterns):
                lines.append(F('  [{p0}] {p1} (confidence={p2})', p0=f'{i}', p1=f'{pat.display_label()}', p2=f'{pat.confidence:.2f}'))
            lines.append("")

            # Constraint types
            def _count_constraint_types(constraints):
                counts = {}
                for con in constraints:
                    counts[con.type] = counts.get(con.type, 0) + 1
                return counts

            obj_con_types = _count_constraint_types(obj.constraints)
            if obj_con_types:
                lines.append(T('Object Constraint Types:'))
                for ctype, count in sorted(obj_con_types.items()):
                    lines.append(F('  {p0}: {p1}', p0=f'{ctype}', p1=f'{count}'))
            else:
                lines.append(T('Object Constraint Types: None'))

            bone_con_types_total = {}
            if hasattr(obj, "pose") and obj.pose:
                for bone in obj.pose.bones:
                    for ctype, count in _count_constraint_types(bone.constraints).items():
                        bone_con_types_total[ctype] = bone_con_types_total.get(ctype, 0) + count
            if bone_con_types_total:
                lines.append(T('Bone Constraint Types (total):'))
                for ctype, count in sorted(bone_con_types_total.items()):
                    lines.append(F('  {p0}: {p1}', p0=f'{ctype}', p1=f'{count}'))
            else:
                lines.append(T('Bone Constraint Types: None'))
            lines.append("")

            # Driver count
            driver_count = 0
            if obj.animation_data and obj.animation_data.drivers:
                driver_count += len(obj.animation_data.drivers)
            if hasattr(obj, "pose") and obj.pose:
                for bone in obj.pose.bones:
                    if bone.animation_data and bone.animation_data.drivers:
                        driver_count += len(bone.animation_data.drivers)
            lines.append(F('Total Drivers: {p0}', p0=f'{driver_count}'))
            lines.append("")

            # Custom property count
            obj_props = len([k for k in obj.keys() if not k.startswith("_")])
            bone_props = 0
            if hasattr(obj, "pose") and obj.pose:
                for bone in obj.pose.bones:
                    bone_props += len([k for k in bone.keys() if not k.startswith("_")])
            lines.append(T('Custom Properties:'))
            lines.append(F('  Object-level: {p0}', p0=f'{obj_props}'))
            lines.append(F('  Bone-level: {p0}', p0=f'{bone_props}'))
            lines.append(F('  Total: {p0}', p0=f'{obj_props + bone_props}'))
            lines.append("")

            # Bone hierarchy info (if armature)
            if hasattr(obj, "pose") and obj.pose:
                lines.append(F('Armature Bones: {p0}', p0=f'{len(obj.pose.bones)}'))
                lines.append(T('Bone Hierarchy:'))
                for bone in obj.pose.bones:
                    depth = 0
                    b = bone
                    while b.parent:
                        depth += 1
                        b = b.parent
                    indent = "  " * (depth + 1)
                    con_str = (F(' ({p0} constraints)', p0=f'{len(bone.constraints)}') if bone.constraints else "")
                    lines.append(F('{p0}{p1}{p2}', p0=f'{indent}', p1=f'{bone.name}', p2=f'{con_str}'))
            else:
                lines.append(T('Armature: No'))

            lines.append("")
            lines.append(T('=== END DIAGNOSTICS ==='))

            text = "\n".join(lines)
            wm.clipboard = text
            self.report({"INFO"}, T('Debug diagnostics copied to clipboard'))
            return {"FINISHED"}
        except Exception as e:
            _log.exception("debug_diagnostics failed")
            report_failure(self, "Diagnostics generation failed", "Undo (Ctrl+Z) and try again", e)
            return {"CANCELLED"}


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

CLASSES: tuple[type, ...] = (
    AA_OT_p8_detect_space_enums,
    AA_OT_p8_detect_parent_patterns,
    AA_OT_p8_detect_influence_patterns,
    AA_OT_p8_detect_custom_props,
    AA_OT_p8_detect_all,
    AA_OT_p8_apply_detected_pattern,
    AA_OT_p8_save_switch_preset,
    AA_OT_p8_load_switch_preset,
    AA_OT_p8_delete_switch_preset,
    AA_OT_p8_compensation_report,
    AA_OT_p8_unsupported_warning,
    AA_OT_p8_debug_diagnostics,
)
