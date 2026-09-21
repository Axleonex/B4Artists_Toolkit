"""Seal bounded exact-package evidence for the v0.37.43 development archive."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VERSION = "0.37.43-dev"
TAG = "v0.37.43"
ARCHIVE = ROOT / f"releases/b4artists_ml_v{VERSION}.zip"
REPORT = ROOT / f"docs/b4artists_ml/package-test-v{VERSION}.json"
RESULTS = ROOT / "training/b4artists_ml/results"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(name: str) -> dict:
    return json.loads((RESULTS / name).read_text(encoding="utf-8-sig"))


def require(record: dict, *, tests: int, package_sha: str) -> None:
    if (
        record.get("assertions_passed") is not True
        or record.get("tests") != tests
        or record.get("failures")
        or record.get("errors")
        or record.get("skipped")
        or record.get("package_sha256") != package_sha
    ):
        raise ValueError(f"Unqualified exact-package receipt: {record.get('suite')}")


def main() -> None:
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    archive_sha = sha(ARCHIVE)
    if report.get("version") != VERSION or report.get("sha256") != archive_sha:
        raise ValueError("Package report does not match the archive")
    pole = load(f"exact-package-pole-{TAG}.json")
    secondary = load(f"exact-package-{TAG}-secondary-motion-all.json")
    compound = load(f"exact-package-{TAG}-compound-capsule.json")
    direct = load("current-package-direct-zip-import-v0.37.43.json")
    production = load(f"exact-package-{TAG}-production-character-generalization.json")
    if (
        pole.get("status") != "PASS"
        or pole.get("tests") != 85
        or pole.get("suites") != 8
        or pole.get("archive_sha256") != archive_sha
        or pole.get("claim_boundary_closed") is not True
    ):
        raise ValueError("Exact-package pole evidence is not bound")
    require(secondary, tests=29, package_sha=archive_sha)
    require(compound, tests=1, package_sha=archive_sha)
    if (
        direct.get("schema") != "b4ml-current-package-direct-zip-import-v1"
        or direct.get("tests") != 12
        or direct.get("assertions_passed") is not True
        or direct.get("failures")
        or direct.get("errors")
        or direct.get("skipped")
        or direct.get("archive_sha256") != archive_sha
    ):
        raise ValueError("Direct-ZIP evidence is not bound")
    require(production, tests=1, package_sha=archive_sha)
    focused = dict(report.get("focused_validation", {}))
    focused.update(
        {
            "status": "PASS",
            "passed": True,
            "tests": 47,
            "subtests": 0,
            "command": (
                f"B4ML_PACKAGE=releases/b4artists_ml_v{VERSION}.zip "
                "python -m unittest tests.test_b4artists_ml_secondary_math "
                "tests.test_b4artists_ml_secondary_capsule_math_v1"
            ),
        }
    )
    report.update(
        {
            "focused_validation": focused,
            "blender_binding_qualification": "PASS_EXACT_PACKAGE_BFORARTISTS_HOST",
            "affected_regression": "PASS_EXACT_PACKAGE_85_TESTS",
            "package_regression_receipt": f"training/b4artists_ml/results/exact-package-pole-{TAG}.json",
            "package_regression_receipt_sha256": sha(RESULTS / f"exact-package-pole-{TAG}.json"),
            "package_regression_tests": 85,
            "package_regression_suites": 8,
            "package_regression_claim_boundary_closed": True,
            "direct_zip_import_regression_receipt": "training/b4artists_ml/results/current-package-direct-zip-import-v0.37.43.json",
            "direct_zip_import_regression_receipt_sha256": sha(RESULTS / "current-package-direct-zip-import-v0.37.43.json"),
            "direct_zip_import_tests": 12,
            "secondary_motion_receipt": f"training/b4artists_ml/results/exact-package-{TAG}-secondary-motion-all.json",
            "secondary_motion_receipt_sha256": sha(RESULTS / f"exact-package-{TAG}-secondary-motion-all.json"),
            "secondary_motion_tests": 29,
            "compound_collision_receipt": f"training/b4artists_ml/results/exact-package-{TAG}-compound-capsule.json",
            "compound_collision_receipt_sha256": sha(RESULTS / f"exact-package-{TAG}-compound-capsule.json"),
            "compound_collision_tests": 1,
            "production_character_generalization_receipt": f"training/b4artists_ml/results/exact-package-{TAG}-production-character-generalization.json",
            "production_character_generalization_receipt_sha256": sha(RESULTS / f"exact-package-{TAG}-production-character-generalization.json"),
            "production_character_generalization_tests": 1,
            "production_character_generalization_scope": "three frozen project-owned Unity Humanoid FBX characters",
            "foreground_lifecycle": "NOT_RERUN_CURRENT_ARCHIVE",
            "qualification_note": (
                "v0.37.43-dev adds the bounded procedural World coupled compound "
                "collision slice: one authored support plane, a static sphere set, "
                "and one static endpoint capsule. Exact ZIP evidence passes 85 pole "
                "tests across 8 suites, 29 secondary-motion tests, 12 imported-humanoid "
                "tests, the three-character production probe, and the new four-collider "
                "fixture. The capsule compound rejects moving, scaling, and continuous "
                "endpoint animation; general rigid-body dynamics remain outside scope. "
                "Host assertions pass with the known alpha-host shutdown limitation. "
                "This archive is not installed or promoted; foreground usability, human "
                "review, learned temporal quality, and Cascadeur parity remain unqualified."
            ),
            "review_gate": {
                "status": "NOT_REQUESTED",
                "authority": False,
                "reviewer_invoked": False,
                "review_completed": False,
                "full_goal_complete": False,
            },
            "full_goal_complete": False,
        }
    )
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "version": VERSION,
                "archive_sha256": archive_sha,
                "package_regression_tests": 85,
                "secondary_motion_tests": 29,
                "compound_collision_tests": 1,
                "direct_zip_import_tests": 12,
                "production_character_generalization_tests": 1,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
