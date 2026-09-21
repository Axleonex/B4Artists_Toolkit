"""Bforartists evidence for one-click Rigify quadruped pole matching."""
from pathlib import Path
import hashlib
import json
import os
import sys
import time
import traceback
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [os.environ.get("B4ML_PACKAGE", str(ROOT)), str(ROOT / "tests")]

import addon_utils
import bpy
from mathutils import Quaternion

import b4artists_ml
from b4artists_ml import quadruped_pose, workflow
from test_b4artists_ml_quadruped_pose import _action_signature, _generate


RECORDS = []


def _source(obj, scene):
    scene.frame_set(13)
    root = obj.pose.bones["root"]
    root.location = (0.006, -0.004, 0.002)
    root.keyframe_insert("location", frame=13)
    return workflow.raw_pose(obj), obj.animation_data.action, _action_signature(obj, obj.animation_data.action)


def _sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class QuadrupedPoleMatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not b4artists_ml.is_bforartists():
            raise unittest.SkipTest("Bforartists required")
        addon_utils.enable("rigify", default_set=True, persistent=False)
        b4artists_ml.register()

    def test_official_match_preserves_pose_action_and_autokey_for_all_profiles(self):
        for kind in ("cat", "horse", "wolf"):
            with self.subTest(profile=kind):
                scene, obj = _generate(kind, normalize_rotation_modes=False)
                profile, _, limbs = quadruped_pose.binding(obj)
                rows = quadruped_pose._pole_match_rows(profile, obj, limbs)
                native_modes = {name: obj.pose.bones[name].rotation_mode
                                for row in rows for name in [*row["ctrl_bones"], *row["extra_ctrls"]]}
                self.assertTrue(any(mode != "QUATERNION" for mode in native_modes.values()))
                if kind == "wolf":
                    obj.pose.bones[rows[0]["ctrl_bones"][0]].scale = (1.03, 0.98, 1.02)
                if kind == "horse":
                    end = obj.pose.bones[rows[0]["ctrl_bones"][-1]]
                    end.location.x += 0.01
                    end.keyframe_insert("location", frame=13)
                    toe = obj.pose.bones[rows[0]["extra_ctrls"][0]]
                    toe.rotation_euler.y += 0.03
                    toe.keyframe_insert("rotation_euler", frame=13)
                bpy.context.view_layer.update()
                source, action, action_signature = _source(obj, scene)
                scene.tool_settings.use_keyframe_insert_auto = True
                metrics = quadruped_pose.match_pole_vectors(obj, scene)
                self.assertEqual(metrics["matched"], 4)
                self.assertLessEqual(metrics["max_position_error"], metrics["tolerance"])
                self.assertLessEqual(metrics["max_rotation_error"], 0.001)
                self.assertLessEqual(metrics["max_linear_error"], metrics["linear_tolerance"])
                self.assertTrue(scene.tool_settings.use_keyframe_insert_auto)
                self.assertTrue(obj.b4ml.quadruped_use_poles)
                self.assertTrue(all(abs(value - 1.0) <= 1e-7 for value in
                                    quadruped_pose.pole_mode_values(obj).values()))
                self.assertIs(obj.animation_data.action, action)
                self.assertEqual(_action_signature(obj, action), action_signature)
                self.assertNotEqual(workflow.raw_pose(obj), source)
                RECORDS.append({"profile": kind, "native_rotation_modes": native_modes, **metrics})

    def test_mixed_modes_match_only_off_limbs_and_second_call_is_idempotent(self):
        scene, obj = _generate("wolf")
        _, _, limbs = quadruped_pose.binding(obj)
        obj.pose.bones[limbs[0]["property_bone"]]["pole_vector"] = True
        bpy.context.view_layer.update()
        first = quadruped_pose.match_pole_vectors(obj, scene)
        self.assertEqual(first["matched"], 3)
        pose = workflow.raw_pose(obj)
        second = quadruped_pose.match_pole_vectors(obj, scene)
        self.assertEqual(second["matched"], 0)
        self.assertEqual(workflow.raw_pose(obj), pose)

    def test_fractional_driven_and_animated_modes_fail_before_mutation(self):
        scene, obj = _generate("cat")
        _, _, limbs = quadruped_pose.binding(obj)
        bone = obj.pose.bones[limbs[0]["property_bone"]]
        del bone["pole_vector"]
        bone["pole_vector"] = 0.5
        before = workflow.raw_pose(obj)
        with self.assertRaisesRegex(ValueError, "exact Off or On"):
            quadruped_pose.match_pole_vectors(obj, scene)
        self.assertEqual(workflow.raw_pose(obj), before)
        bone["pole_vector"] = -5e-8
        near_endpoint = bone["pole_vector"]
        near_type = type(near_endpoint)
        with self.assertRaisesRegex(ValueError, "exact Off or On"):
            quadruped_pose.match_pole_vectors(obj, scene)
        self.assertEqual(bone["pole_vector"], near_endpoint)
        self.assertIs(type(bone["pole_vector"]), near_type)
        del bone["pole_vector"]
        bone["pole_vector"] = False
        driver = bone.driver_add('["pole_vector"]')
        driver.driver.expression = "0.0"
        with self.assertRaisesRegex(ValueError, "undriven Pole Vector"):
            quadruped_pose.match_pole_vectors(obj, scene)
        bone.driver_remove('["pole_vector"]')
        bone.keyframe_insert(data_path='["pole_vector"]', frame=1)
        with self.assertRaisesRegex(ValueError, "Animated Pole Vector"):
            quadruped_pose.match_pole_vectors(obj, scene)
        self.assertEqual(workflow.raw_pose(obj), before)

    def test_matching_enables_pole_preview_and_cancel_preserves_matched_source(self):
        scene, obj = _generate("horse", normalize_rotation_modes=False)
        quadruped_pose.match_pole_vectors(obj, scene)
        source, action, action_signature = _source(obj, scene)
        self.assertEqual(quadruped_pose.begin(obj, scene), 10)
        obj.b4ml.quadruped_targets["Fore Pole L"].target.location.y += 0.01
        bpy.context.view_layer.update()
        metrics = quadruped_pose.solve(obj, scene)
        self.assertLessEqual(metrics["max_pole_error"], metrics["tolerance"])
        quadruped_pose.finish(obj, scene, False)
        self.assertEqual(workflow.raw_pose(obj), source)
        self.assertTrue(all(abs(value - 1.0) <= 1e-7 for value in
                            quadruped_pose.pole_mode_values(obj).values()))
        self.assertIs(obj.animation_data.action, action)
        self.assertEqual(_action_signature(obj, action), action_signature)

    def test_animated_match_controls_reject_and_forced_postcheck_failure_rolls_back(self):
        scene, obj = _generate("wolf")
        profile, _, limbs = quadruped_pose.binding(obj)
        rows = quadruped_pose._pole_match_rows(profile, obj, limbs)
        animated = obj.pose.bones[rows[0]["ctrl_bones"][0]]
        animated.rotation_quaternion = Quaternion((0.0, 1.0, 0.0), 0.08)
        animated.keyframe_insert("rotation_quaternion", frame=1)
        before = workflow.raw_pose(obj)
        before_modes = quadruped_pose.pole_mode_values(obj)
        with self.assertRaisesRegex(ValueError, "range conversion"):
            quadruped_pose.match_pole_vectors(obj, scene)
        self.assertEqual(workflow.raw_pose(obj), before)
        self.assertEqual(quadruped_pose.pole_mode_values(obj), before_modes)

        scene, obj = _generate("horse")
        profile, _, limbs = quadruped_pose.binding(obj)
        rows = quadruped_pose._pole_match_rows(profile, obj, limbs)
        names = set(profile.controls) | {name for row in rows for name in
                                        [*row["ctrl_bones"], *row["extra_ctrls"]]}
        before = workflow.raw_pose(obj, names)
        before_modes = quadruped_pose.pole_mode_values(obj)
        middle = obj.data.bones[rows[0]["ctrl_bones"][2]]
        before_inheritance = (middle.use_inherit_rotation, middle.inherit_scale)
        def forced_failure(*_args, **_kwargs):
            middle.use_inherit_rotation = False
            middle.inherit_scale = "NONE"
            raise ValueError("forced postcheck failure")
        with mock.patch.object(quadruped_pose, "_require_pole_vectors",
                               side_effect=forced_failure):
            with self.assertRaisesRegex(ValueError, "forced postcheck"):
                quadruped_pose.match_pole_vectors(obj, scene)
        self.assertEqual(workflow.raw_pose(obj, names), before)
        self.assertEqual(quadruped_pose.pole_mode_values(obj), before_modes)
        self.assertEqual((middle.use_inherit_rotation, middle.inherit_scale), before_inheritance)

    def test_external_ownership_and_busy_workflows_reject_atomically(self):
        scene, obj = _generate("cat")
        profile, _, limbs = quadruped_pose.binding(obj)
        rows = quadruped_pose._pole_match_rows(profile, obj, limbs)
        pole = obj.pose.bones[rows[0]["ctrl_bones"][1]]
        before = workflow.raw_pose(obj)
        before_modes = quadruped_pose.pole_mode_values(obj)
        pole.lock_location[0] = True
        with self.assertRaisesRegex(ValueError, "control channels changed"):
            quadruped_pose.match_pole_vectors(obj, scene)
        pole.lock_location[0] = False
        constraint = pole.constraints.new("COPY_LOCATION")
        with self.assertRaisesRegex(ValueError, "constrained control"):
            quadruped_pose.match_pole_vectors(obj, scene)
        pole.constraints.remove(constraint)
        driver = pole.driver_add("location", 0)
        driver.driver.expression = "0.0"
        with self.assertRaisesRegex(ValueError, "driven controls"):
            quadruped_pose.match_pole_vectors(obj, scene)
        pole.driver_remove("location", 0)
        mode_bone = obj.pose.bones[limbs[0]["property_bone"]]
        mode_driver = mode_bone.driver_add('["IK_FK"]')
        mode_driver.driver.expression = "0.0"
        with self.assertRaisesRegex(ValueError, "undriven IK/FK"):
            quadruped_pose.match_pole_vectors(obj, scene)
        mode_bone.driver_remove('["IK_FK"]')
        obj.b4ml.temporal_running = True
        with self.assertRaisesRegex(ValueError, "active preview"):
            quadruped_pose.match_pole_vectors(obj, scene)
        obj.b4ml.temporal_running = False
        with mock.patch.object(quadruped_pose.w.motion_layer, "find", return_value=object()):
            with self.assertRaisesRegex(ValueError, "active preview"):
                quadruped_pose.match_pole_vectors(obj, scene)
        self.assertEqual(workflow.raw_pose(obj), before)
        self.assertEqual(quadruped_pose.pole_mode_values(obj), before_modes)

    def test_matched_state_survives_save_reload_without_action_edits(self):
        scene, obj = _generate("horse")
        _, action, action_signature = _source(obj, scene)
        action_name = action.name
        quadruped_pose.match_pole_vectors(obj, scene)
        name = obj.name
        path = ROOT / "training/b4artists_ml/cache/quadruped-pole-match-v1.blend"
        bpy.ops.wm.save_as_mainfile(filepath=str(path))
        bpy.ops.wm.open_mainfile(filepath=str(path), use_scripts=False)
        obj = bpy.data.objects[name]
        bpy.context.view_layer.objects.active = obj
        self.assertTrue(obj.b4ml.quadruped_use_poles)
        self.assertTrue(all(value == 1.0 for value in quadruped_pose.pole_mode_values(obj).values()))
        self.assertEqual(obj.animation_data.action.name, action_name)
        self.assertEqual(_action_signature(obj, obj.animation_data.action), action_signature)

    def test_ui_operator_runs_in_object_mode_and_declares_native_undo(self):
        scene, obj = _generate("cat")
        self.assertEqual(obj.mode, "OBJECT")
        self.assertIn("UNDO", b4artists_ml.ui.B4ML_OT_quadruped_pose.bl_options)
        self.assertEqual(bpy.ops.b4ml.quadruped_pose(operation="MATCH_POLES"), {"FINISHED"})
        self.assertTrue(all(value == 1.0 for value in quadruped_pose.pole_mode_values(obj).values()))


