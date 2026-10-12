"""Tests for R7 control picker / rig UI.

Headless (``python tests/test_picker.py``): the pure layout core — auto-layout
from collections, validation, JSON round-trip, side-mirror.

In-host (``run()``): generate a layout from a live engine rig, select controls
by name (active-bone path), mirror, selection sets, per-character state for two
rigs, and a JSON layout round-trip.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def headless():
    from boneforge.control_ui import layout as L
    colls = {
        "IK": ["forearm.ik-L", "shin.ik-L"],
        "FK": ["upperarm.fk-L"],
        "Root": ["root"],
        "Deform": ["upperarm.def-L"],   # must be excluded (not a control)
        "MCH": ["properties"],          # must be excluded
    }
    lay = L.auto_generate_layout(colls)
    assert L.validate_layout(lay) == [], L.validate_layout(lay)
    cb = L.control_bones(lay)
    assert "forearm.ik-L" in cb and "root" in cb
    assert "upperarm.def-L" not in cb and "properties" not in cb, "deform leaked"
    # JSON round-trips exactly
    lay2 = L.layout_from_json(L.layout_to_json(lay))
    assert lay2 == lay, "layout JSON did not round-trip"
    # layout edit helpers return edited copies and preserve JSON structure
    moved = L.move_control(lay, "forearm.ik-L", dx=0.26, dy=0.24,
                           snap=True, grid=0.25)
    assert moved is not lay
    moved_rect = L.find_control(moved, "forearm.ik-L")["rect"]
    old_rect = L.find_control(lay, "forearm.ik-L")["rect"]
    assert moved_rect[0] == old_rect[0] + 0.25
    assert moved_rect[1] == old_rect[1] + 0.25
    resized = L.resize_control(moved, "forearm.ik-L", dw=-10.0, dh=-10.0)
    assert L.find_control(resized, "forearm.ik-L")["rect"][2] >= 0.1
    relabeled = L.relabel_control(resized, "forearm.ik-L", "Forearm IK")
    assert L.find_control(relabeled, "forearm.ik-L")["label"] == "Forearm IK"
    assert L.validate_layout(L.layout_from_json(L.layout_to_json(relabeled))) == []
    # mirror
    assert L.mirror_bone_name("upperarm.fk-L") == "upperarm.fk-R"
    assert L.mirror_selection(["a-L", "b-R", "COG"]) == ["a-R", "b-L", "COG"]
    print("test_picker PASS  (auto-layout, validate, JSON round-trip, mirror)")


# ── in-host ──────────────────────────────────────────────────

def run():
    import bpy
    import test_rig_build as trb
    from boneforge.autorig.rig_build import RigSpec, build_control_rig
    from boneforge.control_ui import layout as L
    from boneforge.control_ui import picker
    from boneforge.control_ui import selection_sets as ss

    arm_a = trb._fresh_armature(); arm_a.name = "RIG_A"
    build_control_rig(arm_a, RigSpec())
    arm_b = trb._fresh_armature(); arm_b.name = "RIG_B"
    build_control_rig(arm_b, RigSpec())

    # auto-generate a layout from the live rig's collections
    layout = picker.ensure_layout(arm_a)
    cb = set(L.control_bones(layout))
    assert "forearm.ik-L" in cb and "upperarm.fk-L" in cb, "controls missing"
    assert not any(".def-" in n for n in cb), "deform bones leaked into picker"
    assert not any(n == "properties" for n in cb), "MCH leaked into picker"
    print("picker layout generated (%d controls, no deform/MCH)" % len(cb))

    # selection by control -> active bone matches exactly
    n = picker.select_control_bones(arm_a, ["forearm.ik-L"])
    assert n == 1 and arm_a.data.bones.active.name == "forearm.ik-L", \
        ("selection mismatch", arm_a.data.bones.active)
    # the viewport selection too, not only the active bone (on Blender 5 the
    # old highlight call failed silently and nothing was selected)

    def selected(arm):
        if hasattr(arm.pose.bones[0], "select"):
            return {p.name for p in arm.pose.bones if p.select}
        return {b.name for b in arm.data.bones if b.select}
    assert selected(arm_a) == {"forearm.ik-L"}, ("viewport selection", selected(arm_a))
    picker.select_control_bones(arm_a, ["shin.ik-R"], extend=True)
    assert selected(arm_a) == {"forearm.ik-L", "shin.ik-R"}, ("multi-select", selected(arm_a))
    # mirror selection -> the -R partner
    picker.select_control_bones(arm_a, L.mirror_selection(["forearm.ik-L"]))
    assert arm_a.data.bones.active.name == "forearm.ik-R", "mirror failed"
    assert selected(arm_a) == {"forearm.ik-R"}, ("replace selection", selected(arm_a))
    print("picker selection + mirror verified (active bone and viewport selection, "
          "multi-select extends, plain click replaces)")
    # the panel shows what is selected (pressed buttons) with readable labels
    assert picker._is_selected(arm_a, "forearm.ik-R")
    assert not picker._is_selected(arm_a, "forearm.ik-L")
    assert picker.pretty_label("forearm.ik-L") == "forearm IK L"
    assert picker.pretty_label("COG") == "COG"
    ids = sorted(({"id": i} for i in ("thigh.fk-R", "hips", "thigh.fk-L")), key=picker._pair_key)
    assert [c["id"] for c in ids] == ["hips", "thigh.fk-L", "thigh.fk-R"], ids
    print("picker panel shows the selection, left/right paired, readable labels")

    # selection sets (per-character)
    ss.store_set(arm_a, "hands", ["hand.fk-L", "hand.fk-R"])
    assert "hands" in ss.get_sets(arm_a)
    picker.select_control_bones(arm_a, ss.get_sets(arm_a)["hands"])
    assert arm_a.data.bones.active.name in ("hand.fk-L", "hand.fk-R")

    # per-character state isolation: B has its own (empty) sets + own layout
    assert ss.get_sets(arm_b) == {}, "selection sets leaked across rigs"
    picker.set_layout(arm_b, picker.generate_layout(arm_b))
    # tamper A's layout; B's must be unaffected
    trimmed = {"version": L.LAYOUT_VERSION, "controls": layout["controls"][:3]}
    picker.set_layout(arm_a, trimmed)
    assert len(picker.get_layout(arm_a)["controls"]) == 3
    assert len(picker.get_layout(arm_b)["controls"]) > 3, "rig state cross-talk"
    print("per-character picker state verified (two rigs independent)")

    # inline IK/FK from R3 is reachable on the same controls
    from boneforge.advanced_rigging import control_layer as cl
    assert any(nm["prop"] == "IK_FK-arm-L" for nm in cl.discover_limbs(arm_a))
    print("inline IK/FK reachable from picker controls")

    # JSON layout round-trips through a string (import/export)
    text = L.layout_to_json(picker.generate_layout(arm_a))
    again = L.layout_from_json(text)
    assert L.validate_layout(again) == []
    print("layout JSON round-trip verified")
    print("ALL PICKER TESTS PASS")


if __name__ == "__main__":
    headless()
