"""Bforartists tests for procedural quadruped support-phase review."""
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

import b4artists_ml
from b4artists_ml import quadruped_contacts as qc
from b4artists_ml import quadruped_gait as gait
from b4artists_ml import contact_math as cm
from b4artists_ml import workflow as w
from test_b4artists_ml_quadruped_contacts import _candidate


RECORDS = []
PATTERN = (
    ("fore-L", 1.0, 5.0),
    ("hind-R", 1.0, 5.0),
    ("fore-R", 6.25, 11.0),
    ("hind-R", 6.25, 11.0),
    ("fore-L", 8.0, 11.0),
    ("hind-L", 8.0, 11.0),
)


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _install_pattern(obj):
    obj.b4ml.contacts.clear()
    for limb, start, end in PATTERN:
        item = obj.b4ml.contacts.add()
        item.name = f"Accepted {limb} {start:g}-{end:g}"
        item.enabled = True
        item.review_state = "ACCEPTED"
        item.limb = limb
        item.start = start
        item.end = end
        item.blend = 0.0
        item.strength = 1.0
        item.rotation = (1.0, 0.0, 0.0, 0.0)
        item.lock_rotation = False


def _weighted_support(obj, frame):
    return [limb for limb in qc.LIMBS
            if any(row["limb"] == limb and cm.weight(row, frame) > 0.0
                   for row in qc.rows(obj))]


class QuadrupedGaitPhaseRuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not b4artists_ml.is_bforartists():
            raise unittest.SkipTest("Bforartists required")
        addon_utils.enable("rigify", default_set=True, persistent=False)
        b4artists_ml.register()

    def test_every_support_set_has_a_conservative_label(self):
        cases = {
            (): "FLIGHT",
            ("fore-L",): "SINGLE_SUPPORT",
            ("fore-L", "hind-R"): "DIAGONAL_SUPPORT",
            ("fore-R", "hind-R"): "LATERAL_SUPPORT",
            ("fore-L", "fore-R"): "FORE_SUPPORT",
            ("hind-L", "hind-R"): "HIND_SUPPORT",
            ("fore-L", "fore-R", "hind-R"): "TRIPLE_SUPPORT",
            qc.LIMBS: "FULL_SUPPORT",
        }
        for support, expected in cases.items():
            with self.subTest(support=support):
                self.assertEqual(gait.classify(support), expected)
        with self.assertRaisesRegex(ValueError, "Unknown"):
            gait.classify(("tail",))

    def test_cat_horse_wolf_exact_support_phases_are_read_only(self):
        expected = [
            (1.0, 5.0, "DIAGONAL_SUPPORT", ["fore-L", "hind-R"]),
            (5.0, 6.25, "FLIGHT", []),
            (6.25, 8.0, "LATERAL_SUPPORT", ["fore-R", "hind-R"]),
            (8.0, 11.0, "FULL_SUPPORT", list(qc.LIMBS)),
        ]
        for profile in ("cat", "horse", "wolf"):
            with self.subTest(profile=profile):
                scene, obj, _, _, candidate, _, _ = _candidate(profile)
                _install_pattern(obj)
                scene.frame_set(1)
                action_before = qc._action_signature(obj, candidate)
                contacts_before = qc._signature(obj)
                anchors_before = [(item.frame, item.payload) for item in obj.b4ml.anchors]
                actions_before = {action.as_pointer() for action in bpy.data.actions}
                analyze_started = time.perf_counter()
                result = bpy.ops.b4ml.quadruped_gait(operation="ANALYZE")
                analyze_ms = (time.perf_counter() - analyze_started) * 1000.0
                self.assertEqual(result, {"FINISHED"})
                report = gait.report(obj)
                validation_ms = []
                for _ in range(8):
                    validation_started = time.perf_counter()
                    gait.display_report(obj)
                    validation_ms.append((time.perf_counter() - validation_started) * 1000.0)
                self.assertLess(max(validation_ms), 50.0)
                actual = [(row["start"], row["end"], row["phase"], row["support_limbs"])
                          for row in report["phases"]]
                self.assertEqual(actual, expected)
                self.assertTrue(report["procedural"])
                self.assertFalse(report["learned"])
                self.assertFalse(report["gait_inference"])
                self.assertFalse(report["gait_generation"])
                self.assertEqual(report["contact_count"], len(PATTERN))
                self.assertIs(obj.animation_data.action, candidate)
                self.assertIs(obj.b4ml.candidate_action, candidate)
                self.assertEqual(qc._action_signature(obj, candidate), action_before)
                self.assertEqual(qc._signature(obj), contacts_before)
                self.assertEqual([(item.frame, item.payload) for item in obj.b4ml.anchors], anchors_before)
                self.assertEqual({action.as_pointer() for action in bpy.data.actions}, actions_before)
                RECORDS.append({"profile": profile, "phases": actual,
                                "source_unchanged": True, "learned": False,
                                "analyze_ms": analyze_ms,
                                "report_validation_max_ms": max(validation_ms)})

    def test_fractional_navigation_wraps_and_changes_only_playhead_state(self):
        scene, obj, _, _, candidate, _, _ = _candidate("cat")
        _install_pattern(obj)
        scene.frame_set(1)
        action_before = qc._action_signature(obj, candidate)
        contacts_before = qc._signature(obj)
        gait.analyze(obj, scene)
        self.assertEqual(gait.current(obj)["phase"], "DIAGONAL_SUPPORT")
        self.assertEqual(bpy.ops.b4ml.quadruped_gait(operation="NEXT"), {"FINISHED"})
        self.assertAlmostEqual(scene.frame_current + scene.frame_subframe, 5.625)
        self.assertEqual(gait.current(obj)["phase"], "FLIGHT")
        self.assertEqual(_weighted_support(obj, 5.625), gait.current(obj)["support_limbs"])
        for step, expected_frame, expected_phase in ((1, 7.125, "LATERAL_SUPPORT"),
                                                     (1, 9.5, "FULL_SUPPORT"),
                                                     (1, 3.0, "DIAGONAL_SUPPORT"),
                                                     (-1, 9.5, "FULL_SUPPORT")):
            phase = gait.navigate(obj, scene, step)
            frame = scene.frame_current + scene.frame_subframe
            self.assertAlmostEqual(frame, expected_frame)
            self.assertEqual(phase["phase"], expected_phase)
            self.assertEqual(_weighted_support(obj, frame), phase["support_limbs"])
        self.assertIs(obj.animation_data.action, candidate)
        self.assertEqual(qc._action_signature(obj, candidate), action_before)
        self.assertEqual(qc._signature(obj), contacts_before)

    def test_stale_invalid_and_busy_inputs_fail_closed(self):
        scene, obj, _, _, candidate, _, _ = _candidate("wolf")
        _install_pattern(obj)
        action_slot = getattr(obj.animation_data, "action_slot", None)
        curve = next(iter(w.action_curves(candidate, action_slot)))
        strip = candidate.layers[0].strips[0]
        bag = strip.channelbag(action_slot)
        group = bag.groups.new("Gait Phase Source")
        curve.group = group
        envelope = curve.modifiers.new("ENVELOPE")
        envelope_point = envelope.control_points.add(3.0)
        gait.analyze(obj, scene)
        original_report = obj.b4ml.quadruped_gait_report
        action_before = qc._action_signature(obj, candidate)
        slot_before = w._slot(obj.animation_data)
        group.mute = True
        with self.assertRaisesRegex(ValueError, "stale"):
            gait.report(obj)
        group.mute = False
        envelope_point.min -= 0.25
        with self.assertRaisesRegex(ValueError, "stale"):
            gait.report(obj)
        envelope_point.min += 0.25
        self.assertEqual(gait.report(obj)["phase_count"], 4)
        original_lock = curve.lock
        curve.lock = not original_lock
        with self.assertRaisesRegex(ValueError, "stale"):
            gait.report(obj)
        curve.lock = original_lock
        self.assertEqual(gait.report(obj)["phase_count"], 4)
        original_extrapolation = curve.extrapolation
        curve.extrapolation = "LINEAR" if original_extrapolation != "LINEAR" else "CONSTANT"
        with self.assertRaisesRegex(ValueError, "stale"):
            gait.report(obj)
        curve.extrapolation = original_extrapolation
        modifier = curve.modifiers.new("NOISE")
        with self.assertRaisesRegex(ValueError, "stale"):
            gait.report(obj)
        curve.modifiers.remove(modifier)
        self.assertEqual(gait.report(obj)["phase_count"], 4)
        original_name = candidate.name
        candidate.name = original_name + " Original"
        replacement = candidate.copy()
        replacement.name = original_name
        w.assign_action(obj, replacement, slot_before)
        obj.b4ml.candidate_action = replacement
        with self.assertRaisesRegex(ValueError, "stale"):
            gait.report(obj)
        replacement.name = original_name + " Replacement"
        candidate.name = original_name
        w.assign_action(obj, candidate, slot_before)
        obj.b4ml.candidate_action = candidate
        self.assertEqual(gait.report(obj)["phase_count"], 4)
        obj.b4ml.contacts[0].end = 4.75
        with self.assertRaisesRegex(ValueError, "stale"):
            gait.report(obj)
        self.assertEqual(obj.b4ml.quadruped_gait_report, original_report)
        obj.b4ml.contacts[0].end = 5.0
        valid_report = json.loads(original_report)
        hostile = []
        for key, value in (("label", None), ("start", float("nan")),
                           ("support_limbs", ["tail"]), ("support_limbs", [[]]),
                           ("index", 9)):
            row = json.loads(original_report)
            row["phases"][0][key] = value
            hostile.append(row)
        coherent_false = json.loads(original_report)
        coherent_false["phases"][0].update(
            support_limbs=[], support_count=0, phase="FLIGHT", label="Flight")
        hostile.append(coherent_false)
        wrong_count = json.loads(original_report)
        wrong_count["contact_count"] = 1
        hostile.append(wrong_count)
        for row in hostile:
            obj.b4ml.quadruped_gait_report = json.dumps(row)
            with self.assertRaisesRegex(ValueError, "Invalid gait-phase report|stale"):
                gait.report(obj)
        obj.b4ml.quadruped_gait_report = json.dumps(valid_report)
        obj.b4ml.contact_running = True
        with self.assertRaisesRegex(ValueError, "active animation"):
            gait.analyze(obj, scene)
        obj.b4ml.contact_running = False
        self.assertEqual(qc._action_signature(obj, candidate), action_before)
        obj.b4ml.quadruped_gait_report = "[]"
        with self.assertRaisesRegex(ValueError, "Invalid gait-phase report"):
            gait.report(obj)
        obj.b4ml.quadruped_gait_report = json.dumps({
            "schema": 1, "backend": gait.BACKEND, "phases": [{}]})
        with self.assertRaisesRegex(ValueError, "Invalid gait-phase report"):
            gait.navigate(obj, scene, 1)
        gait.clear(obj)
        self.assertEqual(obj.b4ml.quadruped_gait_report, "")
        obj.b4ml.contacts.clear()
        with self.assertRaisesRegex(ValueError, "at least one enabled contact"):
            gait.analyze(obj, scene)
        item = obj.b4ml.contacts.add()
        item.enabled = True
        item.review_state = "ACCEPTED"
        item.limb = "fore-L"
        item.start = item.end = 3.0
        item.strength = 1.0
        item.rotation = (1.0, 0.0, 0.0, 0.0)
        with self.assertRaisesRegex(ValueError, "positive-duration"):
            gait.analyze(obj, scene)

    def test_report_survives_save_reload_with_fractional_boundaries(self):
        scene, obj, _, _, _, _, _ = _candidate("horse")
        _install_pattern(obj)
        gait.analyze(obj, scene)
        expected = gait.report(obj)
        object_name = obj.name
        path = ROOT / "training/b4artists_ml/cache/quadruped-gait-phase-reload.blend"
        path.parent.mkdir(parents=True, exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=str(path))
        bpy.ops.wm.open_mainfile(filepath=str(path), use_scripts=False)
        obj = bpy.data.objects[object_name]
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        actual = gait.report(obj)
        self.assertEqual(actual, expected)
        self.assertEqual(actual["phases"][2]["start"], 6.25)


