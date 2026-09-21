"""Real Bforartists tests for reversible generated-Rigify quadruped posing."""
from pathlib import Path
import hashlib
import importlib
import json
import os
import sys
import time
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, os.environ.get("B4ML_PACKAGE", str(ROOT)))

import addon_utils
import bpy
from mathutils import Euler, Quaternion, Vector

import b4artists_ml
from b4artists_ml import quadruped_pose as qpose
from b4artists_ml import workflow


RECORDS = []


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _generate(profile, normalize_rotation_modes=True):
    scene = bpy.data.scenes.new("B4ML Quadruped Pose " + profile)
    bpy.context.window.scene = scene
    module = importlib.import_module("rigify.metarigs.Animals." + profile)
    data = bpy.data.armatures.new(profile + " pose metarig")
    meta = bpy.data.objects.new(profile + " pose metarig", data)
    scene.collection.objects.link(meta)
    bpy.context.view_layer.objects.active = meta
    meta.select_set(True)
    module.create(meta)
    if meta.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.pose.rigify_generate()
    obj = bpy.context.object
    obj.location = (0.31, -0.19, 0.42)
    obj.rotation_euler = Euler((0.08, -0.11, 0.17))
    obj.scale = (1.12, 1.12, 1.12)
    if normalize_rotation_modes:
        for bone in obj.pose.bones:
            bone.rotation_mode = "QUATERNION"
    bpy.context.view_layer.update()
    return scene, obj


def _action_signature(obj, action):
    slot = obj.animation_data.action_slot if obj.animation_data and hasattr(obj.animation_data, "action_slot") else None
    return [(curve.data_path, curve.array_index,
             [(tuple(key.co), key.interpolation) for key in curve.keyframe_points])
            for curve in workflow.action_curves(action, slot)]


class QuadrupedPoseRuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not b4artists_ml.is_bforartists():
            raise unittest.SkipTest("Bforartists required")
        addon_utils.enable("rigify", default_set=True, persistent=False)
        b4artists_ml.register()

    def _source(self, obj, scene):
        scene.frame_set(7)
        root = obj.pose.bones["root"]
        root.location = (0.013, -0.007, 0.004)
        root.keyframe_insert("location", frame=7)
        action = obj.animation_data.action
        return workflow.raw_pose(obj), action, _action_signature(obj, action)

    def _move_targets(self, obj, amount=1.0):
        deltas = {
            "Body": Vector((0.018, -0.009, 0.014)),
            "Fore Paw L": Vector((0.011, 0.004, 0.007)),
            "Fore Paw R": Vector((-0.008, 0.003, 0.006)),
            "Hind Paw L": Vector((0.006, -0.004, 0.005)),
            "Hind Paw R": Vector((-0.007, -0.003, 0.004)),
        }
        for label, delta in deltas.items():
            item = obj.b4ml.quadruped_targets[label]
            item.target.location += delta * amount
            item.use_orientation = True
            item.target.rotation_mode = "QUATERNION"
            axis = Vector((0.3, 0.7, 0.2)).normalized()
            item.target.rotation_quaternion = (
                Quaternion(axis, 0.035 * amount) @ item.target.rotation_quaternion)
        bpy.context.view_layer.update()

    def test_generated_cat_horse_wolf_solve_keep_and_restore(self):
        for name in ("cat", "horse", "wolf"):
            with self.subTest(profile=name):
                started = time.perf_counter()
                scene, obj = _generate(name)
                source, action, action_signature = self._source(obj, scene)
                _, _, limbs = qpose.binding(obj)
                modes = qpose.mode_values(obj, limbs)
                objects = set(bpy.data.objects)
                self.assertEqual(qpose.begin(obj, scene), 6)
                self.assertEqual(len(obj.b4ml.quadruped_targets), 6)
                self._move_targets(obj)
                metrics = qpose.solve(obj, scene)
                self.assertLessEqual(metrics["max_paw_error"], metrics["tolerance"])
                self.assertLessEqual(metrics["body_error"], metrics["tolerance"])
                self.assertLessEqual(metrics["max_orientation_error"],
                                     metrics["orientation_tolerance"])
                self.assertEqual(set(metrics["orientation_errors"]),
                                 {"Body", "Fore Paw L", "Fore Paw R", "Hind Paw L", "Hind Paw R", "Head"})
                self.assertLessEqual(metrics["passes"], 8)
                self.assertNotEqual(workflow.raw_pose(obj), source)
                qpose.finish(obj, scene, True)
                self.assertEqual(len(obj.b4ml.anchors), 1)
                self.assertEqual(workflow.raw_pose(obj), source)
                self.assertEqual(qpose.mode_values(obj, limbs), modes)
                self.assertIs(obj.animation_data.action, action)
                self.assertEqual(_action_signature(obj, action), action_signature)
                self.assertFalse(obj.b4ml.quadruped_payload)
                self.assertEqual(set(bpy.data.objects), objects)
                RECORDS.append({"profile": name, "metrics": metrics,
                                "source_restored": True, "anchor_saved": True,
                                "seconds": time.perf_counter() - started})

    def test_cancel_and_changed_target_keep_guard(self):
        scene, obj = _generate("cat")
        source, action, action_signature = self._source(obj, scene)
        qpose.begin(obj, scene)
        self._move_targets(obj)
        qpose.solve(obj, scene)
        obj.b4ml.quadruped_targets["Fore Paw L"].target.location.x += 0.01
        bpy.context.view_layer.update()
        with self.assertRaisesRegex(ValueError, "Solve the current quadruped targets"):
            qpose.finish(obj, scene, True)
        qpose.finish(obj, scene, False)
        self.assertEqual(workflow.raw_pose(obj), source)
        self.assertIs(obj.animation_data.action, action)
        self.assertEqual(_action_signature(obj, action), action_signature)

    def test_non_ik_and_metarig_fail_before_mutation(self):
        scene, obj = _generate("wolf")
        source, _, _ = self._source(obj, scene)
        _, _, limbs = qpose.binding(obj)
        obj.pose.bones[limbs[0]["property_bone"]]["IK_FK"] = 1.0
        bpy.context.view_layer.update()
        objects = set(bpy.data.objects)
        with self.assertRaisesRegex(ValueError, "Switch all generated quadruped limbs to IK"):
            qpose.begin(obj, scene)
        self.assertEqual(set(bpy.data.objects), objects)
        self.assertEqual(workflow.raw_pose(obj), source)
        self.assertFalse(obj.b4ml.quadruped_payload)

        obj.pose.bones[limbs[0]["property_bone"]]["IK_FK"] = 0.0
        obj.pose.bones["torso"].lock_location[0] = True
        bpy.context.view_layer.update()
        with self.assertRaisesRegex(ValueError, "requires unlocked XYZ location"):
            qpose.begin(obj, scene)
        self.assertEqual(set(bpy.data.objects), objects)
        self.assertFalse(obj.b4ml.quadruped_payload)
        obj.pose.bones["torso"].lock_location[0] = False

        qpose.begin(obj, scene)
        obj.b4ml.quadruped_targets["Body"].use_orientation = True
        obj.pose.bones["torso"].lock_rotation[0] = True
        with self.assertRaisesRegex(ValueError, "requires unlocked rotation"):
            qpose.solve(obj, scene)
        obj.pose.bones["torso"].lock_rotation[0] = False
        qpose.finish(obj, scene, False)

        module = importlib.import_module("rigify.metarigs.Animals.cat")
        data = bpy.data.armatures.new("cat direct metarig")
        meta = bpy.data.objects.new("cat direct metarig", data)
        scene.collection.objects.link(meta)
        bpy.context.view_layer.objects.active = meta
        module.create(meta)
        if meta.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
        with self.assertRaisesRegex(ValueError, "currently supports generated Rigify"):
            qpose.begin(meta, scene)
        self.assertFalse(meta.b4ml.quadruped_payload)

    def test_solved_preview_survives_save_reload_and_keeps(self):
        scene, obj = _generate("horse")
        source, action, action_signature = self._source(obj, scene)
        action_name = action.name
        qpose.begin(obj, scene)
        self._move_targets(obj, 0.5)
        qpose.solve(obj, scene)
        name = obj.name
        path = ROOT / "training/b4artists_ml/cache/quadruped-pose-reload.blend"
        path.parent.mkdir(parents=True, exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=str(path))
        bpy.ops.wm.open_mainfile(filepath=str(path))
        obj = bpy.data.objects[name]
        scene = bpy.context.scene
        bpy.context.view_layer.objects.active = obj
        self.assertTrue(obj.b4ml.quadruped_payload)
        qpose.finish(obj, scene, True)
        self.assertEqual(len(obj.b4ml.anchors), 1)
        self.assertEqual(workflow.raw_pose(obj), source)
        self.assertEqual(obj.animation_data.action.name, action_name)
        self.assertEqual(_action_signature(obj, obj.animation_data.action), action_signature)


def _run():
    started = time.time()
    selection = os.environ.get("B4ML_QUADRUPED_POSE_TEST")
    suite = (unittest.defaultTestLoader.loadTestsFromName(selection, sys.modules[__name__])
             if selection else unittest.defaultTestLoader.loadTestsFromTestCase(QuadrupedPoseRuntimeTests))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    output = Path(os.environ.get(
        "B4ML_QUADRUPED_POSE_REPORT",
        str(ROOT / "training/b4artists_ml/results/quadruped-pose-v1.json"),
    ))
    report = {
        "complete": result.wasSuccessful(),
        "full_goal_complete": False,
        "qualification": "Deterministic generated-Rigify quadruped body and four-paw pose preview",
        "host": bpy.app.version_string,
        "package_root": str(Path(b4artists_ml.__file__).resolve().parent),
        "runtime_sha256": {"quadruped_pose": _sha(qpose.__file__),
                           "rigs": _sha(Path(qpose.__file__).with_name("rigs.py")),
                           "workflow": _sha(workflow.__file__)},
        "tests_run": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "records": RECORDS,
        "human_reviews": 0,
        "cascadeur_comparisons": 0,
        "outbound_calls": 0,
        "limits": "Generated Rigify cat, horse, and wolf in existing IK mode. Learned quadruped motion, gait physics, contact correction, imported rigs, and human review remain open.",
        "recorded_at": started,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if not result.wasSuccessful():
        raise SystemExit(1)


if __name__ == "__main__":
    _run()
