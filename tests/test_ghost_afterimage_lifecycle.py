"""Real-window history and original-target cleanup in the supported host."""
import sys
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_ghost_snapshot_targets import SnapshotTargets, bpy, ghost_tool, fc
from test_ghost_paths import _cube
from ghost_tool import session_state as ss, snapshot, motion_paths as mp, settings_editor
from ghost_tool.path_handle_drag import HandleDrag
from mathutils import Vector


class Lifecycle(unittest.TestCase):
    maxDiff = None
    setUpClass = classmethod(SnapshotTargets.setUpClass.__func__)
    tearDownClass = classmethod(SnapshotTargets.tearDownClass.__func__)
    activate = SnapshotTargets.activate
    capture = SnapshotTargets.capture
    _drop_deferred_timer = SnapshotTargets._drop_deferred_timer

    def setUp(self):
        window = bpy.context.window_manager.windows[0]
        area = next(a for a in window.screen.areas if a.type == 'VIEW_3D')
        region = next(r for r in area.regions if r.type == 'WINDOW')
        self.enterContext(bpy.context.temp_override(window=window, area=area, region=region))
        from ghost_tool import ghost_data
        import test_ghost_snapshot_targets as fixture
        fixture.Ghost, fixture.GhostStore = ghost_data.Ghost, ghost_data.GhostStore
        fixture.SnapshotStore = snapshot.SnapshotStore
        SnapshotTargets.setUp(self)

    def tearDown(self):
        ss.SessionState.cancel_active()
        self._drop_deferred_timer()

    def data(self):
        return json.loads(json.dumps(snapshot.SnapshotStore.get(bpy.context.scene).to_dict_list()))

    def history(self, before, after):
        self.assertEqual(bpy.ops.ed.undo(), {'FINISHED'})
        self.assertEqual(self.data(), before)
        self.assertEqual(bpy.ops.ed.redo(), {'FINISHED'})
        self.assertEqual(self.data(), after)
        store = snapshot.SnapshotStore.get(bpy.context.scene)
        self.assertEqual(len(store.get_visible()), sum(s['is_visible'] for s in after))
        for snap in store.get_all():
            for binding in snap.bindings:
                self.assertEqual(binding.resolve(bpy.context.scene)[1], '')

    def test_capture_variant_visibility_delete_and_bind_real_history(self):
        bpy.ops.ed.undo_push(message='Before retained references')
        self.assertEqual(bpy.ops.ghost_tool.take_snapshot('EXEC_DEFAULT', True), {'FINISHED'})
        first = self.data()
        self.history([], first)
        uid = first[0]['uid']
        self.assertEqual(bpy.ops.ghost_tool.save_variant('EXEC_DEFAULT', True, parent_uid=uid), {'FINISHED'})
        child = self.data()
        self.history(first, child)
        bpy.ops.ghost_tool.toggle_snapshot('EXEC_DEFAULT', True, snapshot_uid=uid)
        hidden = self.data()
        self.history(child, hidden)
        bpy.ops.ghost_tool.delete_snapshot('EXEC_DEFAULT', True, snapshot_uid=uid)
        deleted = self.data()
        self.history(hidden, deleted)
        self.assertEqual(deleted[0]['parent_uid'], uid)
        # Deliberate mapping is itself a reversible retained-data mutation.
        store = snapshot.SnapshotStore.get(bpy.context.scene)
        raw = store.to_dict_list()
        store.load_from_dict_list(raw)
        self.assertFalse(store.get_all()[0].bindings)
        bpy.ops.ed.undo_push(message='Before explicit bind')
        child_uid = raw[0]['uid']
        bpy.ops.ghost_tool.bind_snapshot('EXEC_DEFAULT', True, snapshot_uid=child_uid)
        self.assertTrue(snapshot.SnapshotStore.get(bpy.context.scene).get_all()[0].bindings)
        bpy.ops.ed.undo()
        self.assertFalse(snapshot.SnapshotStore.get(bpy.context.scene).get_all()[0].bindings)
        bpy.ops.ed.redo()
        self.assertEqual(snapshot.SnapshotStore.get(bpy.context.scene).get_all()[0].bindings[0].resolve(bpy.context.scene)[1], '')

    def start(self):
        self.curve = fc.resolve_fcurve(self.a, '', 'location.x')
        self.before = fc.snapshot_fcurve(self.curve)
        transaction = ss.CurveTransaction(self.scene, [(self.a, '', 'location.x')])
        owner = object()
        self.assertTrue(ss.SessionState.begin_gesture(owner, self.scene, context=bpy.context,
            cancel=transaction.rollback, validate=transaction.valid))
        self.curve.keyframe_points[0].co.y = 50
        self.curve.update()
        return transaction, owner

    def released(self):
        self.assertTrue(ss.SessionState.available())
        self.assertFalse(bpy.app.timers.is_registered(ss._watch_gesture))
        owner = object()
        self.assertTrue(ss.SessionState.begin_gesture(owner, bpy.context.scene))
        ss.SessionState.end_gesture(owner)

    def test_cancel_is_idempotent_and_preserves_retained_payload(self):
        self.capture()
        saved = self.data()
        transaction, owner = self.start()
        ss.SessionState.cancel_active()
        transaction.rollback()
        ss.SessionState.cancel_active()
        self.assertEqual(fc.snapshot_fcurve(self.curve), self.before)
        self.assertEqual(self.data(), saved)
        self.released()

    def test_gesture_tags_are_removed_on_finish_and_rollback(self):
        transaction, owner = self.start()
        self.assertEqual(len(self.curve.modifiers), 1)
        transaction.rollback()
        self.assertEqual(len(self.curve.modifiers), 0)
        self.assertEqual(fc.snapshot_fcurve(self.curve), self.before)
        ss.SessionState.end_gesture(owner)
        transaction, owner = self.start()
        transaction.finish()
        self.assertEqual(len(self.curve.modifiers), 0)
        ss.SessionState.end_gesture(owner)

    def test_editor_ownership_requires_its_screen(self):
        window = bpy.context.window
        target = settings_editor.capture_target(bpy.context)
        target.editor_window = window
        target.editor_screen = window.screen
        settings_editor._targets[window.as_pointer()] = target
        try:
            self.assertTrue(settings_editor._owns_window(window))
            # A later window can reuse a closed window's address, never its screen.
            other = next(s for s in bpy.data.screens if s != window.screen)
            target.editor_screen = other
            self.assertFalse(settings_editor._owns_window(window))
        finally:
            settings_editor._targets.clear()

    def test_replaced_object_never_receives_rollback(self):
        transaction, owner = self.start()
        name = self.a.name
        bpy.data.objects.remove(self.a, do_unlink=True)
        replacement = _cube(name)
        curve = fc.resolve_fcurve(replacement, '', 'location.x')
        before = fc.snapshot_fcurve(curve)
        self.assertIsNone(ss._watch_gesture())
        self.assertEqual(fc.snapshot_fcurve(curve), before)
        transaction.rollback()
        self.released()

    def test_replaced_curve_never_receives_rollback(self):
        transaction, owner = self.start()
        bag = self.a.animation_data.action.layers[0].strips[0].channelbag(self.a.animation_data.action_slot)
        bag.fcurves.remove(self.curve)
        curve = bag.fcurves.new('location', index=0)
        curve.keyframe_points.insert(1, 123)
        self.assertIsNone(ss._watch_gesture())
        self.assertEqual(curve.evaluate(1), 123)
        self.released()

    def test_scene_switch_restores_original_and_releases(self):
        transaction, owner = self.start()
        window = bpy.context.window
        other = bpy.data.scenes.new('Lifecycle other')
        try:
            window.scene = other
            self.assertIsNone(ss._watch_gesture())
            self.assertEqual(fc.snapshot_fcurve(self.curve), self.before)
            self.released()
        finally:
            window.scene = self.scene
            bpy.data.scenes.remove(other)

    def test_closed_source_and_editor_windows_release_original_curves(self):
        original = bpy.context.window
        for lost_role in ('source_window', 'editor_window'):
            windows = set(bpy.context.window_manager.windows)
            print('LIFECYCLE open window', flush=True)
            area = next(a for a in original.screen.areas if a.type == 'VIEW_3D')
            with bpy.context.temp_override(window=original, area=area):
                self.assertEqual(bpy.ops.ghost_tool.open_window(), {'FINISHED'})
            print('LIFECYCLE opened', flush=True)
            extra = next(w for w in bpy.context.window_manager.windows if w not in windows)
            target = settings_editor.EditingTarget(self.scene, self.a, '', None, original, original)
            setattr(target, lost_role, extra)
            settings_editor._targets[original.as_pointer()] = target
            try:
                with bpy.context.temp_override(window=original):
                    transaction, owner = self.start()
                print('LIFECYCLE closing window', flush=True)
                with bpy.context.temp_override(window=extra):
                    bpy.ops.wm.window_close()
                print('LIFECYCLE closed', flush=True)
                self.assertIsNone(ss._watch_gesture())
                self.assertEqual(fc.snapshot_fcurve(self.curve), self.before)
                self.released()
            finally:
                settings_editor._targets.pop(original.as_pointer(), None)

    def test_handle_drag_cancel_and_confirm_do_not_replay_backups(self):
        entry = self.settings.motion_paths.add()
        entry.object_name = self.a.name
        self.settings.paths_show_handles = True
        mp.refresh_paths(bpy.context)
        target = next(t for t in mp.pinned_targets(self.scene) if t.obj == self.a)
        mp._handles[(*target.key, 1)] = mp.key_handles(target, 1, bpy.context.evaluated_depsgraph_get())
        drag = HandleDrag(self.scene, target, 1, 'RIGHT')
        self.assertTrue(drag.ok)
        before = [fc.snapshot_fcurve(c) for c in drag.curves.values()]
        drag.move_to(drag.depth + Vector((1, 2, 3)))
        drag.cancel()
        drag.cancel()
        self.assertEqual([fc.snapshot_fcurve(c) for c in drag.curves.values()], before)
        mp.refresh_paths(bpy.context)
        mp._handles[(*target.key, 1)] = mp.key_handles(target, 1, bpy.context.evaluated_depsgraph_get())
        drag = HandleDrag(self.scene, target, 1, 'RIGHT')
        drag.move_to(drag.depth + Vector((1, 2, 3)))
        drag.confirm(bpy.context)
        confirmed = [fc.snapshot_fcurve(c) for c in drag.curves.values()]
        drag.cancel()
        self.assertEqual([fc.snapshot_fcurve(c) for c in drag.curves.values()], confirmed)

    def test_draw_callbacks_tolerate_restricted_shutdown_context(self):
        from types import SimpleNamespace
        from ghost_tool import viewport_draw
        with patch.object(viewport_draw, 'warn') as warning:
            viewport_draw.draw_ghosts_3d(SimpleNamespace())
            viewport_draw.draw_ghosts_2d(SimpleNamespace())
            warning.assert_not_called()

    def test_actual_undo_redo_cancels_active_gesture_before_history(self):
        saved = json.loads(json.dumps(self.capture().to_dict()))
        name = self.a.name
        curve = fc.resolve_fcurve(self.a, '', 'location.x')
        original = fc.snapshot_fcurve(curve)
        bpy.ops.ed.undo_push(message='Original motion')
        curve.keyframe_points[0].co.y = 9
        curve.update()
        edited = fc.snapshot_fcurve(curve)
        bpy.ops.ed.undo_push(message='Edited motion')
        transaction, owner = self.start()
        bpy.ops.ed.undo()
        self.assertTrue(transaction.finished)
        self.assertEqual(fc.snapshot_fcurve(fc.resolve_fcurve(bpy.data.objects[name], '', 'location.x')), original)
        self.assertEqual(self.data(), [saved])
        self.released()
        bpy.ops.ed.redo()
        self.assertEqual(fc.snapshot_fcurve(fc.resolve_fcurve(bpy.data.objects[name], '', 'location.x')), edited)
        self.released()

    def test_load_pre_and_actual_file_reopen_clear_operation(self):
        saved = json.loads(json.dumps(self.capture().to_dict()))
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / 'lifecycle.blend')
            bpy.ops.wm.save_as_mainfile(filepath=path, check_existing=False)
            transaction, owner = self.start()
            # Actual load invokes the registered pre-handler before replacing RNA.
            bpy.ops.wm.open_mainfile(filepath=path)
            self.assertTrue(transaction.finished)
            self.assertEqual(self.data(), [saved])
            self.released()

    def test_disable_rolls_back_and_reenable_handlers_remain_unique(self):
        saved = json.loads(json.dumps(self.capture().to_dict()))
        transaction, owner = self.start()
        ghost_tool.unregister()
        self.assertEqual(fc.snapshot_fcurve(self.curve), self.before)
        self.released()
        for _ in range(2):
            with patch.object(ghost_tool, '_clear_pycache'):
                ghost_tool.register()
            self.assertEqual(self.data(), [saved])
            for handlers in (bpy.app.handlers.load_pre, bpy.app.handlers.undo_pre, bpy.app.handlers.redo_pre):
                self.assertEqual(sum(h.__module__ == 'ghost_tool.session_state' for h in handlers), 1)
            ghost_tool.unregister()
        with patch.object(ghost_tool, '_clear_pycache'):
            ghost_tool.register()


if __name__ == '__main__':
    result = unittest.TextTestRunner(verbosity=2, failfast=True).run(unittest.defaultTestLoader.loadTestsFromTestCase(Lifecycle))
    if not result.wasSuccessful():
        raise RuntimeError('Lifecycle checks failed')
