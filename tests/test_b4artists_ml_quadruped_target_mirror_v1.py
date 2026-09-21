"""Semantic left/right helper mirroring for generated Rigify quadrupeds."""
from pathlib import Path
from types import SimpleNamespace
import json
import os
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [os.environ.get("B4ML_PACKAGE", str(ROOT)), str(ROOT / "tests")]

import addon_utils
import bpy
from mathutils import Matrix, Quaternion, Vector

import b4artists_ml
from b4artists_ml import quadruped_pose as pose
from b4artists_ml import ui
from b4artists_ml import workflow
from test_b4artists_ml_quadruped_pose import _generate


def matrix_error(actual, expected):
    return max(abs(actual[row][column] - expected[row][column])
               for row in range(4) for column in range(4))


def matrix3_error(actual, expected):
    return max(abs(actual[row][column] - expected[row][column])
               for row in range(3) for column in range(3))


def independent_reflection(record):
    left = pose._saved_target_matrix(record, "Fore Paw L").translation
    right = pose._saved_target_matrix(record, "Fore Paw R").translation
    normal = (left - right).normalized()
    reflection = Matrix.Identity(3)
    for row in range(3):
        for column in range(3):
            reflection[row][column] -= 2.0 * normal[row] * normal[column]
    return reflection


def enable_poles(obj):
    obj.b4ml.quadruped_use_poles = True
    _, _, limbs = pose.binding(obj)
    for row in limbs:
        obj.pose.bones[row["property_bone"]]["pole_vector"] = True


