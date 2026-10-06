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
from test_ghost_paths import C, GhostPaths, K, _cube, _rig, bpy, gd, ghost_tool, mp  # noqa: E402,F401


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
        self.assertIn(C(cube.name, "", 10.0, v=0), mp._cache)   # review 2be23ce9: the vertex path's own key
        mp.forget((cube.name, ""))   # an (object, bone) pair means vertex -1 (the Head/Tail callback's form)
        self.assertNotIn(C(cube.name, "", 10.0), mp._cache)
        self.assertIn(C(cube.name, "", 10.0, v=0), mp._cache)   # forgetting the origin keeps the vertex
        self._drop_deferred_timer()

    def _vertex_path(self, obj, index):
        e = self.settings.motion_paths.add()
        e.object_name, e.vertex_index = obj.name, index
        return e

    def _evaluated_vertex(self, obj, index):
        ev = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
        return ev.matrix_world @ ev.data.vertices[index].co

    def test_vertex_path_samples_evaluated_vertex(self):
        cube = _cube()
        self._vertex_path(cube, 0)
        mp.refresh_paths(bpy.context)
        self.scene.frame_set(13)
        sample = mp._cache[C(cube.name, "", 13.0, v=0)]
        self.assertLess((sample - self._evaluated_vertex(cube, 0)).length, 1e-5)
        self.assertGreater((sample - cube.matrix_world.translation).length, 0.5)   # a corner, not the origin
        self.scene.frame_set(10)
        self._drop_deferred_timer()

    def test_vertex_path_follows_armature_deform(self):
        rig = _rig()
        bpy.ops.mesh.primitive_cube_add(size=0.2, location=(0, 0, 2))
        mesh = bpy.context.object
        group = mesh.vertex_groups.new(name="upper")
        group.add(range(len(mesh.data.vertices)), 1.0, 'REPLACE')
        mesh.modifiers.new("Arm", 'ARMATURE').object = rig
        self._vertex_path(mesh, 0)
        mp.refresh_paths(bpy.context)
        self.scene.frame_set(13)
        sample = mp._cache[C(mesh.name, "", 13.0, v=0)]
        self.assertLess((sample - self._evaluated_vertex(mesh, 0)).length, 1e-5)
        # The rig turns about 0.1 rad between frames 7 and 13 (measured 0.098 units): any motion proves the deform.
        self.assertGreater((sample - mp._cache[C(mesh.name, "", 7.0, v=0)]).length, 0.01)
        mp._dirty.clear()
        mp.mark_dirty_for_id(rig)   # a deformer edit re-samples the vertex path
        self.assertIn(K(mesh.name, v=0), mp._dirty)
        self.scene.frame_set(10)
        self._drop_deferred_timer()

    def test_vertex_path_missing_when_topology_changes(self):
        cube = _cube()
        e = self._vertex_path(cube, 0)
        self.assertFalse(mp.entry_is_missing(e))
        sub = cube.modifiers.new("Sub", 'SUBSURF')
        self.assertTrue(mp.entry_is_missing(e))
        self.assertEqual(mp.pinned_targets(self.scene), [])
        cube.modifiers.remove(sub)
        self.assertFalse(mp.entry_is_missing(e))
        e.vertex_index = 999
        self.assertTrue(mp.entry_is_missing(e))

    def test_vertex_absent_at_a_frame_leaves_a_gap(self):
        # Review b1d2370a: topology that changes over time must not put the object origin into the path.
        cube = _cube()
        sub = cube.modifiers.new("Sub", 'SUBSURF')
        for frame, on in ((1, False), (12, True), (13, False)):   # the vertex is renumbered at frame 12 only
            sub.show_viewport = on
            sub.keyframe_insert("show_viewport", frame=frame)
        self.scene.frame_set(10)   # topology matches here, so the path is not missing
        self._vertex_path(cube, 0)
        self.assertEqual(len(mp.pinned_targets(self.scene)), 1)
        self.assertEqual(mp.refresh_paths(bpy.context), 7)
        self.assertNotIn(C(cube.name, "", 12.0, v=0), mp._cache)
        self.assertEqual({g for g in mp._gaps if g[:3] == K(cube.name, v=0)}, {C(cube.name, "", 12.0, v=0)})
        self.assertIn(C(cube.name, "", 11.0, v=0), mp._cache)
        self.assertIn(C(cube.name, "", 13.0, v=0), mp._cache)
        self.assertEqual(mp.refresh_paths(bpy.context), 0)      # gaps are not re-sampled every refresh
        self.assertFalse(mp.request_missing_samples(bpy.context))
        # Review 23449ef1: the drawn line stops at the gap.
        target = mp.pinned_targets(self.scene)[0]
        segs = mp.path_segments(bpy.context, target)
        self.assertEqual(len(segs), 4)   # 7-8, 8-9, 9-10, 10-11; nothing joins 11 to 13 across the gap
        self.assertEqual(segs[-1][1], mp._cache[C(cube.name, "", 11.0, v=0)])
        mp.forget(K(cube.name, v=0))
        self.assertFalse(any(g[:3] == K(cube.name, v=0) for g in mp._gaps))
        self._drop_deferred_timer()

    def test_path_of_only_gaps_recovers_after_a_mesh_update(self):
        # Review 23449ef1: _cache_keys read only _cache, so a path whose every sampled frame was a gap
        # could never be dirtied again. (A refresh always samples the current frame, where the path
        # resolved, so the all-gap state is set up directly.)
        cube = _cube()
        self._vertex_path(cube, 0)
        mp.clear_cache()
        mp._gaps.update(C(cube.name, "", float(f), v=0) for f in range(7, 14))
        self.assertIn(K(cube.name, v=0), mp._cache_keys())
        mp._dirty.clear()
        mp.mark_dirty_for_id(cube.data)
        self.assertIn(K(cube.name, v=0), mp._dirty)
        self.assertEqual(mp.refresh_paths(bpy.context), 7)   # the dirty path is sampled again, gaps dropped
        self.assertIn(C(cube.name, "", 10.0, v=0), mp._cache)
        self.assertFalse(any(g[:3] == K(cube.name, v=0) for g in mp._gaps))
        self._drop_deferred_timer()

    def test_add_selected_pins_a_vertex_added_in_edit_mode(self):
        # Review b1d2370a: a new BMesh vertex has index -1 until renumbered.
        import bmesh
        bpy.ops.mesh.primitive_plane_add()
        plane = bpy.context.object
        bpy.ops.object.mode_set(mode='EDIT')
        bm = bmesh.from_edit_mesh(plane.data)
        for v in bm.verts:
            v.select = False
        new = bm.verts.new((3.0, 3.0, 0.0))
        new.select = True
        bmesh.update_edit_mesh(plane.data)
        bpy.ops.ghost_tool.paths_add_selected()
        self.assertEqual([e.vertex_index for e in self.settings.motion_paths], [4])   # the plane's 4 + the new one
        bpy.ops.object.mode_set(mode='OBJECT')
        self.assertFalse(mp.entry_is_missing(self.settings.motion_paths[0]))
        self._drop_deferred_timer()

    def test_add_selected_in_edit_mode_adds_vertices(self):
        import bmesh
        bpy.ops.mesh.primitive_grid_add(x_subdivisions=10, y_subdivisions=10)
        grid = bpy.context.object
        bpy.ops.object.mode_set(mode='EDIT')
        bm = bmesh.from_edit_mesh(grid.data)
        bm.verts.ensure_lookup_table()
        self.assertGreaterEqual(len(bm.verts), 63)

        def select(indexes):
            for v in bm.verts:
                v.select = v.index in indexes
            bmesh.update_edit_mesh(grid.data)

        select({0, 1, 2})
        self.assertEqual(bpy.ops.ghost_tool.paths_add_selected(), {'FINISHED'})
        self.assertEqual(sorted(e.vertex_index for e in self.settings.motion_paths), [0, 1, 2])
        self.assertTrue(all(e.object_name == grid.name and e.bone_name == "" for e in self.settings.motion_paths))
        select(set(range(3, 63)))
        bpy.ops.ghost_tool.paths_add_selected()
        self.assertEqual(len(self.settings.motion_paths), 3 + 50)   # at most 50 per click
        self.assertEqual(mp.follow_targets(bpy.context, set()), [])   # Follow ignores an Edit Mode selection
        bpy.ops.object.mode_set(mode='OBJECT')
        self._drop_deferred_timer()

    def test_vertex_paths_get_no_markers(self):
        cube = _cube()
        self._vertex_path(cube, 0)
        mp.refresh_paths(bpy.context)
        self.settings.paths_show_markers = True
        mp.sync_markers(bpy.context)
        # Review b1d2370a: the store itself, not owned_markers (which filters by ownership and hides leaks).
        self.assertEqual(list(gd.GhostStore.get(self.scene)), [])
        self.settings.paths_show_markers = False
        self._drop_deferred_timer()

    def test_vertex_key_frames_and_shape_key_edits(self):
        cube = _cube()
        self._vertex_path(cube, 0)
        target = mp.pinned_targets(self.scene)[0]
        self.assertEqual(mp.key_frames(target), [1.0, 20.0])   # the object's location keys
        cube.shape_key_add(name="Basis")
        bulge = cube.shape_key_add(name="Bulge")
        for frame, value in ((5, 0.0), (15, 1.0)):
            bulge.value = value
            bulge.keyframe_insert("value", frame=frame)
        self.assertEqual(mp.key_frames(mp.pinned_targets(self.scene)[0]), [1.0, 5.0, 15.0, 20.0])
        mp.refresh_paths(bpy.context)
        mp._dirty.clear()
        mp.mark_dirty_for_id(cube.data.shape_keys.animation_data.action)
        self.assertIn(K(cube.name, v=0), mp._dirty)
        mp._dirty.clear()
        mp.mark_dirty_for_id(cube.data)   # a mesh edit moves the vertex too
        self.assertIn(K(cube.name, v=0), mp._dirty)
        self._drop_deferred_timer()

    def test_vertex_row_icon(self):
        from ghost_tool.ui_panel import _row_icon
        e = self._vertex_path(_cube(), 4)
        self.assertEqual(_row_icon(e, False), 'VERTEXSEL')
        self.assertEqual(_row_icon(e, True), 'RADIOBUT_ON')

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
