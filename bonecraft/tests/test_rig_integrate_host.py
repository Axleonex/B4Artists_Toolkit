"""In-Bforartists behavioural test: the control rig drives the skinned mesh.

Builds a box humanoid, runs the Auto-Rig wizard (skeleton + production
skinning) from known markers, then builds the control rig on top and checks:

* the rest pose is unchanged by the bind (no mesh shift),
* exactly one deform skeleton remains (no ``WIZ-`` leftovers, every weighted
  group is a deform bone),
* FK and IK controls move their mesh region, and the opposite side does not,
* FK controls do nothing while a limb is in IK mode (blend really switches),
* spine and head controls move the head.
"""
import math

import bpy
from mathutils import Vector

import boneforge
from boneforge.autorig.constants import BODY_MARKERS
from boneforge.autorig.rig_build import build_control_rig

H = 1.8

MARKERS = {
    "HEAD_TOP": (0, 0, 1.80), "NECK_BASE": (0, 0, 1.50), "PELVIS": (0, 0, 0.95),
    "SHOULDER_LEFT": (0.20, 0, 1.45), "SHOULDER_RIGHT": (-0.20, 0, 1.45),
    "ELBOW_LEFT": (0.47, 0, 1.45), "ELBOW_RIGHT": (-0.47, 0, 1.45),
    "WRIST_LEFT": (0.72, 0, 1.45), "WRIST_RIGHT": (-0.72, 0, 1.45),
    "HIP_LEFT": (0.11, 0, 0.92), "HIP_RIGHT": (-0.11, 0, 0.92),
    "KNEE_LEFT": (0.11, 0, 0.50), "KNEE_RIGHT": (-0.11, 0, 0.50),
    "ANKLE_LEFT": (0.11, 0, 0.09), "ANKLE_RIGHT": (-0.11, 0, 0.09),
    "TOE_LEFT": (0.11, -0.14, 0.02), "TOE_RIGHT": (-0.11, -0.14, 0.02),
    "HEEL_LEFT": (0.11, 0.05, 0.0), "HEEL_RIGHT": (-0.11, 0.05, 0.0),
}

# (centre, half-size, region label)
BOXES = [
    ((0, 0, 1.65), (0.10, 0.10, 0.14), "head"),
    ((0, 0, 1.20), (0.17, 0.10, 0.27), "torso"),
    ((0.47, 0, 1.45), (0.27, 0.05, 0.05), "arm.L"),
    ((0.80, 0, 1.45), (0.07, 0.03, 0.04), "hand.L"),
    ((-0.47, 0, 1.45), (0.27, 0.05, 0.05), "arm.R"),
    ((-0.80, 0, 1.45), (0.07, 0.03, 0.04), "hand.R"),
    ((0.11, 0, 0.52), (0.07, 0.07, 0.40), "leg.L"),
    ((0.11, -0.05, 0.04), (0.06, 0.10, 0.04), "foot.L"),
    ((-0.11, 0, 0.52), (0.07, 0.07, 0.40), "leg.R"),
    ((-0.11, -0.05, 0.04), (0.06, 0.10, 0.04), "foot.R"),
]


