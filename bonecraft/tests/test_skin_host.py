"""In-Bforartists behavioural test for production skinning fixes (P3).

A connected box humanoid whose legs almost touch, plus a separate one-sided
"robot arm" accessory mounted on the back that runs alongside the left arm.
After the Auto-Rig wizard skins it:

* no vertex of the right leg/arm carries weight from a left bone (and v.v.)
  — corrective presets pair same-side joints only, legs are side-clipped by
  bone proximity;
* the accessory is attached rigidly to a torso bone, not the arm it runs
  beside (negative control: the left forearm bone does not move it);
* the known-bad pairing is caught: ``_joint_pairs`` never pairs L with R.
"""
import math

import bpy
from mathutils import Vector

import boneforge
from boneforge.autorig.constants import BODY_MARKERS

MARKERS = {
    "HEAD_TOP": (0, 0, 1.80), "NECK_BASE": (0, 0, 1.50), "PELVIS": (0, 0, 0.95),
    "SHOULDER_LEFT": (0.20, 0, 1.45), "SHOULDER_RIGHT": (-0.20, 0, 1.45),
    "ELBOW_LEFT": (0.47, 0, 1.45), "ELBOW_RIGHT": (-0.47, 0, 1.45),
    "WRIST_LEFT": (0.72, 0, 1.45), "WRIST_RIGHT": (-0.72, 0, 1.45),
    "HIP_LEFT": (0.07, 0, 0.92), "HIP_RIGHT": (-0.07, 0, 0.92),
    "KNEE_LEFT": (0.07, 0, 0.50), "KNEE_RIGHT": (-0.07, 0, 0.50),
    "ANKLE_LEFT": (0.07, 0, 0.09), "ANKLE_RIGHT": (-0.07, 0, 0.09),
    "TOE_LEFT": (0.07, -0.14, 0.02), "TOE_RIGHT": (-0.07, -0.14, 0.02),
    "HEEL_LEFT": (0.07, 0.05, 0.0), "HEEL_RIGHT": (-0.07, 0.05, 0.0),
}
# legs 2 cm apart at their inner faces (centres +-0.07, half-width 0.06)
BODY = [((0, 0, 1.65), (0.10, 0.10, 0.14)), ((0, 0, 1.20), (0.17, 0.10, 0.27)),
        ((0.47, 0, 1.45), (0.27, 0.05, 0.05)), ((-0.47, 0, 1.45), (0.27, 0.05, 0.05)),
        ((0.80, 0, 1.45), (0.07, 0.03, 0.04)), ((-0.80, 0, 1.45), (0.07, 0.03, 0.04)),
        ((0.07, 0, 0.52), (0.06, 0.07, 0.42)), ((-0.07, 0, 0.52), (0.06, 0.07, 0.42)),
        ((0.07, -0.05, 0.04), (0.05, 0.10, 0.04)), ((-0.07, -0.05, 0.04), (0.05, 0.10, 0.04))]
# accessory: a beam from the upper back out past the left hand, 0.35 behind the arm
ACCESSORY = [((0.05, 0.22, 1.42), (0.06, 0.12, 0.06)), ((0.50, 0.35, 1.45), (0.42, 0.04, 0.04))]


def _boxes(bm, boxes):
    import bmesh
    for (c, s) in boxes:
        r = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(s[0] * 2, s[1] * 2, s[2] * 2), verts=r["verts"])
        bmesh.ops.translate(bm, vec=c, verts=r["verts"])
        bmesh.ops.subdivide_edges(bm, edges=list({e for v in r["verts"] for e in v.link_edges}),
                                  cuts=6, use_grid_fill=True)


