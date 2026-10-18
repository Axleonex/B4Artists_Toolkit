"""Real-GUI check: row popups stay open after the click is released.

Run:  bforartists --factory-startup --enable-event-simulate --python popups_pointer_check.py
with BLENDER_USER_SCRIPTS holding the package as B4_anim_assist and AA_STAGE_OUT set.
Family and More lists open on one click and stay open while the pointer moves, even over
another editor; More appears only when tools did not fit, as "+N", and lists just those; an item runs and closes; the same button, the Timeline, another editor or
Esc closes. A clicked popout slider stays open; double-click or a click away applies, Esc
cancels.
"""
import os
import sys
import traceback
from pathlib import Path

import addon_utils
import bpy

OUT = Path(os.environ["AA_STAGE_OUT"])
OUT.mkdir(parents=True, exist_ok=True)
log = open(OUT / "popups-log.txt", "w", encoding="utf-8", buffering=1)
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


def sliders():
    return sys.modules["B4_anim_assist.operators.timeline_slider_ops"]


def window():
    return bpy.context.window_manager.windows[0]


def timeline():
    return next(a for a in window().screen.areas
                if a.type == "DOPESHEET_EDITOR" and a.spaces.active.mode == "TIMELINE")


def region():
    return next(r for r in timeline().regions if r.type == "WINDOW")


def view3d():
    return max((a for a in window().screen.areas if a.type == "VIEW_3D"), key=lambda a: a.width * a.height)


def setup():
    win = window()
    small = timeline()
    view = view3d()
    before = {a.as_pointer() for a in win.screen.areas}
    with bpy.context.temp_override(window=win, area=view):
        bpy.ops.screen.area_split(direction="HORIZONTAL", factor=240 / view.height)
    lower = min((a for a in win.screen.areas if a.as_pointer() not in before), key=lambda a: a.y)
    small.type = "INFO"
    lower.type = "DOPESHEET_EDITOR"
    lower.spaces.active.mode = "TIMELINE"
    obj = bpy.data.objects.new("Pop", None)
    bpy.context.scene.collection.objects.link(obj)
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    for frame, x in ((1, 0.0), (11, 4.0), (21, 10.0)):
        obj.location.x = x
        obj.keyframe_insert("location", index=0, frame=frame)
    state["obj"] = obj
    bpy.context.scene.frame_set(11)
    setattr(win.workspace, PROP, "ALL")


def items():
    with bpy.context.temp_override(window=window(), area=timeline(), region=region()):
        return overlay()._items(bpy.context)


def rows():
    with bpy.context.temp_override(window=window(), area=timeline(), region=region()):
        its, band = overlay()._items(bpy.context)
        return overlay()._list_layout(bpy.context, its, band)


def at(rect):
    x, y, w, h = rect
    return dict(x=round(region().x + x + w / 2), y=round(region().y + y + h / 2))


def item_xy(kind, key):
    return at(next(i for i in items()[0] if i[0] == kind and i[1].split(":", 1)[0] == key)[3])


def row_xy(kind, key):
    return at(next(r for r in rows() if r[0] == kind and r[1] == key)[3])


def ev(kind, value="PRESS", **xy):
    window().event_simulate(type=kind, value=value, **xy)


def click(xy):
    ev("MOUSEMOVE", "NOTHING", **xy)
    ev("LEFTMOUSE", "PRESS", **xy)
    ev("LEFTMOUSE", "RELEASE", **xy)


def list_view():
    st = overlay()._row_menu.get(window().as_pointer())
    return st["view"] if st else None


