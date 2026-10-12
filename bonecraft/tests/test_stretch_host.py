"""In-Bforartists behavioural test: IK stretch reaches the skin.

On an integrated rig in IK mode, the hand control is pulled 0.30 m past the
arm's reach. With ``IK_stretch-arm-L`` = 1 the mesh hand must follow the
control (the deform chain lengthens); with 0 the arm stays rigid (negative
control) — before this, the IK chain stretched but the skin never did.
"""
import bpy
from mathutils import Matrix, Vector

import test_rig_integrate_host as rih
from boneforge.autorig.rig_build import build_control_rig


def _pull(arm, mesh, hand_idx, stretch):
    pb = arm.pose.bones
    pb["properties"]["IK_FK-arm-L"] = 1.0
    pb["properties"]["IK_stretch-arm-L"] = stretch
    arm.update_tag()
    bpy.context.view_layer.update()

    def centre():
        ev = mesh.evaluated_get(bpy.context.evaluated_depsgraph_get()).data.vertices
        c = Vector()
        for i in hand_idx:
            c += mesh.matrix_world @ ev[i].co
        return c / len(hand_idx)

    ctrl = pb["forearm.ik-L"]
    ctrl.location = (0.0, 0.0, 0.0)
    bpy.context.view_layer.update()
    c0 = centre()
    rest = arm.matrix_world @ ctrl.head
    goal = rest + Vector((0.30, 0.0, 0.0))
    ctrl.matrix = arm.matrix_world.inverted() @ Matrix.Translation(goal) \
        @ (arm.matrix_world @ ctrl.matrix).to_3x3().to_4x4()
    bpy.context.view_layer.update()
    moved = (centre() - c0).length
    ev = arm.evaluated_get(bpy.context.evaluated_depsgraph_get())
    gap = ((arm.matrix_world @ ev.pose.bones["hand.def-L"].head) - goal).length
    ctrl.location = (0.0, 0.0, 0.0)
    bpy.context.view_layer.update()
    return moved, gap


def run():
    mesh, labels, arm = rih.build_skinned_rig()
    build_control_rig(arm, context=bpy.context)
    hand_idx = [i for i, lab in enumerate(labels) if lab == "hand.L"]
    moved_on, gap_on = _pull(arm, mesh, hand_idx, 1.0)
    moved_off, gap_off = _pull(arm, mesh, hand_idx, 0.0)
    assert gap_on < 0.01 and moved_on > 0.25, ("stretch does not reach the skin", moved_on, gap_on)
    assert moved_off < 0.01 and gap_off > 0.25, ("rigid setting stretched anyway", moved_off, gap_off)
    print("stretch verified (on: hand follows %.3f m, gap %.3f; off: rigid, moved %.3f)"
          % (moved_on, gap_on, moved_off))
    bpy.data.objects.remove(mesh, do_unlink=True)
    bpy.data.objects.remove(arm, do_unlink=True)
    print("ALL STRETCH TESTS PASS")


if __name__ == "__main__":
    run()
