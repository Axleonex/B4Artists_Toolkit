"""Run the secondary-math suite in a real Bforartists process."""

from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))


def main():
    suite = unittest.defaultTestLoader.loadTestsFromName(
        "test_b4artists_ml_secondary_math")
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    print("B4ML_SECONDARY_MATH_RESULT:",
          "PASS" if result.wasSuccessful() else "FAIL")
    raise SystemExit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
