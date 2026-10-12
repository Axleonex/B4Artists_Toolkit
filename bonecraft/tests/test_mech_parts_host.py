"""In-Bforartists test: Mechanisms parts — objects, loose pieces, pivots, Merge for VRChat, remove."""
import math

import bmesh
import bpy

import boneforge


def _cube(name, loc, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=0.2, location=loc, rotation=rot)
    bpy.context.object.name = name
    return bpy.context.object


def _select(*objs):
    bpy.ops.object.select_all(action='DESELECT')
    for ob in objs:
        ob.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]


def _close(a, b, eps=1e-4):
    return all(abs(x - y) < eps for x, y in zip(a, b))


def _copy(ob):
    """A duplicate as Shift+D or copy/paste makes it: same tags, same bone parent, same modifiers."""
    c = ob.copy()
    bpy.context.scene.collection.objects.link(c)
    return c


def _duplicates(build, records, parts):
    """A part keeps its own object when that object is duplicated, renamed or deleted."""
    lid, base = _cube("Lid", (0, 3, 0), rot=(0, 0, math.pi / 2)), _cube("Base", (0, 3, -1))
    _select(lid, base)
    rig, (pl, pb), _ = parts.add_parts_from_selection(bpy.context)
    obj = lambda pid: records.part_object(records.find(rig.data, pid))
    copy = _copy(lid)
    assert records.tag_ids(copy) == [pl] and (copy.parent, copy.parent_bone) == (rig, lid.parent_bone), "the copy is bound too"
    assert obj(pl) == lid
    lid.name = "Top Lid"                       # the stored name misses; the copy "Lid.001" sorts first
    assert obj(pl) == lid, "a renamed original keeps its part, not its copy"
    parts.bind(rig, [pl])
    assert records.find(rig.data, pl).object_name == "Top Lid" and lid.parent_bone == build.bone_tags(rig)[(pl, "DEF")]

    # the copy added as its own part carries only its new id
    _select(rig, copy)
    _, (pc,), _ = parts.add_parts_from_selection(bpy.context)
    assert records.tag_ids(copy) == [pc], records.tag_ids(copy)
    assert obj(pl) == lid and obj(pc) == copy and copy.parent_bone == build.bone_tags(rig)[(pc, "DEF")]

    # deleting the original leaves the part missing; a bound copy is not adopted
    spare = _copy(lid)
    _select(lid)
    bpy.ops.object.delete()
    assert obj(pl) is None and pl in records.to_model(rig).missing, "a deleted object part is missing"
    assert obj(pc) == copy and records.tag_ids(spare) == [pl]
    parts.bind(rig, [pl])
    assert spare.parent_bone == build.bone_tags(rig)[(pl, "DEF")] and records.find(rig.data, pl).object_name != spare.name
    assert lid.users == 0, "an operator lets go of the deleted object, so Blender can free it"
    parts.reassign(rig, pl, spare)
    assert obj(pl) == spare and pl not in records.to_model(rig).missing

    # a record without an object reference goes by its tag: a lone bound candidate, never a guess
    records.find(rig.data, pb).property_unset("object_ref")
    twin = _copy(base)
    base.name = "Zed Base"
    assert obj(pb) is None, "two bound copies and a stale name: the part is missing, not switched"
    twin.parent = None
    assert obj(pb) == base, "the one still bound to the part's DEF bone wins"

    # a loose part's mesh duplicated: the loose part keeps the original mesh
    me = bpy.data.meshes.new("Gears")
    bm = bmesh.new()
    for off in (0.0, 2.0):
        bmesh.ops.create_cube(bm, size=0.2, matrix=__import__("mathutils").Matrix.Translation((off, 6, 0)))
    bm.to_mesh(me)
    bm.free()
    gears = bpy.data.objects.new("Gears", me)
    bpy.context.scene.collection.objects.link(gears)
    _select(rig, gears)
    _, (g1, g2), _ = parts.add_parts_from_selection(bpy.context)
    gcopy = _copy(gears)
    gears.name = "Zed Gears"
    assert obj(g1) == gears and obj(g2) == gears, "the loose parts keep the original mesh"
    assert records.to_model(rig).missing == set()


