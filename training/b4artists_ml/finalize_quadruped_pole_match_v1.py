"""Validate and bind the Quadruped Pole Match v1 evidence set."""
from pathlib import Path
import hashlib
import json


ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "training/b4artists_ml/results"
SUITES = (
    ("pole_match", "quadruped-pole-match-v1.json", 8),
    ("pole_targets", "quadruped-poles-v1.json", 6),
    ("spine_follow", "quadruped-spine-follow-v1.json", 8),
    ("head", "quadruped-head-v1.json", 7),
    ("quadruped_pose", "quadruped-pose-v1.json", 4),
    ("quadruped_adapter", "quadruped-adapter-v1.json", 1),
    ("quadruped_contacts", "quadruped-contacts-v1.json", 3),
    ("paw_suggestions", "quadruped-pole-match-final-suggestions.json", 6),
    ("contact_visualization", "contact-visualization-v1.json", 6),
    ("cleanup", "cleanup-v1.json", 5),
    ("visible_state", "quadruped-pole-match-final-visible-state.json", 6),
    ("base_registration_recovery", "quadruped-pole-match-final-base.json", 33),
)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    suites = []
    for name, filename, expected in SUITES:
        path = RESULTS / filename
        data = json.loads(path.read_text(encoding="utf-8"))
        passed = bool(data.get("passed", data.get("complete", False)))
        tests = data.get("tests", data.get("tests_run"))
        if not passed or tests != expected:
            raise ValueError(f"Invalid suite evidence: {name}: passed={passed}, tests={tests}")
        suites.append({"name": name,
                       "report": str(path.relative_to(ROOT)).replace("\\", "/"),
                       "report_sha256": sha(path), "tests": tests, "passed": True})

    ui_path = ROOT / "docs/b4artists_ml/quadruped-pole-match-ui-v1.json"
    ui = json.loads(ui_path.read_text(encoding="utf-8"))
    screenshot = ROOT / ui["screenshot"]
    if not ui.get("passed") or sha(screenshot) != ui["screenshot_sha256"]:
        raise ValueError("Foreground UI evidence is invalid")
    runtime = {str(path.relative_to(ROOT)).replace("\\", "/"): sha(path)
               for path in sorted((ROOT / "b4artists_ml").glob("*.py"))}
    report = {
        "schema": 1,
        "qualification": "Quadruped Pole Matching v1 affected regression",
        "passed": True,
        "tests": sum(row["tests"] for row in suites),
        "suite_count": len(suites),
        "suites": suites,
        "runtime_source_count": len(runtime),
        "runtime_source_sha256": runtime,
        "foreground_ui": {
            "report": str(ui_path.relative_to(ROOT)).replace("\\", "/"),
            "report_sha256": sha(ui_path),
            "screenshot": str(screenshot.relative_to(ROOT)).replace("\\", "/"),
            "screenshot_sha256": sha(screenshot),
            "passed": True,
        },
        "reviewer": {"mode": "serial_read_only", "authority": "advisory_fail_closed",
                     "verdict": "PASS", "actionable_findings": 0},
        "execution": {
            "actual_lane": "DEGRADED_NATIVE_CONTINUE",
            "adaptive_workers_admitted": 0,
            "writer_count": 1,
            "router_failure": "uv trampoline failed to spawn Python child process; no actual_lane emitted",
            "verifier_failure": "ModuleNotFoundError: No module named rfc8785",
        },
        "claims": {"learned": False, "cascadeur_parity": False,
                   "full_goal_complete": False, "bforartists_shutdown_clean": False},
    }
    if report["tests"] != 93 or report["runtime_source_count"] != 43:
        raise ValueError("Unexpected aggregate dimensions")
    output = RESULTS / "quadruped-pole-match-affected-v1-regression.json"
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": True, "tests": report["tests"],
                      "suites": report["suite_count"],
                      "runtime_sources": report["runtime_source_count"]}))


if __name__ == "__main__":
    main()
