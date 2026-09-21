"""Causal canonical input and real-rig sampling recovery; no model quality claim."""
from pathlib import Path
import sys, unittest
import numpy as np
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT/'training/b4artists_ml'), str(ROOT/'tests')]
from rig_observations import encode, sample, SCHEMA
from semantic_hierarchy_packet_v1 import packet as hierarchy_packet, STATE_WIDTH
try:
    import bpy
except ImportError:
    bpy = None


def fixture():
    rng = np.random.default_rng(19)
    rest = rng.normal(size=(17, 3))
    rest[11] = (1, 0, 0); rest[14] = (-1, 0, 0)
    rest[5] = (1, 0, 2); rest[8] = (-1, 0, 2)
    r = np.broadcast_to(np.eye(3), (17, 3, 3)).copy()
    p = np.broadcast_to(rest, (4, 17, 3)).copy()
    p[1] += (.2, .1, .3); p[2] -= (.1, 0, 0); p[3] += (.3, .1, .3)
    return rest, r, p, np.broadcast_to(r, (4, 17, 3, 3)).copy()


class ObservationMathTests(unittest.TestCase):
    def test_world_roundtrip_and_exact_endpoints(self):
        args = fixture(); ob = encode(*args, duration=.5, dt=1/30, context=True)
        np.testing.assert_allclose(ob.world_points(ob.positions), args[2], atol=1e-14)
        np.testing.assert_allclose(ob.world_rotations(ob.rotations), args[3], atol=1e-14)
        p, r = ob.baseline(np.array([0., .37, 1.]))
        np.testing.assert_array_equal(p[[0, -1]], ob.positions[:2])
        np.testing.assert_allclose(r[[0, -1]], ob.rotations[:2], atol=1e-14)
        self.assertEqual(ob.features().shape, (667,))
        self.assertEqual(ob.schema, SCHEMA)

    def test_global_translation_rotation_scale_invariance(self):
        from temporal_data import quat_matrix
        args = fixture(); a = encode(*args, duration=.5, dt=1/30, context=True)
        q = quat_matrix(np.array([.8, .1, .3, -.2]))
        rest, r, p, rotations = args
        b = encode(rest @ q.T*2.4+17, q @ r, p @ q.T*2.4+17, q @ rotations, duration=.5, dt=1/30, context=True)
        np.testing.assert_allclose(a.features(), b.features(), atol=1e-14)

    def test_bone_roll_is_calibrated(self):
        from temporal_data import quat_matrix
        rest, r, p, rotations = fixture()
        rolls = quat_matrix(np.random.default_rng(7).normal(size=(17, 4)))
        a = encode(rest, r, p, rotations, duration=.5, dt=1/30, context=True)
        b = encode(rest, r @ rolls, p, rotations @ rolls, duration=.5, dt=1/30, context=True)
        np.testing.assert_allclose(a.features(), b.features(), atol=1e-14)

    def test_composed_rotations_are_projected_to_so3(self):
        rest, rest_rotations, observed, rotations = fixture()
        rotations = rotations.copy()
        rotations[:, :, 0, 0] += 8e-6
        result = encode(rest, rest_rotations, observed, rotations, duration=.5, dt=1/30, context=True)
        identity = result.rotations @ np.swapaxes(result.rotations, -1, -2)
        np.testing.assert_allclose(identity, np.broadcast_to(np.eye(3), identity.shape), atol=1e-12)
        np.testing.assert_allclose(np.linalg.det(result.rotations), 1., atol=1e-12)

    def test_semantic_hierarchy_packet_rejects_nonrigid_edges(self):
        result = encode(*fixture(), duration=.5, dt=1/30, context=True)
        invalid = result.positions.copy()
        invalid[1, 7] += (.1, 0, 0)
        from dataclasses import replace
        with self.assertRaisesRegex(ValueError, "fixed-offset"):
            hierarchy_packet(replace(result, positions=invalid))

    def test_absent_context_cannot_leak(self):
        args = fixture(); a = encode(*args, duration=.5, dt=1/30, context=False)
        args[2][2:] += 900
        b = encode(*args, duration=.5, dt=1/30, context=False)
        np.testing.assert_array_equal(a.features(), b.features())

    def test_invalid_reference_and_rotation_rejected(self):
        args = fixture(); args[0][11] = args[0][14]
        with self.assertRaises(ValueError): encode(*args, duration=.5, dt=1/30, context=True)
        args = fixture(); args[3][0, 0, 0, 0] = -1
        with self.assertRaises(ValueError): encode(*args, duration=.5, dt=1/30, context=True)

    def test_invalid_timing_and_queries(self):
        for d in (-1., np.nan, .01):
            with self.assertRaises(ValueError): encode(*fixture(), duration=d, dt=1/30, context=True)
        ob = encode(*fixture(), duration=.5, dt=1/30, context=True)
        for t in ([np.nan], [-.1], [1.1], .5):
            with self.assertRaises(ValueError): ob.baseline(t)


