"""Real-GUI capture of the Timeline band per stage. Isolated user config; quits itself."""
import os
import traceback
from pathlib import Path

import addon_utils
import bpy

OUT = Path(os.environ["AA_STAGE_OUT"])
OUT.mkdir(parents=True, exist_ok=True)
log = open(OUT / "log.txt", "w", encoding="utf-8", buffering=1)
addon_utils.enable("B4_anim_assist", default_set=True, persistent=False)
bpy.context.preferences.use_preferences_save = False
bpy.context.preferences.view.show_splash = False

STAGES = ["ALL", "BLOCK", "SPLINE", "POLISH", "DELIVER"]
state = {"i": -1, "ticks": 0}


def timeline(window):
    return next((a for a in window.screen.areas if a.type == "DOPESHEET_EDITOR"
                 and a.spaces.active.mode == "TIMELINE"), None)


def setup():
    obj = bpy.data.objects.get("Cube") or bpy.context.view_layer.objects.active
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
    if area.height < 120:
        # Header-only factory Timeline: split the 3D viewport; the created lower
        # 240 px becomes the Timeline (Bforartists 5.2.0 keeps the original on top).
        view = max((a for a in window.screen.areas if a.type == "VIEW_3D"),
                   key=lambda a: a.width * a.height)
        before = {a.as_pointer() for a in window.screen.areas}
        with bpy.context.temp_override(window=window, area=view):
            bpy.ops.screen.area_split(direction="HORIZONTAL", factor=240 / view.height)
        lower = min((a for a in window.screen.areas if a.as_pointer() not in before), key=lambda a: a.y)
        area.type = "INFO"
        lower.type = "DOPESHEET_EDITOR"
        lower.spaces.active.mode = "TIMELINE"
        area = lower
    state["area"] = area.as_pointer()


def step():
    try:
        window = bpy.context.window_manager.windows[0]
        area = timeline(window)
        if state["i"] == -1:
            setup()
            state["i"] = 0
            return 1.5
        if state["i"] >= len(STAGES):
            # Settings surfaces with the Block stage: dialog, then gear popover.
            phase = state.setdefault("settings", 0)
            region = next(r for r in area.regions if r.type == "WINDOW")
            override = dict(window=window, screen=window.screen, area=area, region=region)
            if phase == 0:
                setattr(window.screen, "animassist_timeline_stage", "BLOCK")
                return_after = 1.0
                state["settings"] = 0.5
                return return_after
            elif phase == 0.5:
                with bpy.context.temp_override(**override):
                    bpy.ops.animassist.toolbar_settings("INVOKE_DEFAULT")
                state["settings"] = 1
                return 1.2
            elif phase == 1:
                with bpy.context.temp_override(window=window, screen=window.screen):
                    bpy.ops.screen.screenshot(filepath=str(OUT / "settings-dialog.png"))
                log.write("captured settings dialog\n")
                with bpy.context.temp_override(**override):
                    bpy.ops.wm.call_panel(name="ANIMASSIST_PT_timeline_quick_settings", keep_open=True)
            elif phase == 2:
                with bpy.context.temp_override(window=window, screen=window.screen):
                    bpy.ops.screen.screenshot(filepath=str(OUT / "gear-popover.png"))
                log.write("captured gear popover\n")
            else:
                log.write("done\n"); log.close()
                bpy.ops.wm.quit_blender()
                return None
            state["settings"] = phase + 1
            return 1.2
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
