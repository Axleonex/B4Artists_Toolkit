# bonecraft/tests/test_show_helpers_host.py
"""In-Bforartists test: one Show Helpers preference hides teaching text across BoneCraft (spec §7.1)."""
import bpy

import boneforge


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
    def __init__(self, on):
        self.show_helpers = on

    def __getattr__(self, name):
        return True


class _Ctx:
    def __init__(self, on, active=None):
        if active is not None:
            self.active_object = active
        prefs = _Prefs(on)
        self.preferences = type("P", (), {"addons": {"boneforge": type("A", (), {"preferences": prefs})()}})()

    def __getattr__(self, name):
        return getattr(bpy.context, name)


def _infos(log):
    return [k.get("text") for n, a, k in log if n == "label" and k.get("icon") == 'INFO']


def run():
    bpy.ops.wm.read_factory_settings(use_empty=True)   # an empty scene: no names or modes left by earlier tests
    boneforge.register()
    try:
        from boneforge.core import helpers                      # after register: modules may reload
        from boneforge.taskboard import sidebar
        on, off = _Ctx(True), _Ctx(False)
        assert helpers.helpers_on(bpy.context), "no installed preferences (headless): helpers stay on"
        assert helpers.helpers_on(on) and not helpers.helpers_on(off)
        for ctx, want in ((on, ["What this does."]), (off, [])):
            shim = Shim()
            helpers.draw_helper(shim.layout, ctx, "What this does.", "When to use it.")
            assert _infos(shim.layout.log) == want, (want, shim.layout.log)
            shim = Shim()
            sidebar._draw_explainer(shim.layout, ctx, "What this does.")
            assert _infos(shim.layout.log) == want, "the 17 existing explainers follow the preference"
        # The Setup and Skin panels' own what / when lines follow the preference too.
        from boneforge.i18n import T
        arm = bpy.data.objects.new("HelperArm", bpy.data.armatures.new("HelperArm"))
        bpy.context.scene.collection.objects.link(arm)
        for cls, texts in (
            (sidebar.BF_PT_sb_setup, ["Tools for rigs you already have.", "Use Rig Builder to create a new rig."]),
            (sidebar.BF_PT_sb_skin, ["Paint weights and fix mesh deformation.", "Expand a section below to get started."]),
        ):
            for ctx, want in ((_Ctx(True, arm), True), (_Ctx(False, arm), False)):
                shim = Shim()
                cls.draw(shim, ctx)
                shown = [k.get("text") for n, a, k in shim.layout.log if n == "label"]
                for text in texts:
                    assert (T(text) in shown) == want, (cls.__name__, text, want, shown)
                assert (T(texts[0]) in _infos(shim.layout.log)) == want, (cls.__name__, shim.layout.log)
        assert helpers.say(on, "Step 2 of 3: click the rod part. Esc cancels.", "Rod part").startswith("Step 2")
        assert helpers.say(off, "Step 2 of 3: click the rod part. Esc cancels.", "Rod part") == "Rod part"

        shim = Shim()
        helpers.draw_compact_toggle(shim.layout, on)
        (name, args, kw), = [x for x in shim.layout.log if x[0] == "prop"]
        assert args[1] == "show_helpers" and kw.get("invert_checkbox") and kw.get("toggle") and kw.get("text") == "Compact Mode"
        shim = Shim()
        helpers.draw_compact_toggle(shim.layout, bpy.context)
        assert not [x for x in shim.layout.log if x[0] == "prop"], "no preferences: no button"

        assert not hasattr(bpy.types.Scene, "boneforge_vrc_compact_mode"), "the scene property is retired"
        import inspect
        assert "boneforge_vrc_compact_mode" not in inspect.getsource(sidebar)
        prefs_cls = next(c for c in bpy.types.AddonPreferences.__subclasses__() if getattr(c, "bl_idname", "") == "boneforge")
        assert "show_helpers" in prefs_cls.__annotations__ and prefs_cls.__annotations__["show_helpers"].keywords["default"] is True
    finally:
        boneforge.unregister()
    print("PASS show helpers: one preference, existing explainers follow it, Compact Mode is a shortcut")
