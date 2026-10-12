"""Actual host scope and identity behavior, including deliberate legacy binding."""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_ghost_paths import GhostPaths, _cube, _rig, bpy, ghost_tool
from ghost_tool.ghost_data import Ghost, GhostStore
from ghost_tool.snapshot import GhostSnapshot, SnapshotStore
from ghost_tool import fcurve_utils as fc, settings_editor


class SnapshotTargets(unittest.TestCase):
    _drop_deferred_timer = GhostPaths._drop_deferred_timer

    @classmethod
    def setUpClass(cls):
        with patch.object(ghost_tool, '_clear_pycache'):
            ghost_tool.register()

    @classmethod
    def tearDownClass(cls):
        ghost_tool.unregister()

    def setUp(self):
        GhostPaths.setUp(self)
        self.store = SnapshotStore.get(self.scene)
        self.store.load_from_dict_list([])
        self.a = _cube('Original')
        self.b = _cube('Other')
        for obj in (self.a, self.b):
            for channel in ('location.x', 'location.y'):
                GhostStore.get(self.scene).add(Ghost(frame=10, object_name=obj.name, channel=channel))
        self.activate(self.a)

    def tearDown(self):
        self._drop_deferred_timer()

    def activate(self, obj):
        if bpy.context.object and bpy.context.object.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        for candidate in self.scene.objects:
            candidate.select_set(candidate == obj)
        bpy.context.view_layer.objects.active = obj

    def capture(self, mode='ACTIVE'):
        return self.store.take_snapshot('Reference', self.scene, context=bpy.context, scope=mode)[0]

    def test_active_scope_filters_samples_and_complete_curves(self):
        snap = self.capture()
        self.assertEqual(snap.object_names, {self.a.name})
        self.assertEqual(len(snap.curve_data), 2)
        self.assertTrue(all(e['object_name'] == self.a.name for e in snap.ghost_data + snap.curve_data))
        self.assertEqual(snap.curve_data[0]['keys'], fc.snapshot_fcurve(fc.resolve_fcurve(self.a, '', 'location.x')))
        self.activate(self.b)
        self.assertIs(snap.bindings[0].obj, self.a)
        self.assertEqual(snap.bindings[0].resolve(self.scene)[1], '')

    def test_object_rename_keeps_identity(self):
        snap = self.capture()
        self.a.name = 'Renamed Original'
        self.assertEqual(snap.bindings[0].resolve(self.scene)[1], '')

    def test_same_name_replacement_refuses_without_writes(self):
        snap = self.capture()
        name = self.a.name
        bpy.data.objects.remove(self.a, do_unlink=True)
        replacement = _cube(name)
        before = fc.snapshot_fcurve(fc.resolve_fcurve(replacement, '', 'location.x'))
        self.assertFalse(self.store.restore_snapshot(snap.uid, self.scene))
        self.assertEqual(before, fc.snapshot_fcurve(fc.resolve_fcurve(replacement, '', 'location.x')))

    def test_action_replacement_refuses(self):
        snap = self.capture()
        self.a.animation_data.action = self.a.animation_data.action.copy()
        self.assertFalse(self.store.restore_snapshot(snap.uid, self.scene))
        self.assertIn('action', self.store.last_error)

    def test_slot_switch_refuses(self):
        snap = self.capture()
        self.a.animation_data.action_slot = self.a.animation_data.action.slots.new('OBJECT', 'Different slot')
        self.assertFalse(self.store.restore_snapshot(snap.uid, self.scene))
        self.assertIn('slot', self.store.last_error)

    def test_curve_replacement_refuses(self):
        snap = self.capture()
        action = self.a.animation_data.action
        bag = action.layers[0].strips[0].channelbag(self.a.animation_data.action_slot)
        old = fc.resolve_fcurve(self.a, '', 'location.x')
        # Keep the old allocation alive while removing it from the target channel.
        old.data_path = 'scale'
        replacement = bag.fcurves.new('location', index=0)
        replacement.keyframe_points.insert(1, 99)
        self.assertFalse(self.store.restore_snapshot(snap.uid, self.scene))
        self.assertEqual(replacement.evaluate(1), 99)

    def test_selected_markers_capture_only_selected_channel(self):
        for ghost in GhostStore.get(self.scene):
            ghost.is_selected = ghost.object_name == self.a.name and ghost.channel == 'location.y'
        snap = self.capture('MARKERS')
        self.assertEqual({e['channel'] for e in snap.curve_data}, {'location.y'})

    def test_selected_bones_and_rename(self):
        rig = _rig()
        self.activate(rig)
        bpy.ops.object.mode_set(mode='POSE')
        for pb in rig.pose.bones:
            pb.select = pb.name == 'upper'
            GhostStore.get(self.scene).add(Ghost(frame=10, object_name=rig.name, bone_name=pb.name, channel='location.x'))
        snap = self.capture()
        self.assertEqual(snap.bone_names, {'upper'})
        rig.pose.bones['upper'].name = 'RenamedUpper'
        self.assertEqual(snap.bindings[0].resolve(self.scene)[1], '')
        bpy.ops.object.mode_set(mode='OBJECT')

    def test_selected_path_and_removed_path(self):
        entry = self.scene.ghost_tool.motion_paths.add()
        entry.object_name = self.a.name
        self.scene.ghost_tool.motion_paths_index = 0
        self.activate(self.b)
        snap = self.capture('PATH')
        self.assertEqual(snap.object_names, {self.a.name})
        self.scene.ghost_tool.motion_paths.clear()
        self.assertFalse(self.store.restore_snapshot(snap.uid, self.scene))
        self.assertIn('path', self.store.last_error)

    def test_no_marker_prerequisite(self):
        GhostStore.get(self.scene).clear()
        with self.assertRaisesRegex(ValueError, 'markers'):
            self.capture()

    def test_legacy_unbound_until_explicit_binding(self):
        snap = self.capture()
        self.store.load_from_dict_list([snap.to_dict()])
        self.assertFalse(self.store.restore_snapshot(snap.uid, self.scene))
        self.store.bind_snapshot(snap.uid, self.scene, self.a)
        self.assertTrue(self.store.restore_snapshot(snap.uid, self.scene))

    def test_capture_label_never_writes_path_identity(self):
        from ghost_tool.target_binding import capture_label
        entry = self.scene.ghost_tool.motion_paths.add()
        entry.object_name = self.a.name
        self.scene.ghost_tool.motion_paths_index = 0
        self.scene.ghost_snapshot_scope = 'PATH'
        try:
            self.assertIn(self.a.name, capture_label(bpy.context))
            # Panels draw this label; writing ID data while drawing is refused.
            self.assertNotIn('_ghost_editor_uid', entry.keys())
        finally:
            self.scene.ghost_snapshot_scope = 'ACTIVE'

    def test_copied_bone_identity_keeps_original_binding(self):
        from ghost_tool.target_binding import BONE_UID, BONE_OWNER, CurveBinding
        rig = _rig()
        original = CurveBinding.capture(self.scene, rig, 'upper', 'location.x')
        upper, copy = rig.data.bones['upper'], rig.data.bones['lower']
        # Duplicating a bone copies its custom properties (identity included).
        copy[BONE_UID], copy[BONE_OWNER] = upper[BONE_UID], upper[BONE_OWNER]
        self.assertEqual(original.resolve(self.scene)[1], '')
        self.assertEqual(original.bone_name, 'upper')
        captured = CurveBinding.capture(self.scene, rig, 'lower', 'location.x')
        self.assertNotEqual(captured.bone_uid, original.bone_uid)
        self.assertEqual(captured.resolve(self.scene)[1], '')
        self.assertEqual(original.resolve(self.scene)[1], '')

    def test_reassigned_action_rebinds_loaded_reference(self):
        snap = self.capture()
        action = self.a.animation_data.action
        slot = self.a.animation_data.action_slot
        self.a.animation_data.action = None
        SnapshotStore.clear_all_instances()
        store = SnapshotStore.get(self.scene)  # loaded while unresolvable
        self.a.animation_data.action = action
        self.a.animation_data.action_slot = slot
        self.assertTrue(store.restore_snapshot(snap.uid, self.scene), store.last_error)

    def test_import_with_unreadable_saved_snapshots_is_rejected_cleanly(self):
        import os
        import tempfile
        from ghost_tool import export_import
        self.capture()
        path = os.path.join(tempfile.mkdtemp(prefix='ghost-import-'), 'refs.json')
        self.assertTrue(export_import.export_ghosts(path, self.scene))
        self.store.storage_error = 'Saved snapshot data could not be read.'
        try:
            self.assertFalse(export_import.import_ghosts(path, self.scene))
        finally:
            self.store.storage_error = ''

    def test_common_editor_resolver_stays_locked(self):
        target = settings_editor.capture_target(bpy.context)
        self.activate(self.b)
        self.assertEqual(settings_editor.resolve_target(target, self.scene)[1], '')
        self.assertEqual(target.obj, self.a)
        other = bpy.data.scenes.new('Other scene')
        try:
            self.assertIn('Scene', settings_editor.resolve_target(target, other)[1])
        finally:
            bpy.data.scenes.remove(other)


if __name__ == '__main__':
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(SnapshotTargets))
    if not result.wasSuccessful():
        raise RuntimeError('Snapshot target checks failed')
