"""Capture real sidebar layouts with native region resizing in the owned GUI."""
import bpy
import json
from pathlib import Path


def start(output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    area = max(bpy.context.screen.areas, key=lambda a: a.width * a.height)
    jobs = [(space, width) for space in ("NLA_EDITOR", "GRAPH_EDITOR", "DOPESHEET_EDITOR")
            for width in (220, 280, 360)]
    state = dict(index=0, phase="setup", attempts=0, results=[])

    def tick():
        try:
            if state["index"] >= len(jobs):
                return None
            space, width = jobs[state["index"]]
            if state["phase"] == "setup":
                area.type = space
                area.spaces.active.show_region_ui = True
                if space == "GRAPH_EDITOR":
                    area.spaces.active.mode = "FCURVES"
                if space == "DOPESHEET_EDITOR":
                    area.spaces.active.mode = "DOPESHEET_EDITOR"
                area.spaces.active.dopesheet.show_only_selected = True
                owner = bpy.data.objects["Correction XYZ" if space == "NLA_EDITOR" else "Keying Mesh"]
                for obj in bpy.context.selected_objects:
                    obj.select_set(False)
                owner.select_set(True)
                bpy.context.view_layer.objects.active = owner
                bpy.context.scene.frame_set(10)
                state["phase"] = "frame"
                return 1
            region = next(r for r in area.regions if r.type == "WINDOW")
            ui = next(r for r in area.regions if r.type == "UI")
            if state["phase"] == "frame":
                ui.active_panel_category = "Anim Assist"
                with bpy.context.temp_override(area=area, region=region):
                    if space == "NLA_EDITOR":
                        owner = bpy.context.object
                        owner.animation_data.nla_tracks.active = owner.animation_data.nla_tracks[-1]
                        bpy.ops.nla.view_all()
                        bpy.ops.nla.click_select(mouse_x=500, mouse_y=region.height-88, deselect_all=True)
                    elif space == "GRAPH_EDITOR":
                        bpy.ops.graph.select_all(action="SELECT")
                        bpy.ops.graph.view_all()
                    else:
                        bpy.ops.anim.channels_expand(all=True)
                        bpy.ops.action.select_all(action="SELECT")
                        bpy.ops.action.view_all()
                state["phase"] = "resize"
                return 1
            if state["phase"] in {"press", "move", "release"}:
                window = bpy.context.window
                x, y, end = state["drag"]
                if state["phase"] == "press":
                    window.event_simulate(type="LEFTMOUSE", value="PRESS", x=x, y=y)
                    state["phase"] = "move"
                elif state["phase"] == "move":
                    window.event_simulate(type="MOUSEMOVE", value="NOTHING", x=end, y=y)
                    state["phase"] = "release"
                else:
                    window.event_simulate(type="LEFTMOUSE", value="RELEASE", x=end, y=y)
                    state["phase"] = "resize"
                    state["attempts"] += 1
                return .5
            if abs(ui.width - width) > 2 and state["attempts"] < 4:
                window = bpy.context.window
                x, y = ui.x, ui.y + 200
                end = x + ui.width - width
                window.event_simulate(type="MOUSEMOVE", value="NOTHING", x=x, y=y)
                state.update(phase="press", drag=(x, y, end))
                return .5
            filename = f"{space.lower()}-{width}.png"
            with bpy.context.temp_override(area=area, region=region):
                bpy.ops.screen.screenshot_area(filepath=str(output / filename))
            state["results"].append(dict(editor=space, requested_width=width,
                measured_width=ui.width, ui_scale=bpy.context.preferences.system.ui_scale,
                width_matches=abs(ui.width-width) <= 2, image=filename))
            (output / "screenshots.json").write_text(json.dumps(state["results"], indent=2))
            state.update(index=state["index"]+1, phase="setup", attempts=0)
            return 1
        except Exception:
            import traceback
            (output / "error.txt").write_text(traceback.format_exc())
            return None
    bpy.app.timers.register(tick, first_interval=1)
    return tick
