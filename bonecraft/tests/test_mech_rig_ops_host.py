"""In-Bforartists test: rig_ops drivers in Transform Space and generated actions."""
import math

import bpy

import boneforge


def run():
    bpy.ops.wm.read_factory_settings(use_empty=True)   # an empty scene: no names or modes left by earlier tests
    boneforge.register()
    try:
        from boneforge.core import rig_ops                     # after register: modules may reload
        bpy.ops.object.armature_add(enter_editmode=True)
        arm = bpy.context.object
        eb = arm.data.edit_bones
        eb[0].name = "SRC"
        b = eb.new("DST")
        b.head, b.tail = (1, 0, 0), (1, 1, 0)
        bpy.ops.object.mode_set(mode='POSE')
        for pb in arm.pose.bones:
            pb.rotation_mode = 'XYZ'

        fc = rig_ops.add_driver(arm, 'pose.bones["DST"].rotation_euler', 0, "bc0 * -0.5",
                                [dict(name="bc0", id=arm, bone="SRC", transform_type="ROT_X", space="TRANSFORM_SPACE")])
        var = fc.driver.variables[0]
        assert var.type == "TRANSFORMS" and var.targets[0].transform_space == "TRANSFORM_SPACE"
        assert fc.driver.is_simple_expression
        arm.pose.bones["SRC"].rotation_euler.x = math.radians(400)
        bpy.context.view_layer.update()
        assert round(math.degrees(arm.pose.bones["DST"].rotation_euler.x), 3) == -200.0

        keys = [(0.0, 0.0, "SINE", "EASE_IN_OUT"), (10.0, 1.0, "LINEAR", "")]
        path = 'pose.bones["DST"].location'
        act, slot = rig_ops.ensure_action("BC test", "m1", "m1:s0", path, 1, keys)
        assert act["bc_mech_id"] == "m1" and act["bc_key"] == "m1:s0" and slot.target_id_type == "OBJECT"

        def action_con(name):
            con = arm.pose.bones["DST"].constraints.new('ACTION')
            con.name, con.target, con.subtarget, con.transform_channel = name, arm, "SRC", 'LOCATION_Y'
            con.target_space, con.min, con.max, con.frame_start, con.frame_end = 'LOCAL', 0.0, 1.0, 0, 10
            con.mix_mode = 'AFTER_SPLIT'
            return con

        con = action_con("BC·m1·s0")
        rig_ops.assign_action(con, act, slot)
        assert con.action == act and con.action_slot.identifier == slot.identifier

        before = len(bpy.data.actions)
        act2, slot2 = rig_ops.ensure_action("BC test renamed", "m1", "m1:s0", path, 1,
                                            [(0.0, 0.0, "LINEAR", ""), (10.0, 2.0, "LINEAR", "")], current=con.action)
        assert act2 == act and len(bpy.data.actions) == before and act.name == "BC test renamed", "refilled in place"
        (fcu,) = act.layers[0].strips[0].channelbag(slot2).fcurves
        assert [round(k.co[1], 6) for k in fcu.keyframe_points] == [0.0, 2.0]

        # a duplicated rig shares the action: refilling for one rig must not touch the other's
        twin = action_con("twin")
        rig_ops.assign_action(twin, act, slot)
        assert act.users == 2
        act3, slot3 = rig_ops.ensure_action("BC test", "m1", "m1:s0", path, 1, keys, current=con.action)
        assert act3 != act and act3["bc_key"] == "m1:s0", "a shared action is never refilled"
        rig_ops.assign_action(con, act3, slot3)
        assert act.users == 1 and twin.action == act

        # releasing removes an action only once nothing uses it
        assert not rig_ops.release_action(act)
        arm.pose.bones["DST"].constraints.remove(twin)
        assert rig_ops.release_action(act) and "BC test renamed" not in bpy.data.actions
        assert not rig_ops.release_action(None)
    finally:
        boneforge.unregister()
    print("PASS mechanisms rig_ops: Transform-Space drivers, per-rig actions refilled in place, slots")
