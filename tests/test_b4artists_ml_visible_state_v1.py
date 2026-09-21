"""Exact source-edit detection across RNA modes and collection fallbacks."""
import sys, unittest
from pathlib import Path
from types import SimpleNamespace
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import bpy
from b4artists_ml import temporal_generation as g, workflow as w, rig_state as rs, posing as p


class VisibleStateTests(unittest.TestCase):
    def setUp(self):
        if bpy.context.object and bpy.context.object.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        data = bpy.data.armatures.new('source_guard_test')
        self.obj = bpy.data.objects.new('source_guard_test', data)
        bpy.context.collection.objects.link(self.obj)
        bpy.context.view_layer.objects.active = self.obj
        self.obj.select_set(True)
        bpy.ops.object.mode_set(mode='EDIT')
        parent = None
        for i in range(8):
            b = data.edit_bones.new('joint_' + str(i))
            b.head = (0, 0, i); b.tail = (0, 0, i + 1)
            b.parent = parent
            b.use_connect = i == 1
            parent = b
        bpy.ops.object.mode_set(mode='OBJECT')
        self.scene = bpy.context.scene
        for b, mode in zip(self.obj.pose.bones, ('XYZ','XZY','YXZ','YZX','ZXY','ZYX','QUATERNION','AXIS_ANGLE')):
            b.rotation_mode = mode
            b.rotation_euler = (.1, .2, .3)
            b.rotation_quaternion = (1, .1, .2, .3)
            b.rotation_axis_angle = (.2, 0, 1, 0)

    def tearDown(self):
        data = self.obj.data
        bpy.data.objects.remove(self.obj, do_unlink=True)
        bpy.data.armatures.remove(data)

    def legacy(self, state):
        return (state.frame == p._frame(self.scene)
                and state.pose == w.raw_pose(self.obj)
                and state.modes == rs.mode_values(self.obj)
                and all(tuple(getattr(self.obj, n)) == v for n, v in state.channels.items()))

    def trial(self, owner, field, value):
        original = getattr(owner, field)
        original = tuple(original) if hasattr(original, '__len__') and not isinstance(original, str) else original
        rotations = {n:tuple(getattr(owner,n)) for n in ('rotation_euler','rotation_quaternion','rotation_axis_angle')} if field == 'rotation_mode' else {}
        state = g.VisibleState(self.obj, self.scene)
        self.assertTrue(state.matches())
        try:
            setattr(owner, field, value)
            self.assertEqual(state.matches(), self.legacy(state))
        finally:
            setattr(owner, field, original)
            # Changing rotation mode can convert RNA channels; restore the actual values too.
            for n, v in rotations.items(): setattr(owner, n, v)
        self.assertTrue(state.matches())

    def test_all_rotation_modes_active_inactive_fields_and_locks(self):
        for bone in self.obj.pose.bones:
            for field in ('location','scale','rotation_euler','rotation_quaternion','rotation_axis_angle','lock_location','lock_scale','lock_rotation'):
                with self.subTest(bone=bone.name, field=field):
                    value = list(getattr(bone, field))
                    value[0] = not value[0] if isinstance(value[0], bool) else value[0] + .125
                    self.trial(bone, field, value)
            for field in ('lock_rotations_4d','lock_rotation_w'):
                self.trial(bone, field, True)
            bone.lock_rotations_4d = True
            self.trial(bone, 'lock_rotation_w', True)
            self.trial(bone, 'rotation_mode', 'XYZ' if bone.rotation_mode != 'XYZ' else 'ZYX')

    def test_object_channels_playhead_and_warm_buffer_recovery(self):
        for field in g._CHANNELS:
            value = list(getattr(self.obj, field)); value[0] += .125
            self.trial(self.obj, field, value)
        state = g.VisibleState(self.obj, self.scene)
        before = p._frame(self.scene)
        try:
            self.scene.frame_set(self.scene.frame_current + 1, subframe=.25)
            self.assertFalse(state.matches())
        finally:
            g._frame(self.scene, before)
        self.assertTrue(state.matches())
        bone = self.obj.pose.bones[0]; before = bone.location.copy()
        for _ in range(3):
            self.assertTrue(state.matches())
            bone.location.x += .125
            self.assertFalse(state.matches())
            bone.location = before

    def test_connected_bones_and_renaming(self):
        bone = self.obj.pose.bones[1]
        self.assertTrue(bone.bone.use_connect)
        state = g.VisibleState(self.obj, self.scene)
        bone.lock_location = (True, True, True)
        self.assertEqual(state.matches(), self.legacy(state))
        self.assertTrue(state.matches())  # Already unwritable while connected.
        bone.name += '_renamed'
        self.assertFalse(state.matches())

    def test_structural_change_rejects_without_retained_rna_references(self):
        state = g.VisibleState(self.obj, self.scene)
        bpy.ops.object.mode_set(mode='EDIT')
        b = self.obj.data.edit_bones.new('extra'); b.head=(1,0,0); b.tail=(1,0,1)
        bpy.ops.object.mode_set(mode='OBJECT')
        self.assertFalse(state.matches())

    def test_unsupported_batch_read_and_reordered_collection_fallback(self):
        pose = w.raw_pose(self.obj); check = g._PoseComparison(pose)
        live = tuple(self.obj.pose.bones)
        class Bones:
            def __init__(self, items, error): self.items=items; self.error=error
            def __iter__(self): return iter(self.items)
            def __len__(self): return len(self.items)
            def foreach_get(self, field, values): raise self.error('unsupported')
        for error in (TypeError, AttributeError, RuntimeError):
            for items in (live, tuple(reversed(live))):
                proxy = SimpleNamespace(pose=SimpleNamespace(bones=Bones(items,error)))
                self.assertTrue(check.matches(proxy))
                before = live[0].location.copy(); live[0].location.x += .125
                try:
                    self.assertFalse(check.matches(proxy))
                finally:
                    live[0].location = before
        # An invalid RNA reference remains an error, never a stale-cache success.
        proxy = SimpleNamespace(pose=SimpleNamespace(bones=Bones(live,ReferenceError)))
        with self.assertRaises(ReferenceError): check.matches(proxy)

    def test_empty_pose_and_nonfinite_live_edit(self):
        class Empty:
            def __iter__(self): return iter(())
            def __len__(self): return 0
            def foreach_get(self, field, values): pass
        self.assertTrue(g._PoseComparison({}).matches(SimpleNamespace(pose=SimpleNamespace(bones=Empty()))))
        state = g.VisibleState(self.obj, self.scene)
        self.obj.pose.bones[0].location.x = float('nan')
        self.assertFalse(state.matches())

if __name__ == '__main__': unittest.main()
