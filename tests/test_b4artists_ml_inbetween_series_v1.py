"""Bforartists tests for atomic procedural inbetween-series creation."""
from pathlib import Path
import json
import math
import os
import struct
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [os.environ.get("B4ML_PACKAGE", str(ROOT)), str(ROOT / "tests")]

import bpy
from mathutils import Euler, Quaternion

import b4artists_ml
from b4artists_ml import quadruped_gait, workflow


class InbetweenSeriesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not b4artists_ml.is_bforartists():
            raise unittest.SkipTest("Bforartists required")
        b4artists_ml.register()

    def setUp(self):
        if bpy.context.object and bpy.context.object.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
        data = bpy.data.armatures.new("Inbetween Series Rig")
        self.obj = bpy.data.objects.new("Inbetween Series Rig", data)
        bpy.context.scene.collection.objects.link(self.obj)
        bpy.context.view_layer.objects.active = self.obj
        self.obj.select_set(True)
        bpy.ops.object.mode_set(mode="EDIT")
        for index, name in enumerate(
                ("hips", "upperarm.fk-L", "thigh.fk-R")):
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
        self.scene.tool_settings.use_keyframe_insert_auto = False
        self.scene.frame_set(1)

    def tearDown(self):
        self.scene.tool_settings.use_keyframe_insert_auto = False
        if bpy.context.object and bpy.context.object.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
        obj = bpy.data.objects.get("Inbetween Series Rig")
        if obj:
            data = obj.data
            bpy.data.objects.remove(obj, do_unlink=True)
            if not data.users:
                bpy.data.armatures.remove(data)

    def _set_frame(self, value):
        base = math.floor(value)
        self.scene.frame_set(base, subframe=value-base)

    def _capture(self, frame, value):
        self._set_frame(frame)
        self.hips.location.x = value
        self.hips.scale.x = 1.0 + value / 20.0
        self.hips.rotation_quaternion = Quaternion(
            (0.0, 0.0, 1.0), math.radians(value * 9.0))
        self.arm.location.y = value / 10.0
        self.arm.rotation_euler = Euler(
            (0.0, 0.0, math.radians(value * 9.0)), "XYZ")
        self.leg.rotation_axis_angle = (
            math.radians(value * 6.0), 0.0, 1.0, 0.0)
        for bone, prop in (
                (self.hips, "location"), (self.hips, "scale"),
                (self.hips, "rotation_quaternion"),
                (self.arm, "location"), (self.arm, "rotation_euler"),
                (self.leg, "rotation_axis_angle")):
            bone.keyframe_insert(prop, frame=frame)
        workflow.capture_anchor(self.obj, self.scene, False)

    def _anchor(self, frame):
        return next(anchor for anchor in self.obj.b4ml.anchors
                    if abs(anchor.frame-frame) < 1e-5)

    def _anchors(self):
        return [(float(a.frame), a.name, a.payload) for a in self.obj.b4ml.anchors]

    def _source_digest(self):
        return quadruped_gait._action_digest(
            self.obj, self.obj.animation_data.action)

    def _untouched(self):
        animation = self.obj.animation_data
        return {
            "source": animation.action,
            "slot": getattr(animation, "action_slot", None),
            "digest": self._source_digest(),
            "frame": (self.scene.frame_current, self.scene.frame_subframe),
            "auto_key": self.scene.tool_settings.use_keyframe_insert_auto,
            "pose": {
                bone.name: (
                    tuple(bone.location), tuple(bone.scale), bone.rotation_mode,
                    tuple(bone.rotation_quaternion), tuple(bone.rotation_euler),
                    bool(bone.select),
                )
                for bone in self.obj.pose.bones
            },
        }

    @staticmethod
    def _stored(value):
        return float(struct.unpack("<f", struct.pack("<f", float(value)))[0])

    @staticmethod
    def _timing_oracle(t, easing, bias, departure, arrival):
        if t <= departure:
            active = 0.0
        elif t >= 1.0-arrival:
            active = 1.0
        else:
            active = (t-departure) / (1.0-departure-arrival)
        if active in {0.0, 1.0}:
            shifted = active
        else:
            midpoint = 0.5 + 0.4*bias
            shifted = active / (((1.0/midpoint-2.0)*(1.0-active))+1.0)
        if easing == "SMOOTH":
            return shifted*shifted*(3.0-2.0*shifted)
        if easing == "EASE_IN":
            return shifted*shifted
        if easing == "EASE_OUT":
            return 1.0-(1.0-shifted)*(1.0-shifted)
        return shifted

    def test_counts_one_and_eight_match_uniform_numeric_oracle(self):
        self._capture(1, 0.0)
        self._capture(11, 10.0)
        self.obj.b4ml.easing = "LINEAR"
        self._set_frame(6)
        before_anchors = self._anchors()
        untouched = self._untouched()
        one = workflow.create_inbetween_series(self.obj, self.scene, 1)
        self.assertEqual(one["frames"], [6.0])
        self.assertAlmostEqual(
            json.loads(self._anchor(6).payload)["pose"]["hips"]["location"][0],
            5.0, places=6)
        self.assertEqual(self._anchors()[:2], before_anchors)
        self.assertEqual(self._untouched(), untouched)

        self.obj.b4ml.anchors.remove(len(self.obj.b4ml.anchors)-1)
        self.obj.b4ml.status = "reset"
        before_anchors = self._anchors()
        result = workflow.create_inbetween_series(self.obj, self.scene, 8)
        expected_frames = [
            self._stored(1.0 + 10.0*index/9.0) for index in range(1, 9)]
        self.assertEqual(result["frames"], expected_frames)
        for frame in expected_frames:
            fraction = (frame-1.0)/10.0
            pose = json.loads(self._anchor(frame).payload)["pose"]
            self.assertAlmostEqual(
                pose["hips"]["location"][0], 10.0*fraction, places=5)
            self.assertEqual(len(pose["hips"]["raw_rotation"]), 4)
            self.assertEqual(len(pose["upperarm.fk-L"]["raw_rotation"]), 3)
            expected_q = Quaternion(pose["hips"]["rotation"])
            actual_q = Quaternion(pose["hips"]["raw_rotation"])
            self.assertAlmostEqual(abs(expected_q.dot(actual_q)), 1.0, places=6)
        self.assertEqual(self._anchors()[:2], before_anchors)
        self.assertEqual(self._untouched(), untouched)

    def test_destination_override_with_holds_matches_independent_oracle(self):
        self._capture(1, 0.0)
        self._capture(11, 10.0)
        workflow.set_transition_timing(
            self.obj, 11, True, "EASE_OUT", -.25, .2, .3)
        right_before = self._anchor(11).payload
        self._set_frame(6)
        untouched = self._untouched()
        result = workflow.create_inbetween_series(self.obj, self.scene, 3)
        self.assertEqual(result["timing"], {
            "easing": "EASE_OUT", "bias": -.25,
            "departure_hold": .2, "arrival_hold": .3})
        for frame in result["frames"]:
            fraction = (frame-1.0)/10.0
            weight = self._timing_oracle(
                fraction, "EASE_OUT", -.25, .2, .3)
            payload = json.loads(self._anchor(frame).payload)
            self.assertNotIn("incoming_timing", payload)
            self.assertAlmostEqual(
                payload["pose"]["hips"]["location"][0],
                10.0*weight, places=5)
        self.assertEqual(self._anchor(11).payload, right_before)
        self.assertEqual(workflow.transition_timing(self.obj, 11), {
            "easing": "EASE_OUT", "bias": -.25,
            "departure_hold": .2, "arrival_hold": .3})
        self.assertEqual(self._untouched(), untouched)

    def test_fractional_interval_uses_storage_representable_frames(self):
        self._capture(1, 0.0)
        self._capture(11, 10.0)
        self._anchor(1).frame = 1.25
        self._anchor(11).frame = 2.75
        self._set_frame(2.0)
        result = workflow.create_inbetween_series(self.obj, self.scene, 2)
        expected = [self._stored(1.75), self._stored(2.25)]
        self.assertEqual(result["frames"], expected)
        self.assertTrue(all(1.25 < value < 2.75 for value in result["frames"]))

    def test_bad_counts_and_precision_collapse_fail_before_mutation(self):
        self._capture(1, 0.0)
        self._capture(11, 10.0)
        self._set_frame(6)
        before = self._anchors()
        untouched = self._untouched()
        for count in (0, 9, True, 1.0, "2", None):
            with self.subTest(count=count), self.assertRaisesRegex(
                    ValueError, "between one and eight"):
                workflow.create_inbetween_series(self.obj, self.scene, count)
            self.assertEqual(self._anchors(), before)
            self.assertEqual(self._untouched(), untouched)

        self._anchor(1).frame = 1_000_000.0
        self._anchor(11).frame = 1_000_000.125
        self._set_frame(1_000_000.0625)
        before = self._anchors()
        untouched = self._untouched()
        with self.assertRaisesRegex(ValueError, "precision|ambiguous"):
            workflow.create_inbetween_series(self.obj, self.scene, 8)
        self.assertEqual(self._anchors(), before)
        self.assertEqual(self._untouched(), untouched)

        self._anchor(1_000_000.125).frame = 1_000_001.0
        self._set_frame(1_000_000.5)
        before = self._anchors()
        untouched = self._untouched()
        with self.assertRaisesRegex(ValueError, "evenly spaced.*precision"):
            workflow.create_inbetween_series(self.obj, self.scene, 8)
        self.assertEqual(self._anchors(), before)
        self.assertEqual(self._untouched(), untouched)

        self._anchor(1_000_000.0).frame = 128.0
        self._anchor(1_000_001.0).frame = 128.0001678466797
        self._set_frame(128.00008)
        before = self._anchors()
        untouched = self._untouched()
        with self.assertRaisesRegex(ValueError, "evenly spaced.*precision"):
            workflow.create_inbetween_series(self.obj, self.scene, 7)
        self.assertEqual(self._anchors(), before)
        self.assertEqual(self._untouched(), untouched)

    def test_anchor_and_payload_limits_fail_atomically(self):
        self._capture(1, 0.0)
        self._capture(2, 1.0)
        self._set_frame(1.5)
        before = self._anchors()
        untouched = self._untouched()
        payload_chars = sum(len(anchor.payload) for anchor in self.obj.b4ml.anchors)
        with mock.patch.object(
                workflow, "MAX_ANCHOR_PAYLOAD_CHARS", payload_chars):
            with self.assertRaisesRegex(ValueError, "serialized payload"):
                workflow.create_inbetween_series(self.obj, self.scene, 1)
        self.assertEqual(self._anchors(), before)
        self.assertEqual(self._untouched(), untouched)

        template = self._anchor(2).payload
        for frame in range(3, 129):
            anchor = self.obj.b4ml.anchors.add()
            anchor.frame = frame
            anchor.payload = template
            anchor.name = f"Frame {frame}"
        before = self._anchors()
        untouched = self._untouched()
        with self.assertRaisesRegex(ValueError, "at most 128"):
            workflow.create_inbetween_series(self.obj, self.scene, 1)
        self.assertEqual(self._anchors(), before)
        self.assertEqual(self._untouched(), untouched)

    def test_busy_nla_and_motion_layer_requests_fail_without_changes(self):
        self._capture(1, 0.0)
        self._capture(11, 10.0)
        self._set_frame(6)
        before = self._anchors()
        untouched = self._untouched()

        self.obj.b4ml.temporal_running = True
        with self.assertRaisesRegex(ValueError, "active animation workflow"):
            workflow.create_inbetween_series(self.obj, self.scene, 2)
        self.obj.b4ml.temporal_running = False

        with mock.patch.object(workflow.motion_layer, "find",
                               return_value=object()):
            with self.assertRaisesRegex(ValueError, "kept motion source"):
                workflow.create_inbetween_series(self.obj, self.scene, 2)

        track = self.obj.animation_data.nla_tracks.new()
        track.name = "Blocked"
        track.strips.new(
            "Blocked strip", 1, self.obj.animation_data.action)
        with self.assertRaisesRegex(ValueError, "NLA"):
            workflow.create_inbetween_series(self.obj, self.scene, 2)
        self.obj.animation_data.nla_tracks.remove(track)

        self.assertEqual(self._anchors(), before)
        self.assertEqual(self._untouched(), untouched)

    def test_partial_append_failure_restores_exact_existing_state(self):
        self._capture(1, 0.0)
        self._capture(11, 10.0)
        self._set_frame(6)
        self.scene.tool_settings.use_keyframe_insert_auto = True
        self.hips.select = True
        self.arm.select = False
        self.obj.b4ml.status = "prior status"
        before = self._anchors()
        untouched = self._untouched()
        original = workflow._write_inbetween_anchor
        calls = {"count": 0}

        def fail_after_second(state, item):
            original(state, item)
            calls["count"] += 1
            if calls["count"] == 2:
                raise RuntimeError("forced write failure")

        with mock.patch.object(
                workflow, "_write_inbetween_anchor",
                side_effect=fail_after_second):
            with self.assertRaisesRegex(RuntimeError, "forced write failure"):
                workflow.create_inbetween_series(self.obj, self.scene, 4)
        self.assertEqual(calls["count"], 2)
        self.assertEqual(self._anchors(), before)
        self.assertEqual(self.obj.b4ml.status, "prior status")
        self.assertEqual(self._untouched(), untouched)

    def test_operator_and_save_reload_preserve_series(self):
        self._capture(1, 0.0)
        self._capture(11, 10.0)
        self._set_frame(6)
        source_before = self._source_digest()
        before = self._anchors()
        result = bpy.ops.b4ml.inbetween_series(
            "EXEC_DEFAULT", count=2)
        self.assertEqual(result, {"FINISHED"})
        expected = [self._stored(1.0+10.0/3.0),
                    self._stored(1.0+20.0/3.0)]
        self.assertEqual(
            sorted(frame for frame, _name, _payload in self._anchors()),
            sorted([1.0, 11.0] + expected))
        self.assertEqual(self._source_digest(), source_before)

        name = self.obj.name
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / "inbetween-series-v1.blend")
            bpy.ops.wm.save_as_mainfile(filepath=path)
            bpy.ops.wm.open_mainfile(
                filepath=path, load_ui=False, use_scripts=False)
            self.obj = bpy.data.objects[name]
            self.scene = bpy.context.scene
            self.hips = self.obj.pose.bones["hips"]
            self.arm = self.obj.pose.bones["upperarm.fk-L"]
            bpy.context.view_layer.objects.active = self.obj
            self.obj.select_set(True)
            self.assertEqual(len(self.obj.b4ml.anchors), 4)
            self.assertEqual(self._source_digest(), source_before)


if __name__ == "__main__":
    result = unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(
            InbetweenSeriesTests))
    if not result.wasSuccessful():
        raise SystemExit(1)
