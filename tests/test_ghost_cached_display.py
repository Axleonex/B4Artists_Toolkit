"""Display-only ghost visibility; run in factory-startup Blender/Bforartists."""
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import MagicMock, patch

import bpy
from mathutils import Matrix

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import ghost_tool
from ghost_tool import ghost_data as gd, ghost_pipeline as gp, mesh_ghosts as mg
from ghost_tool import modal_operator as modal, selection_operators as selection
from ghost_tool import viewport_draw as draw
from ghost_tool.ghost_cache import GhostCache
from ghost_tool.session_state import SessionState


class CachedDisplay(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with patch.object(ghost_tool, '_is_bforartists', return_value=True), \
                patch.object(ghost_tool, '_clear_pycache'):
            ghost_tool.register()

    @classmethod
    def tearDownClass(cls):
        ghost_tool.unregister()

    def setUp(self):
        self.scene = bpy.context.scene
        self.settings = self.scene.ghost_tool
        self.settings['is_active'] = True
        self.settings['show_mesh_ghosts'] = True
        self.settings.show_cached_markers = True
        self.settings.show_cached_skin = True
        self.settings.live_point_ghosts = False
        self.settings.live_mesh_ghosts = False
        self.settings.paths_enabled = False
        self.settings.show_level_1 = False
        self.settings.show_arc_lines = False
        self.settings.show_motion_arc = False
        self.settings.show_ballistic_preview = False
        self.settings.show_archetype_preview = False
        self.settings.show_diff_overlay = False
        self.store = gd.GhostStore.get(self.scene)
        self.store.clear()
        self.marker = gd.Ghost(frame=3, generation_level=2, channel='location.x')
        self.store.add(self.marker)
        SessionState.get(self.scene).hovered_ghost_uid = self.marker.uid
        self.coll = mg._get_or_create_collection(self.scene)
        data = bpy.data.meshes.new('CachedDisplayMesh')
        data.from_pydata([(0, 0, 0), (1, 0, 0), (0, 1, 0)], [], [(0, 1, 2)])
        self.skin = bpy.data.objects.new('CachedDisplaySkin', data)
        self.skin[mg.GHOST_TOOL_MESH_GHOST_KEY] = True
        self.skin[mg.GHOST_TOOL_FRAME_KEY] = 3.0
        self.skin[mg.GHOST_TOOL_BASE_ALPHA_KEY] = 0.2
        self.coll.objects.link(self.skin)

    def tearDown(self):
        mg.clear_mesh_ghosts(bpy.context)
        self.store.clear()

    def test_flags_default_to_visible_and_are_saved_with_scene(self):
        for name in ('show_cached_markers', 'show_cached_skin'):
            prop = gd.GhostToolSceneSettings.bl_rna.properties[name]
            self.assertTrue(prop.default)
            self.assertFalse(prop.is_skip_save)

    def test_checkbox_changes_preserve_cache_identity_and_do_not_queue_sampling(self):
        cache = GhostCache.get(self.scene)
        cache.mark_clean()
        version = self.store.version
        settings_hash = gp.compute_settings_hash(self.settings)
        pointers = self.coll.as_pointer(), self.skin.as_pointer(), self.skin.data.as_pointer()
        with patch.object(gp, '_schedule_deferred_update') as queue, \
                patch.object(gp, '_schedule_forced_mesh_regen') as rebuild, \
                patch.object(mg, 'generate_mesh_ghosts') as generate, \
                patch.object(mg, 'clear_mesh_ghosts') as clear:
            for visible in (False, True, False):
                self.settings.show_cached_markers = visible
                self.settings.show_cached_skin = visible
                self.assertEqual(self.coll.hide_viewport, not visible)
                self.assertIs(self.store.get_by_uid(self.marker.uid), self.marker)
                self.assertEqual(self.store.version, version)
                self.assertFalse(self.settings.show_level_1)
                self.assertFalse(cache.is_dirty)
                self.assertEqual(gp.compute_settings_hash(self.settings), settings_hash)
                self.assertEqual(pointers, (self.coll.as_pointer(), self.skin.as_pointer(),
                                            self.skin.data.as_pointer()))
            for action in (queue, rebuild, generate, clear):
                action.assert_not_called()

    def test_hidden_skin_survives_scrubbing_without_losing_objects(self):
        self.settings.show_cached_skin = False
        pointers = self.coll.as_pointer(), self.skin.as_pointer(), self.skin.data.as_pointer()
        for frame in (2, 8, 1, 4):
            self.scene.frame_set(frame)
            mg._on_frame_change(self.scene, bpy.context.evaluated_depsgraph_get())
            self.assertTrue(self.coll.hide_viewport)
            self.assertEqual(pointers, (self.coll.as_pointer(), self.skin.as_pointer(),
                                        self.skin.data.as_pointer()))
        self.settings.show_cached_skin = True
        self.assertFalse(self.coll.hide_viewport)

    def test_recreated_collections_inherit_hidden_skin_setting(self):
        self.settings.show_cached_skin = False
        mg.clear_mesh_ghosts(bpy.context)
        self.assertTrue(mg._get_or_create_collection(self.scene).hide_viewport)

    def test_toggle_uses_owning_scene_and_detaches_shared_collection(self):
        other = self.scene.copy()
        original = self.coll
        original_pointers = self.skin.as_pointer(), self.skin.data.as_pointer()
        try:
            other.ghost_tool.show_cached_skin = False
            private = mg._get_mesh_collection(other)
            self.assertNotEqual(private, original)
            self.assertTrue(private.hide_viewport)
            self.assertFalse(original.hide_viewport)
            self.assertEqual(original_pointers, (self.skin.as_pointer(), self.skin.data.as_pointer()))
            other.ghost_tool.show_cached_skin = True
            self.assertFalse(private.hide_viewport)
            self.settings.show_cached_skin = False
            self.assertTrue(original.hide_viewport)
            self.assertFalse(private.hide_viewport)
        finally:
            with bpy.context.temp_override(scene=other):
                mg.clear_mesh_ghosts(bpy.context)
            bpy.data.scenes.remove(other)

    def test_hidden_markers_cannot_be_picked_or_box_selected(self):
        context = NS(scene=self.scene)
        with patch.object(modal, '_world_to_screen', return_value=(10, 10)):
            self.assertIs(modal._find_ghost_under_cursor(context, 10, 10, 20), self.marker)
            self.settings.show_cached_markers = False
            self.assertIsNone(modal._find_ghost_under_cursor(context, 10, 10, 20))
        self.assertFalse(selection.GHOST_OT_box_select.poll(context))
        self.assertFalse(modal.GhostDragOperator.poll(context))

    def test_hidden_marker_rendering_keeps_arcs_and_snapshot_overlays(self):
        self.settings.show_cached_markers = False
        self.settings.show_arc_lines = True
        self.marker.is_pinned = True
        context = NS(scene=self.scene, region=NS(as_pointer=lambda: 1),
                     window=NS(as_pointer=lambda: 2),
                     region_data=NS(view_matrix=Matrix.Identity(4)))
        with patch.object(draw, 'gpu', MagicMock()), \
                patch.object(draw, '_get_marker_batches', return_value=[]) as markers, \
                patch.object(draw, 'batch_for_shader') as marker_details, \
                patch.object(draw, '_draw_arc_lines') as arcs, \
                patch.object(draw, '_draw_snapshot_overlays') as snapshots:
            draw._draw_ghosts_3d_impl(context, self.settings, self.scene)
            markers.assert_not_called()
            marker_details.assert_not_called()
            arcs.assert_called_once()
            snapshots.assert_called_once()

    def test_explicit_generation_shows_previously_hidden_markers_and_skin(self):
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.mesh.primitive_cube_add()
        obj = bpy.context.object
        try:
            for frame, value in ((1, 0), (20, 2)):
                obj.location.x = value
                obj.keyframe_insert('location', frame=frame)
            self.scene.frame_set(5)
            self.settings.ghost_mode = 'FRAME_STEP'
            self.settings.ghost_range_mode = 'CUSTOM'
            self.settings.custom_range_start = 2
            self.settings.custom_range_end = 4
            self.settings.frame_step = 1
            self.settings.show_cached_markers = False
            self.settings.show_cached_skin = False
            self.assertEqual(bpy.ops.ghost_tool.generate_ghosts(), {'FINISHED'})
            self.assertGreater(len(self.store), 0)
            self.assertTrue(self.settings.show_cached_markers)
            self.assertFalse(self.settings.show_cached_skin)
            self.assertEqual(bpy.ops.ghost_tool.generate_mesh_ghosts(), {'FINISHED'})
            self.assertTrue(self.settings.show_cached_skin)
            self.assertFalse(mg._get_mesh_collection(self.scene).hide_viewport)
            self.assertFalse(self.settings.live_point_ghosts)
            self.assertFalse(self.settings.live_mesh_ghosts)
        finally:
            bpy.data.objects.remove(obj, do_unlink=True)


if __name__ == '__main__':
    result = unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(CachedDisplay))
    if not result.wasSuccessful():
        raise RuntimeError('Ghost Tool cached-display regression failed')
