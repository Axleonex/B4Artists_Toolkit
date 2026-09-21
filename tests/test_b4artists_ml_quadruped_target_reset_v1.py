"""Per-target preview-start reset coverage for generated Rigify quadrupeds."""
from pathlib import Path
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
from b4artists_ml import workflow as workflow
from test_b4artists_ml_quadruped_pose import _generate


RECORDS = []


def _matrix_error(actual, expected):
    return max(abs(actual[row][column] - expected[row][column])
               for row in range(4) for column in range(4))


class QuadrupedTargetResetTests(unittest.TestCase):
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

    def test_cat_horse_wolf_reset_all_helper_kinds_without_source_mutation(self):
        for profile_name, use_poles, labels in (
                ("cat", True, ("Body", "Fore Paw L", "Head", "Hind Pole R")),
                ("horse", False, ("Body", "Hind Paw R", "Head")),
                ("wolf", False, ("Body", "Fore Paw R", "Head"))):
            with self.subTest(profile=profile_name):
                scene, obj = _generate(profile_name)
                bpy.context.view_layer.objects.active = obj
                obj.b4ml.quadruped_use_poles = use_poles
                if use_poles:
                    _, _, limbs = pose.binding(obj)
                    for row in limbs:
                        obj.pose.bones[row["property_bone"]]["pole_vector"] = True
                pose.begin(obj, scene)
                bpy.context.view_layer.update()
                source_pose = workflow.raw_pose(obj)
                source_action = obj.animation_data.action if obj.animation_data else None
                for label in labels:
                    item = obj.b4ml.quadruped_targets[label]
                    start = item.target.matrix_world.copy()
                    enabled = item.enabled
                    orientation = item.use_orientation
                    other = {row.name: row.target.matrix_world.copy()
                             for row in obj.b4ml.quadruped_targets if row.name != label}
                    if label == "Head":
                        item.target.rotation_quaternion.rotate(Quaternion((0.0, 0.0, 1.0), 0.21))
                    elif label in pose.POLE_TARGETS:
                        item.target.location += Vector((0.07, -0.04, 0.03))
                    else:
                        item.target.location += Vector((0.08, -0.03, 0.02))
                        item.target.rotation_quaternion.rotate(Quaternion((0.0, 1.0, 0.0), 0.13))
                    bpy.context.view_layer.update()
                    result = pose.reset_target(obj, scene, label)
                    # Blender can renormalize a quaternion by one float ULP after update;
                    # runtime reset validation still enforces 1e-7 position/angle/scale.
                    self.assertLess(_matrix_error(item.target.matrix_world, start), 1e-6)
                    self.assertEqual(item.enabled, enabled)
                    self.assertEqual(item.use_orientation, orientation)
                    self.assertEqual(workflow.raw_pose(obj), source_pose)
                    self.assertIs((obj.animation_data.action if obj.animation_data else None), source_action)
                    for name, matrix in other.items():
                        self.assertLess(_matrix_error(obj.b4ml.quadruped_targets[name].target.matrix_world,
                                                      matrix), 1e-9)
                    self.assertTrue(result["source_unchanged"])
                RECORDS.append({"profile": profile_name, "labels": list(labels),
                                "source_unchanged": True, "toggles_preserved": True})
                pose.finish(obj, scene, False)

    def test_reset_after_solve_invalidates_keep_until_resolved(self):
        scene, obj = _generate("cat")
        bpy.context.view_layer.objects.active = obj
        pose.begin(obj, scene)
        bpy.context.view_layer.update()
        item = obj.b4ml.quadruped_targets["Fore Paw L"]
        item.target.location.x += 0.01
        pose.solve(obj, scene)
        solved_pose = workflow.raw_pose(obj)
        solved = json.loads(obj.b4ml.quadruped_payload)
        self.assertIsNotNone(solved["signature"])
        self.assertIsNotNone(solved["metrics"])
        pose.reset_target(obj, scene, "Fore Paw L")
        self.assertEqual(workflow.raw_pose(obj), solved_pose)
        reset = json.loads(obj.b4ml.quadruped_payload)
        self.assertIsNone(reset["signature"])
        self.assertIsNone(reset["metrics"])
        with self.assertRaisesRegex(ValueError, "Solve the current quadruped targets"):
            pose.finish(obj, scene, True)
        pose.solve(obj, scene)
        pose.finish(obj, scene, True)
        self.assertEqual(len(obj.b4ml.anchors), 1)

    def test_invalid_ownership_transform_and_metadata_fail_before_mutation(self):
        scene, obj = _generate("wolf")
        bpy.context.view_layer.objects.active = obj
        pose.begin(obj, scene)
        bpy.context.view_layer.update()
        item = obj.b4ml.quadruped_targets["Fore Paw R"]
        item.target.location.x += 0.04
        before = item.target.matrix_world.copy()
        source_pose = workflow.raw_pose(obj)

        parent = bpy.data.objects.new("Quadruped reset foreign parent", None)
        scene.collection.objects.link(parent)
        item.target.parent = parent
        with self.assertRaisesRegex(ValueError, "parenting"):
            pose.reset_target(obj, scene, "Fore Paw R")
        item.target.parent = None
        item.target.matrix_world = before
        item.target.scale = (1.0, 1.0, 1.0)

        item.target.delta_location.x = 0.1
        before = item.target.matrix_world.copy()
        with self.assertRaisesRegex(ValueError, "delta transforms"):
            pose.reset_target(obj, scene, "Fore Paw R")
        self.assertLess(_matrix_error(item.target.matrix_world, before), 1e-9)
        item.target.delta_location = (0.0, 0.0, 0.0)
        item.target.scale = (1.0, 1.0, 1.0)

        constraint = item.target.constraints.new("COPY_LOCATION")
        constraint.target = parent
        constraint.mute = True
        constraint.influence = 0.0
        with self.assertRaisesRegex(ValueError, "constraints"):
            pose.reset_target(obj, scene, "Fore Paw R")
        item.target.constraints.remove(constraint)

        item.target.keyframe_insert(data_path="location", frame=1)
        with self.assertRaisesRegex(ValueError, "animation or drivers"):
            pose.reset_target(obj, scene, "Fore Paw R")
        item.target.animation_data_clear()
        item.target.scale = (1.0, 1.0, 1.0)

        item.target.driver_add("location", 0)
        with self.assertRaisesRegex(ValueError, "animation or drivers"):
            pose.reset_target(obj, scene, "Fore Paw R")
        item.target.animation_data_clear()

        helper_action = bpy.data.actions.new("Quadruped reset helper NLA")
        helper_ad = item.target.animation_data_create()
        helper_track = helper_ad.nla_tracks.new()
        helper_track.mute = True
        helper_track.strips.new("Muted helper strip", 1, helper_action).mute = True
        with self.assertRaisesRegex(ValueError, "animation or drivers"):
            pose.reset_target(obj, scene, "Fore Paw R")
        item.target.animation_data_clear()

        item.target.rotation_mode = "XYZ"
        with self.assertRaisesRegex(ValueError, "rotation mode"):
            pose.reset_target(obj, scene, "Fore Paw R")
        item.target.rotation_mode = "QUATERNION"
        item.target.scale = (1.1, 1.0, 1.0)
        with self.assertRaisesRegex(ValueError, "scale must remain unchanged"):
            pose.reset_target(obj, scene, "Fore Paw R")
        item.target.scale = (1.0, 1.0, 1.0)

        record = json.loads(obj.b4ml.quadruped_payload)
        record["origins"]["Fore Paw R"] = [0.0, 1.0]
        obj.b4ml.quadruped_payload = json.dumps(record)
        before = item.target.matrix_world.copy()
        with self.assertRaisesRegex(ValueError, "Invalid saved quadruped target metadata"):
            pose.reset_target(obj, scene, "Fore Paw R")
        self.assertLess(_matrix_error(item.target.matrix_world, before), 1e-9)
        self.assertEqual(workflow.raw_pose(obj), source_pose)
        with self.assertRaisesRegex(ValueError, "Unknown quadruped target"):
            pose.reset_target(obj, scene, "Tail")
        bpy.data.objects.remove(parent, do_unlink=True)

    def test_legacy_schema_one_and_two_previews_reset_supported_targets(self):
        for schema, label in ((1, "Body"), (2, "Head")):
            with self.subTest(schema=schema):
                scene, obj = _generate("horse" if schema == 1 else "cat")
                bpy.context.view_layer.objects.active = obj
                pose.begin(obj, scene)
                state = obj.b4ml
                record = json.loads(state.quadruped_payload)
                record["schema"] = schema
                record.pop("spine_controls", None)
                if schema == 1:
                    head_index = state.quadruped_targets.find("Head")
                    head = state.quadruped_targets[head_index].target
                    state.quadruped_targets.remove(head_index)
                    bpy.data.objects.remove(head, do_unlink=True)
                    record["origins"].pop("Head", None)
                    record["orientations"].pop("Head", None)
                state.quadruped_payload = json.dumps(record, allow_nan=False)
                bpy.context.view_layer.update()
                item = state.quadruped_targets[label]
                start = item.target.matrix_world.copy()
                if label == "Head":
                    item.target.rotation_quaternion.rotate(Quaternion((0.0, 0.0, 1.0), 0.18))
                else:
                    item.target.location.x += 0.06
                pose.reset_target(obj, scene, label)
                self.assertLess(_matrix_error(item.target.matrix_world, start), 1e-7)
                self.assertEqual(json.loads(state.quadruped_payload)["schema"], schema)
                pose.finish(obj, scene, False)

    def test_replaced_helper_pointer_fails_without_touching_owned_helper_or_rig(self):
        scene, obj = _generate("wolf")
        bpy.context.view_layer.objects.active = obj
        pose.begin(obj, scene)
        bpy.context.view_layer.update()
        item = obj.b4ml.quadruped_targets["Hind Paw L"]
        owned = item.target
        owned.location.x += 0.05
        owned_before = owned.matrix_world.copy()
        rig_before = workflow.raw_pose(obj)
        foreign = bpy.data.objects.new("Foreign quadruped target", None)
        scene.collection.objects.link(foreign)
        foreign["b4ml_owner"] = obj
        foreign["b4ml_session"] = "foreign"
        item.target = foreign
        with self.assertRaisesRegex(ValueError, "missing or replaced"):
            pose.reset_target(obj, scene, "Hind Paw L")
        self.assertLess(_matrix_error(owned.matrix_world, owned_before), 1e-9)
        self.assertEqual(workflow.raw_pose(obj), rig_before)
        item.target = owned
        bpy.data.objects.remove(foreign, do_unlink=True)

    def test_post_write_handler_mutation_rolls_back_all_owned_state(self):
        scene, obj = _generate("cat")
        bpy.context.view_layer.objects.active = obj
        original_action = bpy.data.actions.new("Quadruped reset rollback source")
        workflow.assign_action(obj, original_action)
        pose.begin(obj, scene)
        bpy.context.view_layer.update()
        item = obj.b4ml.quadruped_targets["Body"]
        item.target.location.x += 0.08
        bpy.context.view_layer.update()
        helper_before = item.target.matrix_world.copy()
        pose_before = workflow.raw_pose(obj)
        payload_before = obj.b4ml.quadruped_payload
        status_before = obj.b4ml.status
        slot_before = workflow._slot(obj.animation_data)
        _, _, limbs = pose.binding(obj)
        modes_before = pose.mode_values(obj, limbs)
        torso = obj.pose.bones["torso"]
        torso_settings = (torso.rotation_mode, tuple(torso.lock_location),
                          tuple(torso.lock_rotation), tuple(torso.lock_scale),
                          torso.lock_rotation_w, torso.lock_rotations_4d)
        replacement = bpy.data.actions.new("Quadruped reset foreign action")
        fired = {"value": False}

        def mutate(_scene, _depsgraph):
            if fired["value"]:
                return
            fired["value"] = True
            torso.location.x += 0.25
            torso.rotation_mode = "XYZ" if torso.rotation_mode != "XYZ" else "QUATERNION"
            torso.lock_location = tuple(not value for value in torso.lock_location)
            torso.lock_rotation = tuple(not value for value in torso.lock_rotation)
            torso.lock_scale = tuple(not value for value in torso.lock_scale)
            torso.lock_rotation_w = not torso.lock_rotation_w
            torso.lock_rotations_4d = not torso.lock_rotations_4d
            row = limbs[0]
            obj.pose.bones[row["property_bone"]]["IK_FK"] = 1.0
            workflow.assign_action(obj, replacement)

        bpy.app.handlers.depsgraph_update_post.append(mutate)
        try:
            with self.assertRaisesRegex(ValueError, "source action changed"):
                pose.reset_target(obj, scene, "Body")
        finally:
            if mutate in bpy.app.handlers.depsgraph_update_post:
                bpy.app.handlers.depsgraph_update_post.remove(mutate)
        self.assertTrue(fired["value"])
        self.assertLess(_matrix_error(item.target.matrix_world, helper_before), 1e-7)
        self.assertEqual(workflow.raw_pose(obj), pose_before)
        self.assertIs(obj.animation_data.action, original_action)
        self.assertEqual(workflow._slot(obj.animation_data), slot_before)
        self.assertEqual(pose.mode_values(obj, limbs), modes_before)
        self.assertEqual((torso.rotation_mode, tuple(torso.lock_location),
                          tuple(torso.lock_rotation), tuple(torso.lock_scale),
                          torso.lock_rotation_w, torso.lock_rotations_4d), torso_settings)
        self.assertEqual(obj.b4ml.quadruped_payload, payload_before)
        self.assertEqual(obj.b4ml.status, status_before)

    def test_post_write_pointer_ownership_and_payload_mutation_roll_back(self):
        scene, obj = _generate("horse")
        bpy.context.view_layer.objects.active = obj
        obj.b4ml.quadruped_use_poles = True
        _, _, pole_limbs = pose.binding(obj)
        for row in pole_limbs:
            obj.pose.bones[row["property_bone"]]["pole_vector"] = True
        pose.begin(obj, scene)
        bpy.context.view_layer.update()
        state = obj.b4ml
        item = state.quadruped_targets["Fore Paw L"]
        helper = item.target
        helper.location.x += 0.08
        bpy.context.view_layer.update()
        matrix_before = helper.matrix_world.copy()
        payload_before = state.quadruped_payload
        status_before = state.status
        token_before = helper["b4ml_session"]
        foreign = bpy.data.objects.new("Concurrent foreign target", None)
        scene.collection.objects.link(foreign)
        foreign["b4ml_owner"] = obj
        foreign["b4ml_session"] = token_before
        fired = {"value": False}

        def mutate(_scene, _depsgraph):
            if fired["value"]:
                return
            fired["value"] = True
            item.target = foreign
            helper["b4ml_session"] = "concurrent mutation"
            state.quadruped_payload = "{}"

        bpy.app.handlers.depsgraph_update_post.append(mutate)
        try:
            with self.assertRaisesRegex(ValueError, "target changed while resetting"):
                pose.reset_target(obj, scene, "Fore Paw L")
        finally:
            if mutate in bpy.app.handlers.depsgraph_update_post:
                bpy.app.handlers.depsgraph_update_post.remove(mutate)
        self.assertTrue(fired["value"])
        self.assertIs(item.target, helper)
        self.assertEqual(helper["b4ml_session"], token_before)
        self.assertLess(_matrix_error(helper.matrix_world, matrix_before), 1e-7)
        self.assertEqual(state.quadruped_payload, payload_before)
        self.assertEqual(state.status, status_before)
        bpy.data.objects.remove(foreign, do_unlink=True)

        for label, lock_name, replacement, message in (
                ("Head", "lock_location", (False, False, False), "location must remain locked"),
                ("Fore Pole L", "lock_rotation", (False, False, False), "rotation must remain locked")):
            with self.subTest(label=label):
                current = state.quadruped_targets[label]
                target = current.target
                if label == "Head":
                    target.rotation_quaternion.rotate(Quaternion((0.0, 0.0, 1.0), 0.12))
                else:
                    target.location.x += 0.03
                bpy.context.view_layer.update()
                matrix_before = target.matrix_world.copy()
                locks_before = tuple(getattr(target, lock_name))
                fired = {"value": False}

                def mutate_lock(_scene, _depsgraph, target=target, lock_name=lock_name,
                                replacement=replacement, fired=fired):
                    if fired["value"]:
                        return
                    fired["value"] = True
                    setattr(target, lock_name, replacement)

                bpy.app.handlers.depsgraph_update_post.append(mutate_lock)
                try:
                    with self.assertRaisesRegex(ValueError, message):
                        pose.reset_target(obj, scene, label)
                finally:
                    if mutate_lock in bpy.app.handlers.depsgraph_update_post:
                        bpy.app.handlers.depsgraph_update_post.remove(mutate_lock)
                self.assertTrue(fired["value"])
                self.assertEqual(tuple(getattr(target, lock_name)), locks_before)
                self.assertLess(_matrix_error(target.matrix_world, matrix_before), 1e-6)

        body = state.quadruped_targets["Body"].target
        body.location.y += 0.03
        bpy.context.view_layer.update()
        matrix_before = body.matrix_world.copy()
        rotation_w_before = body.lock_rotation_w
        fired = {"value": False}

        def mutate_4d_lock(_scene, _depsgraph):
            if fired["value"]:
                return
            fired["value"] = True
            body.lock_rotation_w = not rotation_w_before

        bpy.app.handlers.depsgraph_update_post.append(mutate_4d_lock)
        try:
            with self.assertRaisesRegex(ValueError, "lock settings changed"):
                pose.reset_target(obj, scene, "Body")
        finally:
            if mutate_4d_lock in bpy.app.handlers.depsgraph_update_post:
                bpy.app.handlers.depsgraph_update_post.remove(mutate_4d_lock)
        self.assertTrue(fired["value"])
        self.assertEqual(body.lock_rotation_w, rotation_w_before)
        self.assertLess(_matrix_error(body.matrix_world, matrix_before), 1e-6)

    def test_save_reload_then_reset_preserves_source_and_payload(self):
        scene, obj = _generate("horse")
        bpy.context.view_layer.objects.active = obj
        obj.name = "Quadruped target reset reload rig"
        pose.begin(obj, scene)
        bpy.context.view_layer.update()
        item = obj.b4ml.quadruped_targets["Hind Paw R"]
        expected = item.target.matrix_world.copy()
        item.target.location += Vector((0.07, 0.02, -0.01))
        source_pose = workflow.raw_pose(obj)
        path = ROOT / "training/b4artists_ml/cache/quadruped-target-reset-v1.blend"
        bpy.ops.wm.save_as_mainfile(filepath=str(path))
        bpy.ops.wm.open_mainfile(filepath=str(path), use_scripts=False)
        obj = bpy.data.objects["Quadruped target reset reload rig"]
        bpy.context.view_layer.objects.active = obj
        item = obj.b4ml.quadruped_targets["Hind Paw R"]
        pose.reset_target(obj, bpy.context.scene, "Hind Paw R")
        self.assertLess(_matrix_error(item.target.matrix_world, expected), 1e-7)
        self.assertEqual(workflow.raw_pose(obj), source_pose)
        pose.finish(obj, bpy.context.scene, False)

    def test_operator_wires_named_reset_and_preserves_toggles(self):
        scene, obj = _generate("horse")
        bpy.context.view_layer.objects.active = obj
        pose.begin(obj, scene)
        bpy.context.view_layer.update()
        item = obj.b4ml.quadruped_targets["Body"]
        start = item.target.matrix_world.copy()
        item.enabled = False
        item.use_orientation = True
        item.target.location.y += 0.09
        result = bpy.ops.b4ml.quadruped_pose(operation="RESET_TARGET", target_name="Body")
        self.assertEqual(result, {"FINISHED"})
        self.assertLess(_matrix_error(item.target.matrix_world, start), 1e-7)
        self.assertFalse(item.enabled)
        self.assertTrue(item.use_orientation)
        self.assertIn("UNDO", ui.B4ML_OT_quadruped_pose.bl_options)


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(QuadrupedTargetResetTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    report = {
        "complete": result.wasSuccessful(),
        "full_goal_complete": False,
        "qualification": "Generated Rigify quadruped per-target preview-start reset",
        "host": bpy.app.version_string,
        "tests_run": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "records": RECORDS,
        "learned": False,
        "limits": "Generated Rigify cat, horse, and wolf active pose previews only.",
    }
    path = ROOT / "training/b4artists_ml/results" / os.environ.get(
        "B4ML_QUADRUPED_TARGET_RESET_RESULT", "quadruped-target-reset-v1.json")
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("QUADRUPED_TARGET_RESET_RESULT: " + json.dumps(report), flush=True)
    if not result.wasSuccessful():
        raise SystemExit(1)
