"""Bforartists tests for destination-owned transition hold windows."""
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


class TransitionWindowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not b4artists_ml.is_bforartists():
            raise unittest.SkipTest("Bforartists required")
        b4artists_ml.register()

    def setUp(self):
        if bpy.context.object and bpy.context.object.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
        data = bpy.data.armatures.new("Transition Window Rig")
        self.obj = bpy.data.objects.new("Transition Window Rig", data)
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
        obj = bpy.data.objects.get("Transition Window Rig")
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

    def test_window_is_bounded_monotonic_and_preserves_endpoints(self):
        values = [math_core.timing_window(index / 100, .2, .3)
                  for index in range(101)]
        self.assertEqual(values[0], 0.0)
        self.assertEqual(values[-1], 1.0)
        self.assertTrue(all(left <= right for left, right in zip(values, values[1:])))
        self.assertTrue(all(value == 0.0 for value in values[:21]))
        self.assertTrue(all(value == 1.0 for value in values[70:]))
        self.assertAlmostEqual(math_core.timing_window(.45, .2, .3), .5)

    def test_window_rejects_invalid_values(self):
        cases = ((.5, -.1, 0), (.5, 0, -.1), (.5, .91, 0),
                 (.5, 0, .91), (.5, .5, .41), (.5, True, 0),
                 (.5, 0, float("nan")), (1.1, 0, 0))
        for case in cases:
            with self.subTest(case=case), self.assertRaises(ValueError):
                math_core.timing_window(*case)

    def test_runtime_applies_independent_hold_windows(self):
        self._capture(1, 0.0)
        self._capture(11, 10.0)
        self._capture(21, 0.0)
        workflow.set_transition_timing(
            self.obj, 11, True, "LINEAR", 0.0, .2, .3)
        workflow.set_transition_timing(
            self.obj, 21, True, "LINEAR", 0.0, .4, 0.0)
        source = self.obj.animation_data.action
        before = self._source_digest()
        workflow.preview(self.obj, self.scene, "LINEAR")
        for frame, expected in ((2, 0.0), (3, 0.0), (4, 2.0),
                                (8, 10.0), (13, 10.0), (15, 10.0),
                                (18, 5.0), (21, 0.0)):
            self.scene.frame_set(frame)
            self.assertAlmostEqual(self.bone.location.x, expected, places=5)
        metadata = json.loads(self.obj.animation_data.action["b4ml_transition_timing"])
        self.assertEqual((metadata[0]["departure_hold"], metadata[0]["arrival_hold"]),
                         (.2, .3))
        self.assertEqual((metadata[1]["departure_hold"], metadata[1]["arrival_hold"]),
                         (.4, 0.0))
        workflow.finish_preview(self.obj, self.scene, keep=False)
        self.assertIs(self.obj.animation_data.action, source)
        self.assertEqual(self._source_digest(), before)

    def test_global_fallback_has_full_interval_window(self):
        self._capture(1, 0.0)
        self._capture(11, 10.0)
        workflow.preview(self.obj, self.scene, "LINEAR")
        self.scene.frame_set(3)
        self.assertAlmostEqual(self.bone.location.x, 2.0, places=5)
        metadata = json.loads(self.obj.animation_data.action["b4ml_transition_timing"])[0]
        self.assertFalse(metadata["override"])
        self.assertEqual((metadata["departure_hold"], metadata["arrival_hold"]),
                         (0.0, 0.0))
        workflow.finish_preview(self.obj, self.scene, keep=False)

    def test_invalid_window_and_projection_fail_before_mutation(self):
        self._capture(1, 0.0)
        self._capture(3, 2.0)
        before_payloads = self._payloads()
        before_source = self._source_digest()
        with self.assertRaisesRegex(ValueError, "per-transition"):
            workflow.set_transition_timing(
                self.obj, 3, True, "LINEAR", 0.0, .5, .5)
        self.assertEqual(self._payloads(), before_payloads)
        self.assertEqual(self._source_digest(), before_source)
        workflow.set_transition_timing(
            self.obj, 3, True, "LINEAR", 0.0, .2, .2)
        rows = workflow.read_anchors(self.obj)
        samples = {}
        for frame in (1.0, 2.0, 3.0):
            samples[frame] = copy.deepcopy(rows[0 if frame < 3 else 1][1]["pose"])
            if frame == 2:
                samples[frame]["hips"]["location"] = (1.0, 0.0, 0.0)
        source = self.obj.animation_data.action
        with self.assertRaisesRegex(ValueError, "per-transition overrides"):
            workflow.preview(self.obj, self.scene, pose_samples=samples)
        self.assertIs(self.obj.animation_data.action, source)
        self.assertIsNone(self.obj.b4ml.candidate_action)
        self.assertEqual(self._source_digest(), before_source)

    def test_recapture_preserves_window_and_reuse_starts_without_one(self):
        self._capture(1, 0.0)
        self._capture(11, 10.0)
        workflow.set_transition_timing(
            self.obj, 11, True, "SMOOTH", .2, .15, .25)
        self._capture(11, 12.0)
        timing = workflow.transition_timing(self.obj, 11)
        self.assertEqual(timing["easing"], "SMOOTH")
        self.assertAlmostEqual(timing["bias"], .2)
        self.assertAlmostEqual(timing["departure_hold"], .15)
        self.assertAlmostEqual(timing["arrival_hold"], .25)
        self.scene.frame_set(21)
        workflow.reuse_anchor(self.obj, self.scene, 11)
        self.assertIsNone(workflow.transition_timing(self.obj, 21))

    def test_legacy_two_key_record_previews_and_upgrades_safely(self):
        self._capture(1, 0.0)
        self._capture(11, 10.0)
        target = next(anchor for anchor in self.obj.b4ml.anchors
                      if abs(anchor.frame-11) < 1e-5)
        payload = json.loads(target.payload)
        payload['incoming_timing'] = {'easing': 'LINEAR', 'bias': .5}
        target.payload = json.dumps(payload)
        source = self.obj.animation_data.action
        before = self._source_digest()
        timing = workflow.transition_timing(self.obj, 11)
        self.assertEqual(timing, {'easing': 'LINEAR', 'bias': .5,
                                  'departure_hold': 0.0, 'arrival_hold': 0.0})
        workflow.preview(self.obj, self.scene, 'SMOOTH', timing_bias=-1.0)
        self.scene.frame_set(6)
        self.assertAlmostEqual(
            self.bone.location.x,
            10.0 * math_core.timing_weight(.5, 'LINEAR', .5), places=5)
        metadata = json.loads(self.obj.animation_data.action['b4ml_transition_timing'])[0]
        self.assertEqual((metadata['departure_hold'], metadata['arrival_hold']),
                         (0.0, 0.0))
        workflow.finish_preview(self.obj, self.scene, keep=False)
        self.assertIs(self.obj.animation_data.action, source)
        self.assertEqual(self._source_digest(), before)
        self.scene.frame_set(11)
        workflow.capture_anchor(self.obj, self.scene, False)
        upgraded = json.loads(target.payload)['incoming_timing']
        self.assertEqual(set(upgraded),
                         {'easing', 'bias', 'departure_hold', 'arrival_hold'})
        self.assertEqual(self._source_digest(), before)

    def test_removing_first_anchor_clears_new_first_window_permanently(self):
        self._capture(1, 0.0)
        self._capture(11, 10.0)
        self._capture(21, 20.0)
        workflow.set_transition_timing(
            self.obj, 11, True, "LINEAR", 0.0, .4, .2)
        self.scene.frame_set(1)
        result = bpy.ops.b4ml.action('EXEC_DEFAULT', operation='REMOVE')
        self.assertEqual(result, {'FINISHED'})
        self.assertIsNone(workflow.transition_timing(self.obj, 11))
        first = next(anchor for anchor in self.obj.b4ml.anchors
                     if abs(anchor.frame-11) < 1e-5)
        self.assertNotIn('incoming_timing', json.loads(first.payload))
        workflow.preview(self.obj, self.scene, "LINEAR")
        self.scene.frame_set(15)
        self.assertAlmostEqual(self.bone.location.x, 14.0, places=5)
        workflow.finish_preview(self.obj, self.scene, keep=False)

    def test_earlier_capture_and_reuse_clear_persisted_dormant_window(self):
        self._capture(11, 10.0)
        self._capture(21, 20.0)
        first = next(anchor for anchor in self.obj.b4ml.anchors
                     if abs(anchor.frame-11) < 1e-5)
        payload = json.loads(first.payload)
        payload['incoming_timing'] = {
            'easing': 'EASE_IN', 'bias': .2,
            'departure_hold': .3, 'arrival_hold': .2,
        }
        first.payload = json.dumps(payload)
        rows = workflow._read_anchor_rows(self.obj, 1)
        self.assertIsNotNone(workflow._earlier_insert_normalization(
            self.obj.b4ml.anchors, rows, rows[0][0] - 1e-5))
        self._capture(1, 0.0)
        self.assertIsNone(workflow.transition_timing(self.obj, 11))
        first = next(anchor for anchor in self.obj.b4ml.anchors
                     if abs(anchor.frame-1) < 1e-5)
        payload = json.loads(first.payload)
        payload['incoming_timing'] = {
            'easing': 'EASE_OUT', 'bias': -.2,
            'departure_hold': .1, 'arrival_hold': .4,
        }
        first.payload = json.dumps(payload)
        rows = workflow._read_anchor_rows(self.obj, 1)
        self.assertIsNotNone(workflow._earlier_insert_normalization(
            self.obj.b4ml.anchors, rows, rows[0][0] - 1e-5))
        self.scene.frame_set(-9)
        workflow.reuse_anchor(self.obj, self.scene, 21)
        self.assertIsNone(workflow.transition_timing(self.obj, 1))
        workflow.preview(self.obj, self.scene, "LINEAR")
        self.scene.frame_set(-5)
        self.assertAlmostEqual(self.bone.location.x, 12.0, places=5)
        workflow.finish_preview(self.obj, self.scene, keep=False)
        self._capture(1, 0.0)
        self.assertIsNone(workflow.transition_timing(self.obj, 11))
        workflow.preview(self.obj, self.scene, "LINEAR")
        self.scene.frame_set(5)
        self.assertAlmostEqual(self.bone.location.x, 4.0, places=5)
        workflow.finish_preview(self.obj, self.scene, keep=False)

    def test_operator_and_save_reload_preserve_window(self):
        self._capture(1, 0.0)
        self._capture(11, 10.0)
        source_before = self._source_digest()
        boundary = bpy.ops.b4ml.transition_timing(
            'EXEC_DEFAULT', frame=11, use_override=True,
            easing="LINEAR", bias=0.0,
            departure_hold=.6, arrival_hold=.3)
        self.assertEqual(boundary, {"FINISHED"})
        boundary_timing = workflow.transition_timing(self.obj, 11)
        self.assertLessEqual(boundary_timing["departure_hold"] +
                             boundary_timing["arrival_hold"], .900001)
        result = bpy.ops.b4ml.transition_timing(
            'EXEC_DEFAULT', frame=11, use_override=True,
            easing="EASE_OUT", bias=-.25,
            departure_hold=.2, arrival_hold=.3)
        self.assertEqual(result, {"FINISHED"})
        timing = workflow.transition_timing(self.obj, 11)
        self.assertAlmostEqual(timing["departure_hold"], .2, places=6)
        self.assertAlmostEqual(timing["arrival_hold"], .3, places=6)
        self.assertEqual(self._source_digest(), source_before)
        name = self.obj.name
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / "transition-window-v1.blend")
            bpy.ops.wm.save_as_mainfile(filepath=path)
            bpy.ops.wm.open_mainfile(filepath=path, load_ui=False, use_scripts=False)
            self.obj = bpy.data.objects[name]
            self.bone = self.obj.pose.bones["hips"]
            self.scene = bpy.context.scene
            bpy.context.view_layer.objects.active = self.obj
            self.obj.select_set(True)
            timing = workflow.transition_timing(self.obj, 11)
            self.assertAlmostEqual(timing["departure_hold"], .2, places=6)
            self.assertAlmostEqual(timing["arrival_hold"], .3, places=6)
            self.assertEqual(self._source_digest(), source_before)


if __name__ == "__main__":
    result = unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(TransitionWindowTests))
    if not result.wasSuccessful():
        raise SystemExit(1)
