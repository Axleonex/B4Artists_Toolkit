"""In-Bforartists test: Rig Builder in Properties > Scene tab (permanent) plus an
optional Rig Builder tab on the left Tool Shelf (Show Rig Builder switch).

* the four Rig Builder panels register in PROPERTIES / WINDOW / scene and the
  hub polls true with nothing selected, a camera active, and every switch off;
* a "_Shelf" copy of each exists in VIEW_3D / TOOLS / "Rig Builder", children
  under their parent's copy; the shelf hub follows Show Rig Builder;
* no Rig Builder panel in the 3D-viewport sidebar (UI region);
* the shelf copies draw without raising; the hub header reads "Rig Builder".
"""
import bpy

import boneforge

RB = ("BF_PT_rb_setup", "BF_PT_sb_quick_rig", "BF_PT_sb_wizard", "BF_PT_rb_mannequin")
SHELF = "_Shelf"


class _Rec:
    def __init__(self, log):
        self.__dict__["log"] = log
    def __getattr__(self, name):
        def call(*a, **k):
            self.log.append((name, a, k))
            return _Rec(self.log)
        return call
    def __setattr__(self, name, value):
        self.log.append(("set", name, value))


class _Shim:
    def __init__(self):
        self.layout = _Rec([])


class _Prefs:
    def __init__(self, on):
        self.show_tab_boneforge = self.show_tab_cats = self.show_tab_rig_builder = on
    def __getattr__(self, name):
        return True


class _Preferences:
    def __init__(self, on):
        self.addons = {"boneforge": type("A", (), {"preferences": _Prefs(on)})()}
    def __getattr__(self, name):
        return getattr(bpy.context.preferences, name)


class _Ctx:
    def __init__(self, on):
        self.preferences = _Preferences(on)
    def __getattr__(self, name):
        return getattr(bpy.context, name)


class _Instance(_Shim):
    """Stand-in panel instance: methods resolve through the panel class, as in Blender."""
    def __init__(self, panel_cls):
        super().__init__()
        self._cls = panel_cls
    def __getattr__(self, name):
        import types
        value = getattr(self._cls, name)
        return types.MethodType(value, self) if callable(value) and not isinstance(value, type) else value


def _draws_cleanly(panel_cls):
    """Draw into a recording layout; return the error labels it produced."""
    shim = _Instance(panel_cls)
    panel_cls.draw(shim, bpy.context)
    return [k.get("text") for n, a, k in shim.layout.log
            if n == "label" and isinstance(k, dict) and k.get("icon") == "ERROR"], shim.layout.log


def run():
    import addon_utils
    addon_utils.enable("rigify")                               # review finding: exercise Rigify groups
    boneforge.register()
    try:
        from boneforge.autorig import rb_placement as rp     # after register: modules may reload
        from boneforge.core import prefs as prefs_mod
        want = rp.SCENE_PLACEMENT
        for name in RB:
            cls = getattr(bpy.types, name, None)
            assert cls is not None and cls.is_registered, ("not registered", name)
            assert (cls.bl_space_type, cls.bl_region_type, cls.bl_context) == (
                want["bl_space_type"], want["bl_region_type"], want["bl_context"]), name
            shelf = getattr(bpy.types, name + SHELF, None)
            assert shelf is not None, ("no Tool Shelf copy", name)
            assert (shelf.bl_space_type, shelf.bl_region_type, shelf.bl_category) == (
                "VIEW_3D", "TOOLS", rp.RB_CATEGORY), name
            if name != "BF_PT_rb_setup":
                assert shelf.bl_parent_id == "BF_PT_rb_setup" + SHELF, (name, shelf.bl_parent_id)
            errors, _log = _draws_cleanly(shelf)              # must not raise or draw errors
            assert errors == [], ("Tool Shelf copy drew error labels", name, errors)
            missing = [m for m, v in vars(cls).items()
                       if callable(v) and not m.startswith("__") and not hasattr(shelf, m)]
            assert missing == [], ("Tool Shelf copy lacks helper methods", name, missing)
        _errors, log = _draws_cleanly(bpy.types.BF_PT_sb_quick_rig_Shelf)
        metarig_buttons = [a for n, a, k in log if n == "operator" and a and a[0] == "boneforge.add_quick_rig"]
        assert len(metarig_buttons) > 1, ("Rigify metarig buttons missing on the Tool Shelf", len(metarig_buttons))
        in_sidebar = [c.__name__ for c in bpy.types.Panel.__subclasses__()
                      if getattr(c, "is_registered", False)
                      and getattr(c, "bl_category", "") == rp.RB_CATEGORY
                      and getattr(c, "bl_region_type", "") == "UI"]
        assert in_sidebar == [], ("Rig Builder panel in the 3D-viewport sidebar", in_sidebar)
        assert "rig_builder_location" not in prefs_mod.BoneForgePreferences.__annotations__

        hub = bpy.types.BF_PT_rb_setup
        shelf_hub = bpy.types.BF_PT_rb_setup_Shelf
        bpy.context.view_layer.objects.active = None
        assert hub.poll(bpy.context), "Scene tab: Rig Builder must show with nothing selected"
        assert hub.poll(_Ctx(False)), "Scene tab: Rig Builder must ignore the Show Rig Builder switch"
        bpy.ops.object.camera_add()
        assert hub.poll(bpy.context), "Scene tab: Rig Builder must show with a camera active"
        assert shelf_hub.poll(_Ctx(True)) and not shelf_hub.poll(_Ctx(False)), \
            "Tool Shelf tab must follow the Show Rig Builder switch"

        panel = _Shim()
        hub.draw_header(panel, bpy.context)
        assert [k.get("text") for n, a, k in panel.layout.log if n == "label"] == ["Rig Builder"]
    finally:
        boneforge.unregister()
    leftovers = [c.__name__ for c in bpy.types.Panel.__subclasses__()
                 if getattr(c, "is_registered", False) and c.__name__.endswith(SHELF)]
    assert leftovers == [], ("Tool Shelf copies left after unregister", leftovers)
    print("PASS rig builder placement: Scene tab permanent, optional Tool Shelf tab")
