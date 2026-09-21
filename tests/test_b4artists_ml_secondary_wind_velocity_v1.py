"""Wind-relative drag coverage for world secondary motion."""
from pathlib import Path
import json
import math
import os
import sys
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [os.environ.get("B4ML_PACKAGE", str(ROOT)), str(ROOT / "tests")]

import bpy
import b4artists_ml
from b4artists_ml import flight, secondary_math as sm, secondary_motion as secondary, workflow as w
from test_b4artists_ml_secondary_external_acceleration_v1 import location_fixture
from test_b4artists_ml_secondary_motion import curve_values


class SecondaryWindVelocityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b4artists_ml.register()

    def test_math_wind_is_air_friction_relative_velocity_target(self):
        target = np.zeros((14, 3), dtype=float)
        steps = np.ones(13, dtype=float)
        wind = (4., -2., 1.)
        coefficient = .75
        relative, _ = sm.follow_world_vectors(
            target, steps, dt=1/24, frequency=.5, damping=.3,
            air_friction=coefficient, wind_velocity=wind)
        equivalent, _ = sm.follow_world_vectors(
            target, steps, dt=1/24, frequency=.5, damping=.3,
            air_friction=coefficient,
            external_acceleration=tuple(coefficient * value for value in wind))
        np.testing.assert_allclose(relative, equivalent, rtol=0., atol=1e-15)
        self.assertGreater(float(np.max(relative[:, 0])), 0.)
        self.assertLess(float(np.min(relative[:, 1])), 0.)

    def test_math_zero_wind_is_exactly_backward_compatible(self):
        target = np.column_stack((np.linspace(0., 1., 10),
                                  np.linspace(1., -.5, 10),
                                  np.zeros(10)))
        common = dict(dt=1/30, frequency=1.2, damping=.45,
                      air_friction=.35, gravity=(0., 0., -9.81),
                      gravity_scale=.2, external_acceleration=(1., 0., .5))
        previous, previous_metrics = sm.follow_world_vectors(
            target, np.ones(9), **common)
        explicit, explicit_metrics = sm.follow_world_vectors(
            target, np.ones(9), wind_velocity=(0., 0., 0.), **common)
        self.assertTrue(np.array_equal(previous, explicit))
        self.assertEqual(previous_metrics, explicit_metrics)

    def test_math_wind_validation_fails_closed(self):
        for value in ((1., 2.), (float("nan"), 0., 0.), (0., -100.001, 0.)):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    sm.validate_world_settings(
                        gravity=(0., 0., -9.81), gravity_scale=1.,
                        wind_velocity=value)

    def test_math_wind_combines_with_acceleration_and_collision(self):
        target = np.zeros((18, 3), dtype=float)
        result, metrics = sm.follow_world_vectors(
            target, np.ones(17), dt=1/24, frequency=.45, damping=.2,
            air_friction=.8, wind_velocity=(5., 0., -2.),
            external_acceleration=(0., 0., -10.),
            collision_point=(0., 0., -.01), collision_normal=(0., 0., 1.),
            restitution=.1, surface_friction=.25)
        self.assertGreater(metrics["collision_samples"], 0)
        self.assertGreaterEqual(float(np.min(result[:, 2])), -.010000001)
        self.assertGreater(float(np.max(result[:, 0])), 0.)

    def test_boneforge_and_rigify_world_wind_workflow(self):
        for label in ("boneforge", "rigify_default"):
            with self.subTest(rig=label):
                obj, source, selected_name, path = location_fixture(label)
                scene = bpy.context.scene
                state = obj.b4ml
                state.secondary_external_acceleration = (0., 0., 0.)
                state.secondary_wind_velocity = (3., -1., .5)
                state.secondary_air_friction = .8
                original = state.candidate_action
                token = flight._curve_token(obj, original)
                before = curve_values(original, obj, path)
                report = secondary.solve(obj, scene)
                after = curve_values(state.candidate_action, obj, path)
                self.assertEqual(report["schema"], 5)
                self.assertEqual(report["backend"],
                                 "implicit_selected_control_secondary_v4")
                self.assertEqual(report["controls"], [selected_name])
                self.assertEqual(report["wind_velocity"], [3., -1., .5])
                self.assertAlmostEqual(report["wind_velocity_magnitude"],
                                       math.sqrt(10.25), places=8)
                self.assertAlmostEqual(report["wind_forcing_acceleration_magnitude"],
                                       report["air_friction"] *
                                       report["wind_velocity_magnitude"], places=12)
                self.assertTrue(report["priority_poses_preserved"])
                self.assertGreater(report["max_location_correction"], .001)
                self.assertLessEqual(report["max_world_location_error"], 2e-4)
                self.assertNotEqual(before, after)
                self.assertEqual(flight._curve_token(obj, original), token)
                secondary.restore(obj, scene)
                self.assertIs(state.candidate_action, original)
                self.assertEqual(curve_values(original, obj, path), before)
                w.finish_preview(obj, scene, False)
                self.assertIs(obj.animation_data.action, source)

    def test_wind_requires_world_location_and_air_friction_without_mutation(self):
        obj, _, _, _ = location_fixture("boneforge")
        scene = bpy.context.scene
        state = obj.b4ml
        state.secondary_external_acceleration = (0., 0., 0.)
        state.secondary_wind_velocity = (2., 0., 0.)
        original = state.candidate_action
        token = flight._curve_token(obj, original)
        actions = set(bpy.data.actions.keys())
        state.secondary_space = "LOCAL"
        with self.assertRaisesRegex(ValueError, "World simulation space"):
            secondary.solve(obj, scene)
        state.secondary_space = "WORLD"
        state.secondary_location = False
        state.secondary_rotation = True
        with self.assertRaisesRegex(ValueError, "require Location"):
            secondary.solve(obj, scene)
        state.secondary_location = True
        state.secondary_rotation = False
        state.secondary_air_friction = 0.
        with self.assertRaisesRegex(ValueError, "Air Friction above zero"):
            secondary.solve(obj, scene)
        self.assertIs(state.candidate_action, original)
        self.assertIs(obj.animation_data.action, original)
        self.assertEqual(flight._curve_token(obj, original), token)
        self.assertEqual(set(bpy.data.actions.keys()), actions)

    def test_wind_change_invalidates_running_request(self):
        obj, _, _, _ = location_fixture("boneforge")
        scene = bpy.context.scene
        state = obj.b4ml
        state.secondary_external_acceleration = (0., 0., 0.)
        state.secondary_wind_velocity = (2., 0., 0.)
        original = state.candidate_action
        token = flight._curve_token(obj, original)
        secondary.start(obj, scene)
        self.assertFalse(secondary.step(obj))
        state.secondary_wind_velocity = (2.25, 0., 0.)
        with self.assertRaisesRegex(ValueError, "settings changed"):
            secondary.step(obj)
        self.assertFalse(state.secondary_running)
        self.assertIs(state.candidate_action, original)
        self.assertIs(obj.animation_data.action, original)
        self.assertEqual(flight._curve_token(obj, original), token)

    def test_wind_rejects_rotation_only_selected_control(self):
        obj, _, selected_name, _ = location_fixture("boneforge")
        scene = bpy.context.scene
        state = obj.b4ml
        state.secondary_external_acceleration = (0., 0., 0.)
        state.secondary_wind_velocity = (2., 0., 0.)
        action = state.candidate_action
        bone = obj.pose.bones[selected_name]
        path = bone.path_from_id("location")
        curves = w.action_curves(
            action, getattr(obj.animation_data, "action_slot", None))
        for index in range(3):
            curves.remove(curves.find(path, index=index))
        state.secondary_rotation = True
        token = flight._curve_token(obj, action)
        actions = set(bpy.data.actions.keys())
        with self.assertRaisesRegex(ValueError, "every selected control"):
            secondary.solve(obj, scene)
        self.assertIs(state.candidate_action, action)
        self.assertIs(obj.animation_data.action, action)
        self.assertEqual(flight._curve_token(obj, action), token)
        self.assertEqual(set(bpy.data.actions.keys()), actions)

    def test_wind_rejects_mixed_selection_missing_location_curves(self):
        obj, _, selected_name, _ = location_fixture("boneforge")
        scene = bpy.context.scene
        state = obj.b4ml
        state.secondary_external_acceleration = (0., 0., 0.)
        state.secondary_wind_velocity = (2., 0., 0.)
        action = state.candidate_action
        curves = w.action_curves(
            action, getattr(obj.animation_data, "action_slot", None))
        captured = set(json.loads(state.anchors[0].payload)["pose"])
        second = None
        for bone in obj.pose.bones:
            if bone.name == selected_name or bone.name not in captured:
                continue
            rotation_prop, count = secondary._rotation_spec(bone)
            rotation_path = bone.path_from_id(rotation_prop)
            location_path = bone.path_from_id("location")
            if (all(curves.find(rotation_path, index=index) is not None
                    for index in range(count))
                    and all(curves.find(location_path, index=index) is not None
                            for index in range(3))):
                second = bone, location_path
                break
        self.assertIsNotNone(second)
        bone, location_path = second
        if hasattr(bone, "select"):
            bone.select = True
        else:
            bone.bone.select = True
        for index in range(3):
            curves.remove(curves.find(location_path, index=index))
        state.secondary_rotation = True
        token = flight._curve_token(obj, action)
        actions = set(bpy.data.actions.keys())
        with self.assertRaisesRegex(ValueError, bone.name):
            secondary.solve(obj, scene)
        self.assertIs(state.candidate_action, action)
        self.assertIs(obj.animation_data.action, action)
        self.assertEqual(flight._curve_token(obj, action), token)
        self.assertEqual(set(bpy.data.actions.keys()), actions)

    def test_zero_wind_preserves_existing_report_versions(self):
        obj, _, _, _ = location_fixture("boneforge")
        state = obj.b4ml
        state.secondary_wind_velocity = (0., 0., 0.)
        state.secondary_external_acceleration = (0., 0., 0.)
        report = secondary.solve(obj, bpy.context.scene)
        self.assertEqual(report["schema"], 3)
        self.assertEqual(report["backend"],
                         "implicit_selected_control_secondary_v2")
        self.assertEqual(report["wind_velocity"], [0., 0., 0.])
        self.assertEqual(report["wind_velocity_magnitude"], 0.)
        secondary.restore(obj, bpy.context.scene)
        state.secondary_external_acceleration = (1., 0., 0.)
        report = secondary.solve(obj, bpy.context.scene)
        self.assertEqual(report["schema"], 4)
        self.assertEqual(report["backend"],
                         "implicit_selected_control_secondary_v3")

    def test_wind_request_is_serializable_and_exact(self):
        obj, _, _, _ = location_fixture("boneforge")
        state = obj.b4ml
        state.secondary_external_acceleration = (0., 0., 0.)
        state.secondary_wind_velocity = (-3.5, 1.25, 0.)
        raw = secondary.request(obj, bpy.context.scene)
        self.assertEqual(raw["wind_velocity"], [-3.5, 1.25, 0.])
        self.assertEqual(json.loads(json.dumps(raw))["wind_velocity"],
                         [-3.5, 1.25, 0.])


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        SecondaryWindVelocityTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print("B4ML_SECONDARY_WIND_VELOCITY_RESULT:",
          "PASS" if result.wasSuccessful() else "FAIL")
