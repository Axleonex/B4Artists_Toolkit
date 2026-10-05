"""Ghost Tool 3.5: motion paths. Run with:
    bforartists --background --factory-startup --python tests/test_ghost_paths.py
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import ghost_tool  # noqa: E402
from ghost_tool import ghost_data as gd  # noqa: E402
from ghost_tool import motion_paths as mp  # noqa: E402
from ghost_tool.utils import get_scene_id  # noqa: E402


def _clear_scene():
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj)
    for action in list(bpy.data.actions):
        bpy.data.actions.remove(action)


def _rig(name="Rig", location_keys=True):
    data = bpy.data.armatures.new(name)
    rig = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(rig)
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.mode_set(mode='EDIT')
    upper = data.edit_bones.new("upper")
    upper.head, upper.tail = (0, 0, 0), (0, 0, 1)
    lower = data.edit_bones.new("lower")
    lower.head, lower.tail = (0, 0, 1), (0, 0, 2)
    lower.parent = upper
    bpy.ops.object.mode_set(mode='POSE')
    for pb in rig.pose.bones:
        # Pose bones default to QUATERNION; Euler keys would be ignored and the rig would never move.
        pb.rotation_mode = 'XYZ'
    for frame, angle in ((1, 0.0), (10, 0.8), (20, -0.4)):
        for pb in rig.pose.bones:
            pb.rotation_euler = (angle, 0, 0)
            pb.keyframe_insert("rotation_euler", frame=frame)
            if location_keys:
                # Zero offsets: positions are unchanged, but HEAD paths now carry location markers.
                pb.keyframe_insert("location", frame=frame)
    bpy.ops.object.mode_set(mode='OBJECT')
    return rig


def _cube(name="Cube"):
    bpy.ops.mesh.primitive_cube_add()
    cube = bpy.context.object
    cube.name = name
    for frame, x in ((1, 0.0), (20, 4.0)):
        cube.location.x = x
        cube.keyframe_insert("location", frame=frame)
    return cube


class GhostPaths(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with patch.object(ghost_tool, "_clear_pycache"):
            ghost_tool.register()

    @classmethod
    def tearDownClass(cls):
        ghost_tool.unregister()

    def setUp(self):
        _clear_scene()
        self.scene = bpy.context.scene
        self.scene.frame_start, self.scene.frame_end = 1, 20
        self.settings = self.scene.ghost_tool
        self.settings.is_active = True
        self.settings.live_point_ghosts = False
        self.settings.live_mesh_ghosts = False
        self.settings.motion_paths.clear()
        self.settings.paths_enabled = True
        self.settings.paths_follow_selection = False
        self.settings.paths_range_mode = 'AROUND_CURSOR'
        self.settings.paths_before = 3
        self.settings.paths_after = 3
        self.settings.paths_step = 1
        self.settings.paths_show_markers = False
        mp.clear_cache()
        gd.GhostStore.get(self.scene).clear()
        self.scene.frame_set(10)

    def select_bones(self, rig, *names):
        bpy.context.view_layer.objects.active = rig
        for obj in bpy.data.objects:
            obj.select_set(obj is rig)
        bpy.ops.object.mode_set(mode='POSE')
        for pb in rig.pose.bones:
            pb.select = pb.name in names  # Blender 5.x: selection lives on the pose bone
        rig.data.bones.active = rig.data.bones[names[0]]

    def test_harness_registers(self):
        self.assertTrue(hasattr(self.settings, "motion_paths"))

    def test_module_registered(self):
        self.assertIn("motion_paths", ghost_tool._REGISTER_ORDER)

    def test_desired_frames_around_cursor(self):
        self.assertEqual(mp.desired_frames(self.settings, self.scene), [7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0])
        self.settings.paths_step = 2
        self.assertEqual(mp.desired_frames(self.settings, self.scene), [7.0, 9.0, 11.0, 13.0])
        self.settings.paths_range_mode = 'SCENE'
        self.settings.paths_step = 5
        self.assertEqual(mp.desired_frames(self.settings, self.scene), [1.0, 6.0, 11.0, 16.0])

    def test_pinned_targets_resolve_and_skip_missing(self):
        rig = _rig()
        e = self.settings.motion_paths.add(); e.object_name, e.bone_name = rig.name, "lower"
        m = self.settings.motion_paths.add(); m.object_name, m.bone_name = rig.name, "nope"
        targets = mp.pinned_targets(self.scene)
        self.assertEqual([(t.key, t.obj) for t in targets], [((rig.name, "lower"), rig)])
        self.assertTrue(mp.entry_is_missing(m))
        self.assertFalse(mp.entry_is_missing(e))

    def test_follow_selection_targets(self):
        rig = _rig()
        cube = _cube()
        self.settings.paths_follow_selection = True
        self.select_bones(rig, "upper", "lower")
        keys = {t.key for t in mp.follow_targets(bpy.context, pinned_keys=set())}
        self.assertEqual(keys, {(rig.name, "upper"), (rig.name, "lower")})
        self.assertTrue(all(t.color == mp.FOLLOW_COLOR and not t.pinned for t in mp.follow_targets(bpy.context, pinned_keys=set())))
        # a pinned bone is not duplicated
        self.assertEqual({t.key for t in mp.follow_targets(bpy.context, pinned_keys={(rig.name, "upper")})}, {(rig.name, "lower")})
        bpy.ops.object.mode_set(mode='OBJECT')
        for obj in bpy.data.objects:
            obj.select_set(obj is cube)
        bpy.context.view_layer.objects.active = cube
        self.assertEqual({t.key for t in mp.follow_targets(bpy.context, pinned_keys=set())}, {(cube.name, "")})
        self.settings.paths_follow_selection = False
        self.assertEqual(mp.follow_targets(bpy.context, pinned_keys=set()), [])

    def test_refresh_samples_bone_head_and_restores_playhead(self):
        rig = _rig()
        e = self.settings.motion_paths.add(); e.object_name, e.bone_name = rig.name, "lower"
        self.scene.frame_set(10)
        n = mp.refresh_paths(bpy.context)
        self.assertEqual(n, 7)
        self.assertEqual(self.scene.frame_current, 10)
        self.scene.frame_set(8)
        dg = bpy.context.evaluated_depsgraph_get()
        expect = rig.evaluated_get(dg).matrix_world @ rig.evaluated_get(dg).pose.bones["lower"].head
        self.assertLess((mp._cache[(rig.name, "lower", 8.0)] - expect).length, 1e-5)
        self.scene.frame_set(10)

    def test_refresh_is_incremental(self):
        rig = _rig()
        e = self.settings.motion_paths.add(); e.object_name, e.bone_name = rig.name, "upper"
        self.assertEqual(mp.refresh_paths(bpy.context), 7)
        self.assertEqual(mp.refresh_paths(bpy.context), 0)
        self.scene.frame_set(11)
        self.assertEqual(mp.refresh_paths(bpy.context), 1)   # only frame 14 is new
        self.assertNotIn((rig.name, "upper", 7.0), mp._cache)  # frame 7 left the window

    def test_object_path_uses_origin(self):
        cube = _cube()
        e = self.settings.motion_paths.add(); e.object_name = cube.name
        mp.refresh_paths(bpy.context)
        self.scene.frame_set(13)
        self.assertLess((mp._cache[(cube.name, "", 13.0)] - cube.matrix_world.translation).length, 1e-5)
        self.scene.frame_set(10)

    def test_key_edit_dirties_only_that_object(self):
        rig = _rig(); cube = _cube()
        a = self.settings.motion_paths.add(); a.object_name, a.bone_name = rig.name, "upper"
        b = self.settings.motion_paths.add(); b.object_name = cube.name
        mp.refresh_paths(bpy.context)
        mp.mark_dirty_for_id(cube.animation_data.action)
        self.assertEqual(mp.refresh_paths(bpy.context), 7)          # cube only
        mp.mark_dirty_for_id(rig)
        self.assertEqual(mp.refresh_paths(bpy.context), 7)          # rig only

    def test_add_selected_pins_without_duplicates(self):
        rig = _rig()
        self.select_bones(rig, "upper", "lower")
        self.assertEqual(bpy.ops.ghost_tool.paths_add_selected(), {'FINISHED'})
        self.assertEqual([(e.object_name, e.bone_name) for e in self.settings.motion_paths],
                         [(rig.name, "upper"), (rig.name, "lower")])
        bpy.ops.ghost_tool.paths_add_selected()
        self.assertEqual(len(self.settings.motion_paths), 2)
        self.assertNotEqual(tuple(self.settings.motion_paths[0].color), tuple(self.settings.motion_paths[1].color))
        bpy.ops.object.mode_set(mode='OBJECT')
        for obj in bpy.data.objects:
            obj.select_set(False)
        bpy.context.view_layer.objects.active = None
        self.assertFalse(bpy.ops.ghost_tool.paths_add_selected.poll())

    def test_toggle_remove_clear(self):
        rig = _rig()
        self.select_bones(rig, "upper", "lower")
        bpy.ops.ghost_tool.paths_add_selected()
        bpy.ops.ghost_tool.paths_toggle_visible(action='ALL_OFF')
        self.assertFalse(any(e.visible for e in self.settings.motion_paths))
        bpy.ops.ghost_tool.paths_toggle_visible(action='ONE', index=1)
        self.assertEqual([e.visible for e in self.settings.motion_paths], [False, True])
        bpy.ops.ghost_tool.paths_toggle_visible(action='ALL_ON')
        self.assertTrue(all(e.visible for e in self.settings.motion_paths))
        bpy.ops.ghost_tool.paths_remove(index=0)
        self.assertEqual([e.bone_name for e in self.settings.motion_paths], ["lower"])
        mp.refresh_paths(bpy.context)
        bpy.ops.ghost_tool.paths_clear()
        self.assertEqual(len(self.settings.motion_paths), 0)
        self.assertEqual(len(mp._cache), 0)

    def test_path_segments_builder(self):
        rig = _rig()
        e = self.settings.motion_paths.add(); e.object_name, e.bone_name = rig.name, "lower"
        mp.refresh_paths(bpy.context)
        segs = mp.path_segments(bpy.context, mp.pinned_targets(self.scene)[0], mp.desired_frames(self.settings, self.scene))
        self.assertEqual(len(segs), 6)                       # 7 frames -> 6 segments
        self.assertTrue(all(len(c) == 4 for _p0, _p1, c in segs))
        self.settings.paths_style = 'FADE'
        far = mp.path_segments(bpy.context, mp.pinned_targets(self.scene)[0], mp.desired_frames(self.settings, self.scene))
        self.assertLess(far[0][2][3], far[2][2][3])          # farther from playhead = more transparent

    def test_key_frames_for_target(self):
        rig = _rig()
        e = self.settings.motion_paths.add(); e.object_name, e.bone_name = rig.name, "lower"
        self.assertEqual(mp.key_frames(mp.pinned_targets(self.scene)[0]), [1.0, 10.0, 20.0])

    def test_bone_key_frames_only_on_channels_that_move_the_anchor(self):
        rig = _rig()                                         # location + rotation keys on 1, 10, 20
        lower = rig.pose.bones["lower"]
        lower.keyframe_insert("scale", frame=5)              # review 9a redo: scale moves neither point
        lower.keyframe_insert("rotation_euler", frame=15)    # rotation moves the tail, not the head
        e = self.settings.motion_paths.add(); e.object_name, e.bone_name = rig.name, "lower"
        self.assertEqual(mp.key_frames(mp.pinned_targets(self.scene)[0]), [1.0, 10.0, 20.0])
        e.anchor = 'TAIL'
        self.assertEqual(mp.key_frames(mp.pinned_targets(self.scene)[0]), [1.0, 10.0, 15.0, 20.0])

    def test_anchor_change_resamples_a_cached_path(self):
        # Review 9a redo claimed a fully cached path keeps head positions after HEAD -> TAIL.
        rig = _rig()
        e = self.settings.motion_paths.add(); e.object_name, e.bone_name = rig.name, "lower"
        mp.refresh_paths(bpy.context)
        head = mp._cache[(rig.name, "lower", 10.0)].copy()
        e.anchor = 'TAIL'                                    # update callback drops the cache
        self.assertTrue(mp.request_missing_samples(bpy.context))
        mp.refresh_paths(bpy.context)
        tail = rig.matrix_world @ rig.evaluated_get(bpy.context.evaluated_depsgraph_get()).pose.bones["lower"].tail
        self.assertGreater((mp._cache[(rig.name, "lower", 10.0)] - head).length, 1e-4)
        self.assertLess((mp._cache[(rig.name, "lower", 10.0)] - tail).length, 1e-4)

    def test_object_key_frames_only_on_origin_channels(self):
        cube = _cube()                                    # location keys on 1 and 20
        cube.keyframe_insert("scale", frame=5)            # review 9a: scale cannot move the origin
        cube.keyframe_insert("delta_location", frame=7)   # delta_location can
        e = self.settings.motion_paths.add(); e.object_name, e.bone_name = cube.name, ""
        self.assertEqual(mp.key_frames(mp.pinned_targets(self.scene)[0]), [1.0, 7.0, 20.0])

    def test_pinned_targets_skip_objects_outside_scene(self):
        cube = _cube()
        e = self.settings.motion_paths.add(); e.object_name, e.bone_name = cube.name, ""
        self.assertEqual([t.key for t in mp.pinned_targets(self.scene)], [(cube.name, "")])
        for collection in list(cube.users_collection):   # review 9a: still in bpy.data, not in the scene
            collection.objects.unlink(cube)
        self.assertIn(cube.name, bpy.data.objects)
        self.assertEqual(mp.pinned_targets(self.scene), [])
        self.assertTrue(mp.entry_is_missing(e))

    def test_set_color_cancels_on_invalid_index(self):
        self.assertEqual(bpy.ops.ghost_tool.paths_set_color(index=-1), {'CANCELLED'})   # empty list
        cube = _cube()
        e = self.settings.motion_paths.add(); e.object_name, e.bone_name = cube.name, ""
        e.color = (0.0, 0.0, 1.0)
        self.assertEqual(bpy.ops.ghost_tool.paths_set_color(index=-1, color=(1.0, 0.0, 0.0)), {'CANCELLED'})
        self.assertEqual(tuple(e.color), (0.0, 0.0, 1.0))   # review 9a: -1 must not edit the last path
        self.assertEqual(bpy.ops.ghost_tool.paths_set_color(index=0, color=(1.0, 0.0, 0.0), thickness=3), {'FINISHED'})
        self.assertEqual((tuple(e.color), e.thickness), ((1.0, 0.0, 0.0), 3))

    def test_draw_handler_registered(self):
        self.assertIsNotNone(mp._draw_handler)

    def test_pipeline_refreshes_paths_on_frame_change(self):
        from ghost_tool import ghost_pipeline as gp
        rig = _rig()
        e = self.settings.motion_paths.add(); e.object_name, e.bone_name = rig.name, "upper"
        bpy.context.view_layer.objects.active = None
        gp.GhostPipeline.get(self.scene)._run_live_update(bpy.context, self.settings, "h")
        self.assertIn((rig.name, "upper", 10.0), mp._cache)
        self.assertTrue(gp._any_live(self.settings))
        self.settings.paths_enabled = False
        self.assertFalse(gp._any_live(self.settings))

    def test_markers_on_paths_generates_for_pinned_bones_only(self):
        rig = _rig()
        e = self.settings.motion_paths.add(); e.object_name, e.bone_name = rig.name, "lower"
        self.settings.paths_show_markers = True
        count = mp.sync_markers(bpy.context)
        self.assertGreater(count, 0)
        store = gd.GhostStore.get(self.scene)
        self.assertTrue(all(g.bone_name == "lower" for g in store))
        self.settings.paths_show_markers = False
        self.assertEqual(mp.sync_markers(bpy.context), 0)
        self.assertEqual(len(store), 0)

    def test_markers_on_paths_keep_unrelated_markers(self):
        # Review 2026-10-05: toggling Markers on Paths cleared every ghost marker in the store.
        rig = _rig()
        store = gd.GhostStore.get(self.scene)
        other = gd.Ghost(frame=5.0, channel="rotation_euler.x", object_name=rig.name, bone_name="upper")
        store.add(other)
        e = self.settings.motion_paths.add(); e.object_name, e.bone_name = rig.name, "lower"
        self.settings.paths_show_markers = True
        mp._deferred_marker_sync()
        self.assertIn(other.uid, {g.uid for g in store})
        self.assertTrue(any(g.bone_name == "lower" for g in store))
        mp.sync_markers(bpy.context)   # re-sync replaces only its own markers
        self.assertEqual(sum(1 for g in store if g.uid == other.uid), 1)
        self.settings.paths_show_markers = False
        mp._deferred_marker_sync()
        self.assertEqual([g.uid for g in store], [other.uid])

    def _markers_on(self, scene=None):
        """Turn Markers on Paths on without the deferred timer, then sync once."""
        scene = scene or self.scene
        scene.ghost_tool["paths_show_markers"] = True
        return mp.sync_markers(bpy.context if scene is self.scene else SimpleNamespace(scene=scene))

    def test_markers_toggle_defers_sampling(self):
        # Review round 2: the update callback sampled frames (frame_set) inside a property update.
        rig = _rig()
        e = self.settings.motion_paths.add(); e.object_name, e.bone_name = rig.name, "lower"
        store = gd.GhostStore.get(self.scene)
        if bpy.app.timers.is_registered(mp._deferred_marker_sync):
            bpy.app.timers.unregister(mp._deferred_marker_sync)
        self.settings.paths_show_markers = True
        self.assertEqual(len(store), 0)
        self.assertTrue(bpy.app.timers.is_registered(mp._deferred_marker_sync))
        mp._deferred_marker_sync()
        self.assertTrue(any(g.bone_name == "lower" for g in store))

    def test_markers_follow_the_path_list(self):
        # Review round 2: add/remove/clear left markers out of date.
        rig = _rig()
        store = gd.GhostStore.get(self.scene)
        self.select_bones(rig, "lower")
        bpy.ops.ghost_tool.paths_add_selected()
        self._markers_on()
        self.assertEqual({g.bone_name for g in store}, {"lower"})
        self.select_bones(rig, "upper")
        bpy.ops.ghost_tool.paths_add_selected()
        self.assertEqual({g.bone_name for g in store}, {"lower", "upper"})
        bpy.ops.ghost_tool.paths_remove(index=0)          # "lower"
        self.assertEqual({g.bone_name for g in store}, {"upper"})
        bpy.ops.ghost_tool.paths_clear()
        self.assertEqual(len(store), 0)

    def test_object_path_gets_markers(self):
        # Review round 2: object paths (no bone) never produced markers.
        cube = _cube()
        e = self.settings.motion_paths.add(); e.object_name = cube.name
        self.settings.paths_range_mode = 'SCENE'   # the cube's keys (1, 20) lie outside 7-13
        self.assertGreater(self._markers_on(), 0)
        store = gd.GhostStore.get(self.scene)
        self.assertTrue(all(g.object_name == cube.name and g.bone_name == "" for g in store))

    def test_anchor_change_resamples(self):
        # Review round 2: switching HEAD -> TAIL kept drawing the cached head positions.
        rig = _rig()
        e = self.settings.motion_paths.add(); e.object_name, e.bone_name = rig.name, "lower"
        self.assertEqual(mp.refresh_paths(bpy.context), 7)
        e.anchor = 'TAIL'
        self.assertEqual(mp.refresh_paths(bpy.context), 7)
        dg = bpy.context.evaluated_depsgraph_get()
        ev = rig.evaluated_get(dg)
        tail = ev.matrix_world @ ev.pose.bones["lower"].tail
        self.assertLess((mp._cache[(rig.name, "lower", 10.0)] - tail).length, 1e-5)

    def test_marker_ownership_is_per_scene(self):
        # Review round 2: a module-wide uid set let scene B forget scene A's markers.
        rig = _rig()
        other_scene = bpy.data.scenes.new("PathsOther")
        try:
            e = self.settings.motion_paths.add(); e.object_name, e.bone_name = rig.name, "lower"
            self.assertGreater(self._markers_on(), 0)
            self.assertEqual(self._markers_on(other_scene), 0)   # B has no pinned paths
            store = gd.GhostStore.get(self.scene)
            self.assertGreater(len(store), 0)
            self.settings["paths_show_markers"] = False
            mp.sync_markers(bpy.context)
            self.assertEqual(len(store), 0)
        finally:
            bpy.data.scenes.remove(other_scene)

    def test_live_point_refresh_keeps_path_markers(self):
        # Review round 3: live point updates replaced the whole store and dropped path markers.
        from ghost_tool import ghost_pipeline as gp
        rig = _rig()
        e = self.settings.motion_paths.add(); e.object_name, e.bone_name = rig.name, "lower"
        self.assertGreater(self._markers_on(), 0)
        store = gd.GhostStore.get(self.scene)
        owned = {g.uid for g in store}
        bpy.context.view_layer.objects.active = rig
        self.settings["live_point_ghosts"] = True
        gp.GhostPipeline.get(self.scene)._update_point_ghosts_live(bpy.context, rig, self.settings)
        self.assertTrue(owned <= {g.uid for g in store})

    def test_draw_requests_refresh_for_unsampled_targets(self):
        # Review round 3: a newly followed selection drew nothing until a frame or key change.
        from ghost_tool import ghost_pipeline as gp
        cube = _cube()
        self.settings["paths_follow_selection"] = True
        for obj in bpy.data.objects:
            obj.select_set(obj is cube)
        bpy.context.view_layer.objects.active = cube
        mp.clear_cache()

        def reset_timer():
            if bpy.app.timers.is_registered(gp._deferred_live_update):
                bpy.app.timers.unregister(gp._deferred_live_update)
            gp._deferred_update_pending = False

        reset_timer()
        self.assertTrue(mp.request_missing_samples(bpy.context))
        self.assertTrue(bpy.app.timers.is_registered(gp._deferred_live_update))
        mp.refresh_paths(bpy.context)
        reset_timer()
        self.assertFalse(mp.request_missing_samples(bpy.context))
        self.assertFalse(bpy.app.timers.is_registered(gp._deferred_live_update))

    def test_path_markers_stay_inside_the_path_window(self):
        # Review round 3: markers appeared at keys outside the frames the path shows (keys 1/10/20, window 7-13).
        rig = _rig()
        e = self.settings.motion_paths.add(); e.object_name, e.bone_name = rig.name, "lower"
        self.assertGreater(self._markers_on(), 0)
        frames = {g.frame for g in gd.GhostStore.get(self.scene)}
        self.assertEqual(frames, {10.0})

    def test_cache_resamples_after_scene_switch(self):
        # Review rounds 3 and 4: positions sampled in one scene must not be drawn in another.
        # Time remapping makes the same cube evaluate to a different place in the other scene.
        cube = _cube()
        e = self.settings.motion_paths.add(); e.object_name = cube.name
        self.assertEqual(mp.refresh_paths(bpy.context), 7)
        here = mp._cache[(cube.name, "", 10.0)].copy()
        other = bpy.data.scenes.new("PathsOther")
        try:
            other.collection.objects.link(cube)
            other.render.frame_map_old, other.render.frame_map_new = 100, 50
            s = other.ghost_tool
            s["paths_enabled"], s["paths_before"], s["paths_after"] = True, 3, 3
            p = s.motion_paths.add(); p.object_name = cube.name
            other.frame_set(10)

            def other_depsgraph():
                graph = other.view_layers[0].depsgraph
                graph.update()
                return graph

            expected = cube.evaluated_get(other_depsgraph()).matrix_world.translation.copy()
            self.assertGreater((expected - here).length, 0.5)   # the scenes really differ
            fake = SimpleNamespace(scene=other, evaluated_depsgraph_get=other_depsgraph)
            self.assertEqual(mp.refresh_paths(fake), 7)
            self.assertLess((mp._cache[(cube.name, "", 10.0)] - expected).length, 1e-5)
        finally:
            bpy.data.scenes.remove(other)
        self.assertEqual(mp.refresh_paths(bpy.context), 7)
        self.assertLess((mp._cache[(cube.name, "", 10.0)] - here).length, 1e-5)

    def test_marker_resync_keeps_pin_and_selection(self):
        # Review round 4: re-syncing on every refresh replaced markers and lost pin/selection.
        rig = _rig()
        e = self.settings.motion_paths.add(); e.object_name, e.bone_name = rig.name, "lower"
        self.assertGreater(self._markers_on(), 0)
        store = gd.GhostStore.get(self.scene)
        marker = next(g for g in store if g.frame == 10.0)
        marker.is_pinned = marker.is_selected = True
        mp.sync_markers(bpy.context)                      # what a live refresh does
        kept = store.get_by_uid(marker.uid)
        self.assertIsNotNone(kept)
        self.assertTrue(kept.is_pinned and kept.is_selected)
        self.scene.frame_set(20)                           # window 17-23: key 10 leaves it
        mp.sync_markers(bpy.context)
        self.assertIsNotNone(store.get_by_uid(marker.uid))  # pinned markers stay
        self.assertTrue(any(g.frame == 20.0 for g in store))
        self.scene.frame_set(10)

    def test_marker_resync_bumps_store_version_when_positions_move(self):
        # Review round 5: in-place position updates left version-keyed caches stale.
        rig = _rig()
        e = self.settings.motion_paths.add(); e.object_name, e.bone_name = rig.name, "lower"
        self.assertGreater(self._markers_on(), 0)
        store = gd.GhostStore.get(self.scene)
        before = store.version
        mp.sync_markers(bpy.context)
        self.assertEqual(store.version, before)            # nothing moved: no spurious bump
        upper = rig.pose.bones["upper"]
        upper.rotation_euler = (1.4, 0, 0)
        upper.keyframe_insert("rotation_euler", frame=10)
        mp.sync_markers(bpy.context)
        self.assertGreater(store.version, before)

    def test_live_keyframe_ghosts_do_not_duplicate_path_markers(self):
        # Review round 5: KEYFRAMES_ONLY live ghosts and path markers stacked on the same keys.
        from ghost_tool import ghost_pipeline as gp
        rig = _rig()
        e = self.settings.motion_paths.add(); e.object_name, e.bone_name = rig.name, "lower"
        self.assertGreater(self._markers_on(), 0)
        previous_mode = self.settings.ghost_mode
        self.settings.ghost_mode = 'KEYFRAMES_ONLY'   # an enum must go through RNA, not ["..."]
        try:
            self.settings["live_point_ghosts"] = True
            bpy.context.view_layer.objects.active = rig
            gp.GhostPipeline.get(self.scene)._update_point_ghosts_live(bpy.context, rig, self.settings)
            store = gd.GhostStore.get(self.scene)
            identities = [(g.object_name, g.bone_name, g.channel, g.frame) for g in store]
            self.assertTrue(any(i[1] == "upper" for i in identities))   # live ghosts really ran
            self.assertEqual(len(identities), len(set(identities)))
            self.assertTrue(set(mp._marker_uids[get_scene_id(self.scene)]) <= {g.uid for g in store})
        finally:
            self.settings.ghost_mode = previous_mode

    def test_empty_path_window_removes_unpinned_markers(self):
        # Review round 5: an early return left markers behind when the window had no frames.
        rig = _rig()
        e = self.settings.motion_paths.add(); e.object_name, e.bone_name = rig.name, "lower"
        self.assertGreater(self._markers_on(), 0)
        with patch.object(mp, "desired_frames", return_value=[]):
            mp.sync_markers(bpy.context)
        self.assertEqual(len(gd.GhostStore.get(self.scene)), 0)

    def _assert_markers_on_path(self, rig, bone):
        """Every marker of ``bone`` sits on a sampled path point."""
        mp.refresh_paths(bpy.context)
        markers = [g for g in gd.GhostStore.get(self.scene) if g.bone_name == bone]
        self.assertTrue(markers)
        for g in markers:
            sample = mp._cache.get((rig.name, bone, g.frame))
            self.assertIsNotNone(sample, f"{g.channel} marker at unsampled frame {g.frame}")
            self.assertLess((Vector(g.world_position) - sample).length, 1e-5, f"{g.channel} @ {g.frame}")
        return markers

    def test_head_path_markers_lie_on_the_path(self):
        # Review rounds 6/7: rotation markers sat at the tail, off the default HEAD path.
        rig = _rig()
        e = self.settings.motion_paths.add(); e.object_name, e.bone_name = rig.name, "lower"
        self.assertGreater(self._markers_on(), 0)
        markers = self._assert_markers_on_path(rig, "lower")
        self.assertTrue(all(g.channel.startswith("location") for g in markers))

    def test_head_path_without_location_keys_has_no_markers(self):
        # A bone's own rotation never moves its head: no marker can sit on that path.
        rig = _rig(location_keys=False)
        e = self.settings.motion_paths.add(); e.object_name, e.bone_name = rig.name, "lower"
        self.assertEqual(self._markers_on(), 0)

    def test_tail_path_markers_lie_on_the_path(self):
        # Review round 6: location markers stayed at the head on a TAIL path.
        rig = _rig()
        e = self.settings.motion_paths.add(); e.object_name, e.bone_name = rig.name, "lower"
        e.anchor = 'TAIL'
        self.assertGreater(self._markers_on(), 0)
        markers = self._assert_markers_on_path(rig, "lower")
        self.assertEqual({g.channel.split(".")[0] for g in markers}, {"location", "rotation_euler"})

    def test_path_markers_only_on_sampled_frames(self):
        # Review rounds 6/7: Every=2 samples 7/9/11/13, yet the key at 10 got a marker.
        rig = _rig()
        e = self.settings.motion_paths.add(); e.object_name, e.bone_name = rig.name, "lower"
        self.settings["paths_step"] = 2
        self.assertEqual(self._markers_on(), 0)
        self.assertEqual(len(gd.GhostStore.get(self.scene)), 0)
        self.scene.frame_set(11)   # samples 8/10/12/14 include the key at 10
        self.assertGreater(mp.sync_markers(bpy.context), 0)
        sampled = set(mp.desired_frames(self.settings, self.scene))
        self.assertTrue(all(g.frame in sampled for g in gd.GhostStore.get(self.scene)))
        self.scene.frame_set(10)

    def test_manual_generation_keeps_path_markers(self):
        # Review round 6: Generate with clear_existing dropped the path markers.
        from ghost_tool import ghost_pipeline as gp
        rig = _rig()
        e = self.settings.motion_paths.add(); e.object_name, e.bone_name = rig.name, "lower"
        self.assertGreater(self._markers_on(), 0)
        store = gd.GhostStore.get(self.scene)
        owned = {g.uid for g in store}
        pipeline = gp.GhostPipeline.get(self.scene)
        for generate in (pipeline.generate_manual, pipeline.generate_manual_with_preview):
            generate(bpy.context, rig, rig, ["upper", "lower"], gd.MOTION_CHANNELS, 1, clear_existing=True)
            self.assertTrue(owned <= {g.uid for g in store}, generate.__name__)
            self.assertTrue(any(g.bone_name == "upper" for g in store))   # the generation really ran
            identities = [(g.object_name, g.bone_name, g.channel, g.frame) for g in store]
            self.assertEqual(len(identities), len(set(identities)), generate.__name__)

    def test_path_markers_take_over_generated_markers(self):
        # Review round 6: turning Markers on Paths on stacked a second marker on a Generate marker.
        # Fix review 84a65f0c: skipping it instead left that marker off a TAIL path and unowned.
        rig = _rig()
        store = gd.GhostStore.get(self.scene)
        generated = gd.Ghost(frame=10.0, channel="location.x", object_name=rig.name, bone_name="lower",
                             world_position=Vector((9.0, 9.0, 9.0)))
        store.add(generated)
        e = self.settings.motion_paths.add(); e.object_name, e.bone_name = rig.name, "lower"
        e.anchor = 'TAIL'
        self.assertGreater(self._markers_on(), 0)
        identities = [(g.object_name, g.bone_name, g.channel, g.frame) for g in store]
        self.assertEqual(len(identities), len(set(identities)))
        self.assertIn(generated.uid, mp._marker_uids[get_scene_id(self.scene)])   # owned now
        self._assert_markers_on_path(rig, "lower")                                  # moved onto the tail
        self.assertEqual(generated.generation_level, 0)   # review 2d806fff: like every path marker
        self.assertEqual(store.count_by_level(1), 0)       # review a28fbe5: cached level counts follow
        self.assertEqual(store.count_by_level(0), len(store))
        self.settings["paths_show_markers"] = False
        mp.sync_markers(bpy.context)
        self.assertEqual(len(store), 0)

    def test_taken_over_marker_survives_manual_regeneration(self):
        # Fix review 84a65f0c: a skipped identity was not owned, so a rebuild without it lost the marker.
        from ghost_tool import ghost_pipeline as gp
        rig = _rig()
        store = gd.GhostStore.get(self.scene)
        generated = gd.Ghost(frame=10.0, channel="location.x", object_name=rig.name, bone_name="lower")
        store.add(generated)
        e = self.settings.motion_paths.add(); e.object_name, e.bone_name = rig.name, "lower"
        self.assertGreater(self._markers_on(), 0)
        gp.GhostPipeline.get(self.scene).generate_manual(
            bpy.context, rig, rig, ["upper"], gd.MOTION_CHANNELS, 1, clear_existing=True)
        self.assertIn(generated.uid, {g.uid for g in store})

    def test_parent_animation_edit_resamples_child_path(self):
        # Review round 6: editing a parent's keys left the child's cached path stale.
        parent = _cube("Parent")
        child = bpy.data.objects.new("Child", None)
        self.scene.collection.objects.link(child)
        child.parent = parent
        child.location = (0, 0, 1)
        e = self.settings.motion_paths.add(); e.object_name = child.name
        self.assertEqual(mp.refresh_paths(bpy.context), 7)
        parent.location.x = 10.0
        parent.keyframe_insert("location", frame=20)   # moves the parent at every frame after 1
        mp.mark_dirty_for_id(parent.animation_data.action)
        self.assertEqual(mp.refresh_paths(bpy.context), 7)
        self.scene.frame_set(13)
        self.assertLess((mp._cache[(child.name, "", 13.0)] - child.matrix_world.translation).length, 1e-5)
        self.scene.frame_set(10)

    def test_ghost_tools_off_drops_path_cache(self):
        # Gap 2026-10-05: keys edited while Ghost Tools was off are never marked dirty,
        # so turning it back on drew the old path.
        cube = _cube()
        e = self.settings.motion_paths.add(); e.object_name = cube.name
        mp.refresh_paths(bpy.context)
        self.settings.is_active = False
        self.assertEqual(mp._cache, {})
        self.assertEqual(len(self.settings.motion_paths), 1)   # the list stays
        cube.location.x = 10.0
        cube.keyframe_insert("location", frame=20)
        self.settings.is_active = True
        self.assertEqual(mp.refresh_paths(bpy.context), 7)
        self.scene.frame_set(13)
        self.assertLess((mp._cache[(cube.name, "", 13.0)] - cube.matrix_world.translation).length, 1e-5)
        self.scene.frame_set(10)

    def test_undo_redo_drops_path_cache(self):
        # Gap 2026-10-05: undoing a key edit left the edited path cached.
        from ghost_tool import ghost_pipeline as gp
        from ghost_tool.session_state import _on_undo_redo
        self.assertIn(_on_undo_redo, bpy.app.handlers.undo_post)
        self.assertIn(_on_undo_redo, bpy.app.handlers.redo_post)
        cube = _cube()
        e = self.settings.motion_paths.add(); e.object_name = cube.name
        self.assertEqual(mp.refresh_paths(bpy.context), 7)
        _on_undo_redo(self.scene)
        self.assertEqual(mp._cache, {})
        self.assertEqual(mp.refresh_paths(bpy.context), 7)
        if bpy.app.timers.is_registered(gp._deferred_live_update):
            bpy.app.timers.unregister(gp._deferred_live_update)
        gp._deferred_update_pending = False

    def test_file_load_forgets_marker_ownership(self):
        # Review round 5: owned uids survived a file load and could match unrelated ghosts.
        from ghost_tool import ghost_pipeline as gp
        rig = _rig()
        e = self.settings.motion_paths.add(); e.object_name, e.bone_name = rig.name, "lower"
        self.assertGreater(self._markers_on(), 0)
        mp.refresh_paths(bpy.context)
        gp._on_file_load(None)
        self.assertEqual(mp._marker_uids, {})
        self.assertEqual(mp._cache, {})

    def test_depsgraph_update_dirties_every_changed_object(self):
        # Review round 5: the handler stopped at the first Object/Action update.
        from ghost_tool import ghost_pipeline as gp
        rig_a, rig_b = _rig("RigA"), _rig("RigB")
        for rig in (rig_a, rig_b):
            p = self.settings.motion_paths.add(); p.object_name, p.bone_name = rig.name, "upper"
        mp.refresh_paths(bpy.context)
        mp._dirty.clear()
        gp._last_depsgraph_check = 0.0
        fake = SimpleNamespace(updates=[SimpleNamespace(id=rig_a), SimpleNamespace(id=rig_b)])
        gp._on_depsgraph_update_pipeline(self.scene, fake)
        self.assertEqual(mp._dirty, {(rig_a.name, "upper"), (rig_b.name, "upper")})
        if bpy.app.timers.is_registered(gp._deferred_live_update):
            bpy.app.timers.unregister(gp._deferred_live_update)
        gp._deferred_update_pending = False

    def test_key_dots_for_bone_names_needing_escapes(self):
        # Review round 4: key_frames built pose.bones["name"] without escaping.
        rig = _rig()
        rig.data.bones["lower"].name = 'lo"wer'
        e = self.settings.motion_paths.add(); e.object_name, e.bone_name = rig.name, 'lo"wer'
        self.assertEqual(mp.key_frames(mp.pinned_targets(self.scene)[0]), [1.0, 10.0, 20.0])

    def test_add_selected_samples_immediately(self):
        # Review 2026-10-05: the first path stayed invisible until something else triggered a refresh.
        rig = _rig()
        self.select_bones(rig, "upper")
        mp.clear_cache()
        bpy.ops.ghost_tool.paths_add_selected()
        self.assertIn((rig.name, "upper", 10.0), mp._cache)
        self.assertEqual(self.scene.frame_current, 10)

    def test_path_setting_change_schedules_refresh(self):
        from ghost_tool import ghost_pipeline as gp
        if bpy.app.timers.is_registered(gp._deferred_live_update):
            bpy.app.timers.unregister(gp._deferred_live_update)
        gp._deferred_update_pending = False
        self.settings.paths_after = 5
        self.assertTrue(bpy.app.timers.is_registered(gp._deferred_live_update))

    def test_header_strips_appended(self):
        from ghost_tool import ui_panel
        self.assertIn(ui_panel._draw_timeline_header_extension, bpy.types.DOPESHEET_HT_header._dyn_ui_initialize())
        self.assertIn(ui_panel._draw_graph_header_extension, bpy.types.GRAPH_HT_header._dyn_ui_initialize())
        self.assertTrue(hasattr(bpy.types, "GHOST_PT_paths_popover"))

    def test_paths_section_in_popover_and_uilist(self):
        from ghost_tool import ui_panel
        self.assertIn("paths", [s[0] for s in ui_panel.GHOST_SECTIONS])
        self.assertTrue(hasattr(bpy.types, "GHOST_UL_paths"))
        self.assertIn("motion_paths", ui_panel._HELP_TOPICS)

    def test_frame_number_handler_registered(self):
        self.assertIsNotNone(mp._draw_handler_2d)

    def test_refresh_budget_500_samples(self):
        import time
        for i in range(10):
            rig = _rig(name=f"Rig{i}")
            for bone in ("upper", "lower"):
                e = self.settings.motion_paths.add(); e.object_name, e.bone_name = rig.name, bone
        self.settings.paths_before = self.settings.paths_after = 12
        # Median of three: one busy moment cannot fail a correct build, and one lucky run cannot
        # pass a slow one (review rounds 2 and 3).
        timings = []
        for _attempt in range(3):
            mp.clear_cache()
            t0 = time.perf_counter()
            n = mp.refresh_paths(bpy.context)
            timings.append((time.perf_counter() - t0) * 1000)
            self.assertEqual(n, 500)
        dt = sorted(timings)[1]
        print(f"PATHS_PERF samples={n} ms={dt:.0f} runs={[round(t) for t in timings]}", flush=True)
        self.assertLess(dt, 50.0)
        self.assertAlmostEqual(mp.last_refresh_ms(), timings[-1], delta=timings[-1] * 0.5 + 5.0)


if __name__ == "__main__":
    result = unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(GhostPaths))
    print("GHOST_PATHS_RESULT: " + ("PASS" if result.wasSuccessful() else "FAIL"), flush=True)
    if not result.wasSuccessful():
        sys.exit(1)
