"""Prepare an isolated native application for manual toolbar observations.

Launch with --factory-startup --python this-file after staging the exact ZIP
in BLENDER_USER_SCRIPTS/addons. Existing CONFIG/SCRIPTS/DATAFILES directories
are required. This helper records state and prepares an optional simple scene;
it does not exercise tools or classify observations as passing tests.
"""

from pathlib import Path
import builtins
import datetime
import importlib
import json
import os
import time

import addon_utils
import bpy


CONFIG = Path(os.environ["BLENDER_USER_CONFIG"]).resolve()
assert CONFIG.is_dir(), "Precreate the isolated configuration directory"
assert Path(bpy.utils.user_resource("CONFIG")).resolve() == CONFIG, (
    "Application configuration did not resolve to the isolated profile"
)
for variable in ("BLENDER_USER_SCRIPTS", "BLENDER_USER_DATAFILES"):
    assert Path(os.environ[variable]).is_dir(), f"Precreate {variable}"

OUTPUT = Path(os.environ["AA_NATIVE_OBSERVATIONS"]).resolve()
PACKAGE = "B4_anim_assist"
if hasattr(bpy.context.preferences, "use_preferences_save"):
    bpy.context.preferences.use_preferences_save = False


def observe(stage):
    """Record native geometry and scene state when called during manual use."""
    get_fcurves = importlib.import_module(PACKAGE + ".core.fcurve_compat").get_fcurves
    catalogue = importlib.import_module(PACKAGE + ".ui.timeline_catalog")
    prefs = bpy.context.preferences.addons.get(PACKAGE)
    prefs = prefs.preferences if prefs else None
    settings = getattr(bpy.context.scene, "anim_assist", None)
    objects = []
    for obj in bpy.context.scene.objects:
        ad = obj.animation_data
        curves = []
        if ad and ad.action:
            for curve in get_fcurves(ad.action, anim_data=ad):
                curves.append({"path": curve.data_path, "index": curve.array_index,
                    "keys": [{"co": list(key.co), "type": key.type,
                              "selected": key.select_control_point,
                              "interpolation": key.interpolation,
                              "handle_left": list(key.handle_left),
                              "handle_right": list(key.handle_right)}
                             for key in curve.keyframe_points]})
        objects.append({"name": obj.name, "type": obj.type,
                        "selected": obj.select_get(),
                        "numeric_properties": {key: value for key, value in obj.items()
                                               if isinstance(value, (int, float))},
                        "matrix_world": [list(row) for row in obj.matrix_world],
                        "curves": curves})
    windows = []
    for window in bpy.context.window_manager.windows:
        areas = []
        for area in window.screen.areas:
            entry = {"pointer": area.as_pointer(), "type": area.type,
                     "x": area.x, "y": area.y,
                     "width": area.width, "height": area.height,
                     "regions": [{"type": region.type, "x": region.x,
                                  "y": region.y, "width": region.width,
                                  "height": region.height}
                                 for region in area.regions]}
            if area.type == "DOPESHEET_EDITOR":
                space = area.spaces.active
                entry.update(mode=space.mode,
                    toolbar_visible=space.show_region_tool_header,
                    toolbar_hidden_by_user=space.timeline_toolbar_hidden_by_user)
                if space.mode == "TIMELINE":
                    window_region = next((region for region in area.regions
                                          if region.type == "WINDOW"), None)
                    entry["timeline_view"] = ({
                        "width": window_region.width, "height": window_region.height,
                        "bottom_left": list(window_region.view2d.region_to_view(0, 0)),
                        "top_right": list(window_region.view2d.region_to_view(
                            window_region.width, window_region.height))}
                        if window_region and window_region.width and window_region.height else None)
            if area.type == "TEXT_EDITOR":
                text = area.spaces.active.text
                entry.update(text_name=text.name if text else None,
                    owned_legacy_strip=bool(text and text.get("animassist_timeline_toolbar") == 1))
            areas.append(entry)
        windows.append({"pointer": window.as_pointer(),
                        "screen": window.screen.name, "areas": areas})
    record = {"stage": stage,
              "utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
              "binary": bpy.app.binary_path,
              "build_hash": bpy.app.build_hash.decode(),
              "version": list(bpy.app.version), "config": str(CONFIG),
              "bforartists_native_property":
                  "show_toolshelf_tabs" in bpy.types.SpaceView3D.bl_rna.properties,
              "addon_version": list(importlib.import_module(PACKAGE).bl_info["version"]),
              "frame": bpy.context.scene.frame_current,
              "ui_scale": bpy.context.preferences.system.ui_scale,
              "ui_scale_setting": bpy.context.preferences.view.ui_scale,
              "dpi": bpy.context.preferences.system.dpi,
              "pixel_size": bpy.context.preferences.system.pixel_size,
              "addon_enabled": bool(getattr(importlib.import_module(PACKAGE),
                                            "__addon_enabled__", False)),
              "addon_preference_entry": PACKAGE in bpy.context.preferences.addons,
              "active_object": bpy.context.active_object.name if bpy.context.active_object else None,
              "quick_actions": list(catalogue.selected_quick_actions(prefs)) if prefs else None,
              "toolbar_preference": prefs.timeline_toolbar_row if prefs else None,
              "paste_offset": prefs.timeline_paste_offset if prefs else None,
              "reference_frame": settings.reference_frame if settings else None,
              "reference_bookmarks": [{"name": bookmark.name, "frame": bookmark.frame}
                                      for bookmark in settings.bookmarks] if settings else None,
              "active_bookmark_index": settings.active_bookmark_index if settings else None,
              "timeline_spaces": [{"screen": screen.name,
                  "area_pointer": area.as_pointer(), "active_area_type": area.type,
                  "space_pointer": space.as_pointer(),
                  "active": space == area.spaces.active,
                  "toolbar_visible": space.show_region_tool_header,
                  "toolbar_hidden_by_user": space.timeline_toolbar_hidden_by_user}
                  for screen in bpy.data.screens for area in screen.areas
                  for space in area.spaces if space.type == "DOPESHEET_EDITOR"
                  and space.mode == "TIMELINE"],
              "objects": objects,
              "windows": windows}
    records = json.loads(OUTPUT.read_text(encoding="utf-8")) if OUTPUT.exists() else []
    records.append(record)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
    print("Native observation recorded:", stage, str(OUTPUT), flush=True)
    return record


