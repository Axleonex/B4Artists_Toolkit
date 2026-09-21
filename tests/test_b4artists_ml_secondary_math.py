"""Host-independent secondary-motion stability and boundary tests."""
from pathlib import Path
import os
import sys
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, os.environ.get("B4ML_PACKAGE", str(ROOT)))
from b4artists_ml import secondary_math as sm


class SecondaryMathTests(unittest.TestCase):
    def test_vector_follow_is_finite_stable_and_source_bounded(self):
        frames = np.arange(1.0, 22.0)
        target = np.zeros((len(frames), 3))
        target[4:12, 0] = 1.0
        result = sm.apply_vector_follow(target, frames, dt=1/24, frequency=2.2,
            damping=.35, air_friction=.2, strength=.8, blend_frames=2.)
        self.assertTrue(np.isfinite(result).all())
        np.testing.assert_array_equal(result[[0, -1]], target[[0, -1]])
        self.assertGreater(float(np.max(np.abs(result-target))), .05)
        self.assertLess(float(np.max(np.abs(result))), 1.5)

    def test_hostile_time_steps_remain_finite(self):
        values = np.array([[0., 0.], [10., -10.], [-10., 10.], [0., 0.]])
        for dt in (1/1000, 1/24, 2.0):
            result = sm.follow_vectors(values, [1., 1., 1.], dt=dt,
                frequency=30., damping=0., air_friction=0.)
            self.assertTrue(np.isfinite(result).all())
            self.assertLess(float(np.max(np.abs(result))), 11.)

    def test_quaternion_follow_normalizes_and_preserves_endpoints(self):
        angle = np.linspace(0., 1.8, 13)
        target = np.c_[np.cos(angle/2), np.zeros((13, 2)), np.sin(angle/2)]
        envelope = sm.boundary_envelope(np.arange(13.), 3.)
        result = sm.follow_quaternions(target, np.ones(12), dt=1/24,
            frequency=2., damping=.4, air_friction=.1, strength=.75, envelope=envelope)
        np.testing.assert_allclose(np.linalg.norm(result, axis=1), 1., atol=1e-12)
        np.testing.assert_allclose(result[[0, -1]], target[[0, -1]], atol=1e-12)
        self.assertGreater(float(np.max(np.linalg.norm(result-target, axis=1))), .02)

    def test_quaternion_signs_do_not_create_false_turn(self):
        target = np.tile([1., 0., 0., 0.], (5, 1))
        target[2:] *= -1
        result = sm.follow_quaternions(target, np.ones(4), dt=1/24,
            frequency=2., damping=.5, air_friction=.2, strength=1., envelope=np.ones(5))
        self.assertTrue(np.all(np.abs(result[:, 0]) > .999999))

    def test_chain_zero_propagation_matches_independent_followers(self):
        frames = np.arange(13., dtype=float)
        angles = np.linspace(0., 1.4, len(frames))
        first = np.c_[np.cos(angles/2), np.zeros((len(frames), 2)), np.sin(angles/2)]
        second_angles = -.7*angles
        second = np.c_[np.cos(second_angles/2), np.sin(second_angles/2),
                       np.zeros((len(frames), 2))]
        targets = np.stack((first, second), axis=1)
        envelope = sm.priority_envelope(frames, [0., 6., 12.], 2.)
        chain = sm.follow_quaternion_chain(
            targets, np.diff(frames), dt=1/24, frequency=2., damping=.4,
            air_friction=.1, strength=.75, envelope=envelope, propagation=0.)
        independent = np.stack([
            sm.follow_quaternions(targets[:, index], np.diff(frames), dt=1/24,
                frequency=2., damping=.4, air_friction=.1, strength=.75,
                envelope=envelope)
            for index in range(2)
        ], axis=1)
        np.testing.assert_allclose(chain, independent, atol=1e-12)

    def test_chain_propagates_lag_and_preserves_priorities(self):
        frames = np.arange(17., dtype=float)
        angles = .9*np.sin(frames*np.pi/8.)
        base = np.c_[np.cos(angles/2), np.zeros((len(frames), 2)), np.sin(angles/2)]
        targets = np.stack((base, base, base), axis=1)
        envelope = sm.priority_envelope(frames, [0., 8., 16.], 2.)
        uncoupled = sm.follow_quaternion_chain(
            targets, np.diff(frames), dt=1/24, frequency=2., damping=.3,
            air_friction=.1, strength=.9, envelope=envelope, propagation=0.)
        coupled = sm.follow_quaternion_chain(
            targets, np.diff(frames), dt=1/24, frequency=2., damping=.3,
            air_friction=.1, strength=.9, envelope=envelope, propagation=.8)
        self.assertTrue(np.isfinite(coupled).all())
        np.testing.assert_allclose(coupled[[0, 8, 16]], targets[[0, 8, 16]], atol=1e-12)
        self.assertGreater(float(np.max(np.abs(coupled[:, 2]-uncoupled[:, 2]))), .01)
        np.testing.assert_allclose(np.linalg.norm(coupled, axis=2), 1., atol=1e-12)

    def test_forced_chain_transfers_bounded_angular_momentum(self):
        frames = np.arange(9., dtype=float)
        targets = np.tile(np.array((1., 0., 0., 0.)), (len(frames), 3, 1))
        forcing = np.zeros((len(frames), 3, 3), dtype=float)
        forcing[:, 0, 2] = 2.
        envelope = sm.priority_envelope(frames, [0., 4., 8.], 1.)
        result, report = sm.follow_forced_quaternion_chain(
            targets, np.diff(frames), dt=1/24, frequency=1.6, damping=.35,
            air_friction=.1, strength=.9, envelope=envelope, propagation=.8,
            inertias=[2., 1., 3.], angular_accelerations=forcing,
            coupling_passes=2, return_report=True)
        uncoupled = sm.follow_quaternion_chain(
            targets, np.diff(frames), dt=1/24, frequency=1.6, damping=.35,
            air_friction=.1, strength=.9, envelope=envelope, propagation=0.)
        self.assertTrue(np.isfinite(result).all())
        np.testing.assert_allclose(np.linalg.norm(result, axis=2), 1., atol=1e-12)
        np.testing.assert_array_equal(result[[0, 4, 8]], targets[[0, 4, 8]])
        self.assertGreater(float(np.max(np.abs(result-uncoupled))), .001)
        self.assertEqual(report['coupling_passes'], 2)
        self.assertEqual(report['coupling_edges'], 4)
        self.assertEqual(report['coupled_samples'], 8)
        self.assertGreater(report['maximum_internal_angular_impulse'], 0.)
        self.assertLessEqual(report['angular_momentum_residual'], 1e-10)

    def test_forced_chain_validation_fails_closed(self):
        values = np.tile([1., 0., 0., 0.], (4, 2, 1))
        forcing = np.zeros((4, 2, 3))
        common = dict(frame_steps=[1., 1., 1.], dt=1/24, frequency=2.,
                      damping=.5, air_friction=0., strength=1.,
                      envelope=np.ones(4), propagation=.5,
                      angular_accelerations=forcing)
        with self.assertRaisesRegex(ValueError, 'inertias'):
            sm.follow_forced_quaternion_chain(
                values, inertias=[True, 1.], **common)
        with self.assertRaisesRegex(ValueError, 'passes'):
            sm.follow_forced_quaternion_chain(
                values, inertias=[1., 1.], coupling_passes=5, **common)

    def test_chain_validation_fails_closed(self):
        with self.assertRaises(ValueError):
            sm.follow_quaternion_chain(np.zeros((3, 1, 4)), [1., 1.], dt=1/24,
                frequency=2., damping=.5, air_friction=0., strength=1.,
                envelope=np.ones(3), propagation=.5)
        values = np.tile([1., 0., 0., 0.], (3, 2, 1))
        with self.assertRaises(ValueError):
            sm.follow_quaternion_chain(values, [1., 1.], dt=1/24,
                frequency=2., damping=.5, air_friction=0., strength=1.,
                envelope=np.ones(3), propagation=1.1)
        hostile = np.tile([1., 0., 0., 0.], (4, 3, 1)).astype(float)
        hostile[1, :, :] = [0., 1., 0., 0.]
        hostile[2, :, :] = [0., 0., 1., 0.]
        for dt in (1/1000, 1/24, 2.):
            result = sm.follow_quaternion_chain(
                hostile, [1., 1., 1.], dt=dt, frequency=30., damping=0.,
                air_friction=0., strength=1., envelope=np.ones(4),
                propagation=1.)
            self.assertTrue(np.isfinite(result).all())
            np.testing.assert_allclose(np.linalg.norm(result, axis=2), 1., atol=1e-12)

    def test_pairwise_momentum_transfer_conserves_total_momentum(self):
        velocities = np.array([[0., 0., 0.], [4., 0., 0.], [-1., 2., 0.]])
        masses = np.array([2., 1., 3.])
        before = np.sum(masses[:, None] * velocities, axis=0)
        result, report = sm.transfer_pairwise_momentum(velocities, masses, .8)
        after = np.sum(masses[:, None] * result, axis=0)
        np.testing.assert_allclose(after, before, atol=1e-12)
        self.assertLessEqual(report['momentum_residual'], 1e-12)
        self.assertGreater(report['maximum_internal_impulse'], 0.)

    def test_alternating_chain_momentum_passes_conserve_and_reduce_directional_bias(self):
        velocities = np.array([
            [0., 0., 0.], [4., 0., 0.], [-1., 2., 0.], [2., -1., 1.],
            [-3., 1., .5],
        ])
        masses = np.array([2., 1., 3., .75, 1.5])
        before = np.sum(masses[:, None] * velocities, axis=0)
        one, one_report = sm.transfer_chain_momentum(velocities, masses, .8, passes=1)
        multi, multi_report = sm.transfer_chain_momentum(velocities, masses, .8, passes=3)
        np.testing.assert_allclose(np.sum(masses[:, None] * one, axis=0), before, atol=1e-12)
        np.testing.assert_allclose(np.sum(masses[:, None] * multi, axis=0), before, atol=1e-12)
        self.assertEqual(one_report['coupling_passes'], 1)
        self.assertEqual(multi_report['coupling_passes'], 3)
        self.assertEqual(multi_report['coupling_edges'], 12)
        self.assertLessEqual(multi_report['momentum_residual'], 1e-12)
        self.assertLess(float(np.linalg.norm(multi[-1]-multi[-2])),
                        float(np.linalg.norm(one[-1]-one[-2])))
        for invalid in (0, 5, True, 1.5):
            with self.subTest(invalid=invalid):
                with self.assertRaisesRegex(ValueError, 'passes'):
                    sm.transfer_chain_momentum(velocities, masses, .8, passes=invalid)

    def test_world_vector_chain_is_bounded_and_keeps_priority_samples(self):
        frames = np.arange(9., dtype=float)
        targets = np.zeros((len(frames), 2, 3), dtype=float)
        targets[:, 0, 0] = np.sin(frames*.7)
        targets[:, 1, 0] = np.sin(frames*.7) + .35
        envelope = sm.priority_envelope(frames, [0., 4., 8.], 1.)
        result, report = sm.follow_world_vector_chain(
            targets, np.diff(frames), dt=1/24, frequency=2., damping=.35,
            air_friction=.2, strength=.9, envelope=envelope, propagation=.8,
            masses=[2., 1.], accelerations=[[0., 0., -4.], [0., 0., -2.]])
        self.assertTrue(np.isfinite(result).all())
        np.testing.assert_array_equal(result[[0, 4, 8]], targets[[0, 4, 8]])
        self.assertGreater(float(np.max(np.linalg.norm(result-targets, axis=2))), .001)
        self.assertLessEqual(report['momentum_conservation_error'], 1e-10)
        self.assertEqual(report['coupled_samples'], len(frames)-1)

    def test_world_vector_chain_exposes_bounded_multi_pass_coupling(self):
        frames = np.arange(10., dtype=float)
        targets = np.zeros((len(frames), 5, 3), dtype=float)
        targets[:, :, 0] = np.arange(5, dtype=float) * .24
        targets[:, :, 1] = np.sin(frames[:, None] * .35 + np.arange(5)[None, :]) * .08
        envelope = sm.priority_envelope(frames, [0., 5., 9.], 1.)
        result, report = sm.follow_world_vector_chain(
            targets, np.diff(frames), dt=1/24, frequency=2., damping=.35,
            air_friction=.2, strength=.9, envelope=envelope, propagation=.85,
            coupling_passes=3, masses=[2., 1., 3., .75, 1.5],
            accelerations=[[0., 0., -4.], [0., 0., -2.], [0., 0., -1.],
                           [0., 0., -3.], [0., 0., -1.]])
        self.assertTrue(np.isfinite(result).all())
        np.testing.assert_array_equal(result[[0, 5, 9]], targets[[0, 5, 9]])
        self.assertEqual(report['coupling_passes'], 3)
        self.assertEqual(report['coupling_edges'], 12)
        self.assertLessEqual(report['momentum_conservation_error'], 1e-10)

    def test_world_vector_chain_resolves_static_planar_collision(self):
        frames = np.arange(9., dtype=float)
        targets = np.zeros((len(frames), 2, 3), dtype=float)
        targets[:, :, 0] = [[.1, .35]] * len(frames)
        targets[:, :, 2] = -.2
        targets[[0, 4, 8], :, 2] = .2
        envelope = sm.priority_envelope(frames, [0., 4., 8.], 1.)
        triangle = [[[-1., -1., 0.], [1., -1., 0.], [0., 1., 0.]]]
        result, report = sm.follow_world_vector_chain(
            targets, np.diff(frames), dt=1/24, frequency=2., damping=.35,
            air_friction=.2, strength=.9, envelope=envelope, propagation=.8,
            masses=[2., 1.], accelerations=[[0., 0., -4.], [0., 0., -2.]],
            collision_point=(0., 0., 0.), collision_normal=(0., 0., 1.),
            clearance=.01, restitution=.2, surface_friction=.4,
            collision_triangles=triangle)
        self.assertTrue(np.isfinite(result).all())
        np.testing.assert_array_equal(result[[0, 4, 8]], targets[[0, 4, 8]])
        self.assertGreater(report['collision_samples'], 0)
        self.assertGreater(report['max_raw_penetration'], 0.)
        self.assertLessEqual(report['max_penetration_after'], 1e-12)
        self.assertLessEqual(report['momentum_conservation_error'], 1e-10)

    def test_world_vector_chain_resolves_static_sphere_collision(self):
        frames = np.arange(9., dtype=float)
        targets = np.zeros((len(frames), 2, 3), dtype=float)
        targets[:, :, 0] = [[.05, .25]] * len(frames)
        targets[:, :, 2] = -.2
        targets[[0, 4, 8], :, 2] = .6
        envelope = sm.priority_envelope(frames, [0., 4., 8.], 1.)
        result, report = sm.follow_world_vector_chain(
            targets, np.diff(frames), dt=1/24, frequency=2., damping=.35,
            air_friction=.2, strength=.9, envelope=envelope, propagation=.8,
            masses=[2., 1.], accelerations=[[0., 0., -4.], [0., 0., -2.]],
            collision_sphere_center=(.05, 0., 0.), collision_sphere_radius=.25,
            clearance=.01, restitution=.2, surface_friction=.4)
        self.assertTrue(np.isfinite(result).all())
        np.testing.assert_array_equal(result[[0, 4, 8]], targets[[0, 4, 8]])
        self.assertGreater(report['collision_samples'], 0)
        self.assertGreater(report['max_raw_penetration'], 0.)
        self.assertLessEqual(report['max_penetration_after'], 1e-12)
        self.assertLessEqual(report['momentum_conservation_error'], 1e-10)

    def test_world_vector_chain_resolves_deterministic_sphere_sets(self):
        frames = np.arange(9., dtype=float)
        targets = np.zeros((len(frames), 3, 3), dtype=float)
        targets[:, :, 0] = [[-.2, .05, .3]] * len(frames)
        targets[:, :, 2] = -.2
        targets[[0, 4, 8], :, 2] = .65
        envelope = sm.priority_envelope(frames, [0., 4., 8.], 1.)
        spheres = [((-.2, 0., 0.), .25), ((.3, 0., 0.), .25)]
        kwargs = dict(
            frame_steps=np.diff(frames), dt=1/24, frequency=2., damping=.35,
            air_friction=.2, strength=.9, envelope=envelope, propagation=.85,
            masses=[2., 1., 3.],
            accelerations=[[0., 0., -4.], [0., 0., -2.], [0., 0., -1.]],
            clearance=.01, restitution=.2, surface_friction=.4)
        result, report = sm.follow_world_vector_chain(
            targets, collision_spheres=spheres, **kwargs)
        reversed_result, reversed_report = sm.follow_world_vector_chain(
            targets, collision_spheres=list(reversed(spheres)), **kwargs)
        np.testing.assert_array_equal(result, reversed_result)
        np.testing.assert_array_equal(result[[0, 4, 8]], targets[[0, 4, 8]])
        self.assertTrue(np.isfinite(result).all())
        self.assertEqual(report['collision_collider_count'], 2)
        self.assertEqual(report['collision_collider_count'], reversed_report['collision_collider_count'])
        self.assertGreater(report['collision_samples'], 0)
        self.assertGreater(report['max_raw_penetration'], 0.)
        self.assertLessEqual(report['max_penetration_after'], 1e-12)
        self.assertLessEqual(report['momentum_conservation_error'], 1e-10)
        for center, radius in spheres:
            separation = np.linalg.norm(
                result-np.asarray(center), axis=2)-radius-.01
            self.assertGreaterEqual(float(np.min(separation)), -1e-12)

    def test_world_vector_chain_resolves_compound_support_and_static_spheres(self):
        frames = np.arange(9., dtype=float)
        targets = np.zeros((len(frames), 3, 3), dtype=float)
        targets[:, :, 0] = [[-.2, .05, .3]] * len(frames)
        targets[:, :, 2] = -1.0
        targets[[0, 4, 8], :, 2] = .65
        envelope = sm.priority_envelope(frames, [0., 4., 8.], 1.)
        spheres = [((.05, 0., -.8), .4), ((.8, 0., -.8), .2)]
        kwargs = dict(
            frame_steps=np.diff(frames), dt=1/24, frequency=2., damping=.35,
            air_friction=.2, strength=.9, envelope=envelope, propagation=.85,
            masses=[2., 1., 3.],
            accelerations=[[0., 0., -4.], [0., 0., -2.], [0., 0., -1.]],
            clearance=.01, restitution=.2, surface_friction=.4)
        result, report = sm.follow_world_vector_chain(
            targets, np.diff(frames), dt=1/24, frequency=2., damping=.35,
            air_friction=.2, strength=.9, envelope=envelope, propagation=.85,
            masses=[2., 1., 3.],
            accelerations=[[0., 0., -4.], [0., 0., -2.], [0., 0., -1.]],
            collision_point=(0., 0., -.5), collision_normal=(0., 0., 1.),
            collision_spheres=spheres, compound_plane_spheres=True,
            clearance=.01, restitution=.2, surface_friction=.4)
        self.assertTrue(np.isfinite(result).all())
        np.testing.assert_array_equal(result[[0, 4, 8]], targets[[0, 4, 8]])
        self.assertTrue(report['collision_plane'])
        self.assertTrue(report['collision_compound'])
        self.assertEqual(report['collision_collider_count'], 3)
        self.assertGreater(report['collision_samples'], 0)
        self.assertGreater(report['max_raw_penetration'], 0.)
        self.assertLessEqual(report['max_penetration_after'], 1e-12)
        self.assertLessEqual(report['momentum_conservation_error'], 1e-10)
        self.assertGreaterEqual(float(np.min(result[:, :, 2] + .5 - .01)), -1e-12)
        for center, radius in spheres:
            separation = np.linalg.norm(
                result-np.asarray(center), axis=2)-radius-.01
            self.assertGreaterEqual(float(np.min(separation)), -1e-12)

        with self.assertRaisesRegex(ValueError, 'planar or spherical'):
            sm.follow_world_vector_chain(
                targets, np.diff(frames), dt=1/24, frequency=2., damping=.35,
                air_friction=.2, strength=.9, envelope=envelope, propagation=.85,
                masses=[2., 1., 3.],
                accelerations=[[0., 0., -4.], [0., 0., -2.], [0., 0., -1.]],
                collision_point=(0., 0., -.5), collision_normal=(0., 0., 1.),
                collision_spheres=spheres,
                clearance=.01, restitution=.2, surface_friction=.4)

        moving = []
        for offset, radius in ((-.2, .2), (.3, .23)):
            centers = np.zeros((len(frames), 3), dtype=float)
            centers[:, 0] = offset + np.linspace(-.08, .08, len(frames))
            moving.append((centers, np.linspace(radius, radius+.03, len(frames))))
        moving_result, moving_report = sm.follow_world_vector_chain(
            targets, collision_sphere_trajectories=moving, **kwargs)
        self.assertEqual(moving_report['collision_collider_count'], 2)
        self.assertGreater(moving_report['collision_samples'], 0)
        self.assertLessEqual(moving_report['max_penetration_after'], 1e-12)
        for centers, radii in moving:
            separation = (np.linalg.norm(
                moving_result-centers[:, None, :], axis=2)
                - radii[:, None]-.01)
            self.assertGreaterEqual(float(np.min(separation)), -1e-12)

    def test_world_vector_chain_resolves_support_and_one_moving_sphere_compound(self):
        frames = np.arange(9., dtype=float)
        targets = np.zeros((len(frames), 2, 3), dtype=float)
        targets[:, :, 0] = [[.05, .25]] * len(frames)
        targets[:, :, 2] = -.3
        targets[[0, 4, 8], :, 2] = .4
        centers = np.zeros((len(frames), 3), dtype=float)
        centers[:, 0] = np.linspace(-.12, .12, len(frames))
        centers[:, 2] = -.5
        radii = np.linspace(.28, .34, len(frames))
        envelope = sm.priority_envelope(frames, [0., 4., 8.], 1.)
        result, report = sm.follow_world_vector_chain(
            targets, np.diff(frames), dt=1/24, frequency=2., damping=.35,
            air_friction=.2, strength=.9, envelope=envelope, propagation=.8,
            masses=[2., 1.], accelerations=np.zeros((2, 3)),
            collision_point=(0., 0., -.5), collision_normal=(0., 0., 1.),
            collision_sphere_trajectories=[(centers, radii)],
            collision_sphere_continuous=True, compound_plane_spheres=True,
            clearance=.01, restitution=.2, surface_friction=.4)
        self.assertTrue(np.isfinite(result).all())
        np.testing.assert_array_equal(result[[0, 4, 8]], targets[[0, 4, 8]])
        self.assertTrue(report['collision_plane'])
        self.assertTrue(report['collision_compound'])
        self.assertEqual(report['collision_collider_count'], 2)
        self.assertGreater(report['collision_samples'], 0)
        self.assertGreater(report['continuous_collision_samples'], 0)
        self.assertGreater(report['max_raw_penetration'], 0.)
        self.assertLessEqual(report['max_penetration_after'], 1e-12)
        self.assertLessEqual(report['momentum_conservation_error'], 1e-10)
        self.assertGreaterEqual(float(np.min(result[:, :, 2] + .5 - .01)), -1e-12)
        separation = np.linalg.norm(
            result-centers[:, None, :], axis=2)-radii[:, None]-.01
        self.assertGreaterEqual(float(np.min(separation)), -1e-12)

        second_centers = centers.copy()
        second_centers[:, 0] += .8
        third_centers = centers.copy()
        third_centers[:, 0] += 1.6
        fourth_centers = centers.copy()
        fourth_centers[:, 0] += 2.4
        with self.assertRaisesRegex(ValueError, 'one to three moving spheres'):
            sm.follow_world_vector_chain(
                targets, np.diff(frames), dt=1/24, frequency=2., damping=.35,
                air_friction=.2, strength=.9, envelope=envelope, propagation=.8,
                masses=[2., 1.], accelerations=np.zeros((2, 3)),
                collision_point=(0., 0., -.5), collision_normal=(0., 0., 1.),
                collision_sphere_trajectories=[(centers, radii),
                                               (second_centers, radii),
                                               (third_centers, radii),
                                               (fourth_centers, radii)],
                compound_plane_spheres=True, clearance=.01,
                restitution=.2, surface_friction=.4)

    def test_world_vector_chain_resolves_support_and_two_moving_spheres_compound(self):
        frames = np.arange(9., dtype=float)
        targets = np.zeros((len(frames), 2, 3), dtype=float)
        targets[:, :, 0] = [[-.15, .15]] * len(frames)
        targets[:, :, 2] = -.3
        targets[[0, 4, 8], :, 2] = .4
        first_centers = np.zeros((len(frames), 3), dtype=float)
        first_centers[:, 0] = np.linspace(-.15, .15, len(frames))
        first_centers[:, 2] = -.5
        second_centers = np.zeros((len(frames), 3), dtype=float)
        second_centers[:, 0] = np.linspace(.55, .85, len(frames))
        second_centers[:, 2] = -.5
        first_radii = np.linspace(.24, .30, len(frames))
        second_radii = np.linspace(.20, .26, len(frames))
        moving = [(first_centers, first_radii),
                  (second_centers, second_radii)]
        envelope = sm.priority_envelope(frames, [0., 4., 8.], 1.)
        kwargs = dict(
            frame_steps=np.diff(frames), dt=1/24, frequency=2., damping=.35,
            air_friction=.2, strength=.9, envelope=envelope, propagation=.8,
            masses=[2., 1.], accelerations=np.zeros((2, 3)),
            collision_point=(0., 0., -.5), collision_normal=(0., 0., 1.),
            collision_sphere_continuous=True, compound_plane_spheres=True,
            clearance=.01, restitution=.2, surface_friction=.4)
        result, report = sm.follow_world_vector_chain(
            targets, collision_sphere_trajectories=moving, **kwargs)
        reversed_result, reversed_report = sm.follow_world_vector_chain(
            targets, collision_sphere_trajectories=list(reversed(moving)), **kwargs)
        np.testing.assert_array_equal(result, reversed_result)
        self.assertTrue(np.isfinite(result).all())
        np.testing.assert_array_equal(result[[0, 4, 8]], targets[[0, 4, 8]])
        self.assertTrue(report['collision_plane'])
        self.assertTrue(report['collision_compound'])
        self.assertEqual(report['collision_collider_count'], 3)
        self.assertEqual(report['collision_collider_count'],
                         reversed_report['collision_collider_count'])
        self.assertGreater(report['collision_samples'], 0)
        self.assertGreater(report['continuous_collision_samples'], 0)
        self.assertLessEqual(report['max_penetration_after'], 1e-12)
        self.assertLessEqual(report['momentum_conservation_error'], 1e-10)
        self.assertGreaterEqual(float(np.min(result[:, :, 2] + .5 - .01)), -1e-12)
        for centers, radii in moving:
            separation = (np.linalg.norm(
                result-centers[:, None, :], axis=2)-radii[:, None]-.01)
            self.assertGreaterEqual(float(np.min(separation)), -1e-12)

    def test_world_vector_chain_resolves_two_moving_spheres_with_static_set_compound(self):
        frames = np.arange(9., dtype=float)
        targets = np.zeros((len(frames), 2, 3), dtype=float)
        targets[:, :, 0] = [[-.15, .15]] * len(frames)
        targets[:, :, 2] = -.3
        targets[[0, 4, 8], :, 2] = .4
        first_centers = np.zeros((len(frames), 3), dtype=float)
        first_centers[:, 0] = np.linspace(-.15, .15, len(frames))
        first_centers[:, 2] = -.5
        second_centers = np.zeros((len(frames), 3), dtype=float)
        second_centers[:, 0] = np.linspace(.55, .85, len(frames))
        second_centers[:, 2] = -.5
        first_radii = np.linspace(.24, .30, len(frames))
        second_radii = np.linspace(.20, .26, len(frames))
        moving = [(first_centers, first_radii),
                  (second_centers, second_radii)]
        static_spheres = [((1.05, 0., -.5), .15)]
        envelope = sm.priority_envelope(frames, [0., 4., 8.], 1.)
        result, report = sm.follow_world_vector_chain(
            targets, np.diff(frames), dt=1/24, frequency=2., damping=.35,
            air_friction=.2, strength=.9, envelope=envelope, propagation=.8,
            masses=[2., 1.], accelerations=np.zeros((2, 3)),
            collision_point=(0., 0., -.5), collision_normal=(0., 0., 1.),
            collision_spheres=static_spheres,
            collision_sphere_trajectories=moving,
            collision_sphere_continuous=True, compound_plane_spheres=True,
            clearance=.01, restitution=.2, surface_friction=.4)
        self.assertTrue(np.isfinite(result).all())
        np.testing.assert_array_equal(result[[0, 4, 8]], targets[[0, 4, 8]])
        self.assertTrue(report['collision_plane'])
        self.assertTrue(report['collision_compound'])
        self.assertEqual(report['collision_collider_count'], 4)
        self.assertGreater(report['collision_samples'], 0)
        self.assertGreater(report['continuous_collision_samples'], 0)
        self.assertLessEqual(report['max_penetration_after'], 1e-12)
        self.assertLessEqual(report['momentum_conservation_error'], 1e-10)
        self.assertGreaterEqual(float(np.min(result[:, :, 2] + .5 - .01)), -1e-12)
        for center, radius in static_spheres:
            separation = np.linalg.norm(
                result-np.asarray(center), axis=2)-radius-.01
            self.assertGreaterEqual(float(np.min(separation)), -1e-12)
        for centers, radii in moving:
            separation = (np.linalg.norm(
                result-centers[:, None, :], axis=2)-radii[:, None]-.01)
            self.assertGreaterEqual(float(np.min(separation)), -1e-12)

    def test_world_vector_chain_resolves_three_moving_spheres_with_static_set_compound(self):
        frames = np.arange(9., dtype=float)
        targets = np.zeros((len(frames), 3, 3), dtype=float)
        targets[:, :, 0] = [[-1., 0., 1.]] * len(frames)
        targets[:, :, 2] = -.3
        targets[[0, 4, 8], :, 2] = .4
        moving = []
        for center_x in (-1., 0., 1.):
            centers = np.zeros((len(frames), 3), dtype=float)
            centers[:, 0] = center_x + np.linspace(-.08, .08, len(frames))
            centers[:, 2] = -.5
            moving.append((centers, np.linspace(.24, .30, len(frames))))
        static_spheres = [((1.6, 0., -.5), .15)]
        envelope = sm.priority_envelope(frames, [0., 4., 8.], 1.)
        kwargs = dict(
            frame_steps=np.diff(frames), dt=1/24, frequency=2., damping=.35,
            air_friction=.2, strength=.9, envelope=envelope, propagation=.8,
            masses=[2., 1., 3.], accelerations=np.zeros((3, 3)),
            collision_point=(0., 0., -.5), collision_normal=(0., 0., 1.),
            collision_spheres=static_spheres,
            collision_sphere_continuous=True, compound_plane_spheres=True,
            clearance=.01, restitution=.2, surface_friction=.4)
        result, report = sm.follow_world_vector_chain(
            targets, collision_sphere_trajectories=moving, **kwargs)
        reversed_result, reversed_report = sm.follow_world_vector_chain(
            targets, collision_sphere_trajectories=list(reversed(moving)), **kwargs)
        np.testing.assert_array_equal(result, reversed_result)
        self.assertTrue(np.isfinite(result).all())
        np.testing.assert_array_equal(result[[0, 4, 8]], targets[[0, 4, 8]])
        self.assertTrue(report['collision_plane'])
        self.assertTrue(report['collision_compound'])
        self.assertEqual(report['collision_collider_count'], 5)
        self.assertEqual(report['collision_collider_count'],
                         reversed_report['collision_collider_count'])
        self.assertGreater(report['collision_samples'], 0)
        self.assertGreater(report['continuous_collision_samples'], 0)
        self.assertLessEqual(report['max_penetration_after'], 1e-12)
        self.assertLessEqual(report['momentum_conservation_error'], 1e-10)
        self.assertGreaterEqual(float(np.min(result[:, :, 2] + .5 - .01)), -1e-12)
        for center, radius in static_spheres:
            separation = (np.linalg.norm(result-np.asarray(center), axis=2)
                          - radius-.01)
            self.assertGreaterEqual(float(np.min(separation)), -1e-12)
        for centers, radii in moving:
            separation = (np.linalg.norm(result-centers[:, None, :], axis=2)
                          - radii[:, None]-.01)
            self.assertGreaterEqual(float(np.min(separation)), -1e-12)

    def test_world_vector_chain_resolves_static_sphere_set_and_capsule_compound(self):
        frames = np.arange(9., dtype=float)
        targets = np.zeros((len(frames), 3, 3), dtype=float)
        targets[:, :, 0] = [[-.2, .05, .3]] * len(frames)
        targets[:, :, 2] = -1.0
        targets[[0, 4, 8], :, 2] = .65
        envelope = sm.priority_envelope(frames, [0., 4., 8.], 1.)
        spheres = [((.3, 0., -.8), .3), ((1.0, 0., -.8), .15)]
        result, report = sm.follow_world_vector_chain(
            targets, np.diff(frames), dt=1/24, frequency=2., damping=.35,
            air_friction=.2, strength=.9, envelope=envelope, propagation=.85,
            masses=[2., 1., 3.],
            accelerations=[[0., 0., -4.], [0., 0., -2.], [0., 0., -1.]],
            collision_point=(0., 0., -.5), collision_normal=(0., 0., 1.),
            collision_spheres=spheres, compound_plane_spheres=True,
            collision_capsule_start=(-.2, 0., -1.1),
            collision_capsule_end=(-.2, 0., -.5),
            collision_capsule_radius=.18,
            compound_static_capsule=True,
            clearance=.01, restitution=.2, surface_friction=.4)
        self.assertTrue(np.isfinite(result).all())
        np.testing.assert_array_equal(result[[0, 4, 8]], targets[[0, 4, 8]])
        self.assertTrue(report['collision_plane'])
        self.assertTrue(report['collision_compound'])
        self.assertTrue(report['collision_compound_capsule'])
        self.assertEqual(report['collision_collider_count'], 4)
        self.assertGreater(report['collision_samples'], 0)
        self.assertGreater(report['max_raw_penetration'], 0.)
        self.assertLessEqual(report['max_penetration_after'], 1e-8)
        self.assertLessEqual(report['momentum_conservation_error'], 1e-10)
        self.assertGreaterEqual(float(np.min(result[:, :, 2] + .5 - .01)), -1e-12)
        for center, radius in spheres:
            separation = np.linalg.norm(
                result-np.asarray(center), axis=2)-radius-.01
            self.assertGreaterEqual(float(np.min(separation)), -1e-10)

        with self.assertRaisesRegex(ValueError, 'static support plane and static spheres'):
            sm.follow_world_vector_chain(
                targets, np.diff(frames), dt=1/24, frequency=2., damping=.35,
                air_friction=.2, strength=.9, envelope=envelope, propagation=.85,
                masses=[2., 1., 3.],
                accelerations=np.zeros((3, 3)),
                collision_point=(0., 0., -.5), collision_normal=(0., 0., 1.),
                collision_capsule_start=(-.2, 0., -1.1),
                collision_capsule_end=(-.2, 0., -.5),
                collision_capsule_radius=.18,
                compound_static_capsule=True)

        with self.assertRaisesRegex(ValueError, 'only a static capsule'):
            sm.follow_world_vector_chain(
                targets, np.diff(frames), dt=1/24, frequency=2., damping=.35,
                air_friction=.2, strength=.9, envelope=envelope, propagation=.85,
                masses=[2., 1., 3.],
                accelerations=np.zeros((3, 3)),
                collision_point=(0., 0., -.5), collision_normal=(0., 0., 1.),
                collision_spheres=spheres, compound_plane_spheres=True,
                collision_capsule_start=(-.2, 0., -1.1),
                collision_capsule_end=(-.2, 0., -.5),
                collision_capsule_radius=.18,
                compound_static_capsule=True, collision_capsule_continuous=True)

    def test_world_vector_chain_resolves_static_spheres_and_moving_capsule_compound(self):
        frames = np.arange(9., dtype=float)
        targets = np.zeros((len(frames), 3, 3), dtype=float)
        targets[:, :, 0] = [[-.2, .05, .3]] * len(frames)
        targets[:, :, 2] = -1.0
        targets[[0, 4, 8], :, 2] = .65
        envelope = sm.priority_envelope(frames, [0., 4., 8.], 1.)
        spheres = [((.3, 0., -.8), .3), ((1.0, 0., -.8), .15)]
        offsets = np.linspace(-.24, .24, len(frames))
        starts = np.column_stack((offsets, np.zeros(len(frames)),
                                  np.full(len(frames), -1.1)))
        ends = np.column_stack((offsets, np.zeros(len(frames)),
                                np.full(len(frames), -.5)))
        radii = np.linspace(.18, .24, len(frames))
        result, report = sm.follow_world_vector_chain(
            targets, np.diff(frames), dt=1/24, frequency=2., damping=.35,
            air_friction=.2, strength=.9, envelope=envelope, propagation=.85,
            masses=[2., 1., 3.],
            accelerations=[[0., 0., -4.], [0., 0., -2.], [0., 0., -1.]],
            collision_point=(0., 0., -.5), collision_normal=(0., 0., 1.),
            collision_spheres=spheres, compound_plane_spheres=True,
            collision_capsule_trajectories=(starts, ends, radii),
            collision_capsule_continuous=True, compound_moving_capsule=True,
            clearance=.01, restitution=.2, surface_friction=.4)
        self.assertTrue(np.isfinite(result).all())
        np.testing.assert_array_equal(result[[0, 4, 8]], targets[[0, 4, 8]])
        self.assertTrue(report['collision_plane'])
        self.assertTrue(report['collision_compound'])
        self.assertTrue(report['collision_compound_capsule'])
        self.assertEqual(report['collision_collider_count'], 4)
        self.assertGreater(report['collision_samples'], 0)
        self.assertGreater(report['continuous_collision_samples'], 0)
        self.assertGreater(report['max_raw_penetration'], 0.)
        self.assertLessEqual(report['max_penetration_after'], 1e-8)
        self.assertLessEqual(report['momentum_conservation_error'], 1e-10)
        self.assertGreaterEqual(float(np.min(result[:, :, 2] + .5 - .01)), -1e-12)
        for center, radius in spheres:
            separation = np.linalg.norm(
                result-np.asarray(center), axis=2)-radius-.01
            self.assertGreaterEqual(float(np.min(separation)), -1e-10)
        for sample_index, points in enumerate(result):
            closest = np.asarray([
                sm._capsule_closest(point, starts[sample_index], ends[sample_index])
                for point in points])
            separation = np.linalg.norm(points-closest, axis=1)-radii[sample_index]-.01
            self.assertGreaterEqual(float(np.min(separation)), -1e-10)

        with self.assertRaisesRegex(ValueError, 'moving compound capsule requires'):
            sm.follow_world_vector_chain(
                targets, np.diff(frames), dt=1/24, frequency=2., damping=.35,
                air_friction=.2, strength=.9, envelope=envelope, propagation=.85,
                masses=[2., 1., 3.], accelerations=np.zeros((3, 3)),
                collision_point=(0., 0., -.5), collision_normal=(0., 0., 1.),
                collision_capsule_trajectories=(starts, ends, radii),
                compound_plane_spheres=True, compound_moving_capsule=True,
                clearance=.01, restitution=.2, surface_friction=.4)
    def test_world_vector_chain_resolves_static_mesh_compound(self):
        frames = np.arange(9., dtype=float)
        targets = np.zeros((len(frames), 3, 3), dtype=float)
        targets[:, :, 0] = [[.5, .55, .45]] * len(frames)
        targets[:, :, 2] = -.4
        targets[[0, 4, 8], :, 2] = .65
        envelope = sm.priority_envelope(frames, [0., 4., 8.], 1.)
        spheres = [((-.7, 0., -.4), .15), ((1.7, 0., -.4), .15)]
        mesh = [
            [[.25, -.25, -.8], [.75, -.25, -.8], [.75, .25, -.8]],
            [[.25, -.25, -.8], [.75, .25, -.8], [.25, .25, -.8]],
            [[.25, -.25, -.2], [.75, .25, -.2], [.75, -.25, -.2]],
            [[.25, -.25, -.2], [.25, .25, -.2], [.75, .25, -.2]],
            [[.25, -.25, -.8], [.25, .25, -.8], [.25, .25, -.2]],
            [[.25, -.25, -.8], [.25, .25, -.2], [.25, -.25, -.2]],
            [[.75, -.25, -.8], [.75, -.25, -.2], [.75, .25, -.2]],
            [[.75, -.25, -.8], [.75, .25, -.2], [.75, .25, -.8]],
            [[.25, -.25, -.8], [.25, -.25, -.2], [.75, -.25, -.2]],
            [[.25, -.25, -.8], [.75, -.25, -.2], [.75, -.25, -.8]],
            [[.25, .25, -.8], [.75, .25, -.8], [.75, .25, -.2]],
            [[.25, .25, -.8], [.75, .25, -.2], [.25, .25, -.2]],
        ]
        result, report = sm.follow_world_vector_chain(
            targets, np.diff(frames), dt=1/24, frequency=2., damping=.35,
            air_friction=.2, strength=.9, envelope=envelope, propagation=.85,
            masses=[2., 1., 3.],
            accelerations=[[0., 0., -4.], [0., 0., -2.], [0., 0., -1.]],
            collision_point=(0., 0., -1.), collision_normal=(0., 0., 1.),
            collision_spheres=spheres, compound_plane_spheres=True,
            collision_mesh_triangles=mesh, collision_mesh_closed=True,
            compound_static_mesh=True,
            clearance=.01, restitution=.2, surface_friction=.4)
        self.assertTrue(np.isfinite(result).all())
        np.testing.assert_array_equal(result[[0, 4, 8]], targets[[0, 4, 8]])
        self.assertTrue(report['collision_plane'])
        self.assertTrue(report['collision_compound'])
        self.assertTrue(report['collision_compound_mesh'])
        self.assertEqual(report['collision_collider_count'], 4)
        self.assertGreater(report['collision_samples'], 0)
        self.assertGreater(report['max_raw_penetration'], 0.)
        self.assertLessEqual(report['max_penetration_after'], 1e-8)
        self.assertLessEqual(report['momentum_conservation_error'], 1e-10)
        for sample in result:
            for point in sample:
                state = sm.mesh_collision_state(point, mesh, .01, True)
                self.assertLessEqual(max(0., float(state[3])), 1e-8)
        with self.assertRaisesRegex(ValueError, 'static closed mesh, support plane'):
            sm.follow_world_vector_chain(
                targets, np.diff(frames), dt=1/24, frequency=2., damping=.35,
                air_friction=.2, strength=.9, envelope=envelope, propagation=.85,
                masses=[2., 1., 3.], accelerations=np.zeros((3, 3)),
                collision_mesh_triangles=mesh, compound_static_mesh=True)

    def test_world_vector_chain_resolves_moving_sphere_collision(self):
        frames = np.arange(9., dtype=float)
        targets = np.zeros((len(frames), 2, 3), dtype=float)
        targets[:, :, 0] = [[.05, .25]] * len(frames)
        targets[[0, 4, 8], :, 0] = .8
        centers = np.zeros((len(frames), 3), dtype=float)
        centers[:, 0] = np.linspace(-.15, .15, len(frames))
        radii = np.linspace(.2, .3, len(frames))
        envelope = sm.priority_envelope(frames, [0., 4., 8.], 2.)
        result, report = sm.follow_world_vector_chain(
            targets, np.diff(frames), dt=1/24, frequency=2., damping=.35,
            air_friction=.2, strength=.9, envelope=envelope, propagation=.8,
            masses=[2., 1.], accelerations=np.zeros((2, 3)),
            collision_sphere_trajectories=[(centers, radii)],
            clearance=.01, restitution=.2, surface_friction=.4)
        self.assertTrue(np.isfinite(result).all())
        np.testing.assert_allclose(result[[0, 4, 8]], targets[[0, 4, 8]], atol=1e-12)
        self.assertGreater(report['collision_samples'], 0)
        self.assertGreater(report['max_raw_penetration'], 0.)
        self.assertLessEqual(report['max_penetration_after'], 1e-12)
        self.assertLessEqual(report['momentum_conservation_error'], 1e-10)
        self.assertTrue(np.any((envelope > 0.) & (envelope < 1.)))
        for sample_index, sample in enumerate(result):
            separation = np.linalg.norm(sample-centers[sample_index], axis=1)
            separation -= radii[sample_index]+.01
            self.assertGreaterEqual(float(np.min(separation)), -1e-12)

        constant_radius, _ = sm.follow_world_vector_chain(
            targets, np.diff(frames), dt=1/24, frequency=2., damping=.35,
            air_friction=.2, strength=.9, envelope=envelope, propagation=.8,
            masses=[2., 1.], accelerations=np.zeros((2, 3)),
            collision_sphere_trajectories=[(centers, np.full(len(frames), .2))],
            clearance=.01, restitution=.2, surface_friction=.4)
        static_sphere, static_report = sm.follow_world_vector_chain(
            targets, np.diff(frames), dt=1/24, frequency=2., damping=.35,
            air_friction=.2, strength=.9, envelope=envelope, propagation=.8,
            masses=[2., 1.], accelerations=np.zeros((2, 3)),
            collision_sphere_center=centers[-1], collision_sphere_radius=radii[-1],
            clearance=.01, restitution=.2, surface_friction=.4)
        radius_only, _radius_report = sm.follow_world_vector_chain(
            targets, np.diff(frames), dt=1/24, frequency=2., damping=.35,
            air_friction=.2, strength=.9, envelope=envelope, propagation=.8,
            masses=[2., 1.], accelerations=np.zeros((2, 3)),
            collision_sphere_trajectories=[(
                np.repeat(centers[-1][None, :], len(frames), axis=0), radii)],
            clearance=.01, restitution=.2, surface_friction=.4)
        constant_trajectory, constant_report = sm.follow_world_vector_chain(
            targets, np.diff(frames), dt=1/24, frequency=2., damping=.35,
            air_friction=.2, strength=.9, envelope=envelope, propagation=.8,
            masses=[2., 1.], accelerations=np.zeros((2, 3)),
            collision_sphere_trajectories=[(
                np.repeat(centers[-1][None, :], len(frames), axis=0), radii[-1])],
            clearance=.01, restitution=.2, surface_friction=.4)
        self.assertGreater(float(np.max(np.abs(result-constant_radius))), .01)
        self.assertGreater(float(np.max(np.abs(result-static_sphere))), .01)
        self.assertGreater(float(np.max(np.abs(radius_only-static_sphere))), .01)
        np.testing.assert_allclose(constant_trajectory, static_sphere, atol=1e-12)
        self.assertEqual(constant_report, static_report)

        for tiny in (1e-13, np.nextafter(0.0, 1.0)):
            with self.subTest(tiny_strength=tiny):
                tiny_result, tiny_report = sm.follow_world_vector_chain(
                    targets, np.diff(frames), dt=1/24, frequency=2., damping=.35,
                    air_friction=.2, strength=tiny, envelope=envelope,
                    propagation=.8, masses=[2., 1.],
                    accelerations=np.zeros((2, 3)),
                    collision_sphere_trajectories=[(centers, radii)],
                    clearance=.01, restitution=.2, surface_friction=.4)
                for sample_index, sample in enumerate(tiny_result):
                    separation = np.linalg.norm(
                        sample-centers[sample_index], axis=1)
                    separation -= radii[sample_index]+.01
                    self.assertGreaterEqual(float(np.min(separation)), -1e-12)
                self.assertLessEqual(
                    tiny_report['max_penetration_after'], 1e-12)

        with self.assertRaisesRegex(ValueError, 'static or moving sphere'):
            sm.follow_world_vector_chain(
                targets, np.diff(frames), dt=1/24, frequency=2., damping=.35,
                air_friction=.2, strength=.9, envelope=envelope, propagation=.8,
                masses=[2., 1.], accelerations=np.zeros((2, 3)),
                collision_sphere_center=(0., 0., 0.), collision_sphere_radius=.2,
                collision_sphere_trajectories=[(centers, radii)])
        hostile = (
            [(centers[:-1], radii)],
            [(np.full((len(frames), 3), 'bad', dtype=object), radii)],
            [(centers, np.asarray([.2] * 8 + [float('nan')]))],
            [(centers, np.asarray([.2] * 8 + [1001.]))],
            [(centers, True)],
        )
        for trajectories in hostile:
            with self.subTest(trajectories=repr(trajectories)):
                with self.assertRaises(ValueError):
                    sm.follow_world_vector_chain(
                        targets, np.diff(frames), dt=1/24, frequency=2., damping=.35,
                        air_friction=.2, strength=.9, envelope=envelope,
                        propagation=.8, masses=[2., 1.],
                        accelerations=np.zeros((2, 3)),
                        collision_sphere_trajectories=trajectories)

    def test_world_vector_chain_resolves_continuous_sphere_crossing(self):
        frames = np.arange(4., dtype=float)
        targets = np.zeros((len(frames), 2, 3), dtype=float)
        targets[:, :, 0] = -.5
        envelope = np.ones(len(frames), dtype=float)
        accelerations = np.zeros((2, 3), dtype=float)
        accelerations[:, 0] = 1000.0
        result, report = sm.follow_world_vector_chain(
            targets, np.diff(frames), dt=.1, frequency=2., damping=.35,
            air_friction=.2, strength=.9, envelope=envelope, propagation=.8,
            masses=[2., 1.], accelerations=accelerations,
            collision_sphere_center=(0., 0., 0.), collision_sphere_radius=.2,
            collision_sphere_continuous=True, clearance=.01,
            restitution=.2, surface_friction=.4)
        self.assertTrue(np.isfinite(result).all())
        self.assertGreater(report['continuous_collision_samples'], 0)
        self.assertLessEqual(report['max_penetration_after'], 1e-12)
        self.assertGreaterEqual(
            float(np.min(np.linalg.norm(result, axis=2))), .21 - 1e-12)
        self.assertTrue(np.any(result[1:-1, :, 0] > -.5))

    def test_world_vector_chain_resolves_mixed_static_and_moving_sphere_compound(self):
        frames = np.arange(9., dtype=float)
        targets = np.zeros((len(frames), 2, 3), dtype=float)
        targets[:, :, 0] = [[0.0, .2]] * len(frames)
        targets[:, :, 2] = -1.0
        targets[[0, 4, 8], :, 2] = .65
        envelope = sm.priority_envelope(frames, [0., 4., 8.], 1.)
        static_spheres = [((-.55, 0., -.8), .25), ((.65, 0., -.8), .2)]
        moving_centers = np.zeros((len(frames), 3), dtype=float)
        moving_centers[:, 0] = np.linspace(-.45, .45, len(frames))
        moving_centers[:, 2] = -.8
        moving_radii = np.linspace(.22, .28, len(frames))
        result, report = sm.follow_world_vector_chain(
            targets, np.diff(frames), dt=1/24, frequency=2., damping=.35,
            air_friction=.2, strength=.9, envelope=envelope, propagation=.8,
            masses=[2., 1.], accelerations=[[0., 0., -4.], [0., 0., -2.]],
            collision_point=(0., 0., -.5), collision_normal=(0., 0., 1.),
            collision_spheres=static_spheres,
            collision_sphere_trajectories=[(moving_centers, moving_radii)],
            collision_sphere_continuous=True, compound_plane_spheres=True,
            clearance=.01, restitution=.2, surface_friction=.4)
        self.assertTrue(np.isfinite(result).all())
        np.testing.assert_array_equal(result[[0, 4, 8]], targets[[0, 4, 8]])
        self.assertTrue(report['collision_plane'])
        self.assertTrue(report['collision_compound'])
        self.assertEqual(report['collision_collider_count'], 4)
        self.assertGreater(report['collision_samples'], 0)
        self.assertGreater(report['continuous_collision_samples'], 0)
        self.assertGreater(report['max_raw_penetration'], 0.)
        self.assertLessEqual(report['max_penetration_after'], 1e-8)
        self.assertLessEqual(report['momentum_conservation_error'], 1e-10)
        self.assertGreaterEqual(
            float(np.min(result[:, :, 2] + .5 - .01)), -1e-10)
        for sample_index, sample in enumerate(result):
            for center, radius in static_spheres:
                separation = np.linalg.norm(
                    sample-np.asarray(center), axis=1)-radius-.01
                self.assertGreaterEqual(float(np.min(separation)), -1e-10)
            separation = np.linalg.norm(
                sample-moving_centers[sample_index], axis=1)
            separation -= moving_radii[sample_index]+.01
            self.assertGreaterEqual(float(np.min(separation)), -1e-10)

        with self.assertRaisesRegex(ValueError, 'static or moving sphere'):
            sm.follow_world_vector_chain(
                targets, np.diff(frames), dt=1/24, frequency=2., damping=.35,
                air_friction=.2, strength=.9, envelope=envelope, propagation=.8,
                masses=[2., 1.], accelerations=np.zeros((2, 3)),
                collision_spheres=static_spheres,
                collision_sphere_trajectories=[(moving_centers, moving_radii)],
                collision_sphere_continuous=True, clearance=.01)

    def test_world_vector_chain_resolves_continuous_sphere_set_crossings(self):
        frames = np.arange(5., dtype=float)
        targets = np.zeros((len(frames), 2, 3), dtype=float)
        targets[:, :, 0] = -.5
        envelope = np.ones(len(frames), dtype=float)
        accelerations = np.zeros((2, 3), dtype=float)
        accelerations[:, 0] = 1000.0
        spheres = [((0., 0., 0.), .2), ((.8, 0., 0.), .2)]
        kwargs = dict(
            frame_steps=np.diff(frames), dt=.1, frequency=2., damping=.35,
            air_friction=.2, strength=.9, envelope=envelope, propagation=.8,
            masses=[2., 1.], accelerations=accelerations,
            collision_spheres=spheres, collision_sphere_continuous=True,
            clearance=.01, restitution=.2, surface_friction=.4)
        result, report = sm.follow_world_vector_chain(targets, **kwargs)
        reversed_result, reversed_report = sm.follow_world_vector_chain(
            targets, collision_spheres=list(reversed(spheres)), **{
                key: value for key, value in kwargs.items()
                if key != 'collision_spheres'})
        np.testing.assert_array_equal(result, reversed_result)
        self.assertTrue(np.isfinite(result).all())
        self.assertEqual(report['collision_collider_count'], 2)
        self.assertEqual(report['collision_collider_count'],
                         reversed_report['collision_collider_count'])
        self.assertGreater(report['continuous_collision_samples'], 0)
        self.assertLessEqual(report['max_penetration_after'], 1e-12)
        for center, radius in spheres:
            separation = np.linalg.norm(
                result-np.asarray(center), axis=2)-radius-.01
            self.assertGreaterEqual(float(np.min(separation)), -1e-12)

    def test_world_vectors_resolves_continuous_sphere_set_crossings(self):
        frames = np.arange(5., dtype=float)
        targets = np.zeros((len(frames), 3), dtype=float)
        targets[:, 0] = -.5
        accelerations = np.zeros(3, dtype=float)
        accelerations[0] = 100.0
        spheres = [((0., 0., 0.), .2), ((.8, 0., 0.), .2)]
        kwargs = dict(
            dt=.1, frequency=2., damping=.35, air_friction=.2,
            gravity=(0., 0., 0.), gravity_scale=0.,
            external_acceleration=accelerations,
            collision_spheres=spheres, collision_sphere_continuous=True,
            clearance=.01, restitution=.2, surface_friction=.4)
        result, report = sm.follow_world_vectors(
            targets, np.diff(frames), **kwargs)
        reversed_result, reversed_report = sm.follow_world_vectors(
            targets, np.diff(frames), collision_spheres=list(reversed(spheres)),
            **{key: value for key, value in kwargs.items()
               if key != 'collision_spheres'})
        np.testing.assert_array_equal(result, reversed_result)
        self.assertEqual(
            report['continuous_collision_samples'],
            reversed_report['continuous_collision_samples'])
        self.assertGreater(report['continuous_collision_samples'], 0)
        self.assertTrue(np.isfinite(result).all())
        for center, radius in spheres:
            separation = np.linalg.norm(
                result-np.asarray(center), axis=1)-radius-.01
            self.assertGreaterEqual(float(np.min(separation)), -1e-12)

    def test_world_vector_chain_resolves_static_capsule_collision(self):
        frames = np.arange(9., dtype=float)
        targets = np.zeros((len(frames), 2, 3), dtype=float)
        targets[:, :, 0] = [[.05, .25]] * len(frames)
        targets[[0, 4, 8], :, 0] = .6
        envelope = sm.priority_envelope(frames, [0., 4., 8.], 1.)
        result, report = sm.follow_world_vector_chain(
            targets, np.diff(frames), dt=1/24, frequency=2., damping=.35,
            air_friction=.2, strength=.9, envelope=envelope, propagation=.8,
            masses=[2., 1.], accelerations=np.zeros((2, 3)),
            collision_capsule_start=(0., 0., -.5),
            collision_capsule_end=(0., 0., .5), collision_capsule_radius=.2,
            clearance=.01, restitution=.2, surface_friction=.4)
        self.assertTrue(np.isfinite(result).all())
        np.testing.assert_allclose(result[[0, 4, 8]], targets[[0, 4, 8]], atol=1e-12)
        self.assertGreater(report['collision_samples'], 0)
        self.assertGreater(report['max_raw_penetration'], 0.)
        self.assertLessEqual(report['max_penetration_after'], 1e-12)
        self.assertLessEqual(report['momentum_conservation_error'], 1e-10)

    def test_world_vector_chain_resolves_moving_capsule_collision(self):
        frames = np.arange(9., dtype=float)
        targets = np.zeros((len(frames), 2, 3), dtype=float)
        targets[:, :, 0] = [[.05, .25]] * len(frames)
        targets[[0, 4, 8], :, 0] = .8
        offsets = np.linspace(-.12, .12, len(frames))
        starts = np.column_stack((offsets, np.zeros(len(frames)),
                                  np.full(len(frames), -.5)))
        ends = np.column_stack((offsets, np.zeros(len(frames)),
                                np.full(len(frames), .5)))
        radii = np.linspace(.2, .3, len(frames))
        envelope = sm.priority_envelope(frames, [0., 4., 8.], 2.)
        kwargs = dict(
            dt=1/24, frequency=2., damping=.35, air_friction=.2,
            strength=.9, envelope=envelope, propagation=.8,
            masses=[2., 1.], accelerations=np.zeros((2, 3)),
            clearance=.01, restitution=.2, surface_friction=.4)
        result, report = sm.follow_world_vector_chain(
            targets, np.diff(frames),
            collision_capsule_trajectories=(starts, ends, radii), **kwargs)
        self.assertTrue(np.isfinite(result).all())
        np.testing.assert_allclose(result[[0, 4, 8]], targets[[0, 4, 8]], atol=1e-12)
        self.assertGreater(report['collision_samples'], 0)
        self.assertGreater(report['max_raw_penetration'], 0.)
        self.assertLessEqual(report['max_penetration_after'], 1e-12)
        self.assertLessEqual(report['momentum_conservation_error'], 1e-10)
        self.assertTrue(np.any((envelope > 0.) & (envelope < 1.)))
        for sample_index, sample in enumerate(result):
            for point in sample:
                closest = sm._capsule_closest(
                    point, starts[sample_index], ends[sample_index])
                separation = np.linalg.norm(point-closest)-radii[sample_index]-.01
                self.assertGreaterEqual(float(separation), -1e-12)

        fixed_starts = np.repeat(starts[-1][None, :], len(frames), axis=0)
        fixed_ends = np.repeat(ends[-1][None, :], len(frames), axis=0)
        constant, constant_report = sm.follow_world_vector_chain(
            targets, np.diff(frames),
            collision_capsule_trajectories=(fixed_starts, fixed_ends, radii[-1]),
            **kwargs)
        static, static_report = sm.follow_world_vector_chain(
            targets, np.diff(frames),
            collision_capsule_start=starts[-1], collision_capsule_end=ends[-1],
            collision_capsule_radius=radii[-1], **kwargs)
        np.testing.assert_allclose(constant, static, atol=1e-12)
        self.assertEqual(constant_report, static_report)
        self.assertGreater(float(np.max(np.abs(result-constant))), .01)

        radius_only, _ = sm.follow_world_vector_chain(
            targets, np.diff(frames),
            collision_capsule_trajectories=(fixed_starts, fixed_ends, radii),
            **kwargs)
        self.assertGreater(float(np.max(np.abs(radius_only-static))), .01)

        zero_result, zero_report = sm.follow_world_vector_chain(
            targets, np.diff(frames), strength=0.0,
            dt=kwargs['dt'], frequency=kwargs['frequency'],
            damping=kwargs['damping'], air_friction=kwargs['air_friction'],
            envelope=envelope, propagation=kwargs['propagation'],
            masses=kwargs['masses'], accelerations=kwargs['accelerations'],
            clearance=kwargs['clearance'], restitution=kwargs['restitution'],
            surface_friction=kwargs['surface_friction'],
            collision_capsule_trajectories=(starts, ends, radii))
        np.testing.assert_array_equal(zero_result, targets)
        self.assertEqual(zero_report['collision_samples'], 0)
        self.assertGreater(zero_report['max_raw_penetration'], 0.0)
        self.assertEqual(zero_report['max_penetration_after'],
                         zero_report['max_raw_penetration'])

        for tiny in (1e-13, np.nextafter(0.0, 1.0)):
            tiny_result, tiny_report = sm.follow_world_vector_chain(
                targets, np.diff(frames), strength=tiny,
                dt=kwargs['dt'], frequency=kwargs['frequency'],
                damping=kwargs['damping'], air_friction=kwargs['air_friction'],
                envelope=envelope, propagation=kwargs['propagation'],
                masses=kwargs['masses'], accelerations=kwargs['accelerations'],
                clearance=kwargs['clearance'], restitution=kwargs['restitution'],
                surface_friction=kwargs['surface_friction'],
                collision_capsule_trajectories=(starts, ends, radii))
            for sample_index, sample in enumerate(tiny_result):
                for point in sample:
                    closest = sm._capsule_closest(
                        point, starts[sample_index], ends[sample_index])
                    separation = np.linalg.norm(point-closest)-radii[sample_index]-.01
                    self.assertGreaterEqual(float(separation), -1e-12)
            self.assertLessEqual(tiny_report['max_penetration_after'], 1e-12)

        with self.assertRaisesRegex(ValueError, 'static or moving capsule'):
            sm.follow_world_vector_chain(
                targets, np.diff(frames),
                collision_capsule_start=(0., 0., -.5),
                collision_capsule_end=(0., 0., .5), collision_capsule_radius=.2,
                collision_capsule_trajectories=(starts, ends, radii), **kwargs)
        hostile = (
            (starts[:-1], ends, radii),
            (starts, np.full_like(ends, np.nan), radii),
            (starts, starts.copy(), radii),
            (starts, ends, np.asarray([.2] * 8 + [1001.])),
            (starts, ends, True),
            (np.full_like(starts, -np.finfo(float).max),
             np.full_like(ends, np.finfo(float).max), radii),
        )
        for trajectories in hostile:
            with self.subTest(trajectories=repr(trajectories)):
                with self.assertRaises(ValueError):
                    sm.follow_world_vector_chain(
                        targets, np.diff(frames),
                        collision_capsule_trajectories=trajectories, **kwargs)

    def test_world_vector_chain_resolves_continuous_moving_capsule_collision(self):
        frames = np.arange(9., dtype=float)
        targets = np.zeros((len(frames), 2, 3), dtype=float)
        targets[:, :, 0] = [[.05, .25]] * len(frames)
        targets[[0, 4, 8], :, 0] = .8
        offsets = np.linspace(-.12, .12, len(frames))
        starts = np.column_stack((offsets, np.zeros(len(frames)),
                                  np.full(len(frames), -.5)))
        ends = np.column_stack((offsets, np.zeros(len(frames)),
                                np.full(len(frames), .5)))
        radii = np.linspace(.2, .3, len(frames))
        envelope = sm.priority_envelope(frames, [0., 4., 8.], 2.)
        result, report = sm.follow_world_vector_chain(
            targets, np.diff(frames), dt=1/24, frequency=2., damping=.35,
            air_friction=.2, strength=.9, envelope=envelope, propagation=.8,
            masses=[2., 1.], accelerations=np.zeros((2, 3)),
            clearance=.01, restitution=.2, surface_friction=.4,
            collision_capsule_trajectories=(starts, ends, radii),
            collision_capsule_continuous=True)
        self.assertTrue(np.isfinite(result).all())
        np.testing.assert_allclose(result[[0, 4, 8]], targets[[0, 4, 8]], atol=1e-12)
        self.assertGreater(report['continuous_collision_samples'], 0)
        self.assertGreater(report['collision_samples'], 0)
        self.assertLessEqual(report['max_penetration_after'], 1e-12)
        self.assertLessEqual(report['momentum_conservation_error'], 1e-10)
        for sample_index, sample in enumerate(result):
            for point in sample:
                closest = sm._capsule_closest(
                    point, starts[sample_index], ends[sample_index])
                separation = np.linalg.norm(point-closest)-radii[sample_index]-.01
                self.assertGreaterEqual(float(separation), -1e-12)

    def test_world_vector_chain_capsule_response_uses_trajectory_velocity(self):
        frames = np.arange(4., dtype=float)
        targets = np.zeros((4, 2, 3), dtype=float)
        targets[:, :, 0] = .05
        kwargs = dict(
            dt=.1, frequency=1., damping=.2, air_friction=0., strength=1.,
            envelope=np.ones(4), propagation=0., masses=[1., 1.],
            accelerations=np.zeros((2, 3)), clearance=.01,
            restitution=0., surface_friction=0.)
        current_starts = np.tile((0., 0., -.5), (4, 1))
        current_ends = np.tile((0., 0., .5), (4, 1))

        left_history = current_starts.copy()
        left_history[0, 0] = -.2
        right_history = current_starts.copy()
        right_history[0, 0] = .2
        left_ends = current_ends.copy()
        left_ends[0, 0] = -.2
        right_ends = current_ends.copy()
        right_ends[0, 0] = .2
        translated_left, _ = sm.follow_world_vector_chain(
            targets, np.diff(frames),
            collision_capsule_trajectories=(left_history, left_ends, .2), **kwargs)
        translated_right, _ = sm.follow_world_vector_chain(
            targets, np.diff(frames),
            collision_capsule_trajectories=(right_history, right_ends, .2), **kwargs)
        # Geometry is identical from sample 1 onward; opposite sample-0 midpoint
        # histories therefore isolate collider-relative translation velocity.
        np.testing.assert_array_equal(left_history[1:], right_history[1:])
        np.testing.assert_array_equal(left_ends[1:], right_ends[1:])
        self.assertGreater(translated_left[2, 0, 0], translated_right[2, 0, 0])

        expanding, _ = sm.follow_world_vector_chain(
            targets, np.diff(frames),
            collision_capsule_trajectories=(current_starts, current_ends,
                                            (.1, .2, .2, .2)), **kwargs)
        contracting, _ = sm.follow_world_vector_chain(
            targets, np.diff(frames),
            collision_capsule_trajectories=(current_starts, current_ends,
                                            (.3, .2, .2, .2)), **kwargs)
        # Geometry is again identical from sample 1 onward, so the sample-2
        # difference is caused by opposite radial surface velocity histories.
        self.assertGreater(expanding[2, 0, 0], contracting[2, 0, 0])

    def test_world_vector_chain_resolves_static_mesh_collision(self):
        frames = np.arange(9., dtype=float)
        targets = np.zeros((len(frames), 2, 3), dtype=float)
        targets[:, :, 0] = [[.1, .35]] * len(frames)
        targets[:, :, 2] = -.2
        targets[[0, 4, 8], :, 2] = .2
        envelope = sm.priority_envelope(frames, [0., 4., 8.], 1.)
        mesh = [
            [[-2., -2., -1.], [-2., 2., -1.], [-2., 2., 0.]],
            [[-2., -2., -1.], [-2., 2., 0.], [-2., -2., 0.]],
            [[2., -2., -1.], [2., 2., 0.], [2., 2., -1.]],
            [[2., -2., -1.], [2., -2., 0.], [2., 2., 0.]],
            [[-2., -2., -1.], [-2., -2., 0.], [2., -2., 0.]],
            [[-2., -2., -1.], [2., -2., 0.], [2., -2., -1.]],
            [[-2., 2., -1.], [2., 2., -1.], [2., 2., 0.]],
            [[-2., 2., -1.], [2., 2., 0.], [-2., 2., 0.]],
            [[-2., -2., 0.], [-2., 2., 0.], [2., 2., 0.]],
            [[-2., -2., 0.], [2., 2., 0.], [2., -2., 0.]],
            [[-2., -2., -1.], [2., -2., -1.], [2., 2., -1.]],
            [[-2., -2., -1.], [2., 2., -1.], [-2., 2., -1.]],
        ]
        result, report = sm.follow_world_vector_chain(
            targets, np.diff(frames), dt=1/24, frequency=2., damping=.35,
            air_friction=.2, strength=.9, envelope=envelope, propagation=.8,
            masses=[2., 1.], accelerations=[[0., 0., -4.], [0., 0., -2.]],
            collision_mesh_triangles=mesh, collision_mesh_closed=True,
            clearance=.01, restitution=.2, surface_friction=.4)
        self.assertTrue(np.isfinite(result).all())
        np.testing.assert_allclose(result[[0, 4, 8]], targets[[0, 4, 8]], atol=1e-12)
        self.assertGreater(report['collision_samples'], 0)
        self.assertGreater(report['max_raw_penetration'], 0.)
        self.assertLessEqual(report['max_penetration_after'], 1e-12)
        self.assertLessEqual(report['momentum_conservation_error'], 1e-10)

    def test_world_vector_chain_resolves_static_continuous_mesh_crossing(self):
        frames = np.arange(5., dtype=float)
        targets = np.zeros((len(frames), 2, 3), dtype=float)
        targets[:, :, 0] = [[.1, .35]] * len(frames)
        targets[:, :, 2] = np.asarray([1., -1., 1., 1., 1.])[:, None]
        envelope = sm.priority_envelope(frames, [0., 4.], 1.)
        mesh = [
            [[-2., -2., -.05], [-2., 2., -.05], [-2., 2., .05]],
            [[-2., -2., -.05], [-2., 2., .05], [-2., -2., .05]],
            [[2., -2., -.05], [2., 2., .05], [2., 2., -.05]],
            [[2., -2., -.05], [2., -2., .05], [2., 2., .05]],
            [[-2., -2., -.05], [-2., -2., .05], [2., -2., .05]],
            [[-2., -2., -.05], [2., -2., .05], [2., -2., -.05]],
            [[-2., 2., -.05], [2., 2., -.05], [2., 2., .05]],
            [[-2., 2., -.05], [2., 2., .05], [-2., 2., .05]],
            [[-2., -2., .05], [-2., 2., .05], [2., 2., .05]],
            [[-2., -2., .05], [2., 2., .05], [2., -2., .05]],
            [[-2., -2., -.05], [2., -2., -.05], [2., 2., -.05]],
            [[-2., -2., -.05], [2., 2., -.05], [-2., 2., -.05]],
        ]
        result, report = sm.follow_world_vector_chain(
            targets, np.diff(frames), dt=1/24, frequency=12., damping=.1,
            air_friction=0., strength=1., envelope=envelope, propagation=.8,
            masses=[2., 1.], accelerations=np.zeros((2, 3)),
            collision_mesh_triangles=mesh, collision_mesh_closed=True,
            collision_mesh_continuous=True, clearance=.01,
            restitution=.2, surface_friction=.4)
        self.assertTrue(np.isfinite(result).all())
        np.testing.assert_allclose(result[[0, 4]], targets[[0, 4]], atol=1e-12)
        self.assertGreater(report['collision_samples'], 0)
        self.assertGreater(report['continuous_collision_samples'], 0)
        self.assertLessEqual(report['max_raw_penetration'], 1e-12)
        self.assertLessEqual(report['max_penetration_after'], 1e-12)
        self.assertLessEqual(report['momentum_conservation_error'], 1e-10)

    def test_world_vector_chain_resolves_static_exact_swept_volume(self):
        frames = np.arange(5., dtype=float)
        targets = np.zeros((len(frames), 2, 3), dtype=float)
        targets[:, :, 0] = [[.1, .35]] * len(frames)
        targets[:, :, 2] = np.asarray([1., -1., 1., 1., 1.])[:, None]
        envelope = sm.priority_envelope(frames, [0., 4.], 1.)
        mesh = [
            [[-2., -2., -.05], [-2., 2., -.05], [-2., 2., .05]],
            [[-2., -2., -.05], [-2., 2., .05], [-2., -2., .05]],
            [[2., -2., -.05], [2., 2., .05], [2., 2., -.05]],
            [[2., -2., -.05], [2., -2., .05], [2., 2., .05]],
            [[-2., -2., -.05], [-2., -2., .05], [2., -2., .05]],
            [[-2., -2., -.05], [2., -2., .05], [2., -2., -.05]],
            [[-2., 2., -.05], [2., 2., -.05], [2., 2., .05]],
            [[-2., 2., -.05], [2., 2., .05], [-2., 2., .05]],
            [[-2., -2., .05], [-2., 2., .05], [2., 2., .05]],
            [[-2., -2., .05], [2., 2., .05], [2., -2., .05]],
            [[-2., -2., -.05], [2., -2., -.05], [2., 2., -.05]],
            [[-2., -2., -.05], [2., 2., -.05], [-2., 2., -.05]],
        ]
        result, report = sm.follow_world_vector_chain(
            targets, np.diff(frames), dt=1/24, frequency=12., damping=.1,
            air_friction=0., strength=1., envelope=envelope, propagation=.8,
            masses=[2., 1.], accelerations=np.zeros((2, 3)),
            collision_mesh_triangles=mesh, collision_mesh_closed=True,
            collision_mesh_volume_radius=.001, collision_mesh_continuous=True,
            clearance=.001, restitution=.2, surface_friction=.4)
        self.assertTrue(np.isfinite(result).all())
        np.testing.assert_allclose(result[[0, 4]], targets[[0, 4]], atol=1e-12)
        self.assertGreater(report['collision_samples'], 0)
        self.assertGreater(report['continuous_collision_samples'], 0)
        self.assertLessEqual(report['max_raw_penetration'], 1e-12)
        self.assertLessEqual(report['max_penetration_after'], 1e-12)
        self.assertLessEqual(report['momentum_conservation_error'], 1e-10)

    def test_world_vector_chain_resolves_sampled_moving_deforming_mesh(self):
        frames = np.arange(5., dtype=float)
        targets = np.zeros((len(frames), 2, 3), dtype=float)
        targets[:, :, 0] = [[.1, .35]] * len(frames)
        targets[:, :, 2] = np.asarray([.2, -.2, .2, .2, .2])[:, None]
        envelope = sm.priority_envelope(frames, [0., 4.], 1.)
        mesh = np.asarray([
            [[-2., -2., -1.], [-2., 2., -1.], [-2., 2., 0.]],
            [[-2., -2., -1.], [-2., 2., 0.], [-2., -2., 0.]],
            [[2., -2., -1.], [2., 2., 0.], [2., 2., -1.]],
            [[2., -2., -1.], [2., -2., 0.], [2., 2., 0.]],
            [[-2., -2., -1.], [-2., -2., 0.], [2., -2., 0.]],
            [[-2., -2., -1.], [2., -2., 0.], [2., -2., -1.]],
            [[-2., 2., -1.], [2., 2., -1.], [2., 2., 0.]],
            [[-2., 2., -1.], [2., 2., 0.], [-2., 2., 0.]],
            [[-2., -2., 0.], [-2., 2., 0.], [2., 2., 0.]],
            [[-2., -2., 0.], [2., 2., 0.], [2., -2., 0.]],
            [[-2., -2., -1.], [2., -2., -1.], [2., 2., -1.]],
            [[-2., -2., -1.], [2., 2., -1.], [-2., 2., -1.]],
        ])
        trajectory = np.stack([
            mesh + np.asarray((shift, 0., 0.))
            for shift in np.linspace(0., .4, len(frames))])
        result, report = sm.follow_world_vector_chain(
            targets, np.diff(frames), dt=1/24, frequency=12., damping=.1,
            air_friction=0., strength=1., envelope=envelope, propagation=.8,
            masses=[2., 1.], accelerations=np.zeros((2, 3)),
            collision_mesh_trajectories=trajectory, collision_mesh_closed=True,
            collision_mesh_volume_radius=.001, collision_mesh_continuous=True,
            clearance=.001,
            restitution=.2, surface_friction=.4)
        self.assertTrue(np.isfinite(result).all())
        np.testing.assert_allclose(result[[0, 4]], targets[[0, 4]], atol=1e-12)
        self.assertGreater(report['collision_samples'], 0)
        self.assertGreater(report['continuous_collision_samples'], 0)
        self.assertGreater(report['max_raw_penetration'], 0.)
        self.assertLessEqual(report['max_penetration_after'], 1e-12)
        self.assertLessEqual(report['momentum_conservation_error'], 1e-10)

    def test_world_vector_chain_rejects_static_and_sampled_mesh_combination(self):
        values = np.zeros((3, 2, 3), dtype=float)
        mesh = [[[-1., -1., 0.], [1., -1., 0.], [0., 1., 0.]]]
        trajectory = np.asarray([mesh, mesh, mesh], dtype=float)
        with self.assertRaisesRegex(ValueError, 'one static or sampled mesh'):
            sm.follow_world_vector_chain(
                values, [1., 1.], dt=1/24, frequency=2., damping=.5,
                air_friction=0., strength=1., envelope=np.ones(3), propagation=.5,
                masses=[1., 1.], accelerations=np.zeros((2, 3)),
                collision_mesh_triangles=mesh,
                collision_mesh_trajectories=trajectory)

    def test_world_vector_chain_rejects_hostile_inputs(self):
        values = np.zeros((3, 2, 3), dtype=float)
        mesh = [[[-1., -1., 0.], [1., -1., 0.], [0., 1., 0.]]]
        with self.assertRaises(ValueError):
            sm.follow_world_vector_chain(
                values, [1., 1.], dt=1/24, frequency=2., damping=.5,
                air_friction=0., strength=1., envelope=np.ones(3), propagation=1.1,
                masses=[1., 1.], accelerations=np.zeros((2, 3)))
        with self.assertRaisesRegex(ValueError, 'one planar or spherical'):
            sm.follow_world_vector_chain(
                values, [1., 1.], dt=1/24, frequency=2., damping=.5,
                air_friction=0., strength=1., envelope=np.ones(3), propagation=.5,
                masses=[1., 1.], accelerations=np.zeros((2, 3)),
                collision_point=(0., 0., 0.), collision_normal=(0., 0., 1.),
                collision_sphere_center=(0., 0., 0.), collision_sphere_radius=1.)
        with self.assertRaisesRegex(ValueError, 'center and radius'):
            sm.follow_world_vector_chain(
                values, [1., 1.], dt=1/24, frequency=2., damping=.5,
                air_friction=0., strength=1., envelope=np.ones(3), propagation=.5,
                masses=[1., 1.], accelerations=np.zeros((2, 3)),
                collision_sphere_center=(0., 0., 0.))
        with self.assertRaisesRegex(ValueError, 'one planar, spherical, capsule, or mesh'):
            sm.follow_world_vector_chain(
                values, [1., 1.], dt=1/24, frequency=2., damping=.5,
                air_friction=0., strength=1., envelope=np.ones(3), propagation=.5,
                masses=[1., 1.], accelerations=np.zeros((2, 3)),
                collision_point=(0., 0., 0.), collision_normal=(0., 0., 1.),
                collision_mesh_triangles=mesh)
        with self.assertRaisesRegex(ValueError, 'finite-volume collision requires a closed mesh'):
            sm.follow_world_vector_chain(
                values, [1., 1.], dt=1/24, frequency=2., damping=.5,
                air_friction=0., strength=1., envelope=np.ones(3), propagation=.5,
                masses=[1., 1.], accelerations=np.zeros((2, 3)),
                collision_mesh_triangles=mesh, collision_mesh_volume_radius=.1)
        with self.assertRaisesRegex(ValueError, 'requires a closed mesh'):
            sm.follow_world_vector_chain(
                values, [1., 1.], dt=1/24, frequency=2., damping=.5,
                air_friction=0., strength=1., envelope=np.ones(3), propagation=.5,
                masses=[1., 1.], accelerations=np.zeros((2, 3)),
                collision_mesh_triangles=mesh, collision_mesh_continuous=True)
        with self.assertRaises(ValueError):
            sm.transfer_pairwise_momentum(np.zeros((2, 3)), [1., 0.], .5)

    def test_envelope_and_settings_fail_closed(self):
        np.testing.assert_allclose(sm.boundary_envelope([0., 1., 2., 3., 4.], 2.), [0., .5, 1., .5, 0.])
        np.testing.assert_allclose(sm.priority_envelope([0., 1., 2., 3., 4.], [0., 2., 4.], 1.), [0., 1., 0., 1., 0.])
        for kwargs in (
            dict(frequency=0., damping=.5, air_friction=0., strength=1., blend_frames=2., dt=1/24),
            dict(frequency=2., damping=-1., air_friction=0., strength=1., blend_frames=2., dt=1/24),
            dict(frequency=2., damping=.5, air_friction=0., strength=1.1, blend_frames=2., dt=1/24),
            dict(frequency=2., damping=.5, air_friction=float('nan'), strength=1., blend_frames=2., dt=1/24)):
            with self.assertRaises(ValueError):sm.validate_settings(**kwargs)

    def test_world_follow_applies_gravity_without_moving_priority_poses(self):
        frames = np.arange(7., dtype=float)
        target = np.tile([0., 0., 1.], (len(frames), 1))
        envelope = sm.priority_envelope(frames, [0., 3., 6.], 1.)
        result, report = sm.apply_world_vector_follow(
            target, frames, dt=1/24, frequency=1.5, damping=.35,
            air_friction=.1, strength=1., blend_frames=1.,
            gravity=(0., 0., -9.81), gravity_scale=1., envelope=envelope)
        np.testing.assert_array_equal(result[[0, 3, 6]], target[[0, 3, 6]])
        self.assertLess(float(np.min(result[:, 2])), 1.)
        self.assertGreater(report['max_world_correction'], .001)
        self.assertEqual(report['collision_samples'], 0)

    def test_world_follow_resolves_plane_and_damps_tangent(self):
        frames = np.arange(5., dtype=float)
        target = np.array([[0., 0., .2], [1., 0., -2.], [2., 0., -2.],
                           [3., 0., -2.], [4., 0., .2]])
        result, report = sm.apply_world_vector_follow(
            target, frames, dt=.25, frequency=.5, damping=0.,
            air_friction=0., strength=1., blend_frames=0.,
            collision_point=(0., 0., 0.), collision_normal=(0., 0., 1.),
            clearance=.1, restitution=.25, surface_friction=.5,
            collision_mask=[False, True, True, True, False])
        self.assertGreater(report['collision_samples'], 0)
        self.assertGreater(report['max_raw_penetration'], 0.)
        self.assertGreater(report['max_penetration_before'], 1.)
        self.assertLessEqual(report['max_penetration_after'], 1e-12)
        self.assertTrue(np.all(result[1:4, 2] >= .1-1e-12))
        np.testing.assert_array_equal(result[[0, -1]], target[[0, -1]])

    def test_world_settings_and_collision_mask_fail_closed(self):
        with self.assertRaises(ValueError):
            sm.validate_world_settings(gravity=(0., 0.), gravity_scale=1.)
        with self.assertRaises(ValueError):
            sm.validate_world_settings(gravity=(0., 0., -9.81), gravity_scale=1.,
                                       collision_point=(0., 0., 0.))
        with self.assertRaises(ValueError):
            sm.follow_world_vectors([[0., 0., 0.], [1., 0., 0.]], [1.],
                dt=1/24, frequency=2., damping=.5, air_friction=0.,
                collision_mask=[True])

    def test_bounded_plane_uses_simulated_position(self):
        target = np.array([[0., 0., .2], [4., 0., -2.], [4., 0., -2.], [4., 0., .2]])
        triangle = [[[-1., -1., 0.], [1., -1., 0.], [0., 1., 0.]]]
        bounded, report = sm.follow_world_vectors(
            target, [1., 1., 1.], dt=.5, frequency=.4, damping=0., air_friction=0.,
            collision_point=(0., 0., 0.), collision_normal=(0., 0., 1.),
            clearance=.1, collision_triangles=triangle)
        self.assertEqual(report['collision_samples'], 0)
        self.assertLess(float(np.min(bounded[:, 2])), .1)
        with self.assertRaises(ValueError):
            sm.follow_world_vectors(target, [1., 1., 1.], dt=.5, frequency=.4,
                damping=0., air_friction=0., collision_triangles=triangle)


if __name__ == '__main__':
    unittest.main()
