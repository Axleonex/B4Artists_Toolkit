"""Ghost Tool 3.4: header menu, rotation markers, whole-character onion skins.

Run with:
    bforartists --background --factory-startup --python-exit-code 1 --python tests/test_ghost_header_ui.py
"""

from __future__ import annotations

import math
import sys
import types
import unittest
from pathlib import Path

import bpy
from mathutils import Euler, Vector

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import ghost_tool  # noqa: E402
from ghost_tool import ghost_data as gd  # noqa: E402
from ghost_tool import mesh_ghosts as mg  # noqa: E402
from ghost_tool import modal_operator as mo  # noqa: E402
from ghost_tool import motion_channels as mc  # noqa: E402
from ghost_tool import ui_panel  # noqa: E402


def _walk(cls):
    for sub in cls.__subclasses__():
        yield sub
        yield from _walk(sub)


def _clear_scene():
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj)
    for action in list(bpy.data.actions):
        bpy.data.actions.remove(action)


def _fk_rig(name="Rig", rotation_mode="XYZ", location_keys=False):
    """Two-bone chain animated by rotation (and optionally root location)."""
    data = bpy.data.armatures.new(name)
    rig = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(rig)
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.mode_set(mode='EDIT')
    upper = data.edit_bones.new("upper")
    upper.head, upper.tail = (0, 0, 0), (0, 0.1, 1)
    lower = data.edit_bones.new("lower")
    lower.head, lower.tail = (0, 0.1, 1), (0.2, 0.1, 1.8)
    lower.parent = upper
    bpy.ops.object.mode_set(mode='POSE')
    for pose_bone in rig.pose.bones:
        pose_bone.rotation_mode = rotation_mode
    for frame, angle in ((1, 0.0), (10, 0.8), (20, -0.4)):
        for pose_bone, scale in ((rig.pose.bones["upper"], 1.0), (rig.pose.bones["lower"], 0.6)):
            if rotation_mode == 'QUATERNION':
                pose_bone.rotation_quaternion = Euler((angle * scale, 0.2 * angle, 0)).to_quaternion()
                pose_bone.keyframe_insert("rotation_quaternion", frame=frame)
            else:
                pose_bone.rotation_euler = (angle * scale, 0.2 * angle, 0)
                pose_bone.keyframe_insert("rotation_euler", frame=frame)
        if location_keys:
            rig.pose.bones["upper"].location = (angle, 0, 0)
            rig.pose.bones["upper"].keyframe_insert("location", frame=frame)
    bpy.context.scene.frame_set(1)
    return rig


def _fake_drag(ghost, editing_mode='INSERT_KEY'):
    """The drag operator's own methods on a stand-in instance (no modal needed)."""
    op = types.SimpleNamespace(
        _editing_mode=editing_mode, _falloff_neighbors=[], _multi_drag_ghosts=[], _temp_keys={},
        _original_position=ghost.world_position.copy(), _original_local_value=ghost.local_value,
        _undo_snapshots={}, _affected_fcurves={},
    )
    for name in ("_preview_model_a", "_collect_driven_channels", "_solve_channel_values",
                 "_update_fcurve_from_position"):
        setattr(op, name, types.MethodType(mo.GhostDragOperator.__dict__[name], op))
    obj = bpy.data.objects[ghost.object_name]
    op._driven = op._collect_driven_channels(bpy.context, ghost, obj)
    op._rotation_frame = (mc.capture_rotation_frame(bpy.context.scene, obj, ghost.bone_name, ghost.frame)
                          if mc.is_rotation_channel(ghost.channel) else None)
    return op


