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
