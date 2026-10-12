"""In-Bforartists behavioural test: face controls on a wizard-style face.

A synthetic head facing -Y with two separate eyeballs behind eye openings in
the skin, a jaw mass, and a rig carrying the wizard's face bones. After
``add_face_controls``:
- moving an eye target 5 cm sideways turns the eyeball (pupil >= 3 mm) and
  leaves the crown still;
- blinking (shape keys) closes the upper lid over >= 60% of the opening,
  eyeball still, and no face around the eye folds over;
- a mouth corner follows the opening jaw by 0.1-0.5 of the lower lip;
- a second call changes nothing; a rig without eyeball meshes is refused with
  a reason (negative control).
"""
import math

import bmesh
import bpy
from mathutils import Matrix, Vector

from boneforge.autorig import face_controls

EYES = {"L": Vector((0.032, -0.080, 1.62)), "R": Vector((-0.032, -0.080, 1.62))}
EYE_R = 0.012


def _head(with_eyes=True):
    bm = bmesh.new()

    def sphere(centre, radius, segs=32):
        r = bmesh.ops.create_uvsphere(bm, u_segments=segs, v_segments=segs // 2, radius=radius)
        bmesh.ops.translate(bm, vec=centre, verts=r["verts"])
        return r["verts"]
    skull = sphere(Vector((0, 0, 1.60)), 0.10, 128)
    # open the skin in front of each eye (the eye opening)
    cut = [v for v in skull for c in EYES.values()
           if (v.co - c).length < 0.03 and v.co.y < c.y and abs(v.co.z - c.z) < 0.006]
    bmesh.ops.delete(bm, geom=list(set(cut)), context='VERTS')
    sphere(Vector((0, -0.055, 1.50)), 0.045)                 # jaw / chin mass
    if with_eyes:
        for c in EYES.values():
            sphere(c, EYE_R, 16)
    me = bpy.data.meshes.new("BF_FACE")
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new("BF_FACE", me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


BONES = {  # name: (head, tail, parent, deform)
    "head": ((0, 0, 1.45), (0, 0, 1.75), None, True),
    "face_root": ((0, -0.03, 1.49), (0, -0.03, 1.46), "head", True),
    "eye.L": ((0.032, -0.092, 1.62), (0.032, -0.10, 1.62), "face_root", True),
    "eye.R": ((-0.032, -0.092, 1.62), (-0.032, -0.10, 1.62), "face_root", True),
    "nose_tip": ((0, -0.11, 1.58), (0, -0.118, 1.58), "face_root", True),
    "jaw.L": ((0.05, -0.03, 1.49), (0.056, -0.03, 1.49), "face_root", True),
    "jaw.R": ((-0.05, -0.03, 1.49), (-0.056, -0.03, 1.49), "face_root", True),
    "jaw_root": ((0, -0.03, 1.49), (0, -0.03, 1.46), "face_root", True),
    "lip_upper": ((0, -0.092, 1.535), (0, -0.10, 1.535), "face_root", True),
    "lip_lower": ((0, -0.092, 1.52), (0, -0.10, 1.52), "jaw_root", True),
    "chin": ((0, -0.095, 1.49), (0, -0.103, 1.49), "jaw_root", True),
}


def _rig(mesh):
    arm = bpy.data.objects.new("BF_FACE_RIG", bpy.data.armatures.new("BF_FACE_RIG"))
    bpy.context.scene.collection.objects.link(arm)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode='EDIT')
    for name, (h, t, p, d) in BONES.items():
        eb = arm.data.edit_bones.new(name)
        eb.head, eb.tail, eb.use_deform = h, t, d
        if p:
            eb.parent = arm.data.edit_bones[p]
    bpy.ops.object.mode_set(mode='OBJECT')
    groups = {n: mesh.vertex_groups.new(name=n) for n in ("head", "jaw_root", "eye.L", "eye.R")}
    for v in mesh.data.vertices:
        eye = next((s for s, c in EYES.items() if (v.co - c).length < EYE_R * 1.01), None)
        if eye:
            groups["eye." + eye].add([v.index], 1.0, 'REPLACE')
        else:
            # skin blends from the head to the jaw across the mouth line
            j = face_controls.smoothstep(1.535, 1.52, v.co.z) if v.co.y < -0.02 else 0.0
            if j > 0.0:
                groups["jaw_root"].add([v.index], j, 'REPLACE')
            if j < 1.0:
                groups["head"].add([v.index], 1.0 - j, 'REPLACE')
    mod = mesh.modifiers.new("Armature", 'ARMATURE')
    mod.object = arm
    return arm


def _centre(mesh, idx):
    ev = mesh.evaluated_get(bpy.context.evaluated_depsgraph_get()).data.vertices
    return sum((mesh.matrix_world @ ev[i].co for i in idx), Vector()) / max(len(idx), 1)


def _upd(arm):
    arm.update_tag()
    bpy.context.view_layer.update()


def run():
    mesh = _head()
    arm = _rig(mesh)
    info = face_controls.add_face_controls(arm, bpy.context)
    for n in ("eye_master", "eye.ik.L", "lip.corner.L", "face_props"):
        assert n in arm.data.bones, (n, info)
    # lids are blink shape keys (bones blended linearly cut through the eye)
    keys = mesh.data.shape_keys.key_blocks if mesh.data.shape_keys else {}
    for k in ("BF_blink.L", "BF_blink_half.L", "BF_blink.R", "BF_blink_half.R"):
        assert k in keys, (k, info)
    assert "lid.upper.L" not in arm.data.bones
    assert (arm.data.bones["eye.L"].head_local - EYES["L"]).length < 0.002, "eye bone not at eyeball centre"
    pbs = arm.pose.bones
    V = mesh.data.vertices
    eyeball = [v.index for v in V if (v.co - EYES["L"]).length < EYE_R * 1.01]
    pupil = [i for i in eyeball if V[i].co.y < EYES["L"].y - 0.8 * EYE_R]
    crown = [v.index for v in V if v.co.z > 1.69]

    # eye aim
    p0, c0 = _centre(mesh, pupil), _centre(mesh, crown)
    t = pbs["eye.ik.L"]
    t.location = t.bone.matrix_local.inverted().to_3x3() @ Vector((0.05, 0, 0))
    _upd(arm)
    aim = (_centre(mesh, pupil) - p0).length
    crown_aim = (_centre(mesh, crown) - c0).length
    assert aim >= 0.003 and crown_aim <= 0.0005, ("eye aim", aim, crown_aim)
    t.location = (0, 0, 0)
    _upd(arm)

    # blink: upper rim (skin edge above the eye opening, on the eye's axis)
    c = EYES["L"]

    def ang(p):
        d = p - c
        return math.atan2(d.z, -d.y)
    ev = mesh.evaluated_get(bpy.context.evaluated_depsgraph_get()).data.vertices
    skin = [v.index for v in V if v.index not in eyeball and (v.co - c).length < 2 * EYE_R
            and v.co.y < c.y and abs(v.co.x - c.x) < 0.004]
    rim_u = min((i for i in skin if V[i].co.z > c.z), key=lambda i: ang(V[i].co))
    rim_l = max((i for i in skin if V[i].co.z < c.z), key=lambda i: ang(V[i].co))
    a_u, a_l = ang(V[rim_u].co), ang(V[rim_l].co)
    e0 = _centre(mesh, eyeball)
    pbs["face_props"]["blink.L"] = 1.0
    _upd(arm)
    ev = mesh.evaluated_get(bpy.context.evaluated_depsgraph_get()).data.vertices
    closed = (a_u - ang(mesh.matrix_world @ ev[rim_u].co)) / (a_u - a_l)
    eye_still = (_centre(mesh, eyeball) - e0).length
    assert closed >= 0.6 and eye_still <= 0.0005, ("blink", closed, eye_still)
    # no fold-over: faces around the eye keep facing the same way mid-blink
    ring = {v.index for v in V if v.index not in set(eyeball) and (v.co - c).length < 2 * EYE_R}
    polys = [pl.index for pl in mesh.data.polygons if all(i in ring for i in pl.vertices)]

    def normals():
        me = mesh.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh()
        out = {i: me.polygons[i].normal.copy() for i in polys}
        mesh.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh_clear()
        return out
    pbs["face_props"]["blink.L"] = 0.0
    _upd(arm)
    n0 = normals()
    for b in (0.5, 1.0):
        pbs["face_props"]["blink.L"] = b
        _upd(arm)
        n1 = normals()
        folded = sum(1 for i in polys if n0[i].dot(n1[i]) < 0.0)
        assert folded == 0, ("lid folds at blink", b, folded, len(polys))
    pbs["face_props"]["blink.L"] = 0.0
    _upd(arm)

    # lip follow
    corner_p = arm.data.bones["lip.corner.L"].head_local
    # the vertices the corner control fully owns (inside 0.35 of its reach)
    corner = [v.index for v in V if (v.co - corner_p).length < 0.004]
    lower = [v.index for v in V if (v.co - Vector(BONES["lip_lower"][0])).length < 0.01]
    jaw = pbs["jaw_root"]
    jaw.rotation_mode = 'XYZ'
    cc, cl = _centre(mesh, corner), _centre(mesh, lower)
    jaw.rotation_euler = (math.radians(20), 0, 0)
    _upd(arm)
    follow = (_centre(mesh, corner) - cc).length
    ratio = follow / max((_centre(mesh, lower) - cl).length, 1e-9)
    assert 0.1 <= ratio <= 0.5, ("lip follow", ratio, len(corner), len(lower))
    # the jaw-open corrective exists and is driven by the jaw
    keys = mesh.data.shape_keys
    jk = keys.key_blocks.get("BF_jaw_open") if keys else None
    assert jk is not None, "no jaw-open corrective key"
    fc = keys.animation_data.drivers.find('key_blocks["BF_jaw_open"].value')
    assert fc is not None and fc.driver.variables[0].targets[0].bone_target == "jaw_root"
    assert keys.key_blocks.get("BF_jaw_open_sticky") is not None, "no sticky-lips jaw key"
    # sticky lips hold the corners
    pbs["face_props"]["sticky_lips"] = 1.0
    _upd(arm)
    sticky = (_centre(mesh, corner) - cc).length
    assert sticky < 0.25 * follow, ("sticky", sticky, follow)
    jaw.rotation_euler = (0, 0, 0)
    pbs["face_props"]["sticky_lips"] = 0.0
    _upd(arm)

    # idempotent
    n_bones = len(arm.data.bones)
    again = face_controls.add_face_controls(arm, bpy.context)
    assert not again["built"] and len(arm.data.bones) == n_bones, again

    # negative control: no eyeball meshes -> refused with a reason
    bare = _head(with_eyes=False)
    arm2 = _rig(bare)
    res = face_controls.add_face_controls(arm2, bpy.context)
    assert not res["built"] and any("eyeball" in s for s in res["skipped"]), res
    for ob in (mesh, arm, bare, arm2):
        bpy.data.objects.remove(ob, do_unlink=True)
    print("face controls verified (eye aim %.1f mm, crown %.2f mm; blink closes %d%%, eyeball %.2f mm; "
          "lip follow %.2f, sticky holds; idempotent; no-eyeball refused)"
          % (aim * 1000, crown_aim * 1000, closed * 100, eye_still * 1000, ratio))
    print("ALL FACE-CONTROL TESTS PASS")


if __name__ == "__main__":
    run()
