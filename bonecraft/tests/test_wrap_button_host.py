# bonecraft/tests/test_wrap_button_host.py
"""In-Bforartists test: a button too wide for the shelf splits into stacked segments (owner, 2026-10-10).

Blender cannot wrap a button's text, so helpers.draw_wrapped_operator draws one aligned button per
wrapped line, all running the same operator: it reads as one tall button and nothing is cut off.
"""
from boneforge.core import helpers
from mech_draw_stubs import Rec


def _ctx(width):
    region = type("Region", (), {"width": width})() if width else None
    prefs = type("Prefs", (), {"system": type("Sys", (), {"ui_scale": 1.0})()})()
    return type("Ctx", (), {"region": region, "preferences": prefs})()


def _ops(log):
    return [(a, k) for n, a, k in log if n == "operator"]


def run():
    # the default 132 px Tool Shelf: "Open Health Check" in a card does not fit on one button
    log = []
    made = helpers.draw_wrapped_operator(Rec(log), _ctx(132), "boneforge.open_health_check",
                                         "Open Health Check", icon='PLAY', inset=helpers._BOX)
    calls = _ops(log)
    assert len(calls) >= 2, ("split into segments", calls)
    assert all(a == ("boneforge.open_health_check",) for a, k in calls), "every segment runs the same operator"
    assert " ".join(k["text"] for a, k in calls) == "Open Health Check", "nothing lost, nothing added"
    assert calls[0][1]["icon"] == 'PLAY' and all(k["icon"] == 'NONE' for a, k in calls[1:]), "icon once, on top"
    assert len(made) == len(calls), "every segment is returned, so callers can set its properties"
    assert ("column", (), {"align": True}) in log, "segments are aligned: they read as one button"

    # emboss passes through (Task Board's category toggles are flat)
    log = []
    helpers.draw_wrapped_operator(Rec(log), _ctx(132), "boneforge.taskboard_toggle_category",
                                  "Rig Controls (2)", icon='TRIA_DOWN', emboss=False)
    calls = _ops(log)
    assert len(calls) >= 2 and all(k["emboss"] is False for a, k in calls), calls
    assert ("set", "alignment", 'LEFT') in log, "a flat toggle stays left-aligned like a heading"

    # room to spare, or no drawn region (background): one ordinary button
    for ctx in (_ctx(1000), _ctx(0)):
        log = []
        helpers.draw_wrapped_operator(Rec(log), ctx, "boneforge.open_health_check", "Open Health Check", icon='PLAY')
        calls = _ops(log)
        assert len(calls) == 1 and calls[0][1]["text"] == "Open Health Check", calls
    _cats_side()
    print("PASS wrapped buttons: split into aligned segments that share one operator; one button when it fits; "
          "the CATS side wraps too")


class _Side:
    """bpy.context in a right sidebar ``width`` px wide (the add-on's preferences stubbed)."""
    def __init__(self, width):
        self.region = type("Region", (), {"width": width})()
        self.preferences = type("Prefs", (), {"system": type("Sys", (), {"ui_scale": 1.0})(), "addons": {}})()

    def __getattr__(self, name):
        import bpy
        return getattr(bpy.context, name)


def _labels(log):
    return [k.get("text") for n, a, k in log if n == "label" and k.get("text")]


def _cats_side():
    """The right sidebar (CATS tab, 220 px) wraps like the left shelf: nothing ends in '...'."""
    import bpy
    import boneforge
    bpy.ops.wm.read_factory_settings(use_empty=True)
    boneforge.register()
    try:
        bpy.ops.object.armature_add()
        side = _Side(220)
        log = []
        bpy.types.BF_PT_sb_vrchat.draw(type("S", (), {"layout": Rec(log)})(), side)
        texts = _labels(log)
        for whole in ("A — VRChat setup: humanoid bones.", "Performance, clothing and naming: VRChat Tools, below.",
                      "Cats users: Fix Model / Join Meshes / Cleanup /"):
            assert whole not in texts, (whole, "drawn on one clipped line")
        joined = " ".join(texts)                           # wrapping breaks only at spaces: rejoined, every sentence is whole
        for whole in ("A — VRChat setup: humanoid bones.", "B — Body & Physics: hair, visemes.", "C — Finalize: export.",
                      "Performance, clothing and naming: VRChat Tools, below.",
                      "Cats users: Fix Model / Join Meshes / Cleanup / Translate live in the main CATS tool stack."):
            assert whole in joined, (whole, "lost or changed by the wrap", texts)
        # the Armature picker: its label on its own line, the menu the whole width
        log = []
        bpy.types.CATS_PT_target_armature.draw(type("S", (), {"layout": Rec(log)})(), side)
        props = [k for n, a, k in log if n == "prop" and a[1:] == ("boneforge_cats_target_armature_name",)]
        assert props and props[0].get("text") == "", ("the picker leaves its label off", props)
        assert "Armature" in _labels(log), _labels(log)
    finally:
        boneforge.unregister()
