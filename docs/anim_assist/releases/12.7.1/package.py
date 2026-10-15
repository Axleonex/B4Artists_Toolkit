"""Package the 12.7.1 Timeline keyframe-row fix using the 12.7.0 inventory.

Syntax, version metadata and archive contents are inspected as packaging
prerequisites. Only the overlay fix and version metadata may differ.
"""

from pathlib import Path, PurePosixPath
import ast
import hashlib
import json
import sys
import tomllib
import zipfile


PROJECT = Path(__file__).resolve().parents[4]
SOURCE = PROJECT / "anim_assist"
VERSION = "12.7.1"
BASELINE = PROJECT / "releases" / "b4_anim_assist_v12.7.0.zip"
OUTPUT = PROJECT / "releases" / f"b4_anim_assist_v{VERSION}.zip"
RECEIPT = Path(__file__).with_name("package-receipt.json")


def literal_assignment(source, name):
    for node in ast.parse(source).body:
        if isinstance(node, ast.Assign):
            if any(isinstance(target, ast.Name) and target.id == name
                   for target in node.targets):
                return ast.literal_eval(node.value)
        elif isinstance(node, ast.AnnAssign):
            if isinstance(node.target, ast.Name) and node.target.id == name:
                return ast.literal_eval(node.value)
    raise ValueError(f"Missing version field: {name}")


def main():
    with zipfile.ZipFile(BASELINE) as previous:
        names = [entry.filename for entry in previous.infolist() if not entry.is_dir()]
        prior = {name: previous.read(name) for name in names}
    roots = {PurePosixPath(name).parts[0] for name in names}
    if len(roots) != 1:
        raise ValueError("Expected one package root in the baseline release")
    root = roots.pop()
    contents = {}
    syntax_count = 0
    for name in sorted(names):
        relative = PurePosixPath(name).relative_to(root)
        if ".." in relative.parts or "__pycache__" in relative.parts:
            raise ValueError(f"Unexpected baseline path: {name}")
        data = SOURCE.joinpath(*relative.parts).read_bytes()
        if relative.suffix == ".py":
            ast.parse(data.decode("utf-8-sig"), filename=str(relative))
            syntax_count += 1
        contents[name] = data
    info = literal_assignment(contents[f"{root}/__init__.py"].decode("utf-8"), "bl_info")
    constants = contents[f"{root}/constants.py"].decode("utf-8")
    manifest = tomllib.loads(contents[f"{root}/blender_manifest.toml"].decode("utf-8"))
    versions = {
        "bl_info": ".".join(map(str, info["version"])),
        "constants_tuple": ".".join(map(str, literal_assignment(constants, "ADDON_VERSION"))),
        "constants_string": literal_assignment(constants, "ADDON_VERSION_STRING"),
        "manifest": manifest["version"],
    }
    if set(versions.values()) != {VERSION}:
        raise ValueError(f"Version metadata disagrees: {versions}")
    # Line endings follow the checkout; compare content, not CRLF/LF bytes.
    def normal(data):
        return data.replace(b"\r\n", b"\n")
    changed_files = sorted(name for name, data in contents.items()
                           if normal(prior[name]) != normal(data))
    expected_changes = {f"{root}/{name}" for name in (
        "CHANGELOG.md", "__init__.py", "constants.py", "blender_manifest.toml",
        "ui/timeline_overlay.py")}
    if set(changed_files) != expected_changes:
        raise ValueError(f"Unexpected package changes: {changed_files}")
    # Replacement is limited to our generated candidate, verified against its
    # saved receipt. Never overwrite a baseline or an unknown local archive.
    if OUTPUT.exists():
        prior_receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
        if ("--replace-generated" not in sys.argv or prior_receipt["version"] != VERSION
                or hashlib.sha256(OUTPUT.read_bytes()).hexdigest() != prior_receipt["sha256"]):
            raise FileExistsError(f"Output is not the verified generated release: {OUTPUT}")
    candidate = OUTPUT.with_suffix(".zip.tmp")
    with zipfile.ZipFile(candidate, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in contents.items():
            entry = zipfile.ZipInfo(name, date_time=(2026, 10, 14, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = 0o100644 << 16
            archive.writestr(entry, data, compresslevel=9)
    candidate.replace(OUTPUT)
    receipt = {
        "version": VERSION,
        "status": "Timeline keyframe-row fix; local release",
        "package_root": root,
        "files": len(contents),
        "changed_files_from_12_7_0": changed_files,
        "python_files_syntax_parsed": syntax_count,
        "versions": versions,
        "bytes": OUTPUT.stat().st_size,
        "sha256": hashlib.sha256(OUTPUT.read_bytes()).hexdigest(),
        "baseline_sha256": hashlib.sha256(BASELINE.read_bytes()).hexdigest(),
        "source_files_sha256": {name: hashlib.sha256(data).hexdigest()
                                for name, data in contents.items()},
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in receipt.items()
                      if key != "source_files_sha256"}, indent=2))


if __name__ == "__main__":
    main()