def _box_humanoid():
    """One connected, watertight humanoid: boxes fused by a voxel remesh.

    (Separate boxes would each be a "small island" that production skinning
    pins whole to one bone — a skinning concern, not this test's.)
    """
    import bmesh
    bm = bmesh.new()
    for (c, s, _lab) in BOXES:
        res = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(s[0] * 2, s[1] * 2, s[2] * 2), verts=res["verts"])
        bmesh.ops.translate(bm, vec=c, verts=res["verts"])
    me = bpy.data.meshes.new("BF_INT_MESH")
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new("BF_INT_MESH", me)
    bpy.context.scene.collection.objects.link(ob)
    mod = ob.modifiers.new("fuse", 'REMESH')
    mod.mode = 'VOXEL'
    mod.voxel_size = 0.02
    # bake the modifier from the evaluated mesh (operator-free, works headless)
    fused = bpy.data.meshes.new_from_object(
        ob.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    ob.modifiers.remove(mod)
    ob.data = fused
    assert len(fused.vertices) > 2000, ("voxel fuse failed", len(fused.vertices))
    labels = []
    for v in ob.data.vertices:
        best, bd = None, None
        for (c, s, lab) in BOXES:
            d = max(abs(v.co[i] - c[i]) - s[i] for i in range(3))
            if bd is None or d < bd:
                best, bd = lab, d
        labels.append(best)
    return ob, labels


def _refresh():
    """Re-evaluate drivers too (a plain view-layer update may not, headless)."""
    scene = bpy.context.scene
    scene.frame_set(scene.frame_current)
    bpy.context.view_layer.update()


def _centre(mesh, idx):
    _refresh()
    dg = bpy.context.evaluated_depsgraph_get()
    ev = mesh.evaluated_get(dg).data.vertices
    c = Vector()
    for i in idx:
        c += mesh.matrix_world @ ev[i].co
    return c / len(idx)


def _moved(mesh, idx, before):
    return (_centre(mesh, idx) - before).length


def build_skinned_rig():
    """Box humanoid run through the wizard (skeleton + production skinning).

    Returns ``(mesh, labels, armature)``; shared with other in-host tests.
    """
    try:
        boneforge.register()
    except Exception as exc:  # already registered by an earlier suite
        print("register note:", exc)
    from boneforge.autorig.session import recalculate_derived_joints
    from boneforge.autorig import wizard

    mesh, labels = _box_humanoid()
    bpy.context.view_layer.objects.active = mesh
    mesh.select_set(True)
    bpy.ops.boneforge.autorig_wizard_start()
    s = bpy.context.scene.boneforge_autorig_session
    s.mesh_object_name = mesh.name
    for i, name in enumerate(BODY_MARKERS):
        if name in MARKERS:
            m = s.body_markers[i]
            m.position = MARKERS[name]
            m.confidence = 1.0
            m.confirmed = True
    recalculate_derived_joints(s, bpy.context)
    s.rig_type = "BODY_ONLY"
    s.finger_count = 0
    s.wizard_step = wizard.STEP_REVIEW
    assert bpy.ops.boneforge.autorig_generate() == {'FINISHED'}, "wizard generate failed"
    # the rig this mesh is skinned to (an earlier suite may have left another
    # "BoneForge_Rig" behind, so the new one can be "BoneForge_Rig.001")
    arm = next(m.object for m in mesh.modifiers if m.type == 'ARMATURE' and m.object)
    return mesh, labels, arm


def run():
    mesh, labels, arm = build_skinned_rig()
    region = {lab: [i for i, l in enumerate(labels) if l == lab] for lab in set(labels)}

    rest = [mesh.matrix_world @ v.co for v in
            mesh.evaluated_get(bpy.context.evaluated_depsgraph_get()).data.vertices]
    build_control_rig(arm, context=bpy.context)
    bpy.context.view_layer.update()

    # 1) bind did not move the mesh
    now = [mesh.matrix_world @ v.co for v in
           mesh.evaluated_get(bpy.context.evaluated_depsgraph_get()).data.vertices]
    shift = max((a - b).length for a, b in zip(rest, now))
    assert shift < 1e-4, ("rest pose shifted by the bind", shift)

    # 2) one deform skeleton
    names = {b.name for b in arm.data.bones}
    assert not [n for n in names if n.startswith("WIZ-")], "wizard bones left behind"
    deform = {b.name for b in arm.data.bones if b.use_deform}
    gid = {g.index: g.name for g in mesh.vertex_groups}
    weighted = {gid[ge.group] for v in mesh.data.vertices for ge in v.groups if ge.weight > 0}
    assert weighted <= deform, ("weights on non-deform bones", weighted - deform)
    for need in ("upperarm.def-L", "forearm.def-L", "hand.def-L", "thigh.def-R",
                 "shin.def-R", "foot.def-R", "hips", "chest", "head"):
        assert need in weighted, ("engine deform bone carries no weight", need)
    print("bind verified (rest shift %.2e, %d deform bones, %d weighted, no leftovers)"
          % (shift, len(deform), len(weighted)))

    pb = arm.pose.bones

    class _Props:
        """Set IK/FK blend props the way the UI does (tagging the rig), since
        a bare Python ID-property write does not trigger re-evaluation."""
        def __setitem__(self, key, value):
            pb["properties"][key] = value
            arm.update_tag()

    props = _Props()
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode='POSE')

    def rot(bone, deg, axis=2):
        b = pb[bone]
        b.rotation_mode = 'XYZ'
        e = [0.0, 0.0, 0.0]
        e[axis] = math.radians(deg)
        b.rotation_euler = e
        bpy.context.view_layer.update()

    def reset():
        for b in pb:
            b.rotation_euler = (0, 0, 0)
            b.location = (0, 0, 0)
        bpy.context.view_layer.update()

    # 3) FK arm moves the left hand, not the right
    props["IK_FK-arm-L"] = 0.0
    hl, hr = _centre(mesh, region["hand.L"]), _centre(mesh, region["hand.R"])
    rot("upperarm.fk-L", 60)
    fk_l, fk_r = _moved(mesh, region["hand.L"], hl), _moved(mesh, region["hand.R"], hr)
    reset()
    assert fk_l > 0.10 * H, ("FK upper arm does not move the hand", fk_l)
    assert fk_r < 0.002 * H, ("FK left arm moved the right hand", fk_r)

    # 4) IK arm control moves the hand; FK is ignored while in IK
    props["IK_FK-arm-L"] = 1.0
    bpy.context.view_layer.update()
    hl = _centre(mesh, region["hand.L"])
    rot("upperarm.fk-L", 60)
    fk_in_ik = _moved(mesh, region["hand.L"], hl)
    reset()
    hl = _centre(mesh, region["hand.L"])
    pb["forearm.ik-L"].location = (0.0, 0.0, 0.15 * H)
    bpy.context.view_layer.update()
    ik_l = _moved(mesh, region["hand.L"], hl)
    reset()
    props["IK_FK-arm-L"] = 0.0
    assert fk_in_ik < 0.002 * H, ("FK control still drives the arm in IK mode", fk_in_ik)
    assert ik_l > 0.05 * H, ("IK hand control does not move the hand", ik_l)

    # 5) FK leg moves the foot
    props["IK_FK-leg-R"] = 0.0
    fr = _centre(mesh, region["foot.R"])
    rot("thigh.fk-R", 45, axis=0)
    leg = _moved(mesh, region["foot.R"], fr)
    reset()
    assert leg > 0.10 * H, ("FK thigh does not move the foot", leg)

    # 6) spine / head controls move the head
    hd = _centre(mesh, region["head"])
    rot("chest", 30, axis=0)
    chest = _moved(mesh, region["head"], hd)
    reset()
    rot("head", 40, axis=0)
    head = _moved(mesh, region["head"], hd)
    reset()
    assert chest > 0.03 * H and head > 0.01 * H, ("spine/head controls", chest, head)
    bpy.ops.object.mode_set(mode='OBJECT')

    print("controls verified (FK hand %.3f, other hand %.4f, FK-in-IK %.4f, "
          "IK hand %.3f, FK foot %.3f, chest->head %.3f, head %.3f)"
          % (fk_l, fk_r, fk_in_ik, ik_l, leg, chest, head))
    bpy.data.objects.remove(mesh, do_unlink=True)
    bpy.data.objects.remove(arm, do_unlink=True)
    print("ALL RIG-INTEGRATION TESTS PASS")


if __name__ == "__main__":
    run()
