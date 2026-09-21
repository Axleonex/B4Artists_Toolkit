"""Bforartists tests for atomic, order-preserving priority-pose retiming."""
from pathlib import Path
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


class PoseRetimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not b4artists_ml.is_bforartists():
            raise unittest.SkipTest("Bforartists required")
        b4artists_ml.register()

    def setUp(self):
        if bpy.context.object and bpy.context.object.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
        data = bpy.data.armatures.new("Pose Retime Rig")
        self.obj = bpy.data.objects.new("Pose Retime Rig", data)
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
        self.scene.tool_settings.use_keyframe_insert_auto = False
        self.scene.frame_set(1)

    def tearDown(self):
        self.scene = bpy.context.scene
        self.scene.tool_settings.use_keyframe_insert_auto = False
        if bpy.context.object and bpy.context.object.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
        obj = bpy.data.objects.get("Pose Retime Rig")
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

    def _three(self, order=(1, 6, 11)):
        values = {1: 0.0, 6: 5.0, 11: 10.0}
        for frame in order:
            self._capture(frame, values[frame])

    def _anchor(self, frame):
        return next(anchor for anchor in self.obj.b4ml.anchors
                    if abs(anchor.frame-frame) < 1e-5)

    def _anchors(self):
        return [(float(anchor.frame), anchor.name, anchor.payload)
                for anchor in self.obj.b4ml.anchors]

    @staticmethod
    def _stored(value):
        return float(struct.unpack("<f", struct.pack("<f", float(value)))[0])

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
                    tuple(bone.rotation_axis_angle), bool(bone.select),
                )
                for bone in self.obj.pose.bones
            },
        }

    def test_interior_retime_preserves_payload_timing_suffix_and_state(self):
        self._three()
        workflow.set_transition_timing(
            self.obj, 6, True, "EASE_OUT", -.25, .2, .3)
        workflow.set_transition_timing(
            self.obj, 11, True, "EASE_IN", .2, .1, .15)
        middle = self._anchor(6)
        middle.name += " (hero beat)"
        middle_payload = middle.payload
        middle_suffix = middle.name.split(" - ", 1)[1]
        following_payload = self._anchor(11).payload
        self.scene.tool_settings.use_keyframe_insert_auto = True
        self.hips.select = True
        self.arm.select = False
        self._set_frame(7.5)
        untouched = self._untouched()

        result = workflow.retime_anchor(self.obj, self.scene, 6)

        self.assertEqual(result, {
            "source_frame": 6.0, "destination_frame": 7.5, "index": 1})
        moved = self._anchor(7.5)
        self.assertEqual(moved.payload, middle_payload)
        self.assertEqual(moved.name, "Frame 7.5 - " + middle_suffix)
        self.assertEqual(self._anchor(11).payload, following_payload)
        self.assertEqual(workflow.transition_timing(self.obj, 7.5), {
            "easing": "EASE_OUT", "bias": -.25,
            "departure_hold": .2, "arrival_hold": .3})
        with self.assertRaisesRegex(ValueError, "missing"):
            workflow.transition_timing(self.obj, 6)
        self.assertEqual(self._untouched(), untouched)

    def test_first_and_last_use_sorted_neighbors_not_collection_order(self):
        self._three(order=(6, 1, 11))
        self.assertEqual([row[0] for row in self._anchors()], [6.0, 1.0, 11.0])
        self._set_frame(2)
        workflow.retime_anchor(self.obj, self.scene, 1)
        self._set_frame(10)
        workflow.retime_anchor(self.obj, self.scene, 11)
        self.assertEqual([row[0] for row in self._anchors()], [6.0, 2.0, 10.0])
        self.assertEqual([row[0] for row in workflow.read_anchors(self.obj)],
                         [2.0, 6.0, 10.0])

    def test_same_collision_reorder_ambiguity_and_stale_dialog_reject(self):
        self._three()
        for destination, message in (
                (6, "different frame"), (1, "previous"),
                (11, "following"), (12, "following"), (0, "previous")):
            self._set_frame(destination)
            before = self._anchors()
            with self.subTest(destination=destination), self.assertRaisesRegex(
                    ValueError, message):
                workflow.retime_anchor(self.obj, self.scene, 6)
            self.assertEqual(self._anchors(), before)

        duplicate = self.obj.b4ml.anchors.add()
        duplicate.frame = 7.000005
        duplicate.payload = self._anchor(11).payload
        duplicate.name = "Frame 7.000005 - 3 controls"
        self._set_frame(7)
        before = self._anchors()
        with self.assertRaisesRegex(ValueError, "following"):
            workflow.retime_anchor(self.obj, self.scene, 6)
        self.assertEqual(self._anchors(), before)
        self.obj.b4ml.anchors.remove(len(self.obj.b4ml.anchors)-1)

        self._set_frame(7)
        context = workflow.retime_anchor_context(self.obj, self.scene, 6)
        self._set_frame(8)
        before = self._anchors()
        with self.assertRaisesRegex(ValueError, "Timeline changed"):
            workflow.retime_anchor(
                self.obj, self.scene, 6, context["destination_frame"])
        self.assertEqual(self._anchors(), before)

    def test_float32_destination_and_exact_span_boundary(self):
        self._capture(1, 0.0)
        self._capture(11, 10.0)
        requested = 2.123456789
        stored = self._stored(requested)
        self._set_frame(requested)
        result = workflow.retime_anchor(self.obj, self.scene, 1)
        self.assertEqual(result["destination_frame"], stored)
        self.assertTrue(self._anchor(stored).name.startswith(
            f"Frame {stored:.9g} - "))

        self.obj.b4ml.anchors.clear()
        self._capture(1, 0.0)
        self._capture(11, 10.0)
        self._set_frame(-229)
        workflow.retime_anchor(self.obj, self.scene, 1)
        self.assertEqual([row[0] for row in workflow.read_anchors(self.obj)],
                         [-229.0, 11.0])
        self._set_frame(-229.00003)
        before = self._anchors()
        with self.assertRaisesRegex(ValueError, "240 frames"):
            workflow.retime_anchor(self.obj, self.scene, -229)
        self.assertEqual(self._anchors(), before)

    def test_hostile_source_and_malformed_saved_data_reject_atomically(self):
        self._three()
        self._set_frame(7)
        baseline = self._anchors()
        for source in (True, "6", None, float("nan"), float("inf"), 99):
            with self.subTest(source=source), self.assertRaises(ValueError):
                workflow.retime_anchor(self.obj, self.scene, source)
            self.assertEqual(self._anchors(), baseline)

        anchor = self._anchor(6)
        old_payload = anchor.payload
        anchor.payload = "{"
        with self.assertRaisesRegex(ValueError, "Invalid pose anchor"):
            workflow.retime_anchor(self.obj, self.scene, 6)
        anchor.payload = old_payload
        old_name = anchor.name
        anchor.name = "unbound display name"
        with self.assertRaisesRegex(ValueError, "display name"):
            workflow.retime_anchor(self.obj, self.scene, 6)
        anchor.name = old_name
        self.assertEqual(self._anchors(), baseline)

    def test_every_busy_owner_nla_and_motion_layer_fail_closed(self):
        self._three()
        self._set_frame(7)
        state = self.obj.b4ml
        baseline = self._anchors()
        string_fields = (
            "posing_payload", "body_payload", "quadruped_payload")
        bool_fields = (
            "temporal_running", "body_running", "body_live", "contact_running",
            "contact_suggest_running", "flight_running", "secondary_running",
            "cleanup_running")
        for field in string_fields:
            setattr(state, field, "busy")
            with self.subTest(field=field), self.assertRaisesRegex(
                    ValueError, "active animation workflow"):
                workflow.retime_anchor(self.obj, self.scene, 6)
            setattr(state, field, "")
        for field in bool_fields:
            setattr(state, field, True)
            with self.subTest(field=field), self.assertRaisesRegex(
                    ValueError, "active animation workflow"):
                workflow.retime_anchor(self.obj, self.scene, 6)
            setattr(state, field, False)
        state.candidate_action = self.obj.animation_data.action
        with self.assertRaisesRegex(ValueError, "active animation workflow"):
            workflow.retime_anchor(self.obj, self.scene, 6)
        state.candidate_action = None

        with mock.patch.object(workflow.motion_layer, "find", return_value=object()):
            with self.assertRaisesRegex(ValueError, "kept motion source"):
                workflow.retime_anchor(self.obj, self.scene, 6)

        track = self.obj.animation_data.nla_tracks.new()
        track.name = "Retime NLA"
        track.strips.new("Retime strip", 1, self.obj.animation_data.action)
        track.mute = True
        workflow.retime_anchor(self.obj, self.scene, 6)
        self._set_frame(6)
        workflow.retime_anchor(self.obj, self.scene, 7)
        track.mute = False
        self._set_frame(7)
        with self.assertRaisesRegex(ValueError, "Mute NLA"):
            workflow.retime_anchor(self.obj, self.scene, 6)
        self.obj.animation_data.nla_tracks.remove(track)
        self.assertEqual(self._anchors(), baseline)

    def test_partial_frame_and_name_writes_restore_exact_state(self):
        self._three()
        self._set_frame(7)
        self.obj.b4ml.status = "prior status"
        baseline = self._anchors()
        untouched = self._untouched()

        def fail_after_frame(anchor, destination, name):
            anchor.frame = destination
            raise RuntimeError("forced frame write failure")

        with mock.patch.object(
                workflow, "_write_retimed_anchor", side_effect=fail_after_frame):
            with self.assertRaisesRegex(RuntimeError, "frame write"):
                workflow.retime_anchor(self.obj, self.scene, 6)
        self.assertEqual(self._anchors(), baseline)
        self.assertEqual(self.obj.b4ml.status, "prior status")
        self.assertEqual(self._untouched(), untouched)

        original = workflow._write_retimed_anchor

        def fail_after_name(anchor, destination, name):
            original(anchor, destination, name)
            raise RuntimeError("forced name write failure")

        with mock.patch.object(
                workflow, "_write_retimed_anchor", side_effect=fail_after_name):
            with self.assertRaisesRegex(RuntimeError, "name write"):
                workflow.retime_anchor(self.obj, self.scene, 6)
        self.assertEqual(self._anchors(), baseline)
        self.assertEqual(self.obj.b4ml.status, "prior status")
        self.assertEqual(self._untouched(), untouched)

    def test_operator_and_save_reload_preserve_retimed_anchor(self):
        self._three()
        payload = self._anchor(6).payload
        source_digest = self._source_digest()
        self._set_frame(7.25)
        result = bpy.ops.b4ml.retime_anchor(
            "EXEC_DEFAULT", source_frame=6, destination_frame=7.25)
        self.assertEqual(result, {"FINISHED"})
        self.assertEqual(self._anchor(7.25).payload, payload)
        self.assertEqual(self._source_digest(), source_digest)

        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / "pose-retime-v1.blend")
            bpy.ops.wm.save_as_mainfile(filepath=path)
            bpy.ops.wm.open_mainfile(filepath=path, load_ui=False, use_scripts=False)
            self.scene = bpy.context.scene
            self.obj = bpy.data.objects["Pose Retime Rig"]
            self.hips = self.obj.pose.bones["hips"]
            self.arm = self.obj.pose.bones["upperarm.fk-L"]
            self.leg = self.obj.pose.bones["thigh.fk-R"]
            bpy.context.view_layer.objects.active = self.obj
            self.obj.select_set(True)
            self.assertEqual(self._anchor(7.25).payload, payload)
            self.assertEqual(self._source_digest(), source_digest)


if __name__ == "__main__":
    result = unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(PoseRetimeTests))
    if not result.wasSuccessful():
        raise SystemExit(1)
