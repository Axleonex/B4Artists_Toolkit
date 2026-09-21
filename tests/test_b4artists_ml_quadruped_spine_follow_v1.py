"""Bforartists evidence for semantic quadruped Head-to-Spine follow."""
from pathlib import Path
import hashlib
import json
import math
import os
import sys
import time
import traceback
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [os.environ.get("B4ML_PACKAGE", str(ROOT)), str(ROOT / "tests")]

import addon_utils
import bpy
from mathutils import Quaternion, Vector

import b4artists_ml
from b4artists_ml import quadruped_pose, ui, workflow
from test_b4artists_ml_quadruped_pose import _action_signature, _generate


RECORDS = []


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _source(obj, scene):
    scene.frame_set(9)
    root = obj.pose.bones["root"]
    root.location = (0.009, -0.004, 0.006)
    root.keyframe_insert("location", frame=9)
    action = obj.animation_data.action
    return workflow.raw_pose(obj), action, _action_signature(obj, action)


def _turn_head(obj, angle=0.22):
    target = obj.b4ml.quadruped_targets["Head"].target
    target.rotation_quaternion = (
        Quaternion(Vector((0.3, 0.6, 0.4)).normalized(), angle) @
        target.rotation_quaternion
    ).normalized()
    bpy.context.view_layer.update()
    return target.rotation_quaternion.copy()


class QuadrupedSpineFollowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not b4artists_ml.is_bforartists():
            raise unittest.SkipTest("Bforartists required")
        addon_utils.enable("rigify", default_set=True, persistent=False)
        b4artists_ml.register()

    def test_cat_horse_wolf_follow_is_exact_and_preserves_body_and_paws(self):
        for kind in ("cat", "horse", "wolf"):
            with self.subTest(profile=kind):
                scene, obj = _generate(kind)
                source, action, action_signature = _source(obj, scene)
                obj.b4ml.quadruped_spine_follow = 0.6
                obj.b4ml.quadruped_neck_share = 0.75
                quadruped_pose.begin(obj, scene)
                record = json.loads(obj.b4ml.quadruped_payload)
                self.assertEqual(record["schema"], 3)
                profile, _, _ = quadruped_pose.binding(obj)
                self.assertEqual(record["spine_controls"], {
                    "chest": profile.roles["chest"],
                    "neck": profile.roles["neck"],
                })
                requested = _turn_head(obj)
                metrics = quadruped_pose.solve(obj, scene)
                distribution = metrics["spine_distribution"]
                self.assertTrue(distribution["active"])
                self.assertAlmostEqual(distribution["follow"], 0.6, places=6)
                self.assertAlmostEqual(distribution["neck_share"], 0.75, places=6)
                self.assertAlmostEqual(distribution["weights"]["chest"], 0.15, places=6)
                self.assertAlmostEqual(distribution["weights"]["neck"], 0.45, places=6)
                self.assertGreater(distribution["head_delta_radians"], 0.2)
                self.assertLessEqual(max(distribution["orientation_errors"].values()),
                                     metrics["orientation_tolerance"])
                self.assertLessEqual(metrics["orientation_errors"]["Head"],
                                     metrics["orientation_tolerance"])
                self.assertLessEqual(metrics["max_paw_error"], metrics["tolerance"])
                self.assertLessEqual(metrics["body_error"], metrics["tolerance"])
                current = workflow.raw_pose(obj)
                self.assertNotEqual(current[profile.roles["chest"]],
                                    source[profile.roles["chest"]])
                self.assertNotEqual(current[profile.roles["neck"]],
                                    source[profile.roles["neck"]])
                actual = (obj.matrix_world @ obj.pose.bones[profile.roles["head"]].matrix).to_quaternion()
                self.assertLessEqual(actual.rotation_difference(requested).angle,
                                     metrics["orientation_tolerance"])
                quadruped_pose.finish(obj, scene, False)
                self.assertEqual(workflow.raw_pose(obj), source)
                self.assertIs(obj.animation_data.action, action)
                self.assertEqual(_action_signature(obj, action), action_signature)
                RECORDS.append({"profile": kind, "head_error": metrics["orientation_errors"]["Head"],
                                "spine_errors": distribution["orientation_errors"],
                                "paw_error": metrics["max_paw_error"]})

    def test_panel_payload_normalization_rejects_non_objects(self):
        self.assertEqual(ui._json_object("[]"), {})
        self.assertEqual(ui._json_object("null"), {})
        self.assertEqual(ui._json_object("not json"), {})
        self.assertEqual(ui._json_object('{"schema": 3}'), {"schema": 3})

    def test_zero_follow_preserves_direct_head_workflow_and_locked_spine(self):
        scene, obj = _generate("cat")
        source, action, action_signature = _source(obj, scene)
        profile, _, _ = quadruped_pose.binding(obj)
        chest = obj.pose.bones[profile.roles["chest"]]
        neck = obj.pose.bones[profile.roles["neck"]]
        chest.lock_rotation[0] = True
        neck.lock_rotation[2] = True
        source = workflow.raw_pose(obj)
        obj.b4ml.quadruped_spine_follow = 0.0
        quadruped_pose.begin(obj, scene)
        requested = _turn_head(obj, 0.12)
        metrics = quadruped_pose.solve(obj, scene)
        self.assertFalse(metrics["spine_distribution"]["active"])
        self.assertEqual(metrics["spine_distribution"]["orientation_errors"], {})
        actual = (obj.matrix_world @ obj.pose.bones[profile.roles["head"]].matrix).to_quaternion()
        self.assertLessEqual(actual.rotation_difference(requested).angle,
                             metrics["orientation_tolerance"])
        quadruped_pose.finish(obj, scene, False)
        self.assertEqual(workflow.raw_pose(obj), source)
        self.assertIs(obj.animation_data.action, action)
        self.assertEqual(_action_signature(obj, action), action_signature)

    def test_distribution_controls_reject_external_ownership_atomically(self):
        scene, obj = _generate("horse")
        source, action, action_signature = _source(obj, scene)
        profile, _, _ = quadruped_pose.binding(obj)
        chest = obj.pose.bones[profile.roles["chest"]]
        neck = obj.pose.bones[profile.roles["neck"]]
        obj.b4ml.quadruped_spine_follow = 0.5
        objects = set(bpy.data.objects)
        chest.lock_rotation[0] = True
        locked_source = workflow.raw_pose(obj)
        with self.assertRaisesRegex(ValueError, "unlocked rotation"):
            quadruped_pose.begin(obj, scene)
        self.assertFalse(obj.b4ml.quadruped_payload)
        self.assertEqual(set(bpy.data.objects), objects)
        self.assertEqual(workflow.raw_pose(obj), locked_source)
        chest.lock_rotation[0] = False

        quadruped_pose.begin(obj, scene)
        _turn_head(obj)
        neck.lock_rotation[1] = True
        preview = workflow.raw_pose(obj)
        with self.assertRaisesRegex(ValueError, "unlocked rotation"):
            quadruped_pose.solve(obj, scene)
        self.assertEqual(workflow.raw_pose(obj), preview)
        neck.lock_rotation[1] = False
        constraint = chest.constraints.new("COPY_ROTATION")
        preview = workflow.raw_pose(obj)
        with self.assertRaisesRegex(ValueError, "constrained control"):
            quadruped_pose.solve(obj, scene)
        self.assertEqual(workflow.raw_pose(obj), preview)
        chest.constraints.remove(constraint)
        driver = neck.driver_add("rotation_quaternion", 0)
        driver.driver.expression = "0.0"
        bpy.context.view_layer.update()
        preview = workflow.raw_pose(obj)
        with self.assertRaisesRegex(ValueError, "driven control"):
            quadruped_pose.solve(obj, scene)
        self.assertEqual(workflow.raw_pose(obj), preview)
        neck.driver_remove("rotation_quaternion", 0)
        quadruped_pose.finish(obj, scene, False)
        self.assertEqual(workflow.raw_pose(obj), source)
        self.assertIs(obj.animation_data.action, action)
        self.assertEqual(_action_signature(obj, action), action_signature)

    def test_zero_and_one_neck_share_require_only_the_written_control(self):
        for kind, share, locked_role, written_role in (
                ("cat", 0.0, "neck", "chest"),
                ("wolf", 1.0, "chest", "neck")):
            with self.subTest(profile=kind, neck_share=share):
                scene, obj = _generate(kind)
                source, action, action_signature = _source(obj, scene)
                profile, _, _ = quadruped_pose.binding(obj)
                obj.b4ml.quadruped_spine_follow = 0.5
                obj.b4ml.quadruped_neck_share = share
                locked = obj.pose.bones[profile.roles[locked_role]]
                locked.lock_rotation[0] = True
                source = workflow.raw_pose(obj)
                quadruped_pose.begin(obj, scene)
                _turn_head(obj, 0.11)
                metrics = quadruped_pose.solve(obj, scene)
                distribution = metrics["spine_distribution"]
                self.assertTrue(distribution["active"])
                self.assertEqual(distribution["weights"][locked_role], 0.0)
                self.assertAlmostEqual(distribution["weights"][written_role], 0.5, places=6)
                self.assertLessEqual(distribution["orientation_errors"][written_role],
                                     metrics["orientation_tolerance"])
                quadruped_pose.finish(obj, scene, False)
                self.assertEqual(workflow.raw_pose(obj), source)
                self.assertIs(obj.animation_data.action, action)
                self.assertEqual(_action_signature(obj, action), action_signature)

    def test_setting_change_requires_resolve_and_updates_allocation(self):
        scene, obj = _generate("wolf")
        source, action, action_signature = _source(obj, scene)
        obj.b4ml.quadruped_spine_follow = 0.6
        obj.b4ml.quadruped_neck_share = 0.2
        quadruped_pose.begin(obj, scene)
        _turn_head(obj, 0.16)
        first = quadruped_pose.solve(obj, scene)
        self.assertAlmostEqual(first["spine_distribution"]["weights"]["chest"], 0.48, places=6)
        self.assertAlmostEqual(first["spine_distribution"]["weights"]["neck"], 0.12, places=6)
        before = workflow.raw_pose(obj)
        obj.b4ml.quadruped_neck_share = 0.8
        with self.assertRaisesRegex(ValueError, "Solve the current quadruped targets"):
            quadruped_pose.finish(obj, scene, True)
        self.assertEqual(workflow.raw_pose(obj), before)
        second = quadruped_pose.solve(obj, scene)
        self.assertAlmostEqual(second["spine_distribution"]["weights"]["chest"], 0.12, places=6)
        self.assertAlmostEqual(second["spine_distribution"]["weights"]["neck"], 0.48, places=6)
        quadruped_pose.finish(obj, scene, True)
        self.assertEqual(len(obj.b4ml.anchors), 1)
        self.assertEqual(workflow.raw_pose(obj), source)
        self.assertIs(obj.animation_data.action, action)
        self.assertEqual(_action_signature(obj, action), action_signature)

    def test_schema_two_preview_recovers_without_distribution(self):
        scene, obj = _generate("cat")
        source, action, action_signature = _source(obj, scene)
        obj.b4ml.quadruped_spine_follow = 1.0
        quadruped_pose.begin(obj, scene)
        record = json.loads(obj.b4ml.quadruped_payload)
        record["schema"] = 2
        record.pop("spine_controls")
        obj.b4ml.quadruped_payload = json.dumps(record, allow_nan=False)
        _turn_head(obj, 0.1)
        metrics = quadruped_pose.solve(obj, scene)
        self.assertFalse(metrics["spine_distribution"]["active"])
        self.assertEqual(metrics["spine_distribution"]["follow"], 0.0)
        self.assertIn("Head", metrics["orientation_errors"])
        quadruped_pose.finish(obj, scene, False)
        self.assertEqual(workflow.raw_pose(obj), source)
        self.assertIs(obj.animation_data.action, action)
        self.assertEqual(_action_signature(obj, action), action_signature)

    def test_schema_three_spine_settings_survive_reload_and_keep(self):
        scene, obj = _generate("horse")
        source, action, action_signature = _source(obj, scene)
        action_name = action.name
        obj.b4ml.quadruped_spine_follow = 0.73
        obj.b4ml.quadruped_neck_share = 0.61
        quadruped_pose.begin(obj, scene)
        _turn_head(obj, 0.14)
        metrics = quadruped_pose.solve(obj, scene)
        self.assertTrue(metrics["spine_distribution"]["active"])
        name = obj.name
        path = ROOT / "training/b4artists_ml/cache/quadruped-spine-follow-v1.blend"
        bpy.ops.wm.save_as_mainfile(filepath=str(path))
        bpy.ops.wm.open_mainfile(filepath=str(path), use_scripts=False)
        obj = bpy.data.objects[name]
        scene = bpy.context.scene
        bpy.context.view_layer.objects.active = obj
        self.assertEqual(json.loads(obj.b4ml.quadruped_payload)["schema"], 3)
        self.assertAlmostEqual(obj.b4ml.quadruped_spine_follow, 0.73, places=6)
        self.assertAlmostEqual(obj.b4ml.quadruped_neck_share, 0.61, places=6)
        quadruped_pose.finish(obj, scene, True)
        self.assertEqual(len(obj.b4ml.anchors), 1)
        self.assertEqual(workflow.raw_pose(obj), source)
        self.assertEqual(obj.animation_data.action.name, action_name)
        self.assertEqual(_action_signature(obj, obj.animation_data.action), action_signature)
        RECORDS.append({"workflow": "spine_follow_save_reload_keep", "passed": True})