def _mesh():
    """One fused (watertight) body skin plus a separate accessory piece."""
    import bmesh
    bm = bmesh.new()
    _boxes(bm, BODY)
    me = bpy.data.meshes.new("BF_SKIN_MESH")
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new("BF_SKIN_MESH", me)
    bpy.context.scene.collection.objects.link(ob)
    mod = ob.modifiers.new("fuse", 'REMESH')
    mod.mode, mod.voxel_size = 'VOXEL', 0.02
    fused = bpy.data.meshes.new_from_object(ob.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    ob.modifiers.remove(mod)
    bm = bmesh.new()
    bm.from_mesh(fused)
    _boxes(bm, ACCESSORY)          # separate piece(s), not fused into the body
    bm.to_mesh(fused)
    bm.free()
    ob.data = fused
    return ob


def _region(p):
    x, y, z = p
    if y > 0.25 and z > 1.3:
        return "accessory"
    if z < 0.95 and abs(x) < 0.2:
        # the crotch / midline band is legitimately shared by both legs
        if z > 0.88 or abs(x) < 0.03:
            return "mid"
        return "leg.L" if x > 0 else "leg.R"
    if z > 1.3 and abs(x) > 0.3:
        return "arm.L" if x > 0 else "arm.R"
    return "body"


def run():
    try:
        boneforge.register()
    except Exception as exc:
        print("register note:", exc)
    from boneforge.autorig.session import recalculate_derived_joints
    from boneforge.autorig import wizard, skin_gen

    mesh = _mesh()
    bpy.context.view_layer.objects.active = mesh
    mesh.select_set(True)
    bpy.ops.boneforge.autorig_wizard_start()
    s = bpy.context.scene.boneforge_autorig_session
    s.mesh_object_name = mesh.name
    for i, name in enumerate(BODY_MARKERS):
        if name in MARKERS:
            m = s.body_markers[i]
            m.position, m.confidence, m.confirmed = MARKERS[name], 1.0, True
    recalculate_derived_joints(s, bpy.context)
    s.rig_type, s.finger_count, s.wizard_step = "BODY_ONLY", 0, wizard.STEP_REVIEW
    assert bpy.ops.boneforge.autorig_generate() == {'FINISHED'}
    arm = next(m.object for m in mesh.modifiers if m.type == 'ARMATURE' and m.object)

    # 0) the quality score is honest in both directions: a clean mesh bound by
    # surface diffusion scores high, and no method scores above its ceiling
    ceiling = {"AUTO": 1.0, "SEGMENT": 0.8, "ENVELOPE": 0.7, "FALLBACK": 0.5}
    method, score = s.skinning_method, float(s.skinning_quality_score)
    assert method in ceiling and score <= ceiling[method] + 1e-6, (method, score)
    if method == "AUTO":
        assert score >= 0.8, ("clean watertight bind scored low", score)

    # 1) joint pairing never crosses sides
    pairs = skin_gen._joint_pairs(arm, ['forearm.L', 'forearm.R', 'upper_arm.L', 'upper_arm.R'])
    assert pairs and all(skin_gen._bone_side(a) == skin_gen._bone_side(b) for a, b in pairs), pairs

    # 2) no cross-side weights on legs / arms
    gid = {g.index: g.name for g in mesh.vertex_groups}
    cross = 0
    where = []
    acc_bones = {}
    for v in mesh.data.vertices:
        reg = _region(mesh.matrix_world @ v.co)
        for ge in v.groups:
            if ge.weight <= 0.01:
                continue
            side = skin_gen._bone_side(gid[ge.group])
            if reg.endswith(".L") and side == "R" or reg.endswith(".R") and side == "L":
                cross += 1
                where.append(tuple(round(c, 3) for c in mesh.matrix_world @ v.co))
            if reg == "accessory":
                acc_bones[gid[ge.group]] = acc_bones.get(gid[ge.group], 0) + 1
    assert cross == 0, ("cross-side weights", cross, where[:12])

    # 3) the accessory follows the torso, not the arm it runs beside
    assert acc_bones, "accessory has no weights"
    assert all(not skin_gen._bone_side(b) for b in acc_bones), ("accessory on a limb", acc_bones)
    idx = [v.index for v in mesh.data.vertices if _region(mesh.matrix_world @ v.co) == "accessory"]

    def centre():
        ev = mesh.evaluated_get(bpy.context.evaluated_depsgraph_get()).data.vertices
        c = Vector()
        for i in idx:
            c += mesh.matrix_world @ ev[i].co
        return c / len(idx)

    c0 = centre()
    pb = arm.pose.bones["forearm.L"]
    pb.rotation_mode = 'XYZ'
    pb.rotation_euler = (0, 0, math.radians(80))
    for b in arm.pose.bones:
        for con in b.constraints:
            if con.type == 'IK':
                con.influence = 0.0
    bpy.context.view_layer.update()
    moved = (centre() - c0).length
    pb.rotation_euler = (0, 0, 0)
    assert moved < 0.002, ("bending the left forearm moved the back accessory", moved)
    print("skinning verified (%s score %.2f, 0 cross-side weights, accessory on %s, "
          "forearm bend moves it %.4f)" % (method, score, sorted(acc_bones), moved))
    bpy.data.objects.remove(mesh, do_unlink=True)
    bpy.data.objects.remove(arm, do_unlink=True)
    print("ALL SKINNING TESTS PASS")


if __name__ == "__main__":
    run()
