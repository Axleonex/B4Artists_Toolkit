"""Bounded direct-chain selection on real BoneForge and Rigify candidates."""
from pathlib import Path
from unittest import mock
import json
import os
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [os.environ.get("B4ML_PACKAGE", str(ROOT)), str(ROOT / "tests")]

import bpy
import b4artists_ml
from b4artists_ml import flight, secondary_motion as secondary, workflow as w
from test_b4artists_ml_secondary_motion import (
    animate_rotation_group,
    fixture as _secondary_fixture,
    rotation_chain,
)


def fixture(label):
    result = _secondary_fixture(label)
    obj = result[0]
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    if obj.mode != "POSE":
        bpy.ops.object.mode_set(mode="POSE")
    obj.b4ml.secondary_space = "LOCAL"
    obj.b4ml.secondary_rotation = True
    return result


def select_only(obj, names):
    names = set(names)
    for bone in obj.pose.bones:
        secondary._set_selected(bone, bone.name in names)


def snapshot(obj):
    active = obj.data.bones.active
    return {
        "selection": secondary.selected_controls(obj),
        "active": active.name if active else None,
        "chain": bool(obj.b4ml.secondary_chain),
        "status": obj.b4ml.status,
        "swap": obj.b4ml.secondary_selection_swap,
        "candidate": obj.b4ml.candidate_action,
        "assigned": obj.animation_data.action if obj.animation_data else None,
        "token": flight._curve_token(obj, obj.b4ml.candidate_action),
        "anchors": tuple((float(item.frame), item.payload) for item in obj.b4ml.anchors),
        "pose": w.raw_pose(obj),
    }


def eligibility(obj):
    anchors = w.read_anchors(obj)
    captured = set(anchors[0][1]["pose"])
    for _, payload in anchors[1:]:
        captured.intersection_update(payload["pose"])
    curves = w.action_curves(
        obj.b4ml.candidate_action, getattr(obj.animation_data, "action_slot", None))
    drivers = {curve.data_path for curve in obj.animation_data.drivers}
    controls = set(w.profile_for_object(obj).controls)
    return {
        bone.name for bone in obj.pose.bones
        if secondary._eligible_chain_control(
            obj, bone, captured, curves, drivers, controls)[0]
    }


def unique_child_link(obj):
    eligible = eligibility(obj)
    for parent in obj.pose.bones:
        children = [child for child in parent.children if child.name in eligible]
        if parent.name in eligible and len(children) == 1:
            return parent, children[0]
    raise AssertionError("Fixture has no eligible parent with one eligible child")


class SecondaryChainSelectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b4artists_ml.register()

    def test_parent_growth_on_boneforge_and_rigify_preserves_animation(self):
        for label in ("boneforge", "rigify_default"):
            with self.subTest(rig=label):
                obj, _, _, _, _, _ = fixture(label)
                chain = rotation_chain(obj)
                child = chain[1][0]
                select_only(obj, [chain[0][0].name])
                obj.data.bones.active = child.bone
                before = snapshot(obj)
                report = secondary.select_chain(obj, child.name, "PARENTS", 2)
                self.assertEqual(report["controls"], [item[0].name for item in chain])
                self.assertEqual(report["control_count"], 2)
                self.assertFalse(report["semantic_inference"])
                self.assertEqual(set(secondary.selected_controls(obj)), set(report["controls"]))
                self.assertEqual(obj.data.bones.active.name, child.name)
                self.assertTrue(obj.b4ml.secondary_chain)
                after = snapshot(obj)
                for key in ("candidate", "assigned", "token", "anchors", "pose"):
                    self.assertEqual(after[key], before[key])

    def test_child_growth_uses_only_one_eligible_direct_child(self):
        for label in ("boneforge", "rigify_default"):
            with self.subTest(rig=label):
                obj, _, _, _, _, _ = fixture(label)
                parent, child = unique_child_link(obj)
                select_only(obj, [child.name])
                obj.data.bones.active = parent.bone
                before = snapshot(obj)
                report = secondary.select_chain(obj, parent.name, "CHILDREN", 2)
                self.assertEqual(report["controls"], [parent.name, child.name])
                self.assertEqual(set(secondary.selected_controls(obj)),
                                 {parent.name, child.name})
                self.assertEqual(snapshot(obj)["token"], before["token"])
                self.assertEqual(snapshot(obj)["anchors"], before["anchors"])

    def test_registered_operator_uses_active_pose_control(self):
        obj, _, _, _, _, _ = fixture("boneforge")
        chain = rotation_chain(obj)
        child = chain[1][0]
        select_only(obj, [chain[0][0].name])
        obj.data.bones.active = child.bone
        if obj.mode != 'POSE':
            bpy.ops.object.mode_set(mode='POSE')
        self.assertEqual(
            bpy.ops.b4ml.secondary_select_chain(
                direction="PARENTS", max_controls=2),
            {"FINISHED"})
        self.assertEqual(set(secondary.selected_controls(obj)),
                         {item[0].name for item in chain})
        self.assertIn("toward parents", obj.b4ml.status)
        obj.b4ml.temporal_running = True
        self.assertFalse(bpy.ops.b4ml.secondary_select_chain.poll())
        self.assertFalse(bpy.ops.b4ml.secondary_selection_swap.poll())
        obj.b4ml.temporal_running = False

    def test_bound_swap_restores_and_reapplies_exact_selection(self):
        obj, _, _, _, _, _ = fixture("boneforge")
        chain = rotation_chain(obj)
        parent, child = chain[0][0], chain[1][0]
        select_only(obj, [parent.name])
        obj.data.bones.active = child.bone
        obj.b4ml.secondary_chain = False
        before = snapshot(obj)
        secondary.select_chain(obj, child.name, "PARENTS", 2)
        selected = snapshot(obj)
        self.assertNotEqual(selected["swap"], before["swap"])
        secondary.swap_selection(obj)
        restored = snapshot(obj)
        for key in ("selection", "active", "chain", "candidate", "assigned",
                    "token", "anchors", "pose"):
            self.assertEqual(restored[key], before[key])
        secondary.swap_selection(obj)
        reapplied = snapshot(obj)
        for key in ("selection", "active", "chain", "candidate", "assigned",
                    "token", "anchors", "pose"):
            self.assertEqual(reapplied[key], selected[key])
        obj.b4ml.secondary_selection_swap = "{}"
        malformed = snapshot(obj)
        with self.assertRaisesRegex(ValueError, "invalid schema"):
            secondary.swap_selection(obj)
        self.assertEqual(snapshot(obj), malformed)

    def test_invalid_previous_chain_mode_restores_selection_with_coupling_off(self):
        obj, _, _, _, _, _ = fixture("boneforge")
        chain = rotation_chain(obj)
        parent, child = chain[0][0], chain[1][0]
        select_only(obj, [parent.name])
        obj.data.bones.active = child.bone
        obj.b4ml.secondary_chain = True
        report = secondary.select_chain(obj, child.name, "PARENTS", 2)
        self.assertFalse(report["previous_chain_mode_preserved"])
        secondary.swap_selection(obj)
        self.assertEqual(secondary.selected_controls(obj), (parent.name,))
        self.assertEqual(obj.data.bones.active.name, child.name)
        self.assertFalse(obj.b4ml.secondary_chain)

    def test_undo_redo_lifecycle_uses_post_handlers_and_clears_record(self):
        obj, _, _, _, _, _ = fixture("boneforge")
        child = rotation_chain(obj)[1][0]
        obj.data.bones.active = child.bone
        self.assertEqual(bpy.ops.b4ml.secondary_select_chain(
            direction="PARENTS", max_controls=2), {"FINISHED"})
        self.assertTrue(obj.b4ml.secondary_selection_swap)
        self.assertIn(secondary.reset_selection_swap, bpy.app.handlers.undo_post)
        self.assertIn(secondary.reset_selection_swap, bpy.app.handlers.redo_post)
        self.assertNotIn(secondary.reset_selection_swap, bpy.app.handlers.undo_pre)
        self.assertNotIn(secondary.reset_selection_swap, bpy.app.handlers.redo_pre)
        secondary.reset_selection_swap()
        self.assertFalse(obj.b4ml.secondary_selection_swap)

    def test_invalid_request_is_non_mutating(self):
        obj, _, _, _, _, _ = fixture("boneforge")
        chain = rotation_chain(obj)
        active = chain[1][0]
        obj.data.bones.active = active.bone
        before = snapshot(obj)
        for direction, maximum in (("SIDEWAYS", 2), ("PARENTS", True),
                                   ("PARENTS", 1), ("PARENTS", 33)):
            with self.subTest(direction=direction, maximum=maximum):
                with self.assertRaises(ValueError):
                    secondary.select_chain(obj, active.name, direction, maximum)
                self.assertEqual(snapshot(obj), before)
        with self.assertRaisesRegex(ValueError, "disappeared"):
            secondary.select_chain(obj, "missing-control", "PARENTS", 2)
        self.assertEqual(snapshot(obj), before)

    def test_select_and_swap_reject_every_busy_owner_atomically(self):
        obj, _, _, _, _, _ = fixture("boneforge")
        chain = rotation_chain(obj)
        child = chain[1][0]
        obj.data.bones.active = child.bone
        secondary.select_chain(obj, child.name, "PARENTS", 2)
        bool_fields = (
            "temporal_running", "body_running", "body_live", "contact_running",
            "contact_suggest_running", "flight_running", "secondary_running",
            "cleanup_running")
        string_fields = ("body_payload", "posing_payload", "quadruped_payload")
        for field in bool_fields + string_fields:
            setattr(obj.b4ml, field, True if field in bool_fields else "busy")
            before = snapshot(obj)
            with self.subTest(operation="select", field=field), self.assertRaisesRegex(
                    ValueError, "active pose or correction"):
                secondary.select_chain(obj, child.name, "PARENTS", 2)
            self.assertEqual(snapshot(obj), before)
            with self.subTest(operation="swap", field=field), self.assertRaisesRegex(
                    ValueError, "active pose or correction"):
                secondary.swap_selection(obj)
            self.assertEqual(snapshot(obj), before)
            setattr(obj.b4ml, field, False if field in bool_fields else "")

    def test_search_operator_rejects_solver_incompatible_settings_atomically(self):
        obj, _, _, _, _, _ = fixture("boneforge")
        child = rotation_chain(obj)[1][0]
        obj.data.bones.active = child.bone
        for space, rotation in (("WORLD", True), ("LOCAL", False)):
            obj.b4ml.secondary_space = space
            obj.b4ml.secondary_rotation = rotation
            before = snapshot(obj)
            with self.subTest(space=space, rotation=rotation):
                self.assertFalse(bpy.ops.b4ml.secondary_select_chain.poll())
                with self.assertRaisesRegex(ValueError, "Local space and Rotation"):
                    secondary.select_chain(obj, child.name, "PARENTS", 2)
                self.assertEqual(snapshot(obj), before)

    def test_swap_revalidates_chain_eligibility_before_mutation(self):
        obj, _, _, _, _, _ = fixture("boneforge")
        chain = rotation_chain(obj)
        child = chain[1][0]
        obj.data.bones.active = child.bone
        secondary.select_chain(obj, child.name, "PARENTS", 2)
        secondary.swap_selection(obj)
        target = chain[0][0]

        target.lock_rotation = (True, False, False)
        before = snapshot(obj)
        with self.assertRaisesRegex(ValueError, "no longer eligible.*locked"):
            secondary.swap_selection(obj)
        self.assertEqual(snapshot(obj), before)
        target.lock_rotation = (False, False, False)

        prop, _ = secondary._rotation_spec(target)
        driver = target.driver_add(prop, 0)
        driver.driver.expression = "0"
        before = snapshot(obj)
        try:
            with self.assertRaisesRegex(ValueError, "no longer eligible.*driven"):
                secondary.swap_selection(obj)
            self.assertEqual(snapshot(obj), before)
        finally:
            target.driver_remove(prop, 0)

        for field in ("hide", "hide_select"):
            setattr(target.bone, field, True)
            before = snapshot(obj)
            with self.subTest(field=field), self.assertRaisesRegex(
                    ValueError, "no longer eligible.*hidden or not selectable"):
                secondary.swap_selection(obj)
            self.assertEqual(snapshot(obj), before)
            setattr(target.bone, field, False)

    def test_swap_binds_exact_candidate_and_action_slot_identity(self):
        obj, _, _, _, _, _ = fixture("boneforge")
        child = rotation_chain(obj)[1][0]
        obj.data.bones.active = child.bone
        secondary.select_chain(obj, child.name, "PARENTS", 2)
        record = json.loads(obj.b4ml.secondary_selection_swap)
        self.assertEqual(record["schema"], 2)
        self.assertEqual(record["candidate_identity"],
                         secondary._candidate_identity(obj, obj.b4ml.candidate_action))

        changed = dict(record)
        changed["candidate_identity"] = dict(record["candidate_identity"])
        changed["candidate_identity"]["slot_handle"] = -1
        obj.b4ml.secondary_selection_swap = json.dumps(changed)
        before = snapshot(obj)
        with self.assertRaisesRegex(ValueError, "different animation candidate"):
            secondary.swap_selection(obj)
        self.assertEqual(snapshot(obj), before)

        obj.b4ml.secondary_selection_swap = json.dumps(record)
        original = obj.b4ml.candidate_action
        replacement = original.copy()
        original_name = original.name
        original.name = original_name + " Previous"
        replacement.name = original_name
        identifier = w._slot(obj.animation_data)
        w.assign_action(obj, replacement, identifier)
        obj.b4ml.candidate_action = replacement
        before = snapshot(obj)
        with self.assertRaisesRegex(ValueError, "different animation candidate"):
            secondary.swap_selection(obj)
        self.assertEqual(snapshot(obj), before)

    def test_swap_requires_pose_mode_and_custom_deform_admission_is_safe(self):
        obj, _, _, _, _, _ = fixture("boneforge")
        chain = rotation_chain(obj)
        child = chain[1][0]
        obj.data.bones.active = child.bone
        secondary.select_chain(obj, child.name, "PARENTS", 2)
        if obj.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
        before = snapshot(obj)
        self.assertFalse(bpy.ops.b4ml.secondary_selection_swap.poll())
        with self.assertRaisesRegex(ValueError, "Pose Mode"):
            secondary.select_chain(obj, child.name, "PARENTS", 2)
        self.assertEqual(snapshot(obj), before)
        with self.assertRaisesRegex(ValueError, "Pose Mode"):
            secondary.swap_selection(obj)
        self.assertEqual(snapshot(obj), before)
        bpy.ops.object.mode_set(mode="POSE")

        custom = chain[0][0]
        anchors = w.read_anchors(obj)
        captured = set(anchors[0][1]["pose"])
        for _, payload in anchors[1:]:
            captured.intersection_update(payload["pose"])
        curves = w.action_curves(obj.b4ml.candidate_action,
                                 getattr(obj.animation_data, "action_slot", None))
        drivers = {curve.data_path for curve in obj.animation_data.drivers}
        deform_before = custom.bone.use_deform
        custom.bone.use_deform = False
        self.assertTrue(secondary._eligible_chain_control(
            obj, custom, captured, curves, drivers, set())[0])
        custom.bone.use_deform = True
        valid, reason = secondary._eligible_chain_control(
            obj, custom, captured, curves, drivers, set())
        self.assertFalse(valid)
        self.assertIn("unrecognized deform bone", reason)
        custom.bone.use_deform = deform_before

    def test_swap_record_survives_save_but_is_cleared_after_reload(self):
        obj, _, _, _, _, _ = fixture("boneforge")
        child = rotation_chain(obj)[1][0]
        obj.data.bones.active = child.bone
        secondary.select_chain(obj, child.name, "PARENTS", 2)
        self.assertTrue(obj.b4ml.secondary_selection_swap)
        name = obj.name
        path = ROOT / "training/b4artists_ml/cache/secondary-chain-swap-session-only.blend"
        path.parent.mkdir(parents=True, exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=str(path))
        self.assertTrue(obj.b4ml.secondary_selection_swap)
        bpy.ops.wm.open_mainfile(filepath=str(path), use_scripts=False)
        self.assertFalse(bpy.data.objects[name].b4ml.secondary_selection_swap)

    def test_locked_and_driven_active_controls_are_rejected_without_selection_change(self):
        obj, _, _, _, _, _ = fixture("boneforge")
        active = rotation_chain(obj)[1][0]
        obj.data.bones.active = active.bone
        before = snapshot(obj)
        active.lock_rotation = (True, False, False)
        with self.assertRaisesRegex(ValueError, "partially locked"):
            secondary.select_chain(obj, active.name, "PARENTS", 2)
        active.lock_rotation = (False, False, False)
        self.assertEqual(snapshot(obj)["selection"], before["selection"])
        prop, _ = secondary._rotation_spec(active)
        driver = active.driver_add(prop, 0)
        driver.driver.expression = "0"
        try:
            with self.assertRaisesRegex(ValueError, "driven"):
                secondary.select_chain(obj, active.name, "PARENTS", 2)
            self.assertEqual(snapshot(obj)["selection"], before["selection"])
        finally:
            active.driver_remove(prop, 0)

    def test_ambiguous_child_branch_and_mutation_failure_restore_exact_selection(self):
        obj, _, _, _, _, _ = fixture("boneforge")
        branch = next(bone for bone in obj.pose.bones if len(bone.children) > 1)
        obj.data.bones.active = branch.bone
        before = snapshot(obj)
        with mock.patch.object(secondary, "_eligible_chain_control",
                               return_value=(True, "")):
            with self.assertRaisesRegex(ValueError, "branches"):
                secondary.select_chain(obj, branch.name, "CHILDREN", 3)
        self.assertEqual(snapshot(obj), before)

        chain = rotation_chain(obj)
        active = chain[1][0]
        obj.data.bones.active = active.bone
        before = snapshot(obj)
        native = secondary._set_selected
        state = {"calls": 0, "raised": False}

        def fail_once(bone, value):
            state["calls"] += 1
            if not state["raised"] and state["calls"] == 3:
                state["raised"] = True
                raise RuntimeError("injected selection write failure")
            return native(bone, value)

        with mock.patch.object(secondary, "_set_selected", side_effect=fail_once):
            with self.assertRaisesRegex(RuntimeError, "injected"):
                secondary.select_chain(obj, active.name, "PARENTS", 2)
        self.assertEqual(snapshot(obj), before)

    def test_selected_chain_runs_existing_editable_solver(self):
        obj, _, _, _, _, _ = fixture("rigify_default")
        chain = rotation_chain(obj)
        for index, definition in enumerate(chain):
            animate_rotation_group(obj.b4ml.candidate_action, obj, definition,
                                   .45 / (index + 1))
        child = chain[1][0]
        obj.data.bones.active = child.bone
        selected = secondary.select_chain(obj, child.name, "PARENTS", 2)
        priority = obj.b4ml.anchors.add()
        priority.frame = 6.0
        priority.payload = obj.b4ml.anchors[0].payload
        obj.b4ml.secondary_space = "LOCAL"
        obj.b4ml.secondary_rotation = True
        obj.b4ml.secondary_location = False
        report = secondary.solve(obj, bpy.context.scene)
        self.assertEqual(report["backend"], "implicit_selected_control_chain_v1")
        self.assertEqual(report["chain_controls"], selected["controls"])
        self.assertTrue(report["priority_poses_preserved"])
        self.assertTrue(report["editable_linear_keys"])
        secondary.restore(obj, bpy.context.scene)


if __name__ == "__main__":
    unittest.main()
