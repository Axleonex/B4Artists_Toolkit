"""Run the affected secondary-motion suites in a real Bforartists process."""
from pathlib import Path
import os
import sys
import unittest


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "training" / "b4artists_ml"))
sys.path.insert(0, str(ROOT / "tests"))
if os.environ.get("B4ML_PACKAGE"):
    sys.path.insert(0, os.environ["B4ML_PACKAGE"])

MODULES = (
    "test_b4artists_ml_secondary_motion",
    "test_b4artists_ml_secondary_chain_selection_v1",
    "test_b4artists_ml_secondary_external_acceleration_v1",
    "test_b4artists_ml_secondary_wind_velocity_v1",
    "test_b4artists_ml_secondary_velocity_impulse_v1",
    "test_b4artists_ml_secondary_control_loads_v1",
    "test_b4artists_ml_secondary_force_offset_torque_v1",
    "test_b4artists_ml_secondary_load_from_active_v1",
    "test_b4artists_ml_secondary_sphere_collision_v1",
    "test_b4artists_ml_secondary_multi_sphere_collision_v1",
    "test_b4artists_ml_secondary_moving_sphere_collision_v1",
    "test_b4artists_ml_secondary_sphere_fit_v1",
    "test_b4artists_ml_secondary_sphere_proxy_v1",
    "test_b4artists_ml_secondary_capsule_collision_v1",
    "test_b4artists_ml_secondary_self_collision_v1",
    "test_b4artists_ml_secondary_moving_mesh_collision_v1",
)
if not os.environ.get("B4ML_CAPSULE_REGRESSION"):
    MODULES += ("test_b4artists_ml_secondary_mesh_collision_v1",)


def main():
    suite = unittest.TestSuite(
        unittest.defaultTestLoader.loadTestsFromName(name) for name in MODULES)
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    print("B4ML_SECONDARY_AFFECTED_RESULT:",
          "PASS" if result.wasSuccessful() else "FAIL")
    raise SystemExit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
