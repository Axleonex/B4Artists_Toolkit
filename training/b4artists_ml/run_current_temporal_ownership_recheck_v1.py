"""Run temporal ownership suites in isolated Bforartists processes.

Isolation is intentional: save/reload tests preserve the current file, so combining
all temporal suites in one host process also preserves earlier generated fixtures
and turns fixture construction into progressively slower, non-product work.
"""

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
OUTPUT = RESULTS / "current-temporal-ownership-recheck-v1.json"
BFORARTISTS = Path(os.environ.get("B4ML_BFORARTISTS", r"X:\5.1.0\bforartists.exe"))
MARKER = "B4ML_TEMPORAL_OWNERSHIP_RESULT "
CASES = (
    ("test_b4artists_ml_temporal_preview_v1", "TemporalPreviewTests", 10),
    ("test_b4artists_ml_temporal_private_v1", "PrivateTemporalTests", 10),
    ("test_b4artists_ml_temporal_cooperative", "CooperativeTemporalTests", 11),
)
SOURCES = (
    "b4artists_ml/temporal_preview.py",
    "b4artists_ml/temporal_generation.py",
    "b4artists_ml/ui.py",
    "training/b4artists_ml/temporal_cooperative_v1.py",
    "tests/test_b4artists_ml_temporal_preview_v1.py",
    "tests/test_b4artists_ml_temporal_private_v1.py",
    "tests/test_b4artists_ml_temporal_cooperative.py",
    "training/b4artists_ml/run_current_temporal_ownership_recheck_v1.py",
    "training/b4artists_ml/check_current_temporal_ownership_recheck_v1.py",
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
    completed = subprocess.run(
        [str(BFORARTISTS), "--background", "--factory-startup", "--python-expr",
         _expression(module, class_name)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env={**os.environ, "B4ML_RUN_LABEL": "temporal-ownership-" + module},
        check=False,
    )
    combined = completed.stdout + "\n" + completed.stderr
    matches = re.findall(re.escape(MARKER) + r"(\{[^\r\n]+\})", combined)
    if len(matches) != 1:
        raise RuntimeError(module + " did not emit exactly one ownership result marker")
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
    runs = [_run_case(*case) for case in CASES]
    report = {
        "schema": "b4ml-current-temporal-ownership-recheck-v1",
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
        "sources": {relative: _sha256(ROOT / relative) for relative in SOURCES},
        "claim_boundary": {
            "current_worktree_only": True,
            "workflow_ownership_and_recovery_verified": True,
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
