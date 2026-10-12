"""Display-location behavior; run in factory-startup Blender/Bforartists."""
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import bpy
import ghost_tool
from ghost_tool import ui_panel as ui, preferences
from test_ghost_marker_targets_ui import Layout


def context_for(location='HEADER', window=None):
    return NS(scene=bpy.context.scene, window=window or bpy.context.window,
              space_data=NS(show_toolshelf_tabs=True),
              preferences=NS(addons={'ghost_tool': NS(preferences=NS(display_location=location))}))


class DisplayLocation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with patch.object(ghost_tool, '_clear_pycache'):
            ghost_tool.register()

    @classmethod
    def tearDownClass(cls):
        ghost_tool.unregister()

    def tearDown(self):
        ui._ghost_windows.clear()
        if hasattr(ui, '_pending_display_tabs'):
            ui._pending_display_tabs.clear()

    def test_enum_default_and_labels(self):
        prop = preferences.GhostToolPreferences.bl_rna.properties['display_location']
        self.assertEqual(prop.default, 'HEADER')
        self.assertEqual([(v.identifier, v.name) for v in prop.enum_items],
                         [('HEADER', 'Top Header'), ('SIDEBAR', 'Right Sidebar (N)'),
                          ('TOOLS', 'Left Tool Shelf (T)')])
        self.assertFalse(prop.is_skip_save)

    def test_missing_preferences_and_invalid_value_use_header(self):
        for context in (NS(), NS(preferences=NS(addons={})), context_for('unknown')):
            self.assertEqual(ui.display_location(context), 'HEADER')

    def test_exactly_one_full_home_for_each_supported_choice(self):
        panels = (ui.GHOST_PT_header_menu, ui.GHOST_PT_sidebar, ui.GHOST_PT_tool_shelf)
        with patch.object(ui, 'supports_tool_shelf', return_value=True):
            for location, expected in [('HEADER', 0), ('SIDEBAR', 1), ('TOOLS', 2)]:
                self.assertEqual([p.poll(context_for(location)) for p in panels],
                                 [i == expected for i in range(3)])

    def test_unsupported_left_choice_retains_header_access(self):
        context = context_for('TOOLS')
        with patch.object(ui, 'supports_tool_shelf', return_value=False):
            self.assertEqual(ui.display_location(context), 'HEADER')
            self.assertTrue(ui.GHOST_PT_header_menu.poll(context))
            self.assertFalse(ui.GHOST_PT_sidebar.poll(context))
            self.assertFalse(ui.GHOST_PT_tool_shelf.poll(context))
            self.assertEqual(context.preferences.addons['ghost_tool'].preferences.display_location, 'TOOLS')

    def test_separate_and_editor_windows_have_no_duplicate_main_home(self):
        context = context_for('SIDEBAR')
        ui._ghost_windows.add(context.window.as_pointer())
        self.assertTrue(ui.GHOST_PT_window.poll(context))
        self.assertFalse(ui.GHOST_PT_sidebar.poll(context))
        ui._ghost_windows.clear()
        with patch('ghost_tool.settings_editor.is_editor', return_value=True):
            self.assertFalse(ui.GHOST_PT_sidebar.poll(context))

    def test_header_entry_is_hidden_for_side_home(self):
        for location in ('HEADER', 'SIDEBAR'):
            layout = NS(row=lambda **kw: NS(prop=lambda *a, **kw: None,
                           popover=lambda **kw: entries.append(kw['panel'])))
            entries = []
            ui._draw_viewport_header_menu(NS(layout=layout), context_for(location))
            self.assertEqual(entries, ['GHOST_PT_header_menu'] if location == 'HEADER' else [])

    def test_all_homes_use_shared_drawer_distinct_folds_and_footer(self):
        prefixes = []
        for cls in (ui.GHOST_PT_header_menu, ui.GHOST_PT_sidebar, ui.GHOST_PT_tool_shelf):
            layout = Layout()
            with patch.object(ui, 'draw_ghost_tool') as draw:
                cls.draw(NS(layout=layout), bpy.context)
                prefixes.append(draw.call_args.args[2])
            self.assertIn('ghost_tool.open_window', [c[1] for c in layout.calls if c[0] == 'op'])
            self.assertIn('ghost_tool.open_settings_editor', [c[1] for c in layout.calls if c[0] == 'op'])
        self.assertEqual(len(set(prefixes)), 3)

    def test_full_controls_and_target_folds_survive_every_home(self):
        bpy.context.scene.ghost_tool.is_active = True
        from ghost_tool.snapshot import SnapshotStore
        from ghost_tool.ghost_data import GhostStore, Ghost
        bpy.context.active_object.keyframe_insert('location', frame=1)
        GhostStore.get(bpy.context.scene).add(Ghost(frame=1,
            object_name=bpy.context.active_object.name, channel='location.x',
            parent_frame_a=1, parent_frame_b=1))
        snap, error = SnapshotStore.get(bpy.context.scene).take_snapshot(
            'Location test', bpy.context.scene, context=bpy.context, scope='ACTIVE')
        self.assertIsNotNone(snap, error)
        try:
            from ghost_tool import target_binding
            samples = [NS(object_name=bpy.context.active_object.name, bone_name='Bone A'),
                       NS(object_name=bpy.context.active_object.name, bone_name='Bone B')]
            for cls, prefix in ((ui.GHOST_PT_header_menu, 'menu'),
                                (ui.GHOST_PT_sidebar, 'sidebar'), (ui.GHOST_PT_tool_shelf, 'shelf')):
                layout = Layout(closed={'ghost_marker_targets', 'ghost_capture_targets',
                                        f'ghost_snapshot_targets_{snap.uid}'})
                with patch.object(target_binding, 'selected_samples', return_value=(samples, '')), \
                     patch.object(ui, '_marker_target_bones', return_value=['Bone A', 'Bone B']):
                    cls.draw(NS(layout=layout), bpy.context)
                folds = [c[1] for c in layout.calls if c[0] == 'panel']
                for section in ui.GHOST_SECTIONS:
                    self.assertIn(f'ghost_tool_{prefix}_{section[0]}', folds)
                self.assertIn('ghost_capture_targets', folds)
                self.assertIn('ghost_marker_targets', folds)
                self.assertIn(f'ghost_snapshot_targets_{snap.uid}', folds)
                self.assertIn('ghost_tool.take_snapshot', [c[1] for c in layout.calls if c[0] == 'op'])
        finally:
            SnapshotStore.get(bpy.context.scene).delete_snapshot(snap.uid)

    def test_switch_reveals_region_redraws_and_selects_after_layout(self):
        for location, region_type in [('SIDEBAR', 'UI'), ('TOOLS', 'TOOLS')]:
            space = NS(show_region_ui=False, show_region_toolbar=False, show_toolshelf_tabs=False)
            region = NS(type=region_type, active_panel_category='Old Tab')
            redraws = []
            area = NS(type='VIEW_3D', spaces=NS(active=space), regions=[region],
                      as_pointer=lambda: 5, tag_redraw=lambda: redraws.append(True))
            window = NS(screen=NS(areas=[area]), as_pointer=lambda: 9)
            context = context_for(location, window)
            context.window_manager = NS(windows=[window])
            with patch.object(ui, 'supports_tool_shelf', return_value=True), \
                 patch('ghost_tool.settings_editor.is_editor', return_value=False), \
                 patch.object(bpy.app.timers, 'register'), \
                 patch.object(bpy.app.timers, 'is_registered', return_value=False):
                ui.update_display_location(context)
            self.assertTrue(redraws)
            self.assertTrue(space.show_region_ui if location == 'SIDEBAR' else space.show_region_toolbar)
            if location == 'TOOLS':
                self.assertTrue(space.show_toolshelf_tabs)
            with patch.object(ui, 'display_location', return_value=location), \
                 patch.object(ui, '_display_windows', return_value=[window]):
                self.assertIsNone(ui._select_display_tabs())
            self.assertEqual(region.active_panel_category, 'Ghost Tool')

    def test_delayed_tab_selection_cannot_undo_new_choice(self):
        region = NS(type='UI', active_panel_category='User Tab')
        area = NS(regions=[region], as_pointer=lambda: 5)
        window = NS(screen=NS(areas=[area]), as_pointer=lambda: 9)
        ui._pending_display_tabs[(9, 5)] = ('SIDEBAR', 0)
        with patch.object(ui, 'display_location', return_value='HEADER'), \
             patch.object(ui, '_display_windows', return_value=[window]):
            self.assertIsNone(ui._select_display_tabs())
        self.assertEqual(region.active_panel_category, 'User Tab')

    def test_registration_matches_host_and_is_clean_on_reload(self):
        supported = ui.supports_tool_shelf()
        self.assertEqual(ui._shelf_registered,
                         [ui.GHOST_PT_tool_shelf, ui.GHOST_PT_shelf_object, ui.GHOST_PT_shelf_pose]
                         if supported else [])
        ui._pending_display_tabs[(0, 0)] = ('SIDEBAR', 0)
        if not bpy.app.timers.is_registered(ui._select_display_tabs):
            bpy.app.timers.register(ui._select_display_tabs, first_interval=1)
        ghost_tool.unregister()
        self.assertFalse(ui._pending_display_tabs)
        self.assertFalse(bpy.app.timers.is_registered(ui._select_display_tabs))
        self.assertFalse(ui.GHOST_PT_sidebar.is_registered)
        with patch.object(ghost_tool, '_clear_pycache'):
            ghost_tool.register()
        self.assertTrue(ui.GHOST_PT_sidebar.is_registered)


if __name__ == '__main__':
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(DisplayLocation))
    if not result.wasSuccessful():
        raise RuntimeError('Display location checks failed')
