"""Fail closed if Sphere Proxy from Bounds v1 evidence is stale."""
from pathlib import Path
import ast
import hashlib
import json
import sys


ROOT = Path(__file__).resolve().parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(relative):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def verify_hashes(rows):
    assert all(sha(ROOT / relative) == digest for relative, digest in rows.items())


def main():
    assert sys.flags.optimize == 0
    sources = [
        "b4artists_ml/secondary_motion.py",
        "b4artists_ml/ui.py",
        "tests/test_b4artists_ml_secondary_sphere_proxy_v1.py",
        "training/b4artists_ml/run_secondary_sphere_proxy_affected_v1.py",
        "training/b4artists_ml/check_secondary_sphere_proxy_ui_v1.py",
    ]
    for relative in sources:
        ast.parse((ROOT / relative).read_text(encoding="utf-8"))
    runtime = {
        path.relative_to(ROOT).as_posix(): sha(path)
        for path in sorted((ROOT / "b4artists_ml").glob("*.py"))
    }

    focused = load("training/b4artists_ml/results/secondary-sphere-proxy-focused-v1.json")
    assert (focused["passed"] and focused["tests"] == 5
            and focused["failures"] == focused["errors"] == focused["skips"] == 0
            and focused["python_optimize"] == 0
            and focused["runtime_source_sha256"] == runtime)
    assert focused["test_sha256"] == sha(ROOT / sources[2])
    assert len(focused["dependency_source_sha256"]) == 4
    verify_hashes(focused["dependency_source_sha256"])
    verify_hashes(focused["harness_source_sha256"])

    affected = load("training/b4artists_ml/results/secondary-sphere-proxy-affected-v1-regression.json")
    assert (affected["passed"] and affected["tests"] == 197
            and affected["suite_count"] == 16
            and affected["runtime_source_count"] == len(runtime) == 44
            and affected["runtime_source_sha256"] == runtime)
    verify_hashes({"tests/" + module + ".py": digest
                   for module, digest in affected["test_source_sha256"].items()})
    verify_hashes(affected["dependency_source_sha256"])
    verify_hashes(affected["harness_source_sha256"])
    assert all(row["passed"] and row["assertions_completed_before_shutdown"]
               and row["process_exit_code"] == 3221225477
               and sha(ROOT / row["report"]) == row["report_sha256"]
               for row in affected["suites"])

    ui = load("docs/b4artists_ml/secondary-sphere-proxy-ui-v1.json")
    assert (ui["passed"] and ui["python_optimize"] == 0 and ui["step_count"] == 86
            and ui["source_action_unchanged"] and ui["bounds_source_unchanged"]
            and ui["runtime_source_sha256"] == runtime
            and ui["ui_script_sha256"] == sha(ROOT / sources[4])
            and ui["test_script_sha256"] == sha(ROOT / sources[2]))
    verify_hashes(ui["fixture_source_sha256"])
    assert ui["screenshot_sha256"] == sha(ROOT / ui["screenshot"])

    assert sha(ROOT / "releases/b4artists_ml_v0.36.0.zip") == (
        "3a0423b632cdc0b279a43e45c58321d75833927fb4207d8a2b35d213e282e2e5")
    for relative in (
            "docs/b4artists_ml/DELIVERY-ORDER-v1.md",
            "docs/b4artists_ml/ROADMAP.md",
            "docs/b4artists_ml/REQUIREMENTS.md",
            "docs/b4artists_ml/USER_GUIDE.md"):
        text = (ROOT / relative).read_text(encoding="utf-8")
        assert "Sphere Proxy" in text or "sphere proxy" in text or "Bounds Proxy" in text
        if not relative.endswith("USER_GUIDE.md"):
            assert "197" in text
    print(json.dumps({"passed": True, "ast_files": len(sources),
                      "focused_tests": 5, "affected_tests": 197,
                      "affected_suites": 16, "runtime_sources": len(runtime),
                      "ui_steps": ui["step_count"],
                      "frozen_package_unchanged": True}, indent=2))


if __name__ == "__main__":
    main()
