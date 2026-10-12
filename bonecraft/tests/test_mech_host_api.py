"""In-Bforartists test: the host facts the Mechanisms recipes depend on (spec §14).

Pins, on Bforartists 5.2.0 (Blender 5.3 Alpha):
* layered actions: slots, layers, keyframe strips, channelbags; no legacy fcurves;
* Action constraint: action_slot assignment, AFTER_SPLIT adds on rotation and on
  location (AFTER_FULL does not), clamping past the slice, bone rename safety;
* Transform constraint: mix ADD, Gear 2:1, and the ±180° wrap (documented limit);
* simple-expression drivers reading a handle in TRANSFORM_SPACE stay continuous;
* Copy Transforms AFTER_SPLIT adds the handle on top of a driven channel.
"""
import math

import bpy

R = math.radians


def _armature(names):
    bpy.ops.object.mode_set(mode='OBJECT') if bpy.context.object and bpy.context.object.mode != 'OBJECT' else None
    bpy.ops.object.armature_add(enter_editmode=True)
    arm = bpy.context.object
    eb = arm.data.edit_bones
    root = eb[0]
    root.name = "root"
    for i, n in enumerate(names):
        b = eb.new(n)
        b.head, b.tail, b.parent = (i, 0, 0), (i, 1, 0), root
    bpy.ops.object.mode_set(mode='POSE')
    for pb in arm.pose.bones:
        pb.rotation_mode = 'XYZ'
    return arm


def _rotx(arm, name):
    bpy.context.view_layer.update()
    return round(math.degrees(arm.pose.bones[name].matrix.to_euler('XYZ').x), 3)


def _locy(arm, name):
    bpy.context.view_layer.update()
    pb = arm.pose.bones[name]
    return round((pb.bone.matrix_local.inverted() @ pb.matrix).translation.y, 4)


def _action(name, path, index, v1):
    act = bpy.data.actions.new(name)
    assert not hasattr(act, "fcurves"), "legacy Action.fcurves is back; revisit build.py"
    slot = act.slots.new(id_type='OBJECT', name="BoneCraft")
    bag = act.layers.new("BoneCraft").strips.new(type='KEYFRAME').channelbag(slot, ensure=True)
    fc = bag.fcurves.new(path, index=index)
    for f, v in ((0.0, 0.0), (10.0, v1)):
        fc.keyframe_points.insert(f, v).interpolation = 'LINEAR'
    return act, slot, bag


def _action_con(arm, owner, sub, channel, lo, hi, act, slot):
    c = arm.pose.bones[owner].constraints.new('ACTION')
    c.target, c.subtarget, c.target_space = arm, sub, 'LOCAL'
    c.transform_channel, c.min, c.max = channel, lo, hi
    c.frame_start, c.frame_end = 0, 10
    c.action = act
    c.action_slot = slot
    assert c.action_slot is not None and c.action_slot.identifier == slot.identifier
    return c


def _copy(arm, owner, sub):
    c = arm.pose.bones[owner].constraints.new('COPY_TRANSFORMS')
    c.target, c.subtarget = arm, sub
    c.target_space = c.owner_space = 'LOCAL'
    c.mix_mode = 'AFTER_SPLIT'
    return c


