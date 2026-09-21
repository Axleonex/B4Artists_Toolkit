"""Bforartists tests for deterministic interpolation timing controls."""
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
from b4artists_ml import math_core, quadruped_gait, ui, workflow


class TimingControlTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not b4artists_ml.is_bforartists():
            raise unittest.SkipTest("Bforartists required")
        b4artists_ml.register()

    def setUp(self):
        if bpy.context.object and bpy.context.object.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
        data = bpy.data.armatures.new("Timing Control Rig")
        self.obj = bpy.data.objects.new("Timing Control Rig", data)
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
        self.obj.b4ml.selected_only = False
        self.scene = bpy.context.scene
        self.scene.frame_set(1)

    def tearDown(self):
        if bpy.context.object and bpy.context.object.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
        obj = bpy.data.objects.get("Timing Control Rig")
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

    def _source_signature(self):
        action = self.obj.animation_data.action
        return quadruped_gait._action_digest(self.obj, action)

    def test_weights_are_bounded_monotonic_and_preserve_endpoints(self):
        for easing in ("LINEAR", "SMOOTH", "EASE_IN", "EASE_OUT"):
            for bias in (-1.0, -0.35, 0.0, 0.4, 1.0):
                values = [math_core.timing_weight(index / 40, easing, bias)
                          for index in range(41)]
                self.assertEqual(values[0], 0.0)
                self.assertEqual(values[-1], 1.0)
                self.assertTrue(all(0.0 <= value <= 1.0 for value in values))
                self.assertTrue(all(left <= right for left, right in zip(values, values[1:])))
        self.assertAlmostEqual(math_core.timing_weight(.5, "LINEAR", -1), .1)
        self.assertAlmostEqual(math_core.timing_weight(.5, "LINEAR", 0), .5)
        self.assertAlmostEqual(math_core.timing_weight(.5, "LINEAR", 1), .9)

    def test_easing_shapes_and_invalid_values(self):
        self.assertAlmostEqual(math_core.timing_weight(.5, "SMOOTH", 0), .5)
        self.assertAlmostEqual(math_core.timing_weight(.5, "EASE_IN", 0), .25)
        self.assertAlmostEqual(math_core.timing_weight(.5, "EASE_OUT", 0), .75)
        for value in (-1.01, 1.01, float("nan"), True, "early"):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "Timing bias"):
                    math_core.timing_weight(.5, "LINEAR", value)
        with self.assertRaisesRegex(ValueError, "Unknown interpolation"):
            math_core.timing_weight(.5, "BOUNCE", 0)

    def test_runtime_bias_moves_breakdown_but_preserves_poses_and_source(self):
        self._capture(1, 0.0)
        self._capture(11, 10.0)
        source = self.obj.animation_data.action
        source_before = self._source_signature()
        self.scene.frame_set(6)
        workflow.preview(self.obj, self.scene, "LINEAR", timing_bias=1.0)
        candidate = self.obj.animation_data.action
        self.assertIsNot(candidate, source)
        self.assertAlmostEqual(self.bone.location.x, 9.0, places=5)
        self.assertEqual(candidate["b4ml_timing_easing"], "LINEAR")
        self.assertAlmostEqual(candidate["b4ml_timing_bias"], 1.0)
        for frame, expected in ((1, 0.0), (11, 10.0)):
            self.scene.frame_set(frame)
            self.assertAlmostEqual(self.bone.location.x, expected, places=6)
        workflow.finish_preview(self.obj, self.scene, keep=False)
        self.assertIs(self.obj.animation_data.action, source)
        self.assertEqual(self._source_signature(), source_before)

    def test_same_bias_applies_independently_to_multiple_pose_intervals(self):
        self._capture(1, 0.0)
        self._capture(11, 10.0)
        self._capture(21, 0.0)
        workflow.preview(self.obj, self.scene, "LINEAR", timing_bias=1.0)
        self.scene.frame_set(6)
        self.assertAlmostEqual(self.bone.location.x, 9.0, places=5)
        self.scene.frame_set(16)
        self.assertAlmostEqual(self.bone.location.x, 1.0, places=5)
        self.scene.frame_set(11)
        self.assertAlmostEqual(self.bone.location.x, 10.0, places=6)
        workflow.finish_preview(self.obj, self.scene, keep=False)

    def test_invalid_or_projected_bias_fails_before_candidate_mutation(self):
        self._capture(1, 0.0)
        self._capture(11, 10.0)
        source = self.obj.animation_data.action
        before = self._source_signature()
        with self.assertRaisesRegex(ValueError, "Timing bias"):
            workflow.preview(self.obj, self.scene, "LINEAR", timing_bias=float("nan"))
        with self.assertRaisesRegex(ValueError, "already define timing"):
            workflow.preview(self.obj, self.scene, "LINEAR", timing_bias=.25,
                             pose_samples={})
        self.assertIs(self.obj.animation_data.action, source)
        self.assertIsNone(self.obj.b4ml.candidate_action)
        self.assertEqual(self._source_signature(), before)

    def test_projected_candidate_clears_inherited_timing_metadata(self):
        self._capture(1, 0.0)
        self._capture(3, 2.0)
        source = self.obj.animation_data.action
        source["b4ml_timing_easing"] = "EASE_IN"
        source["b4ml_timing_bias"] = .75
        rows = workflow.read_anchors(self.obj)
        samples = {}
        for frame in (1.0, 2.0, 3.0):
            if frame == 1:
                samples[frame] = copy.deepcopy(rows[0][1]["pose"])
            elif frame == 3:
                samples[frame] = copy.deepcopy(rows[1][1]["pose"])
            else:
                samples[frame] = copy.deepcopy(rows[0][1]["pose"])
                samples[frame]["hips"]["location"] = (1.0, 0.0, 0.0)
        workflow.preview(self.obj, self.scene, pose_samples=samples)
        candidate = self.obj.animation_data.action
        self.assertEqual(candidate["b4ml_backend"], "projected_semantic_motion_v1")
        self.assertNotIn("b4ml_timing_easing", candidate)
        self.assertNotIn("b4ml_timing_bias", candidate)
        self.assertEqual(source["b4ml_timing_easing"], "EASE_IN")
        self.assertAlmostEqual(source["b4ml_timing_bias"], .75)
        workflow.finish_preview(self.obj, self.scene, keep=False)

    def test_operator_ui_and_save_reload_preserve_timing_choice(self):
        self._capture(1, 0.0)
        self._capture(11, 10.0)
        self.obj.b4ml.easing = "EASE_OUT"
        self.obj.b4ml.timing_bias = -.5
        name = self.obj.name
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / "timing-controls-v1.blend")
            bpy.ops.wm.save_as_mainfile(filepath=path)
            bpy.ops.wm.open_mainfile(filepath=path, load_ui=False, use_scripts=False)
            self.obj = bpy.data.objects[name]
            self.bone = self.obj.pose.bones["hips"]
            self.scene = bpy.context.scene
            bpy.context.view_layer.objects.active = self.obj
            self.obj.select_set(True)
            self.assertEqual(self.obj.b4ml.easing, "EASE_OUT")
            self.assertAlmostEqual(self.obj.b4ml.timing_bias, -.5)
            self.scene.frame_set(6)
            self.assertEqual(bpy.ops.b4ml.action(operation="PREVIEW"), {"FINISHED"})
            expected = 10.0 * math_core.timing_weight(.5, "EASE_OUT", -.5)
            self.assertAlmostEqual(self.bone.location.x, expected, places=5)
            candidate = self.obj.animation_data.action
            self.assertEqual(candidate["b4ml_timing_easing"], "EASE_OUT")
            self.assertAlmostEqual(candidate["b4ml_timing_bias"], -.5)
            self.assertEqual(bpy.ops.b4ml.action(operation="DISCARD"), {"FINISHED"})
        enum = ui.B4ML_PG_settings.bl_rna.properties["easing"].enum_items
        self.assertEqual({item.identifier for item in enum},
                         {"LINEAR", "SMOOTH", "EASE_IN", "EASE_OUT"})


if __name__ == "__main__":
    result = unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(TimingControlTests))
    if not result.wasSuccessful():
        raise SystemExit(1)
