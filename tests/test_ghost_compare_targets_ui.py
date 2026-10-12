"""Independent Compare target folds; factory-startup Bforartists."""
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_ghost_marker_targets_ui import Layout, bpy, ghost_tool
from ghost_tool import ui_panel as ui, target_binding as tb
from ghost_tool.snapshot import GhostSnapshot


class NativeWidthLayout(Layout):
    def __init__(self, *args, boxed=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.boxed = boxed

    def row(self, **kwargs):
        return NativeWidthLayout(self.calls, self.closed, self.path, boxed=self.boxed)

    column = row

    def box(self, **kwargs):
        return NativeWidthLayout(self.calls, self.closed, self.path, boxed=True)

    def panel(self, key, **kwargs):
        if self.boxed:
            raise AssertionError('Native panels cannot be inside snapshot boxes')
        return super().panel(key, **kwargs)


class CompareTargetsUI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with patch.object(ghost_tool, '_clear_pycache'):
            ghost_tool.register()

    @classmethod
    def tearDownClass(cls):
        ghost_tool.unregister()

    def setUp(self):
        self.scene = bpy.context.scene
        self.scene.ghost_tool.is_active = True
        self.names = [f'mixamorig:LongCharacterFingerBone{i:02}' for i in range(65)]
        self.samples = [SimpleNamespace(object_name='Armature', bone_name=name) for name in self.names]
        self.snapshots = [GhostSnapshot(name='Reference A', uid='a', object_names={'Armature'},
                                       bone_names=set(self.names))]
        self.context = SimpleNamespace(scene=self.scene, active_object=None, window=bpy.context.window,
            region=SimpleNamespace(width=220, type='UI'),
            preferences=SimpleNamespace(view=SimpleNamespace(ui_scale=1)))

    def draw(self, closed=(), reason=''):
        layout = NativeWidthLayout(closed=set(closed))
        store = SimpleNamespace(get_all=lambda:self.snapshots, storage_error='')
        with patch.object(tb, 'selected_samples', return_value=(self.samples, '')) as samples, \
             patch.object(ui.SnapshotStore, 'get', return_value=store), \
             patch.object(ui.SnapshotStore, 'binding_reason', return_value=reason):
            ui._draw_compare(layout, self.context)
            self.assertTrue(all(c.kwargs['assign'] is False for c in samples.call_args_list))
        return layout

    def test_closed_lists_keep_save_restore_and_compare_actions_visible(self):
        layout = self.draw({'ghost_capture_targets', 'ghost_snapshot_targets_a'})
        labels = ' '.join(c[1] for c in layout.calls if c[0] == 'label')
        self.assertNotIn('mixamorig:', labels)
        self.assertIn('65 bones', labels)
        actions = {c[1] for c in layout.calls if c[0] == 'op'}
        self.assertTrue({'ghost_tool.take_snapshot','ghost_tool.restore_snapshot',
                         'ghost_tool.save_variant','ghost_tool.delete_snapshot',
                         'ghost_tool.pin_diff_reference'} <= actions)
        folds = [c for c in layout.calls if c[0] == 'panel']
        self.assertEqual({c[1] for c in folds}, {'ghost_capture_targets','ghost_snapshot_targets_a'})
        self.assertTrue(all(c[2]['default_closed'] for c in folds))

    def test_open_capture_preserves_all_names_at_narrow_width(self):
        layout = self.draw({'ghost_snapshot_targets_a'})
        lines = [c[1] for c in layout.calls if c[0]=='label'
                 and c[3].endswith('/ghost_capture_targets/body')]
        text = ''.join(lines).replace(' ', '')
        for name in self.names:
            self.assertIn(name, text)
        self.assertTrue(all(len(line)<=23 for line in lines))

    def test_snapshot_folds_have_independent_stable_identity(self):
        self.snapshots.append(GhostSnapshot(name='Reference B',uid='b',
            object_names={'SecondRig'},bone_names={'SecondBone'}))
        layout = self.draw({'ghost_capture_targets','ghost_snapshot_targets_a'})
        details = ''.join(c[1] for c in layout.calls if c[0]=='label'
                          and c[3].endswith('/ghost_snapshot_targets_b/body')).replace(' ', '')
        self.assertIn('SecondBone', details)
        self.assertNotIn('mixamorig:', ''.join(c[1] for c in layout.calls if c[0]=='label'))
        self.snapshots.reverse()
        self.snapshots[0].name='Renamed reference'
        other=self.draw({'ghost_capture_targets','ghost_snapshot_targets_a'})
        self.assertEqual({c[1] for c in layout.calls if c[0]=='panel'},
                         {c[1] for c in other.calls if c[0]=='panel'})

    def test_binding_warning_and_recovery_remain_visible_with_details_closed(self):
        layout=self.draw({'ghost_capture_targets','ghost_snapshot_targets_a'},
                         reason='Imported reference. Bind explicitly before restoring.')
        labels=' '.join(c[1] for c in layout.calls if c[0]=='label')
        self.assertIn('Bind explicitly',labels)
        self.assertNotIn('mixamorig:',labels)
        self.assertIn('ghost_tool.bind_snapshot',[c[1] for c in layout.calls if c[0]=='op'])

    def test_no_capture_targets_keeps_recovery_and_save_visible(self):
        self.samples=[]
        layout=self.draw({'ghost_snapshot_targets_a'})
        labels=' '.join(c[1] for c in layout.calls if c[0]=='label')
        self.assertIn('show markers for the chosen target first',labels)
        self.assertNotIn('ghost_capture_targets',[c[1] for c in layout.calls if c[0]=='panel'])
        self.assertIn('ghost_tool.take_snapshot',[c[1] for c in layout.calls if c[0]=='op'])

    def test_compact_capture_counts_unique_targets_without_writing(self):
        with patch.object(tb,'selected_samples',return_value=(self.samples*3,'')) as samples:
            label=tb.capture_label(self.context,compact=True)
        self.assertEqual(label,'Capture: Armature / 65 bones')
        self.assertEqual(samples.call_args.kwargs,{'assign':False})


if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(CompareTargetsUI))
    if not result.wasSuccessful():
        raise RuntimeError('Compare target UI checks failed')
