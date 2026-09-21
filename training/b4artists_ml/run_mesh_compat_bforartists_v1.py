"""Run collision compatibility suites in a real Bforartists process."""
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
    "test_b4artists_ml_secondary_sphere_collision_v1",
    "test_b4artists_ml_secondary_moving_sphere_collision_v1",
    "test_b4artists_ml_secondary_capsule_collision_v1",
    "test_b4artists_ml_secondary_mesh_collision_v1",
)


def main():
    suite = unittest.TestSuite(
        unittest.defaultTestLoader.loadTestsFromName(name) for name in MODULES)
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    raise SystemExit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
