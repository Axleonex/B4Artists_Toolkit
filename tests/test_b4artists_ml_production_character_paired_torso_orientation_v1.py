"""Paired torso-orientation coverage on frozen proportion variants."""
from pathlib import Path
import json
import os
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "tests")]

import bpy
import numpy as np
from mathutils import Quaternion, Vector

import b4artists_ml
from b4artists_ml import body_preview as body
from b4artists_ml import body_solver as solver
from b4artists_ml import workflow
import test_b4artists_ml_production_character_generalization_v1 as generalization


RECORDS = []
TORSO_LABELS = {"Pelvis", "Spine", "Chest"}


class ProductionCharacterPairedTorsoOrientationTests(unittest.TestCase):
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

    def run_profile(self, profile_id):
        scene, obj, mesh = generalization.imported_asset(self.rows[profile_id])
        action = generalization.assign_disposable_action(obj)
        source_pose = workflow.raw_pose(obj)
        source_action_signature = generalization.action_signature(obj, action)
        source_vertices = generalization.evaluated_vertices(mesh)
        body.begin(obj, scene)
        try:
            for item in obj.b4ml.body_targets:
                item.enabled = item.name in TORSO_LABELS
                item.use_orientation = False
            axis = workflow.display_world(obj).to_quaternion() @ Vector((1, 0, 0))
            axis.normalize()
            projection = body.project_coupled_torso_orientation(
                obj, axis, 0.025, 0.04
            )
            points = np.asarray(projection["displayed_targets"], dtype=float)
            spine_goal = Quaternion(projection["displayed_orientations"][0])
            chest_goal = Quaternion(projection["displayed_orientations"][1])
            for index, label in enumerate(("Pelvis", "Spine", "Chest")):
                obj.b4ml.body_targets[label].target.location = points[index]
            obj.b4ml.body_targets["Spine"].use_orientation = True
            obj.b4ml.body_targets["Chest"].use_orientation = True
            obj.b4ml.body_targets["Spine"].target.rotation_quaternion = spine_goal
            obj.b4ml.body_targets["Chest"].target.rotation_quaternion = chest_goal
            obj.b4ml.body_influence = 0.0
            bpy.context.view_layer.update()
            body.solve(obj, iterations=50)

            session = body._get(obj)
            actual_points = session.world_points(session.points())[:3]
            world_rotation = session.world.to_quaternion()
            spine_actual = world_rotation @ obj.pose.bones[
                solver.orientation_bone(session.binding, 1)
            ].matrix.to_quaternion()
            chest_actual = world_rotation @ obj.pose.bones[
                solver.orientation_bone(session.binding, 2)
            ].matrix.to_quaternion()
            pin_error = float(np.max(np.linalg.norm(actual_points - points, axis=1))) / session.scale
            spine_error = solver._angle(spine_goal, spine_actual)
            chest_error = solver._angle(chest_goal, chest_actual)
            coupling = body._read(obj)["metrics"]["torso_coupling"]
            self.assertLess(pin_error, 2e-4)
            self.assertLess(spine_error, 0.001)
            self.assertLess(chest_error, 0.001)
            self.assertEqual(coupling["orientation_joints"], [1, 2])
            deformation = float(np.max(np.linalg.norm(
                generalization.evaluated_vertices(mesh) - source_vertices, axis=1
            )))
            self.assertGreater(deformation, 1e-4)
            RECORDS.append({
                "profile": profile_id,
                "driving_controls": projection["controls"],
                "axis": list(axis),
                "requested_spine_radians": 0.025,
                "requested_chest_radians": 0.04,
                "projection_residual_radians": projection["residual_radians"],
                "projection_progress": projection["progress"],
                "pin_error_body_scales": pin_error,
                "spine_orientation_error_radians": spine_error,
                "chest_orientation_error_radians": chest_error,
                "maximum_mesh_deformation": deformation,
                "iterations": coupling["iterations"],
            })

            body.finish(obj, scene, False)
            self.assertEqual(workflow.raw_pose(obj), source_pose)
            self.assertIs(obj.animation_data.action, action)
            self.assertEqual(generalization.action_signature(obj, action), source_action_signature)
        finally:
            if getattr(obj, "b4ml", None) and obj.b4ml.body_payload:
                body.finish(obj, scene, False)

    def test_standard(self):
        self.run_profile("standard")

    def test_tall_long_limbed(self):
        self.run_profile("tall_long_limbed")

    def test_short_broad(self):
        self.run_profile("short_broad")


if __name__ == "__main__":
    result = unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(
            ProductionCharacterPairedTorsoOrientationTests
        )
    )
    report = {
        "schema": "b4ml-production-character-paired-torso-orientation-v1",
        "tests": result.testsRun,
        "passed": result.wasSuccessful(),
        "failures": len(result.failures),
        "errors": len(result.errors),
        "records": RECORDS,
        "package": b4artists_ml.__file__,
        "claim_boundary": {
            "frozen_proportion_probe_only": True,
            "arbitrary_production_rigs": False,
            "human_visual_quality": False,
            "learned_motion": False,
            "cascadeur_parity": False,
        },
    }
    output = ROOT / "training/b4artists_ml/results" / os.environ.get(
        "B4ML_PRODUCTION_PAIRED_TORSO_RESULT",
        "production-character-paired-torso-orientation-v1-20260917.json",
    )
    output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print("B4ML_PRODUCTION_PAIRED_TORSO_RESULT: " + json.dumps(report), flush=True)
    if not result.wasSuccessful():
        raise SystemExit(1)
