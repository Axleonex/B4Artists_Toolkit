"""Persistent authority, migrations and actual fresh-process blend round trips."""
import copy
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_ghost_snapshot_targets import SnapshotTargets, bpy, ghost_tool, fc
from ghost_tool.snapshot import SnapshotStore, GhostSnapshot
from ghost_tool import export_import, snapshot_storage


def canonical(data):
    return json.dumps(data, sort_keys=True)


class SnapshotPersistence(unittest.TestCase):
    setUpClass = classmethod(SnapshotTargets.setUpClass.__func__)
    tearDownClass = classmethod(SnapshotTargets.tearDownClass.__func__)
    def setUp(self):
        # Re-enable reloads addon classes; fixtures must acquire current stores.
        from ghost_tool import ghost_data, snapshot
        import test_ghost_snapshot_targets as fixture
        fixture.Ghost, fixture.GhostStore = ghost_data.Ghost, ghost_data.GhostStore
        fixture.SnapshotStore = snapshot.SnapshotStore
        globals()['SnapshotStore'] = snapshot.SnapshotStore
        globals()['GhostSnapshot'] = snapshot.GhostSnapshot
        SnapshotTargets.setUp(self)
    tearDown = SnapshotTargets.tearDown
    activate = SnapshotTargets.activate
    capture = SnapshotTargets.capture
    _drop_deferred_timer = SnapshotTargets._drop_deferred_timer

    def import_payload(self, payload, **kwargs):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'reference.json'
            path.write_text(json.dumps(payload), encoding='utf-8')
            return export_import.import_ghosts(str(path), self.scene, **kwargs)

    def test_fresh_process_roundtrip_payload_identity_and_lineage(self):
        parent = self.capture()
        child = self.store.take_variant('', self.scene, parent.uid, context=bpy.context, scope='ACTIVE')
        self.store.toggle_visibility(parent.uid)
        self.a.name = 'RenamedBeforeSave'
        with tempfile.TemporaryDirectory() as directory:
            blend = Path(directory) / 'roundtrip.blend'
            expected = Path(directory) / 'expected.json'
            expected.write_text(canonical(self.store.to_dict_list()), encoding='utf-8')
            bpy.ops.wm.save_as_mainfile(filepath=str(blend), check_existing=False)
            command = [bpy.app.binary_path, '--background', '--factory-startup', '--python-exit-code', '1',
                       '--python', str(Path(__file__).resolve()), '--', '--reopen', str(blend), str(expected)]
            process = subprocess.run(command, env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'),
                capture_output=True, text=True, errors='replace', timeout=60)
            self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
            self.assertIn('FRESH_PROCESS_SNAPSHOT_PASS', process.stdout)

    def test_json_import_remains_unbound_without_explicit_mapping(self):
        snap = self.capture()
        data = snap.to_dict()
        self.store.load_from_dict_list([])
        self.assertTrue(self.import_payload({'version': '2.0.0', 'ghosts': [], 'snapshots': [data]}))
        loaded = SnapshotStore.get(self.scene)
        self.assertFalse(loaded.restore_snapshot(snap.uid, self.scene))
        self.assertTrue(loaded.get_by_uid(snap.uid).ghost_data)

    def test_explicit_mapping_binds_all_full_curves(self):
        data = self.capture().to_dict()
        self.store.load_from_dict_list([])
        self.assertTrue(self.import_payload({'ghosts': [], 'snapshots': [data]}, target_object=self.b))
        loaded = SnapshotStore.get(self.scene).get_all()[0]
        self.assertEqual(loaded.object_names, {self.b.name})
        self.assertTrue(all(b.obj == self.b for b in loaded.bindings))

    def test_uid_collision_remaps_child_parent_together(self):
        parent = self.capture()
        child = self.store.take_variant('', self.scene, parent.uid, context=bpy.context, scope='ACTIVE')
        payload = [parent.to_dict(), child.to_dict()]
        self.assertTrue(self.import_payload({'ghosts': [], 'snapshots': payload}))
        records = SnapshotStore.get(self.scene).get_all()
        self.assertEqual(len(records), 4)
        self.assertEqual(len({s.uid for s in records}), 4)
        self.assertNotEqual(records[0].uid, parent.uid)
        self.assertEqual(records[1].parent_uid, records[0].uid)
        self.assertEqual(records[1].origin['uid'], records[0].uid)

    def test_future_or_malformed_import_preserves_all_retained_data(self):
        snap = self.capture()
        before = canonical(self.store.to_dict_list())
        bad = snap.to_dict()
        bad['schema_version'] = 99
        for payload in ({'version': '99', 'ghosts': []}, {'ghosts': [], 'snapshots': [bad]},
                        {'ghosts': [], 'snapshots': [None]}):
            self.assertFalse(self.import_payload(payload))
            self.assertEqual(canonical(SnapshotStore.get(self.scene).to_dict_list()), before)

    def test_capacity_refuses_capture_and_import_without_eviction(self):
        first = self.capture()
        for _ in range(9):
            self.capture()
        before = canonical(self.store.to_dict_list())
        with self.assertRaisesRegex(ValueError, 'Delete'):
            self.capture()
        self.assertFalse(self.import_payload({'ghosts': [], 'snapshots': [first.to_dict()]}))
        self.assertEqual(canonical(SnapshotStore.get(self.scene).to_dict_list()), before)

    def test_preexisting_over_limit_blend_is_preserved_and_can_delete(self):
        payload = self.capture().to_dict()
        records = []
        for i in range(12):
            data = copy.deepcopy(payload)
            data['uid'] = 'over-' + str(i)
            records.append(GhostSnapshot.from_dict(data))
        snapshot_storage.commit(self.scene, records)
        SnapshotStore.clear_all_instances()
        store = SnapshotStore.get(self.scene)
        self.assertEqual(len(store.get_all()), 12)
        with self.assertRaises(ValueError):
            store.take_snapshot('New', self.scene, context=bpy.context, scope='ACTIVE')
        self.assertTrue(store.delete_snapshot('over-0'))
        self.assertEqual(len(SnapshotStore.get(self.scene).get_all()), 11)

    def test_disable_reenable_retains_payload_and_typed_identity(self):
        self.capture()
        before = canonical(self.store.to_dict_list())
        ghost_tool.unregister()
        with patch.object(ghost_tool, '_clear_pycache'):
            ghost_tool.register()
        # Registration can reload modules; reacquire the live authority class.
        from ghost_tool.snapshot import SnapshotStore as CurrentStore
        restored = CurrentStore.get(bpy.context.scene)
        self.assertEqual(canonical(restored.to_dict_list()), before)
        self.assertEqual(restored.get_all()[0].bindings[0].resolve(bpy.context.scene)[1], '')

    def test_duplicate_scene_cannot_redirect_original_binding(self):
        snap = self.capture()
        duplicate = self.scene.copy()
        try:
            store = SnapshotStore.get(duplicate)
            self.assertEqual(len(store.get_all()), 1)
            self.assertFalse(store.restore_snapshot(snap.uid, duplicate))
            self.assertIn('Scene', store.last_error)
        finally:
            bpy.data.scenes.remove(duplicate)

    def test_deleted_source_stays_missing_after_cache_rebuild(self):
        snap = self.capture()
        name = self.a.name
        bpy.data.objects.remove(self.a, do_unlink=True)
        self.b.name = name
        SnapshotStore.clear_all_instances()
        store = SnapshotStore.get(self.scene)
        self.assertFalse(store.restore_snapshot(snap.uid, self.scene))
        self.assertTrue(store.get_by_uid(snap.uid).ghost_data)


