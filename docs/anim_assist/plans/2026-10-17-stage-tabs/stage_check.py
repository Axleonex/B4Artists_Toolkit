"""Background Bforartists check of Anim Assist stage tabs (no GPU drawing)."""
import sys
import tempfile
import traceback
from pathlib import Path
from types import SimpleNamespace

import bpy

ROOT = Path(sys.argv[sys.argv.index("--") + 1]).resolve()
sys.path.insert(0, str(ROOT))
import anim_assist  # noqa: E402

PROP = "animassist_timeline_stage"
results = []


def check(name, condition):
    results.append((name, bool(condition)))
    print(("PASS " if condition else "FAIL ") + name)


def stage_op(workspace, **kw):
    with bpy.context.temp_override(workspace=workspace):
        return bpy.ops.animassist.timeline_stage(**kw)


try:
    anim_assist.register()
    check("Workspace stage property registered", hasattr(bpy.types.WorkSpace, PROP)
          and not hasattr(bpy.types.Screen, PROP))
    numbers = {i.identifier: i.value for i in bpy.types.WorkSpace.bl_rna.properties[PROP].enum_items}
    check("Stage enum numbers are fixed", numbers == {"ALL": 0, "BLOCK": 1, "SPLINE": 2, "POLISH": 3, "DELIVER": 4})
    space = bpy.data.workspaces[0]
    check("Default stage is All", getattr(space, PROP) == "ALL")
    check("Click tab sets Block", stage_op(space, stage="BLOCK") == {"FINISHED"} and getattr(space, PROP) == "BLOCK")
    stage_op(space, step=1)
    check("Cycle forward reaches Spline", getattr(space, PROP) == "SPLINE")
    stage_op(space, step=-1); stage_op(space, step=-1)
    check("Cycle back reaches All", getattr(space, PROP) == "ALL")
    stage_op(space, step=-1)
    check("Cycle wraps to Deliver", getattr(space, PROP) == "DELIVER")
    check("Unknown stage cancelled", stage_op(space, stage="BOGUS") == {"CANCELLED"}
          and getattr(space, PROP) == "DELIVER")
    other = bpy.data.workspaces[1] if len(bpy.data.workspaces) > 1 else None
    if other is not None:
        check("Stage is per workspace", getattr(other, PROP) == "ALL")

    from anim_assist.ui import timeline_overlay as overlay
    text = overlay.ANIMASSIST_OT_overlay_control.description(
        bpy.context, SimpleNamespace(kind="STAGE", key="POLISH"))
    check("Stage tooltip names its families", "Timing, Pose" in text and "toolset" in text)
    check("Stage dropdown menu registered", hasattr(bpy.types, "ANIMASSIST_MT_timeline_stage"))
    from anim_assist.ui.timeline_catalog import command_description
    check("Spacing wording in T80 tooltip", "keys sit closer together" in command_description("T80", ""))
    check("Spacing wording in Timing Scale tooltip", "spacing" in command_description("SCALE_DRAG", ""))

    # The All tab and the Keys action Select All Visible share the key 'ALL'.
    check("All tab is not treated as the Select All action", overlay._tool_action("STAGE", "ALL") == ""
          and overlay._tool_action("STAGE_CYCLE", "ALL") == "")
    check("Tool kinds still resolve their action", overlay._tool_action("ACTION", "ALL") == "ALL"
          and overlay._tool_action("PRESET", "DRAG:25") == "DRAG"
          and overlay._tool_action("MENU", "keys") == "" and overlay._tool_action("SEARCH", "") == "")

    # Settings surfaces: Stage dropdown, hidden-family note and current wording.
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

    def stage_prop(rec):
        return any(n == "prop" and len(a) > 1 and a[1] == PROP and k.get("text") == "Row Stage"
                   for n, a, k in rec.events)

    def labels(rec):
        return [k.get("text", a[0] if a else "") for n, a, k in rec.events if n == "label"]

    from anim_assist.ui import timeline_settings, timeline_config as model
    from anim_assist import prefs as prefs_module
    from anim_assist.ui.timeline_catalog import ACTIONS
    tl_space, tl_screen, timeline_area = next(
        (w, s, a) for w in bpy.data.workspaces for s in w.screens for a in s.areas
        if a.type == "DOPESHEET_EDITOR" and a.spaces.active.mode == "TIMELINE")
    stage_op(tl_space, stage="BLOCK")
    with bpy.context.temp_override(workspace=tl_space, screen=tl_screen, area=timeline_area):
        text = overlay.ANIMASSIST_OT_overlay_control.description(
            bpy.context, SimpleNamespace(kind="STAGE_CYCLE", key="CYCLE"))
        check("Cycle button tooltip names the current stage", text.startswith("Stage: Block."))
        rec = Rec()
        overlay.draw_stage_controls(rec, bpy.context, "pose")
        check("Stage dropdown drawn", stage_prop(rec))
        check("Hidden-family note for Pose in Block",
              "The Block row has no Pose tools; add them in Toolbar Settings, or choose All or Polish." in labels(rec))
        rec = Rec()
        overlay.draw_stage_controls(rec, bpy.context, "tween")
        check("No note for a family the stage shows", not any("has no" in t for t in labels(rec)))
        record = model.recommended(ACTIONS)
        fake = SimpleNamespace(_record=record, serialize=lambda: record, layout_choice="recommended",
                               row="BLOCK", _stage="BLOCK", entries=[], active_index=0, layout=Rec())
        timeline_settings.ANIMASSIST_OT_toolbar_settings.draw(fake, bpy.context)
        check("Toolbar Settings shows the Row dropdown",
              any(n == "prop" and len(a) > 1 and a[1] == "row" for n, a, k in fake.layout.events))
        check("Toolbar Settings says any tool can go on any row",
              "Any tool can go on any row. Tools are grouped by family; open one to add or remove its tools." in labels(fake.layout)
              and "Changes apply to the row right away." in labels(fake.layout))
        prefs = SimpleNamespace(timeline_toolbar_row=True)
        rec = Rec()
        prefs_module.draw_timeline_quick_settings(rec, bpy.context, prefs)
        check("Quick Tools panel (legacy, not on the row) shows Row Stage on a Timeline", stage_prop(rec))
        check("Quick Tools text says bottom of the Timeline", "Tool row at the bottom of the Timeline" in labels(rec))
        check("Quick Tools text drops stale header text", not any("beside its header" in t for t in labels(rec)))
    plain = next((w, s) for w in bpy.data.workspaces for s in w.screens
                 if not any(a.type == "DOPESHEET_EDITOR" and a.spaces.active.mode == "TIMELINE" for a in s.areas))
    with bpy.context.temp_override(workspace=plain[0], screen=plain[1]):
        rec = Rec()
        overlay.draw_stage_controls(rec, bpy.context, "pose")
        check("No Row Stage without a Timeline (e.g. from Preferences)",
              not stage_prop(rec) and "Open from a Timeline to change its row stage" in labels(rec))
    rec = Rec()
    prefs_module.draw_timeline_quick_settings(rec, bpy.context, SimpleNamespace(timeline_toolbar_row=True))
    check("Preferences (no Timeline) explain stage tabs instead",
          not stage_prop(rec) and "Each workspace picks its stage with the row's stage button" in labels(rec))
    check("Preference description updated",
          "bottom of the Timeline" in prefs_module.AA_AddonPreferences.bl_rna.properties["timeline_toolbar_row"].description
          if hasattr(prefs_module.AA_AddonPreferences, "bl_rna") else True)

    path = Path(tempfile.mkdtemp()) / "stage.blend"
    stage_op(space, stage="POLISH")
    name = space.name
    bpy.ops.wm.save_as_mainfile(filepath=str(path))
    bpy.ops.wm.open_mainfile(filepath=str(path))
    check("Stage persists through save and reopen", getattr(bpy.data.workspaces[name], PROP) == "POLISH")

    for cycle in range(2):
        anim_assist.unregister()
        check(f"Property removed on unregister #{cycle + 1}", not hasattr(bpy.types.WorkSpace, PROP))
        anim_assist.register()
        check(f"Property restored on register #{cycle + 1}", hasattr(bpy.types.WorkSpace, PROP))
    check("Saved stage still readable after re-register", getattr(bpy.data.workspaces[name], PROP) == "POLISH")
    anim_assist.unregister()
except Exception:
    traceback.print_exc()
    results.append(("no exception", False))

failed = [n for n, ok in results if not ok]
print(f"RESULT {len(results) - len(failed)}/{len(results)} passed")
sys.exit(1 if failed else 0)
