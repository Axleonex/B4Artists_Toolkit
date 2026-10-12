# bonecraft/tests/test_mech_build_host.py
"""In-Bforartists test: Mechanisms build in place, by tag (spec §4.5, §5.5, §8, §10)."""
import math

import bpy

import boneforge

R = math.radians


def _cube(name, loc):
    bpy.ops.mesh.primitive_cube_add(size=0.2, location=loc)
    ob = bpy.context.object
    ob.name = name
    return ob


def _rel_rot(arm, name):
    bpy.context.view_layer.update()
    pb = arm.pose.bones[name]
    return math.degrees((pb.bone.matrix_local.inverted() @ pb.matrix).to_euler('XYZ').x)


def _bound_part(parts):
    """One bound OBJECT part in the (empty) scene: (rig, part id, its object)."""
    lid = _cube("Lid", (0, 0, 0))
    rig, (pid,), _ = parts.add_parts_from_selection(bpy.context)
    return rig, pid, lid


def _failed_delete(build, arm, rid):
    """Delete ``rid`` with its rebuild forced to raise once: the record comes back."""
    real_rebuild = build.rebuild
    def boom(*args, **kwargs):
        raise build.BuildError("forced")
    build.rebuild = boom
    try:
        build.delete(arm, rid)
        raise AssertionError("expected BuildError")
    except build.BuildError as exc:
        assert "forced" in str(exc), exc
    finally:
        build.rebuild = real_rebuild


def _delete_keeps_reference():
    """A failed Delete of a bound part puts back its object reference."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    boneforge.register()
    try:
        from boneforge.mechanisms import build, parts, records       # after register
        rig, pid, lid = _bound_part(parts)
        assert records.find(rig.data, pid).is_property_set("object_ref")
        _failed_delete(build, rig, pid)
        pg = records.find(rig.data, pid)
        assert pg.is_property_set("object_ref") and pg.object_ref == lid, "the reference comes back"
    finally:
        boneforge.unregister()


def _delete_keeps_cleared_reference():
    """A failed Delete of a part whose object was deleted: the part stays missing, its tagged copy is not adopted."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    boneforge.register()
    try:
        from boneforge.mechanisms import build, parts, records       # after register
        rig, pid, lid = _bound_part(parts)
        copy = lid.copy()                                          # tagged like the original
        bpy.context.scene.collection.objects.link(copy)
        bpy.ops.object.select_all(action='DESELECT')
        lid.select_set(True)
        bpy.context.view_layer.objects.active = lid
        bpy.ops.object.delete()
        records.refresh_object_names(rig.data)                     # clears the reference: set, but None
        pg = records.find(rig.data, pid)
        assert pg.is_property_set("object_ref") and pg.object_ref is None and records.part_object(pg) is None
        _failed_delete(build, rig, pid)
        pg = records.find(rig.data, pid)
        assert pg.is_property_set("object_ref") and records.part_object(pg) is None, "the copy does not take over"
    finally:
        boneforge.unregister()


