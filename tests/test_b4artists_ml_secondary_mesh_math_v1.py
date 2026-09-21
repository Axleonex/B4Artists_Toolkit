"""Static arbitrary triangle-mesh collision for deterministic secondary motion."""
import importlib.util
from pathlib import Path
import unittest

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "b4artists_ml_secondary_math_mesh", ROOT / "b4artists_ml" / "secondary_math.py")
sm = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(sm)


def cube_triangles():
    faces = (
        ((-1, -1, -1), (-1, 1, -1), (-1, 1, 1), (-1, -1, 1)),
        ((1, -1, -1), (1, -1, 1), (1, 1, 1), (1, 1, -1)),
        ((-1, -1, -1), (-1, -1, 1), (1, -1, 1), (1, -1, -1)),
        ((-1, 1, -1), (1, 1, -1), (1, 1, 1), (-1, 1, 1)),
        ((-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1)),
        ((-1, -1, 1), (-1, 1, 1), (1, 1, 1), (1, -1, 1)),
    )
    return np.asarray([triangle for face in faces
                       for triangle in ((face[0], face[1], face[2]),
                                        (face[0], face[2], face[3]))], dtype=float)


class SecondaryMeshMathTests(unittest.TestCase):
    def test_validation_rejects_degenerate_and_hostile_meshes(self):
        hostile = (
            np.zeros((1, 3, 3)),
            np.full((1, 3, 3), np.nan),
            np.zeros((1, 3, 2)),
            np.ones((sm.MAX_MESH_COLLISION_TRIANGLES + 1, 3, 3)),
        )
        for triangles in hostile:
            with self.subTest(shape=triangles.shape):
                with self.assertRaises(ValueError):
                    sm.validate_mesh_triangles(triangles)

    def test_closed_mesh_reports_inside_and_clearance(self):
        triangles = cube_triangles()
        state = sm.mesh_collision_state((0, 0, 0), triangles, .2, True)
        self.assertTrue(state[0])
        self.assertTrue(state[5])
        self.assertAlmostEqual(state[3], 1.2, places=8)
        self.assertAlmostEqual(np.linalg.norm(np.asarray(state[1])), 1.2, places=8)

    def test_closed_mesh_keeps_outside_points_and_projects_clearance(self):
        triangles = cube_triangles()
        outside = sm.mesh_collision_state((2, 0, 0), triangles, .2, True)
        self.assertFalse(outside[0])
        near = sm.mesh_collision_state((1.1, 0, 0), triangles, .2, True)
        self.assertTrue(near[0])
        self.assertAlmostEqual(near[1][0], 1.2, places=8)
        self.assertFalse(near[5])

    def test_open_mesh_is_a_two_sided_sampled_surface(self):
        triangles = np.asarray((((-1, -1, 0), (1, -1, 0), (0, 1, 0)),), dtype=float)
        state = sm.mesh_collision_state((0, 0, .1), triangles, .25, False)
        self.assertTrue(state[0])
        self.assertAlmostEqual(state[1][2], .25, places=8)

    def test_closed_volume_radius_extends_mesh_exclusion_boundary(self):
        triangles = cube_triangles()
        state = sm.mesh_collision_state(
            (1.1, 0, 0), triangles, clearance=.05, closed=True, volume_radius=.15)
        self.assertTrue(state[0])
        self.assertAlmostEqual(state[3], .10, places=8)
        self.assertAlmostEqual(state[1][0], 1.2, places=8)
        clear = sm.mesh_collision_state(
            (1.3, 0, 0), triangles, clearance=.05, closed=True, volume_radius=.15)
        self.assertFalse(clear[0])

    def test_volume_radius_is_finite_and_nonnegative(self):
        triangles = cube_triangles()
        for radius in (-.1, np.nan, np.inf, True):
            with self.subTest(radius=radius):
                with self.assertRaises(ValueError):
                    sm.mesh_collision_state((1.1, 0, 0), triangles, closed=True,
                                            volume_radius=radius)

    def test_follow_projects_finite_control_volume(self):
        values = np.zeros((4, 3))
        result, report = sm.follow_world_vectors(
            values, np.ones(3), dt=1/24, frequency=1., damping=.5,
            air_friction=0., collision_mesh_triangles=cube_triangles(),
            collision_mesh_closed=True, clearance=.05,
            collision_mesh_volume_radius=.15)
        self.assertGreater(report["collision_samples"], 0)
        for point in result[1:]:
            state = sm.mesh_collision_state(
                point, cube_triangles(), .05, True, volume_radius=.15)
            self.assertFalse(state[0])

    def test_continuous_closed_mesh_catches_segment_crossing(self):
        hit = sm._mesh_segment_hit((2, 0, 0), (-2, 0, 0), cube_triangles())
        self.assertIsNotNone(hit)
        self.assertAlmostEqual(hit[0], .25, places=8)
        self.assertAlmostEqual(hit[1][0], 1.0, places=8)
        self.assertGreater(hit[2][0], 0.99)
        values = np.asarray(((2, 0, 0), (-2, 0, 0)), dtype=float)
        result, report = sm.follow_world_vectors(
            values, (1,), dt=1/24, frequency=20., damping=.5,
            air_friction=0., collision_mesh_triangles=cube_triangles(),
            collision_mesh_closed=True, clearance=.1,
            collision_mesh_continuous=True)
        self.assertGreater(report["collision_samples"], 0)
        self.assertGreaterEqual(result[1][0], .99)

    def test_exact_swept_volume_catches_near_face_without_center_crossing(self):
        triangles = cube_triangles()
        exact = sm._mesh_exact_swept_volume_hit(
            (-2., 0., 1.1), (2., 0., 1.1), triangles, .0, True,
            volume_radius=.2)
        self.assertIsNotNone(exact)
        self.assertAlmostEqual(np.linalg.norm(exact[1]), 1.0, places=8)
        self.assertGreater(exact[0][2], 1.0)
        values = np.asarray(((-2., 0., 1.1), (2., 0., 1.1)), dtype=float)
        result, report = sm.follow_world_vectors(
            values, (1,), dt=1/24, frequency=20., damping=.5,
            air_friction=0., collision_mesh_triangles=triangles,
            collision_mesh_closed=True, collision_mesh_volume_radius=.2,
            collision_mesh_continuous=True)
        self.assertGreater(report["collision_samples"], 0)
        self.assertFalse(sm.mesh_collision_state(
            result[1], triangles, closed=True, volume_radius=.2)[0])
        self.assertGreaterEqual(
            np.linalg.norm(result[1] - np.asarray((-1., 0., 1.))), .2 - 1e-8)

    def test_continuous_mesh_rejects_open_and_sweeps_deforming_inputs(self):
        values = np.zeros((2, 3))
        open_mesh = np.asarray((((-1, -1, 0), (1, -1, 0), (0, 1, 0)),), dtype=float)
        kwargs = dict(dt=1/24, frequency=1., damping=.5, air_friction=0.,
                      collision_mesh_triangles=open_mesh,
                      collision_mesh_continuous=True)
        with self.assertRaisesRegex(ValueError, "closed mesh"):
            sm.follow_world_vectors(values, (1,), **kwargs)
        moving = np.stack((cube_triangles() - (2., 0., 0.),
                           cube_triangles() + (2., 0., 0.)))
        result, report = sm.follow_world_vectors(
            values, (1,), dt=1/24, frequency=1., damping=.5, air_friction=0.,
            collision_mesh_trajectories=moving,
            collision_mesh_closed=True, clearance=.1,
            collision_mesh_continuous=True)
        self.assertGreater(report["collision_samples"], 0)
        self.assertFalse(sm.mesh_collision_state(
            result[1], moving[-1], .1, True)[0])

    def test_deforming_sweep_catches_mesh_motion_with_stationary_control(self):
        base = cube_triangles()
        trajectory = np.stack((base - (2., 0., 0.), base + (2., 0., 0.)))
        values = np.zeros((2, 3))
        result, report = sm.follow_world_vectors(
            values, (1,), dt=1/24, frequency=1., damping=.5, air_friction=0.,
            collision_mesh_trajectories=trajectory,
            collision_mesh_closed=True, clearance=.1,
            collision_mesh_continuous=True)
        self.assertGreater(report["collision_samples"], 0)
        self.assertGreater(float(np.linalg.norm(result[1])), 0.05)

    def test_deforming_volume_sweep_uses_bounded_static_volume_intervals(self):
        base = cube_triangles()
        trajectory = np.stack((base - (2., 0., 0.), base + (2., 0., 0.)))
        values = np.zeros((2, 3))
        result, report = sm.follow_world_vectors(
            values, (1,), dt=1/24, frequency=1., damping=.5, air_friction=0.,
            collision_mesh_trajectories=trajectory,
            collision_mesh_closed=True, clearance=0.0,
            collision_mesh_volume_radius=.2,
            collision_mesh_continuous=True)
        self.assertGreater(report["collision_samples"], 0)
        self.assertGreater(float(np.linalg.norm(result[1])), 0.05)
        self.assertFalse(sm.mesh_collision_state(
            result[1], trajectory[-1], 0.0, True, volume_radius=.2)[0])

    def test_shape_deforming_volume_sweep_uses_bounded_static_volume_intervals(self):
        base = cube_triangles()
        deformed = base.copy()
        deformed[:, :, 2] *= 1.4
        trajectory = np.stack((base + (100., 0., 0.), deformed + (100., 0., 0.)))
        values = np.zeros((2, 3))
        result, report = sm.follow_world_vectors(
            values, (1,), dt=1/24, frequency=1., damping=.5, air_friction=0.,
            collision_mesh_trajectories=trajectory,
            collision_mesh_closed=True, clearance=0.0,
            collision_mesh_volume_radius=.2,
            collision_mesh_continuous=True)
        self.assertEqual(report["collision_samples"], 0)
        np.testing.assert_allclose(result, values, atol=1e-8)

    def test_follow_projects_inside_points_and_reports_contacts(self):
        values = np.zeros((4, 3))
        result, report = sm.follow_world_vectors(
            values, np.ones(3), dt=1/24, frequency=1., damping=.5,
            air_friction=0., collision_mesh_triangles=cube_triangles(),
            collision_mesh_closed=True, clearance=.2)
        self.assertGreater(report["collision_samples"], 0)
        for point in result[1:]:
            state = sm.mesh_collision_state(point, cube_triangles(), .2, True)
            self.assertFalse(state[0])

    def test_deforming_mesh_trajectory_uses_the_current_sample(self):
        base = cube_triangles()
        deformed = base.copy()
        deformed[:, :, 2] *= 1.5
        trajectory = np.stack((base, deformed, base), axis=0)
        validated = sm.validate_mesh_trajectories(trajectory, 3)
        np.testing.assert_array_equal(validated, trajectory)
        values = np.zeros((3, 3))
        result, report = sm.follow_world_vectors(
            values, np.ones(2), dt=1/24, frequency=1., damping=.5,
            air_friction=0., collision_mesh_trajectories=trajectory,
            collision_mesh_closed=True, clearance=.2)
        self.assertEqual(report["collision_samples"], 2)
        self.assertFalse(sm.mesh_collision_state(result[1], deformed, .2, True)[0])
        self.assertFalse(sm.mesh_collision_state(result[2], base, .2, True)[0])

    def test_mesh_trajectory_rejects_wrong_sample_count_and_degenerate_sample(self):
        base = cube_triangles()
        with self.assertRaises(ValueError):
            sm.validate_mesh_trajectories(np.stack((base, base)), 3)
        bad = np.stack((base, base), axis=0)
        bad[1, 0, 2] = bad[1, 0, 1]
        with self.assertRaises(ValueError):
            sm.validate_mesh_trajectories(bad, 2)

    def test_mesh_input_is_exclusive_with_planar_and_sphere_inputs(self):
        values = np.zeros((2, 3))
        kwargs = dict(dt=1/24, frequency=1., damping=.5, air_friction=0.,
                      collision_mesh_triangles=cube_triangles(), collision_mesh_closed=True)
        with self.assertRaisesRegex(ValueError, "collision inputs"):
            sm.follow_world_vectors(values, (1.,), collision_sphere_center=(0, 0, 0),
                                    collision_sphere_radius=.25, **kwargs)
        with self.assertRaisesRegex(ValueError, "one planar"):
            sm.follow_world_vectors(values, (1,), collision_point=(0, 0, 0),
                                    collision_normal=(0, 0, 1), **kwargs)

    def test_self_collision_separates_equal_control_volumes(self):
        points = np.asarray(((0., 0., 0.), (.1, 0., 0.), (0., .1, 0.)))
        result, report = sm.resolve_self_collision_positions(points, .1, .02)
        self.assertGreater(report["collision_pairs"], 0)
        for first in range(len(result)-1):
            for second in range(first+1, len(result)):
                self.assertGreaterEqual(
                    np.linalg.norm(result[second]-result[first]), .22-1e-8)
        self.assertGreater(report["max_raw_penetration"], 0.)
        self.assertEqual(report["max_penetration_after"], 0.)

    def test_self_collision_rejects_hostile_inputs(self):
        for points, radius, clearance in (
                (np.zeros((1, 3)), .1, 0.),
                (np.zeros((2, 3)), 0., 0.),
                (np.zeros((2, 3)), .1, -1.),
                (np.asarray(((0., 0., 0.), (np.nan, 0., 0.))), .1, 0.)):
            with self.subTest(radius=radius, clearance=clearance):
                with self.assertRaises(ValueError):
                    sm.resolve_self_collision_positions(points, radius, clearance)


if __name__ == "__main__":
    unittest.main(verbosity=2)
