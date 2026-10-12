"""In-Bforartists test: building a joint never moves the part's object.

An object part is bone-parented to its DEF bone. A Hinge re-orients that bone along the hinge axis, and
with a pivot away from the object's origin the object followed the bone: it turned 90 degrees and slid
(the Crescent Rose head mount did). Every rebuild must leave bone-parented objects where they were.
"""
import bpy
from mathutils import Matrix

import boneforge


def _cube(name, loc):
    bpy.ops.mesh.primitive_cube_add(size=0.2, location=loc)
    ob = bpy.context.object
    ob.name = name
    return ob


def _same(a, b, tol=1e-4):
    return all(abs(a[i][j] - b[i][j]) < tol for i in range(4) for j in range(4))


def run():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    boneforge.register()
    try:
        from boneforge.mechanisms import build, model as M, parts, records
        head = _cube("Head", (0.0, 0.2, 1.8))
        arm, (pid,), _ = parts.add_parts_from_selection(bpy.context)
        before = head.matrix_world.copy()
        assert _same(before, Matrix.Translation((0.0, 0.2, 1.8))), before
        for axis in ((1, 0, 0), (0, 1, 0), (0, 0, 1)):
            with records.quiet():
                records.find(arm.data, pid).pivot = (0.0, 0.05, 1.7)       # away from the origin, off every axis
            rid = "h%d" % axis.index(1)
            records.add(arm.data, M.Mechanism(rid, "HINGE", "Head Hinge", parts=[pid], axis=axis, min=0, max=150))
            build.rebuild(arm, {pid, rid})
            bpy.context.view_layer.update()
            after = head.matrix_world
            assert _same(before, after), ("axis", axis, "moved the object", [list(r) for r in after])
            build.delete(arm, rid)
            bpy.context.view_layer.update()
            assert _same(before, head.matrix_world), ("delete moved the object", axis)
        # a Slide too
        records.add(arm.data, M.Mechanism("s1", "SLIDE", "Head Slide", parts=[pid], axis=(0, 0, 1), min=0, max=0.3))
        build.rebuild(arm, {pid, "s1"})
        bpy.context.view_layer.update()
        assert _same(before, head.matrix_world), "a Slide moved the object"
        # a rebuild while the rig is POSED must keep the object's rest placement, not bake the pose into it
        rig = records.to_model(arm)
        build.set_value(arm, rig, "s1", 0.25)
        bpy.context.view_layer.update()
        posed = head.matrix_world.copy()
        assert abs(posed.translation.z - 1.8 - 0.25) < 1e-3, posed.translation
        records.find(arm.data, "s1").max = 0.5                                      # a value edit: rebuilds
        build.rebuild(arm, {pid, "s1"})
        bpy.context.view_layer.update()
        assert _same(posed, head.matrix_world), "a posed rebuild moved the object"
        build.set_value(arm, rig, "s1", 0.0)
        bpy.context.view_layer.update()
        assert _same(before, head.matrix_world), ("the pose was baked into the object", [list(r) for r in head.matrix_world])
        # a Sequence drives the joint to 0.3 at slider 1; a full rebuild with the slider at 1 (what Capture Step
        # leaves behind) must not bake that pose into the object either
        seq = records.add(arm.data, M.Sequence("q1", "Extend"))
        records.add_step(seq, M.Step("s1", 0.3, 0.0, 1.0, "LINEAR"))
        build.rebuild(arm)
        rig = records.to_model(arm)
        build.set_value(arm, rig, "q1", 1.0)
        bpy.context.view_layer.update()
        assert abs(head.matrix_world.translation.z - 1.8 - 0.3) < 1e-3, ("sequence did not drive", head.matrix_world.translation)
        build.rebuild(arm)
        bpy.context.view_layer.update()
        build.set_value(arm, rig, "q1", 0.0)
        bpy.context.view_layer.update()
        assert _same(before, head.matrix_world), ("a sequence pose was baked into the object", [list(r) for r in head.matrix_world])
        # the rig is at rest when the rebuild starts and posed when it ends: a step added to a sequence whose
        # slider already sits at 1 (the first Capture Step click leaves it there)
        seq2 = records.add(arm.data, M.Sequence("q2", "Later"))
        build.rebuild(arm)
        rig = records.to_model(arm)
        build.set_value(arm, rig, "q2", 1.0)
        records.add_step(seq2, M.Step("s1", 0.2, 0.0, 1.0, "LINEAR"))
        build.rebuild(arm)
        bpy.context.view_layer.update()
        assert abs(head.matrix_world.translation.z - 1.8 - 0.2) < 1e-3, ("new step did not drive", head.matrix_world.translation)
        build.set_value(arm, rig, "q2", 0.0)
        bpy.context.view_layer.update()
        assert _same(before, head.matrix_world), ("a rest-to-posed rebuild baked the pose", [list(r) for r in head.matrix_world])
        print("PASS mechanism builds keep object parts in place")
    finally:
        boneforge.unregister()
