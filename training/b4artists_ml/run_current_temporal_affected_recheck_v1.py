"""Run the complete affected temporal matrix in isolated Bforartists hosts."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time


ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "training" / "b4artists_ml" / "results"
OUTPUT = RESULTS / "current-temporal-affected-recheck-v1.json"
BFORARTISTS = Path(os.environ.get("B4ML_BFORARTISTS", r"X:\5.1.0\bforartists.exe"))
MARKER = "B4ML_TEMPORAL_AFFECTED_RESULT "
CASES = (
    ("test_b4artists_ml_temporal_preview_v1", "TemporalPreviewTests", 10),
    ("test_b4artists_ml_temporal_runtime_v1", "RuntimeTemporalTests", 8),
    ("test_b4artists_ml_temporal_private_v1", "PrivateTemporalTests", 10),
    ("test_b4artists_ml_temporal_cooperative", "CooperativeTemporalTests", 11),
    ("test_b4artists_ml_temporal_cooperative_pipeline", "CooperativePipelineTests", 15),
    ("test_b4artists_ml_temporal_observer_cooperative", "CooperativeObservationTests", 3),
    ("test_b4artists_ml_temporal_projection", "TemporalProjectionTests", 15),
    ("test_b4artists_ml_anchor_observations", "AnchorObservationTests", 9),
)
SUPPORT_SOURCES = (
    "training/b4artists_ml/temporal_projection.py",
    "training/b4artists_ml/temporal_cooperative_v1.py",
    "training/b4artists_ml/rig_observations.py",
    "training/b4artists_ml/semantic_motion_data.py",
    "tests/test_b4artists_ml_temporal_preview_v1.py",
    "tests/test_b4artists_ml_temporal_runtime_v1.py",
    "tests/test_b4artists_ml_temporal_private_v1.py",
    "tests/test_b4artists_ml_temporal_cooperative.py",
    "tests/test_b4artists_ml_temporal_cooperative_pipeline.py",
    "tests/test_b4artists_ml_temporal_observer_cooperative.py",
    "tests/test_b4artists_ml_temporal_projection.py",
    "tests/test_b4artists_ml_anchor_observations.py",
    "tests/test_b4artists_ml_posing.py",
    "tests/test_b4artists_ml_imported_humanoids.py",
    "tests/test_b4artists_ml_rig_observations.py",
    "training/b4artists_ml/run_current_temporal_affected_recheck_v1.py",
    "training/b4artists_ml/check_current_temporal_affected_recheck_v1.py",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _expression(module: str, class_name: str) -> str:
    paths = [str(ROOT / "tests"), str(ROOT), str(ROOT / "training" / "b4artists_ml")]
    return (
        "import sys,unittest,json;"
        "sys.argv=['bforartists'];"
        f"sys.path[:0]={paths!r};"
        f"import {module} as selected;"
        "result=unittest.TextTestRunner(verbosity=2).run("
        f"unittest.defaultTestLoader.loadTestsFromTestCase(selected.{class_name}));"
        f"print({MARKER!r}+json.dumps({{'module':{module!r},"
        "'tests':result.testsRun,'failures':len(result.failures),"
        "'errors':len(result.errors),'skipped':len(result.skipped),"
        "'passed':result.testsRun-len(result.failures)-len(result.errors)-len(result.skipped),"
        "'successful':result.wasSuccessful()}),flush=True)"
    )


def _run_case(module: str, class_name: str, expected: int) -> dict:
    started = time.perf_counter()
    try:
        completed = subprocess.run(
            [str(BFORARTISTS), "--background", "--factory-startup", "--python-expr",
             _expression(module, class_name)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env={**os.environ, "B4ML_RUN_LABEL": "temporal-affected-" + module},
            check=False,
            timeout=600,
        )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(module + " exceeded the 600-second host limit") from exc
    combined = completed.stdout + "\n" + completed.stderr
    matches = re.findall(re.escape(MARKER) + r"(\{[^\r\n]+\})", combined)
    if len(matches) != 1:
        raise RuntimeError(module + " did not emit exactly one affected result marker")
    result = json.loads(matches[0])
    if result != {
        "module": module,
        "tests": expected,
        "failures": 0,
        "errors": 0,
        "skipped": 0,
        "passed": expected,
        "successful": True,
    }:
        raise RuntimeError(module + " assertions were incomplete: " + json.dumps(result))
    known_shutdown = (
        completed.returncode != 0
        and "EXCEPTION_ACCESS_VIOLATION" in combined
        and "ucrtbase.dll" in combined
    )
    if completed.returncode != 0 and not known_shutdown:
        raise RuntimeError(module + " exited unexpectedly with " + str(completed.returncode))
    return {
        **result,
        "duration_seconds": round(time.perf_counter() - started, 3),
        "host_exit_code": completed.returncode,
        "host_process_clean_exit": completed.returncode == 0,
        "host_exit_classification": "clean" if completed.returncode == 0 else "known_shutdown_only",
    }


def main() -> None:
    if not BFORARTISTS.is_file():
        raise FileNotFoundError(BFORARTISTS)
    RESULTS.mkdir(parents=True, exist_ok=True)
    runs = []
    for case in CASES:
        run = _run_case(*case)
        runs.append(run)
        print(run["module"] + ": PASS " + str(run["tests"]) + "/" + str(run["tests"]), flush=True)
    runtime_paths = sorted((ROOT / "b4artists_ml").glob("*.py"))
    report = {
        "schema": "b4ml-current-temporal-affected-recheck-v1",
        "status": "PASS",
        "host": {
            "executable": BFORARTISTS.as_posix(),
            "executable_sha256": _sha256(BFORARTISTS),
            "isolated_processes": len(runs),
        },
        "runs": runs,
        "totals": {
            "tests": sum(run["tests"] for run in runs),
            "passed": sum(run["passed"] for run in runs),
            "failures": sum(run["failures"] for run in runs),
            "errors": sum(run["errors"] for run in runs),
            "skipped": sum(run["skipped"] for run in runs),
        },
        "runtime_sources": {
            path.relative_to(ROOT).as_posix(): _sha256(path) for path in runtime_paths
        },
        "support_sources": {
            relative: _sha256(ROOT / relative) for relative in SUPPORT_SOURCES
        },
        "claim_boundary": {
            "current_worktree_only": True,
            "affected_temporal_behavior_verified": True,
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
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
