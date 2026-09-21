"""Bforartists binding and guard checks for static arbitrary mesh collision."""
import unittest

import bpy

import b4artists_ml
from b4artists_ml import secondary_motion as secondary
from test_b4artists_ml_secondary_motion import fixture


def mesh_surface(name, location=(0.0, 0.0, 0.0)):
    vertices = (
        (-1, -1, -1), (-1, 1, -1), (-1, 1, 1), (-1, -1, 1),
        (1, -1, -1), (1, -1, 1), (1, 1, 1), (1, 1, -1),
    )
    faces = (
        (0, 1, 2, 3), (4, 5, 6, 7), (0, 4, 7, 1),
        (3, 2, 6, 5), (0, 3, 5, 4), (1, 7, 6, 2),
    )
    data = bpy.data.meshes.new(name + ' Data')
    data.from_pydata(vertices, [], faces)
    data.update()
    obj = bpy.data.objects.new(name, data)
    obj.location = location
    bpy.context.scene.collection.objects.link(obj)
    bpy.context.view_layer.update()
    return obj


class SecondaryMeshBindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b4artists_ml.register()

    def test_request_and_static_mesh_binding(self):
        obj, _, _, _, _, _ = fixture("boneforge")
        state = obj.b4ml
        surface = mesh_surface("B4ML Arbitrary Mesh")
        state.secondary_collision = True
        state.secondary_collision_shape = "MESH"
        state.secondary_collision_mesh = surface
        raw = secondary.request(obj, bpy.context.scene)
        self.assertEqual(raw["collision_shape"], "MESH")
        self.assertEqual(raw["collision_mesh"], surface.name_full)
        triangles, closed, name, token = secondary._mesh_collider_values(
            state, bpy.context.scene, obj, surface)
        self.assertEqual(len(triangles), 12)
        self.assertTrue(closed)
        self.assertEqual(name, "STATIC_MESH:" + surface.name)
        self.assertEqual(token[0], surface.as_pointer())

    def test_parent_animation_modifier_and_rigid_body_guards(self):
        obj, _, _, _, _, _ = fixture("rigify_default")
        state = obj.b4ml
        surface = mesh_surface("B4ML Invalid Mesh")
        parent = bpy.data.objects.new("B4ML Mesh Parent", None)
        bpy.context.scene.collection.objects.link(parent)
        surface.parent = parent
        with self.assertRaisesRegex(ValueError, "unparented"):
            secondary._mesh_collider_values(state, bpy.context.scene, obj, surface)
        surface.parent = None
        surface.keyframe_insert(data_path="location", frame=1.0)
        with self.assertRaisesRegex(ValueError, "static"):
            secondary._mesh_collider_values(state, bpy.context.scene, obj, surface)
        surface.animation_data_clear()
        surface.modifiers.new("Disallowed Deform", "SUBSURF")
        with self.assertRaisesRegex(ValueError, "modifiers"):
            secondary._mesh_collider_values(state, bpy.context.scene, obj, surface)

    def test_shape_key_deforming_mesh_binding_and_samples(self):
        obj, _, _, _, _, _ = fixture("boneforge")
        state = obj.b4ml
        surface = mesh_surface("B4ML Deforming Mesh")
        basis = surface.shape_key_add(name="Basis")
        key = surface.shape_key_add(name="Crouch")
        for vertex in key.data:
            if vertex.co.z > 0.0:
                vertex.co.z *= 1.4
        key.value = 0.0
        key.keyframe_insert(data_path="value", frame=1.0)
        key.value = 1.0
        key.keyframe_insert(data_path="value", frame=11.0)
        state.secondary_collision_shape = "MESH"
        state.secondary_collision_mesh = surface
        state.secondary_collision_mesh_deforming = True
        raw = secondary.request(obj, bpy.context.scene)
        self.assertTrue(raw["collision_mesh_deforming"])
        triangles, closed, name, token = secondary._mesh_collider_values(
            state, bpy.context.scene, obj, surface, True)
        self.assertEqual(len(triangles), 12)
        self.assertTrue(closed)
        self.assertEqual(name, "DEFORMING_MESH:" + surface.name)
        surface.data.calc_loop_triangles()
        topology = tuple(tuple(item.vertices) for item in surface.data.loop_triangles)
        bpy.context.scene.frame_set(1)
        first = secondary._sample_deforming_mesh(surface, topology, bpy.context.scene)
        bpy.context.scene.frame_set(11)
        last = secondary._sample_deforming_mesh(surface, topology, bpy.context.scene)
        self.assertFalse((first == last).all())
        self.assertEqual(token[0], surface.as_pointer())
        state.secondary_collision_continuous = True
        raw = secondary.request(obj, bpy.context.scene)
        self.assertTrue(raw["collision_mesh_continuous"])

    def test_closed_volume_binding_preserves_mesh_sampling_and_radius(self):
        obj, _, _, _, _, _ = fixture("boneforge")
        state = obj.b4ml
        surface = mesh_surface("B4ML Closed Volume Mesh")
        state.secondary_collision = True
        state.secondary_collision_shape = "VOLUME"
        state.secondary_collision_mesh = surface
        state.secondary_collision_volume_radius = .2
        state.secondary_collision_continuous = True
        raw = secondary.request(obj, bpy.context.scene)
        self.assertEqual(raw["collision_shape"], "VOLUME")
        self.assertEqual(raw["collision_mesh"], surface.name_full)
        self.assertAlmostEqual(raw["collision_mesh_volume_radius"], .2)
        self.assertTrue(raw["collision_mesh_continuous"])
        triangles, closed, name, token = secondary._mesh_collider_values(
            state, bpy.context.scene, obj, surface)
        self.assertEqual(len(triangles), 12)
        self.assertTrue(closed)
        self.assertEqual(name, "STATIC_MESH:" + surface.name)
        self.assertEqual(token[0], surface.as_pointer())

    def test_exact_swept_volume_static_report_binding(self):
        obj, _, _, _, _, _ = fixture("rigify_default")
        scene = bpy.context.scene
        state = obj.b4ml
        surface = mesh_surface("B4ML Exact Swept Volume Mesh", location=(100., 0., 0.))
        state.secondary_space = "WORLD"
        state.secondary_rotation = False
        state.secondary_location = True
        state.secondary_collision = True
        state.secondary_collision_shape = "VOLUME"
        state.secondary_collision_mesh = surface
        state.secondary_collision_volume_radius = .2
        state.secondary_collision_continuous = True
        metrics = secondary.solve(obj, scene)
        self.assertEqual(metrics["schema"], 21)
        self.assertEqual(metrics["backend"],
                         "implicit_selected_control_secondary_exact_swept_volume_v1")
        self.assertTrue(metrics["collision_mesh_exact_swept_volume"])
        self.assertEqual(metrics["collision_target_space"],
                         "exact swept-sphere closed evaluated triangle volume")

    def test_open_volume_mesh_is_not_closed(self):
        obj, _, _, _, _, _ = fixture("boneforge")
        state = obj.b4ml
        surface = mesh_surface("B4ML Open Volume Mesh")
        vertices = [tuple(vertex.co) for vertex in surface.data.vertices]
        faces = [tuple(poly.vertices) for poly in surface.data.polygons[:-1]]
        surface.data.clear_geometry()
        surface.data.from_pydata(vertices, [], faces)
        surface.data.update()
        state.secondary_collision_shape = "VOLUME"
        state.secondary_collision_mesh = surface
        triangles, closed, _, _ = secondary._mesh_collider_values(
            state, bpy.context.scene, obj, surface)
        self.assertEqual(len(triangles), 10)
        self.assertFalse(closed)


if __name__ == "__main__":
    result = unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(SecondaryMeshBindingTests))
    print("B4ML_SECONDARY_MESH_BINDING_RESULT:",
          "PASS" if result.wasSuccessful() else "FAIL")
    if not result.wasSuccessful():
        raise SystemExit(1)
