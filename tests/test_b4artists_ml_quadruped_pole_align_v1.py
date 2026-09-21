"""Bforartists evidence for per-limb quadruped Pole Target Align Bend."""
from pathlib import Path
import hashlib
import json
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
from b4artists_ml import quadruped_pose as pose, workflow
from test_b4artists_ml_quadruped_pose import _action_signature, _generate


CHAIN_STEMS = {
    "Rigify Generated Quadruped (Cat)": {
        "fore": ("MCH-upper_arm_ik", "MCH-forearm_ik"),
        "hind": ("MCH-thigh_ik", "MCH-shin_ik"),
    },
    "Rigify Generated Quadruped (Horse)": {
        "fore": ("MCH-upper_arm_ik", "MCH-forearm_ik"),
        "hind": ("MCH-thigh_ik", "MCH-lower_leg_ik"),
    },
    "Rigify Generated Quadruped (Wolf)": {
        "fore": ("MCH-front_thigh_ik", "MCH-front_shin_ik"),
        "hind": ("MCH-thigh_ik", "MCH-shin_ik"),
    },
}
RECORDS = []


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _runtime_hashes():
    return {str(path.relative_to(ROOT)).replace("\\", "/"): _sha(path)
            for path in sorted((ROOT / "b4artists_ml").glob("*.py"))}


def _matrix_error(left, right):
    return max(abs(left[row][column] - right[row][column])
               for row in range(4) for column in range(4))


def _enable_poles(obj):
    _, _, limbs = pose.binding(obj)
    for row in limbs:
        obj.pose.bones[row["property_bone"]]["pole_vector"] = True
    obj.b4ml.quadruped_use_poles = True
    bpy.context.view_layer.update()
    return limbs


def _source(obj, scene):
    scene.frame_set(19)
    root = obj.pose.bones["root"]
    root.location = (0.007, -0.003, 0.002)
    root.keyframe_insert("location", frame=19)
    action = obj.animation_data.action
    return workflow.raw_pose(obj), action, _action_signature(obj, action)


def _row(obj, label):
    _, _, limbs = pose.binding(obj)
    return next(row for row in limbs if row["pole_label"] == label)


def _points(obj, label):
    profile, _, _ = pose.binding(obj)
    row = _row(obj, label)
    kind, side = row["id"].split("-")
    upper_name, lower_name = (stem + "." + side
                              for stem in CHAIN_STEMS[profile.name][kind])
    evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    upper = evaluated.pose.bones[upper_name]
    lower = evaluated.pose.bones[lower_name]
    world = evaluated.matrix_world
    return row, (world @ upper.head, world @ lower.head, world @ lower.tail)


def _bend(root, middle, end):
    axis = (end - root).normalized()
    value = middle - root
    value -= axis * value.dot(axis)
    return value.normalized()


def _misalign(obj, label):
    row, points = _points(obj, label)
    root, middle, end = points
    bend = _bend(*points)
    axis = (end - root).normalized()
    side = axis.cross(bend).normalized()
    scale = json.loads(obj.b4ml.quadruped_payload)["scale"]
    distance = scale * 0.75
    helper = obj.b4ml.quadruped_targets[label].target
    matrix = helper.matrix_world.copy()
    matrix.translation = middle + side * distance
    helper.matrix_world = matrix
    helper.scale = (1.0, 1.0, 1.0)
    bpy.context.view_layer.update()
    return row, points, distance


