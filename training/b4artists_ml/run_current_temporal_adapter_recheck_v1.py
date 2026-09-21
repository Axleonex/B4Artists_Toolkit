"""Record the current temporal math and real-rig adapter regression in Bforartists.

This is current-worktree evidence only.  It does not train or promote a model,
replace frozen package evidence, or make an animator-quality claim.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import time
import unittest


ROOT = Path(__file__).resolve().parents[2]
TRAINING = ROOT / "training" / "b4artists_ml"
TESTS = ROOT / "tests"
sys.path[:0] = [str(ROOT), str(TRAINING), str(TESTS)]

MODULES = (
    "test_b4artists_ml_temporal_runtime_math_v1",
    "test_b4artists_ml_rig_observations",
)
OUTPUT = TRAINING / "results" / "current-temporal-adapter-recheck-v1.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def main() -> int:
    import bpy

    started = _utc()
    began = time.perf_counter()
    suite = unittest.TestSuite(
        unittest.defaultTestLoader.loadTestsFromName(name) for name in MODULES
    )
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    report = {
        "schema": "b4ml-current-temporal-adapter-recheck-v1",
        "recorded_at": _utc(),
        "started_at": started,
        "elapsed_seconds": round(time.perf_counter() - began, 3),
        "scope": (
            "Current-worktree authored temporal math and eight-profile real-rig "
            "observation/semantic hierarchy regression."
        ),
        "host": {
            "application": "Bforartists",
            "version": bpy.app.version_string,
            "build_hash": bpy.app.build_hash.decode("ascii", errors="replace"),
            "process_exit_recorded_by_parent": False,
            "known_shutdown_fault": (
                "The installed alpha host may exit through ucrtbase.dll after "
                "this receipt and passing assertions are written."
            ),
        },
        "modules": list(MODULES),
        "result": {
            "tests": result.testsRun,
            "passed": result.testsRun - len(result.failures) - len(result.errors),
            "failed": len(result.failures),
            "errors": len(result.errors),
            "skipped": len(getattr(result, "skipped", ())),
            "was_successful": result.wasSuccessful(),
            "failure_ids": [case.id() for case, _text in result.failures],
            "error_ids": [case.id() for case, _text in result.errors],
        },
        "sources": {
            path.relative_to(ROOT).as_posix(): _sha256(path)
            for path in (
                Path(__file__).resolve(),
                ROOT / "b4artists_ml" / "temporal_observations.py",
                TRAINING / "rig_observations.py",
                TRAINING / "semantic_hierarchy_packet_v1.py",
                TESTS / "test_b4artists_ml_temporal_runtime_math_v1.py",
                TESTS / "test_b4artists_ml_rig_observations.py",
            )
        },
        "claim_boundary": {
            "current_worktree_only": True,
            "exact_package_qualified": False,
            "learned_temporal_quality_verified": False,
            "model_trained": False,
            "model_promoted": False,
            "independent_animator_usability_verified": False,
            "cascadeur_parity_verified": False,
            "full_goal_complete": False,
        },
    }
    OUTPUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("B4ML_CURRENT_TEMPORAL_ADAPTER_RECEIPT:", OUTPUT)
    print(json.dumps(report["result"], sort_keys=True))
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