def prepare_animation():
    """Give manual tool use an animated active object and a reference object."""
    scene = bpy.context.scene
    obj = bpy.context.active_object
    if obj is None or obj.mode != "OBJECT":
        raise RuntimeError("Use the factory scene in Object mode for preparation")
    obj.name = "AA_ObservedCube"
    for frame, x in ((1, 0.0), (20, 4.0), (40, 1.0)):
        obj.location = (x, 0.0, 0.0)
        obj.keyframe_insert(data_path="location", frame=frame)
    get_fcurves = importlib.import_module(PACKAGE + ".core.fcurve_compat").get_fcurves
    for curve in get_fcurves(obj.animation_data.action, anim_data=obj.animation_data):
        curve.select = True
        for key in curve.keyframe_points:
            key.select_control_point = True
    reference = bpy.data.objects.get("AA_Reference")
    if reference is None:
        reference = bpy.data.objects.new("AA_Reference", None)
        scene.collection.objects.link(reference)
    reference.location = (6.0, 2.0, 0.0)
    reference.select_set(True)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    obj["space"] = 0.0
    scene.frame_end = 60
    scene.frame_set(10)
    return observe("manual-animation-prepared")


def watch_drag(seconds=60):
    """Record changed raw geometry around a manually initiated boundary drag.

    Call before a manual border drag. Samples are held in memory and written
    after release, so repeated file writes do not affect the drag itself.
    Native boundary interactions may not expose an RNA modal operator. Record
    geometry independently, retaining any operator identity that is available.
    This classifies no result and sends no input.
    """
    deadline = time.monotonic() + seconds
    samples = []
    previous_geometry = None

    def tick():
        nonlocal previous_geometry
        windows = []
        for window in bpy.context.window_manager.windows:
            operator_details = [{"idname": getattr(op, "bl_idname", ""),
                                 "rna_type": op.bl_rna.identifier}
                                for op in window.modal_operators]
            operators = [entry["idname"] or entry["rna_type"]
                         for entry in operator_details]
            windows.append({"pointer": window.as_pointer(), "screen": window.screen.name,
                "ui_scale": bpy.context.preferences.system.ui_scale, "operators": operators,
                "operator_details": operator_details,
                "areas": [{"pointer": area.as_pointer(), "type": area.type,
                           "x": area.x, "y": area.y,
                           "height": area.height, "width": area.width,
                           "regions": [{"type": region.type, "height": region.height}
                                       for region in area.regions]}
                          for area in window.screen.areas]})
        geometry = json.dumps(windows, sort_keys=True)
        if geometry != previous_geometry:
            previous_geometry = geometry
            samples.append({"monotonic": time.monotonic(),
                "utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "windows": windows})
        if time.monotonic() >= deadline:
            records = json.loads(OUTPUT.read_text(encoding="utf-8")) if OUTPUT.exists() else []
            records.append({"stage": "native-border-drag-samples", "samples": samples,
                "observation_filter": "Changed geometry independent of modal operator presence; correlate timestamps with manual input"})
            OUTPUT.parent.mkdir(parents=True, exist_ok=True)
            OUTPUT.write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
            print("Native border-drag samples recorded:", len(samples), flush=True)
            return None
        return 0.02

    bpy.app.timers.register(tick, first_interval=0.02)
    print("Native border-drag observation armed", flush=True)


def after_enable():
    # A new, task-owned scene title distinguishes this application from any
    # Bforartists window the owner already has open. Never overwrite a file.
    title_file = os.environ.get("AA_NATIVE_TITLE_FILE")
    if title_file:
        title_path = Path(title_file).resolve()
        if title_path.exists():
            raise FileExistsError(title_path)
        title_path.parent.mkdir(parents=True, exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=str(title_path), check_existing=False)
    observe("fresh-native-row")
    return None


addon_utils.enable(PACKAGE, default_set=True, persistent=True)
if PACKAGE not in bpy.context.preferences.addons:
    raise RuntimeError("Matching add-on did not enable in the isolated profile")
builtins.aa_observe = observe
builtins.aa_prepare_animation = prepare_animation
builtins.aa_watch_drag = watch_drag
bpy.app.timers.register(after_enable, first_interval=2.0)
print("Manual native observation profile prepared:", CONFIG, flush=True)
