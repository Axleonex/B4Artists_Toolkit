"""Validate and bind the complete quadruped Pole Controls v1 evidence set."""
from pathlib import Path
import hashlib
import json


ROOT = Path(__file__).resolve().parents[2]
FOCUSED = ROOT / "training/b4artists_ml/results/quadruped-pole-controls-focused-v1.json"
AFFECTED = ROOT / "training/b4artists_ml/results/quadruped-pole-controls-affected-v1-regression.json"
UI = ROOT / "docs/b4artists_ml/quadruped-pole-controls-ui-v1.json"
UI_SCRIPT = ROOT / "training/b4artists_ml/check_quadruped_pole_controls_ui_v1.py"
FIXTURE_SCRIPT = ROOT / "tests/test_b4artists_ml_quadruped_pose.py"
ALIGN_TEST = ROOT / "tests/test_b4artists_ml_quadruped_pole_align_v1.py"
TEST = ROOT / "tests/test_b4artists_ml_quadruped_pole_controls_v1.py"
RUNNER = ROOT / "training/b4artists_ml/run_quadruped_pole_controls_affected_v1.py"
HARNESS = ROOT / "training/b4artists_ml/run_unittest_report.py"
ROUTING = ROOT / "docs/b4artists_ml/quadruped-pole-controls-routing-v1.json"
OUTPUT = ROOT / "training/b4artists_ml/results/quadruped-pole-controls-v1-final.json"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    focused = json.loads(FOCUSED.read_text(encoding="utf-8"))
    affected = json.loads(AFFECTED.read_text(encoding="utf-8"))
    ui = json.loads(UI.read_text(encoding="utf-8"))
    routing = json.loads(ROUTING.read_text(encoding="utf-8"))
    screenshot = ROOT / ui["screenshot"]
    runtime = {str(path.relative_to(ROOT)).replace("\\", "/"): sha(path)
               for path in sorted((ROOT / "b4artists_ml").glob("*.py"))}
    support = {
        str(FIXTURE_SCRIPT.relative_to(ROOT)).replace("\\", "/"): sha(FIXTURE_SCRIPT),
        str(ALIGN_TEST.relative_to(ROOT)).replace("\\", "/"): sha(ALIGN_TEST),
    }
    if (not focused.get("passed") or focused.get("tests") != 8 or
            focused.get("failures") or focused.get("errors") or
            focused.get("runtime_source_sha256") != runtime or
            focused.get("test_sha256") != sha(TEST) or
            focused.get("support_source_sha256") != support or
            not affected.get("passed") or affected.get("tests") != 136 or
            affected.get("suite_count") != 18 or
            affected.get("runtime_source_count") != len(runtime) or
            affected.get("runtime_source_sha256") != runtime or
            affected.get("test_source_sha256", {}).get(TEST.stem) != sha(TEST) or
            affected.get("runner_sha256") != sha(RUNNER) or
            affected.get("unittest_harness_sha256") != sha(HARNESS) or
            not ui.get("passed") or not ui.get("flip_operator_verified") or
            not ui.get("distance_operator_verified") or
            not ui.get("native_undo_redo_verified") or
            not ui.get("helper_pointer_preserved") or
            not ui.get("distance_undo_redo_verified") or
            not ui.get("payload_undo_redo_verified") or
            not ui.get("source_pose_unchanged") or
            not ui.get("source_action_unchanged") or
            not ui.get("complete_action_digest_verified") or
            not ui.get("action_slot_verified") or not ui.get("modes_unchanged") or
            ui.get("visible_pole_labels") !=
            ["Fore L Pole", "Fore R Pole", "Hind L Pole", "Hind R Pole"] or
            ui.get("narrow_panel_width", 9999) > 300 or
            ui.get("runtime_source_count") != len(runtime) or
            ui.get("runtime_source_sha256") != runtime or
            ui.get("ui_script_sha256") != sha(UI_SCRIPT) or
            ui.get("fixture_script_sha256") != sha(FIXTURE_SCRIPT) or
            ui.get("test_script_sha256") != sha(TEST) or
            ui.get("screenshot_sha256") != sha(screenshot) or
            routing.get("reviewer_verdict") != "PASS" or
            routing.get("actual_lane") != "DEGRADED_NATIVE_CONTINUE" or
            routing.get("outcome") != "fallback"):
        raise ValueError("Quadruped Pole Controls evidence is incomplete or stale")
    result = {
        "schema": 1,
        "qualification": "Quadruped Pole Controls v1",
        "passed": True,
        "focused": {"tests": 8,
                    "report": str(FOCUSED.relative_to(ROOT)).replace("\\", "/"),
                    "report_sha256": sha(FOCUSED)},
        "affected": {"tests": 136, "suites": 18,
                     "report": str(AFFECTED.relative_to(ROOT)).replace("\\", "/"),
                     "report_sha256": sha(AFFECTED)},
        "foreground_ui": {"passed": True, "flip_operator_verified": True,
                          "distance_operator_verified": True,
                          "native_undo_redo_verified": True,
                          "report": str(UI.relative_to(ROOT)).replace("\\", "/"),
                          "report_sha256": sha(UI),
                          "screenshot": str(screenshot.relative_to(ROOT)).replace("\\", "/"),
                          "screenshot_sha256": sha(screenshot)},
        "routing": {"report": str(ROUTING.relative_to(ROOT)).replace("\\", "/"),
                    "report_sha256": sha(ROUTING)},
        "runtime_source_count": len(runtime),
        "runtime_source_sha256": runtime,
        "reviewer": {"mode": "serial_read_only", "authority": "advisory_fail_closed",
                     "verdict": "PASS", "actionable_findings": 0},
        "execution": {
            "actual_lane": "DEGRADED_NATIVE_CONTINUE",
            "adaptive_workers_admitted": 0,
            "writer_count": 1,
            "router_failure": "uv trampoline failed to spawn Python child process; no actual_lane emitted",
            "failed_binding": "canonical evidence venv points to a missing former-user uv Python home"
        },
        "claims": {"procedural": True, "learned": False,
                   "cascadeur_parity": False, "full_goal_complete": False,
                   "bforartists_shutdown_clean": False}
    }
    if result["runtime_source_count"] != 44:
        raise ValueError("Unexpected runtime source count")
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": True, "focused_tests": 8, "affected_tests": 136,
                      "affected_suites": 18, "runtime_sources": 44,
                      "report": str(OUTPUT)}))


if __name__ == "__main__":
    main()
