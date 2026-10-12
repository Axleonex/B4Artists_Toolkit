# bonecraft/tests/test_wrap_layout_host.py
"""In-Bforartists test: every tab's panels wrap text to their region, on either side (owner, 2026-10-10).

core.wrap_layout gives each BoneCraft / CATS / Rig Builder viewport panel a layout that wraps a label
or button too wide for the region (the 132 px Tool Shelf or the 220 px sidebar) instead of letting
Blender cut it to "...". Text that fits, rows, and anything unusual pass through untouched.
"""
import bpy
from bpy.types import Panel

import boneforge
from mech_draw_stubs import Rec

LONG = "Select the armature and the meshes that belong to this avatar first."


class _Ctx:
    """bpy.context in a region ``width`` px wide; ``width`` 0 = no drawn region (background)."""
    def __init__(self, width):
        self.region = type("Region", (), {"width": width})() if width else None
        self.preferences = type("Prefs", (), {"system": type("Sys", (), {"ui_scale": 1.0})(), "addons": {}})()

    def __getattr__(self, name):
        return getattr(bpy.context, name)


def _labels(log):
    return [k.get("text") for n, a, k in log if n == "label"]


def _more(wl):
    """Buttons that use their operator's own label, long-labelled settings, headers, tools enabled later."""
    from boneforge.core.tool_registry import ToolManifest, ToolRegistry
    # a button with no text shows its operator's label: that wraps too
    log = []
    wl.WrapLayout(Rec(log), _Ctx(132)).operator("boneforge.open_health_check", icon='PLAY')
    ops = [k for n, a, k in log if n == "operator"]
    assert len(ops) >= 2 and " ".join(k["text"] for k in ops) == "Open Health Check", ops
    log = []
    wl.WrapLayout(Rec(log), _Ctx(1000)).operator("boneforge.open_health_check", icon='PLAY')
    assert log == [("operator", ("boneforge.open_health_check",), {"icon": 'PLAY'})], log

    # settings: a toggle button stacks like a button; a checkbox keeps its box on the first line;
    # any other setting puts its label above and the control the whole width below
    sc = bpy.types.Scene
    sc.bc_test_flag = bpy.props.BoolProperty()
    sc.bc_test_enum = bpy.props.EnumProperty(items=[("A", "A", "")])
    scene = bpy.context.scene
    try:
        long = "Compact mode for every part of this avatar"
        # a toggle too wide becomes a checkbox with its label wrapped: a stack of toggle segments
        # among other toggles would read as several buttons
        log = []
        wl.WrapLayout(Rec(log), _Ctx(132)).prop(scene, "bc_test_flag", text=long, toggle=True,
                                                invert_checkbox=True)
        props = [k for n, a, k in log if n == "prop"]
        assert len(props) == 1 and not props[0].get("toggle") and props[0].get("invert_checkbox"), props
        assert props[0].get("icon", 'NONE') == 'NONE', ("an icon would draw it as a button again", props)
        assert " ".join([props[0]["text"]] + _labels(log)) == long, log
        # its box narrows only the first line: a word that fits the full width is never split below it
        log = []
        wl.WrapLayout(Rec(log), _Ctx(132)).prop(scene, "bc_test_flag", text="Remove Zero-Weight Bones", toggle=True)
        words = [w for x in [k["text"] for n, a, k in log if n == "prop"] + _labels(log) for w in x.split()]
        assert words == ["Remove", "Zero-Weight", "Bones"], log
        # no text: Blender shows the property's own name, so that is what wraps
        sc.bc_test_named = bpy.props.BoolProperty(name=long)
        log = []
        wl.WrapLayout(Rec(log), _Ctx(132)).prop(scene, "bc_test_named", toggle=True)
        props = [k for n, a, k in log if n == "prop"]
        assert len(props) == 1 and " ".join([props[0]["text"]] + _labels(log)) == long, log
        log = []
        wl.WrapLayout(Rec(log), _Ctx(1000)).prop(scene, "bc_test_named", toggle=True)
        assert log == [("prop", (scene, "bc_test_named"), {})], ("fits: a plain checkbox, never a toggle button", log)
        log = []
        wl.WrapLayout(Rec(log), _Ctx(132)).prop(scene, "bc_test_flag", text=long)
        props = [k for n, a, k in log if n == "prop"]
        assert len(props) == 1 and " ".join([props[0]["text"]] + _labels(log)) == long, log
        log = []
        wl.WrapLayout(Rec(log), _Ctx(132)).prop(scene, "bc_test_enum", text="Target armature for this avatar")
        names = [n for n, a, k in log if n in ("label", "prop")]
        props = [k for n, a, k in log if n == "prop"]
        assert names[-1] == "prop" and "label" in names and props[0]["text"] == "", log
        assert " ".join(_labels(log)) == "Target armature for this avatar", log
        # Blender gives a setting's label well under half the row: "Body Type" goes above in the sidebar
        log = []
        wl.WrapLayout(Rec(log), _Ctx(220)).prop(scene, "bc_test_enum", text="Body Type")
        assert [n for n, a, k in log] == ["label", "prop"], log
        log = []
        wl.WrapLayout(Rec(log), _Ctx(260)).prop(scene, "bc_test_enum", text="Initial Pose")
        assert [n for n, a, k in log] == ["label", "prop"], ("clipped to 'Initial ...' inline at 260 px", log)
        log = []
        wl.WrapLayout(Rec(log), _Ctx(260)).prop(scene, "bc_test_enum", text="Mode")
        assert [n for n, a, k in log] == ["prop"], ("a short label stays inline", log)
        log = []
        wl.WrapLayout(Rec(log), _Ctx(132)).prop(scene, "bc_test_flag", text="On")
        assert log == [("prop", (scene, "bc_test_flag"), {"text": "On"})], log
    finally:
        del sc.bc_test_flag, sc.bc_test_enum
        if hasattr(sc, "bc_test_named"):
            del sc.bc_test_named

    # in a box in the 132 px shelf an icon would leave its line too little room: the icon goes, not the text
    from boneforge.core import helpers
    log = []
    helpers.draw_wrapped(Rec(log), _Ctx(132), "Tools for rigs you already have.", icon='INFO', inset=helpers._BOX)
    assert all(k.get("icon") == 'NONE' for n, a, k in log), log
    assert " ".join(_labels(log)) == "Tools for rigs you already have.", log
    log = []
    helpers.draw_wrapped(Rec(log), _Ctx(220), "Tools for rigs you already have.", icon='INFO', inset=helpers._BOX)
    assert log[0][2]["icon"] == 'INFO', ("the wider sidebar keeps it", log)
    # a button keeps its icon (what it does; a toggle's arrow: open or closed)
    log = []
    helpers.draw_wrapped_operator(Rec(log), _Ctx(132), "boneforge.taskboard_toggle_category", "Rig Controls (1)",
                                  icon='TRIA_DOWN', emboss=False)
    assert [k for n, a, k in log if n == "operator"][0]["icon"] == 'TRIA_DOWN', log
    # "Overview" fits a top-level header in the 132 px shelf, drag handle and all
    log = []
    wl.HeaderLayout(Rec(log), _Ctx(132), root=True).label(text="Overview")
    assert log[0][2]["text"] == "Overview", log

    # headers cannot wrap: the icon always goes, and in a narrow region the title is shortened, never blank
    log = []
    wl.HeaderLayout(Rec(log), _Ctx(132)).label(text="Translate Bone Names", icon='FILE_REFRESH')
    (n, a, k), = log
    assert k.get("icon", 'NONE') == 'NONE' and k["text"].endswith("…") and k["text"].startswith("Trans"), log
    # a top-level section's header also has a drag handle: its title gets less room
    sub_log, root_log = [], []
    wl.HeaderLayout(Rec(sub_log), _Ctx(132)).label(text="Setup Rigging for Avatars")
    wl.HeaderLayout(Rec(root_log), _Ctx(132), root=True).label(text="Setup Rigging for Avatars")
    assert len(root_log[0][2]["text"]) < len(sub_log[0][2]["text"]), (root_log, sub_log)
    log = []
    wl.HeaderLayout(Rec(log), _Ctx(220)).label(text="Visemes", icon='SHAPEKEY_DATA')
    assert log == [("label", (), {"text": "Visemes"})], ("a header never shows an icon, at any width", log)

    class BF_PT_test_late(Panel):
        bl_idname, bl_label = "BF_PT_test_late", "Late"
        bl_space_type, bl_region_type, bl_category = 'VIEW_3D', 'UI', "BoneCraft"
        __module__ = "boneforge.test_late"

        def draw_header(self, context):
            self.layout.label(text="Translate Bone Names", icon='FILE_REFRESH')

        def draw(self, context):
            self.layout.label(text=LONG)

    # a tool switched on after startup: its panels wrap too, headers included
    reg = ToolRegistry()
    reg.register_tool(ToolManifest(id="late", name="Late", description="",
                                   register_fn=lambda: bpy.utils.register_class(BF_PT_test_late)))
    reg.enable("late")
    try:
        assert getattr(BF_PT_test_late.draw, "_bc_wrap_layout", False), "a later tool's panel wraps"
        log = []
        BF_PT_test_late.draw_header(type("S", (), {"layout": Rec(log)})(), _Ctx(132))
        assert log[0][2]["text"].endswith("…"), log
    finally:
        bpy.utils.unregister_class(BF_PT_test_late)



