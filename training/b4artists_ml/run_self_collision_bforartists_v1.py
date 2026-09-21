"""Run the selected-control self-collision binding suite in Bforartists."""
from pathlib import Path
import os
import sys
import unittest


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "training" / "b4artists_ml"))
sys.path.insert(0, str(ROOT / "tests"))
if os.environ.get("B4ML_PACKAGE"):
    sys.path.insert(0, os.environ["B4ML_PACKAGE"])


def main():
    suite = unittest.defaultTestLoader.loadTestsFromName(
        "test_b4artists_ml_secondary_self_collision_v1")
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    raise SystemExit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
