"""Actual Rigify quadruped adapter tests for Bforartists.

The generated rigs are disposable fixtures built by the bundled Rigify add-on.
This milestone qualifies generic capture/interpolation and explicit fail-closed
behavior. It does not qualify quadruped whole-body, contact, flight or ML solves.
"""
from pathlib import Path
import hashlib
import importlib
import json
import os
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, os.environ.get("B4ML_PACKAGE", str(ROOT)))

import addon_utils
import bpy
from mathutils import Quaternion

import b4artists_ml
from b4artists_ml import body_preview, contacts, posing, rigs, workflow


RECORDS = []
EXPECTED = {
    "cat": "Rigify Generated Quadruped (Cat)",
    "horse": "Rigify Generated Quadruped (Horse)",
    "wolf": "Rigify Generated Quadruped (Wolf)",
}


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _generate(profile):
    scene = bpy.data.scenes.new("B4ML Quadruped " + profile)
    bpy.context.window.scene = scene
    module = importlib.import_module("rigify.metarigs.Animals." + profile)
    data = bpy.data.armatures.new(profile + " metarig")
    meta = bpy.data.objects.new(profile + " metarig", data)
    scene.collection.objects.link(meta)
    bpy.context.view_layer.objects.active = meta
    meta.select_set(True)
    module.create(meta)
    if meta.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.pose.rigify_generate()
    obj = bpy.context.object
    for bone in obj.pose.bones:
        bone.rotation_mode = "QUATERNION"
    return scene, obj


def _action_signature(obj, action):
    slot = obj.animation_data.action_slot if obj.animation_data and hasattr(obj.animation_data, "action_slot") else None
    return [(curve.data_path, curve.array_index,
             [(tuple(key.co), key.interpolation) for key in curve.keyframe_points])
            for curve in workflow.action_curves(action, slot)]


class QuadrupedRuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not b4artists_ml.is_bforartists():
            raise unittest.SkipTest("Bforartists required")
        # Bforartists' Rigify preferences must exist while register() builds
        # its dynamic parameter class; a transient enable leaves it partial.
        addon_utils.enable("rigify", default_set=True, persistent=False)
        b4artists_ml.register()

    def test_generated_rigs_capture_interpolate_and_reject_humanoid_solvers(self):
        for index, name in enumerate(EXPECTED):
            with self.subTest(profile=name):
                started = time.perf_counter()
                scene, obj = _generate(name)
                profile = rigs.detect_rig(obj.data.bones.keys())
                self.assertEqual(profile.name, EXPECTED[name])
                self.assertEqual(profile.family, "quadruped")
                self.assertEqual(profile.schema, "quadruped_v1")
                self.assertFalse(profile.missing)
                self.assertTrue(profile.controls)
                forbidden = [control for control in profile.controls
                             if control.startswith(("DEF-", "MCH-", "ORG-", "VIS_"))
                             or "tweak" in control]
                self.assertFalse(forbidden)

                root = obj.pose.bones["root"]
                fore = obj.pose.bones[profile.roles["fore.upper-L"]]
                scene.frame_set(1)
                root.location = (0.0, 0.0, 0.0)
                fore.rotation_quaternion = Quaternion((0, 1, 0), 0.0)
                root.keyframe_insert("location", frame=1)
                fore.keyframe_insert("rotation_quaternion", frame=1)
                workflow.capture_anchor(obj, scene)
                first = workflow.raw_pose(obj, profile.controls)

                scene.frame_set(9)
                root.location = (0.24 + index * 0.03, -0.02 * index, 0.01 * index)
                fore.rotation_quaternion = Quaternion((0, 1, 0), 0.18 + index * 0.02)
                root.keyframe_insert("location", frame=9)
                fore.keyframe_insert("rotation_quaternion", frame=9)
                workflow.capture_anchor(obj, scene)
                last = workflow.raw_pose(obj, profile.controls)
                source = obj.animation_data.action
                source_signature = _action_signature(obj, source)

                frame_count, _ = workflow.preview(obj, scene, "SMOOTH")
                candidate = obj.animation_data.action
                self.assertEqual(frame_count, 9)
                self.assertIsNot(candidate, source)
                candidate_paths = [curve.data_path for curve in workflow.action_curves(
                    candidate, obj.animation_data.action_slot)]
                self.assertFalse([path for path in candidate_paths
                                  if any(token in path for token in ("DEF-", "MCH-", "ORG-", "VIS_", "tweak"))])
                scene.frame_set(1)
                self.assertEqual(first, workflow.raw_pose(obj, profile.controls))
                scene.frame_set(9)
                self.assertEqual(last, workflow.raw_pose(obj, profile.controls))
                self.assertEqual(source_signature, _action_signature(obj, source))
                workflow.finish_preview(obj, scene, keep=False)
                self.assertIs(obj.animation_data.action, source)
                self.assertEqual(source_signature, _action_signature(obj, source))

                before_objects = set(bpy.data.objects)
                before_pose = workflow.raw_pose(obj, profile.controls)
                with self.assertRaisesRegex(ValueError, "supports humanoids"):
                    posing.begin(obj, scene)
                with self.assertRaisesRegex(ValueError, "supports humanoids"):
                    body_preview.begin(obj, scene)
                self.assertEqual(before_objects, set(bpy.data.objects))
                self.assertEqual(before_pose, workflow.raw_pose(obj, profile.controls))
                self.assertFalse(obj.b4ml.posing_payload)
                self.assertFalse(obj.b4ml.body_payload)

                workflow.preview(obj, scene, "SMOOTH")
                scene.frame_set(4)
                with self.assertRaisesRegex(ValueError, "supports humanoids"):
                    contacts.capture(obj, scene)
                self.assertFalse(obj.b4ml.contacts)
                workflow.finish_preview(obj, scene, keep=False)

                RECORDS.append({
                    "profile": name,
                    "detected": profile.name,
                    "family": profile.family,
                    "schema": profile.schema,
                    "controls": len(profile.controls),
                    "missing": list(profile.missing),
                    "frames": frame_count,
                    "candidate_curves": len(candidate_paths),
                    "source_preserved": True,
                    "humanoid_solvers_fail_closed": True,
                    "seconds": time.perf_counter() - started,
                })


def _run():
    started = time.time()
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(QuadrupedRuntimeTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    output = Path(os.environ.get(
        "B4ML_QUADRUPED_REPORT",
        str(ROOT / "training/b4artists_ml/results/quadruped-adapter-v1.json"),
    ))
    report = {
        "complete": result.wasSuccessful(),
        "full_goal_complete": False,
        "qualification": "Rigify quadruped adapter: capture/interpolation and fail-closed humanoid solvers",
        "host": bpy.app.version_string,
        "package_root": str(Path(b4artists_ml.__file__).resolve().parent),
        "runtime_sha256": {name: _sha(module.__file__) for name, module in {
            "rigs": rigs, "workflow": workflow, "posing": posing,
            "body_preview": body_preview, "contacts": contacts,
        }.items()},
        "tests_run": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "records": RECORDS,
        "human_reviews": 0,
        "cascadeur_comparisons": 0,
        "outbound_calls": 0,
        "limits": ("Generated Rigify cat, horse and wolf only. Generic capture and interpolation are qualified; "
                   "quadruped whole-body, contact, flight, learned motion, imported rigs and human review remain open."),
        "recorded_at": started,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if not result.wasSuccessful():
        raise SystemExit(1)


if __name__ == "__main__":
    _run()
