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


def stage_op(screen, **kw):
    with bpy.context.temp_override(screen=screen):
        return bpy.ops.animassist.timeline_stage(**kw)


try:
    anim_assist.register()
    check("Screen stage property registered", hasattr(bpy.types.Screen, PROP))
    screen = bpy.data.screens[0]
    check("Default stage is All", getattr(screen, PROP) == "ALL")
    check("Click tab sets Block", stage_op(screen, stage="BLOCK") == {"FINISHED"} and getattr(screen, PROP) == "BLOCK")
    stage_op(screen, step=1)
    check("Cycle forward reaches Spline", getattr(screen, PROP) == "SPLINE")
    stage_op(screen, step=-1); stage_op(screen, step=-1)
    check("Cycle back reaches All", getattr(screen, PROP) == "ALL")
    stage_op(screen, step=-1)
    check("Cycle wraps to Deliver", getattr(screen, PROP) == "DELIVER")
    check("Unknown stage cancelled", stage_op(screen, stage="BOGUS") == {"CANCELLED"}
          and getattr(screen, PROP) == "DELIVER")
    other = bpy.data.screens[1] if len(bpy.data.screens) > 1 else None
    if other is not None:
        check("Stage is per screen", getattr(other, PROP) == "ALL")

    from anim_assist.ui import timeline_overlay as overlay
    text = overlay.ANIMASSIST_OT_overlay_control.description(
        bpy.context, SimpleNamespace(kind="STAGE", key="POLISH"))
    check("Stage tooltip names its families", "Timing, Pose" in text and "unchanged" in text)
    from anim_assist.ui.timeline_catalog import command_description
    check("Spacing wording in T80 tooltip", "keys sit closer together" in command_description("T80", ""))
    check("Spacing wording in Timing Scale tooltip", "spacing" in command_description("SCALE_DRAG", ""))

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
    tl_screen, timeline_area = next(
        (s, a) for s in bpy.data.screens for a in s.areas
        if a.type == "DOPESHEET_EDITOR" and a.spaces.active.mode == "TIMELINE")
    stage_op(tl_screen, stage="BLOCK")
    with bpy.context.temp_override(screen=tl_screen, area=timeline_area):
        rec = Rec()
        overlay.draw_stage_controls(rec, bpy.context, "pose")
        check("Stage dropdown drawn", stage_prop(rec))
        check("Hidden-family note for Pose in Block",
              "Pose is hidden in the Block stage; choose All or Polish to see it." in labels(rec))
        rec = Rec()
        overlay.draw_stage_controls(rec, bpy.context, "tween")
        check("No note for a family the stage shows", not any("hidden" in t for t in labels(rec)))
        record = model.recommended(ACTIONS)
        fake = SimpleNamespace(_record=record, serialize=lambda: record, layout_choice="recommended",
                               family="bake", entries=[], active_index=0, layout=Rec())
        timeline_settings.ANIMASSIST_OT_toolbar_settings.draw(fake, bpy.context)
        check("Toolbar Settings shows Row Stage", stage_prop(fake.layout))
        check("Toolbar Settings notes Bake hidden in Block",
              "Bake is hidden in the Block stage; choose All or Deliver to see it." in labels(fake.layout))
        prefs = SimpleNamespace(timeline_toolbar_row=True)
        rec = Rec()
        prefs_module.draw_timeline_quick_settings(rec, bpy.context, prefs)
        check("Gear popover on a Timeline shows Row Stage", stage_prop(rec))
        check("Gear popover says bottom of the Timeline", "Tool row at the bottom of the Timeline" in labels(rec))
        check("Gear popover drops stale header text", not any("beside its header" in t for t in labels(rec)))
    rec = Rec()
    prefs_module.draw_timeline_quick_settings(rec, bpy.context, SimpleNamespace(timeline_toolbar_row=True))
    check("Preferences (no Timeline) explain stage tabs instead",
          not stage_prop(rec) and "Each workspace picks its stage with the row's tabs" in labels(rec))
    check("Preference description updated",
          "bottom of the Timeline" in prefs_module.AA_AddonPreferences.bl_rna.properties["timeline_toolbar_row"].description
          if hasattr(prefs_module.AA_AddonPreferences, "bl_rna") else True)

    path = Path(tempfile.mkdtemp()) / "stage.blend"
    stage_op(screen, stage="POLISH")
    name = screen.name
    bpy.ops.wm.save_as_mainfile(filepath=str(path))
    bpy.ops.wm.open_mainfile(filepath=str(path))
    check("Stage persists through save and reopen", getattr(bpy.data.screens[name], PROP) == "POLISH")

    for cycle in range(2):
        anim_assist.unregister()
        check(f"Property removed on unregister #{cycle + 1}", not hasattr(bpy.types.Screen, PROP))
        anim_assist.register()
        check(f"Property restored on register #{cycle + 1}", hasattr(bpy.types.Screen, PROP))
    check("Saved stage still readable after re-register", getattr(bpy.data.screens[name], PROP) == "POLISH")
    anim_assist.unregister()
except Exception:
    traceback.print_exc()
    results.append(("no exception", False))

failed = [n for n, ok in results if not ok]
print(f"RESULT {len(results) - len(failed)}/{len(results)} passed")
sys.exit(1 if failed else 0)
