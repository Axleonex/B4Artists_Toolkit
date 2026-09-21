"""Bforartists tests for atomic ripple retiming of priority poses."""
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


class RippleRetimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not b4artists_ml.is_bforartists():
            raise unittest.SkipTest("Bforartists required")
        b4artists_ml.register()

    def setUp(self):
        if bpy.context.object and bpy.context.object.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
        data = bpy.data.armatures.new("Ripple Retime Rig")
        self.obj = bpy.data.objects.new("Ripple Retime Rig", data)
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
        obj = bpy.data.objects.get("Ripple Retime Rig")
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

    def _four(self, order=(1, 6, 11, 16)):
        values = {1: 0.0, 6: 5.0, 11: 10.0, 16: 15.0}
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

    def test_interior_ripple_preserves_payload_timing_suffix_spacing_and_state(self):
        self._four()
        for frame, easing, bias, departure, arrival in (
                (6, "EASE_OUT", -.25, .2, .3),
                (11, "SMOOTH", .1, .05, .15),
                (16, "EASE_IN", .2, .1, .2)):
            workflow.set_transition_timing(
                self.obj, frame, True, easing, bias, departure, arrival)
        for frame, suffix in ((6, "hero beat"), (11, "anticipation"),
                              (16, "landing")):
            self._anchor(frame).name += " (" + suffix + ")"
        baseline = self._anchors()
        payloads = {frame: self._anchor(frame).payload for frame in (1, 6, 11, 16)}
        suffixes = {frame: self._anchor(frame).name.split(" - ", 1)[1]
                    for frame in (1, 6, 11, 16)}
        self.scene.tool_settings.use_keyframe_insert_auto = True
        self.hips.select = True
        self.arm.select = False
        self._set_frame(8)
        untouched = self._untouched()

        result = workflow.ripple_retime(self.obj, self.scene, 6)

        self.assertEqual(result, {"source_frame": 6.0,
                                  "destination_frame": 8.0,
                                  "delta": 2.0, "moved_count": 3})
        self.assertEqual([row[0] for row in workflow.read_anchors(self.obj)],
                         [1.0, 8.0, 13.0, 18.0])
        self.assertEqual(self._anchor(1).name, baseline[0][1])
        for old, new in ((6, 8), (11, 13), (16, 18)):
            self.assertEqual(self._anchor(new).payload, payloads[old])
            self.assertEqual(self._anchor(new).name,
                             f"Frame {new:.9g} - " + suffixes[old])
        self.assertEqual(workflow.transition_timing(self.obj, 8), {
            "easing": "EASE_OUT", "bias": -.25,
            "departure_hold": .2, "arrival_hold": .3})
        self.assertEqual(workflow.transition_timing(self.obj, 13), {
            "easing": "SMOOTH", "bias": .1,
            "departure_hold": .05, "arrival_hold": .15})
        self.assertEqual(self._untouched(), untouched)

    def test_first_last_both_directions_and_unsorted_storage(self):
        self._four(order=(11, 1, 16, 6))
        self.assertEqual([row[0] for row in self._anchors()], [11.0, 1.0, 16.0, 6.0])
        self._set_frame(4)
        workflow.ripple_retime(self.obj, self.scene, 6)
        self.assertEqual([row[0] for row in self._anchors()], [9.0, 1.0, 14.0, 4.0])
        self.assertEqual([row[0] for row in workflow.read_anchors(self.obj)],
                         [1.0, 4.0, 9.0, 14.0])
        self._set_frame(15)
        result = workflow.ripple_retime(self.obj, self.scene, 14)
        self.assertEqual(result["moved_count"], 1)
        self.assertEqual([row[0] for row in workflow.read_anchors(self.obj)],
                         [1.0, 4.0, 9.0, 15.0])
        self._set_frame(3)
        result = workflow.ripple_retime(self.obj, self.scene, 1)
        self.assertEqual(result["moved_count"], 4)
        self.assertEqual([row[0] for row in workflow.read_anchors(self.obj)],
                         [3.0, 6.0, 11.0, 17.0])

    def test_float32_spacing_threshold_span_and_absolute_bounds(self):
        self._four()
        requested = 8.123456789
        stored = self._stored(requested)
        self._set_frame(requested)
        result = workflow.ripple_retime(self.obj, self.scene, 6)
        self.assertEqual(result["destination_frame"], stored)
        self.assertTrue(self._anchor(stored).name.startswith(
            f"Frame {stored:.9g} - "))

        self.obj.b4ml.anchors.clear()
        for frame, value in ((1, 0.0), (11, 10.0), (241, 20.0)):
            self._capture(frame, value)
        self._set_frame(12)
        before = self._anchors()
        with self.assertRaisesRegex(ValueError, "240 frames"):
            workflow.ripple_retime(self.obj, self.scene, 11)
        self.assertEqual(self._anchors(), before)

        self.obj.b4ml.anchors.clear()
        self._four()
        original = workflow._stored_anchor_frame

        def within_one_percent(value):
            stored_value = original(value)
            return original(stored_value + .04) if abs(value-18) < 1e-4 else stored_value

        self._set_frame(8)
        with mock.patch.object(workflow, "_stored_anchor_frame",
                               side_effect=within_one_percent):
            workflow.ripple_retime(self.obj, self.scene, 6)
        self.assertLess(abs((self._anchor(self._stored(18.04)).frame-
                             self._anchor(13).frame)-5), .05)

        self.obj.b4ml.anchors.clear()
        self._four()

        def beyond_one_percent(value):
            stored_value = original(value)
            return original(stored_value + .06) if abs(value-18) < 1e-4 else stored_value

        self._set_frame(8)
        before = self._anchors()
        with mock.patch.object(workflow, "_stored_anchor_frame",
                               side_effect=beyond_one_percent), self.assertRaisesRegex(
                                   ValueError, "spacing"):
            workflow.ripple_retime(self.obj, self.scene, 6)
        self.assertEqual(self._anchors(), before)

        frame_max = int(self.scene.bl_rna.properties["frame_current"].hard_max)
        self.scene.frame_set(frame_max, subframe=.5)
        with self.assertRaisesRegex(ValueError, "timeline frame range"):
            workflow.ripple_retime(self.obj, self.scene, 1)

    def test_collision_hostile_names_ambiguity_and_stale_dialog_reject(self):
        self._four()
        baseline = self._anchors()
        for source in (True, "6", None, float("nan"), float("inf"), 99):
            self._set_frame(8)
            with self.subTest(source=source), self.assertRaises(ValueError):
                workflow.ripple_retime(self.obj, self.scene, source)
            self.assertEqual(self._anchors(), baseline)
        for destination, message in ((6, "different frame"),
                                     (1, "previous saved pose"),
                                     (-20, "previous saved pose")):
            self._set_frame(destination)
            with self.subTest(destination=destination), self.assertRaisesRegex(
                    ValueError, message):
                workflow.ripple_retime(self.obj, self.scene, 6)
            self.assertEqual(self._anchors(), baseline)

        anchor = self._anchor(11)
        old_name = anchor.name
        for malformed in ("unbound", "Frame 11 - ", "Frame 10 - wrong"):
            anchor.name = malformed
            self._set_frame(8)
            with self.subTest(name=malformed), self.assertRaisesRegex(
                    ValueError, "display name"):
                workflow.ripple_retime(self.obj, self.scene, 6)
            anchor.name = old_name

        self._set_frame(8)
        context = workflow.ripple_retime_context(self.obj, self.scene, 6)
        payload = json.loads(self._anchor(16).payload)
        payload["dialog_stale_marker"] = True
        self._anchor(16).payload = json.dumps(payload, allow_nan=False)
        stale = self._anchors()
        with self.assertRaisesRegex(ValueError, "Saved poses changed"):
            workflow.ripple_retime(
                self.obj, self.scene, 6, context["destination_frame"],
                context["binding"])
        self.assertEqual(self._anchors(), stale)

    def test_every_busy_owner_nla_and_motion_layer_fail_closed(self):
        self._four()
        self._set_frame(8)
        state = self.obj.b4ml
        baseline = self._anchors()
        for field in ("posing_payload", "body_payload", "quadruped_payload"):
            setattr(state, field, "busy")
            with self.subTest(field=field), self.assertRaisesRegex(
                    ValueError, "active animation workflow"):
                workflow.ripple_retime(self.obj, self.scene, 6)
            setattr(state, field, "")
        for field in ("temporal_running", "body_running", "body_live",
                      "contact_running", "contact_suggest_running",
                      "flight_running", "secondary_running", "cleanup_running"):
            setattr(state, field, True)
            with self.subTest(field=field), self.assertRaisesRegex(
                    ValueError, "active animation workflow"):
                workflow.ripple_retime(self.obj, self.scene, 6)
            setattr(state, field, False)
        state.candidate_action = self.obj.animation_data.action
        with self.assertRaisesRegex(ValueError, "active animation workflow"):
            workflow.ripple_retime(self.obj, self.scene, 6)
        state.candidate_action = None
        with mock.patch.object(workflow.motion_layer, "find", return_value=object()):
            with self.assertRaisesRegex(ValueError, "kept motion source"):
                workflow.ripple_retime(self.obj, self.scene, 6)

        track = self.obj.animation_data.nla_tracks.new()
        track.name = "Ripple NLA"
        track.strips.new("Ripple strip", 1, self.obj.animation_data.action)
        track.mute = True
        workflow.ripple_retime(self.obj, self.scene, 6)
        self._set_frame(6)
        workflow.ripple_retime(self.obj, self.scene, 8)
        track.mute = False
        self._set_frame(8)
        with self.assertRaisesRegex(ValueError, "Mute NLA"):
            workflow.ripple_retime(self.obj, self.scene, 6)
        self.obj.animation_data.nla_tracks.remove(track)
        self.assertEqual(self._anchors(), baseline)

    def test_partial_multitem_writes_restore_complete_collection_and_status(self):
        self._four()
        self._set_frame(8)
        self.obj.b4ml.status = "prior status"
        baseline = self._anchors()
        untouched = self._untouched()
        original = workflow._write_retimed_anchor
        calls = []

        def fail_second(anchor, destination, name):
            calls.append(anchor.as_pointer())
            original(anchor, destination, name)
            if len(calls) == 2:
                raise RuntimeError("forced second item failure")

        with mock.patch.object(workflow, "_write_retimed_anchor",
                               side_effect=fail_second), self.assertRaisesRegex(
                                   RuntimeError, "second item"):
            workflow.ripple_retime(self.obj, self.scene, 6)
        self.assertEqual(len(calls), 2)
        self.assertEqual(self._anchors(), baseline)
        self.assertEqual(self.obj.b4ml.status, "prior status")
        self.assertEqual(self._untouched(), untouched)

        for topology_mutation in ("clear", "remove", "add", "move"):
            calls.clear()

            def mutate_topology(anchor, destination, name,
                                mutation=topology_mutation):
                original(anchor, destination, name)
                if calls:
                    return
                calls.append(anchor.as_pointer())
                anchors = self.obj.b4ml.anchors
                if mutation == "clear":
                    anchors.clear()
                elif mutation == "remove":
                    anchors.remove(0)
                elif mutation == "add":
                    extra = anchors.add()
                    extra.frame = 99
                    extra.name = "Frame 99 - injected"
                    extra.payload = baseline[0][2]
                else:
                    anchors.move(0, 1)

            with self.subTest(topology=topology_mutation), mock.patch.object(
                    workflow, "_write_retimed_anchor",
                    side_effect=mutate_topology), self.assertRaises(Exception):
                workflow.ripple_retime(self.obj, self.scene, 6)
            self.assertEqual(self._anchors(), baseline)
            self.assertEqual(self.obj.b4ml.status, "prior status")
            self.assertEqual(self._untouched(), untouched)

        calls.clear()

        def mutate_unmoved(anchor, destination, name):
            original(anchor, destination, name)
            if not calls:
                self._anchor(1).name += " corrupted"
            calls.append(anchor.as_pointer())

        with mock.patch.object(workflow, "_write_retimed_anchor",
                               side_effect=mutate_unmoved), self.assertRaisesRegex(
                                   ValueError, "changed unexpectedly"):
            workflow.ripple_retime(self.obj, self.scene, 6)
        self.assertEqual(self._anchors(), baseline)
        self.assertEqual(self.obj.b4ml.status, "prior status")
        self.assertEqual(self._untouched(), untouched)

    def test_dialog_binding_covers_order_frame_name_payload_and_timeline(self):
        mutations = ("order", "frame", "name", "payload")
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                self.obj.b4ml.anchors.clear()
                self._four()
                self._set_frame(8)
                context = workflow.ripple_retime_context(self.obj, self.scene, 6)
                baseline = self._anchors()
                if mutation == "order":
                    self.obj.b4ml.anchors.move(3, 0)
                elif mutation == "frame":
                    self._anchor(16).frame = 16.25
                elif mutation == "name":
                    self._anchor(16).name += " (changed)"
                else:
                    payload = json.loads(self._anchor(16).payload)
                    payload["changed"] = mutation
                    self._anchor(16).payload = json.dumps(payload, allow_nan=False)
                changed = self._anchors()
                with self.assertRaisesRegex(ValueError, "Saved poses changed"):
                    workflow.ripple_retime(
                        self.obj, self.scene, 6, context["destination_frame"],
                        context["binding"])
                self.assertEqual(self._anchors(), changed)
                self.assertNotEqual(changed, baseline)
        self.obj.b4ml.anchors.clear()
        self._four()
        self._set_frame(8)
        context = workflow.ripple_retime_context(self.obj, self.scene, 6)
        self._set_frame(9)
        before = self._anchors()
        with self.assertRaisesRegex(ValueError, "Timeline changed"):
            workflow.ripple_retime(
                self.obj, self.scene, 6, context["destination_frame"],
                context["binding"])
        self.assertEqual(self._anchors(), before)

    def test_operator_and_save_reload_preserve_complete_ripple(self):
        self._four()
        payloads = [self._anchor(frame).payload for frame in (1, 6, 11, 16)]
        source_digest = self._source_digest()
        self._set_frame(8.25)
        context = workflow.ripple_retime_context(self.obj, self.scene, 6)
        result = bpy.ops.b4ml.ripple_retime(
            "EXEC_DEFAULT", source_frame=6, destination_frame=8.25,
            moved_count=3, source_binding=context["binding"])
        self.assertEqual(result, {"FINISHED"})
        self.assertEqual([row[0] for row in workflow.read_anchors(self.obj)],
                         [1.0, 8.25, 13.25, 18.25])
        self.assertEqual([self._anchor(frame).payload
                          for frame in (1, 8.25, 13.25, 18.25)], payloads)
        self.assertEqual(self._source_digest(), source_digest)

        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / "ripple-retime-v1.blend")
            bpy.ops.wm.save_as_mainfile(filepath=path)
            bpy.ops.wm.open_mainfile(filepath=path, load_ui=False, use_scripts=False)
            self.scene = bpy.context.scene
            self.obj = bpy.data.objects["Ripple Retime Rig"]
            self.hips = self.obj.pose.bones["hips"]
            self.arm = self.obj.pose.bones["upperarm.fk-L"]
            self.leg = self.obj.pose.bones["thigh.fk-R"]
            bpy.context.view_layer.objects.active = self.obj
            self.obj.select_set(True)
            self.assertEqual([row[0] for row in workflow.read_anchors(self.obj)],
                             [1.0, 8.25, 13.25, 18.25])
            self.assertEqual([self._anchor(frame).payload
                              for frame in (1, 8.25, 13.25, 18.25)], payloads)
            self.assertEqual(self._source_digest(), source_digest)


if __name__ == "__main__":
    result = unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(RippleRetimeTests))
    if not result.wasSuccessful():
        raise SystemExit(1)
