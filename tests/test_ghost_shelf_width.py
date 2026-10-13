"""Guarded width writes and once-only policy; run with ordinary Python."""
import ctypes
import importlib.util
from pathlib import Path
import struct
import sys
import types
import unittest
from types import SimpleNamespace as NS
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('ghost_tool.shelf_width', ROOT / 'ghost_tool/shelf_width.py')
sw = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sw)


def raw_region(width=132, height=751, rtype=5, stored=132, at=184, gap=8, size=448):
    raw = bytearray(size)
    struct.pack_into('<hh', raw, at, width, height)
    struct.pack_into('<h', raw, at + gap, rtype)
    struct.pack_into('<h', raw, at + gap + 6, stored)
    return raw


class Locator(unittest.TestCase):
    def test_native_and_shifted_offsets(self):
        self.assertEqual(sw.locate(raw_region(), 132, 751, 5), 198)
        self.assertEqual(sw.locate(raw_region(at=200, gap=12), 132, 751, 5), 218)

    def test_mismatched_dimensions_type_and_stored_width(self):
        for changes in ({'height': 700}, {'rtype': 4}, {'stored': 999}):
            self.assertIsNone(sw.locate(raw_region(**changes), 132, 751, 5))

    def test_ambiguous_candidates_are_rejected(self):
        raw = raw_region()
        struct.pack_into('<hh', raw, 300, 132, 751)
        struct.pack_into('<h', raw, 308, 5)
        struct.pack_into('<h', raw, 314, 132)
        self.assertIsNone(sw.locate(raw, 132, 751, 5))

    def test_multiple_candidates_after_one_dimension_pair_are_rejected(self):
        raw = raw_region()
        struct.pack_into('<h', raw, 204, 5)
        struct.pack_into('<h', raw, 210, 132)
        self.assertIsNone(sw.locate(raw, 132, 751, 5))

    def test_scaling_and_invalid_inputs(self):
        self.assertEqual(sw.locate(raw_region(width=264, height=1502), 264, 1502, 5, 2), 198)
        for scale in (0, -1, float('nan'), float('inf')):
            self.assertIsNone(sw.locate(raw_region(), 132, 751, 5, scale))
        self.assertIsNone(sw.locate(b'\0' * 4, 132, 751, 5))
        self.assertIsNone(sw.locate(raw_region(), 0, 751, 5))

    def test_matching_fallback_and_wider_targets(self):
        self.assertEqual(sw.target(132, 220, 1), 220)
        self.assertEqual(sw.target(132, 360, 1), 360)
        self.assertEqual(sw.target(132, 0, 1), 240)
        self.assertIsNone(sw.target(300, 220, 1))
        self.assertIsNone(sw.target(220, 220, 1))
        self.assertEqual(sw.target(264, 440, 2), 220)
        self.assertEqual(sw.target(264, 0, 2), 240)
        self.assertIsNone(sw.target(132, 220, 0))

    def test_write_changes_only_the_verified_short_and_relayouts(self):
        buffer = (ctypes.c_char * 448).from_buffer_copy(raw_region())
        before = bytes(buffer)
        region = NS(type='TOOLS', width=132, height=751, as_pointer=lambda: ctypes.addressof(buffer))
        area = NS(spaces=NS(active=NS(show_region_toolbar=True)), tag_redraw=lambda: None)
        self.assertTrue(sw.set_width(area, region, 220, scale=1))
        after = bytes(buffer)
        self.assertEqual(struct.unpack_from('<h', after, 198)[0], 220)
        self.assertEqual(before[:198] + before[200:], after[:198] + after[200:])
        self.assertTrue(area.spaces.active.show_region_toolbar)

    def test_failed_lookup_and_invalid_target_do_not_write(self):
        buffer = (ctypes.c_char * 448).from_buffer_copy(raw_region(stored=999))
        before = bytes(buffer)
        region = NS(type='TOOLS', width=132, height=751, as_pointer=lambda: ctypes.addressof(buffer))
        area = NS(spaces=NS(active=NS(show_region_toolbar=True)), tag_redraw=lambda: None)
        self.assertFalse(sw.set_width(area, region, 220, scale=1))
        self.assertFalse(sw.set_width(area, region, 40000, scale=1))
        self.assertEqual(bytes(buffer), before)


