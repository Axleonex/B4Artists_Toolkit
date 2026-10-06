"""Ghost Tool Round E: the fast path sampler. Run with:
    bforartists --background --factory-startup --python tests/test_ghost_paths_fast.py
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_ghost_paths import _clear_scene, _cube, _rig, bpy, ghost_tool  # noqa: E402
from ghost_tool import path_fast_sampler as fs  # noqa: E402

FRAMES = [float(f) for f in range(1, 21)] + [4.5, 12.25]   # subframes too


def _stepped(obj, bone, anchor, frames):
    """What frame stepping gives: the evaluated object (and pose bone) at each frame."""
    scene = bpy.context.scene
    out = []
    for f in frames:
        scene.frame_set(int(f), subframe=f - int(f))
        ev = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
        if bone:
            pb = ev.pose.bones[bone]
            out.append((ev.matrix_world @ (pb.tail if anchor == 'TAIL' else pb.head)).copy())
        else:
            out.append(ev.matrix_world.translation.copy())
    scene.frame_set(1)
    return out


def _rig_in_mode(mode):
    rig = _rig("Rig" + mode)
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.mode_set(mode='POSE')
    rig.animation_data_clear()   # drop _rig's Euler keys; this rig is keyed in ``mode`` below
    for pb in rig.pose.bones:
        pb.rotation_mode = mode
    from mathutils import Euler, Quaternion
    for frame, angle in ((1, 0.0), (10, 0.8), (20, -0.4)):
        for pb in rig.pose.bones:
            e = Euler((angle, 0.3 * angle, -0.2), 'XYZ')
            if mode == 'QUATERNION':
                pb.rotation_quaternion = e.to_quaternion()
                pb.keyframe_insert("rotation_quaternion", frame=frame)
            elif mode == 'AXIS_ANGLE':
                axis, a = e.to_quaternion().to_axis_angle()
                pb.rotation_axis_angle = (a, *axis)
                pb.keyframe_insert("rotation_axis_angle", frame=frame)
            else:
                pb.rotation_euler = Euler(e.to_matrix().to_euler(mode), mode)
                pb.keyframe_insert("rotation_euler", frame=frame)
            pb.location = (0.0, 0.1 * angle, 0.0)
            pb.keyframe_insert("location", frame=frame)
            pb.scale = (1.0 + 0.2 * angle,) * 3
            pb.keyframe_insert("scale", frame=frame)
    bpy.ops.object.mode_set(mode='OBJECT')
    return rig


class FastSampler(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with patch.object(ghost_tool, "_clear_pycache"):
            ghost_tool.register()

    @classmethod
    def tearDownClass(cls):
        ghost_tool.unregister()

    def setUp(self):
        _clear_scene()
        scene = bpy.context.scene
        scene.frame_start, scene.frame_end = 1, 20
        scene.ghost_tool.live_point_ghosts = scene.ghost_tool.live_mesh_ghosts = False
        scene.frame_set(1)

    def assertMatchesStepping(self, obj, bone="", anchor='HEAD'):
        self.assertTrue(fs.fast_eligible(obj, bone), fs.first_ineligibility(obj, bone))
        fast = fs.sample_fast(obj, bone, anchor, FRAMES)
        stepped = _stepped(obj, bone, anchor, FRAMES)
        worst = max((a - b).length for a, b in zip(fast, stepped))
        self.assertLess(worst, 1e-4, f"{obj.name} {bone} {anchor}: {worst}")

    def test_fast_sampler_matches_frame_set_on_fixture_rig(self):
        rig = _rig()
        for bone in ("upper", "lower"):
            for anchor in ('HEAD', 'TAIL'):
                self.assertMatchesStepping(rig, bone, anchor)

    def test_every_rotation_mode(self):
        for mode in ('XYZ', 'XZY', 'YXZ', 'YZX', 'ZXY', 'ZYX', 'QUATERNION', 'AXIS_ANGLE'):
            with self.subTest(mode=mode):
                _clear_scene()
                rig = _rig_in_mode(mode)
                self.assertMatchesStepping(rig, "lower", 'TAIL')

    def test_animated_armature_object_and_object_under_a_static_parent(self):
        rig = _rig()
        rig.rotation_mode = 'YXZ'
        for frame, z in ((1, 0.0), (20, 1.2)):
            rig.rotation_euler = (0.2, 0.0, z)
            rig.location = (z, 0.0, 0.5 * z)
            rig.keyframe_insert("rotation_euler", frame=frame)
            rig.keyframe_insert("location", frame=frame)
        self.assertMatchesStepping(rig, "lower", 'TAIL')
        cube = _cube()
        bpy.ops.object.empty_add(location=(1.0, 2.0, 0.5), rotation=(0.0, 0.3, 0.7))
        parent = bpy.context.object
        cube.parent = parent
        cube.matrix_parent_inverse = parent.matrix_world.inverted()
        cube.delta_location = (0.0, 0.3, 1.0)
        for frame, s in ((1, 1.0), (20, 2.0)):
            cube.scale = (s, 1.0, s)
            cube.keyframe_insert("scale", frame=frame)
        self.assertMatchesStepping(cube)

    def test_connected_bone_ignores_its_location(self):
        rig = _rig()
        bpy.context.view_layer.objects.active = rig
        bpy.ops.object.mode_set(mode='EDIT')
        rig.data.edit_bones["lower"].use_connect = True
        bpy.ops.object.mode_set(mode='POSE')
        lower = rig.pose.bones["lower"]
        for frame, y in ((1, 0.0), (20, 0.7)):
            lower.location = (0.0, y, 0.0)
            lower.keyframe_insert("location", frame=frame)
        bpy.ops.object.mode_set(mode='OBJECT')
        self.assertMatchesStepping(rig, "lower", 'HEAD')

    def test_fast_sampler_refuses_what_it_does_not_model(self):
        rig = _rig()
        self.assertTrue(fs.fast_eligible(rig, "lower"))
        c = rig.pose.bones["lower"].constraints.new('COPY_LOCATION')
        self.assertFalse(fs.fast_eligible(rig, "lower"))                    # a constraint in the chain
        rig.pose.bones["lower"].constraints.remove(c)
        fc = rig.pose.bones["upper"].driver_add("location", 0)
        self.assertFalse(fs.fast_eligible(rig, "lower"))                    # a driver
        rig.pose.bones["upper"].driver_remove("location", 0)
        self.assertTrue(fs.fast_eligible(rig, "lower"))
        bpy.ops.object.empty_add()
        mover = bpy.context.object
        mover.keyframe_insert("location", frame=1)
        rig.parent = mover
        self.assertFalse(fs.fast_eligible(rig, "lower"))                    # an animated parent
        rig.parent = None
        rig.data.bones["lower"].inherit_scale = 'NONE'
        self.assertFalse(fs.fast_eligible(rig, "lower"))                    # non-default inheritance
        rig.data.bones["lower"].inherit_scale = 'FULL'
        rig.delta_scale = (2.0, 1.0, 1.0)
        self.assertFalse(fs.fast_eligible(rig, "upper"))                    # delta scale
        rig.delta_scale = (1.0, 1.0, 1.0)
        track = rig.animation_data.nla_tracks.new()
        self.assertFalse(fs.fast_eligible(rig, "upper"))                    # NLA
        rig.animation_data.nla_tracks.remove(track)
        rig.animation_data.action_blend_type = 'ADD'
        self.assertFalse(fs.fast_eligible(rig, "upper"))                    # Add layers onto the defaults
        rig.animation_data.action_blend_type = 'COMBINE'                    # Blender 5's default: fine
        cube = _cube()
        cube.parent, cube.parent_type, cube.parent_bone = rig, 'BONE', "lower"
        self.assertFalse(fs.fast_eligible(cube))                            # a bone parent
        self.assertFalse(fs.fast_eligible(_cube("Other"), "", vertex_index=0))   # vertex paths step
        self.assertIsNone(fs.first_ineligibility(rig, "lower"))
        del fc


if __name__ == "__main__":
    result = unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(FastSampler))
    print("GHOST_PATHS_FAST_RESULT: " + ("PASS" if result.wasSuccessful() else "FAIL"), flush=True)
    if not result.wasSuccessful():
        sys.exit(1)
