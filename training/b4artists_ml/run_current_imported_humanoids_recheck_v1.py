"""Run the imported-humanoid workflow against the current worktree source."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import time


ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "training" / "b4artists_ml" / "results"
CACHE = ROOT / "training" / "b4artists_ml" / "cache"
HOST = Path(os.environ.get("B4ML_BFORARTISTS", r"X:\5.1.0\bforartists.exe"))
HOST_RUNNER = ROOT / "training" / "b4artists_ml" / "run_unittest_report.py"
ORCHESTRATOR = Path(__file__).resolve()
MODULE = "test_b4artists_ml_imported_humanoids"
EXPECTED_TESTS = 12
LABEL = "current-imported-humanoids-recheck-v1"
HOST_REPORT = RESULTS / f"{LABEL}-host.json"
OUTPUT = RESULTS / f"{LABEL}.json"
LOG = CACHE / f"{LABEL}.log"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if not HOST.is_file():
        raise FileNotFoundError(HOST)
    for path in (HOST_REPORT, OUTPUT):
        if path.exists():
            raise RuntimeError("Evidence already exists: " + str(path))
    RESULTS.mkdir(parents=True, exist_ok=True)
    CACHE.mkdir(parents=True, exist_ok=True)
    command = [
        str(HOST), "--background", "--factory-startup", "--disable-autoexec",
        "--python", str(HOST_RUNNER), "--", "--module", MODULE,
        "--report", str(HOST_REPORT), "--qualification",
        "Current-worktree imported humanoid compatibility recheck",
        "--runner-sha256", _sha256(HOST_RUNNER),
    ]
    started = time.perf_counter()
    environment = dict(
        os.environ,
        B4ML_RUN_LABEL=LABEL,
        PYTHONDONTWRITEBYTECODE="1",
        OPENBLAS_NUM_THREADS="4",
    )
    with LOG.open("w", encoding="utf-8") as stream:
        process = subprocess.run(
            command, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT,
            env=environment, timeout=900, check=False,
        )
    if not HOST_REPORT.is_file():
        raise RuntimeError("Bforartists did not write the host report: " + str(LOG))
    host_report = json.loads(HOST_REPORT.read_text(encoding="utf-8"))
    if (host_report.get("passed") is not True
            or host_report.get("tests") != EXPECTED_TESTS
            or host_report.get("failures") != 0
            or host_report.get("errors") != 0
            or host_report.get("skips") != 0):
        raise RuntimeError("Imported humanoid assertions were incomplete: "
                           + json.dumps(host_report))
    log_text = LOG.read_text(encoding="utf-8", errors="replace")
    known_shutdown = (
        process.returncode != 0
        and "EXCEPTION_ACCESS_VIOLATION" in log_text
        and "ucrtbase.dll" in log_text
    )
    if process.returncode != 0 and not known_shutdown:
        raise RuntimeError("Unexpected Bforartists exit: " + str(process.returncode))
    runtime = {
        path.relative_to(ROOT).as_posix(): _sha256(path)
        for path in sorted((ROOT / "b4artists_ml").glob("*.py"))
    }
    fixture = RESULTS / f"{LABEL}-fixtures.json"
    report = {
        "schema": "b4ml-current-imported-humanoids-recheck-v1",
        "status": "PASS",
        "scope": (
            "Current-worktree Bforartists host recheck of imported humanoid "
            "workflow, source recovery, contact/support paths, and learned "
            "completion behavior. This is not human usability or learned-quality proof."
        ),
        "host": {
            "executable": HOST.as_posix(),
            "executable_sha256": _sha256(HOST),
            "exit_code": process.returncode,
            "exit_classification": "known_shutdown_only" if known_shutdown else "clean",
            "clean_exit": process.returncode == 0,
        },
        "suite": {
            "module": MODULE,
            "tests": host_report["tests"],
            "passed": host_report["passed"],
            "failures": host_report["failures"],
            "errors": host_report["errors"],
            "skips": host_report["skips"],
            "elapsed_seconds": round(time.perf_counter() - started, 3),
        },
        "host_report": HOST_REPORT.relative_to(ROOT).as_posix(),
        "host_report_sha256": _sha256(HOST_REPORT),
        "log": LOG.relative_to(ROOT).as_posix(),
        "log_sha256": _sha256(LOG),
        "fixture_report": fixture.relative_to(ROOT).as_posix() if fixture.is_file() else None,
        "fixture_report_sha256": _sha256(fixture) if fixture.is_file() else None,
        "test_sha256": _sha256(ROOT / "tests" / f"{MODULE}.py"),
        "host_runner_sha256": _sha256(HOST_RUNNER),
        "orchestrator_sha256": _sha256(ORCHESTRATOR),
        "runtime_source_sha256": runtime,
        "claim_boundary": {
            "imported_humanoid_workflow_verified": True,
            "learned_temporal_quality_verified": False,
            "independent_animator_usability_verified": False,
            "cascadeur_parity_verified": False,
            "full_goal_complete": False,
        },
    }
    OUTPUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