def _delete_keeps_unset_reference():
    """A failed Delete of an older record without a reference leaves it without one."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    boneforge.register()
    try:
        from boneforge.mechanisms import build, parts, records       # after register
        rig, pid, _ = _bound_part(parts)
        records.find(rig.data, pid).property_unset("object_ref")
        _failed_delete(build, rig, pid)
        assert not records.find(rig.data, pid).is_property_set("object_ref"), "still unset"
    finally:
        boneforge.unregister()


def run():
    bpy.ops.wm.read_factory_settings(use_empty=True)   # an empty scene: no names or modes left by earlier tests
    boneforge.register()
    try:
        from boneforge.mechanisms import build, model as M, planner, records       # after register
        from boneforge.mechanisms.recipes import sequence as S
        for n, loc in (("Base", (0, 0, 0)), ("Blade", (0, 0, 1)), ("GearA", (1, 0, 0)),
                       ("GearB", (2, 0, 0)), ("Crank", (3, 0, 0)), ("Wheel", (4, 0, 0))):
            _cube(n, loc)
        data = bpy.data.armatures.new("Mech Test")
        arm = bpy.data.objects.new("Mech Test", data)
        bpy.context.scene.collection.objects.link(arm)
        bpy.context.view_layer.objects.active = arm
        parts = [M.Part("base", "Base", object_name="Base"),
                 M.Part("blade", "Blade", object_name="Blade", parent="base", pivot=(0, 0, 1)),
                 M.Part("ga", "GearA", object_name="GearA", pivot=(1, 0, 0)),
                 M.Part("gb", "GearB", object_name="GearB", pivot=(2, 0, 0)),
                 M.Part("cr", "Crank", object_name="Crank", pivot=(3, 0, 0)),
                 M.Part("wh", "Wheel", object_name="Wheel", pivot=(4, 0, 0))]
        mechs = [M.Mechanism("h1", "HINGE", "Blade Hinge", parts=["blade"], min=-170, max=170),
                 M.Mechanism("ha", "HINGE", "A Hinge", parts=["ga"], min=-90, max=90),
                 M.Mechanism("hb", "HINGE", "B Hinge", parts=["gb"], min=-90, max=90),
                 M.Mechanism("g1", "GEAR", "AB Gear", source="ha", target="hb", teeth_source=20, teeth_target=40),
                 M.Mechanism("hc", "HINGE", "Crank Hinge", parts=["cr"], min=-3600, max=3600),
                 M.Mechanism("hw", "HINGE", "Wheel Hinge", parts=["wh"], min=-3600, max=3600),
                 M.Mechanism("g2", "GEAR", "Crank Gear", source="hc", target="hw", ratio=1.0, teeth_source=10, teeth_target=20)]
        seq = M.Sequence("q1", "Unfold", steps=[M.Step("h1", 90.0, 0.0, 0.5, "EASE_IN_OUT")])
        for x in parts + mechs + [seq]:
            records.add(data, x)
        plan, held = build.rebuild(arm)
        assert held == {}, held
        tags = build.bone_tags(arm)
        n_bones = len(data.bones)
        pb = lambda rid, role: arm.pose.bones[tags[(rid, role)]]
        assert all(r.state == "OK" and r.built for r in records._all(data.bonecraft_mech)), \
            [(r.id, r.state, r.message) for r in records._all(data.bonecraft_mech)]

        # Hinge 45° -> DEF 45°
        rig = records.to_model(arm)
        build.set_value(arm, rig, "h1", 45.0)
        assert abs(_rel_rot(arm, tags[("blade", "DEF")]) - 45.0) < 1e-3
        # Gear 2:1 (Transform kind): source 45° -> target -22.5°
        build.set_value(arm, rig, "ha", 45.0)
        assert abs(_rel_rot(arm, tags[("gb", "DEF")]) + 22.5) < 1e-3
        # Free crank (driver kind): 400° -> wheel -200° continuously; no Python
        build.set_value(arm, rig, "hc", 400.0)
        bpy.context.view_layer.update()
        assert abs(math.degrees(pb("wh", "MCH").rotation_euler.x) + 200.0) < 1e-3
        drivers = arm.animation_data.drivers
        assert len(drivers) == 1 and all(fc.driver.is_simple_expression for fc in drivers)
        # Sequence slider 0.4 -> the eased value the planner computes, on top of the handle
        build.set_value(arm, rig, "h1", 0.0)
        build.set_value(arm, rig, "q1", 0.4)
        want = S.value(rig, rig.sequences[0], "h1", 0.4)
        assert abs(_rel_rot(arm, tags[("blade", "DEF")]) - want) < 1e-2, (_rel_rot(arm, tags[("blade", "DEF")]), want)
        build.set_value(arm, rig, "q1", 0.0)

        # A rigger constraint between ours survives a rebuild and ends up below ours
        mch = pb("blade", "MCH")
        mine = mch.constraints.new('COPY_SCALE')
        mine.name = "My Scale"
        mch.constraints.move(len(mch.constraints) - 1, 0)
        build.rebuild(arm, {"h1"})
        names = [c.name for c in mch.constraints]
        assert "My Scale" in names and names.index("My Scale") > max(i for i, n in enumerate(names) if n.startswith("BC·")), names

        # Renamed bones are found by tag: no duplicates, still working
        for rid, role, new in (("h1", "CTRL", "Blade Handle"), ("blade", "MCH", "Blade Mech"), ("q1", "CTRL", "Slider"), ("wh", "MCH", "Wheel Mech")):
            data.bones[tags[(rid, role)]].name = new
        build.rebuild(arm)
        assert len(data.bones) == n_bones, (len(data.bones), n_bones)
        tags = build.bone_tags(arm)
        assert tags[("h1", "CTRL")] == "Blade Handle" and tags[("q1", "CTRL")] == "Slider"
        build.set_value(arm, rig, "q1", 0.4)
        assert abs(_rel_rot(arm, tags[("blade", "DEF")]) - want) < 1e-2, "the action follows the renamed bone"
        build.set_value(arm, rig, "q1", 0.0)
        bpy.context.view_layer.update()
        assert abs(math.degrees(pb("wh", "MCH").rotation_euler.x) + 200.0) < 1e-3, "the driver follows the renamed bone"

        # Value edits update in place; a hand edit holds the record until Keep mine / Restore
        lim = pb("blade", "MCH").constraints["BC·h1·limit"]
        records.find(data, "h1").max = 120.0                         # edit hook -> rebuild
        assert abs(lim.max_x - R(120)) < 1e-6 and pb("blade", "MCH").constraints["BC·h1·limit"] == lim
        lim.max_x = R(100)                                           # by hand
        records.find(data, "h1").min = -20.0
        rec = records.find(data, "h1")
        assert rec.state == "CHANGED_BY_HAND" and "max_x" in rec.message, (rec.state, rec.message)
        assert abs(lim.min_x - R(-170)) < 1e-6, "a held record is not rebuilt"
        build.restore(arm, "h1")
        assert abs(lim.max_x - R(120)) < 1e-6 and abs(lim.min_x - R(-20)) < 1e-6 and rec.state == "OK"
        lim.max_x = R(100)
        build.keep_mine(arm, "h1")
        assert abs(rec.max - 100.0) < 1e-3 and rec.state == "OK"
        assert abs(pb("h1", "CTRL").constraints["BC·h1·handle_limit"].max_x - R(100)) < 1e-6

        # A missing part: its record waits, its rig stays, everything else builds
        bpy.data.objects.remove(bpy.data.objects["Wheel"])
        build.rebuild(arm)
        assert records.find(data, "wh").state == "MISSING_PART" and records.find(data, "g2").state == "MISSING_PART"
        assert ("wh", "MCH") in build.bone_tags(arm) and records.find(data, "h1").state == "OK"

        # A failed build puts every change back: new things go, changed things return to their old values
        def state():
            bones = {b.name: (tuple(b.head_local), tuple(b.tail_local), b.parent.name if b.parent else None) for b in data.bones}
            cons = {(p.name, c.name): tuple(getattr(c, k) for k in ("min_x", "max_x") if hasattr(c, k))
                    for p in arm.pose.bones for c in p.constraints}
            colls = sorted((c.name, c.get("bc_mech_role")) for c in data.collections_all)
            return bones, cons, [c.name for c in pb("blade", "MCH").constraints], colls, sorted(o.name for o in bpy.data.objects)
        old_def = next(c for c in data.collections_all if c.get("bc_mech_role") == "DEF")
        old_def.name = "Old DEF"                                   # untagged: the build will make a new one
        del old_def["bc_mech_role"]
        before = state()
        records.add(data, M.Part("lid", "Lid", object_name="Base", pivot=(0, 1, 0)))
        with records.quiet():
            records.find(data, "h1").max = 150.0                  # an existing limit will change...
            records.find(data, "blade").pivot = (0, 0, 1.5)       # ...and existing bones will move
            records.find(data, "h1").handle_widget = "gear"       # ...and a new widget object appears
        bad = planner.plan_rig(records.to_model(arm))
        last = [c for c in bad.build.constraints if c.tag in ("lid", "h1", "blade")][-1]
        last.params["no_such_setting"] = 1                         # ...before a later setting fails
        try:
            build.apply(arm, bad, {"lid", "h1", "blade"})
            raise AssertionError("expected BuildError")
        except build.BuildError as exc:
            assert "put back" in str(exc)
        assert state() == before, "every bone, constraint value, order, collection and widget is back"
        records.remove(data, "lid")
        with records.quiet():
            records.find(data, "h1").max = 100.0
            records.find(data, "blade").pivot = (0, 0, 1)
            records.find(data, "h1").handle_widget = ""
        old_def.name, old_def["bc_mech_role"] = "Mechanism DEF", "DEF"

        # A bone deleted by hand holds its record; Restore rebuilds it
        with build._edit(arm) as ebs:
            ebs.remove(ebs[build.bone_tags(arm)[("h1", "CTRL")]])
        records.find(data, "h1").min = -30.0
        assert records.find(data, "h1").state == "CHANGED_BY_HAND" and "bone removed" in records.find(data, "h1").message
        build.restore(arm, "h1")
        assert ("h1", "CTRL") in build.bone_tags(arm) and records.find(data, "h1").state == "OK"

        # A channel the rigger drives by hand holds the gear's part before anything changes
        _cube("Wheel", (4, 0, 0))                                  # the missing part comes back
        fc = arm.animation_data.drivers[0]
        fc.driver.variables[0].name = "mine"
        fc.driver.expression = "mine * -0.5"
        records.find(data, "g2").ratio = 3.0
        assert records.find(data, "wh").state == "CHANGED_BY_HAND" and "driven by hand" in records.find(data, "wh").message
        assert fc.driver.expression == "mine * -0.5", "the rigger's driver is untouched"
        fc.driver.variables[0].name = "bc0"
        fc.driver.expression = "bc0 * -0.5"
        build.restore(arm, "wh")

        # A reshaped curve is never overwritten: a record that wants a different curve is held
        step_con = pb("blade", "MCH").constraints["BC·q1·s0"]
        act = step_con.action
        twin = pb("blade", "DEF").constraints.new('ACTION')       # the rigger shares the action
        twin.name, twin.action = "My Twin", act
        bag = act.layers[0].strips[0].channelbag(act.slots[0])
        bag.fcurves[0].keyframe_points.insert(5.0, R(70)).interpolation = 'LINEAR'     # the rigger reshapes it
        build.rebuild(arm, {"q1"})
        assert step_con.action == act and len(bag.fcurves[0].keyframe_points) == 3, "unchanged record: the curve stays"
        records.find(data, "q1").steps[0].value = 80.0
        assert records.find(data, "q1").state == "CHANGED_BY_HAND" and "curve reshaped" in records.find(data, "q1").message
        assert act.users == 2, "shared, and still held: a reshaped curve is never overwritten"
        real_rebuild = build.rebuild

        def _failing_rebuild(*_a, **_k):
            raise build.BuildError("rebuild failed")

        def _restore_fails():
            build.rebuild = _failing_rebuild
            try:
                build.restore(arm, "q1")
                raise AssertionError("the rebuild's error reaches the caller")
            except build.BuildError as exc:
                assert "rebuild failed" in str(exc)
            finally:
                build.rebuild = real_rebuild
        _restore_fails()
        assert "bc_regen" not in act and len(bag.fcurves[0].keyframe_points) == 3 and step_con.action == act,             "a failed Restore leaves no regenerate flag behind"
        assert records.find(data, "q1").state == "CHANGED_BY_HAND"
        build.rebuild(arm, {"q1"})
        assert step_con.action == act and len(bag.fcurves[0].keyframe_points) == 3             and records.find(data, "q1").state == "CHANGED_BY_HAND", "so the next rebuild still keeps the reshaped curve"
        build.keep_mine(arm, "q1")
        assert step_con.action == act and records.find(data, "q1").state == "OK", "Keep mine pins the reshaped curve"
        _restore_fails()
        assert act.get("bc_pinned") and "bc_regen" not in act, "a failed Restore puts the pin back"
        pb("blade", "DEF").constraints.remove(twin)
        build.restore(arm, "q1")
        assert step_con.action != act and len(step_con.action.layers[0].strips[0].channelbag(step_con.action.slots[0]).fcurves[0].keyframe_points) == 2
        assert len([a for a in bpy.data.actions if a.get("bc_mech_id") == "q1"]) == 1, "the replaced action is released"
        assert not [o for o in bpy.data.objects if o.name.startswith("WGT-") and "." in o.name], "no widget copies"

        # Detach keeps the rig as ordinary bones and constraints; Delete removes everything tagged
        try:
            build.detach(arm, "ha")
            raise AssertionError("a joint a Gear Link uses must not be detached")
        except build.BuildError as exc:
            assert "AB Gear" in str(exc)
        build.detach(arm, "g1")
        assert any(c.name.startswith("gear (AB Gear") for c in pb("gb", "MCH").constraints)
        build.detach(arm, "ha")
        assert records.find(data, "ha") is None and ("ha", "CTRL") not in build.bone_tags(arm)
        assert not any(c.name.startswith("BC·ha·") for p in arm.pose.bones for c in p.constraints)
        assert any(c.name.startswith("copy (A Hinge") for c in pb("ga", "MCH").constraints)
        n_actions = len([a for a in bpy.data.actions if a.get("bc_mech_id") == "q1"])
        assert n_actions == 1
        build.delete(arm, "q1")
        assert ("q1", "CTRL") not in build.bone_tags(arm) and not [a for a in bpy.data.actions if a.get("bc_mech_id") == "q1"]
        try:
            build.delete(arm, "blade")
            raise AssertionError("a part in use must not be deleted")
        except build.BuildError as exc:
            assert "Blade Hinge" in str(exc)

        # A hold carries to records that plan items on the held record's bones
        with build._edit(arm) as ebs:
            ebs.remove(ebs[build.bone_tags(arm)[("blade", "MCH")]])
        records.find(data, "h1").min = -25.0                       # h1 uses blade's MCH bone: no KeyError, both held
        h1r, blr = records.find(data, "h1"), records.find(data, "blade")
        assert data.bonecraft_mech.last_error == "", data.bonecraft_mech.last_error
        assert h1r.state == "CHANGED_BY_HAND" and blr.state == "CHANGED_BY_HAND", (h1r.state, blr.state)
        assert "bone removed" in blr.message and "uses Blade" in h1r.message, (blr.message, h1r.message)
        assert ("blade", "MCH") not in build.bone_tags(arm), "a held record is not rebuilt"
        build.restore(arm, "blade")
        assert ("blade", "MCH") in build.bone_tags(arm) and h1r.state == "OK" and blr.state == "OK", (h1r.state, blr.state)
        assert abs(h1r.min + 25.0) < 1e-6 and data.bonecraft_mech.last_error == ""
        tags = build.bone_tags(arm)                                # the restored bone has a new name

        # A delete whose rebuild fails keeps the record, so it can be retried
        real_rebuild = build.rebuild
        def boom(*args, **kwargs):
            raise build.BuildError("forced")
        h1 = records.find(data, "h1")
        fields = (h1.name, h1.type, tuple(h1.parts), h1.min, h1.max)
        place = [m.id for m in data.bonecraft_mech.mechanisms].index("h1")
        kept = (h1.built, h1.snapshot, h1.state, h1.message)
        assert h1.built and h1.snapshot, "h1 was built"
        build.rebuild = boom
        try:
            build.delete(arm, "h1")
            raise AssertionError("expected BuildError")
        except build.BuildError as exc:
            assert "forced" in str(exc), exc
        finally:
            build.rebuild = real_rebuild
        h1 = records.find(data, "h1")
        assert h1 is not None and (h1.name, h1.type, tuple(h1.parts), h1.min, h1.max) == fields
        assert (h1.built, h1.snapshot, h1.state, h1.message) == kept, "built, snapshot and state come back"
        assert [m.id for m in data.bonecraft_mech.mechanisms].index("h1") == place, "and so does its place in the list"
        build.delete(arm, "h1")                                    # the retry works
        assert records.find(data, "h1") is None and ("h1", "CTRL") not in build.bone_tags(arm)

        # Every requested record held: nothing changes, the root bone included
        plan = planner.plan_rig(records.to_model(arm))
        root = build.resolve_names(arm, plan)[planner.ROOT]
        with build._edit(arm) as ebs:
            ebs.remove(ebs[root])
        n_now = len(data.bones)
        held = build.apply(arm, plan, {"hw"}, check={"hw": {"@bones": ["nosuch:CTRL"]}})
        assert list(held) == ["hw"] and len(data.bones) == n_now and root not in data.bones, held
        assert build.apply(arm, plan, set()) == {} and len(data.bones) == n_now and root not in data.bones
    finally:
        boneforge.unregister()
    _delete_keeps_reference()
    _delete_keeps_cleared_reference()
    _delete_keeps_unset_reference()
    print("PASS mechanisms build: hinge, gears (both kinds), sequence, rigger additions, renames, "
          "hand edits, missing parts, rollback, detach, delete (keeping a part's object reference)")