@unittest.skipIf(bpy is None, 'Bforartists required')
class ObservationRigTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import b4artists_ml
        b4artists_ml.register()
        from test_b4artists_ml_posing import boneforge_rig, rigify_rig
        from test_b4artists_ml_imported_humanoids import PROFILES, authored
        cls.rigs = dict(boneforge=boneforge_rig(), basic=rigify_rig(), default=rigify_rig(full=True),
                        basic_meta=rigify_rig(generate=False), default_meta=rigify_rig(full=True, generate=False))
        cls.rigs.update({name: authored(name, index)[0] for index, name in enumerate(PROFILES)})

    def state(self, ob):
        from b4artists_ml import workflow as w, rig_state as rs
        action = ob.animation_data.action if ob.animation_data else None
        keys = []
        if action:
            keys = [(c.data_path, c.array_index, [(tuple(k.co), tuple(k.handle_left), tuple(k.handle_right), k.interpolation) for k in c.keyframe_points])
                    for c in w.action_curves(action, ob.animation_data.action_slot)]
        return (w.raw_pose(ob), rs.mode_values(ob), bpy.context.scene.frame_current,
                bpy.context.scene.frame_subframe, tuple(v for row in ob.matrix_basis for v in row),
                action, tuple((o.name, o.type) for o in bpy.data.objects), len(bpy.data.actions), keys)

    def test_all_profiles_rest_roundtrip_and_recovery(self):
        for name, ob in self.rigs.items():
            with self.subTest(rig=name):
                bpy.context.scene.frame_set(7, subframe=.25)
                before = self.state(ob); result = sample(ob, 2, 12)
                self.assertEqual(self.state(ob), before)
                self.assertEqual(result.positions.shape, (4, 17, 3))
                self.assertEqual(result.features().shape, (667,))
                np.testing.assert_allclose(result.rotations @ np.swapaxes(result.rotations, -1, -2), np.broadcast_to(np.eye(3), (4, 17, 3, 3)), atol=2e-5)
                hierarchy = hierarchy_packet(result)
                reconstructed_positions, reconstructed_rotations = hierarchy.world()
                np.testing.assert_allclose(reconstructed_positions, result.positions, atol=2e-4)
                np.testing.assert_allclose(reconstructed_rotations, result.rotations, atol=2e-10)
                self.assertEqual(hierarchy.state().shape, (4, STATE_WIDTH))

    def test_cancel_restores_state_on_all_profiles(self):
        for name, ob in self.rigs.items():
            with self.subTest(rig=name):
                before = self.state(ob); calls = []
                def cancel():
                    calls.append(1)
                    return len(calls) == 3
                with self.assertRaises(InterruptedError): sample(ob, 2, 12, cancel_requested=cancel)
                self.assertEqual(self.state(ob), before)

    def test_only_known_frames_read_and_animation_preserved(self):
        from unittest.mock import patch
        from b4artists_ml import body_solver as bs
        ob = self.rigs['boneforge']; root = ob.pose.bones[bs.mapping(ob)['root']]
        for frame, x in ((1, -.1), (2, 0), (7, 8), (12, .5), (13, .6)):
            root.location.x = x; root.keyframe_insert('location', frame=frame)
        bpy.context.scene.frame_set(7, subframe=.25)
        before = self.state(ob); visits = []
        from rig_observations import _frame_set
        original = _frame_set
        def record(scene, frame, **kw):
            visits.append((frame, kw.get('subframe', 0.)))
            return original(scene, frame, **kw)
        try:
            with patch('rig_observations._frame_set', record):
                a = sample(ob, 2, 12)
            self.assertEqual(visits, [(2, 0.), (12, 0.), (1, 0.), (13, 0.), (7, .25)])
            self.assertEqual(self.state(ob), before)
            visits.clear()
            with patch('rig_observations._frame_set', record):
                sample(ob, 2, 12, context=False)
            self.assertEqual(visits, [(2, 0.), (12, 0.), (7, .25)])
            self.assertEqual(self.state(ob), before)
            # Changing a hidden key cannot enter known input when observed values
            # are independently identical; direct capture is checked above.
            self.assertEqual(a.duration, 10/bpy.context.scene.render.fps*bpy.context.scene.render.fps_base)
        finally:
            ob.animation_data.action = None
            root.location.x = 0
            bpy.context.view_layer.update()

    def test_frame_evaluation_failure_restores_state(self):
        from unittest.mock import patch
        ob = self.rigs['boneforge']; before = self.state(ob); calls = []
        from rig_observations import _frame_set
        original = _frame_set
        def fail(scene, frame, **kw):
            calls.append(frame)
            if len(calls) == 2: raise RuntimeError('injected frame evaluation failure')
            return original(scene, frame, **kw)
        with patch('rig_observations._frame_set', fail):
            with self.assertRaisesRegex(RuntimeError, 'injected'): sample(ob, 2, 12)
        self.assertEqual(self.state(ob), before)

    def test_actual_rig_object_transform_invariance(self):
        for name, ob in self.rigs.items():
            with self.subTest(rig=name):
                before = ob.matrix_basis.copy()
                a = sample(ob, 2, 12)
                try:
                    ob.location = (2, -3, .7)
                    ob.rotation_euler = (.2, -.3, .4)
                    ob.scale = (1.7,)*3
                    bpy.context.view_layer.update()
                    source = self.state(ob)
                    b = sample(ob, 2, 12)
                    self.assertEqual(self.state(ob), source)
                    np.testing.assert_allclose(a.features(), b.features(), atol=2e-5)
                finally:
                    ob.matrix_basis = before
                    bpy.context.view_layer.update()

    def test_invalid_joint_frames_rejected(self):
        from mathutils import Matrix
        from rig_observations import _orientation
        for values in (((-1,0,0,0),(0,1,0,0),(0,0,1,0),(0,0,0,1)),
                       ((1,.2,0,0),(0,1,0,0),(0,0,1,0),(0,0,0,1)),
                       ((0,0,0,0),(0,1,0,0),(0,0,1,0),(0,0,0,1))):
            with self.assertRaises(ValueError): _orientation(Matrix(values))

    def test_active_solver_owner_rejected(self):
        from b4artists_ml.body_solver import Session
        ob = self.rigs['boneforge']; session = Session(ob)
        try:
            before = self.state(ob)
            with self.assertRaisesRegex(ValueError, 'active'): sample(ob, 2, 12)
            self.assertEqual(self.state(ob), before)
        finally: session.cancel()

    def test_all_active_workflow_flags_rejected(self):
        ob = self.rigs['boneforge']
        active = (
            ('quadruped_payload', 'active'),
            ('temporal_running', True),
            ('body_running', True),
            ('body_live', True),
            ('contact_running', True),
            ('contact_suggest_running', True),
            ('flight_running', True),
            ('secondary_running', True),
            ('cleanup_running', True),
        )
        for attribute, value in active:
            with self.subTest(workflow=attribute):
                before = self.state(ob)
                setattr(ob.b4ml, attribute, value)
                try:
                    with self.assertRaisesRegex(ValueError, 'active'):
                        sample(ob, 2, 12)
                    self.assertEqual(self.state(ob), before)
                finally:
                    setattr(ob.b4ml, attribute, '' if isinstance(value, str) else False)


if __name__ == '__main__': unittest.main()
