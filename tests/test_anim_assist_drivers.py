"""Drivers-mode acceptance, run in an isolated Bforartists process.

  bforartists --background --factory-startup --python-exit-code 1 --python tests/test_anim_assist_drivers.py
Set AA_TEST_ROOT to an extracted release to check the actual installer.
"""
from __future__ import annotations

import os
import json
import importlib
from pathlib import Path
import sys
from types import SimpleNamespace

import bpy

ROOT = Path(os.environ.get("AA_TEST_ROOT", Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(ROOT))

PACKAGE = os.environ.get("AA_TEST_PACKAGE", "anim_assist")
anim_assist = importlib.import_module(PACKAGE)
layout_homes = importlib.import_module(f"{PACKAGE}.ui.layout_homes")


def visibility():
    groups = [getattr(bpy.types, layout_homes.sidebar_group_idname("GRAPH_EDITOR", g.key))
              for g in layout_homes.SIDEBARS["GRAPH_EDITOR"][1]]
    drivers = SimpleNamespace(space_data=SimpleNamespace(type="GRAPH_EDITOR", mode="DRIVERS"))
    action = SimpleNamespace(space_data=SimpleNamespace(type="GRAPH_EDITOR", mode="FCURVES"))
    assert all(not getattr(cls, "poll", lambda ctx: True)(drivers) for cls in groups), "Action groups leak into Drivers mode"
    assert all(cls.poll(action) for cls in groups), "Action groups did not return"
    CLASSES = importlib.import_module(f"{PACKAGE}.ui.driver_panels").CLASSES
    assert len(CLASSES) == 4
    assert all(cls.poll(drivers) and not cls.poll(action) for cls in CLASSES)
    # The header must not expose Action search/repeat or Action submenus in Drivers.
    header_menus = importlib.import_module(f"{PACKAGE}.ui.header_menus")
    class MenuLayout:
        def __init__(self):
            self.menus = []
        def menu(self, name, **kwargs):
            self.menus.append(name)
    layout = MenuLayout()
    menu = getattr(bpy.types, header_menus.menu_idname("GRAPH_EDITOR"))
    menu.draw(SimpleNamespace(layout=layout), drivers)
    assert layout.menus == [f"ANIMASSIST_MT_driver_{key}" for key in
                            ("target", "variables", "response", "diagnostics")]


def snapshot(fc):
    return (fc.extrapolation, [(tuple(k.co), k.interpolation, k.handle_left_type,
             k.handle_right_type, tuple(k.handle_left), tuple(k.handle_right)) for k in fc.keyframe_points],
            [(m.type, m.mute) for m in fc.modifiers])


def fixture():
    scene = bpy.context.scene
    obj = bpy.data.objects.new("Driver test owner", None)
    scene.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    obj["input"] = .5
    obj["output"] = 0.0
    obj["other"] = 0.0
    for frame, value in ((1, 1), (20, 8)):
        obj.location.x = value
        obj.keyframe_insert("location", index=0, frame=frame)
    fc = obj.driver_add('["output"]')
    for modifier in list(fc.modifiers):
        fc.modifiers.remove(modifier)
    fc.driver.expression = "value"
    var = fc.driver.variables.new()
    var.name = "value"
    var.type = "SINGLE_PROP"
    var.targets[0].id = obj
    var.targets[0].data_path = '["input"]'
    for x, y in ((0, 0), (1, 2)):
        kp = fc.keyframe_points.insert(x, y)
        kp.select_control_point = True
        kp.select_left_handle = kp.select_right_handle = False
    fc.select = True
    other = obj.driver_add('["other"]')
    for modifier in list(other.modifiers):
        other.modifiers.remove(modifier)
    other.driver.expression = "1"
    other.keyframe_points.insert(0, 3)
    other.keyframe_points.insert(1, 4)
    other.select = False
    area = max(bpy.context.screen.areas, key=lambda a: a.width * a.height)
    area.type = "GRAPH_EDITOR"
    area.spaces.active.mode = "DRIVERS"
    region = next(r for r in area.regions if r.type == "WINDOW")
    return obj, fc, other, area, region


def main():
    anim_assist.register()
    try:
        visibility()
        dc = importlib.import_module(f"{PACKAGE}.core.driver_context")
        iter_visible_fcurves = importlib.import_module(f"{PACKAGE}.core.context_utils").iter_visible_fcurves
        obj, fc, other, area, region = fixture()
        get_fcurves = importlib.import_module(f"{PACKAGE}.core.fcurve_compat").get_fcurves
        # The Action and unselected driver are sentinel data, never editing targets.
        action_keys = lambda: [(f.data_path, [tuple(k.co) for k in f.keyframe_points])
                               for f in get_fcurves(obj.animation_data.action, anim_data=obj.animation_data)]
        before_action = action_keys()
        before_other = snapshot(other)
        with bpy.context.temp_override(area=area, region=region,
                active_editable_fcurve=fc, visible_fcurves=[fc, other],
                editable_fcurves=[fc, other], selected_editable_fcurves=[fc]):
            assert dc.active_driver(bpy.context) == fc
            assert dc.driver_curves(bpy.context, selected=True) == [fc]
            assert not list(iter_visible_fcurves(bpy.context)), "Action-key fallback in Drivers"
            assert not dc.driver_issues(fc, bpy.context), "Valid fixture reported invalid"
            assert bpy.ops.animassist.driver_interpolation(type="LINEAR") == {"FINISHED"}
            assert all(k.interpolation == "LINEAR" for k in fc.keyframe_points)
            assert bpy.ops.animassist.driver_handles(type="VECTOR") == {"FINISHED"}
            assert all(k.handle_left_type == "VECTOR" for k in fc.keyframe_points)
            assert bpy.ops.animassist.driver_extrapolation(type="LINEAR") == {"FINISHED"}
            assert fc.extrapolation == "LINEAR"
            assert bpy.ops.animassist.driver_modifier_add(type="LIMITS") == {"FINISHED"}
            assert len(fc.modifiers) == 1 and not other.modifiers, ([(m.type, m.name) for m in fc.modifiers], [(m.type, m.name) for m in other.modifiers])
            assert bpy.ops.animassist.driver_select_owner() == {"FINISHED"}
            assert bpy.context.view_layer.objects.active == obj
            # Header navigation may run before the native sidebar has drawn.
            area.spaces.active.show_region_ui = False
            assert bpy.ops.animassist.driver_settings(panel="DRIVER") == {"FINISHED"}
            assert area.spaces.active.show_region_ui
            assert bpy.ops.animassist.driver_settings(panel="MODIFIERS") == {"FINISHED"}
            assert bpy.ops.animassist.driver_refresh() == {"FINISHED"}
            assert bpy.ops.animassist.driver_check() == {"FINISHED"}
            fc.driver.variables[0].targets[0].data_path = '["missing"]'
            assert any("property" in issue.lower() for issue in dc.driver_issues(fc, bpy.context))
            fc.driver.variables[0].targets[0].data_path = '["input"]'
            fc.driver.variables[0].targets[0].id = None
            assert any("target" in issue.lower() for issue in dc.driver_issues(fc, bpy.context))
            fc.driver.variables[0].targets[0].id = obj
            variable = fc.driver.variables.new()
            variable.type = "TRANSFORMS"
            variable.targets[0].id = obj
            variable.targets[0].bone_target = "MissingBone"
            assert any("bone" in issue.lower() for issue in dc.driver_issues(fc, bpy.context))
            fc.driver.variables.remove(variable)
            variable = fc.driver.variables.new()
            variable.type = "CONTEXT_PROP"
            variable.targets[0].context_property = "ACTIVE_SCENE"
            variable.targets[0].data_path = "frame_current"
            assert not dc.driver_issues(fc, bpy.context), "Valid context variable rejected"
            fc.driver.variables.remove(variable)
        assert action_keys() == before_action
        assert before_other == snapshot(other), "Unselected driver changed"
        fc.hide = True
        with bpy.context.temp_override(area=area, region=region, active_editable_fcurve=fc,
                visible_fcurves=[fc, other], selected_editable_fcurves=[fc]):
            assert not dc.driver_curves(bpy.context, selected=True)
            assert dc.active_driver(bpy.context) is None
            assert not bpy.ops.animassist.driver_refresh.poll()
        fc.hide = False
        fc.lock = True
        with bpy.context.temp_override(area=area, region=region, active_editable_fcurve=None,
                visible_fcurves=[fc], selected_editable_fcurves=[]):
            assert dc.driver_curves(bpy.context, selected=True) == [fc]
            assert dc.active_driver(bpy.context) == fc, "Lock hid its own unlock control"
            assert not bpy.ops.animassist.driver_settings.poll(), "Native settings lack an active editable driver"
            assert not dc.driver_curves(bpy.context, selected=True, editable=True)
            assert not bpy.ops.animassist.driver_modifier_add.poll()
            assert not bpy.ops.animassist.driver_interpolation.poll()
            assert not bpy.ops.animassist.driver_handles.poll()
            assert not bpy.ops.animassist.driver_extrapolation.poll()
        fc.lock = False
        with bpy.context.temp_override(area=area, region=region, active_editable_fcurve=None,
                visible_fcurves=[], selected_editable_fcurves=[]):
            assert dc.active_driver(bpy.context) is None
            assert not bpy.ops.animassist.driver_settings.poll()
            assert not bpy.ops.animassist.driver_check.poll()
        area.spaces.active.mode = "FCURVES"
        with bpy.context.temp_override(area=area, region=region):
            assert not dc.driver_curves(bpy.context)
            assert not bpy.ops.animassist.driver_check.poll()
            assert not bpy.ops.animassist.driver_settings.poll()
        print(f"TESTED PACKAGE: {anim_assist.__file__} {anim_assist.bl_info['version']}")
        print("DRIVERS OK: adaptive sidebar/header, actual curve edits, diagnostics, empty/hidden/locked scope, Action and unselected-driver preservation")
    finally:
        anim_assist.unregister()
    print("DRIVERS UNREGISTER OK")


def preview():
    """Disposable real-window fixture, with a read-only observation log for cursor checks."""
    anim_assist.register()
    bpy.context.preferences.view.show_splash = False
    obj, fc, other, area, region = fixture()
    area.spaces.active.show_region_ui = True
    area.spaces.active.show_region_channels = True
    directory = Path(os.environ["AA_DRIVER_PREVIEW"])
    directory.mkdir(parents=True, exist_ok=True)
    with bpy.context.temp_override(area=area, region=region):
        bpy.ops.graph.view_all()
        bpy.context.view_layer.update()
        bpy.ops.ed.undo_push(message="Anim Assist driver test fixture")

    def observe():
        dc = importlib.import_module(f"{PACKAGE}.core.driver_context")
        get_fcurves = importlib.import_module(f"{PACKAGE}.core.fcurve_compat").get_fcurves
        # Undo rebuilds RNA objects: never retain fixture pointers across it.
        obj = bpy.data.objects.get("Driver test owner")
        if obj is None or obj.animation_data is None:
            (directory / "state.json").write_text(json.dumps({"fixture_present": False}))
            return .5
        fc = obj.animation_data.drivers.find('["output"]')
        other = obj.animation_data.drivers.find('["other"]')
        if fc is None or other is None:
            return .5
        graph = next((a for a in bpy.context.window.screen.areas if a.type == "GRAPH_EDITOR"), None)
        data = {"version": list(anim_assist.bl_info["version"]), "host": bpy.app.version_string,
                "output": obj["output"], "selected_owner": bpy.context.view_layer.objects.active.name,
                "driver": {"muted": fc.mute, "locked": fc.lock,
                    "interpolation": [k.interpolation for k in fc.keyframe_points],
                    "handles": [k.handle_left_type for k in fc.keyframe_points],
                    "extrapolation": fc.extrapolation,
                    "modifiers": [m.type for m in fc.modifiers]},
                "other": {"interpolation": [k.interpolation for k in other.keyframe_points],
                    "extrapolation": other.extrapolation, "modifiers": [m.type for m in other.modifiers]},
                "action": [[list(k.co) for k in f.keyframe_points]
                           for f in get_fcurves(obj.animation_data.action, anim_data=obj.animation_data)]}
        if graph:
            with bpy.context.temp_override(area=graph):
                data["mode"] = graph.spaces.active.mode
                active = dc.active_driver(bpy.context)
                data["active_driver"] = active.data_path if active else None
                data["selected_drivers"] = [f.data_path for f in dc.driver_curves(bpy.context, selected=True)]
        (directory / "state.json").write_text(json.dumps(data, indent=2))
        return .5
    bpy.app.timers.register(observe, first_interval=1)


if __name__ == "__main__":
    preview() if os.environ.get("AA_DRIVER_PREVIEW") else main()
