"""Toolbar behavior checks; run in factory-startup Blender/Bforartists."""
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import bpy
import ghost_tool
from ghost_tool import ui_panel as ui


class Layout:
    def __init__(self, calls=None, closed=None, enabled=True):
        self.calls = [] if calls is None else calls
        self.closed = set() if closed is None else closed
        self.enabled = enabled

    def row(self, **kwargs):
        return Layout(self.calls, self.closed, self.enabled)

    column = row
    box = row

    def panel(self, key, **kwargs):
        self.calls.append(('panel', key, kwargs, self.enabled))
        return self.row(), None if key in self.closed else self.row()

    def label(self, **kwargs):
        self.calls.append(('label', kwargs.get('text'), kwargs, self.enabled))

    def prop(self, data, name, **kwargs):
        self.calls.append(('prop', name, kwargs, self.enabled))

    def operator(self, name, **kwargs):
        result = NS()
        self.calls.append(('operator', name, kwargs, self.enabled, result))
        return result

    def popover(self, **kwargs):
        self.calls.append(('popover', kwargs['panel'], kwargs, self.enabled))

    def menu(self, name, **kwargs):
        self.calls.append(('menu', name, kwargs, self.enabled))

    def separator(self, **kwargs):
        self.calls.append(('separator', None, kwargs, self.enabled))

    separator_spacer = separator

    def template_list(self, *args, **kwargs):
        pass


def context_for(width=2400, scale=1.0, mode='OBJECT', active=None):
    return NS(scene=bpy.context.scene, active_object=active, selected_pose_bones=[],
        mode=mode, area=NS(as_pointer=lambda: 123, width=width), window=None,
        space_data=NS(), region=NS(width=width, type='TOOL_HEADER'),
        preferences=NS(view=NS(ui_scale=scale), addons={'ghost_tool': NS(
            preferences=NS(display_location='TOOLBAR', show_toolbar=True))}))


