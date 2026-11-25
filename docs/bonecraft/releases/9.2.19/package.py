"""Rebuild the frozen BoneCraft 9.2.19 archive from canonical source files."""
import ast
import hashlib
import io
import json
from pathlib import Path
import stat
import subprocess
import zipfile


ROOT = Path(__file__).resolve().parents[4]
VERSION = (9, 2, 19)
OUTPUT = ROOT / "releases/BoneCraft-BFA-9.2.19.zip"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def source_bytes(path):
    """Use staged repository bytes, independent of Windows checkout EOLs."""
    checked_out = path.read_bytes()
    data = subprocess.check_output([
        "git", "-C", str(ROOT), "show", ":" + path.relative_to(ROOT).as_posix(),
    ])
    if checked_out.replace(b"\r\n", b"\n") != data.replace(b"\r\n", b"\n"):
        raise RuntimeError(f"Stage source changes before packaging: {path}")
    return data


def build():
    if not (ROOT / ".git").exists():
        raise RuntimeError("Packaging requires a Git checkout with staged source files")
    source = ROOT / "bonecraft/boneforge"
    tree = ast.parse(source_bytes(source / "__init__.py"))
    metadata = next(node.value for node in tree.body
                    if isinstance(node, ast.Assign)
                    and any(isinstance(t, ast.Name) and t.id == "bl_info" for t in node.targets))
    assert tuple(ast.literal_eval(metadata)["version"]) == VERSION
    sidecar = source_bytes(source / "vrchat/export/sidecar.py").decode("utf-8")
    assert 'BONEFORGE_VERSION = "9.2.19"' in sidecar
    paths = [ROOT / name for name in subprocess.check_output([
        "git", "-C", str(ROOT), "ls-files", "bonecraft/boneforge",
    ], text=True).splitlines()]
    paths.sort()
    assert len(paths) == 233, "Review runtime scope before changing package membership"
    assert paths and all("__pycache__" not in path.parts for path in paths)
    payload = {}
    for path in paths:
        data = source_bytes(path)
        if path.suffix == ".py":
            ast.parse(data, filename=str(path))
        payload[path.relative_to(ROOT / "bonecraft").as_posix()] = data
    payload["boneforge/LICENSE"] = source_bytes(ROOT / "LICENSE")

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in sorted(payload.items()):
            entry = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            entry.create_system = 3
            entry.external_attr = (stat.S_IFREG | 0o644) << 16
            entry.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(entry, data, compresslevel=9)
    result = buffer.getvalue()
    with zipfile.ZipFile(io.BytesIO(result)) as archive:
        assert archive.testzip() is None
        assert {name: archive.read(name) for name in archive.namelist()} == payload
    if OUTPUT.exists() and OUTPUT.read_bytes() != result:
        raise RuntimeError("Refusing to overwrite a release archive with different bytes")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    if not OUTPUT.exists():
        OUTPUT.write_bytes(result)
    receipt = {
        "version": "9.2.19",
        "artifact": OUTPUT.relative_to(ROOT).as_posix(),
        "sha256": sha(result),
        "bytes": len(result),
        "python_modules": sum(path.suffix == ".py" for path in paths),
        "members": len(payload),
        "license_source": "LICENSE",
        "source_bytes_match": True,
        "source_input": "Staged Git blobs",
        "crc": "PASS",
        "zip_timestamp": [1980, 1, 1, 0, 0, 0],
        "compression": "DEFLATE level 9",
        "member_sha256": {name: sha(data) for name, data in sorted(payload.items())},
    }
    Path(__file__).with_name("package-receipt.json").write_text(
        json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in receipt.items() if k != "member_sha256"}, indent=2))


if __name__ == "__main__":
    build()
