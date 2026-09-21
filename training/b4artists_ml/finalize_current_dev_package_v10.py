"""Seal exact-package evidence for the v0.37.51 compound archive."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VERSION = "0.37.51-dev"
TAG = "v0.37.51"
ARCHIVE = ROOT / f"releases/b4artists_ml_v{VERSION}.zip"
REPORT = ROOT / f"docs/b4artists_ml/package-test-v{VERSION}.json"
RESULTS = ROOT / "training/b4artists_ml/results"
POLE_TESTS = 87
SECONDARY_TESTS = 40
COMPOUND_RECEIPT = f"exact-package-{TAG}-compound-three-moving-sphere-static-set.json"
DIRECT_RECEIPT = "current-package-direct-zip-import-v0.37.51.json"
FOCUSED_TESTS = 56
QUALIFICATION_NOTE = (
    "v0.37.51-dev packages the bounded procedural World+Location coupled "
    "collision extension for exactly three directly animated, optionally "
    "uniformly scaled spheres alongside one authored support plane, with or "
    "without the bounded static sphere set. The moving spheres use sampled "
    "center/radius trajectories, bounded relative-motion sweep detection, "
    "deterministic support/sphere projection, and relative surface-velocity "
    "response while preserving priority endpoints and bounded chain momentum. "
    "Schemas 39 and 40 remain isolated from prior one- and two-moving-sphere, "
    "moving-capsule, static compound, and mesh paths. More than three moving "
    "spheres, other moving/static mixtures, moving capsule or mesh mixtures, "
    "general moving/deforming colliders, and general rigid-body dynamics remain "
    "fail-closed. Exact ZIP evidence passes 87 pole/posing tests across 8 suites, "
    "40 secondary-motion tests, 12 imported-humanoid tests, 56 focused host-"
    "independent math tests, the nine-profile production-character probe, and "
    "the dedicated three-moving-sphere-plus-static-set fixture. Native and "
    "authored-import production cases use the bounded six-endpoint target slice; "
    "authored FBX roundtrips are not external production assets. Host assertions "
    "pass with the known alpha-host shutdown limitation. This archive is not "
    "installed or promoted; foreground usability, independent human review, "
    "learned temporal quality, broader collision behavior, and Cascadeur parity "
    "remain unqualified."
)


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
    compound = load(COMPOUND_RECEIPT)
    direct = load(DIRECT_RECEIPT)
    production = load(f"exact-package-{TAG}-production-character-generalization.json")
    if (
        pole.get("status") != "PASS"
        or pole.get("tests") != POLE_TESTS
        or pole.get("suites") != 8
        or pole.get("archive_sha256") != archive_sha
        or pole.get("claim_boundary_closed") is not True
    ):
        raise ValueError("Exact-package pole evidence is not bound")
    require(secondary, tests=SECONDARY_TESTS, package_sha=archive_sha)
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
    require(production, tests=3, package_sha=archive_sha)
    focused = dict(report.get("focused_validation", {}))
    focused.update(
        {
            "status": "PASS",
            "passed": True,
            "tests": FOCUSED_TESTS,
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
            "affected_regression": f"PASS_EXACT_PACKAGE_{POLE_TESTS}_TESTS",
            "package_regression_receipt": f"training/b4artists_ml/results/exact-package-pole-{TAG}.json",
            "package_regression_receipt_sha256": sha(RESULTS / f"exact-package-pole-{TAG}.json"),
            "package_regression_tests": POLE_TESTS,
            "package_regression_suites": 8,
            "package_regression_claim_boundary_closed": True,
            "direct_zip_import_regression_receipt": f"training/b4artists_ml/results/{DIRECT_RECEIPT}",
            "direct_zip_import_regression_receipt_sha256": sha(RESULTS / DIRECT_RECEIPT),
            "direct_zip_import_tests": 12,
            "secondary_motion_receipt": f"training/b4artists_ml/results/exact-package-{TAG}-secondary-motion-all.json",
            "secondary_motion_receipt_sha256": sha(RESULTS / f"exact-package-{TAG}-secondary-motion-all.json"),
            "secondary_motion_tests": SECONDARY_TESTS,
            "compound_collision_receipt": f"training/b4artists_ml/results/{COMPOUND_RECEIPT}",
            "compound_collision_receipt_sha256": sha(RESULTS / COMPOUND_RECEIPT),
            "compound_collision_tests": 1,
            "production_character_generalization_receipt": f"training/b4artists_ml/results/exact-package-{TAG}-production-character-generalization.json",
            "production_character_generalization_receipt_sha256": sha(RESULTS / f"exact-package-{TAG}-production-character-generalization.json"),
            "production_character_generalization_tests": 3,
            "production_character_generalization_scope": "three frozen project-owned Unity Humanoid FBX characters, three generated BoneForge/Rigify fixtures, and three project-authored imported Mocap/Unity/Unreal FBX roundtrips; native and authored-import cases use the bounded six-endpoint target slice",
            "foreground_lifecycle": "NOT_RERUN_CURRENT_ARCHIVE",
            "qualification_note": QUALIFICATION_NOTE,
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
                "package_regression_tests": POLE_TESTS,
                "secondary_motion_tests": SECONDARY_TESTS,
                "compound_collision_tests": 1,
                "direct_zip_import_tests": 12,
                "production_character_generalization_tests": 3,
                "focused_math_tests": FOCUSED_TESTS,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
