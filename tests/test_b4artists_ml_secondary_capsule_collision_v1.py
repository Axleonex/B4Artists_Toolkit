"""Blender binding and lifecycle checks for the static capsule collider."""
import unittest

import bpy
import numpy as np
from mathutils import Vector

import b4artists_ml
from b4artists_ml import secondary_motion as secondary
from test_b4artists_ml_secondary_motion import fixture


def endpoint(name, location):
    obj = bpy.data.objects.new(name, None)
    obj.empty_display_type = "SPHERE"
    obj.empty_display_size = 0.1
    obj.location = location
    bpy.context.scene.collection.objects.link(obj)
    bpy.context.view_layer.update()
    return obj


class SecondaryCapsuleBindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b4artists_ml.register()

    def test_request_and_static_endpoint_binding(self):
        obj, _, _, _, _, _ = fixture("boneforge")
        state = obj.b4ml
        start = endpoint("B4ML Capsule Start", (-1.0, 0.0, 0.0))
        end = endpoint("B4ML Capsule End", (1.0, 0.0, 0.0))
        state.secondary_collision = True
        state.secondary_collision_shape = "CAPSULE"
        state.secondary_capsule_start = start
        state.secondary_capsule_end = end
        state.secondary_capsule_radius = 0.25
        raw = secondary.request(obj, bpy.context.scene)
        self.assertEqual(raw["collision_shape"], "CAPSULE")
        self.assertEqual(raw["collision_capsule_start"], start.name_full)
        self.assertEqual(raw["collision_capsule_end"], end.name_full)
        self.assertAlmostEqual(raw["collision_capsule_radius"], 0.25)
        self.assertFalse(raw["collision_capsule_continuous"])
        values = secondary._capsule_collider_values(
            state, bpy.context.scene, obj, start, end, 0.25)
        self.assertEqual(values[3], "STATIC_CAPSULE:" + start.name + ":" + end.name)
        self.assertEqual(values[4][0:2], (start.as_pointer(), end.as_pointer()))

    def test_endpoint_constraints_and_animation_are_rejected(self):
        obj, _, _, _, _, _ = fixture("rigify_default")
        state = obj.b4ml
        start = endpoint("B4ML Capsule Start Invalid", (-1.0, 0.0, 0.0))
        end = endpoint("B4ML Capsule End Invalid", (1.0, 0.0, 0.0))
        state.secondary_capsule_start = start
        state.secondary_capsule_end = end
        parent = endpoint("B4ML Capsule Parent", (0.0, 0.0, 0.0))
        start.parent = parent
        with self.assertRaisesRegex(ValueError, "unparented"):
            secondary._capsule_collider_values(
                state, bpy.context.scene, obj, start, end, 0.25)
        start.parent = None
        start.keyframe_insert(data_path="location", frame=1.0)
        with self.assertRaisesRegex(ValueError, "static"):
            secondary._capsule_collider_values(
                state, bpy.context.scene, obj, start, end, 0.25)

    def test_animated_endpoint_binding_and_sampling_are_bounded(self):
        obj, _, _, _, _, _ = fixture("boneforge")
        state = obj.b4ml
        start = endpoint("B4ML Moving Capsule Start", (-1.0, 0.0, 0.0))
        end = endpoint("B4ML Moving Capsule End", (1.0, 0.0, 0.0))
        for item, first, second in ((start, (-1.0, 0.0, 0.0), (-0.5, 0.0, 0.0)),
                                    (end, (1.0, 0.0, 0.0), (0.5, 0.0, 0.0))):
            for index in range(3):
                item.location[index] = first[index]
                item.keyframe_insert(data_path="location", index=index, frame=1.0)
                item.location[index] = second[index]
                item.keyframe_insert(data_path="location", index=index, frame=3.0)
                item.scale[index] = 1.0
                item.keyframe_insert(data_path="scale", index=index, frame=1.0)
                item.scale[index] = 1.25
                item.keyframe_insert(data_path="scale", index=index, frame=3.0)
        state.secondary_capsule_start = start
        state.secondary_capsule_end = end
        state.secondary_capsule_radius = 0.25
        state.secondary_capsule_moving = True
        state.secondary_capsule_scaling = True
        values = secondary._capsule_collider_values(
            state, bpy.context.scene, obj, start, end, 0.25, True, True)
        self.assertIn("MOVING_SCALING_CAPSULE:", values[3])
        self.assertEqual(values[4][2], "ANIMATED")
        bpy.context.scene.frame_set(2)
        later = secondary._capsule_collider_values(
            state, bpy.context.scene, obj, start, end, 0.25, True, True)
        self.assertEqual(values[4], later[4])
        bpy.context.scene.frame_set(1)
        starts, ends, radii = secondary._sample_capsule_trajectories(
            bpy.context.scene, start, end, 0.25, (1.0, 2.0, 3.0), True, True)
        self.assertEqual(starts.shape, (3, 3))
        self.assertEqual(ends.shape, (3, 3))
        np.testing.assert_allclose(radii, (0.25, 0.28125, 0.3125), atol=1e-8)


if __name__ == "__main__":
    result = unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(SecondaryCapsuleBindingTests))
    print("B4ML_SECONDARY_CAPSULE_BINDING_RESULT:",
          "PASS" if result.wasSuccessful() else "FAIL")
    if not result.wasSuccessful():
        raise SystemExit(1)
