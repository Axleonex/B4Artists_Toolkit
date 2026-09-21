"""Scene-local semantic pose-request reuse for generated Rigify quadrupeds."""
from pathlib import Path
import copy
import json
import os
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [os.environ.get("B4ML_PACKAGE", str(ROOT)), str(ROOT / "tests")]

import addon_utils
import bpy
from mathutils import Quaternion, Vector

import b4artists_ml
from b4artists_ml import quadruped_pose as pose
from b4artists_ml import ui
from b4artists_ml import workflow
from test_b4artists_ml_quadruped_pose import _generate


def matrix3_error(actual, expected):
    return max(abs(actual[row][column] - expected[row][column])
               for row in range(3) for column in range(3))


def enable_poles(obj):
    obj.b4ml.quadruped_use_poles = True
    _, _, limbs = pose.binding(obj)
    for row in limbs:
        obj.pose.bones[row["property_bone"]]["pole_vector"] = True


class QuadrupedPoseAssetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not b4artists_ml.is_bforartists():
            raise unittest.SkipTest("Bforartists required")
        addon_utils.enable("rigify", default_set=True, persistent=False)
        b4artists_ml.register()

    def tearDown(self):
        for obj in list(bpy.data.objects):
            if hasattr(obj, "b4ml") and obj.b4ml.quadruped_payload:
                scene = next(iter(obj.users_scene), bpy.context.scene)
                try:
                    pose.finish(obj, scene, False)
                except Exception:
                    pass

    def _author(self, profile="cat", use_poles=False, operator=False):
        scene, obj = _generate(profile)
        bpy.context.view_layer.objects.active = obj
        if use_poles:
            enable_poles(obj)
        pose.begin(obj, scene)
        state = obj.b4ml
        state.quadruped_spine_follow = 0.45
        state.quadruped_neck_share = 0.65
        paw = state.quadruped_targets["Fore Paw L"]
        paw.target.location += Vector((0.025, -0.012, 0.008))
        paw.use_orientation = True
        paw.target.rotation_quaternion.rotate(Quaternion((0.0, 1.0, 0.0), 0.025))
        if use_poles:
            state.quadruped_targets["Fore Pole L"].target.location += Vector((0.015, 0.008, -0.006))
        bpy.context.view_layer.update()
        pose.solve(obj, scene)
        if operator:
            self.assertEqual(bpy.ops.b4ml.quadruped_pose(operation="SAVE_POSE_ASSET"),
                             {"FINISHED"})
            asset = pose._read_pose_asset(scene)
        else:
            asset = pose.capture_pose_asset(obj, scene)
        text = scene[pose.POSE_ASSET_KEY]
        pose.finish(obj, scene, False)
        return text, asset

    def _assert_applied(self, obj, asset):
        record = json.loads(obj.b4ml.quadruped_payload)
        frame = pose._quadruped_asset_frame(record)
        scale = record["scale"]
        for row in asset["targets"]:
            label = row["label"]
            item = obj.b4ml.quadruped_targets[label]
            start = pose._saved_target_matrix(record, label)
            actual_delta = frame.transposed() @ (
                item.target.matrix_world.translation - start.translation) / scale
            self.assertLess((actual_delta - Vector(row["position_delta"])).length, 2e-6)
            if label not in pose.POLE_TARGETS:
                relative = (frame.transposed() @ item.target.matrix_world.to_3x3() @
                            start.to_3x3().transposed() @ frame)
                expected = Quaternion(row["orientation_delta"]).to_matrix()
                self.assertLess(matrix3_error(relative, expected), 2e-6)
                self.assertEqual(item.use_orientation, row["orientation_enabled"])

    def test_schema_three_asset_applies_across_cat_horse_and_wolf(self):
        text, asset = self._author("cat")
        self.assertEqual(asset["representation"],
                         "semantic_quadruped_target_delta_body_v1")
        self.assertFalse(asset["use_poles"])
        for profile in ("cat", "horse", "wolf"):
            with self.subTest(profile=profile):
                scene, obj = _generate(profile)
                scene[pose.POSE_ASSET_KEY] = text
                bpy.context.view_layer.objects.active = obj
                source_pose = workflow.raw_pose(obj)
                pose.begin(obj, scene)
                result = pose.apply_pose_asset(obj, scene)
                self.assertEqual(result["targets"], 6)
                self.assertEqual(result["cross_rig"], asset["source_profile"] != result["target_profile"])
                self.assertEqual(workflow.raw_pose(obj), source_pose)
                self.assertEqual(obj.b4ml.quadruped_spine_follow, asset["spine_follow"])
                self.assertEqual(obj.b4ml.quadruped_neck_share, asset["neck_share"])
                self.assertIsNone(json.loads(obj.b4ml.quadruped_payload)["signature"])
                self._assert_applied(obj, asset)
                pose.finish(obj, scene, False)

    def test_known_body_local_delta_has_independent_cross_profile_oracle(self):
        _text, asset = self._author("cat")
        asset = copy.deepcopy(asset)
        authored_delta = Vector((0.125, -0.0625, 0.03125))
        authored_rotation = Quaternion((0.0, 0.0, 1.0), 0.175)
        row = next(value for value in asset["targets"] if value["label"] == "Fore Paw L")
        row["position_delta"] = list(authored_delta)
        row["orientation_delta"] = list(authored_rotation)
        row["orientation_enabled"] = True

        scene, obj = _generate("horse")
        scene[pose.POSE_ASSET_KEY] = json.dumps(asset, allow_nan=False)
        bpy.context.view_layer.objects.active = obj
        pose.begin(obj, scene)
        record = json.loads(obj.b4ml.quadruped_payload)
        body_rotation = Quaternion(record["orientations"]["Body"]).normalized()
        start_location = Vector(record["origins"]["Fore Paw L"])
        start_rotation = Quaternion(record["orientations"]["Fore Paw L"]).normalized()
        expected_location = (start_location +
                             body_rotation @ authored_delta * float(record["scale"]))
        body_matrix = body_rotation.to_matrix()
        expected_rotation = (body_matrix @ authored_rotation.to_matrix() @
                             body_matrix.transposed() @
                             start_rotation.to_matrix()).to_quaternion().normalized()

        pose.apply_pose_asset(obj, scene)
        helper = obj.b4ml.quadruped_targets["Fore Paw L"].target
        self.assertLess((helper.matrix_world.translation - expected_location).length, 2e-6)
        self.assertLess(helper.matrix_world.to_quaternion().normalized().rotation_difference(
            expected_rotation).angle, 2e-6)
        self.assertTrue(obj.b4ml.quadruped_targets["Fore Paw L"].use_orientation)

    def test_schema_four_asset_transfers_position_only_poles(self):
        text, asset = self._author("cat", use_poles=True)
        self.assertTrue(asset["use_poles"])
        scene, obj = _generate("horse")
        enable_poles(obj)
        scene[pose.POSE_ASSET_KEY] = text
        bpy.context.view_layer.objects.active = obj
        source_pose = workflow.raw_pose(obj)
        pose.begin(obj, scene)
        result = pose.apply_pose_asset(obj, scene)
        self.assertEqual(result["targets"], 10)
        self.assertTrue(result["cross_rig"])
        self.assertEqual(workflow.raw_pose(obj), source_pose)
        self._assert_applied(obj, asset)

    def test_unsolved_invalid_and_pole_mismatch_fail_without_partial_changes(self):
        scene, obj = _generate("horse")
        bpy.context.view_layer.objects.active = obj
        pose.begin(obj, scene)
        with self.assertRaisesRegex(ValueError, "Solve the current quadruped targets"):
            pose.capture_pose_asset(obj, scene)
        pose.finish(obj, scene, False)
        text, asset = self._author("cat")
        scene, obj = _generate("wolf")
        bpy.context.view_layer.objects.active = obj
        pose.begin(obj, scene)
        snapshot = [(item.name, item.target.matrix_world.copy(), item.use_orientation)
                    for item in obj.b4ml.quadruped_targets]
        pose_before = workflow.raw_pose(obj)
        invalid = ["{", "x" * (pose.POSE_ASSET_MAX_CHARS + 1)]
        wrong = copy.deepcopy(asset)
        wrong["targets"][1]["position_delta"] = [float("nan"), 0.0, 0.0]
        invalid.append(json.dumps(wrong))
        wrong = copy.deepcopy(asset)
        wrong["targets"][1]["label"] = "Body"
        invalid.append(json.dumps(wrong))
        for value in invalid:
            scene[pose.POSE_ASSET_KEY] = value
            with self.assertRaises(ValueError):
                pose.apply_pose_asset(obj, scene)
            self.assertEqual(workflow.raw_pose(obj), pose_before)
            for item, saved in zip(obj.b4ml.quadruped_targets, snapshot):
                self.assertEqual(item.name, saved[0])
                self.assertLess(max(abs(item.target.matrix_world[r][c] - saved[1][r][c])
                                    for r in range(4) for c in range(4)), 1e-7)
                self.assertEqual(item.use_orientation, saved[2])
        pole_asset = copy.deepcopy(asset)
        pole_asset["use_poles"] = True
        scene[pose.POSE_ASSET_KEY] = json.dumps(pole_asset)
        with self.assertRaises(ValueError):
            pose.apply_pose_asset(obj, scene)
        scene[pose.POSE_ASSET_KEY] = text

        valid_payload = obj.b4ml.quadruped_payload
        valid_record = json.loads(valid_payload)
        for invalid_scale in (float("nan"), float("inf"), 0.0, -1.0, 1e308, True):
            with self.subTest(invalid_scale=invalid_scale):
                bad_record = copy.deepcopy(valid_record)
                bad_record["scale"] = invalid_scale
                bad_payload = json.dumps(bad_record, allow_nan=True)
                obj.b4ml.quadruped_payload = bad_payload
                with self.assertRaises(ValueError):
                    pose.apply_pose_asset(obj, scene)
                self.assertEqual(obj.b4ml.quadruped_payload, bad_payload)
                self.assertEqual(workflow.raw_pose(obj), pose_before)
                for item, saved in zip(obj.b4ml.quadruped_targets, snapshot):
                    self.assertIs(item.target, obj.b4ml.quadruped_targets[item.name].target)
                    self.assertLess(max(abs(item.target.matrix_world[r][c] - saved[1][r][c])
                                        for r in range(4) for c in range(4)), 1e-7)
        obj.b4ml.quadruped_payload = valid_payload

        previous_asset = scene[pose.POSE_ASSET_KEY]
        record = json.loads(obj.b4ml.quadruped_payload)
        body_frame = Quaternion(record["orientations"]["Body"]).normalized()
        offset = body_frame @ Vector((float(record["scale"]) * 8.25, 0.0, 0.0))
        for label in ("Body", "Fore Paw L", "Fore Paw R", "Hind Paw L", "Hind Paw R"):
            obj.b4ml.quadruped_targets[label].target.location += offset
        bpy.context.view_layer.update()
        pose.solve(obj, scene)
        with self.assertRaisesRegex(ValueError, "supported body-relative range"):
            pose.capture_pose_asset(obj, scene)
        self.assertEqual(scene[pose.POSE_ASSET_KEY], previous_asset)
        tampered = json.loads(obj.b4ml.quadruped_payload)
        tampered["scale"] = True
        obj.b4ml.quadruped_payload = json.dumps(tampered)
        with self.assertRaisesRegex(ValueError, "Invalid quadruped preview scale"):
            pose.capture_pose_asset(obj, scene)
        self.assertEqual(scene[pose.POSE_ASSET_KEY], previous_asset)

    def test_apply_solve_save_reload_keep_and_operator_contract(self):
        text, asset = self._author("cat", operator=True)
        # Use a pole-bearing asset for a pole-bearing destination.
        text, asset = self._author("horse", use_poles=True)
        scene, obj = _generate("wolf")
        obj.name = "Quadruped pose asset reload rig"
        enable_poles(obj)
        scene[pose.POSE_ASSET_KEY] = text
        bpy.context.view_layer.objects.active = obj
        source_pose = workflow.raw_pose(obj)
        pose.begin(obj, scene)
        self.assertEqual(bpy.ops.b4ml.quadruped_pose(operation="APPLY_POSE_ASSET"),
                         {"FINISHED"})
        pose.solve(obj, scene)
        path = ROOT / "training/b4artists_ml/cache/quadruped-pose-asset-v1.blend"
        bpy.ops.wm.save_as_mainfile(filepath=str(path))
        bpy.ops.wm.open_mainfile(filepath=str(path), use_scripts=False)
        scene = bpy.context.scene
        obj = bpy.data.objects["Quadruped pose asset reload rig"]
        bpy.context.view_layer.objects.active = obj
        self.assertEqual(scene[pose.POSE_ASSET_KEY], text)
        self._assert_applied(obj, asset)
        pose.finish(obj, scene, True)
        self.assertEqual(len(obj.b4ml.anchors), 1)
        self.assertEqual(workflow.raw_pose(obj), source_pose)
        self.assertIn("operation", ui.B4ML_OT_quadruped_pose.__annotations__)

    def test_post_write_collection_interference_rolls_back(self):
        text, _asset = self._author("cat")
        scene, obj = _generate("horse")
        scene[pose.POSE_ASSET_KEY] = text
        bpy.context.view_layer.objects.active = obj
        pose.begin(obj, scene)
        state = obj.b4ml
        before = [(item.name, item.target, item.target.matrix_world.copy(),
                   item.use_orientation) for item in state.quadruped_targets]
        payload = state.quadruped_payload
        rig_pose = workflow.raw_pose(obj)
        fired = {"value": False}

        def mutate(_scene, _depsgraph):
            if fired["value"]:
                return
            fired["value"] = True
            state.quadruped_targets.clear()

        bpy.app.handlers.depsgraph_update_post.append(mutate)
        try:
            with self.assertRaises(ValueError):
                pose.apply_pose_asset(obj, scene)
        finally:
            if mutate in bpy.app.handlers.depsgraph_update_post:
                bpy.app.handlers.depsgraph_update_post.remove(mutate)
        self.assertTrue(fired["value"])
        self.assertEqual(state.quadruped_payload, payload)
        self.assertEqual(workflow.raw_pose(obj), rig_pose)
        self.assertEqual(len(state.quadruped_targets), len(before))
        for item, saved in zip(state.quadruped_targets, before):
            self.assertEqual(item.name, saved[0])
            self.assertIs(item.target, saved[1])
            self.assertLess(max(abs(item.target.matrix_world[r][c] - saved[2][r][c])
                                for r in range(4) for c in range(4)), 1e-6)
            self.assertEqual(item.use_orientation, saved[3])

    def test_post_write_helper_and_setting_interference_rolls_back(self):
        text, _asset = self._author("cat")
        mutations = ("animation_data", "muted_constraint", "ordinary_lock", "spine_settings",
                     "asset_replace", "asset_delete")
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                scene, obj = _generate("horse")
                scene[pose.POSE_ASSET_KEY] = text
                bpy.context.view_layer.objects.active = obj
                pose.begin(obj, scene)
                state = obj.b4ml
                topology = pose._target_topology_snapshot(state)
                snapshots = {item.name: pose._helper_snapshot(item)
                             for item in state.quadruped_targets}
                payload = state.quadruped_payload
                rig_pose = workflow.raw_pose(obj)
                follow = state.quadruped_spine_follow
                neck = state.quadruped_neck_share
                fired = {"value": False}

                def mutate(_scene, _depsgraph):
                    if fired["value"]:
                        return
                    fired["value"] = True
                    helper = state.quadruped_targets["Body"].target
                    if mutation == "animation_data":
                        helper.animation_data_create()
                    elif mutation == "muted_constraint":
                        helper.constraints.new("COPY_LOCATION").mute = True
                    elif mutation == "ordinary_lock":
                        helper.lock_rotation[0] = not helper.lock_rotation[0]
                    elif mutation == "spine_settings":
                        state.quadruped_spine_follow = 0.01
                        state.quadruped_neck_share = 0.99
                    elif mutation == "asset_replace":
                        scene[pose.POSE_ASSET_KEY] = "{}"
                    else:
                        del scene[pose.POSE_ASSET_KEY]

                bpy.app.handlers.depsgraph_update_post.append(mutate)
                try:
                    with self.assertRaises(ValueError):
                        pose.apply_pose_asset(obj, scene)
                finally:
                    if mutate in bpy.app.handlers.depsgraph_update_post:
                        bpy.app.handlers.depsgraph_update_post.remove(mutate)
                self.assertTrue(fired["value"])
                self.assertEqual(state.quadruped_payload, payload)
                self.assertEqual(workflow.raw_pose(obj), rig_pose)
                self.assertEqual(state.quadruped_spine_follow, follow)
                self.assertEqual(state.quadruped_neck_share, neck)
                self.assertEqual(scene[pose.POSE_ASSET_KEY], text)
                self.assertTrue(pose._target_topology_matches(state, topology))
                for item in state.quadruped_targets:
                    saved = snapshots[item.name]
                    self.assertIs(item.target, saved["helper"])
                    self.assertLess(max(abs(item.target.matrix_world[row][column] -
                                            saved["matrix"][row][column])
                                        for row in range(4) for column in range(4)), 1e-6)
                    self.assertTrue(pose._helper_matches_asset_invariants(
                        item.target, saved))


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(QuadrupedPoseAssetTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    raise SystemExit(0 if result.wasSuccessful() else 1)
