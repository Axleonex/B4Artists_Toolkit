"""Run the complete 0.36 development regression on one frozen source tree."""
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
HARNESS = ROOT / "training/b4artists_ml/run_unittest_report.py"
HERE = Path(__file__).resolve()
BASELINE = RESULTS / "full-regression-032-v1-regression.json"
BASELINE_SHA256 = "8d12b115f6b338e94401fee14c5b46bff113bdadad5757bdfc6291da0ecbbd0f"
SUITE_PLAN = RESULTS / "release-036-v1-suite-plan.json"
SUITE_PLAN_SHA256 = "730d386581ceb7515b2d0af0c4e3c884b63bd791b87b78c3bf65f2ea6a17d502"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def runtime_hashes():
    return {str(path.relative_to(ROOT)).replace("\\", "/"): sha(path)
            for path in sorted((ROOT / "b4artists_ml").glob("*.py"))}


def distributable_hashes():
    return {
        path.relative_to(ROOT).as_posix(): sha(path)
        for path in sorted((ROOT / "b4artists_ml").rglob("*"))
        if path.is_file()
        and (path.suffix in (".py", ".json", ".md", ".npz") or path.name == "LICENSE")
    }


def suite_plan():
    if sha(BASELINE) != BASELINE_SHA256:
        raise ValueError("The frozen 0.32 suite plan changed")
    if sha(SUITE_PLAN) != SUITE_PLAN_SHA256:
        raise ValueError("The frozen 0.36 unittest-loader inventory changed")
    inventory = json.loads(SUITE_PLAN.read_text(encoding="utf-8"))
    rows = inventory.get("suites", ())
    plan = [(row["suite"], row["tests"]) for row in rows]
    if (inventory.get("loader") != "unittest.defaultTestLoader.loadTestsFromModule" or
            inventory.get("suite_count") != 87 or inventory.get("tests") != 1017 or
            inventory.get("candidate_suite_count") != 124 or
            inventory.get("excluded_suite_count") != 37 or
            len(inventory.get("excluded_suites", ())) != 37 or
            len({module for module, _ in plan}) != 87 or
            sum(count for _, count in plan) != 1017):
        raise ValueError("Unexpected 0.36 suite-plan dimensions")
    for row in rows:
        path = ROOT / "tests" / (row["suite"] + ".py")
        if sha(path) != row["test_sha256"]:
            raise ValueError("Test source no longer matches frozen inventory: " + row["suite"])
    return tuple(plan)


def source_unchanged(runtime, distributable, tests, runner, harness, suite_plan_digest):
    return (runtime_hashes() == runtime and distributable_hashes() == distributable and
            sha(HERE) == runner and sha(SUITE_PLAN) == suite_plan_digest and
            sha(BASELINE) == BASELINE_SHA256 and sha(HARNESS) == harness and all(
                sha(ROOT / "tests" / (module + ".py")) == digest
                for module, digest in tests.items()))


def main():
    if not HOST.is_file():
        raise FileNotFoundError(HOST)
    plan = suite_plan()
    RESULTS.mkdir(parents=True, exist_ok=True)
    LOGS.mkdir(parents=True, exist_ok=True)
    runtime = runtime_hashes()
    distributable = distributable_hashes()
    tests = {module: sha(ROOT / "tests" / (module + ".py")) for module, _ in plan}
    runner = sha(HERE)
    harness = sha(HARNESS)
    suite_plan_digest = sha(SUITE_PLAN)
    started = time.perf_counter()
    suites = []
    for index, (module, expected) in enumerate(plan, 1):
        if not source_unchanged(runtime, distributable, tests, runner, harness, suite_plan_digest):
            raise ValueError("Source tree changed during release regression")
        report_path = RESULTS / f"release-036-v1-{module}.json"
        log_path = LOGS / f"release-036-v1-{module}.log"
        report_path.unlink(missing_ok=True)
        command = [str(HOST), "--background", "--factory-startup", "--disable-autoexec",
                   "--python", str(HARNESS), "--", "--module", module,
                   "--report", str(report_path), "--qualification",
                   f"B4Artists ML 0.36.0 curated procedural release regression: {module}"]
        launched_ns = time.time_ns()
        child_env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", OPENBLAS_NUM_THREADS="4")
        child_env.pop("PYTHONOPTIMIZE", None)
        with log_path.open("w", encoding="utf-8") as stream:
            process = subprocess.run(
                command, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT,
                env=child_env, timeout=900)
        if not report_path.is_file() or report_path.stat().st_mtime_ns < launched_ns:
            raise ValueError(f"Suite produced no fresh report: {module}; see {log_path}")
        if not source_unchanged(runtime, distributable, tests, runner, harness, suite_plan_digest):
            raise ValueError("Source tree changed during release regression")
        data = json.loads(report_path.read_text(encoding="utf-8"))
        if (not data.get("passed") or data.get("python_optimize") != 0 or
                data.get("tests") != expected or
                data.get("failures") or data.get("errors") or data.get("skips") or
                data.get("test_sha256") != tests[module] or
                data.get("runtime_source_sha256") != runtime or
                data.get("distributable_member_sha256") != distributable):
            raise ValueError(f"Release suite failed: {module}; see {log_path}")
        suites.append({"suite": module, "tests": expected, "passed": True,
                       "process_exit_code": process.returncode,
                       "assertions_completed_before_shutdown": True,
                       "report": str(report_path.relative_to(ROOT)).replace("\\", "/"),
                       "report_sha256": sha(report_path),
                       "log": str(log_path.relative_to(ROOT)).replace("\\", "/")})
        print(json.dumps({"index": index, "suites": len(plan), "suite": module,
                          "tests": expected, "passed": True,
                          "process_exit_code": process.returncode}), flush=True)
    if not source_unchanged(runtime, distributable, tests, runner, harness, suite_plan_digest):
        raise ValueError("Source tree changed before release-regression publication")
    result = {
        "schema": 1,
        "release": "0.36.0",
        "qualification": "Curated B4Artists ML 0.36.0 procedural release regression",
        "passed": True,
        "tests": sum(row["tests"] for row in suites),
        "suite_count": len(suites),
        "suites": suites,
        "runtime_source_count": len(runtime),
        "runtime_source_sha256": runtime,
        "distributable_member_count": len(distributable),
        "distributable_member_sha256": distributable,
        "test_source_sha256": tests,
        "runner_sha256": runner,
        "unittest_harness_sha256": harness,
        "baseline_suite_plan": str(BASELINE.relative_to(ROOT)).replace("\\", "/"),
        "baseline_suite_plan_sha256": sha(BASELINE),
        "suite_plan": str(SUITE_PLAN.relative_to(ROOT)).replace("\\", "/"),
        "suite_plan_sha256": sha(SUITE_PLAN),
        "elapsed_seconds": time.perf_counter() - started,
        "claims": {"procedural_release": True, "learned_temporal_qualified": False,
                   "cascadeur_parity": False, "full_goal_complete": False,
                   "bforartists_shutdown_clean": False},
    }
    if result["tests"] != 1017 or result["suite_count"] != 87 or len(runtime) != 44:
        raise ValueError("Unexpected release-regression dimensions")
    output = RESULTS / "release-036-v1-regression.json"
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": True, "tests": result["tests"],
                      "suites": result["suite_count"],
                      "runtime_sources": len(runtime), "report": str(output)}), flush=True)


if __name__ == "__main__":
    main()