class WideningPolicy(unittest.TestCase):
    def setUp(self):
        sw.forget_all()
        self.prefs = NS(display_location='TOOLS', auto_widen_shelf=True)
        self.context = NS(preferences=NS(system=NS(ui_scale=1), addons={
            'ghost_tool': NS(preferences=self.prefs)}))
        self.space = NS(show_region_toolbar=True, show_region_ui=True)
        self.tools = NS(type='TOOLS', width=132, height=751, as_pointer=lambda: 3)
        self.sidebar = NS(type='UI', width=220)
        self.area = NS(spaces=NS(active=self.space), regions=[self.tools, self.sidebar], as_pointer=lambda: 2)
        self.window = NS(as_pointer=lambda: 1)
        package = types.ModuleType('ghost_tool')
        package.__path__ = []
        ui = types.ModuleType('ghost_tool.ui_panel')
        ui.supports_tool_shelf = lambda: True
        ui.display_location = lambda c: self.prefs.display_location
        ui._ordinary_viewports = lambda c: iter([(self.window, self.area)])
        self.bpy = NS(context=self.context)
        self.modules = patch.dict(sys.modules, {'bpy': self.bpy, 'ghost_tool': package, 'ghost_tool.ui_panel': ui})
        self.modules.start()
        self.addCleanup(self.modules.stop)

    def test_open_sidebar_matches_once_and_later_manual_width_is_preserved(self):
        with patch.object(sw, 'set_width', return_value=True) as write:
            sw.widen_all()
            self.assertEqual(write.call_args.args[2], 220)
            self.tools.width = 150
            sw.widen_all()
            self.assertEqual(write.call_count, 1)

    def test_closed_sidebar_uses_scaled_bonecraft_fallback(self):
        self.space.show_region_ui = False
        self.context.preferences.system.ui_scale = 2
        self.tools.width = 264
        with patch.object(sw, 'set_width', return_value=True) as write:
            sw.widen_all()
            self.assertEqual(write.call_args.args[2], 240)

    def test_wider_shelf_is_never_shrunk(self):
        self.tools.width = 300
        with patch.object(sw, 'set_width') as write:
            sw.widen_all()
            self.tools.width = 150
            sw.widen_all()
            write.assert_not_called()

    def test_hidden_unlaid_out_and_other_homes_are_ignored(self):
        for location in ('TOOLBAR', 'SIDEBAR'):
            self.prefs.display_location = location
            with patch.object(sw, 'set_width') as write:
                sw.widen_all()
                write.assert_not_called()
        self.prefs.display_location = 'TOOLS'
        for flag, width in ((False, 132), (True, 0)):
            self.space.show_region_toolbar, self.tools.width = flag, width
            with patch.object(sw, 'set_width') as write:
                sw.widen_all()
                write.assert_not_called()
        self.assertFalse(sw._done)

    def test_disabled_preference_and_unsupported_host_are_ignored(self):
        self.prefs.auto_widen_shelf = False
        with patch.object(sw, 'set_width') as write:
            sw.widen_all()
            write.assert_not_called()
        self.prefs.auto_widen_shelf = True
        with patch('ghost_tool.ui_panel.supports_tool_shelf', return_value=False), patch.object(sw, 'set_width') as write:
            sw.widen_all()
            write.assert_not_called()

    def test_explicit_reset_and_new_region_are_checked_again(self):
        with patch.object(sw, 'set_width', return_value=True) as write:
            sw.widen_all()
            sw.forget_all()
            sw.widen_all()
            self.tools.as_pointer = lambda: 4
            sw.widen_all()
            self.assertEqual(write.call_count, 3)

    def test_failed_write_is_not_marked_complete(self):
        with patch.object(sw, 'set_width', side_effect=[False, True]) as write:
            sw.widen_all()
            self.assertFalse(sw._done)
            sw.widen_all()
            self.assertEqual(write.call_count, 2)


if __name__ == '__main__':
    result = unittest.main(argv=[sys.argv[0]], verbosity=2, exit=False).result
    if not result.wasSuccessful():
        raise RuntimeError('Shelf width guards failed')
