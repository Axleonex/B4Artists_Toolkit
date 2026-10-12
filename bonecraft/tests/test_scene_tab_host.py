"""In-Bforartists test: CATS, VRChat and Import / Export also live in Properties > Scene tab.

* a Scene-tab copy exists for each root (CATS_PT_main, BF_PT_sb_vrchat,
  BF_PT_sb_io) and for every registered descendant panel;
* copies sit in PROPERTIES / WINDOW / scene, children under their parent's copy;
* the three roots poll true with nothing selected, and no copied child's poll
  reads the CATS sidebar switch (the switch hides only the sidebar tab);
* every copy draws into a recording layout without raising;
* the old Object-tab "BoneCraft VRChat" panel no longer shows;
* unregister removes every copy.
"""
import inspect

import bpy

import boneforge

ROOTS = {"CATS_PT_main": "CATS", "BF_PT_sb_vrchat": "Avatar Tools", "BF_PT_sb_io": "Import / Export"}


class Rec:
    def __init__(self, log):
        self.__dict__["log"] = log
    def __getattr__(self, name):
        def call(*a, **k):
            self.log.append((name, a, k))
            return Rec(self.log)
        return call
    def __setattr__(self, name, value):
        self.log.append(("set", name, value))


class Shim:
    def __init__(self):
        self.layout = Rec([])


class _Prefs:
    """BoneCraft add-on prefs stand-in: every switch on except show_tab_cats."""
    def __init__(self, show_cats):
        self.show_tab_cats = show_cats
    def __getattr__(self, name):
        return True


class _Preferences:
    def __init__(self, show_cats):
        self.addons = {"boneforge": type("A", (), {"preferences": _Prefs(show_cats)})()}
    def __getattr__(self, name):
        return getattr(bpy.context.preferences, name)


class _Ctx:
    """bpy.context with the CATS sidebar switch set as given."""
    def __init__(self, show_cats):
        self.preferences = _Preferences(show_cats)
    def __getattr__(self, name):
        return getattr(bpy.context, name)


def _poll(cls, ctx):
    try:
        return bool(cls.poll(ctx))
    except Exception as exc:                                # noqa: BLE001 - compare failures too
        return "error: " + type(exc).__name__


def _registered_panels():
    return [c for c in bpy.types.Panel.__subclasses__() if getattr(c, "is_registered", False)]


def _descendants(root_id, panels):
    out, frontier = [], [root_id]
    while frontier:
        parent = frontier.pop()
        kids = [c for c in panels if getattr(c, "bl_parent_id", "") == parent
                and getattr(c, "bl_space_type", "") == "VIEW_3D"]
        out += kids
        frontier += [k.bl_idname for k in kids]
    return out


def run():
    boneforge.register()
    try:
        from boneforge.core import scene_tab_mirror as stm      # after register: modules may reload
        panels = _registered_panels()
        bpy.context.view_layer.objects.active = None
        for root_id, label in ROOTS.items():
            copy = getattr(bpy.types, root_id + stm.SUFFIX, None)
            assert copy is not None, ("no Scene-tab copy", root_id)
            assert (copy.bl_space_type, copy.bl_region_type, copy.bl_context) == ("PROPERTIES", "WINDOW", "scene"), copy
            assert copy.poll(bpy.context), ("root must show with nothing selected", root_id)
            shim = Shim()
            copy.draw_header(shim, bpy.context)
            texts = [k.get("text") for n, a, k in shim.layout.log if n == "label"]
            assert label in texts, (root_id, texts)
            for kid in _descendants(root_id, panels):
                kid_copy = getattr(bpy.types, kid.bl_idname + stm.SUFFIX, None)
                assert kid_copy is not None, ("no Scene-tab copy for child", kid.bl_idname)
                assert kid_copy.bl_parent_id == kid.bl_parent_id + stm.SUFFIX, kid_copy.bl_parent_id
                poll = getattr(kid, "poll", None)
                if poll is not None:
                    assert "show_tab_cats" not in inspect.getsource(poll), ("child reads CATS switch", kid.bl_idname)

        lacking = {}
        for copy in stm._classes:
            orig = getattr(bpy.types, copy.bl_idname[:-len(stm.SUFFIX)], None)
            if orig is None:
                continue
            missing = [m for m, v in vars(orig).items()
                       if callable(v) and not m.startswith("__") and not hasattr(copy, m)]
            if missing:
                lacking[copy.__name__] = missing
        assert lacking == {}, ("Scene-tab copies lack helper methods", lacking)

        broken = []
        for copy in list(stm._classes):
            try:
                copy.draw(Shim(), bpy.context)
            except Exception as exc:                       # noqa: BLE001 - report every failure
                broken.append((copy.__name__, type(exc).__name__, str(exc)[:80]))
        assert broken == [], ("Scene-tab copies failed to draw", broken)

        bpy.ops.object.armature_add()
        old = bpy.types.BONEFORGE_PT_vrc_main
        assert not old.poll(bpy.context), "old 'BoneCraft VRChat' Object-tab panel must not show"
        count = len(stm._classes)
        assert count >= 3, count

        # Review finding: run every copy's poll with the CATS sidebar switch ON and OFF.
        results = {c.__name__: (_poll(c, _Ctx(show_cats=True)), _poll(c, _Ctx(show_cats=False)))
                   for c in stm._classes}
        errors = {n: r for n, r in results.items() if any(isinstance(x, str) for x in r)}
        assert errors == {}, ("Scene-tab copy polls raised", errors)
        differs = [n for n, (on, off) in results.items() if on != off]
        assert differs == [], ("Scene-tab copies follow the CATS sidebar switch", differs)

        # Review finding: registering twice keeps one tracked set; unregister still cleans up.
        stm.register()
        assert len(stm._classes) == count, (len(stm._classes), count)

        # Review finding: copies follow runtime tool toggles.
        from boneforge.core.tool_toggle_operator import BF_OT_ToggleTool
        from boneforge.core.tool_registry import get_registry
        def cats_copy():
            return getattr(bpy.types, "CATS_PT_main" + stm.SUFFIX, None) is not None
        started_on = get_registry().is_enabled("vrchat_avatar")
        assert cats_copy() == started_on, ("copy state does not match tool state", started_on)
        before = started_on
        for _ in range(2):                                    # flip, then flip back
            BF_OT_ToggleTool._deferred_work({"tool_id": "vrchat_avatar"})
            now_on = get_registry().is_enabled("vrchat_avatar")
            assert now_on != before, "the toggle did not change the tool state"
            assert cats_copy() == now_on, ("CATS copy does not follow the tool toggle", now_on)
            before = now_on
        assert get_registry().is_enabled("vrchat_avatar") == started_on
    finally:
        boneforge.unregister()
    leftovers = [c.__name__ for c in _registered_panels() if c.__name__.endswith("_Scene")]
    assert leftovers == [], ("Scene-tab copies left after unregister", leftovers)
    print("PASS scene tab: CATS, VRChat, Import / Export copies (%d panels)" % count)
