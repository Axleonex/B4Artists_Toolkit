"""Background Bforartists check of 12.10.0 stage toolsets (settings, pin, tool settings).

Run with BLENDER_USER_SCRIPTS pointing at a folder whose addons/ holds the package
as B4_anim_assist:  bforartists --background --factory-startup --python toolset_check.py
"""
import copy
import sys
import traceback
from types import SimpleNamespace

import addon_utils
import bpy

PROP = "animassist_timeline_stage"
results = []


def check(name, condition):
    results.append((name, bool(condition)))
    print(("PASS " if condition else "FAIL ") + name, flush=True)


class Rec:
    def __init__(self):
        object.__setattr__(self, "events", [])

    def __getattr__(self, name):
        def call(*args, **kwargs):
            self.events.append((name, args, kwargs))
            return SimpleNamespace() if name in {"operator", "popover"} else self
        return call

    def __setattr__(self, name, value):
        pass


class Entries(list):
    def add(self):
        item = SimpleNamespace(name="", action="", family="", mode="BUTTON", label_mode="LABEL", width=120.)
        self.append(item)
        return item


try:
    addon_utils.enable("B4_anim_assist", default_set=True, persistent=False)
    pkg = sys.modules["B4_anim_assist"]
    model = sys.modules["B4_anim_assist.ui.timeline_config"]
    settings = sys.modules["B4_anim_assist.ui.timeline_settings"]
    from B4_anim_assist.prefs import get_prefs, timeline_record
    from B4_anim_assist.ui.timeline_catalog import ACTIONS
    prefs = get_prefs(bpy.context)
    check("Add-on enabled with preferences", prefs is not None)
    timeline_record(prefs, initialize=True)
    check("Fresh record is schema 2 with stages", '"schema_version":2' in prefs.timeline_layouts_json
          and timeline_record(prefs)["active"]["stages"]["BLOCK"] == model.stage_default("BLOCK"))

    space, screen, area = next((w, s, a) for w in bpy.data.workspaces for s in w.screens for a in s.areas
                               if a.type == "DOPESHEET_EDITOR" and a.spaces.active.mode == "TIMELINE")

    def ctx(**kw):
        return bpy.context.temp_override(workspace=space, screen=screen, area=area, **kw)

    def rec():
        return timeline_record(prefs)

    setattr(space, PROP, "BLOCK")

    # Toolbar Settings: entries per stage, edits kept when switching stage.
    fake = SimpleNamespace(entries=Entries(), family="tween", active_index=0, layout_choice="recommended")
    cls = settings.ANIMASSIST_OT_toolbar_settings
    fake.serialize = lambda: cls.serialize(fake)
    fake.populate = lambda data, stage=None: cls.populate(fake, data, stage)
    cls.populate(fake, rec(), "BLOCK")
    check("Block settings list only Tween and Keys", {e.family for e in fake.entries} == {"tween", "keys"})
    check("Family dropdown limited to the stage", [i[0] for i in settings._families(fake, None)] == ["tween", "keys"])
    next(e for e in fake.entries if e.action == "INBETWEEN").mode = "HIDDEN"
    cls.switch_stage(fake, "POLISH")
    check("Switching stage shows Polish families", {e.family for e in fake.entries} == {"timing", "pose"}
          and fake.family in {"timing", "pose"})
    check("Block edit kept after switching", "INBETWEEN" not in fake._record["active"]["stages"]["BLOCK"]["order"])
    cls.switch_stage(fake, "ALL")
    check("All lists every tool", len(fake.entries) == len(ACTIONS) == 96)
    settings.write(bpy.context, fake.serialize())
    check("Applied settings store the Block edit", "INBETWEEN" not in rec()["active"]["stages"]["BLOCK"]["order"])

    with ctx():
        layout = Rec()
        fake2 = SimpleNamespace(_record=rec(), serialize=rec, layout_choice="recommended", family="tween",
                                entries=[], active_index=0, layout=layout, _stage="BLOCK")
        cls.draw(fake2, bpy.context)
        ops = [a[0] for n, a, k in layout.events if n == "operator" and a]
        check("Settings offer Reset Block to Defaults", "animassist.reset_stage_toolbar" in ops)
        layout = Rec(); fake2.layout = layout; fake2._stage = "ALL"
        cls.draw(fake2, bpy.context)
        check("All has no Reset Stage button",
              "animassist.reset_stage_toolbar" not in [a[0] for n, a, k in layout.events if n == "operator" and a])
        check("Reset Stage restores Block", bpy.ops.animassist.reset_stage_toolbar() == {"FINISHED"}
              and rec()["active"]["stages"]["BLOCK"] == model.stage_default("BLOCK"))

        # Saved layouts carry the stages.
        data = rec(); model.set_stage_tool(data, "SPLINE", "SMOOTH", mode="HIDDEN"); settings.write(bpy.context, data)
        check("Save As keeps stages", bpy.ops.animassist.layout_action("EXEC_DEFAULT", operation="SAVE",
              layout_name="Mine") == {"FINISHED"} and "SMOOTH" not in rec()["saved"][0]["stages"]["SPLINE"]["order"])
        mine = rec()["saved"][0]["id"]
        bpy.ops.animassist.restore_toolbar()
        check("Restore Recommended resets stages", rec()["active"]["stages"]["SPLINE"] == model.stage_default("SPLINE"))
        bpy.ops.animassist.layout_action("EXEC_DEFAULT", operation="LOAD", target=mine, discard_changes=True)
        check("Load restores the saved stages", "SMOOTH" not in rec()["active"]["stages"]["SPLINE"]["order"])
        bpy.ops.animassist.restore_toolbar()

        # Search pin follows the shown stage; other families pin into All.
        before_all = copy.deepcopy(rec()["active"]["tools"])
        bpy.ops.animassist.timeline_pin(action="INBETWEEN")
        check("Pin in Block hides Inbetween there only", "INBETWEEN" not in rec()["active"]["stages"]["BLOCK"]["order"]
              and rec()["active"]["tools"] == before_all)
        bpy.ops.animassist.timeline_pin(action="INBETWEEN")
        check("Pin again shows it in Block", "INBETWEEN" in rec()["active"]["stages"]["BLOCK"]["order"])
        block = copy.deepcopy(rec()["active"]["stages"]["BLOCK"])
        bpy.ops.animassist.timeline_pin(action="BAKE_STEP")
        check("Pin of a Bake tool in Block changes All", rec()["active"]["tools"]["BAKE_STEP"]["mode"] == "HIDDEN"
              and rec()["active"]["stages"]["BLOCK"] == block)
        bpy.ops.animassist.timeline_pin(action="BAKE_STEP")

    # Tool Settings: display per stage, amounts shared.
    setattr(space, PROP, "SPLINE")
    tool = copy.deepcopy(rec()["active"]["tools"]["SMOOTH"])
    fields = {k: v for k, v in tool.items() if k not in ("action", "presets", "mode", "label_mode")}
    fake3 = SimpleNamespace(action="SMOOTH", _tool=tool, _target="SPLINE", mode="POPOUT", label_mode="ICON",
                            presets_text="", report=lambda *a: None, **fields)
    fake3.width = 160.
    with ctx():
        settings.ANIMASSIST_OT_tool_settings.execute(fake3, bpy.context)
    data = rec()
    check("Tool Settings in Spline changes Spline display; Icon is ignored for a tool without one",
          data["active"]["stages"]["SPLINE"]["tools"]["SMOOTH"] == {"mode": "POPOUT", "label_mode": "LABEL"})
    # Presets edited in a stage belong to that stage; All keeps its own.
    setattr(space, PROP, "BLOCK")
    tool4 = copy.deepcopy(rec()["active"]["tools"]["DRAG"])
    fields4 = {k: v for k, v in tool4.items() if k not in ("action", "presets", "mode", "label_mode")}
    fake4 = SimpleNamespace(action="DRAG", _tool=tool4, _target="BLOCK", mode="INLINE", label_mode="LABEL",
                            presets_text="10, 90", _shown_presets=[-25., 25., 50., 75., 125.],
                            report=lambda *a: None, **fields4)
    with ctx():
        settings.ANIMASSIST_OT_tool_settings.execute(fake4, bpy.context)
    data4 = rec()
    check("Tool Settings in Block edits Block presets only",
          data4["active"]["stages"]["BLOCK"]["tools"]["DRAG"]["presets"] == [10., 90.]
          and data4["active"]["tools"]["DRAG"]["presets"] == [])
    check("Block key types start as icons",
          all(data["active"]["stages"]["BLOCK"]["tools"][a]["label_mode"] == "ICON"
              for a in ("TYPE_KEYFRAME", "TYPE_BREAKDOWN", "TYPE_EXTREME", "TYPE_HOLD")))
    check("All display unchanged; width shared", data["active"]["tools"]["SMOOTH"]["mode"] == "INLINE"
          and data["active"]["tools"]["SMOOTH"]["label_mode"] == "LABEL" and data["active"]["tools"]["SMOOTH"]["width"] == 160.)

    for cycle in range(2):
        print(f"disable {cycle}", flush=True)
        addon_utils.disable("B4_anim_assist", default_set=False)
        print(f"enable {cycle}", flush=True)
        addon_utils.enable("B4_anim_assist", default_set=False, persistent=False)
    # Re-enabling frees the old preferences struct: look everything up again.
    fresh = sys.modules["B4_anim_assist.prefs"]
    prefs = fresh.get_prefs(bpy.context)
    check("Record survives two disable/enable cycles",
          fresh.timeline_record(prefs)["active"]["stages"]["SPLINE"]["tools"]["SMOOTH"]["mode"] == "POPOUT")
    addon_utils.disable("B4_anim_assist", default_set=False)
except Exception:
    traceback.print_exc()
    results.append(("no exception", False))

failed = [n for n, ok in results if not ok]
print(f"RESULT {len(results) - len(failed)}/{len(results)} passed")
sys.exit(1 if failed else 0)
