"""Marker target folding: run in factory-startup Bforartists."""
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import bpy
import ghost_tool
from ghost_tool import ui_panel as ui


class Layout:
    def __init__(self, calls=None, closed=None, path='root'):
        self.calls = calls if calls is not None else []
        self.closed = closed or set()
        self.path = path

    def row(self, **kwargs):
        return Layout(self.calls, self.closed, self.path)

    column = row
    box = row

    def panel(self, key, **kwargs):
        self.calls.append(('panel', key, kwargs, self.path))
        header = Layout(self.calls, self.closed, self.path + '/' + key + '/header')
        body = None if key in self.closed else Layout(
            self.calls, self.closed, self.path + '/' + key + '/body')
        return header, body

    def label(self, text='', **kwargs):
        self.calls.append(('label', text, kwargs, self.path))

    def operator(self, name, text='', **kwargs):
        self.calls.append(('op', name, text, self.path))
        return SimpleNamespace()

    def prop(self, data, name, **kwargs):
        self.calls.append(('prop', name, kwargs, self.path))

    def menu(self, name, **kwargs):
        self.calls.append(('menu', name, kwargs, self.path))

    def separator(self, **kwargs):
        pass

    def template_list(self, name, *args, **kwargs):
        self.calls.append(('list', name, kwargs, self.path))


class MarkerTargetsUI(unittest.TestCase):
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
        self.bones = [SimpleNamespace(name=f'mixamorig:LongCharacterFingerBone{i:02}',
                                      bone=SimpleNamespace(select=False)) for i in range(65)]
        self.rig = SimpleNamespace(name='Armature', type='ARMATURE',
                                   pose=SimpleNamespace(bones=self.bones))
        self.context = SimpleNamespace(scene=self.scene, active_object=self.rig,
            selected_pose_bones=[], window=bpy.context.window,
            region=SimpleNamespace(width=220, type='UI'),
            preferences=SimpleNamespace(view=SimpleNamespace(ui_scale=1)))

    def test_closed_targets_keep_actions_options_and_other_sections_visible(self):
        layout = Layout(closed={'ghost_marker_targets'})
        ui.draw_ghost_tool(layout, self.context, 'menu')
        labels = [c[1] for c in layout.calls if c[0] == 'label']
        self.assertIn('Onion Skin', labels)
        self.assertIn('Edit Motion', labels)
        self.assertIn('Settings', labels)
        self.assertFalse(any('mixamorig:' in label for label in labels))
        self.assertIn('65 bones', ' '.join(labels))
        actions = [c[1] for c in layout.calls if c[0] == 'op']
        self.assertIn('ghost_tool.generate_ghosts', actions)
        self.assertIn('ghost_tool.clear_ghosts', actions)
        self.assertIn('ghost_tool.generate_mesh_ghosts', actions)
        self.assertIn('live_point_ghosts', [c[1] for c in layout.calls if c[0] == 'prop'])
        folds = [c for c in layout.calls if c[0] == 'panel' and c[1] == 'ghost_marker_targets']
        self.assertEqual(len(folds), 1)
        self.assertTrue(folds[0][2]['default_closed'])

    def test_open_targets_preserve_every_full_bone_name_at_narrow_width(self):
        layout = Layout()
        ui._draw_show_ghosts(layout, self.context)
        details = [c[1] for c in layout.calls if c[0] == 'label'
                   and c[3].endswith('/ghost_marker_targets/body')]
        self.assertTrue(details)
        joined = ''.join(details).replace(' ', '')
        for bone in self.bones:
            self.assertIn(bone.name, joined)
        self.assertTrue(all(len(line) <= 23 for line in details))

    def test_selected_bones_determine_the_count_and_details(self):
        self.context.selected_pose_bones = self.bones[:2]
        layout = Layout()
        ui._draw_show_ghosts(layout, self.context)
        labels = [c[1] for c in layout.calls if c[0] == 'label']
        self.assertIn('2 bones', ' '.join(labels))
        text = ''.join(labels).replace(' ', '')
        self.assertIn(self.bones[0].name, text)
        self.assertNotIn(self.bones[2].name, text)

    def test_collapsed_show_section_does_not_collapse_onion_or_other_tools(self):
        layout = Layout(closed={'ghost_tool_menu_show'})
        ui.draw_ghost_tool(layout, self.context, 'menu')
        actions = [c[1] for c in layout.calls if c[0] == 'op']
        self.assertNotIn('ghost_tool.generate_ghosts', actions)
        self.assertIn('ghost_tool.generate_mesh_ghosts', actions)
        labels = [c[1] for c in layout.calls if c[0] == 'label']
        self.assertIn('Motion Paths', labels)
        self.assertIn('Settings', labels)

    def test_object_only_has_a_compact_target_without_an_empty_fold(self):
        self.context.active_object = SimpleNamespace(name='Cube', type='MESH')
        layout = Layout()
        ui._draw_show_ghosts(layout, self.context)
        self.assertIn('Markers: Cube', [c[1] for c in layout.calls if c[0] == 'label'])
        self.assertNotIn('ghost_marker_targets', [c[1] for c in layout.calls if c[0] == 'panel'])

    def test_missing_target_keeps_the_action_and_recovery_message(self):
        self.context.active_object = None
        layout = Layout()
        ui._draw_show_ghosts(layout, self.context)
        self.assertIn('select an animated object', ' '.join(
            c[1] for c in layout.calls if c[0] == 'label'))
        self.assertIn('ghost_tool.generate_ghosts', [c[1] for c in layout.calls if c[0] == 'op'])


if __name__ == '__main__':
    result = unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(MarkerTargetsUI))
    if not result.wasSuccessful():
        raise RuntimeError('Marker target UI checks failed')
