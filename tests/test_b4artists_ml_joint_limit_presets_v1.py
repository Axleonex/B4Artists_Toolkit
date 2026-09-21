"""Opt-in humanoid joint-limit presets, provenance, overrides and recovery."""
from pathlib import Path
import json
import math
import os
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [os.environ.get('B4ML_PACKAGE', str(ROOT)), str(ROOT / 'tests')]
import bpy
import b4artists_ml
from b4artists_ml import body_preview as body, body_solver as solver, joint_limits as limits, workflow as w
from test_b4artists_ml_context_rig import ContextRigTests
from test_b4artists_ml_imported_humanoids import authored

RECORDS = []


class JointLimitPresetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ContextRigTests.setUpClass()
        cls.fixtures = ContextRigTests()

    def tearDown(self):
        for ob in list(bpy.data.objects):
            if hasattr(ob, 'b4ml') and ob.b4ml.body_payload:
                if not ob.users_scene:
                    continue
                bpy.context.window.scene = ob.users_scene[0]
                bpy.context.view_layer.objects.active = ob
                body.finish(ob, bpy.context.scene, False)
        for session in list(solver._SESSIONS.values()):
            if not session.closed:
                session.cancel()
        body.reset_runtime()

    def preview(self, label):
        if label == 'unity_humanoid':
            ob, _, _ = authored(label, variant=1)
            source = w.raw_pose(ob)
            body.begin(ob, bpy.context.scene)
            return ob, source
        ob, source, session, _, _ = self.fixtures.fixture(label, transformed=True)
        session.cancel()
        bpy.context.view_layer.objects.active = ob
        body.begin(ob, bpy.context.scene)
        return ob, source

    def test_catalog_is_finite_validated_and_explicitly_nonclinical(self):
        rows = []
        for role in ('hips', 'spine.01', 'chest', 'neck', 'head', 'clavicle.fk-L',
                     'upperarm.fk-L', 'forearm.fk-L', 'hand.fk-L',
                     'thigh.fk-L', 'shin.fk-L', 'foot.fk-L'):
            row = limits.preset_values(role, True)
            self.assertEqual(row['space'], 'JOINT')
            self.assertTrue(row['enabled'])
            self.assertFalse(row['use_bend_plane'])
            self.assertTrue(all(math.isfinite(row[key]) for key in ('swing', 'twist_min', 'twist_max')))
            limits.validate({role: {key: row[key] for key in ('space', 'swing', 'twist_min', 'twist_max')}}, {role})
            rows.append(row)
        self.assertIsNone(limits.preset_values('unknown.helper', False))
        with self.assertRaisesRegex(ValueError, 'Unknown joint-limit preset'):
            limits.preset_values('head', True, 'NOT_A_PRESET')
        RECORDS.append(dict(case='catalog', rows=len(rows), learned=False, clinical_anatomy=False))

    def test_boneforge_rigify_and_imported_adapters_apply_semantically(self):
        for label in ('boneforge', 'rigify_basic', 'rigify_default',
                      'metarig_basic', 'metarig_default', 'unity_humanoid'):
            with self.subTest(rig=label):
                ob, source = self.preview(label)
                before = w.raw_pose(ob)
                report = body.apply_limit_preset(ob)
                self.assertEqual(report['preset'], limits.PRESET_ID)
                self.assertFalse(report['learned'])
                self.assertFalse(report['clinical_anatomy'])
                self.assertGreater(len(report['applied']), 12)
                for row in report['applied']:
                    item = ob.b4ml.body_limits[row['control']]
                    self.assertTrue(item.enabled)
                    self.assertEqual(item.preset_provenance, limits.PRESET_PROVENANCE)
                    self.assertEqual(item.space, 'JOINT' if item.joint_available else 'CONTROL')
                self.assertEqual(w.raw_pose(ob), before)
                RECORDS.append(dict(case='adapter', fixture=label, applied=len(report['applied']),
                                    skipped=len(report['skipped']), profile=report['profile']))
                body.finish(ob, bpy.context.scene, False)

    def test_applied_preset_participates_in_an_actual_solve(self):
        for label in ('boneforge', 'rigify_default'):
            with self.subTest(rig=label):
                ob, source = self.preview(label)
                report = body.apply_limit_preset(ob)
                for target in ob.b4ml.body_targets:
                    target.enabled = target.name == 'Pelvis'
                body.solve(ob)
                record = json.loads(ob.b4ml.body_payload)
                self.assertEqual(record['metrics']['requested_joint_limits'], len(report['applied']))
                self.assertLess(record['metrics']['joint_limit_error_radians'], .001)
                self.assertEqual(record['signature']['joint_limits'].keys(),
                                 {row['control'] for row in report['applied']})
                RECORDS.append(dict(case='solve', fixture=label,
                                    requested_limits=record['metrics']['requested_joint_limits'],
                                    limit_error=record['metrics']['joint_limit_error_radians']))
                body.finish(ob, bpy.context.scene, False)
                self.assertEqual(w.raw_pose(ob), source)

    def test_manual_edit_marks_override_and_survives_preview_restart(self):
        ob, source = self.preview('rigify_default')
        body.apply_limit_preset(ob)
        item = next(item for item in ob.b4ml.body_limits if item.enabled)
        name = item.name
        item.swing *= .9
        self.assertEqual(item.preset_provenance, 'Custom override')
        edited = item.swing
        body.finish(ob, bpy.context.scene, False)
        self.assertEqual(w.raw_pose(ob), source)
        body.begin(ob, bpy.context.scene)
        item = ob.b4ml.body_limits[name]
        self.assertAlmostEqual(item.swing, edited, places=6)
        self.assertEqual(item.preset_provenance, 'Custom override')

    def test_running_solve_refuses_preset_without_mutating_settings_or_pose(self):
        ob, _ = self.preview('boneforge')
        body.apply_limit_preset(ob)
        settings = [(item.name, item.enabled, item.space, item.swing, item.twist_min,
                     item.twist_max, item.preset_provenance) for item in ob.b4ml.body_limits]
        pose = w.raw_pose(ob)
        body.start(ob)
        body.step(ob)
        with self.assertRaisesRegex(ValueError, 'running solve'):
            body.apply_limit_preset(ob)
        self.assertEqual(settings, [(item.name, item.enabled, item.space, item.swing,
                                     item.twist_min, item.twist_max, item.preset_provenance)
                                    for item in ob.b4ml.body_limits])
        body.abort(ob)
        self.assertEqual(w.raw_pose(ob), pose)


