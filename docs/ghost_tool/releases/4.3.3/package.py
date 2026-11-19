"""Rebuild the frozen Ghost Tool 4.3.3 archive from canonical source files."""
import ast
import hashlib
import io
import json
from pathlib import Path
import stat
import zipfile


ROOT = Path(__file__).resolve().parents[4]
VERSION = (4, 3, 3)
OUTPUT = ROOT / "releases/b4_ghost_tool_v4.3.3.zip"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def build():
    source = ROOT / "ghost_tool"
    tree = ast.parse((source / "__init__.py").read_bytes())
    metadata = next(node.value for node in tree.body
                    if isinstance(node, ast.Assign)
                    and any(isinstance(t, ast.Name) and t.id == "bl_info" for t in node.targets))
    assert tuple(ast.literal_eval(metadata)["version"]) == VERSION
    paths = sorted(source.rglob("*.py"))
    assert paths and all("__pycache__" not in path.parts for path in paths)
    payload = {}
    for path in paths:
        data = path.read_bytes()
        ast.parse(data, filename=str(path))
        payload[path.relative_to(ROOT).as_posix()] = data
    payload["ghost_tool/LICENSE"] = (ROOT / "LICENSE").read_bytes()

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
        "version": "4.3.3",
        "artifact": OUTPUT.relative_to(ROOT).as_posix(),
        "sha256": sha(result),
        "bytes": len(result),
        "python_modules": len(paths),
        "members": len(payload),
        "license_source": "LICENSE",
        "source_bytes_match": True,
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
