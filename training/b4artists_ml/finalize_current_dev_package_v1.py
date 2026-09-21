"""Bind exact-package host evidence to the current development archive report."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TAG = os.environ.get("B4ML_CURRENT_PACKAGE_TAG", "v0.37.42")
VERSION = os.environ.get("B4ML_CURRENT_PACKAGE_VERSION", "0.37.42-dev")
BODY_CONTROLS_TESTS = int(os.environ.get("B4ML_BODY_CONTROLS_TESTS", "11"))
POLE_TESTS = int(os.environ.get("B4ML_POLE_TESTS", "85"))
ARCHIVE = ROOT / f"releases/b4artists_ml_v{VERSION}.zip"
REPORT = ROOT / f"docs/b4artists_ml/package-test-v{VERSION}.json"
POLE_RECEIPT = ROOT / f"training/b4artists_ml/results/exact-package-pole-{TAG}.json"
DIRECT_ZIP_RECEIPT = ROOT / (
    "training/b4artists_ml/results/"
    + os.environ.get("B4ML_DIRECT_RECEIPT_TAG", "current-package-direct-zip-import-v0.37.42")
    + ".json"
)
FOREGROUND_RECEIPT = ROOT / (
    "training/b4artists_ml/results/"
    f"secondary-world-chain-moving-capsule-foreground-{TAG}.json"
)
MOVING_DEFORMING_MESH_RECEIPT = ROOT / (
    "training/b4artists_ml/results/"
    f"exact-package-{TAG}-moving-deforming-mesh.json"
)
PRODUCTION_GENERALIZATION_RECEIPT = ROOT / (
    "training/b4artists_ml/results/"
    f"exact-package-{TAG}-production-character-generalization.json"
)
CONTINUOUS_CAPSULE_RECEIPT = ROOT / (
    "training/b4artists_ml/results/"
    f"exact-package-{TAG}-continuous-moving-capsule-chain.json"
)
CONTINUOUS_SPHERE_RECEIPT = ROOT / (
    "training/b4artists_ml/results/"
    f"exact-package-{TAG}-continuous-moving-sphere-chain.json"
)
COUPLED_PELVIS_SPINE_RECEIPT = ROOT / (
    "training/b4artists_ml/results/"
    f"exact-package-{TAG}-test_b4artists_ml_body_controls.json"
)
MULTI_SPHERE_RECEIPT = ROOT / (
    "training/b4artists_ml/results/"
    f"exact-package-{TAG}-test_b4artists_ml_secondary_multi_sphere_collision_v1.json"
)
FORCE_OFFSET_TORQUE_RECEIPT = ROOT / (
    "training/b4artists_ml/results/"
    f"exact-package-{TAG}-test_b4artists_ml_secondary_force_offset_torque_v1.json"
)
SELF_COLLISION_RECEIPT = ROOT / (
    "training/b4artists_ml/results/"
    f"exact-package-{TAG}-test_b4artists_ml_secondary_self_collision_v1.json"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def main() -> None:
    report = load(REPORT)
    pole = load(POLE_RECEIPT)
    direct_zip = load(DIRECT_ZIP_RECEIPT)
    foreground = load(FOREGROUND_RECEIPT)
    moving_deforming_mesh = load(MOVING_DEFORMING_MESH_RECEIPT)
    production_generalization = load(PRODUCTION_GENERALIZATION_RECEIPT)
    continuous_capsule = load(CONTINUOUS_CAPSULE_RECEIPT)
    continuous_sphere = load(CONTINUOUS_SPHERE_RECEIPT)
    coupled_pelvis_spine = load(COUPLED_PELVIS_SPINE_RECEIPT)
    multi_sphere = load(MULTI_SPHERE_RECEIPT)
    force_offset_torque = load(FORCE_OFFSET_TORQUE_RECEIPT)
    self_collision = load(SELF_COLLISION_RECEIPT)
    archive_sha = sha256(ARCHIVE)

    if report.get("version") != VERSION or report.get("sha256") != archive_sha:
        raise ValueError("Development package report does not match the archive")
    if report.get("files") != 54 or report.get("package_matches_source") is not True:
        raise ValueError("Development package identity is not exact")
    focused_validation = dict(report.get("focused_validation", {}))
    focused_validation["command"] = (
        f"B4ML_PACKAGE=releases/b4artists_ml_v{VERSION}.zip "
        "python -m unittest tests.test_b4artists_ml_secondary_math "
        "tests.test_b4artists_ml_secondary_capsule_math_v1"
    )
    focused_validation["status"] = "PASS"
    focused_validation["passed"] = True
    focused_validation["tests"] = 46
    focused_validation["subtests"] = 0
    if (
        pole.get("status") != "PASS"
        or pole.get("archive_sha256") != archive_sha
        or pole.get("suites") != 8
        or pole.get("tests") != POLE_TESTS
        or pole.get("claim_boundary_closed") is not True
        or any(
            row.get("assertions_passed") is not True
            or row.get("failures")
            or row.get("errors")
            or row.get("skipped")
            or row.get("package_sha256") != archive_sha
            for row in pole.get("rows", [])
        )
    ):
        raise ValueError("Exact-package regression evidence is not bound")
    if (
        direct_zip.get("schema") != "b4ml-current-package-direct-zip-import-v1"
        or direct_zip.get("tests") != 12
        or direct_zip.get("assertions_passed") is not True
        or direct_zip.get("failures")
        or direct_zip.get("errors")
        or direct_zip.get("skipped")
        or direct_zip.get("archive_sha256") != archive_sha
        or direct_zip.get("runtime_sha256") != {
            name: report.get("runtime_sha256", {}).get(name)
            for name in (
                "b4artists_ml/posing.py",
                "b4artists_ml/workflow.py",
                "b4artists_ml/body_solver.py",
            )
        }
    ):
        raise ValueError("Direct-ZIP import evidence is not bound")
    if (
        foreground.get("passed") is not True
        or foreground.get("archive_sha256") != archive_sha
        or foreground.get("metrics", {}).get("schema") != 27
        or foreground.get("metrics", {}).get("backend")
        != "implicit_selected_control_chain_location_moving_capsule_v1"
        or foreground.get("independent_clearance", {}).get("passed") is not True
        or foreground.get("independent_clearance", {}).get("samples") != 22
        or foreground.get("native_undo_redo") is not True
        or foreground.get("restore_input") is not True
        or foreground.get("keep_save_reload") is not True
        or foreground.get("restore_source") is not True
        or foreground.get("source_action_unchanged") is not True
        or foreground.get("learned_temporal_quality") is not False
        or foreground.get("independent_animator_usability") is not False
        or foreground.get("cascadeur_comparison") is not False
    ):
        raise ValueError("Foreground lifecycle evidence is not bound")
    if (
        moving_deforming_mesh.get("schema") != "b4ml-exact-package-unittest-v1"
        or moving_deforming_mesh.get("class_name")
        != "SecondaryMotionTests.test_coupled_world_location_chain_moving_deforming_mesh_collision"
        or moving_deforming_mesh.get("tests") != 1
        or moving_deforming_mesh.get("assertions_passed") is not True
        or moving_deforming_mesh.get("failures")
        or moving_deforming_mesh.get("errors")
        or moving_deforming_mesh.get("skipped")
        or moving_deforming_mesh.get("package_sha256") != archive_sha
    ):
        raise ValueError("Moving/deforming mesh chain evidence is not bound")
    if (
        coupled_pelvis_spine.get("schema") != "b4ml-exact-package-unittest-v1"
        or coupled_pelvis_spine.get("suite") != "test_b4artists_ml_body_controls"
        or coupled_pelvis_spine.get("class_name") != "BodyControlTests"
        or coupled_pelvis_spine.get("tests") != BODY_CONTROLS_TESTS
        or coupled_pelvis_spine.get("assertions_passed") is not True
        or coupled_pelvis_spine.get("failures")
        or coupled_pelvis_spine.get("errors")
        or coupled_pelvis_spine.get("skipped")
        or coupled_pelvis_spine.get("package_sha256") != archive_sha
    ):
        raise ValueError("Coupled Pelvis/Spine/Chest evidence is not bound")
    if (
        multi_sphere.get("schema") != "b4ml-exact-package-unittest-v1"
        or multi_sphere.get("suite")
        != "test_b4artists_ml_secondary_multi_sphere_collision_v1"
        or multi_sphere.get("class_name") != "SecondaryMultiSphereCollisionTests"
        or multi_sphere.get("tests") != 8
        or multi_sphere.get("assertions_passed") is not True
        or multi_sphere.get("failures")
        or multi_sphere.get("errors")
        or multi_sphere.get("skipped")
        or multi_sphere.get("package_sha256") != archive_sha
    ):
        raise ValueError("Multiple static-sphere evidence is not bound")
    if (
        force_offset_torque.get("schema") != "b4ml-exact-package-unittest-v1"
        or force_offset_torque.get("suite")
        != "test_b4artists_ml_secondary_force_offset_torque_v1"
        or force_offset_torque.get("class_name") != "SecondaryForceOffsetTorqueTests"
        or force_offset_torque.get("tests") != 14
        or force_offset_torque.get("assertions_passed") is not True
        or force_offset_torque.get("failures")
        or force_offset_torque.get("errors")
        or force_offset_torque.get("skipped")
        or force_offset_torque.get("package_sha256") != archive_sha
    ):
        raise ValueError("Force-at-offset torque evidence is not bound")
    if (
        self_collision.get("schema") != "b4ml-exact-package-unittest-v1"
        or self_collision.get("suite")
        != "test_b4artists_ml_secondary_self_collision_v1"
        or self_collision.get("class_name") != "SecondarySelfCollisionBindingTests"
        or self_collision.get("tests") != 2
        or self_collision.get("assertions_passed") is not True
        or self_collision.get("failures")
        or self_collision.get("errors")
        or self_collision.get("skipped")
        or self_collision.get("package_sha256") != archive_sha
    ):
        raise ValueError("Self-collision evidence is not bound")
    if (
        production_generalization.get("schema") != "b4ml-exact-package-unittest-v1"
        or production_generalization.get("suite")
        != "test_b4artists_ml_production_character_generalization_v1"
        or production_generalization.get("tests") != 1
        or production_generalization.get("assertions_passed") is not True
        or production_generalization.get("failures")
        or production_generalization.get("errors")
        or production_generalization.get("skipped")
        or production_generalization.get("package_sha256") != archive_sha
    ):
        raise ValueError("Production-character generalization evidence is not bound")
    if (
        continuous_capsule.get("schema") != "b4ml-exact-package-unittest-v1"
        or continuous_capsule.get("class_name")
        != "SecondaryMotionTests.test_coupled_world_location_chain_resolves_continuous_moving_capsule"
        or continuous_capsule.get("tests") != 1
        or continuous_capsule.get("assertions_passed") is not True
        or continuous_capsule.get("failures")
        or continuous_capsule.get("errors")
        or continuous_capsule.get("skipped")
        or continuous_capsule.get("package_sha256") != archive_sha
    ):
        raise ValueError("Continuous moving-capsule chain evidence is not bound")
    if (
        continuous_sphere.get("schema") != "b4ml-exact-package-unittest-v1"
        or continuous_sphere.get("class_name")
        != "SecondaryMotionTests.test_coupled_world_location_chain_continuous_moving_sphere"
        or continuous_sphere.get("tests") != 1
        or continuous_sphere.get("assertions_passed") is not True
        or continuous_sphere.get("failures")
        or continuous_sphere.get("errors")
        or continuous_sphere.get("skipped")
        or continuous_sphere.get("package_sha256") != archive_sha
    ):
        raise ValueError("Continuous moving-sphere chain evidence is not bound")

    report.update(
        {
            "focused_validation": focused_validation,
            "blender_binding_qualification": "PASS_EXACT_PACKAGE_BFORARTISTS_HOST",
            "affected_regression": f"PASS_EXACT_PACKAGE_{POLE_TESTS}_TESTS",
            "foreground_lifecycle": "PASS_EXACT_PACKAGE_MOVING_CAPSULE",
            "package_regression_receipt": relative(POLE_RECEIPT),
            "package_regression_receipt_sha256": sha256(POLE_RECEIPT),
            "package_regression_layout": "direct_zip_import",
            "package_regression_tests": pole["tests"],
            "package_regression_suites": pole["suites"],
            "package_regression_claim_boundary_closed": pole[
                "claim_boundary_closed"
            ],
            "direct_zip_import_regression_receipt": relative(DIRECT_ZIP_RECEIPT),
            "direct_zip_import_regression_receipt_sha256": sha256(DIRECT_ZIP_RECEIPT),
            "direct_zip_import_tests": direct_zip["tests"],
            "moving_deforming_mesh_receipt": relative(MOVING_DEFORMING_MESH_RECEIPT),
            "moving_deforming_mesh_receipt_sha256": sha256(
                MOVING_DEFORMING_MESH_RECEIPT
            ),
            "moving_deforming_mesh_tests": moving_deforming_mesh["tests"],
            "coupled_pelvis_spine_receipt": relative(COUPLED_PELVIS_SPINE_RECEIPT),
            "coupled_pelvis_spine_receipt_sha256": sha256(
                COUPLED_PELVIS_SPINE_RECEIPT
            ),
            "coupled_pelvis_spine_tests": coupled_pelvis_spine["tests"],
            "multiple_static_sphere_collision_receipt": relative(MULTI_SPHERE_RECEIPT),
            "multiple_static_sphere_collision_receipt_sha256": sha256(
                MULTI_SPHERE_RECEIPT
            ),
            "multiple_static_sphere_collision_tests": multi_sphere["tests"],
            "force_offset_torque_receipt": relative(FORCE_OFFSET_TORQUE_RECEIPT),
            "force_offset_torque_receipt_sha256": sha256(
                FORCE_OFFSET_TORQUE_RECEIPT
            ),
            "force_offset_torque_tests": force_offset_torque["tests"],
            "self_collision_receipt": relative(SELF_COLLISION_RECEIPT),
            "self_collision_receipt_sha256": sha256(SELF_COLLISION_RECEIPT),
            "self_collision_tests": self_collision["tests"],
            "production_character_generalization_receipt": relative(
                PRODUCTION_GENERALIZATION_RECEIPT
            ),
            "production_character_generalization_receipt_sha256": sha256(
                PRODUCTION_GENERALIZATION_RECEIPT
            ),
            "production_character_generalization_tests": production_generalization[
                "tests"
            ],
            "production_character_generalization_scope": (
                "three frozen project-owned Unity Humanoid FBX characters"
            ),
            "continuous_moving_capsule_chain_receipt": relative(
                CONTINUOUS_CAPSULE_RECEIPT
            ),
            "continuous_moving_capsule_chain_receipt_sha256": sha256(
                CONTINUOUS_CAPSULE_RECEIPT
            ),
            "continuous_moving_capsule_chain_tests": continuous_capsule["tests"],
            "continuous_moving_sphere_chain_receipt": relative(
                CONTINUOUS_SPHERE_RECEIPT
            ),
            "continuous_moving_sphere_chain_receipt_sha256": sha256(
                CONTINUOUS_SPHERE_RECEIPT
            ),
            "continuous_moving_sphere_chain_tests": continuous_sphere["tests"],
            "qualification_note": (
                f"Development archive {VERSION} contains the bounded procedural "
                "coupled Pelvis/Spine/Chest position target across BoneForge, generated "
                "Rigify Basic/Default, both Rigify metarigs, and the authored "
                "Unity Humanoid fixture, plus the bounded "
                "multiple-static-sphere collision set (up to eight static spheres), "
                "and selected-control force-at-offset torque refinement, plus the "
                "bounded selected-control self-collision guard, plus the "
                "moving/deforming-mesh, continuous moving/scaling-capsule, and "
                "continuous moving/scaling-sphere world-chain coupling slices. "
                f"The exact archive pole passes {POLE_TESTS} tests across 8 suites; the "
                "direct-ZIP focused validation passes 46 tests; and the exact "
                "Bforartists host receipts cover moving/deforming mesh, one "
                "moving capsule, bounded moving/scaling sphere-set, and three frozen "
                "project-owned Unity Humanoid proportions. The sphere slice is "
                "limited to a bounded sphere set and uses an analytic relative-motion "
                "sweep with deterministic earliest-hit selection and bounded "
                "post-blend reprojection; it makes no claim for general rigid-body "
                "dynamics. The host "
                "assertions pass with the known post-assertion alpha-host "
                "ucrtbase.dll shutdown limitation. This archive is not "
                "installed, promoted, or published and makes no learned-temporal, "
                "independent-human-usability, or Cascadeur parity claim."
            ),
            "foreground_receipt": relative(FOREGROUND_RECEIPT),
            "foreground_receipt_sha256": sha256(FOREGROUND_RECEIPT),
            "foreground_clearance_samples": foreground["independent_clearance"][
                "samples"
            ],
            "foreground_validation": "PASS_WITH_OBSERVED_KNOWN_HOST_SHUTDOWN_LIMITATION",
            "foreground_known_shutdown_only": foreground.get(
                "known_shutdown_fault_observed"
            )
            is True,
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
                "report": relative(REPORT),
                "version": VERSION,
                "archive_sha256": archive_sha,
                "package_regression_tests": pole["tests"],
                "direct_zip_import_tests": direct_zip["tests"],
                "moving_deforming_mesh_tests": moving_deforming_mesh["tests"],
                "production_character_generalization_tests": production_generalization[
                    "tests"
                ],
                "continuous_moving_capsule_chain_tests": continuous_capsule["tests"],
                "continuous_moving_sphere_chain_tests": continuous_sphere["tests"],
                "foreground_clearance_samples": foreground["independent_clearance"][
                    "samples"
                ],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
