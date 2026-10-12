"""Phase 1 target/layout checks; run in factory-startup Bforartists."""
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_ghost_paths import GhostPaths, _cube, bpy, ghost_tool
from test_ghost_paths_folders import _Layout
from ghost_tool import ui_panel as ui
from ghost_tool.snapshot import SnapshotStore
from ghost_tool.ghost_data import Ghost, GhostStore


class Layout(_Layout):
    def row(self, **kwargs):
        return Layout(self.calls)
    column = row
    box = row

    def panel(self, *args, **kwargs):
        self.calls.append(('panel', args[0], kwargs))
        return self, self


class AfterimageUI(unittest.TestCase):
    setUp = GhostPaths.setUp
    _drop_deferred_timer = GhostPaths._drop_deferred_timer

    @classmethod
    def setUpClass(cls):
        with patch.object(ghost_tool, '_clear_pycache'):
            ghost_tool.register()

    @classmethod
    def tearDownClass(cls):
        ghost_tool.unregister()

    def tearDown(self):
        SnapshotStore.get(self.scene).load_from_dict_list([])
        self._drop_deferred_timer()

    def snapshot(self):
        obj = _cube()
        GhostStore.get(self.scene).add(Ghost(frame=10, object_name=obj.name,
            channel='location.x', parent_frame_a=1, parent_frame_b=20))
        snap, _ = SnapshotStore.get(self.scene).take_snapshot('Original timing', self.scene)
        return obj, snap

    def labels(self, layout):
        return [c[1] for c in layout.calls if c[0] == 'label']

    def test_named_snapshot_actions_and_truthful_session_scope(self):
        obj, snap = self.snapshot()
        layout = Layout()
        ui._draw_compare(layout, bpy.context)
        actions = {c[1]: c[2] for c in layout.calls if c[0] == 'op'}
        self.assertEqual(actions['ghost_tool.take_snapshot'], 'Save Snapshot')
        self.assertEqual(actions['ghost_tool.toggle_snapshot'], 'Hide')
        self.assertEqual(actions['ghost_tool.restore_snapshot'], 'Restore')
        self.assertEqual(actions['ghost_tool.delete_snapshot'], 'Delete')
        text = ' '.join(self.labels(layout))
        self.assertIn('Saved snapshots', text)
        self.assertIn('Capture:', text)
        self.assertIn(obj.name, text)
        self.assertIn('complete captured curves', text)
        self.assertIn('Export JSON', text)

    def test_missing_snapshot_target_is_explained(self):
        obj, snap = self.snapshot()
        name = obj.name
        bpy.data.objects.remove(obj, do_unlink=True)
        layout = Layout()
        ui._draw_compare(layout, bpy.context)
        text = ' '.join(self.labels(layout))
        self.assertIn('Unavailable', text)
        self.assertIn(name, text)

    def test_overlay_button_switches_label_and_never_writes_curves(self):
        obj, snap = self.snapshot()
        before = snap.curve_data.copy()
        self.assertEqual(bpy.ops.ghost_tool.toggle_snapshot(snapshot_uid=snap.uid), {'FINISHED'})
        layout = Layout()
        ui._draw_compare(layout, bpy.context)
        self.assertIn(('ghost_tool.toggle_snapshot', 'Show'),
                      [(c[1], c[2]) for c in layout.calls if c[0] == 'op'])
        self.assertEqual(before, snap.curve_data)

    def test_wrap_preserves_full_long_target_at_narrow_width(self):
        layout = Layout()
        context = SimpleNamespace(region=SimpleNamespace(width=180),
                                  preferences=SimpleNamespace(view=SimpleNamespace(ui_scale=1)))
        name = 'Targets: Character_Left_Arm_With_A_Very_Long_Name'
        ui._wrapped_label(layout, context, name)
        lines = self.labels(layout)
        self.assertGreater(len(lines), 1)
        self.assertTrue(all(len(line) <= 17 for line in lines))
        self.assertEqual(''.join(lines).replace(' ', ''), name.replace(' ', ''))

    def test_generation_target_and_options_follow_immediate_action(self):
        obj = _cube()
        layout = Layout()
        ui._draw_show_ghosts(layout, bpy.context)
        calls = layout.calls
        target = next(i for i,c in enumerate(calls) if c[0] == 'label' and obj.name in c[1])
        action = next(i for i,c in enumerate(calls) if c[0] == 'op' and c[1] == 'ghost_tool.generate_ghosts')
        fold = next(i for i,c in enumerate(calls) if c[0] == 'panel')
        self.assertLess(target, action)
        self.assertLess(action, fold)
        from ghost_tool.modal_operator import GHOST_OT_generate
        self.assertNotIn('invoke', GHOST_OT_generate.__dict__)

    def test_popover_wrap_does_not_use_invoking_viewport_width(self):
        layout = Layout()
        context = SimpleNamespace(region=SimpleNamespace(width=1597, type='WINDOW'),
                                  preferences=SimpleNamespace(view=SimpleNamespace(ui_scale=1)))
        ui._wrapped_label(layout, context, 'Session only. Export JSON to keep snapshots.')
        lines = self.labels(layout)
        self.assertGreater(len(lines), 1)
        self.assertTrue(all(len(line) <= 32 for line in lines))

    def test_no_target_stays_visible_with_recovery_text(self):
        layout = Layout()
        context = SimpleNamespace(active_object=None)
        text = ui._marker_target_text(context)
        self.assertIn('select an animated object', text)

    def test_native_shelf_uses_existing_tabs_and_feature_poll(self):
        self.assertEqual(ui.GHOST_PT_shelf_object.bl_category, 'Object')
        self.assertEqual(ui.GHOST_PT_shelf_pose.bl_category, 'Pose')
        self.assertEqual(len(ui._shelf_registered), 2)
        context = SimpleNamespace(mode='OBJECT', space_data=SimpleNamespace(show_toolshelf_tabs=True))
        self.assertTrue(ui.GHOST_PT_shelf_object.poll(context))
        self.assertFalse(ui.GHOST_PT_shelf_pose.poll(context))
        context.space_data.show_toolshelf_tabs = False
        self.assertFalse(ui.GHOST_PT_shelf_object.poll(context))

    def test_locked_editor_label_does_not_follow_selection(self):
        from ghost_tool import settings_editor as editor
        obj = _cube()
        obj.name = 'LockedOriginal'
        captured = editor.capture_target(bpy.context)
        captured.editor_window = bpy.context.window
        pointer = bpy.context.window.as_pointer()
        editor._targets[pointer] = captured
        try:
            bpy.ops.mesh.primitive_cube_add()
            layout = Layout()
            editor.draw_editor(layout, bpy.context)
            text = ' '.join(self.labels(layout))
            self.assertIn('LockedOriginal', text)
            self.assertNotIn('Object: ' + bpy.context.active_object.name, text)
        finally:
            editor._targets.pop(pointer, None)


if __name__ == '__main__':
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(AfterimageUI))
    if not result.wasSuccessful():
        raise RuntimeError('Afterimage UI checks failed')