def run_ui_smoke():
    """Reuse the established real-window modal/undo journey with the preset active."""
    import test_b4artists_ml_context_preview as preview_tests
    preview_tests.VERSION = 'joint-limit-presets-v5'
    os.environ['B4ML_UI_RIG'] = 'boneforge'
    original_begin = preview_tests.PreviewTests.begin
    original_step = body.step

    def begin(test, ob, targets):
        original_begin(test, ob, targets)
        report = body.apply_limit_preset(ob)
        assert len(report['applied']) == 20
        for target in ob.b4ml.body_targets:
            target.enabled = target.name == 'Pelvis'
        ob.b4ml.show_body_targets = False
        ob.b4ml.show_body_limits = True

    def checked_step(ob):
        done = original_step(ob)
        if done:
            record = json.loads(ob.b4ml.body_payload)
            assert record['metrics']['requested_joint_limits'] == 20
            assert record['metrics']['joint_limit_error_radians'] < .001
            assert all(item.preset_provenance == limits.PRESET_PROVENANCE
                       for item in ob.b4ml.body_limits if item.enabled)
        return done

    preview_tests.PreviewTests.begin = begin
    body.step = checked_step
    preview_tests.run_ui_smoke()


if __name__ == '__main__' and '--ui-smoke' in sys.argv:
    run_ui_smoke()
elif __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(JointLimitPresetTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    report = dict(tests=result.testsRun, passed=result.wasSuccessful(),
                  failures=len(result.failures), errors=len(result.errors), records=RECORDS,
                  package=b4artists_ml.__file__)
    output = ROOT / 'training/b4artists_ml/results' / os.environ.get('B4ML_PRESET_RESULT', 'joint-limit-presets-v1.json')
    output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print('JOINT_LIMIT_PRESET_RESULT: ' + json.dumps(report), flush=True)
    if not result.wasSuccessful():
        raise SystemExit(1)
