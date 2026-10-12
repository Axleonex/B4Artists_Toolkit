"""Package the 12.5.0 inline toolbar using the exact 12.4.0 inventory.

No host execution or tests are performed. Syntax, version metadata and archive
contents are inspected as packaging prerequisites.
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
VERSION = "12.5.0"
BASELINE = PROJECT / "releases" / "b4_anim_assist_v12.4.0.zip"
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
    actions = literal_assignment(contents[f"{root}/ui/timeline_catalog.py"].decode("utf-8"), "ACTIONS")
    operators = {}
    for name, data in contents.items():
        if f"{root}/operators/" not in name or not name.endswith(".py"):
            continue
        for cls in ast.parse(data.decode("utf-8-sig")).body:
            if not isinstance(cls, ast.ClassDef):
                continue
            idname = None
            props = set()
            for node in cls.body:
                if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "bl_idname" for t in node.targets):
                    idname = ast.literal_eval(node.value)
                if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                    props.add(node.target.id)
            if idname:
                operators[idname] = props
    for action, (suffix, arguments, label) in actions.items():
        target = f"animassist.{suffix}"
        if target not in operators or not set(arguments).issubset(operators[target]):
            raise ValueError(f"Unknown target or parameter for {action}: {target} {arguments}")
    groups = literal_assignment(contents[f"{root}/ui/timeline_catalog.py"].decode("utf-8"), "GROUPS")
    grouped = {action for _key, _label, entries in groups for action in entries if action is not None}
    if grouped != set(actions) or len(groups) != 7:
        raise ValueError("Catalogue and menu group inventory disagree")
    # Preserve dispatch and the seven families while allowing truthful labels
    # and the approved responsive drawing change.
    with zipfile.ZipFile(BASELINE) as previous:
        prior_catalogue = previous.read(f"{root}/ui/timeline_catalog.py").decode("utf-8")
    prior_actions = literal_assignment(prior_catalogue, "ACTIONS")
    prior_groups = literal_assignment(prior_catalogue, "GROUPS")
    if ({key: row[:2] for key, row in actions.items()} !=
            {key: row[:2] for key, row in prior_actions.items()} or groups != prior_groups):
        raise ValueError("Catalogue targets, parameters or menu groups changed")
    quick = literal_assignment(contents[f"{root}/ui/timeline_catalog.py"].decode("utf-8"), "QUICK_GROUPS")
    quick_actions = [action for _key, _label, entries in quick for action in entries]
    if set(quick_actions) != {"B25", "B50", "B75", "DRAG", "PUSH_PREV", "PULL_PREV",
                              "PULL_NEXT", "PUSH_NEXT", "T80", "T90", "T110", "T120",
                              "RIPPLE", "RANGE", "ALL", "ENDS", "OFFSET"} or len(quick_actions) != 17:
        raise ValueError("Original quick commands missing or duplicated in the catalog")
    with zipfile.ZipFile(BASELINE) as previous:
        changed_files = [name for name, data in contents.items()
                         if name not in previous.namelist() or previous.read(name) != data]
    expected_changes = {f"{root}/{name}" for name in (
        "CHANGELOG.md", "__init__.py", "constants.py", "blender_manifest.toml",
        "prefs.py", "ui/timeline_catalog.py", "ui/timeline_strip.py", "operators/settings_ops.py")}
    defaults = literal_assignment(contents[f"{root}/ui/timeline_catalog.py"].decode("utf-8"), "DEFAULT_QUICK_ACTIONS")
    if set(defaults) != {"B25","B50","B75","DRAG","SMOOTH","NUDGE_LEFT","NUDGE_RIGHT",
                         "RIPPLE","RANGE","ENDS","MIRROR_SELECTED","BAKE_STEP","TRAIL_SHOW"} or len(defaults)!=13:
        raise ValueError("Quick defaults disagree with the approved contract")
    preference_names = ["timeline_quick_" + action.lower() for action in actions]
    if len(set(preference_names)) != 70 or not set(quick_actions).issubset(actions):
        raise ValueError("Quick preference IDs collide or prior presets disappeared")
    if set(changed_files) != expected_changes:
        raise ValueError(f"Unexpected package changes: {changed_files}")
    # Replacement is limited to our generated candidate, verified against its
    # saved receipt. Never overwrite a baseline or an unknown local archive.
    if OUTPUT.exists():
        prior_receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
        if ("--replace-generated" not in sys.argv or prior_receipt["version"] != VERSION
                or hashlib.sha256(OUTPUT.read_bytes()).hexdigest() != prior_receipt["sha256"]):
            raise FileExistsError(f"Candidate is not the verified generated release: {OUTPUT}")
    candidate = OUTPUT.with_suffix(".zip.tmp")
    with zipfile.ZipFile(candidate, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in contents.items():
            entry = zipfile.ZipInfo(name, date_time=(2026, 10, 12, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = 0o100644 << 16
            archive.writestr(entry, data, compresslevel=9)
    candidate.replace(OUTPUT)
    receipt = {
        "version": VERSION,
        "status": "local release; unpublished; actual Bforartists acceptance pending; stand-in verification recorded separately",
        "package_root": root,
        "files": len(contents),
        "changed_files_from_12_4_0": changed_files,
        "python_files_syntax_parsed": syntax_count,
        "catalogue_presets": len(actions),
        "catalogue_unique_existing_operators": len({row[0] for row in actions.values()}),
        "menu_groups": len(groups),
        "default_quick_presets": list(defaults),
        "quick_preference_names": preference_names,
        "prior_quick_button_presets_preserved": 17,
        "catalogue_dispatch_preserved": {k: r[:2] for k,r in actions.items()} == {k: r[:2] for k,r in prior_actions.items()},
        "prior_quick_commands_pinnable": 17,
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
