"""Build a deterministic, local B4Artists ML public-beta archive."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
import zipfile


ROOT = Path(__file__).resolve().parents[2]
VERSION = "0.38.0-beta.1"
ADDON_VERSION = (0, 38, 0)
DEFAULT_ARCHIVE = ROOT / f"releases/b4artists_ml_v{VERSION}.zip"


def packaged_source(root: Path = ROOT) -> dict[str, bytes]:
    allowed = {".py", ".json", ".md", ".npz"}
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted((root / "b4artists_ml").rglob("*"))
        if path.is_file() and (path.suffix in allowed or path.name == "LICENSE")
    }


def addon_version(payload: bytes) -> tuple[int, int, int]:
    tree = ast.parse(payload)
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if not any(isinstance(target, ast.Name) and target.id == "bl_info" for target in node.targets):
            continue
        info = ast.literal_eval(node.value)
        version = info.get("version")
        if isinstance(version, tuple) and all(isinstance(value, int) for value in version):
            return version
    raise ValueError("b4artists_ml/__init__.py does not define a literal bl_info version")


def build(output: Path = DEFAULT_ARCHIVE, root: Path = ROOT) -> dict[str, object]:
    output = output.resolve()
    if output.exists():
        raise FileExistsError(f"refusing to overwrite existing beta archive: {output}")
    source = packaged_source(root)
    if not source or any("__pycache__" in name or name.endswith(".pyc") for name in source):
        raise ValueError("beta package source is empty or contains compiled Python")
    init_payload = source.get("b4artists_ml/__init__.py")
    if init_payload is None or addon_version(init_payload) != ADDON_VERSION:
        raise ValueError("beta package add-on version does not match the public-beta contract")
    for name, payload in source.items():
        if name.endswith(".py"):
            ast.parse(payload)

    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, payload in sorted(source.items()):
            info = zipfile.ZipInfo(name, date_time=(2026, 9, 20, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, payload, compresslevel=9)
    with zipfile.ZipFile(output) as archive:
        if archive.namelist() != sorted(source) or archive.testzip() is not None:
            raise ValueError("beta archive integrity or ordering check failed")
        if not all(archive.read(name) == payload for name, payload in source.items()):
            raise ValueError("beta archive differs from current source")
    return {
        "schema": "b4ml-public-beta-package-v1",
        "version": VERSION,
        "addon_version": list(ADDON_VERSION),
        "archive": output.as_posix(),
        "files": len(source),
        "bytes": output.stat().st_size,
        "sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
        "package_matches_source": True,
        "training_started": False,
        "model_promotion_authorized": False,
        "cascadeur_connector_activation_permitted": False,
        "full_goal_complete": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_ARCHIVE)
    args = parser.parse_args()
    print(json.dumps(build(args.output), sort_keys=True))


if __name__ == "__main__":
    main()
