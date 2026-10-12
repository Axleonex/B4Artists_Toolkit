# bonecraft/tests/test_mech_ops_host.py
"""In-Bforartists test: Mechanisms operators end to end (one undo step each, errors reported)."""
import math

import bmesh
import bpy
from mathutils import Matrix, Vector

import boneforge
from mech_draw_stubs import Ctx, Rec


def _cube(name, loc):
    bpy.ops.mesh.primitive_cube_add(size=0.2, location=loc)
    bpy.context.object.name = name
    return bpy.context.object


def _ok(result):
    assert result == {'FINISHED'}, result


def _refused(call, text):
    """Called from Python, an operator that reports an error raises RuntimeError with the message."""
    try:
        call()
    except RuntimeError as exc:
        assert text in str(exc), (text, str(exc))
        return
    raise AssertionError("not refused: " + text)


def _poll_reason(cls):
    """The reason an operator's poll gives for being off (there is no getter, so catch what poll_message_set receives)."""
    seen = []
    cls.poll_message_set = classmethod(lambda c, msg, *a: seen.append(msg))
    try:
        cls.poll(bpy.context)
    finally:
        del cls.poll_message_set
    return " ".join(seen)


def run():
    bpy.ops.wm.read_factory_settings(use_empty=True)   # an empty scene: no names or modes left by earlier tests
    boneforge.register()
    try:
        from boneforge.mechanisms import build, ops, records                 # after register
        blade, cover = _cube("Blade", (0, 0, 1)), _cube("Cover", (1, 0, 1))
        bpy.ops.object.select_all(action='DESELECT')
        blade.select_set(True)
        cover.select_set(True)
        bpy.context.view_layer.objects.active = blade
        assert not bpy.ops.boneforge.mech_add_joint.poll(), "no rig yet: disabled"
        _ok(bpy.ops.boneforge.mech_add_parts())
        arm = blade.parent
        rec = arm.data.bonecraft_mech
        pb_id, pc_id = rec.parts[0].id, rec.parts[1].id
        assert bpy.ops.boneforge.mech_add_joint.poll()

        _ok(bpy.ops.boneforge.mech_add_joint(type="HINGE", parts=pb_id, axis="X"))
        _ok(bpy.ops.boneforge.mech_add_joint(type="HINGE", parts=pc_id, axis="Y"))
        h1, h2 = rec.mechanisms[0], rec.mechanisms[1]
        assert (h1.name, h2.name) == ("Blade Hinge", "Cover Hinge") and tuple(h2.axis) == (0.0, 1.0, 0.0)

        # Set Max by posing the handle
        rig = records.to_model(arm)
        build.set_value(arm, rig, h1.id, 60.0)
        _ok(bpy.ops.boneforge.mech_set_limit(target=h1.id, which="MAX"))
        assert abs(h1.max - 60.0) < 1e-3

        # Links: a Follow from the blade to the cover; a broken request is reported, not raised
        _ok(bpy.ops.boneforge.mech_add_link(type="FOLLOW", source=pb_id, target=pc_id))
        assert rec.mechanisms[2].name == "Cover Follow" and rec.mechanisms[2].state == "OK"
        _refused(lambda: bpy.ops.boneforge.mech_add_link(type="GEAR", source=pc_id, target=pb_id), "would loop")
        assert len(rec.mechanisms) == 3, "a refused link leaves no record"

        # Align to Selection: a face's normal in Edit Mode
        bpy.ops.mesh.primitive_cube_add(size=0.2, location=(3, 0, 1))
        lid = bpy.context.object
        lid.name = "Lid"
        bpy.ops.object.select_all(action='DESELECT')
        lid.select_set(True)
        bpy.context.view_layer.objects.active = arm
        lid.select_set(True)
        _ok(bpy.ops.boneforge.mech_add_parts())
        lid_id = rec.parts[2].id
        bpy.context.view_layer.objects.active = lid
        bpy.ops.object.mode_set(mode='EDIT')
        bm = bmesh.from_edit_mesh(lid.data)
        for f in bm.faces:
            f.select_set(abs(f.normal.z - 1.0) < 1e-6)
        bmesh.update_edit_mesh(lid.data)
        _ok(bpy.ops.boneforge.mech_add_joint(type="SLIDE", parts=lid_id, axis="SELECTION"))
        assert bpy.context.object.mode == 'EDIT', "the rigger's mode is restored"
        bpy.ops.object.mode_set(mode='OBJECT')
        assert tuple(round(x, 6) for x in rec.mechanisms[3].axis) == (0.0, 0.0, 1.0)

        # Sequence: Capture Step moves the slider to the end first, then captures posed handles
        bpy.context.view_layer.objects.active = arm
        _ok(bpy.ops.boneforge.mech_add_sequence(name="Unfold"))
        seq = rec.sequences[0]
        rig = records.to_model(arm)
        _ok(bpy.ops.boneforge.mech_capture_step(target=seq.id))
        assert abs(build.get_value(arm, rig, seq.id) - 1.0) < 1e-6 and len(seq.steps) == 0
        build.set_value(arm, rig, h1.id, 45.0)
        _ok(bpy.ops.boneforge.mech_capture_step(target=seq.id))
        assert [(s.target, round(s.value, 3), s.start, s.end) for s in seq.steps] == [(h1.id, 45.0, 0.0, 0.25)]
        assert abs(build.get_value(arm, rig, h1.id)) < 1e-6, "handles return to rest"
        build.set_value(arm, rig, h1.id, 10.0)
        _ok(bpy.ops.boneforge.mech_capture_step(target=seq.id))
        assert [(round(s.value, 3), s.start, s.end) for s in seq.steps][1] == (55.0, 0.25, 0.5)

        # A refused rebuild rolls Capture Step and Remove Step back (a CANCELLED operator is not undone)
        real_rebuild = build.rebuild
        calls = []

        def refuse_once(*a, **k):
            if not calls:
                calls.append(1)
                raise build.BuildError("simulated rebuild failure")
            return real_rebuild(*a, **k)
        build.rebuild = refuse_once
        try:
            build.set_value(arm, rig, h1.id, 20.0)
            _refused(lambda: bpy.ops.boneforge.mech_capture_step(target=seq.id), "simulated")
            assert len(seq.steps) == 2, "the refused capture left no step"
            assert abs(build.get_value(arm, rig, h1.id) - 20.0) < 1e-4, "the posed handle is unchanged"
            build.set_value(arm, rig, h1.id, 0.0)
            calls.clear()
            _refused(lambda: bpy.ops.boneforge.mech_remove_step(target=seq.id, index=0), "simulated")
            assert [(round(s.value, 3), s.start, s.end) for s in seq.steps] == [(45.0, 0.0, 0.25), (55.0, 0.25, 0.5)],                 "the refused removal left the steps in place"
        finally:
            build.rebuild = real_rebuild

        # Polls say why they are off
        bpy.context.view_layer.objects.active = lid
        bpy.ops.object.mode_set(mode='EDIT')
        assert not bpy.ops.boneforge.mech_add_parts.poll(), "Add Parts is off in Edit Mode"
        assert "Object Mode" in _poll_reason(ops.BC_OT_mech_add_parts)
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.view_layer.objects.active = arm
        assert not bpy.ops.boneforge.mech_apply_pivot.poll(), "no pivot marker selected"
        assert "pivot marker" in _poll_reason(ops.BC_OT_mech_apply_pivot)

        # Align to Selection gives the true world normal on a rotated, non-uniformly scaled cube
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(5, 0, 1))
        slab = bpy.context.object
        slab.name = "Slab"
        slab.data.transform(Matrix.Rotation(math.radians(45), 4, 'Z'))   # slanted faces, then a stretched object
        slab.scale = (2.0, 1.0, 1.0)
        bpy.context.view_layer.update()
        bpy.ops.object.select_all(action='DESELECT')
        slab.select_set(True)
        bpy.context.view_layer.objects.active = arm
        slab.select_set(True)
        _ok(bpy.ops.boneforge.mech_add_parts())
        slab_id = next(p.id for p in rec.parts if p.object_name == "Slab")
        bpy.context.view_layer.objects.active = slab
        bpy.ops.object.mode_set(mode='EDIT')
        bm = bmesh.from_edit_mesh(slab.data)
        for f in bm.faces:
            f.select_set(False)
        face = max(bm.faces, key=lambda f: f.normal.x)                    # a slanted face, in object space
        face.select_set(True)
        bm.select_history.clear()
        bm.select_history.add(face)
        n_obj = face.normal.copy()
        m3 = slab.matrix_world.to_3x3().copy()                            # the matrix the operator will read
        bmesh.update_edit_mesh(slab.data)
        _ok(bpy.ops.boneforge.mech_add_joint(type="SLIDE", parts=slab_id, axis="SELECTION"))
        bpy.ops.object.mode_set(mode='OBJECT')
        true_world = (m3.inverted().transposed() @ n_obj).normalized()
        plain_world = (m3 @ n_obj).normalized()
        assert (true_world - plain_world).length > 0.1, "the cube must tell the two transforms apart"
        got = Vector(rec.mechanisms[-1].axis)
        want = arm.matrix_world.inverted().to_3x3() @ true_world
        assert (got - want).length < 1e-4, (tuple(got), tuple(want))
        bpy.context.view_layer.objects.active = arm
        h1, h2 = rec.mechanisms[0], rec.mechanisms[1]     # adding a fifth record may move the collection: look them up again
        seq = rec.sequences[0]

        # Forms: save, move away, go back with keys
        rig = records.to_model(arm)
        build.set_value(arm, rig, seq.id, 0.0)
        build.set_value(arm, rig, h2.id, 20.0)
        _ok(bpy.ops.boneforge.mech_save_form(name="Stowed"))
        build.set_value(arm, rig, h2.id, 0.0)
        _ok(bpy.ops.boneforge.mech_go_to_form(name="Stowed", insert_keys=True))
        assert abs(build.get_value(arm, rig, h2.id) - 20.0) < 1e-4
        assert arm.animation_data and arm.animation_data.action, "Go to Form inserted keys"

        # Changed by hand -> Keep mine / Restore through the operators
        lim = arm.pose.bones[build.bone_tags(arm)[(pc_id, "MCH")]].constraints[f"BC·{h2.id}·limit"]
        lim.max_x = math.radians(50)
        rec.active_mech = 1                                     # selecting runs the hand-edit check
        assert h2.state == "CHANGED_BY_HAND"
        _ok(bpy.ops.boneforge.mech_keep_mine(target=h2.id))
        assert abs(h2.max - 50.0) < 1e-3 and h2.state == "OK"

        # Select the bone a "How this works" note names
        _ok(bpy.ops.boneforge.mech_select_bone(bone=lim.id_data.pose.bones[build.bone_tags(arm)[(pc_id, "MCH")]].name))

        # Delete in the right order; Detach keeps the rig
        _refused(lambda: bpy.ops.boneforge.mech_delete(target=pb_id), "Blade Hinge")
        _ok(bpy.ops.boneforge.mech_delete(target=seq.id))
        _ok(bpy.ops.boneforge.mech_detach(target=rec.mechanisms[2].id))
        assert len(rec.mechanisms) == 4, "two hinges and two slides remain once the Follow is detached"

        # a renamed part object keeps its own axes and its Apply Transforms; a deleted one refuses the axis
        from boneforge.mechanisms import parts
        if bpy.context.object is not None and bpy.context.object.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')          # Select Bone left the rig in Pose Mode
        bpy.ops.mesh.primitive_cube_add(size=0.2, location=(7, 0, 1), rotation=(0, 0, math.pi / 2))
        turned = bpy.context.object
        turned.name = "Turned"
        bpy.ops.object.select_all(action='DESELECT')
        turned.select_set(True)
        bpy.context.view_layer.objects.active = arm
        _ok(bpy.ops.boneforge.mech_add_parts())
        turned_id = next(p.id for p in rec.parts if p.object_name == "Turned")
        turned.name = "Turned Renamed"
        _ok(bpy.ops.boneforge.mech_add_joint(type="HINGE", parts=turned_id, axis="X"))
        want = arm.matrix_world.inverted().to_3x3() @ Vector((0.0, 1.0, 0.0))    # X turned 90 degrees about Z
        assert (Vector(rec.mechanisms[-1].axis) - want).length < 1e-4, tuple(rec.mechanisms[-1].axis)
        assert parts.needs_apply(turned)
        from boneforge.mechanisms import ui
        rec.active_part = next(i for i, p in enumerate(rec.parts) if p.id == turned_id)
        log = []
        ui.draw_parts(Rec(log), Ctx())
        assert any(n == "label" and k.get("text") == ui.T("Unapplied rotation or scale tilts the axes.") for n, a, k in log)             and any(n == "operator" and a == ("boneforge.mech_apply_transforms",) for n, a, k in log),             "the parts panel warns about the renamed object's rotation and offers Apply Transforms"
        _ok(bpy.ops.boneforge.mech_apply_transforms(target=turned_id))
        assert not parts.needs_apply(turned) and turned.name == "Turned Renamed"
        bpy.data.objects.remove(turned)
        try:
            ops.part_axis(arm, records.find(arm.data, turned_id), "X")
            raise AssertionError("a part without its mesh has no axes")
        except build.BuildError as exc:
            assert str(exc) == "Part 'Turned' has no mesh: Reassign it first.", str(exc)
        _refused(lambda: bpy.ops.boneforge.mech_add_joint(type="SLIDE", parts=turned_id, axis="X"), "Reassign it first")
        _refused(lambda: bpy.ops.boneforge.mech_apply_transforms(target=turned_id), "missing")
    finally:
        boneforge.unregister()
    print("PASS mechanisms operators: parts, joints, limits, links, align, capture, forms, keep mine, delete, detach")
