"""Bforartists tests for destination-owned per-transition timing."""
from pathlib import Path
import copy
import json
import math
import os
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [os.environ.get("B4ML_PACKAGE", str(ROOT)), str(ROOT / "tests")]

import bpy

import b4artists_ml
from b4artists_ml import math_core, quadruped_gait, workflow


class TransitionTimingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not b4artists_ml.is_bforartists():
            raise unittest.SkipTest("Bforartists required")
        b4artists_ml.register()

    def setUp(self):
        if bpy.context.object and bpy.context.object.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
        data = bpy.data.armatures.new("Transition Timing Rig")
        self.obj = bpy.data.objects.new("Transition Timing Rig", data)
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
        obj = bpy.data.objects.get("Transition Timing Rig")
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

    def _source_digest(self):
        return quadruped_gait._action_digest(self.obj, self.obj.animation_data.action)

    def _payloads(self):
        return [(anchor.frame, anchor.payload) for anchor in self.obj.b4ml.anchors]

    def test_destination_owned_overrides_drive_independent_intervals(self):
        self._capture(1, 0.0)
        self._capture(11, 10.0)
        self._capture(21, 0.0)
        workflow.set_transition_timing(self.obj, 11, True, "LINEAR", 1.0)
        workflow.set_transition_timing(self.obj, 21, True, "EASE_IN", 0.0)
        source = self.obj.animation_data.action
        source_before = self._source_digest()
        workflow.preview(self.obj, self.scene, "SMOOTH", timing_bias=-1.0)
        candidate = self.obj.animation_data.action
        self.scene.frame_set(6)
        self.assertAlmostEqual(self.bone.location.x, 9.0, places=5)
        self.scene.frame_set(16)
        self.assertAlmostEqual(self.bone.location.x, 7.5, places=5)
        self.scene.frame_set(11)
        self.assertAlmostEqual(self.bone.location.x, 10.0, places=6)
        metadata = json.loads(candidate["b4ml_transition_timing"])
        self.assertEqual(metadata, [
            {"bias": 1.0, "destination_frame": 11.0,
             "easing": "LINEAR", "departure_hold": 0.0,
             "arrival_hold": 0.0, "override": True},
            {"bias": 0.0, "destination_frame": 21.0,
             "easing": "EASE_IN", "departure_hold": 0.0,
             "arrival_hold": 0.0, "override": True},
        ])
        workflow.finish_preview(self.obj, self.scene, keep=False)
        self.assertIs(self.obj.animation_data.action, source)
        self.assertEqual(self._source_digest(), source_before)

    def test_disabled_override_uses_global_timing(self):
        self._capture(1, 0.0)
        self._capture(11, 10.0)
        workflow.set_transition_timing(self.obj, 11, True, "EASE_IN", 1.0)
        workflow.set_transition_timing(self.obj, 11, False)
        self.assertIsNone(workflow.transition_timing(self.obj, 11))
        workflow.preview(self.obj, self.scene, "EASE_OUT", timing_bias=-0.5)
        self.scene.frame_set(6)
        expected = 10.0 * math_core.timing_weight(.5, "EASE_OUT", -.5)
        self.assertAlmostEqual(self.bone.location.x, expected, places=5)
        metadata = json.loads(self.obj.animation_data.action["b4ml_transition_timing"])
        self.assertFalse(metadata[0]["override"])
        workflow.finish_preview(self.obj, self.scene, keep=False)

    def test_invalid_and_corrupt_edits_fail_before_mutation(self):
        self._capture(1, 0.0)
        self._capture(11, 10.0)
        before_payloads = self._payloads()
        before_source = self._source_digest()
        cases = ((1, True, "LINEAR", 0.0),
                 (11, True, "BOUNCE", 0.0),
                 (11, True, "LINEAR", float("nan")),
                 (99, True, "LINEAR", 0.0))
        for case in cases:
            with self.subTest(case=case), self.assertRaises(ValueError):
                workflow.set_transition_timing(self.obj, *case)
            self.assertEqual(self._payloads(), before_payloads)
            self.assertEqual(self._source_digest(), before_source)
        target = next(anchor for anchor in self.obj.b4ml.anchors
                      if abs(anchor.frame-11) < 1e-5)
        valid = target.payload
        payload = json.loads(valid)
        payload["incoming_timing"] = {"easing": "LINEAR", "bias": "early"}
        target.payload = json.dumps(payload)
        with self.assertRaisesRegex(ValueError, "per-transition"):
            workflow.preview(self.obj, self.scene)
        self.assertIsNone(self.obj.b4ml.candidate_action)
        self.assertEqual(self._source_digest(), before_source)
        target.payload = valid

    def test_hostile_recapture_and_ui_marker_are_bounded(self):
        self._capture(1, 0.0)
        self._capture(11, 10.0)
        target = next(anchor for anchor in self.obj.b4ml.anchors
                      if abs(anchor.frame-11) < 1e-5)
        valid = target.payload
        hostile_values = (
            '{"padding":"' + ('x' * workflow.MAX_ANCHOR_PAYLOAD_CHARS) + '"}',
            ('[' * 1500) + '0' + (']' * 1500),
        )
        for hostile in hostile_values:
            with self.subTest(size=len(hostile)):
                target.payload = hostile
                self.assertFalse(workflow.has_transition_timing_override(hostile))
                self.scene.frame_set(11)
                with self.assertRaisesRegex(ValueError, 'Invalid pose anchor'):
                    workflow.capture_anchor(self.obj, self.scene, False)
        target.payload = valid

    def test_null_record_is_neutral_for_projection_and_metadata(self):
        self._capture(1, 0.0)
        self._capture(3, 2.0)
        target = next(anchor for anchor in self.obj.b4ml.anchors
                      if abs(anchor.frame-3) < 1e-5)
        payload = json.loads(target.payload)
        payload['incoming_timing'] = None
        target.payload = json.dumps(payload)
        self.assertFalse(workflow.has_transition_timing_override(target.payload))
        rows = workflow.read_anchors(self.obj)
        samples = {}
        for frame in (1.0, 2.0, 3.0):
            samples[frame] = copy.deepcopy(rows[0 if frame < 3 else 1][1]['pose'])
            if frame == 2:
                samples[frame]['hips']['location'] = (1.0, 0.0, 0.0)
        workflow.preview(self.obj, self.scene, pose_samples=samples)
        candidate = self.obj.animation_data.action
        self.assertNotIn('b4ml_transition_timing', candidate)
        workflow.finish_preview(self.obj, self.scene, keep=False)

    def test_recapture_rejects_ambiguous_overcount_and_growth_atomically(self):
        self._capture(1, 0.0)
        self._capture(11, 10.0)
        source_before = self._source_digest()
        status_before = self.obj.b4ml.status
        target = next(anchor for anchor in self.obj.b4ml.anchors
                      if abs(anchor.frame-11) < 1e-5)
        duplicate = self.obj.b4ml.anchors.add()
        duplicate.frame = 11
        duplicate.payload = target.payload
        duplicate.name = target.name
        ambiguous = self._payloads()
        self.scene.frame_set(11)
        with self.assertRaisesRegex(ValueError, 'ambiguous'):
            workflow.capture_anchor(self.obj, self.scene, False)
        self.assertEqual(self._payloads(), ambiguous)
        self.assertEqual(self.obj.b4ml.status, status_before)
        self.assertEqual(self._source_digest(), source_before)
        self.obj.b4ml.anchors.remove(len(self.obj.b4ml.anchors)-1)

        while len(self.obj.b4ml.anchors) <= 128:
            extra = self.obj.b4ml.anchors.add()
            extra.frame = 1000 + len(self.obj.b4ml.anchors)
            extra.payload = '{}'
        overcount = self._payloads()
        with self.assertRaisesRegex(ValueError, 'at most 128'):
            workflow.capture_anchor(self.obj, self.scene, False)
        self.assertEqual(self._payloads(), overcount)
        self.assertEqual(self.obj.b4ml.status, status_before)
        self.assertEqual(self._source_digest(), source_before)
        while len(self.obj.b4ml.anchors) > 2:
            self.obj.b4ml.anchors.remove(len(self.obj.b4ml.anchors)-1)

        first = next(anchor for anchor in self.obj.b4ml.anchors
                     if abs(anchor.frame-1) < 1e-5)
        target = next(anchor for anchor in self.obj.b4ml.anchors
                      if abs(anchor.frame-11) < 1e-5)
        full_target_payload = target.payload
        target.payload = '{}'
        first_payload = json.loads(first.payload)
        first_payload['padding'] = ''
        base = json.dumps(first_payload)
        desired = workflow.MAX_ANCHOR_PAYLOAD_CHARS - len(target.payload) - 1
        first_payload['padding'] = 'x' * (desired - len(base))
        first.payload = json.dumps(first_payload)
        self.assertEqual(sum(len(value.payload) for value in self.obj.b4ml.anchors),
                         workflow.MAX_ANCHOR_PAYLOAD_CHARS - 1)
        before_growth = self._payloads()
        with self.assertRaisesRegex(ValueError, 'serialized payload limit'):
            workflow.capture_anchor(self.obj, self.scene, False)
        self.assertEqual(self._payloads(), before_growth)
        self.assertEqual(self.obj.b4ml.status, status_before)
        self.assertEqual(self._source_digest(), source_before)
        target.payload = full_target_payload

    def test_recapture_preserves_override_but_pose_reuse_does_not_copy_it(self):
        self._capture(1, 0.0)
        self._capture(11, 10.0)
        workflow.set_transition_timing(self.obj, 11, True, "EASE_OUT", .4)
        self._capture(11, 12.0)
        self.assertEqual(workflow.transition_timing(self.obj, 11),
                         {"easing": "EASE_OUT", "bias": .4,
                          "departure_hold": 0.0, "arrival_hold": 0.0})
        self.scene.frame_set(21)
        workflow.reuse_anchor(self.obj, self.scene, 11)
        self.assertIsNone(workflow.transition_timing(self.obj, 21))

    def test_active_candidate_and_projected_samples_reject_overrides(self):
        self._capture(1, 0.0)
        self._capture(3, 2.0)
        workflow.set_transition_timing(self.obj, 3, True, "EASE_IN", .2)
        rows = workflow.read_anchors(self.obj)
        samples = {}
        for frame in (1.0, 2.0, 3.0):
            samples[frame] = copy.deepcopy(rows[0 if frame < 3 else 1][1]["pose"])
            if frame == 2:
                samples[frame]["hips"]["location"] = (1.0, 0.0, 0.0)
        source = self.obj.animation_data.action
        before = self._source_digest()
        with self.assertRaisesRegex(ValueError, "per-transition overrides"):
            workflow.preview(self.obj, self.scene, pose_samples=samples)
        self.assertIs(self.obj.animation_data.action, source)
        self.assertIsNone(self.obj.b4ml.candidate_action)
        self.assertEqual(self._source_digest(), before)
        workflow.set_transition_timing(self.obj, 3, False)
        workflow.preview(self.obj, self.scene)
        payloads = self._payloads()
        with self.assertRaisesRegex(ValueError, "active animation workflow"):
            workflow.set_transition_timing(self.obj, 3, True, "LINEAR", 0.0)
        self.assertEqual(self._payloads(), payloads)
        workflow.finish_preview(self.obj, self.scene, keep=False)

    def test_operator_and_save_reload(self):
        self._capture(1, 0.0)
        self._capture(11, 10.0)
        source_before = self._source_digest()
        result = bpy.ops.b4ml.transition_timing(
            'EXEC_DEFAULT', frame=11, use_override=True,
            easing="EASE_OUT", bias=-.35)
        self.assertEqual(result, {"FINISHED"})
        timing = workflow.transition_timing(self.obj, 11)
        self.assertEqual(timing["easing"], "EASE_OUT")
        self.assertAlmostEqual(timing["bias"], -.35, places=6)
        self.assertEqual(self._source_digest(), source_before)
        name = self.obj.name
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / "transition-timing-v1.blend")
            bpy.ops.wm.save_as_mainfile(filepath=path)
            bpy.ops.wm.open_mainfile(filepath=path, load_ui=False, use_scripts=False)
            self.obj = bpy.data.objects[name]
            self.bone = self.obj.pose.bones["hips"]
            self.scene = bpy.context.scene
            bpy.context.view_layer.objects.active = self.obj
            self.obj.select_set(True)
            timing = workflow.transition_timing(self.obj, 11)
            self.assertEqual(timing["easing"], "EASE_OUT")
            self.assertAlmostEqual(timing["bias"], -.35, places=6)
            self.assertEqual(self._source_digest(), source_before)


if __name__ == "__main__":
    result = unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(TransitionTimingTests))
    if not result.wasSuccessful():
        raise SystemExit(1)
