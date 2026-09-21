"""Build the next immutable local development archive from current source."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import zipfile

from build_current_dev_package_v3 import packaged_source


ROOT = Path(__file__).resolve().parents[2]
VERSION = "0.37.43-dev"
ARCHIVE = ROOT / f"releases/b4artists_ml_v{VERSION}.zip"
REPORT = ROOT / f"docs/b4artists_ml/package-test-v{VERSION}.json"
PRIOR_REPORT = ROOT / "docs/b4artists_ml/package-test-v0.37.42-dev.json"


def main() -> None:
    source = packaged_source()
    if ARCHIVE.exists():
        raise RuntimeError(f"development archive already exists: {ARCHIVE}")
    with zipfile.ZipFile(
        ARCHIVE, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=9
    ) as archive:
        for name, payload in sorted(source.items()):
            info = zipfile.ZipInfo(name, date_time=(2026, 9, 16, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, payload, compresslevel=9)
    with zipfile.ZipFile(ARCHIVE) as archive:
        if archive.namelist() != sorted(source):
            raise RuntimeError("archive member ordering does not match source")
        if archive.testzip() is not None:
            raise RuntimeError("archive integrity check failed")
        if not all(archive.read(name) == payload for name, payload in source.items()):
            raise RuntimeError("archive payload does not match source")

    report = json.loads(PRIOR_REPORT.read_text(encoding="utf-8"))
    report.update(
        {
            "version": VERSION,
            "files": len(source),
            "bytes": ARCHIVE.stat().st_size,
            "sha256": hashlib.sha256(ARCHIVE.read_bytes()).hexdigest(),
            "package_matches_source": True,
            "full_goal_complete": False,
            "runtime_sha256": {
                name: hashlib.sha256(payload).hexdigest()
                for name, payload in source.items()
            },
            "blender_binding_qualification": "pending",
            "affected_regression": "pending",
            "foreground_lifecycle": "pending",
            "focused_validation": {
                "status": "PENDING",
                "tests": None,
                "package": f"releases/b4artists_ml_v{VERSION}.zip",
            },
            "review_gate": {
                "status": "NOT_REQUESTED",
                "authority": False,
                "reviewer_invoked": False,
                "review_completed": False,
                "full_goal_complete": False,
            },
        }
    )
    for key in (
        "package_regression_receipt", "package_regression_receipt_sha256",
        "package_regression_tests", "package_regression_suites",
        "direct_zip_import_regression_receipt", "direct_zip_import_regression_receipt_sha256",
        "direct_zip_import_tests", "foreground_receipt", "foreground_receipt_sha256",
        "foreground_clearance_samples", "moving_deforming_mesh_receipt",
        "moving_deforming_mesh_receipt_sha256", "moving_deforming_mesh_tests",
        "coupled_pelvis_spine_receipt", "coupled_pelvis_spine_receipt_sha256",
        "coupled_pelvis_spine_tests", "multiple_static_sphere_collision_receipt",
        "multiple_static_sphere_collision_receipt_sha256", "multiple_static_sphere_collision_tests",
        "force_offset_torque_receipt", "force_offset_torque_receipt_sha256",
        "force_offset_torque_tests", "self_collision_receipt", "self_collision_receipt_sha256",
        "self_collision_tests", "production_character_generalization_receipt",
        "production_character_generalization_receipt_sha256", "production_character_generalization_tests",
        "continuous_moving_capsule_chain_receipt", "continuous_moving_capsule_chain_receipt_sha256",
        "continuous_moving_capsule_chain_tests", "continuous_moving_sphere_chain_receipt",
        "continuous_moving_sphere_chain_receipt_sha256", "continuous_moving_sphere_chain_tests",
    ):
        report[key] = None
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "archive": str(ARCHIVE),
                "version": VERSION,
                "files": len(source),
                "bytes": ARCHIVE.stat().st_size,
                "sha256": report["sha256"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
