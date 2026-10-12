"""In-Bforartists behavioural test: skirt bones follow the legs.

A synthetic lower body: two leg tubes (thighs + shins) and a cone skirt
around them, weighted like a real bind (skirt -> hips, legs -> thighs /
shins). After ``add_skirt_bones``:
- a ring of skirt bones exists, and the rest pose does not move;
- lifting the right thigh 60 deg forward swings the front-right of the hem
  forward (with the leg) while the back of the skirt stays put;
- negative control: trousers (legs only, no skirt) get no skirt bones.
"""
import math

import bmesh
import bpy
from mathutils import Matrix, Vector

from boneforge.autorig import skirt_rig

HIP_Z, KNEE_Z, ANKLE_Z = 1.0, 0.55, 0.1
LEG_X = 0.1


def _tube(bm, x, z0, z1, r):
    res = bmesh.ops.create_cone(bm, cap_ends=False, segments=16, radius1=r, radius2=r, depth=z0 - z1)
    bmesh.ops.translate(bm, vec=(x, 0, (z0 + z1) / 2), verts=res["verts"])
    return res["verts"]


def _scene(with_skirt=True):
    bm = bmesh.new()
    for x in (LEG_X, -LEG_X):
        _tube(bm, x, HIP_Z, ANKLE_Z, 0.05)
        for v in bm.verts:
            pass
    if with_skirt:
        res = bmesh.ops.create_cone(bm, cap_ends=False, segments=32, radius1=0.35, radius2=0.2, depth=0.45)
        bmesh.ops.translate(bm, vec=(0, 0, HIP_Z - 0.225 + 0.05), verts=res["verts"])
        bmesh.ops.subdivide_edges(bm, edges=[e for e in bm.edges if all(v in res["verts"] for v in e.verts)
                                             and abs(e.verts[0].co.z - e.verts[1].co.z) > 1e-4],
                                  cuts=5, use_grid_fill=False)
    me = bpy.data.meshes.new("BF_SKIRT")
    bm.to_mesh(me)
    bm.free()
    mesh = bpy.data.objects.new("BF_SKIRT", me)
    bpy.context.scene.collection.objects.link(mesh)
    arm = bpy.data.objects.new("BF_SKIRT_RIG", bpy.data.armatures.new("BF_SKIRT_RIG"))
    bpy.context.scene.collection.objects.link(arm)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode='EDIT')
    ebs = arm.data.edit_bones
    hips = ebs.new("hips"); hips.head, hips.tail = (0, 0, HIP_Z), (0, 0, HIP_Z + 0.15)
    for side, x in (("L", LEG_X), ("R", -LEG_X)):
        th = ebs.new("thigh.def-" + side); th.head, th.tail = (x, 0, HIP_Z), (x, -0.02, KNEE_Z)
        th.parent = hips
        sh = ebs.new("shin.def-" + side); sh.head, sh.tail = (x, -0.02, KNEE_Z), (x, 0, ANKLE_Z)
        sh.parent, sh.use_connect = th, True
    bpy.ops.object.mode_set(mode='OBJECT')
    groups = {n: mesh.vertex_groups.new(name=n) for n in
              ("hips", "thigh.def-L", "thigh.def-R", "shin.def-L", "shin.def-R")}
    for v in mesh.data.vertices:
        r_leg = min(math.hypot(v.co.x - x, v.co.y) for x in (LEG_X, -LEG_X))
        if r_leg < 0.06:
            side = "L" if v.co.x > 0 else "R"
            groups[("thigh.def-" if v.co.z > KNEE_Z else "shin.def-") + side].add([v.index], 1.0, 'REPLACE')
        else:
            groups["hips"].add([v.index], 1.0, 'REPLACE')
    mod = mesh.modifiers.new("Armature", 'ARMATURE')
    mod.object = arm
    return mesh, arm


def _positions(mesh):
    ev = mesh.evaluated_get(bpy.context.evaluated_depsgraph_get()).data.vertices
    return [mesh.matrix_world @ v.co for v in ev]


def run():
    mesh, arm = _scene()
    rest = _positions(mesh)
    info = skirt_rig.add_skirt_bones(arm, bpy.context)
    skirt = [b for b in info["built"] if b.startswith("skirt.")]
    assert len(skirt) >= 6, info
    bpy.context.view_layer.update()
    shift = max((a - b).length for a, b in zip(rest, _positions(mesh)))
    assert shift < 1e-4, ("skirt bones moved the rest pose", shift)
    V = mesh.data.vertices
    hem = [v.index for v in V if math.hypot(v.co.x, v.co.y) > 0.15 and v.co.z < HIP_Z - 0.3]
    front_right = [i for i in hem if V[i].co.y < -0.1 and V[i].co.x < 0]
    back = [i for i in hem if V[i].co.y > 0.15]
    assert front_right and back, (len(front_right), len(back))
    th = arm.pose.bones["thigh.def-R"]
    th.rotation_mode = 'XYZ'
    best = None
    for sgn in (1, -1):
        th.rotation_euler = (sgn * math.radians(60), 0, 0)
        bpy.context.view_layer.update()
        y = (arm.matrix_world @ th.tail).y
        if best is None or y < best[0]:
            best = (y, sgn)
    th.rotation_euler = (best[1] * math.radians(60), 0, 0)
    bpy.context.view_layer.update()
    now = _positions(mesh)
    fwd = sum(rest[i].y - now[i].y for i in front_right) / len(front_right)
    back_move = sum((now[i] - rest[i]).length for i in back) / len(back)
    assert fwd > 0.05, ("front-right hem did not swing forward with the leg", fwd)
    assert back_move < 0.3 * fwd, ("back of the skirt moved with the leg", back_move, fwd)
    for ob in (mesh, arm):
        bpy.data.objects.remove(ob, do_unlink=True)

    # negative control: trousers only
    mesh, arm = _scene(with_skirt=False)
    res = skirt_rig.add_skirt_bones(arm, bpy.context)
    assert not res["built"] and any("no skirt" in s for s in res["skipped"]), res
    for ob in (mesh, arm):
        bpy.data.objects.remove(ob, do_unlink=True)
    print("skirt verified (%d skirt bones, rest shift %.1e m; leg lift 60 deg: front hem %.0f mm "
          "forward, back %.0f mm; trousers skipped)" % (len(skirt), shift, fwd * 1000, back_move * 1000))
    print("ALL SKIRT TESTS PASS")


if __name__ == "__main__":
    run()
