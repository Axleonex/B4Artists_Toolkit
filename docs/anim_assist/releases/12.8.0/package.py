"""Build the 12.8.0 add-on from the existing inventory and three NLA modules."""
from pathlib import Path, PurePosixPath
import ast
import hashlib
import json
import sys
import tomllib
import zipfile

PROJECT = Path(__file__).resolve().parents[4]
VERSION = "12.8.0"
OUTPUT = PROJECT / "releases" / f"b4_anim_assist_v{VERSION}.zip"
RECEIPT = Path(__file__).with_name("package-receipt.json")


def assignment(source, name):
    for node in ast.parse(source).body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in node.targets):
            return ast.literal_eval(node.value)
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.target.id == name:
            return ast.literal_eval(node.value)
    raise ValueError(name)


def main():
    with zipfile.ZipFile(PROJECT / "releases/b4_anim_assist_v12.7.1.zip") as baseline:
        names = [e.filename for e in baseline.infolist() if not e.is_dir()]
    roots = {PurePosixPath(n).parts[0] for n in names}
    assert len(roots) == 1
    root = roots.pop()
    names += [f"{root}/{n}" for n in ("core/nla_context.py", "operators/nla_ops.py", "ui/nla_panels.py")]
    assert len(names) == len(set(names))
    contents = {}
    for name in sorted(names):
        relative = PurePosixPath(name).relative_to(root)
        assert ".." not in relative.parts and "__pycache__" not in relative.parts
        data = (PROJECT / "anim_assist").joinpath(*relative.parts).read_bytes()
        if relative.suffix == ".py":
            ast.parse(data.decode("utf-8-sig"), filename=str(relative))
        text = data.decode("utf-8", errors="replace").lower()
        assert not any(token in text for token in ("co-authored-by:", "generated-by:")), relative
        contents[name] = data
    get = lambda name: contents[f"{root}/{name}"].decode("utf-8")
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
            entry = zipfile.ZipInfo(name, (2026, 10, 15, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = 0o100644 << 16
            archive.writestr(entry, data, compresslevel=9)
    temporary.replace(OUTPUT)
    receipt = dict(version=VERSION, status="Local add-on release", package_root=root,
        files=len(contents), python_files=sum(n.endswith(".py") for n in contents),
        bytes=OUTPUT.stat().st_size, sha256=hashlib.sha256(OUTPUT.read_bytes()).hexdigest(),
        source_files_sha256={n: hashlib.sha256(d).hexdigest() for n, d in contents.items()})
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k:v for k,v in receipt.items() if k != "source_files_sha256"}, indent=2))


if __name__ == "__main__":
    main()
