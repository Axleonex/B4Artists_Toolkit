"""GUI acceptance check: the shelves start wide enough (owner, 2026-10-10).

Needs a real window, so it is not part of run_headless.py. Run it with the add-on installed in a
scripts folder Bforartists can see, from the bonecraft folder:

    BLENDER_USER_SCRIPTS=<folder holding addons/boneforge> bforartists --factory-startup --python tests/gui_shelf_width.py

It writes PASS or FAIL lines to ``gui_shelf_width.txt`` next to this file and quits.
"""
import os

import bpy

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gui_shelf_width.txt")
lines = []


def check(ok, what):
    lines.append(("PASS " if ok else "FAIL ") + what)


def regions():
    win = bpy.context.window_manager.windows[0]
    area = max((a for a in win.screen.areas if a.type == 'VIEW_3D'), key=lambda a: a.width * a.height)
    return win, area, {r.type: r for r in area.regions if r.type in ("TOOLS", "UI")}


def step2():
    from boneforge.core import shelf_width
    win, area, regs = regions()
    scale = bpy.context.preferences.system.ui_scale
    check(regs["TOOLS"].width >= 240 * scale, f"left shelf widened: {regs['TOOLS'].width} px")
    check(regs["UI"].width >= 260 * scale, f"right sidebar widened: {regs['UI'].width} px")
    # the user drags it narrower: a second pass leaves their choice alone
    shelf_width.set_width(area, regs["TOOLS"], 150)
    shelf_width.widen_all()
    bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=2)
    win, area, regs = regions()
    check(regs["TOOLS"].width < 240 * scale, f"a shelf made narrower by hand stays so: {regs['TOOLS'].width} px")
    open(OUT, "w").write("\n".join(lines) + "\n")
    bpy.ops.wm.quit_blender()


def step1():
    win, area, regs = regions()
    area.spaces.active.show_region_toolbar = True
    area.spaces.active.show_region_ui = True
    bpy.app.timers.register(step2, first_interval=3.0)


bpy.ops.preferences.addon_enable(module="boneforge")
bpy.app.timers.register(step1, first_interval=1.0)