def _copy_after_delete():
    """A copy added as its own part after its original was deleted carries only its new id."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    boneforge.register()
    try:
        from boneforge.mechanisms import parts, records       # after register
        lid = _cube("Lid", (0, 0, 0))
        _select(lid)
        rig, (pl,), _ = parts.add_parts_from_selection(bpy.context)
        copy = _copy(lid)
        _select(lid)
        bpy.ops.object.delete()
        records.refresh_object_names(rig.data)                     # the reference is set, but None
        pg = records.find(rig.data, pl)
        assert pg.is_property_set("object_ref") and pg.object_ref is None
        _select(copy)
        _, (pc,), _ = parts.add_parts_from_selection(bpy.context)
        assert records.tag_ids(copy) == [pc], records.tag_ids(copy)
        assert records.part_object(records.find(rig.data, pl)) is None, "the old part stays missing"
    finally:
        boneforge.unregister()


def _loose_siblings():
    """Loose parts share their mesh: adding another loose part from it keeps every id on the mesh."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    boneforge.register()
    try:
        from boneforge.mechanisms import build, model as M, parts, records       # after register
        me = bpy.data.meshes.new("Pieces")
        bm = bmesh.new()
        for off in (0.0, 2.0):
            bmesh.ops.create_cube(bm, size=0.2, matrix=__import__("mathutils").Matrix.Translation((off, 0, 0)))
        bm.to_mesh(me)
        bm.free()
        pieces = bpy.data.objects.new("Pieces", me)
        bpy.context.scene.collection.objects.link(pieces)
        _select(pieces)
        rig, (g1, g2), _ = parts.add_parts_from_selection(bpy.context)
        pieces.vertex_groups.new(name="Third").add(range(4), 1.0, 'REPLACE')
        records.add(rig.data, M.Part("g3", "Third", kind="LOOSE", object_name=pieces.name, vertex_group="Third"))
        build.rebuild(rig, {"g3"})
        parts.bind(rig, ["g3"])
        assert sorted(records.tag_ids(pieces)) == sorted([g1, g2, "g3"]), records.tag_ids(pieces)
        assert all(records.part_object(records.find(rig.data, p)) == pieces for p in (g1, g2, "g3"))
    finally:
        boneforge.unregister()


