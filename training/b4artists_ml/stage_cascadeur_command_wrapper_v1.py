"""Stage an exact Cascadeur command-wrapper bundle without installing it."""

from __future__ import annotations

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
OUTPUT = Path(os.environ.get(
    "B4ML_CASCADEUR_BUNDLE_ROOT",
    str(RESULTS / "cascadeur-command-wrapper-bundle-v1"),
))

SOURCE_FILES = {
    "package_init": TRAIN / "cascadeur_cli" / "__init__.py",
    "module_init": TRAIN / "cascadeur_cli" / "commands" / "__init__.py",
    "policy": TRAIN / "cascadeur_connector_policy_v1.py",
    "wrapper": TRAIN / "cascadeur_cli" / "commands" / "b4ml_cascadeur_import_audit.py",
}
BUNDLE_RELATIVE = {
    "package_init": Path("cascadeur_cli") / "__init__.py",
    "module_init": Path("cascadeur_cli") / "commands" / "__init__.py",
    "policy": Path("cascadeur_cli") / "commands" / "cascadeur_connector_policy_v1.py",
    "wrapper": Path("cascadeur_cli") / "commands" / "b4ml_cascadeur_import_audit.py",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> dict[str, object]:
    if OUTPUT.exists():
        raise FileExistsError(f"Refusing to overwrite existing bundle: {OUTPUT}")
    missing = [key for key, path in SOURCE_FILES.items() if not path.is_file()]
    if missing:
        raise RuntimeError("Missing wrapper sources: " + ", ".join(missing))

    OUTPUT.mkdir(parents=True)
    files = {}
    try:
        for key, source in SOURCE_FILES.items():
            target = OUTPUT / BUNDLE_RELATIVE[key]
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
            files[key] = {
                "bundle_path": target.relative_to(OUTPUT).as_posix(),
                "source_path": source.relative_to(ROOT).as_posix(),
                "source_sha256": sha256(source),
                "bundle_sha256": sha256(target),
                "bytes": target.stat().st_size,
            }

        manifest = {
            "schema": "b4ml-cascadeur-command-wrapper-bundle-v1",
            "status": "STAGED",
            "scope": (
                "Repository-local command-wrapper bundle only. The bundle is not "
                "installed into Cascadeur and does not modify Program Files, "
                "Cascadeur settings, source assets, or the B4ML runtime."
            ),
            "bundle_root": OUTPUT.relative_to(ROOT).as_posix()
            if OUTPUT.is_relative_to(ROOT) else str(OUTPUT),
            "destination_root": r"C:\Program Files\Cascadeur\resources\scripts\python\commands",
            "files": files,
            "installed_mutation_performed": False,
            "claims": {
                "wrapper_contract_verified": True,
                "deployment_verified": False,
                "cascadeur_import_verified": False,
                "conversion_verified": False,
                "parity_verified": False,
                "full_goal_complete": False,
            },
        }
        manifest_path = OUTPUT / "manifest.json"
        manifest_path.write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(json.dumps(manifest, indent=2, sort_keys=True))
        return manifest
    except Exception:
        shutil.rmtree(OUTPUT)
        raise


if __name__ == "__main__":
    main()
