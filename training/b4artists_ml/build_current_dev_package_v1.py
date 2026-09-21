"""Build a deterministic local development archive from the current source."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import zipfile


ROOT = Path(__file__).resolve().parents[2]
VERSION = "0.37.38-dev"
ARCHIVE = ROOT / f"releases/b4artists_ml_v{VERSION}.zip"
REPORT = ROOT / f"docs/b4artists_ml/package-test-v{VERSION}.json"


def packaged_source() -> dict[str, bytes]:
    return {
        path.relative_to(ROOT).as_posix(): path.read_bytes()
        for path in sorted((ROOT / "b4artists_ml").rglob("*"))
        if path.is_file()
        and (path.suffix in {".py", ".json", ".md", ".npz"} or path.name == "LICENSE")
    }


def main() -> None:
    source = packaged_source()
    if ARCHIVE.exists():
        raise RuntimeError(f"development archive already exists: {ARCHIVE}")
    with zipfile.ZipFile(
        ARCHIVE, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=9
    ) as archive:
        for name, payload in sorted(source.items()):
            info = zipfile.ZipInfo(name, date_time=(2026, 9, 15, 0, 0, 0))
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

    prior = json.loads(
        (ROOT / "docs/b4artists_ml/package-test-v0.37.37-dev.json").read_text(
            encoding="utf-8"
        )
    )
    report = dict(prior)
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
            "continuous_moving_sphere_chain_receipt": None,
            "continuous_moving_sphere_chain_receipt_sha256": None,
            "continuous_moving_sphere_chain_tests": None,
            "package_regression_receipt": None,
            "package_regression_receipt_sha256": None,
            "package_regression_layout": None,
            "package_regression_validation_receipt": None,
            "package_regression_validation_receipt_sha256": None,
            "extracted_package_regression_receipt": None,
            "direct_zip_import_regression_receipt": None,
            "direct_zip_import_regression_receipt_sha256": None,
            "direct_zip_import_tests": None,
            "foreground_receipt": None,
            "foreground_receipt_sha256": None,
            "foreground_validation_receipt": None,
            "foreground_modal_receipt": None,
            "foreground_modal_receipt_sha256": None,
            "foreground_modal_validation_receipt": None,
            "review_gate": {
                "status": "NOT_REQUESTED",
                "authority": False,
                "reviewer_invoked": False,
                "review_completed": False,
                "full_goal_complete": False,
            },
        }
    )
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
