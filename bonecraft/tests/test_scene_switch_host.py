# bonecraft/tests/test_scene_switch_host.py
"""In-Bforartists test: Preferences > Tabs > Scene Properties shows or hides BoneCraft in Properties > Scene tab.

* The switch is a preference, on by default, drawn below the tab switches after a gap, shaped like
  the tab rows: the name on the left where the checkboxes start, then one Show button as wide as a
  Left | Right bar, blue while on.
* Off: every BoneCraft section root in the Scene tab (Rig Builder, Mechanisms, CATS, VRChat,
  VRChat Tools, Import / Export) polls false, so its sub-panels go with it.
* On: those roots poll true, as before.
* The switch touches nothing else: the Rig Builder viewport tab and the Armature data copies
  poll the same with it on or off.
"""
import bpy

import boneforge

SCENE_ROOTS = ("BF_PT_rb_setup", "BF_PT_mech_Scene", "CATS_PT_main_Scene", "BF_PT_sb_vrchat_Scene",
               "BF_PT_cats_vrc_tools_Scene", "BF_PT_sb_io_Scene")


class _Prefs:
    def __init__(self, scene):
        self.show_scene_tab = scene

    def __getattr__(self, name):
        return True


class _Ctx:
    """bpy.context with Scene Properties set to ``scene``; every other BoneCraft preference is on."""
    def __init__(self, scene):
        prefs = _Prefs(scene)
        self.preferences = type("P", (), {"addons": {"boneforge": type("A", (), {"preferences": prefs})()}})()

    def __getattr__(self, name):
        return getattr(bpy.context, name)


def run():
    from boneforge.core.prefs import BoneForgePreferences, _draw_tabs
    notes = BoneForgePreferences.__annotations__
    assert "scene_properties" not in notes, "one toggle button, not a Show | Hide bar"
    assert notes["show_scene_tab"].keywords["default"] is True, "Scene Properties starts on"

    from mech_draw_stubs import Rec
    log = []
    _draw_tabs(Rec(log), _Prefs(True))
    props = [(a[1], k) for n, a, k in log if n == "prop"]
    assert props[-1] == ("show_scene_tab", {"text": "Show", "toggle": True}), ("one Show toggle, last", props)
    names = [i for i, (n, a, k) in enumerate(log) if n == "label" and k.get("text") == "Scene Properties"]
    assert len(names) == 1 and "icon" not in log[names[0]][2], "the name, no icon"
    tail = log[:names[0]]
    last_tab = max(i for i, (n, a, k) in enumerate(tail) if n == "prop")
    assert any(n == "separator" for n, a, k in tail[last_tab:]), "a gap between the tab switches and Scene Properties"
    assert not [e for e in log if e == ("set", "alignment", "CENTER")], "left-aligned like the tab rows"
    splits = [(i, k.get("factor")) for i, (n, a, k) in enumerate(log) if n == "split"]
    assert [f for i, f in splits] == [0.325] and splits[0][0] < names[0], ("name, then the bar under Left | Right", splits)

    boneforge.register()
    try:
        bpy.ops.object.armature_add()
        on, off = _Ctx(True), _Ctx(False)
        roots = [c for c in bpy.types.Panel.__subclasses__()
                 if getattr(c, "is_registered", False) and c.__module__.startswith("boneforge")
                 and getattr(c, "bl_space_type", "") == "PROPERTIES" and getattr(c, "bl_context", "") == "scene"
                 and not getattr(c, "bl_parent_id", "")]
        assert sorted(c.bl_idname for c in roots) == sorted(SCENE_ROOTS), sorted(c.bl_idname for c in roots)
        for c in roots:
            assert c.poll(on) is True, (c.bl_idname, "shows while Scene Properties is on")
            assert c.poll(off) is False, (c.bl_idname, "hides while Scene Properties is off")

        from boneforge.core import properties_mirror
        others = [bpy.types.BF_PT_rb_setup_Shelf] + list(properties_mirror._mirror_classes)
        moved = [c.__name__ for c in others if bool(c.poll(on)) != bool(c.poll(off))]
        assert moved == [], ("panels outside the Scene tab follow Scene Properties", moved)
    finally:
        boneforge.unregister()
    print("PASS Scene Properties switch: a Show toggle under the Left | Right bars (on by default), hides the %d Scene-tab sections "
          "and nothing else" % len(SCENE_ROOTS))