def _run():
    started = time.time()
    selected = os.environ.get("B4ML_GAIT_PHASE_TEST", "").strip()
    suite = (unittest.defaultTestLoader.loadTestsFromName(
        f"{__name__}.QuadrupedGaitPhaseRuntimeTests.{selected}") if selected else
        unittest.defaultTestLoader.loadTestsFromTestCase(QuadrupedGaitPhaseRuntimeTests))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    output = Path(os.environ.get(
        "B4ML_GAIT_PHASE_REPORT",
        str(ROOT / "training/b4artists_ml/results/quadruped-gait-phase-v1.json")))
    report = {
        "complete": result.wasSuccessful(),
        "full_goal_complete": False,
        "qualification": "Procedural support-phase review from animator-accepted quadruped contacts",
        "host": bpy.app.version_string,
        "package_root": str(Path(b4artists_ml.__file__).resolve().parent),
        "runtime_sha256": {
            "quadruped_gait": _sha(gait.__file__),
            "quadruped_contacts": _sha(qc.__file__),
            "workflow": _sha(w.__file__),
        },
        "tests_run": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "records": RECORDS,
        "human_reviews": 0,
        "cascadeur_comparisons": 0,
        "outbound_calls": 0,
        "limits": ("Generated Rigify cat, horse, and wolf; accepted contact intervals only. "
                   "No motion inference, gait naming, gait generation, learned model, or dynamics claim."),
        "recorded_at": started,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("B4ML_REPORT:", output)
    if not result.wasSuccessful():
        raise SystemExit(1)


if __name__ == "__main__":
    _run()
