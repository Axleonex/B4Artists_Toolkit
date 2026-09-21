"""Bulk contact review and proposal navigation on supported rig families."""
from pathlib import Path
import json
import os
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [os.environ.get('B4ML_PACKAGE', str(ROOT)), str(ROOT / 'tests')]

import addon_utils
import bpy

import b4artists_ml
from b4artists_ml import contacts, quadruped_contacts, ui
from test_b4artists_ml_contacts import fixture
from test_b4artists_ml_quadruped_contacts import _signature
from test_b4artists_ml_quadruped_suggestions import prepared as quadruped_prepared


def add_contact(obj, limb, review_state, start, *, enabled=True, end=None):
    item = obj.b4ml.contacts.add()
    item.name = f'{limb} {review_state.lower()} {start:g}'
    item.limb = limb
    item.review_state = review_state
    item.enabled = enabled
    item.start = start
    item.end = start + 1.0 if end is None else end
    item.confidence = .75
    item.provenance = 'TEST_REVIEW'
    item.reason = 'review control fixture'
    return len(obj.b4ml.contacts) - 1


class ContactReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        addon_utils.enable('rigify', default_set=True, persistent=False)
        b4artists_ml.register()

    def test_humanoid_bulk_review_preserves_mixed_states_and_animation(self):
        obj, source, _, _ = fixture('boneforge')
        candidate = obj.b4ml.candidate_action
        obj.b4ml.contacts.clear()
        proposed = [add_contact(obj, limb, 'PROPOSED', frame)
                    for limb, frame in (('leg-L', 2.0), ('leg-R', 5.0))]
        accepted = add_contact(obj, 'leg-L', 'ACCEPTED', 8.0, enabled=True)
        rejected = add_contact(obj, 'leg-R', 'REJECTED', 9.0, enabled=False)
        foreign = add_contact(obj, 'fore-L', 'PROPOSED', 3.0, enabled=True)
        before_candidate = _signature(obj, candidate)
        before_source = _signature(obj, source)

        self.assertEqual(bpy.ops.b4ml.contact(operation='ACCEPT_ALL'), {'FINISHED'})
        self.assertTrue(all(obj.b4ml.contacts[index].review_state == 'ACCEPTED'
                            and obj.b4ml.contacts[index].enabled for index in proposed))
        self.assertEqual((obj.b4ml.contacts[accepted].review_state,
                          obj.b4ml.contacts[accepted].enabled), ('ACCEPTED', True))
        self.assertEqual((obj.b4ml.contacts[rejected].review_state,
                          obj.b4ml.contacts[rejected].enabled), ('REJECTED', False))
        self.assertEqual(obj.b4ml.contacts[foreign].review_state, 'PROPOSED')
        self.assertEqual(ui._contact_review_counts(obj),
                         {'PROPOSED': 0, 'ACCEPTED': 3, 'REJECTED': 1})
        self.assertIn('Accepted 2 contact suggestions', obj.b4ml.status)
        self.assertEqual(_signature(obj, candidate), before_candidate)
        self.assertEqual(_signature(obj, source), before_source)
        self.assertIs(obj.animation_data.action, candidate)
        self.assertIn('UNDO', ui.B4ML_OT_contact.bl_options)

        snapshot = contacts._contact_signature(obj)
        with self.assertRaisesRegex(RuntimeError, 'No compatible proposed'):
            bpy.ops.b4ml.contact(operation='ACCEPT_ALL')
        self.assertEqual(contacts._contact_signature(obj), snapshot)
        add_contact(obj, 'arm-L', 'PROPOSED', 10.25)
        self.assertEqual(bpy.ops.b4ml.contact(operation='REJECT_ALL'), {'FINISHED'})
        self.assertEqual(ui._contact_review_counts(obj),
                         {'PROPOSED': 0, 'ACCEPTED': 3, 'REJECTED': 2})
        self.assertEqual(_signature(obj, candidate), before_candidate)
        self.assertEqual(_signature(obj, source), before_source)

    def test_quadruped_bulk_review_filters_humanoid_rows(self):
        scene, obj, source, source_signature, candidate, candidate_signature, _ = quadruped_prepared('cat')
        paw_indices = [add_contact(obj, limb, 'PROPOSED', frame)
                       for limb, frame in zip(quadruped_contacts.LIMBS, (1.0, 3.0, 5.0, 7.0))]
        humanoid = add_contact(obj, 'leg-L', 'PROPOSED', 2.0)

        self.assertEqual(bpy.ops.b4ml.contact(operation='ACCEPT_ALL'), {'FINISHED'})
        self.assertTrue(all(obj.b4ml.contacts[index].review_state == 'ACCEPTED'
                            for index in paw_indices))
        self.assertEqual(obj.b4ml.contacts[humanoid].review_state, 'PROPOSED')
        self.assertEqual(len(quadruped_contacts.rows(obj)), 4)
        self.assertEqual(_signature(obj, candidate), candidate_signature)
        self.assertEqual(_signature(obj, source), source_signature)
        self.assertIs(obj.animation_data.action, candidate)
        self.assertAlmostEqual(scene.frame_current + scene.frame_subframe, 6.0)

    def test_navigation_is_fractional_cyclic_and_animation_neutral(self):
        obj, source, _, _ = fixture('boneforge')
        scene = bpy.context.scene
        candidate = obj.b4ml.candidate_action
        obj.b4ml.contacts.clear()
        late = add_contact(obj, 'leg-R', 'PROPOSED', 9.75)
        early = add_contact(obj, 'leg-L', 'PROPOSED', 1.25)
        middle = add_contact(obj, 'leg-R', 'PROPOSED', 5.5)
        add_contact(obj, 'leg-L', 'ACCEPTED', 4.0)
        add_contact(obj, 'leg-R', 'REJECTED', 7.0, enabled=False)
        add_contact(obj, 'fore-R', 'PROPOSED', 3.0)
        before_candidate = _signature(obj, candidate)
        before_source = _signature(obj, source)

        obj.b4ml.contact_index = early
        expected = ((middle, 5.5, 'NEXT_PROPOSED'),
                    (late, 9.75, 'NEXT_PROPOSED'),
                    (early, 1.25, 'NEXT_PROPOSED'),
                    (late, 9.75, 'PREVIOUS_PROPOSED'))
        for index, frame, operation in expected:
            self.assertEqual(bpy.ops.b4ml.contact(operation=operation), {'FINISHED'})
            self.assertEqual(obj.b4ml.contact_index, index)
            self.assertAlmostEqual(scene.frame_current + scene.frame_subframe, frame)
        self.assertIn('3/3', obj.b4ml.status)
        self.assertEqual(_signature(obj, candidate), before_candidate)
        self.assertEqual(_signature(obj, source), before_source)
        self.assertIs(obj.animation_data.action, candidate)

        self.assertEqual(bpy.ops.b4ml.contact(operation='ACCEPT_ALL'), {'FINISHED'})
        snapshot = contacts._contact_signature(obj)
        with self.assertRaisesRegex(RuntimeError, 'No compatible proposed'):
            bpy.ops.b4ml.contact(operation='NEXT_PROPOSED')
        self.assertEqual(contacts._contact_signature(obj), snapshot)
        self.assertEqual(_signature(obj, candidate), before_candidate)


if __name__ == '__main__':
    result = unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(ContactReviewTests))
    report = {'tests': result.testsRun, 'passed': result.wasSuccessful(),
              'failures': len(result.failures), 'errors': len(result.errors),
              'package': b4artists_ml.__file__}
    path = ROOT / 'training/b4artists_ml/results' / os.environ.get(
        'B4ML_CONTACT_REVIEW_RESULT', 'contact-review-v1.json')
    path.write_text(json.dumps(report, indent=2) + '\n')
    print('CONTACT_REVIEW_RESULT: ' + json.dumps(report), flush=True)
    if not result.wasSuccessful():
        raise SystemExit(1)
