"""Run host-independent math suites against an exact add-on ZIP."""

from __future__ import annotations

import hashlib
import json
import os
from importlib import resources
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(os.environ["B4ML_PACKAGE"]).resolve()
TAG = os.environ.get("B4ML_MATH_TAG", "exact-package-v0.37.47-focused-secondary-math")
OUTPUT = ROOT / "training" / "b4artists_ml" / "results" / f"{TAG}.json"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    if PACKAGE.suffix.lower() != ".zip" or not PACKAGE.is_file():
        raise RuntimeError("B4ML_PACKAGE must name an exact ZIP archive")
    sys.path[:0] = [str(PACKAGE), str(ROOT)]
    suites = [
        unittest.defaultTestLoader.loadTestsFromName(
            "tests.test_b4artists_ml_secondary_math.SecondaryMathTests"),
        unittest.defaultTestLoader.loadTestsFromName(
            "tests.test_b4artists_ml_secondary_capsule_math_v1.SecondaryCapsuleMathTests"),
    ]
    suite = unittest.TestSuite(suites)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    loaded_package = sys.modules.get("b4artists_ml")
    package_origin = str(getattr(loaded_package, "__file__", "")).replace("\\", "/")
    expected_prefix = str(PACKAGE).replace("\\", "/") + "/"
    if not package_origin.startswith(expected_prefix):
        raise RuntimeError("Addon was not imported from the exact ZIP: " + package_origin)
    runtime = {
        "b4artists_ml/secondary_math.py": sha256_bytes(
            resources.files("b4artists_ml").joinpath("secondary_math.py").read_bytes())
    }
    record = {
        "schema": "b4ml-exact-package-unittest-v1",
        "suite": "test_b4artists_ml_secondary_math + test_b4artists_ml_secondary_capsule_math_v1",
        "class_name": "SecondaryMathTests + SecondaryCapsuleMathTests",
        "tests": result.testsRun,
        "assertions_passed": result.wasSuccessful(),
        "failures": [case.id() for case, _text in result.failures],
        "errors": [case.id() for case, _text in result.errors],
        "skipped": [case.id() for case, _reason in result.skipped],
        "runtime_sha256": runtime,
        "package": str(PACKAGE),
        "package_sha256": hashlib.sha256(PACKAGE.read_bytes()).hexdigest(),
        "package_import_origin": package_origin,
        "host": "CPython host-independent math",
    }
    OUTPUT.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(record, sort_keys=True))
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
