"""Bforartists evidence for quadruped Pole Target Flip Side and Set Distance."""
from pathlib import Path
import hashlib
import json
import math
import os
import sys
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [os.environ.get("B4ML_PACKAGE", str(ROOT)), str(ROOT / "tests")]

import addon_utils
import bpy
from mathutils import Vector

import b4artists_ml
from b4artists_ml import quadruped_gait, quadruped_pose as pose, workflow
from test_b4artists_ml_quadruped_pose import _generate
from test_b4artists_ml_quadruped_pole_align_v1 import (
    _bend, _enable_poles, _matrix_error, _misalign, _points, _source,
)


RECORDS = []


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _runtime_hashes():
    return {str(path.relative_to(ROOT)).replace("\\", "/"): _sha(path)
            for path in sorted((ROOT / "b4artists_ml").glob("*.py"))}


def _target_state(obj):
    return [(item.name, item.target, item.pole, item.enabled, item.use_orientation,
             item.use_pole, item.pole_distance, item.learn_bend,
             item.target.matrix_world.copy())
            for item in obj.b4ml.quadruped_targets]


def _action_evidence(obj, action):
    slot = getattr(obj.animation_data, "action_slot", None)
    return {
        "name": action.name,
        "digest": quadruped_gait._action_digest(obj, action),
        "slot_handle": getattr(obj.animation_data, "action_slot_handle", 0),
        "slot_identifier": getattr(slot, "identifier", None),
        "slot_target": getattr(slot, "target_id_type", None),
    }


def _assert_action_unchanged(case, obj, action, evidence, require_identity=True):
    if require_identity:
        case.assertIs(obj.animation_data.action, action)
    case.assertEqual(obj.animation_data.action.name, evidence["name"])
    case.assertEqual(_action_evidence(obj, obj.animation_data.action), evidence)


class QuadrupedPoleControlTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not b4artists_ml.is_bforartists():
            raise unittest.SkipTest("Bforartists required")
        addon_utils.enable("rigify", default_set=True, persistent=False)
        b4artists_ml.register()

    def tearDown(self):
        for obj in list(bpy.data.objects):
            if hasattr(obj, "b4ml") and obj.b4ml.quadruped_payload:
                if obj.users_scene:
                    bpy.context.window.scene = obj.users_scene[0]
                try:
                    pose.finish(obj, bpy.context.scene, False)
                except Exception:
                    pose._cleanup(obj, json.loads(obj.b4ml.quadruped_payload), restore=True)

    def test_flip_all_four_poles_on_cat_horse_and_wolf(self):
        for kind in ("cat", "horse", "wolf"):
            with self.subTest(profile=kind):
                scene, obj = _generate(kind)
                bpy.context.view_layer.objects.active = obj
                _enable_poles(obj)
                source, action, _ = _source(obj, scene)
                action_evidence = _action_evidence(obj, action)
                pose.begin(obj, scene)
                rig_pose = workflow.raw_pose(obj)
                requested = {}
                records = []
                for label in pose.POLE_TARGETS:
                    row, points, distance = _misalign(obj, label)
                    item = obj.b4ml.quadruped_targets[label]
                    options = (item.enabled, item.use_orientation, item.use_pole,
                               item.pole_distance, item.learn_bend)
                    expected = -_bend(*points)
                    result = pose.flip_pole_to_opposite_bend(obj, scene, label)
                    _, current = _points(obj, label)
                    actual = (item.target.matrix_world.translation - current[1]).normalized()
                    self.assertLess(actual.angle(expected), 1e-6)
                    self.assertAlmostEqual((item.target.matrix_world.translation - current[1]).length,
                                           distance, places=6)
                    self.assertEqual((item.enabled, item.use_orientation, item.use_pole,
                                      item.pole_distance, item.learn_bend), options)
                    self.assertEqual((result["operation"], result["limb"]), ("FLIP", row["id"]))
                    requested[label] = expected
                    records.append({"label": label, "distance": result["distance"],
                                    "error": result["direction_error_radians"]})
                self.assertEqual(workflow.raw_pose(obj), rig_pose)
                _assert_action_unchanged(self, obj, action, action_evidence)
                metrics = pose.solve(obj, scene)
                self.assertLessEqual(metrics["max_paw_error"], metrics["tolerance"])
                self.assertLessEqual(metrics["max_pole_error"], metrics["tolerance"])
                bend_responses = {}
                for label, direction in requested.items():
                    response = _bend(*_points(obj, label)[1]).dot(direction)
                    self.assertGreater(response, 0.9)
                    bend_responses[label] = response
                RECORDS.append({"profile": kind, "flip": records,
                                "bend_response_dot": bend_responses,
                                "max_paw_error": metrics["max_paw_error"],
                                "max_pole_error": metrics["max_pole_error"]})
                pose.finish(obj, scene, False)
                self.assertEqual(workflow.raw_pose(obj), source)

    def test_set_distance_preserves_each_ray_and_only_changes_requested_distance(self):
        scene, obj = _generate("horse")
        bpy.context.view_layer.objects.active = obj
        _enable_poles(obj)
        _source(obj, scene)
        pose.begin(obj, scene)
        rig_pose = workflow.raw_pose(obj)
        distances = (0.25, 0.5, 0.75, 1.0)
        for label, requested in zip(pose.POLE_TARGETS, distances):
            item = obj.b4ml.quadruped_targets[label]
            scale_locks = tuple(item.target.lock_scale)
            _, points = _points(obj, label)
            before_direction = (item.target.matrix_world.translation - points[1]).normalized()
            before = _target_state(obj)
            result = pose.set_pole_distance(obj, scene, label, requested)
            _, after_points = _points(obj, label)
            after_direction = (item.target.matrix_world.translation - after_points[1]).normalized()
            self.assertLess(after_direction.angle(before_direction), 1e-6)
            scale = json.loads(obj.b4ml.quadruped_payload)["scale"]
            self.assertAlmostEqual((item.target.matrix_world.translation - after_points[1]).length /
                                   scale, requested, places=6)
            self.assertAlmostEqual(item.pole_distance, requested, places=6)
            self.assertAlmostEqual(result["distance_body_scales"], requested, places=6)
            self.assertAlmostEqual(result["stored_distance_body_scales"], requested, places=6)
            self.assertEqual(tuple(item.target.lock_scale), scale_locks)
            for saved, current in zip(before, obj.b4ml.quadruped_targets):
                if current.name == label:
                    self.assertEqual((current.enabled, current.use_orientation, current.use_pole,
                                      current.learn_bend), saved[3:6] + (saved[7],))
                else:
                    self.assertEqual(current.pole_distance, saved[6])
                    self.assertLess(_matrix_error(current.target.matrix_world, saved[8]), 1e-7)
        self.assertEqual(workflow.raw_pose(obj), rig_pose)
        record = json.loads(obj.b4ml.quadruped_payload)
        self.assertIsNone(record["signature"])
        self.assertIsNone(record["metrics"])

    def test_visible_operators_invalidate_keep_and_have_native_undo(self):
        scene, obj = _generate("cat")
        bpy.context.view_layer.objects.active = obj
        _enable_poles(obj)
        _source(obj, scene)
        pose.begin(obj, scene)
        pose.solve(obj, scene)
        self.assertEqual(bpy.ops.b4ml.quadruped_pose(
            operation="FLIP_POLE", target_name="Fore Pole L"), {"FINISHED"})
        record = json.loads(obj.b4ml.quadruped_payload)
        self.assertIsNone(record["signature"])
        with self.assertRaisesRegex(ValueError, "Solve the current quadruped targets"):
            pose.finish(obj, scene, True)
        pose.solve(obj, scene)
        item = obj.b4ml.quadruped_targets["Hind Pole R"]
        item.pole_distance = 0.65
        self.assertEqual(bpy.ops.b4ml.quadruped_pose(
            operation="SET_POLE_DISTANCE", target_name="Hind Pole R"), {"FINISHED"})
        self.assertAlmostEqual(pose.set_pole_distance(
            obj, scene, "Hind Pole R", 0.7)["distance_body_scales"], 0.7, places=6)
        self.assertIn("UNDO", b4artists_ml.ui.B4ML_OT_quadruped_pose.bl_options)

    def test_invalid_requests_and_singular_geometry_are_atomic(self):
        scene, obj = _generate("wolf")
        bpy.context.view_layer.objects.active = obj
        _enable_poles(obj)
        _source(obj, scene)
        pose.begin(obj, scene)
        before = _target_state(obj)
        payload = obj.b4ml.quadruped_payload
        status = obj.b4ml.status
        rig_pose = workflow.raw_pose(obj)
        helper = obj.b4ml.quadruped_targets["Fore Pole R"].target
        helper.lock_location[0] = True
        with self.assertRaisesRegex(ValueError, "unlocked XYZ location"):
            pose.flip_pole_to_opposite_bend(obj, scene, "Fore Pole R")
        helper.lock_location[0] = False
        helper.lock_scale[1] = True
        with self.assertRaisesRegex(ValueError, "unlocked XYZ scale"):
            pose.set_pole_distance(obj, scene, "Fore Pole R", 0.5)
        helper.lock_scale[1] = False
        obj.b4ml.candidate_action = obj.animation_data.action
        with self.assertRaisesRegex(ValueError, "active animation workflow"):
            pose.set_pole_distance(obj, scene, "Fore Pole R", 0.5)
        obj.b4ml.candidate_action = None
        for value in (None, True, "0.5", float("nan"), float("inf"), 0.09, 4.01):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "finite number"):
                    pose.set_pole_distance(obj, scene, "Fore Pole R", value)
        with self.assertRaisesRegex(ValueError, "Unknown quadruped Pole Target"):
            pose.flip_pole_to_opposite_bend(obj, scene, "Missing")
        with mock.patch.object(pose, "_evaluated_pole_bend_points",
                               return_value=(("upper", "lower"),
                                             (Vector((0, 0, 0)), Vector((1, 0, 0)),
                                              Vector((2, 0, 0))))):
            with self.assertRaisesRegex(ValueError, "too straight"):
                pose.flip_pole_to_opposite_bend(obj, scene, "Hind Pole L")
        self.assertEqual(obj.b4ml.quadruped_payload, payload)
        self.assertEqual(obj.b4ml.status, status)
        self.assertEqual(workflow.raw_pose(obj), rig_pose)
        for saved, current in zip(before, obj.b4ml.quadruped_targets):
            self.assertEqual((current.name, current.target, current.pole, current.enabled,
                              current.use_orientation, current.use_pole,
                              current.pole_distance, current.learn_bend), saved[:8])
            self.assertLess(_matrix_error(current.target.matrix_world, saved[8]), 1e-7)

    def test_dependency_handler_interference_rolls_back_distance_and_topology(self):
        scene, obj = _generate("cat")
        bpy.context.view_layer.objects.active = obj
        _enable_poles(obj)
        _source(obj, scene)
        pose.begin(obj, scene)
        state = obj.b4ml
        before = _target_state(obj)
        payload = state.quadruped_payload
        status = state.status
        rig_pose = workflow.raw_pose(obj)
        object_matrix = obj.matrix_world.copy()
        foreign = bpy.data.objects.new("Concurrent pole distance target", None)
        scene.collection.objects.link(foreign)
        fired = {"value": False}

        def mutate(_scene, _depsgraph):
            if fired["value"]:
                return
            fired["value"] = True
            state.quadruped_targets["Hind Paw R"].target = foreign
            state.quadruped_payload = "{}"
            obj.pose.bones["torso"].rotation_mode = "XYZ"
            obj.location.x += 2.0

        bpy.app.handlers.depsgraph_update_post.append(mutate)
        try:
            with self.assertRaisesRegex(ValueError,
                                        "state changed|metadata changed|missing or replaced"):
                pose.set_pole_distance(obj, scene, "Fore Pole R", 0.6)
        finally:
            if mutate in bpy.app.handlers.depsgraph_update_post:
                bpy.app.handlers.depsgraph_update_post.remove(mutate)
        self.assertTrue(fired["value"])
        self.assertEqual((state.quadruped_payload, state.status), (payload, status))
        self.assertEqual(workflow.raw_pose(obj), rig_pose)
        self.assertLess(_matrix_error(obj.matrix_world, object_matrix), 1e-7)
        for saved, current in zip(before, state.quadruped_targets):
            self.assertEqual((current.name, current.target, current.pole, current.enabled,
                              current.use_orientation, current.use_pole,
                              current.pole_distance, current.learn_bend), saved[:8])
            self.assertLess(_matrix_error(current.target.matrix_world, saved[8]), 1e-7)
        bpy.data.objects.remove(foreign, do_unlink=True)

    def test_parent_inverse_interference_is_detected_and_rolled_back(self):
        scene, obj = _generate("horse")
        parent = bpy.data.objects.new("Pole controls parent", None)
        scene.collection.objects.link(parent)
        parent.location = (1.25, -0.75, 0.5)
        world = obj.matrix_world.copy()
        obj.parent = parent
        obj.matrix_parent_inverse = parent.matrix_world.inverted()
        obj.matrix_world = world
        bpy.context.view_layer.objects.active = obj
        _enable_poles(obj)
        _source(obj, scene)
        pose.begin(obj, scene)
        state = obj.b4ml
        before = _target_state(obj)
        payload = state.quadruped_payload
        status = state.status
        rig_pose = workflow.raw_pose(obj)
        object_matrix = obj.matrix_world.copy()
        parent_inverse = obj.matrix_parent_inverse.copy()
        original_snapshot = pose._object_transform_snapshot
        gate = {"armed": False, "snapshot": None, "matcher_rejected": False}
        fired = {"value": False}

        def capture_and_arm(target):
            snapshot = original_snapshot(target)
            if target is obj:
                gate["snapshot"] = snapshot
                gate["armed"] = True
            return snapshot

        def mutate_parent_space(_scene, _depsgraph):
            if fired["value"] or not gate["armed"]:
                return
            fired["value"] = True
            changed = obj.matrix_parent_inverse.copy()
            changed[0][3] += 0.25
            obj.matrix_parent_inverse = changed
            gate["matcher_rejected"] = not pose._object_transform_matches(
                obj, gate["snapshot"])

        pose._object_transform_snapshot = capture_and_arm
        bpy.app.handlers.depsgraph_update_post.append(mutate_parent_space)
        try:
            with self.assertRaisesRegex(ValueError,
                                        "rig object transform changed|Return the rig object"):
                pose.flip_pole_to_opposite_bend(obj, scene, "Fore Pole L")
        finally:
            pose._object_transform_snapshot = original_snapshot
            if mutate_parent_space in bpy.app.handlers.depsgraph_update_post:
                bpy.app.handlers.depsgraph_update_post.remove(mutate_parent_space)
        self.assertTrue(fired["value"])
        self.assertTrue(gate["matcher_rejected"])
        self.assertEqual((state.quadruped_payload, state.status), (payload, status))
        self.assertEqual(workflow.raw_pose(obj), rig_pose)
        self.assertLess(_matrix_error(obj.matrix_world, object_matrix), 1e-7)
        self.assertLess(_matrix_error(obj.matrix_parent_inverse, parent_inverse), 1e-12)
        for saved, current in zip(before, state.quadruped_targets):
            self.assertEqual((current.name, current.target, current.pole, current.enabled,
                              current.use_orientation, current.use_pole,
                              current.pole_distance, current.learn_bend), saved[:8])
            self.assertLess(_matrix_error(current.target.matrix_world, saved[8]), 1e-7)

        obj.parent = None
        obj.matrix_world = object_matrix
        bpy.data.objects.remove(parent, do_unlink=True)

    def test_foreign_workflow_started_during_update_is_preserved_and_edit_rolls_back(self):
        scene, obj = _generate("horse")
        bpy.context.view_layer.objects.active = obj
        _enable_poles(obj)
        _source(obj, scene)
        pose.begin(obj, scene)
        state = obj.b4ml
        item = state.quadruped_targets["Hind Pole L"]
        matrix = item.target.matrix_world.copy()
        distance = item.pole_distance
        payload = state.quadruped_payload
        status = state.status
        fired = {"value": False}

        def start_foreign(_scene, _depsgraph):
            if fired["value"]:
                return
            fired["value"] = True
            state.body_payload = "foreign-workflow-owns-shared-state"
            state.status = "Foreign workflow started"

        bpy.app.handlers.depsgraph_update_post.append(start_foreign)
        try:
            with self.assertRaisesRegex(ValueError, "Another animation workflow started"):
                pose.set_pole_distance(obj, scene, "Hind Pole L", 0.8)
        finally:
            if start_foreign in bpy.app.handlers.depsgraph_update_post:
                bpy.app.handlers.depsgraph_update_post.remove(start_foreign)
        self.assertTrue(fired["value"])
        self.assertLess(_matrix_error(item.target.matrix_world, matrix), 1e-7)
        self.assertAlmostEqual(item.pole_distance, distance, places=7)
        self.assertEqual(state.quadruped_payload, payload)
        self.assertEqual(state.body_payload, "foreign-workflow-owns-shared-state")
        self.assertEqual(state.status, "Foreign workflow started")
        state.body_payload = ""
        state.status = status

    def test_flip_and_distance_survive_reload_then_solve_and_keep(self):
        scene, obj = _generate("wolf")
        bpy.context.view_layer.objects.active = obj
        _enable_poles(obj)
        source, action, _ = _source(obj, scene)
        action_evidence = _action_evidence(obj, action)
        action_name = action.name
        pose.begin(obj, scene)
        pose.flip_pole_to_opposite_bend(obj, scene, "Fore Pole L")
        pose.set_pole_distance(obj, scene, "Fore Pole L", 0.55)
        expected = obj.b4ml.quadruped_targets["Fore Pole L"].target.matrix_world.copy()
        obj.name = "Quadruped pole controls reload rig"
        path = ROOT / "training/b4artists_ml/cache/quadruped-pole-controls-v1.blend"
        bpy.ops.wm.save_as_mainfile(filepath=str(path))
        bpy.ops.wm.open_mainfile(filepath=str(path), use_scripts=False)
        obj = bpy.data.objects["Quadruped pole controls reload rig"]
        scene = bpy.context.scene
        bpy.context.view_layer.objects.active = obj
        item = obj.b4ml.quadruped_targets["Fore Pole L"]
        self.assertLess(_matrix_error(item.target.matrix_world, expected), 1e-7)
        self.assertAlmostEqual(item.pole_distance, 0.55, places=6)
        metrics = pose.solve(obj, scene)
        self.assertLessEqual(metrics["max_pole_error"], metrics["tolerance"])
        pose.finish(obj, scene, True)
        self.assertEqual(len(obj.b4ml.anchors), 1)
        self.assertEqual(workflow.raw_pose(obj), source)
        self.assertEqual(obj.animation_data.action.name, action_name)
        _assert_action_unchanged(self, obj, action, action_evidence, require_identity=False)


if __name__ == "__main__":
    result = unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(QuadrupedPoleControlTests))
    report = {"schema": 1, "qualification": "Quadruped Pole Controls v1",
              "passed": result.wasSuccessful(), "tests": result.testsRun,
              "failures": len(result.failures), "errors": len(result.errors),
              "records": RECORDS, "learned": False,
              "cascadeur_parity": False, "full_goal_complete": False,
              "runtime_source_sha256": _runtime_hashes(),
              "test_sha256": _sha(__file__),
              "support_source_sha256": {
                  "tests/test_b4artists_ml_quadruped_pose.py":
                      _sha(ROOT / "tests/test_b4artists_ml_quadruped_pose.py"),
                  "tests/test_b4artists_ml_quadruped_pole_align_v1.py":
                      _sha(ROOT / "tests/test_b4artists_ml_quadruped_pole_align_v1.py"),
              }}
    output = ROOT / "training/b4artists_ml/results/quadruped-pole-controls-focused-v1.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    raise SystemExit(0 if result.wasSuccessful() else 1)
