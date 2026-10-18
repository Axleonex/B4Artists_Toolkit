"""Real-GUI check: Toolbar Settings edits one row at a time and applies changes live.

Run:  bforartists --factory-startup --enable-event-simulate --python settings_live_check.py
with BLENDER_USER_SCRIPTS holding the package as B4_anim_assist and AA_STAGE_OUT set.
With the panel open: the Row dropdown shows the Timeline's row; hiding a tool removes it
from the Timeline row at once; choosing another row switches the Timeline and the list; the
panel stays open while the pointer moves away; a click outside or Esc closes it and keeps
the changes.
"""
import os
import sys
import traceback
from pathlib import Path

import addon_utils
import bpy

OUT = Path(os.environ["AA_STAGE_OUT"])
OUT.mkdir(parents=True, exist_ok=True)
log = open(OUT / "settings-log.txt", "w", encoding="utf-8", buffering=1)
addon_utils.enable("B4_anim_assist", default_set=True, persistent=False)
bpy.context.preferences.use_preferences_save = False
bpy.context.preferences.view.show_splash = False
PROP = "animassist_timeline_stage"
results = []
state = {}


def check(name, ok):
    results.append((name, bool(ok)))
    log.write(("PASS " if ok else "FAIL ") + name + "\n")


def mod(name):
    return sys.modules["B4_anim_assist." + name]


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
    setattr(win.workspace, PROP, "BLOCK")


def row_keys():
    with bpy.context.temp_override(window=window(), area=timeline(), region=region()):
        return {i[1].split(":", 1)[0] for i in mod("ui.timeline_overlay")._items(bpy.context)[0]}


def stored_block():
    prefs = mod("prefs")
    return prefs.timeline_record(prefs.get_prefs(bpy.context))["active"]["stages"]["BLOCK"]["order"]


def open_dialog():
    r = region()
    xy = dict(x=r.x + r.width // 2, y=r.y + r.height // 2)
    window().event_simulate(type="MOUSEMOVE", value="NOTHING", **xy)
    with bpy.context.temp_override(window=window(), area=timeline(), region=r):
        bpy.ops.animassist.toolbar_settings("INVOKE_DEFAULT")


def dialog():
    return mod("ui.timeline_settings")._editors.get(window().as_pointer())


def plan():
    yield setup, 1.5
    yield (lambda: check("Range shows on the Block row first", "RANGE" in row_keys())), 0.2
    yield open_dialog, 1.0
    yield (lambda: check("Toolbar Settings opens on the Timeline's row (Block)",
                         dialog() is not None and dialog().row == "BLOCK"
                         and {e.family for e in dialog().entries} == {"tween", "keys"})), 0.2
    yield (lambda: bpy.ops.screen.screenshot(filepath=str(OUT / "settings-block.png"))), 0.4

    def hide_range():
        with bpy.context.temp_override(window=window()):
            next(e for e in dialog().entries if e.action == "RANGE").mode = "HIDDEN"
    yield hide_range, 0.6
    yield (lambda: check("Hiding a tool updates the Timeline row while the dialog is open",
                         dialog() is not None and "RANGE" not in row_keys() and "RANGE" not in stored_block())), 0.2

    def pick_spline():
        with bpy.context.temp_override(window=window(), workspace=window().workspace):
            dialog().row = "SPLINE"
    yield pick_spline, 0.6
    yield (lambda: check("Choosing the Spline row switches the Timeline and the list",
                         getattr(window().workspace, PROP) == "SPLINE"
                         and {e.family for e in dialog().entries} == {"curves", "motion"})), 0.2
    yield (lambda: bpy.ops.screen.screenshot(filepath=str(OUT / "settings-spline.png"))), 0.4
    def move_away():
        for x, y in ((600, 500), (900, 300), (1500, 150), (100, 900)):
            window().event_simulate(type="MOUSEMOVE", value="NOTHING", x=x, y=y)
    yield move_away, 0.8
    yield (lambda: check("Toolbar Settings stays open while the pointer moves away", dialog() is not None)), 0.2

    def click_outside():
        r = region()
        xy = dict(x=r.x + 30, y=r.y + 30)
        window().event_simulate(type="MOUSEMOVE", value="NOTHING", **xy)
        window().event_simulate(type="LEFTMOUSE", value="PRESS", **xy)
        window().event_simulate(type="LEFTMOUSE", value="RELEASE", **xy)
    yield click_outside, 0.8
    yield (lambda: check("A click outside closes it and keeps the change",
                         dialog() is None and "RANGE" not in stored_block())), 0.2
    yield open_dialog, 1.0
    yield (lambda: (window().event_simulate(type="ESC", value="PRESS"),
                    window().event_simulate(type="ESC", value="RELEASE"))), 0.8
    yield (lambda: check("Esc closes it and keeps the change", dialog() is None and "RANGE" not in stored_block())), 0.2


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