class GhostHeaderUI(unittest.TestCase):
    def setUp(self):
        _clear_scene()
        self.scene = bpy.context.scene
        self.scene.frame_start, self.scene.frame_end = 1, 20
        gd.GhostStore.get(self.scene).clear()

    # -------------------------------------------------------------- layout
    def test_no_viewport_sidebar_tab_and_header_menu_present(self):
        ours = {c.__name__: c for c in _walk(bpy.types.Panel)
                if (c.__module__ or "").startswith("ghost_tool") and getattr(c, "is_registered", False)}
        sidebar = [n for n, c in ours.items() if c.bl_space_type == 'VIEW_3D' and c.bl_region_type == 'UI']
        self.assertEqual(sidebar, ["GHOST_PT_window"])  # only in "Open in Separate Window" windows
        self.assertFalse(ui_panel.GHOST_PT_window.poll(bpy.context))
        self.assertIn("GHOST_PT_header_menu", ours)
        self.assertEqual(ours["GHOST_PT_header_menu"].bl_region_type, 'HEADER')
        draws = getattr(bpy.types.VIEW3D_MT_editor_menus.draw, "_draw_funcs", [])
        self.assertIn(ui_panel._draw_viewport_header_menu, draws)
        self.assertTrue(hasattr(bpy.ops.ghost_tool, "open_window"))
        self.assertEqual([s[1] for s in ui_panel.GHOST_SECTIONS],
                         ["Show Ghosts", "Onion Skin", "Edit Motion", "Compare", "Physics", "Look", "Settings"])

    # -------------------------------------------------------------- rotation markers
    def test_rotation_only_rig_gets_markers_on_bone_tails(self):
        for mode in ("XYZ", "QUATERNION"):
            with self.subTest(mode=mode):
                _clear_scene()
                rig = _fk_rig(rotation_mode=mode)
                ghosts = gd.generate_ghosts_frame_step(rig, rig, ["upper", "lower"], mc.MOTION_CHANNELS,
                                                       [4.0, 7.0, 14.0])
                self.assertTrue(ghosts, "rotation-only animation produced no markers")
                self.assertEqual(gd.generate_ghosts_frame_step(rig, rig, ["upper", "lower"], mc.LOCATION_CHANNELS,
                                                               [4.0]), [])
                for ghost in ghosts:
                    self.assertTrue(mc.is_rotation_channel(ghost.channel))
                    self.scene.frame_set(int(ghost.frame))
                    tail = rig.matrix_world @ rig.pose.bones[ghost.bone_name].tail
                    self.assertLess((ghost.world_position - tail).length, 1e-4)

    def test_location_markers_stay_on_the_head(self):
        rig = _fk_rig(location_keys=True)
        ghosts = [g for g in gd.generate_ghosts_frame_step(rig, rig, ["upper"], mc.MOTION_CHANNELS, [5.0])
                  if g.channel.startswith("location")]
        self.assertEqual(len(ghosts), 3)
        self.scene.frame_set(5)
        head = rig.matrix_world @ rig.pose.bones["upper"].head
        for ghost in ghosts:
            self.assertLess((ghost.world_position - head).length, 1e-4)

    def test_rotation_drag_aims_the_bone_at_the_drop_point(self):
        for mode in ("XYZ", "ZXY", "QUATERNION"):
            with self.subTest(mode=mode):
                _clear_scene()
                rig = _fk_rig(rotation_mode=mode)
                store = gd.GhostStore.get(self.scene)
                store.replace_all(gd.generate_ghosts_frame_step(rig, rig, ["lower"], mc.MOTION_CHANNELS, [6.0]))
                ghost = store.all_ghosts[0]
                self.scene.frame_set(6)
                head = rig.matrix_world @ rig.pose.bones["lower"].head
                target = head + Vector((0.6, -0.3, 0.5)).normalized() * 2.0
                op = _fake_drag(ghost)
                self.assertEqual(len(op._driven), 4 if mode == 'QUATERNION' else 3)
                op._update_fcurve_from_position(bpy.context, ghost, target)
                self.scene.frame_set(6)
                pose_bone = rig.pose.bones["lower"]
                aimed = (rig.matrix_world @ pose_bone.tail) - (rig.matrix_world @ pose_bone.head)
                self.assertLess(math.degrees(aimed.angle(target - head)), 0.05)
                # every sibling marker moved with it
                for entry in op._driven:
                    if entry["ghost"] is not None:
                        self.assertLess((entry["ghost"].world_position - target).length, 1e-6)

    def test_rotation_drag_in_reshape_mode(self):
        """The default "Reshape Handles" drop bends the curve through the new pose without adding keys."""
        rig = _fk_rig()
        store = gd.GhostStore.get(self.scene)
        store.replace_all(gd.generate_ghosts_frame_step(rig, rig, ["lower"], mc.MOTION_CHANNELS, [6.0]))
        ghost = store.all_ghosts[0]
        keys_before = {e.data_path + str(e.array_index): len(e.keyframe_points)
                       for e in rig.animation_data.action.fcurves} if hasattr(rig.animation_data.action, "fcurves") else None
        self.scene.frame_set(6)
        head = rig.matrix_world @ rig.pose.bones["lower"].head
        target = head + Vector((0.5, -0.2, 0.6)).normalized() * 2.0
        self.scene.ghost_tool.curve_mode = 'FREE'
        op = _fake_drag(ghost, editing_mode='RESHAPE')
        # A real drag re-applies the reshape on every mouse move; Free handles converge on the pose.
        for _ in range(30):
            op._update_fcurve_from_position(bpy.context, ghost, target)
        self.scene.frame_set(6)
        pose_bone = rig.pose.bones["lower"]
        aimed = (rig.matrix_world @ pose_bone.tail) - (rig.matrix_world @ pose_bone.head)
        self.assertLess(math.degrees(aimed.angle(target - head)), 0.05)
        self.assertFalse(op._temp_keys)
        if keys_before is not None:
            self.assertEqual(keys_before, {e.data_path + str(e.array_index): len(e.keyframe_points)
                                           for e in rig.animation_data.action.fcurves})

    def test_location_drag_lands_where_dropped(self):
        rig = _fk_rig(location_keys=True)
        store = gd.GhostStore.get(self.scene)
        store.replace_all([g for g in gd.generate_ghosts_frame_step(rig, rig, ["upper"], mc.MOTION_CHANNELS, [5.0])
                           if g.channel.startswith("location")])
        ghost = store.all_ghosts[0]
        target = ghost.world_position + Vector((0.3, 0.4, -0.2))
        op = _fake_drag(ghost)
        op._update_fcurve_from_position(bpy.context, ghost, target)
        self.scene.frame_set(5)
        head = rig.matrix_world @ rig.pose.bones["upper"].head
        self.assertLess((head - target).length, 1e-4)

    def test_rotation_drag_cancel_restores_curves(self):
        rig = _fk_rig()
        store = gd.GhostStore.get(self.scene)
        store.replace_all(gd.generate_ghosts_frame_step(rig, rig, ["upper"], mc.MOTION_CHANNELS, [6.0]))
        ghost = store.all_ghosts[0]
        op = _fake_drag(ghost)
        from ghost_tool import fcurve_utils
        for entry in op._driven:
            op._undo_snapshots[entry["key"]] = fcurve_utils.snapshot_fcurve(entry["fcurve"])
            op._affected_fcurves[entry["key"]] = entry["fcurve"]
        before = {e["key"]: [tuple(k.co) for k in e["fcurve"].keyframe_points] for e in op._driven}
        op._update_fcurve_from_position(bpy.context, ghost, ghost.world_position + Vector((0.5, 0, 0)))
        self.assertTrue(op._temp_keys)
        op._drag_session = None
        op._active_ghost = ghost
        op._cleanup = types.MethodType(mo.GhostDragOperator.__dict__["_cleanup"], op)
        op.report = lambda *a, **k: None
        mo.GhostDragOperator.__dict__["_cancel_drag"](op, bpy.context)
        after = {e: [tuple(k.co) for k in fc.keyframe_points] for e, fc in
                 ((entry["key"], entry["fcurve"]) for entry in _fake_drag(ghost)._driven)}
        self.assertEqual(before, after)

    # -------------------------------------------------------------- onion skin
    def _character(self, name, parented=True):
        rig = _fk_rig(name=name)
        bpy.ops.object.mode_set(mode='OBJECT')
        meshes = []
        for part in ("body", "shirt"):
            mesh = bpy.data.meshes.new(f"{name}_{part}")
            mesh.from_pydata([(0, 0, 0), (0.2, 0, 0), (0, 0.2, 0.5)], [], [(0, 1, 2)])
            obj = bpy.data.objects.new(f"{name}_{part}", mesh)
            self.scene.collection.objects.link(obj)
            if parented or part == "body":
                obj.parent = rig
            modifier = obj.modifiers.new("Armature", 'ARMATURE')
            modifier.object = rig
            meshes.append(obj)
        return rig, meshes

    def test_onion_skin_ghosts_every_mesh_of_every_character(self):
        rig_a, meshes_a = self._character("A")
        rig_b, meshes_b = self._character("B", parented=False)  # shirt only deformed, not parented
        self.assertEqual(set(mg.resolve_mesh_objects(rig_a)), set(meshes_a))
        self.assertEqual(set(mg.resolve_mesh_objects(rig_b)), set(meshes_b))
        for obj in bpy.data.objects:
            obj.select_set(obj in (rig_a, rig_b))
        bpy.context.view_layer.objects.active = rig_a
        sources = mg.ghost_source_objects(bpy.context)
        self.assertEqual(set(sources), {rig_a, rig_b})
        count = mg.generate_mesh_ghosts(bpy.context, sources, [4.0, 8.0], past_count=5, future_count=5)
        self.assertEqual(count, 2 * 4)  # 2 frames x 4 meshes
        ghosts = [o for o in bpy.data.objects if o.get(mg.GHOST_TOOL_MESH_GHOST_KEY)]
        self.assertEqual({o["ghost_tool_source"] for o in ghosts}, {m.name for m in meshes_a + meshes_b})
        self.assertTrue(all(o.hide_select for o in ghosts))
        self.assertEqual(len({o.name for o in ghosts}), len(ghosts))
        self.assertTrue(mg.update_mesh_ghosts_incremental(bpy.context) in (True, False))

    def test_xray_and_fade(self):
        rig, meshes = self._character("C")
        settings = self.scene.ghost_tool
        mg.generate_mesh_ghosts(bpy.context, rig, [2.0, 4.0, 18.0], past_count=5, future_count=5)
        ghosts = [o for o in bpy.data.objects if o.get(mg.GHOST_TOOL_MESH_GHOST_KEY)]
        self.assertTrue(ghosts and not any(o.show_in_front for o in ghosts))
        settings.mesh_ghost_xray = True
        self.assertTrue(all(o.show_in_front for o in ghosts))
        settings.mesh_ghost_xray = False
        self.assertFalse(any(o.show_in_front for o in ghosts))
        settings.ghost_falloff_curve = 'EXPONENTIAL'   # markers' fade no longer drives onion skins
        settings.mesh_ghost_falloff = 'CONSTANT'
        alphas = {round(mg._compute_ghost_color_alpha(f, 10.0, 16.0, settings)[1], 5) for f in (2.0, 9.0, 18.0)}
        self.assertEqual(len(alphas), 1)
        settings.mesh_ghost_falloff = 'LINEAR'
        alphas = [mg._compute_ghost_color_alpha(f, 10.0, 16.0, settings)[1] for f in (9.0, 2.0)]
        self.assertGreater(alphas[0], alphas[1])


if __name__ == "__main__":
    ghost_tool.register()
    try:
        result = unittest.main(argv=[sys.argv[0]], exit=False, verbosity=2).result
    finally:
        ghost_tool.unregister()
    if not result.wasSuccessful():
        sys.exit(1)
