"""In-Bforartists behavioural test for the control-rig engine.

Requires a real Bforartists host (bpy). Builds a rig on a fresh armature
and asserts the constraint/driver/collection network the engine promised
actually exists on the live armature — the behavioural counterpart to the
pure plan test (tests/test_build_plan.py).

R0 baseline coverage (all exercised against real bpy):
  * the IK/FK + pole + driver + foot-roll network exists on the live rig;
  * re-running the build is idempotent (no duplicated bones/constraints/drivers);
  * a skinned deform mesh actually moves under an FK pose and under an IK solve.
"""
import math

import bpy
from mathutils import Matrix

from boneforge.autorig.rig_build import RigSpec, compute_build_plan, build_control_rig


def _fresh_armature():
    # Ensure a clean OBJECT-mode context (a prior test may have left a
    # different object active in POSE/EDIT mode).
    if bpy.context.object is not None and bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.armature_add(enter_editmode=False)
    arm = bpy.context.active_object
    arm.name = "BF_TEST_RIG"
    # remove the default bone so the engine starts clean
    bpy.ops.object.mode_set(mode='EDIT')
    for eb in list(arm.data.edit_bones):
        arm.data.edit_bones.remove(eb)
    bpy.ops.object.mode_set(mode='OBJECT')
    return arm


def _counts(arm):
    return (
        len(arm.pose.bones),
        sum(len(pb.constraints) for pb in arm.pose.bones),
        len(arm.animation_data.drivers) if arm.animation_data else 0,
    )


# -- network -----------------------------------------------------------

def _check_network(arm, plan):
    """Golden-rig regression: the live counts must EQUAL the plan's, not just
    clear a floor — so a regression that drops constraints/drivers is caught."""
    n_bones, n_constraints, n_drivers = _counts(arm)
    counts = plan.counts()
    print("live rig: bones=%d constraints=%d drivers=%d (plan: %d/%d/%d)"
          % (n_bones, n_constraints, n_drivers,
             counts["bones"], counts["constraints"], counts["drivers"]))

    assert n_bones == counts["bones"], ("bone count drift", n_bones, counts["bones"])
    assert n_constraints == counts["constraints"], \
        ("constraint count drift", n_constraints, counts["constraints"])
    assert n_drivers == counts["drivers"], \
        ("driver count drift", n_drivers, counts["drivers"])
    ik = [c for pb in arm.pose.bones for c in pb.constraints if c.type == 'IK']
    assert len(ik) == 4, ("expect 4 IK constraints", len(ik))
    live_colls = {c.name for c in arm.data.collections}
    plan_colls = {c.name for c in plan.collections}
    # the engine must create exactly the planned collections; the only allowed
    # extra is the host's default "Bones" collection from armature_add.
    assert plan_colls <= live_colls, ("missing collections", plan_colls - live_colls)
    assert live_colls - plan_colls <= {"Bones"}, \
        ("unexpected extra collections", live_colls - plan_colls)
    print("in-host golden-rig verified (exact bone/constraint/driver counts "
          "match the plan; collections = plan + host default)")


def _check_foot_roll(arm):
    """The driven foot-roll network (the path that surfaced the apply bug)."""
    for side in ("L", "R"):
        for which in ("heel", "ball"):
            pb = arm.pose.bones.get("roll_%s-%s" % (which, side))
            assert pb is not None, ("missing foot-roll bone", which, side)
            lim = [c for c in pb.constraints if c.type == 'LIMIT_ROTATION']
            assert lim, ("foot-roll bone has no LIMIT_ROTATION", which, side)
    # one rotation driver per heel/ball bone (4 total)
    roll_drivers = [d for d in arm.animation_data.drivers
                    if "roll_" in d.data_path]
    assert len(roll_drivers) >= 4, ("expect >=4 foot-roll drivers",
                                    len(roll_drivers))
    print("foot-roll network verified (limits + rotation drivers, both sides)")


# -- idempotency -------------------------------------------------------

def _check_idempotent(arm, spec):
    before = _counts(arm)
    build_control_rig(arm, spec)            # rebuild on the same armature
    after = _counts(arm)
    assert before == after, ("re-run not idempotent", before, after)
    print("idempotent re-run verified (counts stable: %r)" % (after,))


