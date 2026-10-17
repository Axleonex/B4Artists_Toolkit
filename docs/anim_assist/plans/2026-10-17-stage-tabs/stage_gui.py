"""Real-GUI capture of the Timeline band per stage. Isolated user config; quits itself."""
import os
import traceback
from pathlib import Path

import addon_utils
import bpy

OUT = Path(os.environ["AA_STAGE_OUT"])
OUT.mkdir(parents=True, exist_ok=True)
log = open(OUT / "log.txt", "w", encoding="utf-8")
addon_utils.enable("B4_anim_assist", default_set=True, persistent=False)
bpy.context.preferences.use_preferences_save = False

STAGES = ["ALL", "BLOCK", "SPLINE", "POLISH", "DELIVER"]
state = {"i": -1, "ticks": 0}


def timeline(window):
    return next((a for a in window.screen.areas if a.type == "DOPESHEET_EDITOR"
                 and a.spaces.active.mode == "TIMELINE"), None)


def setup():
    obj = bpy.context.view_layer.objects.active or next(iter(bpy.data.objects), None)
    if obj:
        for frame, x in ((1, 0), (12, 2), (24, 0)):
            obj.location.x = x
            obj.keyframe_insert("location", index=0, frame=frame)
    window = bpy.context.window_manager.windows[0]
    area = timeline(window)
    if area is None:
        area = min(window.screen.areas, key=lambda a: a.y)
        area.type = "DOPESHEET_EDITOR"
        area.spaces.active.mode = "TIMELINE"
    log.write(f"timeline {area.width}x{area.height}\n")
    if area.height < 140:
        with bpy.context.temp_override(window=window, area=area):
            result = bpy.ops.screen.area_move(x=area.x + area.width // 2, y=area.y + area.height,
                                              delta=140 - area.height)
        log.write(f"area_move {result}\n")


def step():
    try:
        window = bpy.context.window_manager.windows[0]
        area = timeline(window)
        if state["i"] == -1:
            setup()
            state["i"] = 0
            return 1.5
        if state["i"] >= len(STAGES):
            log.write("done\n"); log.close()
            bpy.ops.wm.quit_blender()
            return None
        stage = STAGES[state["i"]]
        if state["ticks"] == 0:
            setattr(window.screen, "animassist_timeline_stage", stage)
            area.tag_redraw()
            state["ticks"] = 1
            return 0.6
        with bpy.context.temp_override(window=window, screen=window.screen, area=area):
            bpy.ops.screen.screenshot_area(filepath=str(OUT / f"stage-{stage.lower()}.png"))
        log.write(f"captured {stage} at {area.width}x{area.height}\n")
        state["i"] += 1
        state["ticks"] = 0
        return 0.3
    except Exception:
        log.write(traceback.format_exc()); log.close()
        bpy.ops.wm.quit_blender()
        return None


bpy.app.timers.register(step, first_interval=2.0)