def reopen(blend, expected):
    ghost_tool.register()
    bpy.ops.wm.open_mainfile(filepath=blend)
    scene = bpy.context.scene
    store = SnapshotStore.get(scene)
    assert canonical(store.to_dict_list()) == canonical(json.loads(Path(expected).read_text(encoding='utf-8')))
    parent, child = store.get_all()
    assert child.parent_uid == parent.uid and child.origin['uid'] == parent.uid
    assert not parent.is_visible and child.is_visible
    for snap in store.get_all():
        for binding in snap.bindings:
            assert binding.obj == bpy.data.objects['RenamedBeforeSave']
            assert binding.resolve(scene)[1] == ''
    obj = bpy.data.objects['RenamedBeforeSave']
    bpy.data.objects.remove(obj, do_unlink=True)
    bpy.ops.mesh.primitive_cube_add()
    bpy.context.object.name = 'RenamedBeforeSave'
    bpy.context.object.keyframe_insert('location', frame=1)
    assert not store.restore_snapshot(child.uid, scene)
    print('FRESH_PROCESS_SNAPSHOT_PASS', flush=True)


if __name__ == '__main__':
    if '--reopen' in sys.argv:
        i = sys.argv.index('--reopen')
        reopen(sys.argv[i + 1], sys.argv[i + 2])
    else:
        result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(SnapshotPersistence))
        if not result.wasSuccessful():
            raise RuntimeError('Snapshot persistence checks failed')
