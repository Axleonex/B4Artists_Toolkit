"""In-Bforartists behavioural test for the R3 control-usability layer.

Builds a generated engine rig + skinned mesh and verifies the animator
control operations behave:

  * the IK/FK blend driver actually engages on a switch;
  * IK->FK snap is exact (no pop) — it copies the solved chain onto FK;
  * FK->IK snap lands the IK control exactly on the FK end-effector, puts the
    pole on the bend side, and turns the pole angle until the solved elbow
    sits on the FK elbow. (Checking only the hand missed a 5-11 cm elbow
    flip seen in the viewport pass, 2026-09-26.)
  * frame-range bake produces keys; foot-roll drives the mesh; global scale
    respects protected locks; per-character state stays isolated.
"""
import math

import bpy

import test_rig_build as trb
from boneforge.autorig.rig_build import RigSpec, build_control_rig
from boneforge.advanced_rigging import control_layer as cl
from boneforge.advanced_rigging import control_math as cm


def _build_rig():
    arm = trb._fresh_armature()
    build_control_rig(arm, RigSpec())
    return arm


def _limb(arm, prop):
    for names in cl.discover_limbs(arm):
        if names["prop"] == prop:
            return names
    raise AssertionError("limb %s not found" % prop)


def _action_fcurves(action):
    """F-curves of an action across legacy and slotted (4.4+) action APIs."""
    layers = getattr(action, "layers", None)
    if layers:
        fcurves = []
        for layer in layers:
            for strip in layer.strips:
                for cb in getattr(strip, "channelbags", []):
                    fcurves.extend(cb.fcurves)
        if fcurves:
            return fcurves
    return list(getattr(action, "fcurves", []))


def _eval_constraint_influence(arm, bone, con_name):
    deps = bpy.context.evaluated_depsgraph_get()
    deps.update()
    ev = arm.evaluated_get(deps)
    return ev.pose.bones[bone].constraints[con_name].influence


def test_blend_driver_engages():
    arm = _build_rig()
    names = _limb(arm, "IK_FK-arm-L")
    def_bone = names["def"][0]
    # FK by default -> the IK-blend influence is 0
    cl._set_blend(arm, names, to_ik=False)
    assert _eval_constraint_influence(arm, def_bone, "BF_IKblend-0") < 0.5
    # switching to IK must drive it to 1
    cl.switch_limb(arm, names, to_ik=True)
    assert _eval_constraint_influence(arm, def_bone, "BF_IKblend-0") > 0.5, \
        "IK/FK blend driver did not engage on switch"
    print("blend driver verified (FK->IK engages the IK-blend influence)")
    trb._clear_pose(arm)


def test_ik_to_fk_exact():
    """IK -> FK copies the solved chain onto FK: must not pop the mesh."""
    arm = _build_rig()
    obj = trb._skinned_mesh(arm)
    names = _limb(arm, "IK_FK-arm-L")
    # make an IK-driven pose: blend to IK and move the IK control
    cl._set_blend(arm, names, to_ik=True)
    ik = arm.pose.bones[names["ik"]]
    ik.location = (0.0, 0.0, 0.25)
    bpy.context.view_layer.update()
    ik_coords = trb._eval_world_coords(obj)
    # snap to FK and switch
    cl.switch_limb(arm, names, to_ik=False)
    fk_coords = trb._eval_world_coords(obj)
    pop = trb._max_disp(ik_coords, fk_coords)
    assert pop < 0.01, ("IK->FK switch popped the mesh", pop)
    print("no-pop IK->FK verified (max pop = %.4f)" % pop)
    trb._clear_pose(arm)


def test_fk_to_ik_endeffector():
    """FK -> IK must land the IK control on the FK end-effector + set a pole."""
    arm = _build_rig()
    names = _limb(arm, "IK_FK-arm-L")
    arm.pose.bones["properties"]["IK_FK-arm-L"] = 0.0
    for bone_name, ang in zip(names["fk"], (30, 75, 0)):
        pb = arm.pose.bones[bone_name]
        pb.rotation_mode = 'XYZ'
        pb.rotation_euler = (0.0, 0.0, math.radians(ang))
    bpy.context.view_layer.update()
    fk_hand = arm.pose.bones[names["fk"][2]].head.copy()
    fk_elbow = arm.pose.bones[names["fk"][1]].head.copy()
    shoulder = arm.pose.bones[names["fk"][0]].head.copy()

    cl.snap_ik_to_fk(arm, names)
    ik_head = arm.pose.bones[names["ik"]].head.copy()
    assert (ik_head - fk_hand).length < 1e-4, \
        ("IK control did not land on FK hand", (ik_head - fk_hand).length)

    # pole sits on the FK bend side (same side of the chord as the FK elbow)
    chord = (fk_hand - shoulder)
    pole_head = arm.pose.bones[names["pole"]].head.copy()
    n_elbow = (fk_elbow - shoulder) - chord * ((fk_elbow - shoulder).dot(chord)
                                               / max(chord.dot(chord), 1e-9))
    n_pole = (pole_head - shoulder) - chord * ((pole_head - shoulder).dot(chord)
                                               / max(chord.dot(chord), 1e-9))
    assert n_elbow.dot(n_pole) > 0, "pole not on the FK bend side"
    con = cl._ik_constraint(arm, names)
    assert con is not None
    ik_elbow = arm.pose.bones[names["mch"][1]].head.copy()
    elbow_gap = (ik_elbow - fk_elbow).length
    assert elbow_gap < 1e-3, ("IK elbow is not on the FK elbow", elbow_gap)
    print("FK->IK verified (control on FK hand, pole on bend side, elbow "
          "gap %.5f, pole_angle=%.3f)" % (elbow_gap, con.pole_angle))
    trb._clear_pose(arm)