class QuadrupedPoleAlignTests(unittest.TestCase):
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
                    record = json.loads(obj.b4ml.quadruped_payload)
                    pose._cleanup(obj, record, restore=True)

    def test_all_four_poles_align_on_cat_horse_and_wolf(self):
        for kind in ("cat", "horse", "wolf"):
            with self.subTest(profile=kind):
                scene, obj = _generate(kind)
                bpy.context.view_layer.objects.active = obj
                _enable_poles(obj)
                source, action, action_signature = _source(obj, scene)
                pose.begin(obj, scene)
                rig_pose = workflow.raw_pose(obj)
                rig_settings = pose._pose_settings(obj)
                records = []
                intended_bends = {}
                for label in pose.POLE_TARGETS:
                    row, before_points, distance = _misalign(obj, label)
                    helper = obj.b4ml.quadruped_targets[label].target
                    result = pose.align_pole_to_current_bend(obj, scene, label)
                    _, after_points = _points(obj, label)
                    expected_direction = _bend(*before_points)
                    actual_direction = (helper.matrix_world.translation - after_points[1]).normalized()
                    error = actual_direction.angle(expected_direction)
                    self.assertLess(error, 1e-6)
                    self.assertAlmostEqual((helper.matrix_world.translation - after_points[1]).length,
                                           distance, places=6)
                    self.assertEqual(result["limb"], row["id"])
                    self.assertLess(result["direction_error_radians"], 1e-6)
                    self.assertEqual(workflow.raw_pose(obj), rig_pose)
                    self.assertEqual(pose._pose_settings(obj), rig_settings)
                    intended_bends[label] = expected_direction
                    records.append({"label": label, "error": error,
                                    "distance": result["distance"]})
                self.assertIs(obj.animation_data.action, action)
                self.assertEqual(_action_signature(obj, action), action_signature)
                metrics = pose.solve(obj, scene)
                self.assertLessEqual(metrics["max_paw_error"], metrics["tolerance"])
                self.assertLessEqual(metrics["max_pole_error"], metrics["tolerance"])
                for label in pose.POLE_TARGETS:
                    _, after_solve = _points(obj, label)
                    self.assertGreater(_bend(*after_solve).dot(intended_bends[label]), 0.99)
                RECORDS.append({"profile": kind, "poles": records,
                                "max_paw_error": metrics["max_paw_error"],
                                "max_pole_error": metrics["max_pole_error"]})
                pose.finish(obj, scene, False)
                self.assertEqual(workflow.raw_pose(obj), source)

    def test_visible_operator_invalidates_keep_and_preserves_options(self):
        scene, obj = _generate("cat")
        bpy.context.view_layer.objects.active = obj
        _enable_poles(obj)
        _source(obj, scene)
        pose.begin(obj, scene)
        pose.solve(obj, scene)
        item = obj.b4ml.quadruped_targets["Fore Pole L"]
        options = (item.enabled, item.use_orientation, item.use_pole,
                   item.pole_distance, item.learn_bend)
        _misalign(obj, "Fore Pole L")
        self.assertEqual(bpy.ops.b4ml.quadruped_pose(
            operation="ALIGN_POLE", target_name="Fore Pole L"), {"FINISHED"})
        record = json.loads(obj.b4ml.quadruped_payload)
        self.assertIsNone(record["signature"])
        self.assertIsNone(record["metrics"])
        self.assertEqual((item.enabled, item.use_orientation, item.use_pole,
                          item.pole_distance, item.learn_bend), options)
        with self.assertRaisesRegex(ValueError, "Solve the current quadruped targets"):
            pose.finish(obj, scene, True)
        self.assertIn("UNDO", b4artists_ml.ui.B4ML_OT_quadruped_pose.bl_options)

    def test_legacy_unknown_straight_and_unbounded_requests_are_atomic(self):
        scene, obj = _generate("wolf")
        bpy.context.view_layer.objects.active = obj
        _enable_poles(obj)
        _source(obj, scene)
        pose.begin(obj, scene)
        helper = obj.b4ml.quadruped_targets["Hind Pole R"].target
        before = helper.matrix_world.copy()
        payload = obj.b4ml.quadruped_payload
        record = json.loads(payload)
        record["schema"] = 3
        obj.b4ml.quadruped_payload = json.dumps(record)
        with self.assertRaisesRegex(ValueError, "schema-4"):
            pose.align_pole_to_current_bend(obj, scene, "Hind Pole R")
        self.assertLess(_matrix_error(helper.matrix_world, before), 1e-7)
        obj.b4ml.quadruped_payload = payload
        with self.assertRaisesRegex(ValueError, "Unknown quadruped Pole Target"):
            pose.align_pole_to_current_bend(obj, scene, "Missing")
        with mock.patch.object(pose, "_evaluated_pole_bend_points",
                               return_value=(("upper", "lower"),
                                             (Vector((0, 0, 0)), Vector((1, 0, 0)),
                                              Vector((2, 0, 0))))):
            with self.assertRaisesRegex(ValueError, "too straight"):
                pose.align_pole_to_current_bend(obj, scene, "Hind Pole R")
        payload = obj.b4ml.quadruped_payload
        rig_pose = workflow.raw_pose(obj)
        action = obj.animation_data.action
        action_signature = _action_signature(obj, action)
        for invalid in (True, "1.0", float("nan"), float("inf"), 0.0, -1.0):
            with self.subTest(invalid_scale=repr(invalid)):
                malformed = json.loads(payload)
                malformed["scale"] = invalid
                obj.b4ml.quadruped_payload = json.dumps(malformed)
                current = helper.matrix_world.copy()
                with self.assertRaisesRegex(ValueError, "Invalid quadruped preview scale"):
                    pose.align_pole_to_current_bend(obj, scene, "Hind Pole R")
                self.assertLess(_matrix_error(helper.matrix_world, current), 1e-7)
                self.assertEqual(workflow.raw_pose(obj), rig_pose)
                self.assertIs(obj.animation_data.action, action)
                self.assertEqual(_action_signature(obj, action), action_signature)
        obj.b4ml.quadruped_payload = payload
        _, points = _points(obj, "Hind Pole R")
        matrix = helper.matrix_world.copy()
        matrix.translation = points[1]
        helper.matrix_world = matrix
        helper.scale = (1.0, 1.0, 1.0)
        bpy.context.view_layer.update()
        centred = helper.matrix_world.copy()
        with self.assertRaisesRegex(ValueError, "0.1 to 8 body scales"):
            pose.align_pole_to_current_bend(obj, scene, "Hind Pole R")
        self.assertLess(_matrix_error(helper.matrix_world, centred), 1e-7)

    def test_hostile_helper_and_changed_modes_reject_before_mutation(self):
        scene, obj = _generate("horse")
        bpy.context.view_layer.objects.active = obj
        limbs = _enable_poles(obj)
        _source(obj, scene)
        pose.begin(obj, scene)
        item = obj.b4ml.quadruped_targets["Fore Pole L"]
        before = item.target.matrix_world.copy()
        item.target.delta_location.x = 0.1
        with self.assertRaisesRegex(ValueError, "delta transforms"):
            pose.align_pole_to_current_bend(obj, scene, "Fore Pole L")
        item.target.delta_location = (0, 0, 0)
        constraint = item.target.constraints.new("COPY_LOCATION")
        with self.assertRaisesRegex(ValueError, "constraints"):
            pose.align_pole_to_current_bend(obj, scene, "Fore Pole L")
        item.target.constraints.remove(constraint)
        obj.pose.bones[limbs[0]["property_bone"]]["pole_vector"] = False
        with self.assertRaisesRegex(ValueError, "Pole Vector mode changed"):
            pose.align_pole_to_current_bend(obj, scene, "Fore Pole L")
        self.assertLess(_matrix_error(item.target.matrix_world, before), 1e-7)
        obj.pose.bones[limbs[0]["property_bone"]]["pole_vector"] = True

    def test_post_update_interference_rolls_back_all_owned_state(self):
        scene, obj = _generate("horse")
        bpy.context.view_layer.objects.active = obj
        _enable_poles(obj)
        _source(obj, scene)
        pose.begin(obj, scene)
        _misalign(obj, "Fore Pole R")
        state = obj.b4ml
        matrices = {item.name: item.target.matrix_world.copy()
                    for item in state.quadruped_targets}
        topology = [(item.name, item.target, item.enabled, item.use_orientation)
                    for item in state.quadruped_targets]
        payload = state.quadruped_payload
        status = state.status
        rig_pose = workflow.raw_pose(obj)
        rig_settings = pose._pose_settings(obj)
        foreign = bpy.data.objects.new("Concurrent Align Bend target", None)
        scene.collection.objects.link(foreign)
        victim = state.quadruped_targets["Hind Paw R"]
        fired = {"value": False}

        def mutate(_scene, _depsgraph):
            if fired["value"]:
                return
            fired["value"] = True
            victim.target = foreign
            state.quadruped_payload = "{}"
            obj.pose.bones["torso"].rotation_mode = "XYZ"

        bpy.app.handlers.depsgraph_update_post.append(mutate)
        try:
            with self.assertRaisesRegex(ValueError,
                                        "state changed|metadata changed|missing or replaced"):
                pose.align_pole_to_current_bend(obj, scene, "Fore Pole R")
        finally:
            if mutate in bpy.app.handlers.depsgraph_update_post:
                bpy.app.handlers.depsgraph_update_post.remove(mutate)
        self.assertTrue(fired["value"])
        self.assertEqual(state.quadruped_payload, payload)
        self.assertEqual(state.status, status)
        self.assertEqual(workflow.raw_pose(obj), rig_pose)
        self.assertEqual(pose._pose_settings(obj), rig_settings)
        for saved, item in zip(topology, state.quadruped_targets):
            self.assertEqual(item.name, saved[0])
            self.assertIs(item.target, saved[1])
            self.assertEqual((item.enabled, item.use_orientation), saved[2:])
            self.assertLess(_matrix_error(item.target.matrix_world, matrices[item.name]), 1e-6)
        bpy.data.objects.remove(foreign, do_unlink=True)

    def test_aligned_request_survives_reload_then_solves_and_keeps(self):
        scene, obj = _generate("cat")
        bpy.context.view_layer.objects.active = obj
        _enable_poles(obj)
        source, action, action_signature = _source(obj, scene)
        action_name = action.name
        pose.begin(obj, scene)
        _misalign(obj, "Hind Pole L")
        pose.align_pole_to_current_bend(obj, scene, "Hind Pole L")
        expected = obj.b4ml.quadruped_targets["Hind Pole L"].target.matrix_world.copy()
        obj.name = "Quadruped Align Bend reload rig"
        path = ROOT / "training/b4artists_ml/cache/quadruped-pole-align-v1.blend"
        bpy.ops.wm.save_as_mainfile(filepath=str(path))
        bpy.ops.wm.open_mainfile(filepath=str(path), use_scripts=False)
        obj = bpy.data.objects["Quadruped Align Bend reload rig"]
        scene = bpy.context.scene
        bpy.context.view_layer.objects.active = obj
        self.assertLess(_matrix_error(
            obj.b4ml.quadruped_targets["Hind Pole L"].target.matrix_world, expected), 1e-7)
        metrics = pose.solve(obj, scene)
        self.assertLessEqual(metrics["max_pole_error"], metrics["tolerance"])
        pose.finish(obj, scene, True)
        self.assertEqual(len(obj.b4ml.anchors), 1)
        self.assertEqual(workflow.raw_pose(obj), source)
        self.assertEqual(obj.animation_data.action.name, action_name)
        self.assertEqual(_action_signature(obj, obj.animation_data.action), action_signature)


if __name__ == "__main__":
    result = unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(QuadrupedPoleAlignTests))
    report = {"schema": 1, "qualification": "Quadruped Align Bend v1",
              "passed": result.wasSuccessful(), "tests": result.testsRun,
              "failures": len(result.failures), "errors": len(result.errors),
              "records": RECORDS, "learned": False,
              "cascadeur_parity": False, "full_goal_complete": False,
              "runtime_source_sha256": _runtime_hashes(),
              "test_sha256": _sha(__file__)}
    output = ROOT / "training/b4artists_ml/results/quadruped-pole-align-focused-v1.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("QUADRUPED_POLE_ALIGN_RESULT: " + json.dumps(report), flush=True)
    if not result.wasSuccessful():
        raise SystemExit(1)
