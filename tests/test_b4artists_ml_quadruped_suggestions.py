"""Native reviewed paw discovery, correction, rejection and lifecycle checks."""
from pathlib import Path
import hashlib
import json
import os
import sys
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [os.environ.get('B4ML_PACKAGE', str(ROOT)), str(ROOT / 'tests')]
import addon_utils
import bpy
from mathutils import Vector
import b4artists_ml
from b4artists_ml import contacts, quadruped_contacts as qc, workflow as w
from test_b4artists_ml_quadruped_contacts import _candidate, _signature

RECORDS = []


def prepared(profile='horse'):
    scene, obj, source, source_signature, candidate, signature, mapping = _candidate(profile)
    points = [Vector(item.point) for item in obj.b4ml.contacts]
    obj.b4ml.contacts.clear()
    obj.b4ml.support_plane_point = sum(points, Vector()) / len(points)
    obj.b4ml.support_plane_normal = (0, 0, 1)
    obj.b4ml.contact_suggest_distance = .2
    obj.b4ml.contact_suggest_speed = .001
    obj.b4ml.contact_suggest_min_frames = 3
    obj.b4ml.contact_suggest_gap_frames = 0
    return scene, obj, source, source_signature, candidate, signature, points


class QuadrupedSuggestionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        addon_utils.enable('rigify', default_set=True, persistent=False)
        b4artists_ml.register()

    def test_three_profiles_review_to_correction_preserves_source(self):
        for profile in ('cat', 'horse', 'wolf'):
            with self.subTest(profile=profile):
                scene, obj, source, source_signature, candidate, signature, _ = prepared(profile)
                pose = w.raw_pose(obj)
                started = time.perf_counter()
                self.assertEqual(bpy.ops.b4ml.contact_suggest(), {'FINISHED'})
                report = json.loads(obj.b4ml.contact_suggestion_report)
                self.assertEqual(report['family'], 'quadruped')
                self.assertEqual(report['suggestions'], 4)
                self.assertEqual(set(report['limbs']), set(qc.LIMBS))
                self.assertFalse(report['learned'])
                self.assertFalse(report['gait_inference'])
                self.assertEqual(qc.rows(obj), [])
                self.assertEqual(w.raw_pose(obj), pose)
                self.assertEqual(scene.frame_current, 6)
                self.assertEqual(_signature(obj, candidate), signature)
                for i, item in enumerate(obj.b4ml.contacts):
                    self.assertEqual(item.review_state, 'PROPOSED')
                    self.assertEqual(item.provenance, 'AUTHORED_PLANE')
                    self.assertIn('matching grounded priority poses', item.reason)
                    obj.b4ml.contact_index = i
                    self.assertEqual(bpy.ops.b4ml.contact(operation='ACCEPT'), {'FINISHED'})
                self.assertEqual(bpy.ops.b4ml.contact_solve(), {'FINISHED'})
                fit = json.loads(obj.b4ml.contact_metrics)
                self.assertEqual(fit['contacts'], 4)
                self.assertLessEqual(fit['max_after'], 2e-4)
                self.assertEqual(_signature(obj, candidate), signature)
                qc.restore_before_contacts(obj, scene)
                w.finish_preview(obj, scene, keep=False)
                self.assertIs(obj.animation_data.action, source)
                self.assertEqual(_signature(obj, source), source_signature)
                RECORDS.append(dict(profile=profile, scan=report, correction=fit,
                                    source_restored=True, seconds=time.perf_counter()-started))

    def test_bounded_surface_and_rejected_proposals(self):
        scene, obj, _, _, candidate, signature, points = prepared()
        center = sum(points, Vector()) / len(points)
        bpy.ops.mesh.primitive_plane_add(size=20, location=center)
        surface = bpy.context.object
        obj.b4ml.contact_surface = surface
        bpy.context.view_layer.objects.active = obj
        report = contacts.suggest(obj, scene)
        self.assertEqual(report['suggestions'], 4)
        self.assertTrue(report['surface'].startswith('STATIC_PLANAR_MESH:'))
        obj.b4ml.contact_index = 0
        self.assertEqual(bpy.ops.b4ml.contact(operation='REJECT'), {'FINISHED'})
        self.assertEqual(qc.rows(obj), [])
        surface.location.x += 100
        self.assertEqual(contacts.suggest(obj, scene)['suggestions'], 0)
        self.assertEqual(len(obj.b4ml.contacts), 0)
        self.assertIs(obj.animation_data.action, candidate)
        self.assertEqual(_signature(obj, candidate), signature)

    def test_cancel_and_changed_frame_rate_publish_nothing(self):
        scene, obj, _, _, candidate, signature, _ = prepared()
        contacts.suggest_start(obj, scene)
        self.assertFalse(contacts.suggest_step(obj))
        contacts.suggest_abort(obj)
        self.assertFalse(obj.b4ml.contact_suggest_running)
        contacts.suggest_start(obj, scene)
        while not obj.b4ml.contact_suggest_progress.startswith('Preparing rig mapping'):
            self.assertFalse(contacts.suggest_step(obj))
        scene.render.fps += 1
        try:
            with self.assertRaisesRegex(ValueError, 'Frame rate changed'):
                contacts.suggest_step(obj)
        finally:
            scene.render.fps -= 1
        self.assertEqual(len(obj.b4ml.contacts), 0)
        self.assertFalse(obj.b4ml.contact_suggest_running)
        self.assertIs(obj.animation_data.action, candidate)
        self.assertEqual(_signature(obj, candidate), signature)
        self.assertEqual(scene.frame_current, 6)

    def test_proposals_survive_reload_and_accepted_holds_survive_rescan(self):
        scene, obj, _, _, _, _, _ = prepared()
        contacts.suggest(obj, scene)
        obj.b4ml.contact_index = 0
        bpy.ops.b4ml.contact(operation='ACCEPT')
        accepted = contacts._contact_signature(obj)[0]
        name = obj.name
        path = ROOT / 'training/b4artists_ml/cache/quadruped-suggestions-reload.blend'
        bpy.ops.wm.save_as_mainfile(filepath=str(path))
        bpy.ops.wm.open_mainfile(filepath=str(path), use_scripts=False)
        obj = bpy.data.objects[name]
        bpy.context.view_layer.objects.active = obj
        self.assertEqual(contacts._contact_signature(obj)[0], accepted)
        self.assertEqual(sum(i.review_state == 'PROPOSED' for i in obj.b4ml.contacts), 3)
        self.assertEqual(len(qc.rows(obj)), 1)
        report = contacts.suggest(obj, bpy.context.scene)
        self.assertEqual(report['accepted_preserved'], 1)
        self.assertEqual(contacts._contact_signature(obj)[0], accepted)

    def test_early_input_edits_cancel_before_publication(self):
        scene, obj, _, _, candidate, signature, _ = prepared()
        changes = (
            ('Frame rate changed', lambda: setattr(scene.render, 'fps', scene.render.fps + 1),
             lambda: setattr(scene.render, 'fps', scene.render.fps - 1)),
            ('Priority poses changed', lambda: setattr(obj.b4ml.anchors[0], 'frame', 1.25),
             lambda: setattr(obj.b4ml.anchors[0], 'frame', 1.0)),
            ('Rig transform changed', lambda: setattr(obj.location, 'x', 1.0),
             lambda: setattr(obj.location, 'x', 0.0)),
        )
        for message, change, undo in changes:
            with self.subTest(input=message):
                contacts.suggest_start(obj, scene)
                self.assertFalse(contacts.suggest_step(obj))
                change()
                bpy.context.view_layer.update()
                try:
                    with self.assertRaisesRegex(ValueError, message):
                        while not contacts.suggest_step(obj):
                            pass
                    self.assertEqual(len(obj.b4ml.contacts), 0)
                    self.assertFalse(obj.b4ml.contact_suggest_running)
                    self.assertIs(obj.animation_data.action, candidate)
                    self.assertEqual(_signature(obj, candidate), signature)
                    self.assertEqual(scene.frame_current, 6)
                finally:
                    contacts.suggest_abort(obj)
                    obj.b4ml.contacts.clear()
                    undo()
                    bpy.context.view_layer.update()

    def test_fractional_priority_frame_is_sampled(self):
        scene, obj, _, _, candidate, signature, _ = prepared()
        anchor = obj.b4ml.anchors.add()
        anchor.frame = 5.5
        anchor.payload = obj.b4ml.anchors[0].payload
        report = contacts.suggest(obj, scene)
        self.assertEqual(report['frames'], 12)
        self.assertIs(obj.animation_data.action, candidate)
        self.assertEqual(_signature(obj, candidate), signature)
        self.assertEqual(scene.frame_current, 6)


if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(QuadrupedSuggestionTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    report = dict(passed=result.wasSuccessful(), tests=result.testsRun,
                  failures=[(t.id(), trace) for t, trace in result.failures],
                  errors=[(t.id(), trace) for t, trace in result.errors], records=RECORDS,
                  runtime_sha256={p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                  for p in Path(b4artists_ml.__file__).parent.glob('*.py')},
                  full_goal_complete=False, human_reviews=0, cascadeur_comparisons=0)
    output = Path(os.environ['B4ML_PAW_SUGGEST_REPORT'])
    output.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    if not result.wasSuccessful():
        raise SystemExit(1)
