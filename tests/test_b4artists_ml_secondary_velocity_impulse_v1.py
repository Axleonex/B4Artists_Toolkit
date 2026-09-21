"""Frame-authored velocity-impulse coverage for world secondary motion."""
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
from mathutils import Vector
from b4artists_ml import flight, secondary_math as sm, secondary_motion as secondary, workflow as w
from test_b4artists_ml_secondary_external_acceleration_v1 import location_fixture
from test_b4artists_ml_secondary_motion import curve_values


def impulse_fixture(label):
    obj, source, selected_name, path = location_fixture(label)
    state = obj.b4ml
    state.secondary_external_acceleration = (0., 0., 0.)
    state.secondary_wind_velocity = (0., 0., 0.)
    state.secondary_impulse_velocity = (3., -1., .5)
    state.secondary_impulse_frame = 6.
    return obj, source, selected_name, path


class SecondaryVelocityImpulseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b4artists_ml.register()

    def test_math_impulse_starts_after_authored_sample(self):
        target = np.zeros((10, 3), dtype=float)
        result, _ = sm.follow_world_vectors(
            target, np.ones(9), dt=1/24, frequency=.5, damping=.25,
            air_friction=.2, velocity_impulse=(4., -2., 1.), impulse_index=3)
        self.assertTrue(np.array_equal(result[:4], target[:4]))
        self.assertGreater(result[4, 0], 0.)
        self.assertLess(result[4, 1], 0.)
        self.assertGreater(result[4, 2], 0.)

    def test_math_zero_impulse_is_exactly_backward_compatible(self):
        target = np.column_stack((np.linspace(0., 1., 10),
                                  np.linspace(1., -.5, 10),
                                  np.zeros(10)))
        common = dict(dt=1/30, frequency=1.2, damping=.45,
                      air_friction=.35, gravity=(0., 0., -9.81),
                      gravity_scale=.2, external_acceleration=(1., 0., .5),
                      wind_velocity=(2., -1., 0.))
        previous, previous_metrics = sm.follow_world_vectors(
            target, np.ones(9), **common)
        explicit, explicit_metrics = sm.follow_world_vectors(
            target, np.ones(9), velocity_impulse=(0., 0., 0.), **common)
        self.assertTrue(np.array_equal(previous, explicit))
        self.assertEqual(previous_metrics, explicit_metrics)

    def test_math_impulse_validation_and_index_fail_closed(self):
        for value in ((1., 2.), (float("nan"), 0., 0.), (0., 100.001, 0.)):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    sm.validate_world_settings(
                        gravity=(0., 0., -9.81), gravity_scale=1.,
                        velocity_impulse=value)
        target = np.zeros((4, 3), dtype=float)
        for index in (None, -1, 3, 1.5, True):
            with self.subTest(index=index):
                with self.assertRaises(ValueError):
                    sm.follow_world_vectors(
                        target, np.ones(3), dt=1/24, frequency=.5, damping=.2,
                        air_friction=.1, velocity_impulse=(1., 0., 0.),
                        impulse_index=index)
        with self.assertRaises(ValueError):
            sm.follow_world_vectors(
                target, np.ones(3), dt=1/24, frequency=.5, damping=.2,
                air_friction=.1, velocity_impulse=(0., 0., 0.), impulse_index=0)

    def test_math_impulse_preserves_priority_and_collides(self):
        frames = np.arange(1., 12.)
        target = np.zeros((len(frames), 3), dtype=float)
        envelope = sm.priority_envelope(frames, [1., 6., 11.], 2.)
        result, metrics = sm.apply_world_vector_follow(
            target, frames, dt=1/24, frequency=.5, damping=.25,
            air_friction=.2, strength=1., blend_frames=2., envelope=envelope,
            velocity_impulse=(2., 0., -8.), impulse_index=5,
            collision_point=(0., 0., -.01), collision_normal=(0., 0., 1.))
        self.assertTrue(np.array_equal(result[[0, 5, 10]], target[[0, 5, 10]]))
        self.assertGreater(metrics["collision_samples"], 0)
        self.assertGreater(float(np.max(result[:, 0])), 0.)

    def test_boneforge_and_rigify_world_impulse_workflow(self):
        for label in ("boneforge", "rigify_default"):
            with self.subTest(rig=label):
                obj, source, selected_name, path = impulse_fixture(label)
                scene = bpy.context.scene
                state = obj.b4ml
                original = state.candidate_action
                token = flight._curve_token(obj, original)
                before = curve_values(original, obj, path)
                report = secondary.solve(obj, scene)
                after = curve_values(state.candidate_action, obj, path)
                self.assertEqual(report["schema"], 6)
                self.assertEqual(report["backend"],
                                 "implicit_selected_control_secondary_v5")
                self.assertEqual(report["controls"], [selected_name])
                self.assertEqual(report["impulse_velocity"], [3., -1., .5])
                self.assertAlmostEqual(report["impulse_velocity_magnitude"],
                                       math.sqrt(10.25), places=8)
                self.assertEqual(report["impulse_frame"], 6.)
                self.assertTrue(report["priority_poses_preserved"])
                self.assertGreater(report["max_location_correction"], .001)
                self.assertLessEqual(report["max_world_location_error"], 2e-4)
                self.assertNotEqual(before, after)
                for axis_before, axis_after in zip(before, after):
                    for priority_index in (0, 5, -1):
                        self.assertEqual(axis_before[1][priority_index][1],
                                         axis_after[1][priority_index][1])
                self.assertEqual(flight._curve_token(obj, original), token)
                secondary.restore(obj, scene)
                self.assertIs(state.candidate_action, original)
                self.assertEqual(curve_values(original, obj, path), before)
                w.finish_preview(obj, scene, False)
                self.assertIs(obj.animation_data.action, source)

    def test_impulse_requires_world_location_and_valid_frame_atomically(self):
        obj, _, _, _ = impulse_fixture("boneforge")
        scene = bpy.context.scene
        state = obj.b4ml
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
        for frame in (-1., 11., float("nan")):
            with self.subTest(frame=frame):
                state.secondary_impulse_frame = frame
                with self.assertRaisesRegex(ValueError, "impulse frame"):
                    secondary.solve(obj, scene)
        self.assertIs(state.candidate_action, original)
        self.assertIs(obj.animation_data.action, original)
        self.assertEqual(flight._curve_token(obj, original), token)
        self.assertEqual(set(bpy.data.actions.keys()), actions)

    def test_fractional_impulse_frame_becomes_exact_sample(self):
        obj, _, _, _ = impulse_fixture("boneforge")
        state = obj.b4ml
        state.secondary_impulse_frame = 5.25
        report = secondary.solve(obj, bpy.context.scene)
        self.assertEqual(report["impulse_frame"], 5.25)
        self.assertEqual(report["samples"], 12)
        self.assertTrue(report["priority_poses_preserved"])

    def test_distinct_fractional_priority_anchor_remains_exact(self):
        obj, _, selected_name, _ = impulse_fixture("boneforge")
        scene = bpy.context.scene
        state = obj.b4ml
        state.secondary_impulse_frame = 4.5
        priority = state.anchors.add()
        priority.frame = 5.25
        priority.payload = state.anchors[0].payload
        bone = obj.pose.bones[selected_name]
        path = bone.path_from_id("location")
        curves = w.action_curves(
            state.candidate_action, getattr(obj.animation_data, "action_slot", None))
        source_group = [curves.find(path, index=index) for index in range(3)]
        for index, curve in enumerate(source_group):
            key = curve.keyframe_points.insert(5.25, .37 + .11 * index)
            key.interpolation = "LINEAR"
            curve.update()
        expected_local = np.array([curve.evaluate(5.25) for curve in source_group])
        scene.frame_set(5, subframe=.25)
        expected_world = Vector((w.display_world(obj) @ bone.matrix).translation)
        report = secondary.solve(obj, scene)
        self.assertEqual(report["impulse_frame"], 4.5)
        self.assertEqual(report["priority_poses"], 4)
        output_curves = w.action_curves(
            state.candidate_action, getattr(obj.animation_data, "action_slot", None))
        output_group = [output_curves.find(path, index=index) for index in range(3)]
        actual_local = np.array([curve.evaluate(5.25) for curve in output_group])
        np.testing.assert_allclose(actual_local, expected_local, rtol=0., atol=1e-7)
        for curve, expected in zip(output_group, expected_local):
            key = next((item for item in curve.keyframe_points
                        if abs(float(item.co.x) - 5.25) < 1e-8), None)
            self.assertIsNotNone(key)
            self.assertAlmostEqual(float(key.co.y), float(expected), places=7)
        scene.frame_set(5, subframe=.25)
        actual_world = Vector((w.display_world(obj) @ bone.matrix).translation)
        self.assertLessEqual((actual_world - expected_world).length, 2e-4)

    def test_impulse_change_invalidates_running_request(self):
        obj, _, _, _ = impulse_fixture("boneforge")
        state = obj.b4ml
        original = state.candidate_action
        token = flight._curve_token(obj, original)
        secondary.start(obj, bpy.context.scene)
        self.assertFalse(secondary.step(obj))
        state.secondary_impulse_frame = 5.5
        with self.assertRaisesRegex(ValueError, "settings changed"):
            secondary.step(obj)
        self.assertFalse(state.secondary_running)
        self.assertIs(state.candidate_action, original)
        self.assertIs(obj.animation_data.action, original)
        self.assertEqual(flight._curve_token(obj, original), token)

    def test_impulse_rejects_missing_location_curves(self):
        obj, _, selected_name, _ = impulse_fixture("boneforge")
        state = obj.b4ml
        action = state.candidate_action
        path = obj.pose.bones[selected_name].path_from_id("location")
        curves = w.action_curves(
            action, getattr(obj.animation_data, "action_slot", None))
        for index in range(3):
            curves.remove(curves.find(path, index=index))
        state.secondary_rotation = True
        token = flight._curve_token(obj, action)
        actions = set(bpy.data.actions.keys())
        with self.assertRaisesRegex(ValueError, "every selected control"):
            secondary.solve(obj, bpy.context.scene)
        self.assertIs(state.candidate_action, action)
        self.assertIs(obj.animation_data.action, action)
        self.assertEqual(flight._curve_token(obj, action), token)
        self.assertEqual(set(bpy.data.actions.keys()), actions)

    def test_zero_impulse_preserves_existing_report_versions(self):
        obj, _, _, _ = impulse_fixture("boneforge")
        state = obj.b4ml
        state.secondary_impulse_velocity = (0., 0., 0.)
        state.secondary_external_acceleration = (0., 0., 0.)
        state.secondary_wind_velocity = (0., 0., 0.)
        report = secondary.solve(obj, bpy.context.scene)
        self.assertEqual(report["schema"], 3)
        self.assertEqual(report["backend"],
                         "implicit_selected_control_secondary_v2")
        self.assertEqual(report["impulse_velocity"], [0., 0., 0.])
        self.assertEqual(report["impulse_velocity_magnitude"], 0.)
        self.assertIsNone(report["impulse_frame"])
        secondary.restore(obj, bpy.context.scene)
        state.secondary_wind_velocity = (1., 0., 0.)
        report = secondary.solve(obj, bpy.context.scene)
        self.assertEqual(report["schema"], 5)
        self.assertEqual(report["backend"],
                         "implicit_selected_control_secondary_v4")

    def test_zero_impulse_ignores_hostile_dormant_frame_exactly(self):
        obj, _, _, path = impulse_fixture("boneforge")
        state = obj.b4ml
        state.secondary_impulse_velocity = (0., 0., 0.)
        state.secondary_external_acceleration = (0., 0., 0.)
        state.secondary_wind_velocity = (0., 0., 0.)
        baseline = None
        for frame in (float("nan"), float("inf"), -1000000., 1000000.):
            with self.subTest(frame=frame):
                state.secondary_impulse_frame = frame
                raw = secondary.request(obj, bpy.context.scene)
                self.assertIsNone(raw["impulse_frame"])
                report = secondary.solve(obj, bpy.context.scene)
                self.assertEqual(report["schema"], 3)
                self.assertEqual(report["backend"],
                                 "implicit_selected_control_secondary_v2")
                self.assertIsNone(report["impulse_frame"])
                current = curve_values(state.candidate_action, obj, path)
                if baseline is None:
                    baseline = current
                else:
                    self.assertEqual(current, baseline)
                secondary.restore(obj, bpy.context.scene)

    def test_impulse_request_is_serializable_and_exact(self):
        obj, _, _, _ = impulse_fixture("boneforge")
        state = obj.b4ml
        state.secondary_impulse_velocity = (-3.5, 1.25, 0.)
        state.secondary_impulse_frame = 4.25
        raw = secondary.request(obj, bpy.context.scene)
        self.assertEqual(raw["impulse_velocity"], [-3.5, 1.25, 0.])
        self.assertEqual(raw["impulse_frame"], 4.25)
        encoded = json.loads(json.dumps(raw))
        self.assertEqual(encoded["impulse_velocity"], [-3.5, 1.25, 0.])
        self.assertEqual(encoded["impulse_frame"], 4.25)


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        SecondaryVelocityImpulseTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print("B4ML_SECONDARY_VELOCITY_IMPULSE_RESULT:",
          "PASS" if result.wasSuccessful() else "FAIL")