class QuadrupedTargetMirrorTests(unittest.TestCase):
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

    def test_left_to_right_mirrors_paws_and_optional_poles_on_all_profiles(self):
        for profile_name, use_poles in (("cat", True), ("horse", False), ("wolf", False)):
            with self.subTest(profile=profile_name):
                scene, obj = _generate(profile_name)
                bpy.context.view_layer.objects.active = obj
                if use_poles:
                    enable_poles(obj)
                pose.begin(obj, scene)
                bpy.context.view_layer.update()
                record = json.loads(obj.b4ml.quadruped_payload)
                reflection = independent_reflection(record)
                implementation_reflection = pose._mirror_reflection(record)
                self.assertLess(matrix3_error(reflection, implementation_reflection), 5e-6)
                self.assertAlmostEqual(implementation_reflection.determinant(), -1.0, places=6)
                rig_pose = workflow.raw_pose(obj)
                source_action = obj.animation_data.action if obj.animation_data else None
                _, _, limbs = pose.binding(obj)
                modes = pose.mode_values(obj, limbs)
                pole_modes = pose.pole_mode_values(obj, limbs) if use_poles else None
                unchanged = {label: obj.b4ml.quadruped_targets[label].target.matrix_world.copy()
                             for label in ("Body", "Head")}
                expected = {}
                toggles = {}
                for left, right in pose.MIRROR_PAIRS:
                    source = obj.b4ml.quadruped_targets[left]
                    destination = obj.b4ml.quadruped_targets[right]
                    source.target.location += Vector((0.08, -0.03, 0.02))
                    source.target.rotation_quaternion.rotate(
                        Quaternion((0.0, 1.0, 0.0), 0.17))
                    destination.enabled = False
                    destination.use_orientation = True
                    toggles[right] = (destination.enabled, destination.use_orientation)
                    bpy.context.view_layer.update()
                    source_start = pose._saved_target_matrix(record, left)
                    destination_start = pose._saved_target_matrix(record, right)
                    source_delta = (source.target.matrix_world.to_3x3() @
                                    source_start.to_3x3().transposed())
                    expected[right] = {
                        "location": (destination_start.translation + reflection @
                                     (source.target.matrix_world.translation -
                                      source_start.translation)),
                        "rotation_delta": reflection @ source_delta @ reflection,
                        "start_rotation": destination_start.to_3x3(),
                    }
                    if use_poles:
                        left_pole = left.replace("Paw", "Pole")
                        right_pole = right.replace("Paw", "Pole")
                        pole_source = obj.b4ml.quadruped_targets[left_pole]
                        pole_destination = obj.b4ml.quadruped_targets[right_pole]
                        pole_source.target.location += Vector((0.04, 0.02, -0.03))
                        bpy.context.view_layer.update()
                        pole_source_start = pose._saved_target_matrix(record, left_pole)
                        pole_destination_start = pose._saved_target_matrix(record, right_pole)
                        expected[right_pole] = {
                            "location": (pole_destination_start.translation + reflection @
                                         (pole_source.target.matrix_world.translation -
                                          pole_source_start.translation)),
                            "rotation_delta": Matrix.Identity(3),
                            "start_rotation": pole_destination_start.to_3x3(),
                        }
                source_before = {left: obj.b4ml.quadruped_targets[left].target.matrix_world.copy()
                                 for left, _ in pose.MIRROR_PAIRS}
                result = pose.mirror_targets(obj, scene, "LEFT_TO_RIGHT")
                self.assertEqual(result["targets"], 4 if use_poles else 2)
                self.assertEqual(result["poles"], 2 if use_poles else 0)
                for label, wanted in expected.items():
                    actual = obj.b4ml.quadruped_targets[label].target.matrix_world
                    self.assertLess((actual.translation - wanted["location"]).length, 1e-6)
                    actual_delta = actual.to_3x3() @ wanted["start_rotation"].transposed()
                    self.assertLess(matrix3_error(actual_delta, wanted["rotation_delta"]), 1e-6)
                    self.assertLess(abs(actual.to_3x3().determinant() - 1.0), 2e-6)
                for label, before in source_before.items():
                    self.assertLess(matrix_error(
                        obj.b4ml.quadruped_targets[label].target.matrix_world, before), 1e-7)
                for label, before in unchanged.items():
                    self.assertLess(matrix_error(
                        obj.b4ml.quadruped_targets[label].target.matrix_world, before), 1e-7)
                for label, values in toggles.items():
                    item = obj.b4ml.quadruped_targets[label]
                    self.assertEqual((item.enabled, item.use_orientation), values)
                self.assertEqual(workflow.raw_pose(obj), rig_pose)
                self.assertIs(obj.animation_data.action if obj.animation_data else None, source_action)
                self.assertEqual(pose.mode_values(obj, limbs), modes)
                if use_poles:
                    self.assertEqual(pose.pole_mode_values(obj, limbs), pole_modes)
                pose.finish(obj, scene, False)

    def test_right_to_left_supports_legacy_schema_one_and_two(self):
        for schema in (1, 2):
            with self.subTest(schema=schema):
                scene, obj = _generate("horse")
                bpy.context.view_layer.objects.active = obj
                pose.begin(obj, scene)
                state = obj.b4ml
                record = json.loads(state.quadruped_payload)
                record["schema"] = schema
                record.pop("spine_controls", None)
                if schema == 1:
                    index = state.quadruped_targets.find("Head")
                    helper = state.quadruped_targets[index].target
                    state.quadruped_targets.remove(index)
                    bpy.data.objects.remove(helper, do_unlink=True)
                    record["origins"].pop("Head", None)
                    record["orientations"].pop("Head", None)
                state.quadruped_payload = json.dumps(record, allow_nan=False)
                for _, right in pose.MIRROR_PAIRS:
                    item = state.quadruped_targets[right]
                    item.target.location += Vector((-0.06, 0.02, 0.01))
                bpy.context.view_layer.update()
                reflection = independent_reflection(record)
                expected = {}
                for left, right in pose.MIRROR_PAIRS:
                    source_start = pose._saved_target_matrix(record, right)
                    destination_start = pose._saved_target_matrix(record, left)
                    expected[left] = (destination_start.translation + reflection @
                                      (state.quadruped_targets[right].target.matrix_world.translation -
                                       source_start.translation))
                result = pose.mirror_targets(obj, scene, "RIGHT_TO_LEFT")
                self.assertEqual(result["targets"], 2)
                self.assertEqual(json.loads(state.quadruped_payload)["schema"], schema)
                for label, location in expected.items():
                    self.assertLess((state.quadruped_targets[label].target.matrix_world.translation -
                                     location).length, 1e-6)
                pose.finish(obj, scene, False)

    def test_mirror_invalidates_solved_result_and_keep_until_resolved(self):
        scene, obj = _generate("wolf")
        bpy.context.view_layer.objects.active = obj
        pose.begin(obj, scene)
        obj.b4ml.quadruped_targets["Fore Paw L"].target.location.x += 0.01
        pose.solve(obj, scene)
        self.assertIsNotNone(json.loads(obj.b4ml.quadruped_payload)["signature"])
        pose.mirror_targets(obj, scene, "LEFT_TO_RIGHT")
        record = json.loads(obj.b4ml.quadruped_payload)
        self.assertIsNone(record["signature"])
        self.assertIsNone(record["metrics"])
        with self.assertRaisesRegex(ValueError, "Solve the current quadruped targets"):
            pose.finish(obj, scene, True)
        pose.solve(obj, scene)
        pose.finish(obj, scene, True)
        self.assertEqual(len(obj.b4ml.anchors), 1)

    def test_invalid_direction_helper_state_and_metadata_fail_atomically(self):
        scene, obj = _generate("cat")
        bpy.context.view_layer.objects.active = obj
        pose.begin(obj, scene)
        destination = obj.b4ml.quadruped_targets["Fore Paw R"].target
        before = destination.matrix_world.copy()
        rig_pose = workflow.raw_pose(obj)
        payload = obj.b4ml.quadruped_payload
        with self.assertRaisesRegex(ValueError, "Unknown quadruped mirror direction"):
            pose.mirror_targets(obj, scene, "SIDEWAYS")
        parent = bpy.data.objects.new("Quadruped mirror foreign parent", None)
        scene.collection.objects.link(parent)
        destination.parent = parent
        with self.assertRaisesRegex(ValueError, "parenting"):
            pose.mirror_targets(obj, scene, "LEFT_TO_RIGHT")
        destination.parent = None
        destination.matrix_world = before
        destination.scale = (1.0, 1.0, 1.0)
        destination.animation_data_create()
        with self.assertRaisesRegex(ValueError, "animation or drivers"):
            pose.mirror_targets(obj, scene, "LEFT_TO_RIGHT")
        destination.animation_data_clear()
        record = json.loads(payload)
        record["origins"]["Fore Paw L"] = [0.0, 1.0]
        obj.b4ml.quadruped_payload = json.dumps(record)
        with self.assertRaisesRegex(ValueError, "Invalid saved quadruped target metadata"):
            pose.mirror_targets(obj, scene, "LEFT_TO_RIGHT")
        self.assertLess(matrix_error(destination.matrix_world, before), 1e-7)
        self.assertEqual(workflow.raw_pose(obj), rig_pose)
        obj.b4ml.quadruped_payload = payload
        bpy.data.objects.remove(parent, do_unlink=True)

    def test_post_write_interference_rolls_back_all_helpers_and_rig_state(self):
        scene, obj = _generate("horse")
        bpy.context.view_layer.objects.active = obj
        pose.begin(obj, scene)
        state = obj.b4ml
        source = state.quadruped_targets["Fore Paw L"].target
        source.location.x += 0.07
        bpy.context.view_layer.update()
        matrices = {item.name: item.target.matrix_world.copy() for item in state.quadruped_targets}
        payload = state.quadruped_payload
        status = state.status
        rig_pose = workflow.raw_pose(obj)
        torso = obj.pose.bones["torso"]
        torso_mode = torso.rotation_mode
        foreign = bpy.data.objects.new("Concurrent quadruped mirror target", None)
        scene.collection.objects.link(foreign)
        item = state.quadruped_targets["Hind Paw R"]
        original = item.target
        fired = {"value": False}

        def mutate(_scene, _depsgraph):
            if fired["value"]:
                return
            fired["value"] = True
            item.target = foreign
            state.quadruped_payload = "{}"
            torso.rotation_mode = "XYZ" if torso_mode != "XYZ" else "QUATERNION"

        bpy.app.handlers.depsgraph_update_post.append(mutate)
        try:
            with self.assertRaisesRegex(ValueError, "metadata changed"):
                pose.mirror_targets(obj, scene, "LEFT_TO_RIGHT")
        finally:
            if mutate in bpy.app.handlers.depsgraph_update_post:
                bpy.app.handlers.depsgraph_update_post.remove(mutate)
        self.assertTrue(fired["value"])
        self.assertIs(item.target, original)
        for label, matrix in matrices.items():
            self.assertLess(matrix_error(state.quadruped_targets[label].target.matrix_world,
                                         matrix), 1e-6)
        self.assertEqual(workflow.raw_pose(obj), rig_pose)
        self.assertEqual(torso.rotation_mode, torso_mode)
        self.assertEqual(state.quadruped_payload, payload)
        self.assertEqual(state.status, status)
        bpy.data.objects.remove(foreign, do_unlink=True)

    def test_source_binding_interference_is_detected_and_rolled_back(self):
        for change_action in (False, True):
            with self.subTest(change_action=change_action):
                scene, obj = _generate("horse")
                bpy.context.view_layer.objects.active = obj
                pose.begin(obj, scene)
                state = obj.b4ml
                state.quadruped_targets["Fore Paw L"].target.location.x += 0.03
                bpy.context.view_layer.update()
                source_before = state.quadruped_source
                ad_before = obj.animation_data
                action_before = ad_before.action if ad_before else None
                slot_before = workflow._slot(ad_before) if ad_before else ""
                payload_before = state.quadruped_payload
                matrices = {item.name: item.target.matrix_world.copy()
                            for item in state.quadruped_targets}
                foreign = bpy.data.actions.new("Concurrent quadruped mirror source")
                fired = {"value": False}

                def mutate(_scene, _depsgraph):
                    if fired["value"]:
                        return
                    fired["value"] = True
                    if change_action:
                        obj.animation_data_create().action = foreign
                    state.quadruped_source = foreign

                bpy.app.handlers.depsgraph_update_post.append(mutate)
                try:
                    with self.assertRaisesRegex(ValueError, "source binding"):
                        pose.mirror_targets(obj, scene, "LEFT_TO_RIGHT")
                finally:
                    if mutate in bpy.app.handlers.depsgraph_update_post:
                        bpy.app.handlers.depsgraph_update_post.remove(mutate)
                self.assertTrue(fired["value"])
                self.assertIs(state.quadruped_source, source_before)
                current_ad = obj.animation_data
                self.assertIs(current_ad.action if current_ad else None, action_before)
                self.assertEqual(workflow._slot(current_ad) if current_ad else "", slot_before)
                self.assertEqual(state.quadruped_payload, payload_before)
                for label, matrix in matrices.items():
                    self.assertLess(matrix_error(
                        state.quadruped_targets[label].target.matrix_world, matrix), 1e-6)
                bpy.data.actions.remove(foreign)
                pose.finish(obj, scene, False)

    def test_collection_clear_interference_reconstructs_complete_topology(self):
        scene, obj = _generate("cat")
        bpy.context.view_layer.objects.active = obj
        enable_poles(obj)
        pose.begin(obj, scene)
        state = obj.b4ml
        state.quadruped_targets["Fore Paw L"].target.location.x += 0.03
        bpy.context.view_layer.update()
        topology = [(item.name, item.target, item.pole, item.enabled,
                     item.use_orientation, item.use_pole, item.pole_distance,
                     item.learn_bend, item.target.matrix_world.copy())
                    for item in state.quadruped_targets]
        payload_before = state.quadruped_payload
        fired = {"value": False}

        def mutate(_scene, _depsgraph):
            if fired["value"]:
                return
            fired["value"] = True
            state.quadruped_targets.clear()

        bpy.app.handlers.depsgraph_update_post.append(mutate)
        try:
            with self.assertRaises(ValueError) as caught:
                pose.mirror_targets(obj, scene, "LEFT_TO_RIGHT")
        finally:
            if mutate in bpy.app.handlers.depsgraph_update_post:
                bpy.app.handlers.depsgraph_update_post.remove(mutate)
        self.assertTrue(fired["value"], str(caught.exception))
        self.assertEqual(state.quadruped_payload, payload_before)
        self.assertEqual(len(state.quadruped_targets), len(topology))
        for item, saved in zip(state.quadruped_targets, topology):
            self.assertEqual(item.name, saved[0])
            self.assertIs(item.target, saved[1])
            self.assertIs(item.pole, saved[2])
            self.assertEqual((item.enabled, item.use_orientation, item.use_pole,
                              item.pole_distance, item.learn_bend), saved[3:8])
            self.assertLess(matrix_error(item.target.matrix_world, saved[8]), 1e-6)

    def test_save_reload_operator_and_ui_wiring(self):
        scene, obj = _generate("horse")
        bpy.context.view_layer.objects.active = obj
        obj.name = "Quadruped mirror reload rig"
        pose.begin(obj, scene)
        obj.b4ml.quadruped_targets["Hind Paw L"].target.location.y += 0.08
        path = ROOT / "training/b4artists_ml/cache/quadruped-target-mirror-v1.blend"
        bpy.ops.wm.save_as_mainfile(filepath=str(path))
        bpy.ops.wm.open_mainfile(filepath=str(path), use_scripts=False)
        obj = bpy.data.objects["Quadruped mirror reload rig"]
        bpy.context.view_layer.objects.active = obj
        result = bpy.ops.b4ml.quadruped_pose(
            operation="MIRROR_TARGETS", mirror_direction="LEFT_TO_RIGHT")
        self.assertEqual(result, {"FINISHED"})
        self.assertIn("UNDO", ui.B4ML_OT_quadruped_pose.bl_options)

        class FakeRow:
            def __init__(self):
                self.calls = []

            def operator(self, *args, **kwargs):
                operator = SimpleNamespace()
                self.calls.append((args, kwargs, operator))
                return operator

        row = FakeRow()
        left = ui._draw_quadruped_mirror(row, "LEFT_TO_RIGHT", "Mirror L to R")
        right = ui._draw_quadruped_mirror(row, "RIGHT_TO_LEFT", "Mirror R to L")
        self.assertEqual((left.operation, left.mirror_direction),
                         ("MIRROR_TARGETS", "LEFT_TO_RIGHT"))
        self.assertEqual((right.operation, right.mirror_direction),
                         ("MIRROR_TARGETS", "RIGHT_TO_LEFT"))


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(QuadrupedTargetMirrorTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    raise SystemExit(0 if result.wasSuccessful() else 1)