def run():
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(QuadrupedSpineFollowTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    report = {
        "tests": result.testsRun,
        "passed": result.wasSuccessful(),
        "failures": len(result.failures),
        "errors": len(result.errors),
        "skips": len(result.skipped),
        "records": RECORDS,
        "host": bpy.app.version_string,
        "package": b4artists_ml.__file__,
        "runtime_sha256": {
            "quadruped_pose": _sha(quadruped_pose.__file__),
            "ui": _sha(ROOT / "b4artists_ml/ui.py"),
            "test": _sha(__file__),
        },
        "learned": False,
        "outbound_calls": 0,
        "full_goal_complete": False,
    }
    output = ROOT / "training/b4artists_ml/results/quadruped-spine-follow-v1.json"
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("QUADRUPED_SPINE_FOLLOW_RESULT: " + json.dumps(report), flush=True)
    if not result.wasSuccessful():
        raise SystemExit(1)


def run_ui_smoke():
    QuadrupedSpineFollowTests.setUpClass()
    scene, obj = _generate("wolf")
    _source(obj, scene)
    obj.b4ml.quadruped_spine_follow = 0.64
    obj.b4ml.quadruped_neck_share = 0.72
    state = {"name": obj.name, "phase": "operate", "started": time.monotonic(),
             "scrolls": 0, "events": []}

    def tick():
        try:
            if time.monotonic() - state["started"] > 45:
                raise AssertionError("Quadruped Spine Follow UI timed out")
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
                if state["phase"] == "operate":
                    window.event_simulate(type="ESC", value="PRESS")
                    assert bpy.ops.b4ml.quadruped_pose(operation="BEGIN") == {"FINISHED"}
                    _turn_head(obj, 0.2)
                    assert bpy.ops.b4ml.quadruped_pose(operation="SOLVE") == {"FINISHED"}
                    metrics = json.loads(obj.b4ml.quadruped_payload)["metrics"]
                    distribution = metrics["spine_distribution"]
                    assert distribution["active"]
                    assert abs(distribution["follow"] - 0.64) <= 1e-6
                    assert abs(distribution["neck_share"] - 0.72) <= 1e-6
                    assert max(distribution["orientation_errors"].values()) <= metrics["orientation_tolerance"]
                    assert metrics["max_paw_error"] <= metrics["tolerance"]
                    state["metrics"] = metrics
                    state["events"].append("Spine Follow and Neck Share solved through the visible operator")
                    bpy.ops.view3d.view_selected(use_all_regions=False)
                    state["phase"] = "scroll"
                    return 0.35
                if state["phase"] == "scroll":
                    window.cursor_warp(sidebar.x + sidebar.width // 2,
                                       sidebar.y + sidebar.height // 2)
                    window.event_simulate(type="WHEELDOWNMOUSE", value="PRESS",
                                          x=sidebar.x + sidebar.width // 2,
                                          y=sidebar.y + sidebar.height // 2)
                    state["scrolls"] += 1
                    if state["scrolls"] < 28:
                        return 0.035
                    state["phase"] = "capture"
                    return 0.6
                path = ROOT / "training/b4artists_ml/cache/quadruped-spine-follow-ui-v1.png"
                bpy.ops.screen.screenshot(filepath=str(path))
                metrics = state["metrics"]
                distribution = metrics["spine_distribution"]
                report = {
                    "passed": True,
                    "fixture": "generated Rigify wolf",
                    "events": state["events"],
                    "spine_follow": distribution["follow"],
                    "neck_share": distribution["neck_share"],
                    "spine_orientation_errors": distribution["orientation_errors"],
                    "orientation_tolerance": metrics["orientation_tolerance"],
                    "head_orientation_error": metrics["orientation_errors"]["Head"],
                    "max_paw_error": metrics["max_paw_error"],
                    "paw_tolerance": metrics["tolerance"],
                    "screenshot": str(path.relative_to(ROOT)),
                    "screenshot_sha256": _sha(path),
                    "elapsed_seconds": time.monotonic() - state["started"],
                }
                quadruped_pose.finish(obj, scene, False)
                report["source_restored_after_cancel"] = not obj.b4ml.quadruped_payload
                (ROOT / "docs/b4artists_ml/quadruped-spine-follow-ui-v1.json").write_text(
                    json.dumps(report, indent=2) + "\n", encoding="utf-8")
                print("QUADRUPED_SPINE_FOLLOW_UI_RESULT: " + json.dumps(report), flush=True)
                bpy.ops.wm.quit_blender()
                return None
        except Exception as exc:
            report = {"passed": False, "phase": state["phase"], "error": str(exc),
                      "traceback": traceback.format_exc(), "events": state["events"]}
            (ROOT / "docs/b4artists_ml/quadruped-spine-follow-ui-v1.json").write_text(
                json.dumps(report, indent=2) + "\n", encoding="utf-8")
            print("QUADRUPED_SPINE_FOLLOW_UI_RESULT: " + json.dumps(report), flush=True)
            bpy.ops.wm.quit_blender()
            return None

    bpy.app.timers.register(tick, first_interval=0.5)


if __name__ == "__main__" and "--ui-smoke" in sys.argv:
    run_ui_smoke()
elif __name__ == "__main__":
    run()
