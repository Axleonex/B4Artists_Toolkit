"""Background Bforartists check: the three Deliver tools added in 12.10.0 run from the
Timeline toolbar dispatch and change the scene as described.

Run with BLENDER_USER_SCRIPTS holding the package as B4_anim_assist:
    bforartists --background --factory-startup --python deliver_check.py
"""
import sys
import traceback

import addon_utils
import bpy

results = []


def check(name, ok):
    results.append((name, bool(ok)))
    print(("PASS " if ok else "FAIL ") + name, flush=True)


try:
    addon_utils.enable("B4_anim_assist", default_set=True, persistent=False)
    strip = sys.modules["B4_anim_assist.ui.timeline_strip"]
    p7s = sys.modules["B4_anim_assist.core.p7_session"]
    from B4_anim_assist.ui.timeline_catalog import ACTIONS
    from B4_anim_assist.ui import timeline_config as model
    check("Catalogue has 92 actions", len(ACTIONS) == 92)
    check("Deliver defaults include the three tools",
          {"BAKE_PREVIEW", "BAKE_INTEGER", "CLEANUP_ALL"}
          <= set(model.stage_default("DELIVER")["order"]))

    scene = bpy.context.scene
    obj = bpy.data.objects.get("Cube") or bpy.data.objects.new("Cube", bpy.data.meshes.new("Cube"))
    if obj.name not in scene.collection.objects and obj.name not in bpy.context.view_layer.objects:
        scene.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    for frame, x in ((1, 0.0), (10.5, 2.0), (20, 0.0)):
        obj.location.x = x
        obj.keyframe_insert("location", index=0, frame=frame)
    scene.frame_start, scene.frame_end = 1, 30

    space, screen, area = next((w, s, a) for w in bpy.data.workspaces for s in w.screens for a in s.areas
                               if a.type == "DOPESHEET_EDITOR" and a.spaces.active.mode == "TIMELINE")
    region = next(r for r in area.regions if r.type == "WINDOW")

    def ctx():
        return bpy.context.temp_override(workspace=space, screen=screen, area=area, region=region,
                                         active_object=obj, object=obj, selected_objects=[obj])

    def run(action):
        with ctx():
            try:
                bpy.ops.animassist.timeline_tool(action=action)
            except RuntimeError as exc:
                print("dispatch:", action, exc, flush=True)

    def reason(action):
        with ctx():
            return strip._unavailable(bpy.context, area, action)

    def frames():
        fc = next(f for f in obj.animation_data.action.fcurves if f.data_path == "location" and f.array_index == 0) \
            if hasattr(obj.animation_data.action, "fcurves") else None
        if fc is None:
            from B4_anim_assist.core.fcurve_compat import get_fcurves
            fc = next(f for f in get_fcurves(obj.animation_data.action, anim_data=obj.animation_data)
                      if f.data_path == "location" and f.array_index == 0)
        return [k.co.x for k in fc.keyframe_points]

    def temps():
        return [o for o in bpy.data.objects if o.get(p7s.TAG_TEMP)]

    constraints_before = len(obj.constraints)

    # Bake Keys to Integer Frames.
    check("Integer Frames: a sub-frame key exists first", any(f != int(f) for f in frames()))
    run("BAKE_INTEGER")
    check("Integer Frames rounds every key to a whole frame", all(f == int(f) for f in frames()))

    # Bake Preview Range.
    scene.use_preview_range = False
    check("Bake Preview explains a missing preview range",
          reason("BAKE_PREVIEW") == "Select an object and turn on the scene preview range")
    scene.use_preview_range = True
    scene.frame_preview_start, scene.frame_preview_end = 5, 15
    check("Bake Preview available with a preview range", reason("BAKE_PREVIEW") == "")
    run("BAKE_PREVIEW")
    baked = set(round(f) for f in frames())
    check("Bake Preview keys every frame 5-15", set(range(5, 16)) <= baked)
    scene.use_preview_range = False

    # Remove All Proxy Sessions.
    check("Clean All explains when there is nothing to remove",
          reason("CLEANUP_ALL") == "Have proxy helpers or sessions to remove")
    run("PROXY_TRANSLATION")
    check("A translation proxy session exists", len(temps()) > 0 and len(obj.constraints) > constraints_before)
    run("CLEANUP_ALL")
    check("Clean All removes every proxy helper and constraint",
          not temps() and len(obj.constraints) == constraints_before)

    # One-Click Proxy & Bake is not offered on the toolbar: the existing operator constrains
    # the object to a static proxy and flattens its motion (measured 2026-10-17).
    check("One-Click Proxy & Bake is not offered", "PROXY_BAKE" not in ACTIONS)
    addon_utils.disable("B4_anim_assist", default_set=False)
except Exception:
    traceback.print_exc()
    results.append(("no exception", False))

failed = [n for n, ok in results if not ok]
print(f"RESULT {len(results) - len(failed)}/{len(results)} passed", flush=True)
sys.exit(1 if failed else 0)
