"""Run current-source mapping-correction adapter coverage in Bforartists."""

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
TEST = ROOT / "tests" / "test_b4artists_ml_mapping_corrections_v1.py"
ORCHESTRATOR = Path(__file__).resolve()
MODULE = "test_b4artists_ml_mapping_corrections_v1"
EXPECTED_TESTS = 11
LABEL = "current-mapping-corrections-recheck-v3"
FOCUSED_REPORT = RESULTS / f"{LABEL}-focused.json"
HOST_REPORT = RESULTS / f"{LABEL}-host.json"
OUTPUT = RESULTS / f"{LABEL}.json"
LOG = CACHE / f"{LABEL}.log"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if not HOST.is_file():
        raise FileNotFoundError(HOST)
    for path in (FOCUSED_REPORT, HOST_REPORT, OUTPUT):
        if path.exists():
            raise RuntimeError("Evidence already exists: " + str(path))
    RESULTS.mkdir(parents=True, exist_ok=True)
    CACHE.mkdir(parents=True, exist_ok=True)
    command = [
        str(HOST), "--background", "--factory-startup", "--disable-autoexec",
        "--python", str(TEST),
    ]
    started = time.perf_counter()
    environment = dict(
        os.environ,
        B4ML_RUN_LABEL=LABEL,
        B4ML_MAPPING_CORRECTIONS_RESULT=FOCUSED_REPORT.name,
        PYTHONDONTWRITEBYTECODE="1",
        OPENBLAS_NUM_THREADS="4",
    )
    with LOG.open("w", encoding="utf-8") as stream:
        process = subprocess.run(
            command, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT,
            env=environment, timeout=900, check=False,
        )
    if not FOCUSED_REPORT.is_file():
        raise RuntimeError("Bforartists did not write the focused report: " + str(LOG))
    focused = json.loads(FOCUSED_REPORT.read_text(encoding="utf-8"))
    if (focused.get("tests") != EXPECTED_TESTS or focused.get("passed") is not True
            or focused.get("failures") != 0 or focused.get("errors") != 0):
        raise RuntimeError("Focused mapping-correction receipt was incomplete")
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
    report = {
        "schema": "b4ml-current-mapping-corrections-recheck-v1",
        "status": "PASS",
        "scope": (
            "Current-worktree Bforartists adapter-bound mapping-correction recheck "
            "covering BoneForge, Rigify Basic, Rigify Default, and imported "
            "Mocap, Unity, and Unreal Humanoid fixtures with rollback and "
            "save/reload assertions."
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
            "tests": focused["tests"],
            "passed": focused["passed"],
            "failures": focused["failures"],
            "errors": focused["errors"],
            "skips": focused.get("skips", 0),
            "focused_tests": focused["tests"],
            "elapsed_seconds": round(time.perf_counter() - started, 3),
        },
        "focused_report": FOCUSED_REPORT.relative_to(ROOT).as_posix(),
        "focused_report_sha256": _sha256(FOCUSED_REPORT),
        "log": LOG.relative_to(ROOT).as_posix(),
        "log_sha256": _sha256(LOG),
        "focused_test_sha256": _sha256(TEST),
        "orchestrator_sha256": _sha256(ORCHESTRATOR),
        "runtime_source_sha256": runtime,
        "claim_boundary": {
            "boneforge_verified": True,
            "rigify_basic_verified": True,
            "rigify_default_verified": True,
            "imported_humanoid_verified": True,
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
