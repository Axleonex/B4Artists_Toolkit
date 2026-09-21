"""Run and bind the affected regression for quadruped gait-phase review."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys
import time


ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "training/b4artists_ml/results"
LOGS = ROOT / "training/b4artists_ml/cache"
HOST = Path(os.environ.get("B4ML_BFORARTISTS", "X:/5.1.0/bforartists.exe"))
RUNNER = ROOT / "training/b4artists_ml/run_unittest_report.py"
SUITES = (
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


def main():
    if not HOST.is_file():
        raise FileNotFoundError(HOST)
    RESULTS.mkdir(parents=True, exist_ok=True)
    LOGS.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    suites = []
    for name, module, expected in SUITES:
        report_path = RESULTS / f"quadruped-gait-affected-{name}-v1.json"
        log_path = LOGS / f"quadruped-gait-affected-{name}-v1.log"
        command = [str(HOST), "--background", "--factory-startup", "--disable-autoexec",
                   "--python", str(RUNNER), "--", "--module", module,
                   "--report", str(report_path), "--qualification",
                   f"Quadruped gait-phase affected regression: {name}"]
        with log_path.open("w", encoding="utf-8") as stream:
            process = subprocess.run(command, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT,
                                     env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1",
                                              OPENBLAS_NUM_THREADS="4"), timeout=900)
        data = json.loads(report_path.read_text(encoding="utf-8"))
        if not data.get("passed") or data.get("tests") != expected:
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
    runtime = {str(path.relative_to(ROOT)).replace("\\", "/"): sha(path)
               for path in sorted((ROOT / "b4artists_ml").glob("*.py"))}
    result = {
        "schema": 1,
        "qualification": "Procedural quadruped gait-phase affected regression",
        "passed": True,
        "tests": sum(row["tests"] for row in suites),
        "suite_count": len(suites),
        "suites": suites,
        "runtime_source_count": len(runtime),
        "runtime_source_sha256": runtime,
        "elapsed_seconds": time.perf_counter() - started,
        "claims": {"procedural": True, "learned": False, "gait_generation": False,
                   "cascadeur_parity": False, "full_goal_complete": False,
                   "bforartists_shutdown_clean": False},
    }
    if result["tests"] != 99 or result["runtime_source_count"] != 44:
        raise ValueError("Unexpected affected-regression dimensions")
    output = RESULTS / "quadruped-gait-affected-v1-regression.json"
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": True, "tests": result["tests"],
                      "suites": result["suite_count"],
                      "runtime_sources": result["runtime_source_count"],
                      "report": str(output)}), flush=True)


if __name__ == "__main__":
    main()
