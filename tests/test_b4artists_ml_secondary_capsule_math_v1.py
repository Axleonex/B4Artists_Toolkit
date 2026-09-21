"""Static analytic capsule collision for deterministic secondary motion."""
import os
import importlib.util
from pathlib import Path
import unittest

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
if os.environ.get("B4ML_PACKAGE"):
    from b4artists_ml import secondary_math as sm
else:
    SPEC = importlib.util.spec_from_file_location(
        "b4artists_ml_secondary_math_capsule", ROOT / "b4artists_ml" / "secondary_math.py")
    sm = importlib.util.module_from_spec(SPEC)
    SPEC.loader.exec_module(sm)


class SecondaryCapsuleMathTests(unittest.TestCase):
    def test_validation_rejects_degenerate_and_hostile_endpoints(self):
        hostile = (
            ((0, 0, 0), (0, 0, 0), 0.1),
            ((0, 0), (0, 0, 1), 0.1),
            ((0, 0, 0), (0, 0, 1), True),
            ((0, 0, float("nan")), (0, 0, 1), 0.1),
            ((0, 0, 0), (0, 0, 1), 0.0),
            ((0, 0, 0), (0, 0, 1), 1001.0),
        )
        for start, end, radius in hostile:
            with self.subTest(start=start, end=end, radius=radius):
                with self.assertRaises(ValueError):
                    sm.validate_capsule_collider(start, end, radius)

    def test_centerline_degeneracy_uses_stable_radial_axis(self):
        values = np.tile((0.0, 0.0, 0.0), (4, 1))
        result, report = sm.follow_world_vectors(
            values, np.ones(3), dt=1 / 24, frequency=1.0, damping=0.5,
            air_friction=0.0, collision_capsule_start=(0, 0, -1),
            collision_capsule_end=(0, 0, 1), collision_capsule_radius=0.5)
        np.testing.assert_array_equal(result[1:], np.tile((0.5, 0.0, 0.0), (3, 1)))
        self.assertEqual(report["collision_samples"], 3)

    def test_capsule_excludes_segment_and_end_cap_points(self):
        values = np.asarray(((0.0, 0.0, 0.0), (0.1, 0.0, 0.0),
                             (0.0, 0.0, 1.8), (0.0, 0.0, 2.0)))
        result, report = sm.apply_world_vector_follow(
            values, (1.0, 2.0, 3.0, 4.0), dt=1 / 24, frequency=1.0,
            damping=0.5, air_friction=0.0, strength=0.0, blend_frames=0.0,
            collision_capsule_start=(0, 0, -1), collision_capsule_end=(0, 0, 1),
            collision_capsule_radius=0.5, envelope=np.ones(4))
        for point in result:
            segment = np.asarray((0.0, 0.0, min(1.0, max(-1.0, point[2]))))
            self.assertGreaterEqual(np.linalg.norm(point - segment), 0.5 - 1e-10)
        self.assertGreater(report["max_penetration_before"], 0.0)
        self.assertLessEqual(report["max_penetration_after"], 1e-10)

    def test_capsule_sweep_finds_first_crossing_between_clear_samples(self):
        swept = sm._capsule_sweep_hit(
            (-2.0, 0.0, 0.0), (2.0, 0.0, 0.0),
            (0.0, 0.0, -1.0), (0.0, 0.0, 1.0), 0.5, 0.0,
            ((1.0, 0.0, 0.0),))
        self.assertIsNotNone(swept)
        projected, normal, penetration, alpha = swept
        self.assertAlmostEqual(alpha, 0.375, places=10)
        np.testing.assert_allclose(projected, (-0.5, 0.0, 0.0), atol=1e-10)
        np.testing.assert_allclose(normal, (-1.0, 0.0, 0.0), atol=1e-10)
        self.assertLessEqual(penetration, 1e-10)

    def test_capsule_sweep_rejects_clear_segment(self):
        self.assertIsNone(sm._capsule_sweep_hit(
            (-2.0, 2.0, 0.0), (2.0, 2.0, 0.0),
            (0.0, 0.0, -1.0), (0.0, 0.0, 1.0), 0.5, 0.0))

    def test_capsule_trajectory_validation_requires_stable_finite_samples(self):
        starts = ((0.0, 0.0, -1.0), (0.1, 0.0, -1.0), (0.2, 0.0, -1.0))
        ends = ((0.0, 0.0, 1.0), (0.1, 0.0, 1.0), (0.2, 0.0, 1.0))
        values = sm.validate_capsule_trajectories((starts, ends, 0.5), 3)
        self.assertEqual(values[0].shape, (3, 3))
        np.testing.assert_array_equal(values[2], np.full(3, 0.5))
        with self.assertRaises(ValueError):
            sm.validate_capsule_trajectories((starts, ends, (0.5, 0.5)), 3)
        with self.assertRaises(ValueError):
            sm.validate_capsule_trajectories((starts, starts, 0.5), 3)

    def test_moving_capsule_sweep_catches_bounded_interpolated_contact(self):
        swept = sm._capsule_trajectory_sweep_hit(
            (-2.0, 0.0, 0.0), (2.0, 0.0, 0.0),
            (0.0, 0.0, -1.0), (0.0, 0.0, 1.0), 0.5,
            (0.0, 0.0, -1.0), (0.0, 0.0, 1.0), 0.5, 0.0,
            ((1.0, 0.0, 0.0),))
        self.assertIsNotNone(swept)
        projected, normal, penetration, alpha = swept
        np.testing.assert_allclose(projected, (-0.5, 0.0, 0.0), atol=1e-10)
        np.testing.assert_allclose(normal, (-1.0, 0.0, 0.0), atol=1e-10)
        self.assertGreaterEqual(alpha, 0.0)
        self.assertLessEqual(alpha, 1.0)
        self.assertLessEqual(penetration, 1e-10)

    def test_moving_capsule_relative_sweep_catches_surface_crossing_stationary_point(self):
        swept = sm._capsule_trajectory_sweep_hit(
            (0.0, 0.0, 0.0), (0.0, 0.0, 0.0),
            (2.0, 0.0, -1.0), (2.0, 0.0, 1.0), 0.25,
            (-2.0, 0.0, -1.0), (-2.0, 0.0, 1.0), 0.25, 0.0,
            ((1.0, 0.0, 0.0),))
        self.assertIsNotNone(swept)
        projected, normal, penetration, alpha = swept
        self.assertGreaterEqual(alpha, 0.0)
        self.assertLessEqual(alpha, 1.0)
        self.assertLessEqual(penetration, 0.25 + 1e-10)
        self.assertGreater(abs(float(normal[0])), 0.9)
        self.assertLessEqual(abs(float(projected[0])), 0.25 + 1e-10)

    def test_moving_capsule_world_follow_uses_relative_velocity_and_clearance(self):
        values = np.asarray(((0.0, 0.0, 0.0), (1.5, 0.0, 0.0)))
        trajectories = (
            ((0.0, 0.0, -1.0), (0.0, 0.0, -1.0)),
            ((0.0, 0.0, 1.0), (0.0, 0.0, 1.0)),
            (0.5, 0.5),
        )
        result, report = sm.follow_world_vectors(
            values, (1.0,), dt=1 / 24, frequency=10.0, damping=0.5,
            air_friction=0.0, collision_capsule_trajectories=trajectories,
            collision_capsule_continuous=True)
        np.testing.assert_allclose(result[1], (0.5, 0.0, 0.0), atol=1e-10)
        self.assertEqual(report["collision_samples"], 1)
        projected, metrics = sm.apply_world_vector_follow(
            values, (1.0, 2.0), dt=1 / 24, frequency=1.0, damping=0.5,
            air_friction=0.0, strength=0.0, blend_frames=0.0,
            collision_capsule_trajectories=trajectories, envelope=np.ones(2))
        self.assertLessEqual(metrics["max_penetration_after"], 1e-10)
        np.testing.assert_allclose(projected[0], (0.5, 0.0, 0.0), atol=1e-10)

    def test_follow_world_vectors_integrates_a_capsule_moving_across_stationary_control(self):
        trajectories = (
            ((2.0, 0.0, -1.0), (-2.0, 0.0, -1.0)),
            ((2.0, 0.0, 1.0), (-2.0, 0.0, 1.0)),
            (0.25, 0.25),
        )
        result, report = sm.follow_world_vectors(
            np.asarray(((0.0, 0.0, 0.0), (0.0, 0.0, 0.0))), (1.0,),
            dt=1 / 24, frequency=1.0, damping=0.5, air_friction=0.0,
            collision_capsule_trajectories=trajectories,
            collision_capsule_continuous=True)
        self.assertEqual(report["collision_samples"], 1)
        self.assertTrue(np.isfinite(result).all())
        np.testing.assert_allclose(result[1], (0.25, 0.0, 0.0), atol=1e-10)

    def test_follow_world_vectors_uses_capsule_sweep_between_samples(self):
        values = np.asarray(((-2.0, 0.0, 0.0), (2.0, 0.0, 0.0)))
        result, report = sm.follow_world_vectors(
            values, (1.0,), dt=1 / 24, frequency=10.0, damping=0.5,
            air_friction=0.0, collision_capsule_start=(0, 0, -1),
            collision_capsule_end=(0, 0, 1), collision_capsule_radius=0.5,
            collision_capsule_continuous=True)
        np.testing.assert_allclose(result[1], (-0.5, 0.0, 0.0), atol=1e-10)
        self.assertEqual(report["collision_samples"], 1)

    def test_capsule_input_is_exclusive_with_sphere_and_plane(self):
        values = np.zeros((2, 3))
        kwargs = dict(dt=1 / 24, frequency=1.0, damping=0.5, air_friction=0.0,
                      collision_capsule_start=(0, 0, -1),
                      collision_capsule_end=(0, 0, 1), collision_capsule_radius=0.5)
        with self.assertRaisesRegex(ValueError, "spherical or capsule"):
            sm.follow_world_vectors(values, (1.0,), collision_sphere_center=(0, 0, 0),
                                    collision_sphere_radius=0.25, **kwargs)
        with self.assertRaisesRegex(ValueError, "planar, spherical, or capsule"):
            sm.follow_world_vectors(values, (1.0,), collision_point=(0, 0, 0),
                                    collision_normal=(0, 0, 1), **kwargs)


if __name__ == "__main__":
    unittest.main(verbosity=2)
