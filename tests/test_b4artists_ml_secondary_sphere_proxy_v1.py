"""World-bounds sphere-proxy creation for secondary collision setup."""
from itertools import product
from pathlib import Path
import os
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [os.environ.get("B4ML_PACKAGE", str(ROOT)), str(ROOT / "tests")]

import bpy
from mathutils import Vector
import b4artists_ml
from b4artists_ml import secondary_motion as secondary
from b4artists_ml import secondary_math
from test_b4artists_ml_secondary_sphere_collision_v1 import sphere_fixture


def make_offset_box(name, location, local_center=(0.0, 0.0, 0.0),
                    half_extents=(0.1, 0.2, 0.3)):
    mesh = bpy.data.meshes.new(name + " Mesh")
    mesh.from_pydata([
        (local_center[0] + sx * half_extents[0],
         local_center[1] + sy * half_extents[1],
         local_center[2] + sz * half_extents[2])
        for sx, sy, sz in product((-1.0, 1.0), repeat=3)
    ], [], [])
    mesh.update()
    source = bpy.data.objects.new(name, mesh)
    source.location = location
    bpy.context.scene.collection.objects.link(source)
    bpy.context.view_layer.update()
    return source


def expected_sphere(source):
    corners = [source.matrix_world @ Vector(corner) for corner in source.bound_box]
    center = sum(corners, Vector((0.0, 0.0, 0.0))) / 8.0
    radius = max((corner - center).length for corner in corners)
    return center, radius, corners


class SecondarySphereProxyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b4artists_ml.register()

    def test_proxy_centers_offset_world_bounds_and_adds_static_row(self):
        obj, _, _, old, _ = sphere_fixture()
        source = make_offset_box(
            "B4ML Proxy Offset", old.location + Vector((2.0, -1.0, 0.5)),
            (0.6, -0.25, 0.4), (0.15, 0.3, 0.2))
        source.rotation_euler = (0.2, -0.35, 0.5)
        source.scale = (1.5, 0.75, 2.0)
        bpy.context.view_layer.update()
        expected_center, expected_radius, corners = expected_sphere(source)
        source_state = (tuple(source.location), tuple(source.rotation_euler),
                        tuple(source.scale), source.data.as_pointer())
        state = obj.b4ml
        state.secondary_sphere_collider = source
        state.secondary_sphere_radius = 0.01
        state.secondary_sphere_moving = True
        state.secondary_sphere_scaling = True

        report = secondary.create_sphere_proxy_from_bounds(obj, bpy.context.scene)
        proxy = bpy.data.objects[report["collider"]]
        item = state.secondary_spheres[-1]
        self.assertEqual(report["source"], source.name_full)
        self.assertEqual(proxy.type, "EMPTY")
        self.assertEqual(proxy.empty_display_type, "SPHERE")
        self.assertIsNone(proxy.parent)
        self.assertFalse(proxy.constraints)
        self.assertTrue(proxy["b4ml_sphere_proxy"])
        self.assertEqual(proxy["b4ml_sphere_source"], source.name_full)
        self.assertLess((proxy.matrix_world.translation - expected_center).length, 1e-6)
        self.assertAlmostEqual(report["radius"], expected_radius, places=6)
        self.assertTrue(all((corner - proxy.matrix_world.translation).length <= item.radius
                            for corner in corners))
        self.assertEqual(item.collider, proxy)
        self.assertFalse(item.moving)
        self.assertFalse(item.scaling)
        self.assertEqual(state.secondary_sphere_collider, proxy)
        self.assertEqual(state.secondary_sphere_radius, item.radius)
        self.assertFalse(state.secondary_sphere_moving)
        self.assertFalse(state.secondary_sphere_scaling)
        self.assertEqual((tuple(source.location), tuple(source.rotation_euler),
                          tuple(source.scale), source.data.as_pointer()), source_state)

    def test_proxy_accepts_parented_bound_geometry_but_remains_unparented(self):
        obj, _, _, old, _ = sphere_fixture()
        parent = bpy.data.objects.new("B4ML Proxy Parent", None)
        parent.location = old.location + Vector((1.0, 2.0, -0.5))
        parent.rotation_euler = (0.1, 0.2, -0.3)
        bpy.context.scene.collection.objects.link(parent)
        source = make_offset_box("B4ML Proxy Child", (0.3, -0.2, 0.7),
                                 (0.2, 0.1, -0.3), (0.4, 0.15, 0.25))
        source.parent = parent
        bpy.context.view_layer.update()
        expected_center, _, corners = expected_sphere(source)
        obj.b4ml.secondary_sphere_collider = source

        report = secondary.create_sphere_proxy_from_bounds(obj, bpy.context.scene)
        proxy = bpy.data.objects[report["collider"]]
        self.assertIsNone(proxy.parent)
        self.assertLess((proxy.matrix_world.translation - expected_center).length, 1e-6)
        self.assertTrue(all(
            (corner - proxy.matrix_world.translation).length <= report["radius"]
            for corner in corners))

    def test_proxy_operator_supports_native_undo_redo(self):
        obj, _, _, old, _ = sphere_fixture()
        source = make_offset_box("B4ML Proxy Undo", old.location, (0.4, 0.0, 0.0))
        state = obj.b4ml
        state.secondary_sphere_collider = source
        obj_name = obj.name
        bpy.context.preferences.edit.use_global_undo = True
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        if obj.mode != "POSE":
            bpy.ops.object.mode_set(mode="POSE")
        bpy.ops.ed.undo_push(message="Before sphere proxy creation")
        self.assertEqual(
            bpy.ops.b4ml.secondary_sphere(operation="PROXY", index=-1), {"FINISHED"})
        proxy_name = obj.b4ml.secondary_spheres[-1].collider.name
        bpy.ops.ed.undo_push(message="Sphere proxy creation complete")
        self.assertIn(proxy_name, bpy.data.objects)
        self.assertEqual(bpy.ops.ed.undo(), {"FINISHED"})
        obj = bpy.data.objects[obj_name]
        self.assertNotIn(proxy_name, bpy.data.objects)
        self.assertEqual(len(obj.b4ml.secondary_spheres), 0)
        self.assertEqual(bpy.ops.ed.redo(), {"FINISHED"})
        obj = bpy.data.objects[obj_name]
        self.assertIn(proxy_name, bpy.data.objects)
        self.assertEqual(len(obj.b4ml.secondary_spheres), 1)

    def test_proxy_rejects_missing_unavailable_and_busy_sources_atomically(self):
        obj, _, _, old, _ = sphere_fixture()
        state = obj.b4ml
        original_objects = set(bpy.data.objects.keys())
        original_radius = state.secondary_sphere_radius
        state.secondary_sphere_collider = None
        with self.assertRaisesRegex(ValueError, "Choose a geometric object"):
            secondary.create_sphere_proxy_from_bounds(obj, bpy.context.scene)
        source = make_offset_box("B4ML Proxy Busy", old.location)
        state.secondary_sphere_collider = source
        state.secondary_running = True
        with self.assertRaisesRegex(ValueError, "active animation workflow"):
            secondary.create_sphere_proxy_from_bounds(obj, bpy.context.scene)
        state.secondary_running = False
        empty_mesh = bpy.data.objects.new(
            "B4ML Proxy Empty", bpy.data.meshes.new("B4ML Proxy Empty Mesh"))
        bpy.context.scene.collection.objects.link(empty_mesh)
        bpy.context.view_layer.update()
        state.secondary_sphere_collider = empty_mesh
        before_failure = set(bpy.data.objects.keys())
        with self.assertRaisesRegex(ValueError, "no available geometric bounds"):
            secondary.create_sphere_proxy_from_bounds(obj, bpy.context.scene)
        self.assertEqual(set(bpy.data.objects.keys()), before_failure)
        self.assertEqual(len(state.secondary_spheres), 0)
        self.assertEqual(state.secondary_sphere_radius, original_radius)
        self.assertTrue(original_objects <= set(bpy.data.objects.keys()))

    def test_proxy_rejects_a_full_set_without_creating_data(self):
        obj, _, _, old, _ = sphere_fixture()
        source = make_offset_box("B4ML Proxy Full", old.location)
        state = obj.b4ml
        state.secondary_sphere_collider = source
        for _ in range(secondary_math.MAX_SPHERE_COLLIDERS):
            state.secondary_spheres.add()
        before_objects = set(bpy.data.objects.keys())
        with self.assertRaisesRegex(ValueError, "limited"):
            secondary.create_sphere_proxy_from_bounds(obj, bpy.context.scene)
        self.assertEqual(set(bpy.data.objects.keys()), before_objects)
        self.assertEqual(len(state.secondary_spheres), secondary_math.MAX_SPHERE_COLLIDERS)
        self.assertEqual(state.secondary_sphere_collider, source)


if __name__ == "__main__":
    unittest.main()
