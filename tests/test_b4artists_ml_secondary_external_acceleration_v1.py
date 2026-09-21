"""Uniform external-acceleration coverage for world secondary motion."""
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
from test_b4artists_ml_secondary_motion import curve_values, fixture


FOREIGN_OWNERS = (
    ("temporal_running", True),
    ("body_running", True),
    ("body_live", True),
    ("body_payload", "{}"),
    ("posing_payload", "{}"),
    ("quadruped_payload", "{}"),
    ("flight_running", True),
    ("contact_running", True),
    ("contact_suggest_running", True),
    ("cleanup_running", True),
)


def location_fixture(label):
    obj, source, _, _, selected_name, _ = fixture(label)
    state = obj.b4ml
    selected = obj.pose.bones[selected_name]
    path = selected.path_from_id("location")
    curves = w.action_curves(
        state.candidate_action, getattr(obj.animation_data, "action_slot", None))
    group = [curves.find(path, index=index) for index in range(3)]
    if not all(group):
        raise AssertionError("Fixture selected control lacks complete location curves")
    for frame in range(1, 12):
        key = min(group[0].keyframe_points,
                  key=lambda item: abs(float(item.co.x) - frame))
        key.co.y = .12 * math.sin((frame - 1) * math.pi / 5)
        key.interpolation = "LINEAR"
        group[0].update()
    priority = state.anchors.add()
    priority.frame = 6.
    priority.payload = state.anchors[0].payload
    state.secondary_space = "WORLD"
    state.secondary_rotation = False
    state.secondary_location = True
    state.secondary_frequency = 1.25
    state.secondary_damping = .6
    state.secondary_air_friction = .2
    state.secondary_strength = 1.
    state.secondary_gravity = 0.
    state.secondary_external_acceleration = (4., -1.5, .75)
    return obj, source, selected_name, path


def pose_near(before, after):
    if before.keys() != after.keys():
        return False
    for name, expected in before.items():
        actual = after[name]
        if (expected["mode"] != actual["mode"]
                or expected["channels"] != actual["channels"]):
            return False
        for field in ("location", "scale", "rotation", "raw_rotation"):
            if not np.allclose(expected[field], actual[field], rtol=0., atol=1e-12):
                return False
    return True


class SecondaryExternalAccelerationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b4artists_ml.register()

    def test_math_acceleration_preserves_priority_samples(self):
        frames = np.arange(1., 12.)
        target = np.zeros((len(frames), 3), dtype=float)
        envelope = sm.priority_envelope(frames, [1., 6., 11.], 2.)
        result, metrics = sm.apply_world_vector_follow(
            target, frames, dt=1/24, frequency=.5, damping=.35,
            air_friction=.1, strength=1., blend_frames=2., envelope=envelope,
            external_acceleration=(6., -2., 1.))
        self.assertTrue(np.array_equal(result[[0, 5, 10]], target[[0, 5, 10]]))
        self.assertGreater(float(np.max(np.linalg.norm(result-target, axis=1))), .001)
        self.assertGreater(metrics["max_world_correction"], .001)

    def test_math_acceleration_adds_to_scaled_scene_gravity(self):
        target = np.zeros((9, 3), dtype=float)
        steps = np.ones(8, dtype=float)
        combined, _ = sm.follow_world_vectors(
            target, steps, dt=1/24, frequency=.8, damping=.5,
            air_friction=.2, gravity=(0., 0., -10.), gravity_scale=.5,
            external_acceleration=(3., 1., 2.))
        equivalent, _ = sm.follow_world_vectors(
            target, steps, dt=1/24, frequency=.8, damping=.5,
            air_friction=.2, external_acceleration=(3., 1., -3.))
        self.assertTrue(np.array_equal(combined, equivalent))

    def test_math_acceleration_validation_fails_closed(self):
        for value in ((1., 2.), (float("nan"), 0., 0.), (100.001, 0., 0.)):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    sm.validate_world_settings(
                        gravity=(0., 0., -9.81), gravity_scale=1.,
                        external_acceleration=value)

    def test_math_acceleration_respects_planar_collision(self):
        target = np.zeros((12, 3), dtype=float)
        result, metrics = sm.follow_world_vectors(
            target, np.ones(11), dt=1/24, frequency=.5, damping=.25,
            air_friction=0., external_acceleration=(2., 0., -20.),
            collision_point=(0., 0., -.01), collision_normal=(0., 0., 1.),
            clearance=0., restitution=.2, surface_friction=.5)
        self.assertGreater(metrics["collision_samples"], 0)
        self.assertGreater(metrics["max_raw_penetration"], 0.)
        self.assertGreaterEqual(float(np.min(result[:, 2])), -.010000001)
        self.assertGreater(float(np.max(result[:, 0])), 0.)

    def test_boneforge_and_rigify_world_acceleration(self):
        for label in ("boneforge", "rigify_default"):
            with self.subTest(rig=label):
                obj, source, selected_name, path = location_fixture(label)
                scene = bpy.context.scene
                state = obj.b4ml
                original = state.candidate_action
                original_token = flight._curve_token(obj, original)
                before = curve_values(original, obj, path)
                report = secondary.solve(obj, scene)
                output = state.candidate_action
                after = curve_values(output, obj, path)
                self.assertEqual(report["schema"], 4)
                self.assertEqual(report["backend"], "implicit_selected_control_secondary_v3")
                self.assertEqual(report["controls"], [selected_name])
                self.assertEqual(report["external_acceleration"], [4., -1.5, .75])
                self.assertAlmostEqual(
                    report["external_acceleration_magnitude"],
                    math.sqrt(4.**2 + 1.5**2 + .75**2), places=8)
                self.assertTrue(report["priority_poses_preserved"])
                self.assertGreater(report["max_location_correction"], .001)
                self.assertLessEqual(report["max_world_location_error"], 2e-4)
                self.assertNotEqual(after, before)
                for axis_before, axis_after in zip(before, after):
                    for priority_index in (0, 5, -1):
                        self.assertEqual(axis_before[1][priority_index][1],
                                         axis_after[1][priority_index][1])
                self.assertEqual(flight._curve_token(obj, original), original_token)
                self.assertIs(state.secondary_input, original)
                secondary.restore(obj, scene)
                self.assertIs(state.candidate_action, original)
                self.assertEqual(curve_values(original, obj, path), before)
                w.finish_preview(obj, scene, False)
                self.assertIs(obj.animation_data.action, source)

    def test_acceleration_requires_world_location_without_mutation(self):
        obj, _, _, _ = location_fixture("boneforge")
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
        self.assertIs(state.candidate_action, original)
        self.assertIs(obj.animation_data.action, original)
        self.assertEqual(flight._curve_token(obj, original), token)
        self.assertEqual(set(bpy.data.actions.keys()), actions)

    def test_acceleration_change_invalidates_running_request(self):
        obj, _, _, _ = location_fixture("boneforge")
        scene = bpy.context.scene
        state = obj.b4ml
        original = state.candidate_action
        token = flight._curve_token(obj, original)
        secondary.start(obj, scene)
        self.assertFalse(secondary.step(obj))
        state.secondary_external_acceleration = (
            state.secondary_external_acceleration[0] + .25,
            state.secondary_external_acceleration[1],
            state.secondary_external_acceleration[2])
        with self.assertRaisesRegex(ValueError, "settings changed"):
            secondary.step(obj)
        self.assertFalse(state.secondary_running)
        self.assertIs(state.candidate_action, original)
        self.assertIs(obj.animation_data.action, original)
        self.assertEqual(flight._curve_token(obj, original), token)

    def test_every_foreign_owner_blocks_admission_atomically(self):
        obj, _, _, _ = location_fixture("boneforge")
        scene = bpy.context.scene
        state = obj.b4ml
        original = state.candidate_action
        token = flight._curve_token(obj, original)
        actions = set(bpy.data.actions.keys())
        status = state.status
        for field, active in FOREIGN_OWNERS:
            with self.subTest(owner=field):
                setattr(state, field, active)
                self.assertFalse(bpy.ops.b4ml.secondary_solve.poll())
                self.assertFalse(bpy.ops.b4ml.secondary.poll())
                with self.assertRaisesRegex(ValueError, "active pose or correction"):
                    secondary.start(obj, scene)
                self.assertFalse(state.secondary_running)
                self.assertIs(state.candidate_action, original)
                self.assertIs(obj.animation_data.action, original)
                self.assertEqual(flight._curve_token(obj, original), token)
                self.assertEqual(set(bpy.data.actions.keys()), actions)
                self.assertEqual(state.status, status)
                setattr(state, field, False if isinstance(active, bool) else "")

    def test_every_foreign_owner_aborts_cooperative_solve_atomically(self):
        obj, _, _, _ = location_fixture("boneforge")
        scene = bpy.context.scene
        state = obj.b4ml
        original = state.candidate_action
        token = flight._curve_token(obj, original)
        actions = set(bpy.data.actions.keys())
        status = state.status
        pose = w.raw_pose(obj)
        for field, active in FOREIGN_OWNERS:
            with self.subTest(owner=field):
                secondary.start(obj, scene)
                steps = 0
                while set(bpy.data.actions.keys()) == actions:
                    self.assertFalse(secondary.step(obj))
                    steps += 1
                    self.assertLess(steps, 500)
                setattr(state, field, active)
                try:
                    caught = False
                    for _ in range(20):
                        try:
                            secondary.step(obj)
                        except ValueError as exc:
                            self.assertRegex(str(exc), "started during secondary")
                            caught = True
                            break
                    self.assertTrue(caught)
                    self.assertFalse(state.secondary_running)
                    self.assertIs(state.candidate_action, original)
                    self.assertIs(obj.animation_data.action, original)
                    self.assertEqual(flight._curve_token(obj, original), token)
                    self.assertEqual(set(bpy.data.actions.keys()), actions)
                    self.assertEqual(state.status, status)
                    self.assertTrue(pose_near(pose, w.raw_pose(obj)))
                finally:
                    setattr(state, field, False if isinstance(active, bool) else "")

    def test_every_foreign_owner_blocks_restore_atomically(self):
        obj, _, _, _ = location_fixture("boneforge")
        scene = bpy.context.scene
        state = obj.b4ml
        original = state.candidate_action
        secondary.solve(obj, scene)
        output = state.candidate_action
        token = flight._curve_token(obj, output)
        actions = set(bpy.data.actions.keys())
        status = state.status
        for field, active in FOREIGN_OWNERS:
            with self.subTest(owner=field):
                setattr(state, field, active)
                with self.assertRaisesRegex(ValueError, "active correction"):
                    secondary.restore(obj, scene)
                self.assertIs(state.candidate_action, output)
                self.assertIs(state.secondary_input, original)
                self.assertIs(state.secondary_output, output)
                self.assertIs(obj.animation_data.action, output)
                self.assertEqual(flight._curve_token(obj, output), token)
                self.assertEqual(set(bpy.data.actions.keys()), actions)
                self.assertEqual(state.status, status)
                setattr(state, field, False if isinstance(active, bool) else "")
        secondary.restore(obj, scene)
        self.assertIs(state.candidate_action, original)

    def test_acceleration_rejects_rotation_only_selected_control(self):
        obj, _, selected_name, _ = location_fixture("boneforge")
        scene = bpy.context.scene
        state = obj.b4ml
        action = state.candidate_action
        bone = obj.pose.bones[selected_name]
        path = bone.path_from_id("location")
        curves = w.action_curves(action, getattr(obj.animation_data, "action_slot", None))
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

    def test_acceleration_rejects_mixed_location_curve_selection(self):
        obj, _, selected_name, _ = location_fixture("boneforge")
        scene = bpy.context.scene
        state = obj.b4ml
        action = state.candidate_action
        curves = w.action_curves(action, getattr(obj.animation_data, "action_slot", None))
        captured = set(json.loads(state.anchors[0].payload)["pose"])
        second = None
        for bone in obj.pose.bones:
            if bone.name == selected_name or bone.name not in captured:
                continue
            rotation_path, count = secondary._rotation_spec(bone)
            rotation_path = bone.path_from_id(rotation_path)
            location_path = bone.path_from_id("location")
            if (all(curves.find(rotation_path, index=index) is not None for index in range(count))
                    and all(curves.find(location_path, index=index) is not None for index in range(3))):
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

    def test_zero_acceleration_preserves_existing_backend(self):
        obj, _, _, _ = location_fixture("boneforge")
        state = obj.b4ml
        state.secondary_external_acceleration = (0., 0., 0.)
        state.secondary_gravity = .5
        report = secondary.solve(obj, bpy.context.scene)
        self.assertEqual(report["schema"], 3)
        self.assertEqual(report["backend"], "implicit_selected_control_secondary_v2")
        self.assertEqual(report["external_acceleration"], [0., 0., 0.])
        self.assertEqual(report["external_acceleration_magnitude"], 0.)


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        SecondaryExternalAccelerationTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print("B4ML_SECONDARY_EXTERNAL_ACCELERATION_RESULT:",
          "PASS" if result.wasSuccessful() else "FAIL")