def run():
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(QuadrupedPoleMatchTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    report = {"schema": 1, "qualification": "Quadruped Pole Matching v1",
              "passed": result.wasSuccessful(), "tests": result.testsRun,
              "failures": len(result.failures), "errors": len(result.errors),
              "records": RECORDS}
    path = ROOT / "training/b4artists_ml/results/quadruped-pole-match-v1.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("B4ML_RESULT:", "PASS" if result.wasSuccessful() else "FAIL")
    print("B4ML_REPORT:", path)
    return result.wasSuccessful()


def run_ui_smoke():
    QuadrupedPoleMatchTests.setUpClass()
    scene, obj = _generate("cat", normalize_rotation_modes=False)
    profile, _, limbs = quadruped_pose.binding(obj)
    rows = quadruped_pose._pole_match_rows(profile, obj, limbs)
    written = {name for row in rows for name in
               [row["ctrl_bones"][0], row["ctrl_bones"][1], *row["ctrl_bones"][2:-1]]}
    _, action, action_signature = _source(obj, scene)
    scene.tool_settings.use_keyframe_insert_auto = True
    obj.b4ml.quadruped_use_poles = True
    state = {"name": obj.name, "action": action.name, "phase": "capture_button",
             "started": time.monotonic(), "events": []}

    def finish(report):
        output = ROOT / "docs/b4artists_ml/quadruped-pole-match-ui-v1.json"
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print("QUADRUPED_POLE_MATCH_UI_RESULT: " + json.dumps(report), flush=True)
        bpy.ops.wm.quit_blender()
        return None

    def tick():
        try:
            if time.monotonic() - state["started"] > 45:
                raise AssertionError("Quadruped Pole Match UI timed out")
            window = bpy.context.window_manager.windows[0]
            area = next(value for value in window.screen.areas if value.type == "VIEW_3D")
            region = next(value for value in area.regions if value.type == "WINDOW")
            sidebar = next(value for value in area.regions if value.type == "UI")
            area.spaces.active.show_region_ui = True
            if hasattr(sidebar, "active_panel_category"):
                sidebar.active_panel_category = "B4Artists ML"
            obj = bpy.data.objects[state["name"]]
            window.view_layer.objects.active = obj
            obj.select_set(True)
            override = dict(window=window, area=area, region=region, object=obj,
                            active_object=obj, selected_objects=[obj],
                            selected_editable_objects=[obj])
            with bpy.context.temp_override(**override):
                if state["phase"] == "capture_button":
                    path = ROOT / "training/b4artists_ml/cache/quadruped-pole-match-ui-v1.png"
                    bpy.ops.screen.screenshot(filepath=str(path))
                    state["screenshot"] = path
                    state["phase"] = "match"
                    return 0.4
                if state["phase"] == "match":
                    window.event_simulate(type="ESC", value="PRESS")
                    state["before_pose"] = workflow.raw_pose(obj, written)
                    bpy.ops.ed.undo_push(message="Quadruped pole match baseline")
                    assert bpy.ops.b4ml.quadruped_pose(operation="MATCH_POLES") == {"FINISHED"}
                    assert all(value == 1.0 for value in quadruped_pose.pole_mode_values(obj).values())
                    assert window.scene.tool_settings.use_keyframe_insert_auto
                    assert obj.animation_data.action.name == state["action"]
                    assert _action_signature(obj, obj.animation_data.action) == action_signature
                    state["matched_pose"] = workflow.raw_pose(obj, written)
                    assert state["matched_pose"] != state["before_pose"]
                    bpy.ops.ed.undo_push(message="Quadruped pole matching complete")
                    state["events"].append("Matched and enabled four poles through the visible operator")
                    state["phase"] = "undo"
                    return 0.4
                if state["phase"] == "undo":
                    assert bpy.ops.ed.undo() == {"FINISHED"}
                    state["phase"] = "verify_undo"
                    return 0.4
                if state["phase"] == "verify_undo":
                    obj = bpy.data.objects[state["name"]]
                    assert all(value == 0.0 for value in quadruped_pose.pole_mode_values(obj).values())
                    assert workflow.raw_pose(obj, written) == state["before_pose"]
                    assert window.scene.tool_settings.use_keyframe_insert_auto
                    assert obj.animation_data.action.name == state["action"]
                    assert _action_signature(obj, obj.animation_data.action) == action_signature
                    state["events"].append("Native Undo restored all four pole modes")
                    assert bpy.ops.ed.redo() == {"FINISHED"}
                    state["phase"] = "verify_redo"
                    return 0.5
                obj = bpy.data.objects[state["name"]]
                assert all(value == 1.0 for value in quadruped_pose.pole_mode_values(obj).values())
                assert workflow.raw_pose(obj, written) == state["matched_pose"]
                assert window.scene.tool_settings.use_keyframe_insert_auto
                assert obj.animation_data.action.name == state["action"]
                assert _action_signature(obj, obj.animation_data.action) == action_signature
                state["events"].append("Native Redo restored the matched pole state")
                path = state["screenshot"]
                return finish({
                    "passed": True,
                    "fixture": "generated Rigify cat",
                    "events": state["events"],
                    "action_unchanged": True,
                    "auto_key_preserved": True,
                    "screenshot": str(path.relative_to(ROOT)),
                    "screenshot_sha256": _sha(path),
                    "elapsed_seconds": time.monotonic() - state["started"],
                })
        except Exception as exc:
            return finish({"passed": False, "phase": state["phase"], "error": str(exc),
                           "traceback": traceback.format_exc(), "events": state["events"]})

    bpy.app.timers.register(tick, first_interval=0.5)


if __name__ == "__main__" and "--ui-smoke" in sys.argv:
    run_ui_smoke()
elif __name__ == "__main__":
    try:
        ok = run()
    except BaseException:
        traceback.print_exc()
        ok = False
    if not ok:
        raise SystemExit(1)
