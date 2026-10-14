"""Exercise production lifecycle functions with native-access fault guards.

Ordinary Python; the fixture raises if registration accesses a viewport before
the main loop is ready. This does not emulate or claim to reproduce a C crash.
"""
import ast
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
NS = types.SimpleNamespace


def functions(path, module, names):
    tree = ast.parse(path.read_bytes(), filename=str(path))
    nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names]
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), 'exec'), module.__dict__)


class Timers:
    def __init__(self):
        self.pending = {}

    def register(self, callback, **options):
        assert callback not in self.pending, 'Duplicate timer'
        self.pending[callback] = options

    def is_registered(self, callback):
        return callback in self.pending

    def unregister(self, callback):
        del self.pending[callback]

    def run(self, callback):
        self.pending.pop(callback)
        result = callback()
        if result is not None:
            self.pending[callback] = {}
        return result


class StartupRegistration(unittest.TestCase):
    def setUp(self):
        self.ready = False
        self.reads = 0
        self.redraws = []
        self.space = NS(show_region_tool_header=False, show_region_ui=False,
                        show_region_toolbar=False, show_toolshelf_tabs=False)
        owner = self

        class Area:
            type = 'VIEW_3D'
            regions = []

            @property
            def spaces(self):
                owner.reads += 1
                assert owner.ready, 'Native viewport accessed before main-loop readiness'
                return NS(active=owner.space)

            def as_pointer(self):
                return 2

            def tag_redraw(self):
                owner.redraws.append(True)

        self.area = Area()
        self.window = NS(as_pointer=lambda: 1, screen=NS(areas=[self.area]))
        self.values = NS(display_location='TOOLS', show_toolbar=True)
        self.context = NS(window_manager=NS(windows=[self.window]),
                          preferences=NS(addons={'ghost_tool': NS(preferences=self.values)}))
        self.timers = Timers()
        self.bpy = NS(context=self.context, app=NS(background=False, timers=self.timers),
                      utils=NS(register_class=lambda cls: None, unregister_class=lambda cls: None))
        self.ui = types.ModuleType('ghost_tool.ui_panel')
        self.ui.__package__ = 'ghost_tool'
        self.ui.bpy = self.bpy
        self.ui._pending_display_tabs = {}
        self.ui._pending_display_update = None
        self.ui._ghost_windows = set()
        self.ui.display_location = lambda c: c.preferences.addons['ghost_tool'].preferences.display_location
        self.ui.toolbar_visible = lambda c: c.preferences.addons['ghost_tool'].preferences.show_toolbar
        self.ui._header_appends = []
        self.ui._shelf_registered = []
        self.ui.CLASSES = ()
        self.ui.log = lambda *args: None
        self.bpy.types = NS(Scene=NS())
        functions(ROOT / 'ghost_tool/ui_panel.py', self.ui, {
            '_ordinary_viewports', '_select_display_tabs', 'update_display_location',
            'update_toolbar_visibility', 'schedule_display_location_update',
            '_apply_display_location_update', 'cancel_display_location_update', 'unregister'})
        self.pref = types.ModuleType('ghost_tool.preferences')
        self.pref.__package__ = 'ghost_tool'
        self.pref.bpy = self.bpy
        self.pref.CLASSES = ()
        self.pref.register_keymaps = lambda: None
        functions(ROOT / 'ghost_tool/preferences.py', self.pref, {
            '_update_display_location', '_update_toolbar_visibility',
            'migrate_display_location', 'register'})
        settings = types.ModuleType('ghost_tool.settings_editor')
        settings.is_editor = lambda context: False
        shelf = types.ModuleType('ghost_tool.shelf_width')
        shelf.forget_all = lambda: None
        package = types.ModuleType('ghost_tool')
        package.__path__ = []
        self.modules = patch.dict(sys.modules, {'ghost_tool': package,
            'ghost_tool.ui_panel': self.ui, 'ghost_tool.settings_editor': settings,
            'ghost_tool.shelf_width': shelf})
        self.modules.start()
        self.addCleanup(self.modules.stop)

    def run_update(self):
        self.ready = True
        self.assertIsNone(self.timers.run(self.ui._apply_display_location_update))

    def test_registration_never_reads_uninitialized_viewport(self):
        self.pref.register()
        self.assertEqual(self.reads, 0)
        self.assertEqual(len(self.timers.pending), 1)
        self.assertTrue(self.timers.pending[self.ui._apply_display_location_update]['persistent'])
        self.run_update()
        self.assertTrue(self.space.show_region_toolbar)
        self.assertTrue(self.space.show_toolshelf_tabs)

    def test_saved_locations_are_applied_after_readiness(self):
        for home, flag in [('TOOLBAR', 'show_region_tool_header'),
                           ('SIDEBAR', 'show_region_ui'), ('TOOLS', 'show_region_toolbar')]:
            self.values.display_location = home
            self.pref.register()
            self.run_update()
            self.assertTrue(getattr(self.space, flag))

    def test_legacy_migration_callbacks_do_not_read_viewports(self):
        pref_module = self.pref
        context = self.context

        class Legacy:
            _home = 'HEADER'
            _visible = False

            @property
            def display_location(self):
                return self._home

            @display_location.setter
            def display_location(self, value):
                self._home = value
                pref_module._update_display_location(self, context)

            @property
            def show_toolbar(self):
                return self._visible

            @show_toolbar.setter
            def show_toolbar(self, value):
                self._visible = value
                pref_module._update_toolbar_visibility(self, context)

        self.context.preferences.addons['ghost_tool'].preferences = Legacy()
        self.pref.register()
        self.assertEqual(self.reads, 0)
        self.assertEqual(len(self.timers.pending), 1)
        self.run_update()
        self.assertTrue(self.space.show_region_tool_header)

    def test_hidden_toolbar_is_preserved(self):
        self.values.display_location = 'TOOLBAR'
        self.values.show_toolbar = False
        self.pref.register()
        self.run_update()
        self.assertFalse(self.space.show_region_tool_header)

    def test_visibility_callback_only_redraws_other_home(self):
        self.values.display_location = 'SIDEBAR'
        self.pref._update_toolbar_visibility(self.values, self.context)
        self.assertEqual(self.reads, 0)
        self.run_update()
        self.assertFalse(self.space.show_region_ui)
        self.assertTrue(self.redraws)

    def test_background_registration_does_not_schedule_ui(self):
        self.bpy.app.background = True
        self.pref.register()
        self.pref._update_display_location(self.values, self.context)
        self.pref._update_toolbar_visibility(self.values, self.context)
        self.assertEqual(self.reads, 0)
        self.assertEqual(self.timers.pending, {})

    def test_requests_coalesce_and_use_latest_context(self):
        self.pref.register()
        self.pref._update_toolbar_visibility(self.values, self.context)
        self.assertEqual(len(self.timers.pending), 1)
        self.values.display_location = 'TOOLBAR'
        self.run_update()
        self.assertTrue(self.space.show_region_tool_header)
        self.assertFalse(self.space.show_region_toolbar)

    def test_screenless_window_is_skipped(self):
        self.pref.register()
        self.window.screen = None
        self.run_update()
        self.assertEqual(self.reads, 0)

    def test_unregister_cancels_pending_ui_access(self):
        self.pref.register()
        self.ui.unregister()
        self.assertEqual(self.timers.pending, {})
        self.assertEqual(self.reads, 0)


if __name__ == '__main__':
    result = unittest.main(argv=[sys.argv[0]], exit=False).result
    if not result.wasSuccessful():
        raise RuntimeError('Ghost startup lifecycle tests failed')
