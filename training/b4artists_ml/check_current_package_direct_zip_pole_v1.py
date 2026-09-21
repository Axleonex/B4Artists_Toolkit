"""Validate the complete pole-control regression executed from the current ZIP."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = ROOT / "releases" / "b4artists_ml_v0.37.29-dev.zip"
PACKAGE_REPORT = ROOT / "docs" / "b4artists_ml" / "package-test-v0.37.29-dev.json"
RAW_RECEIPT = ROOT / "training" / "b4artists_ml" / "results" / "current-zip-pole-v2-regression.json"
OUTPUT = ROOT / "training" / "b4artists_ml" / "results" / "current-package-direct-zip-pole-validation-v1.json"

EXPECTED_TESTS = {
    "test_b4artists_ml_pole_align_v1": 6,
    "test_b4artists_ml_pole_flip_v1": 4,
    "test_b4artists_ml_pole_distance_v1": 5,
    "test_b4artists_ml_target_reset_v1": 8,
    "test_b4artists_ml_target_mirror_v1": 7,
    "test_b4artists_ml_body_controls": 8,
    "test_b4artists_ml_context_preview": 10,
    "test_b4artists_ml": 34,
}
KNOWN_SHUTDOWN_EXITS = {0, 1, -1073741819, 3221225477}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    package = json.loads(PACKAGE_REPORT.read_text(encoding="utf-8-sig"))
    rows = json.loads(RAW_RECEIPT.read_text(encoding="utf-8-sig"))
    archive_sha256 = sha256(ARCHIVE)
    row_by_suite = {row.get("suite"): row for row in rows}
    runtime_matches = all(
        row.get("runtime_sha256", {}).get(name) == digest
        for row in rows
        for name, digest in row.get("runtime_sha256", {}).items()
        if name in package.get("runtime_sha256", {})
    )
    assertions_passed = (
        package.get("version") == "0.37.29-dev"
        and package.get("package_matches_source") is True
        and package.get("sha256") == archive_sha256
        and set(row_by_suite) == set(EXPECTED_TESTS)
        and all(
            row.get("tests") == expected
            and row.get("assertions_passed") is True
            and not row.get("failures")
            and not row.get("errors")
            and not row.get("skipped")
            and row.get("host_exit") in KNOWN_SHUTDOWN_EXITS
            for suite, expected in EXPECTED_TESTS.items()
            for row in [row_by_suite[suite]]
        )
        and runtime_matches
    )
    record = {
        "schema": "b4ml-current-package-direct-zip-pole-validation-v1",
        "status": "PASS" if assertions_passed else "FAIL",
        "archive": str(ARCHIVE),
        "archive_sha256": archive_sha256,
        "package_report": str(PACKAGE_REPORT.relative_to(ROOT)),
        "raw_receipt": str(RAW_RECEIPT.relative_to(ROOT)),
        "raw_receipt_sha256": sha256(RAW_RECEIPT),
        "suites": len(rows),
        "tests": sum(row.get("tests", 0) for row in rows),
        "runtime_matches_source": runtime_matches,
        "known_shutdown_exits": sorted(KNOWN_SHUTDOWN_EXITS),
        "claim_boundary_closed": True,
    }
    OUTPUT.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(record, indent=2))
    if not assertions_passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
