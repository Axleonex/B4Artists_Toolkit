"""Persistent per-control force/mass coverage for world secondary motion."""
from pathlib import Path
import json
import math
import os
import sys
import tempfile
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [os.environ.get("B4ML_PACKAGE", str(ROOT)), str(ROOT / "tests")]

import bpy
import b4artists_ml
from b4artists_ml import flight, secondary_math as sm, secondary_motion as secondary, workflow as w
from test_b4artists_ml_secondary_external_acceleration_v1 import FOREIGN_OWNERS, location_fixture
from test_b4artists_ml_secondary_motion import curve_values


def load_fixture(label, force=(6., -2., 1.), mass=2.):
    obj, source, selected_name, path = location_fixture(label)
    enter_pose(obj)
    state = obj.b4ml
    state.secondary_external_acceleration = (0., 0., 0.)
    state.secondary_wind_velocity = (0., 0., 0.)
    state.secondary_impulse_velocity = (0., 0., 0.)
    state.secondary_load_force = force
    state.secondary_load_mass = mass
    secondary.assign_control_loads(obj, force, mass)
    return obj, source, selected_name, path


def enter_pose(obj):
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    if obj.mode != "POSE":
        bpy.ops.object.mode_set(mode="POSE")


def set_selected(obj, names):
    names = set(names)
    for bone in obj.pose.bones:
        if hasattr(bone, "select"):
            bone.select = bone.name in names
        else:
            bone.bone.select = bone.name in names


def peer_location_controls(obj):
    state = obj.b4ml
    curves = w.action_curves(
        state.candidate_action, getattr(obj.animation_data, "action_slot", None))
    recognized = set(w.profile_for_object(obj).controls)
    candidates = []
    for bone in obj.pose.bones:
        path = bone.path_from_id("location")
        if (bone.name in recognized and not bone.constraints
                and all(curves.find(path, index=index) is not None for index in range(3))):
            candidates.append((bone, path))
    def ancestor(first, second):
        parent = second.parent
        while parent:
            if parent == first:
                return True
            parent = parent.parent
        return False
    for index, (first, first_path) in enumerate(candidates):
        for second, second_path in candidates[index + 1:]:
            if not ancestor(first, second) and not ancestor(second, first):
                return (first.name, first_path), (second.name, second_path)
    raise AssertionError("Fixture has no independent animated location controls")


class SecondaryControlLoadTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b4artists_ml.register()

    def test_math_force_over_mass_and_mass_scaling(self):
        np.testing.assert_array_equal(
            sm.control_load_acceleration((6., -2., 1.), 2.),
            np.array((3., -1., .5)))
        np.testing.assert_array_equal(
            sm.control_load_acceleration((6., -2., 1.), 4.),
            np.array((1.5, -.5, .25)))

    def test_math_load_validation_fails_closed(self):
        invalid = (
            ((1., 2.), 1.),
            ((float("nan"), 0., 0.), 1.),
            ((True, 0., 0.), 1.),
            ((1_000_001., 0., 0.), 1.),
            ((1., 0., 0.), True),
            ((1., 0., 0.), 0.),
            ((1., 0., 0.), 10_001.),
            ((101., 0., 0.), 1.),
        )
        for force, mass in invalid:
            with self.subTest(force=force, mass=mass):
                with self.assertRaises(ValueError):
                    sm.control_load_acceleration(force, mass)

    def test_assignment_record_is_deterministic_and_clear_is_exact(self):
        obj, _, selected_name, _ = location_fixture("boneforge")
        enter_pose(obj)
        report = secondary.assign_control_loads(obj, (4., -2., 1.), 2.)
        self.assertEqual(report["controls"], [selected_name])
        self.assertEqual(report["acceleration"], [2., -1., .5])
        stored = json.loads(obj.b4ml.secondary_control_loads)
        self.assertEqual(stored["schema"], 1)
        self.assertEqual(stored["loads"], [{"control": selected_name,
                                            "force": [4., -2., 1.], "mass": 2.}])
        self.assertEqual(secondary.control_load_count(obj), 1)
        cleared = secondary.clear_control_loads(obj)
        self.assertEqual(cleared["removed"], 1)
        self.assertEqual(obj.b4ml.secondary_control_loads, "")
        self.assertEqual(secondary.control_load_count(obj), 0)

    def test_corrupt_and_wrong_rig_records_fail_closed(self):
        obj, _, selected_name, _ = location_fixture("boneforge")
        valid = {"schema": 1, "bone_signature": "wrong", "loads": []}
        hostile = (
            "{",
            json.dumps(valid),
            json.dumps({"schema": 1,
                        "bone_signature": secondary.rig_mapping.bone_signature(obj),
                        "loads": [{"control": selected_name,
                                   "force": [101., 0., 0.], "mass": 1.}]}),
        )
        for text in hostile:
            with self.subTest(text=text[:20]):
                obj.b4ml.secondary_control_loads = text
                self.assertIsNone(secondary.control_load_count(obj))
                with self.assertRaises((ValueError, TypeError)):
                    secondary.request(obj, bpy.context.scene)
        recovered = secondary.clear_all_control_loads(obj)
        self.assertTrue(recovered["removed_all"])
        self.assertEqual(obj.b4ml.secondary_control_loads, "")

    def test_boneforge_and_rigify_load_workflow(self):
        for label in ("boneforge", "rigify_default"):
            with self.subTest(rig=label):
                obj, source, selected_name, path = load_fixture(label)
                state = obj.b4ml
                original = state.candidate_action
                token = flight._curve_token(obj, original)
                before = curve_values(original, obj, path)
                report = secondary.solve(obj, bpy.context.scene)
                after = curve_values(state.candidate_action, obj, path)
                self.assertEqual(report["schema"], 7)
                self.assertEqual(report["backend"],
                                 "implicit_selected_control_secondary_v6")
                self.assertEqual(report["controls"], [selected_name])
                self.assertEqual(report["loaded_controls"], 1)
                self.assertEqual(report["control_loads"], [{
                    "control": selected_name, "force": [6., -2., 1.],
                    "mass": 2., "acceleration": [3., -1., .5],
                    "acceleration_magnitude": math.sqrt(10.25)}])
                self.assertGreater(report["max_location_correction"], .001)
                self.assertLessEqual(report["max_world_location_error"], 2e-4)
                self.assertNotEqual(before, after)
                self.assertEqual(flight._curve_token(obj, original), token)
                secondary.restore(obj, bpy.context.scene)
                self.assertEqual(curve_values(original, obj, path), before)
                w.finish_preview(obj, bpy.context.scene, False)
                self.assertIs(obj.animation_data.action, source)

    def test_distinct_selected_controls_keep_distinct_loads(self):
        obj, _, _, _ = location_fixture("boneforge")
        enter_pose(obj)
        (first, _), (second, _) = peer_location_controls(obj)
        set_selected(obj, (first,))
        secondary.assign_control_loads(obj, (4., 0., 0.), 2.)
        set_selected(obj, (second,))
        secondary.assign_control_loads(obj, (0., 9., 0.), 3.)
        set_selected(obj, (first, second))
        report = secondary.solve(obj, bpy.context.scene)
        rows = {item["control"]: item for item in report["control_loads"]}
        self.assertEqual(rows[first]["acceleration"], [2., 0., 0.])
        self.assertEqual(rows[second]["acceleration"], [0., 3., 0.])
        self.assertEqual(report["loaded_controls"], 2)

    def test_valid_external_and_control_accelerations_compose(self):
        target = np.zeros((9, 3), dtype=float)
        steps = np.ones(8, dtype=float)
        combined, _ = sm.follow_world_vectors(
            target, steps, dt=1/24, frequency=.8, damping=.5,
            air_friction=.2, external_acceleration=(80., 0., 0.),
            control_acceleration=(30., 0., 0.))
        equivalent, _ = sm.follow_world_vectors(
            target, steps, dt=1/24, frequency=.8, damping=.5,
            air_friction=.2, gravity=(30., 0., 0.), gravity_scale=1.,
            external_acceleration=(80., 0., 0.))
        self.assertTrue(np.array_equal(combined, equivalent))

        obj, _, selected_name, path = load_fixture(
            "boneforge", force=(60., 0., 0.), mass=2.)
        obj.b4ml.secondary_external_acceleration = (80., 0., 0.)
        report = secondary.solve(obj, bpy.context.scene)
        loaded = curve_values(obj.b4ml.candidate_action, obj, path)
        self.assertEqual(report["external_acceleration"], [80., 0., 0.])
        self.assertEqual(report["control_loads"][0]["control"], selected_name)
        self.assertEqual(report["control_loads"][0]["acceleration"], [30., 0., 0.])

        expected_obj, _, _, expected_path = location_fixture("boneforge")
        expected_state = expected_obj.b4ml
        expected_state.secondary_external_acceleration = (80., 0., 0.)
        expected_state.secondary_gravity = 1.
        bpy.context.scene.use_gravity = True
        bpy.context.scene.gravity = (30., 0., 0.)
        secondary.solve(expected_obj, bpy.context.scene)
        expected = curve_values(expected_state.candidate_action,
                                expected_obj, expected_path)
        self.assertEqual(loaded, expected)

        baseline_obj, _, _, baseline_path = location_fixture("boneforge")
        baseline_state = baseline_obj.b4ml
        baseline_state.secondary_external_acceleration = (80., 0., 0.)
        baseline_state.secondary_gravity = 0.
        secondary.solve(baseline_obj, bpy.context.scene)
        baseline = curve_values(baseline_state.candidate_action,
                                baseline_obj, baseline_path)
        self.assertNotEqual(loaded, baseline)

    def test_selected_load_mutation_requires_pose_mode_atomically(self):
        obj, _, _, _ = location_fixture("boneforge")
        if obj.mode != "OBJECT":
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.mode_set(mode="OBJECT")
        before = obj.b4ml.secondary_control_loads
        with self.assertRaisesRegex(ValueError, "Pose Mode"):
            secondary.assign_control_loads(obj, (1., 0., 0.), 1.)
        with self.assertRaisesRegex(ValueError, "Pose Mode"):
            secondary.clear_control_loads(obj)
        self.assertEqual(obj.b4ml.secondary_control_loads, before)

    def test_zero_load_preserves_existing_solver_version_and_output(self):
        baseline_obj, _, _, baseline_path = location_fixture("boneforge")
        baseline_state = baseline_obj.b4ml
        baseline_state.secondary_external_acceleration = (0., 0., 0.)
        baseline_state.secondary_wind_velocity = (0., 0., 0.)
        baseline_state.secondary_impulse_velocity = (0., 0., 0.)
        baseline_report = secondary.solve(baseline_obj, bpy.context.scene)
        baseline = curve_values(baseline_state.candidate_action,
                                baseline_obj, baseline_path)

        obj, _, selected_name, path = location_fixture("boneforge")
        enter_pose(obj)
        state = obj.b4ml
        state.secondary_external_acceleration = (0., 0., 0.)
        state.secondary_load_force = (0., 0., 0.)
        secondary.assign_control_loads(obj, (0., 0., 0.), 7.)
        report = secondary.solve(obj, bpy.context.scene)
        self.assertEqual(report["schema"], 3)
        self.assertEqual(report["backend"], "implicit_selected_control_secondary_v2")
        self.assertEqual(report["loaded_controls"], 0)
        self.assertEqual(report["control_loads"][0]["control"], selected_name)
        self.assertEqual(report["max_control_load_acceleration"], 0.)
        self.assertEqual(report["schema"], baseline_report["schema"])
        self.assertEqual(report["backend"], baseline_report["backend"])
        self.assertEqual(curve_values(state.candidate_action, obj, path), baseline)

    def test_active_load_requires_world_location_atomically(self):
        obj, _, _, _ = load_fixture("boneforge")
        state = obj.b4ml
        original = state.candidate_action
        token = flight._curve_token(obj, original)
        actions = set(bpy.data.actions.keys())
        state.secondary_space = "LOCAL"
        with self.assertRaisesRegex(ValueError, "World simulation space"):
            secondary.solve(obj, bpy.context.scene)
        state.secondary_space = "WORLD"
        state.secondary_location = False
        state.secondary_rotation = True
        with self.assertRaisesRegex(ValueError, "require Location"):
            secondary.solve(obj, bpy.context.scene)
        self.assertIs(state.candidate_action, original)
        self.assertEqual(flight._curve_token(obj, original), token)
        self.assertEqual(set(bpy.data.actions.keys()), actions)

    def test_active_load_rejects_missing_location_curves(self):
        obj, _, selected_name, _ = load_fixture("boneforge")
        state = obj.b4ml
        action = state.candidate_action
        path = obj.pose.bones[selected_name].path_from_id("location")
        curves = w.action_curves(action, getattr(obj.animation_data, "action_slot", None))
        for index in range(3):
            curves.remove(curves.find(path, index=index))
        with self.assertRaisesRegex(ValueError, "every selected control"):
            secondary.solve(obj, bpy.context.scene)
        self.assertIs(state.candidate_action, action)

    def test_load_change_invalidates_cooperative_solve_and_rolls_back(self):
        obj, _, _, _ = load_fixture("boneforge")
        state = obj.b4ml
        original = state.candidate_action
        token = flight._curve_token(obj, original)
        secondary.start(obj, bpy.context.scene)
        self.assertFalse(secondary.step(obj))
        record = json.loads(state.secondary_control_loads)
        record["loads"][0]["mass"] = 3.
        state.secondary_control_loads = json.dumps(record, sort_keys=True,
                                                    separators=(",", ":"))
        with self.assertRaisesRegex(ValueError, "settings changed"):
            secondary.step(obj)
        self.assertFalse(state.secondary_running)
        self.assertIs(state.candidate_action, original)
        self.assertIs(obj.animation_data.action, original)
        self.assertEqual(flight._curve_token(obj, original), token)

    def test_assignment_respects_every_workflow_owner(self):
        obj, _, _, _ = location_fixture("boneforge")
        enter_pose(obj)
        state = obj.b4ml
        before = state.secondary_control_loads
        for field, value in FOREIGN_OWNERS:
            with self.subTest(owner=field):
                setattr(state, field, value)
                with self.assertRaisesRegex(ValueError, "Finish the active"):
                    secondary.assign_control_loads(obj, (1., 0., 0.), 1.)
                self.assertEqual(state.secondary_control_loads, before)
                setattr(state, field, False if isinstance(value, bool) else "")

    def test_assignments_survive_save_and_reload(self):
        obj, _, selected_name, _ = location_fixture("boneforge")
        enter_pose(obj)
        secondary.assign_control_loads(obj, (2., 4., -1.), 2.)
        object_name = obj.name
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / "secondary-control-loads.blend")
            bpy.ops.wm.save_as_mainfile(filepath=path, check_existing=False)
            bpy.ops.wm.open_mainfile(filepath=path, load_ui=False, use_scripts=False)
        loaded = bpy.data.objects[object_name]
        rows = secondary.request(loaded, bpy.context.scene)["control_loads"]
        self.assertEqual(rows, [{"control": selected_name,
                                 "force": [2., 4., -1.], "mass": 2.}])
        self.assertEqual(secondary.control_load_count(loaded), 1)


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(SecondaryControlLoadTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print("B4ML_SECONDARY_CONTROL_LOADS_RESULT:",
          "PASS" if result.wasSuccessful() else "FAIL")
