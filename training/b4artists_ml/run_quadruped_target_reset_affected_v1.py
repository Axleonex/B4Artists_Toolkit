"""Run and bind the affected regression for quadruped target reset."""
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
SUITES = (
    ("target_reset", "test_b4artists_ml_quadruped_target_reset_v1", 9),
    ("gait_phase", "test_b4artists_ml_quadruped_gait_phase_v1", 5),
    ("pole_match", "test_b4artists_ml_quadruped_pole_match_v1", 8),
    ("pole_targets", "test_b4artists_ml_quadruped_poles_v1", 6),
    ("spine_follow", "test_b4artists_ml_quadruped_spine_follow_v1", 8),
    ("head", "test_b4artists_ml_quadruped_head_v1", 7),
    ("quadruped_pose", "test_b4artists_ml_quadruped_pose", 4),
    ("quadruped_adapter", "test_b4artists_ml_quadrupeds", 1),
    ("quadruped_contacts", "test_b4artists_ml_quadruped_contacts", 3),
    ("paw_suggestions", "test_b4artists_ml_quadruped_suggestions", 6),
    ("contact_visualization", "test_b4artists_ml_contact_visualization_v1", 6),
    ("cleanup", "test_b4artists_ml_cleanup_v1", 5),
    ("visible_state", "test_b4artists_ml_visible_state_v1", 6),
    ("base_registration_recovery", "test_b4artists_ml", 34),
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
    suites = []
    frozen_runtime = runtime_hashes()
    frozen_tests = {module: sha(ROOT / "tests" / (module + ".py"))
                    for _, module, _ in SUITES}
    for name, module, expected in SUITES:
        if runtime_hashes() != frozen_runtime or any(
                sha(ROOT / "tests" / (test_module + ".py")) != digest
                for test_module, digest in frozen_tests.items()):
            raise ValueError("Source tree changed during affected regression")
        report_path = RESULTS / f"quadruped-target-reset-affected-{name}-v1.json"
        log_path = LOGS / f"quadruped-target-reset-affected-{name}-v1.log"
        report_path.unlink(missing_ok=True)
        command = [str(HOST), "--background", "--factory-startup", "--disable-autoexec",
                   "--python", str(RUNNER), "--", "--module", module,
                   "--report", str(report_path), "--qualification",
                   f"Quadruped target-reset affected regression: {name}"]
        launched_ns = time.time_ns()
        with log_path.open("w", encoding="utf-8") as stream:
            process = subprocess.run(command, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT,
                                     env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1",
                                              OPENBLAS_NUM_THREADS="4"), timeout=900)
        if not report_path.is_file() or report_path.stat().st_mtime_ns < launched_ns:
            raise ValueError(f"Affected suite produced no fresh report: {name}; see {log_path}")
        if runtime_hashes() != frozen_runtime or any(
                sha(ROOT / "tests" / (test_module + ".py")) != digest
                for test_module, digest in frozen_tests.items()):
            raise ValueError("Source tree changed during affected regression")
        data = json.loads(report_path.read_text(encoding="utf-8"))
        if (not data.get("passed") or data.get("tests") != expected or
                data.get("test_sha256") != frozen_tests[module] or
                data.get("runtime_source_sha256") != frozen_runtime):
            raise ValueError(f"Affected suite failed: {name}; see {log_path}")
        suites.append({
            "name": name,
            "tests": expected,
            "passed": True,
            "process_exit_code": process.returncode,
            "assertions_completed_before_shutdown": True,
            "report": str(report_path.relative_to(ROOT)).replace("\\", "/"),
            "report_sha256": sha(report_path),
            "log": str(log_path.relative_to(ROOT)).replace("\\", "/"),
        })
        print(json.dumps({"suite": name, "tests": expected, "passed": True,
                          "process_exit_code": process.returncode}), flush=True)
    if runtime_hashes() != frozen_runtime or any(
            sha(ROOT / "tests" / (module + ".py")) != digest
            for module, digest in frozen_tests.items()):
        raise ValueError("Source tree changed before affected-regression publication")
    result = {
        "schema": 1,
        "qualification": "Generated Rigify quadruped per-target reset affected regression",
        "passed": True,
        "tests": sum(row["tests"] for row in suites),
        "suite_count": len(suites),
        "suites": suites,
        "runtime_source_count": len(frozen_runtime),
        "runtime_source_sha256": frozen_runtime,
        "test_source_sha256": frozen_tests,
        "elapsed_seconds": time.perf_counter() - started,
        "claims": {"procedural": True, "learned": False,
                   "cascadeur_parity": False, "full_goal_complete": False,
                   "bforartists_shutdown_clean": False},
    }
    if result["tests"] != 108 or result["suite_count"] != 14 or result["runtime_source_count"] != 44:
        raise ValueError("Unexpected affected-regression dimensions")
    output = RESULTS / "quadruped-target-reset-affected-v1-regression.json"
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": True, "tests": result["tests"],
                      "suites": result["suite_count"],
                      "runtime_sources": result["runtime_source_count"],
                      "report": str(output)}), flush=True)


if __name__ == "__main__":
    main()
