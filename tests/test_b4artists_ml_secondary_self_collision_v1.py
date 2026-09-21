"""Bforartists binding and solve checks for selected-control self-collision."""
import json
import unittest

import bpy
from mathutils import Vector

import b4artists_ml
from b4artists_ml import secondary_motion as secondary, workflow as w
from test_b4artists_ml_secondary_motion import fixture


class SecondarySelfCollisionBindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b4artists_ml.register()

    def test_request_and_single_control_guard(self):
        obj, _, _, _, _, _ = fixture("boneforge")
        state = obj.b4ml
        state.secondary_space = "WORLD"
        state.secondary_location = True
        state.secondary_self_collision = True
        state.secondary_self_collision_radius = 0.05
        raw = secondary.request(obj, bpy.context.scene)
        self.assertTrue(raw["self_collision"])
        self.assertAlmostEqual(raw["self_collision_radius"], 0.05)
        with self.assertRaisesRegex(ValueError, "at least two"):
            next(secondary.correction_steps(obj, bpy.context.scene))

    def test_two_control_world_solve_separates_crossing_paths(self):
        obj, _, _, _, _, _ = fixture("rigify_default")
        scene = bpy.context.scene
        captured = set(json.loads(obj.b4ml.anchors[0].payload)["pose"])
        curves = w.action_curves(
            obj.b4ml.candidate_action,
            getattr(obj.animation_data, "action_slot", None))
        eligible = []
        for name in captured:
            bone = obj.pose.bones[name]
            if len(w._channels(bone)["location"]) != 3:
                continue
            path = bone.path_from_id("location")
            if all(curves.find(path, index=index) is not None
                   for index in range(3)):
                eligible.append(name)
        pairs = [(first, second) for index, first in enumerate(eligible[:-1])
                 for second in eligible[index+1:]
                 if obj.pose.bones[first].parent == obj.pose.bones[second].parent]
        self.assertTrue(pairs, "fixture needs two editable sibling location controls")
        names = sorted(pairs[0])
        scene.frame_set(1)
        displayed = w.display_world(obj)
        center = (displayed @ obj.pose.bones[names[0]].matrix).translation.copy()

        def set_world(name, target, frame):
            scene.frame_set(frame)
            bpy.context.view_layer.update()
            displayed = w.display_world(obj)
            bone = obj.pose.bones[name]
            desired = displayed @ bone.matrix
            desired.translation = Vector(target)
            local = obj.convert_space(
                pose_bone=bone, matrix=displayed.inverted() @ desired,
                from_space="POSE", to_space="LOCAL")
            bone.location = local.to_translation()
            bone.keyframe_insert(data_path="location", frame=frame)

        offset = Vector((.11, 0., 0.))
        set_world(names[0], center - offset*.5, 1)
        set_world(names[1], center + offset*.5, 1)
        set_world(names[0], center + offset*.5, 11)
        set_world(names[1], center - offset*.5, 11)
        for bone in obj.pose.bones:
            if hasattr(bone, "select"):
                bone.select = bone.name in names
            else:
                bone.bone.select = bone.name in names
        obj.data.bones.active = obj.data.bones[names[0]]
        state = obj.b4ml
        state.secondary_space = "WORLD"
        state.secondary_rotation = False
        state.secondary_location = True
        state.secondary_self_collision = True
        state.secondary_self_collision_radius = .05
        state.secondary_collision_clearance = .005
        state.secondary_strength = 1.0
        metrics = secondary.solve(obj, scene)
        self.assertEqual(metrics["schema"], 19)
        self.assertEqual(metrics["backend"],
                         "implicit_selected_control_secondary_self_collision_v1")
        self.assertGreater(metrics["self_collision_samples"], 0)
        self.assertGreater(metrics["max_self_collision_penetration"], 0.)
        self.assertLessEqual(metrics["max_penetration_after"], 1e-6)
        self.assertTrue(metrics["editable_linear_keys"])


if __name__ == "__main__":
    result = unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(
            SecondarySelfCollisionBindingTests))
    print("B4ML_SECONDARY_SELF_COLLISION_BINDING_RESULT:",
          "PASS" if result.wasSuccessful() else "FAIL")
    if not result.wasSuccessful():
        raise SystemExit(1)
