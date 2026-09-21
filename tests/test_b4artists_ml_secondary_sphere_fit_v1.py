"""Explicit sphere-radius fitting from collider bounds."""
from itertools import product
from pathlib import Path
import math
import os
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [os.environ.get("B4ML_PACKAGE", str(ROOT)), str(ROOT / "tests")]

import bpy
from mathutils import Vector
import b4artists_ml
from b4artists_ml import secondary_motion as secondary
from test_b4artists_ml_secondary_sphere_collision_v1 import sphere_fixture
from test_b4artists_ml_secondary_moving_sphere_collision_v1 import animate_radius_scale


def make_box(name, center, half_extents=(0.1, 0.2, 0.3)):
    mesh = bpy.data.meshes.new(name + " Mesh")
    mesh.from_pydata([
        (sx * half_extents[0], sy * half_extents[1], sz * half_extents[2])
        for sx, sy, sz in product((-1.0, 1.0), repeat=3)
    ], [], [])
    mesh.update()
    collider = bpy.data.objects.new(name, mesh)
    collider.location = center
    bpy.context.scene.collection.objects.link(collider)
    bpy.context.view_layer.update()
    return collider


class SecondarySphereFitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b4artists_ml.register()

    def test_staged_fit_snapshots_enclosing_world_radius(self):
        obj, _, _, old, _ = sphere_fixture()
        collider = make_box("B4ML Fit World", old.location, (0.1, 0.2, 0.3))
        collider.scale = (2.0, 0.5, 1.5)
        collider.rotation_euler = (0.3, -0.4, 0.2)
        bpy.context.view_layer.update()
        state = obj.b4ml
        state.secondary_sphere_collider = collider
        state.secondary_sphere_radius = 0.01
        expected = max((collider.matrix_world.to_3x3() @ Vector(corner)).length
                       for corner in collider.bound_box)
        report = secondary.fit_sphere_collider_radius(obj, bpy.context.scene)
        self.assertEqual(report["basis"], "WORLD")
        self.assertEqual(report["collider"], collider.name_full)
        self.assertAlmostEqual(report["radius"], expected, places=6)
        self.assertAlmostEqual(state.secondary_sphere_radius, expected, places=6)
        self.assertEqual(report["radius"], state.secondary_sphere_radius)
        self.assertTrue(all(
            (collider.matrix_world.to_3x3() @ Vector(corner)).length
            <= state.secondary_sphere_radius for corner in collider.bound_box))

    def test_scaling_fit_stores_local_base_radius(self):
        obj, _, _, old, _ = sphere_fixture()
        collider = make_box("B4ML Fit Scaling", old.location, (0.1, 0.2, 0.3))
        animate_radius_scale(collider)
        bpy.context.scene.frame_set(3)
        bpy.context.view_layer.update()
        state = obj.b4ml
        state.secondary_sphere_collider = collider
        state.secondary_sphere_scaling = True
        expected = math.sqrt(0.1 ** 2 + 0.2 ** 2 + 0.3 ** 2)
        report = secondary.fit_sphere_collider_radius(obj, bpy.context.scene)
        self.assertEqual(report["basis"], "LOCAL")
        self.assertAlmostEqual(state.secondary_sphere_radius, expected, places=6)
        scale = sum(collider.matrix_world.to_scale()) / 3.0
        self.assertAlmostEqual(state.secondary_sphere_radius * scale,
                               expected * 1.3, places=6)
        self.assertEqual(report["radius"], state.secondary_sphere_radius)
        self.assertTrue(all(
            (collider.matrix_world.to_3x3() @ Vector(corner)).length
            <= state.secondary_sphere_radius * scale
            for corner in collider.bound_box))

    def test_list_fit_changes_only_chosen_row(self):
        obj, _, _, old, _ = sphere_fixture()
        first = make_box("B4ML Fit Row A", old.location, (0.1, 0.2, 0.3))
        second = make_box("B4ML Fit Row B", old.location + Vector((2.0, 0.0, 0.0)),
                          (0.4, 0.1, 0.2))
        state = obj.b4ml
        state.secondary_sphere_collider = first
        state.secondary_sphere_radius = 0.05
        secondary.add_sphere_collider(obj, bpy.context.scene)
        state.secondary_sphere_collider = second
        state.secondary_sphere_radius = 0.07
        secondary.add_sphere_collider(obj, bpy.context.scene)
        staged = state.secondary_sphere_radius
        other = state.secondary_spheres[0].radius
        report = secondary.fit_sphere_collider_radius(obj, bpy.context.scene, 1)
        self.assertAlmostEqual(report["radius"], math.sqrt(0.21), places=6)
        self.assertAlmostEqual(state.secondary_spheres[1].radius,
                               math.sqrt(0.21), places=6)
        self.assertEqual(report["radius"], state.secondary_spheres[1].radius)
        self.assertTrue(all(
            (second.matrix_world.to_3x3() @ Vector(corner)).length
            <= state.secondary_spheres[1].radius for corner in second.bound_box))
        self.assertEqual(state.secondary_spheres[0].radius, other)
        self.assertEqual(state.secondary_sphere_radius, staged)

    def test_fit_operator_supports_native_undo_redo(self):
        obj, _, _, old, _ = sphere_fixture()
        collider = make_box("B4ML Fit Undo", old.location, (0.2, 0.3, 0.4))
        state = obj.b4ml
        state.secondary_sphere_collider = collider
        state.secondary_sphere_radius = 0.05
        obj_name = obj.name
        expected = math.sqrt(0.29)
        bpy.context.preferences.edit.use_global_undo = True
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        if obj.mode != "POSE":
            bpy.ops.object.mode_set(mode="POSE")
        bpy.ops.ed.undo_push(message="Before sphere radius fit")
        self.assertEqual(
            bpy.ops.b4ml.secondary_sphere(operation="FIT", index=-1), {"FINISHED"})
        bpy.ops.ed.undo_push(message="Sphere radius fit complete")
        self.assertAlmostEqual(state.secondary_sphere_radius, expected, places=6)
        self.assertEqual(bpy.ops.ed.undo(), {"FINISHED"})
        obj = bpy.data.objects[obj_name]
        self.assertAlmostEqual(obj.b4ml.secondary_sphere_radius, 0.05, places=6)
        self.assertEqual(bpy.ops.ed.redo(), {"FINISHED"})
        obj = bpy.data.objects[obj_name]
        self.assertAlmostEqual(obj.b4ml.secondary_sphere_radius, expected, places=6)

    def test_fit_rejects_missing_bounds_index_and_busy_state_atomically(self):
        obj, _, _, empty, _ = sphere_fixture()
        state = obj.b4ml
        original = state.secondary_sphere_radius
        with self.assertRaisesRegex(ValueError, "geometric bounds"):
            secondary.fit_sphere_collider_radius(obj, bpy.context.scene)
        with self.assertRaisesRegex(ValueError, "staged sphere"):
            secondary.fit_sphere_collider_radius(obj, bpy.context.scene, 0)
        empty_mesh = bpy.data.objects.new(
            "B4ML Fit Empty Mesh", bpy.data.meshes.new("B4ML Fit Empty Mesh Data"))
        empty_mesh.location = empty.location
        bpy.context.scene.collection.objects.link(empty_mesh)
        bpy.context.view_layer.update()
        state.secondary_sphere_collider = empty_mesh
        with self.assertRaisesRegex(ValueError, "no available geometric bounds"):
            secondary.fit_sphere_collider_radius(obj, bpy.context.scene)
        zero = make_box("B4ML Fit Zero", empty.location, (0.0, 0.0, 0.0))
        state.secondary_sphere_collider = zero
        with self.assertRaisesRegex(ValueError, "bounds|radius"):
            secondary.fit_sphere_collider_radius(obj, bpy.context.scene)
        state.secondary_running = True
        with self.assertRaisesRegex(ValueError, "active animation workflow"):
            secondary.fit_sphere_collider_radius(obj, bpy.context.scene)
        state.secondary_running = False
        self.assertEqual(state.secondary_sphere_radius, original)


if __name__ == "__main__":
    unittest.main()
