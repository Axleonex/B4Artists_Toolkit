"""Real Bforartists tests for generated-Rigify four-paw contact correction."""
from pathlib import Path
import hashlib
import json
import os
import sys
import time
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [os.environ.get("B4ML_PACKAGE", str(ROOT)), str(ROOT / "tests")]

import addon_utils
import bpy
from mathutils import Vector

import b4artists_ml
from b4artists_ml import quadruped_contacts as qc
from b4artists_ml import quadruped_pose as qp
from b4artists_ml import workflow as w
from test_b4artists_ml_quadruped_pose import _generate


RECORDS = []


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _signature(obj, action):
    slot = obj.animation_data.action_slot if obj.animation_data and hasattr(obj.animation_data, "action_slot") else None
    return [(curve.data_path, curve.array_index,
             [(tuple(key.co), key.interpolation) for key in curve.keyframe_points])
            for curve in w.action_curves(action, slot)]


def _candidate(profile):
    scene, obj = _generate(profile)
    root = obj.pose.bones["root"]
    for frame in (1, 11):
        scene.frame_set(frame)
        root.location = (0.0, 0.0, 0.0)
        root.keyframe_insert("location", frame=frame)
        w.capture_anchor(obj, scene)
    source = obj.animation_data.action
    source_signature = _signature(obj, source)
    w.preview(obj, scene, "LINEAR")
    candidate = obj.animation_data.action
    _, _, limbs = qp.binding(obj)
    mapping = {row["id"]: row for row in limbs}
    scene.frame_set(1)
    obj.b4ml.contacts.clear()
    for limb in qc.LIMBS:
        obj.b4ml.quadruped_contact_limb = limb
        item = qc.capture(obj, scene)
        item.start = 1.0
        item.end = 11.0
        item.blend = 0.0
        item.strength = 1.0
        item.lock_rotation = True
    scene.frame_set(6)
    deltas = {
        "fore-L": Vector((0.035, 0.000, 0.008)),
        "fore-R": Vector((-0.030, 0.004, 0.006)),
        "hind-L": Vector((0.025, -0.004, 0.007)),
        "hind-R": Vector((-0.028, 0.000, 0.005)),
    }
    for limb, delta in deltas.items():
        control = obj.pose.bones[mapping[limb]["ik"]]
        control.location += delta
        control.keyframe_insert("location", frame=6)
    bpy.context.view_layer.update()
    return scene, obj, source, source_signature, candidate, _signature(obj, candidate), mapping


class QuadrupedContactRuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not b4artists_ml.is_bforartists():
            raise unittest.SkipTest("Bforartists required")
        addon_utils.enable("rigify", default_set=True, persistent=False)
        b4artists_ml.register()

    def test_cat_horse_wolf_four_paw_correction_and_source_recovery(self):
        for profile in ("cat", "horse", "wolf"):
            with self.subTest(profile=profile):
                started = time.perf_counter()
                scene, obj, source, source_signature, candidate, candidate_signature, _ = _candidate(profile)
                report = qc.solve(obj, scene)
                result = obj.animation_data.action
                self.assertIsNot(result, candidate)
                self.assertEqual(report["contacts"], 4)
                self.assertGreater(report["contact_drift_before"], 1e-3)
                self.assertLessEqual(report["max_after"], 2e-4)
                self.assertLessEqual(report["contact_drift_after"], 2e-4)
                self.assertLessEqual(report["orientation_error_radians"], 1e-3)
                self.assertFalse(report["learned"])
                self.assertFalse(report["gait_inference"])
                self.assertEqual(_signature(obj, candidate), candidate_signature)
                self.assertEqual(_signature(obj, source), source_signature)
                qc.restore_before_contacts(obj, scene)
                self.assertIs(obj.animation_data.action, candidate)
                self.assertEqual(_signature(obj, candidate), candidate_signature)
                w.finish_preview(obj, scene, keep=False)
                self.assertIs(obj.animation_data.action, source)
                self.assertEqual(_signature(obj, source), source_signature)
                RECORDS.append(dict(profile=profile, report=report,
                                    input_preserved=True, source_restored=True,
                                    seconds=time.perf_counter() - started))

    def test_cancel_priority_conflict_and_rotation_lock_fail_without_mutation(self):
        scene, obj, _, _, candidate, candidate_signature, mapping = _candidate("cat")
        qc.start(obj, scene)
        self.assertFalse(qc.step(obj))
        qc.abort(obj)
        self.assertFalse(obj.b4ml.contact_running)
        self.assertIs(obj.animation_data.action, candidate)
        self.assertEqual(_signature(obj, candidate), candidate_signature)

        obj.b4ml.contacts[0].point.x += 0.1
        with self.assertRaisesRegex(ValueError, "conflicts with priority pose"):
            qc.solve(obj, scene)
        self.assertIs(obj.animation_data.action, candidate)
        self.assertEqual(_signature(obj, candidate), candidate_signature)
        obj.b4ml.contacts[0].point.x -= 0.1

        control = obj.pose.bones[mapping["fore-L"]["ik"]]
        control.lock_rotation[0] = True
        with self.assertRaisesRegex(ValueError, "require unlocked rotation"):
            qc.solve(obj, scene)
        control.lock_rotation[0] = False
        self.assertIs(obj.animation_data.action, candidate)
        self.assertEqual(_signature(obj, candidate), candidate_signature)
        w.finish_preview(obj, scene, keep=False)

    def test_corrected_candidate_keep_save_reload_and_restore_source(self):
        scene, obj, source, source_signature, _, _, _ = _candidate("horse")
        source_name = source.name
        qc.solve(obj, scene)
        w.finish_preview(obj, scene, keep=True)
        kept_name = obj.animation_data.action.name
        object_name = obj.name
        path = ROOT / "training/b4artists_ml/cache/quadruped-contacts-reload.blend"
        path.parent.mkdir(parents=True, exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=str(path))
        bpy.ops.wm.open_mainfile(filepath=str(path), use_scripts=False)
        obj = bpy.data.objects[object_name]
        scene = bpy.context.scene
        bpy.context.view_layer.objects.active = obj
        self.assertEqual(obj.animation_data.action.name, kept_name)
        w.restore_kept_source(obj, scene)
        self.assertEqual(obj.animation_data.action.name, source_name)
        self.assertEqual(_signature(obj, obj.animation_data.action), source_signature)


def _run():
    started = time.time()
    selected = os.environ.get("B4ML_QUADRUPED_CONTACT_TEST", "").strip()
    suite = (unittest.defaultTestLoader.loadTestsFromName(
        f"{__name__}.QuadrupedContactRuntimeTests.{selected}") if selected else
        unittest.defaultTestLoader.loadTestsFromTestCase(QuadrupedContactRuntimeTests))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    output = Path(os.environ.get(
        "B4ML_QUADRUPED_CONTACT_REPORT",
        str(ROOT / "training/b4artists_ml/results/quadruped-contacts-v1.json")))
    report = {
        "complete": result.wasSuccessful(),
        "full_goal_complete": False,
        "qualification": "Animator-authored four-paw contact correction on generated Rigify quadrupeds",
        "host": bpy.app.version_string,
        "package_root": str(Path(b4artists_ml.__file__).resolve().parent),
        "runtime_sha256": {
            "quadruped_contacts": _sha(qc.__file__),
            "quadruped_pose": _sha(qp.__file__),
            "workflow": _sha(w.__file__)
        },
        "tests_run": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "records": RECORDS,
        "human_reviews": 0,
        "cascadeur_comparisons": 0,
        "outbound_calls": 0,
        "limits": ("Generated Rigify cat, horse and wolf with animator-authored intervals and existing IK. "
                   "Automatic contact inference, gait, balance, arbitrary surfaces, learned motion and human review remain open."),
        "recorded_at": started
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if not result.wasSuccessful():
        raise SystemExit(1)


if __name__ == "__main__":
    _run()
