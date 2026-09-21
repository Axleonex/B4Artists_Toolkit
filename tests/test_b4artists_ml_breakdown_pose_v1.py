"""Bforartists tests for editable full-body and selected-control breakdown poses."""
from pathlib import Path
import json
import math
import os
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [os.environ.get("B4ML_PACKAGE", str(ROOT)), str(ROOT / "tests")]

import bpy
from mathutils import Euler, Quaternion

import b4artists_ml
from b4artists_ml import quadruped_gait, workflow


class BreakdownPoseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not b4artists_ml.is_bforartists():
            raise unittest.SkipTest("Bforartists required")
        b4artists_ml.register()

    def setUp(self):
        if bpy.context.object and bpy.context.object.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
        data = bpy.data.armatures.new("Breakdown Pose Rig")
        self.obj = bpy.data.objects.new("Breakdown Pose Rig", data)
        bpy.context.scene.collection.objects.link(self.obj)
        bpy.context.view_layer.objects.active = self.obj
        self.obj.select_set(True)
        bpy.ops.object.mode_set(mode="EDIT")
        for index, name in enumerate(("hips", "upperarm.fk-L", "thigh.fk-R")):
            bone = data.edit_bones.new(name)
            bone.head = (float(index), 0.0, 0.0)
            bone.tail = (float(index), 0.0, 1.0)
        bpy.ops.object.mode_set(mode="POSE")
        self.hips = self.obj.pose.bones["hips"]
        self.hips.rotation_mode = "QUATERNION"
        self.arm = self.obj.pose.bones["upperarm.fk-L"]
        self.arm.rotation_mode = "XYZ"
        self.leg = self.obj.pose.bones["thigh.fk-R"]
        self.leg.rotation_mode = "AXIS_ANGLE"
        self.scene = bpy.context.scene
        self.scene.frame_set(1)

    def tearDown(self):
        if bpy.context.object and bpy.context.object.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
        obj = bpy.data.objects.get("Breakdown Pose Rig")
        if obj:
            data = obj.data
            bpy.data.objects.remove(obj, do_unlink=True)
            if not data.users:
                bpy.data.armatures.remove(data)

    def _capture(self, frame, value):
        self.scene.frame_set(frame)
        self.hips.location.x = value
        self.hips.scale.x = 1.0 + value / 20.0
        self.hips.rotation_quaternion = Quaternion((0.0, 0.0, 1.0),
                                                   math.radians(value * 9.0))
        self.arm.location.y = value / 10.0
        self.arm.rotation_euler = Euler((0.0, 0.0, math.radians(value * 9.0)), "XYZ")
        self.leg.rotation_axis_angle = (math.radians(value * 6.0), 0.0, 1.0, 0.0)
        for bone, prop in ((self.hips, "location"), (self.hips, "scale"),
                           (self.hips, "rotation_quaternion"),
                           (self.arm, "location"), (self.arm, "rotation_euler"),
                           (self.leg, "rotation_axis_angle")):
            bone.keyframe_insert(prop, frame=frame)
        workflow.capture_anchor(self.obj, self.scene, False)

    def _anchor(self, frame):
        return next(anchor for anchor in self.obj.b4ml.anchors
                    if abs(anchor.frame-frame) < 1e-5)

    def _payloads(self):
        return [(anchor.frame, anchor.payload) for anchor in self.obj.b4ml.anchors]

    def _source_digest(self):
        return quadruped_gait._action_digest(self.obj, self.obj.animation_data.action)

    def test_context_uses_adjacent_poses_and_natural_playhead_fraction(self):
        self._capture(1, 0.0)
        self._capture(11, 10.0)
        self._capture(21, 20.0)
        self.scene.frame_set(16)
        values = workflow.breakdown_context(self.obj, self.scene)
        self.assertEqual((values["left"][0], values["right"][0]), (11.0, 21.0))
        self.assertAlmostEqual(values["natural_blend"], .5)
        for frame, message in ((1, "already"), (22, "strictly between")):
            self.scene.frame_set(frame)
            with self.subTest(frame=frame), self.assertRaisesRegex(ValueError, message):
                workflow.breakdown_context(self.obj, self.scene)

    def test_full_body_breakdown_preserves_source_and_destination_timing(self):
        self._capture(1, 0.0)
        self._capture(11, 10.0)
        workflow.set_transition_timing(self.obj, 11, True, "EASE_OUT", -.2, .1, .2)
        source = self.obj.animation_data.action
        before = self._source_digest()
        self.scene.frame_set(4)
        result = workflow.create_breakdown_anchor(self.obj, self.scene, .75)
        self.assertEqual(result["selected_controls"], sorted(result["selected_controls"]))
        self.assertEqual(len(result["selected_controls"]), 3)
        payload = json.loads(self._anchor(4).payload)
        self.assertAlmostEqual(payload["pose"]["hips"]["location"][0], 7.5)
        self.assertAlmostEqual(payload["pose"]["hips"]["scale"][0], 1.375)
        self.assertAlmostEqual(payload["pose"]["upperarm.fk-L"]["location"][1], .75)
        self.assertIsNone(workflow.transition_timing(self.obj, 4))
        timing = workflow.transition_timing(self.obj, 11)
        self.assertEqual((timing["easing"], timing["departure_hold"],
                          timing["arrival_hold"]), ("EASE_OUT", .1, .2))
        self.assertIs(self.obj.animation_data.action, source)
        self.assertEqual(self._source_digest(), before)
        workflow.preview(self.obj, self.scene, "LINEAR")
        self.scene.frame_set(4)
        self.assertAlmostEqual(self.hips.location.x, 7.5, places=5)
        workflow.finish_preview(self.obj, self.scene, keep=False)
        self.assertIs(self.obj.animation_data.action, source)
        self.assertEqual(self._source_digest(), before)

    def test_selected_controls_use_requested_blend_and_others_use_natural_blend(self):
        self._capture(1, 0.0)
        self._capture(11, 10.0)
        self.scene.frame_set(4)
        workflow.preview(self.obj, self.scene, self.obj.b4ml.easing,
                         timing_bias=self.obj.b4ml.timing_bias)
        self.scene.frame_set(4)
        expected_arm_location = self.arm.location.y
        expected_arm_rotation = self.arm.rotation_euler.to_quaternion()
        workflow.finish_preview(self.obj, self.scene, keep=False)
        for bone in self.obj.pose.bones:
            bone.select = bone.name == "hips"
        self.scene.frame_set(4)
        result = workflow.create_breakdown_anchor(
            self.obj, self.scene, .8, selected_only=True)
        self.assertEqual(result["selected_controls"], ["hips"])
        payload = json.loads(self._anchor(4).payload)["pose"]
        self.assertAlmostEqual(payload["hips"]["location"][0], 8.0)
        self.assertAlmostEqual(payload["upperarm.fk-L"]["location"][1],
                               expected_arm_location, places=6)
        arm_rotation = Quaternion(payload["upperarm.fk-L"]["rotation"])
        self.assertAlmostEqual(abs(arm_rotation.dot(expected_arm_rotation)),
                               1.0, places=6)
        hips_angle = Quaternion(payload["hips"]["rotation"]).angle
        self.assertAlmostEqual(hips_angle, math.radians(72), places=5)

    def test_selected_controls_preserve_destination_timed_unselected_pose(self):
        self._capture(1, 0.0)
        self._capture(11, 10.0)
        workflow.set_transition_timing(
            self.obj, 11, True, "EASE_OUT", -.25, .2, .3)
        self.scene.frame_set(4)
        workflow.preview(self.obj, self.scene, "SMOOTH", timing_bias=.75)
        self.scene.frame_set(4)
        expected_arm_location = self.arm.location.y
        expected_arm_rotation = self.arm.rotation_euler.to_quaternion()
        workflow.finish_preview(self.obj, self.scene, keep=False)
        for bone in self.obj.pose.bones:
            bone.select = bone.name == "hips"
        self.scene.frame_set(4)
        workflow.create_breakdown_anchor(
            self.obj, self.scene, .8, selected_only=True)
        payload = json.loads(self._anchor(4).payload)["pose"]
        self.assertAlmostEqual(payload["hips"]["location"][0], 8.0)
        self.assertAlmostEqual(payload["upperarm.fk-L"]["location"][1],
                               expected_arm_location, places=6)
        arm_rotation = Quaternion(payload["upperarm.fk-L"]["rotation"])
        self.assertAlmostEqual(abs(arm_rotation.dot(expected_arm_rotation)),
                               1.0, places=6)

    def test_blended_payload_has_consistent_native_raw_rotations(self):
        self._capture(1, 0.0)
        self._capture(11, 10.0)
        self.scene.frame_set(6)
        workflow.create_breakdown_anchor(self.obj, self.scene, .5)
        pose = json.loads(self._anchor(6).payload)["pose"]
        self.assertEqual(len(pose["hips"]["raw_rotation"]), 4)
        self.assertEqual(len(pose["upperarm.fk-L"]["raw_rotation"]), 3)
        self.assertEqual(len(pose["thigh.fk-R"]["raw_rotation"]), 4)
        for name, values in pose.items():
            expected = Quaternion(values["rotation"])
            mode = values["mode"]
            if mode == "QUATERNION":
                actual = Quaternion(values["raw_rotation"])
            elif mode == "AXIS_ANGLE":
                angle, x, y, z = values["raw_rotation"]
                actual = Quaternion((x, y, z), angle)
            else:
                actual = Euler(values["raw_rotation"], mode).to_quaternion()
            self.assertAlmostEqual(abs(expected.dot(actual)), 1.0, places=6, msg=name)

    def test_endpoint_blends_create_holds_without_moving_neighbor_anchors(self):
        for blend, expected in ((0.0, 0.0), (1.0, 10.0)):
            with self.subTest(blend=blend):
                if len(self.obj.b4ml.anchors):
                    self.obj.b4ml.anchors.clear()
                self._capture(1, 0.0)
                self._capture(11, 10.0)
                self.scene.frame_set(6)
                workflow.create_breakdown_anchor(self.obj, self.scene, blend)
                self.assertAlmostEqual(
                    json.loads(self._anchor(6).payload)["pose"]["hips"]["location"][0],
                    expected)
                self.assertEqual(sorted(anchor.frame for anchor in self.obj.b4ml.anchors),
                                 [1.0, 6.0, 11.0])

    def test_invalid_requests_fail_before_anchor_or_source_mutation(self):
        self._capture(1, 0.0)
        self._capture(11, 10.0)
        before_anchors = self._payloads()
        before_source = self._source_digest()
        cases = ((6, True, False, "blend"), (6, 1.1, False, "blend"),
                 (1, .5, False, "already"), (12, .5, False, "strictly between"),
                 (6, .5, True, "Select at least one"))
        for frame, blend, selected, message in cases:
            self.scene.frame_set(frame)
            for bone in self.obj.pose.bones:
                bone.select = False
            with self.subTest(frame=frame, blend=blend), self.assertRaisesRegex(
                    ValueError, message):
                workflow.create_breakdown_anchor(
                    self.obj, self.scene, blend, selected_only=selected)
            self.assertEqual(self._payloads(), before_anchors)
            self.assertEqual(self._source_digest(), before_source)
        self.obj.b4ml.interpolation_method = 'AUTHORED'
        self.scene.frame_set(6)
        with self.assertRaisesRegex(ValueError, 'Pose Blending'):
            workflow.create_breakdown_anchor(self.obj, self.scene, .5)
        self.assertEqual(self._payloads(), before_anchors)
        self.assertEqual(self._source_digest(), before_source)

    def test_operator_and_save_reload_preserve_breakdown(self):
        self._capture(1, 0.0)
        self._capture(11, 10.0)
        source_before = self._source_digest()
        self.scene.frame_set(6)
        result = bpy.ops.b4ml.breakdown_pose(
            'EXEC_DEFAULT', blend=.65, selected_only=False)
        self.assertEqual(result, {"FINISHED"})
        self.assertAlmostEqual(
            json.loads(self._anchor(6).payload)["pose"]["hips"]["location"][0],
            6.5, places=6)
        self.assertEqual(self._source_digest(), source_before)
        name = self.obj.name
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / "breakdown-pose-v1.blend")
            bpy.ops.wm.save_as_mainfile(filepath=path)
            bpy.ops.wm.open_mainfile(filepath=path, load_ui=False, use_scripts=False)
            self.obj = bpy.data.objects[name]
            self.hips = self.obj.pose.bones["hips"]
            self.arm = self.obj.pose.bones["upperarm.fk-L"]
            self.leg = self.obj.pose.bones["thigh.fk-R"]
            self.scene = bpy.context.scene
            bpy.context.view_layer.objects.active = self.obj
            self.obj.select_set(True)
            self.assertAlmostEqual(
                json.loads(self._anchor(6).payload)["pose"]["hips"]["location"][0],
                6.5, places=6)
            self.assertEqual(self._source_digest(), source_before)


if __name__ == "__main__":
    result = unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(BreakdownPoseTests))
    if not result.wasSuccessful():
        raise SystemExit(1)
