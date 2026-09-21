"""Recall-active workflow coverage for persistent secondary control loads."""
from pathlib import Path
import json
import os
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [os.environ.get("B4ML_PACKAGE", str(ROOT)), str(ROOT / "tests")]

import bpy
import b4artists_ml
from b4artists_ml import flight, secondary_motion as secondary
from test_b4artists_ml_secondary_external_acceleration_v1 import FOREIGN_OWNERS, location_fixture
from test_b4artists_ml_secondary_force_offset_torque_v1 import enter_pose, torque_fixture


def visible_values(obj):
    state = obj.b4ml
    return (tuple(state.secondary_load_force), float(state.secondary_load_mass),
            tuple(state.secondary_load_offset), float(state.secondary_load_inertia))


def overwrite_visible(obj):
    state = obj.b4ml
    state.secondary_load_force = (-3.0, 2.0, 1.0)
    state.secondary_load_mass = 9.0
    state.secondary_load_offset = (0.0, 0.0, -0.75)
    state.secondary_load_inertia = 12.0


def activate(obj, name):
    obj.data.bones.active = obj.data.bones[name]


def recall_fixture(label, **kwargs):
    result = torque_fixture(label, **kwargs)
    activate(result[0], result[2])
    return result


class SecondaryLoadFromActiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b4artists_ml.register()

    def test_schema_two_assignment_recalls_every_visible_value(self):
        obj, _, control, _, _ = recall_fixture("boneforge")
        overwrite_visible(obj)
        report = secondary.load_active_control_load(obj)
        self.assertEqual(report, {
            "control": control, "force": [0.0, 4.0, 0.0], "mass": 2.0,
            "offset": [0.5, 0.0, 0.0], "rotational_inertia": 1.0})
        self.assertEqual(visible_values(obj),
                         ((0.0, 4.0, 0.0), 2.0, (0.5, 0.0, 0.0), 1.0))
        self.assertEqual(obj.b4ml.status,
                         "Loaded secondary assignment from " + control)

    def test_schema_one_assignment_recalls_compatibility_defaults(self):
        obj, _, control, _ = location_fixture("boneforge")
        enter_pose(obj)
        activate(obj, control)
        secondary.assign_control_loads(obj, (2.0, -1.0, 0.5), 4.0)
        self.assertEqual(json.loads(obj.b4ml.secondary_control_loads)["schema"], 1)
        overwrite_visible(obj)
        report = secondary.load_active_control_load(obj)
        self.assertEqual(report["control"], control)
        self.assertEqual(visible_values(obj),
                         ((2.0, -1.0, 0.5), 4.0, (0.0, 0.0, 0.0), 1.0))

    def test_recall_does_not_change_assignment_or_animation(self):
        obj, _, _, _, _ = recall_fixture("boneforge")
        state = obj.b4ml
        assignment = state.secondary_control_loads
        candidate = state.candidate_action
        token = flight._curve_token(obj, candidate)
        secondary.load_active_control_load(obj)
        self.assertEqual(state.secondary_control_loads, assignment)
        self.assertIs(state.candidate_action, candidate)
        self.assertIs(obj.animation_data.action, candidate)
        self.assertEqual(flight._curve_token(obj, candidate), token)

    def test_unassigned_active_control_fails_without_changing_fields(self):
        obj, _, control, _ = location_fixture("boneforge")
        enter_pose(obj)
        activate(obj, control)
        overwrite_visible(obj)
        before = visible_values(obj)
        with self.assertRaisesRegex(ValueError, "has no assigned load"):
            secondary.load_active_control_load(obj)
        self.assertEqual(visible_values(obj), before)

    def test_active_control_must_be_selected(self):
        obj, _, control, _, _ = recall_fixture("boneforge")
        bone = obj.pose.bones[control]
        if hasattr(bone, "select"):
            bone.select = False
        else:
            bone.bone.select = False
        before = visible_values(obj)
        with self.assertRaisesRegex(ValueError, "Select one active pose control"):
            secondary.load_active_control_load(obj)
        self.assertEqual(visible_values(obj), before)

    def test_recall_requires_pose_mode(self):
        obj, _, _, _, _ = recall_fixture("boneforge")
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode="OBJECT")
        before = visible_values(obj)
        with self.assertRaisesRegex(ValueError, "Pose Mode"):
            secondary.load_active_control_load(obj)
        self.assertEqual(visible_values(obj), before)

    def test_corrupt_record_fails_without_changing_fields(self):
        obj, _, _, _, _ = recall_fixture("boneforge")
        obj.b4ml.secondary_control_loads = "{"
        overwrite_visible(obj)
        before = visible_values(obj)
        with self.assertRaisesRegex(ValueError, "invalid"):
            secondary.load_active_control_load(obj)
        self.assertEqual(visible_values(obj), before)

    def test_recall_respects_every_workflow_owner(self):
        obj, _, _, _, _ = recall_fixture("boneforge")
        state = obj.b4ml
        overwrite_visible(obj)
        before = visible_values(obj)
        for field, value in FOREIGN_OWNERS:
            with self.subTest(owner=field):
                setattr(state, field, value)
                with self.assertRaisesRegex(ValueError, "Finish the active"):
                    secondary.load_active_control_load(obj)
                self.assertEqual(visible_values(obj), before)
                setattr(state, field, False if isinstance(value, bool) else "")


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        SecondaryLoadFromActiveTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print("B4ML_SECONDARY_LOAD_FROM_ACTIVE_RESULT:",
          "PASS" if result.wasSuccessful() else "FAIL")
