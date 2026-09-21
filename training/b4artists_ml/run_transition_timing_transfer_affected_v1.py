"""Run and bind the affected regression for Transition Timing Transfer."""
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
    ("timing_transfer", "test_b4artists_ml_transition_timing_transfer_v1", 6),
    ("breakdown_pose", "test_b4artists_ml_breakdown_pose_v1", 8),
    ("transition_window", "test_b4artists_ml_transition_window_v1", 10),
    ("transition_timing", "test_b4artists_ml_transition_timing_v1", 9),
    ("timing_controls", "test_b4artists_ml_timing_controls_v1", 7),
    ("pole_controls", "test_b4artists_ml_quadruped_pole_controls_v1", 8),
    ("pole_align", "test_b4artists_ml_quadruped_pole_align_v1", 6),
    ("pose_asset", "test_b4artists_ml_quadruped_pose_asset_v1", 7),
    ("target_mirror", "test_b4artists_ml_quadruped_target_mirror_v1", 8),
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


def source_unchanged(frozen_runtime, frozen_tests, frozen_runner, frozen_harness):
    return runtime_hashes() == frozen_runtime and all(
        sha(ROOT / "tests" / (module + ".py")) == digest
        for module, digest in frozen_tests.items()) and sha(HERE) == frozen_runner and sha(RUNNER) == frozen_harness


def main():
    if not HOST.is_file():
        raise FileNotFoundError(HOST)
    RESULTS.mkdir(parents=True, exist_ok=True)
    LOGS.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    frozen_runtime = runtime_hashes()
    frozen_tests = {module: sha(ROOT / "tests" / (module + ".py"))
                    for _, module, _ in SUITES}
    frozen_runner = sha(HERE)
    frozen_harness = sha(RUNNER)
    suites = []
    for name, module, expected in SUITES:
        if not source_unchanged(frozen_runtime, frozen_tests, frozen_runner, frozen_harness):
            raise ValueError("Source tree changed during affected regression")
        report_path = RESULTS / f"transition-timing-transfer-affected-{name}-v1.json"
        log_path = LOGS / f"transition-timing-transfer-affected-{name}-v1.log"
        report_path.unlink(missing_ok=True)
        command = [str(HOST), "--background", "--factory-startup", "--disable-autoexec",
                   "--python", str(RUNNER), "--", "--module", module,
                   "--report", str(report_path), "--qualification",
                   f"Transition Timing Transfer affected regression: {name}"]
        launched_ns = time.time_ns()
        with log_path.open("w", encoding="utf-8") as stream:
            process = subprocess.run(
                command, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT,
                env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1",
                         OPENBLAS_NUM_THREADS="4"), timeout=900)
        if not report_path.is_file() or report_path.stat().st_mtime_ns < launched_ns:
            raise ValueError(f"Affected suite produced no fresh report: {name}; see {log_path}")
        if not source_unchanged(frozen_runtime, frozen_tests, frozen_runner, frozen_harness):
            raise ValueError("Source tree changed during affected regression")
        data = json.loads(report_path.read_text(encoding="utf-8"))
        if (not data.get("passed") or data.get("tests") != expected or
                data.get("test_sha256") != frozen_tests[module] or
                data.get("runtime_source_sha256") != frozen_runtime):
            raise ValueError(f"Affected suite failed: {name}; see {log_path}")
        suites.append({"name": name, "tests": expected, "passed": True,
                       "process_exit_code": process.returncode,
                       "assertions_completed_before_shutdown": True,
                       "report": str(report_path.relative_to(ROOT)).replace("\\", "/"),
                       "report_sha256": sha(report_path),
                       "log": str(log_path.relative_to(ROOT)).replace("\\", "/")})
        print(json.dumps({"suite": name, "tests": expected, "passed": True,
                          "process_exit_code": process.returncode}), flush=True)
    if not source_unchanged(frozen_runtime, frozen_tests, frozen_runner, frozen_harness):
        raise ValueError("Source tree changed before affected-regression publication")
    result = {
        "schema": 1,
        "qualification": "Deterministic Transition Timing Transfer affected regression",
        "passed": True,
        "tests": sum(row["tests"] for row in suites),
        "suite_count": len(suites),
        "suites": suites,
        "runtime_source_count": len(frozen_runtime),
        "runtime_source_sha256": frozen_runtime,
        "test_source_sha256": frozen_tests,
        "runner_sha256": frozen_runner,
        "unittest_harness_sha256": frozen_harness,
        "elapsed_seconds": time.perf_counter() - started,
        "claims": {"procedural": True, "learned": False,
                   "cascadeur_parity": False, "full_goal_complete": False,
                   "bforartists_shutdown_clean": False},
    }
    if result["tests"] != 177 or result["suite_count"] != 23 or result["runtime_source_count"] != 44:
        raise ValueError("Unexpected affected-regression dimensions")
    output = RESULTS / "transition-timing-transfer-affected-v1-regression.json"
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": True, "tests": result["tests"],
                      "suites": result["suite_count"],
                      "runtime_sources": result["runtime_source_count"],
                      "report": str(output)}), flush=True)


if __name__ == "__main__":
    main()