def _settings_apart_from_actions(wl):
    """Icons are for operators: a setting never looks like a button, and settings and actions are set apart
    (UI critique, 2026-10-10: it was hard to tell an operator from a property)."""
    sc = bpy.types.Scene
    sc.bc_test_opt = bpy.props.BoolProperty(name="Fit")
    scene = bpy.context.scene
    try:
        # an icon toggle in a column becomes a plain checkbox, whatever the width
        for width in (0, 132, 1000):
            log = []
            wl.WrapLayout(Rec(log), _Ctx(width)).prop(scene, "bc_test_opt", text="Fit", toggle=True, icon='FULLSCREEN_ENTER')
            (n, a, k), = [x for x in log if x[0] == "prop"]
            assert k.get("icon", 'NONE') == 'NONE' and not k.get("toggle"), (width, "a setting is a checkbox", log)
        # an icon-only control and an unembossed fold arrow keep their icon: it is all they show
        log = []
        lay = wl.WrapLayout(Rec(log), _Ctx(1000))
        lay.prop(scene, "bc_test_opt", text="", icon='HIDE_OFF')
        lay.prop(scene, "bc_test_opt", icon='TRIA_DOWN', emboss=False)
        assert [k.get("icon") for n, a, k in log if n == "prop"] == ['HIDE_OFF', 'TRIA_DOWN'], log
        # settings, then actions: a gap between them; none between two of a kind, none after a label
        # in a row too (its width is shared, so nothing wraps there): a setting is not a button
        log = []
        wl.WrapLayout(Rec(log), _Ctx(1000)).row(align=True).prop(scene, "bc_test_opt", toggle=True, icon='CON_KINEMATIC')
        assert [k for n, a, k in log if n == "prop"] == [{}], log
        log = []
        lay = wl.WrapLayout(Rec(log), _Ctx(1000))
        lay.prop(scene, "bc_test_opt", text="Fit")
        lay.prop(scene, "bc_test_opt", text="Fit")
        lay.operator("boneforge.open_health_check", text="Go", icon='PLAY')
        lay.operator("boneforge.open_health_check", text="Go", icon='PLAY')
        lay.label(text="Next")
        lay.prop(scene, "bc_test_opt", text="Fit")
        kinds = [n for n, a, k in log if n in ("prop", "operator", "separator", "label")]
        assert kinds == ["prop", "prop", "separator", "operator", "operator", "label", "prop"], kinds
    finally:
        del sc.bc_test_opt



