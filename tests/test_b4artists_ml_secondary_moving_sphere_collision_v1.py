"""Directly animated rigid spherical colliders for secondary motion."""
from pathlib import Path
import math
import os
import sys
import tempfile
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [os.environ.get("B4ML_PACKAGE", str(ROOT)), str(ROOT / "tests")]

import bpy
from mathutils import Vector
import b4artists_ml
from b4artists_ml import flight, secondary_math as sm, secondary_motion as secondary, workflow as w
from test_b4artists_ml_secondary_sphere_collision_v1 import make_sphere, sphere_fixture


def animate_center(collider, offsets=((-0.04, 0.0, 0.0),
                                      (0.0, 0.0, 0.0),
                                      (0.04, 0.0, 0.0))):
    base = collider.location.copy()
    for frame, offset in zip((1.0, 6.0, 11.0), offsets):
        collider.location = base + Vector(offset)
        collider.keyframe_insert(data_path="location", frame=frame)
    action = collider.animation_data.action
    for curve in w.action_curves(action, getattr(collider.animation_data, "action_slot", None)):
        for key in curve.keyframe_points:
            key.interpolation = "LINEAR"
    bpy.context.scene.frame_set(6)
    bpy.context.view_layer.update()
    return action


def animate_radius_scale(collider):
    for frame, value in ((1.0, 1.0), (3.0, 1.3), (6.0, 1.0),
                         (8.0, 1.3), (11.0, 1.0)):
        collider.scale = (value, value, value)
        collider.keyframe_insert(data_path="scale", frame=frame)
    action = collider.animation_data.action
    for curve in w.action_curves(action, getattr(collider.animation_data, "action_slot", None)):
        for key in curve.keyframe_points:
            key.interpolation = "LINEAR"
    bpy.context.scene.frame_set(6)
    bpy.context.view_layer.update()
    return action


def moving_fixture(label="boneforge"):
    obj, source, control, collider, positions = sphere_fixture(label)
    action = animate_center(collider)
    obj.b4ml.secondary_sphere_moving = True
    return obj, source, control, collider, action, positions


class SecondaryMovingSphereCollisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b4artists_ml.register()

    def test_math_sampled_centers_are_order_independent_and_use_relative_velocity(self):
        targets = np.zeros((5, 3), dtype=float)
        moving = np.asarray(((-2.0, 0.0, 0.0),
                             (-0.6, 0.0, 0.0),
                             (0.0, 0.0, 0.0),
                             (0.6, 0.0, 0.0),
                             (2.0, 0.0, 0.0)))
        upper = moving + np.asarray((0.0, 0.35, 0.0))
        trajectories = [(moving, 0.7), (upper, 0.45)]
        outputs = []
        for ordered in (trajectories, list(reversed(trajectories))):
            result, report = sm.follow_world_vectors(
                targets, np.ones(4), dt=0.25, frequency=0.05,
                damping=0.0, air_friction=0.0, restitution=0.5,
                surface_friction=0.25,
                collision_sphere_trajectories=ordered)
            outputs.append(result)
            self.assertGreater(report["collision_samples"], 0)
            self.assertGreater(report["max_raw_penetration"], 0.0)
            for centers, radius in trajectories:
                distances = np.linalg.norm(result-centers, axis=1)-radius
                self.assertTrue(np.all(distances[1:] >= -1e-8))
        np.testing.assert_array_equal(outputs[0], outputs[1])
        # The center moves 0.6 units during the third step. A relative-velocity
        # response must transfer some of that motion to the contacted point.
        self.assertGreater(outputs[0][3, 0], 0.0)

    def test_math_rejects_malformed_or_mixed_trajectory_inputs(self):
        target = np.zeros((3, 3))
        hostile = (
            [],
            [(np.zeros((2, 3)), 1.0)],
            [(np.zeros((3, 2)), 1.0)],
            [(np.full((3, 3), np.nan), 1.0)],
            [(np.zeros((3, 3)), 0.0)],
        )
        for trajectories in hostile:
            with self.subTest(shape=str(trajectories)[:40]):
                with self.assertRaises(ValueError):
                    sm.validate_sphere_trajectories(trajectories, 3)
        with self.assertRaisesRegex(ValueError, "one sphere input form"):
            sm.follow_world_vectors(
                target, (1.0, 1.0), dt=1 / 24, frequency=1.0,
                damping=0.5, air_friction=0.0,
                collision_sphere_center=(0.0, 0.0, 0.0),
                collision_sphere_radius=1.0,
                collision_sphere_trajectories=[(np.zeros((3, 3)), 1.0)])

    def test_math_sampled_radii_expand_and_transfer_surface_velocity(self):
        targets = np.repeat(np.asarray(((0.6, 0.0, 0.0),)), 5, axis=0)
        centers = np.zeros((5, 3), dtype=float)
        radii = np.asarray((0.5, 0.7, 0.9, 1.1, 1.3), dtype=float)
        result, report = sm.follow_world_vectors(
            targets, np.ones(4), dt=0.25, frequency=0.05,
            damping=0.0, air_friction=0.0, restitution=0.5,
            surface_friction=0.0,
            collision_sphere_trajectories=[(centers, radii)])
        self.assertGreater(report["collision_samples"], 0)
        self.assertGreater(report["max_raw_penetration"], 0.0)
        distances = np.linalg.norm(result[1:], axis=1)
        self.assertTrue(np.all(distances >= radii[1:]-1e-10))
        self.assertTrue(np.any(distances > radii[1:]+1e-3))
        self.assertGreater(result[-1, 0], targets[-1, 0])

    def test_math_rejects_malformed_sampled_radii(self):
        centers = np.zeros((3, 3), dtype=float)
        hostile = (
            np.ones(2),
            np.ones((3, 1)),
            np.asarray((1.0, np.nan, 1.0)),
            np.asarray((1.0, 0.0, 1.0)),
            np.asarray((1.0, 1001.0, 1.0)),
            np.asarray((True, True, True)),
        )
        for radii in hostile:
            with self.subTest(radii=repr(radii)):
                with self.assertRaises(ValueError):
                    sm.validate_sphere_trajectories([(centers, radii)], 3)

    def test_boneforge_and_rigify_follow_animated_center(self):
        for label in ("boneforge", "rigify_default"):
            with self.subTest(rig=label):
                obj, source, control, collider, collider_action, _ = moving_fixture(label)
                state = obj.b4ml
                original = state.candidate_action
                input_token = flight._curve_token(obj, original)
                collider_token = flight._curve_token(collider, collider_action)
                report = secondary.solve(obj, bpy.context.scene)
                self.assertEqual(report["schema"], 11)
                self.assertEqual(report["backend"], "implicit_selected_control_secondary_v10")
                self.assertEqual(report["collision_surface"], "MOVING_SPHERE:" + collider.name)
                self.assertEqual(report["moving_collision_spheres"], 1)
                self.assertEqual(report["collision_target_space"],
                                 "evaluated direct object location")
                self.assertTrue(report["relative_velocity_response"])
                self.assertTrue(report["collision_spheres"][0]["moving"])
                self.assertGreater(report["collision_samples"], 0)
                self.assertLessEqual(report["max_desired_penetration_after"], 1e-8)
                self.assertLessEqual(report["max_penetration_after"], 1e-6)
                scene = bpy.context.scene
                for frame in range(1, 12):
                    scene.frame_set(frame)
                    actual = (w.display_world(obj) @ obj.pose.bones[control].matrix).translation
                    separation = ((actual-collider.matrix_world.translation).length
                                  - state.secondary_sphere_radius
                                  - state.secondary_collision_clearance)
                    self.assertGreaterEqual(separation, -1e-6)
                self.assertEqual(flight._curve_token(obj, original), input_token)
                self.assertEqual(flight._curve_token(collider, collider_action), collider_token)
                secondary.restore(obj, scene)
                w.finish_preview(obj, scene, False)
                self.assertIs(obj.animation_data.action, source)

    def test_boneforge_follows_uniform_radius_scale_animation(self):
        obj, source, control, collider, _ = sphere_fixture("boneforge")
        collider_action = animate_radius_scale(collider)
        state = obj.b4ml
        state.secondary_sphere_scaling = True
        source_token = flight._curve_token(obj, state.candidate_action)
        collider_token = flight._curve_token(collider, collider_action)
        report = secondary.solve(obj, bpy.context.scene)
        self.assertEqual(report["schema"], 12)
        self.assertEqual(report["backend"], "implicit_selected_control_secondary_v11")
        self.assertEqual(report["scaling_collision_spheres"], 1)
        self.assertEqual(report["moving_collision_spheres"], 0)
        self.assertTrue(report["relative_radius_velocity_response"])
        self.assertEqual(report["collision_target_space"],
                         "evaluated direct object location and uniform scale")
        self.assertLessEqual(report["max_penetration_after"], 1e-6)
        self.assertEqual(flight._curve_token(obj, state.secondary_input), source_token)
        self.assertEqual(flight._curve_token(collider, collider_action), collider_token)

    def test_collection_add_undo_redo_preserves_motion_mode(self):
        obj, _, _, collider, action, _ = moving_fixture()
        state = obj.b4ml
        bpy.context.preferences.edit.use_global_undo = True
        obj_name, collider_name, action_name = obj.name, collider.name, action.name
        bpy.ops.ed.undo_push(message="Before moving sphere add")
        self.assertEqual(bpy.ops.b4ml.secondary_sphere(operation="ADD"), {"FINISHED"})
        bpy.ops.ed.undo_push(message="Moving sphere add complete")
        self.assertEqual(len(state.secondary_spheres), 1)
        self.assertTrue(state.secondary_spheres[0].moving)
        self.assertEqual(bpy.ops.ed.undo(), {"FINISHED"})
        obj = bpy.data.objects[obj_name]
        self.assertEqual(len(obj.b4ml.secondary_spheres), 0)
        self.assertEqual(bpy.ops.ed.redo(), {"FINISHED"})
        obj = bpy.data.objects[obj_name]
        collider = bpy.data.objects[collider_name]
        self.assertEqual(len(obj.b4ml.secondary_spheres), 1)
        self.assertTrue(obj.b4ml.secondary_spheres[0].moving)
        self.assertIs(obj.b4ml.secondary_spheres[0].collider, collider)
        self.assertEqual(collider.animation_data.action.name, action_name)

    def test_mixed_static_and_moving_set_uses_sampled_schema(self):
        obj, _, _, moving, _, _ = moving_fixture()
        state = obj.b4ml
        secondary.add_sphere_collider(obj, bpy.context.scene)
        static = make_sphere("B4ML Far Static Sphere",
                             moving.matrix_world.translation + Vector((5.0, 0.0, 0.0)))
        state.secondary_sphere_collider = static
        state.secondary_sphere_radius = 0.25
        state.secondary_sphere_moving = False
        secondary.add_sphere_collider(obj, bpy.context.scene)
        report = secondary.solve(obj, bpy.context.scene)
        self.assertEqual(report["schema"], 11)
        self.assertEqual(report["collision_sphere_count"], 2)
        self.assertEqual(report["moving_collision_spheres"], 1)
        self.assertEqual(report["collision_surface"],
                         "SPHERES:MOVING:" + moving.name + "|STATIC:" + static.name)
        self.assertEqual([row.get("moving", False)
                          for row in report["collision_spheres"]], [True, False])
        self.assertLessEqual(report["max_penetration_after"], 1e-6)

    def test_hostile_moving_center_animation_rejects_atomically(self):
        cases = ("MISSING", "PARTIAL", "MODIFIER", "SCALE", "DRIVER")
        for case in cases:
            with self.subTest(case=case):
                obj, _, _, collider, _ = sphere_fixture()
                state = obj.b4ml
                state.secondary_sphere_moving = True
                if case != "MISSING":
                    action = animate_center(collider)
                    curves = list(w.action_curves(
                        action, getattr(collider.animation_data, "action_slot", None)))
                    if case == "PARTIAL":
                        collider.animation_data_clear()
                        collider.keyframe_insert(data_path="location", index=0, frame=1.0)
                    elif case == "MODIFIER":
                        curves[0].modifiers.new("NOISE")
                    elif case == "SCALE":
                        collider.keyframe_insert(data_path="scale", frame=1.0)
                    elif case == "DRIVER":
                        collider.driver_add("rotation_euler", 0).driver.expression = "0"
                original = state.candidate_action
                token = flight._curve_token(obj, original)
                actions = set(bpy.data.actions.keys())
                with self.assertRaises(ValueError):
                    secondary.solve(obj, bpy.context.scene)
                self.assertIs(state.candidate_action, original)
                self.assertEqual(flight._curve_token(obj, original), token)
                self.assertEqual(set(bpy.data.actions.keys()), actions)

    def test_hostile_radius_scale_animation_rejects_atomically(self):
        cases = ("MISSING", "PARTIAL", "MUTED", "NONUNIFORM", "NEGATIVE",
                 "MODIFIER", "DRIVER", "NLA")
        for case in cases:
            with self.subTest(case=case):
                obj, _, _, collider, _ = sphere_fixture()
                state = obj.b4ml
                state.secondary_sphere_scaling = True
                if case != "MISSING":
                    if case == "PARTIAL":
                        collider.scale = (1.0, 1.0, 1.0)
                        collider.keyframe_insert(data_path="scale", index=0, frame=1.0)
                    else:
                        action = animate_radius_scale(collider)
                        curves = [curve for curve in w.action_curves(
                            action, getattr(collider.animation_data, "action_slot", None))
                            if curve.data_path == "scale"]
                        if case == "MUTED":
                            curves[0].mute = True
                        elif case == "NONUNIFORM":
                            collider.scale = (1.3, 1.1, 1.3)
                            collider.keyframe_insert(data_path="scale", frame=3.0)
                        elif case == "NEGATIVE":
                            collider.scale = (-1.0, -1.0, -1.0)
                            collider.keyframe_insert(data_path="scale", frame=3.0)
                        elif case == "MODIFIER":
                            curves[0].modifiers.new("NOISE")
                        elif case == "DRIVER":
                            collider.driver_add("rotation_euler", 0).driver.expression = "0"
                        elif case == "NLA":
                            collider.animation_data.nla_tracks.new()
                original = state.candidate_action
                token = flight._curve_token(obj, original)
                actions = set(bpy.data.actions.keys())
                with self.assertRaises(ValueError):
                    secondary.solve(obj, bpy.context.scene)
                self.assertIs(state.candidate_action, original)
                self.assertEqual(flight._curve_token(obj, original), token)
                self.assertEqual(set(bpy.data.actions.keys()), actions)

    def test_radius_scale_post_sampling_change_fails_closed(self):
        obj, _, _, collider, _ = sphere_fixture()
        action = animate_radius_scale(collider)
        state = obj.b4ml
        state.secondary_sphere_scaling = True
        original = state.candidate_action
        token = flight._curve_token(obj, original)
        action_inventory = set(bpy.data.actions.keys())
        secondary.start(obj, bpy.context.scene)
        sampled = 0
        for _ in range(128):
            self.assertFalse(secondary.step(obj))
            if state.secondary_progress == "Sampling evaluated world controls":
                sampled += 1
                if sampled == 11:
                    break
        self.assertEqual(sampled, 11)
        curve = next(curve for curve in w.action_curves(
            action, getattr(collider.animation_data, "action_slot", None))
            if curve.data_path == "scale" and curve.array_index == 1)
        curve.keyframe_points[1].co.y += 0.05
        with self.assertRaisesRegex(ValueError, "surface changed"):
            for _ in range(512):
                if secondary.step(obj):
                    self.fail("Changed radius animation unexpectedly completed")
        self.assertFalse(state.secondary_running)
        self.assertIs(state.candidate_action, original)
        self.assertIs(obj.animation_data.action, original)
        self.assertEqual(flight._curve_token(obj, original), token)
        self.assertEqual(set(bpy.data.actions.keys()), action_inventory)

    def test_priority_conflict_and_mid_solve_action_mutation_restore_input(self):
        obj, _, control, collider, _, _ = moving_fixture()
        state = obj.b4ml
        original = state.candidate_action
        token = flight._curve_token(obj, original)
        bpy.context.scene.frame_set(6)
        priority = (w.display_world(obj) @ obj.pose.bones[control].matrix).translation
        collider.location = priority
        collider.keyframe_insert(data_path="location", frame=6.0)
        with self.assertRaisesRegex(ValueError, "priority pose"):
            secondary.solve(obj, bpy.context.scene)
        self.assertIs(state.candidate_action, original)
        self.assertEqual(flight._curve_token(obj, original), token)

        obj, _, _, collider, action, _ = moving_fixture()
        state = obj.b4ml
        original = state.candidate_action
        token = flight._curve_token(obj, original)
        secondary.start(obj, bpy.context.scene)
        self.assertFalse(secondary.step(obj))
        curve = next(curve for curve in w.action_curves(
            action, getattr(collider.animation_data, "action_slot", None))
            if curve.data_path == "location" and curve.array_index == 1)
        curve.keyframe_points[0].co.y += 0.02
        with self.assertRaisesRegex(ValueError, "surface changed"):
            secondary.step(obj)
        self.assertFalse(state.secondary_running)
        self.assertIs(state.candidate_action, original)
        self.assertIs(obj.animation_data.action, original)
        self.assertEqual(flight._curve_token(obj, original), token)

    def test_post_sampling_evaluation_state_changes_fail_closed(self):
        for case in ("INFLUENCE", "DELTA_LOCATION", "LAYER", "LIVE_CENTER"):
            with self.subTest(case=case):
                obj, _, _, collider, action, _ = moving_fixture()
                state = obj.b4ml
                original = state.candidate_action
                input_token = flight._curve_token(obj, original)
                action_inventory = set(bpy.data.actions.keys())
                secondary.start(obj, bpy.context.scene)
                sampled = 0
                for _ in range(128):
                    self.assertFalse(secondary.step(obj))
                    if state.secondary_progress == "Sampling evaluated world controls":
                        sampled += 1
                        if sampled == 11:
                            break
                self.assertEqual(sampled, 11)
                handler = None
                if case == "INFLUENCE":
                    collider.animation_data.action_influence = 0.5
                elif case == "DELTA_LOCATION":
                    collider.delta_location.x += 0.25
                elif case == "LAYER":
                    layer = action.layers[0]
                    if hasattr(layer, "influence"):
                        layer.influence = 0.5
                    elif hasattr(layer, "mute"):
                        layer.mute = True
                    else:
                        layer.name = "Changed After Sampling"
                else:
                    def handler(_scene, _depsgraph=None):
                        matrix = collider.matrix_world.copy()
                        matrix.translation.x += 0.25
                        collider.matrix_world = matrix
                    bpy.app.handlers.frame_change_post.append(handler)
                try:
                    with self.assertRaisesRegex(ValueError, "surface changed"):
                        for _ in range(512):
                            if secondary.step(obj):
                                self.fail("Changed moving collider unexpectedly completed")
                        self.fail("Changed moving collider did not terminate")
                finally:
                    if handler in bpy.app.handlers.frame_change_post:
                        bpy.app.handlers.frame_change_post.remove(handler)
                self.assertFalse(state.secondary_running)
                self.assertIs(state.candidate_action, original)
                self.assertIs(obj.animation_data.action, original)
                self.assertEqual(flight._curve_token(obj, original), input_token)
                self.assertEqual(set(bpy.data.actions.keys()), action_inventory)

    def test_moving_mode_and_center_action_survive_save_reload(self):
        obj, _, _, collider, action, _ = moving_fixture("rigify_default")
        state = obj.b4ml
        secondary.add_sphere_collider(obj, bpy.context.scene)
        obj_name, collider_name, action_name = obj.name, collider.name, action.name
        with tempfile.TemporaryDirectory(prefix="b4ml-moving-sphere-") as directory:
            path = str(Path(directory) / "moving-sphere.blend")
            self.assertEqual(
                bpy.ops.wm.save_as_mainfile(filepath=path, check_existing=False),
                {"FINISHED"})
            self.assertEqual(
                bpy.ops.wm.open_mainfile(filepath=path, load_ui=False, use_scripts=False),
                {"FINISHED"})
        obj = bpy.data.objects[obj_name]
        collider = bpy.data.objects[collider_name]
        self.assertEqual(len(obj.b4ml.secondary_spheres), 1)
        self.assertTrue(obj.b4ml.secondary_spheres[0].moving)
        self.assertIs(obj.b4ml.secondary_spheres[0].collider, collider)
        self.assertEqual(collider.animation_data.action.name, action_name)

    def test_radius_scale_mode_add_undo_redo_and_save_reload(self):
        obj, _, _, collider, _ = sphere_fixture("boneforge")
        action = animate_radius_scale(collider)
        state = obj.b4ml
        state.secondary_sphere_scaling = True
        bpy.context.preferences.edit.use_global_undo = True
        obj_name, collider_name, action_name = obj.name, collider.name, action.name
        bpy.ops.ed.undo_push(message="Before scaled sphere add")
        self.assertEqual(bpy.ops.b4ml.secondary_sphere(operation="ADD"), {"FINISHED"})
        bpy.ops.ed.undo_push(message="Scaled sphere add complete")
        self.assertTrue(state.secondary_spheres[0].scaling)
        self.assertEqual(bpy.ops.ed.undo(), {"FINISHED"})
        self.assertEqual(len(bpy.data.objects[obj_name].b4ml.secondary_spheres), 0)
        self.assertEqual(bpy.ops.ed.redo(), {"FINISHED"})
        obj = bpy.data.objects[obj_name]
        self.assertTrue(obj.b4ml.secondary_spheres[0].scaling)
        with tempfile.TemporaryDirectory(prefix="b4ml-scaled-sphere-") as directory:
            path = str(Path(directory) / "scaled-sphere.blend")
            self.assertEqual(bpy.ops.wm.save_as_mainfile(
                filepath=path, check_existing=False), {"FINISHED"})
            self.assertEqual(bpy.ops.wm.open_mainfile(
                filepath=path, load_ui=False, use_scripts=False), {"FINISHED"})
        obj = bpy.data.objects[obj_name]
        collider = bpy.data.objects[collider_name]
        self.assertEqual(len(obj.b4ml.secondary_spheres), 1)
        self.assertTrue(obj.b4ml.secondary_spheres[0].scaling)
        self.assertIs(obj.b4ml.secondary_spheres[0].collider, collider)
        self.assertEqual(collider.animation_data.action.name, action_name)


if __name__ == "__main__":
    result = unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(
            SecondaryMovingSphereCollisionTests))
    print("B4ML_SECONDARY_MOVING_SPHERE_RESULT:",
          "PASS" if result.wasSuccessful() else "FAIL")
    if not result.wasSuccessful():
        raise SystemExit(1)
