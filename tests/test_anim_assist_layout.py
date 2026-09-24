"""Anim Assist layout check: no 3D Viewport sidebar tab, three organised homes.

Run with:
    bforartists --background --factory-startup --python tests/test_anim_assist_layout.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import anim_assist  # noqa: E402
from anim_assist import constants  # noqa: E402
from anim_assist.ui import header_menus, layout_homes  # noqa: E402


def _walk(cls):
    for sub in cls.__subclasses__():
        yield sub
        yield from _walk(sub)


def _our_panels() -> list[type]:
    seen: dict[str, type] = {}
    for cls in _walk(bpy.types.Panel):
        if (cls.__module__ or "").startswith("anim_assist") and getattr(cls, "is_registered", False):
            seen[cls.__name__] = cls
    return list(seen.values())


def _parent_chain(cls, by_idname) -> list[str]:
    chain, parent = [], getattr(cls, "bl_parent_id", "")
    while parent:
        chain.append(parent)
        parent = getattr(by_idname.get(parent), "bl_parent_id", "")
    return chain


def main() -> None:
    anim_assist.register()
    try:
        panels = _our_panels()
        by_idname = {getattr(c, "bl_idname", c.__name__): c for c in panels}

        # 1. Nothing in the 3D Viewport sidebar.
        viewport = [c.__name__ for c in panels
                    if c.bl_space_type == "VIEW_3D" and c.bl_region_type == "UI"]
        assert not viewport, f"3D Viewport sidebar still has Anim Assist panels: {viewport}"

        # 2. Graph Editor / Dope Sheet: one tab, only title + groups at the top level.
        for space, (_subtitle, groups) in layout_homes.SIDEBARS.items():
            sidebar = [c for c in panels if c.bl_space_type == space and c.bl_region_type == "UI"]
            cats = {c.bl_category for c in sidebar}
            assert cats == {constants.ANIMASSIST_CATEGORY}, (space, cats)
            top = {getattr(c, "bl_idname", c.__name__) for c in sidebar if not getattr(c, "bl_parent_id", "")}
            expected = {layout_homes.sidebar_group_idname(space, "title")}
            expected |= {layout_homes.sidebar_group_idname(space, g.key) for g in groups}
            assert top == expected, (space, sorted(top ^ expected))
            for group in groups:
                for name in group.panels:
                    assert name in {c.__name__ for c in sidebar}, (space, name)

        # 3. Properties home: everything under the root, grouped by scope.
        home = [c for c in panels if c.bl_space_type == "PROPERTIES" and c.bl_region_type == "WINDOW"]
        for cls in home:
            assert cls.bl_context == layout_homes.PROPERTIES_CONTEXT, cls.__name__
            idname = getattr(cls, "bl_idname", cls.__name__)
            if idname != layout_homes.HOME_ROOT_IDNAME:
                assert layout_homes.HOME_ROOT_IDNAME in _parent_chain(cls, by_idname), idname
        home_names = {c.__name__ for c in home}
        for group in layout_homes.PROPERTIES_GROUPS:
            assert layout_homes.home_group_idname(group.key) in home_names, group.key
            for name in group.panels:
                assert name in home_names, name

        # 4. The three homes are organised differently.
        orders = [tuple(g.label for g in groups) for _s, groups in layout_homes.SIDEBARS.values()]
        orders.append(tuple(g.label for g in layout_homes.PROPERTIES_GROUPS))
        assert len(set(orders)) == 3, orders

        # 5. Every menu and pie entry points at a real operator.
        ops = set(dir(bpy.ops.animassist))
        for space, (_target, _pref, submenus) in header_menus.MENUS.items():
            for _key, _label, _icon, entries in submenus:
                missing = [e for e in entries if e is not None and e not in ops]
                assert not missing, (space, missing)
            assert hasattr(bpy.types, header_menus.menu_idname(space)), space
        missing = [op for op, _t, _i in header_menus.PIE_SLOTS if op not in ops]
        assert not missing, missing
        for op in ("open_home", "open_home_window", "add_workspace"):
            assert op in ops, op

        # 6. Every new preference has a tooltip.
        prefs_rna = anim_assist.AA_AddonPreferences.bl_rna.properties
        for name in ("pie_hotkey_enabled", "header_menu_view3d", "header_menu_graph", "header_menu_dopesheet"):
            assert prefs_rna[name].description, name

        print(f"LAYOUT OK: {len(panels)} panels, 0 in the 3D Viewport sidebar")
    finally:
        anim_assist.unregister()

    leftovers = [c.__name__ for c in _our_panels()]
    assert not leftovers, f"panels left registered: {leftovers}"
    print("UNREGISTER OK")


if __name__ == "__main__":
    main()
