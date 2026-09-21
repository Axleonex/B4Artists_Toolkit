"""Verify a local public-beta archive against the live add-on source."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import zipfile

import build_public_beta_package_v1 as builder


ROOT = Path(__file__).resolve().parents[2]


def check(archive_path: Path, root: Path = ROOT) -> dict[str, object]:
    archive_path = archive_path.resolve()
    source = builder.packaged_source(root)
    if not archive_path.is_file():
        raise FileNotFoundError(archive_path)
    if archive_path.name != builder.DEFAULT_ARCHIVE.name:
        raise ValueError(
            "archive filename differs from the public-beta contract: "
            f"expected {builder.DEFAULT_ARCHIVE.name}"
        )
    with zipfile.ZipFile(archive_path) as archive:
        names = archive.namelist()
        if names != sorted(source):
            raise ValueError("archive member set or order differs from the public-beta source")
        if archive.testzip() is not None:
            raise ValueError("archive has a corrupted member")
        if not all(archive.read(name) == payload for name, payload in source.items()):
            raise ValueError("archive payload differs from live source")
        version = builder.addon_version(archive.read("b4artists_ml/__init__.py"))
    if version != builder.ADDON_VERSION:
        raise ValueError("archive add-on version differs from the beta contract")
    return {
        "schema": "b4ml-public-beta-package-check-v1",
        "status": "PASS",
        "version": builder.VERSION,
        "archive": archive_path.as_posix(),
        "archive_sha256": hashlib.sha256(archive_path.read_bytes()).hexdigest(),
        "files": len(source),
        "addon_version": list(version),
        "package_matches_source": True,
        "training_started": False,
        "model_promotion_authorized": False,
        "cascadeur_connector_activation_permitted": False,
        "full_goal_complete": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = check(args.archive)
    if args.output is not None:
        if args.output.exists():
            raise FileExistsError(f"refusing to overwrite existing receipt: {args.output}")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
