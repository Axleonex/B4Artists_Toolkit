# bonecraft/tests/test_tab_sides_host.py
"""In-Bforartists test: each viewport tab sits on its chosen side (left Tool Shelf / right sidebar) and moves at once.

The test host has no installed 'boneforge' add-on entry, so the preferences read as their defaults
(BoneCraft and Rig Builder left, CATS right); a side change is driven through ``place(key, side)``.
"""
import logging
from types import SimpleNamespace as NS

import bpy

import boneforge
from mech_draw_stubs import Rec

GATED = {"cats": "CATS_PT_main", "boneforge": "BF_PT_sb_setup", "rig_builder": "BF_PT_rb_setup_Shelf"}


class _Prefs:
    def __init__(self, on):
        self.show_tab_boneforge = self.show_tab_cats = self.show_tab_rig_builder = on

    def __getattr__(self, name):
        return True


class _Ctx:
    """bpy.context with every BoneCraft show switch set to ``on``."""
    def __init__(self, on):
        prefs = _Prefs(on)
        self.preferences = type("P", (), {"addons": {"boneforge": type("A", (), {"preferences": prefs})()}})()

    def __getattr__(self, name):
        return getattr(bpy.context, name)


def _side_ctx(**sides):
    """A context whose BoneCraft preferences hold only the given side settings (others read as their default)."""
    prefs = NS(**sides)
    return NS(preferences=NS(addons={"boneforge": NS(preferences=prefs)}))


def _regions(ts, category):
    return {c.bl_region_type for c in ts.panels_of(category)}


def _children_follow(ts, category):
    by = {c.bl_idname: c for c in ts.panels_of(category)}
    bad = [c.bl_idname for c in by.values()
           if getattr(c, "bl_parent_id", "") in by and by[c.bl_parent_id].bl_region_type != c.bl_region_type]
    assert bad == [], ("a child is not on its parent's side", category, bad)


def _all_panels(base):
    for cls in base.__subclasses__():
        yield cls
        yield from _all_panels(cls)


def _copies():
    return sorted(c.__name__ for c in bpy.types.Panel.__subclasses__()
                  if getattr(c, "is_registered", False) and getattr(c, "bl_space_type", "") == "PROPERTIES"
                  and c.__module__.split(".")[0] == "boneforge")


