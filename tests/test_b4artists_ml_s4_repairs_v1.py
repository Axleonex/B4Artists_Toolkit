"""Focused regressions for defects found by the September 2026 S4 review."""
from pathlib import Path
import sys
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from b4artists_ml import math_core
from b4artists_ml import secondary_math as sm


class S4RepairMathTests(unittest.TestCase):
    def test_pose_blend_handles_opposite_huge_finite_components(self):
        channels = {'location': [0, 1, 2], 'scale': [0, 1, 2],
                    'rotation': [0, 1, 2, 3]}
        first = {'Bone': {'mode': 'QUATERNION', 'channels': channels,
                          'rotation': (1.0, 0.0, 0.0, 0.0),
                          'location': (1e308, 0.0, 0.0),
                          'scale': (1.0, 1.0, 1.0)}}
        second = {'Bone': {'mode': 'QUATERNION', 'channels': channels,
                           'rotation': (1.0, 0.0, 0.0, 0.0),
                           'location': (-1e308, 0.0, 0.0),
                           'scale': (1.0, 1.0, 1.0)}}
        self.assertEqual(math_core.blend_pose(first, second, 0.0)['Bone']['location'][0], 1e308)
        self.assertEqual(math_core.blend_pose(first, second, 1.0)['Bone']['location'][0], -1e308)
        self.assertTrue(np.isfinite(math_core.blend_pose(first, second, 0.5)['Bone']['location']).all())

    def test_bounded_plane_residual_ignores_points_outside_surface(self):
        values = np.full((3, 2, 3), (10.0, 10.0, -1.0), dtype=float)
        result, report = sm.follow_world_vector_chain(
            values, (1.0, 1.0), dt=1/24, frequency=1.0, damping=1.0,
            air_friction=0.0, strength=1.0, envelope=(0.0, 1.0, 0.0),
            propagation=0.0, masses=(1.0, 1.0), accelerations=np.zeros((2, 3)),
            collision_point=(0.0, 0.0, 0.0), collision_normal=(0.0, 0.0, 1.0),
            collision_triangles=(((0.0, 0.0, 0.0), (1.0, 0.0, 0.0),
                                  (0.0, 1.0, 0.0)),))
        np.testing.assert_allclose(result, values)
        self.assertEqual(report['max_penetration_after'], 0.0)

    def test_forced_quaternion_chain_is_continuous_at_zero_force(self):
        values = np.tile(np.array((1.0, 0.0, 0.0, 0.0)), (3, 2, 1))
        values[1, 0] = (2**-0.5, 0.0, 0.0, 2**-0.5)
        common = dict(dt=1/24, frequency=1.0, damping=0.0,
                      air_friction=0.0, strength=1.0,
                      envelope=(0.0, 1.0, 0.0), propagation=1.0)
        baseline = sm.follow_quaternion_chain(values, (1.0, 1.0), **common)
        forcing = np.zeros((3, 2, 3), dtype=float)
        forcing[1, 0, 2] = 1e-10
        forced = sm.follow_forced_quaternion_chain(
            values, (1.0, 1.0), inertias=(1.0, 1.0),
            angular_accelerations=forcing, **common)
        np.testing.assert_allclose(forced, baseline, atol=1e-11, rtol=0.0)

    def test_huge_finite_quaternion_normalizes_without_overflow(self):
        self.assertEqual(math_core.unit_quaternion((1e200, 0.0, 0.0, 0.0)),
                         (1.0, 0.0, 0.0, 0.0))
        q = math_core.unit_quaternion((1e308, 1e308, 1e308, 1e308))
        self.assertAlmostEqual(sum(value*value for value in q), 1.0)

    def test_static_sphere_penetration_has_defined_response_state(self):
        values = np.zeros((2, 3), dtype=float)
        result, report = sm.follow_world_vectors(
            values, [1.0], dt=1/24, frequency=1.0, damping=1.0,
            air_friction=0.0, collision_sphere_center=(0.0, 0.0, 0.0),
            collision_sphere_radius=1.0)
        self.assertGreaterEqual(np.linalg.norm(result[1]), 1.0-1e-8)
        self.assertGreater(report['collision_samples'], 0)

    def test_zero_influence_preserves_capsule_samples_and_endpoints(self):
        values = np.zeros((3, 3), dtype=float)
        result, _ = sm.apply_world_vector_follow(
            values, [0.0, 1.0, 2.0], dt=1/24, frequency=1.0,
            damping=1.0, air_friction=0.0, strength=0.0, blend_frames=0.0,
            collision_capsule_start=(0.0, 0.0, -1.0),
            collision_capsule_end=(0.0, 0.0, 1.0),
            collision_capsule_radius=1.0)
        np.testing.assert_array_equal(result, values)

    def test_moving_capsule_trajectory_reaches_continuous_integrator(self):
        values = np.zeros((3, 3), dtype=float)
        starts = [(-2.0, 0.0, -1.0), (2.0, 0.0, -1.0), (4.0, 0.0, -1.0)]
        ends = [(-2.0, 0.0, 1.0), (2.0, 0.0, 1.0), (4.0, 0.0, 1.0)]
        result, report = sm.apply_world_vector_follow(
            values, [0.0, 1.0, 2.0], dt=1.0, frequency=0.1,
            damping=1.0, air_friction=0.0, strength=1.0, blend_frames=0.0,
            collision_capsule_trajectories=(starts, ends, [0.5, 0.5, 0.5]),
            collision_capsule_continuous=True,
            envelope=np.ones(3))
        self.assertGreater(report['continuous_collision_samples'], 0)
        self.assertTrue(np.isfinite(result).all())

    def test_world_chain_keeps_static_spheres_with_moving_set(self):
        values = np.asarray([
            [[0.0, 0.0, 0.0], [0.0, 2.0, 0.0]],
            [[0.0, 0.0, 0.0], [0.0, 2.0, 0.0]],
            [[0.0, 0.0, 0.0], [0.0, 2.0, 0.0]],
        ])
        moving = ([(-3.0, 0.0, 0.0)]*3, 0.25)
        result, report = sm.follow_world_vector_chain(
            values, [1.0, 1.0], dt=1/24, frequency=1.0, damping=1.0,
            air_friction=0.0, strength=1.0, envelope=[0.0, 1.0, 0.0],
            propagation=0.0, masses=[1.0, 1.0], accelerations=np.zeros((2, 3)),
            collision_point=(0.0, 0.0, -2.0),
            collision_normal=(0.0, 0.0, 1.0),
            collision_spheres=[((0.0, 0.0, 0.0), 1.0)],
            collision_sphere_trajectories=[moving],
            compound_plane_spheres=True)
        self.assertGreaterEqual(np.linalg.norm(result[1, 0]), 1.0-1e-8)
        self.assertGreater(report['collision_samples'], 0)

    def test_continuous_sphere_allows_departure_from_contact(self):
        values = np.asarray([(1.0, 0.0, 0.0),
                             (2.0, 0.0, 0.0),
                             (3.0, 0.0, 0.0)])
        result, _ = sm.follow_world_vectors(
            values, [1.0, 1.0], dt=1.0, frequency=1.0, damping=0.0,
            air_friction=0.0, collision_sphere_center=(0.0, 0.0, 0.0),
            collision_sphere_radius=1.0, collision_sphere_continuous=True)
        self.assertGreater(result[1, 0], 1.0)
        self.assertGreater(result[2, 0], result[1, 0])

    def test_world_chain_projects_exact_sphere_center(self):
        values = np.zeros((3, 2, 3), dtype=float)
        result, _ = sm.follow_world_vector_chain(
            values, [1.0, 1.0], dt=1/24, frequency=1.0, damping=1.0,
            air_friction=0.0, strength=1.0, envelope=[0.0, 1.0, 0.0],
            propagation=0.0, masses=[1.0, 1.0],
            accelerations=np.zeros((2, 3)),
            collision_sphere_center=(0.0, 0.0, 0.0),
            collision_sphere_radius=1.0)
        self.assertGreaterEqual(np.linalg.norm(result[1, 0]), 1.0-1e-8)

    def test_mesh_contact_projects_along_face_normal(self):
        triangle = np.asarray([[(0.0, 0.0, 0.0),
                                (10.0, 0.0, 0.0),
                                (0.0, 10.0, 0.0)]])
        state = sm._mesh_collision_state(
            (1.0, 1.0, 0.0), triangle, 0.1, False,
            fallbacks=((1.0, 0.0, 0.0),))
        self.assertTrue(state[0])
        self.assertAlmostEqual(abs(state[1][2]), 0.1)

    def test_closed_mesh_shared_edge_hit_counts_once(self):
        vertices = np.asarray([
            (0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0),
            (0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)], dtype=float)
        faces = ((0, 2, 1), (0, 3, 2), (4, 5, 6), (4, 6, 7),
                 (0, 1, 5), (0, 5, 4), (3, 7, 6), (3, 6, 2),
                 (0, 4, 7), (0, 7, 3), (1, 2, 6), (1, 6, 5))
        triangles = np.asarray([[vertices[i] for i in face] for face in faces])
        direction = np.asarray((1.0, 0.3713906763541037,
                                0.2176242636071215))
        point = np.asarray((0.5, 0.5-0.5*direction[1],
                            0.5-0.5*direction[2]))
        self.assertTrue(sm._mesh_inside(point, triangles))

    def test_parallel_segment_closest_points_reach_overlap(self):
        first, second, _, _ = sm._segment_segment_closest(
            (0, 0, 0), (2, 0, 0), (1, 1, 0), (3, 1, 0))
        self.assertAlmostEqual(np.linalg.norm(first-second), 1.0)
        first, second, _, _ = sm._segment_segment_closest(
            (0, 0, 0), (2, 0, 0), (1, 0, 0), (3, 0, 0))
        self.assertAlmostEqual(np.linalg.norm(first-second), 0.0)

    def test_chain_plane_projects_published_blend(self):
        values = np.zeros((3, 2, 3), dtype=float)
        values[:, :, 2] = -1.0
        result, report = sm.follow_world_vector_chain(
            values, [1.0, 1.0], dt=1/24, frequency=1.0, damping=1.0,
            air_friction=0.0, strength=0.5, envelope=[0.0, 1.0, 0.0],
            propagation=0.0, masses=[1.0, 1.0],
            accelerations=np.zeros((2, 3)),
            collision_point=(0.0, 0.0, 0.0),
            collision_normal=(0.0, 0.0, 1.0))
        self.assertGreaterEqual(float(np.min(result[1, :, 2])), -1e-10)
        self.assertAlmostEqual(report['max_penetration_after'], 1.0)

    def test_chain_continuous_multi_sphere_stops_at_entry(self):
        values = np.zeros((3, 2, 3), dtype=float)
        values[0, :, 0] = -2.0
        values[1:, :, 0] = 2.0
        result, _ = sm.follow_world_vector_chain(
            values, [1.0, 1.0], dt=1.0, frequency=30.0, damping=0.0,
            air_friction=0.0, strength=0.1, envelope=[0.0, 1.0, 0.0],
            propagation=0.0, masses=[1.0, 1.0],
            accelerations=np.zeros((2, 3)),
            collision_spheres=[((0, 0, 0), 0.5), ((10, 0, 0), 0.5)],
            collision_sphere_continuous=True)
        self.assertLessEqual(float(np.max(result[1, :, 0])), -0.5+1e-8)

    def test_chain_continuous_capsule_uses_entry_contact_and_counts_collider(self):
        values = np.zeros((3, 2, 3), dtype=float)
        values[0, :, 0] = -2.0
        values[1:, :, 0] = 2.0
        result, report = sm.follow_world_vector_chain(
            values, [1.0, 1.0], dt=1.0, frequency=30.0, damping=0.0,
            air_friction=0.0, strength=0.1, envelope=[0.0, 1.0, 0.0],
            propagation=0.0, masses=[1.0, 1.0],
            accelerations=np.zeros((2, 3)),
            collision_capsule_start=(0, 0, -1),
            collision_capsule_end=(0, 0, 1), collision_capsule_radius=1.0,
            collision_capsule_continuous=True)
        self.assertLessEqual(float(np.max(result[1, :, 0])), -1.0+1e-8)
        self.assertEqual(report['collision_collider_count'], 1)

    def test_vector_follow_projects_published_plane_blend(self):
        values = np.asarray(((0, 0, 1), (0, 0, -1), (0, 0, 1)), dtype=float)
        result, report = sm.apply_world_vector_follow(
            values, (0, 1, 2), dt=1.0, frequency=1.0, damping=1.0,
            air_friction=0.0, strength=0.5, blend_frames=0.0,
            collision_point=(0, 0, 0), collision_normal=(0, 0, 1))
        self.assertGreaterEqual(result[1, 2], -1e-10)
        self.assertLessEqual(report['max_penetration_after'], 1e-10)

    def test_vector_follow_sweeps_published_sphere_blend(self):
        values = np.asarray(((-2, 0, 0), (2, 0, 0), (2, 0, 0)), dtype=float)
        result, _ = sm.apply_world_vector_follow(
            values, (0, 1, 2), dt=1.0, frequency=1.0, damping=1.0,
            air_friction=0.0, strength=0.1, blend_frames=0.0,
            collision_sphere_center=(0, 0, 0), collision_sphere_radius=1.0,
            collision_sphere_continuous=True)
        self.assertLessEqual(result[1, 0], -1.0+1e-8)

    def test_chain_projects_center_of_coincident_spheres(self):
        values = np.zeros((3, 2, 3), dtype=float)
        result, _ = sm.follow_world_vector_chain(
            values, (1, 1), dt=1/24, frequency=1.0, damping=1.0,
            air_friction=0.0, strength=1.0, envelope=(0, 1, 0),
            propagation=0.0, masses=(1, 1), accelerations=np.zeros((2, 3)),
            collision_spheres=(((0, 0, 0), 1.0), ((0, 0, 0), 1.0)))
        self.assertGreaterEqual(np.linalg.norm(result[1, 0]), 1.0-1e-8)

    def test_exact_mesh_sweep_prefers_entry_over_inside_endpoint_projection(self):
        faces = (
            ((-1,-1,-1),(-1,1,-1),(-1,1,1),(-1,-1,1)),
            ((1,-1,-1),(1,-1,1),(1,1,1),(1,1,-1)),
            ((-1,-1,-1),(-1,-1,1),(1,-1,1),(1,-1,-1)),
            ((-1,1,-1),(1,1,-1),(1,1,1),(-1,1,1)),
            ((-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1)),
            ((-1,-1,1),(-1,1,1),(1,1,1),(1,-1,1)),
        )
        triangles = np.asarray([triangle for face in faces for triangle in
                                ((face[0], face[1], face[2]),
                                 (face[0], face[2], face[3]))], dtype=float)
        hit = sm._mesh_exact_swept_volume_hit(
            (-2, 0, 0), (0.9, 0, 0), triangles, 0.0, True,
            volume_radius=0.1)
        self.assertIsNotNone(hit)
        self.assertAlmostEqual(hit[0][0], -1.1, places=7)

    def test_vector_follow_sweeps_published_capsule_blend(self):
        values = np.asarray(((-2, 0, 0), (2, 0, 0), (2, 0, 0)), dtype=float)
        result, _ = sm.apply_world_vector_follow(
            values, (0, 1, 2), dt=1.0, frequency=1.0, damping=0.0,
            air_friction=0.0, strength=0.1, blend_frames=0.0,
            collision_capsule_start=(0, 0, -1),
            collision_capsule_end=(0, 0, 1), collision_capsule_radius=1.0,
            collision_capsule_continuous=True, envelope=np.asarray((0, 1, 0)))
        self.assertLessEqual(result[1, 0], -1.0+1e-8)

    def test_exact_mesh_sweep_allows_departure_from_contact(self):
        triangle = np.asarray((((1, -1, -1), (1, 1, -1), (1, 0, 1)),), dtype=float)
        hit = sm._mesh_exact_swept_volume_hit(
            (2, 0, 0), (3, 0, 0), triangle, 0.0, False,
            volume_radius=1.0)
        self.assertIsNone(hit)

    def test_exact_mesh_sweep_accepts_inward_motion_from_clearance_contact(self):
        def box(x0, x1, y0, y1, z0, z1):
            vertices = (
                (x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
                (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1))
            faces = ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4),
                     (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7))
            return np.asarray([
                (vertices[a], vertices[b], vertices[c])
                for a, b, c, d in faces
                for a, b, c in ((a, b, c), (a, c, d))], dtype=float)

        cases = (
            (box(-0.5, 0.0, -1, 1, -1, 1), (0.1, 0, 0), (-1, 0, 0),
             0.1, 0.0, 0, 0.1),
            (box(0, 1, 0, 1, 0, 1), (-0.1, 0.4, 0.5), (2, 0.4, 0.5),
             0.0, 0.1, 0, -0.1),
            (box(-1, 1, -1, 1, -1, 1), (0, 0, 1.1), (0, 0, -2),
             0.0, 0.1, 2, 1.1))
        for triangles, previous, current, clearance, radius, axis, expected in cases:
            with self.subTest(previous=previous):
                hit = sm._mesh_exact_swept_volume_hit(
                    previous, current, triangles, clearance, True,
                    volume_radius=radius)
                self.assertIsNotNone(hit)
                self.assertAlmostEqual(hit[0][axis], expected, places=8)

        cube = cases[1][0]
        hit = sm._mesh_deforming_volume_sweep_hit(
            (-10, 0, 1.05), (22, 0, 1.05), cube, cube,
            0.1, True, volume_radius=0.0)
        self.assertIsNotNone(hit)

        cube = cases[2][0]
        segment_hit = sm._mesh_segment_hit(
            (1, 0, 0), (-2, 0, 0), cube, closed=True)
        self.assertIsNotNone(segment_hit)
        self.assertAlmostEqual(segment_hit[1][0], 1.0, places=12)
        exact_hit = sm._mesh_exact_swept_volume_hit(
            (1, 0, 0), (-2, 0, 0), cube, 0.0, True)
        self.assertIsNotNone(exact_hit)
        self.assertAlmostEqual(exact_hit[0][0], 1.0, places=12)

        translated = cube + np.asarray((0.0, 0.0, 0.2))
        velocity = sm._mesh_surface_velocity(
            (0, 0, 1.2), 2, cube, translated, 1.0)
        np.testing.assert_allclose(velocity, (0, 0, 0.2), atol=1e-12)

        tangent_point = (0, -1.3713906763541037, 0.7823757363928785)
        self.assertFalse(sm._mesh_inside(tangent_point, cube))
        state = sm.mesh_collision_state(
            (0.999999995, 0, 0), cube, clearance=0.1, closed=True)
        self.assertTrue(state[0])
        self.assertAlmostEqual(state[1][0], 1.1, places=8)

    def test_continuous_modes_require_their_collider(self):
        values = np.zeros((2, 3), dtype=float)
        settings = dict(dt=1.0, frequency=1.0, damping=0.0,
                        air_friction=0.0)
        with self.assertRaisesRegex(ValueError, 'requires a capsule'):
            sm.follow_world_vectors(
                values, (1.0,), collision_capsule_continuous=True,
                **settings)
        with self.assertRaisesRegex(ValueError, 'requires a mesh'):
            sm.follow_world_vectors(
                values, (1.0,), collision_mesh_continuous=True,
                collision_mesh_closed=True, **settings)

    def test_moving_sphere_contact_advances_remaining_sample_time(self):
        values = np.zeros((3, 3), dtype=float)
        centers = np.asarray(((-2, 0, 0), (2, 0, 0), (2, 0, 0)), dtype=float)
        kwargs = dict(dt=1.0, frequency=1.0, damping=0.0,
                      air_friction=0.0,
                      collision_sphere_trajectories=((centers, 0.5),),
                      collision_sphere_continuous=True)
        result, report = sm.follow_world_vectors(values, (1.0, 1.0), **kwargs)
        self.assertGreaterEqual(result[1, 0], 2.5-1e-10)
        self.assertGreater(report['continuous_collision_samples'], 0)
        published, _ = sm.apply_world_vector_follow(
            values, (0.0, 1.0, 2.0), strength=1.0, blend_frames=0.0,
            envelope=np.asarray((0.0, 1.0, 0.0)), **kwargs)
        self.assertGreaterEqual(published[1, 0], 2.5-1e-10)

    def test_moving_sphere_remainder_sweeps_the_other_spheres(self):
        values = np.zeros((2, 3), dtype=float)
        moving = np.asarray(((-2, 0, 0), (2, 0, 0)), dtype=float)
        stationary = np.asarray(((3, 0, 0), (3, 0, 0)), dtype=float)
        result, report = sm.follow_world_vectors(
            values, (1.0,), dt=1.0, frequency=1.0, damping=0.0,
            air_friction=0.0, restitution=1.0,
            collision_sphere_trajectories=((moving, 0.5), (stationary, 0.5)),
            collision_sphere_continuous=True)
        self.assertGreaterEqual(report['continuous_collision_samples'], 2)
        self.assertLessEqual(result[1, 0], 2.5+1e-10)

    def test_mixed_boolean_angular_acceleration_is_rejected(self):
        quaternions = np.tile((1.0, 0.0, 0.0, 0.0), (3, 1))
        with self.assertRaisesRegex(ValueError, 'booleans'):
            sm.follow_forced_quaternions(
                quaternions, (1.0, 1.0), dt=1/24, frequency=1.0,
                damping=1.0, air_friction=0.0, strength=1.0,
                envelope=(0.0, 1.0, 0.0),
                angular_accelerations=((True, 0, 0),)*3)

    def test_rotating_capsule_sweep_does_not_collapse_at_half_turn(self):
        hit = sm._capsule_trajectory_sweep_hit(
            (0, 10, 0), (0, 10, 0), (-1, 0, 0), (1, 0, 0), 0.1,
            (1, 0, 0), (-1, 0, 0), 0.1, 0.0)
        self.assertIsNone(hit)

    def test_moving_capsule_contact_advances_remaining_sample_time(self):
        values = np.zeros((3, 3), dtype=float)
        starts = np.asarray(((-2, -1, 0), (2, -1, 0), (2, -1, 0)), dtype=float)
        ends = np.asarray(((-2, 1, 0), (2, 1, 0), (2, 1, 0)), dtype=float)
        radii = np.full(3, 0.5, dtype=float)
        kwargs = dict(dt=1.0, frequency=1.0, damping=0.0,
                      air_friction=0.0,
                      collision_capsule_trajectories=(starts, ends, radii),
                      collision_capsule_continuous=True)
        result, report = sm.follow_world_vectors(values, (1.0, 1.0), **kwargs)
        self.assertGreaterEqual(result[1, 0], 2.5-1e-10)
        self.assertGreater(report['continuous_collision_samples'], 0)
        published, _ = sm.apply_world_vector_follow(
            values, (0.0, 1.0, 2.0), strength=1.0, blend_frames=0.0,
            envelope=np.asarray((0.0, 1.0, 0.0)), **kwargs)
        self.assertGreaterEqual(published[1, 0], 2.5-1e-10)

    def test_zero_strength_chain_report_keeps_compound_fields(self):
        values = np.zeros((3, 2, 3), dtype=float)
        _, report = sm.follow_world_vector_chain(
            values, (1.0, 1.0), dt=1/24, frequency=1.0, damping=1.0,
            air_friction=0.0, strength=0.0, envelope=(0.0, 1.0, 0.0),
            propagation=0.0, masses=(1.0, 1.0),
            accelerations=np.zeros((2, 3)))
        self.assertFalse(report['collision_compound_capsule'])
        self.assertFalse(report['collision_compound_mesh'])

    def test_follow_projects_overlapping_spheres_without_oscillation(self):
        values = np.zeros((2, 3), dtype=float)
        result, _ = sm.follow_world_vectors(
            values, (1,), dt=1/24, frequency=1.0, damping=1.0,
            air_friction=0.0,
            collision_spheres=(((-0.5, 0, 0), 1.0), ((0.5, 0, 0), 1.0)))
        self.assertGreaterEqual(np.linalg.norm(result[1]-(-0.5, 0, 0)), 1.0-1e-8)
        self.assertGreaterEqual(np.linalg.norm(result[1]-(0.5, 0, 0)), 1.0-1e-8)

    def test_moving_capsule_sweep_projects_against_final_sample(self):
        values = np.zeros((2, 3), dtype=float)
        starts = np.asarray(((-2, -1, 0), (0, -1, 0)), dtype=float)
        ends = np.asarray(((-2, 1, 0), (0, 1, 0)), dtype=float)
        result, _ = sm.follow_world_vectors(
            values, (1,), dt=1.0, frequency=1.0, damping=1.0,
            air_friction=0.0,
            collision_capsule_trajectories=(starts, ends, (1.0, 1.0)),
            collision_capsule_continuous=True)
        closest = sm._capsule_closest(result[1], starts[1], ends[1])
        self.assertGreaterEqual(np.linalg.norm(result[1]-closest), 1.0-1e-8)

    def test_vector_follow_sweeps_published_moving_sphere_blend(self):
        values = np.asarray(((-2, 0, 0), (2, 0, 0), (2, 0, 0)), dtype=float)
        result, _ = sm.apply_world_vector_follow(
            values, (0, 1, 2), dt=1.0, frequency=30.0, damping=0.0,
            air_friction=0.0, strength=0.1, blend_frames=0.0,
            collision_sphere_trajectories=((np.zeros((3, 3)), 1.0),),
            collision_sphere_continuous=True, envelope=np.asarray((0, 1, 0)))
        self.assertLessEqual(result[1, 0], -1.0+1e-8)

    def test_vector_follow_sweeps_published_mesh_blend(self):
        faces = (
            ((-.1,-1,-1),(-.1,1,-1),(-.1,1,1),(-.1,-1,1)),
            ((.1,-1,-1),(.1,-1,1),(.1,1,1),(.1,1,-1)),
            ((-.1,-1,-1),(-.1,-1,1),(.1,-1,1),(.1,-1,-1)),
            ((-.1,1,-1),(.1,1,-1),(.1,1,1),(-.1,1,1)),
            ((-.1,-1,-1),(.1,-1,-1),(.1,1,-1),(-.1,1,-1)),
            ((-.1,-1,1),(-.1,1,1),(.1,1,1),(.1,-1,1)),
        )
        triangles = np.asarray([triangle for face in faces for triangle in
                                ((face[0], face[1], face[2]),
                                 (face[0], face[2], face[3]))], dtype=float)
        values = np.asarray(((-2, 0, 0), (2, 0, 0), (2, 0, 0)), dtype=float)
        result, _ = sm.apply_world_vector_follow(
            values, (0, 1, 2), dt=1.0, frequency=30.0, damping=0.0,
            air_friction=0.0, strength=0.1, blend_frames=0.0,
            collision_mesh_triangles=triangles, collision_mesh_closed=True,
            collision_mesh_continuous=True, clearance=0.01,
            envelope=np.asarray((0, 1, 0)))
        self.assertLessEqual(result[1, 0], -0.11+1e-8)


if __name__ == '__main__':
    unittest.main(argv=[__file__])
