"""In-Bforartists test: the Preferences tab switches affect only side panels.

With every switch OFF (BoneCraft, CATS, Show Rig Builder):
* the BoneCraft sidebar hubs, the whole CATS sidebar tab (including the main
  CATS section) and the Import / Export section poll false;
* every Properties copy — Scene tab (core/scene_tab_mirror) and Armature data
  (core/properties_mirror) — polls exactly as with the switches ON.
"""
import bpy

import boneforge

SWITCHES = ("show_tab_boneforge", "show_tab_cats", "show_tab_rig_builder")
SIDEBAR_GATED = ("BF_PT_sb_setup", "BF_PT_sb_skin", "BF_PT_sb_animate",
                 "CATS_PT_main", "BF_PT_sb_vrchat", "BF_PT_sb_io", "BF_PT_rb_setup_Shelf")
# Properties sections that must stay VISIBLE with every switch off (review finding).
PERMANENT = ("BF_PT_rb_setup", "CATS_PT_main_Scene", "BF_PT_sb_vrchat_Scene", "BF_PT_sb_io_Scene",
             "BF_PT_sb_setup_Prop", "BF_PT_sb_skin_Prop", "BF_PT_sb_animate_Prop")


class _Prefs:
    def __init__(self, on):
        for s in SWITCHES:
            setattr(self, s, on)
    def __getattr__(self, name):
        return True


class _Preferences:
    def __init__(self, on):
        self.addons = {"boneforge": type("A", (), {"preferences": _Prefs(on)})()}
    def __getattr__(self, name):
        return getattr(bpy.context.preferences, name)


class _Ctx:
    """bpy.context with every BoneCraft tab switch set to *on*."""
    def __init__(self, on):
        self.preferences = _Preferences(on)
    def __getattr__(self, name):
        return getattr(bpy.context, name)


def _poll(cls, ctx):
    try:
        return bool(cls.poll(ctx))
    except Exception as exc:                                # noqa: BLE001 - compare failures too
        return "error: " + type(exc).__name__


def run():
    boneforge.register()
    try:
        from boneforge.core import tab_switches, properties_mirror, scene_tab_mirror
        on, off = _Ctx(True), _Ctx(False)
        lifted = tab_switches.tabs_on(off).preferences.addons["boneforge"].preferences
        assert all(getattr(lifted, s) is True for s in SWITCHES), "tabs_on must report every switch on"
        assert tab_switches.tabs_on(off).scene is bpy.context.scene

        bpy.ops.object.armature_add()                         # armature copies need an armature
        for name in SIDEBAR_GATED:
            cls = getattr(bpy.types, name)
            assert _poll(cls, on) is True, (name, "should show with its switch on")
            assert _poll(cls, off) is False, (name, "side panel must hide with its switch off")

        copies = list(properties_mirror._mirror_classes) + list(scene_tab_mirror._classes)
        assert copies, "no Properties copies registered"
        shelf_in_props = [c.__name__ for c in properties_mirror._mirror_classes if "_Shelf" in c.__name__]
        assert shelf_in_props == [], ("Tool Shelf copies mirrored into Armature data", shelf_in_props)
        errors = {c.__name__: (_poll(c, on), _poll(c, off)) for c in copies
                  if isinstance(_poll(c, on), str) or isinstance(_poll(c, off), str)}
        assert errors == {}, ("Properties copy polls raised", errors)
        follow = [c.__name__ for c in copies if _poll(c, on) != _poll(c, off)]
        assert follow == [], ("Properties copies follow a tab switch", follow)
        hidden = [n for n in PERMANENT if _poll(getattr(bpy.types, n), off) is not True]
        assert hidden == [], ("Properties sections hidden with the switches off", hidden)
    finally:
        boneforge.unregister()
    print("PASS tab switches: side panels only (%d Properties copies unaffected)" % len(copies))