class _Folding:
    """A layout whose panel() folds like Blender's: (header, body), body None while closed."""
    def __init__(self, log, open_):
        self.log, self.open_ = log, open_

    def panel(self, idname, default_closed=False):
        self.log.append(("panel", (idname,), {"default_closed": default_closed}))
        return Rec(self.log), (Rec(self.log) if self.open_ else None)

    def __getattr__(self, name):
        return getattr(Rec(self.log), name)


def _options_fold(wl):
    """Actions first, their options in a fold below it, closed by default (UI critique, 2026-10-10)."""
    from boneforge.core import helpers
    log = []
    body = helpers.options_fold(wl.WrapLayout(_Folding(log, True), _Ctx(1000)), "bc_test_opts")
    assert ("panel", ("bc_test_opts",), {"default_closed": True}) in log, log
    assert ("label", (), {"text": "Options"}) in log, ("the fold is titled Options", log)
    assert isinstance(body, wl.WrapLayout), ("what is drawn inside still wraps", body)
    log = []
    assert helpers.options_fold(wl.WrapLayout(_Folding(log, False), _Ctx(1000)), "bc_test_opts") is None,         "closed: nothing to draw"
    # a layout with no folds (a stand-in, an old host): the options draw in a plain column
    log = []
    body = helpers.options_fold(Rec(log), "bc_test_opts")
    assert body is not None and ("column", (), {}) in log, log


