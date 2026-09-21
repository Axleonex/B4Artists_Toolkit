"""Native coverage for projected torso targets with additional foot pins."""
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
from b4artists_ml import posing
from b4artists_ml import rig_state
from b4artists_ml import workflow
from test_b4artists_ml_context_rig import ContextRigTests
from test_b4artists_ml_imported_humanoids import authored, keys

RECORDS = []


class CoupledFullBodyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b4artists_ml.register()
        ContextRigTests.setUpClass()
        cls.fixtures = ContextRigTests()

    def tearDown(self):
        for obj in list(bpy.data.objects):
            if hasattr(obj, "b4ml") and obj.b4ml.body_payload and obj.users_scene:
                body.finish(obj, obj.users_scene[0], False)
        body.reset_runtime()

    def fixture(self, label):
        if label == "unity_humanoid_fbx":
            obj, _mesh, _roles = authored("unity_humanoid", 1)
            return obj, workflow.raw_pose(obj), obj.animation_data.action, keys(obj)
        obj, source, session, _targets, _mask = self.fixtures.fixture(label, transformed=True)
        session.cancel()
        return obj, source, None, None

    def run_fixture(self, label):
        obj, source, action, action_keys = self.fixture(label)
        scene = next(iter(obj.users_scene), bpy.context.scene)
        bpy.context.window.scene = scene
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        source_modes = rig_state.mode_values(obj)
        body.begin(obj, scene)
        session = body._get(obj)
        before_feet = session.world_points(session.points())[[13, 16]].copy()
        for item in obj.b4ml.body_targets:
            item.enabled = item.name in {"Pelvis", "Spine", "Chest"}
            item.use_orientation = False
            item.use_pole = False
        axis = Vector(session.basis[:, 0])
        spine = obj.b4ml.body_targets["Spine"]
        chest = obj.b4ml.body_targets["Chest"]
        spine_angle, chest_angle = ((.008, .012)
                                    if label.startswith("metarig_") else (.03, .045))
        projection = body.project_coupled_torso_orientation(
            obj, axis, spine_angle, chest_angle)
        for index, label_name in enumerate(("Pelvis", "Spine", "Chest")):
            obj.b4ml.body_targets[label_name].target.location = projection["displayed_targets"][index]
        spine.use_orientation = True
        chest.use_orientation = True
        spine.target.rotation_quaternion = Quaternion(projection["displayed_orientations"][0])
        chest.target.rotation_quaternion = Quaternion(projection["displayed_orientations"][1])
        obj.b4ml.body_influence = 0.0
        body.solve(obj)
        metrics = body._read(obj)["metrics"]
        self.assertLess(metrics["pin_error"], 2e-4)
        coupling = metrics["torso_coupling"]
        self.assertLess(coupling["orientation_error_radians"], .001)
        self.assertLess(coupling["chest_orientation_error_radians"], .001)
        body.finish(obj, scene, True)
        payload = json.loads(obj.b4ml.anchors[0].payload)
        rig_state.restore_values(obj, payload.get("rig_modes", rig_state.canonical_modes(obj)))
        workflow.restore_pose(obj, payload["pose"])
        posing._update(obj)
        posing.begin(obj, scene)
        for item in obj.b4ml.pose_targets:
            item.enabled = item.name in {"leg-L", "leg-R"}
            if item.name == "leg-L":
                item.target.location = before_feet[0]
            elif item.name == "leg-R":
                item.target.location = before_feet[1]
        repin = posing.solve(obj, scene)
        max_repin = max(row["normalized_error"] for row in repin)
        self.assertLess(max_repin, 2e-4)
        posing.finish(obj, scene, True)
        RECORDS.append({
            "fixture": label,
            "pin_error_body_scales": metrics["pin_error"],
            "spine_orientation_error_radians": coupling["orientation_error_radians"],
            "chest_orientation_error_radians": coupling["chest_orientation_error_radians"],
            "maximum_contact_repin_error": max_repin,
            "projection_residual_radians": projection["residual_radians"],
            "requested_orientation_radians": [spine_angle, chest_angle],
            "iterations": metrics["iterations"],
        })
        rig_state.restore_values(obj, source_modes)
        workflow.restore_pose(obj, source)
        posing._update(obj)
        obj.b4ml.anchors.clear()
        self.assertEqual(workflow.raw_pose(obj), source)
        if action is not None:
            self.assertIs(obj.animation_data.action, action)
            self.assertEqual(keys(obj), action_keys)

    def test_projected_torso_with_feet_on_six_adapters(self):
        labels = (*self.fixtures.builders, "unity_humanoid_fbx")
        requested = os.environ.get("B4ML_COUPLED_FULL_BODY_FIXTURES")
        if requested:
            selected = tuple(value.strip() for value in requested.split(",") if value.strip())
            if not selected or not set(selected) <= set(labels):
                raise ValueError("Unknown coupled-full-body fixture selection")
            labels = selected
        for label in labels:
            with self.subTest(rig=label):
                self.run_fixture(label)


if __name__ == "__main__":
    result = unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(CoupledFullBodyTests)
    )
    report = {
        "schema": "b4ml-coupled-full-body-v1",
        "tests": result.testsRun,
        "passed": result.wasSuccessful(),
        "failures": len(result.failures),
        "errors": len(result.errors),
        "records": RECORDS,
        "package": b4artists_ml.__file__,
        "claim_boundary": {
            "procedural_only": True,
            "human_visual_quality": False,
            "learned_motion": False,
            "cascadeur_parity": False,
        },
    }
    output = ROOT / "training/b4artists_ml/results" / os.environ.get(
        "B4ML_COUPLED_FULL_BODY_RESULT", "coupled-full-body-v1.json"
    )
    output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print("B4ML_COUPLED_FULL_BODY_RESULT: " + json.dumps(report), flush=True)
    if not result.wasSuccessful():
        raise SystemExit(1)
