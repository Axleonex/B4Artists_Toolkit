"""Bforartists evidence for generated-Rigify quadruped pole targets."""
from pathlib import Path
import hashlib
import json
import os
import sys
import time
import traceback
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [os.environ.get("B4ML_PACKAGE", str(ROOT)), str(ROOT / "tests")]

import addon_utils
import bpy
from mathutils import Vector

import b4artists_ml
from b4artists_ml import quadruped_pose, workflow
from test_b4artists_ml_quadruped_pose import _action_signature, _generate


RECORDS = []


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _source(obj, scene):
    scene.frame_set(11)
    root = obj.pose.bones["root"]
    root.location = (0.008, -0.005, 0.003)
    root.keyframe_insert("location", frame=11)
    action = obj.animation_data.action
    return workflow.raw_pose(obj), action, _action_signature(obj, action)


def _enable_poles(obj):
    _, _, limbs = quadruped_pose.binding(obj)
    for row in limbs:
        obj.pose.bones[row["property_bone"]]["pole_vector"] = True
    obj.b4ml.quadruped_use_poles = True
    bpy.context.view_layer.update()
    return limbs


def _move_poles(obj, amount=1.0):
    deltas = {
        "Fore Pole L": Vector((0.018, -0.011, 0.009)),
        "Fore Pole R": Vector((-0.014, -0.008, 0.006)),
        "Hind Pole L": Vector((0.013, 0.010, 0.008)),
        "Hind Pole R": Vector((-0.016, 0.009, 0.007)),
    }
    for label, delta in deltas.items():
        helper = obj.b4ml.quadruped_targets[label].target
        helper.location += delta * amount
    bpy.context.view_layer.update()
    return {label: obj.b4ml.quadruped_targets[label].target.matrix_world.translation.copy()
            for label in deltas}


class QuadrupedPoleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not b4artists_ml.is_bforartists():
            raise unittest.SkipTest("Bforartists required")
        addon_utils.enable("rigify", default_set=True, persistent=False)
        b4artists_ml.register()

    def test_cat_horse_wolf_poles_are_exact_and_paws_remain_pinned(self):
        expected = {
            "cat": {"fore-L": "upper_arm_ik_target.L", "fore-R": "upper_arm_ik_target.R",
                    "hind-L": "thigh_ik_target.L", "hind-R": "thigh_ik_target.R"},
            "horse": {"fore-L": "upper_arm_ik_target.L", "fore-R": "upper_arm_ik_target.R",
                      "hind-L": "thigh_ik_target.L", "hind-R": "thigh_ik_target.R"},
            "wolf": {"fore-L": "front_thigh_ik_target.L", "fore-R": "front_thigh_ik_target.R",
                     "hind-L": "thigh_ik_target.L", "hind-R": "thigh_ik_target.R"},
        }
        for kind in ("cat", "horse", "wolf"):
            with self.subTest(profile=kind):
                scene, obj = _generate(kind)
                limbs = _enable_poles(obj)
                source, action, action_signature = _source(obj, scene)
                self.assertEqual(quadruped_pose.begin(obj, scene), 10)
                record = json.loads(obj.b4ml.quadruped_payload)
                self.assertEqual(record["schema"], 4)
                self.assertEqual(record["pole_controls"], expected[kind])
                bend_stems = {"cat": {"fore": "ORG-forearm", "hind": "ORG-shin"},
                              "horse": {"fore": "ORG-forearm", "hind": "ORG-lower_leg"},
                              "wolf": {"fore": "ORG-front_shin", "hind": "ORG-shin"}}
                bends_before = {row["id"]: (obj.matrix_world @
                    obj.pose.bones[bend_stems[kind][row["id"].split("-")[0]] + "." +
                                   row["id"].split("-")[1]].head).copy()
                    for row in limbs}
                requested = _move_poles(obj)
                metrics = quadruped_pose.solve(obj, scene)
                self.assertEqual(set(metrics["pole_errors"]), set(quadruped_pose.POLE_TARGETS))
                self.assertLessEqual(metrics["max_pole_error"], metrics["tolerance"])
                self.assertLessEqual(metrics["max_paw_error"], metrics["tolerance"])
                for row in limbs:
                    actual = obj.matrix_world @ obj.pose.bones[row["pole"]].matrix.translation
                    self.assertLessEqual((actual - requested[row["pole_label"]]).length,
                                         metrics["tolerance"])
                    bend_name = (bend_stems[kind][row["id"].split("-")[0]] + "." +
                                 row["id"].split("-")[1])
                    bend_after = obj.matrix_world @ obj.pose.bones[bend_name].head
                    self.assertGreater((bend_after - bends_before[row["id"]]).length, 1e-5)
                quadruped_pose.finish(obj, scene, False)
                self.assertEqual(workflow.raw_pose(obj), source)
                self.assertIs(obj.animation_data.action, action)
                self.assertEqual(_action_signature(obj, action), action_signature)
                RECORDS.append({"profile": kind, "max_pole_error": metrics["max_pole_error"],
                                "max_paw_error": metrics["max_paw_error"]})

    def test_position_only_helper_contract_rejects_external_control_atomically(self):
        scene, obj = _generate("cat")
        _enable_poles(obj)
        source, action, action_signature = _source(obj, scene)
        quadruped_pose.begin(obj, scene)
        item = obj.b4ml.quadruped_targets["Fore Pole L"]
        self.assertFalse(item.use_orientation)
        self.assertEqual(tuple(item.target.lock_rotation), (True, True, True))
        self.assertEqual(item.target.empty_display_type, "CIRCLE")

        for mutation, restore, message in (
                (lambda: setattr(item, "use_orientation", True),
                 lambda: setattr(item, "use_orientation", False), "position-only"),
                (lambda: setattr(item.target, "lock_rotation", (False, True, True)),
                 lambda: setattr(item.target, "lock_rotation", (True, True, True)), "rotation must remain locked"),
                (lambda: setattr(item.target, "rotation_mode", "XYZ"),
                 lambda: setattr(item.target, "rotation_mode", "QUATERNION"), "rotation mode must remain Quaternion"),
                (lambda: item.target.constraints.new("COPY_LOCATION"),
                 lambda: item.target.constraints.remove(item.target.constraints[-1]), "constraints are not supported")):
            before = workflow.raw_pose(obj)
            mutation()
            with self.assertRaisesRegex(ValueError, message):
                quadruped_pose.solve(obj, scene)
            self.assertEqual(workflow.raw_pose(obj), before)
            restore()
            bpy.context.view_layer.update()
        quadruped_pose.finish(obj, scene, False)
        self.assertEqual(workflow.raw_pose(obj), source)
        self.assertIs(obj.animation_data.action, action)
        self.assertEqual(_action_signature(obj, action), action_signature)

    def test_pole_controls_reject_locks_constraints_and_drivers_before_mutation(self):
        scene, obj = _generate("horse")
        _, _, limbs = quadruped_pose.binding(obj)
        obj.b4ml.quadruped_use_poles = True
        untouched = workflow.raw_pose(obj)
        with self.assertRaisesRegex(ValueError, "Enable Rigify Pole Vector"):
            quadruped_pose.begin(obj, scene)
        self.assertEqual(workflow.raw_pose(obj), untouched)
        _enable_poles(obj)
        property_bone = obj.pose.bones[limbs[0]["property_bone"]]
        del property_bone["pole_vector"]
        property_bone["pole_vector"] = 0.5
        with self.assertRaisesRegex(ValueError, "Enable Rigify Pole Vector"):
            quadruped_pose.begin(obj, scene)
        self.assertFalse(obj.b4ml.quadruped_payload)
        del property_bone["pole_vector"]
        property_bone["pole_vector"] = True
        driver = property_bone.driver_add('["pole_vector"]')
        driver.driver.expression = "1.0"
        bpy.context.view_layer.update()
        with self.assertRaisesRegex(ValueError, "undriven Pole Vector"):
            quadruped_pose.begin(obj, scene)
        self.assertFalse(obj.b4ml.quadruped_payload)
        property_bone.driver_remove('["pole_vector"]')
        source, action, action_signature = _source(obj, scene)
        pole = obj.pose.bones[limbs[0]["pole"]]
        objects = set(bpy.data.objects)
        pole.lock_location[0] = True
        with self.assertRaisesRegex(ValueError, "unlocked XYZ location"):
            quadruped_pose.begin(obj, scene)
        self.assertFalse(obj.b4ml.quadruped_payload)
        self.assertEqual(set(bpy.data.objects), objects)
        pole.lock_location[0] = False

        quadruped_pose.begin(obj, scene)
        _move_poles(obj, 0.5)
        changed_mode = obj.pose.bones[limbs[1]["property_bone"]]
        del changed_mode["pole_vector"]
        changed_mode["pole_vector"] = 0.5
        before = workflow.raw_pose(obj)
        with self.assertRaisesRegex(ValueError, "Pole Vector mode changed"):
            quadruped_pose.solve(obj, scene)
        self.assertEqual(workflow.raw_pose(obj), before)
        del changed_mode["pole_vector"]
        changed_mode["pole_vector"] = True
        constraint = pole.constraints.new("COPY_LOCATION")
        before = workflow.raw_pose(obj)
        with self.assertRaisesRegex(ValueError, "constrained control"):
            quadruped_pose.solve(obj, scene)
        self.assertEqual(workflow.raw_pose(obj), before)
        pole.constraints.remove(constraint)
        driver = pole.driver_add("location", 0)
        driver.driver.expression = "0.0"
        bpy.context.view_layer.update()
        with self.assertRaisesRegex(ValueError, "driven control"):
            quadruped_pose.solve(obj, scene)
        self.assertEqual(workflow.raw_pose(obj), before)
        pole.driver_remove("location", 0)
        quadruped_pose.finish(obj, scene, False)
        self.assertEqual(workflow.raw_pose(obj), source)
        self.assertIs(obj.animation_data.action, action)
        self.assertEqual(_action_signature(obj, action), action_signature)

    def test_changed_pole_requires_resolve_before_keep(self):
        scene, obj = _generate("wolf")
        _enable_poles(obj)
        source, action, action_signature = _source(obj, scene)
        quadruped_pose.begin(obj, scene)
        _move_poles(obj, 0.5)
        quadruped_pose.solve(obj, scene)
        obj.b4ml.quadruped_targets["Hind Pole R"].target.location.x += 0.01
        bpy.context.view_layer.update()
        before = workflow.raw_pose(obj)
        with self.assertRaisesRegex(ValueError, "Solve the current quadruped targets"):
            quadruped_pose.finish(obj, scene, True)
        self.assertEqual(workflow.raw_pose(obj), before)
        quadruped_pose.solve(obj, scene)
        quadruped_pose.finish(obj, scene, True)
        self.assertEqual(len(obj.b4ml.anchors), 1)
        self.assertEqual(workflow.raw_pose(obj), source)
        self.assertIs(obj.animation_data.action, action)
        self.assertEqual(_action_signature(obj, action), action_signature)

    def test_schema_three_preview_recovers_without_pole_targets(self):
        scene, obj = _generate("cat")
        _enable_poles(obj)
        source, action, action_signature = _source(obj, scene)
        quadruped_pose.begin(obj, scene)
        state = obj.b4ml
        record = json.loads(state.quadruped_payload)
        record["schema"] = 3
        record.pop("pole_controls")
        for label in quadruped_pose.POLE_TARGETS:
            index = next(i for i, item in enumerate(state.quadruped_targets) if item.name == label)
            helper = state.quadruped_targets[index].target
            state.quadruped_targets.remove(index)
            bpy.data.objects.remove(helper, do_unlink=True)
        state.quadruped_payload = json.dumps(record, allow_nan=False)
        self.assertEqual(len(state.quadruped_targets), 6)
        metrics = quadruped_pose.solve(obj, scene)
        self.assertNotIn("Fore Pole L", metrics.get("pole_errors", {}))
        self.assertEqual(metrics["max_pole_error"], 0.0)
        quadruped_pose.finish(obj, scene, False)
        self.assertEqual(workflow.raw_pose(obj), source)
        self.assertIs(obj.animation_data.action, action)
        self.assertEqual(_action_signature(obj, action), action_signature)

    def test_schema_four_poles_survive_reload_and_keep(self):
        scene, obj = _generate("horse")
        _enable_poles(obj)
        source, action, action_signature = _source(obj, scene)
        action_name = action.name
        quadruped_pose.begin(obj, scene)
        _move_poles(obj, 0.65)
        metrics = quadruped_pose.solve(obj, scene)
        self.assertLessEqual(metrics["max_pole_error"], metrics["tolerance"])
        name = obj.name
        path = ROOT / "training/b4artists_ml/cache/quadruped-poles-v1.blend"
        bpy.ops.wm.save_as_mainfile(filepath=str(path))
        bpy.ops.wm.open_mainfile(filepath=str(path), use_scripts=False)
        obj = bpy.data.objects[name]
        scene = bpy.context.scene
        bpy.context.view_layer.objects.active = obj
        self.assertEqual(json.loads(obj.b4ml.quadruped_payload)["schema"], 4)
        quadruped_pose.finish(obj, scene, True)
        self.assertEqual(len(obj.b4ml.anchors), 1)
        self.assertEqual(workflow.raw_pose(obj), source)
        self.assertEqual(obj.animation_data.action.name, action_name)
        self.assertEqual(_action_signature(obj, obj.animation_data.action), action_signature)
        RECORDS.append({"workflow": "quadruped_pole_save_reload_keep", "passed": True})


