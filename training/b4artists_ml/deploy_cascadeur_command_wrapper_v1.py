"""Deploy the staged Cascadeur command wrapper only with explicit ``--apply``."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil


ROOT = Path(os.environ.get(
    "B4ML_REPO",
    r"X:\Scripting Attempts\B4Artists_Tools\B4Artists_Anim_Tools_github",
))
TRAIN = ROOT / "training" / "b4artists_ml"
RESULTS = TRAIN / "results"
BUNDLE = Path(os.environ.get(
    "B4ML_CASCADEUR_BUNDLE_ROOT",
    str(RESULTS / "cascadeur-command-wrapper-bundle-v1"),
))
DESTINATION = Path(os.environ.get(
    "B4ML_CASCADEUR_COMMAND_ROOT",
    r"C:\Program Files\Cascadeur\resources\scripts\python\commands",
))
OUTPUT = RESULTS / "cascadeur-command-wrapper-deployment-v1.json"
EXPECTED = ("package_init", "module_init", "policy", "wrapper")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_bundle() -> tuple[dict, dict[str, Path]]:
    manifest_path = BUNDLE / "manifest.json"
    if not manifest_path.is_file():
        raise FileNotFoundError(manifest_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    if manifest.get("schema") != "b4ml-cascadeur-command-wrapper-bundle-v1":
        raise ValueError("Unexpected wrapper bundle schema")
    if manifest.get("status") != "STAGED":
        raise ValueError("Wrapper bundle is not staged")
    files = manifest.get("files", {})
    if tuple(sorted(files)) != tuple(sorted(EXPECTED)):
        raise ValueError("Wrapper bundle file set is incomplete")
    paths = {}
    for key in EXPECTED:
        relative = Path(files[key]["bundle_path"])
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError("Unsafe bundle path: " + str(relative))
        path = BUNDLE / relative
        if not path.is_file():
            raise FileNotFoundError(path)
        if sha256(path) != files[key]["bundle_sha256"]:
            raise ValueError("Bundle hash mismatch: " + key)
        if files[key]["source_sha256"] != files[key]["bundle_sha256"]:
            raise ValueError("Source/bundle hash mismatch: " + key)
        paths[key] = path
    return manifest, paths


def write_report(report: dict) -> dict:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return report


def main(argv: list[str] | None = None) -> dict:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Copy only missing hash-verified wrapper files into the configured command root.",
    )
    args = parser.parse_args(argv)
    manifest, bundle_paths = load_bundle()
    destination_paths = {
        key: DESTINATION / Path(manifest["files"][key]["bundle_path"])
        for key in EXPECTED
    }
    existing = [key for key, path in destination_paths.items() if path.exists()]
    base = {
        "schema": "b4ml-cascadeur-command-wrapper-deployment-v1",
        "scope": (
            "Explicit local deployment helper for the staged Cascadeur command "
            "wrapper. Dry run is the default; existing destination files are "
            "never overwritten. This does not run Cascadeur or claim import, "
            "conversion, animation, or parity."
        ),
        "bundle_manifest": str((BUNDLE / "manifest.json").relative_to(ROOT)).replace("\\", "/")
        if BUNDLE.is_relative_to(ROOT) else str(BUNDLE / "manifest.json"),
        "destination_root": str(DESTINATION),
        "existing_destination_files": existing,
        "apply_requested": args.apply,
        "mutation_performed": False,
        "claims": {
            "bundle_verified": True,
            "deployment_verified": False,
            "cascadeur_import_verified": False,
            "conversion_verified": False,
            "parity_verified": False,
            "full_goal_complete": False,
        },
    }
    if existing:
        return write_report({**base, "status": "REFUSED_EXISTING_DESTINATION"})
    if not args.apply:
        return write_report({**base, "status": "DRY_RUN_READY"})
    if not DESTINATION.is_dir():
        return write_report({**base, "status": "DESTINATION_ROOT_MISSING"})

    created: list[Path] = []
    created_dirs: list[Path] = []

    def rollback() -> list[str]:
        failures: list[str] = []
        for path in reversed(created):
            try:
                if path.is_file():
                    path.unlink()
            except OSError:
                failures.append(str(path))
        for directory in reversed(created_dirs):
            try:
                if directory.is_dir() and not any(directory.iterdir()):
                    directory.rmdir()
            except OSError:
                failures.append(str(directory))
        return failures

    try:
        for key, source in bundle_paths.items():
            target = destination_paths[key]
            missing_dirs: list[Path] = []
            cursor = target.parent
            while not cursor.exists():
                missing_dirs.append(cursor)
                cursor = cursor.parent
            target.parent.mkdir(parents=True, exist_ok=True)
            created_dirs.extend(
                directory for directory in missing_dirs if directory.is_dir()
            )
            shutil.copyfile(source, target)
            created.append(target)
        for key, target in destination_paths.items():
            if sha256(target) != sha256(bundle_paths[key]):
                raise ValueError("Post-deployment hash mismatch: " + key)
    except PermissionError as error:
        rollback_failures = rollback()
        return write_report({
            **base,
            "status": "PERMISSION_REQUIRED" if not rollback_failures else "ROLLBACK_FAILED",
            "permission_error": str(error),
            "created_before_failure": [str(path) for path in created],
            "rollback_verified": not rollback_failures,
            "mutation_performed": bool(rollback_failures),
            "next_action": (
                "Retry --apply from an elevated PowerShell after confirming the "
                "destination_root is the intended Cascadeur installation."
                if not rollback_failures
                else "Inspect and clean the reported rollback failures before retrying."
            ),
        })
    except Exception:
        rollback()
        raise
    return write_report({
        **base,
        "status": "DEPLOYED",
        "mutation_performed": True,
        "claims": {**base["claims"], "deployment_verified": True},
    })


if __name__ == "__main__":
    main()
