"""Paired Spine/Chest orientation shaping in the bounded coupled torso chart."""
from pathlib import Path
import json
import os
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "tests"), str(ROOT / "training/b4artists_ml")]

import bpy
import numpy as np

import b4artists_ml
from b4artists_ml import body_preview as body
from b4artists_ml import body_solver as solver
from b4artists_ml import posing
from b4artists_ml import workflow
from test_b4artists_ml_context_rig import ContextRigTests
from test_b4artists_ml_imported_humanoids import authored, keys


RECORDS = []
TORSO_LABELS = {"Pelvis", "Spine", "Chest"}


def reachable_paired_target(obj):
    """Return one exact local-chart pose that visibly changes both torso joints."""
    session = solver.Session(obj)
    spine_name = solver.orientation_bone(session.binding, 1)
    chest_name = solver.orientation_bone(session.binding, 2)
    baseline_spine = obj.pose.bones[spine_name].matrix.to_quaternion().copy()
    baseline_chest = obj.pose.bones[chest_name].matrix.to_quaternion().copy()
    columns = []
    try:
        for control in solver.coupled_torso_controls(session.binding):
            slot = session.binding["rotations"].index(control)
            for axis in range(3):
                parameters = np.zeros(3 + 3 * len(session.q0))
                parameters[3 + slot * 3 + axis] = 0.08
                session._apply(parameters)
                posing._update(obj)
                spine = obj.pose.bones[spine_name].matrix.to_quaternion().copy()
                chest = obj.pose.bones[chest_name].matrix.to_quaternion().copy()
                spine_angle = solver._angle(baseline_spine, spine)
                chest_angle = solver._angle(baseline_chest, chest)
                columns.append((spine_angle, chest_angle, slot, control, axis))
                workflow.restore_pose(obj, session.normalized)
                posing._update(obj)
        spine_column = max(columns, key=lambda row: row[0])
        chest_column = max(columns, key=lambda row: row[1])
        best = None
        for spine_sign in (-1.0, 1.0):
            for chest_sign in (-1.0, 1.0):
                parameters = np.zeros(3 + 3 * len(session.q0))
                parameters[3 + spine_column[2] * 3 + spine_column[4]] += 0.06 * spine_sign
                parameters[3 + chest_column[2] * 3 + chest_column[4]] += 0.06 * chest_sign
                session._apply(parameters)
                posing._update(obj)
                spine = obj.pose.bones[spine_name].matrix.to_quaternion().copy()
                chest = obj.pose.bones[chest_name].matrix.to_quaternion().copy()
                spine_angle = solver._angle(baseline_spine, spine)
                chest_angle = solver._angle(baseline_chest, chest)
                score = min(spine_angle, chest_angle)
                if best is None or score > best[0]:
                    best = (
                        score,
                        session.world_points(session.points())[:3].copy(),
                        session.world.to_quaternion() @ spine,
                        session.world.to_quaternion() @ chest,
                        f"{spine_column[3]}+{chest_column[3]}",
                        [spine_column[4], chest_column[4]],
                    )
                workflow.restore_pose(obj, session.normalized)
                posing._update(obj)
        if best is None or best[0] < 0.005:
            raise AssertionError("No mapped torso control reaches paired Spine/Chest shaping")
        return best
    finally:
        if not session.closed:
            session.cancel()


class CoupledTorsoOrientationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b4artists_ml.register()
        ContextRigTests.setUpClass()
        cls.fixtures = ContextRigTests()

    def tearDown(self):
        for obj in list(bpy.data.objects):
            if hasattr(obj, "b4ml") and obj.b4ml.body_payload:
                if obj.users_scene:
                    bpy.context.window.scene = obj.users_scene[0]
                body.finish(obj, bpy.context.scene, False)
        body.reset_runtime()

    def fixture(self, label):
        if label == "unity_humanoid_fbx":
            obj, _mesh, _roles = authored("unity_humanoid", 1)
            return obj, workflow.raw_pose(obj), obj.animation_data.action, keys(obj)
        obj, source, session, _targets, _mask = self.fixtures.fixture(label, transformed=True)
        session.cancel()
        return obj, source, None, None

    def solve_fixture(self, label):
        obj, source, action, action_keys = self.fixture(label)
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        score, points, spine_goal, chest_goal, control, axis = reachable_paired_target(obj)
        body.begin(obj, bpy.context.scene)
        for item in obj.b4ml.body_targets:
            item.enabled = item.name in TORSO_LABELS
            item.use_orientation = False
        for index, name in enumerate(("Pelvis", "Spine", "Chest")):
            obj.b4ml.body_targets[name].target.location = points[index]
        spine = obj.b4ml.body_targets["Spine"]
        chest = obj.b4ml.body_targets["Chest"]
        spine.use_orientation = True
        chest.use_orientation = True
        spine.target.rotation_quaternion = spine_goal
        chest.target.rotation_quaternion = chest_goal
        obj.b4ml.body_influence = 0.0
        bpy.context.view_layer.update()

        session = body._get(obj)
        request = body._request(obj, session)
        self.assertEqual(set(request[3]), {1, 2})
        before = workflow.raw_pose(obj)
        body.solve(obj)
        points_after = session.world_points(session.points())[:3]
        world_rotation = session.world.to_quaternion()
        spine_after = world_rotation @ obj.pose.bones[
            solver.orientation_bone(session.binding, 1)
        ].matrix.to_quaternion()
        chest_after = world_rotation @ obj.pose.bones[
            solver.orientation_bone(session.binding, 2)
        ].matrix.to_quaternion()
        pin_error = float(np.max(np.linalg.norm(points_after - points, axis=1))) / session.scale
        spine_error = solver._angle(spine_goal, spine_after)
        chest_error = solver._angle(chest_goal, chest_after)
        metrics = body._read(obj)["metrics"]
        coupling = metrics["torso_coupling"]
        self.assertLess(pin_error, 2e-4)
        self.assertLess(spine_error, 0.001)
        self.assertLess(chest_error, 0.001)
        self.assertEqual(coupling["target_count"], 3)
        self.assertEqual(coupling["orientation_joints"], [1, 2])
        self.assertLess(coupling["orientation_error_radians"], 0.001)
        self.assertLess(coupling["chest_orientation_error_radians"], 0.001)
        self.assertNotEqual(workflow.raw_pose(obj), before)
        RECORDS.append({
            "fixture": label,
            "driving_control": control,
            "axis": axis,
            "minimum_source_orientation_change_radians": score,
            "pin_error_body_scales": pin_error,
            "spine_orientation_error_radians": spine_error,
            "chest_orientation_error_radians": chest_error,
            "iterations": coupling["iterations"],
        })

        body.finish(obj, bpy.context.scene, False)
        self.assertEqual(workflow.raw_pose(obj), source)
        if action is not None:
            self.assertIs(obj.animation_data.action, action)
            self.assertEqual(keys(obj), action_keys)

    def test_paired_spine_chest_orientation_on_six_adapters(self):
        for label in (*self.fixtures.builders, "unity_humanoid_fbx"):
            with self.subTest(rig=label):
                self.solve_fixture(label)

    def test_chest_orientation_without_pinned_chest_fails_before_pose_mutation(self):
        obj, _source, _action, _action_keys = self.fixture("boneforge")
        body.begin(obj, bpy.context.scene)
        for item in obj.b4ml.body_targets:
            item.enabled = item.name in {"Pelvis", "Spine"}
            item.use_orientation = False
        spine = obj.b4ml.body_targets["Spine"]
        chest = obj.b4ml.body_targets["Chest"]
        spine.use_orientation = True
        chest.use_orientation = True
        before = workflow.raw_pose(obj)
        with self.assertRaisesRegex(solver.CoupledTorsoError, "optional pinned Chest"):
            body.solve(obj)
        self.assertEqual(workflow.raw_pose(obj), before)


if __name__ == "__main__":
    result = unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(CoupledTorsoOrientationTests)
    )
    report = {
        "schema": "b4ml-coupled-torso-orientation-v1",
        "tests": result.testsRun,
        "passed": result.wasSuccessful(),
        "failures": len(result.failures),
        "errors": len(result.errors),
        "records": RECORDS,
        "package": b4artists_ml.__file__,
        "claim_boundary": {
            "procedural_only": True,
            "learned_motion": False,
            "production_character_qualification": False,
            "cascadeur_parity": False,
        },
    }
    path = ROOT / "training/b4artists_ml/results" / os.environ.get(
        "B4ML_COUPLED_TORSO_ORIENTATION_RESULT", "coupled-torso-orientation-v1.json"
    )
    path.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print("B4ML_COUPLED_TORSO_ORIENTATION_RESULT: " + json.dumps(report), flush=True)
    if not result.wasSuccessful():
        raise SystemExit(1)
