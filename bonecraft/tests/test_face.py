"""In-Bforartists behavioural test for the R2 face rig.

Builds a head with the face option and verifies the facial network deforms:
the jaw opens (and deforms a skinned vertex), the eyes aim at their target,
and the lower lip follows the jaw by the soft-lips amount — reduced as
sticky-lips rises (so the lips stay sealed while the jaw opens).
"""
import math

import bpy
from mathutils import Matrix

import test_rig_build as trb
from boneforge.autorig.rig_build import RigSpec, build_control_rig


def _skin(arm, name_to_tail):
    names = list(name_to_tail)
    mesh = bpy.data.meshes.new("BF_FACE_SKIN")
    mesh.from_pydata([name_to_tail[n] for n in names], [], [])
    mesh.update()
    obj = bpy.data.objects.new("BF_FACE_SKIN", mesh)
    bpy.context.scene.collection.objects.link(obj)
    for i, n in enumerate(names):
        vg = obj.vertex_groups.new(name=n)
        vg.add([i], 1.0, 'REPLACE')
    mod = obj.modifiers.new("Armature", 'ARMATURE')
    mod.object = arm
    return obj, names


def _eval_bone_dir(arm, name):
    deps = bpy.context.evaluated_depsgraph_get()
    deps.update()
    pb = arm.evaluated_get(deps).pose.bones[name]
    v = pb.tail - pb.head
    return v.normalized() if v.length > 1e-9 else v


def run():
    arm = trb._fresh_armature()
    build_control_rig(arm, RigSpec(face=True))

    tails = {
        "jaw": (0.0, -0.10, 1.55),
        "eye-L": (0.035, -0.105, 1.665),
    }
    obj, names = _skin(arm, tails)
    bpy.context.view_layer.update()
    rest = trb._eval_world_coords(obj)
    ji, ei = names.index("jaw"), names.index("eye-L")
    lip_rest_dir = _eval_bone_dir(arm, "lip.lower")

    # -- jaw open deforms the jaw vertex; lower lip follows (soft, sticky=0) --
    trb._clear_pose(arm)
    jaw = arm.pose.bones["jaw"]
    jaw.rotation_mode = 'XYZ'
    jaw.rotation_euler = (-0.5, 0.0, 0.0)
    props = arm.pose.bones["face_props"]
    props["soft_lips"], props["sticky_lips"] = 0.6, 0.0
    arm.update_tag()
    bpy.context.view_layer.update()
    open_coords = trb._eval_world_coords(obj)
    jaw_disp = (rest[ji] - open_coords[ji]).length
    assert jaw_disp > 0.01, ("jaw did not deform", jaw_disp)
    soft_dir = _eval_bone_dir(arm, "lip.lower")
    soft_angle = soft_dir.angle(lip_rest_dir, 0.0)
    assert soft_angle > 0.05, ("lower lip did not follow jaw (soft)", soft_angle)
    print("jaw deform verified (%.3f); soft-lips follow = %.3f rad"
          % (jaw_disp, soft_angle))

    # -- sticky-lips reduces the follow (lips stay sealed) --
    props["sticky_lips"] = 1.0
    arm.update_tag()
    bpy.context.view_layer.update()
    sticky_dir = _eval_bone_dir(arm, "lip.lower")
    sticky_angle = sticky_dir.angle(lip_rest_dir, 0.0)
    assert sticky_angle < soft_angle - 0.02, \
        ("sticky-lips did not reduce follow", sticky_angle, soft_angle)
    print("sticky-lips verified (follow %.3f -> %.3f rad as sticky 0->1)"
          % (soft_angle, sticky_angle))

    # -- eye aim: moving the eye target rotates the eyeball + deforms it --
    trb._clear_pose(arm)
    eye_ik = arm.pose.bones["eye.ik-L"]
    eye_ik.location = (0.18, 0.0, 0.0)        # swing the look target sideways
    arm.update_tag()
    bpy.context.view_layer.update()
    eye_coords = trb._eval_world_coords(obj)
    eye_disp = (rest[ei] - eye_coords[ei]).length
    assert eye_disp > 0.005, ("eye did not aim/deform", eye_disp)
    print("eye aim verified (eyeball deformed %.3f under target move)" % eye_disp)

    trb._clear_pose(arm)
    print("ALL FACE TESTS PASS")
