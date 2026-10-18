"""Real-GUI pointer check of the stage dropdown (simulated mouse and keyboard events).

Run:  bforartists --factory-startup --enable-event-simulate --python dropdown_pointer_check.py
with BLENDER_USER_SCRIPTS holding the package as B4_anim_assist and AA_STAGE_OUT set.
Covers: one click opens and it stays open; hovering keeps it open; clicking a stage
switches and closes; clicking the stage button again, the Timeline canvas, another
editor, or pressing Esc closes it without changing the stage or the frame.
"""
import os
import sys
import traceback
from pathlib import Path

import addon_utils
import bpy

OUT = Path(os.environ["AA_STAGE_OUT"])
OUT.mkdir(parents=True, exist_ok=True)
log = open(OUT / "pointer-log.txt", "w", encoding="utf-8", buffering=1)
addon_utils.enable("B4_anim_assist", default_set=True, persistent=False)
bpy.context.preferences.use_preferences_save = False
bpy.context.preferences.view.show_splash = False
PROP = "animassist_timeline_stage"
results = []


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
    # A narrower Timeline (about 900 px) also exercises the stage list on a tight row.
    before = {a.as_pointer() for a in win.screen.areas}
    with bpy.context.temp_override(window=win, area=lower):
        bpy.ops.screen.area_split(direction="VERTICAL", factor=900 / lower.width)
    for area in win.screen.areas:
        if area.as_pointer() not in before:
            area.type = "INFO"
    bpy.context.scene.frame_set(30)


def layout():
    with bpy.context.temp_override(window=window(), area=timeline(), region=region()):
        items, band = overlay()._items(bpy.context)
        menu = overlay()._menu_items(bpy.context, items, band)
    return items, band, menu


def centre(rect):
    x, y, w, h = rect
    return dict(x=round(region().x + x + w / 2), y=round(region().y + y + h / 2))


def ev(kind, value="PRESS", **xy):
    window().event_simulate(type=kind, value=value, **xy)


def click_at(xy):
    ev("MOUSEMOVE", "NOTHING", **xy)
    ev("LEFTMOUSE", "PRESS", **xy)
    ev("LEFTMOUSE", "RELEASE", **xy)


def is_open():
    return overlay()._stage_menu.get(window().as_pointer()) == timeline().as_pointer()


def stage():
    return getattr(window().workspace, PROP)


def button():
    return centre(layout()[0][0][3])


def item(key):
    return centre(next(m for m in layout()[2] if m[1] == key)[3])


def shot(name):
    with bpy.context.temp_override(window=window(), screen=window().screen):
        bpy.ops.screen.screenshot(filepath=str(OUT / name))


state = {}


def plan():
    yield setup, 1.5
    yield (lambda: (setattr(window().workspace, PROP, "ALL"),
                    check("Compact stage button shown", layout()[0][0][0] == "STAGE_CYCLE"))), 0.5
    # One click opens; it stays open after the release.
    yield (lambda: click_at(button())), 0.6
    yield (lambda: check("One click opens the dropdown and it stays open", is_open())), 0.2
    yield (lambda: ev("MOUSEMOVE", "NOTHING", **item("POLISH"))), 0.6
    yield (lambda: (check("Hovering a stage keeps it open and highlights it",
                          is_open() and overlay()._hover.get(window().as_pointer())
                          == (timeline().as_pointer(), "STAGE_ITEM", "POLISH")),
                    shot("dropdown-hover.png"))), 0.4
    yield (lambda: click_at(item("POLISH"))), 0.6
    yield (lambda: check("Clicking a stage switches to it and closes", stage() == "POLISH" and not is_open())), 0.2
    # Clicking the stage button again closes without changing the stage.
    yield (lambda: click_at(button())), 0.6
    yield (lambda: click_at(button())), 0.6
    yield (lambda: check("Clicking the stage button again closes it", not is_open() and stage() == "POLISH")), 0.2
    # Clicking the Timeline canvas closes without moving the frame.
    yield (lambda: click_at(button())), 0.6
    yield (lambda: state.__setitem__("frame", bpy.context.scene.frame_current)), 0.1
    yield (lambda: click_at(dict(x=region().x + region().width // 2,
                                 y=region().y + region().height - 30))), 0.6
    yield (lambda: check("Clicking the Timeline closes it without scrubbing",
                         not is_open() and stage() == "POLISH"
                         and bpy.context.scene.frame_current == state["frame"])), 0.2
    # Clicking another editor closes it.
    yield (lambda: click_at(button())), 0.6
    yield (lambda: (lambda v: click_at(dict(x=v.x + v.width // 2, y=v.y + v.height // 2)))(
        max((a for a in window().screen.areas if a.type == "VIEW_3D"), key=lambda a: a.width * a.height))), 0.6
    yield (lambda: check("Clicking another editor closes it", not is_open())), 0.2
    # Esc closes it.
    yield (lambda: click_at(button())), 0.6
    yield (lambda: ev("MOUSEMOVE", "NOTHING", **button())), 0.2
    yield (lambda: (ev("ESC", "PRESS"), ev("ESC", "RELEASE"))), 0.6
    yield (lambda: check("Esc closes it", not is_open() and stage() == "POLISH")), 0.2


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
