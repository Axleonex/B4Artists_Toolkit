# bonecraft/tests/test_mech_records_host.py
"""In-Bforartists test: Mechanisms records on the armature, edit hooks, active rig."""
import dataclasses

import bpy

import boneforge


def _eq(x, y):
    if isinstance(x, (list, tuple)):
        return len(x) == len(y) and all(_eq(a, b) for a, b in zip(x, y))
    if isinstance(x, float) or isinstance(y, float):
        return abs(x - y) < 1e-6
    return x == y


def _same(a, b):
    for f in dataclasses.fields(a):
        x, y = getattr(a, f.name), getattr(b, f.name)
        if f.name == "steps":
            assert len(x) == len(y) and all(_same(p, q) for p, q in zip(x, y)), f.name
        else:
            assert _eq(x, y), (type(a).__name__, f.name, x, y)
    return True


def run():
    bpy.ops.wm.read_factory_settings(use_empty=True)   # an empty scene: no names or modes left by earlier tests
    boneforge.register()
    try:
        from boneforge.core.tool_registry import get_registry          # after register: modules may reload
        from boneforge.mechanisms import model as M, records
        assert get_registry().is_enabled("mechanisms")
        assert hasattr(bpy.types.Armature, "bonecraft_mech")
        bpy.ops.object.armature_add()
        arm = bpy.context.object
        assert not records.has_records(arm.data) and records.active_rig(bpy.context) is None
        bpy.ops.mesh.primitive_cube_add()
        cube = bpy.context.object

        p = M.Part("p1", "Blade", object_name=cube.name, pivot=(0.0, 0.0, 1.0), size=0.25)
        q = M.Part("p2", "Cover", object_name=cube.name, parent="p1")
        h = M.Mechanism("m1", "HINGE", "Blade Hinge", parts=["p1"], min=-10.0, max=90.0)
        t = M.Mechanism("t1", "TELESCOPE", "Mast", parts=["p1", "p2"], axis=(0.0, 0.0, 1.0), length=0.75, shares=[0.25, 0.5])
        s = M.Sequence("s1", "Fold", steps=[M.Step("m1", 90.0, 0.0, 0.5, "LINEAR")])
        hits = []
        hook = lambda pg, ctx: hits.append(records.record_id(pg))
        records.EDIT_HOOKS.append(hook)
        try:
            for x in (p, q, h, t, s):
                records.add(arm.data, x)
            assert hits == [], "writes inside quiet() must not run the edit hooks"
            assert records.has_records(arm.data)
            rig = records.to_model(arm)
            assert [x.id for x in rig.parts] == ["p1", "p2"] and _same(rig.parts[0], p) and _same(rig.parts[1], q)
            assert _same(rig.mechanisms[0], h) and _same(rig.mechanisms[1], t)
            assert rig.sequences[0].name == "Fold" and _same(rig.sequences[0].steps[0], s.steps[0])
            assert rig.missing == set()
            assert records.taken_ids(arm.data) == {"p1", "p2", "m1", "t1", "s1"}

            records.find(arm.data, "m1").max = 45.0
            records.find(arm.data, "s1").steps[0].value = 30.0
            assert hits == ["m1", "s1"], hits

            records.find(arm.data, "p2").object_name = "No Such Object"
            assert records.to_model(arm).missing == {"p2"}
            with records.quiet():
                pg = records.find(arm.data, "p2")
                pg.kind, pg.object_name, pg.vertex_group = "LOOSE", cube.name, "DEF-Cover"
            assert records.to_model(arm).missing == {"p2"}, "a loose part needs its vertex group"
            cube.vertex_groups.new(name="DEF-Cover")
            assert records.to_model(arm).missing == set()

            cube.parent = arm
            bpy.context.view_layer.objects.active = cube
            assert records.active_rig(bpy.context) == arm and records.owner(arm.data) == arm
            records.mark(arm.data, built={"m1"}, skipped={"p2": "Part 'Cover' is missing"}, held={})
            assert records.built_ids(arm.data) == {"m1"}
            assert (records.find(arm.data, "p2").state, records.find(arm.data, "p2").message) == ("MISSING_PART", "Part 'Cover' is missing")
            from boneforge.mechanisms import planner
            with records.quiet():
                records.find(arm.data, "t1").shares = "0.5, abc"          # a typo in Shares
            rig = records.to_model(arm)                                    # reading the record does not raise...
            assert len(rig.mech("t1").shares) == 2 and rig.mech("t1").shares[1] != rig.mech("t1").shares[1], "abc reads as NaN"
            try:
                planner.plan_rig(rig)
                raise AssertionError("a typo in Shares must be refused by the plan")
            except planner.PlanError as exc:                               # ...the plan says what is wrong
                assert "shares must add up" in str(exc), exc
            assert records.remove(arm.data, "t1") and records.find(arm.data, "t1") is None
            assert not records.remove(arm.data, "t1")
        finally:
            records.EDIT_HOOKS.remove(hook)
    finally:
        boneforge.unregister()
    assert not hasattr(bpy.types.Armature, "bonecraft_mech")
    print("PASS mechanisms records: round trip, edit hooks, missing parts, active rig, tool on by default")
