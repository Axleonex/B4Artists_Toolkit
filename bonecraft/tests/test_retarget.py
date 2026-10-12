"""In-Bforartists behavioural test for the R4 retargeting workflow.

Retargets a synthetic source clip from >=3 source naming families (the
``maps/`` presets) onto an engine rig, verifying: namespace resolution +
missing-bone diagnostics, motion fidelity (the retargeted FK bone points where
the source bone points, although the two rest in different orientations —
motion-capture rests are arbitrary, so fidelity is judged on pose, not on
rotation relative to rest), per-bone tweaks, and batch (one clean action per
source).
"""
import math

import bpy

import test_rig_build as trb
from boneforge.autorig.rig_build import RigSpec, build_control_rig
from boneforge.autorig import maps
from boneforge.autorig import retarget_core as rc
from boneforge.autorig.retarget import retarget_clip_corrected


def _q_angle(q):
    return 2.0 * math.acos(min(1.0, abs(q.w)))


def _object_mode():
    if bpy.context.object is not None and bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')


def _source_arm(name, upper_src, fore_src, along_x=False):
    """A 2-bone source chain pointing +Z (a different rest from the +X target),
    so the retarget must actually correct orientation — or along +X like the
    target when ``along_x`` (rotation relative to rest is then comparable)."""
    _object_mode()
    bpy.ops.object.armature_add(enter_editmode=True)
    arm = bpy.context.active_object
    arm.name = name
    ebs = arm.data.edit_bones
    for eb in list(ebs):
        ebs.remove(eb)
    end1, end2 = ((0.3, 0, 0), (0.6, 0, 0)) if along_x else ((0, 0, 0.3), (0, 0, 0.6))
    up = ebs.new(upper_src); up.head = (0, 0, 0); up.tail = end1
    fo = ebs.new(fore_src); fo.head = end1; fo.tail = end2
    fo.parent = up
    bpy.ops.object.mode_set(mode='OBJECT')
    return arm


def _animate(arm, bone, axis, deg, f0=1, f1=5):
    from mathutils import Quaternion
    pb = arm.pose.bones[bone]
    pb.rotation_mode = 'QUATERNION'
    scene = bpy.context.scene
    scene.frame_set(f0)
    pb.rotation_quaternion = (1, 0, 0, 0)
    pb.keyframe_insert("rotation_quaternion", frame=f0)
    scene.frame_set(f1)
    pb.rotation_quaternion = Quaternion(axis, math.radians(deg))
    pb.keyframe_insert("rotation_quaternion", frame=f1)


def _retarget_one(map_name):
    preset = maps.load_map(map_name)
    tgt_to_src = {t: s for s, t in preset["bones"].items()}
    assert "upperarm.fk-L" in tgt_to_src and "forearm.fk-L" in tgt_to_src, map_name
    upper_src_raw = tgt_to_src["upperarm.fk-L"]
    fore_src_raw = tgt_to_src["forearm.fk-L"]
    # source bones carry a capture namespace
    upper_src = "mocap:" + rc.strip_namespace(upper_src_raw)
    fore_src = "mocap:" + rc.strip_namespace(fore_src_raw)

    src = _source_arm("SRC_" + map_name, upper_src, fore_src)
    _animate(src, upper_src, (1, 0, 0), 30.0)

    target = trb._fresh_armature()
    build_control_rig(target, RigSpec())

    # build mappings through the namespace; omit one source to see a diagnostic
    source_names = [upper_src, fore_src]
    target_names = {b.name for b in target.data.bones}
    res = rc.build_mappings(preset, source_names, target_names)
    name_map = rc.matched_name_map(res)
    assert "upperarm.fk-L" in name_map.values(), (map_name, name_map)
    assert res["missing_source"], "expected missing-source diagnostics"

    n = retarget_clip_corrected(src, target, name_map, 1, 5)
    assert n == 5, (map_name, n)

    # fidelity: the retargeted FK bone points where the source bone points
    bpy.context.scene.frame_set(5)
    bpy.context.view_layer.update()
    sb, tb = src.pose.bones[upper_src], target.pose.bones["upperarm.fk-L"]
    sdir = (src.matrix_world @ sb.tail - src.matrix_world @ sb.head).normalized()
    tdir = (target.matrix_world @ tb.tail - target.matrix_world @ tb.head).normalized()
    ang = math.degrees(sdir.angle(tdir))
    assert ang < 3.0, ("motion not preserved (direction error deg)", map_name, ang)
    # negative control: without the retarget the target keeps its rest (+X)
    rest_dir = (target.matrix_world.to_3x3() @ (tb.bone.tail_local - tb.bone.head_local)).normalized()
    assert math.degrees(sdir.angle(rest_dir)) > 30.0, "test pose too close to rest"

    bpy.data.objects.remove(src, do_unlink=True)
    return target, name_map, ang


def run():
    families = maps.available_maps()
    usable = []
    for m in families:
        preset = maps.load_map(m)
        inv = set(preset["bones"].values())
        if {"upperarm.fk-L", "forearm.fk-L"} <= inv:
            usable.append(m)
    assert len(usable) >= 3, ("need >=3 source families", usable)
    print("retarget: %d source families available" % len(usable))

    last_target = last_map = None
    for m in usable[:3]:
        last_target, last_map, ang = _retarget_one(m)
        print("  %-18s motion preserved (%.2f deg direction error)" % (m, ang))

    # per-bone tweak: a 0.5 multiplier halves the retargeted rotation
    src = _source_arm("SRC_TWEAK",
                      "mocap:Up", "mocap:Fore", along_x=True)
    _animate(src, "mocap:Up", (1, 0, 0), 40.0)
    target = trb._fresh_armature(); build_control_rig(target, RigSpec())
    name_map = {"mocap:Up": "upperarm.fk-L"}
    tweaks = {"mocap:Up": rc.BoneTweak(rot_multiplier=0.5)}
    retarget_clip_corrected(src, target, name_map, 1, 5, tweaks=tweaks)
    bpy.context.scene.frame_set(5); bpy.context.view_layer.update()
    ang = math.degrees(_q_angle(target.pose.bones["upperarm.fk-L"].rotation_quaternion))
    assert abs(ang - 20.0) < 3.0, ("tweak multiplier not applied", ang)
    print("per-bone tweak verified (0.5x of 40 deg -> %.1f deg)" % ang)
    bpy.data.objects.remove(src, do_unlink=True)

    # batch: two source clips -> two distinct target actions
    actions_before = set(bpy.data.actions.keys())
    for i in range(2):
        s = _source_arm("SRC_BATCH%d" % i, "mocap:Up", "mocap:Fore")
        _animate(s, "mocap:Up", (1, 0, 0), 20.0 + 10 * i)
        tgt = trb._fresh_armature(); build_control_rig(tgt, RigSpec())
        tgt.animation_data_create()
        act = bpy.data.actions.new("BATCH_%d" % i)
        tgt.animation_data.action = act
        retarget_clip_corrected(s, tgt, {"mocap:Up": "upperarm.fk-L"}, 1, 5)
        bpy.data.objects.remove(s, do_unlink=True)
    new_actions = set(bpy.data.actions.keys()) - actions_before
    assert sum(1 for a in new_actions if a.startswith("BATCH_")) == 2, new_actions
    print("batch verified (2 clips -> 2 clean target actions)")

    print("ALL RETARGET TESTS PASS")
