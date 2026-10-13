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
bpy.app.timers.register(after_enable, first_interval=2.0)
print("Manual native observation profile prepared:", CONFIG, flush=True)
