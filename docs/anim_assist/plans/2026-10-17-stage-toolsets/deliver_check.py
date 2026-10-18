"""Background Bforartists check: the Deliver and Spline tools added in 12.10.0 run from the
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
    check("Catalogue has 96 actions", len(ACTIONS) == 96)
    check("Deliver defaults include the four tools",
          {"BAKE_PREVIEW", "BAKE_INTEGER", "PROXY_BAKE", "CLEANUP_ALL"}
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

    def ctx(target=None):
        target = target or obj
        return bpy.context.temp_override(workspace=space, screen=screen, area=area, region=region,
                                         active_object=target, object=target, selected_objects=[target])

    def run(action, target=None):
        with ctx(target):
            try:
                bpy.ops.animassist.timeline_tool(action=action)
            except RuntimeError as exc:
                print("dispatch:", action, exc, flush=True)

    def reason(action):
        with ctx():
            return strip._unavailable(bpy.context, area, action)

    def reason_for(action, target):
        with ctx(target):
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

    # One-Click Proxy & Bake keeps the object's world motion (12.9.x baked a static proxy and
    # flattened it) and leaves an open proxy session on another object alone.
    from B4_anim_assist.core.p7_properties import get_p7
    p7 = get_p7(bpy.context)
    mover = bpy.data.objects.new("Mover", None)
    scene.collection.objects.link(mover)
    for frame, x, z in ((1, 0.0, 0.0), (8, 2.0, 1.0), (14, 1.0, 3.0), (20, 0.0, 0.0)):
        mover.location = (x, 0.0, z)
        mover.keyframe_insert("location", frame=frame)

    def world(target):
        out = []
        for f in range(1, 31):
            scene.frame_set(f)
            out.append(target.matrix_world.translation.copy())
        scene.frame_set(1)
        return out

    before = world(mover)
    run("PROXY_TRANSLATION")
    open_session = p7.active_session_id
    open_helpers = len(temps())
    actions_before = len(bpy.data.actions)
    check("Proxy & Bake available with an object selected", reason("PROXY_BAKE") == "")
    run("PROXY_BAKE", mover)
    after = world(mover)
    error = max((a - b).length for a, b in zip(before, after))
    print("Proxy & Bake max world error:", round(error, 5), flush=True)
    check("Proxy & Bake keeps the world motion (max error under 0.01)", error < 0.01)
    check("Proxy & Bake leaves no constraint on the object", len(mover.constraints) == 0)
    check("Proxy & Bake leaves the open session and its helpers alone",
          p7.active_session_id == open_session and len(temps()) == open_helpers > 0)
    check("Proxy & Bake leaves no orphan proxy Action", len(bpy.data.actions) == actions_before)
    run("CLEANUP_ALL")
    check("Clean All then removes the remaining session", not temps())

    # Spline stage: To Stepped / To Spline set the selected keys' interpolation; trails moved here.
    check("Spline shows Curves and Motion; Deliver shows Bake only",
          model.stage_families("SPLINE") == ("curves", "motion") and model.stage_families("DELIVER") == ("bake",))
    check("Spline defaults start with To Spline and end with the trails toggle",
          model.stage_default("SPLINE")["order"][0] == "TO_SPLINE"
          and model.stage_default("SPLINE")["order"][-1] == "TRAIL_TOGGLE")
    # The Timeline shows the selected objects' curves; select only the mover.
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    mover.select_set(True)
    bpy.context.view_layer.objects.active = mover
    from B4_anim_assist.core.fcurve_compat import get_fcurves
    curves = list(get_fcurves(mover.animation_data.action, anim_data=mover.animation_data))
    for fc in curves:
        for k in fc.keyframe_points:
            k.select_control_point = False
    check("To Spline explains when no keys are selected",
          reason_for("TO_SPLINE", mover) == "Select editable keys on an animated object")
    for fc in curves:
        for k in fc.keyframe_points:
            k.select_control_point = True
    run("TO_STEPPED", mover)
    check("To Stepped sets selected keys to Constant",
          all(k.interpolation == "CONSTANT" for fc in curves for k in fc.keyframe_points))
    run("TO_SPLINE", mover)
    check("To Spline sets selected keys to Bezier",
          all(k.interpolation == "BEZIER" for fc in curves for k in fc.keyframe_points))

    # Version B: Breakdown presets replace Push/Pull Prev/Next with the same results.
    bd = bpy.data.objects.new("Bd", None)
    scene.collection.objects.link(bd)
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    bd.select_set(True)
    bpy.context.view_layer.objects.active = bd

    def key_bd():
        bd.animation_data_clear()
        for frame, x in ((1, 0.0), (21, 10.0)):
            bd.location.x = x
            bd.keyframe_insert("location", index=0, frame=frame)
        scene.frame_set(11)

    def x_at_11():
        fc = next(f for f in get_fcurves(bd.animation_data.action, anim_data=bd.animation_data)
                  if f.data_path == "location" and f.array_index == 0)
        return round(fc.evaluate(11), 4)

    results_bd = {}
    for button, preset in (("PUSH_PREV", -25.), ("PULL_PREV", 25.), ("PULL_NEXT", 75.), ("PUSH_NEXT", 125.)):
        key_bd(); run(button, bd); by_button = x_at_11()
        key_bd()
        with ctx(bd):
            bpy.ops.animassist.timeline_slider("EXEC_DEFAULT", action="DRAG", value=preset, preset=True)
        results_bd[button] = (by_button, x_at_11())
    print("Breakdown button vs preset:", results_bd, flush=True)
    check("Breakdown presets -25/25/75/125 match Push/Pull Prev/Next",
          all(a == b for a, b in results_bd.values()) and results_bd["PUSH_PREV"][0] == -2.5)
    check("Block shows Breakdown presets -25..125; All shows 25/50/75 as ticks",
          model.stage_view(model.recommended(ACTIONS)["active"], "BLOCK")[1]["DRAG"]["presets"] == [-25., 25., 50., 75., 125.]
          and model.recommended(ACTIONS)["active"]["tools"]["DRAG"]["presets"] == [25., 50., 75.]
          and model.recommended(ACTIONS)["active"]["tools"]["DRAG"]["ticks"] is True)

    # Reduce and Ripple sliders: live preview, Esc restores, presets match the old buttons.
    session = sys.modules["B4_anim_assist.core.timeline_slider_session"]
    rr = bpy.data.objects.new("RR", None)
    scene.collection.objects.link(rr)
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    rr.select_set(True)
    bpy.context.view_layer.objects.active = rr

    def key_rr():
        rr.animation_data_clear()
        for frame in range(1, 31):
            rr.location.x = frame * 0.1 + (0.004 if frame % 2 else 0.0)  # near-straight line with tiny noise
            rr.keyframe_insert("location", index=0, frame=frame)
        scene.frame_set(10)

    def rr_frames():
        fc = next(f for f in get_fcurves(rr.animation_data.action, anim_data=rr.animation_data)
                  if f.data_path == "location" and f.array_index == 0)
        return [round(k.co.x, 3) for k in fc.keyframe_points]

    key_rr(); original = rr_frames()
    with ctx(rr):
        tx = session.capture(bpy.context, "REDUCE")
        tx.preview(0.05); previewed = rr_frames(); tx.cancel()
    check("Reduce slider previews fewer keys and Esc restores them",
          len(previewed) < len(original) and rr_frames() == original)
    key_rr(); run("REDUCE", rr); by_button = rr_frames()
    key_rr()
    with ctx(rr):
        bpy.ops.animassist.timeline_slider("EXEC_DEFAULT", action="REDUCE", value=0.01, preset=True)
    check("Reduce preset 0.01 matches the Reduce button", rr_frames() == by_button and len(by_button) < len(original))

    key_rr()
    with ctx(rr):
        tx = session.capture(bpy.context, "RIPPLE")
        tx.preview(3); moved = rr_frames(); tx.cancel()
    check("Ripple slider previews keys after the playhead moving 3 frames and Esc restores",
          moved[:10] == original[:10] and moved[10] == original[10] + 3 and rr_frames() == original)
    with ctx(rr):
        tx = session.capture(bpy.context, "RIPPLE")
        tx.preview(-10); clamped = rr_frames(); tx.cancel()
    check("Ripple earlier stops one frame after the playhead", clamped[10] == 11.0 and clamped[9] == 10.0)
    key_rr(); run("RIPPLE", rr); by_ripple = rr_frames()
    key_rr()
    with ctx(rr):
        bpy.ops.animassist.timeline_slider("EXEC_DEFAULT", action="RIPPLE", value=1, preset=True)
    check("Ripple preset 1 matches the Ripple button", rr_frames() == by_ripple and by_ripple != original)

    # Version B: one eye button shows and hides trails.
    p5mod = sys.modules["B4_anim_assist.operators.p5_overlay_ops"]
    before_trails = p5mod.trails_shown()
    run("TRAIL_TOGGLE", bd)
    after_once = p5mod.trails_shown()
    run("TRAIL_TOGGLE", bd)
    check("Trails toggle shows, then hides trails", before_trails is False and after_once is True
          and p5mod.trails_shown() is False)
    addon_utils.disable("B4_anim_assist", default_set=False)
except Exception:
    traceback.print_exc()
    results.append(("no exception", False))

failed = [n for n, ok in results if not ok]
print(f"RESULT {len(results) - len(failed)}/{len(results)} passed", flush=True)
sys.exit(1 if failed else 0)
