"""Ghost Tool Round D: vertex paths. Run with:
    bforartists --background --factory-startup --python tests/test_ghost_paths_vertex.py
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_ghost_paths import C, GhostPaths, K, _cube, _rig, bpy, ghost_tool, mp  # noqa: E402,F401


class GhostPathVertices(unittest.TestCase):
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

    def test_vertex_index_defaults_to_none_and_labels(self):
        e = self.settings.motion_paths.add()
        e.object_name = "Cube"
        self.assertEqual(e.vertex_index, -1)          # older entries follow the origin or a bone
        self.assertEqual(e.label, "Cube")
        e.vertex_index = 123
        self.assertEqual(e.label, "Cube · v123")
        e.bone_name = "upper"                          # a vertex wins over a stray bone name
        self.assertEqual(e.label, "Cube · v123")
        e.vertex_index = -5
        self.assertEqual(e.vertex_index, -1)          # clamped: -1 is the only "no vertex" value

    def test_path_key_carries_the_vertex(self):
        # Round D part 2: (object, bone, vertex); an origin path and a vertex path of one object differ.
        cube = _cube()
        origin = self.settings.motion_paths.add(); origin.object_name = cube.name
        vertex = self.settings.motion_paths.add(); vertex.object_name, vertex.vertex_index = cube.name, 0
        self.assertEqual((mp.entry_key(origin), mp.entry_key(vertex)), (K(cube.name), K(cube.name, v=0)))
        mp.refresh_paths(bpy.context)
        self.assertIn(C(cube.name, "", 10.0), mp._cache)
        mp.forget((cube.name, ""))   # an (object, bone) pair means vertex -1 (the Head/Tail callback's form)
        self.assertNotIn(C(cube.name, "", 10.0), mp._cache)
        self._drop_deferred_timer()

    def test_vertex_index_survives_save_and_load(self):
        e = self.settings.motion_paths.add()
        e.object_name, e.vertex_index = "Cube", 7
        scene_name = self.scene.name
        with tempfile.TemporaryDirectory() as tmp:
            path = str(Path(tmp) / "vertex.blend")
            bpy.ops.wm.save_as_mainfile(filepath=path)
            bpy.ops.wm.open_mainfile(filepath=path)
            # The saved scene by name, not whichever scene is active after the load (review 45cd3457).
            entry = bpy.data.scenes[scene_name].ghost_tool.motion_paths[0]
            self.assertEqual((entry.object_name, entry.vertex_index), ("Cube", 7))
        self._drop_deferred_timer()


if __name__ == "__main__":
    result = unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(GhostPathVertices))
    print("GHOST_PATH_VERTICES_RESULT: " + ("PASS" if result.wasSuccessful() else "FAIL"), flush=True)
    if not result.wasSuccessful():
        sys.exit(1)
