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


class HeaderLayout(Layout):
    def row(self, **kwargs):
        return HeaderLayout(self.calls, self.closed, self.path)

    def popover(self, **kwargs):
        self.calls.append(('popover', kwargs['panel'], kwargs, self.path))


def context_for(location='TOOLBAR', window=None, visible=True):
    return NS(scene=bpy.context.scene, window=window or bpy.context.window,
              space_data=NS(show_toolshelf_tabs=True),
              preferences=NS(addons={'ghost_tool': NS(preferences=NS(
                  display_location=location, show_toolbar=visible))}))


def viewport_fixture(pointer, *, visible=False):
    redraws = []
    space = NS(show_region_tool_header=visible, show_region_ui=False,
               show_region_toolbar=False, show_toolshelf_tabs=False)
    area = NS(type='VIEW_3D', spaces=NS(active=space), regions=[],
              as_pointer=lambda: pointer, tag_redraw=lambda: redraws.append(True))
    return area, space, redraws


class DisplayLocation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with patch.object(ghost_tool, '_clear_pycache'):
            ghost_tool.register()
        bpy.ops.mesh.primitive_cube_add()

    @classmethod
    def tearDownClass(cls):
        ghost_tool.unregister()

    def tearDown(self):
        ui._ghost_windows.clear()
        if hasattr(ui, '_pending_display_tabs'):
            ui._pending_display_tabs.clear()

    def test_enum_default_and_labels(self):
        prop = preferences.GhostToolPreferences.bl_rna.properties['display_location']
        self.assertEqual(prop.default, 'TOOLBAR')
        self.assertEqual([(v.identifier, v.name) for v in prop.enum_items],
                         [('TOOLBAR', 'Top Toolbar'), ('SIDEBAR', 'Right Sidebar (N)'),
                          ('TOOLS', 'Left Tool Shelf (T)')])
        self.assertEqual({v.identifier: v.value for v in prop.enum_items},
                         {'TOOLBAR': 3, 'SIDEBAR': 1, 'TOOLS': 2})
        self.assertFalse(prop.is_skip_save)
        visibility = preferences.GhostToolPreferences.bl_rna.properties['show_toolbar']
        self.assertTrue(visibility.default)
        self.assertFalse(visibility.is_skip_save)
        action = bpy.ops.ghost_tool.set_toolbar_visibility.get_rna_type().properties['show']
        self.assertTrue(action.is_hidden)
        self.assertTrue(action.is_skip_save)

    def test_missing_preferences_and_legacy_value_use_toolbar(self):
        for context in (NS(), NS(preferences=NS(addons={})), context_for('unknown'), context_for('HEADER')):
            self.assertEqual(ui.display_location(context), 'TOOLBAR')

    def test_saved_enum_values_and_header_migration(self):
        addon = bpy.context.preferences.addons.get('ghost_tool')
        created = addon is None
        if created:
            addon = bpy.context.preferences.addons.new()
            addon.module = 'ghost_tool'
        prefs = addon.preferences
        original = (prefs.display_location, prefs.show_toolbar)
        try:
            # Install the old schema to write exactly the values an upgrade
            # loads; AddonPreferences has no Python IDProperty access.
            class LegacyPreferences(bpy.types.AddonPreferences):
                bl_idname = 'ghost_tool'
                display_location: bpy.props.EnumProperty(items=(
                    ('HEADER', 'Header', '', 0), ('SIDEBAR', 'Sidebar', '', 1),
                    ('TOOLS', 'Tools', '', 2), ('TOOLBAR', 'Toolbar', '', 3)), default='HEADER')
                show_toolbar: bpy.props.BoolProperty(default=True)
            for name in ('SIDEBAR', 'TOOLS', 'TOOLBAR', 'HEADER'):
                bpy.utils.unregister_class(preferences.GhostToolPreferences)
                bpy.utils.register_class(LegacyPreferences)
                prefs = addon.preferences
                prefs.display_location = name
                prefs.show_toolbar = False
                bpy.utils.unregister_class(LegacyPreferences)
                bpy.utils.register_class(preferences.GhostToolPreferences)
                prefs = addon.preferences
                preferences.migrate_display_location(bpy.context)
                self.assertEqual(prefs.display_location, 'TOOLBAR' if name == 'HEADER' else name)
                self.assertEqual(prefs.show_toolbar, name == 'HEADER')
                preferences.migrate_display_location(bpy.context)
                self.assertEqual(prefs.display_location, 'TOOLBAR' if name == 'HEADER' else name)
        finally:
            prefs.display_location, prefs.show_toolbar = original
            if created:
                bpy.context.preferences.addons.remove(addon)

    def test_exactly_one_full_home_for_each_supported_choice(self):
        panels = (ui.GHOST_PT_header_menu, ui.GHOST_PT_sidebar, ui.GHOST_PT_tool_shelf)
        with patch.object(ui, 'supports_tool_shelf', return_value=True):
            for location, expected in [('SIDEBAR', 1), ('TOOLS', 2)]:
                self.assertEqual([p.poll(context_for(location)) for p in panels],
                                 [i == expected for i in range(3)])
            self.assertEqual([p.poll(context_for('TOOLBAR')) for p in panels], [True, False, False])

    def test_unsupported_left_choice_uses_toolbar_with_recovery_access(self):
        context = context_for('TOOLS')
        with patch.object(ui, 'supports_tool_shelf', return_value=False):
            self.assertEqual(ui.display_location(context), 'TOOLBAR')
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

    def test_visible_toolbar_and_side_homes_have_no_view_recovery_duplicate(self):
        for location in ('HEADER', 'TOOLBAR', 'SIDEBAR', 'TOOLS'):
            layout = HeaderLayout()
            with patch.object(ui, 'supports_tool_shelf', return_value=True):
                ui._draw_viewport_view_menu(NS(layout=layout), context_for(location))
            self.assertFalse(layout.calls)

    def test_view_recovery_is_available_for_both_hidden_states(self):
        for ghost_visible, native_visible in ((False, True), (True, False), (False, False)):
            context = context_for('TOOLBAR', visible=ghost_visible)
            context.space_data.show_region_tool_header = native_visible
            layout = HeaderLayout()
            ui._draw_viewport_view_menu(NS(layout=layout), context)
            self.assertEqual([c[1] for c in layout.calls if c[0] == 'op'],
                             ['ghost_tool.set_toolbar_visibility'])
            self.assertIn('Show Ghost Toolbar', [c[2] for c in layout.calls if c[0] == 'op'])
            self.assertEqual(context.space_data.show_region_tool_header, native_visible)

    def test_toolbar_recovery_excludes_legacy_windows(self):
        context = context_for('TOOLBAR')
        ui._ghost_windows.add(context.window.as_pointer())
        self.assertFalse(ui.GHOST_PT_header_menu.poll(context))
        layout = HeaderLayout()
        ui._draw_viewport_view_menu(NS(layout=layout), context)
        self.assertFalse(layout.calls)
        ui._ghost_windows.clear()
        with patch('ghost_tool.settings_editor.is_editor', return_value=True):
            self.assertFalse(ui.GHOST_PT_header_menu.poll(context))

    def test_toolbar_choice_reveals_all_ordinary_viewports_without_tab_timer(self):
        view_a, space_a, redraw_a = viewport_fixture(11)
        view_b, space_b, redraw_b = viewport_fixture(12)
        legacy_view, legacy_space, legacy_redraw = viewport_fixture(13)
        editor_view, editor_space, editor_redraw = viewport_fixture(17)
        window_a = NS(screen=NS(areas=[view_a]), as_pointer=lambda: 101)
        window_b = NS(screen=NS(areas=[view_b]), as_pointer=lambda: 102)
        legacy_window = NS(screen=NS(areas=[legacy_view]), as_pointer=lambda: 103)
        editor_window = NS(screen=NS(areas=[editor_view]), as_pointer=lambda: 107)
        ui._ghost_windows.add(103)
        context = context_for('TOOLBAR', window_a)
        context.window_manager = NS(windows=[window_a, window_b, legacy_window, editor_window])
        with patch('ghost_tool.settings_editor.is_editor',
                   side_effect=lambda ctx: ctx.window.as_pointer() == 107), \
             patch.object(bpy.app.timers, 'register') as timer:
            ui.update_display_location(context)
        self.assertTrue(space_a.show_region_tool_header)
        self.assertTrue(space_b.show_region_tool_header)
        self.assertFalse(legacy_space.show_region_tool_header)
        self.assertFalse(editor_space.show_region_tool_header)
        self.assertTrue(redraw_a and redraw_b)
        self.assertFalse(legacy_redraw)
        self.assertFalse(editor_redraw)
        self.assertFalse(ui._pending_display_tabs)
        timer.assert_not_called()

    def test_hidden_toolbar_and_draw_do_not_force_native_row(self):
        view, space, redraws = viewport_fixture(14)
        window = NS(screen=NS(areas=[view]), as_pointer=lambda: 104)
        context = context_for('TOOLBAR', window, visible=False)
        self.assertEqual(ui.display_location(context), 'TOOLBAR')
        context.window_manager = NS(windows=[window])
        with patch('ghost_tool.settings_editor.is_editor', return_value=False):
            ui.update_display_location(context)
        self.assertFalse(space.show_region_tool_header)
        self.assertTrue(redraws)
        context.preferences.addons['ghost_tool'].preferences.show_toolbar = True
        ui._draw_viewport_view_menu(NS(layout=HeaderLayout()), context)
        self.assertFalse(space.show_region_tool_header)
        self.assertTrue(ui.GHOST_PT_header_menu.poll(context))

    def test_explicit_show_recovers_hidden_row_even_when_preference_was_true(self):
        view, space, _ = viewport_fixture(15)
        window = NS(screen=NS(areas=[view]), as_pointer=lambda: 105)
        context = context_for('TOOLBAR', window)
        context.window_manager = NS(windows=[window])
        with patch('ghost_tool.settings_editor.is_editor', return_value=False):
            result = ui.GHOST_OT_set_toolbar_visibility.execute(NS(show=True), context)
        self.assertEqual(result, {'FINISHED'})
        self.assertTrue(space.show_region_tool_header)

    def test_hide_preserves_native_row_cache_and_scene_settings(self):
        from ghost_tool.ghost_data import GhostStore, Ghost
        view, space, redraws = viewport_fixture(16, visible=True)
        window = NS(screen=NS(areas=[view]), as_pointer=lambda: 106)
        context = context_for('TOOLBAR', window)
        context.window_manager = NS(windows=[window])
        store = GhostStore.get(context.scene)
        marker = Ghost(frame=23, object_name=bpy.context.active_object.name,
                       channel='location.y', parent_frame_a=20, parent_frame_b=30)
        store.add(marker)
        settings = context.scene.ghost_tool
        original = (settings.is_active, settings.show_level_1, settings.show_mesh_ghosts,
                    settings.live_point_ghosts, settings.live_mesh_ghosts)
        count = len(store)
        with patch('ghost_tool.settings_editor.is_editor', return_value=False):
            result = ui.GHOST_OT_set_toolbar_visibility.execute(NS(show=False), context)
        self.assertEqual(result, {'FINISHED'})
        self.assertFalse(context.preferences.addons['ghost_tool'].preferences.show_toolbar)
        self.assertEqual(ui.display_location(context), 'TOOLBAR')
        self.assertTrue(space.show_region_tool_header)
        self.assertTrue(redraws)
        self.assertEqual(len(store), count)
        self.assertEqual(original, (settings.is_active, settings.show_level_1, settings.show_mesh_ghosts,
                                  settings.live_point_ghosts, settings.live_mesh_ghosts))
        context.preferences.addons['ghost_tool'].preferences.display_location = 'SIDEBAR'
        with patch('ghost_tool.settings_editor.is_editor', return_value=False):
            ui.update_display_location(context)
        self.assertTrue(space.show_region_tool_header)

    def test_show_selects_toolbar_and_visibility_callback_only_reveals_its_home(self):
        view, space, redraws = viewport_fixture(18)
        window = NS(screen=NS(areas=[view]), as_pointer=lambda: 108)
        context = context_for('SIDEBAR', window, visible=False)
        context.window_manager = NS(windows=[window])
        prefs = context.preferences.addons['ghost_tool'].preferences
        with patch('ghost_tool.settings_editor.is_editor', return_value=False):
            preferences._update_toolbar_visibility(prefs, context)
            self.assertFalse(space.show_region_tool_header)
            self.assertFalse(space.show_region_ui)
            self.assertFalse(redraws)  # Callbacks must not traverse startup RNA.
            ui.update_toolbar_visibility(context)  # Deferred body's current context.
            self.assertTrue(redraws)
            result = ui.GHOST_OT_set_toolbar_visibility.execute(NS(show=True), context)
        self.assertEqual(result, {'FINISHED'})
        self.assertEqual(prefs.display_location, 'TOOLBAR')
        self.assertTrue(prefs.show_toolbar)
        self.assertTrue(space.show_region_tool_header)

    def test_all_homes_share_drawer_and_keep_legacy_launch_buttons_removed(self):
        prefixes = []
        for cls in (ui.GHOST_PT_sidebar, ui.GHOST_PT_tool_shelf):
            layout = Layout()
            with patch.object(ui, 'draw_ghost_tool') as draw:
                cls.draw(NS(layout=layout), bpy.context)
                prefixes.append(draw.call_args.args[2])
            self.assertNotIn('ghost_tool.open_window', [c[1] for c in layout.calls if c[0] == 'op'])
            self.assertNotIn('ghost_tool.open_settings_editor', [c[1] for c in layout.calls if c[0] == 'op'])
        self.assertEqual(len(set(prefixes)), 2)

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
            for cls, prefix in ((ui.GHOST_PT_sidebar, 'sidebar'), (ui.GHOST_PT_tool_shelf, 'shelf')):
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
                self.assertNotIn('ghost_tool.open_settings_editor',
                                 [c[1] for c in layout.calls if c[0] == 'op'])
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
        with patch.object(ui, 'display_location', return_value='TOOLBAR'), \
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