def run():
    bpy.ops.wm.read_factory_settings(use_empty=True)   # an empty scene: no names or modes left by earlier tests
    assert bpy.app.version[:2] == (5, 3), bpy.app.version_string
    arm = _armature(["CTRL-SEQ", "CTRL-B", "MCH-B", "CTRL-S", "MCH-S", "SRC", "MCH-T", "CTRL-A", "MCH-D"])
    pb = arm.pose.bones

    # Action constraint on a rotation channel, sequence slider 0..1 -> +90°
    _copy(arm, "MCH-B", "CTRL-B")
    act, slot, bag = _action("BC_probe_rot", 'pose.bones["MCH-B"].rotation_euler', 0, R(90))
    ac = _action_con(arm, "MCH-B", "CTRL-SEQ", 'LOCATION_Y', 0.0, 1.0, act, slot)
    ac.mix_mode = 'AFTER_SPLIT'
    pb["CTRL-B"].rotation_euler.x = R(10)
    pb["CTRL-SEQ"].location.y = 0.5
    assert _rotx(arm, "MCH-B") == 55.0, _rotx(arm, "MCH-B")
    pb["CTRL-SEQ"].location.y = 1.5
    assert _rotx(arm, "MCH-B") == 100.0, ("slider past the slice must hold the end value", _rotx(arm, "MCH-B"))
    pb["CTRL-SEQ"].location.y = 0.5
    arm.data.bones["MCH-B"].name = "MCH-B-renamed"
    assert [f.data_path for f in bag.fcurves] == ['pose.bones["MCH-B-renamed"].rotation_euler']
    assert _rotx(arm, "MCH-B-renamed") == 55.0

    # Action constraint on a location channel with the handle rotated: AFTER_SPLIT adds, AFTER_FULL does not
    _copy(arm, "MCH-S", "CTRL-S")
    act2, slot2, _ = _action("BC_probe_loc", 'pose.bones["MCH-S"].location', 1, 0.5)
    ac2 = _action_con(arm, "MCH-S", "CTRL-S", 'ROTATION_X', 0.0, R(90), act2, slot2)
    pb["CTRL-S"].location.y = 0.2
    pb["CTRL-S"].rotation_euler.x = R(90)
    ac2.mix_mode = 'AFTER_SPLIT'
    assert _locy(arm, "MCH-S") == 0.7, _locy(arm, "MCH-S")
    ac2.mix_mode = 'AFTER_FULL'
    assert _locy(arm, "MCH-S") != 0.7, "AFTER_FULL now adds location; the pin may be revisited"

    # Transform constraint: Gear 2:1, mix ADD, and the documented ±180° wrap
    tc = pb["MCH-T"].constraints.new('TRANSFORM')
    tc.target, tc.subtarget = arm, "SRC"
    tc.target_space = tc.owner_space = 'LOCAL'
    tc.map_from = tc.map_to = 'ROTATION'
    tc.from_min_x_rot, tc.from_max_x_rot = 0.0, 1.0
    tc.to_min_x_rot, tc.to_max_x_rot = 0.0, -0.5
    tc.mix_mode_rot = 'ADD'
    tc.use_motion_extrapolate = True
    pb["SRC"].rotation_euler.x = R(45)
    assert _rotx(arm, "MCH-T") == -22.5, _rotx(arm, "MCH-T")
    pb["SRC"].rotation_euler.x = R(190)
    assert _rotx(arm, "MCH-T") == 85.0, ("Transform input no longer wraps; D11 may be simplified", _rotx(arm, "MCH-T"))

    # Driver: simple expression, TRANSFORMS variable in TRANSFORM_SPACE, continuous past one turn
    assert "TRANSFORMS" in [i.identifier for i in bpy.types.DriverVariable.bl_rna.properties['type'].enum_items]
    fc = pb["MCH-D"].driver_add("rotation_euler", 0)
    drv = fc.driver
    drv.type = 'SCRIPTED'
    v = drv.variables.new()
    v.name, v.type = "bc0", 'TRANSFORMS'
    t = v.targets[0]
    t.id, t.bone_target, t.transform_type, t.transform_space = arm, "CTRL-A", 'ROT_X', 'TRANSFORM_SPACE'
    drv.expression = "bc0 * -0.5"
    assert drv.is_simple_expression
    _copy(arm, "MCH-D", "CTRL-B")                         # CTRL-B is at 10°
    for deg, want in ((400, 10 - 200), (720, 10 - 360)):
        pb["CTRL-A"].rotation_euler.x = R(deg)
        bpy.context.view_layer.update()
        assert round(math.degrees(pb["MCH-D"].rotation_euler.x), 3) == -deg / 2, deg
        got = _rotx(arm, "MCH-D") % 360
        assert abs(got - want % 360) < 1e-3, (deg, got, want % 360)
    print("PASS mechanisms host API: slots, AFTER_SPLIT, clamp, rename, Transform wrap, simple drivers")