def empty_timeline():
    return dict(x=region().x + region().width // 2, y=region().y + region().height - 40)


def in_view3d():
    v = view3d()
    return dict(x=v.x + v.width // 2, y=v.y + v.height // 2)


def frames():
    from B4_anim_assist.core.fcurve_compat import get_fcurves
    obj = bpy.data.objects["Pop"]  # undo replaces the object, so look it up by name
    fc = next(f for f in get_fcurves(obj.animation_data.action, anim_data=obj.animation_data)
              if f.data_path == "location" and f.array_index == 0)
    return [round(k.co.x, 2) for k in fc.keyframe_points]


def press(xy):
    ev("MOUSEMOVE", "NOTHING", **xy)
    ev("LEFTMOUSE", "PRESS", **xy)


def release(xy):
    ev("LEFTMOUSE", "RELEASE", **xy)


def hidden_tools():
    with bpy.context.temp_override(window=window(), area=timeline(), region=region()):
        its, _band = overlay()._items(bpy.context)
        return overlay()._row_hidden_tools(bpy.context, its)


def overflow_all():
    """Show every Pose, Bake and Motion tool on the All row so some cannot fit."""
    model = sys.modules["B4_anim_assist.ui.timeline_config"]
    settings = sys.modules["B4_anim_assist.ui.timeline_settings"]
    catalog = sys.modules["B4_anim_assist.ui.timeline_catalog"]
    data = settings.record(bpy.context)
    for key, _label, actions in catalog.GROUPS:
        if key in {"pose", "bake", "motion"}:
            for action in actions:
                if action:
                    model.set_stage_tool(data, "ALL", action, mode="BUTTON")
    settings.write(bpy.context, data)


def active_slider():
    return sliders()._active.get(window().as_pointer())


def plan():
    yield setup, 1.5
    # Family list: one click opens and it stays open after release and while moving.
    yield (lambda: click(item_xy("MENU", "keys"))), 0.6
    yield (lambda: check("Clicking a family opens its list and it stays after release",
                         list_view() == ("FAMILY", "keys"))), 0.1
    yield (lambda: ev("MOUSEMOVE", "NOTHING", **empty_timeline())), 0.3
    yield (lambda: ev("MOUSEMOVE", "NOTHING", **in_view3d())), 0.4
    yield (lambda: check("The list stays open while the pointer moves, even over another editor",
                         list_view() == ("FAMILY", "keys"))), 0.1
    yield (lambda: click(row_xy("RUN", "ALL"))), 0.6
    yield (lambda: check("Clicking an item runs it and closes the list", list_view() is None)), 0.1
    # Ways to close.
    yield (lambda: click(item_xy("MENU", "keys"))), 0.5
    yield (lambda: click(item_xy("MENU", "keys"))), 0.5
    yield (lambda: check("Clicking the same family again closes it", list_view() is None)), 0.1
    yield (lambda: click(item_xy("MENU", "keys"))), 0.5
    yield (lambda: click(empty_timeline())), 0.5
    yield (lambda: check("Clicking the Timeline closes it", list_view() is None)), 0.1
    yield (lambda: click(item_xy("MENU", "keys"))), 0.5
    yield (lambda: click(in_view3d())), 0.5
    yield (lambda: check("Clicking another editor closes it", list_view() is None)), 0.1
    yield (lambda: click(item_xy("MENU", "keys"))), 0.5
    yield (lambda: (ev("ESC", "PRESS"), ev("ESC", "RELEASE"))), 0.5
    yield (lambda: check("Esc closes it", list_view() is None)), 0.1
    # Another family button switches lists.
    yield (lambda: click(item_xy("MENU", "keys"))), 0.5
    yield (lambda: click(item_xy("MENU", "pose"))), 0.5
    yield (lambda: check("Clicking another family switches to its list", list_view() == ("FAMILY", "pose"))), 0.1
    yield (lambda: bpy.ops.screen.screenshot(filepath=str(OUT / "family-list.png"))), 0.3
    yield (lambda: click(item_xy("MENU", "pose"))), 0.5
    # More has one job: it appears only when tools did not fit, as "+N", and lists them.
    yield (lambda: check("Everything fits on the wide All row, so there is no More button",
                         not any(i[0] == "MORE" for i in items()[0]))), 0.1
    yield overflow_all, 0.6

    def more_label():
        found = [i for i in items()[0] if i[0] == "MORE"]
        state["more"] = found[0][2] if found else ""
        return state["more"]
    yield (lambda: check("With more tools than fit, More shows how many did not fit",
                         more_label().startswith("+") and int(more_label()[1:]) == len(hidden_tools()))), 0.1
    yield (lambda: click(item_xy("MORE", ""))), 0.5
    yield (lambda: check("More opens and stays open", list_view() == ("MORE", ""))), 0.1
    yield (lambda: bpy.ops.screen.screenshot(filepath=str(OUT / "more-list.png"))), 0.3
    yield (lambda: check("More lists exactly the tools that did not fit, and no families",
                         [r[1] for r in rows() if r[0] == "RUN"] == hidden_tools()
                         and not any(r[0] == "FAMILY" for r in rows()))), 0.1
    yield (lambda: click(empty_timeline())), 0.5
    yield (lambda: bpy.ops.animassist.restore_toolbar()), 0.6
    # Find is a magnifier icon; with nothing typed it browses tools by family.
    yield (lambda: check("Find is an icon-only button", any(i[0] == "SEARCH" and i[2] == "" for i in items()[0]))), 0.1
    yield (lambda: click(item_xy("SEARCH", ""))), 1.0
    yield (lambda: bpy.ops.screen.screenshot(filepath=str(OUT / "find-browse.png"))), 0.4
    yield (lambda: (ev("ESC", "PRESS"), ev("ESC", "RELEASE"))), 0.6
    # Popout slider: a click keeps it open; double-click applies.
    yield (lambda: state.__setitem__("before", frames())), 0.1
    yield (lambda: press(item_xy("POPOUT", "SCALE_DRAG"))), 0.3
    yield (lambda: release(item_xy("POPOUT", "SCALE_DRAG"))), 0.5
    yield (lambda: check("Clicking a popout slider keeps it open after release",
                         active_slider() is not None and getattr(active_slider(), "_sticky", False))), 0.1
    yield (lambda: bpy.ops.screen.screenshot(filepath=str(OUT / "popout-open.png"))), 0.3

    def press_track(fraction):
        op = active_slider()
        tx, ty, tw, th = op._pop_track
        xy = dict(x=round(region().x + tx + tw * fraction), y=round(region().y + ty + th / 2))
        ev("MOUSEMOVE", "NOTHING", **xy); ev("LEFTMOUSE", "PRESS", **xy)
        state["track_xy"] = xy

    def lift():
        ev("LEFTMOUSE", "RELEASE", **state["track_xy"])

    yield (lambda: press_track(.8)), 0.3
    yield lift, 0.4
    yield (lambda: check("Adjusting on the popout keeps it open", active_slider() is not None)), 0.1
    # The simulator cannot send a real double-click, so ask the popout how it treats one.
    def double_click_answer():
        from types import SimpleNamespace
        op = active_slider()
        bx, by, bw, bh = op._pop_box
        fake = SimpleNamespace(type="LEFTMOUSE", value="DOUBLE_CLICK", mouse_region_x=bx + bw / 2, mouse_region_y=by + bh / 2)
        state["dbl"] = op._sticky_event(fake)

    yield double_click_answer, 0.1
    yield (lambda: check("A double-click inside the popout applies", state["dbl"] == "APPLY")), 0.1
    yield (lambda: (ev("RET", "PRESS"), ev("RET", "RELEASE"))), 0.6
    yield (lambda: (log.write(f"  frames before {state['before']} after {frames()}\n"),
                    check("Applying closes the popout and keeps the adjustment",
                          active_slider() is None and frames() != state["before"]))), 0.2
    # Click away applies; Esc cancels.
    yield (lambda: bpy.ops.ed.undo()), 0.5
    yield (lambda: state.__setitem__("before", frames())), 0.1
    yield (lambda: press(item_xy("POPOUT", "SCALE_DRAG"))), 0.3
    yield (lambda: release(item_xy("POPOUT", "SCALE_DRAG"))), 0.5
    yield (lambda: press_track(.2)), 0.3
    yield lift, 0.4
    yield (lambda: press(empty_timeline())), 0.3
    yield (lambda: release(empty_timeline())), 0.5
    yield (lambda: check("Clicking away applies and closes the popout",
                         active_slider() is None and frames() != state["before"])), 0.2
    yield (lambda: state.__setitem__("before", frames())), 0.1
    yield (lambda: press(item_xy("POPOUT", "SCALE_DRAG"))), 0.3
    yield (lambda: release(item_xy("POPOUT", "SCALE_DRAG"))), 0.5
    yield (lambda: press_track(.9)), 0.3
    yield lift, 0.4
    yield (lambda: (ev("ESC", "PRESS"), ev("ESC", "RELEASE"))), 0.6
    yield (lambda: check("Esc cancels the popout and restores the keys",
                         active_slider() is None and frames() == state["before"])), 0.2


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
