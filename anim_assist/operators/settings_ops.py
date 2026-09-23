"""Import / export addon preferences to JSON."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import bpy
from bpy.props import StringProperty
from bpy_extras.io_utils import ExportHelper, ImportHelper

from .. import constants
from ..core.logging import get_logger
from ..core.helpers import report_failure

_log = get_logger(__name__)


def _prefs_available(context: bpy.types.Context) -> bool:
    """Return whether addon preferences are reachable."""
    addons = getattr(getattr(context, "preferences", None), "addons", None)
    if addons is None:
        return False
    addon = addons.get(constants.ADDON_PACKAGE)
    return addon is not None and getattr(addon, "preferences", None) is not None


def _get_prefs(context: bpy.types.Context):
    addons = getattr(getattr(context, "preferences", None), "addons", None)
    if addons is None:
        return None
    addon = addons.get(constants.ADDON_PACKAGE)
    return getattr(addon, "preferences", None) if addon is not None else None


def _is_compatible_value(current_value: Any, new_value: Any) -> bool:
    if isinstance(current_value, bool):
        return isinstance(new_value, bool)
    if isinstance(current_value, int) and not isinstance(current_value, bool):
        return isinstance(new_value, int) and not isinstance(new_value, bool)
    if isinstance(current_value, float):
        return isinstance(new_value, (int, float)) and not isinstance(
            new_value, bool
        )
    if isinstance(current_value, str):
        return isinstance(new_value, str)
    return True


class AA_OT_export_settings(bpy.types.Operator, ExportHelper):
    bl_idname = "anim_assist.export_settings"
    bl_label = "Export AnimAssist Settings"
    bl_description = "Export addon preferences to a JSON file"
    bl_options = {"REGISTER"}

    filename_ext = ".json"
    filter_glob: StringProperty(default="*.json", options={"HIDDEN"})  # type: ignore[valid-type]

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return _prefs_available(context)

    def execute(self, context: bpy.types.Context):
        prefs = _get_prefs(context)
        if prefs is None:
            self.report({"ERROR"}, "Add-on preferences unavailable. Re-enable Anim Assist in Preferences > Add-ons")
            return {"CANCELLED"}

        if not self.filepath:
            self.report({"ERROR"}, "Choose a file to export to first")
            return {"CANCELLED"}

        data: dict[str, Any] = {}
        for key in constants.MODULE_KEYS:
            attr = f"enable_{key}"
            if hasattr(prefs, attr):
                data[attr] = getattr(prefs, attr)
        data["debug_mode"] = prefs.debug_mode
        data["performance_mode"] = prefs.performance_mode
        data["diagnostics_visible"] = prefs.diagnostics_visible
        data["_version"] = constants.ADDON_VERSION_STRING

        try:
            Path(self.filepath).write_text(
                json.dumps(data, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
        except (OSError, ValueError, TypeError) as exc:
            report_failure(self, "Could not export settings", "Choose a writable location and try again", exc)
            _log.exception("Settings export failed")
            return {"CANCELLED"}

        self.report({"INFO"}, f"Settings exported to {self.filepath}")
        return {"FINISHED"}


class AA_OT_import_settings(bpy.types.Operator, ImportHelper):
    bl_idname = "anim_assist.import_settings"
    bl_label = "Import AnimAssist Settings"
    bl_description = "Import addon preferences from a JSON file"
    bl_options = {"REGISTER", "UNDO"}

    filename_ext = ".json"
    filter_glob: StringProperty(default="*.json", options={"HIDDEN"})  # type: ignore[valid-type]

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return _prefs_available(context)

    def execute(self, context: bpy.types.Context):
        prefs = _get_prefs(context)
        if prefs is None:
            self.report({"ERROR"}, "Add-on preferences unavailable. Re-enable Anim Assist in Preferences > Add-ons")
            return {"CANCELLED"}

        if not self.filepath:
            self.report({"ERROR"}, "Choose a settings file to import first")
            return {"CANCELLED"}

        try:
            raw = Path(self.filepath).read_text(encoding="utf-8")
            data = json.loads(raw)
        except (OSError, json.JSONDecodeError) as exc:
            report_failure(self, "Could not import settings", "Choose a settings file exported by Anim Assist", exc)
            _log.exception("Settings import failed")
            return {"CANCELLED"}

        if not isinstance(data, dict):
            self.report({"ERROR"}, "Import failed: JSON root must be an object")
            return {"CANCELLED"}

        applied = 0
        for key, value in data.items():
            if key.startswith("_"):
                continue
            if not hasattr(prefs, key):
                continue

            current_value = getattr(prefs, key)
            if not _is_compatible_value(current_value, value):
                _log.warning(
                    "Skipping setting '%s': expected %s, got %s",
                    key,
                    type(current_value).__name__,
                    type(value).__name__,
                )
                continue

            try:
                setattr(prefs, key, value)
                applied += 1
            except Exception:
                _log.warning("Could not apply setting '%s'", key, exc_info=True)

        self.report({"INFO"}, f"Applied {applied} settings from {self.filepath}")
        return {"FINISHED"}