"""In-Bforartists test: Test sweeps a mechanism through its range and back, keys nothing, restores the pose."""
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
        from boneforge.mechanisms import build, model as M, records, test_sweep        # after register
        assert test_sweep.sweep_values(0.0, 90.0, 3) == [0.0, 30.0, 60.0, 90.0, 60.0, 30.0, 0.0]
        for n, loc in (("Frame", (0, 0, 0)), ("Arm", (0, 0, 1)), ("Cyl", (1, 0, 0)), ("Rod", (1, 0, 1)), ("Spin", (2, 0, 0))):
            _cube(n, loc)
        data = bpy.data.armatures.new("Test Rig")
        arm = bpy.data.objects.new("Test Rig", data)
        bpy.context.scene.collection.objects.link(arm)
        bpy.context.view_layer.objects.active = arm
        for x in (M.Part("fr", "Frame", object_name="Frame"),
                  M.Part("ar", "Arm", object_name="Arm", parent="fr", pivot=(0, 0, 1)),
                  M.Part("cy", "Cyl", object_name="Cyl", parent="fr", pivot=(1, 0, 0)),
                  M.Part("ro", "Rod", object_name="Rod", parent="ar", pivot=(1, 0, 1)),
                  M.Part("sp", "Spin", object_name="Spin", pivot=(2, 0, 0)),
                  M.Mechanism("h1", "HINGE", "Arm Hinge", parts=["ar"], min=-20, max=80),
                  M.Mechanism("hs", "HINGE", "Spin Hinge", parts=["sp"], min=-720, max=720),
                  M.Mechanism("p1", "PISTON", "Lift", parts=["cy", "ro"]),
                  M.Mechanism("f1", "FOLLOW", "Spin Follow", source="h1", target="hs", source_range=(0, 80), target_range=(0, 30)),
                  M.Sequence("q1", "Unfold", steps=[M.Step("h1", 60.0)])):
            records.add(data, x)
        build.rebuild(arm)
        rig = records.to_model(arm)
        assert test_sweep.driver_of(rig, "h1") == ("h1", -20.0, 80.0)
        assert test_sweep.driver_of(rig, "hs") == ("hs", 0.0, 360.0), "a free hinge sweeps one turn"
        odd = M.MechRig(parts=[M.Part("o", "O")], mechanisms=[M.Mechanism("ho", "HINGE", "O Hinge", parts=["o"], min=-20, max=400)])
        assert test_sweep.driver_of(odd, "ho") == ("ho", 0.0, 360.0), "a full turn or more has no limits (spec §6)"
        assert test_sweep.driver_of(rig, "f1") == ("h1", -20.0, 80.0), "a link sweeps its source"
        assert test_sweep.driver_of(rig, "p1") == ("h1", -20.0, 80.0), "a piston sweeps its nearest moving ancestor"
        assert test_sweep.driver_of(rig, "q1") == ("q1", 0.0, 1.0)
        build.set_value(arm, rig, "h1", 15.0)
        build.set_value(arm, rig, "q1", 0.3)
        seen = []
        sweep = test_sweep.Sweep(arm, rig, "h1", frames=4)
        while sweep.step():
            seen.append(round(build.get_value(arm, rig, "h1"), 4))
        assert seen == [-20.0, 5.0, 30.0, 55.0, 80.0, 55.0, 30.0, 5.0, -20.0], seen
        assert abs(build.get_value(arm, rig, "h1") - 15.0) < 1e-4 and abs(build.get_value(arm, rig, "q1") - 0.3) < 1e-6, \
            "every control is restored"
        assert arm.animation_data is None or arm.animation_data.action is None, "Test writes no keyframes"
        half = test_sweep.Sweep(arm, rig, "q1", frames=2)
        half.step()
        half.step()
        half.stop()
        assert abs(build.get_value(arm, rig, "q1") - 0.3) < 1e-6, "stopping early restores too"
        lone = M.MechRig(parts=[M.Part("a", "A"), M.Part("b", "B")],
                         mechanisms=[M.Mechanism("pp", "PISTON", "Lone", parts=["a", "b"])])
        try:
            test_sweep.driver_of(lone, "pp")
            raise AssertionError("a piston nothing moves cannot be tested")
        except build.BuildError as exc:
            assert "Nothing moves" in str(exc)
        import inspect
        assert "event.timer" not in inspect.getsource(test_sweep.BC_OT_mech_test.modal),             "Event has no timer property in Bforartists 5.2.0; modal() paces by timer.time_duration"
        import types
        op = test_sweep.BC_OT_mech_test
        ticks = types.SimpleNamespace(time_duration=0.0)
        fake = types.SimpleNamespace(sweep=test_sweep.Sweep(arm, rig, "q1", frames=2), timer=ticks,
                                     _end=lambda ctx, result: result)
        tick = types.SimpleNamespace(type='TIMER')
        ctx = types.SimpleNamespace(area=None)
        for dur, want_i in ((0.0, 1), (0.0, 1), (0.05, 2), (0.05, 2), (0.1, 3)):    # 24 steps per second of timer time
            ticks.time_duration = dur
            assert op.modal(fake, ctx, tick) == {'PASS_THROUGH'}
            assert fake.sweep.i == want_i, (dur, fake.sweep.i)
        ticks.time_duration = 1.0
        assert op.modal(fake, ctx, tick) == {'FINISHED'}, "the sweep ends when its values run out"
        fake.sweep = test_sweep.Sweep(arm, rig, "q1", frames=2)
        fake.sweep.step()
        assert op.modal(fake, ctx, types.SimpleNamespace(type='ESC')) == {'CANCELLED'}
        assert abs(build.get_value(arm, rig, "q1") - 0.3) < 1e-6, "Esc restores"
        assert "cancel" in op.__dict__, "Test defines cancel()"
        removed = []
        fake.sweep = test_sweep.Sweep(arm, rig, "q1", frames=2)
        fake.sweep.step()
        fake._end = lambda c, r: op._end(fake, c, r)
        op.cancel(fake, types.SimpleNamespace(window_manager=types.SimpleNamespace(event_timer_remove=removed.append)))
        assert removed == [ticks] and abs(build.get_value(arm, rig, "q1") - 0.3) < 1e-6,             "Blender cancelling the modal restores the pose and removes the timer"
        before = (build.get_value(arm, rig, "h1"), build.get_value(arm, rig, "q1"), build.get_value(arm, rig, "hs"))
        assert bpy.ops.boneforge.mech_test(target="h1") == {'FINISHED'}, "the execute path sweeps at once"
        after = (build.get_value(arm, rig, "h1"), build.get_value(arm, rig, "q1"), build.get_value(arm, rig, "hs"))
        assert all(abs(a - b) < 1e-4 for a, b in zip(before, after)), (before, after)
        assert arm.animation_data is None or arm.animation_data.action is None, "the operator writes no keyframes"
        assert bpy.ops.boneforge.mech_test(target="q1") == {'FINISHED'}
        assert abs(build.get_value(arm, rig, "q1") - 0.3) < 1e-6
        assert hasattr(bpy.types, "BONEFORGE_OT_mech_test"), "registered (bpy.types uses the idname form)"
    finally:
        boneforge.unregister()
    print("PASS mechanisms test sweep: ranges, sources, ancestors, restore, no keys")
