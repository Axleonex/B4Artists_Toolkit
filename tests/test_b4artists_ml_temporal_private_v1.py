"""Private temporal generation: output equivalence, source edits and lifecycle."""
from pathlib import Path
import sys, unittest
from unittest.mock import patch
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT/'tests'), str(ROOT/'training/b4artists_ml')]
import bpy
from b4artists_ml import temporal_generation as g, temporal_private as private
from b4artists_ml import temporal_math, workflow as w, posing as p, body_solver as solver
from test_b4artists_ml_temporal_cooperative import CooperativeTemporalTests
from test_b4artists_ml_anchor_observations import AnchorObservationTests


class PrivateTemporalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        AnchorObservationTests.setUpClass()
        cls.helper = CooperativeTemporalTests()
        cls.helper.helper = AnchorObservationTests()

    def setUp(self):
        g.register()

    def tearDown(self):
        g.before_host_change()

    def fixture(self, label='boneforge'):
        ob, binding = self.helper.fixture(label)
        return ob, binding, self.helper.visible(ob), self.helper.inventory()

    def job(self, ob, **options):
        return private.PrivateJob(ob, lambda o,t:o.baseline(t),
            dict(context=False, prepare_predictor=temporal_math.prepare, **options),
            chunk_seconds=0)

    def advance(self, ob, job, phase):
        before = self.helper.visible(ob)
        for _ in range(3000):
            progress = next(job)
            self.assertEqual(self.helper.visible(ob), before)
            if progress['phase'] == phase:
                return
        self.fail('Missing private stage: ' + phase)

    def clean(self, ob, before, inventory):
        self.assertEqual(self.helper.visible(ob), before)
        self.assertEqual(self.helper.inventory(), inventory)
        self.assertFalse(g._LIVE)
        self.assertFalse(g._OWNERS)
        self.assertNotIn(ob.as_pointer(), solver._SESSIONS)

    def test_all_existing_rig_profiles_match_guarded_generation(self):
        for label in self.helper.helper.builders:
            with self.subTest(profile=label):
                ob, _, before, inventory = self.fixture(label)
                expected, _ = g.generate_samples(ob, lambda o,t:o.baseline(t),
                    context=False, prepare_predictor=temporal_math.prepare)
                (actual, _), _, _ = self.helper.consume(ob,
                    g.generate_private_steps(ob, lambda o,t:o.baseline(t),
                        context=False, prepare_predictor=temporal_math.prepare))
                self.helper.compare(actual, expected)
                for frame, row in w.read_anchors(ob):
                    self.assertEqual(actual[frame], row['pose'])
                self.clean(ob, before, inventory)
                w.preview(ob, bpy.context.scene, pose_samples=actual)
                w.finish_preview(ob, bpy.context.scene, False)
                self.clean(ob, before, inventory)

    def test_cancel_and_host_change_at_preparation_and_solve_boundaries(self):
        for phase in ('preparing_copy', 'preparing_scene', 'preparing_prune',
                      'working_rig_ready', 'observing', 'derivatives'):
            for lifecycle in (False, True):
                with self.subTest(phase=phase, lifecycle=lifecycle):
                    ob, _, before, inventory = self.fixture()
                    job = self.job(ob)
                    self.advance(ob, job, phase)
                    if lifecycle:
                        g.before_host_change()
                    else:
                        job.cancel()
                    with self.assertRaises(InterruptedError):
                        next(job)
                    self.clean(ob, before, inventory)

    def test_intervening_edits_reject_and_preserve_new_state(self):
        for edit in ('pose', 'frame', 'curve', 'anchor', 'fps', 'object', 'rotation_mode'):
            with self.subTest(edit=edit):
                ob, binding, _, inventory = self.fixture()
                job = self.job(ob)
                self.advance(ob, job, 'derivatives')
                root = ob.pose.bones[binding['root']]
                scene = bpy.context.scene
                if edit == 'pose': root.location.y += .125; p._update(ob)
                elif edit == 'frame': scene.frame_set(9, subframe=.125)
                elif edit == 'curve': root.keyframe_insert('location', frame=4)
                elif edit == 'anchor': ob.b4ml.anchors[0].frame += .125
                elif edit == 'fps': scene.render.fps = 24
                elif edit == 'object': ob.location.y += .125; p._update(ob)
                else: root.rotation_mode = 'XYZ'; root.rotation_euler.x = .125; p._update(ob)
                changed = self.helper.visible(ob)
                with self.assertRaisesRegex(ValueError, 'changed'):
                    next(job)
                job.close()
                self.clean(ob, changed, inventory)

    def test_foreign_workflow_started_while_paused_rejects_and_preserves_state(self):
        for attribute in ('body_running', 'body_live', 'contact_suggest_running',
                          'secondary_running', 'cleanup_running'):
            with self.subTest(workflow=attribute):
                ob, _, before, inventory = self.fixture()
                job = self.job(ob)
                self.advance(ob, job, 'derivatives')
                setattr(ob.b4ml, attribute, True)
                try:
                    with self.assertRaisesRegex(ValueError, 'Another animation workflow'):
                        next(job)
                    job.close()
                    self.clean(ob, before, inventory)
                finally:
                    setattr(ob.b4ml, attribute, False)

    def test_direct_close_preserves_newer_source_pose(self):
        ob, binding, _, inventory = self.fixture('rigify_basic')
        job = self.job(ob)
        self.advance(ob, job, 'derivatives')
        ob.pose.bones[binding['root']].location.y += .125
        p._update(ob)
        changed = self.helper.visible(ob)
        job.close()
        self.clean(ob, changed, inventory)

    def test_failed_copy_preparation_recovers_resources(self):
        ob, _, before, inventory = self.fixture()
        job = self.job(ob)
        with patch.object(private.body_proxy.EvaluationProxy, 'update',
                          side_effect=RuntimeError('injected copy failure')):
            with self.assertRaisesRegex(RuntimeError, 'copy failure'):
                while True: next(job)
        self.clean(ob, before, inventory)

    def test_fallback_keeps_existing_guarded_path(self):
        ob, _, before, inventory = self.fixture()
        with patch.object(private.body_proxy, 'dependency_bones',
                          side_effect=ValueError('unsupported copy dependency')):
            job = g.generate_private_steps(ob, lambda o,t:o.baseline(t), context=False)
        self.assertEqual(job.execution_path, 'guarded_source')
        self.helper.consume(ob, job)
        self.clean(ob, before, inventory)

    def test_duplicate_private_owner_cannot_cancel_first_job(self):
        ob, _, before, inventory = self.fixture()
        first = self.job(ob)
        with self.assertRaisesRegex(ValueError, 'already owns'):
            self.job(ob)
        self.assertIs(g._OWNERS[ob.as_pointer()], first.guard)
        first.close()
        self.clean(ob, before, inventory)

    def test_private_provider_error_does_not_publish_or_change_source(self):
        ob, _, before, inventory = self.fixture()
        def fail(*args):
            raise RuntimeError('injected provider failure')
        job = private.PrivateJob(ob, fail, dict(context=False))
        with self.assertRaisesRegex(RuntimeError, 'provider failure'):
            while True: next(job)
        self.clean(ob, before, inventory)
        self.assertFalse(ob.b4ml.candidate_action)

    def test_invalid_chunk_budget_rejects_without_ownership(self):
        ob, _, before, inventory = self.fixture()
        for budget in (-1, .11, float('nan'), float('inf')):
            with self.assertRaises(ValueError):
                private.PrivateJob(ob, lambda o,t:o.baseline(t), {}, chunk_seconds=budget)
        self.clean(ob, before, inventory)