class ToolbarUI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Only the platform registration gate is substituted on the stand-in.
        with patch.object(ghost_tool, '_is_bforartists', return_value=True), \
             patch.object(ghost_tool, '_clear_pycache'):
            ghost_tool.register()

    @classmethod
    def tearDownClass(cls):
        ghost_tool.unregister()

    def setUp(self):
        bpy.context.scene.ghost_tool['is_active'] = True

    def draw(self, context):
        layout = Layout()
        ui._draw_viewport_tool_header(NS(layout=layout), context)
        return layout.calls

    def test_full_toolbar_keeps_same_controls_at_every_width_and_scale(self):
        wide = self.draw(context_for())
        panels = [c[1] for c in wide if c[0] == 'popover']
        self.assertEqual(panels, ['GHOST_PT_toolbar_menu', 'GHOST_PT_marker_options',
            'GHOST_PT_skin_options', 'GHOST_PT_paths_popover', 'GHOST_PT_edit_popover',
            'GHOST_PT_compare_popover', 'GHOST_PT_physics_popover',
            'GHOST_PT_look_popover', 'GHOST_PT_settings_popover'])
        def controls(calls):
            return [(c[0], c[1], c[2], c[3]) for c in calls
                    if c[0] in {'operator', 'popover', 'prop'}]
        for mode in ('OBJECT', 'POSE'):
            for width, scale in ((2400, 1), (1400, 1), (1050, 1),
                                 (530, 1), (530, 1.5), (2400, 2)):
                with self.subTest(mode=mode, width=width, scale=scale):
                    self.assertEqual(controls(self.draw(context_for(width, scale, mode))),
                                     controls(wide))
        menu = Layout()
        ui._draw_toolbar_menu(menu, context_for(600))
        self.assertEqual([c[1] for c in menu.calls if c[0] == 'popover'], panels[1:])
        self.assertNotIn('ghost_tool.restore_snapshot', [c[1] for c in menu.calls])

    def test_other_modes_keep_the_existing_minimal_layout(self):
        self.assertEqual(ui._toolbar_tier(context_for(2400)), 'FULL')
        self.assertEqual(ui._toolbar_tier(context_for(2400, 1, 'SCULPT')), 'MINIMAL')
        self.assertEqual([c[1] for c in self.draw(context_for(530, 2, 'SCULPT'))
                          if c[0] == 'popover'], ['GHOST_PT_toolbar_menu'])

    def test_missing_targets_keep_options_enabled_and_options_do_not_generate(self):
        calls = self.draw(context_for(active=None))
        arrows = [c for c in calls if c[0] == 'popover' and c[1] in
                  {'GHOST_PT_marker_options', 'GHOST_PT_skin_options'}]
        self.assertEqual(len(arrows), 2)
        self.assertTrue(all(c[3] for c in arrows))
        for cls, flag in ((ui.GHOST_PT_marker_options, 'show_cached_markers'),
                          (ui.GHOST_PT_skin_options, 'show_cached_skin')):
            self.assertTrue(cls.poll(context_for(active=None)))
            panel = NS(layout=Layout(), section_key=cls.section_key)
            cls.draw(panel, context_for(active=None))
            self.assertEqual(panel.layout.calls[0][0:2], ('prop', flag))
            self.assertFalse(any(c[0] == 'operator' and c[1] in {
                'ghost_tool.generate_ghosts', 'ghost_tool.generate_mesh_ghosts'}
                for c in panel.layout.calls))

    def test_hidden_location_and_inactive_recovery(self):
        context = context_for()
        context.preferences.addons['ghost_tool'].preferences.show_toolbar = False
        self.assertEqual(self.draw(context), [])
        context.preferences.addons['ghost_tool'].preferences.show_toolbar = True
        context.preferences.addons['ghost_tool'].preferences.display_location = 'SIDEBAR'
        self.assertEqual(self.draw(context), [])
        bpy.context.scene.ghost_tool['is_active'] = False
        menu = Layout()
        ui._draw_toolbar_menu(menu, context_for())
        self.assertIn('is_active', [c[1] for c in menu.calls if c[0] == 'prop'])
        self.assertEqual(len([c for c in menu.calls if c[0] == 'popover']), 8)
        self.assertIn('ghost_tool.set_toolbar_visibility', [c[1] for c in menu.calls])

    def test_native_row_hidden_has_direct_show_recovery(self):
        context = context_for()
        context.space_data.show_region_tool_header = False
        menu = Layout()
        ui.GHOST_PT_header_menu.draw(NS(layout=menu), context)
        recovery = [c for c in menu.calls if c[1] == 'ghost_tool.set_toolbar_visibility'][0]
        self.assertEqual(recovery[2]['text'], 'Show Toolbar')
        self.assertTrue(recovery[4].show)
        self.assertFalse(context.space_data.show_region_tool_header)

    def test_target_fold_reuses_state_and_leaves_other_options_reachable(self):
        bone = NS(name='LongTargetBone', bone=NS(select=True))
        rig = NS(name='Rig', type='ARMATURE', pose=NS(bones=[bone]))
        context = context_for(active=rig)
        panel = NS(layout=Layout(closed={'ghost_marker_targets'}), section_key='show')
        ui.GHOST_PT_marker_options.draw(panel, context)
        self.assertIn('ghost_marker_targets', [c[1] for c in panel.layout.calls if c[0] == 'panel'])
        self.assertNotIn('Rig / LongTargetBone', ' '.join(str(c[1]) for c in panel.layout.calls))
        self.assertIn('live_point_ghosts', [c[1] for c in panel.layout.calls if c[0] == 'prop'])
        self.assertNotIn('ghost_marker_sampling_options', [c[1] for c in panel.layout.calls])
        full = Layout(closed={'ghost_marker_targets'})
        ui._draw_show_ghosts(full, context)
        self.assertIn('ghost_marker_targets', [c[1] for c in full.calls if c[0] == 'panel'])
        self.assertIn('ghost_marker_sampling_options', [c[1] for c in full.calls if c[0] == 'panel'])

    def test_draw_preserves_frame_and_generated_data_and_native_header(self):
        from ghost_tool.ghost_data import GhostStore
        from ghost_tool.ghost_pipeline import GhostPipeline
        store = GhostStore.get(bpy.context.scene)
        before = (bpy.context.scene.frame_current, len(store))
        fail = AssertionError('drawing must not schedule or evaluate previews')
        with patch.object(ui, 'update_display_location', side_effect=AssertionError('draw mutated region')), \
             patch.object(GhostPipeline, 'mark_dirty', side_effect=fail), \
             patch.object(GhostPipeline, 'mark_object_dirty', side_effect=fail), \
             patch.object(GhostPipeline, '_evaluate_ghosts', side_effect=fail), \
             patch.object(bpy.app.timers, 'register', side_effect=fail):
            self.draw(context_for())
            ui._draw_toolbar_menu(Layout(), context_for())
        self.assertEqual(before, (bpy.context.scene.frame_current, len(store)))
        funcs = bpy.types.VIEW3D_HT_tool_header.draw._draw_funcs
        self.assertEqual(sum(f is ui._draw_viewport_tool_header for f in funcs), 1)
        self.assertGreater(len(funcs), 1)


if __name__ == '__main__':
    result = unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(ToolbarUI))
    if not result.wasSuccessful():
        raise RuntimeError('Ghost toolbar UI checks failed')