def run():
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(QuadrupedPoleTests)
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
    output = ROOT / "training/b4artists_ml/results/quadruped-poles-v1.json"
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("QUADRUPED_POLES_RESULT: " + json.dumps(report), flush=True)
    if not result.wasSuccessful():
        raise SystemExit(1)


def run_ui_smoke():
    QuadrupedPoleTests.setUpClass()
    scene, obj = _generate("wolf")
    _enable_poles(obj)
    source, _, _ = _source(obj, scene)
    state = {"name": obj.name, "phase": "operate", "started": time.monotonic(),
             "scrolls": 0, "events": []}

    def tick():
        try:
            if time.monotonic() - state["started"] > 45:
                raise AssertionError("Quadruped Pole UI timed out")
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
                    requested = _move_poles(obj, 0.7)
                    assert bpy.ops.b4ml.quadruped_pose(operation="SOLVE") == {"FINISHED"}
                    metrics = json.loads(obj.b4ml.quadruped_payload)["metrics"]
                    assert metrics["max_pole_error"] <= metrics["tolerance"]
                    assert metrics["max_paw_error"] <= metrics["tolerance"]
                    state["metrics"] = metrics
                    state["requested"] = {key: list(value) for key, value in requested.items()}
                    state["events"].append("Four pole targets solved through the visible operator")
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
                    if state["scrolls"] < 20:
                        return 0.04
                    state["phase"] = "capture"
                    return 0.6
                path = ROOT / "training/b4artists_ml/cache/quadruped-poles-ui-v1.png"
                bpy.ops.screen.screenshot(filepath=str(path))
                metrics = state["metrics"]
                report = {
                    "passed": True,
                    "fixture": "generated Rigify wolf",
                    "events": state["events"],
                    "pole_targets": list(quadruped_pose.POLE_TARGETS),
                    "max_pole_error": metrics["max_pole_error"],
                    "max_paw_error": metrics["max_paw_error"],
                    "tolerance": metrics["tolerance"],
                    "screenshot": str(path.relative_to(ROOT)),
                    "screenshot_sha256": _sha(path),
                    "elapsed_seconds": time.monotonic() - state["started"],
                }
                quadruped_pose.finish(obj, scene, False)
                report["source_restored_after_cancel"] = workflow.raw_pose(obj) == source
                (ROOT / "docs/b4artists_ml/quadruped-poles-ui-v1.json").write_text(
                    json.dumps(report, indent=2) + "\n", encoding="utf-8")
                print("QUADRUPED_POLES_UI_RESULT: " + json.dumps(report), flush=True)
                bpy.ops.wm.quit_blender()
                return None
        except Exception as exc:
            report = {"passed": False, "phase": state["phase"], "error": str(exc),
                      "traceback": traceback.format_exc(), "events": state["events"]}
            (ROOT / "docs/b4artists_ml/quadruped-poles-ui-v1.json").write_text(
                json.dumps(report, indent=2) + "\n", encoding="utf-8")
            print("QUADRUPED_POLES_UI_RESULT: " + json.dumps(report), flush=True)
            bpy.ops.wm.quit_blender()
            return None

    bpy.app.timers.register(tick, first_interval=0.5)


if __name__ == "__main__" and "--ui-smoke" in sys.argv:
    run_ui_smoke()
elif __name__ == "__main__":
    run()
