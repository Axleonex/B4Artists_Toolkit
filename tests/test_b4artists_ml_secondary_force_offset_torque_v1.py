"""Force-at-offset torque coverage for deterministic world secondary motion."""
from pathlib import Path
import json
import math
import os
import sys
import tempfile
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [os.environ.get("B4ML_PACKAGE", str(ROOT)), str(ROOT / "tests")]

import bpy
from mathutils import Quaternion
import b4artists_ml
from b4artists_ml import flight, secondary_math as sm, secondary_motion as secondary, workflow as w
from test_b4artists_ml_secondary_external_acceleration_v1 import FOREIGN_OWNERS
from test_b4artists_ml_secondary_motion import curve_values, fixture


def enter_pose(obj):
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    if obj.mode != "POSE":
        bpy.ops.object.mode_set(mode="POSE")


def torque_fixture(label, *, offset=(0.5, 0.0, 0.0), inertia=1.0):
    obj, source, _, _, control, rotation_path = fixture(label)
    state = obj.b4ml
    priority = state.anchors.add()
    priority.frame = 6.0
    priority.payload = state.anchors[0].payload
    state.secondary_space = "WORLD"
    state.secondary_rotation = True
    state.secondary_location = True
    state.secondary_chain = False
    state.secondary_frequency = 1.25
    state.secondary_damping = 0.6
    state.secondary_air_friction = 0.2
    state.secondary_strength = 1.0
    state.secondary_gravity = 0.0
    state.secondary_external_acceleration = (0.0, 0.0, 0.0)
    state.secondary_wind_velocity = (0.0, 0.0, 0.0)
    state.secondary_impulse_velocity = (0.0, 0.0, 0.0)
    state.secondary_collision = False
    state.secondary_load_force = (0.0, 4.0, 0.0)
    state.secondary_load_mass = 2.0
    state.secondary_load_offset = offset
    state.secondary_load_inertia = inertia
    enter_pose(obj)
    secondary.assign_control_loads(obj, (0.0, 4.0, 0.0), 2.0, offset, inertia)
    location_path = obj.pose.bones[control].path_from_id("location")
    curves = w.action_curves(
        state.candidate_action, getattr(obj.animation_data, "action_slot", None))
    if not all(curves.find(location_path, index=index) for index in range(3)):
        raise AssertionError("Torque fixture lacks complete location curves")
    return obj, source, control, rotation_path, location_path


class SecondaryForceOffsetTorqueTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b4artists_ml.register()

    def test_math_cross_product_direction_and_inertia_scaling(self):
        orientations = np.tile(np.array((1.0, 0.0, 0.0, 0.0)), (3, 1))
        torque, angular = sm.control_load_angular_acceleration(
            (0.0, 4.0, 0.0), (0.5, 0.0, 0.0), 2.0, orientations)
        np.testing.assert_array_equal(torque, np.tile((0.0, 0.0, 2.0), (3, 1)))
        np.testing.assert_array_equal(angular, np.tile((0.0, 0.0, 1.0), (3, 1)))
        _, slower = sm.control_load_angular_acceleration(
            (0.0, 4.0, 0.0), (0.5, 0.0, 0.0), 4.0, orientations)
        np.testing.assert_array_equal(slower, angular * 0.5)

    def test_math_local_offset_rotates_with_target_orientation(self):
        orientations = np.array((
            (1.0, 0.0, 0.0, 0.0),
            tuple(Quaternion((0.0, 0.0, 1.0), math.pi / 2.0)),
        ))
        torque, _ = sm.control_load_angular_acceleration(
            (0.0, 4.0, 0.0), (0.5, 0.0, 0.0), 1.0, orientations)
        np.testing.assert_allclose(torque[0], (0.0, 0.0, 2.0), atol=1e-12)
        np.testing.assert_allclose(torque[1], (0.0, 0.0, 0.0), atol=2e-7)

    def test_math_torque_validation_fails_closed(self):
        hostile = (
            ((1.0, 0.0, 0.0), (1.0, 2.0), 1.0),
            ((True, 0.0, 0.0), (1.0, 0.0, 0.0), 1.0),
            ((1.0, 0.0, 0.0), (float("nan"), 0.0, 0.0), 1.0),
            ((1.0, 0.0, 0.0), (1001.0, 0.0, 0.0), 1.0),
            ((1.0, 0.0, 0.0), (1.0, 0.0, 0.0), True),
            ((1.0, 0.0, 0.0), (1.0, 0.0, 0.0), 0.0),
            ((0.0, 101.0, 0.0), (1.0, 0.0, 0.0), 1.0),
        )
        for force, offset, inertia in hostile:
            with self.subTest(force=force, offset=offset, inertia=inertia):
                with self.assertRaises(ValueError):
                    sm.validate_control_torque_settings(force, offset, inertia)

    def test_math_zero_forcing_is_exact_legacy_follower(self):
        targets = np.array([
            tuple(Quaternion((0.0, 0.0, 1.0), angle))
            for angle in np.linspace(0.0, 0.8, 9)])
        steps = np.ones(8)
        envelope = sm.boundary_envelope(np.arange(9.0), 2.0)
        legacy = sm.follow_quaternions(
            targets, steps, dt=1 / 24, frequency=1.2, damping=0.5,
            air_friction=0.2, strength=0.8, envelope=envelope)
        forced = sm.follow_forced_quaternions(
            targets, steps, dt=1 / 24, frequency=1.2, damping=0.5,
            air_friction=0.2, strength=0.8, envelope=envelope,
            angular_accelerations=np.zeros((9, 3)))
        self.assertTrue(np.array_equal(forced, legacy))

    def test_math_forcing_changes_interior_and_preserves_endpoints(self):
        targets = np.tile(np.array((1.0, 0.0, 0.0, 0.0)), (9, 1))
        forcing = np.tile((0.0, 0.0, 2.0), (9, 1))
        result = sm.follow_forced_quaternions(
            targets, np.ones(8), dt=1 / 24, frequency=0.8, damping=0.4,
            air_friction=0.1, strength=1.0,
            envelope=sm.boundary_envelope(np.arange(9.0), 2.0),
            angular_accelerations=forcing)
        self.assertTrue(np.array_equal(result[[0, -1]], targets[[0, -1]]))
        self.assertGreater(float(np.max(np.abs(result[1:-1, 3]))), 1e-5)
        with self.assertRaisesRegex(ValueError, "booleans"):
            sm.follow_forced_quaternions(
                targets, np.ones(8), dt=1 / 24, frequency=0.8, damping=0.4,
                air_friction=0.1, strength=1.0,
                envelope=sm.boundary_envelope(np.arange(9.0), 2.0),
                angular_accelerations=np.zeros((9, 3), dtype=bool))
        with self.assertRaisesRegex(ValueError, "angular acceleration limit"):
            sm.follow_forced_quaternions(
                targets, np.ones(8), dt=1 / 24, frequency=0.8, damping=0.4,
                air_friction=0.1, strength=1.0,
                envelope=sm.boundary_envelope(np.arange(9.0), 2.0),
                angular_accelerations=np.tile((100.0, 100.0, 100.0), (9, 1)))

    def test_schema_two_record_is_deterministic_and_clear_is_exact(self):
        obj, _, _, _, _ = torque_fixture("boneforge")
        stored = json.loads(obj.b4ml.secondary_control_loads)
        control = secondary.selected_controls(obj)[0]
        self.assertEqual(stored["schema"], 2)
        self.assertEqual(stored["loads"], [{
            "control": control, "force": [0.0, 4.0, 0.0], "mass": 2.0,
            "offset": [0.5, 0.0, 0.0], "rotational_inertia": 1.0}])
        self.assertEqual(secondary.control_load_count(obj), 1)
        self.assertEqual(secondary.clear_control_loads(obj)["removed"], 1)
        self.assertEqual(obj.b4ml.secondary_control_loads, "")

    def test_schema_one_record_remains_compatible(self):
        obj, _, _, _, _ = torque_fixture("boneforge", offset=(0.0, 0.0, 0.0))
        stored = json.loads(obj.b4ml.secondary_control_loads)
        self.assertEqual(stored["schema"], 1)
        row = secondary.request(obj, bpy.context.scene)["control_loads"][0]
        self.assertEqual(set(row), {"control", "force", "mass"})

    def test_zero_offset_and_nondefault_inertia_preserve_force_only_output(self):
        baseline, _, _, _, baseline_path = torque_fixture(
            "boneforge", offset=(0.0, 0.0, 0.0), inertia=1.0)
        baseline_report = secondary.solve(baseline, bpy.context.scene)
        baseline_values = curve_values(baseline.b4ml.candidate_action, baseline, baseline_path)

        obj, _, _, _, location_path = torque_fixture(
            "boneforge", offset=(0.0, 0.0, 0.0), inertia=7.0)
        report = secondary.solve(obj, bpy.context.scene)
        self.assertEqual(report["schema"], 7)
        self.assertEqual(report["backend"], "implicit_selected_control_secondary_v6")
        self.assertEqual(report["torque_controls"], 0)
        self.assertEqual(report["max_control_torque"], 0.0)
        self.assertEqual(curve_values(obj.b4ml.candidate_action, obj, location_path),
                         baseline_values)
        self.assertEqual(report["max_location_correction"],
                         baseline_report["max_location_correction"])

    def test_boneforge_and_rigify_force_at_offset_workflow(self):
        for label in ("boneforge", "rigify_default"):
            with self.subTest(rig=label):
                obj, source, control, rotation_path, location_path = torque_fixture(label)
                state = obj.b4ml
                original = state.candidate_action
                token = flight._curve_token(obj, original)
                before_rotation = curve_values(original, obj, rotation_path)
                before_location = curve_values(original, obj, location_path)
                report = secondary.solve(obj, bpy.context.scene)
                self.assertEqual(report["schema"], 8)
                self.assertEqual(report["backend"], "implicit_selected_control_secondary_v7")
                self.assertEqual(report["controls"], [control])
                self.assertEqual(report["torque_controls"], 1)
                self.assertGreater(report["max_control_torque"], 0.0)
                self.assertGreater(report["max_control_angular_acceleration"], 0.0)
                self.assertGreater(report["max_rotation_correction_radians"], 1e-5)
                self.assertGreater(report["max_location_correction"], 1e-5)
                self.assertLessEqual(report["max_world_location_error"], 2e-4)
                self.assertLessEqual(report["max_world_rotation_error_radians"], 2e-3)
                output = state.candidate_action
                self.assertNotEqual(curve_values(output, obj, rotation_path), before_rotation)
                self.assertNotEqual(curve_values(output, obj, location_path), before_location)
                self.assertEqual(flight._curve_token(obj, original), token)
                secondary.restore(obj, bpy.context.scene)
                self.assertIs(state.candidate_action, original)
                w.finish_preview(obj, bpy.context.scene, False)
                self.assertIs(obj.animation_data.action, source)

    def test_torque_requires_world_location_and_rotation_atomically(self):
        obj, _, _, _, _ = torque_fixture("boneforge")
        state = obj.b4ml
        original = state.candidate_action
        token = flight._curve_token(obj, original)
        actions = set(bpy.data.actions.keys())
        state.secondary_space = "LOCAL"
        with self.assertRaisesRegex(ValueError, "World simulation space"):
            secondary.solve(obj, bpy.context.scene)
        state.secondary_space = "WORLD"
        state.secondary_location = False
        with self.assertRaisesRegex(ValueError, "require Location"):
            secondary.solve(obj, bpy.context.scene)
        state.secondary_location = True
        state.secondary_rotation = False
        with self.assertRaisesRegex(ValueError, "requires Rotation"):
            secondary.solve(obj, bpy.context.scene)
        self.assertIs(state.candidate_action, original)
        self.assertEqual(flight._curve_token(obj, original), token)
        self.assertEqual(set(bpy.data.actions.keys()), actions)

    def test_torque_rejects_missing_rotation_curves_atomically(self):
        obj, _, control, _, _ = torque_fixture("boneforge")
        state = obj.b4ml
        action = state.candidate_action
        bone = obj.pose.bones[control]
        prop, count = secondary._rotation_spec(bone)
        path = bone.path_from_id(prop)
        curves = w.action_curves(action, getattr(obj.animation_data, "action_slot", None))
        for index in range(count):
            curves.remove(curves.find(path, index=index))
        with self.assertRaisesRegex(ValueError, "complete editable rotation curves"):
            secondary.solve(obj, bpy.context.scene)
        self.assertIs(state.candidate_action, action)

    def test_offset_change_invalidates_cooperative_solve_and_rolls_back(self):
        obj, _, _, _, _ = torque_fixture("boneforge")
        state = obj.b4ml
        original = state.candidate_action
        token = flight._curve_token(obj, original)
        secondary.start(obj, bpy.context.scene)
        self.assertFalse(secondary.step(obj))
        record = json.loads(state.secondary_control_loads)
        record["loads"][0]["offset"] = [0.25, 0.0, 0.0]
        state.secondary_control_loads = json.dumps(
            record, sort_keys=True, separators=(",", ":"))
        with self.assertRaisesRegex(ValueError, "settings changed"):
            secondary.step(obj)
        self.assertFalse(state.secondary_running)
        self.assertIs(state.candidate_action, original)
        self.assertIs(obj.animation_data.action, original)
        self.assertEqual(flight._curve_token(obj, original), token)

    def test_assignment_respects_every_workflow_owner(self):
        obj, _, _, _, _, _ = fixture("boneforge")
        enter_pose(obj)
        state = obj.b4ml
        before = state.secondary_control_loads
        for field, value in FOREIGN_OWNERS:
            with self.subTest(owner=field):
                setattr(state, field, value)
                with self.assertRaisesRegex(ValueError, "Finish the active"):
                    secondary.assign_control_loads(
                        obj, (0.0, 4.0, 0.0), 2.0, (0.5, 0.0, 0.0), 1.0)
                self.assertEqual(state.secondary_control_loads, before)
                setattr(state, field, False if isinstance(value, bool) else "")

    def test_schema_two_assignment_survives_save_and_reload(self):
        obj, _, control, _, _ = torque_fixture("boneforge")
        object_name = obj.name
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / "secondary-force-offset.blend")
            bpy.ops.wm.save_as_mainfile(filepath=path, check_existing=False)
            bpy.ops.wm.open_mainfile(filepath=path, load_ui=False, use_scripts=False)
        loaded = bpy.data.objects[object_name]
        row = secondary.request(loaded, bpy.context.scene)["control_loads"]
        self.assertEqual(row, [{
            "control": control, "force": [0.0, 4.0, 0.0], "mass": 2.0,
            "offset": [0.5, 0.0, 0.0], "rotational_inertia": 1.0}])
        self.assertEqual(secondary.control_load_count(loaded), 1)


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        SecondaryForceOffsetTorqueTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print("B4ML_SECONDARY_FORCE_OFFSET_TORQUE_RESULT:",
          "PASS" if result.wasSuccessful() else "FAIL")
