"""Bounded sets of static spherical colliders for secondary motion."""
from pathlib import Path
import json
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


def multi_sphere_fixture(label="boneforge"):
    obj, source, control, first, positions = sphere_fixture(label)
    state = obj.b4ml
    secondary.add_sphere_collider(obj, bpy.context.scene)
    second = make_sphere("B4ML Sphere B " + label,
                         first.matrix_world.translation + Vector((0.06, 0.0, 0.0)))
    state.secondary_sphere_collider = second
    state.secondary_sphere_radius = 0.1
    secondary.add_sphere_collider(obj, bpy.context.scene)
    return obj, source, control, first, second, positions


class SecondaryMultiSphereCollisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b4artists_ml.register()

    def test_math_overlapping_spheres_are_order_independent_and_excluded(self):
        targets = np.zeros((3, 3), dtype=float)
        spheres = [((-0.4, 0.0, 0.0), 1.0), ((0.4, 0.0, 0.0), 1.0)]
        outputs = []
        for ordered in (spheres, list(reversed(spheres))):
            result, report = sm.apply_world_vector_follow(
                targets, (1.0, 2.0, 3.0), dt=1 / 24, frequency=1.0,
                damping=0.5, air_friction=0.0, strength=0.0,
                blend_frames=0.0, collision_spheres=ordered,
                envelope=np.zeros(3))
            outputs.append(result)
            self.assertGreater(report["collision_samples"], 0)
            self.assertGreater(report["max_raw_penetration"], 0.0)
            self.assertAlmostEqual(report["max_penetration_after"], 0.6)
            for center, radius in spheres:
                separation = np.linalg.norm(result-np.asarray(center), axis=1)-radius
                self.assertTrue(np.all(separation <= 0.0))
            np.testing.assert_array_equal(result, targets)
        np.testing.assert_array_equal(outputs[0], outputs[1])

    def test_math_validation_exclusivity_and_empty_mask(self):
        valid = [((float(index) * 3.0, 0.0, 0.0), 1.0)
                 for index in range(sm.MAX_SPHERE_COLLIDERS)]
        hostile = ([], valid + [((99.0, 0.0, 0.0), 1.0)],
                   [((0.0, 0.0), 1.0)], [((0.0, 0.0, 0.0), 0.0)],
                   [{"center": (0.0, 0.0, 0.0), "radius": 1.0}])
        for colliders in hostile:
            with self.subTest(colliders=colliders):
                with self.assertRaises(ValueError):
                    sm.validate_sphere_colliders(colliders)
        with self.assertRaisesRegex(ValueError, "one sphere input form"):
            sm.follow_world_vectors(
                np.zeros((2, 3)), (1.0,), dt=1 / 24, frequency=1.0,
                damping=0.5, air_friction=0.0,
                collision_sphere_center=(0.0, 0.0, 0.0),
                collision_sphere_radius=1.0, collision_spheres=valid)
        targets = np.asarray(((0.0, 0.0, 0.0),
                              (0.1, 0.0, 0.0),
                              (0.2, 0.0, 0.0)))
        result, report = sm.apply_world_vector_follow(
            targets, (1.0, 2.0, 3.0), dt=1 / 24, frequency=1.0,
            damping=0.5, air_friction=0.0, strength=0.0,
            blend_frames=0.0, collision_spheres=valid[:2],
            collision_mask=(False, False, False), envelope=np.zeros(3))
        np.testing.assert_array_equal(result, targets)
        self.assertEqual(report["max_penetration_before"], 0.0)
        self.assertEqual(report["max_penetration_after"], 0.0)

    def test_collection_operator_add_duplicate_remove_and_clear(self):
        obj, _, _, first, _ = sphere_fixture()
        state = obj.b4ml
        bpy.context.preferences.edit.use_global_undo = True
        obj_name = obj.name
        first_name = first.name
        bpy.ops.ed.undo_push(message="Before sphere-set add")
        self.assertEqual(bpy.ops.b4ml.secondary_sphere(operation="ADD"), {"FINISHED"})
        bpy.ops.ed.undo_push(message="Sphere-set add complete")
        self.assertEqual(len(state.secondary_spheres), 1)
        self.assertIs(state.secondary_spheres[0].collider, first)
        self.assertAlmostEqual(state.secondary_spheres[0].radius, 0.1)
        self.assertEqual(bpy.ops.ed.undo(), {"FINISHED"})
        obj = bpy.data.objects[obj_name]
        state = obj.b4ml
        self.assertEqual(len(state.secondary_spheres), 0)
        self.assertEqual(bpy.ops.ed.redo(), {"FINISHED"})
        obj = bpy.data.objects[obj_name]
        state = obj.b4ml
        first = bpy.data.objects[first_name]
        self.assertEqual(len(state.secondary_spheres), 1)
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        if obj.mode != "POSE":
            bpy.ops.object.mode_set(mode="POSE")
        with self.assertRaisesRegex(RuntimeError, "already in the set"):
            bpy.ops.b4ml.secondary_sphere(operation="ADD")
        self.assertEqual(len(state.secondary_spheres), 1)
        second = make_sphere("B4ML Operator Sphere B", first.location + Vector((0.5, 0.0, 0.0)))
        state.secondary_sphere_collider = second
        state.secondary_sphere_radius = 0.2
        self.assertEqual(bpy.ops.b4ml.secondary_sphere(operation="ADD"), {"FINISHED"})
        self.assertEqual(len(state.secondary_spheres), 2)
        self.assertEqual(bpy.ops.b4ml.secondary_sphere(operation="REMOVE", index=0), {"FINISHED"})
        self.assertEqual(len(state.secondary_spheres), 1)
        self.assertIs(state.secondary_spheres[0].collider, second)
        self.assertEqual(bpy.ops.b4ml.secondary_sphere(operation="CLEAR"), {"FINISHED"})
        self.assertEqual(len(state.secondary_spheres), 0)

    def test_boneforge_and_rigify_multiple_sphere_workflow(self):
        for label in ("boneforge", "rigify_default"):
            with self.subTest(rig=label):
                obj, source, control, first, second, _ = multi_sphere_fixture(label)
                state = obj.b4ml
                original = state.candidate_action
                input_token = flight._curve_token(obj, original)
                report = secondary.solve(obj, bpy.context.scene)
                self.assertEqual(report["schema"], 10)
                self.assertEqual(report["backend"], "implicit_selected_control_secondary_v9")
                self.assertEqual(report["collision_shape"], "SPHERE")
                self.assertEqual(report["collision_sphere_count"], 2)
                self.assertEqual(
                    report["collision_surface"],
                    "STATIC_SPHERES:" + first.name + "|" + second.name)
                self.assertEqual(
                    [item["collider"] for item in report["collision_spheres"]],
                    [first.name_full, second.name_full])
                for item in report["collision_spheres"]:
                    self.assertAlmostEqual(item["radius"], 0.1, places=6)
                self.assertIsNone(report["collision_sphere_radius"])
                self.assertGreater(report["collision_samples"], 0)
                self.assertGreater(report["max_raw_penetration"], 0.0)
                self.assertLessEqual(report["max_desired_penetration_after"], 1e-8)
                self.assertLessEqual(report["max_penetration_after"], 1e-6)
                self.assertLessEqual(report["max_world_location_error"], 2e-4)
                scene = bpy.context.scene
                for frame in range(1, 12):
                    scene.frame_set(frame)
                    actual = (w.display_world(obj) @ obj.pose.bones[control].matrix).translation
                    for item in state.secondary_spheres:
                        separation = ((actual-item.collider.matrix_world.translation).length
                                      - item.radius-state.secondary_collision_clearance)
                        self.assertGreaterEqual(separation, -1e-6)
                self.assertEqual(flight._curve_token(obj, original), input_token)
                self.assertIsNot(state.candidate_action, original)
                secondary.restore(obj, scene)
                self.assertIs(state.candidate_action, original)
                w.finish_preview(obj, scene, False)
                self.assertIs(obj.animation_data.action, source)

    def test_second_sphere_priority_conflict_rejects_atomically(self):
        obj, _, control, _, second, _ = multi_sphere_fixture()
        state = obj.b4ml
        original = state.candidate_action
        token = flight._curve_token(obj, original)
        actions = set(bpy.data.actions.keys())
        priority = w.display_world(obj) @ obj.pose.bones[control].matrix
        second.location = priority.translation
        bpy.context.view_layer.update()
        with self.assertRaisesRegex(ValueError, "priority pose"):
            secondary.solve(obj, bpy.context.scene)
        self.assertIs(state.candidate_action, original)
        self.assertEqual(flight._curve_token(obj, original), token)
        self.assertEqual(set(bpy.data.actions.keys()), actions)

    def test_second_sphere_mutation_cancels_and_restores(self):
        obj, _, _, _, second, _ = multi_sphere_fixture()
        state = obj.b4ml
        original = state.candidate_action
        token = flight._curve_token(obj, original)
        secondary.start(obj, bpy.context.scene)
        self.assertFalse(secondary.step(obj))
        second.location.x += 0.25
        bpy.context.view_layer.update()
        with self.assertRaisesRegex(ValueError, "surface changed"):
            secondary.step(obj)
        self.assertFalse(state.secondary_running)
        self.assertIs(state.candidate_action, original)
        self.assertIs(obj.animation_data.action, original)
        self.assertEqual(flight._curve_token(obj, original), token)

    def test_collection_radius_keys_and_drivers_reject_atomically(self):
        for mode in ("KEYED", "DRIVEN"):
            with self.subTest(mode=mode):
                obj, _, _, _, _, _ = multi_sphere_fixture()
                state = obj.b4ml
                item = state.secondary_spheres[1]
                if mode == "KEYED":
                    self.assertTrue(item.keyframe_insert(data_path="radius", frame=1.0))
                else:
                    driver = obj.driver_add(item.path_from_id("radius"))
                    driver.driver.expression = "0.1"
                original = state.candidate_action
                token = flight._curve_token(obj, original)
                actions = set(bpy.data.actions.keys())
                with self.assertRaisesRegex(ValueError, "radius must be static"):
                    secondary.solve(obj, bpy.context.scene)
                self.assertIs(state.candidate_action, original)
                self.assertEqual(flight._curve_token(obj, original), token)
                self.assertEqual(set(bpy.data.actions.keys()), actions)

    def test_sphere_set_survives_save_and_reload(self):
        obj, _, _, first, second, _ = multi_sphere_fixture()
        obj_name = obj.name
        expected = [(first.name, 0.1), (second.name, 0.1)]
        with tempfile.TemporaryDirectory(prefix="b4ml-multi-sphere-") as directory:
            path = str(Path(directory) / "sphere-set.blend")
            self.assertEqual(
                bpy.ops.wm.save_as_mainfile(filepath=path, check_existing=False),
                {"FINISHED"})
            self.assertEqual(
                bpy.ops.wm.open_mainfile(filepath=path, load_ui=False, use_scripts=False),
                {"FINISHED"})
        obj = bpy.data.objects[obj_name]
        bpy.context.view_layer.objects.active = obj
        actual = [(item.collider.name, float(item.radius))
                  for item in obj.b4ml.secondary_spheres]
        self.assertEqual([row[0] for row in actual], [row[0] for row in expected])
        for (_, radius), (_, expected_radius) in zip(actual, expected):
            self.assertAlmostEqual(radius, expected_radius, places=6)


if __name__ == "__main__":
    result = unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(
            SecondaryMultiSphereCollisionTests))
    print("B4ML_SECONDARY_MULTI_SPHERE_RESULT:",
          "PASS" if result.wasSuccessful() else "FAIL")
    if not result.wasSuccessful():
        raise SystemExit(1)
