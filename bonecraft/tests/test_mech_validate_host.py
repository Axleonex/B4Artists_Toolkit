"""In-Bforartists test: Mechanisms checks reach the Rig Validator and the Task Board."""
import bpy

import boneforge


def _cube(name, loc):
    bpy.ops.mesh.primitive_cube_add(size=0.2, location=loc)
    bpy.context.object.name = name
    return bpy.context.object


def run():
    bpy.ops.wm.read_factory_settings(use_empty=True)   # an empty scene: no names or modes left by earlier tests
    boneforge.register()
    try:
        from boneforge.advanced_rigging import rig_validator                     # after register
        from boneforge.mechanisms import build, model as M, records, validate
        from boneforge.taskboard import tasks
        assert "mechanisms" in rig_validator._custom_checks
        _cube("Base", (0, 0, 0))
        _cube("Lid", (0, 0, 1))
        data = bpy.data.armatures.new("Check Rig")
        arm = bpy.data.objects.new("Check Rig", data)
        bpy.context.scene.collection.objects.link(arm)
        bpy.context.view_layer.objects.active = arm
        _cube("Crank", (2, 0, 0))
        _cube("Wheel", (3, 0, 0))
        for x in (M.Part("ba", "Base", object_name="Base"), M.Part("li", "Lid", object_name="Lid", parent="ba", pivot=(0, 0, 1)),
                  M.Part("cr", "Crank", object_name="Crank", pivot=(2, 0, 0)), M.Part("wh", "Wheel", object_name="Wheel", pivot=(3, 0, 0)),
                  M.Mechanism("h1", "HINGE", "Lid Hinge", parts=["li"], min=0, max=90),
                  M.Mechanism("hc", "HINGE", "Crank Hinge", parts=["cr"], min=-3600, max=3600),
                  M.Mechanism("hw", "HINGE", "Wheel Hinge", parts=["wh"], min=-3600, max=3600),
                  M.Mechanism("g1", "GEAR", "Crank Gear", source="hc", target="hw", teeth_source=10, teeth_target=20),
                  M.Sequence("q1", "Open", steps=[M.Step("h1", 90.0, 0.0, 1.0, "LINEAR")])):
            records.add(data, x)
        build.rebuild(arm)
        assert validate.rig_checks(arm) == []
        # a clean rig (hyphenated CTRL-/MCH-/DEF- names, a no-Python gear driver) shows no validator errors
        assert any(fc.driver.type == 'SCRIPTED' for fc in arm.animation_data.drivers), "the free gear uses a driver"
        noisy = [(r.check_name, r.status, r.message) for r in rig_validator.run_all_checks(arm) if r.status in ("fail", "warn")]
        assert not [n for n in noisy if n[0] in ("naming", "drivers")], noisy
        assert not [n for n in noisy if n[1] == "fail"], noisy
        assert "validator_errors" not in [t.task_id for t in tasks.check_rig_validator(arm)], noisy
        # still left (needs build.py, outside this change): the root bone is in no bone collection
        assert all(n[0] == "collections" and "'root'" in n[2] for n in noisy), noisy

        # saved and reloaded with Auto Run Python Scripts off, the rig still moves (spec §6, §10.4)
        import math, os, tempfile
        path = os.path.join(tempfile.gettempdir(), "bc_mech_reload_test.blend")
        bpy.ops.wm.save_as_mainfile(filepath=path, check_existing=False)
        bpy.ops.wm.open_mainfile(filepath=path, load_ui=False)
        os.remove(path)
        assert not bpy.context.preferences.filepaths.use_scripts_auto_execute
        arm = bpy.data.objects["Check Rig"]
        data = arm.data
        rig = records.to_model(arm)
        build.set_value(arm, rig, "hc", 400.0)                                 # free gear: a no-Python driver
        build.set_value(arm, rig, "q1", 1.0)                                   # sequence: an Action constraint
        bpy.context.view_layer.update()
        tags = build.bone_tags(arm)
        assert abs(math.degrees(arm.pose.bones[tags[("wh", "MCH")]].rotation_euler.x) + 200.0) < 1e-3
        lid = arm.pose.bones[tags[("li", "DEF")]]
        assert abs(math.degrees((lid.bone.matrix_local.inverted() @ lid.matrix).to_euler('XYZ').x) - 90.0) < 1e-2
        build.set_value(arm, rig, "hc", 0.0)
        build.set_value(arm, rig, "q1", 0.0)
        assert [r.status for r in validate.check_mechanisms(arm)] == ["pass"]

        tags = build.bone_tags(arm)
        dfm = arm.pose.bones[tags[("li", "DEF")]]
        dfm.constraints.new('COPY_SCALE').name = "My Scale"                      # the rigger moves a DEF bone
        fc = arm.driver_add('pose.bones["%s"].scale' % tags[("ba", "DEF")], 0)
        fc.driver.type = 'SCRIPTED'
        fc.driver.expression = "len('ab')"                                       # needs Python
        found = validate.rig_checks(arm)
        assert any(r.status == "warn" and "len('ab')" in r.message for r in rig_validator.check_drivers(arm)),             "a driver that needs Python still warns in the drivers check"
        assert any(s == "warn" and "My Scale" in m for s, m, b in found), found
        assert any(s == "fail" and "needs Python" in m for s, m, b in found), found
        assert any(s == "warn" and "drivers BoneCraft did not add" in m for s, m, b in found), found
        bpy.data.objects.remove(bpy.data.objects["Lid"])
        assert any(s == "fail" and "Part 'Lid' is missing" in m for s, m, b in validate.rig_checks(arm))

        names = [r.check_name for r in rig_validator.run_all_checks(arm)]
        assert "mechanisms" in names, "the Rig Validator runs the Mechanisms checks"
        board = tasks.check_rig_validator(arm)
        assert [t.task_id for t in board] == ["validator_errors"], [t.task_id for t in board]
        assert validate.rig_checks(bpy.data.objects.new("Bare", bpy.data.armatures.new("Bare"))) == []
        other = bpy.data.objects.new("Other", bpy.data.armatures.new("Other"))   # no records: its Python driver is not ours
        bpy.context.scene.collection.objects.link(other)
        ofc = other.driver_add("location", 0)
        ofc.driver.type = 'SCRIPTED'
        ofc.driver.expression = "len('ab')"
        assert validate.rig_checks(other) == [] and validate.check_mechanisms(other) == []
        bpy.context.view_layer.update()
        warn_only = tasks.check_rig_validator(other)                            # warnings alone reach the Task Board
        assert [t.task_id for t in warn_only] == ["validator_warnings"], [t.task_id for t in warn_only]
        names_arm = bpy.data.objects.new("Names", bpy.data.armatures.new("Names"))
        bpy.context.scene.collection.objects.link(names_arm)
        bpy.context.view_layer.objects.active = names_arm
        bpy.ops.object.mode_set(mode='EDIT')
        for n in ("Bad Name!", "DEF-lid.L", "MCH-lip_upper"):
            eb = names_arm.data.edit_bones.new(n)
            eb.tail = (0, 0, 1)
        bpy.ops.object.mode_set(mode='OBJECT')
        bad = {r.affected_bone for r in rig_validator.check_naming(names_arm) if r.status == "fail"}
        assert bad == {"Bad Name!"}, bad
    finally:
        boneforge.unregister()
    from boneforge.advanced_rigging import rig_validator
    assert "mechanisms" not in rig_validator._custom_checks, "unregister removes the check"
    print("PASS mechanisms validator: reload with scripts off, plan, missing parts, DEF bones moved by hand, Python drivers, Task Board")
