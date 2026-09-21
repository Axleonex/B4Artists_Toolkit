"""Run and bind the affected regression for external secondary acceleration."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import time


ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "training/b4artists_ml/results"
LOGS = ROOT / "training/b4artists_ml/cache"
HOST = Path(os.environ.get("B4ML_BFORARTISTS", "X:/5.1.0/bforartists.exe"))
RUNNER = ROOT / "training/b4artists_ml/run_unittest_report.py"
HERE = Path(__file__).resolve()
SUITES = (
    ("external_acceleration", "test_b4artists_ml_secondary_external_acceleration_v1", 13),
    ("secondary_math", "test_b4artists_ml_secondary_math", 12),
    ("secondary_motion", "test_b4artists_ml_secondary_motion", 11),
    ("chain_selection", "test_b4artists_ml_secondary_chain_selection_v1", 16),
    ("visible_state", "test_b4artists_ml_visible_state_v1", 6),
    ("registration_recovery", "test_b4artists_ml", 33),
)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def runtime_hashes():
    return {str(path.relative_to(ROOT)).replace("\\", "/"): sha(path)
            for path in sorted((ROOT / "b4artists_ml").glob("*.py"))}


def main():
    if not HOST.is_file():
        raise FileNotFoundError(HOST)
    RESULTS.mkdir(parents=True, exist_ok=True)
    LOGS.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    frozen_runtime = runtime_hashes()
    frozen_tests = {module: sha(ROOT / "tests" / (module + ".py"))
                    for _, module, _ in SUITES}
    frozen_harness = {
        str(RUNNER.relative_to(ROOT)).replace("\\", "/"): sha(RUNNER),
        str(HERE.relative_to(ROOT)).replace("\\", "/"): sha(HERE),
    }

    def assert_frozen():
        if runtime_hashes() != frozen_runtime:
            raise ValueError("Runtime changed during affected regression")
        if any(sha(ROOT / "tests" / (module + ".py")) != digest
               for module, digest in frozen_tests.items()):
            raise ValueError("Tests changed during affected regression")
        if any(sha(ROOT / relative) != digest
               for relative, digest in frozen_harness.items()):
            raise ValueError("Affected-regression harness changed during execution")

    suites = []
    for name, module, expected in SUITES:
        assert_frozen()
        report = RESULTS / f"secondary-external-acceleration-affected-{name}-v1.json"
        log = LOGS / f"secondary-external-acceleration-affected-{name}-v1.log"
        report.unlink(missing_ok=True)
        launched_ns = time.time_ns()
        with log.open("w", encoding="utf-8") as stream:
            process = subprocess.run(
                [str(HOST), "--background", "--factory-startup", "--disable-autoexec",
                 "--python", str(RUNNER), "--", "--module", module,
                 "--report", str(report), "--qualification",
                 "External secondary acceleration affected regression: " + name,
                 "--runner-sha256", frozen_harness[
                     str(RUNNER.relative_to(ROOT)).replace("\\", "/")],
                 "--driver", str(HERE), "--driver-sha256", frozen_harness[
                     str(HERE.relative_to(ROOT)).replace("\\", "/")]],
                cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT,
                env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1",
                         OPENBLAS_NUM_THREADS="4"), timeout=900)
        if not report.is_file() or report.stat().st_mtime_ns < launched_ns:
            raise ValueError("Affected suite produced no fresh report: " + name)
        data = json.loads(report.read_text(encoding="utf-8"))
        if (not data.get("passed") or data.get("tests") != expected
                or data.get("failures") != 0 or data.get("errors") != 0
                or data.get("skips") != 0 or data.get("python_optimize") != 0
                or data.get("test_sha256") != frozen_tests[module]
                or data.get("runtime_source_sha256") != frozen_runtime
                or data.get("harness_source_sha256") != {
                    str(RUNNER.relative_to(ROOT)).replace("\\", "/"):
                    frozen_harness[str(RUNNER.relative_to(ROOT)).replace("\\", "/")],
                    str(HERE.relative_to(ROOT)).replace("\\", "/"):
                    frozen_harness[str(HERE.relative_to(ROOT)).replace("\\", "/")]}):
            raise ValueError("Affected suite failed: " + name)
        suites.append({
            "name": name, "tests": expected, "passed": True,
            "process_exit_code": process.returncode,
            "assertions_completed_before_shutdown": True,
            "report": str(report.relative_to(ROOT)).replace("\\", "/"),
            "report_sha256": sha(report),
            "log": str(log.relative_to(ROOT)).replace("\\", "/"),
        })
        print(json.dumps({"suite": name, "tests": expected, "passed": True,
                          "process_exit_code": process.returncode}), flush=True)
    assert_frozen()
    result = {
        "schema": 1,
        "qualification": "Uniform world secondary acceleration affected regression",
        "passed": True,
        "tests": sum(row["tests"] for row in suites),
        "suite_count": len(suites),
        "suites": suites,
        "runtime_source_count": len(frozen_runtime),
        "runtime_source_sha256": frozen_runtime,
        "test_source_sha256": frozen_tests,
        "harness_source_sha256": frozen_harness,
        "elapsed_seconds": time.perf_counter() - started,
        "claims": {"procedural": True, "learned": False,
                   "force_or_torque_solver": False, "cascadeur_parity": False,
                   "full_goal_complete": False, "bforartists_shutdown_clean": False},
    }
    if result["tests"] != 91 or result["suite_count"] != 6 or result["runtime_source_count"] != 44:
        raise ValueError("Unexpected affected-regression dimensions")
    output = RESULTS / "secondary-external-acceleration-affected-v1-regression.json"
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": True, "tests": result["tests"],
                      "suites": result["suite_count"],
                      "runtime_sources": result["runtime_source_count"],
                      "report": str(output)}, indent=2))


if __name__ == "__main__":
    main()
