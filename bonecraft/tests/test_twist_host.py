"""In-Bforartists behavioural test: forearm twist bones stop the wrist pinch.

On an integrated rig (wizard skin + control rig), turning the hand 90 degrees
about its own axis should twist the forearm gradually. Without twist bones the
forearm stays put while the hand turns, so all 90 degrees happen at the wrist
(a tear, or a "candy wrapper" pinch where weights blend). Measured before and
after ``add_twist_bones`` on the same rig: the largest twist jump between
neighbouring forearm rings must drop to <= 50 degrees.
"""
import math

import bpy
from mathutils import Vector

import test_rig_integrate_host as rih
from boneforge.autorig.rig_build import build_control_rig
from boneforge.autorig import rig_integrate as ri


def twist_profile(mesh, arm, fore_idx, hand_idx, side="L", deg=90.0):
    """Largest twist jump (degrees) between neighbouring forearm/hand rings.

    Turns the FK hand ``deg`` about its own axis and measures how far each
    ring of the forearm (10% bins from elbow to wrist) plus the hand turns
    about the forearm axis. Without twist bones the forearm stays at 0 while
    the hand turns fully: one ``deg``-sized tear at the wrist.
    """
    import math as _m
    import bpy as _bpy
    fb = arm.data.bones["forearm.def-" + side]
    h, t = arm.matrix_world @ fb.head_local, arm.matrix_world @ fb.tail_local
    d, length = (t - h).normalized(), (t - h).length

    def radial(p):
        v = p - h
        return v - d * v.dot(d)

    def positions():
        ev = mesh.evaluated_get(_bpy.context.evaluated_depsgraph_get()).data.vertices
        return {i: mesh.matrix_world @ ev[i].co for i in list(fore_idx) + list(hand_idx)}

    pb = arm.pose.bones
    pb["properties"]["IK_FK-arm-" + side] = 0.0
    arm.update_tag(); _bpy.context.view_layer.update()
    p0 = positions()
    hand = pb["hand.fk-" + side]; hand.rotation_mode = 'XYZ'
    hand.rotation_euler = (0.0, _m.radians(deg), 0.0)
    _bpy.context.view_layer.update()
    p1 = positions()
    hand.rotation_euler = (0.0, 0.0, 0.0); _bpy.context.view_layer.update()

    def angle(i):
        a, b = radial(p0[i]), radial(p1[i])
        if a.length < 1e-6 or b.length < 1e-6:
            return None
        ang = _m.degrees(a.angle(b))
        return ang if a.cross(b).dot(d) >= 0 else -ang

    rings = {}
    for i in fore_idx:
        u = (p0[i] - h).dot(d) / length
        if 0.0 <= u <= 1.0:
            ang = angle(i)
            if ang is not None:
                rings.setdefault(min(int(u * 10), 9), []).append(ang)
    hand_angles = [a for a in (angle(i) for i in hand_idx) if a is not None]
    means = [sum(v) / len(v) for k, v in sorted(rings.items()) if len(v) >= 3]
    if hand_angles:
        means.append(sum(hand_angles) / len(hand_angles))
    return max((abs(b - a) for a, b in zip(means, means[1:])), default=0.0)


def run():
    mesh, labels, arm = rih.build_skinned_rig()
    build_control_rig(arm, context=bpy.context)
    idx_fore = [i for i, lab in enumerate(labels) if lab == "arm.L"]
    idx_hand = [i for i, lab in enumerate(labels) if lab == "hand.L"]
    base = twist_profile(mesh, arm, idx_fore, idx_hand)
    added = ri.add_twist_bones(arm, segments=2)
    assert set(ri.twist_bone_names("L", 2)) <= set(added), added
    fixed = twist_profile(mesh, arm, idx_fore, idx_hand)
    assert fixed <= 50.0, ("wrist still tears with twist bones", base, fixed)
    assert fixed < base - 20.0, ("twist bones did not help", base, fixed)
    assert ri.add_twist_bones(arm, segments=2) == [], "not idempotent"
    # the task board's fix button calls this operator (it used to not exist)
    bpy.context.view_layer.objects.active = arm
    assert bpy.ops.boneforge.generate_twist_bones() == {'FINISHED'}
    print("twist verified (largest ring-to-ring twist jump %.0f -> %.0f deg for a 90 deg wrist turn)"
          % (base, fixed))
    bpy.data.objects.remove(mesh, do_unlink=True)
    bpy.data.objects.remove(arm, do_unlink=True)
    print("ALL TWIST TESTS PASS")


if __name__ == "__main__":
    run()