def run():
    bpy.ops.wm.read_factory_settings(use_empty=True)   # an empty scene: no names or modes left by earlier tests
    boneforge.register()
    try:
        from boneforge import tab_sides as ts                     # after register: modules may reload
        from boneforge.core import prefs as prefs_mod
        from boneforge.core.tool_toggle_operator import BF_OT_ToggleTool

        # Defaults after register: BoneCraft (Mechanisms included) and Rig Builder left, CATS right.
        assert len(ts.panels_of("BoneCraft")) > 10 and len(ts.panels_of("CATS")) > 10
        assert len(ts.panels_of("Rig Builder")) == 4
        assert _regions(ts, "BoneCraft") == {"TOOLS"}, _regions(ts, "BoneCraft")
        assert _regions(ts, "Rig Builder") == {"TOOLS"}, _regions(ts, "Rig Builder")
        assert _regions(ts, "CATS") == {"UI"}, _regions(ts, "CATS")
        assert bpy.types.BF_PT_mech.bl_region_type == "TOOLS", "Mechanisms moves with the BoneCraft tab"
        for cat in ("BoneCraft", "CATS", "Rig Builder"):
            _children_follow(ts, cat)
        copies = _copies()
        assert copies, "no Properties copies registered"
        copies_cats = ts.panels_of("CATS")
        bpy.ops.object.armature_add()                             # the gated root panels show for an armature

        # A side change moves the whole tab, children included; moving to the same side moves nothing.
        for key, cat, other, home in (("cats", "CATS", "LEFT", "RIGHT"), ("boneforge", "BoneCraft", "RIGHT", "LEFT"),
                                      ("rig_builder", "Rig Builder", "RIGHT", "LEFT")):
            count = len(ts.panels_of(cat))
            assert ts.place(key, other) == count, (key, "every panel moves")
            assert _regions(ts, cat) == {ts.region_for(other)}, (key, _regions(ts, cat))
            assert len(ts.panels_of(cat)) == count, (key, "no panel lost on the way")
            _children_follow(ts, cat)
            gate = getattr(bpy.types, GATED[key])
            assert gate.poll(_Ctx(True)) and not gate.poll(_Ctx(False)), (key, "the show switch still works there")
            assert ts.place(key, other) == 0, (key, "already there")
            assert ts.place(key, home) == count and _regions(ts, cat) == {ts.region_for(home)}, key
        assert _copies() == copies, "Properties copies are untouched by a move"

        # place_all puts every tab back on its preference's side.
        ts.place("cats", "LEFT")
        ts.place_all()
        assert _regions(ts, "CATS") == {"UI"} and _regions(ts, "BoneCraft") == {"TOOLS"}

        # The saved side settings decide: place_all reads each tab's side from the preferences it is given.
        ts.place_all(_side_ctx(side_cats="LEFT", side_boneforge="RIGHT"))
        assert _regions(ts, "CATS") == {"TOOLS"}, _regions(ts, "CATS")
        assert _regions(ts, "BoneCraft") == {"UI"}, _regions(ts, "BoneCraft")
        assert _regions(ts, "Rig Builder") == {"TOOLS"}, "a setting that is not there reads as its default"
        assert ts.place("cats", context=_side_ctx(side_cats="RIGHT")) == len(copies_cats)
        assert _regions(ts, "CATS") == {"UI"}
        assert ts.place("rig_builder", context=_side_ctx(side_rig_builder="RIGHT")) == 4
        assert _regions(ts, "Rig Builder") == {"UI"}, _regions(ts, "Rig Builder")
        ts.place_all()
        assert _regions(ts, "BoneCraft") == {"TOOLS"}

        # All or nothing: if any panel cannot be registered on the new side (a parent, or a child whose parent
        # already moved), the whole tab goes back to its old side, every panel registered; nothing raises.
        real, log = bpy.utils.register_class, logging.getLogger("boneforge.tab_sides")
        child = next(c.bl_idname for c in ts.panels_of("CATS") if getattr(c, "bl_parent_id", "") == "CATS_PT_main")
        for refused in ("CATS_PT_main", child):
            def refuse_left(cls, refused=refused):
                if cls.bl_idname == refused and cls.bl_region_type == "TOOLS":
                    raise RuntimeError("refused for the test")
                return real(cls)

            bpy.utils.register_class, level = refuse_left, log.level
            log.setLevel(logging.CRITICAL)                        # the expected failure stays out of the test output
            try:
                moved = ts.place("cats", "LEFT")                  # must not raise
            finally:
                bpy.utils.register_class = real
                log.setLevel(level)
            panels = ts.panels_of("CATS")
            assert moved == 0, (refused, moved)
            assert len(panels) == len(copies_cats), (refused, "every CATS panel is registered again")
            assert _regions(ts, "CATS") == {"UI"}, (refused, _regions(ts, "CATS"))
            _children_follow(ts, "CATS")
        assert ts.place("cats", "LEFT") == len(copies_cats) and ts.place("cats", "RIGHT") == len(copies_cats)

        # A tool switched off and on again lands on its tab's side (the toggle operator's deferred work).
        BF_OT_ToggleTool._deferred_work({"tool_id": "mechanisms"})
        assert getattr(bpy.types, "BF_PT_mech", None) is None, "Mechanisms switched off"
        BF_OT_ToggleTool._deferred_work({"tool_id": "mechanisms"})
        assert bpy.types.BF_PT_mech.bl_region_type == "TOOLS", "switched back on: on the BoneCraft side"
        _children_follow(ts, "BoneCraft")
        assert _copies() == copies, "the rebuilt Properties copies are the same set, still in Properties"

        # A tool whose panels sit under another package's panel (Control UI's picker under BF_PT_sb_animate)
        # registers straight on its tab's side: when it was off at startup (its class still on the coded side) ...
        import boneforge.control_ui.picker as picker_mod
        BF_OT_ToggleTool._deferred_work({"tool_id": "control_ui"})               # off
        picker_mod.BONEFORGE_PT_picker.bl_region_type = "UI"                     # as coded
        BF_OT_ToggleTool._deferred_work({"tool_id": "control_ui"})               # on
        picker = getattr(bpy.types, "BONEFORGE_PT_picker", None)
        assert picker is not None and picker.bl_region_type == "TOOLS", ("tool off at startup", picker)
        # ... and when its tab moved while it was off.
        BF_OT_ToggleTool._deferred_work({"tool_id": "control_ui"})               # off
        real_side = ts.side_of
        ts.side_of = lambda key, context=None: "RIGHT" if key == "boneforge" else real_side(key, context)
        try:
            ts.place_all()                                                       # BoneCraft moves right
            BF_OT_ToggleTool._deferred_work({"tool_id": "control_ui"})           # on
            picker = getattr(bpy.types, "BONEFORGE_PT_picker", None)
            assert picker is not None and picker.bl_region_type == "UI", ("tab moved while off", picker)
            _children_follow(ts, "BoneCraft")
        finally:
            ts.side_of = real_side
        ts.place_all()
        assert bpy.types.BONEFORGE_PT_picker.bl_region_type == "TOOLS" and _regions(ts, "BoneCraft") == {"TOOLS"}
        # ... and when the side changed but its timer has not run yet (the parent still sits on the old side).
        BF_OT_ToggleTool._deferred_work({"tool_id": "control_ui"})               # off
        ts.side_of = lambda key, context=None: "RIGHT" if key == "boneforge" else real_side(key, context)
        try:
            BF_OT_ToggleTool._deferred_work({"tool_id": "control_ui"})           # on, before any place_all
            picker = getattr(bpy.types, "BONEFORGE_PT_picker", None)
            assert picker is not None and picker.bl_region_type == "UI", ("side change still pending", picker)
            assert bpy.types.BF_PT_sb_animate.bl_region_type == "UI"
            _children_follow(ts, "BoneCraft")
        finally:
            ts.side_of = real_side
        ts.place_all()
        assert bpy.types.BONEFORGE_PT_picker.bl_region_type == "TOOLS" and _regions(ts, "BoneCraft") == {"TOOLS"}
        assert bpy.utils.register_class.__module__ != "boneforge.tab_sides", "register_class is restored"

        # A side setting changed in Preferences moves the tab on the next timer tick.
        tick = ts.schedule("cats")
        assert bpy.app.timers.is_registered(tick)
        assert tick() is None, "the timer runs once"
        if bpy.app.timers.is_registered(tick):
            bpy.app.timers.unregister(tick)
        # Two changes before the timer fires: each tick reads the setting when it runs, so the last change wins.
        setting, real_side = {}, ts.side_of
        ts.side_of = lambda key, context=None: setting.get(key) or real_side(key, context)
        try:
            for first, last in (("RIGHT", "LEFT"), ("LEFT", "RIGHT")):
                setting["cats"] = first
                ticks = [ts.schedule("cats")]
                setting["cats"] = last
                ticks.append(ts.schedule("cats"))
                for t in ticks:
                    t()
                    if bpy.app.timers.is_registered(t):
                        bpy.app.timers.unregister(t)
                assert _regions(ts, "CATS") == {ts.region_for(last)}, (first, last, _regions(ts, "CATS"))
                assert ts.place("cats") == 0, "an extra tick moves nothing"
                # The first tick runs before the second change: each tick follows the setting of its moment.
                setting["cats"] = first
                tick_a = ts.schedule("cats")
                tick_a()
                assert _regions(ts, "CATS") == {ts.region_for(first)}, (first, _regions(ts, "CATS"))
                setting["cats"] = last
                tick_b = ts.schedule("cats")
                tick_b()
                assert _regions(ts, "CATS") == {ts.region_for(last)}, (last, _regions(ts, "CATS"))
                for t in (tick_a, tick_b):
                    if bpy.app.timers.is_registered(t):
                        bpy.app.timers.unregister(t)
        finally:
            ts.side_of = real_side

        # The Rig Builder viewport copy is registered straight on its chosen side (no move needed).
        from boneforge.taskboard import sidebar
        real_side = ts.side_of
        ts.side_of = lambda key, context=None: "RIGHT" if key == "rig_builder" else real_side(key, context)
        try:
            sidebar.unregister_rig_builder()
            sidebar.register_rig_builder()
            assert _regions(ts, "Rig Builder") == {"UI"}, "registered on the right before any move"
        finally:
            ts.side_of = real_side
            sidebar.unregister_rig_builder()
            sidebar.register_rig_builder()
        assert _regions(ts, "Rig Builder") == {"TOOLS"} and len(ts.panels_of("Rig Builder")) == 4

        # Preferences: each side setting defaults as the owner chose and sits next to its show switch.
        notes = prefs_mod.BoneForgePreferences.__annotations__
        for key, _cat, side_pref, show_pref in ts.TABS:
            assert notes[side_pref].keywords["default"] == ts.DEFAULT_SIDE[key], side_pref
            assert notes[side_pref].keywords["update"] is not None, side_pref
        stub = type("S", (), {"show_tab_boneforge": True, "show_tab_cats": False, "show_tab_rig_builder": True})()
        layout = Rec([])
        prefs_mod._draw_tabs(layout, stub)
        props = [(a[1], k) for n, a, k in layout.log if n == "prop"]
        assert props == [("show_tab_boneforge", {}), ("side_boneforge", {"expand": True}),
                         ("show_tab_cats", {}), ("side_cats", {"expand": True}),
                         ("show_tab_rig_builder", {}), ("side_rig_builder", {"expand": True}),
                         ("show_scene_tab", {"text": "Show", "toggle": True})], props
        actives = [v for n, a, v in layout.log if n == "set" and a == "active"]
        assert actives == [True, False, True], ("a hidden tab's side buttons are greyed out", actives)
    finally:
        boneforge.unregister()
    left = [c.__name__ for c in bpy.types.Panel.__subclasses__()
            if getattr(c, "is_registered", False) and c.__module__.split(".")[0] == "boneforge"]
    assert left == [], ("panels left registered after unregister", left[:5])

    # Disable and enable the add-on again (a reload): every tab is placed on its side again. Put every class
    # back on the sidebar first, so the check cannot pass on regions left over from the first session.
    for cls in _all_panels(bpy.types.Panel):
        if (cls.__module__.split(".")[0] == "boneforge" and getattr(cls, "bl_space_type", "") == "VIEW_3D"
                and getattr(cls, "bl_category", "") in ("BoneCraft", "CATS", "Rig Builder")):
            cls.bl_region_type = "UI"
    boneforge.register()
    try:
        from boneforge import tab_sides as ts
        assert _regions(ts, "BoneCraft") == {"TOOLS"} and _regions(ts, "Rig Builder") == {"TOOLS"}
        assert _regions(ts, "CATS") == {"UI"}
    finally:
        boneforge.unregister()
    print("PASS tab sides: defaults, moves, toggle, timer, preferences")
