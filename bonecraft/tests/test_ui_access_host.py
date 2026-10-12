# bonecraft/tests/test_ui_access_host.py
"""In-Bforartists test: BoneCraft's tools sit where Bforartists puts its own (UI critique, 2026-10-10).

- Panel headers carry no icons; icons are for operators.
- Day-to-day operators are buttons in Bforartists' own Tool Shelf tabs (Pose, Weights), drawn the way
  Bforartists draws its tabs: operators only, each with an icon, no properties among them.
- Everything is reachable from a header menu: Add > Armature, Pose, Weights, Object.
"""
import bpy

import boneforge
from mech_draw_stubs import Ctx, Rec

SHELF = {"BC_PT_shelf_pose": ("Pose", "posemode"), "BC_PT_shelf_weights": ("Weights", "weightpaint")}
MENU_HOOKS = {"VIEW3D_MT_armature_add", "VIEW3D_MT_pose", "VIEW3D_MT_paint_weight", "VIEW3D_MT_object"}
TABS = {"BoneCraft", "CATS", "Rig Builder"}


class Shim:
    def __init__(self):
        self.layout = Rec([])


def _icons():
    return set(bpy.types.UILayout.bl_rna.functions["label"].parameters["icon"].enum_items.keys())


def _op_exists(idname):
    cat, name = idname.split(".", 1)
    return hasattr(getattr(bpy.ops, cat, None), name)


def _registered_panels():
    seen = set()

    def walk(c):
        for s in c.__subclasses__():
            seen.add(s)
            walk(s)
    walk(bpy.types.Panel)
    return [c for c in seen if getattr(c, "is_registered", False)]


def _ours(cls):
    idn = getattr(cls, "bl_idname", "")
    return getattr(cls, "bl_category", "") in TABS or idn.startswith(("BF_PT_", "BONEFORGE_PT_", "CATS_PT_", "BC_PT_"))


def _header_icons():
    out = []
    for cls in _registered_panels():
        if not _ours(cls) or "draw_header" not in dir(cls):
            continue
        shim = Shim()
        try:
            cls.draw_header(shim, bpy.context)
        except Exception:                                  # noqa: BLE001 - a header that needs a real panel
            continue
        for n, a, k in shim.layout.log:
            if n in ("label", "prop", "operator") and k.get("icon", 'NONE') not in ('NONE', None):
                out.append((cls.bl_idname, k.get("text"), k["icon"]))
    return out


def _check_shelf(icons):
    for idn, (category, ctx) in SHELF.items():
        cls = getattr(bpy.types, idn, None)
        assert cls is not None, (idn, "not registered")
        assert cls.bl_space_type == 'VIEW_3D' and cls.bl_region_type == 'TOOLS', (idn, cls.bl_region_type)
        assert cls.bl_category == category and cls.bl_context == ctx, (idn, cls.bl_category, cls.bl_context)
        shim = Shim()
        cls.draw(shim, Ctx())
        log = shim.layout.log
        ops = [(a[0], k) for n, a, k in log if n == "operator"]
        assert ops, (idn, "draws no buttons")
        assert not [n for n, a, k in log if n in ("prop", "menu", "label")], (idn, "operators only", log)
        for op, k in ops:
            assert _op_exists(op), (idn, op, "no such operator")
            assert k.get("icon", 'NONE') in icons and k.get("icon") != 'NONE', (idn, op, k.get("icon"))


def _check_menus():
    for hook in MENU_HOOKS:
        funcs = getattr(getattr(bpy.types, hook).draw, "_draw_funcs", [])
        assert any(getattr(f, "__module__", "").startswith("boneforge") for f in funcs), (hook, "no BoneCraft entry")
    from boneforge.core import access
    for menu in access.MENUS:
        shim = Shim()
        menu.draw(shim, bpy.context)
        log = shim.layout.log
        assert not [n for n, a, k in log if n == "prop"], (menu.bl_idname, "a menu holds operators, not settings")
        for n, a, k in log:
            if n == "operator":
                assert _op_exists(a[0]), (menu.bl_idname, a[0], "no such operator")
            if n == "menu":
                assert getattr(bpy.types, a[0], None) is not None, (menu.bl_idname, a[0], "no such menu")


def run():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    boneforge.register()
    try:
        icons = _icons()
        bad = _header_icons()
        assert not bad, ("panel headers carry no icons", bad)
        _check_shelf(icons)
        _check_menus()
    finally:
        boneforge.unregister()
    # unregister leaves the host's menus as they were
    for hook in MENU_HOOKS:
        funcs = getattr(getattr(bpy.types, hook).draw, "_draw_funcs", [])
        assert not any(getattr(f, "__module__", "").startswith("boneforge") for f in funcs), (hook, "left behind")
    assert getattr(bpy.types, "BC_PT_shelf_pose", None) is None, "shelf panel left behind"
