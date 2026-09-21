"""Run isolated pole/body-preview suites against an exact ZIP package."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time


ROOT = Path(__file__).resolve().parents[2]
HOST = Path(os.environ.get("B4ML_BFORARTISTS", r"X:\5.1.0\bforartists.exe"))
ARCHIVE = Path(os.environ.get(
    "B4ML_ARCHIVE",
    str(ROOT / "releases" / "b4artists_ml_v0.37.34-dev.zip"),
)).resolve()
TAG = os.environ.get("B4ML_EXACT_POLE_TAG", "v0.37.34")
RESULTS = ROOT / "training" / "b4artists_ml" / "results"
CACHE = ROOT / "training" / "b4artists_ml" / "cache"
HOST_RUNNER = ROOT / "training" / "b4artists_ml" / "run_exact_package_unittest_host_v1.py"
OUTPUT = RESULTS / f"exact-package-pole-{TAG}.json"
MODULES = (
    ("test_b4artists_ml_pole_align_v1", "PoleAlignTests", 6),
    ("test_b4artists_ml_pole_flip_v1", "PoleFlipTests", 4),
    ("test_b4artists_ml_pole_distance_v1", "PoleDistanceTests", 5),
    ("test_b4artists_ml_target_reset_v1", "TargetResetTests", 8),
    ("test_b4artists_ml_target_mirror_v1", "TargetMirrorTests", 7),
    ("test_b4artists_ml_body_controls", "BodyControlTests", int(os.environ.get("B4ML_BODY_CONTROLS_TESTS", "10"))),
    ("test_b4artists_ml_context_preview", "PreviewTests", 10),
    ("test_b4artists_ml", None, 34),
)
KNOWN_SHUTDOWN_EXITS = {0, 1, 11, -1073741819, 3221225477}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def main() -> int:
    if not ARCHIVE.is_file():
        raise FileNotFoundError(ARCHIVE)
    if not HOST_RUNNER.is_file():
        raise FileNotFoundError(HOST_RUNNER)
    started = time.perf_counter()
    rows = []
    for module, class_name, expected_tests in MODULES:
        report = RESULTS / f"exact-package-{TAG}-{module}.json"
        log = CACHE / f"exact-package-{TAG}-{module}.log"
        reused = os.environ.get("B4ML_EXACT_POLE_REUSE") == "1" and report.is_file()
        if reused:
            row = json.loads(report.read_text(encoding="utf-8"))
            process_return = row.get("host_exit", 3221225477)
        else:
            report.unlink(missing_ok=True)
            log.parent.mkdir(parents=True, exist_ok=True)
            environment = dict(
                os.environ,
                B4ML_PACKAGE=str(ARCHIVE),
                PYTHONDONTWRITEBYTECODE="1",
                OPENBLAS_NUM_THREADS="4",
            )
            with log.open("w", encoding="utf-8") as stream:
                process = subprocess.run(
                    [
                        str(HOST), "--background", "--factory-startup",
                        "--disable-autoexec", "--python", str(HOST_RUNNER), "--",
                        "--module", module,
                        *((["--class-name", class_name] if class_name else [])),
                        "--report", str(report),
                    ],
                    cwd=ROOT,
                    stdout=stream,
                    stderr=subprocess.STDOUT,
                    env=environment,
                    timeout=900,
                    check=False,
                )
            row = json.loads(report.read_text(encoding="utf-8")) if report.is_file() else {
            "schema": "b4ml-exact-package-unittest-v1",
            "suite": module,
            "tests": 0,
            "assertions_passed": False,
            "failures": [],
            "errors": ["Missing host receipt"],
            "skipped": [],
            }
            process_return = process.returncode
        row.update(
            expected_tests=expected_tests,
            host_exit=process_return,
            known_shutdown_only=(
                row.get("assertions_passed") is True
                and process_return in KNOWN_SHUTDOWN_EXITS
            ),
            log=str(log.relative_to(ROOT)),
            reused_individual_receipt=reused,
        )
        rows.append(row)
        print(json.dumps(row, sort_keys=True), flush=True)
    passed = all(
        row.get("tests") == row.get("expected_tests")
        and row.get("assertions_passed") is True
        and not row.get("failures")
        and not row.get("errors")
        and not row.get("skipped")
        and row.get("host_exit") in KNOWN_SHUTDOWN_EXITS
        and row.get("package_sha256") == sha256(ARCHIVE)
        for row in rows
    )
    payload = {
        "schema": "b4ml-exact-package-pole-regression-v1",
        "recorded_at": utc_now(),
        "status": "PASS" if passed else "FAIL",
        "archive": str(ARCHIVE),
        "archive_sha256": sha256(ARCHIVE),
        "host_runner": str(HOST_RUNNER.relative_to(ROOT)).replace("\\", "/"),
        "host_runner_sha256": sha256(HOST_RUNNER),
        "suites": len(rows),
        "tests": sum(row.get("tests", 0) for row in rows),
        "rows": rows,
        "elapsed_seconds": time.perf_counter() - started,
        "claim_boundary_closed": True,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "tests": payload["tests"], "output": str(OUTPUT)}))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
