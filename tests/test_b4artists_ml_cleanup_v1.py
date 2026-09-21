"""Native reversible animation-cleanup workflows for humanoids and quadrupeds."""
from pathlib import Path
import json
import os
import sys
import time
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [os.environ.get('B4ML_PACKAGE', str(ROOT)), str(ROOT/'tests')]

import addon_utils
import bpy

import b4artists_ml
from b4artists_ml import cleanup, contacts, flight, posing, workflow as w
from test_b4artists_ml_contacts import fixture
from test_b4artists_ml_quadruped_contacts import _candidate as quadruped_candidate


RECORDS = []


def select_only(obj, name):
    for bone in obj.pose.bones:
        if hasattr(bone, 'select'):
            bone.select = bone.name == name
        else:
            bone.bone.select = bone.name == name


def curve(obj, action, path, index=0):
    slot = next((item for item in action.slots if item.identifier == w._slot(obj.animation_data)), None)
    return w.action_curves(action, slot).find(path, index=index)


def curve_state(value):
    return cleanup._curve_state(value)


def add_reducible_motion(obj, action, name, bump=.02):
    bone = obj.pose.bones[name]
    path = bone.path_from_id('location')
    value = curve(obj, action, path, 0)
    if value is None:
        raise AssertionError('Fixture lacks the selected control location curve')
    start = float(value.evaluate(1.0))
    end = float(value.evaluate(11.0))
    for frame in range(1, 12):
        point = next((key for key in value.keyframe_points if abs(float(key.co.x)-frame) < 1e-6), None)
        if point is None:
            point = value.keyframe_points.insert(float(frame), 0.0, options={'FAST'})
        point.co.y = start+(end-start)*(frame-1)/10 + (bump if frame == 6 else 0.0)
        point.interpolation = 'LINEAR'
    value.update()
    return path, curve_state(value)


class CleanupRuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        addon_utils.enable('rigify', default_set=True, persistent=False)
        b4artists_ml.register()

    def test_humanoid_cleanup_preserves_source_priority_and_accepted_contacts(self):
        obj, source, source_signature, modes = fixture('boneforge', transformed=True)
        scene = bpy.context.scene
        state = obj.b4ml
        original = state.candidate_action
        path, _ = add_reducible_motion(obj, original, 'arm.pole-L', bump=.1)
        input_token = flight._curve_token(obj, original)
        source_curve = curve(obj, original, path)
        endpoints = (float(source_curve.evaluate(1.0)), float(source_curve.evaluate(11.0)))
        protected = cleanup._accepted_contact_controls(obj, 1.0, 11.0)
        self.assertTrue(protected)
        protected_states = {}
        for name in protected:
            bone = obj.pose.bones[name]
            for prop in ('location', 'rotation_quaternion', 'rotation_euler'):
                candidate_path = bone.path_from_id(prop)
                for index in range(4):
                    value = curve(obj, original, candidate_path, index)
                    if value is not None:
                        protected_states[(candidate_path, index)] = curve_state(value)
        state.cleanup_scope = 'CAPTURED'
        state.cleanup_smooth = True
        state.cleanup_strength = 0.7
        state.cleanup_reduce = True
        state.cleanup_tolerance = 0.025
        step_ms = []
        cleanup.start(obj, scene)
        while True:
            began = time.perf_counter()
            done = cleanup.step(obj)
            step_ms.append((time.perf_counter()-began)*1000)
            if done:
                break
        report = json.loads(state.cleanup_metrics)
        output = state.candidate_action
        self.assertEqual(report['backend'], 'contact_aware_curve_cleanup_v1')
        self.assertFalse(report['learned'])
        self.assertGreater(report['keys_removed'], 0)
        self.assertEqual(report['keys_before']-report['keys_after'], report['keys_removed'])
        self.assertGreater(report['curves_smoothed'], 0)
        self.assertTrue(set(report['protected_contact_controls']))
        self.assertEqual(report['accepted_contacts'], 2)
        self.assertGreater(report['contact_samples'], 0)
        self.assertLess(report['contact_sample_frames'], report['contact_samples'])
        self.assertEqual(report['contact_frame_evaluations'], 2*report['contact_sample_frames'])
        self.assertLessEqual(report['max_contact_position_drift'], 2e-6)
        self.assertLessEqual(report['max_contact_rotation_drift_radians'], 2e-5)
        self.assertGreaterEqual(report['max_scalar_derivative_jump_before'], 0.0)
        self.assertGreaterEqual(report['max_scalar_derivative_jump_after'], 0.0)
        self.assertTrue(report['priority_poses_preserved'])
        self.assertTrue(report['contacts_preserved'])
        self.assertEqual(flight._curve_token(obj, original), input_token)
        output_curve = curve(obj, output, path)
        self.assertEqual((float(output_curve.evaluate(1.0)), float(output_curve.evaluate(11.0))), endpoints)
        for key, before in protected_states.items():
            self.assertEqual(curve_state(curve(obj, output, *key)), before)
        self.assertIs(state.cleanup_input, original)
        self.assertIs(state.cleanup_output, output)
        RECORDS.append(dict(report, step_p95_ms=sorted(step_ms)[int(.95*(len(step_ms)-1))],
                            step_max_ms=max(step_ms), step_count=len(step_ms)))
        cleanup.restore(obj, scene)
        self.assertIs(state.candidate_action, original)
        self.assertEqual(flight._curve_token(obj, original), input_token)
        w.finish_preview(obj, scene, False)
        self.assertIs(obj.animation_data.action, source)
        self.assertEqual(contacts._action_signature(obj), source_signature)

    def test_abort_and_changed_request_leave_input_selected(self):
        obj, _, _, _ = fixture('boneforge')
        scene = bpy.context.scene
        state = obj.b4ml
        state.contacts.clear()
        original = state.candidate_action
        root = posing.bindings(obj)[1]
        add_reducible_motion(obj, original, root)
        select_only(obj, root)
        before = flight._curve_token(obj, original)
        cleanup.start(obj, scene)
        self.assertFalse(cleanup.step(obj))
        cleanup.abort(obj)
        self.assertFalse(state.cleanup_running)
        self.assertIs(obj.animation_data.action, original)
        self.assertIs(state.candidate_action, original)
        self.assertEqual(flight._curve_token(obj, original), before)
        cleanup.start(obj, scene)
        self.assertFalse(cleanup.step(obj))
        state.cleanup_strength += 0.1
        with self.assertRaisesRegex(ValueError, 'changed'):
            cleanup.step(obj)
        self.assertFalse(state.cleanup_running)
        self.assertIs(obj.animation_data.action, original)
        self.assertEqual(flight._curve_token(obj, original), before)

    def test_fractional_priority_frames_remain_keyed_and_exact(self):
        obj, _, _, _ = fixture('boneforge')
        scene = bpy.context.scene
        state = obj.b4ml
        state.contacts.clear()
        original = state.candidate_action
        root = posing.bindings(obj)[1]
        select_only(obj, root)
        path = obj.pose.bones[root].path_from_id('location')
        value = curve(obj, original, path, 0)
        for index in range(len(value.keyframe_points)-1, -1, -1):
            value.keyframe_points.remove(value.keyframe_points[index], fast=True)
        for frame, sample in ((1.25, 0.0), (3.5, .1), (6.5, .24), (8.0, .27), (10.75, .38)):
            key = value.keyframe_points.insert(frame, sample, options={'FAST'})
            key.interpolation = 'LINEAR'
        value.update()
        state.anchors[0].frame = 1.25
        state.anchors[1].frame = 10.75
        middle = state.anchors.add()
        middle.frame = 6.5
        middle.payload = state.anchors[0].payload
        middle.name = 'Fractional priority'
        state.cleanup_scope = 'SELECTED'
        state.cleanup_tolerance = .03
        before = flight._curve_token(obj, original)
        report = cleanup.solve(obj, scene)
        output = curve(obj, state.candidate_action, path, 0)
        priorities = {round(float(key.co.x), 5): float(key.co.y) for key in output.keyframe_points}
        self.assertEqual(priorities[1.25], 0.0)
        self.assertEqual(priorities[6.5], float(value.evaluate(6.5)))
        self.assertEqual(priorities[10.75], float(value.evaluate(10.75)))
        self.assertEqual(report['priority_poses'], 3)
        self.assertTrue(report['priority_poses_preserved'])
        self.assertEqual(flight._curve_token(obj, original), before)

    def test_keep_save_reload_and_restore_source(self):
        obj, source, source_signature, modes = fixture('rigify_default')
        scene = bpy.context.scene
        state = obj.b4ml
        state.contacts.clear()
        root = posing.bindings(obj)[1]
        add_reducible_motion(obj, state.candidate_action, root)
        select_only(obj, root)
        state.cleanup_scope = 'SELECTED'
        state.cleanup_tolerance = 0.025
        cleanup.solve(obj, scene)
        result = state.candidate_action
        self.assertIn('b4ml_cleanup_metrics', result)
        w.finish_preview(obj, scene, True)
        self.assertIs(state.kept_action, result)
        self.assertIsNone(state.cleanup_input)
        source_name = source.name
        filename = ROOT/'training/b4artists_ml/cache/cleanup-kept-v1.blend'
        name = obj.name
        bpy.ops.wm.save_as_mainfile(filepath=str(filename))
        bpy.ops.wm.open_mainfile(filepath=str(filename), load_ui=False, use_scripts=False)
        obj = bpy.data.objects[name]
        scene = bpy.context.scene
        bpy.context.view_layer.objects.active = obj
        self.assertIn('b4ml_cleanup_metrics', obj.animation_data.action)
        report = json.loads(obj.animation_data.action['b4ml_cleanup_metrics'])
        self.assertTrue(report['source_action_unchanged'])
        w.restore_kept_source(obj, scene)
        self.assertEqual(obj.animation_data.action.name, source_name)
        self.assertEqual(contacts._action_signature(obj), source_signature)

    def test_quadruped_contact_protection_and_remaining_control_cleanup(self):
        scene, obj, _, _, candidate, _, mapping = quadruped_candidate('cat')
        state = obj.b4ml
        name = mapping['fore-L']['ik']
        select_only(obj, name)
        state.cleanup_scope = 'SELECTED'
        before = flight._curve_token(obj, candidate)
        with self.assertRaisesRegex(ValueError, 'protected by accepted contacts'):
            cleanup.solve(obj, scene)
        self.assertIs(obj.animation_data.action, candidate)
        self.assertIs(state.candidate_action, candidate)
        self.assertEqual(flight._curve_token(obj, candidate), before)
        state.cleanup_scope = 'CAPTURED'
        step_ms = []
        step_phases = []
        cleanup.start(obj, scene)
        while True:
            began = time.perf_counter()
            done = cleanup.step(obj)
            step_ms.append((time.perf_counter()-began)*1000)
            step_phases.append(state.cleanup_progress or 'Complete')
            if done:
                break
        report = json.loads(state.cleanup_metrics)
        self.assertEqual(report['accepted_contacts'], 4)
        self.assertEqual(report['contact_samples'], 12)
        self.assertEqual(report['contact_sample_frames'], 3)
        self.assertEqual(report['contact_frame_evaluations'], 6)
        self.assertTrue(report['protected_contact_controls'])
        self.assertTrue(report['cleaned_controls'])
        self.assertGreater(report['keys_removed'], 0)
        self.assertLessEqual(report['max_contact_position_drift'], 2e-6)
        self.assertLessEqual(report['max_contact_rotation_drift_radians'], 2e-5)
        RECORDS.append(dict(report, fixture='quadruped-cat',
                            step_p95_ms=sorted(step_ms)[int(.95*(len(step_ms)-1))],
                            step_max_ms=max(step_ms), step_max_phase=step_phases[step_ms.index(max(step_ms))],
                            step_count=len(step_ms)))
        cleanup.restore(obj, scene)
        self.assertIs(state.candidate_action, candidate)
        self.assertEqual(flight._curve_token(obj, candidate), before)


if __name__ == '__main__':
    started = time.perf_counter()
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(CleanupRuntimeTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    report = dict(tests=result.testsRun, passed=result.wasSuccessful(),
                  failures=len(result.failures), errors=len(result.errors), skips=len(result.skipped),
                  records=RECORDS, elapsed_seconds=time.perf_counter()-started,
                  package=b4artists_ml.__file__)
    output = ROOT/'training/b4artists_ml/results/cleanup-v1.json'
    output.write_text(json.dumps(report, indent=2)+'\n')
    print('CLEANUP_RESULT: '+json.dumps(report), flush=True)
    if not result.wasSuccessful():
        raise SystemExit(1)