def run():
    bpy.ops.wm.read_factory_settings(use_empty=True)   # an empty scene: no names or modes left by earlier tests
    boneforge.register()
    try:
        from boneforge.mechanisms import build, model as M, parts, records       # after register
        a, b = _cube("Frame", (0, 0, 0)), _cube("Arm", (0, 0, 1), rot=(0.3, 0, 0))
        mw = {ob.name: ob.matrix_world.copy() for ob in (a, b)}
        _select(a, b)
        arm, pids, warn = parts.add_parts_from_selection(bpy.context)
        assert arm.type == 'ARMATURE' and len(pids) == 2 and warn == ["Arm"], warn
        tags = build.bone_tags(arm)
        for ob, pid in zip((a, b), pids):
            assert (ob.parent, ob.parent_type, ob.parent_bone) == (arm, 'BONE', tags[(pid, "DEF")])
        bpy.context.view_layer.update()
        assert all(_close(ob.matrix_world.col[3], mw[ob.name].col[3]) for ob in (a, b)), "objects keep their place"
        assert parts.needs_apply(b) and not parts.needs_apply(a)

        # renaming a part's object is harmless: parts are tagged, and bind writes the new name back
        a.name = "Frame Renamed"
        assert records.to_model(arm).missing == set(), "a renamed object part is not missing"
        assert records.part_object(records.find(arm.data, pids[0])) == a
        build.rebuild(arm)
        assert records.find(arm.data, pids[0]).state == "OK"
        assert (a.parent, a.parent_bone) == (arm, build.bone_tags(arm)[(pids[0], "DEF")]), "the rebuild keeps it bound"
        parts.bind(arm, [pids[0]])
        assert records.find(arm.data, pids[0]).object_name == "Frame Renamed", "bind writes the current name back"
        a.name = "Frame Moved"
        impostor = _cube("Frame Renamed", (5, 5, 5))           # an untagged mesh takes the old name
        assert impostor.name == "Frame Renamed"
        assert records.part_object(records.find(arm.data, pids[0])) == a, "the tagged object wins over the old name"
        parts.bind(arm, [pids[0]])
        assert records.find(arm.data, pids[0]).object_name == "Frame Moved" and impostor.parent is None             and "bc_mech_part" not in impostor, "the impostor is neither bound nor recorded"
        bpy.data.objects.remove(impostor)
        a.name = "Frame"
        decoy = _cube("Gone", (9, 9, 9))
        records.add(arm.data, M.Part("gone", "Gone", object_name="Gone"))
        build.rebuild(arm, {"gone"})
        parts.bind(arm, ["gone"])
        assert decoy.get("bc_mech_part") == "gone"
        bpy.data.objects.remove(decoy)
        assert records.to_model(arm).missing == {"gone"}, "a deleted object is still missing"
        build.delete(arm, "gone")
        assert records.to_model(arm).missing == set()
        parts.apply_transforms(b)
        assert not parts.needs_apply(b)
        _select(a, b)
        try:
            parts.add_parts_from_selection(bpy.context)
            raise AssertionError("adding the same objects twice must be refused")
        except build.BuildError:
            pass

        # one mesh with two loose pieces -> two LOOSE parts bound by vertex groups
        mesh = bpy.data.meshes.new("Pieces")
        bm = bmesh.new()
        for off in (0.0, 2.0):
            bmesh.ops.create_cube(bm, size=0.2, matrix=__import__("mathutils").Matrix.Translation((off, 0, 3)))
        bm.to_mesh(mesh)
        bm.free()
        pieces = bpy.data.objects.new("Pieces", mesh)
        bpy.context.scene.collection.objects.link(pieces)
        assert len(parts.islands(mesh)) == 2
        _select(pieces, arm)
        bpy.context.view_layer.objects.active = arm
        _, loose, _ = parts.add_parts_from_selection(bpy.context)
        tags = build.bone_tags(arm)
        assert len(loose) == 2
        for pid in loose:
            pg = records.find(arm.data, pid)
            assert pg.kind == "LOOSE" and pg.vertex_group == tags[(pid, "DEF")] and pieces.vertex_groups.get(pg.vertex_group)
        assert any(m.type == 'ARMATURE' and m.object == arm for m in pieces.modifiers)
        assert _close(records.find(arm.data, loose[1]).pivot, (2.0, 0, 3)), tuple(records.find(arm.data, loose[1]).pivot)

        # Reassign: the new object takes the bone; the old one is released where it stands
        spare = _cube("Spare", (4, 0, 0))
        bpy.context.view_layer.update()
        a_before = a.matrix_world.copy()
        parts.reassign(arm, pids[0], spare)
        bpy.context.view_layer.update()
        assert a.parent is None and _close(a.matrix_world.col[3], a_before.col[3]), "the old object is released in place"
        assert (spare.parent, spare.parent_bone) == (arm, build.bone_tags(arm)[(pids[0], "DEF")])
        parts.reassign(arm, pids[0], a)
        bpy.context.view_layer.update()
        assert spare.parent is None and a.parent == arm and a.parent_bone == build.bone_tags(arm)[(pids[0], "DEF")]

        # Reassign refuses what cannot work, and changes nothing when it does
        def refused(pid, ob):
            pg = records.find(arm.data, pid)
            name, parent = pg.object_name, ob.parent if ob is not None else None
            try:
                parts.reassign(arm, pid, ob)
                raise AssertionError("reassign should have been refused")
            except build.BuildError:
                pass
            assert pg.object_name == name and (ob is None or ob.parent == parent), "a refused reassign changes nothing"

        refused(pids[0], arm)                       # not a mesh
        refused(pids[0], b)                         # already another part
        refused(loose[0], spare)                    # a loose part needs its vertex group on the new mesh
        empty_g = _cube("EmptyGroup", (7, 0, 0))
        lg = records.find(arm.data, loose[0]).vertex_group
        empty_g.vertex_groups.new(name=lg)          # the group exists but weights nothing
        refused(loose[0], empty_g)
        empty_g.vertex_groups[lg].add(range(len(empty_g.data.vertices)), 0.0, 'REPLACE')     # assigned at weight 0
        refused(loose[0], empty_g)
        skin = _cube("Skin", (6, 0, 0))
        skin.vertex_groups.new(name=lg).add(range(len(skin.data.vertices)), 1.0, 'REPLACE')
        parts.reassign(arm, loose[0], skin)
        assert records.find(arm.data, loose[0]).object_name == "Skin"
        assert any(m.type == 'ARMATURE' and m.object == arm for m in skin.modifiers), "the new mesh is skinned"

        # loose parts of one mesh share it: two can be reassigned to the same mesh
        both = _cube("Both", (8, 0, 0))
        halves = (range(0, 4), range(4, 8))
        for lp, half in zip(loose, halves):
            both.vertex_groups.new(name=records.find(arm.data, lp).vertex_group).add(list(half), 1.0, 'REPLACE')
        for lp in loose:
            parts.reassign(arm, lp, both)
        for lp, half in zip(loose, halves):
            gi = both.vertex_groups[records.find(arm.data, lp).vertex_group].index
            assert {v.index for v in both.data.vertices if any(g.group == gi for g in v.groups)} == set(half),                 "each loose part keeps its own vertices"
        assert all(records.find(arm.data, lp).object_name == "Both" for lp in loose)
        assert len([m for m in both.modifiers if m.type == 'ARMATURE' and m.object == arm]) == 1
        for lp in reversed(loose):
            parts.reassign(arm, lp, pieces)
        assert all(records.find(arm.data, lp).object_name == "Pieces" for lp in loose)
        refused(pids[0], pieces)                    # an object part may not take a mesh other parts use

        # Edit Pivot: the bones move, the object stays where it is
        bpy.context.view_layer.update()
        before = b.matrix_world.copy()
        dg = bpy.context.evaluated_depsgraph_get()
        pe = pieces.evaluated_get(dg)
        loose_before = [tuple(pe.matrix_world @ v.co) for v in pe.data.vertices]
        lempty = parts.start_pivot(bpy.context, arm, loose[1])
        lempty.location = (2.5, 0.0, 3.5)
        parts.apply_pivot(bpy.context, lempty)
        bpy.context.view_layer.update()
        pe = pieces.evaluated_get(bpy.context.evaluated_depsgraph_get())
        loose_after = [tuple(pe.matrix_world @ v.co) for v in pe.data.vertices]
        assert len(loose_after) == len(loose_before) == 16 and all(_close(x, y) for x, y in zip(loose_before, loose_after)),             "Edit Pivot on a loose piece keeps its geometry in place"
        before = b.matrix_world.copy()
        empty = parts.start_pivot(bpy.context, arm, pids[1])
        empty.location = (0.5, 0.0, 1.0)
        parts.apply_pivot(bpy.context, empty)
        assert not [o for o in bpy.data.objects if o.get("bc_pivot_for")], "the pivot marker is removed"
        assert _close(arm.data.bones[build.bone_tags(arm)[(pids[1], "DEF")]].head_local, (0.5, 0, 1))
        bpy.context.view_layer.update()
        assert all(_close(b.matrix_world[r], before[r]) for r in range(4)), "Edit Pivot keeps the object in place"

        # Merge for VRChat, with the rig posed: geometry merges at rest; parts become loose pieces
        records.add(arm.data, M.Mechanism("h1", "HINGE", "Arm Hinge", parts=[pids[1]], min=-90, max=90))
        build.rebuild(arm)
        rig = records.to_model(arm)
        build.set_value(arm, rig, "h1", 30.0)
        stale = a.vertex_groups.new(name=build.bone_tags(arm)[(pids[1], "DEF")])      # a leftover weight to another part's bone
        stale.add(range(len(a.data.vertices)), 1.0, 'REPLACE')
        merged = parts.merge_for_vrchat(bpy.context, arm)
        a_group = build.bone_tags(arm)[(pids[0], "DEF")]
        w = {g.name: [] for g in merged.vertex_groups}
        for v in merged.data.vertices:
            for ge in v.groups:
                w[merged.vertex_groups[ge.group].name].append(v.index)
        assert len(w[a_group]) == 8 and not set(w[a_group]) & set(w[build.bone_tags(arm)[(pids[1], "DEF")]]),             "no vertex is weighted to two part bones"
        assert "Frame" not in bpy.data.objects or "Arm" not in bpy.data.objects
        for pid in pids:
            pg = records.find(arm.data, pid)
            assert (pg.kind, pg.object_name) == ("LOOSE", merged.name) and merged.vertex_groups.get(pg.vertex_group)
        assert arm.data.pose_position == 'POSE' and abs(build.get_value(arm, rig, "h1") - 30.0) < 1e-4
        assert records.to_model(arm).missing == set()

        # Remove Part: refused while used; allowed when unused, and its bones go
        try:
            parts.remove_part(arm, pids[1])
            raise AssertionError("a part used by a hinge must not be removed")
        except build.BuildError:
            pass
        parts.remove_part(arm, loose[0])
        assert (loose[0], "DEF") not in build.bone_tags(arm) and records.find(arm.data, loose[0]) is None
        _duplicates(build, records, parts)
    finally:
        boneforge.unregister()
    _copy_after_delete()
    _loose_siblings()
    print("PASS mechanisms parts: objects, loose pieces, apply transforms, edit pivot, merge for VRChat, remove, duplicates")