def test_bake_range():
    arm = _build_rig()
    names = _limb(arm, "IK_FK-arm-L")
    scene = bpy.context.scene
    scene.frame_start, scene.frame_end = 1, 5
    arm.pose.bones["properties"]["IK_FK-arm-L"] = 0.0
    fk0 = arm.pose.bones[names["fk"][0]]
    fk0.rotation_mode = 'XYZ'
    scene.frame_set(1)
    fk0.rotation_euler = (0.0, 0.0, 0.0)
    fk0.keyframe_insert("rotation_euler", frame=1)
    scene.frame_set(5)
    fk0.rotation_euler = (0.0, 0.0, math.radians(50))
    fk0.keyframe_insert("rotation_euler", frame=5)

    n = cl.bake_limb(arm, names, to_ik=True, frame_start=1, frame_end=5)
    assert n == 5, ("expected 5 baked frames", n)
    fcs = [fc for fc in _action_fcurves(arm.animation_data.action)
           if names["ik"] in fc.data_path and "location" in fc.data_path]
    assert fcs, "IK control has no baked location f-curves"
    frames = sorted(int(round(kp.co[0])) for kp in fcs[0].keyframe_points)
    assert frames[0] <= 1 and frames[-1] >= 5 and len(frames) >= 5, frames
    print("bake verified (%d frames, IK keys on %d..%d)"
          % (n, frames[0], frames[-1]))


def test_foot_roll_drives_mesh():
    arm = _build_rig()
    cl.key_foot_roll(arm, "L", 1.0, frame=1)
    # the driver (rotation_euler.x = max(0, v) * 1.2) must actually rotate the
    # toe/ball bone — read the evaluated copy where drivers are applied
    deps = bpy.context.evaluated_depsgraph_get()
    deps.update()
    ev = arm.evaluated_get(deps)
    roll = ev.pose.bones["roll_ball-L"].rotation_euler.x
    assert abs(roll) > 0.5, ("foot-roll driver did not rotate the bone", roll)
    print("foot-roll behaviour verified (value drives the bone: %.2f rad)"
          % roll)


def test_global_scale_respects_locks():
    arm = _build_rig()
    root = arm.pose.bones["root"]
    assert cl.global_rig_scale(arm, 2.0) is True
    assert abs(root.scale.x - 2.0) < 1e-6, root.scale[:]
    root.scale = (1.0, 1.0, 1.0)
    root.lock_scale = (True, True, True)
    assert cl.global_rig_scale(arm, 2.0) is False
    assert abs(root.scale.x - 1.0) < 1e-6, "locked root was scaled"
    print("global scale verified (scales, and respects protected locks)")


def test_pin_and_inherit():
    arm = _build_rig()
    names = _limb(arm, "IK_FK-arm-L")
    assert cl.toggle_ik_pin(arm, names) is True
    assert all(arm.pose.bones[names["ik"]].lock_location)
    assert cl.toggle_ik_pin(arm, names) is False
    assert not any(arm.pose.bones[names["ik"]].lock_location)
    before = arm.pose.bones[names["fk"][0]].bone.use_inherit_rotation
    after = cl.toggle_limb_inherit(arm, names)
    assert after != before, "lock-free inherit did not toggle"
    print("pin + lock-free inherit verified")


def test_per_character_state_isolated():
    arm1 = _build_rig()
    arm1.name = "RIG_A"
    arm2 = _build_rig()
    arm2.name = "RIG_B"
    cl.set_control_flag(arm1, "demo", 111)
    cl.set_control_flag(arm2, "demo", 222)
    assert cl.get_control_flag(arm1, "demo") == 111
    assert cl.get_control_flag(arm2, "demo") == 222
    print("per-character state isolation verified (two rigs independent)")


def run():
    n_limbs = len(cl.discover_limbs(_build_rig()))
    assert n_limbs >= 4, ("expected >=4 IK/FK limbs", n_limbs)
    print("control layer: discovered %d IK/FK limbs" % n_limbs)
    test_blend_driver_engages()
    test_ik_to_fk_exact()
    test_fk_to_ik_endeffector()
    test_bake_range()
    test_foot_roll_drives_mesh()
    test_global_scale_respects_locks()
    test_pin_and_inherit()
    test_per_character_state_isolated()
    print("ALL CONTROL-LAYER TESTS PASS")
