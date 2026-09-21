"""Validate and bind the complete quadruped per-target reset evidence set."""
from pathlib import Path
import hashlib
import json


ROOT = Path(__file__).resolve().parents[2]
FOCUSED = ROOT / "training/b4artists_ml/results/quadruped-target-reset-focused-v1.json"
AFFECTED = ROOT / "training/b4artists_ml/results/quadruped-target-reset-affected-v1-regression.json"
UI = ROOT / "docs/b4artists_ml/quadruped-target-reset-ui-v1.json"
ROUTING = ROOT / "docs/b4artists_ml/quadruped-target-reset-routing-v1.json"
OUTPUT = ROOT / "training/b4artists_ml/results/quadruped-target-reset-v1-final.json"


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
    if (not focused.get("passed") or focused.get("tests") != 9 or
            focused.get("failures") or focused.get("errors") or
            focused.get("runtime_source_sha256") != runtime or
            not affected.get("passed") or affected.get("tests") != 107 or
            affected.get("suite_count") != 14 or
            affected.get("runtime_source_sha256") != runtime or
            not ui.get("passed") or not ui.get("native_undo_redo_verified") or
            ui.get("screenshot_sha256") != sha(screenshot) or
            routing.get("reviewer_verdict") != "PASS"):
        raise ValueError("Quadruped target-reset evidence is incomplete or stale")
    result = {
        "schema": 1,
        "qualification": "Quadruped per-target reset v1",
        "passed": True,
        "focused": {"tests": 9,
                    "report": str(FOCUSED.relative_to(ROOT)).replace("\\", "/"),
                    "report_sha256": sha(FOCUSED)},
        "affected": {"tests": 107, "suites": 14,
                     "report": str(AFFECTED.relative_to(ROOT)).replace("\\", "/"),
                     "report_sha256": sha(AFFECTED)},
        "foreground_ui": {"passed": True, "native_undo_redo_verified": True,
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
            "verifier_failure": "ModuleNotFoundError: No module named rfc8785",
        },
        "claims": {"procedural": True, "learned": False,
                   "cascadeur_parity": False, "full_goal_complete": False,
                   "bforartists_shutdown_clean": False},
    }
    if result["runtime_source_count"] != 44:
        raise ValueError("Unexpected runtime source count")
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": True, "focused_tests": 9, "affected_tests": 107,
                      "affected_suites": 14, "runtime_sources": 44,
                      "report": str(OUTPUT)}))


if __name__ == "__main__":
    main()
