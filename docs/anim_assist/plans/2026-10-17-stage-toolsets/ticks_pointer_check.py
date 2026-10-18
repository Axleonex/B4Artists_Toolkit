"""Real-GUI check: clicking a preset tick on a stage slider applies exactly that preset.

Run:  bforartists --factory-startup --enable-event-simulate --python ticks_pointer_check.py
with BLENDER_USER_SCRIPTS holding the package as B4_anim_assist and AA_STAGE_OUT set.
Block's Breakdown track spans -25 to 125 with ticks at -25/25/50/75/125: a simulated click
on a tick, between keys 0 (frame 1) and 10 (frame 21) at frame 11, must key that preset.
"""
import os
import sys
import traceback
from pathlib import Path

import addon_utils
import bpy

OUT = Path(os.environ["AA_STAGE_OUT"])
OUT.mkdir(parents=True, exist_ok=True)
log = open(OUT / "ticks-log.txt", "w", encoding="utf-8", buffering=1)
addon_utils.enable("B4_anim_assist", default_set=True, persistent=False)
bpy.context.preferences.use_preferences_save = False
bpy.context.preferences.view.show_splash = False
PROP = "animassist_timeline_stage"
results = []
state = {}


def check(name, ok):
    results.append((name, bool(ok)))
    log.write(("PASS " if ok else "FAIL ") + name + "\n")


def overlay():
    return sys.modules["B4_anim_assist.ui.timeline_overlay"]


def model():
    return sys.modules["B4_anim_assist.ui.timeline_config"]


def window():
    return bpy.context.window_manager.windows[0]


def timeline():
    return next(a for a in window().screen.areas
                if a.type == "DOPESHEET_EDITOR" and a.spaces.active.mode == "TIMELINE")


def region():
    return next(r for r in timeline().regions if r.type == "WINDOW")


def setup():
    win = window()
    small = timeline()
    view = max((a for a in win.screen.areas if a.type == "VIEW_3D"), key=lambda a: a.width * a.height)
    before = {a.as_pointer() for a in win.screen.areas}
    with bpy.context.temp_override(window=win, area=view):
        bpy.ops.screen.area_split(direction="HORIZONTAL", factor=240 / view.height)
    lower = min((a for a in win.screen.areas if a.as_pointer() not in before), key=lambda a: a.y)
    small.type = "INFO"
    lower.type = "DOPESHEET_EDITOR"
    lower.spaces.active.mode = "TIMELINE"
    obj = bpy.data.objects.new("Tick", None)
    bpy.context.scene.collection.objects.link(obj)
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    state["obj"] = obj
    setattr(win.workspace, PROP, "BLOCK")
    rekey()


def rekey():
    obj = state["obj"]
    obj.animation_data_clear()
    for frame, x in ((1, 0.0), (21, 10.0)):
        obj.location.x = x
        obj.keyframe_insert("location", index=0, frame=frame)
    bpy.context.scene.frame_set(11)


def value_at_11():
    from B4_anim_assist.core.fcurve_compat import get_fcurves
    obj = state["obj"]
    fc = next(f for f in get_fcurves(obj.animation_data.action, anim_data=obj.animation_data)
              if f.data_path == "location" and f.array_index == 0)
    return round(fc.evaluate(11), 3)


def tick_point(preset, low=-25., high=125.):
    with bpy.context.temp_override(window=window(), area=timeline(), region=region()):
        items = overlay()._items(bpy.context)[0]
        item = next(i for i in items if i[1] == "DRAG")
        scale = bpy.context.preferences.system.ui_scale
        track = overlay()._parts(item[3], item[2], scale)[0]
    x = track[0] + track[2] * (preset - low) / (high - low)
    state["kind"] = item[0]
    return dict(x=round(region().x + x), y=round(region().y + track[1] + track[3] / 2))


def click(preset, low=-25., high=125.):
    xy = tick_point(preset, low, high)
    win = window()
    win.event_simulate(type="MOUSEMOVE", value="NOTHING", **xy)
    win.event_simulate(type="LEFTMOUSE", value="PRESS", **xy)
    win.event_simulate(type="LEFTMOUSE", value="RELEASE", **xy)


def plan():
    yield setup, 1.5
    yield (lambda: check("Block shows Breakdown as an inline slider with ticks",
                         tick_point(50) and state["kind"] == "SLIDER")), 0.3
    for preset, expected in ((125, 12.5), (-25, -2.5), (50, 5.0), (75, 7.5)):
        yield rekey, 0.4
        yield (lambda p=preset: click(p)), 0.8
        yield (lambda p=preset, e=expected: (log.write(f"  tick {p}: key at frame 11 = {value_at_11()}\n"),
                                             check(f"Clicking the {p} tick keys {e}", value_at_11() == e))), 0.2
    # All's Recommended row: Breakdown 0-100 with ticks at 25/50/75.
    yield (lambda: setattr(window().workspace, PROP, "ALL")), 0.6
    yield rekey, 0.4
    yield (lambda: click(75, 0., 100.)), 0.8
    yield (lambda: check("All row: Breakdown is inline with ticks and the 75 tick keys 7.5",
                         state["kind"] == "SLIDER" and value_at_11() == 7.5)), 0.2
    yield (lambda: bpy.ops.screen.screenshot(filepath=str(OUT / "all-ticks.png"))), 0.5
    yield (lambda: (setattr(window().workspace, PROP, "BLOCK"),
                    bpy.ops.screen.screenshot(filepath=str(OUT / "block-ticks.png")))), 0.5


def runner():
    it = plan()

    def tick():
        try:
            fn, delay = next(it)
            fn()
            return delay
        except StopIteration:
            failed = [n for n, ok in results if not ok]
            log.write(f"RESULT {len(results) - len(failed)}/{len(results)} passed\n")
            log.close()
            bpy.ops.wm.quit_blender()
            return None
        except Exception:
            log.write(traceback.format_exc())
            log.close()
            bpy.ops.wm.quit_blender()
            return None
    return tick


bpy.app.timers.register(runner(), first_interval=2.0)
