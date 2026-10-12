"""Run in a factory-startup Bforartists process against an extracted candidate.

Usage: bforartists --background --factory-startup --python-exit-code 1
       --python runtime-check.py -- <isolated extraction directory>
"""

import json
import sys
import traceback
from pathlib import Path

import bpy

ROOT = Path(sys.argv[sys.argv.index("--") + 1])
sys.path.insert(0, str(ROOT))
import B4_anim_assist as addon
from B4_anim_assist.core import p10_tool_registry as registry
from B4_anim_assist.core.fcurve_compat import get_fcurves
from B4_anim_assist.operators import p10_shelf_ops as shelf


def frames(obj):
    curves = get_fcurves(obj.animation_data.action, anim_data=obj.animation_data)
    return sorted({round(key.co.x, 4) for curve in curves for key in curve.keyframe_points})


checks = []


def check(name, condition, detail=None):
    checks.append({"name": name, "passed": bool(condition), "detail": detail})
    if not condition:
        raise AssertionError(name + ": " + repr(detail))


out = {"host": bpy.app.version_string, "checks": checks}
registered = False
try:
    addon.register()
    registered = True
    tools = registry.all_tools()
    check("catalogue populated on enable", len(tools) > 0, len(tools))
    for tool in tools:
        getattr(bpy.ops.animassist, tool.op_id.split(".")[1]).get_rna_type()
    check("catalogue entries resolve to registered operators", True, len(tools))
    check("dispatch wrappers excluded", not any(t.op_id in {
        "animassist.p10_search_tools", "animassist.p10_repeat_last"} for t in tools))
    check("setup completes", bpy.ops.animassist.p10_first_run_setup() == {'FINISHED'})
    p10 = bpy.context.scene.anim_assist_p10
    p10.max_recents = 7
    p10.shelf_mode = 'FAVORITES'
    item = p10.favorites.add()
    item.op_id = 'animassist.p6_scale_keys'
    item.label = 'My timing tool'
    check("repeated setup completes", bpy.ops.animassist.p10_first_run_setup() == {'FINISHED'})
    check("repeated setup preserves settings and favorites",
          p10.max_recents == 7 and p10.shelf_mode == 'FAVORITES'
          and len(p10.favorites) == 1 and p10.favorites[0].label == 'My timing tool')
    check("catalogue has no repeated-setup duplicates", len(registry.all_tools()) == len(tools))
    first = shelf._get_tool_items(None, bpy.context)
    check("search enum populated and retained", len(first) == len(tools)
          and first is shelf._get_tool_items(None, bpy.context), len(first))

    bpy.ops.object.select_all(action='DESELECT')
    obj = bpy.data.objects.new('Repair timing fixture', None)
    bpy.context.scene.collection.objects.link(obj)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    for frame, value in ((1, 0.0), (10, 1.0), (20, 0.0)):
        obj.location.x = value
        obj.keyframe_insert(data_path='location', frame=frame)
    area = max(bpy.context.screen.areas, key=lambda a: a.width * a.height)
    area.type = 'GRAPH_EDITOR'
    with bpy.context.temp_override(area=area):
        p6 = bpy.context.scene.anim_assist_p6
        p6.anchor_mode = 'CUSTOM'
        p6.pivot_frame = 0
        p6.range_mode = 'SCENE'
        p6.scale_factor = 1.5
        check("search invokes Retime scene settings",
              bpy.ops.animassist.p10_search_tools(tool_enum='animassist.p6_scale_keys') == {'FINISHED'})
        check("search scale changes animation", frames(obj) == [1.5, 15.0, 30.0], frames(obj))
        check("completed search added to Recents", p10.recents[0].op_id == 'animassist.p6_scale_keys')
        p6.offset_frames = 2
        check("second search executes", bpy.ops.animassist.p10_search_tools(
            tool_enum='animassist.p6_offset_keys') == {'FINISHED'})
        check("latest completed tool is first", p10.recents[0].op_id == 'animassist.p6_offset_keys')
        check("Repeat Last executes latest tool", bpy.ops.animassist.p10_repeat_last() == {'FINISHED'})
        check("Repeat Last uses latest offset", frames(obj) == [5.5, 19.0, 34.0], frames(obj))
        p6.scale_factor = 5
        check("explicit scale invocation executes", bpy.ops.animassist.p6_scale_keys(
            'INVOKE_DEFAULT', scale_factor=2) == {'FINISHED'})
        check("explicit scale survives scene default", frames(obj) == [11.0, 38.0, 68.0], frames(obj))
        p6.offset_frames = 100
        check("explicit offset invocation executes", bpy.ops.animassist.p6_offset_keys(
            'INVOKE_DEFAULT', offset_frames=3) == {'FINISHED'})
        check("explicit offset survives scene default", frames(obj) == [14.0, 41.0, 71.0], frames(obj))
        # A real tool cancels with a warning when its reference is absent.
        before = [item.op_id for item in p10.recents]
        result = bpy.ops.animassist.p10_search_tools(tool_enum='animassist.blend_toward_reference')
        check("target cancellation propagates through Search", result == {'CANCELLED'}, sorted(result))
        check("cancelled search leaves Recents unchanged", [item.op_id for item in p10.recents] == before)
        # bpy.ops raises RuntimeError for ERROR reports, even when the operator
        # correctly returns CANCELLED. Exercise that separate error pathway.
        try:
            bpy.ops.animassist.p10_search_tools(tool_enum='animassist.p12_bake_lipsync')
        except RuntimeError as error:
            check("unconfigured lipsync fails instead of reporting success",
                  'Could not run the tool from the shelf' in str(error), str(error))
        else:
            check("unconfigured lipsync fails instead of reporting success", False)
        check("failed lipsync leaves Recents unchanged", [item.op_id for item in p10.recents] == before)
        check("clearing Recents through Search stays empty", bpy.ops.animassist.p10_search_tools(
            tool_enum='animassist.p10_clear_recents') == {'FINISHED'} and len(p10.recents) == 0)

    addon.unregister()
    registered = False
    check("disable clears catalogue", not registry.all_tools())
    addon.register()
    registered = True
    check("re-enable restores catalogue", len(registry.all_tools()) == len(tools))
    out['passed'] = True
except Exception:
    out['passed'] = False
    out['error'] = traceback.format_exc()
    raise
finally:
    if registered:
        addon.unregister()
    (ROOT / 'runtime-results.json').write_text(json.dumps(out, indent=2), encoding='utf-8')
    print('REPAIR_RUNTIME_RESULT ' + json.dumps(out))
