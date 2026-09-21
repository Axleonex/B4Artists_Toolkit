"""Bforartists binding checks for direct moving triangle-mesh collision."""
import unittest

import bpy

import b4artists_ml
from b4artists_ml import secondary_motion as secondary
from test_b4artists_ml_secondary_mesh_collision_v1 import mesh_surface
from test_b4artists_ml_secondary_motion import fixture


class SecondaryMovingMeshBindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b4artists_ml.register()

    def test_direct_transform_trajectory_binding(self):
        obj, _, _, _, _, _ = fixture("boneforge")
        scene = bpy.context.scene
        surface = mesh_surface("B4ML Moving Mesh", location=(2., 0., 0.))
        surface.keyframe_insert(data_path="location", frame=1.0)
        surface.location = (-2., 0., 0.)
        surface.keyframe_insert(data_path="location", frame=11.0)
        state = obj.b4ml
        state.secondary_collision = True
        state.secondary_collision_shape = "MESH"
        state.secondary_collision_mesh = surface
        state.secondary_collision_mesh_moving = True
        state.secondary_collision_continuous = True
        raw = secondary.request(obj, scene)
        self.assertTrue(raw["collision_mesh_moving"])
        self.assertTrue(raw["collision_mesh_continuous"])
        triangles, closed, name, token = secondary._mesh_collider_values(
            state, scene, obj, surface, moving=True)
        self.assertEqual(len(triangles), 12)
        self.assertTrue(closed)
        self.assertEqual(name, "MOVING_MESH:" + surface.name)
        surface.data.calc_loop_triangles()
        topology = tuple(tuple(item.vertices) for item in surface.data.loop_triangles)
        scene.frame_set(1)
        first = secondary._sample_deforming_mesh(surface, topology, scene)
        scene.frame_set(11)
        last = secondary._sample_deforming_mesh(surface, topology, scene)
        self.assertFalse((first == last).all())
        self.assertEqual(token[0], surface.as_pointer())

    def test_moving_mesh_rejects_non_transform_action_data(self):
        obj, _, _, _, _, _ = fixture("rigify_default")
        surface = mesh_surface("B4ML Moving Mesh Invalid")
        surface.keyframe_insert(data_path="location", frame=1.0)
        surface["unsafe"] = 1.0
        surface.keyframe_insert(data_path='["unsafe"]', frame=1.0)
        state = obj.b4ml
        state.secondary_collision_mesh_moving = True
        with self.assertRaisesRegex(ValueError, "object transforms only"):
            secondary._mesh_collider_values(state, bpy.context.scene, obj,
                                            surface, moving=True)

    def test_moving_and_shape_key_deforming_mesh_binding(self):
        obj, _, _, _, _, _ = fixture("boneforge")
        scene = bpy.context.scene
        surface = mesh_surface("B4ML Moving Deforming Mesh", location=(2., 0., 0.))
        surface.keyframe_insert(data_path="location", frame=1.0)
        surface.location = (-2., 0., 0.)
        surface.keyframe_insert(data_path="location", frame=11.0)
        surface.shape_key_add(name="Basis")
        key = surface.shape_key_add(name="Crouch")
        for vertex in key.data:
            if vertex.co.z > 0.0:
                vertex.co.z *= 1.4
        key.value = 0.0
        key.keyframe_insert(data_path="value", frame=1.0)
        key.value = 1.0
        key.keyframe_insert(data_path="value", frame=11.0)
        state = obj.b4ml
        state.secondary_collision = True
        state.secondary_collision_shape = "MESH"
        state.secondary_collision_mesh = surface
        state.secondary_collision_mesh_moving = True
        state.secondary_collision_mesh_deforming = True
        raw = secondary.request(obj, scene)
        self.assertTrue(raw["collision_mesh_moving"])
        self.assertTrue(raw["collision_mesh_deforming"])
        triangles, closed, name, token = secondary._mesh_collider_values(
            state, scene, obj, surface, deforming=True, moving=True)
        self.assertEqual(len(triangles), 12)
        self.assertTrue(closed)
        self.assertEqual(name, "MOVING_DEFORMING_MESH:" + surface.name)
        self.assertEqual(token[0], surface.as_pointer())

    def test_moving_closed_volume_reports_bounded_swept_backend(self):
        obj, _, _, _, _, _ = fixture("rigify_default")
        scene = bpy.context.scene
        surface = mesh_surface("B4ML Moving Closed Volume", location=(100., 0., 0.))
        surface.keyframe_insert(data_path="location", frame=1.0)
        surface.location = (96., 0., 0.)
        surface.keyframe_insert(data_path="location", frame=11.0)
        state = obj.b4ml
        state.secondary_space = "WORLD"
        state.secondary_rotation = False
        state.secondary_location = True
        state.secondary_collision = True
        state.secondary_collision_shape = "VOLUME"
        state.secondary_collision_mesh = surface
        state.secondary_collision_mesh_moving = True
        state.secondary_collision_volume_radius = .2
        state.secondary_collision_continuous = True
        metrics = secondary.solve(obj, scene)
        self.assertEqual(metrics["schema"], 22)
        self.assertEqual(metrics["backend"],
                         "implicit_selected_control_secondary_continuous_moving_swept_volume_v1")
        self.assertTrue(metrics["collision_mesh_bounded_swept_volume"])
        self.assertFalse(metrics["collision_mesh_exact_swept_volume"])
        self.assertEqual(metrics["collision_target_space"],
                         "bounded continuous-time closed moving swept triangle volume")

    def test_deforming_closed_volume_reports_bounded_swept_backend(self):
        obj, _, _, _, _, _ = fixture("rigify_default")
        scene = bpy.context.scene
        surface = mesh_surface("B4ML Deforming Closed Volume", location=(100., 0., 0.))
        surface.shape_key_add(name="Basis")
        key = surface.shape_key_add(name="Crouch")
        for vertex in key.data:
            if vertex.co.z > 0.0:
                vertex.co.z *= 1.4
        key.value = 0.0
        key.keyframe_insert(data_path="value", frame=1.0)
        key.value = 1.0
        key.keyframe_insert(data_path="value", frame=11.0)
        state = obj.b4ml
        state.secondary_space = "WORLD"
        state.secondary_rotation = False
        state.secondary_location = True
        state.secondary_collision = True
        state.secondary_collision_shape = "VOLUME"
        state.secondary_collision_mesh = surface
        state.secondary_collision_mesh_deforming = True
        state.secondary_collision_volume_radius = .2
        state.secondary_collision_continuous = True
        metrics = secondary.solve(obj, scene)
        self.assertEqual(metrics["schema"], 22)
        self.assertEqual(metrics["backend"],
                         "implicit_selected_control_secondary_continuous_deforming_swept_volume_v1")
        self.assertTrue(metrics["collision_mesh_bounded_swept_volume"])
        self.assertFalse(metrics["collision_mesh_exact_swept_volume"])
        self.assertEqual(metrics["collision_target_space"],
                         "bounded continuous-time closed deforming swept triangle volume")


if __name__ == "__main__":
    result = unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(
            SecondaryMovingMeshBindingTests))
    print("B4ML_SECONDARY_MOVING_MESH_BINDING_RESULT:",
          "PASS" if result.wasSuccessful() else "FAIL")
    if not result.wasSuccessful():
        raise SystemExit(1)
