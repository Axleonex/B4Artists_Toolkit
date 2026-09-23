"""Run and record the host-independent B4ML regression surface.

This deliberately excludes tests whose source imports Blender or orchestration-only
modules. It is complementary evidence, not a substitute for the Bforartists host
regression.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
RESULT = ROOT / "training" / "b4artists_ml" / "results" / "host-independent-regression-v1.json"
VALIDATOR = ROOT / "training" / "b4artists_ml" / "check_host_independent_regression_v1.py"
EXCLUSION_TOKENS = ("bpy", "prime_bridge", "addon_utils")
sys.path.insert(0, str(ROOT))

import pytest


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _discover() -> tuple[list[Path], dict[str, list[str]]]:
    selected: list[Path] = []
    excluded: dict[str, list[str]] = {}
    discovered = {
        path
        for pattern in ("test_b4artists_ml*.py", "test_cascadeur*.py", "test_capsule*.py")
        for path in (ROOT / "tests").glob(pattern)
    }
    for path in sorted(discovered):
        source = path.read_text(encoding="utf-8")
        matches = [token for token in EXCLUSION_TOKENS if token in source]
        relative = path.relative_to(ROOT).as_posix()
        if matches:
            excluded[relative] = matches
        else:
            selected.append(path)
    return selected, excluded


class _ResultCounter:
    collected = 0
    passed = 0
    failed = 0
    errors = 0
    skipped = 0

    def pytest_collection_modifyitems(self, session, config, items):
        self.collected = len(items)

    def pytest_runtest_logreport(self, report):
        if report.when != "call":
            return
        if report.passed:
            self.passed += 1
        elif report.failed:
            self.failed += 1
        elif report.skipped:
            self.skipped += 1

    def pytest_collectreport(self, report):
        if report.failed:
            self.errors += 1


def main() -> dict:
    selected, excluded = _discover()
    counter = _ResultCounter()
    exit_code = pytest.main(["-q", *(str(path) for path in selected)], plugins=[counter])
    report = {
        "schema": "b4ml-host-independent-regression-v1",
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if exit_code == 0 else "FAIL",
        "scope": (
            "Host-independent Python tests only. Files containing bpy, prime_bridge, "
            "or addon_utils are explicitly excluded; this does not replace the "
            "Bforartists-host regression."
        ),
        "selection_rule": {
            "globs": [
                "tests/test_b4artists_ml*.py",
                "tests/test_cascadeur*.py",
                "tests/test_capsule*.py",
            ],
            "excluded_source_tokens": list(EXCLUSION_TOKENS),
        },
        "pytest": {
            "exit_code": exit_code,
            "collected": counter.collected,
            "passed_calls": counter.passed,
            "failed_calls": counter.failed,
            "collection_errors": counter.errors,
            "skipped_calls": counter.skipped,
        },
        "selected_sources": {
            path.relative_to(ROOT).as_posix(): _sha256(path) for path in selected
        },
        "excluded_host_bound_sources": excluded,
        "runner_sha256": _sha256(Path(__file__)),
        "validator": VALIDATOR.relative_to(ROOT).as_posix(),
        "validator_sha256": _sha256(VALIDATOR),
        "claim_boundary": {
            "host_runtime_verified": False,
            "independent_animator_usability_verified": False,
            "learned_temporal_quality_verified": False,
            "cascadeur_comparison_verified": False,
            "full_goal_complete": False,
        },
    }
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if exit_code != 0:
        raise SystemExit(exit_code)
    return report


if __name__ == "__main__":
    main()
