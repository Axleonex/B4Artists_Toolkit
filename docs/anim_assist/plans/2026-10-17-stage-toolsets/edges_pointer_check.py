"""Real-GUI check: the row clears the Timeline scrollbar and Blender's area corners.

Run:  bforartists --factory-startup --enable-event-simulate --python edges_pointer_check.py
with BLENDER_USER_SCRIPTS holding the package as B4_anim_assist and AA_STAGE_OUT set.
With the channel list closed and a wide Timeline (stage tabs shown), the row sits above
the horizontal scrollbar strip, its first and last buttons are inset from the area's
corners, and clicks near the outer edge of the first tab and the last button still work.
"""
import os
import sys
import traceback
from pathlib import Path

import addon_utils
import bpy

OUT = Path(os.environ["AA_STAGE_OUT"])
OUT.mkdir(parents=True, exist_ok=True)
log = open(OUT / "edges-log.txt", "w", encoding="utf-8", buffering=1)
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
    lower.spaces.active.show_region_channels = False  # the "side menu" closed, as reported
    setattr(win.workspace, PROP, "ALL")


def items():
    with bpy.context.temp_override(window=window(), area=timeline(), region=region()):
        return overlay()._items(bpy.context)


def plan():
    yield setup, 1.5

    def geometry():
        its, band = items()
        reg, area = region(), timeline()
        scale = bpy.context.preferences.system.ui_scale
        first, last = its[0], its[-1]
        state.update(first=first, last=last, band=band, scale=scale)
        log.write(f"  region x={reg.x} w={reg.width}; area x={area.x} w={area.width}; band y={band[1]:.0f}; "
                  f"first {first[0]} x={first[3][0]:.0f}; last {last[0]} right={last[3][0] + last[3][2]:.0f}\n")
        check("Channel list closed: the row reaches the area's left edge", reg.x <= area.x + 1)
        check("The row sits above the scrollbar strip", band[1] >= overlay().SCROLLBAR_LIFT * scale - .5)
        check("The first button is inset from the left corner", first[3][0] >= overlay().CORNER_INSET * scale - .5)
        check("The last button is inset from the right corner",
              last[3][0] + last[3][2] <= reg.width - overlay().CORNER_INSET * scale + .5)
        check("Stage tabs show on this wide Timeline", first[0] == "STAGE")

    yield geometry, 0.2
    # Click 3 px inside the first tab's outer edge: it must switch the stage, not start a corner drag.
    def click_edge():
        first = next(i for i in items()[0] if i[0] == "STAGE" and i[1] == "BLOCK")
        x, y, w, h = first[3]
        xy = dict(x=round(region().x + x + 3), y=round(region().y + y + h / 2))
        win = window()
        win.event_simulate(type="MOUSEMOVE", value="NOTHING", **xy)
        win.event_simulate(type="LEFTMOUSE", value="PRESS", **xy)
        win.event_simulate(type="LEFTMOUSE", value="RELEASE", **xy)

    def click_first_edge():
        first = items()[0][0]
        x, y, w, h = first[3]
        xy = dict(x=round(region().x + x + 2), y=round(region().y + y + 3))
        win = window()
        win.event_simulate(type="MOUSEMOVE", value="NOTHING", **xy)
        win.event_simulate(type="LEFTMOUSE", value="PRESS", **xy)
        win.event_simulate(type="LEFTMOUSE", value="RELEASE", **xy)
        state["first_key"] = first[1]

    yield click_edge, 0.6
    yield (lambda: check("A click near a tab's edge switches the stage",
                         getattr(window().workspace, PROP) == "BLOCK")), 0.1
    yield (lambda: setattr(window().workspace, PROP, "SPLINE")), 0.4
    yield click_first_edge, 0.6
    yield (lambda: check("A click in the bottom-left corner of the first tab selects it",
                         getattr(window().workspace, PROP) == state["first_key"]
                         and len(window().screen.areas) == state.setdefault("areas", len(window().screen.areas)))), 0.1
    # Pointer near the bottom so Blender shows the scrollbar, then capture.
    yield (lambda: window().event_simulate(type="MOUSEMOVE", value="NOTHING",
                                           x=region().x + region().width // 2, y=region().y + 6)), 0.6
    yield (lambda: bpy.ops.screen.screenshot(filepath=str(OUT / "edges.png"))), 0.4


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
