"""Ghost Tool Round F: Bezier handles on motion paths. Run with:
    bforartists --background --factory-startup --python tests/test_ghost_paths_handles.py
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_ghost_paths import C, GhostPaths, K, _cube, _rig, bpy, ghost_tool, mp  # noqa: E402,F401
from test_ghost_paths_folders import _Layout  # noqa: E402


class GhostPathHandles(unittest.TestCase):
    """Uses GhostPaths' scene setup without re-running its tests."""

    setUp = GhostPaths.setUp
    select_bones = GhostPaths.select_bones
    _drop_deferred_timer = GhostPaths._drop_deferred_timer

    @classmethod
    def setUpClass(cls):
        with patch.object(ghost_tool, "_clear_pycache"):
            ghost_tool.register()

    @classmethod
    def tearDownClass(cls):
        ghost_tool.unregister()

    def test_show_handles_setting_and_toggle(self):
        from ghost_tool import ui_panel
        self.assertFalse(self.settings.paths_show_handles)   # off: existing files look as before
        layout = _Layout()
        ui_panel._draw_motion_paths(layout, bpy.context)
        self.assertIn(("prop", "paths_show_handles", "Handles"), [c[:3] for c in layout.calls])
        with patch.object(ghost_tool.ghost_data, "_schedule_path_refresh") as refresh:
            self.settings.paths_show_handles = True
        refresh.assert_called_once()   # turning it on samples the handle points
        self.settings.paths_show_handles = False
        self._drop_deferred_timer()


if __name__ == "__main__":
    result = unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(GhostPathHandles))
    print("GHOST_PATH_HANDLES_RESULT: " + ("PASS" if result.wasSuccessful() else "FAIL"), flush=True)
    if not result.wasSuccessful():
        sys.exit(1)