def run():
    from boneforge.core import wrap_layout as wl

    # a label too wide for the Tool Shelf wraps; the words survive whole and in order
    log = []
    lay = wl.WrapLayout(Rec(log), _Ctx(132))
    lay.label(text=LONG, icon='INFO')
    lines = _labels(log)
    assert len(lines) >= 3 and " ".join(lines) == LONG, lines
    icons = [k.get("icon") for n, a, k in log if n == "label"]
    assert icons[0] == 'INFO' and set(icons[1:]) == {'NONE'}, icons

    # the wider right sidebar needs fewer lines; a text that fits is one ordinary, untouched call
    log = []
    wl.WrapLayout(Rec(log), _Ctx(220)).label(text=LONG)
    assert 1 < len(_labels(log)) < len(lines), _labels(log)
    log = []
    wl.WrapLayout(Rec(log), _Ctx(132)).label(text="Short", icon='INFO')
    assert log == [("label", (), {"text": "Short", "icon": 'INFO'})], log

    # no drawn region (background, tests): everything passes through exactly as called
    log = []
    wl.WrapLayout(Rec(log), _Ctx(0)).label(text=LONG, icon='INFO')
    assert log == [("label", (), {"text": LONG, "icon": 'INFO'})], log

    # a column or box keeps wrapping (a box narrows the room); a row's width is shared, so it passes through
    log = []
    root = wl.WrapLayout(Rec(log), _Ctx(220))
    assert isinstance(root.column(align=True), wl.WrapLayout) and isinstance(root.box(), wl.WrapLayout)
    assert not isinstance(root.row(), wl.WrapLayout) and not isinstance(root.split(), wl.WrapLayout)
    boxed, plain = [], []
    wl.WrapLayout(Rec(boxed), _Ctx(220)).box().label(text=LONG)
    wl.WrapLayout(Rec(plain), _Ctx(220)).label(text=LONG)
    assert len(_labels(boxed)) >= len(_labels(plain)), "a box has less room than its panel"

    # attributes set on the wrapper reach the real layout
    log = []
    w = wl.WrapLayout(Rec(log), _Ctx(132))
    w.enabled = False
    assert ("set", "enabled", False) in log

    # a button too wide splits into segments that run the same operator; props set on it reach every segment
    log = []
    op = wl.WrapLayout(Rec(log), _Ctx(132)).operator("boneforge.open_health_check", text="Open the Health Check now",
                                                     icon='PLAY')
    op.category = "RIG"
    ops = [k for n, a, k in log if n == "operator"]
    sets = [x for x in log if x[0] == "set" and x[1] == "category"]
    assert len(ops) >= 2 and len(sets) == len(ops), (ops, sets)
    log = []
    wl.WrapLayout(Rec(log), _Ctx(132)).operator("boneforge.open_health_check", text="Go")
    assert log == [("operator", ("boneforge.open_health_check",), {"text": "Go"})], log

    # install(): BoneCraft-tab panels draw through it, with helper methods seeing the wrapped layout too
    bpy.ops.wm.read_factory_settings(use_empty=True)
    boneforge.register()
    _more(wl)
    _settings_apart_from_actions(wl)
    _options_fold(wl)

    class BF_PT_test_wrap(Panel):
        bl_idname, bl_label = "BF_PT_test_wrap", "Test"
        bl_space_type, bl_region_type, bl_category = 'VIEW_3D', 'UI', "CATS"
        __module__ = "boneforge.test_wrap"

        def _body(self):
            self.layout.label(text=LONG)

        def draw(self, context):
            self._body()

    try:
        bpy.utils.register_class(BF_PT_test_wrap)
        wl.install()
        wl.install()                                       # idempotent: wraps once
        log = []
        shim = type("S", (), {"layout": Rec(log)})()
        BF_PT_test_wrap.draw(shim, _Ctx(220))
        assert len(_labels(log)) >= 2 and " ".join(_labels(log)) == LONG, _labels(log)
        # a hub that already draws through a wrapper (delegated draw) is not wrapped twice
        log = []
        shim = type("S", (), {"layout": wl.WrapLayout(Rec(log), _Ctx(220)),
                              "_body": BF_PT_test_wrap.__dict__["_body"]})()
        BF_PT_test_wrap.draw(shim, _Ctx(220))
        assert " ".join(_labels(log)) == LONG, _labels(log)
        assert getattr(bpy.types, "BF_PT_sb_overview").draw.__dict__.get("_bc_wrap_layout"), "the BoneCraft tab is wrapped"
    finally:
        bpy.utils.unregister_class(BF_PT_test_wrap)
        boneforge.unregister()
    print("PASS wrap layout: labels and buttons wrap to the region on either side; fitting text, rows and "
          "background draws pass through; every tab's panels draw through it")
