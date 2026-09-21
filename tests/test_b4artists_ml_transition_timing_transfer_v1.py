"""Bforartists tests for the rig-local transition timing clipboard."""
from pathlib import Path
import json
import os
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [os.environ.get("B4ML_PACKAGE", str(ROOT)), str(ROOT / "tests")]

import bpy

import b4artists_ml
from b4artists_ml import quadruped_gait, workflow


class TransitionTimingTransferTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not b4artists_ml.is_bforartists():
            raise unittest.SkipTest("Bforartists required")
        b4artists_ml.register()

    def setUp(self):
        if bpy.context.object and bpy.context.object.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
        data = bpy.data.armatures.new("Timing Transfer Rig")
        self.obj = bpy.data.objects.new("Timing Transfer Rig", data)
        bpy.context.scene.collection.objects.link(self.obj)
        bpy.context.view_layer.objects.active = self.obj
        self.obj.select_set(True)
        bpy.ops.object.mode_set(mode="EDIT")
        for index, name in enumerate(("hips", "upperarm.fk-L", "thigh.fk-R")):
            bone = data.edit_bones.new(name)
            bone.head = (float(index), 0.0, 0.0)
            bone.tail = (float(index), 0.0, 1.0)
        bpy.ops.object.mode_set(mode="POSE")
        self.bone = self.obj.pose.bones["hips"]
        self.bone.rotation_mode = "QUATERNION"
        self.scene = bpy.context.scene
        self.scene.frame_set(1)

    def tearDown(self):
        if bpy.context.object and bpy.context.object.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
        obj = bpy.data.objects.get("Timing Transfer Rig")
        if obj:
            data = obj.data
            bpy.data.objects.remove(obj, do_unlink=True)
            if not data.users:
                bpy.data.armatures.remove(data)

    def _capture(self, frame, x):
        self.scene.frame_set(frame)
        self.bone.location.x = x
        self.bone.keyframe_insert("location", frame=frame)
        workflow.capture_anchor(self.obj, self.scene, False)

    def _three_anchors(self):
        self._capture(1, 0.0)
        self._capture(11, 10.0)
        self._capture(21, 20.0)

    def _source_digest(self):
        return quadruped_gait._action_digest(self.obj, self.obj.animation_data.action)

    def _payloads(self):
        return [(anchor.frame, anchor.payload) for anchor in self.obj.b4ml.anchors]

    def test_copy_override_and_paste_preserve_exact_timing_and_source(self):
        self._three_anchors()
        workflow.set_transition_timing(
            self.obj, 11, True, "EASE_OUT", -.25, .2, .3)
        source_before = self._source_digest()
        copied = workflow.copy_transition_timing(self.obj, 11)
        self.assertEqual(copied["source"], "OVERRIDE")
        self.assertEqual(copied["timing"], {
            "easing": "EASE_OUT", "bias": -.25,
            "departure_hold": .2, "arrival_hold": .3})
        workflow.paste_transition_timing(self.obj, 21)
        self.assertEqual(workflow.transition_timing(self.obj, 21), copied["timing"])
        self.assertEqual(workflow.transition_timing(self.obj, 11), copied["timing"])
        self.assertEqual(self._source_digest(), source_before)

    def test_copy_global_timing_is_a_stable_explicit_snapshot(self):
        self._three_anchors()
        self.obj.b4ml.easing = "EASE_IN"
        self.obj.b4ml.timing_bias = .4
        copied = workflow.copy_transition_timing(self.obj, 11)
        self.assertEqual(copied["source"], "GLOBAL_SNAPSHOT")
        self.obj.b4ml.easing = "LINEAR"
        self.obj.b4ml.timing_bias = -1.0
        workflow.paste_transition_timing(self.obj, 21)
        pasted = workflow.transition_timing(self.obj, 21)
        self.assertEqual(pasted["easing"], "EASE_IN")
        self.assertAlmostEqual(pasted["bias"], .4, places=6)
        self.assertEqual(pasted["departure_hold"], 0.0)
        self.assertEqual(pasted["arrival_hold"], 0.0)

    def test_paste_replaces_only_the_destination_record(self):
        self._three_anchors()
        workflow.set_transition_timing(self.obj, 11, True, "EASE_OUT", -.2, .1, .2)
        workflow.set_transition_timing(self.obj, 21, True, "EASE_IN", .8, .0, .1)
        first_before = next(anchor.payload for anchor in self.obj.b4ml.anchors
                            if abs(anchor.frame-1) < 1e-5)
        workflow.copy_transition_timing(self.obj, 11)
        clipboard = self.obj.b4ml.timing_clipboard
        workflow.paste_transition_timing(self.obj, 21)
        self.assertEqual(workflow.transition_timing(self.obj, 11),
                         workflow.transition_timing(self.obj, 21))
        self.assertEqual(next(anchor.payload for anchor in self.obj.b4ml.anchors
                              if abs(anchor.frame-1) < 1e-5), first_before)
        self.assertEqual(self.obj.b4ml.timing_clipboard, clipboard)

    def test_invalid_frames_and_clipboards_fail_atomically(self):
        self._three_anchors()
        before = self._payloads()
        source_before = self._source_digest()
        for frame, message in ((True, "source frame"), (float('nan'), "source frame"),
                               (1, "first pose"), (99, "missing")):
            with self.subTest(frame=frame), self.assertRaisesRegex(ValueError, message):
                workflow.copy_transition_timing(self.obj, frame)
            self.assertEqual(self._payloads(), before)
        workflow.copy_transition_timing(self.obj, 11)
        with self.assertRaisesRegex(ValueError, "first pose"):
            workflow.paste_transition_timing(self.obj, 1)
        self.assertEqual(self._payloads(), before)
        for hostile in ('', '{}', '{"schema":1}', '[' * 1500 + '0' + ']' * 1500):
            self.obj.b4ml.timing_clipboard = hostile
            with self.subTest(size=len(hostile)), self.assertRaisesRegex(
                    ValueError, "timing"):
                workflow.paste_transition_timing(self.obj, 21)
            self.assertEqual(self._payloads(), before)
            self.assertEqual(self._source_digest(), source_before)

    def test_mode_and_active_workflow_guards_preserve_state(self):
        self._three_anchors()
        before = self._payloads()
        self.obj.b4ml.interpolation_method = "AUTHORED"
        with self.assertRaisesRegex(ValueError, "Pose Blending"):
            workflow.copy_transition_timing(self.obj, 11)
        self.obj.b4ml.interpolation_method = "POSES"
        workflow.copy_transition_timing(self.obj, 11)
        clipboard = self.obj.b4ml.timing_clipboard
        status = self.obj.b4ml.status
        source_before = self._source_digest()
        self.obj.b4ml.interpolation_method = "AUTHORED"
        with self.assertRaisesRegex(ValueError, "Pose Blending"):
            workflow.paste_transition_timing(self.obj, 21)
        self.assertEqual(self._payloads(), before)
        self.assertEqual(self.obj.b4ml.timing_clipboard, clipboard)
        self.assertEqual(self.obj.b4ml.status, status)
        self.assertEqual(self._source_digest(), source_before)
        self.obj.b4ml.interpolation_method = "POSES"
        workflow.preview(self.obj, self.scene)
        with self.assertRaisesRegex(ValueError, "active animation workflow"):
            workflow.paste_transition_timing(self.obj, 21)
        workflow.finish_preview(self.obj, self.scene, keep=False)
        self.assertEqual(self._payloads(), before)

    def test_operator_and_save_reload_preserve_clipboard_and_paste(self):
        self._three_anchors()
        workflow.set_transition_timing(self.obj, 11, True, "EASE_OUT", -.35, .1, .25)
        source_before = self._source_digest()
        result = bpy.ops.b4ml.transition_timing_transfer(
            'EXEC_DEFAULT', operation='COPY', frame=11)
        self.assertEqual(result, {'FINISHED'})
        result = bpy.ops.b4ml.transition_timing_transfer(
            'EXEC_DEFAULT', operation='PASTE', frame=21)
        self.assertEqual(result, {'FINISHED'})
        name = self.obj.name
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / 'timing-transfer-v1.blend')
            bpy.ops.wm.save_as_mainfile(filepath=path)
            bpy.ops.wm.open_mainfile(filepath=path, load_ui=False, use_scripts=False)
            self.obj = bpy.data.objects[name]
            self.bone = self.obj.pose.bones['hips']
            self.scene = bpy.context.scene
            bpy.context.view_layer.objects.active = self.obj
            self.obj.select_set(True)
            self.assertTrue(self.obj.b4ml.timing_clipboard)
            self.assertEqual(workflow.transition_timing(self.obj, 21), {
                'easing': 'EASE_OUT', 'bias': -.35,
                'departure_hold': .1, 'arrival_hold': .25})
            self.assertEqual(self._source_digest(), source_before)


if __name__ == '__main__':
    result = unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(TransitionTimingTransferTests))
    if not result.wasSuccessful():
        raise SystemExit(1)
