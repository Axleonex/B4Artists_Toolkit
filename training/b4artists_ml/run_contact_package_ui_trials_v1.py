"""Repeat the actual-window contact workflow against the extracted 0.20.1 package."""
from pathlib import Path
import json
import os
import subprocess
import time


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "training/b4artists_ml/cache/contact-performance-package-v1"
RESULT = ROOT / "training/b4artists_ml/results/contact-suggestions-ui-v1.json"
OUTPUT = ROOT / "training/b4artists_ml/results/contact-performance-package-ui-trials-v1.json"
HOST = Path("X:/5.1.0/bforartists.exe")
TEST = ROOT / "tests/test_b4artists_ml_contact_suggestions.py"


def percentile(values, fraction):
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, int(fraction * len(ordered)))]


def main(trials=3):
    assert BASE.is_dir() and not OUTPUT.exists()
    rows = []
    started = time.perf_counter()
    for index in range(trials):
        if RESULT.exists():
            RESULT.unlink()
        env = dict(os.environ, B4ML_PACKAGE=str(BASE), PYTHONDONTWRITEBYTECODE="1", OPENBLAS_NUM_THREADS="4")
        process = subprocess.run(
            [
                str(HOST),
                "--factory-startup",
                "--disable-autoexec",
                "--enable-event-simulate",
                "--python",
                str(TEST),
                "--",
                "--ui-smoke",
            ],
            cwd=ROOT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
            env=env,
            timeout=180,
        )
        if not RESULT.exists():
            raise RuntimeError(f"Actual-window trial {index + 1} produced no result (host exit {process.returncode})")
        report = json.loads(RESULT.read_text(encoding="utf-8"))
        if not report.get("passed"):
            raise RuntimeError(f"Actual-window trial {index + 1} failed: {report}")
        assert Path(report["package"]).resolve().is_relative_to(BASE.resolve())
        correction = report["correction"]
        slowest_suggestion = max(report["suggestion_step_details"], key=lambda row: row["elapsed_ms"])
        slowest_correction = max(report["correction_step_details"], key=lambda row: row["elapsed_ms"])
        rows.append(
            dict(
                trial=index + 1,
                host_exit=process.returncode,
                exact_package=True,
                package=report["package"],
                functional_pass=True,
                suggestion_elapsed_ms=report["suggestion"]["elapsed_ms"],
                suggestion_step_p95_ms=report["suggestion_step_p95_ms"],
                suggestion_step_max_ms=report["suggestion_step_max_ms"],
                suggestion_slowest_phase=slowest_suggestion["progress"],
                correction_elapsed_ms=correction["elapsed_ms"],
                correction_step_p95_ms=report["correction_step_p95_ms"],
                correction_step_max_ms=report["correction_step_max_ms"],
                correction_slowest_phase=slowest_correction["progress"],
                correction_error=correction["max_after"],
                fit_frames=correction["frames"],
                validation_frames=correction["validation_frames"],
                backend=correction["backend"],
            )
        )
    suggestion_max = [row["suggestion_step_max_ms"] for row in rows]
    correction_max = [row["correction_step_max_ms"] for row in rows]
    elapsed = [row["correction_elapsed_ms"] for row in rows]
    gates = dict(
        all_functional=all(row["functional_pass"] for row in rows),
        every_suggestion_callback_below_50ms=max(suggestion_max) < 50.0,
        every_correction_callback_below_50ms=max(correction_max) < 50.0,
        every_correction_below_8s=max(elapsed) < 8000.0,
        correction_error_below_2e_4=max(row["correction_error"] for row in rows) < 2e-4,
    )
    result = dict(
        schema=1,
        passed=all(gates.values()),
        exact_package=True,
        trials=rows,
        summary=dict(
            correction_elapsed_median_ms=percentile(elapsed, 0.5),
            correction_elapsed_max_ms=max(elapsed),
            suggestion_callback_max_ms=max(suggestion_max),
            correction_callback_max_ms=max(correction_max),
        ),
        gates=gates,
        host_shutdown_qualified=all(row["host_exit"] == 0 for row in rows),
        note="Bforartists 5.1.0 has a known post-result access violation on this host; functional evidence is written before shutdown.",
        elapsed_seconds=time.perf_counter() - started,
    )
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2), flush=True)
    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
