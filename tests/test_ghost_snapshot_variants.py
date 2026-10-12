"""Variant independence, real host curve history and atomic restoration."""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_ghost_snapshot_targets import SnapshotTargets, bpy, ghost_tool, fc
from ghost_tool.snapshot import SnapshotStore


class SnapshotVariants(unittest.TestCase):
    setUpClass = classmethod(SnapshotTargets.setUpClass.__func__)
    tearDownClass = classmethod(SnapshotTargets.tearDownClass.__func__)
    setUp = SnapshotTargets.setUp
    tearDown = SnapshotTargets.tearDown
    activate = SnapshotTargets.activate
    capture = SnapshotTargets.capture
    _drop_deferred_timer = SnapshotTargets._drop_deferred_timer

    def test_variant_origin_and_payload_survive_parent_delete(self):
        parent = self.capture()
        old = parent.to_dict()
        curve = fc.resolve_fcurve(self.a, '', 'location.x')
        curve.keyframe_points[0].co.y = 8
        curve.update()
        self.assertEqual(len(self.store.get_all()), 1)
        child = self.store.take_variant('', self.scene, parent.uid, context=bpy.context, scope='ACTIVE')
        self.assertEqual(parent.to_dict(), old)
        self.assertNotEqual(child.curve_data, parent.curve_data)
        saved = child.to_dict()
        self.store.delete_snapshot(parent.uid)
        self.assertEqual(self.store.get_by_uid(child.uid).to_dict(), saved)
        self.assertEqual(child.origin['name'], parent.name)

    def test_variant_wrong_scope_refuses_without_creating_child(self):
        parent = self.capture()
        self.activate(self.b)
        with self.assertRaisesRegex(ValueError, 'scope'):
            self.store.take_variant('', self.scene, parent.uid, context=bpy.context, scope='ACTIVE')
        self.assertEqual(len(self.store.get_all()), 1)

    def test_show_hide_never_changes_animation_or_payload(self):
        snap = self.capture()
        curve = fc.resolve_fcurve(self.a, '', 'location.x')
        before = fc.snapshot_fcurve(curve)
        payload = snap.curve_data.copy()
        for _ in range(4):
            bpy.ops.ghost_tool.toggle_snapshot(snapshot_uid=snap.uid)
            self.store.get_visible()
        self.assertEqual(fc.snapshot_fcurve(curve), before)
        self.assertEqual(snap.curve_data, payload)

    def test_later_write_failure_rolls_back_all_curves(self):
        snap = self.capture()
        curves = [fc.resolve_fcurve(self.a, '', c) for c in ('location.x', 'location.y')]
        for curve in curves:
            curve.keyframe_points[0].co.y += 7
            curve.update()
        before = [fc.snapshot_fcurve(c) for c in curves]
        original = fc.restore_fcurve
        calls = []
        def fail_second(curve, keys):
            calls.append(curve)
            if len(calls) == 2:
                curve.keyframe_points[0].co.y = 99
                return False
            return original(curve, keys)
        with patch.object(fc, 'restore_fcurve', side_effect=fail_second):
            self.assertFalse(self.store.restore_snapshot(snap.uid, self.scene))
        self.assertEqual([fc.snapshot_fcurve(c) for c in curves], before)

    def test_freed_curve_address_reuse_writes_only_the_original_channel(self):
        snap = self.capture()
        captured = snap.curve_data[0]['keys']
        bag = self.a.animation_data.action.layers[0].strips[0].channelbag(self.a.animation_data.action_slot)
        bag.fcurves.remove(fc.resolve_fcurve(self.a, '', 'location.x'))
        curve = bag.fcurves.new('location', index=0)
        curve.keyframe_points.insert(1, 123)
        # Curves carry no persistent tag (it would block Cycles). A new curve
        # at a new address is refused; at a reused address it is the same
        # channel, so only the captured keys of that channel may be written.
        if self.store.restore_snapshot(snap.uid, self.scene):
            self.assertEqual(fc.snapshot_fcurve(fc.resolve_fcurve(self.a, '', 'location.x')), captured)
        else:
            self.assertEqual(curve.evaluate(1), 123)

    def test_capture_keeps_curve_evaluation_and_allows_cycles(self):
        curve = fc.resolve_fcurve(self.a, '', 'location.x')
        frames = [-20, 1, 5.5, 10, 20, 45]
        before = [curve.evaluate(f) for f in frames]
        snap = self.capture()
        self.assertEqual([curve.evaluate(f) for f in frames], before)
        self.assertEqual(len(curve.modifiers), 0)
        # Blender only accepts Cycles as the first modifier (Make Cyclic).
        self.assertIsNotNone(curve.modifiers.new('CYCLES'))
        self.assertEqual(snap.bindings[0].resolve(self.scene)[1], '')

    def test_legacy_identity_tags_are_removed_and_references_still_restore(self):
        from ghost_tool import snapshot_storage, target_binding
        snap = self.capture()
        curve = fc.resolve_fcurve(self.a, '', 'location.x')
        tag = curve.modifiers.new('LIMITS')
        tag.mute = True
        tag.name = target_binding.CURVE_TAG + 'legacy'
        snapshot_storage.remove_stale_curve_tags()
        self.assertEqual(len(curve.modifiers), 0)
        self.assertTrue(self.store.restore_snapshot(snap.uid, self.scene))

    def test_legacy_sampled_restore_skips_samples_it_cannot_reshape(self):
        snap = self.capture()
        legacy = snap.to_dict()
        legacy['curve_data'] = []
        outside = dict(legacy['ghost_data'][0])
        outside['frame'] = 45.0  # beyond the last key: no segment to reshape
        legacy['ghost_data'].append(outside)
        self.store.load_from_dict_list([legacy])
        self.store.bind_snapshot(snap.uid, self.scene, self.a)
        self.assertTrue(self.store.restore_snapshot(snap.uid, self.scene), self.store.last_error)

    def test_restore_operator_actual_undo_and_redo(self):
        snap = self.capture()
        name = self.a.name
        original = fc.snapshot_fcurve(fc.resolve_fcurve(self.a, '', 'location.x'))
        curve = fc.resolve_fcurve(self.a, '', 'location.x')
        curve.keyframe_points[0].co.y += 5
        curve.update()
        edited = fc.snapshot_fcurve(curve)
        bpy.ops.ed.undo_push(message='Before Ghost restore')
        self.assertEqual(bpy.ops.ghost_tool.restore_snapshot('EXEC_DEFAULT', True, snapshot_uid=snap.uid), {'FINISHED'})
        self.assertEqual(fc.snapshot_fcurve(fc.resolve_fcurve(bpy.data.objects[name], '', 'location.x')), original)
        self.assertEqual(bpy.ops.ed.undo(), {'FINISHED'})
        self.assertEqual(fc.snapshot_fcurve(fc.resolve_fcurve(bpy.data.objects[name], '', 'location.x')), edited)
        self.assertEqual(bpy.ops.ed.redo(), {'FINISHED'})
        self.assertEqual(fc.snapshot_fcurve(fc.resolve_fcurve(bpy.data.objects[name], '', 'location.x')), original)


if __name__ == '__main__':
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(SnapshotVariants))
    if not result.wasSuccessful():
        raise RuntimeError('Snapshot variant checks failed')
