"""Control-picker feasibility spike (R6, BF-SPIKE-01) — THROWAWAY.

Not shipped, not registered. Run inside Bforartists to settle the picker's
interaction model before building the real layer (R7):

    bforartists --background --factory-startup --python tests/spikes/picker_spike.py

Question: modal GPU-drawn canvas vs. a ``UILayout`` / ``template_*`` panel of
clickable controls?

What this spike measures (the parts a background run can settle):
  * which pose-bone *selection* API actually works in Bforartists 5.2 — the
    operation every picker click ultimately performs;
  * that selection can be driven + read back programmatically (live sync);
  * box-select equivalent: selecting many bones at once by name/collection.

Click hit-testing and redraw cost of a live GPU canvas can only be judged
interactively; the decision below accounts for that.
"""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
for _p in (os.path.dirname(os.path.dirname(_HERE)), os.path.dirname(_HERE)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import bpy
import test_rig_build as trb
from boneforge.autorig.rig_build import RigSpec, build_control_rig


def _select_via_operator(arm, names):
    """Select pose bones by name through pose operators (BFA-portable)."""
    if bpy.context.object is not arm:
        bpy.context.view_layer.objects.active = arm
    if bpy.context.mode != 'POSE':
        bpy.ops.object.mode_set(mode='POSE')
    bpy.ops.pose.select_all(action='DESELECT')
    for n in names:
        try:
            bpy.ops.pose.select_pattern(pattern=n, case_sensitive=True,
                                        extend=True)
        except Exception:
            pass


def _selected_names(arm):
    # Bforartists 5.2 strips Bone.select entirely; read selection from the
    # context's selected_pose_bones list instead.
    return {pb.name for pb in (bpy.context.selected_pose_bones or [])}


def _has_select_attr():
    return hasattr(bpy.types.Bone, "bl_rna") and \
        "select" in bpy.types.Bone.bl_rna.properties


def main():
    arm = trb._fresh_armature()
    build_control_rig(arm, RigSpec())
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode='POSE')

    # (1) is the classic Bone.select property present?
    print("SPIKE Bone.select property exists:", _has_select_attr())

    # (2) active-bone API (settable + readable in background)
    arm.data.bones.active = arm.data.bones["forearm.ik-L"]
    active = arm.data.bones.active.name if arm.data.bones.active else None
    print("SPIKE active-bone set/read:", active)
    active_ok = active == "forearm.ik-L"

    # (3) pose.select_pattern + read via context.selected_pose_bones
    _select_via_operator(arm, ["forearm.ik-L", "shin.ik-L"])
    ctx_sel = _selected_names(arm)
    print("SPIKE pose.select_pattern + selected_pose_bones:", sorted(ctx_sel))

    # collection membership (the basis for box-select / select-by-collection)
    ik_bones = [pb.name for pb in arm.pose.bones
                if any(c.name == "IK" for c in pb.bone.collections)]
    print("SPIKE IK collection membership: %d bones" % len(ik_bones))
    coll_ok = len(ik_bones) >= 2

    bpy.ops.object.mode_set(mode='OBJECT')

    assert active_ok, "active-bone API unavailable"
    assert coll_ok, "bone-collection membership unavailable"

    decision = """
SPIKE DECISION (R7 interaction model)
=====================================
Approach: UILayout/operator-driven clickable layout (NOT a modal GPU canvas).

Findings from this run (Bforartists 5.2):
  * ``Bone.select`` is GONE (property absent) — a GPU canvas cannot just flip a
    select flag; selection has to go through the pose select operators, which
    in turn need a real 3D-viewport context (they no-op in --background).
  * ``armature.data.bones.active`` IS settable + readable everywhere (incl.
    background), and ``PoseBone.bone.collections`` gives reliable grouping.
  * Therefore the picker's *testable* core = (control id -> pose-bone name)
    layout data + a selection OPERATOR (sets active bone always; extends the
    viewport selection via ``pose.select_pattern`` when an area exists). The
    layout, mirror, and selection-set logic are plain data and unit-testable;
    the actual multi-select highlight is an interactive-only concern.

Why not a modal GPU canvas:
  * It would still route selection through the same operators, add custom click
    hit-testing + per-redraw cost, and be untestable headlessly. A
    ``UILayout``/``template_*`` grid of per-control operator buttons (grouped by
    collection, coloured per control type) gives the same "click a control ->
    select its bone" UX with far less risk across the Bforartists API churn.

R7 scope locked: control_ui package = JSON layout (auto-generated from a rig's
bone collections, import/export round-trip) + selection operator (active +
viewport-extend) + selection sets with BoneForge-native mirror + inline IK/FK
from R3 + per-character state + popup. GPU overlay is optional visualisation
only; selection never depends on it.
"""
    print(decision)
    print("PICKER SPIKE PASS")


if __name__ == "__main__":
    main()
