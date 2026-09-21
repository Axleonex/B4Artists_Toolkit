"""Coupled Spine-orientation coverage on frozen proportion variants.

This is a Bforartists-host procedural compatibility probe, not production
qualification or animator-review evidence. It uses only the three frozen,
project-owned Unity Humanoid comparison FBXs and preserves each source Action.
"""
import json
import sys
import unittest
from pathlib import Path

import bpy
import numpy as np
from mathutils import Quaternion

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "tests")]

import b4artists_ml
from b4artists_ml import body_preview as body
from b4artists_ml import body_solver as solver
from b4artists_ml import posing, workflow
import test_b4artists_ml_production_character_generalization_v1 as generalization


TORSO_LABELS = {"Pelvis", "Spine", "Chest"}


def feasible_spine_target(obj, session):
    """Derive a reachable Spine rotation and matching three torso pins."""
    name = solver.orientation_bone(session.binding, 1)
    baseline = obj.pose.bones[name].matrix.to_quaternion().copy()
    best = None
    for control in solver.coupled_torso_controls(session.binding):
        slot = session.binding["rotations"].index(control)
        for axis in range(3):
            parameters = np.zeros(3 + 3 * len(session.q0))
            parameters[3 + slot * 3 + axis] = 0.08
            session._apply(parameters)
            posing._update(obj)
            orientation = obj.pose.bones[name].matrix.to_quaternion().copy()
            angle = solver._angle(baseline, orientation)
            if best is None or angle > best[0]:
                best = (
                    angle,
                    parameters.copy(),
                    session.world_points(session.points()).copy(),
                    orientation,
                )
            workflow.restore_pose(obj, session.normalized)
            posing._update(obj)
    if best is None or best[0] < 0.02:
        raise AssertionError("No mapped control reaches semantic Spine orientation")
    return best[2], session.world.to_quaternion() @ best[3], best[1]


class ProductionCharacterSpineOrientationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b4artists_ml.register()
        manifest = json.loads(generalization.MANIFEST_PATH.read_text(encoding="utf-8-sig"))
        if manifest.get("schema") != "b4ml-portable-comparison-character-manifest-v1":
            raise ValueError("Portable comparison-character manifest changed")
        cls.rows = {row["id"]: row for row in manifest["assets"]}
        if set(cls.rows) != set(generalization.PROFILE_IDS):
            raise ValueError("Frozen proportion-variant set changed")

    def tearDown(self):
        body.reset_runtime()

    def run_frozen_profile(self, profile_id):
        scene, obj, mesh = generalization.imported_asset(self.rows[profile_id])
        action = generalization.assign_disposable_action(obj)
        source_pose = workflow.raw_pose(obj)
        source_action_signature = generalization.action_signature(obj, action)
        source_vertices = generalization.evaluated_vertices(mesh)

        seed_session = solver.Session(obj)
        try:
            points, goal, source_parameters = feasible_spine_target(obj, seed_session)
        finally:
            if not seed_session.closed:
                seed_session.cancel()

        body.begin(obj, scene)
        try:
            rows = body._target_rows(json.loads(obj.b4ml.body_payload))
            labels = {label for _, label in rows}
            if not TORSO_LABELS <= labels:
                raise AssertionError("Frozen humanoid is missing a coupled torso target")
            for _, label in rows:
                item = obj.b4ml.body_targets[label]
                item.enabled = label in TORSO_LABELS
            for index, label in enumerate(("Pelvis", "Spine", "Chest")):
                obj.b4ml.body_targets[label].target.location = points[index]
            spine = obj.b4ml.body_targets["Spine"]
            spine.use_orientation = True
            spine.target.rotation_quaternion = goal
            obj.b4ml.body_influence = 0.0
            bpy.context.view_layer.update()

            request = body._request(obj, body._get(obj))
            self.assertLess(solver._angle(Quaternion(request[3][1]), goal), 0.001)
            self.assertLess(
                float(np.max(np.linalg.norm(request[0][:3] - points[:3], axis=1))),
                1e-6,
            )

            session = body._get(obj)
            session._apply(source_parameters)
            posing._update(obj)
            replay_points = session.world_points(session.points())
            spine_name = solver.orientation_bone(session.binding, 1)
            replay_orientation = (
                session.world.to_quaternion()
                @ obj.pose.bones[spine_name].matrix.to_quaternion()
            )
            self.assertLess(
                float(np.max(np.linalg.norm(replay_points[:3] - points[:3], axis=1)))
                / session.scale,
                2e-4,
            )
            self.assertLess(solver._angle(goal, replay_orientation), 0.001)
            workflow.restore_pose(obj, session.normalized)
            posing._update(obj)

            body.solve(obj)
            actual_points = session.world_points(session.points())
            actual_orientation = (
                session.world.to_quaternion()
                @ obj.pose.bones[spine_name].matrix.to_quaternion()
            )
            pin_error = float(
                np.max(np.linalg.norm(actual_points[:3] - points[:3], axis=1))
                / session.scale
            )
            orientation_error = solver._angle(goal, actual_orientation)
            metrics = body._read(obj)["metrics"]
            coupling = metrics["torso_coupling"]
            self.assertLess(pin_error, 2e-4)
            self.assertLess(float(metrics["length_error"]), 0.002)
            self.assertLess(orientation_error, 0.001)
            self.assertLess(float(metrics["orientation_error_radians"]), 0.001)
            self.assertEqual(coupling["target_count"], 3)
            self.assertEqual(coupling["orientation_joint"], 1)
            self.assertTrue(np.isfinite(coupling["residual_norm"]))
            deformation = float(
                np.max(
                    np.linalg.norm(
                        generalization.evaluated_vertices(mesh) - source_vertices,
                        axis=1,
                    )
                )
            )
            self.assertGreater(deformation, 1e-4)

            body.finish(obj, scene, False)
            self.assertEqual(workflow.raw_pose(obj), source_pose)
            self.assertIs(obj.animation_data.action, action)
            self.assertEqual(
                generalization.action_signature(obj, action), source_action_signature
            )
        finally:
            if getattr(obj, "b4ml", None) and obj.b4ml.body_payload:
                body.finish(obj, scene, False)

    def test_standard_proportion_keeps_coupled_spine_orientation_bounded(self):
        self.run_frozen_profile("standard")

    def test_tall_long_limb_proportion_keeps_coupled_spine_orientation_bounded(self):
        self.run_frozen_profile("tall_long_limbed")

    def test_short_broad_proportion_keeps_coupled_spine_orientation_bounded(self):
        self.run_frozen_profile("short_broad")


if __name__ == "__main__":
    result = unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(
            ProductionCharacterSpineOrientationTests
        )
    )
    print(
        "B4ML_PRODUCTION_SPINE_ORIENTATION_RESULT:",
        "PASS" if result.wasSuccessful() else "FAIL",
        flush=True,
    )
    if not result.wasSuccessful():
        raise SystemExit(1)
