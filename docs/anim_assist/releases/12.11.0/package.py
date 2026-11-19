"""Build the exact 12.11.0 installer from the 12.10.3 inventory plus Drivers modules."""
from pathlib import Path, PurePosixPath
import ast
import hashlib
import json
import sys
import tomllib
import zipfile

PROJECT = Path(__file__).resolve().parents[4]
VERSION = "12.11.0"
OUTPUT = PROJECT / "releases" / f"b4_anim_assist_v{VERSION}.zip"
RECEIPT = Path(__file__).with_name("package-receipt.json")
ADDED = ("core/driver_context.py", "operators/driver_ops.py", "ui/driver_panels.py")


def assignment(source, name):
    for node in ast.parse(source).body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in node.targets):
            return ast.literal_eval(node.value)
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.target.id == name:
            return ast.literal_eval(node.value)
    raise ValueError(name)


def main():
    with zipfile.ZipFile(PROJECT / "releases/b4_anim_assist_v12.10.3.zip") as baseline:
        names = [entry.filename for entry in baseline.infolist() if not entry.is_dir()]
    roots = {PurePosixPath(name).parts[0] for name in names}
    assert len(roots) == 1
    root = roots.pop()
    names += [f"{root}/{path}" for path in ADDED]
    assert len(names) == len(set(names))
    contents = {}
    for name in sorted(names):
        relative = PurePosixPath(name).relative_to(root)
        assert ".." not in relative.parts and "__pycache__" not in relative.parts
        data = (PROJECT / "anim_assist").joinpath(*relative.parts).read_bytes()
        if relative.suffix == ".py":
            ast.parse(data.decode("utf-8-sig"), filename=str(relative))
        contents[name] = data
    get = lambda name: contents[f"{root}/{name}"].decode("utf-8-sig")
    versions = [".".join(map(str, assignment(get("__init__.py"), "bl_info")["version"])),
                ".".join(map(str, assignment(get("constants.py"), "ADDON_VERSION"))),
                assignment(get("constants.py"), "ADDON_VERSION_STRING"),
                tomllib.loads(get("blender_manifest.toml"))["version"]]
    assert set(versions) == {VERSION}, versions
    if OUTPUT.exists():
        saved = json.loads(RECEIPT.read_text())
        assert "--replace-generated" in sys.argv and saved["sha256"] == hashlib.sha256(OUTPUT.read_bytes()).hexdigest()
    temporary = OUTPUT.with_suffix(".zip.tmp")
    with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in contents.items():
            entry = zipfile.ZipInfo(name, (2026, 11, 19, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = 0o100644 << 16
            archive.writestr(entry, data, compresslevel=9)
    temporary.replace(OUTPUT)
    with zipfile.ZipFile(OUTPUT) as archive:
        assert archive.testzip() is None
        assert all(archive.read(name) == data for name, data in contents.items())
    receipt = dict(version=VERSION, status="Local release candidate; not published", package_root=root,
        files=len(contents), python_files=sum(name.endswith(".py") for name in contents),
        bytes=OUTPUT.stat().st_size, sha256=hashlib.sha256(OUTPUT.read_bytes()).hexdigest(),
        source_files_sha256={name: hashlib.sha256(data).hexdigest() for name, data in contents.items()})
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in receipt.items() if key != "source_files_sha256"}, indent=2))


if __name__ == "__main__":
    main()