# -- deform ------------------------------------------------------------

_DEF_TAILS = {
    "upperarm.def-L": (0.45, 0.0, 1.45),
    "forearm.def-L": (0.70, 0.0, 1.45),
    "hand.def-L": (0.85, 0.0, 1.45),
    "thigh.def-L": (0.11, 0.0, 0.52),
    "shin.def-L": (0.12, 0.0, 0.10),
    "foot.def-L": (0.12, 0.18, 0.03),
}


def _skinned_mesh(arm):
    """One vertex per left-side deform bone, each weighted 1.0 to its bone."""
    names = list(_DEF_TAILS)
    mesh = bpy.data.meshes.new("BF_TEST_SKIN")
    mesh.from_pydata([_DEF_TAILS[n] for n in names], [], [])
    mesh.update()
    obj = bpy.data.objects.new("BF_TEST_SKIN", mesh)
    bpy.context.scene.collection.objects.link(obj)
    for i, n in enumerate(names):
        vg = obj.vertex_groups.new(name=n)
        vg.add([i], 1.0, 'REPLACE')
    mod = obj.modifiers.new("Armature", 'ARMATURE')
    mod.object = arm
    return obj


def _eval_world_coords(obj):
    deps = bpy.context.evaluated_depsgraph_get()
    deps.update()
    obj_eval = obj.evaluated_get(deps)
    me = obj_eval.to_mesh()
    coords = [obj_eval.matrix_world @ v.co for v in me.vertices]
    obj_eval.to_mesh_clear()
    return coords


def _max_disp(a, b):
    return max((va - vb).length for va, vb in zip(a, b))


def _clear_pose(arm):
    for pb in arm.pose.bones:
        pb.matrix_basis = Matrix()
    for side in ("L", "R"):
        for kind in ("arm", "leg"):
            key = "IK_FK-%s-%s" % (kind, side)
            if key in arm.pose.bones["properties"]:
                arm.pose.bones["properties"][key] = 0.0
    # update_tag so the IK/FK blend drivers re-evaluate the reset property
    arm.update_tag()
    bpy.context.view_layer.update()


def _check_deform(arm):
    obj = _skinned_mesh(arm)
    bpy.context.view_layer.update()
    rest = _eval_world_coords(obj)

    # --- FK pose: pure FK (blend = 0), rotate FK upper bones ---
    _clear_pose(arm)
    for name in ("upperarm.fk-L", "thigh.fk-L"):
        pb = arm.pose.bones[name]
        pb.rotation_mode = 'XYZ'
        pb.rotation_euler = (0.0, 0.0, math.radians(45))
    bpy.context.view_layer.update()
    fk_disp = _max_disp(rest, _eval_world_coords(obj))
    assert fk_disp > 0.01, ("FK pose did not deform mesh", fk_disp)
    print("FK deform verified (max vertex displacement = %.3f)" % fk_disp)

    # --- IK solve: blend = 1, translate the IK foot/hand targets ---
    _clear_pose(arm)
    arm.pose.bones["properties"]["IK_FK-arm-L"] = 1.0
    arm.pose.bones["properties"]["IK_FK-leg-L"] = 1.0
    for name in ("forearm.ik-L", "shin.ik-L"):
        pb = arm.pose.bones[name]
        pb.location = (0.0, 0.0, 0.30)      # along the control's local axis
    arm.update_tag()                        # engage the IK/FK blend drivers
    bpy.context.view_layer.update()
    ik_disp = _max_disp(rest, _eval_world_coords(obj))
    assert ik_disp > 0.01, ("IK solve did not deform mesh", ik_disp)
    print("IK deform verified (max vertex displacement = %.3f)" % ik_disp)

    _clear_pose(arm)


def run():
    spec = RigSpec()
    plan = compute_build_plan(spec)
    arm = _fresh_armature()
    build_control_rig(arm, spec)

    _check_network(arm, plan)
    _check_foot_roll(arm)
    _check_idempotent(arm, spec)
    _check_deform(arm)
