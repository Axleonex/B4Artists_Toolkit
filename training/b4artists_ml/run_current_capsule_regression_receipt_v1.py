"""Self-recording current-worktree capsule-compatible Bforartists regression run."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys
import time
import unittest

import bpy


ROOT = Path(__file__).resolve().parents[2]
if os.environ.get("B4ML_PACKAGE"):
    sys.path.insert(0, os.environ["B4ML_PACKAGE"])
sys.path.insert(0, str(ROOT / "training" / "b4artists_ml"))
sys.path.insert(0, str(ROOT / "tests"))

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
)


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _summary(result: unittest.TestResult, started: str, elapsed: float) -> dict:
    loaded_module = sys.modules.get("b4artists_ml.secondary_motion")
    loaded_package = sys.modules.get("b4artists_ml")
    return {
        "schema": "b4ml-current-capsule-regression-receipt-v1",
        "recorded_at": _utc(),
        "scope": "Current worktree capsule-compatible 14-suite Bforartists regression; not exact archive evidence.",
        "source_root": str(ROOT),
        "package_selector": os.environ.get("B4ML_PACKAGE", "<unset>"),
        "package_sha256": (
            _sha256(Path(os.environ["B4ML_PACKAGE"]))
            if os.environ.get("B4ML_PACKAGE")
            else None
        ),
        "import_provenance": {
            "package_file": str(getattr(loaded_package, "__file__", "<not-loaded>")),
            "secondary_motion_file": str(getattr(loaded_module, "__file__", "<not-loaded>")),
            "sys_path_prefix": [str(item) for item in sys.path[:8]],
        },
        "modules": list(MODULES),
        "started_at": started,
        "elapsed_seconds": round(elapsed, 3),
        "result": {
            "tests": result.testsRun,
            "passed": result.testsRun - len(result.failures) - len(result.errors),
            "failed": len(result.failures),
            "errors": len(result.errors),
            "skipped": len(getattr(result, "skipped", ())),
            "was_successful": result.wasSuccessful(),
            "failure_ids": [case.id() for case, _text in result.failures],
            "error_ids": [case.id() for case, _text in result.errors],
            "failure_details": [
                {"test": case.id(), "traceback": text}
                for case, text in result.failures
            ],
            "error_details": [
                {"test": case.id(), "traceback": text}
                for case, text in result.errors
            ],
        },
        "host_boundary": {
            "runtime": "Bforartists 5.1.0 / Blender 5.2.0 Alpha",
            "known_shutdown_fault": "The host may exit with ucrtbase.dll access violation after the receipt is written.",
            "exact_archive_evidence": "docs/b4artists_ml/capsule-exact-revalidation-v2.json",
        },
        "claim_boundary": "This receipt does not replace exact-package binding, foreground lifecycle, independent animator review, learned temporal quality, or Cascadeur comparison evidence.",
    }


def main() -> int:
    started = _utc()
    began = time.perf_counter()
    suite = unittest.TestSuite(
        unittest.defaultTestLoader.loadTestsFromName(name) for name in MODULES
    )
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    payload = _summary(result, started, time.perf_counter() - began)
    output = Path(os.environ.get(
        "B4ML_CAPSULE_OUTPUT",
        str(ROOT / "training" / "b4artists_ml" / "results" / "current-capsule-regression-v2.json"),
    ))
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print("B4ML_CURRENT_CAPSULE_REGRESSION_RECEIPT:", str(output))
    print(json.dumps(payload["result"], sort_keys=True))
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
