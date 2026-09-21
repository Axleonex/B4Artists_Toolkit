"""Static spherical-volume collision for deterministic secondary motion."""
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
from mathutils import Vector
import b4artists_ml
from b4artists_ml import flight, secondary_math as sm, secondary_motion as secondary, workflow as w
from test_b4artists_ml_secondary_motion import curve_values, fixture


def make_sphere(name, center):
    collider = bpy.data.objects.new(name, None)
    collider.empty_display_type = "SPHERE"
    collider.empty_display_size = 0.1
    collider.location = center
    bpy.context.scene.collection.objects.link(collider)
    bpy.context.view_layer.update()
    return collider


def sphere_fixture(label="boneforge"):
    obj, source, _, _, control, _ = fixture(label)
    state = obj.b4ml
    priority = state.anchors.add()
    priority.frame = 6.0
    priority.payload = state.anchors[0].payload
    scene = bpy.context.scene
    positions = []
    for frame in (1.0, 6.0, 11.0):
        scene.frame_set(int(frame))
        positions.append((w.display_world(obj) @ obj.pose.bones[control].matrix).translation.copy())
    scene.frame_set(6)
    lowest = min(positions, key=lambda value: value.z)
    center = Vector((lowest.x, lowest.y, lowest.z - 0.14))
    collider = make_sphere("B4ML Sphere " + label, center)
    state.secondary_space = "WORLD"
    state.secondary_rotation = False
    state.secondary_location = True
    state.secondary_chain = False
    state.secondary_frequency = 0.5
    state.secondary_damping = 0.45
    state.secondary_air_friction = 0.15
    state.secondary_strength = 1.0
    state.secondary_blend_frames = 2.0
    state.secondary_gravity = 4.0
    state.secondary_external_acceleration = (0.0, 0.0, 0.0)
    state.secondary_wind_velocity = (0.0, 0.0, 0.0)
    state.secondary_impulse_velocity = (0.0, 0.0, 0.0)
    state.secondary_collision = True
    state.secondary_collision_shape = "SPHERE"
    state.secondary_sphere_collider = collider
    state.secondary_sphere_radius = 0.1
    state.secondary_collision_clearance = 0.01
    state.secondary_restitution = 0.2
    state.secondary_surface_friction = 0.4
    return obj, source, control, collider, positions


class SecondarySphereCollisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b4artists_ml.register()

    def test_math_sphere_excludes_points_and_reports_penetration(self):
        values = np.tile((0.0, 0.0, 1.1), (6, 1))
        result, report = sm.follow_world_vectors(
            values, np.ones(5), dt=0.25, frequency=0.05, damping=0.0,
            air_friction=0.0, external_acceleration=(0.0, 0.0, -10.0),
            collision_sphere_center=(0.0, 0.0, 0.0),
            collision_sphere_radius=1.0, restitution=0.25,
            surface_friction=0.5)
        self.assertGreater(report["collision_samples"], 0)
        self.assertGreater(report["max_raw_penetration"], 0.0)
        self.assertTrue(np.all(np.linalg.norm(result[1:], axis=1) >= 1.0 - 1e-10))
        targets = np.asarray(((2.0, 0.0, 0.0),
                              (0.0, 0.0, 0.0),
                              (2.0, 0.0, 0.0)))
        projected, projected_report = sm.apply_world_vector_follow(
            targets, (1.0, 2.0, 3.0), dt=1 / 24, frequency=1.0, damping=0.5,
            air_friction=0.0, strength=0.0, blend_frames=0.0,
            collision_sphere_center=(0.0, 0.0, 0.0),
            collision_sphere_radius=1.0, envelope=np.ones(3))
        # Zero influence is an exact no-op even when the authored target is
        # inside a collider; the report still exposes the retained penetration.
        np.testing.assert_array_equal(projected, targets)
        self.assertAlmostEqual(projected_report["max_penetration_after"], 1.0)
        self.assertAlmostEqual(
            projected_report["max_world_correction"],
            float(np.max(np.linalg.norm(projected-targets, axis=1))))

    def test_math_center_degeneracy_uses_deterministic_outward_axis(self):
        values = np.zeros((3, 3))
        result, report = sm.follow_world_vectors(
            values, (1.0, 1.0), dt=1 / 24, frequency=1.0, damping=0.5,
            air_friction=0.0, collision_sphere_center=(0.0, 0.0, 0.0),
            collision_sphere_radius=1.0)
        np.testing.assert_array_equal(result[1], (0.0, 0.0, 1.0))
        self.assertEqual(report["collision_samples"], 2)

    def test_math_outside_sphere_is_noop(self):
        values = np.tile((2.0, 0.0, 0.0), (4, 1))
        baseline, baseline_report = sm.follow_world_vectors(
            values, np.ones(3), dt=1 / 24, frequency=1.0, damping=0.5,
            air_friction=0.0)
        result, report = sm.follow_world_vectors(
            values, np.ones(3), dt=1 / 24, frequency=1.0, damping=0.5,
            air_friction=0.0, collision_sphere_center=(0.0, 0.0, 0.0),
            collision_sphere_radius=1.0)
        np.testing.assert_array_equal(result, baseline)
        self.assertEqual(report, baseline_report)

    def test_math_sphere_validation_and_collider_exclusivity(self):
        hostile = (((0.0, 0.0), 1.0), ((True, False, False), 1.0),
                   ((0.0, 0.0, float("nan")), 1.0), ((0.0, 0.0, 0.0), True),
                   ((0.0, 0.0, 0.0), 0.0), ((0.0, 0.0, 0.0), 1001.0))
        for center, radius in hostile:
            with self.subTest(center=center, radius=radius):
                with self.assertRaises(ValueError):
                    sm.validate_sphere_collider(center, radius)
        with self.assertRaisesRegex(ValueError, "provided together"):
            sm.follow_world_vectors(
                np.zeros((2, 3)), (1.0,), dt=1 / 24, frequency=1.0,
                damping=0.5, air_friction=0.0,
                collision_sphere_center=(0.0, 0.0, 0.0))
        with self.assertRaisesRegex(ValueError, "one planar or spherical"):
            sm.follow_world_vectors(
                np.zeros((2, 3)), (1.0,), dt=1 / 24, frequency=1.0,
                damping=0.5, air_friction=0.0,
                collision_point=(0.0, 0.0, 0.0),
                collision_normal=(0.0, 0.0, 1.0),
                collision_sphere_center=(0.0, 0.0, 0.0),
                collision_sphere_radius=1.0)

    def test_boneforge_and_rigify_sphere_collision_workflow(self):
        for label in ("boneforge", "rigify_default"):
            with self.subTest(rig=label):
                obj, source, control, collider, _ = sphere_fixture(label)
                state = obj.b4ml
                original = state.candidate_action
                token = flight._curve_token(obj, original)
                path = obj.pose.bones[control].path_from_id("location")
                before = curve_values(original, obj, path)
                report = secondary.solve(obj, bpy.context.scene)
                self.assertEqual(report["schema"], 9)
                self.assertEqual(report["backend"], "implicit_selected_control_secondary_v8")
                self.assertEqual(report["collision_shape"], "SPHERE")
                self.assertEqual(report["collision_surface"], "STATIC_SPHERE:" + collider.name)
                self.assertAlmostEqual(report["collision_sphere_radius"], 0.1, places=6)
                self.assertGreater(report["collision_samples"], 0)
                self.assertGreater(report["max_raw_penetration"], 0.0)
                self.assertEqual(report["max_penetration_before"], 0.0)
                self.assertLessEqual(report["max_desired_penetration_after"], 1e-8)
                self.assertLessEqual(report["max_penetration_after"], 1e-6)
                self.assertEqual(report["collision_penetration_tolerance"], 1e-6)
                self.assertLessEqual(report["max_world_location_error"], 2e-4)
                scene = bpy.context.scene
                for frame in range(1, 12):
                    scene.frame_set(frame)
                    actual = (w.display_world(obj) @ obj.pose.bones[control].matrix).translation
                    separation = ((actual-collider.matrix_world.translation).length
                                  - state.secondary_sphere_radius
                                  - state.secondary_collision_clearance)
                    self.assertGreaterEqual(separation, -1e-6)
                scene.frame_set(6)
                self.assertNotEqual(curve_values(state.candidate_action, obj, path), before)
                self.assertEqual(flight._curve_token(obj, original), token)
                secondary.restore(obj, bpy.context.scene)
                self.assertIs(state.candidate_action, original)
                w.finish_preview(obj, bpy.context.scene, False)
                self.assertIs(obj.animation_data.action, source)

    def test_priority_pose_inside_sphere_rejects_atomically(self):
        obj, _, control, collider, _ = sphere_fixture()
        state = obj.b4ml
        original = state.candidate_action
        token = flight._curve_token(obj, original)
        actions = set(bpy.data.actions.keys())
        matrix = w.display_world(obj) @ obj.pose.bones[control].matrix
        collider.location = matrix.translation
        bpy.context.view_layer.update()
        with self.assertRaisesRegex(ValueError, "priority pose"):
            secondary.solve(obj, bpy.context.scene)
        self.assertIs(state.candidate_action, original)
        self.assertEqual(flight._curve_token(obj, original), token)
        self.assertEqual(set(bpy.data.actions.keys()), actions)

    def test_sphere_collider_must_be_explicit_static_scene_object(self):
        obj, _, _, collider, _ = sphere_fixture()
        state = obj.b4ml
        state.secondary_sphere_collider = None
        with self.assertRaisesRegex(ValueError, "Choose"):
            secondary.solve(obj, bpy.context.scene)
        state.secondary_sphere_collider = obj
        with self.assertRaisesRegex(ValueError, "own sphere"):
            secondary.solve(obj, bpy.context.scene)
        state.secondary_sphere_collider = collider
        parent = make_sphere("B4ML Sphere Parent", (0.0, 0.0, 0.0))
        collider.parent = parent
        with self.assertRaisesRegex(ValueError, "unparented and static"):
            secondary.solve(obj, bpy.context.scene)

    def test_rigid_body_collider_rejects_atomically(self):
        obj, _, _, _, _ = sphere_fixture()
        state = obj.b4ml
        original = state.candidate_action
        token = flight._curve_token(obj, original)
        actions = set(bpy.data.actions.keys())
        bpy.ops.object.mode_set(mode="OBJECT")
        mesh = bpy.data.meshes.new("B4ML Rigid Sphere Mesh")
        mesh.from_pydata(((-0.1, -0.1, -0.1), (0.1, -0.1, -0.1),
                          (0.0, 0.1, -0.1), (0.0, 0.0, 0.1)), (),
                         ((0, 1, 2), (0, 3, 1), (1, 3, 2), (2, 3, 0)))
        collider = bpy.data.objects.new("B4ML Rigid Sphere", mesh)
        bpy.context.scene.collection.objects.link(collider)
        bpy.ops.object.select_all(action="DESELECT")
        collider.select_set(True)
        bpy.context.view_layer.objects.active = collider
        self.assertEqual(bpy.ops.rigidbody.object_add(), {"FINISHED"})
        state.secondary_sphere_collider = collider
        collider.select_set(False)
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode="POSE")
        with self.assertRaisesRegex(ValueError, "rigid-body"):
            secondary.solve(obj, bpy.context.scene)
        self.assertIs(state.candidate_action, original)
        self.assertEqual(flight._curve_token(obj, original), token)
        self.assertEqual(set(bpy.data.actions.keys()), actions)

    def test_frame_dependent_collider_motion_rejects_atomically(self):
        obj, _, _, collider, _ = sphere_fixture()
        state = obj.b4ml
        original = state.candidate_action
        token = flight._curve_token(obj, original)
        actions = set(bpy.data.actions.keys())
        initial = collider.location.copy()

        def move_with_frame(scene, *_):
            collider.location.x = initial.x + scene.frame_current * 0.01

        bpy.app.handlers.frame_change_post.append(move_with_frame)
        try:
            with self.assertRaisesRegex(ValueError, "surface changed"):
                secondary.solve(obj, bpy.context.scene)
        finally:
            bpy.app.handlers.frame_change_post.remove(move_with_frame)
            collider.location = initial
            bpy.context.scene.frame_set(6)
        self.assertIs(state.candidate_action, original)
        self.assertEqual(flight._curve_token(obj, original), token)
        self.assertEqual(set(bpy.data.actions.keys()), actions)

    def test_keyed_and_driven_radius_reject_atomically(self):
        for mode in ("KEYED", "DRIVEN"):
            with self.subTest(mode=mode):
                obj, _, _, _, _ = sphere_fixture()
                state = obj.b4ml
                original = state.candidate_action
                radius_path = state.path_from_id("secondary_sphere_radius")
                if mode == "KEYED":
                    self.assertTrue(state.keyframe_insert(
                        data_path="secondary_sphere_radius", frame=1.0))
                else:
                    driver = obj.driver_add(radius_path)
                    driver.driver.expression = "0.1"
                token = flight._curve_token(obj, original)
                actions = set(bpy.data.actions.keys())
                with self.assertRaisesRegex(ValueError, "radius must be static"):
                    secondary.solve(obj, bpy.context.scene)
                self.assertIs(state.candidate_action, original)
                self.assertEqual(flight._curve_token(obj, original), token)
                self.assertEqual(set(bpy.data.actions.keys()), actions)

    def test_collider_motion_cancels_cooperative_solve_and_restores_input(self):
        obj, _, _, collider, _ = sphere_fixture()
        state = obj.b4ml
        original = state.candidate_action
        token = flight._curve_token(obj, original)
        secondary.start(obj, bpy.context.scene)
        self.assertFalse(secondary.step(obj))
        collider.location.x += 0.25
        bpy.context.view_layer.update()
        with self.assertRaisesRegex(ValueError, "surface changed"):
            secondary.step(obj)
        self.assertFalse(state.secondary_running)
        self.assertIs(state.candidate_action, original)
        self.assertIs(obj.animation_data.action, original)
        self.assertEqual(flight._curve_token(obj, original), token)

    def test_request_binds_shape_object_radius_and_visible_properties(self):
        obj, _, _, collider, _ = sphere_fixture()
        raw = secondary.request(obj, bpy.context.scene)
        self.assertEqual(raw["collision_shape"], "SPHERE")
        self.assertEqual(raw["collision_sphere"], collider.name_full)
        self.assertAlmostEqual(raw["collision_sphere_radius"], 0.1, places=6)
        self.assertTrue(hasattr(obj.b4ml, "secondary_collision_shape"))
        self.assertTrue(hasattr(obj.b4ml, "secondary_sphere_collider"))
        self.assertTrue(hasattr(obj.b4ml, "secondary_sphere_radius"))

    def test_planar_collision_keeps_legacy_schema_and_backend(self):
        obj, _, _, _, _ = sphere_fixture()
        state = obj.b4ml
        state.secondary_collision_shape = "PLANE"
        state.secondary_sphere_collider = None
        state.support_plane_point = (0.0, 0.0, -100.0)
        state.support_plane_normal = (0.0, 0.0, 1.0)
        report = secondary.solve(obj, bpy.context.scene)
        self.assertEqual(report["schema"], 3)
        self.assertEqual(report["backend"], "implicit_selected_control_secondary_v2")
        self.assertEqual(report["collision_shape"], "PLANE")


if __name__ == "__main__":
    result = unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(SecondarySphereCollisionTests))
    print("B4ML_SECONDARY_SPHERE_RESULT:", "PASS" if result.wasSuccessful() else "FAIL")
    if not result.wasSuccessful():
        raise SystemExit(1)
